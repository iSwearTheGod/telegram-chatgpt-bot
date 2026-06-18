import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

from keyboards.main_menu import RANDOM_FACT_BUTTON_TEXT
from keyboards.random_fact import get_random_fact_keyboard
from prompts import RANDOM_FACT_SYSTEM_PROMPT
from services.openai_service import OpenAIService, OpenAIServiceError


logger = logging.getLogger(__name__)
router = Router(name=__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RANDOM_IMAGE_PATH = PROJECT_ROOT / "assets" / "random.png"


async def send_random_fact(
    message: Message,
    openai_service: OpenAIService,
) -> None:
    try:
        if not RANDOM_IMAGE_PATH.is_file():
            raise FileNotFoundError
        await message.answer_photo(FSInputFile(RANDOM_IMAGE_PATH))
    except (OSError, TelegramAPIError) as error:
        logger.error(
            "Не удалось отправить заставку: %s",
            type(error).__name__,
        )
        await message.answer("Не удалось загрузить заставку.")

    try:
        async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id,
        ):
            fact = await openai_service.generate_text(
                system_prompt=RANDOM_FACT_SYSTEM_PROMPT,
                user_prompt="Расскажи новый случайный факт.",
            )
    except OpenAIServiceError:
        await message.answer(
            "Не удалось получить факт от ChatGPT. "
            "Попробуйте ещё раз немного позже.",
            reply_markup=get_random_fact_keyboard(),
        )
        return

    await message.answer(
        fact,
        reply_markup=get_random_fact_keyboard(),
    )


@router.message(Command("random"))
@router.message(F.text == RANDOM_FACT_BUTTON_TEXT)
async def handle_random_fact(
    message: Message,
    openai_service: OpenAIService,
) -> None:
    await send_random_fact(message, openai_service)


@router.callback_query(F.data == "random:again")
async def handle_random_fact_again(
    callback: CallbackQuery,
    openai_service: OpenAIService,
) -> None:
    await callback.answer()
    if isinstance(callback.message, Message):
        await send_random_fact(callback.message, openai_service)
