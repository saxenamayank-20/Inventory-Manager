from sqlalchemy.orm import Session
from backend import models, schemas


# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────
def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
    """Insert a new item into the database and return it."""
    db_item = models.Item(
        name=item.name,
        description=item.description,
        price=item.price,
        quantity=item.quantity,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# ─────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────
def get_item(db: Session, item_id: int) -> models.Item | None:
    """Fetch a single item by its primary key."""
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def get_items(db: Session, skip: int = 0, limit: int = 100) -> list[models.Item]:
    """Fetch a paginated list of all items."""
    return db.query(models.Item).offset(skip).limit(limit).all()


def search_items(db: Session, keyword: str) -> list[models.Item]:
    """Search items by name (case-insensitive partial match)."""
    return db.query(models.Item).filter(
        models.Item.name.ilike(f"%{keyword}%")
    ).all()


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────
def update_item(db: Session, item_id: int, updates: schemas.ItemUpdate) -> models.Item | None:
    """Update only the provided fields of an item."""
    db_item = get_item(db, item_id)
    if not db_item:
        return None

    # Only update fields that were explicitly provided (not None)
    update_data = updates.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item


# ─────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────
def delete_item(db: Session, item_id: int) -> models.Item | None:
    """Delete an item by ID and return the deleted item, or None if not found."""
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    db.delete(db_item)
    db.commit()
    return db_item
