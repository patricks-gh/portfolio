import pandas as pd
import numpy as np
import csv as csv
import re
import logging
from tqdm import tqdm
import chardet
import os
import tkinter as tk
from tkinter import filedialog, messagebox

##########################################################################
#                             LOGGING SETUP                              #
##########################################################################

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

##########################################################################
#                             FILE PICKER                                #
##########################################################################

root = tk.Tk()
root.withdraw() # Keep this code to hide main tkinter window 

input_csv = filedialog.askopenfilename(
    title="SELECT CSV FILE",
    filetypes=[("CSV Files", "*.csv"), ("All files","*.*")]
)

if not input_csv:
    messagebox.showwarning("No file selected.", "Closing window now...")
    exit()


##########################################################################
#                             OUTPUT FILE                                #
##########################################################################

base_name = os.path.splitext(os.path.basename(input_csv))[0]
output_csv = f"{base_name}_cleaned.csv"
tmp_file = "csv_file_tab_removed.csv"
NULL_VALUE = "NULL"
SEP = "\t"


##########################################################################
#                             FILE ENCODING                              #
##########################################################################

logging.info("Detecting file encoding...")
with open(input_csv, 'rb') as f: 
    raw_data = f.read(10000)
    enc = chardet.detect(raw_data)['encoding'] or 'utf-8'
logging.info(f"Detected encoding: {enc}")


##########################################################################
#                         REMOVE TABS FROM DATA                          #
##########################################################################

logging.info("Removing tabs and preparing clean copy...")

# Determine safe encoding for reading
safe_enc = enc if enc and enc.lower() in ['utf-8', 'latin1', 'iso-8859-1'] else 'utf-8'

# Read file safely, replacing undecodable chars
with open(input_csv, 'r', encoding=safe_enc, errors='replace') as f:
    content = f.read().replace('\t', '')

# Write file safely, also handling encoding errors
# Use the same encoding as safe_enc, and replace unencodable chars
with open(tmp_file, 'w', encoding=safe_enc, errors='replace') as f:
    f.write(content)

##########################################################################
#                   READ CSV WITH PROGRESS BAR DISPLAYED                 #
##########################################################################

logging.info("Loading CSV into DataFrame...")
chunks = []
for chunk in tqdm(pd.read_csv(tmp_file, encoding=safe_enc, dtype=str, chunksize=100000, low_memory=False),desc="Reading CSV in chunks"):
    chunks.append(chunk)
df = pd.concat(chunks, ignore_index=True)
logging.info(f"CSV loaded successfully, Rows: {len(df):,}, Columns: {len(df.columns)}")


##########################################################################
#                             COLUMN CLEANING                            #
##########################################################################

def clean_column_name(col):
    cleaned = re.sub(r'[^0-9a-zA-Z]+', '_', col.strip())
    cleaned = cleaned.rstrip('_').lower()
    return cleaned

df.columns = [clean_column_name(col) for col in df.columns]

# Handle duplicate column names
df.columns = [f"{col}_{i+1}" if (df.columns[:i] == col).any() else col 
              for i, col in enumerate(df.columns)]

##########################################################################
#                             NORMALIZE VALUES                           #
##########################################################################

def normalize_values(df):
    for col in tqdm(df.columns, desc="Normalizing Column Values"):
        
        # Convert values to str 
        df[col] = df[col].astype(str).str.strip()

        # For boolean-like text
        df[col] = df[col].replace(
            {"yes": "1", "no": "0", "true": "1", "false": "0"},
            regex=True
        )

        # attempt numeric conversion safely
        try:
            df[col] = pd.to_numeric(df[col])
        except Exception:
            pass
    
    return df

df = normalize_values(df)


##########################################################################
#                    HANDLE NULLS AND DATETIME NaT                       #
##########################################################################

# 1. Fix datetime columns safely
for col in df.select_dtypes(include=[np.datetime64, 'datetime']).columns:
    df[col] = df[col].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else NULL_VALUE)

# 2. Replace numeric NaN, blanks, and "nan" strings with NULL
df = df.replace([np.nan, 'nan', '', 'NaT'], NULL_VALUE)



##########################################################################
#                             SUMMARY REPORT                             #
##########################################################################
logging.info("Generating summary...")
logging.info(f"Final DataFrame shape: {df.shape}")
logging.info("Missing values per column (before replacement): ")
logging.info(df.replace(NULL_VALUE, np.nan).isna().sum().to_dict())


##########################################################################
#                                  OUTPUT                                #
##########################################################################

logging.info("Writing cleansed CSV to output...")
df.to_csv(output_csv, sep=SEP, index=False, quoting=csv.QUOTE_MINIMAL)


messagebox.showinfo("CSV Cleaner", f"Cleaning complete!\nSaved to: \n{os.path.abspath(output_csv)}")
logging.info(f"Cleaning complete!\nSaved to: \n{os.path.abspath(output_csv)}")