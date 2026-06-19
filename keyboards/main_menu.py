from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from keyboards.quiz import QUIZ_BUTTON_TEXT
from keyboards.talk import TALK_BUTTON_TEXT


RANDOM_FACT_BUTTON_TEXT = "🎲 Случайный факт"
GPT_CHAT_BUTTON_TEXT = "💬 Спросить GPT"

MENU_BUTTON_TEXTS = (
    RANDOM_FACT_BUTTON_TEXT,
    GPT_CHAT_BUTTON_TEXT,
    TALK_BUTTON_TEXT,
    QUIZ_BUTTON_TEXT,
    "🌐 Переводчик",
    "📄 Помощь с резюме",
    "🖼 Распознать изображение",
)

UNAVAILABLE_MENU_BUTTON_TEXTS = MENU_BUTTON_TEXTS[4:]

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
