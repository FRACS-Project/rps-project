"""Ingredient service: shared ingredient list with unique names."""

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
    """Business logic for ingredients."""

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db
        self.crud = IngredientCrud(self.db)

    def create_ingredient(self, ingredient: IngredientCreate) -> Ingredient:
        """Create an ingredient and commit.

        Raises:
            DuplicateIngredientNameError: If an ingredient already has this name.
        """
        if self.crud.get_ingredient_by_name(ingredient.name):
            raise DuplicateIngredientNameError()

        return self.crud.create_ingredient(ingredient)
    
    def pre_create_ingredient(self, ingredient: IngredientCreate) -> Ingredient:
        """Create an ingredient without committing. Used when saving a recipe.

        Raises:
            DuplicateIngredientNameError: If an ingredient already has this name.
        """
        if self.crud.get_ingredient_by_name(ingredient.name):
            raise DuplicateIngredientNameError()

        return self.crud.pre_create_ingredient(ingredient)

    def get_ingredients(self, offset: OffsetQuery = 0, limit: LimitQuery = 100) -> list[Ingredient]:
        """Return a page of ingredients."""
        return self.crud.read_ingredients(offset, limit)

    def get_ingredient(self, ingredient_id: uuid.UUID) -> Ingredient:
        """Return an ingredient by ID.

        Raises:
            IngredientNotFoundError: If no ingredient has this ID.
        """
        ingredient = self.crud.read_ingredient(ingredient_id)
        if not ingredient:
            raise IngredientNotFoundError()

        return ingredient

    def update_ingredient(self, ingredient_id: uuid.UUID, ingredient: IngredientUpdate) -> Ingredient:
        """Partially update an ingredient. Does not re-check name uniqueness.

        Args:
            ingredient_id: ID of the ingredient.
            ingredient: Fields to change.

        Returns:
            The updated ingredient.

        Raises:
            IngredientNotFoundError: If no ingredient has this ID.
        """
        db_ingredient = self.crud.read_ingredient(ingredient_id)
        if not db_ingredient:
            raise IngredientNotFoundError()

        ingredient_data = ingredient.model_dump(exclude_unset=True)

        return self.crud.update_ingredient(db_ingredient, ingredient_data)

    def delete_ingredient(self, ingredient_id: uuid.UUID) -> dict:
        """Delete an ingredient.

        Returns:
            `{"ok": True}`.

        Raises:
            IngredientNotFoundError: If no ingredient has this ID.
        """
        db_ingredient = self.crud.read_ingredient(ingredient_id)
        if not db_ingredient:
            raise IngredientNotFoundError()

        self.crud.delete_ingredient(db_ingredient)
        return {"ok": True}