import json

from pydantic import ValidationError

from app.common.logger import get_logger
from app.core.exceptions import SchemaValidationError
from app.planning.agents.base_agent import BaseAgent
from app.planning.prompt_builder import (
    regen_block_system_prompt,
    regen_block_user_message,
    regen_day_system_prompt,
    regen_day_user_message,
)
from app.planning.schemas import DayPlan, ItinerarySchema, ResearchBundle, TimeBlock

logger = get_logger(__name__)


class DayRegenerationAgent(BaseAgent):
    """Regenerates a single DayPlan given the existing itinerary context."""

    name = "day_regenerator"
    tools = []

    async def regenerate_day(
        self,
        day_number: int,
        itinerary: ItinerarySchema,
        research: ResearchBundle,
        constraint: str | None = None,
    ) -> DayPlan:
        user_msg = regen_day_user_message(day_number, itinerary, research, constraint)
        raw = await self.run(
            user_message=user_msg,
            system_prompt=regen_day_system_prompt(),
            response_format={"type": "json_object"},
        )
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SchemaValidationError(f"Day regenerator returned invalid JSON: {exc}") from exc
        try:
            return DayPlan.model_validate(data)
        except ValidationError as exc:
            raise SchemaValidationError(f"Regenerated day failed schema validation: {exc}") from exc


class BlockRegenerationAgent(BaseAgent):
    """Regenerates a single TimeBlock given the existing day context."""

    name = "block_regenerator"
    tools = []

    async def regenerate_block(
        self,
        day_number: int,
        block_label: str,
        itinerary: ItinerarySchema,
        research: ResearchBundle,
        constraint: str | None = None,
    ) -> TimeBlock:
        user_msg = regen_block_user_message(day_number, block_label, itinerary, research, constraint)
        raw = await self.run(
            user_message=user_msg,
            system_prompt=regen_block_system_prompt(),
            response_format={"type": "json_object"},
        )
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SchemaValidationError(f"Block regenerator returned invalid JSON: {exc}") from exc
        try:
            return TimeBlock.model_validate(data)
        except ValidationError as exc:
            raise SchemaValidationError(f"Regenerated block failed schema validation: {exc}") from exc
