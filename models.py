from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base,relationship

Base = declarative_base()


class Outlet(Base):
    __tablename__ = "outlet"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    menuItem = relationship("MenuItem", back_populates="outlet")

class MenuItem(Base):
    __tablename__ = "menuItem"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False) 
    price = Column(Integer, nullable=False)
    outlet_id = Column(Integer, ForeignKey("outlet.id"), nullable=False)

    outlet = relationship("Outlet", back_populates="menuItem")
    order_item = relationship("OrderItem", back_populates="menu")

class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)

    order = relationship("Orders", back_populates="student")

class Orders(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    date_time = Column(DateTime, nullable=False)
    total_price = Column(Integer, nullable=False)

    student = relationship("Student", back_populates="order")
    order_item = relationship("OrderItem", back_populates="order")
    
class OrderItem(Base):
    __tablename__ = "order_item"
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    menu_id = Column(Integer, ForeignKey("menuItem.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

    order = relationship("Orders", back_populates="order_item")
    menu = relationship("MenuItem", back_populates="order_item")

class Payment(Base):
    __tablename__ = "payment"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    date_time = Column(DateTime, nullable=False)
    intiated = Column(bool, nullable=False)
    completed = Column(bool, nullable=False)
    ref_id = Column(String, nullable=False)

class OrderStatus(Base):
    __tablename__ = "order_status"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    intiated = Column(Integer, nullable=False)
    completed = Column(Integer, nullable=False)
    date_time = Column(DateTime, nullable=False)


class GetFoodOutlet(BaseModel):
    id : int
    name : str

    class Config():
        from_attributes = True

class AddFoodOutlet(BaseModel):
    id : int
    name : str

class AddMenuItem(BaseModel):
    id : int
    name : str
    price : int