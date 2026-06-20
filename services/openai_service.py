import base64
import json
import logging

from openai import AsyncOpenAI, OpenAIError


logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_MIME_TYPES = frozenset(
    {"image/jpeg", "image/png", "image/webp"}
)
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024


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

    async def analyze_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
    ) -> str:
        if not image_bytes:
            raise OpenAIServiceError("Получено пустое изображение.")
        if mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
            raise OpenAIServiceError("Неподдерживаемый формат изображения.")
        if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
            raise OpenAIServiceError("Изображение превышает допустимый размер.")

        encoded_image = base64.b64encode(image_bytes).decode("ascii")
        data_url = f"data:{mime_type};base64,{encoded_image}"

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Опиши содержимое этого изображения.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url},
                            },
                        ],
                    },
                ],
                timeout=60.0,
            )
        except OpenAIError as error:
            logger.error(
                "Ошибка анализа изображения через OpenAI: %s",
                type(error).__name__,
            )
            raise OpenAIServiceError(
                "Не удалось проанализировать изображение."
            ) from error

        if not response.choices:
            raise OpenAIServiceError("OpenAI вернул ответ без вариантов.")

        content = response.choices[0].message.content
        if not content or not content.strip():
            raise OpenAIServiceError("OpenAI вернул пустой ответ.")

        return content.strip()

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
