import os
import psycopg2

conn = psycopg2.connect(
    os.environ.get("DATABASE_URL")
)