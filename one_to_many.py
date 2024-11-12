# main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel
from typing import List

# Database setup
DATABASE_URL = "sqlite:///./ecommerce.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    
    # One-to-Many relationship with orders
    orders = relationship("Order", back_populates="user",cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Back reference to User
    user = relationship("User", back_populates="orders")

    def __repr__(self):
        return f"<Order(id={self.id}, product_name={self.product_name}, quantity={self.quantity}, price={self.price}, user_id={self.user_id})>"

# Create tables in the database
Base.metadata.create_all(bind=engine)

# FastAPI app instance
app = FastAPI()

# Dependency to get a new session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class OrderBase(BaseModel):
    product_name: str
    quantity: int
    price: float

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    user_id: int
    username: str

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    orders: List[OrderResponse] = []


    class Config:
        orm_mode = True

# CRUD Operations and Endpoints

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Updated delete endpoint for users
@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"detail": f"User with ID {user_id} has been deleted successfully"}




@app.post("/users/{user_id}/orders/", response_model=OrderResponse)
def create_order_for_user(user_id: int, order: OrderCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_order = Order(
        product_name=order.product_name,
        quantity=order.quantity,
        price=order.price,
        user_id=user_id
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@app.get("/orders/{order_id}", response_model=OrderResponse)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    response = {
        "id": order.id,
        "product_name": order.product_name,
        "quantity": order.quantity,
        "price": order.price,
        "user_id": order.user_id,
        "username": order.user.username  # Include the username here
    }
    return response

@app.get("/orders", response_model=List[OrderResponse])
def read_order(db: Session = Depends(get_db)):
    order = db.query(Order).all()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    for i in order:
        i.username =  i.user.username

    return order

@app.get("/users/") # response_model=List[UserResponse]
def read_users(db: Session = Depends(get_db)):

    users = db.query(User).all()
    return users
