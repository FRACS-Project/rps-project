"""Bookmark endpoints under `/bookmark/me`, for the logged-in user."""

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
    """Bookmark a recipe. `recipe_id` is a query parameter. Returns the recipe."""

    service = BookmarkService(session)
    return service.create_bookmark_by_user(recipe_id, current_user.id)


@router.get("/me", response_model=list[RecipePublicWithAll])
def get_my_bookmarks(
        offset: OffsetQuery = DEFAULT_OFFSET,
        limit: LimitQuery = DEFAULT_LIMIT,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """List the recipes you bookmarked, paginated with `offset` and `limit`."""
    service = BookmarkService(session)
    return service.get_bookmarks_by_user(offset, limit, current_user.id)


@router.get("/me/{recipe_id}", response_model=RecipePublicWithAll)
def get_my_bookmark(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """Get a recipe you bookmarked.

    Raises:
        BookmarkNotFoundError: 404 if you have not bookmarked this recipe.
    """

    service = BookmarkService(session)
    return service.get_bookmark_by_user(recipe_id, current_user.id)


@router.delete("/me/{recipe_id}")
def delete_bookmark(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """Remove a bookmark. The recipe itself is not deleted.

    Raises:
        BookmarkNotFoundError: 404 if you have not bookmarked this recipe.
    """

    service = BookmarkService(session)
    return service.delete_bookmark_by_user(recipe_id, current_user.id)
