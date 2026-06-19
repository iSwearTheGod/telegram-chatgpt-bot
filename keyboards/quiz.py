from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


QUIZ_BUTTON_TEXT = "🧠 Квиз"


def get_quiz_topics_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Python",
                    callback_data="quiz:topic:python",
                ),
                InlineKeyboardButton(
                    text="История",
                    callback_data="quiz:topic:history",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="География",
                    callback_data="quiz:topic:geography",
                ),
                InlineKeyboardButton(
                    text="Кино",
                    callback_data="quiz:topic:movies",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Закончить",
                    callback_data="common:finish",
                )
            ],
        ]
    )


def get_quiz_exit_keyboard() -> InlineKeyboardMarkup:
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


def get_quiz_result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ещё вопрос",
                    callback_data="quiz:again",
                ),
                InlineKeyboardButton(
                    text="Сменить тему",
                    callback_data="quiz:change_topic",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Закончить",
                    callback_data="common:finish",
                )
            ],
        ]
    )
