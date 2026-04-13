import os
import subprocess

print("🚀 Starting Network Fault Prediction System...\n")

# Train only if model doesn't exist
if not os.path.exists("models/model.pkl"):
    print("🧠 Training model...")
    subprocess.run("python models/train_model.py", shell=True)
else:
    print("✅ Model already exists. Skipping training.")

print("🌐 Starting full system (Backend + Frontend)...")
subprocess.run("python backend/app.py", shell=True)