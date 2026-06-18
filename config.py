import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Config:
    telegram_bot_token: str
    openai_api_key: str
    openai_model: str


def _get_required_variable(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Обязательная переменная {name} не задана.")
    return value


def load_config() -> Config:
    load_dotenv()

    return Config(
        telegram_bot_token=_get_required_variable("TELEGRAM_BOT_TOKEN"),
        openai_api_key=_get_required_variable("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )
