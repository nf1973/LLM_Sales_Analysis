import kagglehub
import pandas as pd
import os
import sqlite3
import chardet

# Download latest version of the sales dataset
path = kagglehub.dataset_download("kyanyoga/sample-sales-data")

# Check how the file is encoded
with open(os.path.join(path, "sales_data_sample.csv"), "rb") as f:
    raw_data = f.read(10000)
    encoding_detected = chardet.detect(raw_data)["encoding"]

# Read CSV
df = pd.read_csv(os.path.join(path, "sales_data_sample.csv"), encoding=encoding_detected)

# Convert ORDERDATE column to a proper datetime format (e.g., YYYY-MM-DD)
df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce').dt.strftime('%Y-%m-%d')

# Create SQLite database
db_name = "sales_data.db"  
conn = sqlite3.connect(db_name)
df.to_sql("sales", conn, if_exists="replace", index=False)

print(pd.read_sql("SELECT name FROM PRAGMA_TABLE_INFO('sales');", conn))
print(pd.read_sql("SELECT COUNT(*) FROM sales;", conn), "rows")
print(pd.read_sql("SELECT COUNT(DISTINCT CUSTOMERNAME) FROM sales;", conn), "unique customers")
print(pd.read_sql("SELECT COUNT(DISTINCT CONTACTLASTNAME) FROM sales;", conn), "unique contact last names")
print(pd.read_sql("SELECT COUNT(DISTINCT YEAR_ID) FROM sales;", conn), "unique years")
print(pd.read_sql("SELECT COUNT(DISTINCT PRODUCTLINE) FROM sales;", conn), "unique product lines")
print(pd.read_sql("SELECT COUNT(DISTINCT COUNTRY) FROM sales;", conn), "unique countries")
print(pd.read_sql("SELECT * FROM sales LIMIT 5;", conn))
print(pd.read_sql("SELECT ORDERDATE FROM sales LIMIT 5;", conn))


conn.close()

