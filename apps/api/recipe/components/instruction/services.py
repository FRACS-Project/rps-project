"""Instruction service.

Single-instruction CRUD for the admin routes, plus the `sync_*` methods
that `RecipeService` calls to write a recipe's steps inside its transaction.
"""

import uuid
from sqlmodel import Session

from . import (
    Instruction,
    InstructionNotFoundError
)

from .schemas import (
    InstructionCreate,
    InstructionUpdate,
    NewInstructionCreate,
    PatchInstruction
)

from .crud import InstructionCrud

from ...models import Recipe

from ....utils import LimitQuery, OffsetQuery

class InstructionService:
    """Business logic for instructions."""

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db
        self.crud = InstructionCrud(self.db)

    def create_instruction(self, instruction: InstructionCreate) -> Instruction:
        """Create an instruction and commit."""
        return self.crud.create_instruction(instruction)
    
    def pre_create_instruction(self, instruction: InstructionCreate) -> Instruction:
        """Create an instruction without committing."""
        return self.crud.pre_create_instruction(instruction)


    def get_instructions(self, offset: OffsetQuery = 0, limit: LimitQuery = 100) -> list[Instruction]:
        """Return a page of instructions from all recipes."""
        return self.crud.read_instructions(offset, limit)

    def get_instruction(self, instruction_id: uuid.UUID) -> Instruction:
        """Return an instruction by ID.

        Raises:
            InstructionNotFoundError: If no instruction has this ID.
        """
        instruction = self.crud.read_instruction(instruction_id)
        if not instruction:
            raise InstructionNotFoundError()

        return instruction

    def update_instruction(self, instruction_id: uuid.UUID, instruction: InstructionUpdate) -> Instruction:
        """Partially update an instruction and commit.

        Args:
            instruction_id: ID of the instruction.
            instruction: Fields to change.

        Returns:
            The updated instruction.

        Raises:
            InstructionNotFoundError: If no instruction has this ID.
        """
        db_instruction = self.crud.read_instruction(instruction_id)
        if not db_instruction:
            raise InstructionNotFoundError()
        
        instruction_data = instruction.model_dump(exclude_unset=True)
        
        return self.crud.update_instruction(db_instruction, instruction_data)
    
    def pre_update_instruction(self, instruction_id: uuid.UUID, instruction: InstructionUpdate) -> Instruction:
        """Partially update an instruction without committing.

        Args:
            instruction_id: ID of the instruction.
            instruction: Fields to change.

        Returns:
            The updated instruction.

        Raises:
            InstructionNotFoundError: If no instruction has this ID.
        """
        db_instruction = self.crud.read_instruction(instruction_id)
        if not instruction:
            raise InstructionNotFoundError()
        
        instruction_data = instruction.model_dump(exclude_unset=True)
        
        return self.crud.pre_update_instruction(db_instruction, instruction_data)

    def delete_instruction(self, instruction_id: uuid.UUID) -> dict:
        """Delete an instruction and commit.

        Raises:
            InstructionNotFoundError: If no instruction has this ID.
        """
        db_instruction = self.crud.read_instruction(instruction_id)
        if not db_instruction:
            raise InstructionNotFoundError()
        
        self.crud.delete_instruction(db_instruction)
        return {"ok": True}
    
    def pre_delete_instruction(self, instruction_id: uuid.UUID) -> dict:
        """Delete an instruction without committing.

        Raises:
            InstructionNotFoundError: If no instruction has this ID.
        """
        db_instruction = self.crud.read_instruction(instruction_id)
        if not db_instruction:
            raise InstructionNotFoundError()
        
        self.crud.pre_delete_instruction(db_instruction)
        return {"ok": True}

    def sync_instructions_on_create(
            self,
            recipe_id: uuid.UUID,
            instructions: list[NewInstructionCreate]
    ) -> None:
        """Create the steps of a new recipe. Does not commit.

        Args:
            recipe_id: ID of the new recipe.
            instructions: Steps from the `NewRecipe` body.
        """
        for instruction in instructions:
            self.pre_create_instruction(
                InstructionCreate(
                    title=instruction.title,
                    details=instruction.details,
                    recipe_id=recipe_id
                )
            )

    def sync_instructions_on_update(
            self,
            db_recipe: Recipe,
            instructions: list[PatchInstruction]
    ) -> None:
        """Make the recipe's steps match the payload. Does not commit.

        Steps whose ID is missing from the payload are deleted, steps with an ID
        are updated, and `new` steps are created.

        Args:
            db_recipe: Recipe being edited.
            instructions: Full list of steps from the `PatchRecipe` body.
        """
        new_instruction_ids = {
            instruction.id
            for instruction in instructions
            if instruction.id
        }

        instruction_ids_to_delete = {
            instruction.id
            for instruction in db_recipe.instructions
            if instruction.id not in new_instruction_ids
        }

        for instruction_id in instruction_ids_to_delete:
            self.pre_delete_instruction(instruction_id)

        db_recipe.instructions = [
            instruction
            for instruction in db_recipe.instructions
            if instruction.id not in instruction_ids_to_delete
        ]

        for instruction in instructions:
            if instruction.new:
                self.pre_create_instruction(
                    InstructionCreate(
                        title=instruction.title,
                        details=instruction.details,
                        recipe_id=db_recipe.id
                    )
                )
            elif instruction.id:
                self.pre_update_instruction(
                    instruction.id,
                    InstructionUpdate(
                        title=instruction.title,
                        details=instruction.details,
                        recipe_id=db_recipe.id
                    )
                )