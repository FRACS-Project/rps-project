"""Tag endpoints under `/tag`. Login required; writes are admin only."""

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
    """Admin: create a tag.

    Raises:
        DuplicateTagNameError: 409 if a tag already has this name.
    """
    service = TagService(session)
    return service.create_tag(tag)


@router.get("/", response_model=list[TagPublic])
def get_tags(
        offset: OffsetQuery = DEFAULT_OFFSET,
        limit: LimitQuery = DEFAULT_LIMIT,
        session: Session = Depends(get_session)):
    """List tags, paginated with `offset` and `limit`."""
    service = TagService(session)
    return service.get_tags(offset, limit)


@router.get("/{tag_id}", response_model=TagPublic)
def get_tag(
        tag_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Get a tag by ID.

    Raises:
        TagNotFoundError: 404 if no tag has this ID.
    """

    service = TagService(session)
    return service.get_tag(tag_id)


@router.patch("/{tag_id}", response_model=TagPublic, dependencies=[Depends(get_current_admin_user)])
def update_tag(
        tag_id: uuid.UUID,
        tag: TagUpdate,
        session: Session = Depends(get_session)):
    """Admin: rename a tag.

    Raises:
        TagNotFoundError: 404 if no tag has this ID.
    """

    service = TagService(session)
    return service.update_tag(tag_id, tag)


@router.delete("/{tag_id}", dependencies=[Depends(get_current_admin_user)])
def delete_tag(
        tag_id: uuid.UUID,
        session: Session = Depends(get_session)):
    """Admin: delete a tag.

    Raises:
        TagNotFoundError: 404 if no tag has this ID.
    """

    service = TagService(session)
    return service.delete_tag(tag_id)
