##############################################################################################################
#
# Pydantic schemas for recipe data validation and serialization.
#
# This module defines the various schemas used for creating, updating, and
# returning recipe data through the API endpoints.
#
##############################################################################################################

from sqlmodel import Field
from pydantic import field_validator
import re
import uuid

from . import RecipeBase

class RecipeSchemaBase(RecipeBase):

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[a-zA-ZÀ-ÿ0-9'\-\s]+$", v):
            raise ValueError("Name must only contain letters and spaces")
        return v

class RecipePublic(RecipeBase):
    """Schema for publicly viewable recipe data.
    
    Attributes:
        id (UUID): The recipe's unique identifier.
        name (str): The recipe name.
        preparation_time (int): Preparation time in minutes.
        cooking_time (int): Cooking time in minutes.
        description (str): Recipe description.
    """
    id: uuid.UUID
    owner_id: uuid.UUID
    owner_name: str | None = None

class RecipeCreate(RecipeSchemaBase):
    """Schema for creating a new recipe.
    
    Inherits all base recipe fields that are required for creation.
    """
    owner_id: uuid.UUID


class RecipeUpdate(RecipeSchemaBase):
    """Schema for updating recipe data.
    
    All fields are optional to allow partial updates.
    
    Attributes:
        name (str, optional): The updated recipe name.
        preparation_time (int, optional): Updated preparation time in minutes.
        cooking_time (int, optional): Updated cooking time in minutes.
        description (str, optional): Updated recipe description.
    """
    name: str| None = None
    preparation_time: int| None = None
    cooking_time: int| None = None
    description: str| None = None
    base_serving: int | None = None


class RecipeUpdateAdmin(RecipeSchemaBase):
    """Schema for updating recipe data.
    
    All fields are optional to allow partial updates.
    
    Attributes:
        name (str, optional): The updated recipe name.
        preparation_time (int, optional): Updated preparation time in minutes.
        cooking_time (int, optional): Updated cooking time in minutes.
        description (str, optional): Updated recipe description.
        owner_id (UUID, optional): Updated owner id.
    """
    name: str| None = None
    preparation_time: int| None = None
    cooking_time: int| None = None
    description: str| None = None
    base_serving: int | None = None
    owner_id: uuid.UUID | None = None


class RecipePublicWithAll(RecipePublic):
    """Extended recipe schema including all related data.
    
    Extends RecipePublic to include nested related information.
    
    Attributes:
        tags (list[TagPublic] | None): The tags for this recipe.
        ingredients (list[RecipeIngredientPublicWithAll] | None): The ingredients in this recipe.
        instructions (list[InstructionPublic] | None): The instructions for this recipe.
    """
    tags: list["TagPublic"] | None = None
    ingredients: list["RecipeIngredientPublicWithAll"] | None = None
    instructions: list["InstructionPublic"] | None = None
    images: list["ImagePublic"] | None = None


class NewRecipe(RecipeSchemaBase):
    """Schema for creating a recipe with related entities.

    Attributes:
        tags (list[TagRef]): Tags to associate with the recipe.
        ingredients (list[NewRecipeIngredient]): Ingredients to attach to the recipe.
        instructions (list[InstructionCreateTest]): Instructions for the recipe.
    """
    tags: list["TagRef"] = Field(min_length=1)
    ingredients: list["NewRecipeIngredient"] = Field(min_length=1)
    instructions: list["NewInstructionCreate"] = Field(min_length=1)
    images: list["ImageCreate"] | None = None

class PatchRecipe(RecipeSchemaBase):
    """Schema for creating a recipe with related entities.

    Attributes:
        tags (list[TagRef]): Tags to associate with the recipe.
        ingredients (list[NewRecipeIngredient]): Ingredients to attach to the recipe.
        instructions (list[InstructionCreateTest]): Instructions for the recipe.
    """
    name: str| None = None
    preparation_time: int| None = None
    cooking_time: int| None = None
    description: str| None = None
    tags: list["TagRef"] | None = None
    ingredients: list["PatchRecipeIngredient"] | None = None
    instructions: list["PatchInstruction"] | None = None


from .components.recipe_ingredient.schemas import RecipeIngredientPublicWithAll, NewRecipeIngredient, PatchRecipeIngredient
from .components.instruction.schemas import InstructionPublic, NewInstructionCreate, PatchInstruction
from ..shared.tag.schemas import TagRef, TagPublic
from ..shared.image.schemas import ImageCreate, ImagePublic
RecipeUpdate.model_rebuild()
RecipePublicWithAll.model_rebuild()
NewRecipe.model_rebuild()
PatchRecipe.model_rebuild()