##############################################################################################################
#
# CRUD operations for managing ingredients in the application.
#
# This module provides functions to create, read, update, and delete ingredient entities
# in the database. It handles all database interactions related to ingredients.
#
##############################################################################################################

import uuid
from sqlmodel import Session, select

from . import Ingredient
from .schemas import IngredientCreate


class IngredientCrud:

    def __init__(self, db: Session):
        """Initialize IngredientCrud with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db

    def create_ingredient(self, ingredient: IngredientCreate) -> Ingredient:
        """Create a new ingredient in the database.

        Args:
            ingredient (IngredientCreate): The ingredient data to create.

        Returns:
            Ingredient: The newly created ingredient instance.
        """
        db_ingredient = Ingredient.model_validate(ingredient)
        self.db.add(db_ingredient)
        self.db.commit()
        self.db.refresh(db_ingredient)
        return db_ingredient
    
    def pre_create_ingredient(self, ingredient: IngredientCreate) -> Ingredient:
        """Create a new ingredient in the database.

        Args:
            ingredient (IngredientCreate): The ingredient data to create.

        Returns:
            Ingredient: The newly created ingredient instance.
        """
        db_ingredient = Ingredient.model_validate(ingredient)
        self.db.add(db_ingredient)
        self.db.flush()
        return db_ingredient

    def read_ingredients(self, offset: int = 0, limit: int = 100) -> list[Ingredient]:
        """Retrieve a paginated list of ingredients.

        Args:
            offset (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[Ingredient]: A list of ingredient instances.
        """
        return self.db.exec(select(Ingredient).offset(offset).limit(limit)).all()

    def read_ingredient(self, ingredient_id: uuid.UUID) -> Ingredient | None:
        """Retrieve a specific ingredient by its ID.

        Args:
            ingredient_id (uuid.UUID): The unique identifier of the ingredient.

        Returns:
            Ingredient | None: The found ingredient instance or None if not found.
        """
        return self.db.get(Ingredient, ingredient_id)

    def update_ingredient(self, db_ingredient: Ingredient, ingredient: dict) -> Ingredient:
        """Update an existing ingredient's information.

        Args:
            db_ingredient (Ingredient): The existing ingredient instance to update.
            ingredient (dict): The new ingredient data to apply.

        Returns:
            Ingredient: The updated ingredient instance.
        """
        db_ingredient.sqlmodel_update(ingredient)
        self.db.add(db_ingredient)
        self.db.commit()
        self.db.refresh(db_ingredient)
        return db_ingredient

    def delete_ingredient(self, db_ingredient: Ingredient) -> dict:
        """Delete an ingredient from the database.

        Args:
            db_ingredient (Ingredient): The ingredient instance to delete.

        Returns:
            dict: Confirmation message.
        """
        self.db.delete(db_ingredient)
        self.db.commit()
        return {"ok": True}

    def get_ingredient_by_name(self, name: str) -> Ingredient | None:
        """Retrieve an ingredient by its name.

        Args:
            name (str): The name of the ingredient to search for.

        Returns:
            Ingredient | None: The found ingredient instance or None if not found.
        """
        query = select(Ingredient).where(Ingredient.name == name)
        return self.db.exec(query).first()
