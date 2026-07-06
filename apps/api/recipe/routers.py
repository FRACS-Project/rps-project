##############################################################################################################
#
# Recipe Management Routes
#
# This module provides HTTP endpoints for recipe management.
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
    RecipeCreate,
    RecipePublic,
    RecipeUpdate,
    RecipePublicWithAll,
    NewRecipe,
    PatchRecipe
)

from ..shared.image.schemas import ImagePublic

from ..utils import (
    LimitQuery,
    OffsetQuery,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)

from .services import RecipeService
from ..user.schemas import UserPublic
from ..db import get_session
from ..core import get_current_admin_user, get_current_active_user

router = APIRouter(
    prefix="/recipe",
    tags=["Recipe"],
    # dependencies=[Depends(get_current_active_user)]
)


@router.post("/me", response_model=RecipePublicWithAll)
def create_new_recipe(
        recipe: NewRecipe,
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

    service = RecipeService(session)
    return service.create_recipe_by_user(recipe, current_user.id)


@router.get("/me", response_model=list[RecipePublicWithAll])
def get_my_recipes(
        offset: OffsetQuery = DEFAULT_OFFSET,
        limit: LimitQuery = DEFAULT_LIMIT,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """Retrieve recipes created by the current user.

    Args:
        offset (OffsetQuery): Number of recipes to skip (for pagination).
        limit (LimitQuery): Maximum number of recipes to return.
        session (Session): Database session dependency.
        current_user (UserPublic): Current authenticated user.

    Returns:
        List[RecipePublicWithAll]: List of user's recipes with related data.
    """
    service = RecipeService(session)
    return service.get_recipes_by_user(offset, limit, current_user.id)


@router.get("/me/{recipe_id}", response_model=RecipePublicWithAll)
def get_my_recipe(
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

    service = RecipeService(session)
    return service.get_recipe(recipe_id, current_user.id)


@router.patch("/me/{recipe_id}", response_model=RecipePublicWithAll)
def update_recipe(
        recipe_id: uuid.UUID,
        recipe: PatchRecipe,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """Update a specific recipe by its ID.

    Args:
        recipe_id (UUID): The unique identifier of the recipe.
        recipe (RecipeUpdate): Fields to update and their new values.
        session (Session): The database session dependency.
        current_user (UserPublic): Current authenticated user.

    Returns:
        RecipePublicWithAll: The updated recipe data.
    """

    service = RecipeService(session)
    return service.update_recipe_by_user(recipe_id, recipe, current_user.id)


@router.delete("/me/{recipe_id}")
def delete_recipe(
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

    service = RecipeService(session)
    return service.delete_recipe_by_user(recipe_id, current_user.id)


@router.post("/", response_model=RecipePublic, dependencies=[Depends(get_current_admin_user)])
def create_recipe(recipe: RecipeCreate,
                  session: Session = Depends(get_session)):
    """Create a new recipe.

    Args:
        recipe (RecipeCreate): Recipe payload.
        session (Session): Database session dependency.

    Returns:
        RecipePublic: Created recipe data.
    """
    service = RecipeService(session)
    return service.create_recipe(recipe)


@router.get("/", response_model=list[RecipePublicWithAll])
def get_recipes(
        offset: OffsetQuery = DEFAULT_OFFSET,
        limit: LimitQuery = DEFAULT_LIMIT,
        session: Session = Depends(get_session)):
    """Retrieve a paginated list of recipes.

    Args:
        offset (OffsetQuery): Number of recipes to skip (for pagination).
        limit (LimitQuery): Maximum number of recipes to return.
        session (Session): Database session dependency.

    Returns:
        List[RecipePublicWithAll]: List of recipes with related data.
    """
    service = RecipeService(session)
    return service.get_recipes(offset, limit)


@router.get("/{recipe_id}", response_model=RecipePublicWithAll)
def get_recipe(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Retrieve a specific recipe by its ID.

    Args:
        recipe_id (UUID): The unique identifier of the recipe.
        session (Session): The database session dependency.

    Returns:
        RecipePublicWithAll: The recipe with related data.
    """

    service = RecipeService(session)
    return service.get_recipe(recipe_id)


@router.get("/{recipe_id}/images", response_model=list[ImagePublic])
def get_recipe_images(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session)):

    service = RecipeService(session)

    return service.get_recipe_images(recipe_id)


@router.get("/{recipe_id}/images/primary", response_model=ImagePublic)
def get_recipe_image_primary(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session)):

    service = RecipeService(session)

    return service.get_recipe_image_primary(recipe_id)


@router.patch("/{recipe_id}", response_model=RecipePublicWithAll, dependencies=[Depends(get_current_admin_user)])
def update_recipe(
        recipe_id: uuid.UUID,
        recipe: RecipeUpdate,
        session: Session = Depends(get_session)):
    """Update a specific recipe by its ID.

    Args:
        recipe_id (UUID): The unique identifier of the recipe.
        recipe (RecipeUpdate): Fields to update and their new values.
        session (Session): The database session dependency.

    Returns:
        RecipePublicWithAll: The updated recipe data.
    """

    service = RecipeService(session)
    return service.update_recipe(recipe_id, recipe)


@router.delete("/{recipe_id}", dependencies=[Depends(get_current_admin_user)])
def delete_recipe(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Delete a recipe by its ID.

    Args:
        recipe_id (UUID): The unique identifier of the recipe.
        session (Session): The database session dependency.

    Returns:
        dict: Confirmation message.
    """

    service = RecipeService(session)
    return service.delete_recipe(recipe_id)
