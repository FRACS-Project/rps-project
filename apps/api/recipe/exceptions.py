##############################################################################################################
#
# Recipe Exceptions
#
# HTTPException subclasses used by the recipe service layer for consistent API errors.
#
##############################################################################################################

from fastapi import HTTPException, status

class DuplicateRecipeNameError(HTTPException):
    """Raised when a recipe name is already in use."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Recipe name already exists"
        )

class RecipeNotFoundError(HTTPException):
    """Raised when a recipe lookup fails."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )

class NoTagInRecipeError(HTTPException):
    """Raised when there is no tag in a recipe."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found in the recipe"
        )


class NoIngredientInRecipeError(HTTPException):
    """Raised when there is no ingredient in a recipe."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found in the recipe"
        )


class NoInstructionInRecipeError(HTTPException):
    """Raised when there are no instructions in a recipe."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructions not found in the recipe"
        )

class NoImageInRecipeError(HTTPException):
    """Raised when there are no instructions in a recipe."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Images not found in the recipe"
        )


class EmptyRecipeUpdateError(HTTPException):
    """Raised when no fields are provided for a recipe update."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

class NotUserRecipeError(HTTPException):
    """Raised when the user id is not the same as the owner id of the recipe"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Wrong user provided"
        )