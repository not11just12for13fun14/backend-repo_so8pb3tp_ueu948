"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (kept for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Movie schema for film database
class Movie(BaseModel):
    """
    Movies collection schema
    Collection name: "movie"
    """
    title: str = Field(..., min_length=1, description="Movie title")
    year: Optional[int] = Field(None, ge=1888, le=2100, description="Release year")
    genres: Optional[List[str]] = Field(default=None, description="List of genres")
    rating: Optional[float] = Field(default=None, ge=0, le=10, description="Rating 0-10")
    poster_url: Optional[str] = Field(default=None, description="Poster image URL")
    description: Optional[str] = Field(default=None, description="Short synopsis")
    director: Optional[str] = Field(default=None, description="Director name")
    cast: Optional[List[str]] = Field(default=None, description="Main cast")

# Add your own schemas here as needed.
