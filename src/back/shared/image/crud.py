##############################################################################################################
#
# CRUD operations for managing Images in the application.
#
# This module provides functions to create, read, update, and delete Image entities
# in the database. It handles all database interactions related to Images.
#
##############################################################################################################

import uuid
from sqlmodel import Session, select

from . import Image
from .schemas import ImageCreate


class ImageCrud:

    def __init__(self, db: Session):
        """Initialize ImageCrud with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db

    def create_image(self, image: ImageCreate) -> Image:
        """Create a new Image in the database.

        Args:
            image (ImageCreate): The image data to create.

        Returns:
            Image: The newly created image instance.
        """
        db_image = Image.model_validate(image)
        self.db.add(db_image)
        self.db.commit()
        self.db.refresh(db_image)
        return db_image
    
    def pre_create_image(self, image: ImageCreate) -> Image:
        """Create a new Image in the database.

        Args:
            image (ImageCreate): The image data to create.

        Returns:
            Image: The newly created image instance.
        """
        db_image = Image.model_validate(image)
        self.db.add(db_image)
        self.db.flush()
        return db_image

    def read_images(self, offset: int = 0, limit: int = 100) -> list[Image]:
        """Retrieve a paginated list of images.

        Args:
            offset (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[Image]: A list of Image instances.
        """
        return self.db.exec(select(Image).offset(offset).limit(limit)).all()

    def read_image(self, image_id: uuid.UUID) -> Image | None:
        """Retrieve a specific Image by its ID.

        Args:
            image_id (uuid.UUID): The unique identifier of the Image.

        Returns:
            Image | None: The found Image instance or None if not found.
        """
        return self.db.get(Image, image_id)

    def update_image(self, db_image: Image, image: dict) -> Image:
        """Update an existing Image's information.

        Args:
            db_image (Image): The existing Image instance to update.
            image (dict): The new image data to apply.

        Returns:
            Image: The updated image instance.
        """
        db_image.sqlmodel_update(image)
        self.db.add(db_image)
        self.db.commit()
        self.db.refresh(db_image)
        return db_image

    def delete_image(self, db_image: Image) -> dict:
        """Delete a Image from the database.

        Args:
            db_image (Image): The Image instance to delete.

        Returns:
            dict: Confirmation message.
        """
        self.db.delete(db_image)
        self.db.commit()
        return {"ok": True}

    def get_images_by_recipe(self, id: uuid.UUID, offset: int = 0, limit: int = 100) -> list[Image]:
        """Retrieve a image by its name.

        Args:
            name (str): The name of the image to search for.

        Returns:
            Image | None: The found image instance or None if not found.
        """
        query = select(Image).where(Image.recipe_id == id)
        return self.db.exec(query.offset(offset).limit(limit)).all()
