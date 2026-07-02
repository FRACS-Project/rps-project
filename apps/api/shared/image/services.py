##############################################################################################################
#
# Image Service Layer - Business Logic and Validation
#
# This module contains the service layer for Image management.
# Services handle all business logic, validation, and coordinate between routes and CRUD.
#
# Architecture:
#   - Receives requests from routes (HTTP layer)
#   - Validates business rules (duplicates, existence)
#   - Coordinates CRUD operations (database layer)
#   - Handles error conditions with domain-specific exceptions
#
# Key Responsibilities:
#   - Image creation with duplicate name checking
#   - Image retrieval and pagination
#   - Image updates and deletion with existence validation
#
##############################################################################################################

import uuid
import base64
from pathlib import Path

import magic
import base64

from sqlmodel import Session

from ...core.path import UPLOADS_DIR

from . import (
    Image,
    ImageStatus,
    DuplicateImageError,
    ImageNotFoundError,
    WrongImageType
)

from ...recipe import Recipe

from .schemas import (
    ImagePublic,
    ImageCreate,
    ImageUpdate,
    ImagePayload
)

from .crud import ImageCrud

from ...utils import LimitQuery, OffsetQuery


class ImageService:
    """Service layer for Image management.

    Handles all business logic related to Images including creation, validation,
    and lifecycle operations. Coordinates between HTTP routes and database CRUD.
    """

    def __init__(self, db: Session):
        """Initialize ImageService with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db
        self.crud = ImageCrud(self.db)

    def create_image(self, image: ImageCreate) -> Image:
        """Create a new Image with duplicate name validation.

        Args:
            image (ImageCreate): The image data to create.

        Returns:
            Image: The newly created image.
        """

        return self.crud.pre_create_image(image)

    def create_recipe_image_by_user(self, image: ImageCreate) -> Image:
        """Create a new Image with duplicate name validation.

        Args:
            image (ImageCreate): The image data to create.

        Returns:
            Image: The newly created image.
        """

        return self.crud.pre_create_image(image)

    def get_images(self, offset: OffsetQuery = 0, limit: LimitQuery = 100) -> list[Image]:
        """Retrieve a paginated list of Images.

        Args:
            offset (int): Number of images to skip (for pagination).
            limit (int): Maximum number of images to return.

        Returns:
            List[Image]: List of images.
        """
        return self.crud.read_images(offset, limit)

    def get_image(self, image_id: uuid.UUID) -> Image:
        """Retrieve a specific Image by ID.

        Args:
            image_id (uuid.UUID): The unique identifier of the image.

        Returns:
            Image: The found image instance.

        Raises:
            ImageNotFoundError: If the Image is not found.
        """
        image = self.crud.read_image(image_id)
        if not image:
            raise ImageNotFoundError()

        return image

    def get_images_by_recipe(self, recipe_id: uuid.UUID) -> list[ImagePublic]:
        """Retrieve the list of images from a recipe.

        Args:
            name (str): The name of the image.

        Returns:
            List[Image]: The found image instance.

        Raises:
            ImageNotFoundError: If the Image is not found.
        """
        images = self.crud.get_images_by_recipe(recipe_id)
        image_pub = []

        for image in images:
            if not image:
                raise ImageNotFoundError()
            image_bytes = Path(UPLOADS_DIR/str(image.id)).read_bytes()
            image_pub.append(
                ImagePublic(
                    id=image.id,
                    data_base64=base64.b64encode(image_bytes).decode("utf-8")
                )
            )

        return image_pub

    def update_image(self, image_id: uuid.UUID, image: ImageUpdate) -> Image:
        """Update an existing Image's information.

        Args:
            image_id (uuid.UUID): The unique identifier of the image.
            image (ImageUpdate): The new image data to apply.

        Returns:
            Image: The updated image instance.

        Raises:
            ImageNotFoundError: If the Image is not found.
        """
        db_image = self.crud.read_image(image_id)
        if not db_image:
            raise ImageNotFoundError()

        image_data = image.model_dump(exclude_unset=True)

        return self.crud.update_image(db_image, image_data)
    
    def pre_update_image(self, image_id: uuid.UUID, image: ImageUpdate) -> Image:
        db_image = self.crud.read_image(image_id)
        if not image:
            raise ImageNotFoundError()
        
        image_data = image.model_dump(exclude_unset=True)
        
        return self.crud.pre_update_image(db_image, image_data)

    def delete_image(self, image_id: uuid.UUID) -> dict:
        """Delete a Image by ID.

        Args:
            image_id (uuid.UUID): The unique identifier of the image.

        Raises:
            ImageNotFoundError: If the Image is not found.
        """
        db_image = self.crud.read_image(image_id)
        if not db_image:
            raise ImageNotFoundError()

        self.crud.delete_image(db_image)
        return {"ok": True}

    def pre_delete_image(self, image_id: uuid.UUID) -> dict:
        """Delete an image.

        Args:
            image_id (UUID): The unique identifier of the image to delete.

        Raises:
            imageNotFoundError: If the image is not found.
        """
        db_image = self.crud.read_image(image_id)
        if not db_image:
            raise ImageNotFoundError()

        self.crud.pre_delete_image(db_image)
        return {"ok": True}

    def magic_validation(self, images: list[ImageCreate] | ImageCreate):
        """Validate that the image has the proper type (image/jpeg, image/png, image/webp)

        Args:
            images (list[ImageCreate] | ImageCreate): Depends of the payload that was send (for recipe multiples images but for the profil picture it's only 1)

        Raises:
            WrongImageType: Raise en exception if the type is not include in the list
        """
        allowed = {"image/jpeg", "image/png", "image/webp"}
        items = images if isinstance(images, list) else [images]

        for image in items:
            try:
                raw = base64.b64decode(image.data_base64, validate=True)
                mime = magic.from_buffer(raw, mime=True)
            except Exception:
                raise WrongImageType()
            if mime not in allowed:
                raise WrongImageType()

    def sync_recipe_images_on_create(
        self,
        recipe_id: uuid.UUID,
        images: list[ImagePayload],
        user_id: uuid.UUID
    ) -> None:
        """Add the images for a new recipe"""

        for i, image in enumerate(images):
            if i == 0:
                image_created = self.crud.pre_create_image(
                    ImageCreate(
                        status=ImageStatus.PENDING,
                        is_primary=True,
                        owner_id=user_id,
                        recipe_id=recipe_id
                    )
                )
            else:
                image_created = self.crud.pre_create_image(
                    ImageCreate(
                        status=ImageStatus.PENDING,
                        owner_id=user_id,
                        recipe_id=recipe_id
                    )
                )
            self._store_image(image.data_base64, image_created.id)
            self.update_image(
                image_created.id,
                ImageUpdate(status=ImageStatus.ACTIVE)
            )

    def sync_recipe_images_on_update(
        self,
        db_recipe: Recipe,
        images: list[ImagePayload],
        recipe_id: uuid.UUID
    ):
        # Set ids for the images that are already in the recipe
        old_img_ids = {
            image.id
            for image in images
            if image.id
        }

        # Set ids for the images that are no longer in the recipe
        images_to_delete = {
            image.id
            for image in db_recipe.images
            if image.id not in old_img_ids
        }

        for id in images_to_delete:
            self.pre_delete_image(id)
            Path(UPLOADS_DIR/str(id)).unlink(missing_ok=True)

        db_recipe.images = [
            img
            for img in db_recipe.images
            if img.id not in images_to_delete
        ]

        for i, image in enumerate(images):
            if image.new:
                image_created = self.crud.pre_create_image(
                    ImageCreate(
                        status=ImageStatus.PENDING,
                        owner_id=db_recipe.owner_id,
                        recipe_id=recipe_id
                    )
                )
                self._store_image(image.data_base64, image_created.id)
                self.update_image(
                    image_created.id,
                    ImageUpdate(status=ImageStatus.ACTIVE)
                )
        
        recipe_images = self.get_images_by_recipe(recipe_id)
        for i, image in enumerate(recipe_images):
            if i == 0:
                self.update_image(
                    image.id,
                    ImageUpdate(
                        is_primary=True
                    )
                )
            else:
                self.update_image(
                    image.id,
                    ImageUpdate(
                        is_primary=False
                    )
                )


    def _store_image(self, image_base64: str, image_id: uuid.UUID):
        raw = base64.b64decode(image_base64, validate=True)
        Path(UPLOADS_DIR/str(image_id)).write_bytes(raw)
