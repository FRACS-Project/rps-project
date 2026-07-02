##############################################################################################################
#
# Pydantic schemas for instruction data validation and serialization.
#
# This module defines the various schemas used for creating, updating, and
# returning instruction data through the API endpoints.
#
##############################################################################################################

import uuid
from pydantic import BaseModel, model_validator, field_validator

from . import InstructionBase


class InstructionPublic(InstructionBase):
    """Schema for returning instruction data in API responses.

    Includes all base instruction fields plus the unique identifier.

    Attributes:
        id (uuid.UUID): The unique identifier for the instruction.
    """
    id: uuid.UUID


class InstructionCreate(InstructionBase):
    """Schema for creating a new instruction.

    Inherits all base instruction fields that are required for creation.

    Attributes:
        recipe_id (UUID): The recipe identifier for this instruction.
    """
    recipe_id: uuid.UUID


class InstructionUpdate(InstructionBase):
    """Schema for updating instruction data.

    All fields are optional to allow partial updates.

    Attributes:
        title (str, optional): The updated instruction title.
        details (str, optional): The updated instruction details.
        recipe_id (UUID, optional): The updated recipe reference.
    """
    title: str | None = None
    details: str | None = None
    recipe_id: uuid.UUID | None = None


class NewInstructionCreate(BaseModel):
    """Schema for creating a new instruction.

    Inherits all base instruction fields that are required for creation.
    """
    id: uuid.UUID | None = None
    title: str
    details: str


class PatchInstruction(BaseModel):
    id: uuid.UUID | None = None
    title: str
    details: str
    new: bool = False

    @model_validator(mode="after")
    def validate_new_or_existing(self) -> "PatchInstruction":
        has_id = self.id is not None
        is_new = self.new is True

        if has_id and is_new:
            raise ValueError("Provide either instruction_id (existing) or new=true (new instruction), not both.")
        if is_new and has_id:
            raise ValueError("When new=true, instruction_id must be absent.")
        if not is_new and not has_id:
            raise ValueError("When new=false, instruction_id is required.")

        return self
