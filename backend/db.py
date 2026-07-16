from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS network_metrics (
    id SERIAL PRIMARY KEY,
    latency FLOAT,
    packet_loss FLOAT,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    status VARCHAR(50),
    link_status INT,
    traffic FLOAT,
    scenario VARCHAR(50),
    latitude FLOAT,
    longitude FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()