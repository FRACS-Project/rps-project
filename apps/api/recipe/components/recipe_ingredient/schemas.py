"""Request and response schemas for recipe ingredients."""

from typing import TYPE_CHECKING, Optional
import uuid, re
from pydantic import BaseModel, field_validator, model_validator

from .models import RecipeIngredientBase, Unit

from ....shared.ingredient.schemas import IngredientPublic


class RecipeIngredientPublic(BaseModel):
    """Recipe ingredient line returned by the API, without the ingredient.

    Attributes:
        id: ID of the line.
        quantity: Amount of the ingredient.
        unit: Unit of the quantity.
    """
    id: uuid.UUID
    quantity: float
    unit: Unit | None = None


class RecipeIngredientCreate(RecipeIngredientBase):
    """Recipe ingredient fields used to insert a row."""
    pass
    

class RecipeIngredientUpdate(RecipeIngredientBase):
    """Partial update of a recipe ingredient line. Only the fields sent are changed.

    Attributes:
        quantity: New amount. Typed `int`, unlike the float on the model.
    """
    unit: Unit | None = None
    quantity: int | None = None

    ingredient_id: uuid.UUID | None = None
    recipe_id: uuid.UUID | None = None


class RecipeIngredientPublicWithAll(RecipeIngredientPublic):
    """Recipe ingredient line returned with its ingredient.

    Attributes:
        ingredient: The ingredient used.
    """
    ingredient: IngredientPublic | None = None


class NewRecipeIngredient(BaseModel):
    """One ingredient line in the `NewRecipe` body.

    Send either `ingredient_id` for an existing ingredient, or `new=True` and
    a `name` to create one.

    Attributes:
        ingredient_id: ID of an existing ingredient.
        name: Name of the ingredient to create.
        quantity: Amount of the ingredient.
        unit: Unit of the quantity.
        new: True to create the ingredient.
    """
    ingredient_id: uuid.UUID | None = None
    name: str | None = None
    quantity: float
    unit: Unit
    new: bool = False

    @model_validator(mode="after")
    def validate_existing_or_new(self):
        """Require either `ingredient_id`, or `new=True` with a `name`, but not both."""
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
    """One ingredient line in the `PatchRecipe` body.

    Send `recipe_ingredient_id` to keep and update an existing line. For the
    ingredient, send `ingredient_id`, or `new=True` and a `name` to create it.
    A line without `recipe_ingredient_id` is added.

    Attributes:
        ingredient_id: ID of an existing ingredient.
        name: Name of the ingredient to create.
        quantity: Amount of the ingredient.
        unit: Unit of the quantity.
        new: True to create the ingredient.
        recipe_ingredient_id: ID of the existing line to update.
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
        """Strip and lowercase the name, and allow only letters (accents included) and spaces."""
        if v is None:
            return None
        v = v.strip().lower()
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", v):
            raise ValueError("Name must only contain letters and spaces")
        return v
    
    @model_validator(mode="after")
    def validate_id_or_name(self) -> "PatchRecipeIngredient":
        """Check the ingredient reference.

        `new=True` requires a `name` and no `ingredient_id`. Otherwise `name` is
        not allowed, and `ingredient_id` or `recipe_ingredient_id` is required.
        """
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