from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


TRANSLATOR_BUTTON_TEXT = "🌐 Переводчик"


def get_translator_languages_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Английский",
                    callback_data="translate:language:english",
                ),
                InlineKeyboardButton(
                    text="Русский",
                    callback_data="translate:language:russian",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Немецкий",
                    callback_data="translate:language:german",
                ),
                InlineKeyboardButton(
                    text="Испанский",
                    callback_data="translate:language:spanish",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Французский",
                    callback_data="translate:language:french",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Закончить",
                    callback_data="common:finish",
                )
            ],
        ]
    )


def get_translator_actions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Сменить язык",
                    callback_data="translate:change_language",
                ),
                InlineKeyboardButton(
                    text="Закончить",
                    callback_data="common:finish",
                ),
            ]
        ]
    )
