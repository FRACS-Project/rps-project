"""Database access for recipe ingredient lines. No validation; the service layer handles that.

`pre_*` methods only flush, so they can run inside a recipe transaction
that is committed once.
"""

import uuid
from sqlmodel import Session, select

from . import RecipeIngredient
from .schemas import RecipeIngredientCreate


class RecipeIngredientCrud:
    """Queries and writes for the recipe ingredient table."""

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db

    def create_recipe_ingredient(self, recipe_ingredient: RecipeIngredientCreate) -> RecipeIngredient:
        """Insert a recipe ingredient line and commit."""
        db_recipe_ingredient = RecipeIngredient.model_validate(
            recipe_ingredient)
        self.db.add(db_recipe_ingredient)
        self.db.commit()
        self.db.refresh(db_recipe_ingredient)
        return db_recipe_ingredient
    
    def pre_create_recipe_ingredient(self, recipe_ingredient: RecipeIngredientCreate) -> RecipeIngredient:
        """Add a recipe ingredient line and flush without committing."""
        db_recipe_ingredient = RecipeIngredient.model_validate(recipe_ingredient)
        self.db.add(db_recipe_ingredient)
        self.db.flush()
        return db_recipe_ingredient

    def read_recipe_ingredients(self, offset: int = 0, limit: int = 100) -> list[RecipeIngredient]:
        """Return a page of recipe ingredient lines from all recipes."""
        return self.db.exec(select(RecipeIngredient).offset(offset).limit(limit)).all()

    def read_recipe_ingredient(self, recipe_ingredient_id: uuid.UUID) -> RecipeIngredient | None:
        """Return the recipe ingredient line with this ID, or None."""
        return self.db.get(RecipeIngredient, recipe_ingredient_id)

    def update_recipe_ingredient(
        self,
        db_recipe_ingredient: RecipeIngredient,
        recipe_ingredient: dict
    ) -> RecipeIngredient:
        """Apply the given fields to a line and commit."""
        db_recipe_ingredient.sqlmodel_update(recipe_ingredient)
        self.db.add(db_recipe_ingredient)
        self.db.commit()
        self.db.refresh(db_recipe_ingredient)
        return db_recipe_ingredient
    
    def pre_update_recipe_ingredient(
        self,
        db_recipe_ingredient: RecipeIngredient,
        recipe_ingredient: dict
    ) -> RecipeIngredient:
        """Apply the given fields to a line and flush without committing."""
        db_recipe_ingredient.sqlmodel_update(recipe_ingredient)
        self.db.add(db_recipe_ingredient)
        self.db.flush()
        return db_recipe_ingredient

    def delete_recipe_ingredient(self, db_recipe_ingredient: RecipeIngredient) -> dict:
        """Delete a line and commit."""
        self.db.delete(db_recipe_ingredient)
        self.db.commit()
        return {"ok": True}
    
    def pre_delete_recipe_ingredient(self, db_recipe_ingredient: RecipeIngredient) -> dict:
        """Mark a line for deletion without committing."""
        self.db.delete(db_recipe_ingredient)
        return {"ok": True}

    def get_recipe_ingredient_by_pair(
        self,
        recipe_id: uuid.UUID,
        ingredient_id: uuid.UUID
    ) -> RecipeIngredient | None:
        """Return the line linking this recipe and ingredient, or None."""
        query = select(RecipeIngredient).where(
            RecipeIngredient.recipe_id == recipe_id,
            RecipeIngredient.ingredient_id == ingredient_id,
        )
        return self.db.exec(query).first()
