import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import load_config
from handlers.common import router as common_router
from handlers.gpt_chat import router as gpt_chat_router
from handlers.quiz import router as quiz_router
from handlers.random_fact import router as random_fact_router
from handlers.talk import router as talk_router
from services.openai_service import OpenAIService


async def set_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Открыть главное меню"),
        BotCommand(command="help", description="Помощь по командам"),
        BotCommand(command="random", description="Получить случайный факт"),
        BotCommand(command="gpt", description="Задать вопрос ChatGPT"),
        BotCommand(
            command="talk",
            description="Поговорить с известной личностью",
        ),
        BotCommand(command="quiz", description="Начать квиз"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    config = load_config()
    bot = Bot(token=config.telegram_bot_token)
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher["openai_service"] = OpenAIService(
        api_key=config.openai_api_key,
        model=config.openai_model,
    )
    dispatcher.include_router(quiz_router)
    dispatcher.include_router(talk_router)
    dispatcher.include_router(gpt_chat_router)
    dispatcher.include_router(random_fact_router)
    dispatcher.include_router(common_router)

    try:
        await set_bot_commands(bot)
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен.")
