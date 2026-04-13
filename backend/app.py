from flask import Flask, request, jsonify, render_template
import os
import joblib
import numpy as np

app = Flask(__name__)

model = joblib.load("models/model.pkl")

# Serve frontend
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    features = np.array([[
        data["latency"],
        data["packet_loss"],
        data["cpu_usage"],
        data["memory_usage"]
    ]])

    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]

    return jsonify({
        "failure_prediction": int(prediction),
        "failure_probability": float(probability)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))