"""Request and response schemas for recipes.

`NewRecipe` and `PatchRecipe` are the user-facing bodies that carry the
whole recipe (ingredients, tags, instructions, images) in one request.
The nested schemas are imported at the bottom to avoid circular imports,
then the models are rebuilt.
"""

from sqlmodel import Field
from pydantic import field_validator
import re
import uuid

from . import RecipeBase

class RecipeSchemaBase(RecipeBase):
    """Base for recipe request bodies. Adds validation of the recipe name."""

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        """Strip spaces and allow only letters (accents included), digits, spaces, `'` and `-`."""
        v = v.strip()
        if not re.match(r"^[a-zA-ZÀ-ÿ0-9'\-\s]+$", v):
            raise ValueError("Name must only contain letters and spaces")
        return v

class RecipePublic(RecipeBase):
    """Recipe fields returned by the API, without related data.

    Attributes:
        id: The recipe's ID.
        owner_id: ID of the owner.
        owner_name: Owner's username, when filled in.
    """
    id: uuid.UUID
    owner_id: uuid.UUID
    owner_name: str | None = None

class RecipeCreate(RecipeSchemaBase):
    """Recipe fields only, used to insert the recipe row.

    Attributes:
        owner_id: ID of the owner.
    """
    owner_id: uuid.UUID


class RecipeUpdate(RecipeSchemaBase):
    """Admin partial update of the recipe fields. Only the fields sent are changed."""
    name: str| None = None
    preparation_time: int| None = None
    cooking_time: int| None = None
    description: str| None = None
    base_serving: int | None = None


class RecipeUpdateAdmin(RecipeSchemaBase):
    """Like `RecipeUpdate`, but can also change the owner. Not used by any route yet.

    Attributes:
        owner_id: New owner ID.
    """
    name: str| None = None
    preparation_time: int| None = None
    cooking_time: int| None = None
    description: str| None = None
    base_serving: int | None = None
    owner_id: uuid.UUID | None = None


class RecipePublicWithAll(RecipePublic):
    """Recipe returned with all its related data.

    Attributes:
        tags: Tags of the recipe.
        ingredients: Ingredient lines, each with its ingredient.
        instructions: Preparation steps.
        images: Active images.
    """
    tags: list["TagPublic"] | None = None
    ingredients: list["RecipeIngredientPublicWithAll"] | None = None
    instructions: list["InstructionPublic"] | None = None
    images: list["ImagePublic"] | None = None


class NewRecipe(RecipeSchemaBase):
    """Body for creating a recipe with everything in one request.

    Each tag and ingredient either references an existing one by ID or has
    `new=True` and a name to create it.

    Attributes:
        tags: At least one tag.
        ingredients: At least one ingredient line.
        instructions: At least one step.
        images: Optional images as base64.
    """
    tags: list["TagRef"] = Field(min_length=1)
    ingredients: list["NewRecipeIngredient"] = Field(min_length=1)
    instructions: list["NewInstructionCreate"] = Field(min_length=1)
    images: list["ImagePayload"] | None = None

class PatchRecipe(RecipeSchemaBase):
    """Body for editing a recipe with everything in one request.

    The recipe is replaced by what is sent: ingredient lines, instructions and
    tags that are missing from the lists are removed. `images` works the same
    way when sent; when it is omitted, images are left as they are.

    Attributes:
        tags: Full list of tags to keep or create.
        ingredients: Full list of ingredient lines; existing ones are matched
            by `recipe_ingredient_id`.
        instructions: Full list of steps; existing ones are matched by `id`.
        images: Full list of images to keep (`id`) or add (`new` + base64).
    """
    name: str| None = None
    preparation_time: int| None = None
    cooking_time: int| None = None
    description: str| None = None
    tags: list["TagRef"] | None = None
    ingredients: list["PatchRecipeIngredient"] | None = None
    instructions: list["PatchInstruction"] | None = None
    images: list["ImagePayload"] | None = None


from .components.recipe_ingredient.schemas import RecipeIngredientPublicWithAll, NewRecipeIngredient, PatchRecipeIngredient
from .components.instruction.schemas import InstructionPublic, NewInstructionCreate, PatchInstruction
from ..shared.tag.schemas import TagRef, TagPublic
from ..shared.image.schemas import ImagePayload, ImagePublic, ImageUpdate
RecipeUpdate.model_rebuild()
RecipePublicWithAll.model_rebuild()
NewRecipe.model_rebuild()
PatchRecipe.model_rebuild()