"""Ingredient table model. Ingredients are shared by all users and recipes."""

import uuid
from sqlmodel import SQLModel, Field


# class IngredientType(str, Enum):
#     """Enumeration of ingredient types.
    
#     Defines the three categories of ingredients based on their physical state
#     and measurement units:
#     - LIQUID: Measured in ml, cl, or l
#     - SOLID: Measured in g or kg
#     - UNIT: Measured in pieces, spoons, or pinches
#     """
#     LIQUID = "liquid"
#     SOLID = "solid"
#     UNIT = "unit"


class IngredientBase(SQLModel):
    """Fields shared by the ingredient table and its schemas.

    Attributes:
        name: Ingredient name.
    """
    name: str
    # type: IngredientType


class Ingredient(IngredientBase, table=True):
    """Ingredient table.

    Attributes:
        id: Primary key.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)