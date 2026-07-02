##############################################################################################################
#
# Image Management Routes
#
# This module provides HTTP endpoints for image management.
# Routes handle HTTP request/response and delegate business logic to the service layer.
#
# Architecture:
#   - Routes: HTTP layer (request parsing, response formatting)
#   - Services: Business logic (validation, orchestration)
#   - CRUD: Database operations (queries, inserts, updates, deletes)
#
##############################################################################################################

import uuid

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session

from .schemas import (
    ImageCreate,
    ImagePublic,
    ImageUpdate,
)

from ...utils import (
    LimitQuery,
    OffsetQuery,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)

from .services import ImageService
from ...user.schemas import UserPublic
from ...db import get_session
from ...core import get_current_admin_user, get_current_active_user

router = APIRouter(
    prefix="/image",
    tags=["Image"],
    dependencies=[Depends(get_current_active_user)]
)


@router.get("/recipe/{recipe_id}", response_model=list[ImagePublic])
def get_images_by_recipe(
        recipe_id: uuid.UUID,
        session: Session = Depends(get_session)
):
    """Retrieve all the images of a recipe by it's id (recipe).

    Args:
        recipe_id (UUID): The unique identifier of the recipe.
        session (Session): The database session dependency.

    Returns:
        ImagePublic: The image with related data.
    """
    service = ImageService(session)
    return service.get_images_by_recipe(recipe_id)


# @router.post("/me", response_model=ImagePublic)
# def create_new_image(
#         image: ImageCreate,
#         session: Session = Depends(get_session),
#         current_user: UserPublic = Depends(get_current_active_user)
# ):
#     """Create a image with ingredients and instructions in one request.

#     Args:
#         image (NewImage): Aggregated image payload.
#         session (Session): The database session dependency.
#         current_user (UserPublic): Current authenticated user.

#     Returns:
#         ImagePublic: Created image with related data.
#     """

#     service = ImageService(session)
#     return service.create_image_by_user(image, current_user.id)


# @router.get("/me", response_model=list[ImagePublic])
# def get_my_images(
#         offset: OffsetQuery = DEFAULT_OFFSET,
#         limit: LimitQuery = DEFAULT_LIMIT,
#         session: Session = Depends(get_session),
#         # current_user: UserPublic = Depends(get_current_active_user)

# ):
#     """Retrieve images created by the current user.

#     Args:
#         offset (OffsetQuery): Number of images to skip (for pagination).
#         limit (LimitQuery): Maximum number of images to return.
#         session (Session): Database session dependency.
#         current_user (UserPublic): Current authenticated user.

#     Returns:
#         List[ImagePublic]: List of user's images with related data.
#     """
#     service = ImageService(session)
#     return service.get_images_by_recipe(offset, limit)


# @router.get("/me/{image_id}", response_model=ImagePublic)
# def get_my_image(
#         image_id: uuid.UUID,
#         session: Session = Depends(get_session),
#         current_user: UserPublic = Depends(get_current_active_user)
# ):
#     """Retrieve a specific image by its ID.

#     Args:
#         image_id (UUID): The unique identifier of the image.
#         session (Session): The database session dependency.
#         current_user (UserPublic): Current authenticated user.

#     Returns:
#         ImagePublic: The image with related data.
#     """

#     service = ImageService(session)
#     return service.get_image(image_id, current_user.id)


# @router.patch("/me/{image_id}", response_model=ImagePublic)
# def update_image(
#         image_id: uuid.UUID,
#         image: ImageUpdate,
#         session: Session = Depends(get_session),
#         current_user: UserPublic = Depends(get_current_active_user)
# ):
#     """Update a specific image by its ID.

#     Args:
#         image_id (UUID): The unique identifier of the image.
#         image (ImageUpdate): Fields to update and their new values.
#         session (Session): The database session dependency.
#         current_user (UserPublic): Current authenticated user.

#     Returns:
#         ImagePublic: The updated image data.
#     """

#     service = ImageService(session)
#     return service.update_image_by_user(image_id, image, current_user.id)


# @router.delete("/me/{image_id}")
# def delete_image(
#         image_id: uuid.UUID,
#         session: Session = Depends(get_session),
#         current_user: UserPublic = Depends(get_current_active_user)
# ):
#     """Delete the image by its ID for the current user.

#     Args:
#         image_id (UUID): The unique identifier of the image.
#         session (Session): The database session dependency.
#         current_user (UserPublic): Current authenticated user.

#     Returns:
#         dict: Confirmation message.
#     """

#     service = ImageService(session)
#     return service.delete_image_by_user(image_id, current_user.id)


# @router.post("/", response_model=ImagePublic, dependencies=[Depends(get_current_admin_user)])
# def create_image(image: ImageCreate,
#                  session: Session = Depends(get_session)):
#     """Create a new image.

#     Args:
#         image (ImageCreate): Image payload.
#         session (Session): Database session dependency.

#     Returns:
#         ImagePublic: Created image data.
#     """
#     service = ImageService(session)
#     return service.create_image(image)


# @router.get("/", response_model=list[ImagePublic])
# def get_images(
#         offset: OffsetQuery = DEFAULT_OFFSET,
#         limit: LimitQuery = DEFAULT_LIMIT,
#         session: Session = Depends(get_session)):
#     """Retrieve a paginated list of images.

#     Args:
#         offset (OffsetQuery): Number of images to skip (for pagination).
#         limit (LimitQuery): Maximum number of images to return.
#         session (Session): Database session dependency.

#     Returns:
#         List[ImagePublic]: List of images with related data.
#     """
#     service = ImageService(session)
#     return service.get_images(offset, limit)


# @router.get("/{image_id}", response_model=ImagePublic)
# def get_image(
#         image_id: uuid.UUID,
#         session: Session = Depends(get_session)):
#     """Retrieve a specific image by its ID.

#     Args:
#         image_id (UUID): The unique identifier of the image.
#         session (Session): The database session dependency.

#     Returns:
#         ImagePublic: The image with related data.
#     """

#     service = ImageService(session)
#     return service.get_image(image_id)


# @router.patch("/{image_id}", response_model=ImagePublic, dependencies=[Depends(get_current_admin_user)])
# def update_image(
#         image_id: uuid.UUID,
#         image: ImageUpdate,
#         session: Session = Depends(get_session)):
#     """Update a specific image by its ID.

#     Args:
#         image_id (UUID): The unique identifier of the image.
#         image (ImageUpdate): Fields to update and their new values.
#         session (Session): The database session dependency.

#     Returns:
#         ImagePublic: The updated image data.
#     """

#     service = ImageService(session)
#     return service.update_image(image_id, image)


# @router.delete("/{image_id}", dependencies=[Depends(get_current_admin_user)])
# def delete_image(
#         image_id: uuid.UUID,
#         session: Session = Depends(get_session)):
#     """Delete a image by its ID.

#     Args:
#         image_id (UUID): The unique identifier of the image.
#         session (Session): The database session dependency.

#     Returns:
#         dict: Confirmation message.
#     """

#     service = ImageService(session)
#     return service.delete_image(image_id)
