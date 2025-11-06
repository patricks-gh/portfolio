"""
Introduction:

This example shows how to:
    1. Create a Spark session
    2. Read CSV files as DataFrames
    3. Register them as temporary SQL views
    4. Query them using spark.sql()
    5. View spark.sql query results 


📖TIP:
    Spark prints a lot of information to the console. To keep your terminal clean,
    you can run this script like this:
        python app.py > output.txt 2> error.txt
    That will save your query results to 'output.txt' and any Spark warnings/errors to 'error.txt'.
    (Optional: skip this if you are comfortable with log messages.)
"""

from pyspark.sql import SparkSession

# 1. Create Spark session
spark = SparkSession.builder \
    .appName("ReadCustomers") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN") #Prevent flood of INFO logs


# 2. Read the CSV file (with header columns)
customers_df = spark.read.option("header", True).csv("../csv/customers_dirty.csv")
products_df = spark.read.option("header", True).csv("../csv/products_dirty.csv")
sales_df = spark.read.option("header", True).csv("../csv/sales_dirty.csv")

# 3. Register DataFrames as temporary SQL views so we can query them with spark.sql()
customers_df.createOrReplaceTempView("customers")
products_df.createOrReplaceTempView("products")
sales_df.createOrReplaceTempView("sales")

# 4. Execute SQL commands on temporary SQL view
customers = spark.sql("SELECT * FROM customers ORDER BY customer_name")
products = spark.sql("SELECT * FROM products ORDER BY product_name asc")
sales = spark.sql("SELECT sale_date, count(1) as total_sales FROM sales GROUP BY sale_date ORDER BY total_sales desc")

# 5. Display results 
customers.show(5, truncate=False)
products.show(5, truncate=False)
sales.show(5, truncate=False)

# Stop Spark session
spark.stop()
