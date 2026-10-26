
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

username = "root"
password = "Trisha@73"

encoded_password = quote_plus(password)

engine = create_engine(
    f"mysql+pymysql://{username}:{encoded_password}@127.0.0.1:3306/ecommerce_analytics"
)

tables = {
    "order_items": "Data/olist_order_items_dataset.csv",
    "products": "Data/olist_products_dataset.csv",
    "customers": "Data/olist_customers_dataset.csv",
    "payments": "Data/olist_order_payments_dataset.csv"
}

for table_name, file_path in tables.items():
    df = pd.read_csv(file_path)

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=5000
    )

    print(f"{table_name}: {len(df)} rows loaded")

print("\nAll sales analysis tables loaded successfully!")
