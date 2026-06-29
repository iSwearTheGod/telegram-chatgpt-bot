import logging

from aiogram.types import ErrorEvent, Message

logger = logging.getLogger(__name__)

ERROR_MESSAGE = (
    "Произошла непредвиденная ошибка. Попробуйте повторить действие или "
    "вернитесь в меню командой /start."
)


async def handle_unexpected_error(event: ErrorEvent) -> bool:
    logger.error(
        "Непредвиденная ошибка обработчика: %s",
        type(event.exception).__name__,
    )

    message = event.update.message
    if message is None and event.update.callback_query is not None:
        callback_message = event.update.callback_query.message
        if isinstance(callback_message, Message):
            message = callback_message

    if message is not None:
        try:
            await message.answer(ERROR_MESSAGE)
        except Exception as error:
            logger.error(
                "Не удалось уведомить пользователя об ошибке: %s",
                type(error).__name__,
            )

    return True
