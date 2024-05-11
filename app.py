# James Carlson
# Coding Temple - SE FT-144
# Module 6: Mini-Project | E-Commerce API

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, make_transient
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from typing import List
from flask_cors import CORS
import datetime, random

# create and configure app
app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:Password123!@localhost/ecommerce_project_db"
app.json.sort_keys = False

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)

### ============ PYTHON CLASSES / SQL TABLES ============ ###

class Customer(Base):
    __tablename__ = "Customers"
    customer_id:    Mapped[int] = mapped_column(primary_key=True)
    name:           Mapped[str] = mapped_column(db.String(255), nullable=False)
    email:          Mapped[str] = mapped_column(db.String(320))
    phone:          Mapped[str] = mapped_column(db.String(15))

    orders:         Mapped[List["Order"]] = db.relationship(back_populates="customer")

# Join table for order and product tables
order_product = db.Table(
    "Order_Product",
    Base.metadata,
    db.Column("product_id", db.ForeignKey("Products.product_id"), primary_key=True),
    db.Column("order_id", db.ForeignKey("Orders.order_id"), primary_key=True)
)

class Product(Base):
    __tablename__ = "Products"
    product_id:     Mapped[int] =   mapped_column(primary_key=True)
    name:           Mapped[str] =   mapped_column(db.String(255), nullable=False)
    price:          Mapped[float] = mapped_column(db.Float, nullable=False)

    def __str__(self):
        return f"Product: {self.product_id} {self.name}"

class Order(Base):
    __tablename__ = "Orders"
    order_id:           Mapped[int] =               mapped_column(primary_key=True)
    customer_id:        Mapped[int] =               mapped_column(db.ForeignKey("Customers.customer_id"))
    order_date:         Mapped[datetime.date] =     mapped_column(db.Date, nullable=False)

    delivery_date:      Mapped[datetime.date] =     mapped_column(db.Date, nullable=False )
    delivery_complete:  Mapped[bool] =              mapped_column(db.Boolean, default=False)
    order_total:        Mapped[float] =             mapped_column(db.Float)
    order_cancelled:    Mapped[bool] =              mapped_column(db.Boolean, default=False)

    customer:           Mapped["Customer"] =        db.relationship(back_populates="orders")
    products:           Mapped[List["Product"]] =   db.relationship(secondary=order_product)

    def __str__(self):
        return f"Order: {self.order_id} | Customer: {self.customer_id}"

with app.app_context():
    db.create_all()
    # db.drop_all() # uncomment to reset database

### ============ SCHEMA FOR TABLES ============ ###

# Product Schema
class ProductSchema(ma.Schema):
    product_id =    fields.Integer(required=False)
    name =          fields.String(required=True)
    price =         fields.Float(required=True)

    class Meta:
        fields = ("product_id", "name", "price")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Order Schema
class OrderSchema(ma.Schema):
    order_id =          fields.Integer(required=False)
    customer_id =       fields.Integer(required=True)
    customer_name =     fields.String(attribute="customer.name")
    order_date =        fields.Date(required=True)
    delivery_date =     fields.Date(required=False)
    delivery_complete = fields.Boolean(required=False)
    order_total       = fields.Float(required=False)
    order_cancelled =   fields.Boolean(required=False)
    products =          fields.List(fields.Nested(ProductSchema))

    class Meta:
        fields = ("order_id", "customer_id", "customer_name", "order_date", "delivery_date", 
                  "delivery_complete", "products", "order_total", "order_cancelled")

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

# Customer Schemas
class CustomerSchema(ma.Schema):
    customer_id =   fields.Integer(required=False)
    name =          fields.String(required=True)
    email =         fields.String(required=True)
    phone =         fields.String(required=True)
    orders =        fields.List(fields.Nested(OrderSchema))

    class Meta:
        fields = ("customer_id", "name", "email", "phone", "orders")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


### ============ APP ROUTES ============ ###

# home page
@app.route("/")
def home():
    return "<h1>WELCOME</h1>"

### ============ APP ROUTES: CUSTOMER ROUTES ============ ###

