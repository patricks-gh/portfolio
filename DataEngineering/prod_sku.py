import pandas as pd
import re
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe

gc = gspread.service_account(filename="../../python/auth_keys/service_account.json")

sheet = gc.open("Admin - The Beauty Hub Store").worksheet("productlist")

df = get_as_dataframe(sheet, evaluate_formulas=True).dropna(how='all')

#Checks if the target columns exist, if not throw an error
required_cols = ["Brand","Product Name","Unit"]

for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Missing Column: {col}")

#Main function 
def product_sku_creation(row):

    #Replace NaN values with empty strings instead, as this affects the SKU to be Brand-ProductName-NaN for products w/ blank Unit
    brand = "" if pd.isna(row.get('Brand')) else str(row['Brand']).strip()
    product = "" if pd.isna(row.get('Product Name')) else str(row['Product Name']).strip()
    unit = "" if pd.isna(row.get('Unit')) else str(row['Unit']).strip()

    #Remove special characters from product names, this also affects the SKU to be Brand-Product#Name(-100G for product names with a special character
    brand_clean = re.sub(r'[^A-Za-z0-9\s-]', '', brand)
    product_clean = re.sub(r'[^A-Za-z0-9\s-]', '', product)

    #BRAND CODE
    if not brand_clean:
        brand_code = ""
    elif brand.isdigit():
        brand_code = brand_clean
    else:
        brand_words = re.split(r'[\s-]+', brand_clean)
        brand_words = [w for w in brand_words if w]
        if len(brand_words) == 1:
            brand_code = brand_clean[0].upper() + brand_clean[-1].upper()
        else:
            brand_code = ''.join(word[0].upper() for word in brand_words if word)
    
    #PRODUCT CODE
    if not product_clean:
        product_code = ""
    else:
        product_words = re.split(r'[\s-]+', product_clean)
        product_code = ''.join(word[0].upper() for word in product_words if word)

    #UNIT CODE 
    unit_code = re.sub(r'\s+', '', unit.upper()) if unit else ""

    parts = [p for p in [brand_code, product_code, unit_code] if p]
    return "-".join(parts)

if "SKU" not in df.columns:
    df["SKU"] = ""

df = df.dropna(how="all").reset_index(drop=True)


for i in range(len(df)):
    if pd.isna(df.iloc[i]["SKU"]) or df.iloc[i]["SKU"] == "":
        df.loc[i, "SKU"] = product_sku_creation(df.loc[i])

# Write the updated dataframe to google sheet 
set_with_dataframe(sheet, df)


print("SKUs updated in google sheets")