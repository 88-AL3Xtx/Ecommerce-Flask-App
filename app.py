
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from sqlalchemy import DateTime, Float, ForeignKey, String, func, select, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List



# Initialized Flask - 1)
app = Flask(__name__)



# MYSQL database configuration - 2)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Matty1229@localhost/ecommerce_app'   # ----> This will create our database connection.



# Creating our Base Model - 3)
class Base(DeclarativeBase):
    pass

# Here, we are going to Initialize our extentions
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)


# ====== Creating my Tables & Association / Junction table =============


# Table Buyer
class Buyer(Base):
    __tablename__ = "buyers"

    id: Mapped[int] = mapped_column(primary_key=True)       # --------> This is our primary Key id for buyer's table
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # ----> This is our string value name with its datatype String with a nullable false in which it cannot accept a null value.
    address: Mapped[str] = mapped_column(String(100), nullable=False)  #------> Same as above, with 100 characters max.
    email: Mapped[str] = mapped_column(String(100), unique=True)  # ----> Same as above but includes a unique=true, which the value in the column must be unique. can't have the same value in that column.

    orders : Mapped[List["Orders"]]= relationship(back_populates= "buyer")  # This is a one - to - many relationship with the Orders table referencing the buyer.



# Association Table
order_product = Table(    # ----> This is our junction table.
    "order_product",      # --> this is our table name
    Base.metadata,   # ---> This tells SQLAlchemy that this table should be included in the same metadata collection as your ORM models.
    Column("order_id", ForeignKey("orders.id"), primary_key=True),  # ---> This creates our column name, "order_id" referencing our foreignkey "orders.id" in our Orders table id. The primary key uniquely identifies each row in the table.
    Column("product_id", ForeignKey("products.id"), primary_key=True) #---> Same as above.
)


# Table
class Orders(Base):                 # -----> This is our Orders Table.
    __tablename__ = "orders"  # --> Table name

    id: Mapped[int] = mapped_column(primary_key=True)  # ----> This is our id column with its datatype "int" referencing an integer. Our primary Key.
    order_date = mapped_column(DateTime, default=func.now())  # ----> This is our order_date table. Including our TimeStamp which tells SQLAlchemy to automatically set the value of this column to the current date and time (according to the database server’s clock) when a new row is inserted and no value is provided for this column.
    buyer_id: Mapped[int] = mapped_column(ForeignKey("buyers.id"), nullable=False) # --> This is our buyer_id column which references our buyers id. It cannot accept a null value.


    buyer : Mapped["Buyer"] = relationship(back_populates= "orders")  # one to many relationship with the buyer referencing the orders.

    placed_products: Mapped[List["Products"]] = relationship(secondary=order_product, back_populates= "placed_orders")  # This will be our many-to-many relationship with the association table.



#Table
class Products(Base):
    __tablename__ = "products"   # --> Our products table

    id: Mapped[int] = mapped_column(primary_key=True)     # ---> This is our id column. our primary key for the products table.
    product_name: Mapped[str] = mapped_column(String(100)) #---> Our product's name column. Including 100 characters.
    price: Mapped[float] = mapped_column(Float, nullable=False) # ---> This is our price column. It will be a Float as a datatype. It cannot accept a null value.


    placed_orders: Mapped[List["Orders"]] = relationship(secondary=order_product, back_populates= "placed_products")  # --> This is our many - to - many relationship. with our Orders table and Products



# ===============SCHEMAS ==============================================

# What a schema does it describes the structure of the data and how various objects relate to one another.
# Therefore, by using schema we can serialized objects.
# By serialization - meaning we can convert our python objects into JSON.
# By deserilazation - we can translate JSON objects into python usable objects or dictionary.

class BuyerSchema(ma.SQLAlchemyAutoSchema):   # ---> This will be our Buyer schema to validate our buyer data
    class Meta:
        model = Buyer



class ProductSchema(ma.SQLAlchemyAutoSchema):  #--> This will be our Product schema to valiadate our product data
    class Meta:
        model = Products



