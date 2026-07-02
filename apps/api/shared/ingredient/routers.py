##############################################################################################################
#
# Ingredient Management Routes
#
# This module provides HTTP endpoints for Ingredient management.
# Routes handle HTTP request/response and delegate business logic to the service layer.
#
# Architecture:
#   - Routes: HTTP layer (request parsing, response formatting)
#   - Services: Business logic (validation, orchestration)
#   - CRUD: Database operations (queries, inserts, updates, deletes)
#
##############################################################################################################

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
    """Create a new Ingredient.

    Args:
        ingredient (IngredientCreate): Ingredient payload.
        session (Session): Database session dependency.

    Returns:
        IngredientPublic: Created Ingredient data.
    """
    service = IngredientService(session)
    return service.create_ingredient(ingredient)


@router.get("/", response_model=list[IngredientPublic])
def get_ingredients(
        offset: OffsetQuery = DEFAULT_OFFSET,
        limit: LimitQuery = DEFAULT_LIMIT,
        session: Session = Depends(get_session)
):
    """Retrieve a paginated list of Ingredients.

    Args:
        offset (OffsetQuery): Number of ingredients to skip (for pagination).
        limit (LimitQuery): Maximum number of ingredients to return.
        session (Session): Database session dependency.

    Returns:
        List[IngredientPublic]: List of ingredients.
    """
    service = IngredientService(session)
    return service.get_ingredients(offset, limit)


@router.get("/{ingredient_id}", response_model=IngredientPublic)
def get_ingredient(
        ingredient_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Retrieve a specific Ingredient by its ID.

    Args:
        ingredient_id (UUID): The unique identifier of the ingredient.
        session (Session): The database session dependency.

    Returns:
        IngredientPublic: The ingredient data.
    """

    service = IngredientService(session)
    return service.get_ingredient(ingredient_id)


@router.patch("/{ingredient_id}", response_model=IngredientPublic, dependencies=[Depends(get_current_admin_user)])
def update_ingredient(
        ingredient_id: uuid.UUID,
        ingredient: IngredientUpdate,
        session: Session = Depends(get_session)):
    """Update a specific Ingredient by its ID.

    Args:
        ingredient_id (UUID): The unique identifier of the ingredient.
        ingredient (IngredientUpdate): Fields to update and their new values.
        session (Session): The database session dependency.

    Returns:
        IngredientPublic: The updated ingredient data.
    """

    service = IngredientService(session)
    return service.update_ingredient(ingredient_id, ingredient)


@router.delete("/{ingredient_id}", dependencies=[Depends(get_current_admin_user)])
def delete_ingredient(
        ingredient_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Delete a Ingredient by its ID.

    Args:
        ingredient_id (UUID): The unique identifier of the ingredient.
        session (Session): The database session dependency.

    Returns:
        dict: Confirmation message.
    """

    service = IngredientService(session)
    return service.delete_ingredient(ingredient_id)