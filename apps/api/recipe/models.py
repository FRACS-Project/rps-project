"""Recipe table model."""

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
    """Fields shared by the recipe table and its schemas.

    Attributes:
        name: Recipe name, unique per owner.
        preparation_time: Preparation time in minutes.
        cooking_time: Cooking time in minutes.
        description: Free text description.
        base_serving: Number of servings the quantities are written for.
    """
    name: str
    preparation_time: int = 0
    cooking_time: int = 0
    description: str = ""
    base_serving: int = 0


class Recipe(RecipeBase, table=True):
    """Recipe table.

    Deleting a recipe also deletes its ingredient links, instructions and
    images. Tags are linked through `RecipeTag` and are not deleted.

    Attributes:
        id: Primary key.
        date_created: Creation time (UTC).
        owner_id: ID of the user who owns the recipe.
        owner: The user who owns the recipe.
        ingredients: Ingredient lines (quantity, unit, ingredient).
        instructions: Preparation steps.
        tags: Tags attached to the recipe.
        images: Images attached to the recipe.
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