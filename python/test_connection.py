from database import engine
from sqlalchemy import text

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE();"))
        database_name = result.scalar()

        print(f"Connected successfully!")
        print(f"Database: {database_name}")

except Exception as e:
    print("Database connection failed.")
    print(e)