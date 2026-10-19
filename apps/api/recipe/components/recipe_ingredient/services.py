##############################################################################################################
#
# Recipe Ingredient Service Layer - Business Logic and Validation
#
# This module contains the service layer for recipe-ingredient management.
# Services handle all business logic, validation, and coordinate between routes and CRUD.
#
##############################################################################################################

import uuid
from sqlmodel import Session

from . import (
    RecipeIngredient,
    DuplicateRecipeIngredientError,
    RecipeIngredientNotFoundError,
)

from .schemas import (
    RecipeIngredientCreate,
    RecipeIngredientUpdate,
    PatchRecipeIngredient,
    NewRecipeIngredient
)

from .crud import RecipeIngredientCrud

from ....shared.ingredient.services import IngredientService
from ....shared.ingredient.schemas import IngredientCreate

from ...models import Recipe

from ....utils import (
    LimitQuery,
    OffsetQuery,
    DEFAULT_LIMIT,
    DEFAULT_OFFSET
)


class RecipeIngredientService:
    """Service layer for recipe-ingredient management."""

    def __init__(self, db: Session):
        """Initialize RecipeIngredientService with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db
        self.crud = RecipeIngredientCrud(self.db)
        self.ingredient_service = IngredientService(self.db)

    def create_recipe_ingredient(self, recipe_ingredient: RecipeIngredientCreate) -> RecipeIngredient:
        """Create a recipe-ingredient relationship with duplicate validation.

        Args:
            recipe_ingredient (RecipeIngredientCreate): Relationship payload.

        Returns:
            RecipeIngredient: The newly created relationship instance.

        Raises:
            DuplicateRecipeIngredientError: If the relationship already exists.
        """
        existing = self.crud.get_recipe_ingredient_by_pair(
            recipe_ingredient.recipe_id,
            recipe_ingredient.ingredient_id,
        )
        if existing:
            raise DuplicateRecipeIngredientError()

        return self.crud.create_recipe_ingredient(recipe_ingredient)
    
    def pre_create_recipe_ingredient(self, recipe_ingredient: RecipeIngredientCreate) -> RecipeIngredient:
        """Create a recipe-ingredient relationship with duplicate validation.

        Args:
            recipe_ingredient (RecipeIngredientCreate): Relationship payload.

        Returns:
            RecipeIngredient: The newly created relationship instance.

        Raises:
            DuplicateRecipeIngredientError: If the relationship already exists.
        """
        existing = self.crud.get_recipe_ingredient_by_pair(
            recipe_ingredient.recipe_id,
            recipe_ingredient.ingredient_id,
        )
        if existing:
            raise DuplicateRecipeIngredientError()

        return self.crud.pre_create_recipe_ingredient(recipe_ingredient)

    def get_recipe_ingredients(self, offset: OffsetQuery = DEFAULT_OFFSET, limit: LimitQuery = DEFAULT_LIMIT) -> list[RecipeIngredient]:
        """Retrieve a paginated list of recipe-ingredient relationships.

        Args:
            offset (OffsetQuery): Number of relationships to skip (for pagination).
            limit (LimitQuery): Maximum number of relationships to return.

        Returns:
            list[RecipeIngredient]: List of relationships.
        """
        return self.crud.read_recipe_ingredients(offset, limit)

    def get_recipe_ingredient(self, recipe_ingredient_id: uuid.UUID) -> RecipeIngredient:
        """Retrieve a specific recipe-ingredient relationship by ID.

        Args:
            recipe_ingredient_id (UUID): The unique identifier of the relationship.

        Returns:
            RecipeIngredient: The relationship instance.

        Raises:
            RecipeIngredientNotFoundError: If the relationship is not found.
        """
        recipe_ingredient = self.crud.read_recipe_ingredient(
            recipe_ingredient_id)
        if not recipe_ingredient:
            raise RecipeIngredientNotFoundError()

        return recipe_ingredient

    def update_recipe_ingredient(
        self,
        recipe_ingredient_id: uuid.UUID,
        recipe_ingredient: RecipeIngredientUpdate | PatchRecipeIngredient,
    ) -> RecipeIngredient:
        """Update an existing recipe-ingredient relationship.

        Args:
            recipe_ingredient_id (UUID): The unique identifier of the relationship.
            recipe_ingredient (RecipeIngredientUpdate): The new data to apply.

        Returns:
            RecipeIngredient: The updated relationship instance.

        Raises:
            RecipeIngredientNotFoundError: If the relationship is not found.
        """
        db_recipe_ingredient = self.crud.read_recipe_ingredient(
            recipe_ingredient_id)
        if not db_recipe_ingredient:
            raise RecipeIngredientNotFoundError()

        recipe_ingredient_data = recipe_ingredient.model_dump(
            exclude_unset=True)
        return self.crud.update_recipe_ingredient(db_recipe_ingredient, recipe_ingredient_data)
    
    def pre_update_recipe_ingredient(
        self,
        recipe_ingredient_id: uuid.UUID,
        recipe_ingredient: RecipeIngredientUpdate,
    ) -> RecipeIngredient:
        """Update an existing recipe-ingredient relationship.

        Args:
            recipe_ingredient_id (UUID): The unique identifier of the relationship.
            recipe_ingredient (RecipeIngredientUpdate): The new data to apply.

        Returns:
            RecipeIngredient: The updated relationship instance.

        Raises:
            RecipeIngredientNotFoundError: If the relationship is not found.
        """
        db_recipe_ingredient = self.crud.read_recipe_ingredient(
            recipe_ingredient_id)
        if not db_recipe_ingredient:
            raise RecipeIngredientNotFoundError()

        recipe_ingredient_data = recipe_ingredient.model_dump(exclude_unset=True)
        return self.crud.pre_update_recipe_ingredient(db_recipe_ingredient, recipe_ingredient_data)

    def delete_recipe_ingredient(self, recipe_ingredient_id: uuid.UUID) -> dict:
        """Delete a recipe-ingredient relationship by ID.

        Args:
            recipe_ingredient_id (UUID): The unique identifier of the relationship.

        Returns:
            dict: Confirmation message.

        Raises:
            RecipeIngredientNotFoundError: If the relationship is not found.
        """
        db_recipe_ingredient = self.crud.read_recipe_ingredient(
            recipe_ingredient_id)
        if not db_recipe_ingredient:
            raise RecipeIngredientNotFoundError()

        return self.crud.delete_recipe_ingredient(db_recipe_ingredient)
    
    def pre_delete_recipe_ingredient(self, recipe_ingredient_id: uuid.UUID) -> dict:
        """Delete a recipe-ingredient relationship by ID.

        Args:
            recipe_ingredient_id (UUID): The unique identifier of the relationship.

        Returns:
            dict: Confirmation message.

        Raises:
            RecipeIngredientNotFoundError: If the relationship is not found.
        """
        db_recipe_ingredient = self.crud.read_recipe_ingredient(
            recipe_ingredient_id)
        if not db_recipe_ingredient:
            raise RecipeIngredientNotFoundError()

        return self.crud.pre_delete_recipe_ingredient(db_recipe_ingredient)

    def sync_ingredients_on_create(
            self,
            recipe_id: uuid.UUID,
            ingredients: list[NewRecipeIngredient]
    ) -> None:
        """Create all ingredients for a new recipe."""
        for ingredient in ingredients:
            if ingredient.new:
                created_ingredient = self.ingredient_service.pre_create_ingredient(
                    IngredientCreate(name=ingredient.name)
                )
                ingredient.ingredient_id = created_ingredient.id
            # Create RecipeIngredient
            self._create_recipe_ingredient(ingredient, recipe_id)

    def sync_ingredients_on_update(
            self,
            db_recipe: Recipe,
            ingredients: list[PatchRecipeIngredient]
        ) -> None:
        """Update ingredients for existing recipe (delete removed, update/create others)."""
        new_recipe_ingredient_ids = {
            ingredient.recipe_ingredient_id
            for ingredient in ingredients
            if ingredient.recipe_ingredient_id  # Filter out None
        }

        recipe_ingredient_ids_to_delete = {
            ingredient.id
            for ingredient in db_recipe.ingredients
            if ingredient.id not in new_recipe_ingredient_ids
        }

        for recipe_ingredient_id in recipe_ingredient_ids_to_delete:
            self.pre_delete_recipe_ingredient(recipe_ingredient_id)

        db_recipe.ingredients = [
            ingredient
            for ingredient in db_recipe.ingredients 
            if ingredient.id not in recipe_ingredient_ids_to_delete
        ]

        for ingredient in ingredients:
            if ingredient.new:
                created_ingredient = self.ingredient_service.pre_create_ingredient(
                    IngredientCreate(name=ingredient.name)
                )
                ingredient.ingredient_id = created_ingredient.id

            if ingredient.recipe_ingredient_id and not ingredient.new:
                self.pre_update_recipe_ingredient(
                    ingredient.recipe_ingredient_id,
                    RecipeIngredientUpdate(
                        quantity=ingredient.quantity,
                        unit=ingredient.unit,
                        ingredient_id=ingredient.ingredient_id
                    )
                )
            else:
                self._create_recipe_ingredient(ingredient, db_recipe.id)

    def _create_recipe_ingredient(
            self,
            ingredient: NewRecipeIngredient | PatchRecipeIngredient,
            recipe_id: uuid.UUID
    ):
        self.pre_create_recipe_ingredient(
            RecipeIngredientCreate(
                quantity=ingredient.quantity,
                unit=ingredient.unit,
                ingredient_id=ingredient.ingredient_id,
                recipe_id=recipe_id
            )
        )