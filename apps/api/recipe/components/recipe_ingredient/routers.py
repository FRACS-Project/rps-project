"""Recipe ingredient endpoints under `/recipe_ingredient`.

Login required for reads; writes are admin only. Users edit ingredient
lines through `PATCH /recipe/me/{recipe_id}` instead.
"""

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
    """Admin: add an ingredient line to any recipe.

    Raises:
        DuplicateRecipeIngredientError: 409 if the recipe already uses this ingredient.
    """
    service = RecipeIngredientService(session)
    return service.create_recipe_ingredient(recipe_ingredient)


@router.get("/", response_model=list[RecipeIngredientPublicWithAll])
def get_recipe_ingredients(
    offset: OffsetQuery = DEFAULT_OFFSET,
    limit: LimitQuery = DEFAULT_LIMIT,
    session: Session = Depends(get_session)
) -> list[RecipeIngredientPublicWithAll]:
    """List ingredient lines from all recipes, paginated with `offset` and `limit`."""
    service = RecipeIngredientService(session)
    return service.get_recipe_ingredients(offset, limit)


@router.get("/{recipe_ingredient_id}", response_model=RecipeIngredientPublicWithAll)
def get_recipe_ingredient(
    recipe_ingredient_id: uuid.UUID,
    session: Session = Depends(get_session)
) -> RecipeIngredientPublic:
    """Get an ingredient line by ID.

    Raises:
        RecipeIngredientNotFoundError: 404 if no line has this ID.
    """
    service = RecipeIngredientService(session)
    return service.get_recipe_ingredient(recipe_ingredient_id)





@router.patch("/{recipe_ingredient_id}", response_model=RecipeIngredientPublicWithAll, dependencies=[Depends(get_current_admin_user)])
def update_recipe_ingredient(
    recipe_ingredient_id: uuid.UUID,
    recipe_ingredient: RecipeIngredientUpdate,
    session: Session = Depends(get_session)
):
    """Admin: partially update an ingredient line.

    Raises:
        RecipeIngredientNotFoundError: 404 if no line has this ID.
    """
    service = RecipeIngredientService(session)
    return service.update_recipe_ingredient(recipe_ingredient_id, recipe_ingredient)


@router.delete("/{recipe_ingredient_id}", dependencies=[Depends(get_current_admin_user)])
def delete_recipe_ingredient(
    recipe_ingredient_id: uuid.UUID,
    session: Session = Depends(get_session)
) -> dict[str, bool]:
    """Admin: delete an ingredient line.

    Raises:
        RecipeIngredientNotFoundError: 404 if no line has this ID.
    """
    service = RecipeIngredientService(session)
    return service.delete_recipe_ingredient(recipe_ingredient_id)
