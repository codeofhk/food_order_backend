from fastapi import FastAPI,Request,Response,HTTPException,Depends,status
from fastapi.middleware.cors import CORSMiddleware
from models import AddFoodOutlet
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from utils import dummy_response
from models import Base
from models import (
    AddFoodOutlet,
    GetFoodOutlet,
    AddMenuItem,
)
from models import (
    Outlet,
    MenuItem,
    Student,
    Orders,
    OrderItem,
    Payment,
    OrderStatus
)
import sqlite3 as sql
import datetime as dat
import httpx


app = FastAPI()

#database Connection
DATABASE_URL = "sqlite:///./food_order.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''database = "food_order.db"
database_connection = sql.connect(database)
cursor = database_connection.cursor()'''

merchant_url = "http://localhost:6000"
user_url = "http://localhost:7000"

origins = [
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def check_server():
    return {"status": "ok"}

@app.put("/food-outlet/{id}/close/")
async def close_outlet(id:int, db:Session = Depends(get_db)):
    try:
        outlet = db.query(Outlet).filter(Outlet.id == id).first()
        outlet.closed = 1
        db.commit()
        db.refresh(outlet)
        return {"message": "Outlet closed successfully"}
    except:
        raise HTTPException(status_code=404, detail=f"Error")

@app.put("/food-outlet/{id}/open/")
async def open_outlet(id:int, db:Session = Depends(get_db)):
    try:
        outlet = db.query(Outlet).filter(Outlet.id == id).first()
        outlet.closed = 0
        db.commit()
        db.refresh(outlet)
        return {"message": "Outlet opened successfully"}
    except:
        raise HTTPException(status_code=404, detail=f"Error")

@app.get("/food-outlet/{id}", responses = {
        status.HTTP_200_OK: {"model": GetFoodOutlet},
        status.HTTP_404_NOT_FOUND: {"description": "Food Outlet not found"},
})
def get_food_outlets(id:int, db: Session = Depends(get_db)):
    outlet = db.query(Outlet).filter(Outlet.id == id).first()
    if outlet is None:
        raise HTTPException(status_code=404, detail=f"Food Outlet with id {id} not found")
    return GetFoodOutlet.model_validate(outlet)

@app.post("/food-outlet/", responses={
        200: {"model": AddFoodOutlet},
        #404: {"model": HTTPException}
},
summary="Create a new food outlet",
description="Create a new food outlet, provide with name",)
async def create_food_outlet(Request: Request, db: Session = Depends(get_db)):
    try:
        data = await Request.json()
        id = db.query(Outlet).count() 
        for i in range(len(data)):
            id = id + 1
            new_outlet = Outlet(id = id ,name = data[i]["name"])
            db.add(new_outlet)
            db.commit()
            db.refresh(new_outlet)
        return {"message": "Food outlet added successfully"}
    except:
        raise HTTPException(status_code=404, detail=f"Error")

@app.put("/food-outlet/{id}/name/") 
async def update_food_outlet_name(Request: Request, id:int, db: Session = Depends(get_db)):
    response = await Request.json()
    try:
        new_name = response["name"]
        outlet = db.query(Outlet).filter(Outlet.id == id).first()
        outlet.name = new_name
        db.commit()
        db.refresh(outlet)
        return {"message": "Food outlet name updated successfully"}
    except:
        raise HTTPException(status_code=404, detail=f"Error")

@app.delete("/food-outlet/{id}/")
def delete_food_outlet(id:int , db:Session = Depends(get_db)):
    outlet = db.query(Outlet).filter(Outlet.id == id).first()
    if outlet is None:
        raise HTTPException(status_code=404, detail=f"Food Outlet with id {id} not found")
    db.delete(outlet)
    db.commit()
    db.refresh(outlet)
    return {"message": "Food outlet deleted successfully"}


@app.get("/food-outlet/{id}/menu/")
def get_menu(id:int, db:Session = Depends(get_db)):
    try:
        menu = db.query(MenuItem).filter(MenuItem.outlet_id == id).all()
        return menu
    except:
        raise HTTPException(status_code=404, detail=f"Error")

@app.post("/food-outlet/{outlet_id}/menu/")
async def add_menu(Request : Request, outlet_id:int, db:Session = Depends(get_db)):
    try:
        data = await Request.json()
        id = db.query(MenuItem).count()
        for i in range(len(data)):
            id = id + 1
            new_menu = MenuItem(id = id, name = data[i]["name"], price = data[i]["price"], outlet_id = outlet_id)
            db.add(new_menu)
            db.commit()
            db.refresh(new_menu)
        return {"message": "Menu added successfully"}
    except:
        raise HTTPException(status_code=404, detail=f"Error")


@app.delete("/food-outlet/{outlet_id}/menu/{menu_id}/")
def delete_menu_item(outlet_id:int, menu_id:int, db:Session = Depends(get_db)):
    try:
        menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
        db.delete(menu)
        db.commit()
        db.refresh(menu)
        return {"message": "Menu item deleted successfully"}
    except:
        raise HTTPException(status_code=404, detail=f"Error")

@app.put("/food-outlet/{outlet_id}/menu/{menu_id}/price/")
async def change_menu_item_price(Request: Request, outlet_id:int, menu_id:int, db:Session = Depends(get_db)):
    response = await Request.json()
    try:
        new_price = response["price"]
        menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
        menu.price = new_price
        db.commit()
        db.refresh(menu)
        return {"message": "Menu item price updated successfully"}
    except:
        raise HTTPException(status_code=404, detail=f"Error")

@app.put("/food-outlet/{outlet_id}/menu/{menu_id}/name/")
async def change_menu_item_price(Request: Request, outlet_id:int, menu_id:int, db:Session = Depends(get_db)):
    response = await Request.json()
    try:
        new_name = response["name"]
        menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
        menu.name = new_name
        db.commit()
        db.refresh(menu)
        return {"message": "Menu item name updated successfully"}
    except:
        raise HTTPException(status_code=404, detail=f"Error")

@app.post("/student/")
async def add_student(Request:Request, db: Session = Depends(get_db)):
    try:
        data = await Request.json()
        id = db.query(Student).count()
        for i in range(len(data)):
            id = id + 1
            new_student = Student(id = id, name = data[i]["name"], password = data[i]["password"], phone = data[i]["phone"], email = data[i]["email"])
            db.add(new_student)
            db.commit()
            db.refresh(new_student)
        return {"message": "Student added successfully"}
    except:
        raise HTTPException(status_code=404, detail=f"Error")
    #return dummy_response

@app.get("/student/{id}/")
def get_student_by_id(id:int, db:Session = Depends(get_db)):
    try:
        student = db.query(Student).filter(Student.id == id).first()
        return student
    except: 
        raise HTTPException(status_code=404, detail=f"Student with id {id} not found")

@app.delete("/student/{id}/")
def delete_student(id:int, db:Session = Depends(get_db)):
    try:
        student = db.query(Student).filter(Student.id == id).first()
        db.delete(student)
        db.commit()
        db.refresh(student)
        return {"message": "Student deleted successfully"}
    except:
        raise HTTPException(status_code=404, detail=f"Error")

@app.put("/student/{id}/name/")
async def update_student_name(Request:Request, id:int, db:Session = Depends(get_db)):
    response = await Request.json()
    try:
        student = db.query(Student).filter(Student.id == id).first()
        student.name = response["name"]
        db.commit()
        db.refresh(student)
        return {"message": "Student name updated successfully"}
    except : 
        raise HTTPException(status_code=404, detail=f"Error")


@app.put("/student/{id}/password/")
async def update_student_password(Request:Request, id:int, db:Session = Depends(get_db)):
    response = await Request.json()
    try:
        student = db.query(Student).filter(Student.id == id).first()
        student.password = response["password"]
        db.commit()
        db.refresh(student)
        return {"message": "Student password updated successfully"}
    except :
        raise HTTPException(status_code=404, detail=f"Error")

@app.put("/student/{id}/phone/")
async def update_student_phone(Request:Request, id:int, db:Session = Depends(get_db)):
    response = await Request.json()
    try:
        student = db.query(Student).filter(Student.id == id).first()
        student.phone = response["phone"]
        db.commit()
        db.refresh(student)
        return {"message": "Student phone updated successfully"}
    except :
        raise HTTPException(status_code=404, detail=f"Error")

@app.put("/student/{id}/email/")
async def update_student_email(Request:Request, id:int, db:Session = Depends(get_db)):
    response = await Request.json()
    try:
        student = db.query(Student).filter(Student.id == id).first()
        student.email = response["email"]
        db.commit()
        db.refresh(student)
        return {"message": "Student email updated successfully"}
    except :
        raise HTTPException(status_code=404, detail=f"Error")
    

@app.post("/payment/intiate/")
async def initiate_payment(Request:Request, db:Session = Depends(get_db)):
    response = await Request.json()
    try:
        order_id = response["order_id"]
        amount = response["amount"]
        intiated = 1
        amount = response["amount"]
        completed = 0
        id = db.query(Payment).count() + 1
        new_payment = Payment(id = id, order_id = order_id, amount = amount, intiated = intiated, completed = completed)
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
        return {"message": "Payment initiated successfully", "pyament_id": id}
    except:
        raise HTTPException(status_code=404, detail=f"Error")
    
@app.put("/payment/{id}/success/")
async def update_payment_status(Request:Request, id:int, db:Session = Depends(get_db)):
    response = await Request.json()
    try:
        payment = db.query(Orders).filter(Orders.id == id).first()
        payment.completed = 1
        db.commit()
        db.refresh(payment)
        return {"message": "Payment status updated successfully"}
    except:
        raise HTTPException(status_code=404, detail=f"Error")

@app.post("/food-outlet/order/")
async def create_order(Request:Request, db:Session = Depends(get_db)):
    response = await Request.json()
    try:
        order_id = db.query(Orders).count() + 1
        student_id = response["student_id"]
        data_time = str(dat.datetime.now())
        order_item = response["order_item"]
        total_price = 0
        menu_acc_outlet_id = {}
        for i in response:
            outlet_id = db.query(MenuItem.outlet_id).filter(MenuItem.id == i["menu_id"]).first()
            if outlet_id not in menu_acc_outlet_id:
                menu_acc_outlet_id[outlet_id] = [{i["menu_id"]:i["quantity"]}]
            else:
                menu_acc_outlet_id[outlet_id].append({i["menu_id"] : i["quantity"]})

        for i in menu_acc_outlet_id:
            total_price = 0
            for j in menu_acc_outlet_id[i]:
                new_order_acc_outlet = OrderItem(order_id = order_id, menu_id = j, quantity = menu_acc_outlet_id[i][j], price = db.query(MenuItem.price).filter(MenuItem.id == i).first())
                total_price = total_price + menu_acc_outlet_id[i][j]["price"] * menu_acc_outlet_id[i][j]["quantity"]
                db.add(new_order_acc_outlet)
                db.commit()
                db.refresh(new_order_acc_outlet)
            
            new_order= Orders(id = order_id, student_id = student_id, date_time = data_time, total_price = total_price)

            order_status = OrderStatus(order_id = order_id, intiated = 1, completed = 0, date_time = data_time)
            db.add(order_status)
            db.commit()
            db.refresh(order_status)
            order_id += 1

            #orderid are grouped by outlet id

            return {"message": "Order created successfully"}


        '''for i in range(len(order_item)):
            new_order_item = OrderItem(order_id = order_id, menu_id = order_item[i]["menu_id"], quantity = order_item[i]["quantity"], price = order_item[i]["price"])
            if new_order_item.price != db.query(MenuItem).filter(MenuItem.id == new_order_item.menu_id).first().price:
                raise HTTPException(status_code=404, detail=f"Price mismatch")
            db.add(new_order_item)
            db.commit()
            db.refresh(new_order_item)
            total_price = total_price + order_item[i]["price"] * order_item[i]["quantity"]
        
        new_order = Orders(id = order_id, student_id = student_id, date_time = data_time, total_price = total_price)
        db.add(new_order)
        db.commit()
        db.refresh(new_order)'''

        '''async with httpx.AsyncClient() as client:
            await client.post(f"{merchant_url}/order/", json={"order_id": order_id})''' #making the merchant app 

    except:
        raise HTTPException(status_code=404, detail=f"Error")
    
@app.get("/food-outlet/order/outlet/{outlet_id}/")
async def get_order_by_outlet_id(outlet_id:int, db:Session = Depends(get_db)):
    try:
        orders = db.query(OrderStatus).filter(OrderStatus.completed == 0).all()
        outlet_orders = {}
        ordered_items = {}
        for order in orders:
            ordered_items[order]  = []
            ordered_items.append(db.query(OrderItem.menu_id).filter(OrderItem.id == order.order_id).scalar())
        for order in ordered_items:
            if db.query(MenuItem).filter(MenuItem.id == ordered_items[order][0]).first().outlet_id == outlet_id:
                outlet_orders[order] = []
                for item in ordered_items[order]:
                    outlet_orders.append(db.query(MenuItem.name).filter(MenuItem.id == item).first())
        
        return outlet_orders
    except:
        raise HTTPException(status_code=404, detail=f"Error")
    
@app.put("/food-outlet/order/{id}/status/completed/")
async def update_order_status(Request:Request, id:int, db:Session = Depends(get_db)):
    response = await Request.json()
    try:
        order_status = db.query(OrderStatus).filter(OrderStatus.order_id == id).first()
        order_status.completed = 1
        db.commit()
        db.refresh(order_status)
        return {"message": "Order status updated successfully"}
    except:
        raise HTTPException(status_code=404, detail=f"Error")


@app.get("/food-outlet/order/{id}/")
def get_order_by_id(id:int, db:Session = Depends(get_db)):
    try:
        order = db.query(Orders).filter(Orders.id == id).first()
        return order
    except:
        raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
         

@app.get("/food-outlet/menu/all/")
def get_all_menu(db:Session = Depends(get_db)):
    menu = db.query(MenuItem).all()
    return menu


@app.get("/food-outlet/order/all/")
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(Orders).all()
    return orders

@app.get("payment/{id}/")
def get_payment_by_id(id:int, db:Session = Depends(get_db)):
    try:
        payment = db.query(Payment).filter(Payment.id == id).first()
        return payment
    except:
        raise HTTPException(status_code=404, detail=f"Payment with id {id} not found")

@app.get("payment/all/")
def get_all_payments(db:Session = Depends(get_db)):
    payments = db.query(Payment).all()
    return payments

@app.get("food-order/all/")
def get_all_order_items(db:Session = Depends(get_db)):
    order_items = db.query(Orders).all()
    return order_items

@app.get("/food-outlet/", responses = {
        status.HTTP_200_OK: {"model": GetFoodOutlet},
})
def get_food_outlets(db: Session = Depends(get_db)):
    outlets = db.query(Outlet).all()
    return outlets

@app.get("/student/all")
def get_student(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return students