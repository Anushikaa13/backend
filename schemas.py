from pydantic import BaseModel, Field, field_validator, EmailStr
import re

# ---------- USERS ----------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username must be 3-50 characters")
    password: str = Field(..., min_length=8, max_length=100, description="Password must be 8-100 characters")
    
    @field_validator('username')
    def validate_username(cls, v):
        """Validate username: alphanumeric and underscores only"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v
    
    @field_validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

# ---------- PRODUCTS ----------
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: str = Field(..., min_length=1, max_length=1000, description="Product description")
    price: float = Field(..., gt=0, le=1000000, description="Price must be positive and <= 1,000,000")
    quantity: int = Field(..., ge=0, le=1000000, description="Quantity must be >= 0 and <= 1,000,000")
    
    @field_validator('name')
    def validate_name(cls, v):
        """Validate product name"""
        if v.strip() == '':
            raise ValueError('Product name cannot be empty or whitespace only')
        return v.strip()
    
    @field_validator('description')
    def validate_description(cls, v):
        """Validate product description"""
        if v.strip() == '':
            raise ValueError('Description cannot be empty or whitespace only')
        return v.strip()

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True