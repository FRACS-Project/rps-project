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

import uuid
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

from .components.recipe_ingredient.services import RecipeIngredientService

from .components.instruction.services import InstructionService

from ..shared.tag.services import TagService

from ..shared.image.schemas import ImagePublic, ImagePayload
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

    def get_recipe_images(self, recipe_id: uuid.UUID) -> list[ImagePublic]:

        return self.image_service.get_images_by_recipe(recipe_id)

    def get_recipe_image_primary(self, recipe_id: uuid.UUID) -> ImagePublic:

        return self.image_service.get_primary_image_by_recipe(recipe_id)

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

    def get_recipe_by_user(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> Recipe:
        """Retrieve a recipe owned by the user."""
        return self._get_owned_recipe(recipe_id, user_id)

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

        # Create ingredient (if needed) and link ingredient to recipe
        self.recipe_ingredient_service.sync_ingredients_on_create(
            created_recipe.id,
            recipe.ingredients
        )

        # Create tag (if needed) and link tag to Recipe
        self.tag_service.sync_tags_on_create(created_recipe, recipe.tags)

        # Add Instructions to Recipe
        self.instruction_service.sync_instructions_on_create(created_recipe.id, recipe.instructions)

        # Add Image to the recipe
        if recipe.images:
            self.image_service.sync_recipe_images_on_create(
                created_recipe.id,
                recipe.images,
                user_id
            )

        self.crud.save()

        if recipe.images:
            self.image_service.store_pending_recipe_images(recipe.images, created_recipe.id)

        self.image_service.delete_pending_recipe_images(created_recipe.id)

        return self.crud.refresh_recipe(created_recipe)

    def update_recipe_by_user(
        self,
        recipe_id: uuid.UUID,
        recipe: PatchRecipe,
        user_id: uuid.UUID
    ) -> Recipe:
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
        db_recipe = self._get_owned_recipe(recipe_id, user_id)

        self._validate_ingredients(recipe.ingredients)
        self._validate_tags(recipe.tags)
        self._validate_instructions(recipe.instructions)
        self._validate_images(recipe.images)

        # Update recipe
        if (db_recipe.name != recipe.name) and self.crud.read_recipe_by_name_by_user(recipe.name, user_id):
            raise DuplicateRecipeNameError()

        db_recipe.name = recipe.name
        db_recipe.preparation_time = recipe.preparation_time
        db_recipe.cooking_time = recipe.cooking_time
        db_recipe.description = recipe.description
        db_recipe.base_serving = recipe.base_serving

        # Update recipe ingredients
        self.recipe_ingredient_service.sync_ingredients_on_update(
            db_recipe,
            recipe.ingredients
        )

        # Update tags
        self.tag_service.sync_tags_on_update(
            db_recipe,
            recipe.tags
        )

        # Update instructions
        self.instruction_service.sync_instructions_on_update(
            db_recipe,
            recipe.instructions
        )

        if recipe.images is not None:
            self.image_service.sync_recipe_images_on_update(
                db_recipe,
                recipe.images
            )

        self.crud.save()
        
        if recipe.images:
            self.image_service.store_pending_recipe_images(recipe.images, recipe_id)
        
        self.image_service.delete_pending_recipe_images(recipe_id)

        return self.crud.refresh_recipe(db_recipe)

    def delete_recipe_by_user(self, recipe_id: uuid.UUID, user_id: uuid.UUID):
        """Delete a recipe of a user by recipe ID.

        Args:
            recipe_id (uuid.UUID): The unique identifier of the recipe.
            user_id (uuid.UUID): The unique identifier of the user

        Raises:
            RecipeNotFoundError: If the recipe is not found.
        """
        db_recipe = self._get_owned_recipe(recipe_id, user_id)

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
        if not tags or not all(tag.id or (tag.new and tag.name) for tag in tags):
            raise NoTagInRecipeError()

    def _validate_instructions(self, instructions: list) -> None:
        if not instructions or not all(
                instruction.id or (instruction.title and instruction.details) for instruction in instructions):
            raise NoInstructionInRecipeError()

    def _validate_images(self, images: list[ImagePayload]) -> None:
        if not images:
            return

        if not all(
                (image.new and image.data_base64) or image.id for image in images):
            raise NoImageInRecipeError()

        self.image_service.magic_validation(images)

    # ── Private: Helpers ─────────────────────────────────────────────────────────────────────────────────────────────────
    def _get_owned_recipe(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> Recipe:
        """Return the recipe if it exists and belongs to the user."""
        db_recipe = self.crud.read_recipe(recipe_id)
        if not db_recipe:
            raise RecipeNotFoundError()
        if db_recipe.owner_id != user_id:
            raise NotUserRecipeError()
        return db_recipe