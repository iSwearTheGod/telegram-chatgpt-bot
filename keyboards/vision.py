from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


VISION_BUTTON_TEXT = "🖼 Распознать изображение"


def get_vision_exit_keyboard() -> InlineKeyboardMarkup:
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
