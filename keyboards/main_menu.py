from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


MENU_BUTTON_TEXTS = (
    "🎲 Случайный факт",
    "💬 Спросить GPT",
    "🎭 Поговорить",
    "🧠 Квиз",
    "🌐 Переводчик",
    "📄 Помощь с резюме",
    "🖼 Распознать изображение",
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=MENU_BUTTON_TEXTS[0]),
            KeyboardButton(text=MENU_BUTTON_TEXTS[1]),
        ],
        [
            KeyboardButton(text=MENU_BUTTON_TEXTS[2]),
            KeyboardButton(text=MENU_BUTTON_TEXTS[3]),
        ],
        [
            KeyboardButton(text=MENU_BUTTON_TEXTS[4]),
            KeyboardButton(text=MENU_BUTTON_TEXTS[5]),
        ],
        [KeyboardButton(text=MENU_BUTTON_TEXTS[6])],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)