class OrderSchema(ma.SQLAlchemyAutoSchema):  # --> This will be our Order schema to validate our order schema
    class Meta:
        model = Orders
        include_fk = True #  I will apply this beacuse the Auto Schema doesn't automatically recognize foreign keys (buyer_id)



# === Initialized Schemas ===

buyer_schema = BuyerSchema()   #----> This is going to be an intance of our Buyer schema class in which can only translate a (single) buyer object.
buyers_schema = BuyerSchema(many=True) #---> This allows for the serialization of a list of many Buyer objects in which it can traslate a (list/many) of them.

order_schema = OrderSchema()   # --------> This will be the same as the above buyer schema but order.
orders_schema = OrderSchema(many=True)  # ----> This will be the same as the above buyer schema but order.


product_schema = ProductSchema()  # -----> This will be the same as the above buyer schema but product.
products_schema = ProductSchema(many=True) # ---> This will be the same as the above buyer schema but product.



#-----------------------------------------------------------------------------------------------------

# ========== Creating Routes / Creating API Endpoints C.R.U.D =============================


# *** User C.R.U.D ***

# READ the buyers with a GET request.

@app.route('/buyers', methods=["GET"])    #----> The buyers is the endpoint.  Its when a client makes an HTTP GET request to the URL path /buyers. In which it will repond to the GET request only.
def get_buyers():
    query = select(Buyer)
    buyers = db.session.execute(query).scalars().all() #---> This will execute the query and concert row objects into scalar objects.

    return buyers_schema.jsonify(buyers), 200

# # # READ - Individual

@app.route('/buyers/<int:id>', methods=["GET"])
def get_buyer(id):
    buyer = db.session.get(Buyer, id)
    return buyer_schema.jsonify(buyer), 200



# # ==========================================================

# # CREATE the buyers with a post request.
@app.route('/buyers', methods=["POST"])
def create_buyer():
    try:
        buyer_data = buyer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_buyer = Buyer(name = buyer_data["name"], address = buyer_data['address'], email = buyer_data['email'])
    db.session.add(new_buyer)
    db.session.commit()

    return buyer_schema.jsonify(new_buyer), 200 #----> So the message will include this jsonify with new_buyer and the 201 status. Meaning that is a successful creation status and that it work. -- Route complete --
#                                                      ------> Now to Test it, we are going to use Postman. Postman is a wonderfull tool for testing APIs making sure that the calls are functioning perfectly.


# # ==========================================================

# # UPDATE Individual User

@app.route('/buyers/<int:id>', methods=["PUT"])
def update_buyer(id):
    buyer = db.session.get(Buyer, id)

    if not buyer:
        return jsonify({"message": "Invalid buyer id, try again ....."}), 400  # ---> If it doesnt return the buyer id, will return a 400 status code which will return the message provided.

    try:
        buyer_data = buyer_schema.load(request.json)
    except ValidationError as e:  # -------> This will through them an error the front end if they send us something we dont need like or simply missing information needed like name or email. And that is going to come as a form of a Marshmaloow "ValidationError".
        return jsonify(e.messages),


    buyer.name = buyer_data["name"]    # -----> This will apply the and ensure the name, adress, and email in the postman which will update in our database.
    buyer.address = buyer_data["address"]
    buyer.email = buyer_data["email"]

    db.session.commit()
    return buyer_schema.jsonify(buyer), 200

# # ==========================================================


# # DELETE Individual User.

@app.route('/buyers/<int:id>', methods=['DELETE'])  #----> The buyers is the endpoint.  Its when a client makes an HTTP Delete request to the URL path /buyers. In which it will repond to the Delete request only.
def delete_buyer(id):
    buyer = db.session.get(Buyer, id)

    if not buyer:
        return jsonify({"message": "Invalid buyer id, try again..."}), 400

    db.session.delete(buyer)
    db.session.commit()

    return jsonify({"message": f"You've successfully deleted the buyer {id}."}), 200


