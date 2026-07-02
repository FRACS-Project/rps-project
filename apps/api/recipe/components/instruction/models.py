##############################################################################################################
#
# Database models for instruction management.
#
# This module defines the SQLModel classes for instruction data persistence,
# including base instruction information and the complete instruction model.
#
##############################################################################################################

from typing import TYPE_CHECKING
import uuid
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from recipe.models import Recipe


class InstructionBase(SQLModel):
    """Base model for instruction information.
    
    Attributes:
        title (str): The instruction title or step name.
        details (str): Detailed description of the instruction.
    """
    title: str
    details: str


class Instruction(InstructionBase, table=True):
    """Complete instruction model for database storage.
    
    Extends InstructionBase to include:
    - Unique identifier
    - Relationship to recipe
    
    Attributes:
        id (UUID): Unique identifier for the instruction.
        title (str): The instruction title or step name.
        details (str): Detailed description of the instruction.
        recipe_id (UUID): Foreign key reference to the recipe.
        recipe (Recipe): Related recipe object.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    recipe_id: uuid.UUID = Field(foreign_key="recipe.id", ondelete="CASCADE")
    recipe: "Recipe" = Relationship(back_populates="instructions")

