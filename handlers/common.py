from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.main_menu import MENU_BUTTON_TEXTS, main_menu


router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()

    first_name = message.from_user.first_name if message.from_user else None
    greeting = f"Привет, {first_name}!" if first_name else "Привет!"
    await message.answer(
        f"{greeting}\n\n"
        "Этот бот постепенно объединит полезные инструменты на основе ИИ. "
        "Выберите раздел в главном меню.",
        reply_markup=main_menu,
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "Доступные команды:\n"
        "/start — открыть главное меню\n"
        "/help — показать эту справку\n\n"
        "Новые функции добавляются постепенно.",
        reply_markup=main_menu,
    )


@router.message(F.text.in_(MENU_BUTTON_TEXTS))
async def handle_unavailable_menu_action(message: Message) -> None:
    await message.answer("Эта функция пока находится в разработке.")
