from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
import time

from database import engine
import models, schemas
from auth import (
    get_db, hash_password, authenticate_user,
    create_access_token, get_current_user
)
from security import (
    limiter, RATE_LIMITS, request_logger, 
    sanitize_string, validate_price, validate_quantity,
    validate_sort_parameter, validate_sort_order
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#-----------------------------Day 7 + Day 8 tasks---------------------------------------#
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Day 7 Product Management API",
    description="Secure Product Management with Rate Limiting & Input Validation",
    version="1.0.0"
)

# Add state for rate limiter
app.state.limiter = limiter

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Request timing middleware
@app.middleware("http")
async def add_request_timing(request: Request, call_next):
    """Log request duration and monitor performance"""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    response.headers["X-Process-Time"] = str(duration)
    return response

@app.get("/health")
def health_check():
    logger.info("Health check endpoint called")
    return {"message": "Welcome to the Product Management API"}

# ==========================
# USER SIGNUP
# ==========================
@app.post("/signup")
@limiter.limit(RATE_LIMITS["signup"])
def signup(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Signup attempt for username: {user.username}")
    
    # Sanitize input
    username = sanitize_string(user.username, max_length=50)
    
    if db.query(models.User).filter(models.User.username == username).first():
        logger.warning(f"Signup failed: Username {username} already exists")
        raise HTTPException(400, "Username already exists")

    new_user = models.User(
        username=username,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    logger.info(f"User {username} created successfully")
    return {"message": "User created successfully"}

# ==========================
# LOGIN
# ==========================
@app.post("/token")
@limiter.limit(RATE_LIMITS["login"])
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    logger.info(f"Login attempt for username: {form_data.username}")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Login failed for username: {form_data.username}")
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": user.username})
    logger.info(f"User {form_data.username} logged in successfully")
    return {"access_token": token, "token_type": "bearer"}

# ==========================
# CREATE PRODUCT
# ==========================
@app.post("/products", response_model=schemas.ProductResponse)
@limiter.limit(RATE_LIMITS["products"])
def create_product(
    request: Request,
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    logger.info(f"Creating product: {product.name} by user: {user}")
    
    # Validate inputs
    name = sanitize_string(product.name, max_length=200)
    description = sanitize_string(product.description, max_length=1000)
    price = validate_price(product.price)
    quantity = validate_quantity(product.quantity)
    
    db_product = models.Product(
        name=name,
        description=description,
        price=price,
        quantity=quantity
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    logger.info(f"Product created successfully with ID: {db_product.id}")
    return db_product

# =========================================================
# READ PRODUCTS (FILTER + SORT)
# Day 8 - Added pagination for performance and scalability
# =========================================================
@app.get("/products", response_model=List[schemas.ProductResponse])
@limiter.limit(RATE_LIMITS["get_products"])
def get_products(
    request: Request,
    # ==========================FILTER PARAMETERS=======================
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),

    # ==========================SORT PARAMETERS=========================
    sort_by: Optional[str] = Query("price", pattern="^(price|quantity|name)$"),
    sort_order: Optional[str] = Query("asc", pattern="^(asc|desc)$"),

    # ==========================PAGINATION==============================
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),

    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Validate sort parameters
    sort_by = validate_sort_parameter(sort_by, ["price", "quantity", "name"])
    sort_order = validate_sort_order(sort_order)
    
    # Validate price filters
    if min_price is not None:
        min_price = validate_price(min_price)
    if max_price is not None:
        max_price = validate_price(max_price)
    
    query = db.query(models.Product)

    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
  
    sort_column = getattr(models.Product, sort_by)

    if sort_order == "desc":
        sort_column = sort_column.desc()
    
    query = query.order_by(sort_column)

    # Pagination for heavy load
    logger.info(f"Fetching products: skip={skip}, limit={limit}, sort_by={sort_by}, order={sort_order}")
    products = query.offset(skip).limit(limit).all()

    return products

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
@limiter.limit(RATE_LIMITS["products"])
def delete_product(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    logger.info(f"Deleting product ID: {product_id} by user: {user}")
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        logger.warning(f"Delete failed: Product ID {product_id} not found")
        raise HTTPException(404, "Product not found")

    db.delete(product)
    db.commit()
    logger.info(f"Product ID {product_id} deleted successfully")
    return {"message": "Product deleted"}

#CICD TEST