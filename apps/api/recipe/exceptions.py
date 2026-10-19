"""HTTP errors raised by the recipe service."""

from fastapi import HTTPException, status

class DuplicateRecipeNameError(HTTPException):
    """409: the user already has a recipe with this name."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Recipe name already exists"
        )

class RecipeNotFoundError(HTTPException):
    """404: no recipe has this ID."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )

class NoTagInRecipeError(HTTPException):
    """404: the payload has no tags, or a tag has neither an ID nor a new name."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found in the recipe"
        )


class NoIngredientInRecipeError(HTTPException):
    """404: the payload has no usable ingredient (none with an ID or a name)."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found in the recipe"
        )


class NoInstructionInRecipeError(HTTPException):
    """404: the payload has no instructions, or one has neither an ID nor a title and details."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructions not found in the recipe"
        )

class NoImageInRecipeError(HTTPException):
    """404: an image in the payload has neither an ID nor new base64 data."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Images not found in the recipe"
        )


class EmptyRecipeUpdateError(HTTPException):
    """400: the update body has no fields set."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

class NotUserRecipeError(HTTPException):
    """403: the recipe belongs to another user."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Wrong user provided"
        )