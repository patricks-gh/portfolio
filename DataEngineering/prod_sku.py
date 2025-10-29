import pandas as pd
import re
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe

# Connect to Google Sheets
gc = gspread.service_account(filename="../../python/auth_keys/service_account.json")
sheet = gc.open("Admin - The Beauty Hub").worksheet("productlist")

# Read sheet into DataFrame
df = get_as_dataframe(sheet, evaluate_formulas=True).dropna(how='all')

# --- Validation ---
required_cols = ["Brand", "Product Name", "Unit"]
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Missing Column: {col}")

# --- SKU Generation Function ---
def product_sku_creation(row):
    # Replace NaN with empty strings
    brand = "" if pd.isna(row.get('Brand')) else str(row['Brand']).strip()
    product = "" if pd.isna(row.get('Product Name')) else str(row['Product Name']).strip()
    unit = "" if pd.isna(row.get('Unit')) else str(row['Unit']).strip()

    # Remove special characters
    brand_clean = re.sub(r'[^A-Za-z0-9\s-]', '', brand)
    product_clean = re.sub(r'[^A-Za-z0-9\s-]', '', product)

    # --- Brand Code ---
    if not brand_clean:
        brand_code = ""
    elif brand_clean.isdigit():
        brand_code = brand_clean
    else:
        brand_words = [w for w in re.split(r'[\s-]+', brand_clean) if w]
        if len(brand_words) == 1:
            brand_code = brand_clean[0].upper() + brand_clean[-1].upper()
        else:
            brand_code = ''.join(w[0].upper() for w in brand_words)

    # --- Product Code ---
    if not product_clean:
        product_code = ""
    else:
        product_words = [w for w in re.split(r'[\s-]+', product_clean) if w]
        product_code = ''.join(w[0].upper() for w in product_words)

    # --- Unit Code ---
    unit_code = re.sub(r'\s+', '', unit.upper()) if unit else ""

    # Join non-empty parts
    parts = [p for p in [brand_code, product_code, unit_code] if p]
    return "-".join(parts)

# --- SKU Column Prep ---
if "SKU" not in df.columns:
    df["SKU"] = ""

# Convert to pandas string dtype (preserves NaN) and clean up bad values
df["SKU"] = (
    df["SKU"]
    .astype("string")
    .replace(["nan", "NaN", "None"], "")
    .fillna("")
)

# Drop fully empty rows & reset index
df = df.dropna(how="all").reset_index(drop=True)

# --- SKU Assignment ---
mask = df["SKU"].astype(str).str.strip().str.lower().isin(["", "nan", "none"])
df.loc[mask, "SKU"] = df.loc[mask].apply(product_sku_creation, axis=1)

# --- Write back to Google Sheets ---
set_with_dataframe(sheet, df)

print("✅ SKUs updated in Google Sheets successfully!")
