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
from prompts import QUIZ_SYSTEM_PROMPT, build_quiz_prompt
from quiz_data import QUIZ_TOPICS
from services.openai_service import OpenAIService, OpenAIServiceError
from states.quiz import QuizStates


logger = logging.getLogger(__name__)
router = Router(name=__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUIZ_IMAGE_PATH = PROJECT_ROOT / "assets" / "quiz.png"


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
            question_data = await openai_service.chat_json(
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
    except OpenAIServiceError:
        await callback.message.answer(
            "Не удалось подготовить вопрос. Попробуйте выбрать тему ещё раз "
            "немного позже.",
            reply_markup=get_quiz_topics_keyboard(),
        )
        return

    question = cast(str, question_data["question"])
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
async def handle_quiz_answer_placeholder(message: Message) -> None:
    await message.answer(
        "Ответ получен. Проверку ответа мы добавим на следующем этапе "
        "разработки.",
        reply_markup=get_quiz_exit_keyboard(),
    )


@router.message(QuizStates.waiting_for_answer, ~F.text)
async def handle_quiz_non_text_answer(message: Message) -> None:
    await message.answer(
        "Ответ на вопрос нужно отправить текстом.",
        reply_markup=get_quiz_exit_keyboard(),
    )
