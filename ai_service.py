
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from config import settings


class AIServiceError(Exception):
    """Raised when the AI provider cannot complete a request."""


class AIService:
    """EnterpriseFlow AI service using OpenRouter-hosted LLMs."""

    def __init__(self) -> None:
        if not settings.openrouter_api_key:
            raise AIServiceError(
                "OPENROUTER_API_KEY is not configured."
            )

        if not settings.openrouter_model:
            raise AIServiceError(
                "OPENROUTER_MODEL is not configured."
            )

        self.llm = ChatOpenAI(
            model=settings.openrouter_model,
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=30.0,
            max_retries=0,
            max_tokens=500,
        )

    async def answer(
        self,
        question: str,
        context: str = "",
    ) -> str:
        """Generate an answer, grounding it in retrieved context when available."""

        if context.strip():
            instructions = (
                "You are EnterpriseFlow AI, an enterprise "
                "operations copilot. Answer the user's question "
                "using the retrieved document excerpts below. "
                "Do not invent policies, facts, or citations. "
                "If the excerpts do not contain the answer, "
                "say that the available documents do not provide "
                "enough information. Distinguish document facts "
                "from any inference.\n\n"
                "Retrieved excerpts:\n"
                f"{context}"
            )
        else:
            instructions = (
                "You are EnterpriseFlow AI, an enterprise "
                "operations copilot. No relevant uploaded "
                "document excerpts were retrieved. You may "
                "answer general questions, but clearly state "
                "that the answer is not grounded in the uploaded "
                "knowledge base. Never invent company policies."
            )

        try:
            response = await self.llm.ainvoke(
                [
                    SystemMessage(content=instructions),
                    HumanMessage(content=question),
                ]
            )

            answer = response.content

            if not isinstance(answer, str):
                answer = str(answer)

            answer = answer.strip()

            if not answer:
                raise AIServiceError(
                    "The AI provider returned an empty answer."
                )

            return answer

        except AIServiceError:
            raise

        except Exception as exc:
            # Do not expose provider details in API responses.
            raise AIServiceError(
                "The AI provider request failed."
            ) from exc
