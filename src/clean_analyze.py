import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# 1. MySQL Database Connection
DATABASE_URL = "mysql+pymysql://root:Trisha%4073@localhost:3306/ecommerce_analytics"
engine = create_engine(DATABASE_URL)

print("--- 1. Loading raw data from MySQL ---")
# Loading available tables safely
orders = pd.read_sql("SELECT * FROM orders", con=engine)
order_items = pd.read_sql("SELECT * FROM order_items", con=engine)
customers = pd.read_sql("SELECT * FROM customers", con=engine)
products = pd.read_sql("SELECT * FROM products", con=engine)

print("--- 2. Data Cleaning & Transformations ---")
# Date columns conversion to Datetime format
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])

# Handle missing categories if any
if 'product_category_name' in products.columns:
    products['product_category_name'].fillna('Uncategorized', inplace=True)
else:
    products['product_category_name'] = 'Uncategorized'

# Master Order Level Dataset creation using merges
df = order_items.merge(orders, on='order_id', how='inner')
df = df.merge(products[['product_id', 'product_category_name']], on='product_id', how='left')
df = df.merge(customers[['customer_id', 'customer_unique_id', 'customer_state']], on='customer_id', how='left')

# Handle Missing Values in price/freight
df['price'] = df['price'].fillna(0)
df['freight_value'] = df['freight_value'].fillna(0)
df['total_amount'] = df['price'] + df['freight_value']

print("--- 3. RFM Customer Segmentation Calculation ---")
# Reference date for Recency calculation (1 day after max order date)
max_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

# Group by unique customer
rfm = df.groupby('customer_unique_id').agg({
    'order_purchase_timestamp': lambda x: (max_date - x.max()).days, # Recency
    'order_id': 'nunique',                                           # Frequency
    'total_amount': 'sum'                                           # Monetary
}).reset_index()

rfm.columns = ['customer_unique_id', 'Recency', 'Frequency', 'Monetary']

# Assign R, F, M Scores from 1 to 5 safely
rfm['R_score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
rfm['M_score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')

# Convert categories to string for concatenation
rfm['R_score'] = rfm['R_score'].astype(str)
rfm['F_score'] = rfm['F_score'].astype(str)
rfm['M_score'] = rfm['M_score'].astype(str)
rfm['RFM_Score'] = rfm['R_score'] + rfm['F_score'] + rfm['M_score']

def segment_customer(row):
    r, f = int(row['R_score']), int(row['F_score'])
    if r >= 4 and f >= 4:
        return 'Champions'
    elif r >= 3 and f >= 3:
        return 'Loyal Customers'
    elif r >= 3 and f <= 2:
        return 'Promising / Recent'
    elif r <= 2 and f >= 3:
        return 'At Risk / Need Attention'
    else:
        return 'Lost Customers'

rfm['Customer_Segment'] = rfm.apply(segment_customer, axis=1)

print("--- 4. Exporting Cleaned Data & RFM to MySQL ---")
df.to_sql('fact_master_orders', con=engine, if_exists='replace', index=False)
rfm.to_sql('dim_customer_rfm', con=engine, if_exists='replace', index=False)

print("Data Cleaning and RFM computation successfully completed!")

df.to_csv('fact_master_orders.csv', index=False)
rfm.to_csv('dim_customer_rfm.csv', index=False)