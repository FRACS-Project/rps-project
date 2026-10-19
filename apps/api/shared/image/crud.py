"""Database access for image rows. No validation and no file handling; the service layer handles that.

`pre_*` methods only flush, so they can run inside a recipe transaction
that is committed once.
"""

import uuid
from sqlmodel import Session, select

from . import Image, ImageStatus
from .schemas import ImageCreate


class ImageCrud:
    """Queries and writes for the image table."""

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db

    def create_image(self, image: ImageCreate) -> Image:
        """Insert an image row and commit."""
        db_image = Image.model_validate(image)
        self.db.add(db_image)
        self.db.commit()
        self.db.refresh(db_image)
        return db_image
    
    def pre_create_image(self, image: ImageCreate) -> Image:
        """Add an image row and flush without committing, so its ID is available."""
        db_image = Image.model_validate(image)
        self.db.add(db_image)
        self.db.flush()
        return db_image

    def read_images(self, offset: int = 0, limit: int = 100) -> list[Image]:
        """Return a page of image rows."""
        return self.db.exec(select(Image).offset(offset).limit(limit)).all()

    def read_image(self, image_id: uuid.UUID) -> Image | None:
        """Return the image row with this ID, or None."""
        return self.db.get(Image, image_id)

    def update_image(self, db_image: Image, image: dict) -> Image:
        """Apply the given fields to an image row and commit."""
        db_image.sqlmodel_update(image)
        self.db.add(db_image)
        self.db.commit()
        self.db.refresh(db_image)
        return db_image
    
    def pre_update_image(self, db_image: Image, image: dict) -> Image:
        """Apply the given fields to an image row and flush without committing."""
        db_image.sqlmodel_update(image)
        self.db.add(db_image)
        self.db.flush()
        return db_image

    def delete_image(self, db_image: Image) -> dict:
        """Delete an image row and commit. Does not delete the file."""
        self.db.delete(db_image)
        self.db.commit()
        return {"ok": True}
    
    def pre_delete_image(self, db_image: Image) -> dict:
        """Mark an image row for deletion without committing. Does not delete the file."""
        self.db.delete(db_image)
        return {"ok": True}


    def get_images_by_recipe(self, id: uuid.UUID, offset: int = 0, limit: int = 100) -> list[Image]:
        """Return a page of the recipe's image rows, oldest first."""
        query = select(Image).where(Image.recipe_id == id).order_by(Image.date_created.asc())
        return self.db.exec(query.offset(offset).limit(limit)).all()

    def get_images_by_recipe_by_status(
            self,
            id: uuid.UUID,
            status: ImageStatus,
            offset: int = 0,
            limit: int = 100
    ) -> list[Image]:
                """Return a page of the recipe's image rows with this status, oldest first."""
                query = (select(Image)
                    .where(Image.recipe_id == id, Image.status == status)
                    .order_by(Image.date_created.asc()))
                return self.db.exec(query.offset(offset).limit(limit)).all()
