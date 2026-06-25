##############################################################################################################
#
# Ingredient Service Layer - Business Logic and Validation
#
# This module contains the service layer for Ingredient management.
# Services handle all business logic, validation, and coordinate between routes and CRUD.
#
# Architecture:
#   - Receives requests from routes (HTTP layer)
#   - Validates business rules (duplicates, existence)
#   - Coordinates CRUD operations (database layer)
#   - Handles error conditions with domain-specific exceptions
#
# Key Responsibilities:
#   - Ingredient creation with duplicate name checking
#   - Ingredient retrieval and pagination
#   - Ingredient updates and deletion with existence validation
#
##############################################################################################################

import uuid
from sqlmodel import Session

from . import (
    Ingredient,
    DuplicateIngredientNameError,
    IngredientNotFoundError
)

from .schemas import (
    IngredientCreate,
    IngredientUpdate
)

from .crud import IngredientCrud

from ...utils import LimitQuery, OffsetQuery


class IngredientService:
    """Service layer for Ingredient management.

    Handles all business logic related to Ingredients including creation, validation,
    and lifecycle operations. Coordinates between HTTP routes and database CRUD.
    """

    def __init__(self, db: Session):
        """Initialize IngredientService with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db
        self.crud = IngredientCrud(self.db)

    def create_ingredient(self, ingredient: IngredientCreate) -> Ingredient:
        """Create a new Ingredient with duplicate name validation.

        Args:
            ingredient (IngredientCreate): The ingredient data to create.

        Returns:
            Ingredient: The newly created ingredient.

        Raises:
            DuplicateIngredientNameError: If Ingredient name already exists.
        """
        if self.crud.get_ingredient_by_name(ingredient.name):
            raise DuplicateIngredientNameError()

        return self.crud.create_ingredient(ingredient)
    
    def pre_create_ingredient(self, ingredient: IngredientCreate) -> Ingredient:
        """Create a new Ingredient with duplicate name validation.

        Args:
            ingredient (IngredientCreate): The ingredient data to create.

        Returns:
            Ingredient: The newly created ingredient.

        Raises:
            DuplicateIngredientNameError: If Ingredient name already exists.
        """
        if self.crud.get_ingredient_by_name(ingredient.name):
            raise DuplicateIngredientNameError()

        return self.crud.pre_create_ingredient(ingredient)

    def get_ingredients(self, offset: OffsetQuery = 0, limit: LimitQuery = 100) -> list[Ingredient]:
        """Retrieve a paginated list of Ingredients.

        Args:
            offset (int): Number of ingredients to skip (for pagination).
            limit (int): Maximum number of ingredients to return.

        Returns:
            List[Ingredient]: List of ingredients.
        """
        return self.crud.read_ingredients(offset, limit)

    def get_ingredient(self, ingredient_id: uuid.UUID) -> Ingredient:
        """Retrieve a specific Ingredient by ID.

        Args:
            ingredient_id (uuid.UUID): The unique identifier of the ingredient.

        Returns:
            Ingredient: The found ingredient instance.

        Raises:
            IngredientNotFoundError: If the Ingredient is not found.
        """
        ingredient = self.crud.read_ingredient(ingredient_id)
        if not ingredient:
            raise IngredientNotFoundError()

        return ingredient

    def update_ingredient(self, ingredient_id: uuid.UUID, ingredient: IngredientUpdate) -> Ingredient:
        """Update an existing Ingredient's information.

        Args:
            ingredient_id (uuid.UUID): The unique identifier of the ingredient.
            ingredient (IngredientUpdate): The new ingredient data to apply.

        Returns:
            Ingredient: The updated ingredient instance.

        Raises:
            IngredientNotFoundError: If the Ingredient is not found.
        """
        db_ingredient = self.crud.read_ingredient(ingredient_id)
        if not db_ingredient:
            raise IngredientNotFoundError()

        ingredient_data = ingredient.model_dump(exclude_unset=True)

        return self.crud.update_ingredient(db_ingredient, ingredient_data)

    def delete_ingredient(self, ingredient_id: uuid.UUID) -> dict:
        """Delete an ingredient by ID.

        Args:
            ingredient_id (uuid.UUID): The unique identifier of the ingredient.

        Raises:
            IngredientNotFoundError: If the Ingredient is not found.
        """
        db_ingredient = self.crud.read_ingredient(ingredient_id)
        if not db_ingredient:
            raise IngredientNotFoundError()

        self.crud.delete_ingredient(db_ingredient)
        return {"ok": True}