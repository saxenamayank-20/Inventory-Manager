from sqlalchemy.orm import Session
from backend import models, schemas


# create
def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
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


# read
def get_item(db: Session, item_id: int) -> models.Item | None:
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def get_items(db: Session, skip: int = 0, limit: int = 100) -> list[models.Item]:
    return db.query(models.Item).offset(skip).limit(limit).all()


def search_items(db: Session, keyword: str) -> list[models.Item]:
    # partial match, case-insensitive
    return db.query(models.Item).filter(
        models.Item.name.ilike(f"%{keyword}%")
    ).all()


# update
def update_item(db: Session, item_id: int, updates: schemas.ItemUpdate) -> models.Item | None:
    db_item = get_item(db, item_id)
    if not db_item:
        return None

    # only touch the fields that were sent
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # name, price, quantity can't be null in the db, description can
        if value is None and field != "description":
            continue
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item


# delete
def delete_item(db: Session, item_id: int) -> models.Item | None:
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    db.delete(db_item)
    db.commit()
    return db_item
