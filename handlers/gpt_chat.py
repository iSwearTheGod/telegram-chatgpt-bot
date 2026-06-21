import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

from keyboards.gpt_chat import get_gpt_chat_keyboard
from keyboards.main_menu import GPT_CHAT_BUTTON_TEXT
from prompts import GPT_CHAT_SYSTEM_PROMPT
from services.openai_service import OpenAIService, OpenAIServiceError
from states.gpt_chat import GPTChatStates
from utils.messages import split_message

logger = logging.getLogger(__name__)
router = Router(name=__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GPT_IMAGE_PATH = PROJECT_ROOT / "assets" / "gpt.png"
HISTORY_LIMIT = 12


async def start_gpt_chat(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(GPTChatStates.chatting)
    await state.update_data(history=[])

    try:
        if not GPT_IMAGE_PATH.is_file():
            raise FileNotFoundError
        await message.answer_photo(FSInputFile(GPT_IMAGE_PATH))
    except (OSError, TelegramAPIError) as error:
        logger.error(
            "Не удалось отправить заставку GPT-чата: %s",
            type(error).__name__,
        )

    await message.answer(
        "Режим ChatGPT запущен. Напишите свой вопрос.\n\n"
        "Бот будет учитывать несколько последних сообщений диалога.",
        reply_markup=get_gpt_chat_keyboard(),
    )


@router.message(Command("gpt"))
@router.message(F.text == GPT_CHAT_BUTTON_TEXT)
async def handle_gpt_chat_start(
    message: Message,
    state: FSMContext,
) -> None:
    await start_gpt_chat(message, state)


@router.message(
    GPTChatStates.chatting,
    F.text,
    ~F.text.startswith("/"),
)
async def handle_gpt_chat_message(
    message: Message,
    state: FSMContext,
    openai_service: OpenAIService,
) -> None:
    user_text = message.text
    if not user_text:
        return

    data = await state.get_data()
    history: list[dict[str, str]] = data.get("history", [])
    request_messages = [
        {"role": "system", "content": GPT_CHAT_SYSTEM_PROMPT},
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
            "Не удалось получить ответ от ChatGPT. Попробуйте отправить "
            "сообщение ещё раз немного позже.",
            reply_markup=get_gpt_chat_keyboard(),
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
            reply_markup=(
                get_gpt_chat_keyboard() if is_last_part else None
            ),
        )


@router.message(GPTChatStates.chatting, ~F.text)
async def handle_gpt_chat_non_text(message: Message) -> None:
    await message.answer(
        "В этом режиме отправьте текстовое сообщение.",
        reply_markup=get_gpt_chat_keyboard(),
    )
