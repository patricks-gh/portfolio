"""
Introduction:

This example shows basic clean up on the following columns:
    1. Clean Headers
    2. Clean Names
    3. Clean Emails
    4. Clean Cities
    5. Clean Countries 

This will only contain 2 main parts: raw and staging while dev and prod will be in the next one.

📖TIP:
    Spark prints a lot of information to the console. To keep your terminal clean,
    you can run this script like this:
        python app.py > output.txt 2> error.txt
    That will save your query results to 'output.txt' and any Spark warnings/errors to 'error.txt'.
    (Optional: skip this if you are comfortable with log messages.)
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import regexp_replace, trim, initcap, col
import pandas as pd
import os
import re

################################ CREATE A SPARK SESSION ################################                  

spark = SparkSession.builder \
    .appName("data_cleanup") \
    .master("local[*]") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")


################################ LOAD CSV INTO A DATAFRAME ################################  
               
# raw: uncleaned column names, values, and formatting
customers_df = spark.read.option("header", True).csv("../csv/customers_dirty.csv")


################################ PERFORM BASIC DATA CLEANUP ################################                  

# staging: cleaned column names, values, and formatting ready for transformation 
# 1. headers
def clean_headers(df):
    clean_cols = []
    for col in df.columns:
        new_col = col.lower()                 # lowercase
        new_col = new_col.strip()             # remove leading/trailing spaces
        new_col = re.sub(r'[^a-zA-Z0-9]+', '_', new_col)  # replace special chars w/ underscore
        new_col = re.sub(r'_+', '_', new_col) # remove repeated __
        new_col = new_col.rstrip('_')         # remove trailing _
        clean_cols.append(new_col)
    return df.toDF(*clean_cols)

customers = clean_headers(customers_df)

# 2. customer_name: capitalize initial letters and trim white spaces
customers = customers \
        .filter((F.col("customer_id").isNotNull()) & (F.col("customer_id") != "")) \
        .withColumn("customer_name", F.initcap(F.trim("customer_name"))) 

# 3. email: trim white spaces, lower caps, and check email format
customers = customers \
        .withColumn("email", F.lower(F.trim("email"))) \
        .withColumn("email", F.when(
                F.col("email").rlike(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
                F.col("email")
            ).otherwise(None)
        )

# 4. city: trim white spaces, capitialize initials, and set null to bad format
customers = customers \
        .withColumn("city", F.trim(F.col("city"))) \
        .withColumn("city", F.initcap(F.col("city"))) \
        .withColumn("city", F.when(F.col("city").isin("", "NA", "N/A", "-", "Unknown"), None) \
                          .otherwise(F.col("city")))

# 5. country: trim white spaces, capitialize initials, and set null to bad format
customers = customers \
        .withColumn("country", trim(col("country"))) \
        .withColumn("country", regexp_replace(col("country"), r'\?', '')) \
        .withColumn("country", regexp_replace(col("country"), r'\(.*?\)', '')) \
        .withColumn("country", initcap(col("country"))) \
        .withColumn("country", F.when(col("country") == "", None).otherwise(col("country")))


################################ CREATE A NEW CSV FOR STAGING DATA ################################  

# Convert dataframe to pandas
customers_staging = customers.toPandas()

# Optional: replace None/null with 'NULL' for ETL
customers_staging = customers_staging.fillna("NULL")

output_csv_path = "staging/customers_staging.csv"

# Create staging folder if it doesn't exist
os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

# Write CSV
customers_staging.to_csv(output_csv_path, sep="\t", index=False)
print(f"Customer staging data written to: {output_csv_path}")

################################ DISPLAY DATA FOR VALIDATION ################################                  

customers.select("customer_id", "customer_name", "email", "city", "country").sample(0.1).show(20, False)
