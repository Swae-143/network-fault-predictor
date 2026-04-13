import pandas as pd
import numpy as np

np.random.seed(42)

n = 1000

data = pd.DataFrame({
    "latency": np.random.normal(50, 10, n),
    "packet_loss": np.random.normal(2, 1, n),
    "cpu_usage": np.random.normal(60, 15, n),
    "memory_usage": np.random.normal(65, 10, n),
})

# Create failure condition
data["failure"] = (
    (data["latency"] > 70) |
    (data["packet_loss"] > 4) |
    (data["cpu_usage"] > 85)
).astype(int)

data.to_csv("network_data.csv", index=False)

print("Data generated!")