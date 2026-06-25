##############################################################################################################
#
# Recipe Service Layer - Business Logic and Validation
#
# This module contains the service layer for recipe management.
# Services handle all business logic, validation, and coordinate between routes and CRUD.
#
# Architecture:
#   - Receives requests from routes (HTTP layer)
#   - Validates business rules (duplicates, existence)
#   - Coordinates CRUD operations (database layer)
#   - Handles error conditions with domain-specific exceptions
#
# Key Responsibilities:
#   - Recipe creation with duplicate name checking
#   - Recipe retrieval and pagination
#   - Recipe updates and deletion with existence validation
#
##############################################################################################################

import uuid, os, base64
from pathlib import Path
from sqlmodel import Session

from . import (
    Recipe,
    DuplicateRecipeNameError,
    RecipeNotFoundError,
    NoTagInRecipeError,
    NoIngredientInRecipeError,
    NoInstructionInRecipeError,
    NoImageInRecipeError,
    EmptyRecipeUpdateError,
    NotUserRecipeError
)

from .schemas import (
    RecipeCreate,
    RecipeUpdate,
    NewRecipe,
    PatchRecipe,
)

from .crud import RecipeCrud

from .components import RecipeIngredient, Instruction

from .components.recipe_ingredient.schemas import (
    RecipeIngredientCreate,
    RecipeIngredientUpdate,
    PatchRecipeIngredient,
    NewRecipeIngredient
)
from .components.recipe_ingredient.services import RecipeIngredientService

from .components.instruction.schemas import InstructionCreate, InstructionUpdate, NewInstructionCreate, PatchInstruction
from .components.instruction.services import InstructionService

from ..shared import Ingredient
from ..shared.ingredient.schemas import IngredientCreate
from ..shared.ingredient.services import IngredientService

from ..shared import Tag, TagNotFoundError
from ..shared.tag.schemas import TagCreate, TagRef
from ..shared.tag.services import TagService

from ..shared import Image
from ..shared.image.schemas import ImageCreate, ImageRecipeCreate
from ..shared.image.services import ImageService


