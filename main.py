from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, List

from database import engine
import models, schemas
from auth import (
    get_db, hash_password, authenticate_user,
    create_access_token, get_current_user
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Day 7 Product Management API")

# ==========================
# USER SIGNUP
# ==========================
@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(400, "Username already exists")

    new_user = models.User(
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

# ==========================
# LOGIN
# ==========================
@app.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# ==========================
# CREATE PRODUCT
# ==========================
@app.post("/products", response_model=schemas.ProductResponse)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# ==========================
# READ PRODUCTS (FILTER + SORT)
# ==========================
@app.get("/products", response_model=List[schemas.ProductResponse])
def get_products(
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    sort_by: Optional[str] = Query("price"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(models.Product)

    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)

    if sort_by in ["price", "quantity", "name"]:
        query = query.order_by(getattr(models.Product, sort_by))

    return query.all()

# ==========================
# UPDATE PRODUCT
# ==========================
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(404, "Product not found")

    for key, value in product.dict().items():
        setattr(db_product, key, value)

    db.commit()
    return {"message": "Product updated"}

# ==========================
# DELETE PRODUCT
# ==========================
@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}
