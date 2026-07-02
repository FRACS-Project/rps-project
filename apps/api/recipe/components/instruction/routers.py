##############################################################################################################
#
# Instruction Management Routes
#
# This module provides HTTP endpoints for Instruction management.
# Routes handle HTTP request/response and delegate business logic to the service layer.
#
# Architecture:
#   - Routes: HTTP layer (request parsing, response formatting)
#   - Services: Business logic (validation, orchestration)
#   - CRUD: Database operations (queries, inserts, updates, deletes)
#
##############################################################################################################

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from .schemas import (
    InstructionCreate,
    InstructionPublic,
    InstructionUpdate
)

from ....utils import (
    LimitQuery,
    OffsetQuery,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)

from .services import InstructionService
from ....db import get_session
from ....core import get_current_admin_user, get_current_active_user

router = APIRouter(
    prefix="/instruction",
    tags=["Instruction"],
    dependencies=[Depends(get_current_active_user)]
)


@router.post("/", response_model=InstructionPublic, dependencies=[Depends(get_current_admin_user)])
def create_instruction(instruction: InstructionCreate,
                       session: Session = Depends(get_session)):
    """Create a new Instruction.

    Args:
        instruction (InstructionCreate): Instruction payload.
        session (Session): Database session dependency.

    Returns:
        InstructionPublic: Created Instruction data.
    """
    service = InstructionService(session)
    return service.create_instruction(instruction)


@router.get("/", response_model=list[InstructionPublic])
def get_instructions(
        offset: OffsetQuery = DEFAULT_OFFSET,
        limit: LimitQuery = DEFAULT_LIMIT,
        session: Session = Depends(get_session)):
    """Retrieve a paginated list of Instructions.

    Args:
        offset (OffsetQuery): Number of instructions to skip (for pagination).
        limit (LimitQuery): Maximum number of instructions to return.
        session (Session): Database session dependency.

    Returns:
        List[InstructionPublic]: List of instructions.
    """
    service = InstructionService(session)
    return service.get_instructions(offset, limit)


@router.get("/{instruction_id}", response_model=InstructionPublic)
def get_instruction(
        instruction_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Retrieve a specific Instruction by its ID.

    Args:
        instruction_id (UUID): The unique identifier of the instruction.
        session (Session): The database session dependency.

    Returns:
        InstructionPublic: The instruction data.
    """

    service = InstructionService(session)
    return service.get_instruction(instruction_id)


@router.patch("/{instruction_id}", response_model=InstructionPublic, dependencies=[Depends(get_current_admin_user)])
def update_instruction(
        instruction_id: uuid.UUID,
        instruction: InstructionUpdate,
        session: Session = Depends(get_session)):
    """Update a specific Instruction by its ID.

    Args:
        instruction_id (UUID): The unique identifier of the instruction.
        instruction (InstructionUpdate): Fields to update and their new values.
        session (Session): The database session dependency.

    Returns:
        InstructionPublic: The updated instruction data.
    """

    service = InstructionService(session)
    return service.update_instruction(instruction_id, instruction)


@router.delete("/{instruction_id}", dependencies=[Depends(get_current_admin_user)])
def delete_instruction(
        instruction_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Delete an instruction by its ID.

    Args:
        instruction_id (UUID): The unique identifier of the instruction.
        session (Session): The database session dependency.

    Returns:
        dict: Confirmation message.
    """

    service = InstructionService(session)
    return service.delete_instruction(instruction_id)
