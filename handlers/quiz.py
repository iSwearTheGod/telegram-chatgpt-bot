import logging
from pathlib import Path
from typing import cast

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

from keyboards.quiz import (
    QUIZ_BUTTON_TEXT,
    get_quiz_exit_keyboard,
    get_quiz_topics_keyboard,
)
from prompts import (
    QUIZ_ANSWER_CHECK_SYSTEM_PROMPT,
    QUIZ_SYSTEM_PROMPT,
    build_quiz_answer_check_prompt,
    build_quiz_prompt,
)
from quiz_data import QUIZ_TOPICS
from services.openai_service import OpenAIService, OpenAIServiceError
from states.quiz import QuizStates


logger = logging.getLogger(__name__)
router = Router(name=__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUIZ_IMAGE_PATH = PROJECT_ROOT / "assets" / "quiz.png"


def validate_question_data(data: dict[str, object]) -> dict[str, str]:
    fields = ("question", "correct_answer", "explanation")
    if any(
        not isinstance(data.get(field), str)
        or not cast(str, data[field]).strip()
        for field in fields
    ):
        logger.error("JSON-ответ OpenAI не соответствует структуре вопроса.")
        raise OpenAIServiceError("Некорректная структура вопроса.")

    return {field: cast(str, data[field]).strip() for field in fields}


def validate_answer_check(data: dict[str, object]) -> tuple[bool, str]:
    is_correct = data.get("is_correct")
    feedback = data.get("feedback")
    if not isinstance(is_correct, bool) or not isinstance(feedback, str):
        logger.error("JSON-ответ OpenAI не соответствует проверке ответа.")
        raise OpenAIServiceError("Некорректная структура проверки ответа.")

    feedback = feedback.strip()
    if not feedback:
        logger.error("OpenAI вернул пустой комментарий к ответу.")
        raise OpenAIServiceError("Пустой комментарий к ответу.")

    return is_correct, feedback


async def start_quiz(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.update_data(score=0, questions_count=0)
    await state.set_state(QuizStates.choosing_topic)

    try:
        if not QUIZ_IMAGE_PATH.is_file():
            raise FileNotFoundError
        await message.answer_photo(FSInputFile(QUIZ_IMAGE_PATH))
    except (OSError, TelegramAPIError) as error:
        logger.error(
            "Не удалось отправить заставку квиза: %s",
            type(error).__name__,
        )

    await message.answer(
        "Выберите тему квиза.",
        reply_markup=get_quiz_topics_keyboard(),
    )


@router.message(Command("quiz"))
@router.message(F.text == QUIZ_BUTTON_TEXT)
async def handle_quiz_start(
    message: Message,
    state: FSMContext,
) -> None:
    await start_quiz(message, state)


@router.callback_query(
    QuizStates.choosing_topic,
    F.data.startswith("quiz:topic:"),
)
async def handle_quiz_topic(
    callback: CallbackQuery,
    state: FSMContext,
    openai_service: OpenAIService,
) -> None:
    topic_id = callback.data.rsplit(":", maxsplit=1)[-1]
    topic = QUIZ_TOPICS.get(topic_id)

    if topic is None:
        await callback.answer("Неизвестная тема.")
        if isinstance(callback.message, Message):
            await callback.message.answer(
                "Пожалуйста, выберите тему из списка.",
                reply_markup=get_quiz_topics_keyboard(),
            )
        return

    await callback.answer()
    current_data = await state.get_data()
    await state.update_data(
        topic_id=topic_id,
        topic_name=topic["name"],
        score=current_data.get("score", 0),
        questions_count=current_data.get("questions_count", 0),
    )

    if not isinstance(callback.message, Message):
        return

    try:
        async with ChatActionSender.typing(
            bot=callback.bot,
            chat_id=callback.message.chat.id,
        ):
            question_data = validate_question_data(
                await openai_service.chat_json(
                    [
                        {"role": "system", "content": QUIZ_SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": build_quiz_prompt(
                                topic["name"],
                                topic["description"],
                            ),
                        },
                    ]
                )
            )
    except OpenAIServiceError:
        await callback.message.answer(
            "Не удалось подготовить вопрос. Попробуйте выбрать тему ещё раз "
            "немного позже.",
            reply_markup=get_quiz_topics_keyboard(),
        )
        return

    question = question_data["question"]
    await state.update_data(
        question=question,
        correct_answer=question_data["correct_answer"],
        explanation=question_data["explanation"],
    )
    await state.set_state(QuizStates.waiting_for_answer)

    await callback.message.answer(
        f"{question}\n\nСледующее текстовое сообщение будет считаться ответом.",
        reply_markup=get_quiz_exit_keyboard(),
    )


@router.message(
    QuizStates.choosing_topic,
    F.text,
    ~F.text.startswith("/"),
)
async def handle_message_before_topic(message: Message) -> None:
    await message.answer(
        "Сначала выберите тему квиза с помощью кнопок.",
        reply_markup=get_quiz_topics_keyboard(),
    )


@router.message(
    QuizStates.waiting_for_answer,
    F.text,
    ~F.text.startswith("/"),
)
async def handle_quiz_answer(
    message: Message,
    state: FSMContext,
    openai_service: OpenAIService,
) -> None:
    user_answer = message.text
    if not user_answer:
        return

    data = await state.get_data()
    required_fields = (
        "topic_name",
        "question",
        "correct_answer",
        "explanation",
    )
    if any(
        not isinstance(data.get(field), str)
        or not cast(str, data[field]).strip()
        for field in required_fields
    ):
        logger.error("В FSM отсутствуют данные текущего вопроса.")
        await state.clear()
        await message.answer(
            "Данные вопроса потеряны. Начните новый квиз командой /quiz."
        )
        return

    topic_name = cast(str, data["topic_name"])
    question = cast(str, data["question"])
    correct_answer = cast(str, data["correct_answer"])
    explanation = cast(str, data["explanation"])
    score = int(data.get("score", 0))
    questions_count = int(data.get("questions_count", 0))

    try:
        async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id,
        ):
            is_correct, feedback = validate_answer_check(
                await openai_service.chat_json(
                    [
                        {
                            "role": "system",
                            "content": QUIZ_ANSWER_CHECK_SYSTEM_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": build_quiz_answer_check_prompt(
                                topic_name=topic_name,
                                question=question,
                                correct_answer=correct_answer,
                                user_answer=user_answer,
                                explanation=explanation,
                            ),
                        },
                    ]
                )
            )
    except OpenAIServiceError:
        await message.answer(
            "Не удалось проверить ответ. Попробуйте отправить его ещё раз "
            "немного позже.",
            reply_markup=get_quiz_exit_keyboard(),
        )
        return

    questions_count += 1
    if is_correct:
        score += 1

    await state.update_data(
        score=score,
        questions_count=questions_count,
    )
    await state.set_state(QuizStates.viewing_result)

    if is_correct:
        result_text = (
            "✅ Правильно!\n\n"
            f"Комментарий: {feedback}\n\n"
            f"Правильный ответ: {correct_answer}\n\n"
            f"Счёт: {score}/{questions_count}"
        )
    else:
        result_text = (
            "❌ Неправильно.\n\n"
            f"Комментарий: {feedback}\n\n"
            f"Правильный ответ: {correct_answer}\n\n"
            f"Объяснение: {explanation}\n\n"
            f"Счёт: {score}/{questions_count}"
        )

    await message.answer(
        result_text,
        reply_markup=get_quiz_exit_keyboard(),
    )


@router.message(QuizStates.waiting_for_answer, ~F.text)
async def handle_quiz_non_text_answer(message: Message) -> None:
    await message.answer(
        "Ответ на вопрос нужно отправить текстом.",
        reply_markup=get_quiz_exit_keyboard(),
    )


@router.message(
    QuizStates.viewing_result,
    F.text,
    ~F.text.startswith("/"),
)
async def handle_text_after_quiz_result(message: Message) -> None:
    await message.answer(
        "Ответ уже проверен. Завершите квиз или дождитесь следующих действий.",
        reply_markup=get_quiz_exit_keyboard(),
    )
