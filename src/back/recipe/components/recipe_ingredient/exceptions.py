##############################################################################################################
#
# Recipe Ingredient Exceptions
#
# HTTPException subclasses used by the recipe ingredient service layer for consistent API errors.
#
##############################################################################################################

from fastapi import HTTPException, status


class DuplicateRecipeIngredientError(HTTPException):
	"""Raised when a recipe already contains the ingredient."""

	def __init__(self):
		super().__init__(
			status_code=status.HTTP_409_CONFLICT,
			detail="Ingredient already added to this recipe",
		)


class RecipeIngredientNotFoundError(HTTPException):
	"""Raised when a recipe-ingredient lookup fails."""

	def __init__(self):
		super().__init__(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Recipe ingredient not found",
		)
