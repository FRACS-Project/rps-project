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
    PatchRecipeIngredient
)

from .crud import RecipeIngredientCrud

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
