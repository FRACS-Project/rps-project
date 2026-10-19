"""Recipe ingredient service.

Single-line CRUD for the admin routes, plus the `sync_*` methods that
`RecipeService` calls to write a recipe's ingredient lines (creating new
ingredients when needed) inside its transaction.
"""

import uuid
from sqlmodel import Session

from . import (
    RecipeIngredient,
    DuplicateRecipeIngredientError,
    RecipeIngredientNotFoundError,
)

from .schemas import (
    RecipeIngredientCreate,
    RecipeIngredientUpdate,
    PatchRecipeIngredient,
    NewRecipeIngredient
)

from .crud import RecipeIngredientCrud

from ....shared.ingredient.services import IngredientService
from ....shared.ingredient.schemas import IngredientCreate

from ...models import Recipe

from ....utils import (
    LimitQuery,
    OffsetQuery,
    DEFAULT_LIMIT,
    DEFAULT_OFFSET
)


class RecipeIngredientService:
    """Business logic for recipe ingredient lines."""

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session, also used to create new ingredients.
        """
        self.db = db
        self.crud = RecipeIngredientCrud(self.db)
        self.ingredient_service = IngredientService(self.db)

    def create_recipe_ingredient(self, recipe_ingredient: RecipeIngredientCreate) -> RecipeIngredient:
        """Add an ingredient line to a recipe and commit.

        Raises:
            DuplicateRecipeIngredientError: If the recipe already uses this ingredient.
        """
        existing = self.crud.get_recipe_ingredient_by_pair(
            recipe_ingredient.recipe_id,
            recipe_ingredient.ingredient_id,
        )
        if existing:
            raise DuplicateRecipeIngredientError()

        return self.crud.create_recipe_ingredient(recipe_ingredient)
    
    def pre_create_recipe_ingredient(self, recipe_ingredient: RecipeIngredientCreate) -> RecipeIngredient:
        """Add an ingredient line to a recipe without committing.

        Raises:
            DuplicateRecipeIngredientError: If the recipe already uses this ingredient.
        """
        existing = self.crud.get_recipe_ingredient_by_pair(
            recipe_ingredient.recipe_id,
            recipe_ingredient.ingredient_id,
        )
        if existing:
            raise DuplicateRecipeIngredientError()

        return self.crud.pre_create_recipe_ingredient(recipe_ingredient)

    def get_recipe_ingredients(self, offset: OffsetQuery = DEFAULT_OFFSET, limit: LimitQuery = DEFAULT_LIMIT) -> list[RecipeIngredient]:
        """Return a page of recipe ingredient lines from all recipes."""
        return self.crud.read_recipe_ingredients(offset, limit)

    def get_recipe_ingredient(self, recipe_ingredient_id: uuid.UUID) -> RecipeIngredient:
        """Return a recipe ingredient line by ID.

        Raises:
            RecipeIngredientNotFoundError: If no line has this ID.
        """
        recipe_ingredient = self.crud.read_recipe_ingredient(
            recipe_ingredient_id)
        if not recipe_ingredient:
            raise RecipeIngredientNotFoundError()

        return recipe_ingredient

    def update_recipe_ingredient(
        self,
        recipe_ingredient_id: uuid.UUID,
        recipe_ingredient: RecipeIngredientUpdate | PatchRecipeIngredient,
    ) -> RecipeIngredient:
        """Partially update a line and commit.

        Args:
            recipe_ingredient_id: ID of the line.
            recipe_ingredient: Fields to change.

        Returns:
            The updated line.

        Raises:
            RecipeIngredientNotFoundError: If no line has this ID.
        """
        db_recipe_ingredient = self.crud.read_recipe_ingredient(
            recipe_ingredient_id)
        if not db_recipe_ingredient:
            raise RecipeIngredientNotFoundError()

        recipe_ingredient_data = recipe_ingredient.model_dump(
            exclude_unset=True)
        return self.crud.update_recipe_ingredient(db_recipe_ingredient, recipe_ingredient_data)
    
    def pre_update_recipe_ingredient(
        self,
        recipe_ingredient_id: uuid.UUID,
        recipe_ingredient: RecipeIngredientUpdate,
    ) -> RecipeIngredient:
        """Partially update a line without committing.

        Args:
            recipe_ingredient_id: ID of the line.
            recipe_ingredient: Fields to change.

        Returns:
            The updated line.

        Raises:
            RecipeIngredientNotFoundError: If no line has this ID.
        """
        db_recipe_ingredient = self.crud.read_recipe_ingredient(
            recipe_ingredient_id)
        if not db_recipe_ingredient:
            raise RecipeIngredientNotFoundError()

        recipe_ingredient_data = recipe_ingredient.model_dump(exclude_unset=True)
        return self.crud.pre_update_recipe_ingredient(db_recipe_ingredient, recipe_ingredient_data)

    def delete_recipe_ingredient(self, recipe_ingredient_id: uuid.UUID) -> dict:
        """Delete a line and commit.

        Raises:
            RecipeIngredientNotFoundError: If no line has this ID.
        """
        db_recipe_ingredient = self.crud.read_recipe_ingredient(
            recipe_ingredient_id)
        if not db_recipe_ingredient:
            raise RecipeIngredientNotFoundError()

        return self.crud.delete_recipe_ingredient(db_recipe_ingredient)
    
    def pre_delete_recipe_ingredient(self, recipe_ingredient_id: uuid.UUID) -> dict:
        """Delete a line without committing.

        Raises:
            RecipeIngredientNotFoundError: If no line has this ID.
        """
        db_recipe_ingredient = self.crud.read_recipe_ingredient(
            recipe_ingredient_id)
        if not db_recipe_ingredient:
            raise RecipeIngredientNotFoundError()

        return self.crud.pre_delete_recipe_ingredient(db_recipe_ingredient)

    def sync_ingredients_on_create(
            self,
            recipe_id: uuid.UUID,
            ingredients: list[NewRecipeIngredient]
    ) -> None:
        """Create the ingredient lines of a new recipe. Does not commit.

        `new` ingredients are created first, then linked.

        Args:
            recipe_id: ID of the new recipe.
            ingredients: Lines from the `NewRecipe` body.
        """
        for ingredient in ingredients:
            if ingredient.new:
                created_ingredient = self.ingredient_service.pre_create_ingredient(
                    IngredientCreate(name=ingredient.name)
                )
                ingredient.ingredient_id = created_ingredient.id
            # Create RecipeIngredient
            self._create_recipe_ingredient(ingredient, recipe_id)

    def sync_ingredients_on_update(
            self,
            db_recipe: Recipe,
            ingredients: list[PatchRecipeIngredient]
        ) -> None:
        """Make the recipe's ingredient lines match the payload. Does not commit.

        Lines whose `recipe_ingredient_id` is missing from the payload are deleted,
        lines with one are updated, and the others are added. `new` ingredients
        are created first.

        Args:
            db_recipe: Recipe being edited.
            ingredients: Full list of lines from the `PatchRecipe` body.
        """
        new_recipe_ingredient_ids = {
            ingredient.recipe_ingredient_id
            for ingredient in ingredients
            if ingredient.recipe_ingredient_id  # Filter out None
        }

        recipe_ingredient_ids_to_delete = {
            ingredient.id
            for ingredient in db_recipe.ingredients
            if ingredient.id not in new_recipe_ingredient_ids
        }

        for recipe_ingredient_id in recipe_ingredient_ids_to_delete:
            self.pre_delete_recipe_ingredient(recipe_ingredient_id)

        db_recipe.ingredients = [
            ingredient
            for ingredient in db_recipe.ingredients 
            if ingredient.id not in recipe_ingredient_ids_to_delete
        ]

        for ingredient in ingredients:
            if ingredient.new:
                created_ingredient = self.ingredient_service.pre_create_ingredient(
                    IngredientCreate(name=ingredient.name)
                )
                ingredient.ingredient_id = created_ingredient.id

            if ingredient.recipe_ingredient_id and not ingredient.new:
                self.pre_update_recipe_ingredient(
                    ingredient.recipe_ingredient_id,
                    RecipeIngredientUpdate(
                        quantity=ingredient.quantity,
                        unit=ingredient.unit,
                        ingredient_id=ingredient.ingredient_id
                    )
                )
            else:
                self._create_recipe_ingredient(ingredient, db_recipe.id)

    def _create_recipe_ingredient(
            self,
            ingredient: NewRecipeIngredient | PatchRecipeIngredient,
            recipe_id: uuid.UUID
    ):
        """Add one ingredient line to the recipe without committing."""
        self.pre_create_recipe_ingredient(
            RecipeIngredientCreate(
                quantity=ingredient.quantity,
                unit=ingredient.unit,
                ingredient_id=ingredient.ingredient_id,
                recipe_id=recipe_id
            )
        )