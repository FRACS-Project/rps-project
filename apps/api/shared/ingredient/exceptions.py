##############################################################################################################
#
# Ingredient Exceptions
#
# HTTPException subclasses used by the Ingredient service layer for consistent API errors.
#
##############################################################################################################

from fastapi import HTTPException, status

class DuplicateIngredientNameError(HTTPException):
    """Raised when an ingredient name is already in use."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ingredient name already exists"
        )

class IngredientNotFoundError(HTTPException):
    """Raised when an ingredient lookup fails."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found"
        )