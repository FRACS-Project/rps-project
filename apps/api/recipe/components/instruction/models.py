"""Instruction table model: the preparation steps of a recipe."""

from typing import TYPE_CHECKING
import uuid
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from recipe.models import Recipe


class InstructionBase(SQLModel):
    """Fields shared by the instruction table and its schemas.

    Attributes:
        title: Short name of the step.
        details: Full text of the step.
    """
    title: str
    details: str


class Instruction(InstructionBase, table=True):
    """Instruction table. Deleted with its recipe.

    Attributes:
        id: Primary key.
        recipe_id: ID of the recipe.
        recipe: The recipe this step belongs to.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    recipe_id: uuid.UUID = Field(foreign_key="recipe.id", ondelete="CASCADE")
    recipe: "Recipe" = Relationship(back_populates="instructions")

