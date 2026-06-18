from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


RANDOM_FACT_BUTTON_TEXT = "🎲 Случайный факт"
GPT_CHAT_BUTTON_TEXT = "💬 Спросить GPT"

MENU_BUTTON_TEXTS = (
    RANDOM_FACT_BUTTON_TEXT,
    GPT_CHAT_BUTTON_TEXT,
    "🎭 Поговорить",
    "🧠 Квиз",
    "🌐 Переводчик",
    "📄 Помощь с резюме",
    "🖼 Распознать изображение",
)

UNAVAILABLE_MENU_BUTTON_TEXTS = MENU_BUTTON_TEXTS[2:]

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
