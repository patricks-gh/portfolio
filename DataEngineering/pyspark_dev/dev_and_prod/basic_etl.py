"""
Introduction:

This example shows basic dev scripts on staging data:
    1. Read data from staging files
    2. Review data from staging files 
    3-4. Perform filtering/transformation

📖TIP:
    Spark prints a lot of information to the console. To keep your terminal clean,
    you can run this script like this:
        python app.py > output.txt 2> error.txt
    That will save your query results to 'output.txt' and any Spark warnings/errors to 'error.txt'.
    (Optional: skip this if you are comfortable with log messages.)
"""

from pyspark.sql import SparkSession
import os

################################ CREATE A SPARK SESSION ################################                  

spark = SparkSession.builder \
    .appName("basic_etl") \
    .master("local[*]") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")


################################ LOAD CSV INTO A DATAFRAME ################################  

customers_staging = spark.read.option("header", True).option("sep", "\t").csv("../data_cleanup/staging/customers_staging.csv")
sales_raw = spark.read.option("header", True).option("sep", ",").csv("../csv/sales_dirty.csv") # No data cleanup for this demo, a challenge from me (Patrick) for you to perform.

################################ PERFORM SOME BASIC QUERIES ################################  

# Place staging files into temporary views
customers_staging.createOrReplaceTempView("customers")
sales_raw.createOrReplaceTempView("sales")

# View the data initially before making any changes
test_customers = spark.sql("select * from customers")
test_sales = spark.sql("select * from sales")

test_customers.show(10, truncate=False)
test_sales.show(10, truncate=False)

# filter only customers who has email
customers_w_contact = spark.sql("select * from customers where email is not null")

# filter only sales data for 2025
sales_filtered_by_dt = spark.sql("select * from sales where sale_date >= '2025-01-01'") 

customers_w_contact.createOrReplaceTempView("customers_filtered")
sales_filtered_by_dt.createOrReplaceTempView("sales_filtered")

# Perform a simple join and count how many sales per customer with email there is for 2025
customers_dev = spark.sql("""
    SELECT 
        c.customer_id, 
        c.customer_name, 
        c.email, 
        COUNT(s.sale_id) AS total_sales
    FROM customers_filtered AS c
    LEFT JOIN sales_filtered AS s 
        ON c.customer_id = s.customer_id
    GROUP BY 
        c.customer_id, 
        c.customer_name, 
        c.email
""")

customers_dev.show(10)


################################ CREATE A CSV FILE FOR PROD DATA ################################  

# Convert dataframe to pandas
customers_dev = customers_dev.toPandas()

# Optional: replace None/null with 'NULL' for ETL
customers_dev = customers_dev.fillna("NULL")

output_csv_path = "dev/customers_dev.csv"

# Create staging folder if it doesn't exist
os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

# Write CSV
customers_dev.to_csv(output_csv_path, sep="\t", index=False)
print(f"Customer dev data written to: {output_csv_path}")


# Once prod data has been created it can be used or ingested elsewhere that uses SQL scripting