import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from keyboards.translator import (
    TRANSLATOR_BUTTON_TEXT,
    get_translator_actions_keyboard,
    get_translator_languages_keyboard,
)
from states.translator import TranslatorStates
from translator_data import TRANSLATION_LANGUAGES


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
