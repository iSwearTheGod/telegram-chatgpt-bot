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
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
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
