"""Database access for ingredients. No validation; the service layer handles that.

`pre_create_ingredient` only flushes, so it can run inside a recipe
transaction that is committed once.
"""

import uuid
from sqlmodel import Session, select

from . import Ingredient
from .schemas import IngredientCreate


class IngredientCrud:
    """Queries and writes for the ingredient table."""

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db

    def create_ingredient(self, ingredient: IngredientCreate) -> Ingredient:
        """Insert an ingredient and commit."""
        db_ingredient = Ingredient.model_validate(ingredient)
        self.db.add(db_ingredient)
        self.db.commit()
        self.db.refresh(db_ingredient)
        return db_ingredient
    
    def pre_create_ingredient(self, ingredient: IngredientCreate) -> Ingredient:
        """Add an ingredient and flush without committing, so its ID is available."""
        db_ingredient = Ingredient.model_validate(ingredient)
        self.db.add(db_ingredient)
        self.db.flush()
        return db_ingredient

    def read_ingredients(self, offset: int = 0, limit: int = 100) -> list[Ingredient]:
        """Return a page of ingredients."""
        return self.db.exec(select(Ingredient).offset(offset).limit(limit)).all()

    def read_ingredient(self, ingredient_id: uuid.UUID) -> Ingredient | None:
        """Return the ingredient with this ID, or None."""
        return self.db.get(Ingredient, ingredient_id)

    def update_ingredient(self, db_ingredient: Ingredient, ingredient: dict) -> Ingredient:
        """Apply the given fields to an ingredient and commit."""
        db_ingredient.sqlmodel_update(ingredient)
        self.db.add(db_ingredient)
        self.db.commit()
        self.db.refresh(db_ingredient)
        return db_ingredient

    def delete_ingredient(self, db_ingredient: Ingredient) -> dict:
        """Delete an ingredient and commit."""
        self.db.delete(db_ingredient)
        self.db.commit()
        return {"ok": True}

    def get_ingredient_by_name(self, name: str) -> Ingredient | None:
        """Return the ingredient with exactly this name, or None."""
        query = select(Ingredient).where(Ingredient.name == name)
        return self.db.exec(query).first()
