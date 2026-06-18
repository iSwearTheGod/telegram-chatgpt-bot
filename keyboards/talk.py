from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


TALK_BUTTON_TEXT = "🎭 Поговорить"


def get_personality_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Альберт Эйнштейн",
                    callback_data="talk:person:einstein",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Уильям Шекспир",
                    callback_data="talk:person:shakespeare",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Леонардо да Винчи",
                    callback_data="talk:person:da_vinci",
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


def get_talk_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Сменить личность",
                    callback_data="talk:change",
                ),
                InlineKeyboardButton(
                    text="Закончить",
                    callback_data="common:finish",
                ),
            ]
        ]
    )
