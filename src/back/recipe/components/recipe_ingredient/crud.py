##############################################################################################################
#
# CRUD operations for managing recipe-ingredient relationships.
#
# This module provides functions to create, read, update, and delete recipe-ingredient
# relationships in the database. It handles all database interactions related to linking
# recipes with their ingredients.
#
##############################################################################################################

import uuid
from sqlmodel import Session, select

from . import RecipeIngredient
from .schemas import RecipeIngredientCreate


class RecipeIngredientCrud:

    def __init__(self, db: Session):
        """Initialize RecipeIngredientCrud with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db

    def create_recipe_ingredient(self, recipe_ingredient: RecipeIngredientCreate) -> RecipeIngredient:
        """Create a recipe-ingredient relationship in the database.

        Args:
            recipe_ingredient (RecipeIngredientCreate): Relationship data to create.

        Returns:
            RecipeIngredient: The newly created relationship instance.
        """
        db_recipe_ingredient = RecipeIngredient.model_validate(
            recipe_ingredient)
        self.db.add(db_recipe_ingredient)
        self.db.commit()
        self.db.refresh(db_recipe_ingredient)
        return db_recipe_ingredient
    
    def pre_create_recipe_ingredient(self, recipe_ingredient: RecipeIngredientCreate) -> RecipeIngredient:
        """Create a recipe-ingredient relationship in the database.

        Args:
            recipe_ingredient (RecipeIngredientCreate): Relationship data to create.

        Returns:
            RecipeIngredient: The newly created relationship instance.
        """
        db_recipe_ingredient = RecipeIngredient.model_validate(recipe_ingredient)
        self.db.add(db_recipe_ingredient)
        self.db.flush()
        return db_recipe_ingredient

    def read_recipe_ingredients(self, offset: int = 0, limit: int = 100) -> list[RecipeIngredient]:
        """Retrieve a paginated list of recipe-ingredient relationships.

        Args:
            offset (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[RecipeIngredient]: A list of relationship instances.
        """
        return self.db.exec(select(RecipeIngredient).offset(offset).limit(limit)).all()

    def read_recipe_ingredient(self, recipe_ingredient_id: uuid.UUID) -> RecipeIngredient | None:
        """Retrieve a specific recipe-ingredient relationship by its ID.

        Args:
            recipe_ingredient_id (uuid.UUID): The unique identifier of the relationship.

        Returns:
            RecipeIngredient | None: The found relationship or None if not found.
        """
        return self.db.get(RecipeIngredient, recipe_ingredient_id)

    def update_recipe_ingredient(
        self,
        db_recipe_ingredient: RecipeIngredient,
        recipe_ingredient: dict
    ) -> RecipeIngredient:
        """Update an existing recipe-ingredient relationship.

        Args:
            db_recipe_ingredient (RecipeIngredient): The existing relationship to update.
            recipe_ingredient (dict): The new relationship data to apply.

        Returns:
            RecipeIngredient: The updated relationship instance.
        """
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
        """Update an existing recipe-ingredient relationship.

        Args:
            db_recipe_ingredient (RecipeIngredient): The existing relationship to update.
            recipe_ingredient (dict): The new relationship data to apply.

        Returns:
            RecipeIngredient: The updated relationship instance.
        """
        db_recipe_ingredient.sqlmodel_update(recipe_ingredient)
        self.db.add(db_recipe_ingredient)
        self.db.flush()
        return db_recipe_ingredient

    def delete_recipe_ingredient(self, db_recipe_ingredient: RecipeIngredient) -> dict:
        """Delete a recipe-ingredient relationship.

        Args:
            db_recipe_ingredient (RecipeIngredient): The relationship instance to delete.

        Returns:
            dict: Confirmation message.
        """
        self.db.delete(db_recipe_ingredient)
        self.db.commit()
        return {"ok": True}
    
    def pre_delete_recipe_ingredient(self, db_recipe_ingredient: RecipeIngredient) -> dict:
        """Delete a recipe-ingredient relationship.

        Args:
            db_recipe_ingredient (RecipeIngredient): The relationship instance to delete.

        Returns:
            dict: Confirmation message.
        """
        self.db.delete(db_recipe_ingredient)
        return {"ok": True}

    def get_recipe_ingredient_by_pair(
        self,
        recipe_id: uuid.UUID,
        ingredient_id: uuid.UUID
    ) -> RecipeIngredient | None:
        """Retrieve a recipe-ingredient relationship by recipe and ingredient IDs.

        Args:
            recipe_id (uuid.UUID): The recipe identifier.
            ingredient_id (uuid.UUID): The ingredient identifier.

        Returns:
            RecipeIngredient | None: The found relationship or None if not found.
        """
        query = select(RecipeIngredient).where(
            RecipeIngredient.recipe_id == recipe_id,
            RecipeIngredient.ingredient_id == ingredient_id,
        )
        return self.db.exec(query).first()