# get all customers
@app.route("/customers", methods = ["GET"])
def get_customers():
    # fetch and return all rows from Customers table
    query = select(Customer)
    result = db.session.execute(query).scalars()
    customers = result.all()
    return customers_schema.jsonify(customers)

# get single customer by id
@app.route("/customers/<int:id>", methods=["GET"])
def get_customer(id):
    query = select(Customer).filter(Customer.customer_id == id)
    customer = db.session.execute(query).scalar()
    return customer_schema.jsonify(customer)

# search customers by name
@app.route('/customers/search/<string:keyword>', methods=["GET"])
def search_customers(keyword):
    search = f"%{keyword}%"
    query = select(Customer).where(Customer.name.like(search)).order_by(Customer.name.asc())
    customer = db.session.execute(query).scalars()
    return customers_schema.jsonify(customer)

# add new customer
@app.route("/customers", methods=["POST"])
def add_customer():
    # validate incoming customer data
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    
    # insert new customer into Customers table
    with Session(db.engine) as session:
        new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
        session.add(new_customer)
        session.commit()
    return jsonify({"Message":"New Customer Added Successfully"}), 201

# update existing customer
@app.route("/customers/<int:id>", methods=["PUT"])
def update_customer(id):
    with Session(db.engine) as session:
        with session.begin():

            # find customer to update
            query = select(Customer).filter(Customer.customer_id == id)
            result = session.execute(query).scalar()
            if result is None:
                return jsonify({"Error":"Customer Not Found"}), 404
            customer = result

            # validate incoming customer data
            try:
                customer_data = customer_schema.load(request.json)
            except ValidationError as error:
                return jsonify(error.messages), 400
            
            # update data for specified customer
            for field, value in customer_data.items():
                setattr(customer, field, value)
            session.commit()
    return jsonify({"Message":"Customer Details Updated Successfully"}), 200

# delete customer from table
@app.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    try:
        # find and delete customer
        delete_statement = delete(Customer).where(Customer.customer_id==id)
        with db.session.begin():
            result = db.session.execute(delete_statement)
            if result.rowcount == 0:
                return jsonify({"Error":"Customer Not Found"}), 404
        return jsonify({"Message":"Customer Removed Successfully"}), 200
    
    # handle errors - including trying to delete a customer that is used in an order
    except Exception as error:
        return jsonify({"Error": f"{error}"})

### ============ APP ROUTES: PRODUCT ROUTES ============ ###

# get all products
@app.route("/products", methods = ["GET"])
def get_products():
    # fetch and return all rows from Products table
    query = select(Product)
    result = db.session.execute(query).scalars()
    products = result.all()
    return products_schema.jsonify(products)

# get single product by id
@app.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    query = select(Product).filter(Product.product_id == id)
    product = db.session.execute(query).scalar()
    return product_schema.jsonify(product)

# search for product by name
@app.route('/products/search/<string:keyword>', methods=["GET"])
def search_products(keyword):
    search = f"%{keyword}%"
    query = select(Product).where(Product.name.like(search)).order_by(Product.name.asc())
    products = db.session.execute(query).scalars()
    return products_schema.jsonify(products)

# add new product
@app.route("/products", methods=["POST"])
def add_product():
    # validate incoming product data
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    
    # insert new product into Products table
    with Session(db.engine) as session:
        new_product = Product(name=product_data['name'], price=product_data['price'])
        session.add(new_product)
        session.commit()
    return jsonify({"Message":"New Product Added Successfully"}), 201

# update existing product
@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    with Session(db.engine) as session:
        with session.begin():

            # find product to update
            query = select(Product).filter(Product.product_id == id)
            result = session.execute(query).scalar()
            if result is None:
                return jsonify({"Error":"Product Not Found"}), 404
            product = result

            # validate incoming product data
            try:
                product_data = product_schema.load(request.json)
            except ValidationError as error:
                return jsonify(error.messages), 400
            
            # update data for specified product
            for field, value in product_data.items():
                setattr(product, field, value)
            session.commit()
    return jsonify({"Message":"Product Details Updated Successfully"}), 200

