"""HTTP errors raised by the ingredient service."""

from fastapi import HTTPException, status

class DuplicateIngredientNameError(HTTPException):
    """409: an ingredient with this name already exists."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ingredient name already exists"
        )

class IngredientNotFoundError(HTTPException):
    """404: no ingredient has this ID."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found"
        )