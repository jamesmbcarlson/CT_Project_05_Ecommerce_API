## Project: E-Commerce API

Author: James Carlson

This project was built as an assignment for Coding Temple.

<br>
This application utilizes Flask and SQLAlchemy to manage a database of <b>Customers</b>, <b>Products</b>, and the <b>Orders</b> a Customer can place using Products, using a series of API requests.

<br>
In <i>/supporting_files</i>, you can find a list of packages used in this application, as well as an import file for the Postman API requests detailed below:


### <b>Customer Requests</b>
- <b><span style=color:rgb(107,221,154)>GET</span> ALL CUSTOMERS</b> - Retrieves all customers and their details, including any orders they have placed.
- <b><span style=color:rgb(107,221,154)>GET</span> CUSTOMER BY ID</b> - Retrieves single customer by thier unique identifier.
- <b><span style=color:rgb(107,221,154)>GET</span> CUSTOMERS BY SEARCH</b> - Retrieves customers whose names match the given search term. 
- <b><span style=color:rgb(255,228,126)>CREATE</span> CUSTOMER</b> - Adds new customer to table with required fields "name", "email", and "phone"
- <b><span style=color:rgb(116,174,246)>UPDATE</span> CUSTOMER</b> - Changes details of an existing customer at given ID.
- <b><span style=color:rgb(247,154,142)>DELETE</span> CUSTOMER</b> - Removes customer with given ID from database. A customer cannot be removed if they are associated with an order.

### <b>Product Requests</b>
- <b><span style=color:rgb(107,221,154)>GET</span> ALL PRODUCTS</b> - Retrieves all products and their details.
- <b><span style=color:rgb(107,221,154)>GET</span> PRODUCT BY ID</b> - Retrieves single product by its unique identifier.
- <b><span style=color:rgb(107,221,154)>GET</span> PRODUCTS BY SEARCH</b> - Retrieves products whose names match the given search term. 
- <b><span style=color:rgb(255,228,126)>CREATE</span> PRODUCT</b> - Adds new product to table with required fields "name" and "price"
- <b><span style=color:rgb(116,174,246)>UPDATE</span> PRODUCT</b> - Changes details of an existing product at given ID.
- <b><span style=color:rgb(247,154,142)>DELETE</span> PRODUCT</b> - Removes product with given ID from database. A product cannot be removed if they are associated with an order.

### <b>Order Requests</b>
- <b><span style=color:rgb(107,221,154)>GET</span> ALL ORDERS</b> - Retrieves all orders and their details.
- <b><span style=color:rgb(107,221,154)>GET</span> ORDER BY ID</b> - Retrieves single order by its unique identifier.
- <b><span style=color:rgb(255,228,126)>CREATE</span> ORDER</b> - 
    - Create/place new order to table with required fields "customer_id" (associates order with existing customer), "order_date", and "products", which takes a list of product_ids associated with existing products.
    - A delivery_date field is also randomly set 2 to 5 days after the order_date (not delivering on Sundays, of course)!
    - If the delivery_date has occured before today, delivery_complete is marked as true.
    - The total cost of all products in order is stored in order_total.
- <b><span style=color:rgb(116,174,246)>CANCEL</span> ORDER</b> - If an order has not already been delivered, it can be cancelled, marking the order_cancelled field to true.

<br>Below is an example of a customer with an order in its json format:

```
{
    "customer_id": 1,
    "name": "James Carlson",
    "email": "jamesmbcarlson@gmail.com",
    "phone": "719-555-5555",
    "orders": [
        {
            "order_id": 1,
            "customer_id": 1,
            "customer_name": "James Carlson",
            "order_date": "2024-04-12",
            "delivery_date": "2024-04-17",
            "delivery_complete": false,
            "products": [
                {
                    "product_id": 1,
                    "name": "Steam Deck 512GB OLED",
                    "price": 549.0
                },
                {
                    "product_id": 2,
                    "name": "Steam Deck 1TB OLED",
                    "price": 649.0
                }
            ],
            "order_total": 1198.0,
            "order_cancelled": false
        }
    ]
}
```

Thank you for reviewing my code!