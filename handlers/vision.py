import logging
from io import BytesIO
from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

from keyboards.vision import VISION_BUTTON_TEXT, get_vision_exit_keyboard
from prompts import VISION_SYSTEM_PROMPT
from services.openai_service import (
    MAX_IMAGE_SIZE_BYTES,
    SUPPORTED_IMAGE_MIME_TYPES,
    OpenAIService,
    OpenAIServiceError,
)
from states.vision import VisionStates
from utils.messages import split_message

logger = logging.getLogger(__name__)
router = Router(name=__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VISION_IMAGE_PATH = PROJECT_ROOT / "assets" / "vision.png"


async def start_vision(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(VisionStates.waiting_for_image)

    try:
        if not VISION_IMAGE_PATH.is_file():
            raise FileNotFoundError
        await message.answer_photo(FSInputFile(VISION_IMAGE_PATH))
    except (OSError, TelegramAPIError) as error:
        logger.error(
            "Не удалось отправить заставку распознавания изображений: %s",
            type(error).__name__,
        )

    await message.answer(
        "Отправьте фотографию, и бот опишет, что на ней изображено.\n\n"
        "После получения результата можно отправить ещё одно изображение.",
        reply_markup=get_vision_exit_keyboard(),
    )


@router.message(Command("vision"))
@router.message(F.text == VISION_BUTTON_TEXT)
async def handle_vision_start(message: Message, state: FSMContext) -> None:
    await start_vision(message, state)


async def analyze_telegram_image(
    message: Message,
    openai_service: OpenAIService,
    file_id: str,
    mime_type: str,
    file_size: int | None,
) -> None:
    if mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
        await send_unsupported_image_message(message)
        return

    if file_size is not None and file_size > MAX_IMAGE_SIZE_BYTES:
        await send_image_too_large_message(message)
        return

    try:
        with BytesIO() as image_buffer:
            await message.bot.download(file_id, destination=image_buffer)
            image_bytes = image_buffer.getvalue()
    except (OSError, TelegramAPIError) as error:
        logger.error(
            "Ошибка загрузки изображения из Telegram: %s",
            type(error).__name__,
        )
        await message.answer(
            "Не удалось загрузить изображение из Telegram. Попробуйте "
            "отправить его ещё раз.",
            reply_markup=get_vision_exit_keyboard(),
        )
        return

    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        await send_image_too_large_message(message)
        return

    try:
        async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id,
        ):
            description = await openai_service.analyze_image(
                image_bytes=image_bytes,
                mime_type=mime_type,
                prompt=VISION_SYSTEM_PROMPT,
            )
    except OpenAIServiceError:
        await message.answer(
            "Не удалось распознать изображение. Попробуйте отправить его "
            "ещё раз немного позже.",
            reply_markup=get_vision_exit_keyboard(),
        )
        return

    description_parts = split_message(description)
    for index, part in enumerate(description_parts):
        is_last_part = index == len(description_parts) - 1
        await message.answer(
            part,
            reply_markup=(
                get_vision_exit_keyboard() if is_last_part else None
            ),
        )


@router.message(VisionStates.waiting_for_image, F.photo)
async def handle_vision_photo(
    message: Message,
    openai_service: OpenAIService,
) -> None:
    photo = message.photo[-1]
    await analyze_telegram_image(
        message=message,
        openai_service=openai_service,
        file_id=photo.file_id,
        mime_type="image/jpeg",
        file_size=photo.file_size,
    )


@router.message(VisionStates.waiting_for_image, F.document)
async def handle_vision_document(
    message: Message,
    openai_service: OpenAIService,
) -> None:
    document = message.document
    mime_type = document.mime_type or ""
    if not mime_type.startswith("image/"):
        await message.answer(
            "Отправьте фотографию или файл изображения в формате JPG, PNG "
            "или WEBP.",
            reply_markup=get_vision_exit_keyboard(),
        )
        return

    await analyze_telegram_image(
        message=message,
        openai_service=openai_service,
        file_id=document.file_id,
        mime_type=mime_type,
        file_size=document.file_size,
    )


async def send_unsupported_image_message(message: Message) -> None:
    await message.answer(
        "Отправьте фотографию или файл изображения в формате JPG, PNG или "
        "WEBP.",
        reply_markup=get_vision_exit_keyboard(),
    )


async def send_image_too_large_message(message: Message) -> None:
    await message.answer(
        "Изображение слишком большое. Отправьте файл размером не более 10 МБ.",
        reply_markup=get_vision_exit_keyboard(),
    )


@router.message(
    VisionStates.waiting_for_image,
    F.text,
    ~F.text.startswith("/"),
)
@router.message(VisionStates.waiting_for_image, ~F.text)
async def handle_vision_unsupported_message(message: Message) -> None:
    await message.answer(
        "В этом режиме отправьте фотографию или файл изображения JPG, PNG "
        "или WEBP.",
        reply_markup=get_vision_exit_keyboard(),
    )
