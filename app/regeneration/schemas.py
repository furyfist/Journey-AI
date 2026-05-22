from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class RegenerateScope(str, Enum):
    full_trip = "full_trip"
    day = "day"
    single_block = "single_block"


class RegenerateRequest(BaseModel):
    scope: RegenerateScope
    day_number: Optional[int] = Field(
        default=None, ge=1, le=30,
        description="Required for scope=day or single_block",
    )
    block_label: Optional[Literal["morning", "afternoon", "evening"]] = Field(
        default=None,
        description="Required for scope=single_block",
    )
    constraint: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Natural language constraint e.g. 'make it vegetarian', 'avoid museums'",
    )

    @model_validator(mode="after")
    def _validate_scope_fields(self) -> "RegenerateRequest":
        if self.scope == RegenerateScope.day and self.day_number is None:
            raise ValueError("day_number is required when scope is 'day'")
        if self.scope == RegenerateScope.single_block:
            if self.day_number is None:
                raise ValueError("day_number is required when scope is 'single_block'")
            if self.block_label is None:
                raise ValueError("block_label is required when scope is 'single_block'")
        return self
