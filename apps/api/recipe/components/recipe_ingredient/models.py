"""Recipe ingredient table model: one ingredient line of a recipe, with quantity and unit."""

import uuid
from enum import Enum
from typing import TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field

from ....shared.ingredient import Ingredient

if TYPE_CHECKING:
    from recipe.models import Recipe


class Unit(str, Enum):
    """Units allowed for an ingredient quantity."""
    ML = "ml"
    CL = "cl"
    L = "l"
    G = "g"
    KG = "kg"
    PIECE = "piece"
    SPOON = "spoon"
    PINCH = "pinch"


class RecipeIngredientBase(SQLModel):
    """Fields shared by the recipe ingredient table and its schemas.

    Attributes:
        quantity: Amount of the ingredient, for the recipe's `base_serving`.
        unit: Unit of the quantity; None for plain counts.
        ingredient_id: ID of the ingredient.
        recipe_id: ID of the recipe.
    """
    quantity: float
    unit: Unit | None = None

    ingredient_id: uuid.UUID = Field(foreign_key="ingredient.id")
    recipe_id: uuid.UUID = Field(foreign_key="recipe.id", ondelete="CASCADE")


class RecipeIngredient(RecipeIngredientBase, table=True):
    """Recipe ingredient table. Deleted with its recipe.

    Attributes:
        id: Primary key.
        recipe: The recipe this line belongs to.
        ingredient: The ingredient used.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    recipe: "Recipe" = Relationship(back_populates="ingredients")
    ingredient: Ingredient = Relationship()
