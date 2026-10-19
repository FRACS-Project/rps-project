##############################################################################################################
#
# Database models for recipe management.
#
# This module defines the SQLModel classes for recipe data persistence,
# including base recipe information and the complete recipe model with
# relationships to user, recipe ingredients and instructions.
#
##############################################################################################################

from typing import TYPE_CHECKING
import uuid
from sqlmodel import Relationship, SQLModel, Field
from datetime import datetime, timezone

from .components.recipe_tag.models import RecipeTag

if TYPE_CHECKING:
    from .components import RecipeIngredient
    from .components import Instruction
    from ..user import User
    from ..shared import Tag, Image


class RecipeBase(SQLModel):
    """Base model for recipe information.
    
    Attributes:
        name (str): The recipe name.
        preparation_time (int): Time in minutes to prepare the recipe. Defaults to 0.
        cooking_time (int): Time in minutes to cook the recipe. Defaults to 0.
        description (str): Detailed description of the recipe. Defaults to empty string.
    """
    name: str
    preparation_time: int = 0
    cooking_time: int = 0
    description: str = ""
    base_serving: int = 0


class Recipe(RecipeBase, table=True):
    """Complete recipe model for database storage.
    
    Extends RecipeBase to include:
    - Unique identifier
    - Creation timestamp
    - Relationship to user
    - Relationship to recipe ingredients
    - Relationship to recipe instructions
    
    Attributes:
        id (UUID): Unique identifier for the recipe.
        date_created (datetime): When the recipe was created.
        owner (User): The user who created the recipe.
        owner_id (UUID): Foreign key to the user.
        ingredients (list[RecipeIngredient]): The ingredients used in this recipe.
        instructions (list[Instruction]): The instructions for this recipe.
        tags (list[Tag]): The tags associated with this recipe.
        images (list[Image]): The images associated with this recipe.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    owner: "User" = Relationship(back_populates="recipes")
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    ingredients: list["RecipeIngredient"] = Relationship(back_populates="recipe", cascade_delete=True)
    instructions: list["Instruction"] = Relationship(back_populates="recipe", cascade_delete=True)
    tags: list["Tag"] = Relationship(
        back_populates="recipes",
        link_model=RecipeTag,
    )

    images: list["Image"] = Relationship(back_populates="recipe", cascade_delete=True)