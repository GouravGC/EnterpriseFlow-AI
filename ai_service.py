import asyncio

from openai import AsyncOpenAI, APIError, APITimeoutError
from config import settings


class AIServiceError(Exception):
    """Raised when the AI provider cannot complete a request."""


class AIService:
    def __init__(self) -> None:
        if not settings.openrouter_api_key or not settings.openrouter_model:
            raise AIServiceError("OpenRouter configuration is missing.")

        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=30.0,
            max_retries=1,
        )
        self.model = settings.openrouter_model

    async def answer(self, question: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are EnterpriseFlow AI, an enterprise "
                            "operations assistant. Be accurate, concise, "
                            "and explicitly state when information is uncertain."
                        ),
                    },
                    {"role": "user", "content": question},
                ],
                max_tokens=500,
            )

            answer = response.choices[0].message.content
            if not answer:
                raise AIServiceError("The AI provider returned an empty answer.")

            return answer.strip()

        except APITimeoutError as exc:
            raise AIServiceError("The AI request timed out.") from exc
        except APIError as exc:
            raise AIServiceError("The AI provider request failed.") from exc

    async def close(self) -> None:
        await self.client.close()