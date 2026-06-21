import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

from keyboards.talk import (
    TALK_BUTTON_TEXT,
    get_personality_keyboard,
    get_talk_keyboard,
)
from prompts import TALK_PERSONALITIES
from services.openai_service import OpenAIService, OpenAIServiceError
from states.talk import TalkStates
from utils.messages import split_message

logger = logging.getLogger(__name__)
router = Router(name=__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TALK_IMAGE_PATH = PROJECT_ROOT / "assets" / "talk.png"
HISTORY_LIMIT = 12


async def start_talk_mode(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(TalkStates.choosing_person)

    try:
        if not TALK_IMAGE_PATH.is_file():
            raise FileNotFoundError
        await message.answer_photo(FSInputFile(TALK_IMAGE_PATH))
    except (OSError, TelegramAPIError) as error:
        logger.error(
            "Не удалось отправить заставку режима разговора: %s",
            type(error).__name__,
        )

    await message.answer(
        "Выберите личность для образовательного диалога.",
        reply_markup=get_personality_keyboard(),
    )


@router.message(Command("talk"))
@router.message(F.text == TALK_BUTTON_TEXT)
async def handle_talk_start(
    message: Message,
    state: FSMContext,
) -> None:
    await start_talk_mode(message, state)


@router.callback_query(
    TalkStates.choosing_person,
    F.data.startswith("talk:person:"),
)
async def handle_personality_choice(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    person_id = callback.data.rsplit(":", maxsplit=1)[-1]
    personality = TALK_PERSONALITIES.get(person_id)

    if personality is None:
        await callback.answer("Неизвестная личность.")
        if isinstance(callback.message, Message):
            await callback.message.answer(
                "Пожалуйста, выберите личность из списка.",
                reply_markup=get_personality_keyboard(),
            )
        return

    await callback.answer()
    await state.set_state(TalkStates.chatting)
    await state.update_data(
        person_id=person_id,
        person_name=personality["name"],
        system_prompt=personality["system_prompt"],
        history=[],
    )

    if isinstance(callback.message, Message):
        await callback.message.answer(
            f"Начинаем диалог: {personality['name']}. "
            "Напишите первое сообщение.",
            reply_markup=get_talk_keyboard(),
        )


@router.callback_query(TalkStates.chatting, F.data == "talk:change")
async def handle_personality_change(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await callback.answer()
    await state.clear()
    await state.set_state(TalkStates.choosing_person)

    if isinstance(callback.message, Message):
        await callback.message.answer(
            "Выберите новую личность.",
            reply_markup=get_personality_keyboard(),
        )


@router.message(
    TalkStates.chatting,
    F.text,
    ~F.text.startswith("/"),
)
async def handle_talk_message(
    message: Message,
    state: FSMContext,
    openai_service: OpenAIService,
) -> None:
    user_text = message.text
    if not user_text:
        return

    data = await state.get_data()
    system_prompt = data.get("system_prompt")
    history: list[dict[str, str]] = data.get("history", [])

    if not isinstance(system_prompt, str):
        await state.clear()
        await state.set_state(TalkStates.choosing_person)
        await message.answer(
            "Сначала выберите личность с помощью кнопок.",
            reply_markup=get_personality_keyboard(),
        )
        return

    request_messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_text},
    ]

    try:
        async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id,
        ):
            answer = await openai_service.chat(request_messages)
    except OpenAIServiceError:
        await message.answer(
            "Не удалось получить ответ. Попробуйте отправить сообщение ещё "
            "раз немного позже.",
            reply_markup=get_talk_keyboard(),
        )
        return

    updated_history = [
        *history,
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": answer},
    ][-HISTORY_LIMIT:]
    await state.update_data(history=updated_history)

    answer_parts = split_message(answer)
    for index, part in enumerate(answer_parts):
        is_last_part = index == len(answer_parts) - 1
        await message.answer(
            part,
            reply_markup=get_talk_keyboard() if is_last_part else None,
        )


@router.message(TalkStates.chatting, ~F.text)
async def handle_talk_non_text(message: Message) -> None:
    await message.answer(
        "В этом режиме отправьте текстовое сообщение.",
        reply_markup=get_talk_keyboard(),
    )


@router.message(
    TalkStates.choosing_person,
    F.text,
    ~F.text.startswith("/"),
)
async def handle_message_before_personality(message: Message) -> None:
    await message.answer(
        "Сначала выберите личность с помощью кнопок.",
        reply_markup=get_personality_keyboard(),
    )
