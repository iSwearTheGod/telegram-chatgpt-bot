from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_random_fact_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Хочу ещё факт",
                    callback_data="random:again",
                ),
                InlineKeyboardButton(
                    text="Закончить",
                    callback_data="common:finish",
                ),
            ]
        ]
    )
