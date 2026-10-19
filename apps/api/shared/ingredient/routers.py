"""Ingredient endpoints under `/ingredient`. Login required; writes are admin only."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from .schemas import (
    IngredientCreate,
    IngredientPublic,
    IngredientUpdate
)

from ...utils import (
    LimitQuery,
    OffsetQuery,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)

from .services import IngredientService
from ...db import get_session
from ...core import get_current_admin_user, get_current_active_user

router = APIRouter(
    prefix="/ingredient",
    tags=["Ingredient"],
    dependencies=[Depends(get_current_active_user)]
)


@router.post("/", response_model=IngredientPublic, dependencies=[Depends(get_current_admin_user)])
def create_ingredient(ingredient: IngredientCreate, session: Session = Depends(get_session)):
    """Admin: create an ingredient.

    Raises:
        DuplicateIngredientNameError: 409 if an ingredient already has this name.
    """
    service = IngredientService(session)
    return service.create_ingredient(ingredient)


@router.get("/", response_model=list[IngredientPublic])
def get_ingredients(
        offset: OffsetQuery = DEFAULT_OFFSET,
        limit: LimitQuery = DEFAULT_LIMIT,
        session: Session = Depends(get_session)
):
    """List ingredients, paginated with `offset` and `limit`."""
    service = IngredientService(session)
    return service.get_ingredients(offset, limit)


@router.get("/{ingredient_id}", response_model=IngredientPublic)
def get_ingredient(
        ingredient_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Get an ingredient by ID.

    Raises:
        IngredientNotFoundError: 404 if no ingredient has this ID.
    """

    service = IngredientService(session)
    return service.get_ingredient(ingredient_id)


@router.patch("/{ingredient_id}", response_model=IngredientPublic, dependencies=[Depends(get_current_admin_user)])
def update_ingredient(
        ingredient_id: uuid.UUID,
        ingredient: IngredientUpdate,
        session: Session = Depends(get_session)):
    """Admin: rename an ingredient.

    Raises:
        IngredientNotFoundError: 404 if no ingredient has this ID.
    """

    service = IngredientService(session)
    return service.update_ingredient(ingredient_id, ingredient)


@router.delete("/{ingredient_id}", dependencies=[Depends(get_current_admin_user)])
def delete_ingredient(
        ingredient_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Admin: delete an ingredient.

    Raises:
        IngredientNotFoundError: 404 if no ingredient has this ID.
    """

    service = IngredientService(session)
    return service.delete_ingredient(ingredient_id)