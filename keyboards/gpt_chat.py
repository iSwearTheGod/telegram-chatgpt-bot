from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_gpt_chat_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Закончить",
                    callback_data="common:finish",
                )
            ]
        ]
    )
