from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

username = "root"
password = "Trisha@73"

encoded_password = quote_plus(password)

engine = create_engine(
    f"mysql+pymysql://{username}:{encoded_password}@127.0.0.1:3306/ecommerce_analytics"
)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE()"))
        print("Connected successfully!")
        print("Database:", result.scalar())
except Exception as error:
    print("Connection failed:")
    print(error)
