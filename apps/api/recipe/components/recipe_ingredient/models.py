##############################################################################################################
#
# Database models for recipe-ingredient relationships.
#
# This module defines the SQLModel classes for recipe-ingredient junction table,
# including quantity and unit information for each recipe ingredient.
#
##############################################################################################################

import uuid
from enum import Enum
from typing import TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field

from ....shared.ingredient import Ingredient

if TYPE_CHECKING:
    from recipe.models import Recipe


class Unit(str, Enum):
    """Enumeration of measurement units for recipe ingredients.

    Defines various units of measurement:
    - Volume units: ML (milliliter), CL (centiliter), L (liter)
    - Mass units: G (gram), KG (kilogram)
    - Count units: PIECE, SPOON, PINCH
    """
    ML = "ml"
    CL = "cl"
    L = "l"
    G = "g"
    KG = "kg"
    PIECE = "piece"
    SPOON = "spoon"
    PINCH = "pinch"


class RecipeIngredientBase(SQLModel):
    """Base model for recipe-ingredient relationship.

    Attributes:
        quantity (float): The quantity of the ingredient required.
        unit (Optional[Unit]): The unit of measurement for the quantity.
        ingredient_id (UUID): Foreign key reference to the ingredient.
        recipe_id (UUID): Foreign key reference to the recipe.
    """
    quantity: float
    unit: Unit | None = None

    ingredient_id: uuid.UUID = Field(foreign_key="ingredient.id")
    recipe_id: uuid.UUID = Field(foreign_key="recipe.id", ondelete="CASCADE")


class RecipeIngredient(RecipeIngredientBase, table=True):
    """Complete recipe-ingredient model for database storage.

    Junction table linking recipes to ingredients with quantity and unit information.

    Extends RecipeIngredientBase to include:
    - Unique identifier
    - Relationships to recipe and ingredient

    Attributes:
        id (UUID): Unique identifier for this recipe-ingredient relationship.
        quantity (float): The quantity of the ingredient required.
        unit (Optional[Unit]): The unit of measurement for the quantity.
        ingredient_id (UUID): Foreign key reference to the ingredient.
        recipe_id (UUID): Foreign key reference to the recipe.
        recipe (Recipe): Related recipe object.
        ingredient (Ingredient): Related ingredient object.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    recipe: "Recipe" = Relationship(back_populates="ingredients")
    ingredient: Ingredient = Relationship()
