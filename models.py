from sqlalchemy import Column, Integer, String, Float
from database import Base

class User(Base):
 __tablename__ = "users"

 id = Column(Integer, primary_key=True, index=True)
 username = Column(String, unique=True, index=True, nullable=False)
 hashed_password = Column(String, nullable=False)


class Product(Base):
 __tablename__ = "products"
 id = Column(Integer, primary_key=True, index=True)
 name = Column(String, index=True)
 description = Column(String)
 price = Column(Float)
 quantity = Column(Integer)