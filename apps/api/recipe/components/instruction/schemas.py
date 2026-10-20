"""Request and response schemas for instructions."""

import uuid
from pydantic import BaseModel, model_validator, field_validator

from . import InstructionBase


class InstructionPublic(InstructionBase):
    """Instruction returned by the API.

    Attributes:
        id: The instruction's ID.
    """
    id: uuid.UUID


class InstructionCreate(InstructionBase):
    """Instruction fields used to insert a row.

    Attributes:
        recipe_id: ID of the recipe.
    """
    recipe_id: uuid.UUID


class InstructionUpdate(InstructionBase):
    """Partial update of an instruction. Only the fields sent are changed."""
    title: str | None = None
    details: str | None = None
    recipe_id: uuid.UUID | None = None


class NewInstructionCreate(BaseModel):
    """One step in the `NewRecipe` body.

    Attributes:
        id: Ignored on create.
        title: Short name of the step.
        details: Full text of the step.
    """
    id: uuid.UUID | None = None
    title: str
    details: str


class PatchInstruction(BaseModel):
    """One step in the `PatchRecipe` body.

    Send `id` to keep and update an existing step, or `new=True` without an
    `id` to add one.

    Attributes:
        id: ID of an existing step.
        title: Short name of the step.
        details: Full text of the step.
        new: True to create this step.
    """
    id: uuid.UUID | None = None
    title: str
    details: str
    new: bool = False

    @model_validator(mode="after")
    def validate_new_or_existing(self) -> "PatchInstruction":
        """Require exactly one of `id` or `new=True`."""
        has_id = self.id is not None
        is_new = self.new is True

        if has_id and is_new:
            raise ValueError("Provide either id (existing) or new=true (new instruction), not both.")
        if not is_new and not has_id:
            raise ValueError(
                "You have to provide at least one, either id (existing) or new=true (new instruction)."
            )

        return self
