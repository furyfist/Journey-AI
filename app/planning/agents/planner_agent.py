import json

from app.common.logger import get_logger
from app.core.exceptions import SchemaValidationError
from app.planning.agents.base_agent import BaseAgent
from app.planning.prompt_builder import planner_system_prompt, planner_user_message
from app.planning.schemas import ResearchBundle

logger = get_logger(__name__)


class PlannerAgent(BaseAgent):
    name = "planner"

    async def run_planning(self, prompt: str, research: ResearchBundle) -> dict:
        """Detect persona and produce a rough day-by-day plan. Returns a plain dict."""
        user_msg = planner_user_message(prompt, research)
        raw = await self.run(
            user_message=user_msg,
            system_prompt=planner_system_prompt(),
            response_format={"type": "json_object"},
        )
        try:
            plan = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SchemaValidationError(f"Planner returned invalid JSON: {exc}") from exc

        if "persona" not in plan or "days" not in plan:
            raise SchemaValidationError("Planner output missing required 'persona' or 'days' fields")

        return plan
