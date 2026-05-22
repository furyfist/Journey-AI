import json

from pydantic import TypeAdapter, ValidationError

from app.common.logger import get_logger
from app.planning.agents.base_agent import BaseAgent
from app.planning.prompt_builder import critic_system_prompt, critic_user_message
from app.planning.schemas import Conflict, ItinerarySchema, ResearchBundle

logger = get_logger(__name__)

_conflict_list = TypeAdapter(list[Conflict])


class CriticAgent(BaseAgent):
    name = "critic"
    tools = []  # no tool calls — pure reasoning

    async def run_critique(
        self,
        itinerary: ItinerarySchema,
        pre_conflicts: list[Conflict],
        research: ResearchBundle,
    ) -> list[Conflict]:
        """
        Review the itinerary and return any additional Conflict objects found by the LLM.
        Never raises — returns [] on any failure so the pipeline keeps moving.
        """
        user_msg = critic_user_message(itinerary, pre_conflicts, research)
        try:
            raw = await self.run(
                user_message=user_msg,
                system_prompt=critic_system_prompt(),
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            logger.warning("critic LLM call failed, skipping: %s", exc)
            return []

        try:
            data = json.loads(raw)
            llm_conflicts = _conflict_list.validate_python(data.get("conflicts", []))
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.warning("critic returned unparseable output: %s", exc)
            return []

        logger.info("critic found %d additional conflicts", len(llm_conflicts))
        return llm_conflicts
