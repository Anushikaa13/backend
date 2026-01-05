from fastapi import FastAPI

app = FastAPI()

students = [
    {"id": 1, "name": "Alice", "age": 20},
    {"id": 2, "name": "Bob", "age": 22},
    {"id": 3, "name": "Charlie", "age": 23},
]

@app.get("/")
def read_root():
    return {"message": "Welcome to the Student API"}

@app.get("/students")
def get_students():
    return  students