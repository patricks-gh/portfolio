import pandas as pd
import os
import re

INPUT_FOLDER = "picklist_input"
OUTPUT_FOLDER = "picklist_output"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Detect the only file in picklist_input
files = os.listdir(INPUT_FOLDER)
excel_files = [f for f in files if f.lower().endswith((".xls", ".xlsx"))]

if len(excel_files) != 1:
    raise Exception("picklist_input must contain exactly ONE Excel file.")

input_path = os.path.join(INPUT_FOLDER, excel_files[0])
print(f"Reading: {input_path}")

df = pd.read_excel(input_path)

output_rows = []

for _, row in df.iterrows():
    order_sn = row["order_sn"]
    info = str(row["product_info"])

    # Split by markers [1] [2] [3]
    products = re.split(r'\[\d+\]\s*', info)
    products = [p.strip() for p in products if p.strip()]

    for p in products:
        name = re.search(r'Product Name:(.*?);', p)
        variant = re.search(r'Variation Name:(.*?);', p)
        price = re.search(r'Price:\s*₱?(\d+)', p)
        quantity = re.search(r'Quantity:\s*(\d+)', p)

        output_rows.append({
            "order_sn": order_sn,
            "product_name": name.group(1).strip() if name else "",
            "variant_name": variant.group(1).strip() if variant else "",
            "price": int(price.group(1)) if price else None,
            "quantity": int(quantity.group(1)) if quantity else None
        })

clean_df = pd.DataFrame(output_rows)

# Save output
output_path = os.path.join(OUTPUT_FOLDER, "clean_output.xlsx")
clean_df.to_excel(output_path, index=False)

print(f"Done! Saved cleaned file to: {output_path}")