# delete product from table
@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    try:
        # find and delete product
        delete_statement = delete(Product).where(Product.product_id==id)
        with db.session.begin():
            result = db.session.execute(delete_statement)
            if result.rowcount == 0:
                return jsonify({"Error":"Product Not Found"}), 404
        return jsonify({"Message":"Product Removed Successfully"}), 200
        # handle errors - including trying to delete a product that is used in an order
    except Exception as error:
        return jsonify({"Error": f"{error}"})

### ============ APP ROUTES: ORDER ROUTES ============ ###

# get all orders
@app.route("/orders", methods = ["GET"])
def get_orders():
    # fetch and return all rows from Orders table, adding customer name to order as well
    query = select(Order, Customer.name).join_from(Order, Customer)
    result = db.session.execute(query).scalars()
    products = result.all()
    return orders_schema.jsonify(products)
# to-do, add and print products!

# get single order by id
@app.route("/orders/<int:id>", methods=["GET"])
def get_order(id):
    # fetch and return order by ID, displaying customer name as well
    query = select(Order, Customer.name).join_from(Order, Customer).where(Order.order_id == id)
    order = db.session.execute(query).scalar()
    return order_schema.jsonify(order)

# add new order to Order table
@app.route("/orders", methods=["POST"])
def add_order():
    try:
        # separate products list to parse below
        json_order = request.json
        products = json_order.pop('products')
        if products == []:
            return jsonify({"Error":"Cannot Place Order without Products"}), 400
        # validate incoming order data
        order_data = order_schema.load(json_order)
    except ValidationError as error:
        return jsonify(error.messages), 400
    
    with Session(db.engine) as session:
        with session.begin():
            # create new order for insertion into Order table
            new_order = Order(
                customer_id=order_data['customer_id'],
                order_date=order_data['order_date'], 
                delivery_date=set_delivery_date(order_data['order_date'])
                )
            # if delivery date is in the past, it must be complete!
            if new_order.delivery_date < datetime.date.today():
                new_order.delivery_complete = True
            
            # keep track of order total
            order_total = 0.0

            # populate order products using product IDs passed in via json
            for id in products:
                product = session.execute(select(Product).filter(Product.product_id == id)).scalar()
                if product:
                    new_order.products.append(product)
                    order_total += product.price
                    # print(f"\nPRODUCT ADDED: {product.__str__()}\n") # used for debugging
                    # known issue: cannot order more than 1 of a product
                else:
                    return jsonify({"Error": f"Product with ID {id} Not found"}), 404

            # add order total into Order
            new_order.order_total = order_total

            # insert new order into Order table
            session.add(new_order)
            session.commit()
    return jsonify({"Message":"New Order Added Successfully"}), 201

# create randomized delivery date 2-5 days after order date
def set_delivery_date(order_date):
    estimated_delivery_span = random.randint(2,5)
    delivery_date = order_date + datetime.timedelta(days=estimated_delivery_span)
    # if delivery date is a Sunday, deliver next day; no deliveries on Sundays!
    if delivery_date.weekday() == 6:
        delivery_date += datetime.timedelta(days=1)
    return delivery_date

# cancel existing order if not already completed
@app.route("/orders/cancel/<int:id>", methods=["PUT"])
def cancel_order(id):
    with Session(db.engine) as session:
        with session.begin():

            # find order to update
            query = select(Order).filter(Order.order_id == id)
            result = session.execute(query).scalar()
            if result is None:
                return jsonify({"Error":"Order Not Found"}), 404
            order = result

            # check if delivery has already been completed; if so, cannot be cancelled
            if order.delivery_complete == True:
                return jsonify({"Error":"Order has already been delivered. It cannot be cancelled."}), 400
            
            # cancel order
            else:
                setattr(order, "order_cancelled", True)
            session.commit()            
    return jsonify({"Message":f"Order Cancelled"}), 200

# run script in debug mode
if __name__ == "__main__":
    app.run(debug=True)