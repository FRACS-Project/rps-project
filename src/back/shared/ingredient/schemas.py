##############################################################################################################
#
# Pydantic schemas for ingredient data validation and serialization.
#
# This module defines the various schemas used for creating, updating, and
# returning ingredient data through the API endpoints.
#
##############################################################################################################

from pydantic import field_validator
import re
import uuid
from . import IngredientBase


class IngredientSchemaBase(IngredientBase):

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[a-zA-ZÀ-ÿ'\-\s]+$", v):
            raise ValueError("Name must only contain letters and spaces")
        return v


class IngredientPublic(IngredientBase):
    """Schema for publicly viewable ingredient data.
    
    Attributes:
        id (UUID): The ingredient's unique identifier.
        name (str): The ingredient name.
        type (IngredientType): The ingredient type.
    """
    id: uuid.UUID


class IngredientCreate(IngredientSchemaBase):
    """Schema for creating a new ingredient.
    
    Inherits all base ingredient fields that are required for creation.
    """
    pass


class IngredientUpdate(IngredientSchemaBase):
    """Schema for updating ingredient data.
    
    All fields are optional to allow partial updates.
    
    Attributes:
        name (str, optional): The updated ingredient name.
        type (IngredientType, optional): The updated ingredient type.
    """
    name: str | None = None
