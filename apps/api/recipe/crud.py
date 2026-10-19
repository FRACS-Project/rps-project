"""Database access for recipes. No validation; the service layer handles that.

`pre_*` methods only flush, so the service can create a recipe and its
related rows in one transaction and commit once with `save()`.
"""

import uuid
from sqlmodel import Session, select

from . import Recipe
from .schemas import RecipeCreate


class RecipeCrud:
    """Queries and writes for the recipe table."""

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db

    def read_recipe(self, recipe_id: uuid.UUID) -> Recipe | None:
        """Return the recipe with this ID, or None."""
        return self.db.get(Recipe, recipe_id)

    def read_recipe_by_name(self, name: str):
        """Return a recipe with exactly this name, from any user, or None."""
        query = select(Recipe).where(Recipe.name == name)
        return self.db.exec(query).first()
    
    def read_recipe_by_name_by_user(self, name: str, user_id: uuid.UUID):
        """Return the user's recipe with exactly this name, or None."""
        query = select(Recipe).where(Recipe.name == name, Recipe.owner_id == user_id)
        return self.db.exec(query).first()

    def read_recipes(self, offset: int, limit: int) -> list[Recipe]:
        """Return a page of recipes from all users."""
        return self.db.exec(select(Recipe).offset(offset).limit(limit)).all()

    def read_recipes_by_name(self, offset: int, limit: int, name: str) -> Recipe | None:
        """Return a page of recipes whose name contains `name` (case-insensitive)."""
        query = select(Recipe).where(Recipe.name.ilike(
            f"%{name}%")).offset(offset).limit(limit)
        return self.db.exec(query).all()

    def read_recipes_by_user(self, offset: int, limit: int, user_id: uuid.UUID) -> list[Recipe]:
        """Return a page of the user's recipes."""
        query = select(Recipe).where(Recipe.owner_id ==
                                     user_id).offset(offset).limit(limit)
        return self.db.exec(query).all()

    def create_recipe(self, recipe: RecipeCreate, mod: str) -> Recipe:
        """Insert a recipe and commit.

        Args:
            recipe: Recipe fields.
            mod: Unused.

        Returns:
            The created recipe.
        """
        db_recipe = Recipe.model_validate(recipe)
        self.db.add(db_recipe)
        self.db.commit()
        self.db.refresh(db_recipe)
        return db_recipe

    def pre_create_recipe(self, recipe: RecipeCreate) -> Recipe:
        """Add a recipe and flush without committing, so its ID is available.

        Args:
            recipe: Recipe fields.

        Returns:
            The pending recipe.
        """
        db_recipe = Recipe.model_validate(recipe)
        self.db.add(db_recipe)
        self.db.flush()
        return db_recipe

    def update_recipe(self, db_recipe: Recipe, recipe: dict) -> Recipe:
        """Apply the given fields to a recipe and commit.

        Args:
            db_recipe: Recipe to update.
            recipe: Fields to change.

        Returns:
            The updated recipe.
        """
        db_recipe.sqlmodel_update(recipe)
        self.db.add(db_recipe)
        self.db.commit()
        self.db.refresh(db_recipe)
        return db_recipe

    def delete_recipe(self, db_recipe: Recipe) -> dict:
        """Delete a recipe and commit. Its ingredient lines, instructions and images are deleted too."""
        self.db.delete(db_recipe)
        self.db.commit()
        return {"ok": True}

    def save_recipe(self, db_recipe: Recipe) -> Recipe:
        """Add the recipe to the session, commit, and return it refreshed."""
        self.db.add(db_recipe)
        self.db.commit()
        self.db.refresh(db_recipe)
        return db_recipe
    
    def refresh_recipe(self, db_recipe: Recipe) -> Recipe:
        """Reload the recipe and its relationships from the database."""
        self.db.refresh(db_recipe)
        return db_recipe
    
    def save(self) -> None:
        """Commit the current transaction."""
        self.db.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""
        self.db.rollback()

    
