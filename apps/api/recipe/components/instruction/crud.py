"""Database access for instructions. No validation; the service layer handles that.

`pre_*` methods only flush, so they can run inside a recipe transaction
that is committed once.
"""

import uuid
from sqlmodel import Session, select

from . import Instruction 
from .schemas import InstructionCreate


class InstructionCrud:
    """Queries and writes for the instruction table."""

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db

    def create_instruction(self, instruction: InstructionCreate) -> Instruction:
        """Insert an instruction and commit."""
        db_instruction = Instruction.model_validate(instruction)
        self.db.add(db_instruction)
        self.db.commit()
        self.db.refresh(db_instruction)
        return db_instruction
    
    def pre_create_instruction(self, instruction: InstructionCreate) -> Instruction:
        """Add an instruction and flush without committing."""
        db_instruction = Instruction.model_validate(instruction)
        self.db.add(db_instruction)
        self.db.flush()
        return db_instruction

    def read_instructions(self, offset: int = 0, limit: int = 100) -> list[Instruction]:
        """Return a page of instructions from all recipes."""
        return self.db.exec(select(Instruction).offset(offset).limit(limit)).all()

    def read_instruction(self, instruction_id: uuid.UUID) -> Instruction | None:
        """Return the instruction with this ID, or None."""
        return self.db.get(Instruction, instruction_id)

    def update_instruction(self, db_instruction: Instruction, instruction: dict) -> Instruction:
        """Apply the given fields to an instruction and commit."""
        db_instruction.sqlmodel_update(instruction)
        self.db.add(db_instruction)
        self.db.commit()
        self.db.refresh(db_instruction)
        return db_instruction
    
    def pre_update_instruction(self, db_instruction: Instruction, instruction: dict) -> Instruction:
        """Apply the given fields to an instruction and flush without committing."""
        db_instruction.sqlmodel_update(instruction)
        self.db.add(db_instruction)
        self.db.flush()
        return db_instruction

    def delete_instruction(self, db_instruction: Instruction) -> dict:
        """Delete an instruction and commit."""
        self.db.delete(db_instruction)
        self.db.commit()
        return {"ok": True}
    
    def pre_delete_instruction(self, db_instruction: Instruction) -> dict:
        """Mark an instruction for deletion without committing."""
        self.db.delete(db_instruction)
        return {"ok": True}
