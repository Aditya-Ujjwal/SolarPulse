from sqlalchemy import create_engine

DB_USER = "root"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "solarpulse"

connection_string = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    connection_string,
    pool_pre_ping=True
)

print("Database connection created successfully.")