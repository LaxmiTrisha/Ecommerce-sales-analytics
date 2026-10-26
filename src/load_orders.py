
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

username = "root"
password = "Trisha@73"

encoded_password = quote_plus(password)

engine = create_engine(
    f"mysql+pymysql://{username}:{encoded_password}@127.0.0.1:3306/ecommerce_analytics"
)

# Read CSV
df = pd.read_csv("Data/olist_orders_dataset.csv")

# Load data into MySQL
df.to_sql(
    name="orders",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=5000
)

print("Orders data loaded successfully!")

# Verify the row count
with engine.connect() as connection:
    result = connection.exec_driver_sql(
        "SELECT COUNT(*) FROM orders"
    )
    print("Rows in MySQL:", result.scalar())