class RecipeService:
    """Service layer for recipe management.

    Handles all business logic related to recipes including creation, validation,
    and lifecycle operations. Coordinates between HTTP routes and database CRUD.
    """
    # ── Constructor ─────────────────────────────────────────────────────────────────────────────────────────────────

    def __init__(self, db: Session):
        """Initialize RecipeService with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db
        self.crud = RecipeCrud(self.db)
        self.ingredient_service = IngredientService(self.db)
        self.recipe_ingredient_service = RecipeIngredientService(self.db)
        self.instruction_service = InstructionService(self.db)
        self.image_service = ImageService(self.db)
        self.tag_service = TagService(self.db)

    # ── Public: Queries ─────────────────────────────────────────────────────────────────────────────────────────────────
    def get_recipe(self, recipe_id: uuid.UUID) -> Recipe:
        """Retrieve a specific recipe by ID.

        Args:
            recipe_id (uuid.UUID): The unique identifier of the recipe.

        Returns:
            Recipe: The found recipe instance.

        Raises:
            RecipeNotFoundError: If the recipe is not found.
        """
        recipe = self.crud.read_recipe(recipe_id)
        if not recipe:
            raise RecipeNotFoundError()

        return recipe

    def get_recipes(self, offset: int = 0, limit: int = 0) -> list[Recipe]:
        """Retrieve a paginated list of recipes.

        Args:
            offset (int): Number of recipes to skip (for pagination).
            limit (int): Maximum number of recipes to return.

        Returns:
            List[Recipe]: List of recipes.
        """
        return self.crud.read_recipes(offset, limit)

    # ── Public: User-scoped Queries ─────────────────────────────────────────────────────────────────────────────────────────────────
    def get_recipes_by_name(self, offset: int, limit: int, recipe_name: str):
        return self.crud.read_recipes_by_name(offset, limit, recipe_name)

    def get_recipes_by_user(self, offset: int, limit: int, user_id: uuid.UUID) -> list[Recipe]:
        """Retrieve a paginated list of recipes for a given user.

        Args:
            offset (int): Number of recipes to skip (for pagination).
            limit (int): Maximum number of recipes to return.
            user_id (UUID): The user's unique identifier.

        Returns:
            list[Recipe]: List of recipes for the given user.
        """
        recipe = self.crud.read_recipes_by_user(offset, limit, user_id)
        return recipe

    def get_recipe_by_user(self, recipe_id: uuid.UUID, user_id: uuid.UUID):
        pass

    # ── Public: Commands ─────────────────────────────────────────────────────────────────────────────────────────────────
    def create_recipe(self, recipe: RecipeCreate) -> Recipe:
        """Create a new recipe with duplicate name validation.

        Args:
            recipe (RecipeCreate): The recipe data to create.

        Returns:
            Recipe: The newly created recipe.

        Raises:
            DuplicateRecipeNameError: If recipe name already exists.
        """
        if self.crud.read_recipe_by_name(recipe.name):
            raise DuplicateRecipeNameError()

        return self.crud.create_recipe(recipe)

    def update_recipe(self, recipe_id: uuid.UUID, recipe: RecipeUpdate) -> Recipe:
        """Update an existing recipe's information.

        Args:
            recipe_id (uuid.UUID): The unique identifier of the recipe.
            recipe (RecipeUpdate): The new recipe data to apply.

        Returns:
            Recipe: The updated recipe instance.

        Raises:
            RecipeNotFoundError: If the recipe is not found.
        """
        db_recipe = self.crud.read_recipe(recipe_id)
        if not db_recipe:
            raise RecipeNotFoundError()

        recipe_data = recipe.model_dump(exclude_unset=True)

        if not recipe_data:
            raise EmptyRecipeUpdateError()

        return self.crud.update_recipe(db_recipe, recipe_data)

    def delete_recipe(self, recipe_id: uuid.UUID) -> dict[str, bool]:
        """Delete a recipe by ID.

        Args:
            recipe_id (uuid.UUID): The unique identifier of the recipe.

        Raises:
            RecipeNotFoundError: If the recipe is not found.
        """
        db_recipe = self.crud.read_recipe(recipe_id)
        if not db_recipe:
            raise RecipeNotFoundError()

        self.crud.delete_recipe(db_recipe)
        return {"ok": True}

    # ── Public: User-scoped Commands ─────────────────────────────────────────────────────────────────────────────────────────────────
    def create_recipe_by_user(self, recipe: NewRecipe, user_id: uuid.UUID) -> Recipe:
        """Create a recipe and related entities in one operation.

        Args:
            recipe (NewRecipe): The aggregated recipe payload.
            user_id (UUID): The user's unique identifier.

        Returns:
            Recipe: The created recipe with related data.

        Raises:
            NoIngredientInRecipeError: If no ingredients are provided.
            NoTagInRecipeError: If no tags are provided.
            NoInstructionInRecipeError: If no instructions are provided.
        """

        if self.crud.read_recipe_by_name_by_user(recipe.name, user_id):
            raise DuplicateRecipeNameError()

        self._validate_ingredients(recipe.ingredients)
        self._validate_tags(recipe.tags)
        self._validate_instructions(recipe.instructions)
        self._validate_images(recipe.images)

        # Create Recipe
        recipe_data = RecipeCreate(
            name=recipe.name,
            preparation_time=recipe.preparation_time,
            cooking_time=recipe.cooking_time,
            description=recipe.description,
            base_serving=recipe.base_serving,
            owner_id=user_id
        )
        created_recipe = self.crud.pre_create_recipe(recipe_data)
        created_recipe.owner_id = user_id

        recipe.instructions

        # Create ingredient (if needed) and link ingredient to recipe
        self._sync_ingredients_on_create(created_recipe, recipe.ingredients)

        # Create tag (if needed) and link tag to Recipe
        self._sync_tags_on_create(created_recipe, recipe.tags)

        # Add Instructions to Recipe
        self._sync_instructions_on_create(created_recipe, recipe.instructions)

        # Add Image to the recipe
        self._sync_images_on_create(created_recipe, recipe.images, user_id)

        self.crud.save()

        return self.crud.refresh_recipe(created_recipe)

    def update_recipe_by_user(self, recipe_id: uuid.UUID, recipe: PatchRecipe, user_id: uuid.UUID) -> Recipe:
        """Update an existing recipe's information.

        Args:
            recipe_id (uuid.UUID): The unique identifier of the recipe.
            recipe (RecipeUpdate): The new recipe data to apply.
            user_id (UUID): The user's unique identifier.

        Returns:
            Recipe: The updated recipe instance.

        Raises:
            RecipeNotFoundError: If the recipe is not found.
        """

        # Get recipe
        db_recipe = self.crud.read_recipe(recipe_id)
        if not db_recipe:
            raise RecipeNotFoundError()
        elif not db_recipe.owner_id == user_id:
            raise NotUserRecipeError()

        self._validate_ingredients(recipe.ingredients)
        self._validate_tags(recipe.tags)
        self._validate_instructions(recipe.instructions)

        # Update recipe
        if (db_recipe.name != recipe.name) and self.crud.read_recipe_by_name(recipe.name):
            raise DuplicateRecipeNameError()

        db_recipe.name = recipe.name
        db_recipe.preparation_time = recipe.preparation_time
        db_recipe.cooking_time = recipe.cooking_time
        db_recipe.description = recipe.description
        db_recipe.base_serving = recipe.base_serving

        # Update recipe ingredients
        self._sync_ingredients_on_update(
            db_recipe, recipe.ingredients, recipe_id)

        # Update tags
        self._sync_tags_on_update(db_recipe, recipe.tags)

        # Update instructions
        self._sync_instructions_on_update(
            db_recipe, recipe.instructions, recipe_id)

        self.crud.save()

        return self.crud.refresh_recipe(db_recipe)

    def delete_recipe_by_user(self, recipe_id: uuid.UUID, user_id: uuid.UUID):
        """Delete a recipe of a user by recipe ID.

        Args:
            recipe_id (uuid.UUID): The unique identifier of the recipe.
            user_id (uuid.UUID): The unique identifier of the user

        Raises:
            RecipeNotFoundError: If the recipe is not found.
        """
        db_recipe = self.crud.read_recipe(recipe_id)
        if not db_recipe:
            raise RecipeNotFoundError()
        elif not db_recipe.owner_id == user_id:
            raise NotUserRecipeError()

        self.crud.delete_recipe(db_recipe)
        return {"ok": True}

    # ── Private: Validation ─────────────────────────────────────────────────────────────────────────────────────────────────
    def _validate_ingredients(self, ingredients: list) -> None:
        """Validate that ingredients exist and are provided."""
        if not ingredients or not any(
                ingredient.ingredient_id or ingredient.name for ingredient in ingredients):
            raise NoIngredientInRecipeError()

    def _validate_tags(self, tags: list) -> None:
        """Validate that tags exist and are provided"""
        if not tags or not all(tag.id or tag.name for tag in tags):
            raise NoTagInRecipeError()

    def _validate_instructions(self, instructions: list) -> None:
        if not instructions or not all(
                instruction.id or (instruction.title and instruction.details) for instruction in instructions):
            raise NoInstructionInRecipeError()

    def _validate_images(self, images: list) -> None:
        if not images:
            return

        if not all(
                (image.id and image.data_base64) or image.data_base64 for image in images):
            raise NoImageInRecipeError()

        self.image_service.magic_validation(images)

    # ── Private: Creation ─────────────────────────────────────────────────────────────────────────────────────────────────
    def _sync_ingredients_on_create(self, recipe: Recipe, ingredients: list[NewRecipeIngredient]) -> None:
        """Create all ingredients for a new recipe."""
        for ingredient in ingredients:
            if ingredient.new:
                ingredient_data = IngredientCreate(name=ingredient.name)
                created_ing = self.ingredient_service.pre_create_ingredient(
                    ingredient_data)
                ingredient.ingredient_id = created_ing.id
            # Create RecipeIngredient
            self.recipe_ingredient_service.pre_create_recipe_ingredient(
                RecipeIngredientCreate(
                    quantity=ingredient.quantity,
                    unit=ingredient.unit,
                    ingredient_id=ingredient.ingredient_id,
                    recipe_id=recipe.id
                )
            )

    def _sync_tags_on_create(self, recipe: Recipe, tags: list[TagRef]):
        """Create all tags for a new recipe"""
        for tag in tags:
            if tag.new:
                tag_obj = self.tag_service.pre_create_tag(
                    TagCreate(name=tag.name))
            elif tag.id:
                tag_obj = self.tag_service.get_tag(tag.id)
            recipe.tags.append(tag_obj)

    def _sync_instructions_on_create(self, recipe: Recipe, instructions: list[NewInstructionCreate]) -> None:
        """Create all instructions for a new recipe"""
        for instruction in instructions:
            self.instruction_service.create_instruction(
                InstructionCreate(
                    title=instruction.title,
                    details=instruction.details,
                    recipe_id=recipe.id
                )
            )

    def _sync_images_on_create(self, recipe: Recipe, images: list[ImageCreate], user_id: uuid.UUID) -> None:
        """Add the images for a new recipe"""
        BASE_DIR = os.path.abspath("/app")
        IMAGE_DIR = os.path.abspath(os.path.join(BASE_DIR,"storage","uploads"))
        for image in images:
            image_created = self.image_service.create_recipe_image_by_user(
                ImageRecipeCreate(
                    owner_id=user_id,
                    recipe_id=recipe.id
                )
            )
            raw = base64.b64decode(image.data_base64, validate=True)
            temp = os.path.abspath(os.path.join(IMAGE_DIR, str(image_created.id)))
            Path(temp).write_bytes(raw)



    # ── Private: Update ─────────────────────────────────────────────────────────────────────────────────────────────────
    def _sync_ingredients_on_update(self, db_recipe: Recipe, ingredients: list[PatchRecipeIngredient], recipe_id: uuid.UUID) -> None:
        """Update ingredients for existing recipe (delete removed, update/create others)."""
        new_recipe_ingredient_ids = {
            ing.recipe_ingredient_id
            for ing in ingredients
            if ing.recipe_ingredient_id  # Filter out None
        }

        recipe_ingredient_to_delete = {
            ing.id
            for ing in db_recipe.ingredients
            if ing.id not in new_recipe_ingredient_ids
        }

        for id in recipe_ingredient_to_delete:
            self.recipe_ingredient_service.pre_delete_recipe_ingredient(id)

        db_recipe.ingredients = [
            ing for ing in db_recipe.ingredients if ing.id not in recipe_ingredient_to_delete]

        for ingredient in ingredients:
            if ingredient.new:
                # Create ingredient
                created = self.ingredient_service.pre_create_ingredient(
                    IngredientCreate(name=ingredient.name))
                ingredient.ingredient_id = created.id
                # Create RecipeIngredient
                self.recipe_ingredient_service.pre_create_recipe_ingredient(
                    RecipeIngredientCreate(
                        quantity=ingredient.quantity,
                        unit=ingredient.unit,
                        ingredient_id=ingredient.ingredient_id,
                        recipe_id=recipe_id
                    )
                )
            else:
                # Update recipe_ingredients
                if ingredient.recipe_ingredient_id:
                    self.recipe_ingredient_service.pre_update_recipe_ingredient(
                        ingredient.recipe_ingredient_id,
                        RecipeIngredientUpdate(
                            quantity=ingredient.quantity,
                            unit=ingredient.unit,
                            ingredient_id=ingredient.ingredient_id
                        )
                    )
                else:
                    # Create RecipeIngredient
                    self.recipe_ingredient_service.pre_create_recipe_ingredient(
                        RecipeIngredientCreate(
                            quantity=ingredient.quantity,
                            unit=ingredient.unit,
                            ingredient_id=ingredient.ingredient_id,
                            recipe_id=recipe_id
                        )
                    )

    def _sync_tags_on_update(self, db_recipe: Recipe, tags: list[TagRef]) -> None:
        """Update tags for existing recipe (delete removed, update/create others)."""
        desired_tag_ids: set[uuid.UUID] = set()

        for tag in tags:
            if tag.new:
                created = self.tag_service.pre_create_tag(
                    TagCreate(name=tag.name))
                desired_tag_ids.add(created.id)
            elif tag.id:
                desired_tag_ids.add(tag.id)

        current_tag_ids = {tag.id for tag in db_recipe.tags}
        tag_to_remove = current_tag_ids - desired_tag_ids
        tag_to_add = desired_tag_ids - current_tag_ids

        db_recipe.tags = [
            tag for tag in db_recipe.tags if tag.id not in tag_to_remove]

        for tag_id in tag_to_add:
            db_recipe.tags.append(self.tag_service.get_tag(tag_id))

    def _sync_instructions_on_update(self, db_recipe: Recipe, instructions: list[PatchInstruction], recipe_id: uuid.UUID) -> None:
        """Update instructions for existing recipe (delete removed, update/create others)."""
        new_instruction_ids = {
            ins.id
            for ins in instructions
            if ins.id
        }

        instruction_to_delete = {
            ins.id
            for ins in db_recipe.instructions
            if ins.id not in new_instruction_ids
        }

        for id in instruction_to_delete:
            self.instruction_service.pre_delete_instruction(id)

        db_recipe.instructions = [
            ins for ins in db_recipe.instructions if ins.id not in instruction_to_delete]

        for instruction in instructions:
            if instruction.new:
                self.instruction_service.pre_create_instruction(
                    InstructionCreate(
                        title=instruction.title,
                        details=instruction.details,
                        recipe_id=db_recipe.id
                    )
                )
            elif instruction.id:
                self.instruction_service.pre_update_instruction(
                    instruction.id,
                    InstructionUpdate(
                        title=instruction.title,
                        details=instruction.details,
                        recipe_id=db_recipe.id
                    )
                )
