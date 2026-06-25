##############################################################################################################
#
# Pydantic schemas for recipe-ingredient data validation and serialization.
#
# This module defines the various schemas used for creating, updating, and
# returning recipe-ingredient data through the API endpoints.
#
##############################################################################################################

from typing import TYPE_CHECKING, Optional
import uuid, re
from pydantic import BaseModel, field_validator, model_validator

from .models import RecipeIngredientBase, Unit

from ....shared.ingredient.schemas import IngredientPublic


class RecipeIngredientPublic(BaseModel):
    """Schema for publicly viewable recipe-ingredient data.
    
    Attributes:
        id (UUID): The recipe-ingredient relationship's unique identifier.
        quantity (int): The quantity of the ingredient required.
        unit (Optional[Unit]): The unit of measurement for the quantity.
    """
    id: uuid.UUID
    quantity: int
    unit: Unit | None = None


class RecipeIngredientCreate(RecipeIngredientBase):
    """Schema for creating a recipe-ingredient relationship.
    
    Inherits base recipe-ingredient fields with custom validation for unit types.
    """
    pass
    

class RecipeIngredientUpdate(RecipeIngredientBase):
    """Schema for updating recipe-ingredient relationship data.
    
    All fields are optional to allow partial updates.
    
    Attributes:
        name (str, optional): The ingredient name (if updating).
        quantity (int, optional): The updated quantity.
        unit (Optional[Unit], optional): The updated unit of measurement.
        ingredient_id (Optional[UUID], optional): The updated ingredient reference.
        recipe_id (UUID): The recipe reference for the relationship.
    """
    unit: Unit | None = None
    quantity: int | None = None

    ingredient_id: uuid.UUID | None = None
    recipe_id: uuid.UUID | None = None


class RecipeIngredientPublicWithAll(RecipeIngredientPublic):
    """Extended recipe-ingredient schema including the full ingredient data.
    
    Extends RecipeIngredientPublic to include nested ingredient information.
    
    Attributes:
        id (UUID): The recipe-ingredient relationship's unique identifier.
        quantity (int): The quantity of the ingredient required.
        unit (Optional[Unit]): The unit of measurement for the quantity.
        ingredient (Optional[IngredientPublic]): The complete ingredient information.
    """
    ingredient: IngredientPublic | None = None


class NewRecipeIngredient(BaseModel):
    """Schema for adding a recipe ingredient using an existing or new ingredient.

    Attributes:
        ingredient_id (UUID, optional): Existing ingredient identifier.
        name (str, optional): New ingredient name.
        new (IngredientType, optional): New ingredient type.
        quantity (float): Quantity of the ingredient.
        unit (Unit, optional): Unit of measurement for the quantity.
    """
    ingredient_id: uuid.UUID | None = None
    name: str | None = None
    quantity: float
    unit: Unit
    new: bool = False

    @model_validator(mode="after")
    def validate_existing_or_new(self):
        has_id = self.ingredient_id is not None
        has_name = self.name is not None
        is_new = self.new is True
        
        if has_id and is_new:
            raise ValueError("Provide either ingredient_id (existing ingredient) or new=true (new ingredient), not both.")
        if is_new and not has_name:
            raise ValueError("When new=true, name is required.")
        if not is_new and not has_id:
            raise ValueError("When new=false, id is required.")
        if has_id and has_name:
            raise ValueError("When id provided, don't provide name.")

        return self
    

class PatchRecipeIngredient(BaseModel):
    """Schema for modifying a recipe ingredient using an existing or new ingredient.

    Attributes:
        ingredient_id (UUID, optional): Existing ingredient identifier.
        name (str, optional): New ingredient name.
        new (IngredientType, optional): New ingredient type.
        quantity (float): Quantity of the ingredient.
        unit (Unit, optional): Unit of measurement for the quantity.
    """
    ingredient_id: uuid.UUID | None = None
    name: str | None = None
    quantity: float | None = None
    unit: Unit | None = None
    new: bool = False
    recipe_ingredient_id: uuid.UUID | None = None

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip().lower()
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", v):
            raise ValueError("Name must only contain letters and spaces")
        return v
    
    @model_validator(mode="after")
    def validate_id_or_name(self) -> "PatchRecipeIngredient":
        has_id = self.ingredient_id is not None
        has_name = self.name is not None
        is_new = self.new is True
        has_recipe_ingredient_id = self.recipe_ingredient_id is not None

        if has_id and is_new:
            raise ValueError("Provide either ingredient_id (existing ingredient) or new=true (new ingredient), not both.")
        if is_new and not has_name:
            raise ValueError("When new=true, name is required.")
        if not is_new and has_name:
            raise ValueError("When new=false, name is not allowed. Use ingredient_id or set new=true.")
        if not is_new and not has_id and not has_recipe_ingredient_id:
            raise ValueError("When new=false, provide ingredient_id or recipe_ingredient_id.")

        return self