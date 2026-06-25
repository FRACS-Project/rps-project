##############################################################################################################
#
# CRUD operations for managing recipes in the application.
#
# This module provides functions to create, read, update, and delete recipe entities
# in the database. It handles all database interactions related to recipes.
#
##############################################################################################################

import uuid
from sqlmodel import Session, select

from . import Recipe
from .schemas import RecipeCreate


class RecipeCrud:

    def __init__(self, db: Session):
        """Initialize RecipeCrud with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db

    def read_recipe(self, recipe_id: uuid.UUID) -> Recipe | None:
        """Retrieve a specific recipe by its ID.

        Args:
            recipe_id (uuid.UUID): The unique identifier of the recipe.

        Returns:
            Recipe | None: The found recipe instance or None if not found.
        """
        return self.db.get(Recipe, recipe_id)

    def read_recipe_by_name(self, name: str):
        """Retrieve the recipe that has the exact same name.

        Args:
            name (str): The name of the recipe to search for.

        Returns:
            Recipe | None: The found recipe instance or None if not found.
        """
        query = select(Recipe).where(Recipe.name == name)
        return self.db.exec(query).first()
    
    def read_recipe_by_name_by_user(self, name: str, user_id: uuid.UUID):
        query = select(Recipe).where(Recipe.name == name, Recipe.owner_id == user_id)
        return self.db.exec(query).first()

    def read_recipes(self, offset: int, limit: int) -> list[Recipe]:
        """Retrieve a paginated list of recipes.

        Args:
            offset (int): Number of records to skip.
            limit (int): Maximum number of records to return.

        Returns:
            list[Recipe]: A list of recipe instances.
        """
        return self.db.exec(select(Recipe).offset(offset).limit(limit)).all()

    def read_recipes_by_name(self, offset: int, limit: int, name: str) -> Recipe | None:
        """Retrieve all recipe that contains the name.

        Args:
            name (str): The name of the recipe to search for.

        Returns:
            Recipe | None: The found recipe instance or None if not found.
        """
        query = select(Recipe).where(Recipe.name.ilike(
            f"%{name}%")).offset(offset).limit(limit)
        return self.db.exec(query).all()

    def read_recipes_by_user(self, offset: int, limit: int, user_id: uuid.UUID) -> list[Recipe]:
        """Retrieve recipes belonging to a specific user.

        Args:
            offset (int): Number of records to skip.
            limit (int): Maximum number of records to return.
            user_id (uuid.UUID): The user's unique identifier.

        Returns:
            list[Recipe]: A list of recipe instances for the specified user.
        """
        query = select(Recipe).where(Recipe.owner_id ==
                                     user_id).offset(offset).limit(limit)
        return self.db.exec(query).all()

    def create_recipe(self, recipe: RecipeCreate, mod: str) -> Recipe:
        """Create a new recipe in the database.

        Args:
            recipe (RecipeCreate): The recipe data to create.

        Returns:
            Recipe: The newly created recipe instance.
        """
        db_recipe = Recipe.model_validate(recipe)
        self.db.add(db_recipe)
        self.db.commit()
        self.db.refresh(db_recipe)
        return db_recipe

    def pre_create_recipe(self, recipe: RecipeCreate) -> Recipe:
        """Create a new recipe in the database.

        Args:
            recipe (RecipeCreate): The recipe data to create.

        Returns:
            Recipe: The newly created recipe instance.
        """
        db_recipe = Recipe.model_validate(recipe)
        self.db.add(db_recipe)
        self.db.flush()
        return db_recipe

    def update_recipe(self, db_recipe: Recipe, recipe: dict) -> Recipe:
        """Update an existing recipe's information.

        Args:
            db_recipe (Recipe): The existing recipe instance to update.
            recipe (dict): The new recipe data to apply.

        Returns:
            Recipe: The updated recipe instance.
        """
        db_recipe.sqlmodel_update(recipe)
        self.db.add(db_recipe)
        self.db.commit()
        self.db.refresh(db_recipe)
        return db_recipe

    def delete_recipe(self, db_recipe: Recipe) -> dict:
        """Delete a recipe from the database.

        Args:
            db_recipe (Recipe): The recipe instance to delete.

        Returns:
            dict: Confirmation message.
        """
        self.db.delete(db_recipe)
        self.db.commit()
        return {"ok": True}

    def save_recipe(self, db_recipe: Recipe) -> Recipe:
        """Save changes to an existing recipe instance.

        Args:
            db_recipe (Recipe): The recipe instance to save.

        Returns:
            Recipe: The saved recipe instance with refreshed state.
        """
        self.db.add(db_recipe)
        self.db.commit()
        self.db.refresh(db_recipe)
        return db_recipe
    
    def refresh_recipe(self, db_recipe: Recipe) -> Recipe:
        self.db.refresh(db_recipe)
        return db_recipe
    
    def save(self) -> None:
        """Commit current transaction."""
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    
