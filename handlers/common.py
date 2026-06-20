from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.main_menu import main_menu


router = Router(name=__name__)


async def show_main_menu(
    message: Message,
    first_name: str | None = None,
) -> None:
    if first_name:
        text = (
            f"Привет, {first_name}!\n\n"
            "Этот бот постепенно объединит полезные инструменты на основе ИИ. "
            "Выберите раздел в главном меню."
        )
    else:
        text = "Главное меню открыто. Выберите нужный раздел."

    await message.answer(text, reply_markup=main_menu)


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()

    first_name = message.from_user.first_name if message.from_user else None
    await show_main_menu(message, first_name)


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "Доступные команды:\n"
        "/start — открыть главное меню\n"
        "/help — показать эту справку\n"
        "/random — получить случайный факт\n"
        "/gpt — задать вопрос ChatGPT\n"
        "/talk — поговорить с известной личностью\n"
        "/quiz — начать квиз\n"
        "/translate — перевести текст\n"
        "/resume — создать шаблон резюме\n"
        "/vision — распознать изображение\n\n"
        "Новые функции добавляются постепенно.",
        reply_markup=main_menu,
    )


@router.callback_query(F.data == "common:finish")
async def handle_finish(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await callback.answer()
    await state.clear()
    if isinstance(callback.message, Message):
        await show_main_menu(callback.message)
