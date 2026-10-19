"""Instruction endpoints under `/instruction`.

Login required for reads; writes are admin only. Users edit steps through
`PATCH /recipe/me/{recipe_id}` instead.
"""

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
    """Admin: add a step to any recipe."""
    service = InstructionService(session)
    return service.create_instruction(instruction)


@router.get("/", response_model=list[InstructionPublic])
def get_instructions(
        offset: OffsetQuery = DEFAULT_OFFSET,
        limit: LimitQuery = DEFAULT_LIMIT,
        session: Session = Depends(get_session)):
    """List steps from all recipes, paginated with `offset` and `limit`."""
    service = InstructionService(session)
    return service.get_instructions(offset, limit)


@router.get("/{instruction_id}", response_model=InstructionPublic)
def get_instruction(
        instruction_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Get a step by ID.

    Raises:
        InstructionNotFoundError: 404 if no instruction has this ID.
    """

    service = InstructionService(session)
    return service.get_instruction(instruction_id)


@router.patch("/{instruction_id}", response_model=InstructionPublic, dependencies=[Depends(get_current_admin_user)])
def update_instruction(
        instruction_id: uuid.UUID,
        instruction: InstructionUpdate,
        session: Session = Depends(get_session)):
    """Admin: partially update a step.

    Raises:
        InstructionNotFoundError: 404 if no instruction has this ID.
    """

    service = InstructionService(session)
    return service.update_instruction(instruction_id, instruction)


@router.delete("/{instruction_id}", dependencies=[Depends(get_current_admin_user)])
def delete_instruction(
        instruction_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Admin: delete a step.

    Raises:
        InstructionNotFoundError: 404 if no instruction has this ID.
    """

    service = InstructionService(session)
    return service.delete_instruction(instruction_id)
