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

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List, Literal

# -----------------------------------------------------------------------------
# Listing schema for a secondhand marketplace
# Collection name: "listing"
# -----------------------------------------------------------------------------
class ContactInfo(BaseModel):
    name: Optional[str] = Field(None, description="Seller name")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")

class Listing(BaseModel):
    title: str = Field(..., description="Listing title")
    description: Optional[str] = Field(None, description="Detailed description")
    category: Optional[str] = Field(None, description="Category like Furniture, Clothing, Electronics")
    condition: Optional[Literal["Neu", "Wie neu", "Gut", "Okay", "Gebraucht"]] = Field(
        None, description="Item condition in German"
    )
    brand: Optional[str] = Field(None, description="Brand/Label")
    size: Optional[str] = Field(None, description="Size (for clothes/shoes)")
    color: Optional[str] = Field(None, description="Primary color")
    material: Optional[str] = Field(None, description="Main material")
    price: float = Field(..., ge=0, description="Price amount")
    currency: str = Field("EUR", description="Currency code, default EUR")
    location: Optional[str] = Field(None, description="City or area")

    delivery_options: List[str] = Field(
        default_factory=list,
        description="Delivery methods like Versand, Abholung, Treffen",
    )
    image_urls: List[str] = Field(default_factory=list, description="Image URLs")
    tags: List[str] = Field(default_factory=list, description="Search tags")

    contact: Optional[ContactInfo] = Field(None, description="Seller contact info")

# -----------------------------------------------------------------------------
# Example schemas kept for reference (not used directly by the app)
# -----------------------------------------------------------------------------
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
