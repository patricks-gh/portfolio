import pandas as pd
import re
import base64
import uuid
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe

gc = gspread.service_account(filename="../../../python/auth_keys/service_account.json")
sheet = gc.open("Admin - The Beauty Hub").worksheet("productlist")

# Load sheet
df = get_as_dataframe(sheet, evaluate_formulas=True)

# -------------------------------------------------------
# CLEANUP
# -------------------------------------------------------

required_cols = ["Brand", "Product Name", "Unit"]
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Missing Column: {col}")

# Normalize empty text values
for col in required_cols:
    df[col] = (
        df[col]
        .astype("string")
        .replace(["nan", "NaN", None], "")
        .fillna("")
        .str.strip()
    )

# Remove rows where ALL 3 are empty
df = df[~(
    (df["Brand"] == "") &
    (df["Product Name"] == "") &
    (df["Unit"] == "")
)]
df = df.reset_index(drop=True)

# -------------------------------------------------------
# PRODUCT ID HANDLING
# -------------------------------------------------------

if "Product ID" not in df.columns:
    df["Product ID"] = ""

df["Product ID"] = (
    df["Product ID"]
    .astype("string")
    .replace(["nan", "NaN", "None"], "")
    .fillna("")
    .str.strip()
)

def generate_product_id():
    # Generate a UUID4
    u = uuid.uuid4()
    # Convert to bytes and encode in URL-safe base64, remove trailing '='
    b64_uuid = base64.urlsafe_b64encode(u.bytes).rstrip(b'=').decode('ascii')
    return b64_uuid

# NEW RULE:
# Generate ONLY IF:
# - Product ID is blank
# - Brand NOT empty
# - Product Name NOT empty
# (Unit can be empty)
mask_pid = (
    (df["Product ID"] == "") &
    (df["Brand"] != "") &
    (df["Product Name"] != "")
)

df.loc[mask_pid, "Product ID"] = df.loc[mask_pid].apply(
    lambda row: generate_product_id(), axis=1
)

# -------------------------------------------------------
# SKU GENERATION
# -------------------------------------------------------

def product_sku_creation(row):
    brand = str(row.get('Brand', "")).strip()
    product = str(row.get('Product Name', "")).strip()
    unit = str(row.get('Unit', "")).strip()

    brand_clean = re.sub(r'[^A-Za-z0-9\s-]', '', brand)
    product_clean = re.sub(r'[^A-Za-z0-9\s-]', '', product)

    # Brand Code
    if not brand_clean:
        brand_code = ""
    elif brand_clean.isdigit():
        brand_code = brand_clean
    else:
        parts = [w for w in re.split(r'[\s-]+', brand_clean) if w]
        brand_code = parts[0][0].upper() + parts[-1][0].upper() if len(parts) == 1 else ''.join(w[0].upper() for w in parts)

    # Product Code
    if not product_clean:
        product_code = ""
    else:
        parts = [w for w in re.split(r'[\s-]+', product_clean) if w]
        product_code = ''.join(w[0].upper() for w in parts)

    # Unit code
    unit_code = re.sub(r'\s+', '', unit.upper())

    parts = [p for p in [brand_code, product_code, unit_code] if p]
    return "-".join(parts)

if "SKU" not in df.columns:
    df["SKU"] = ""

df["SKU"] = (
    df["SKU"]
    .astype("string")
    .replace(["nan", "NaN", "None"], "")
    .fillna("")
    .str.strip()
)

mask_sku = (df["SKU"] == "")
df.loc[mask_sku, "SKU"] = df.loc[mask_sku].apply(product_sku_creation, axis=1)

# -------------------------------------------------------
# WRITE BACK
# -------------------------------------------------------

set_with_dataframe(sheet, df)
print("✅ Product IDs + SKUs updated successfully!")
