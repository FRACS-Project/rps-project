"""Recipe service.

For user requests, `RecipeService` orchestrates the whole recipe: it
validates the payload, delegates ingredients, tags, instructions and images
to their own services, and commits once. User-scoped methods check that
the recipe belongs to the user. Admin methods work on the recipe fields only.
"""

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
    """Business logic for recipes."""
    # ── Constructor ─────────────────────────────────────────────────────────────────────────────────────────────────

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session shared by all the services it uses, so one
                commit covers the whole recipe.
        """
        self.db = db
        self.crud = RecipeCrud(self.db)
        self.recipe_ingredient_service = RecipeIngredientService(self.db)
        self.instruction_service = InstructionService(self.db)
        self.image_service = ImageService(self.db)
        self.tag_service = TagService(self.db)

    # ── Public: Queries ─────────────────────────────────────────────────────────────────────────────────────────────────
    def get_recipe(self, recipe_id: uuid.UUID) -> Recipe:
        """Return a recipe by ID, from any user.

        Args:
            recipe_id: ID of the recipe.

        Returns:
            The recipe.

        Raises:
            RecipeNotFoundError: If no recipe has this ID.
        """
        recipe = self.crud.read_recipe(recipe_id)
        if not recipe:
            raise RecipeNotFoundError()

        return recipe

    def get_recipe_images(self, recipe_id: uuid.UUID) -> list[ImagePublic]:
        """Return the recipe's active images."""

        return self.image_service.get_images_by_recipe(recipe_id)

    def get_recipe_image_primary(self, recipe_id: uuid.UUID) -> ImagePublic:
        """Return the recipe's primary image.

        Raises:
            ImageNotFoundError: If the recipe has no primary image.
        """

        return self.image_service.get_primary_image_by_recipe(recipe_id)

    def get_recipes(self, offset: int = 0, limit: int = 0) -> list[Recipe]:
        """Return a page of recipes from all users.

        Args:
            offset: Number of recipes to skip.
            limit: Maximum number of recipes to return.

        Returns:
            The recipes in this page.
        """
        return self.crud.read_recipes(offset, limit)

    # ── Public: User-scoped Queries ─────────────────────────────────────────────────────────────────────────────────────────────────
    def get_recipes_by_name(self, offset: int, limit: int, recipe_name: str):
        """Return a page of recipes whose name contains `recipe_name`."""
        return self.crud.read_recipes_by_name(offset, limit, recipe_name)

    def get_recipes_by_user(self, offset: int, limit: int, user_id: uuid.UUID) -> list[Recipe]:
        """Return a page of the user's recipes.

        Args:
            offset: Number of recipes to skip.
            limit: Maximum number of recipes to return.
            user_id: ID of the owner.

        Returns:
            The user's recipes in this page.
        """
        recipe = self.crud.read_recipes_by_user(offset, limit, user_id)
        return recipe

    def get_recipe_by_user(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> Recipe:
        """Return one of the user's recipes.

        Args:
            recipe_id: ID of the recipe.
            user_id: ID of the user making the request.

        Returns:
            The recipe.

        Raises:
            RecipeNotFoundError: If no recipe has this ID.
            NotUserRecipeError: If the recipe belongs to another user.
        """
        return self._get_owned_recipe(recipe_id, user_id)

    # ── Public: Commands ─────────────────────────────────────────────────────────────────────────────────────────────────
    def create_recipe(self, recipe: RecipeCreate) -> Recipe:
        """Admin: create a recipe row only, without related data.

        Args:
            recipe: Recipe fields, including the owner.

        Returns:
            The created recipe.

        Raises:
            DuplicateRecipeNameError: If any recipe already has this name.
        """
        if self.crud.read_recipe_by_name(recipe.name):
            raise DuplicateRecipeNameError()

        return self.crud.create_recipe(recipe)

    def update_recipe(self, recipe_id: uuid.UUID, recipe: RecipeUpdate) -> Recipe:
        """Admin: partially update the recipe fields. Only the fields sent are changed.

        Args:
            recipe_id: ID of the recipe.
            recipe: Fields to change.

        Returns:
            The updated recipe.

        Raises:
            RecipeNotFoundError: If no recipe has this ID.
            EmptyRecipeUpdateError: If no field is set.
        """
        db_recipe = self.crud.read_recipe(recipe_id)
        if not db_recipe:
            raise RecipeNotFoundError()

        recipe_data = recipe.model_dump(exclude_unset=True)

        if not recipe_data:
            raise EmptyRecipeUpdateError()

        return self.crud.update_recipe(db_recipe, recipe_data)

    def delete_recipe(self, recipe_id: uuid.UUID) -> dict[str, bool]:
        """Admin: delete any recipe.

        Args:
            recipe_id: ID of the recipe.

        Returns:
            `{"ok": True}`.

        Raises:
            RecipeNotFoundError: If no recipe has this ID.
        """
        db_recipe = self.crud.read_recipe(recipe_id)
        if not db_recipe:
            raise RecipeNotFoundError()

        self.crud.delete_recipe(db_recipe)
        return {"ok": True}

    # ── Public: User-scoped Commands ─────────────────────────────────────────────────────────────────────────────────────────────────
    def create_recipe_by_user(self, recipe: NewRecipe, user_id: uuid.UUID) -> Recipe:
        """Create a recipe with its ingredients, tags, instructions and images.

        Everything is written in one transaction. New image files are saved to
        disk only after the commit succeeds.

        Args:
            recipe: The full recipe payload.
            user_id: ID of the owner.

        Returns:
            The created recipe with its related data.

        Raises:
            DuplicateRecipeNameError: If the user already has a recipe with this name.
            NoIngredientInRecipeError: If the ingredients are missing or invalid.
            NoTagInRecipeError: If the tags are missing or invalid.
            NoInstructionInRecipeError: If the instructions are missing or invalid.
            NoImageInRecipeError: If an image has neither an ID nor data.
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
        """Replace a recipe's fields and related data with the payload.

        Ingredient lines, tags and instructions missing from the payload are
        removed; new ones are created. Images are only synced when `images` is
        sent. Everything is written in one transaction.

        Args:
            recipe_id: ID of the recipe.
            recipe: The full recipe payload.
            user_id: ID of the user making the request.

        Returns:
            The updated recipe with its related data.

        Raises:
            RecipeNotFoundError: If no recipe has this ID.
            NotUserRecipeError: If the recipe belongs to another user.
            DuplicateRecipeNameError: If the new name is used by another of the user's recipes.
            NoIngredientInRecipeError: If the ingredients are missing or invalid.
            NoTagInRecipeError: If the tags are missing or invalid.
            NoInstructionInRecipeError: If the instructions are missing or invalid.
            NoImageInRecipeError: If an image has neither an ID nor data.
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
        """Delete one of the user's recipes.

        Args:
            recipe_id: ID of the recipe.
            user_id: ID of the user making the request.

        Returns:
            `{"ok": True}`.

        Raises:
            RecipeNotFoundError: If no recipe has this ID.
            NotUserRecipeError: If the recipe belongs to another user.
        """
        db_recipe = self._get_owned_recipe(recipe_id, user_id)

        self.crud.delete_recipe(db_recipe)
        return {"ok": True}

    # ── Private: Validation ─────────────────────────────────────────────────────────────────────────────────────────────────
    def _validate_ingredients(self, ingredients: list) -> None:
        """Raise NoIngredientInRecipeError unless at least one ingredient has an ID or a name."""
        if not ingredients or not any(
                ingredient.ingredient_id or ingredient.name for ingredient in ingredients):
            raise NoIngredientInRecipeError()

    def _validate_tags(self, tags: list) -> None:
        """Raise NoTagInRecipeError unless every tag has an ID or is new with a name."""
        if not tags or not all(tag.id or (tag.new and tag.name) for tag in tags):
            raise NoTagInRecipeError()

    def _validate_instructions(self, instructions: list) -> None:
        """Raise NoInstructionInRecipeError unless every step has an ID or a title and details."""
        if not instructions or not all(
                instruction.id or (instruction.title and instruction.details) for instruction in instructions):
            raise NoInstructionInRecipeError()

    def _validate_images(self, images: list[ImagePayload]) -> None:
        """Check each image has an ID or new data, then check the file types.

        Raises:
            NoImageInRecipeError: If an image has neither.
            WrongImageType: If a new image is not an allowed image type.
        """
        if not images:
            return

        if not all(
                (image.new and image.data_base64) or image.id for image in images):
            raise NoImageInRecipeError()

        self.image_service.magic_validation(images)

    # ── Private: Helpers ─────────────────────────────────────────────────────────────────────────────────────────────────
    def _get_owned_recipe(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> Recipe:
        """Return the recipe if it exists and belongs to the user.

        Raises:
            RecipeNotFoundError: If no recipe has this ID.
            NotUserRecipeError: If the recipe belongs to another user.
        """
        db_recipe = self.crud.read_recipe(recipe_id)
        if not db_recipe:
            raise RecipeNotFoundError()
        if db_recipe.owner_id != user_id:
            raise NotUserRecipeError()
        return db_recipe