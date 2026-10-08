from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from backend.database import engine, get_db
from backend import models, crud, schemas

# create the tables if they don't exist yet
models.Base.metadata.create_all(bind=engine)

# app
app = FastAPI(
    title="Item Inventory API",
    description="A full-stack CRUD API built with FastAPI and MySQL. Manage your inventory with ease!",
    version="1.0.0",
    contact={"name": "Mayank Saxena"},
)

# let the streamlit app call the api
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open to everyone for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# health check
@app.get("/", tags=["Health"])
def root():
    return {"message": "🚀 Item Inventory API is running!", "docs": "/docs"}


# POST /items
@app.post(
    "/items",
    response_model=schemas.ItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Items"],
    summary="Create a new item",
)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Add a new item."""
    return crud.create_item(db=db, item=item)


# GET /items
@app.get(
    "/items",
    response_model=List[schemas.ItemResponse],
    tags=["Items"],
    summary="Get all items",
)
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List items, 100 at a time by default."""
    return crud.get_items(db=db, skip=skip, limit=limit)


# GET /items/search, has to be above /items/{item_id} or 'search' gets read as an id
@app.get(
    "/items/search",
    response_model=List[schemas.ItemResponse],
    tags=["Items"],
    summary="Search items by name",
)
def search_items(keyword: str, db: Session = Depends(get_db)):
    """Search by name, partial and case-insensitive. 404 if nothing matches."""
    results = crud.search_items(db=db, keyword=keyword)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No items found matching '{keyword}'"
        )
    return results


# GET /items/{item_id}
@app.get(
    "/items/{item_id}",
    response_model=schemas.ItemResponse,
    tags=["Items"],
    summary="Get a single item by ID",
)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """Get one item by id."""
    db_item = crud.get_item(db=db, item_id=item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return db_item


# PUT /items/{item_id}
@app.put(
    "/items/{item_id}",
    response_model=schemas.ItemResponse,
    tags=["Items"],
    summary="Update an existing item",
)
def update_item(item_id: int, updates: schemas.ItemUpdate, db: Session = Depends(get_db)):
    """Update only the fields you send."""
    updated = crud.update_item(db=db, item_id=item_id, updates=updates)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return updated


# DELETE /items/{item_id}
@app.delete(
    "/items/{item_id}",
    tags=["Items"],
    summary="Delete an item",
)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item by id."""
    deleted = crud.delete_item(db=db, item_id=item_id)
    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return {
        "message": f"✅ Item '{deleted.name}' (ID: {deleted.id}) deleted successfully."
    }
