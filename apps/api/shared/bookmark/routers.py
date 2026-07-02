##############################################################################################################
#
# Bookmark Management Routes
#
# This module provides HTTP endpoints for bookmark management.
# Routes handle HTTP request/response and delegate business logic to the service layer.
#
# Architecture:
#   - Routes: HTTP layer (request parsing, response formatting)
#   - Services: Business logic (validation, orchestration)
#   - CRUD: Database operations (queries, inserts, updates, deletes)
#
##############################################################################################################

import uuid
from fastapi import APIRouter, Depends
from sqlmodel import Session

from ...recipe.schemas import (
    RecipePublicWithAll
)

from .services import BookmarkService

from ...utils import (
    LimitQuery,
    OffsetQuery,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)

from ...user.schemas import UserPublic
from ...db import get_session
from ...core import get_current_active_user

router = APIRouter(
    prefix="/bookmark",
    tags=["Bookmark"],
    # dependencies=[Depends(get_current_active_user)]
)


@router.post("/me", response_model=RecipePublicWithAll)
def create_bookmark(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """Create a recipe with ingredients and instructions in one request.

    Args:
        recipe (NewRecipe): Aggregated recipe payload.
        session (Session): The database session dependency.
        current_user (UserPublic): Current authenticated user.

    Returns:
        RecipePublicWithAll: Created recipe with related data.
    """

    service = BookmarkService(session)
    return service.create_bookmark_by_user(recipe_id, current_user.id)


@router.get("/me", response_model=list[RecipePublicWithAll])
def get_my_bookmarks(
        offset: OffsetQuery = DEFAULT_OFFSET,
        limit: LimitQuery = DEFAULT_LIMIT,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """Retrieve bookmarked recipes by the current user.

    Args:
        offset (OffsetQuery): Number of recipes to skip (for pagination).
        limit (LimitQuery): Maximum number of recipes to return.
        session (Session): Database session dependency.
        current_user (UserPublic): Current authenticated user.

    Returns:
        List[RecipePublicWithAll]: List of user's recipes with related data.
    """
    service = BookmarkService(session)
    return service.get_bookmarks_by_user(offset, limit, current_user.id)


@router.get("/me/{recipe_id}", response_model=RecipePublicWithAll)
def get_my_bookmark(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """Retrieve a specific recipe by its ID.

    Args:
        recipe_id (UUID): The unique identifier of the recipe.
        session (Session): The database session dependency.
        current_user (UserPublic): Current authenticated user.

    Returns:
        RecipePublicWithAll: The recipe with related data.
    """

    service = BookmarkService(session)
    return service.get_bookmark_by_user(recipe_id, current_user.id)


@router.delete("/me/{recipe_id}")
def delete_bookmark(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """Delete the recipe by its ID for the current user.

    Args:
        recipe_id (UUID): The unique identifier of the recipe.
        session (Session): The database session dependency.
        current_user (UserPublic): Current authenticated user.

    Returns:
        dict: Confirmation message.
    """

    service = BookmarkService(session)
    return service.delete_bookmark_by_user(recipe_id, current_user.id)
