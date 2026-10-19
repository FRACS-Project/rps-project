"""HTTP errors raised by the recipe ingredient service."""

from fastapi import HTTPException, status


class DuplicateRecipeIngredientError(HTTPException):
	"""409: the recipe already uses this ingredient."""

	def __init__(self):
		super().__init__(
			status_code=status.HTTP_409_CONFLICT,
			detail="Ingredient already added to this recipe",
		)


class RecipeIngredientNotFoundError(HTTPException):
	"""404: no recipe ingredient has this ID."""

	def __init__(self):
		super().__init__(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Recipe ingredient not found",
		)
