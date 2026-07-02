##############################################################################################################
#
# CRUD operations for managing instructions in the application.
#
# This module provides functions to create, read, update, and delete instruction entities
# in the database. It handles all database interactions related to instructions.
#
##############################################################################################################

import uuid
from sqlmodel import Session, select

from . import Instruction 
from .schemas import InstructionCreate


class InstructionCrud:

    def __init__(self, db: Session):
        """Initialize InstructionCrud with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db

    def create_instruction(self, instruction: InstructionCreate) -> Instruction:
        """Create a new instruction in the database.

        Args:
            instruction (InstructionCreate): The instruction data to create.

        Returns:
            Instruction: The newly created instruction instance.    
        """
        db_instruction = Instruction.model_validate(instruction)
        self.db.add(db_instruction)
        self.db.commit()
        self.db.refresh(db_instruction)
        return db_instruction
    
    def pre_create_instruction(self, instruction: InstructionCreate) -> Instruction:
        """Create a new instruction in the database.

        Args:
            instruction (InstructionCreate): The instruction data to create.

        Returns:
            Instruction: The newly created instruction instance.    
        """
        db_instruction = Instruction.model_validate(instruction)
        self.db.add(db_instruction)
        self.db.flush()
        return db_instruction

    def read_instructions(self, offset: int = 0, limit: int = 100) -> list[Instruction]:
        """Retrieve a paginated list of instructions.

        Args:
            offset (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[Instruction]: A list of instruction instances.
        """
        return self.db.exec(select(Instruction).offset(offset).limit(limit)).all()

    def read_instruction(self, instruction_id: uuid.UUID) -> Instruction | None:
        """Retrieve a specific instruction by its ID.

        Args:
            instruction_id (uuid.UUID): The unique identifier of the instruction.

        Returns:
            Instruction | None: The found instruction instance or None if not found.
        """
        return self.db.get(Instruction, instruction_id)

    def update_instruction(self, db_instruction: Instruction, instruction: dict) -> Instruction:
        """Update an existing instruction's information.

        Args:
            db_instruction (Instruction): The existing instruction instance to update.
            instruction (InstructionUpdate): The new instruction data to apply.

        Returns:
            Instruction: The updated instruction instance.
        """
        db_instruction.sqlmodel_update(instruction)
        self.db.add(db_instruction)
        self.db.commit()
        self.db.refresh(db_instruction)
        return db_instruction
    
    def pre_update_instruction(self, db_instruction: Instruction, instruction: dict) -> Instruction:
        """Update an existing instruction's information.

        Args:
            db_instruction (Instruction): The existing instruction instance to update.
            instruction (InstructionUpdate): The new instruction data to apply.

        Returns:
            Instruction: The updated instruction instance.
        """
        db_instruction.sqlmodel_update(instruction)
        self.db.add(db_instruction)
        self.db.flush()
        return db_instruction

    def delete_instruction(self, db_instruction: Instruction) -> dict:
        """Delete an instruction from the database.

        Args:
            db_instruction (Instruction): The instruction instance to delete.

        Returns:
            dict: Confirmation message.
        """
        self.db.delete(db_instruction)
        self.db.commit()
        return {"ok": True}
    
    def pre_delete_instruction(self, db_instruction: Instruction) -> dict:
        """Delete an instruction from the database.

        Args:
            db_instruction (Instruction): The instruction instance to delete.

        Returns:
            dict: Confirmation message.
        """
        self.db.delete(db_instruction)
        return {"ok": True}
