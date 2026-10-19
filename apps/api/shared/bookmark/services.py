"""Bookmark service.

Saves and removes bookmarks, and returns the bookmarked recipes rather
than the bookmark rows.
"""

import uuid
from sqlmodel import Session

from . import BookmarkNotFoundError
from .schemas import BookmarkCreate
from .crud import BookmarkCrud

from ...recipe import Recipe
from ...recipe.services import RecipeService

class BookmarkService:
    """Business logic for bookmarks."""
    # ── Constructor ─────────────────────────────────────────────────────────────────────────────────────────────────

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db
        self.crud = BookmarkCrud(self.db)
        self.recipe_service = RecipeService(self.db)

    # ── Public: Queries ─────────────────────────────────────────────────────────────────────────────────────────────────
    def get_bookmark_by_user(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> Recipe:
        """Return a recipe the user bookmarked.

        Args:
            recipe_id: ID of the recipe.
            user_id: ID of the user.

        Returns:
            The bookmarked recipe.

        Raises:
            BookmarkNotFoundError: If the user has not bookmarked this recipe.
            RecipeNotFoundError: If the recipe no longer exists.
        """

        if not self.crud.read_bookmark(recipe_id, user_id):
            raise BookmarkNotFoundError()

        recipe = self.recipe_service.get_recipe(recipe_id)
        
        return recipe
    
    def get_bookmarks_by_user(self, offset: int, limit: int, user_id: uuid.UUID) -> list[Recipe]:
        """Return a page of the recipes the user bookmarked.

        Args:
            offset: Number of bookmarks to skip.
            limit: Maximum number of bookmarks to return.
            user_id: ID of the user.

        Returns:
            The bookmarked recipes.
        """
        bookmarks = self.crud.read_bookmarks(offset, limit, user_id)
        recipes = []
        if bookmarks:
            for bookmark in bookmarks:
                recipes.append(self.recipe_service.get_recipe(bookmark.recipe_id))
        return recipes

    def create_bookmark_by_user(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> Recipe:
        """Bookmark a recipe for the user.

        Does not check first whether the recipe exists or is already bookmarked.

        Args:
            recipe_id: ID of the recipe.
            user_id: ID of the user.

        Returns:
            The bookmarked recipe.
        """
        bookmark = BookmarkCreate(recipe_id=recipe_id, user_id=user_id)
        db_bookmark = self.crud.create_bookmark(bookmark)
        db_recipe = self.recipe_service.get_recipe(db_bookmark.recipe_id)
        return db_recipe
    
    def delete_bookmark_by_user(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """Remove the user's bookmark on a recipe.

        Args:
            recipe_id: ID of the recipe.
            user_id: ID of the user.

        Returns:
            `{"ok": True}`.

        Raises:
            BookmarkNotFoundError: If the user has not bookmarked this recipe.
        """
        db_bookmark = self.crud.read_bookmark(recipe_id, user_id)
        if not db_bookmark:
            raise BookmarkNotFoundError()

        self.crud.delete_bookmark(db_bookmark)
        return {"ok": True}
    