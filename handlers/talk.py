import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from keyboards.talk import (
    TALK_BUTTON_TEXT,
    get_personality_keyboard,
    get_talk_keyboard,
)
from prompts import TALK_PERSONALITIES
from states.talk import TalkStates


logger = logging.getLogger(__name__)
router = Router(name=__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TALK_IMAGE_PATH = PROJECT_ROOT / "assets" / "talk.png"


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


@router.callback_query(F.data == "talk:change")
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
