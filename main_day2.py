from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

#Product model
app = FastAPI()
class Product(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

products :  List[Product] = []

@app.get("/")
def read_root():
    return {"message": "Welcome to the Product API"}        

@app.get("/products", response_model=List[Product])
def get_products():
    return products

@app.post("/products", response_model=Product)
def create_product(product: Product):
    products.append(product)
    return product

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    for product in products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/{product_id}", response_model=Product)
def delete_product(product_id: int):
    for index, product in enumerate(products):
        if product.id == product_id:
            deleted_product = products.pop(index)
            return deleted_product
    raise HTTPException(status_code=404, detail="Product not found")

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, updated_product: Product):
    for index, product in enumerate(products):
        if product.id == product_id:
            products[index] = updated_product
            return updated_product
    raise HTTPException(status_code=404, detail="Product not found")
    