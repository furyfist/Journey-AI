import asyncio
import json
from typing import Any, Optional

import openai

from app.common.logger import get_logger
from app.core.config import settings
from app.core.exceptions import GroqAPIError

logger = get_logger(__name__)

_MAX_TOOL_ITERATIONS = 8


class BaseAgent:
    """
    Shared Groq interaction layer.
    Handles the full tool-call loop: send → get tool_calls → execute → send results → repeat.
    Subclasses implement _execute_tool() and set self.tools.
    """

    name: str = "base"
    tools: list[dict] = []

    def __init__(self, http=None):
        self._http = http
        self._groq = openai.AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )

    async def _execute_tool(self, tool_name: str, args: dict) -> Any:
        raise NotImplementedError(f"{self.name} has no handler for tool '{tool_name}'")

    async def run(
        self,
        user_message: str,
        system_prompt: str,
        response_format: Optional[dict] = None,
        model: Optional[str] = None,
    ) -> str:
        chosen_model = model or settings.groq_model
        messages: list[dict] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        kwargs: dict = {
            "model": chosen_model,
            "messages": messages,
            "max_tokens": settings.groq_max_tokens,
            "temperature": settings.groq_temperature,
        }
        if self.tools:
            kwargs["tools"] = self.tools
            kwargs["tool_choice"] = "auto"
        if response_format:
            kwargs["response_format"] = response_format

        last_exc: Exception = RuntimeError("no attempts made")
        for attempt in range(3):
            try:
                return await self._tool_loop(kwargs, list(messages))
            except openai.RateLimitError as exc:
                raise GroqAPIError("Groq rate limit exceeded") from exc
            except openai.APIStatusError as exc:
                last_exc = exc
                if attempt == 1:
                    kwargs["model"] = settings.groq_fallback_model
                if attempt < 2:
                    await asyncio.sleep(2**attempt)
            except GroqAPIError:
                raise
            except Exception as exc:
                last_exc = exc
                if attempt < 2:
                    await asyncio.sleep(2**attempt)

        raise GroqAPIError(f"Groq call failed after retries: {last_exc}") from last_exc

    async def _tool_loop(self, kwargs: dict, messages: list[dict]) -> str:
        for _ in range(_MAX_TOOL_ITERATIONS):
            response = await self._groq.chat.completions.create(**kwargs)
            msg = response.choices[0].message

            if not msg.tool_calls:
                return msg.content or ""

            # Append assistant turn with tool_calls
            assistant_turn: dict = {"role": "assistant", "content": msg.content}
            if msg.tool_calls:
                assistant_turn["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ]
            messages.append(assistant_turn)

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}

                logger.info("agent=%s tool=%s args=%s", self.name, tool_name, args)
                try:
                    result = await self._execute_tool(tool_name, args)
                    content = json.dumps(result, default=str)
                except Exception as exc:
                    content = json.dumps({"error": str(exc)})

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": content,
                    }
                )

            kwargs["messages"] = messages

        raise GroqAPIError("Tool-call loop exceeded maximum iterations")
