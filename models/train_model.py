import pandas as pd
import psycopg2
import os
import joblib
from sklearn.ensemble import RandomForestClassifier

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="network_db",
    user="postgres",
    password="admin123"
)

# Load data
query = """
SELECT latency, packet_loss, cpu_usage, memory_usage, link_status, traffic, scenario
FROM network_metrics
"""
df = pd.read_sql(query, conn)

# Clean data (remove nulls)
df = df.dropna(subset=["scenario"])

# Normalize text
df["scenario"] = df["scenario"].str.strip().str.upper()

# Encode labels
label_map = {
    "NORMAL": 0,
    "HIGH_TRAFFIC": 1,
    "CONGESTION": 2,
    "FIBRE_CUT": 3,
    "LINK_DOWN": 4
}

df["scenario"] = df["scenario"].map(label_map)

# Remove invalid mappings
df = df.dropna(subset=["scenario"])

# Features (AFTER CLEANING)
X = df[['latency', 'packet_loss', 'cpu_usage', 'memory_usage', 'link_status', 'traffic']]

# Target
y = df["scenario"]

print("Unique scenarios:", df["scenario"].unique())
print("Samples:", len(df))

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)


# Save model in correct location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

joblib.dump(model, MODEL_PATH)

print("✅ Multi-class model trained!")