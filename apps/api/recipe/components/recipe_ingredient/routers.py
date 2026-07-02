##############################################################################################################
#
# Recipe-ingredient management router providing CRUD operations for recipe-ingredient relationships.
#
# This module implements the REST API endpoints for managing recipe-ingredient relationships,
# including creation, retrieval, updating, and deletion of recipe-ingredient associations.
#
##############################################################################################################

import uuid
from fastapi import APIRouter, Depends
from sqlmodel import Session

from ....db import get_session
from ....utils import (
    LimitQuery,
    OffsetQuery,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)
from ....core import get_current_admin_user, get_current_active_user
from .services import RecipeIngredientService
from .schemas import (
    RecipeIngredientCreate,
    RecipeIngredientPublic,
    RecipeIngredientPublicWithAll,
    RecipeIngredientUpdate
)

router = APIRouter(
    prefix="/recipe_ingredient",
    tags=["RecipeIngredient"],
    dependencies=[Depends(get_current_active_user)]
)


@router.post("/", response_model=RecipeIngredientPublicWithAll, dependencies=[Depends(get_current_admin_user)])
def create_recipe_ingredient(
    recipe_ingredient: RecipeIngredientCreate,
    session: Session = Depends(get_session)
) -> RecipeIngredientPublic:
    """Create a recipe-ingredient relationship.

    Args:
        recipe_ingredient (RecipeIngredientCreate): Relationship payload.
        session (Session): Database session dependency.

    Returns:
        RecipeIngredientPublic: Created relationship data.
    """
    service = RecipeIngredientService(session)
    return service.create_recipe_ingredient(recipe_ingredient)


@router.get("/", response_model=list[RecipeIngredientPublicWithAll])
def get_recipe_ingredients(
    offset: OffsetQuery = DEFAULT_OFFSET,
    limit: LimitQuery = DEFAULT_LIMIT,
    session: Session = Depends(get_session)
) -> list[RecipeIngredientPublicWithAll]:
    """Retrieve a paginated list of recipe-ingredient relationships.

    Args:
        offset (OffsetQuery): Number of relationships to skip (for pagination).
        limit (LimitQuery): Maximum number of relationships to return.
        session (Session): Database session dependency.

    Returns:
        List[RecipeIngredientPublicWithAll]: List of relationships with ingredient data.
    """
    service = RecipeIngredientService(session)
    return service.get_recipe_ingredients(offset, limit)


@router.get("/{recipe_ingredient_id}", response_model=RecipeIngredientPublicWithAll)
def get_recipe_ingredient(
    recipe_ingredient_id: uuid.UUID,
    session: Session = Depends(get_session)
) -> RecipeIngredientPublic:
    """Retrieve a specific recipe-ingredient relationship by ID.

    Args:
        recipe_ingredient_id (UUID): The unique identifier of the relationship.
        session (Session): Database session dependency.

    Returns:
        RecipeIngredientPublic: Relationship data.
    """
    service = RecipeIngredientService(session)
    return service.get_recipe_ingredient(recipe_ingredient_id)





@router.patch("/{recipe_ingredient_id}", response_model=RecipeIngredientPublicWithAll, dependencies=[Depends(get_current_admin_user)])
def update_recipe_ingredient(
    recipe_ingredient_id: uuid.UUID,
    recipe_ingredient: RecipeIngredientUpdate,
    session: Session = Depends(get_session)
):
    """Update a specific recipe-ingredient relationship by ID.

    Args:
        recipe_ingredient_id (UUID): The unique identifier of the relationship.
        recipe_ingredient (RecipeIngredientUpdate): Fields to update.
        session (Session): Database session dependency.

    Returns:
        RecipeIngredientPublic: Updated relationship data.
    """
    service = RecipeIngredientService(session)
    return service.update_recipe_ingredient(recipe_ingredient_id, recipe_ingredient)


@router.delete("/{recipe_ingredient_id}", dependencies=[Depends(get_current_admin_user)])
def delete_recipe_ingredient(
    recipe_ingredient_id: uuid.UUID,
    session: Session = Depends(get_session)
) -> dict[str, bool]:
    """Delete a recipe-ingredient relationship by ID.

    Args:
        recipe_ingredient_id (UUID): The unique identifier of the relationship.
        session (Session): Database session dependency.

    Returns:
        dict[str, bool]: Confirmation message.
    """
    service = RecipeIngredientService(session)
    return service.delete_recipe_ingredient(recipe_ingredient_id)
