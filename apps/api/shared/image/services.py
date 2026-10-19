"""Image service: image rows plus the files in `UPLOADS_DIR`.

Saving recipe images happens in two steps so a failed request never
leaves files without rows:

1. Inside the recipe transaction, `sync_recipe_images_on_*` creates
   PENDING rows for new images and marks removed images as PENDING.
2. After the commit, `store_pending_recipe_images` writes the new files
   and marks them ACTIVE, then `delete_pending_recipe_images` deletes
   every image still PENDING (removed ones and failed writes).
"""

import uuid
import base64
from pathlib import Path
import logging

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
    """Business logic for images and their files."""

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db
        self.crud = ImageCrud(self.db)
        self.logger = logging.getLogger(__name__)

    def create_image(self, image: ImageCreate) -> Image:
        """Create an image row without committing."""

        return self.crud.pre_create_image(image)

    def create_recipe_image_by_user(self, image: ImageCreate) -> Image:
        """Create an image row without committing. Same as `create_image`."""

        return self.crud.pre_create_image(image)

    def get_images(self, offset: OffsetQuery = 0, limit: LimitQuery = 100) -> list[Image]:
        """Return a page of image rows."""
        return self.crud.read_images(offset, limit)

    def get_image(self, image_id: uuid.UUID) -> Image:
        """Return an image row by ID.

        Raises:
            ImageNotFoundError: If no image has this ID.
        """
        image = self.crud.read_image(image_id)
        if not image:
            raise ImageNotFoundError()

        return image

    def get_images_by_recipe(self, recipe_id: uuid.UUID) -> list[ImagePublic]:
        """Return the recipe's active images, with their files as base64.

        Args:
            recipe_id: ID of the recipe.

        Returns:
            The images, oldest first.
        """
        db_images = self.crud.get_images_by_recipe_by_status(recipe_id, ImageStatus.ACTIVE)
        image_pub = []

        for image in db_images:
            image_bytes = Path(UPLOADS_DIR/str(image.id)).read_bytes()
            image_pub.append(
                ImagePublic(
                    id=image.id,
                    data_base64=base64.b64encode(image_bytes).decode("utf-8")
                )
            )

        return image_pub

    def get_primary_image_by_recipe(self, recipe_id: uuid.UUID) -> ImagePublic:
        """Return the recipe's primary image, with its file as base64.

        Raises:
            ImageNotFoundError: If the recipe has no active primary image.
        """
        db_images = self.crud.get_images_by_recipe_by_status(recipe_id, ImageStatus.ACTIVE)

        for image in db_images:
            if image.is_primary:
                image_bytes = Path(UPLOADS_DIR/str(image.id)).read_bytes()
                return ImagePublic(
                    id=image.id,
                    data_base64=base64.b64encode(image_bytes).decode("utf-8")
                )
        raise ImageNotFoundError()

    def update_image(self, image_id: uuid.UUID, image: ImageUpdate) -> Image:
        """Partially update an image row and commit.

        Raises:
            ImageNotFoundError: If no image has this ID.
        """
        db_image = self.crud.read_image(image_id)
        if not db_image:
            raise ImageNotFoundError()

        image_data = image.model_dump(exclude_unset=True)

        return self.crud.update_image(db_image, image_data)

    def pre_update_image(self, image_id: uuid.UUID, image: ImageUpdate) -> Image:
        """Partially update an image row without committing.

        Raises:
            ImageNotFoundError: If no image has this ID.
        """
        db_image = self.crud.read_image(image_id)
        if not db_image:
            raise ImageNotFoundError()

        image_data = image.model_dump(exclude_unset=True)

        return self.crud.pre_update_image(db_image, image_data)

    def delete_image(self, image_id: uuid.UUID) -> dict:
        """Delete an image row and commit. Does not delete the file.

        Raises:
            ImageNotFoundError: If no image has this ID.
        """
        db_image = self.crud.read_image(image_id)
        if not db_image:
            raise ImageNotFoundError()

        self.crud.delete_image(db_image)
        return {"ok": True}

    def pre_delete_image(self, image_id: uuid.UUID) -> dict:
        """Delete an image row without committing. Does not delete the file.

        Raises:
            ImageNotFoundError: If no image has this ID.
        """
        db_image = self.crud.read_image(image_id)
        if not db_image:
            raise ImageNotFoundError()

        self.crud.pre_delete_image(db_image)
        return {"ok": True}

    def magic_validation(self, images: list[ImagePayload] | ImagePayload):
        """Check that every new image is valid base64 of a JPEG, PNG or WebP file.

        The type is read from the file content (libmagic), not from a name or
        header sent by the client. Images without `new` are skipped.

        Args:
            images: One image (e.g. a profile picture) or a recipe's list of images.

        Raises:
            WrongImageType: If the data is not valid base64 or not an allowed type.
        """
        allowed = {"image/jpeg", "image/png", "image/webp"}
        items = images if isinstance(images, list) else [images]

        for image in items:
            if image.new:
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
        """Create a PENDING row for each image of a new recipe. Does not commit.

        Sets each payload's `id` to the new row's ID, so the files can be saved
        under that name after the commit.

        Args:
            recipe_id: ID of the new recipe.
            images: Images from the `NewRecipe` body.
            user_id: ID of the uploader.
        """

        for image in images:
            image.id = self.crud.pre_create_image(
                ImageCreate(
                    status=ImageStatus.PENDING,
                    owner_id=user_id,
                    recipe_id=recipe_id
                )
            ).id

    def sync_recipe_images_on_update(
            self,
            db_recipe: Recipe,
            images: list[ImagePayload]
    ) -> None:
        """Make the recipe's images match the payload. Does not commit.

        Images missing from the payload are marked PENDING so they get deleted
        after the commit. New images get a PENDING row, and their payload's `id`
        is set to it.

        Args:
            db_recipe: Recipe being edited.
            images: Full list of images from the `PatchRecipe` body.
        """
        # Set ids for the images that are already in the recipe
        kept_image_ids = {
            image.id
            for image in images
            if image.id
        }

        # Set ids for the images that are no longer in the recipe
        image_ids_to_delete = {
            image.id
            for image in db_recipe.images
            if image.id not in kept_image_ids
        }

        for image_id in image_ids_to_delete:
            self.pre_update_image(
                image_id,
                ImageUpdate(status=ImageStatus.PENDING)
            )

        for image in images:
            if image.new:
                image.id = self.crud.pre_create_image(
                    ImageCreate(
                        status=ImageStatus.PENDING,
                        owner_id=db_recipe.owner_id,
                        recipe_id=db_recipe.id
                    )
                ).id

    def store_pending_recipe_images(self, images: list[ImagePayload], recipe_id: uuid.UUID):
        """Write the new images' files and mark them ACTIVE. Call after the commit.

        A file that fails to write is logged and left PENDING, so
        `delete_pending_recipe_images` removes its row. The oldest active image
        then becomes the primary one.

        Args:
            images: Payload images whose `id` was set by a `sync_*` method.
            recipe_id: ID of the recipe.
        """
   
        for image in images:
            if image.new:
                try:
                    self._store_image(image.data_base64, image.id)
                except OSError:
                    self.logger.exception("Failed to store image %s", image.id)
                else:    
                    self.update_image(image.id, ImageUpdate(status=ImageStatus.ACTIVE))

        self._make_primary_image(recipe_id)

    def delete_pending_recipe_images(self, recipe_id: uuid.UUID):
        """Delete the recipe's PENDING images: file first, then row.

        If a file cannot be deleted, the error is logged and the row is kept.

        Args:
            recipe_id: ID of the recipe.
        """
        db_images = self.crud.get_images_by_recipe_by_status(recipe_id, ImageStatus.PENDING)
        for image in db_images:
            try:
                Path(UPLOADS_DIR/str(image.id)).unlink(missing_ok=True)
            except OSError:
                self.logger.exception("Failed to delete image %s", image.id)
            else:
                self.crud.delete_image(image)

    def _make_primary_image(self, recipe_id):
        """Make the recipe's oldest active image the primary one, and unset the others."""
        db_images = self.crud.get_images_by_recipe_by_status(recipe_id, ImageStatus.ACTIVE)
        for i, image in enumerate(db_images):
            if i == 0:
                self.update_image(
                    image.id,
                    ImageUpdate(is_primary=True)
                )
            else:
                self.update_image(
                    image.id,
                    ImageUpdate(is_primary=False)
                )

    def _store_image(self, image_base64: str, image_id: uuid.UUID):
        """Decode the base64 data and write it to `UPLOADS_DIR/<image_id>`."""
        raw = base64.b64decode(image_base64, validate=True)
        Path(UPLOADS_DIR/str(image_id)).write_bytes(raw)
