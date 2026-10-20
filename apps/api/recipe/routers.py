"""Recipe endpoints under `/recipe`.

- `/recipe/me...`: the logged-in user's recipes (create, list, get, edit, delete).
- `/recipe/...`: public reads of any recipe, and admin-only writes.
"""

import uuid
from fastapi import APIRouter, Depends
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
    dependencies=[Depends(get_current_active_user)]
)


@router.post("/me", response_model=RecipePublicWithAll)
def create_my_recipe(
        recipe: NewRecipe,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """Create a recipe with its ingredients, tags, instructions and images.

    Raises:
        DuplicateRecipeNameError: 409 if you already have a recipe with this name.
        NoIngredientInRecipeError: 404 if the ingredients are missing or invalid.
        NoTagInRecipeError: 404 if the tags are missing or invalid.
        NoInstructionInRecipeError: 404 if the instructions are missing or invalid.
        NoImageInRecipeError: 404 if an image has neither an ID nor data.
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
    """List your recipes, paginated with `offset` and `limit`."""
    service = RecipeService(session)
    return service.get_recipes_by_user(offset, limit, current_user.id)


@router.get("/me/{recipe_id}", response_model=RecipePublicWithAll)
def get_my_recipe(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """Get one of your recipes.

    Raises:
        RecipeNotFoundError: 404 if no recipe has this ID.
        NotUserRecipeError: 403 if the recipe is not yours.
    """

    service = RecipeService(session)
    return service.get_recipe_by_user(recipe_id, current_user.id)


@router.patch("/me/{recipe_id}", response_model=RecipePublicWithAll)
def update_my_recipe(
        recipe_id: uuid.UUID,
        recipe: PatchRecipe,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """Edit one of your recipes. Send the full recipe: missing ingredients, tags and steps are removed.

    Raises:
        RecipeNotFoundError: 404 if no recipe has this ID.
        NotUserRecipeError: 403 if the recipe is not yours.
        DuplicateRecipeNameError: 409 if you already have another recipe with this name.
    """

    service = RecipeService(session)
    return service.update_recipe_by_user(recipe_id, recipe, current_user.id)


@router.delete("/me/{recipe_id}")
def delete_my_recipe(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session),
        current_user: UserPublic = Depends(get_current_active_user)
):
    """Delete one of your recipes.

    Raises:
        RecipeNotFoundError: 404 if no recipe has this ID.
        NotUserRecipeError: 403 if the recipe is not yours.
    """

    service = RecipeService(session)
    return service.delete_recipe_by_user(recipe_id, current_user.id)


@router.post("/", response_model=RecipePublic, dependencies=[Depends(get_current_admin_user)])
def create_recipe(
        recipe: RecipeCreate,
        session: Session = Depends(get_session)
):
    """Admin: create a recipe row for any owner, without related data.

    Raises:
        DuplicateRecipeNameError: 409 if any recipe already has this name.
    """
    service = RecipeService(session)
    return service.create_recipe(recipe)


@router.get("/", response_model=list[RecipePublicWithAll])
def get_recipes(
        offset: OffsetQuery = DEFAULT_OFFSET,
        limit: LimitQuery = DEFAULT_LIMIT,
        session: Session = Depends(get_session)
):
    """List recipes from all users, paginated with `offset` and `limit`."""
    service = RecipeService(session)
    return service.get_recipes(offset, limit)


@router.get("/{recipe_id}", response_model=RecipePublicWithAll)
def get_recipe(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session)
):
    """Get any recipe by ID.

    Raises:
        RecipeNotFoundError: 404 if no recipe has this ID.
    """

    service = RecipeService(session)
    return service.get_recipe(recipe_id)


@router.get("/{recipe_id}/images", response_model=list[ImagePublic])
def get_recipe_images(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session)
):
    """List the recipe's active images."""

    service = RecipeService(session)

    return service.get_recipe_images(recipe_id)


@router.get("/{recipe_id}/images/primary", response_model=ImagePublic)
def get_recipe_image_primary(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session)
):
    """Get the recipe's primary image.

    Raises:
        ImageNotFoundError: 404 if the recipe has no primary image.
    """

    service = RecipeService(session)

    return service.get_recipe_image_primary(recipe_id)


@router.patch(
        "/{recipe_id}",
        response_model=RecipePublicWithAll,
        dependencies=[Depends(get_current_admin_user)]
)
def update_recipe(
        recipe_id: uuid.UUID,
        recipe: RecipeUpdate,
        session: Session = Depends(get_session)
):
    """Admin: partially update any recipe's fields. Only the fields sent are changed.

    Raises:
        RecipeNotFoundError: 404 if no recipe has this ID.
        EmptyRecipeUpdateError: 400 if no field is sent.
    """

    service = RecipeService(session)
    return service.update_recipe(recipe_id, recipe)


@router.delete("/{recipe_id}", dependencies=[Depends(get_current_admin_user)])
def delete_recipe(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session)
):
    """Admin: delete any recipe.

    Raises:
        RecipeNotFoundError: 404 if no recipe has this ID.
    """

    service = RecipeService(session)
    return service.delete_recipe(recipe_id)
