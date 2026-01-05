# ======================================================
# Day 3: Authentication in FastAPI
# Goal: Secure APIs using JWT with token expiry
# ======================================================

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import List
import asyncio
import time
from functools import lru_cache

app = FastAPI()

# Security Configuration
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(
 schemes=["argon2"],
 deprecated="auto"
)
#admin123
# Fake Database (hashed password)
fake_users_db = {
 "admin": {
 "username": "admin",
 "hashed_password": '$argon2id$v=19$m=65536,t=3,p=4$rZWSMoYwpvT+vzdGqPW+Vw$iY3YsHZZM0Egu5qCpF7TIMH5k60541pmtWMj1Xs6lBA'
 }
}

# ======================================================
# Pydantic Model
# ======================================================
class Product(BaseModel):
 id: int
 name: str
 price: float
 quantity: int

products: List[Product] = []

# Password Utilities
def verify_password(plain_password, hashed_password):
 return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
 user = fake_users_db.get(username)
 if not user:
   return None
 if not verify_password(password, user["hashed_password"]):
   return None
 return user

# ======================================================
# JWT Token Utilities
# ======================================================
def create_access_token(data: dict, expires_delta: timedelta):
 to_encode = data.copy()
 expire = datetime.utcnow() + expires_delta
 to_encode.update({"exp": expire})
 return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return username

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid"
        )

# ======================================================
# Day 3 – Task 1: Login API with Expiry
# ======================================================
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
 user = authenticate_user(
 form_data.username,
 form_data.password
 )

 if not user:
  raise HTTPException(
  status_code=status.HTTP_401_UNAUTHORIZED,
  detail="Incorrect username or password"
  )

 access_token = create_access_token(
 data={"sub": user["username"]},
 expires_delta=timedelta(
 minutes=ACCESS_TOKEN_EXPIRE_MINUTES
 )
 )

 return {
 "access_token": access_token,
 "token_type": "bearer",
 "expires_in_minutes": ACCESS_TOKEN_EXPIRE_MINUTES
 }

# ======================================================
# Day 3 – Task 2: Protected Product APIs
# ======================================================
@app.post("/products")
def add_product(
 product: Product,
 current_user: str = Depends(get_current_user)
):
 products.append(product)
 return {"message": "Product added successfully"}

@app.get("/products")
def get_products(
 current_user: str = Depends(get_current_user)
):
 return products


# -------------------- DAY 4 TASKS ------------------------

# Performance Optimization

# =========================================================

# ---------------------------------------------------------
# Task 1: Async I/O 
# ---------------------------------------------------------

@app.get("/async-products")
async def async_get_products(
  user: str = Depends(get_current_user)
):
 await asyncio.sleep(0.1)  # simulate async I/O delay
 return products


# ---------------------------------------------------------
# Task 1: Caching 
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def cached_products():
    return products

@app.get("/cached-products")
def get_cached_products(
    user: str = Depends(get_current_user)
):
 return cached_products()


# ---------------------------------------------------------
# Task 2: Benchmark Performance
# ---------------------------------------------------------



@app.get("/benchmark")
def benchmark_api(
    user: str = Depends(get_current_user)
):

    start = time.time()
    for _ in range(1000):
        _ = products
    end = time.time()
    return {
        "message": "Benchmark completed",
        "time_taken_seconds": end - start
    }