# # ==========================================================


# # ****** Product C.R.U.D ******


# # READ All Products

@app.route('/products', methods=['GET'])  #----> The /products endpoint.  Its when a client makes an HTTP GET request to the URL path /products. In which it will repond to the Get request only.
def get_products():
    query = select(Products)
    products = db.session.execute(query).scalars().all()

    return products_schema.jsonify(products), 200


# # # # READ - Individual product

@app.route('/products/<int:id>', methods=["GET"])
def get_product(id):
    product = db.session.get(Products, id)
    return product_schema.jsonify(product), 200

# # ---------------------------------------------------------------

# CREATE product
@app.route('/products', methods=["POST"])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.message), 400

    new_product = Products(product_name = product_data["product_name"], price = float(product_data["price"]))

    db.session.add(new_product)  # ---> this will add our input new_product into our database and postman.
    db.session.commit()  # -------> this will commit our new_product into our database.

    return product_schema.jsonify(new_product)


# # ---------------------------------------------------------------

# UPDATE - product
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Products, id)

    if not product:
        return jsonify({"Message": "Invalid product id, try again..."}), 400

    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    product.product_name = product_data['product_name']
    product.price = float(product_data["price"])

    db.session.commit()
    return product_schema.jsonify(product), 200


# # ---------------------------------------------------------------

# # DELETE - product
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Products, id)

    if not product:
        return jsonify({"Message": "Invalid product id, try again."}), 400

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": f"You've successfully deleted the user {id}"}), 200



#___________________________________________________________________________________

# Order C.R.U.D ---

# == CREATE the Order ==
@app.route('/orders', methods=['POST'])
def create_order():

    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400


    # Retreve the customer by its Id
    buyer = db.session.get(Buyer, order_data["buyer_id"])


    # We are going to check if the buyer exists.
    if buyer:
        new_order = Orders(order_date = order_data["order_date"], buyer_id = order_data["buyer_id"])

        db.session.add(new_order)
        db.session.commit()

        return jsonify({"message": "New order placed!", "order" : order_schema.dump(new_order)}), 201
    else:
        return jsonify({"message":  "Invalid buyer id"}), 400


# == ADD a product To Order ==

@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product(order_id, product_id):

    order = db.session.get(Orders, order_id)
    product = db.session.get(Products, product_id)

    if order and product:
        if product not in order.placed_products:
            order.placed_products.append(product)
            db.session.commit()
            return jsonify({"message": "You've successfully added the product to the order."}), 200
        else:
            return jsonify({"message": "Product is already included to the order."}), 400
    else:
        return jsonify({"message": "Invalid order id or product id."}), 400



# == DELETE A Product from an Order ===

@app.route('/ordenes/<int:order_id>/remove_product/<int:product_id>', methods=["DELETE"])
def remove_product(order_id, product_id):

    order = db.session.get(Orders, order_id)
    product = db.session.get(Products, product_id)


    if not order or not product:
       return jsonify({"message": "The order or product was not found."}), 400
    if product not in order.placed_products:
       return jsonify({"message": "The product is not in the order"}), 400

    order.placed_products.remove(product)
    db.session.commit()

    return jsonify({"message": "The product has been remove from the order."}), 200




# == GET ====== Get All Orders for a Buyer ==

@app.route('/buyers/my-orders/<int:buyer_id>', methods=['GET'])
def my_orders(buyer_id):
    buyer = db.session.get(Buyer, buyer_id)
    return orders_schema.jsonify(buyer.orders)




# === GET ===== Get all products for an order ==

@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_products_for_order(order_id):
    order = db.session.get(Orders, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return products_schema.jsonify(order.placed_products), 200





# -----------------------------------------------------------------------------------------------------


if __name__ == "__main__":

    with app.app_context():
        db.create_all()        # This will create all of our tables.
    #    db.drop_all()           # This will delete all of our tables.

    app.run(debug=True)
