##############################################################################################################
#
# Bookmark Service Layer - Business Logic and Validation
#
# This module contains the service layer for bookmark management.
# Services handle all business logic, validation, and coordinate between routes and CRUD.
#
# Architecture:
#   - Receives requests from routes (HTTP layer)
#   - Validates business rules (duplicates, existence)
#   - Coordinates CRUD operations (database layer)
#   - Handles error conditions with domain-specific exceptions
#
# Key Responsibilities:
#   - Recipe creation with duplicate name checking
#   - Recipe retrieval and pagination
#   - Recipe updates and deletion with existence validation
#
##############################################################################################################

import uuid
from sqlmodel import Session

from . import BookmarkNotFoundError
from .schemas import BookmarkCreate
from .crud import BookmarkCrud

from ...recipe import Recipe
from ...recipe.services import RecipeService

class BookmarkService:
    """Service layer for recipe management.

    Handles all business logic related to recipes including creation, validation,
    and lifecycle operations. Coordinates between HTTP routes and database CRUD.
    """
    # ── Constructor ─────────────────────────────────────────────────────────────────────────────────────────────────

    def __init__(self, db: Session):
        """Initialize RecipeService with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db
        self.crud = BookmarkCrud(self.db)
        self.recipe_service = RecipeService(self.db)

    # ── Public: Queries ─────────────────────────────────────────────────────────────────────────────────────────────────
    def get_bookmark_by_user(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> Recipe:
        """Retrieve a specific recipe by ID.

        Args:
            recipe_id (uuid.UUID): The unique identifier of the recipe.

        Returns:
            Recipe: The found recipe instance.

        Raises:
            RecipeNotFoundError: If the recipe is not found.
        """

        # On teste si le bookmark existe bien donc on teste combinaison bookmark et user
        # On récupère la recette et on la renvoie

        if not self.crud.read_bookmark(recipe_id, user_id):
            raise BookmarkNotFoundError()

        recipe = self.recipe_service.get_recipe(recipe_id)
        
        return recipe
    
    def get_bookmarks_by_user(self, offset: int, limit: int, user_id: uuid.UUID) -> list[Recipe]:
        bookmarks = self.crud.read_bookmarks(offset, limit, user_id)
        recipes = []
        if bookmarks:
            for bookmark in bookmarks:
                recipes.append(self.recipe_service.get_recipe(bookmark.recipe_id))
        return recipes

    def create_bookmark_by_user(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> Recipe:
        bookmark = BookmarkCreate(recipe_id=recipe_id, user_id=user_id)
        db_bookmark = self.crud.create_bookmark(bookmark)
        db_recipe = self.recipe_service.get_recipe(db_bookmark.recipe_id)
        return db_recipe
    
    def delete_bookmark_by_user(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        db_bookmark = self.crud.read_bookmark(recipe_id, user_id)
        if not db_bookmark:
            raise BookmarkNotFoundError()

        self.crud.delete_bookmark(db_bookmark)
        return {"ok": True}
    