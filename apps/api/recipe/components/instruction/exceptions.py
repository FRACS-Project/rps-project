"""HTTP errors raised by the instruction service."""

from fastapi import HTTPException, status

# class DuplicateInstructionNameError(HTTPException):
#     """Raised when a Instruction name is already in use."""
#     def __init__(self):
#         super().__init__(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Instruction name already exists"
#         )

class InstructionNotFoundError(HTTPException):
    """404: no instruction has this ID."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instruction not found"
        )