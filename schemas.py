from pydantic import BaseModel

# ---------- USERS ----------
class UserCreate(BaseModel):
 username: str
 password: str

 
# ---------- PRODUCTS ----------
class ProductBase(BaseModel):
 name: str
 description: str
 price: float
 quantity: int

class ProductCreate(ProductBase):
 pass

class ProductUpdate(ProductBase):
 pass

class ProductResponse(ProductBase):
 id: int

class Config:
 from_attributes = True