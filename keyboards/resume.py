from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


RESUME_BUTTON_TEXT = "📄 Помощь с резюме"


def get_resume_exit_keyboard() -> InlineKeyboardMarkup:
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


def get_resume_result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Создать заново",
                    callback_data="resume:restart",
                ),
                InlineKeyboardButton(
                    text="Закончить",
                    callback_data="common:finish",
                ),
            ]
        ]
    )
