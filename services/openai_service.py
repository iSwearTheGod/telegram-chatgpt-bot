import json
import logging

from openai import AsyncOpenAI, OpenAIError


logger = logging.getLogger(__name__)


class OpenAIServiceError(Exception):
    """Ошибка при получении ответа от OpenAI."""


class OpenAIService:
    def __init__(self, api_key: str, model: str) -> None:
        self._model = model
        self._client = AsyncOpenAI(api_key=api_key, timeout=30.0)

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        return await self.chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )

    async def chat(self, messages: list[dict[str, str]]) -> str:
        request_messages = [message.copy() for message in messages]

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=request_messages,
            )
        except OpenAIError as error:
            logger.error(
                "Ошибка запроса к OpenAI: %s",
                type(error).__name__,
            )
            raise OpenAIServiceError(
                "Не удалось получить ответ от OpenAI."
            ) from error

        if not response.choices:
            raise OpenAIServiceError("OpenAI вернул ответ без вариантов.")

        content = response.choices[0].message.content
        if not content or not content.strip():
            raise OpenAIServiceError("OpenAI вернул пустой ответ.")

        return content.strip()

    async def chat_json(
        self,
        messages: list[dict[str, str]],
    ) -> dict[str, object]:
        request_messages = [message.copy() for message in messages]

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=request_messages,
                response_format={"type": "json_object"},
            )
        except OpenAIError as error:
            logger.error(
                "Ошибка JSON-запроса к OpenAI: %s",
                type(error).__name__,
            )
            raise OpenAIServiceError(
                "Не удалось получить JSON-ответ от OpenAI."
            ) from error

        if not response.choices:
            raise OpenAIServiceError("OpenAI вернул ответ без вариантов.")

        content = response.choices[0].message.content
        if not content or not content.strip():
            raise OpenAIServiceError("OpenAI вернул пустой ответ.")

        try:
            data = json.loads(content)
        except json.JSONDecodeError as error:
            logger.error(
                "OpenAI вернул некорректный JSON: %s",
                type(error).__name__,
            )
            raise OpenAIServiceError(
                "OpenAI вернул некорректный JSON."
            ) from error

        if not isinstance(data, dict):
            logger.error("JSON-ответ OpenAI не является объектом.")
            raise OpenAIServiceError(
                "JSON-ответ OpenAI не является объектом."
            )

        return data
