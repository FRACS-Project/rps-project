##############################################################################################################
#
# Instruction Service Layer - Business Logic and Validation
#
# This module contains the service layer for instruction management.
# Services handle all business logic, validation, and coordinate between routes and CRUD.
#
# Architecture:
#   - Receives requests from routes (HTTP layer)
#   - Validates business rules (duplicates, existence)
#   - Coordinates CRUD operations (database layer)
#   - Handles error conditions with domain-specific exceptions
#
# Key Responsibilities:
#   - Instruction creation with duplicate name checking
#   - Instruction retrieval and pagination
#   - Instruction updates and deletion with existence validation
#
##############################################################################################################

import uuid
from sqlmodel import Session

from . import (
    Instruction,
    InstructionNotFoundError
)

from .schemas import (
    InstructionCreate,
    InstructionUpdate
)

from .crud import InstructionCrud

from ....utils import LimitQuery, OffsetQuery

class InstructionService:
    """Service layer for instruction management.

    Handles all business logic related to instructions including creation, validation,
    and lifecycle operations. Coordinates between HTTP routes and database CRUD.
    """

    def __init__(self, db: Session):
        """Initialize InstructionService with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db
        self.crud = InstructionCrud(self.db)

    def create_instruction(self, instruction: InstructionCreate) -> Instruction:
        """Create a new instruction in the database.
        
        Args:
            instruction (InstructionCreate): The instruction data to create.
            
        Returns:
            Instruction: The newly created instruction instance.
        """
        return self.crud.create_instruction(instruction)
    
    def pre_create_instruction(self, instruction: InstructionCreate) -> Instruction:
        """Create a new instruction in the database.
        
        Args:
            instruction (InstructionCreate): The instruction data to create.
            
        Returns:
            Instruction: The newly created instruction instance.
        """
        return self.crud.pre_create_instruction(instruction)


    def get_instructions(self, offset: OffsetQuery = 0, limit: LimitQuery = 100) -> list[Instruction]:
        """Retrieve a paginated list of all instructions.
        
        Args:
            offset (OffsetQuery): Number of instructions to skip (for pagination).
            limit (LimitQuery): Maximum number of instructions to return.
            
        Returns:
            List[Instruction]: List of instructions.
        """
        return self.crud.read_instructions(offset, limit)

    def get_instruction(self, instruction_id: uuid.UUID) -> Instruction:
        """Retrieve a specific instruction by ID.
        
        Args:
            instruction_id (UUID): The unique identifier of the instruction to retrieve.
            
        Returns:
            Instruction: The instruction information.
        """
        instruction = self.crud.read_instruction(instruction_id)
        if not instruction:
            raise InstructionNotFoundError()

        return instruction

    def update_instruction(self, instruction_id: uuid.UUID, instruction: InstructionUpdate) -> Instruction:
        """Update a specific instruction's information.

        This endpoint allows partial updates to an instruction's data, only modifying
        the fields that are provided in the update request.

        Args:
            instruction_id (UUID): The unique identifier of the instruction to update.
            instruction (InstructionUpdate): The fields to update and their new values.

        Returns:
            Instruction: The updated instruction instance.

        Raises:
            InstructionNotFoundError: If the instruction is not found.
        """
        db_instruction = self.crud.read_instruction(instruction_id)
        if not instruction:
            raise InstructionNotFoundError()
        
        instruction_data = instruction.model_dump(exclude_unset=True)
        
        return self.crud.update_instruction(db_instruction, instruction_data)
    
    def pre_update_instruction(self, instruction_id: uuid.UUID, instruction: InstructionUpdate) -> Instruction:
        """Update a specific instruction's information.

        This endpoint allows partial updates to an instruction's data, only modifying
        the fields that are provided in the update request.

        Args:
            instruction_id (UUID): The unique identifier of the instruction to update.
            instruction (InstructionUpdate): The fields to update and their new values.

        Returns:
            Instruction: The updated instruction instance.

        Raises:
            InstructionNotFoundError: If the instruction is not found.
        """
        db_instruction = self.crud.read_instruction(instruction_id)
        if not instruction:
            raise InstructionNotFoundError()
        
        instruction_data = instruction.model_dump(exclude_unset=True)
        
        return self.crud.pre_update_instruction(db_instruction, instruction_data)

    def delete_instruction(self, instruction_id: uuid.UUID) -> dict:
        """Delete an instruction.

        Args:
            instruction_id (UUID): The unique identifier of the instruction to delete.

        Raises:
            InstructionNotFoundError: If the instruction is not found.
        """
        db_instruction = self.crud.read_instruction(instruction_id)
        if not db_instruction:
            raise InstructionNotFoundError()
        
        self.crud.delete_instruction(db_instruction)
        return {"ok": True}
    
    def pre_delete_instruction(self, instruction_id: uuid.UUID) -> dict:
        """Delete an instruction.

        Args:
            instruction_id (UUID): The unique identifier of the instruction to delete.

        Raises:
            InstructionNotFoundError: If the instruction is not found.
        """
        db_instruction = self.crud.read_instruction(instruction_id)
        if not db_instruction:
            raise InstructionNotFoundError()
        
        self.crud.pre_delete_instruction(db_instruction)
        return {"ok": True}
