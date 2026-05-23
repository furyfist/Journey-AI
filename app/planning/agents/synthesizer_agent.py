import json
from typing import Optional

from pydantic import ValidationError

from app.common.logger import get_logger
from app.core.exceptions import SchemaValidationError
from app.planning.agents.base_agent import BaseAgent
from app.planning.prompt_builder import synthesizer_system_prompt, synthesizer_user_message
from app.planning.schemas import ItinerarySchema, ResearchBundle

logger = get_logger(__name__)


class SynthesizerAgent(BaseAgent):
    name = "synthesizer"

    async def run_synthesis(
        self,
        prompt: str,
        research: ResearchBundle,
        persona_hint: Optional[str] = None,
        interests: Optional[list[str]] = None,
        constraints: Optional[list[str]] = None,
        travel_party: Optional[str] = None,
    ) -> ItinerarySchema:
        """Plan and convert research into a fully validated ItinerarySchema (absorbs planner)."""
        user_msg = synthesizer_user_message(
            prompt=prompt,
            research=research,
            persona_hint=persona_hint or research.persona_hint,
            interests=interests or research.interests,
            constraints=constraints or research.constraints,
            travel_party=travel_party or research.travel_party,
        )
        raw = await self.run(
            user_message=user_msg,
            system_prompt=synthesizer_system_prompt(),
            response_format={"type": "json_object"},
        )
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SchemaValidationError(f"Synthesizer returned invalid JSON: {exc}") from exc

        try:
            return ItinerarySchema.model_validate(data)
        except ValidationError as exc:
            logger.warning("SchemaValidationError rate check — synthesizer validation failed: %s", exc)
            raise SchemaValidationError(f"Itinerary failed schema validation: {exc}") from exc
