##############################################################################################################
#
# Database models for ingredient management.
#
# This module defines the SQLModel classes for ingredient data persistence,
# including base ingredient information and the complete ingredient model.
#
##############################################################################################################

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
    """Base model for ingredient information.
    
    Attributes:
        name (str): The ingredient name.
        type (IngredientType): The category type of the ingredient.
    """
    name: str
    # type: IngredientType


class Ingredient(IngredientBase, table=True):
    """Complete ingredient model for database storage.
    
    Extends IngredientBase to include a unique identifier.
    
    Attributes:
        id (UUID): Unique identifier for the ingredient.
        name (str): The ingredient name.
        type (IngredientType): The category type of the ingredient.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)