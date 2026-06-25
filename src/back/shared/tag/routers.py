##############################################################################################################
#
# Tag Management Routes
#
# This module provides HTTP endpoints for Tag management.
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
    TagCreate,
    TagPublic,
    TagUpdate
)

from ...utils import (
    LimitQuery,
    OffsetQuery,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)

from .services import TagService
from ...db import get_session
from ...core import get_current_admin_user, get_current_active_user

router = APIRouter(
    prefix="/tag",
    tags=["Tag"],
    dependencies=[Depends(get_current_active_user)]
)


@router.post("/", response_model=TagPublic, dependencies=[Depends(get_current_admin_user)])
def create_tag(tag: TagCreate,
               session: Session = Depends(get_session)):
    """Create a new Tag.

    Args:
        tag (TagCreate): Tag payload.
        session (Session): Database session dependency.

    Returns:
        TagPublic: Created Tag data.
    """
    service = TagService(session)
    return service.create_tag(tag)


@router.get("/", response_model=list[TagPublic])
def get_tags(
        offset: OffsetQuery = DEFAULT_OFFSET,
        limit: LimitQuery = DEFAULT_LIMIT,
        session: Session = Depends(get_session)):
    """Retrieve a paginated list of Tags.

    Args:
        offset (OffsetQuery): Number of tags to skip (for pagination).
        limit (LimitQuery): Maximum number of tags to return.
        session (Session): Database session dependency.

    Returns:
        List[TagPublic]: List of tags.
    """
    service = TagService(session)
    return service.get_tags(offset, limit)


@router.get("/{tag_id}", response_model=TagPublic)
def get_tag(
        tag_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Retrieve a specific Tag by its ID.

    Args:
        tag_id (UUID): The unique identifier of the tag.
        session (Session): The database session dependency.

    Returns:
        TagPublic: The tag data.
    """

    service = TagService(session)
    return service.get_tag(tag_id)


@router.patch("/{tag_id}", response_model=TagPublic, dependencies=[Depends(get_current_admin_user)])
def update_tag(
        tag_id: uuid.UUID,
        tag: TagUpdate,
        session: Session = Depends(get_session)):
    """Update a specific Tag by its ID.

    Args:
        tag_id (UUID): The unique identifier of the tag.
        tag (TagUpdate): Fields to update and their new values.
        session (Session): The database session dependency.

    Returns:
        TagPublic: The updated tag data.
    """

    service = TagService(session)
    return service.update_tag(tag_id, tag)


@router.delete("/{tag_id}", dependencies=[Depends(get_current_admin_user)])
def delete_tag(
        tag_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Delete a Tag by its ID.

    Args:
        tag_id (UUID): The unique identifier of the tag.
        session (Session): The database session dependency.

    Returns:
        dict: Confirmation message.
    """

    service = TagService(session)
    return service.delete_tag(tag_id)
