from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
    name:        str   = Field(..., min_length=1, max_length=100, examples=["Laptop"])
    description: Optional[str] = Field(None, examples=["A powerful laptop"])
    price:       float = Field(..., gt=0, examples=[49999.99])
    quantity:    int   = Field(..., ge=0, examples=[10])


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    # everything optional, only sent fields get updated
    name:        Optional[str]   = Field(None, min_length=1, max_length=100, examples=["Gaming Laptop"])
    description: Optional[str]   = Field(None, examples=["Updated description"])
    price:       Optional[float] = Field(None, gt=0, examples=[59999.99])
    quantity:    Optional[int]   = Field(None, ge=0, examples=[5])


class ItemResponse(ItemBase):
    id:         int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # so it can read sqlalchemy objects
