import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

from keyboards.translator import (
    TRANSLATOR_BUTTON_TEXT,
    get_translator_actions_keyboard,
    get_translator_languages_keyboard,
)
from prompts import build_translation_system_prompt
from services.openai_service import OpenAIService, OpenAIServiceError
from states.translator import TranslatorStates
from translator_data import TRANSLATION_LANGUAGES
from utils.messages import split_message

logger = logging.getLogger(__name__)
router = Router(name=__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRANSLATOR_IMAGE_PATH = PROJECT_ROOT / "assets" / "translator.png"


async def start_translator(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(TranslatorStates.choosing_language)

    try:
        if not TRANSLATOR_IMAGE_PATH.is_file():
            raise FileNotFoundError
        await message.answer_photo(FSInputFile(TRANSLATOR_IMAGE_PATH))
    except (OSError, TelegramAPIError) as error:
        logger.error(
            "Не удалось отправить заставку переводчика: %s",
            type(error).__name__,
        )

    await message.answer(
        "Выберите язык перевода.",
        reply_markup=get_translator_languages_keyboard(),
    )


@router.message(Command("translate"))
@router.message(F.text == TRANSLATOR_BUTTON_TEXT)
async def handle_translator_start(
    message: Message,
    state: FSMContext,
) -> None:
    await start_translator(message, state)


@router.callback_query(
    TranslatorStates.choosing_language,
    F.data.startswith("translate:language:"),
)
async def handle_translation_language(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    language_id = callback.data.rsplit(":", maxsplit=1)[-1]
    language = TRANSLATION_LANGUAGES.get(language_id)

    if language is None:
        await callback.answer("Неизвестный язык.")
        if isinstance(callback.message, Message):
            await callback.message.answer(
                "Пожалуйста, выберите язык из списка.",
                reply_markup=get_translator_languages_keyboard(),
            )
        return

    await callback.answer()
    await state.update_data(
        language_id=language_id,
        language_name=language["name"],
    )
    await state.set_state(TranslatorStates.waiting_for_text)

    if isinstance(callback.message, Message):
        await callback.message.answer(
            f"Выбран язык: {language['name']}.\n\n"
            "Отправьте текст, который нужно перевести.",
            reply_markup=get_translator_actions_keyboard(),
        )


@router.message(
    TranslatorStates.choosing_language,
    F.text,
    ~F.text.startswith("/"),
)
async def handle_text_before_language(message: Message) -> None:
    await message.answer(
        "Сначала выберите язык с помощью кнопок.",
        reply_markup=get_translator_languages_keyboard(),
    )


@router.message(
    TranslatorStates.waiting_for_text,
    F.text,
    ~F.text.startswith("/"),
)
async def handle_translation_text(
    message: Message,
    state: FSMContext,
    openai_service: OpenAIService,
) -> None:
    source_text = message.text
    if not source_text or not source_text.strip():
        await message.answer(
            "Отправьте непустой текст для перевода.",
            reply_markup=get_translator_actions_keyboard(),
        )
        return

    data = await state.get_data()
    language_id = data.get("language_id")
    language = (
        TRANSLATION_LANGUAGES.get(language_id)
        if isinstance(language_id, str)
        else None
    )
    if language is None:
        await state.clear()
        await state.set_state(TranslatorStates.choosing_language)
        await message.answer(
            "Сначала выберите язык с помощью кнопок.",
            reply_markup=get_translator_languages_keyboard(),
        )
        return

    try:
        async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id,
        ):
            translation = await openai_service.generate_text(
                system_prompt=build_translation_system_prompt(
                    language["prompt_name"]
                ),
                user_prompt=source_text,
            )
    except OpenAIServiceError:
        await message.answer(
            "Не удалось выполнить перевод. Попробуйте отправить текст ещё "
            "раз немного позже.",
            reply_markup=get_translator_actions_keyboard(),
        )
        return

    translation_parts = split_message(translation)
    for index, part in enumerate(translation_parts):
        is_last_part = index == len(translation_parts) - 1
        await message.answer(
            part,
            reply_markup=(
                get_translator_actions_keyboard() if is_last_part else None
            ),
        )


@router.message(TranslatorStates.waiting_for_text, ~F.text)
async def handle_translation_non_text(message: Message) -> None:
    await message.answer(
        "В этом режиме отправьте текстовое сообщение.",
        reply_markup=get_translator_actions_keyboard(),
    )


@router.callback_query(
    TranslatorStates.waiting_for_text,
    F.data == "translate:change_language",
)
async def handle_translation_language_change(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await callback.answer()
    await state.clear()
    await state.set_state(TranslatorStates.choosing_language)

    if isinstance(callback.message, Message):
        await callback.message.answer(
            "Выберите новый язык перевода.",
            reply_markup=get_translator_languages_keyboard(),
        )
