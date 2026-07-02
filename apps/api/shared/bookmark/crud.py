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

from . import Bookmark
from .schemas import BookmarkCreate


class BookmarkCrud:

    def __init__(self, db: Session):
        """Initialize RecipeCrud with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db

    def read_bookmark(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> Bookmark | None:
        """Retrieve a specific recipe by its ID.

        Args:
            recipe_id (uuid.UUID): The unique identifier of the recipe.

        Returns:
            Recipe | None: The found recipe instance or None if not found.
        """
        query = select(Bookmark).where(
            Bookmark.user_id == user_id,
            Bookmark.recipe_id == recipe_id,
        )
        return self.db.exec(query).first()

    def read_bookmarks(self, offset: int, limit: int, user_id: uuid.UUID) -> list[Bookmark]:
        """Retrieve a paginated list of recipes.

        Args:
            offset (int): Number of records to skip.
            limit (int): Maximum number of records to return.

        Returns:
            list[Recipe]: A list of recipe instances.
        """
        query = select(Bookmark).where(Bookmark.user_id == user_id)

        return self.db.exec(query.offset(offset).limit(limit)).all()

    def create_bookmark(self, bookmark: BookmarkCreate) -> Bookmark:

        db_bookmark = Bookmark.model_validate(bookmark)
        self.db.add(db_bookmark)
        self.db.commit()
        self.db.refresh(db_bookmark)
        return db_bookmark

    def delete_bookmark(self, db_bookmark: Bookmark) -> dict:
        """Delete a recipe from the database.

        Args:
            db_recipe (Recipe): The recipe instance to delete.

        Returns:
            dict: Confirmation message.
        """
        self.db.delete(db_bookmark)
        self.db.commit()
        return {"ok": True}
