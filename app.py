from flask import Flask, jsonify, render_template
import mysql.connector
import plotly.express as px
import plotly.io as pio
import pandas as pd

app = Flask(__name__)
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='bobatea'
    )
    return connection

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()

     # Fetch customer data from the 'customers' table
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    cursor.execute("SELECT * FROM Orders")
    orders = cursor.fetchall()

     # Fetch customer data from the 'customers' table
    cursor.execute("SELECT * FROM Supplier_Order_Items")
    supplier_order_items = cursor.fetchall()

    cursor.execute("SELECT * FROM Supplier_orders")
    supplier_orders = cursor.fetchall()

    cursor.execute("SELECT customer_id, loyalty_points FROM customers")
    data = cursor.fetchall()

    # Query to get the total sales amount from the orders table
    cursor.execute("""
        SELECT SUM(total_amount) AS total_sales
FROM orders;
    """)
    # Fetch the result
    total_sales_amount = cursor.fetchone()

    cursor.execute("""
    SELECT COUNT(*) AS number_of_orders
    FROM orders;
""")
    num_orders = cursor.fetchone()

    cursor.execute("""
    SELECT COUNT(*) AS pending_orders
    FROM supplier_orders
    WHERE status = 'Pending';
""")

# Fetch the result
    pending_orders = cursor.fetchone()

    cursor.execute("""
    SELECT COUNT(*) AS total_customers
    FROM customers;
""")

# Fetch the result
    total_customers = cursor.fetchone()

    # Query for the latest order
    cursor.execute("""
    SELECT *
    FROM orders
    ORDER BY date DESC
    LIMIT 1;
""")
    latest_order = cursor.fetchone()

# Query for the latest supplier order
    cursor.execute("""
    SELECT *
    FROM supplier_orders
    ORDER BY order_date DESC
    LIMIT 1;
""")
    latest_supplier_order = cursor.fetchone()


# Optionally, format the value (e.g., as currency with 2 decimal places)


    
    # Extract customer ids and loyalty points
    customer_ids = [row['customer_id'] for row in data]
    loyalty_points = [row['loyalty_points'] for row in data]

    # Create a DataFrame using Plotly Express
    df = pd.DataFrame({
        'Customer ID': customer_ids,
        'Loyalty Points': loyalty_points
    })
  # Create a Plotly chart (bar chart in this case)
    fig = px.bar(df, x='Customer ID', y='Loyalty Points', title="Customer Loyalty Points")
    # Convert Plotly figure to HTML to embed in the template
    chart_html = pio.to_html(fig, full_html=False)




     # SQL query to get top 3 customers by total spending
    cursor.execute("""
        SELECT cName, SUM(total_amount) AS total_spent
        FROM Orders
        JOIN Customers ON Orders.customer_id = Customers.customer_id
        GROUP BY cName
        ORDER BY total_spent DESC
        LIMIT 3;
    """)
    data = cursor.fetchall()

    # Prepare data for Plotly pie chart
    customer_names = [row['cName'] for row in data]
    total_spent = [row['total_spent'] for row in data]

    # Create a DataFrame for easy handling with Plotly
    df = pd.DataFrame({
        'Customer Name': customer_names,
        'Total Spent': total_spent
    })

    # Create a Plotly Pie chart
    fig = px.pie(df, names='Customer Name', values='Total Spent', title="Top 3 Customers by Total Spending")

    # Convert Plotly figure to HTML to embed in the template
    pie_chart_html = pio.to_html(fig, full_html=False)



    # Query to get the most popular addons by total quantity used
    cursor.execute("""
        SELECT aName, SUM(quantity) AS total_used
        FROM Order_Addons
        JOIN Addons ON Order_Addons.addon_id = Addons.addon_id
        GROUP BY aName
        ORDER BY total_used DESC;
    """)
    data = cursor.fetchall()

    # Prepare data for Plotly pie chart
    addon_names = [row['aName'] for row in data]
    total_used = [row['total_used'] for row in data]

    # Create a DataFrame for easy handling with Plotly
    df = pd.DataFrame({
        'Addon Name': addon_names,
        'Total Used': total_used
    })

    # Create a Plotly Pie chart for most popular addons
    fig = px.pie(df, names='Addon Name', values='Total Used', title="Most Popular Addons")

    # Convert Plotly figure to HTML to embed in the template
    addons_pie_chart_html = pio.to_html(fig, full_html=False)


     # Query to get the total_amount grouped by date
    cursor.execute("""
        SELECT date, SUM(total_amount) AS total_spent
        FROM Orders
        GROUP BY date
        ORDER BY date;
    """)
    data = cursor.fetchall()

    # Prepare data for Plotly line chart
    dates = [row['date'] for row in data]
    total_spent = [row['total_spent'] for row in data]

    # Create a DataFrame for easy handling with Plotly
    df = pd.DataFrame({
        'Date': dates,
        'Total Spent': total_spent
    })

    # Create a Plotly Line chart
    fig = px.line(df, x='Date', y='Total Spent', title="Total Amount Spent Over Time")

    # Convert Plotly figure to HTML to embed in the template
    line_chart_html = pio.to_html(fig, full_html=False)

# Query to get the top 10 supplier orders and their total amounts (prices)
    cursor.execute("""
    SELECT soi.supplier_order_id, SUM(soi.quantity * soi.item_price) AS total_amount
    FROM supplier_order_items soi
    GROUP BY soi.supplier_order_id
    ORDER BY total_amount DESC
    LIMIT 10;
    """)
    data = cursor.fetchall()

    # Ensure data is returned in dictionary-like structure
    order_ids = [row['supplier_order_id'] for row in data]
    total_amounts = [row['total_amount'] for row in data]

    # Create a DataFrame for easy handling with Plotly
    df = pd.DataFrame({
        'Order ID': order_ids,
        'Total Amount ($)': total_amounts
    })

    # Create a Plotly Column chart (Vertical Bar chart)
    fig = px.bar(df, x='Order ID', y='Total Amount ($)', title="Top 10 Supplier Orders by Total Amount")

    # Convert Plotly figure to HTML to embed in the template
    supply_column_chart_html = pio.to_html(fig, full_html=False)


    cursor.close()
    conn.close()
    return render_template('index.html', latest_order=latest_order,latest_supplier_order=latest_supplier_order,total_customers=total_customers,pending_orders=pending_orders,num_orders=num_orders,total_sales_amount=total_sales_amount,orders=orders, products=products, customers=customers, supplier_order_items=supplier_order_items, supplier_orders=supplier_orders, chart_html=chart_html, pie_chart_html=pie_chart_html, addons_pie_chart_html=addons_pie_chart_html, line_chart_html=line_chart_html, supply_column_chart_html=supply_column_chart_html)

if __name__ == '__main__':
    app.run(debug=True)
