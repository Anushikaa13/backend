from sqlalchemy import Column, Integer, String, Float, Index
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
 price = Column(Float, index=True)  #Day 8 - Added index to price
 quantity = Column(Integer , index=True) #Day 8 - Added index to quantity

 Index("ix_price", price)  # Day 8 - Create index on price
 Index("ix_quantity", quantity)  # Day 8 - Create index on quantity