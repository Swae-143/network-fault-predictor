import threading
import time
import subprocess
import pandas as pd
import joblib
model = joblib.load("models/model.pkl")
from flask import Flask, jsonify, send_from_directory
import os
from backend.snmp_simulator import get_snmp_metrics
from backend.db import conn, cursor
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText


app = Flask(__name__, static_folder="../frontend", static_url_path="")

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

import datetime

def trigger_alert(status):

    current_time = datetime.datetime.now()

    # 🚨 Fibre cut
    if status == "FIBRE_CUT":
        print(f"[CRITICAL 🚨] Fibre cut detected at {current_time}")

        send_email_alert(
            "Fibre Cut Detected",
            "A fibre cut has been detected. Network services may be unavailable."
        )

        send_sms_alert(
            "FIBRE CUT detected. Immediate engineer response required."
        )

    # 🚨 Hardware failure
    elif status == "HARDWARE_FAILURE":
        print(f"[CRITICAL 🚨] Hardware failure detected at {current_time}")

        send_email_alert(
            "Hardware Failure Detected",
            "Critical hardware failure detected on network infrastructure."
        )

        send_sms_alert(
            "HARDWARE FAILURE detected. Immediate action required."
        )

    # 🚨 Link down
    elif status == "LINK_DOWN":
        print(f"[CRITICAL 🚨] Link down detected at {current_time}")

        send_email_alert(
            "Link Down Detected",
            "A network link is currently down."
        )

        send_sms_alert(
            "LINK DOWN detected. Check backbone connectivity."
        )

    # ⚠️ Congestion
    elif status == "CONGESTION":
        print(f"[WARNING ⚠️] Network congestion detected at {current_time}")

    # ✅ Normal
    elif status == "NORMAL":
        print(f"[OK ✅] Network healthy at {current_time}")

def send_email_alert(subject, body):
    sender = "EMAIL_USER"
    password = "EMAIL_PASS"
    receiver = "muutwikaeliaserndafetango@gmail.com"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        server = smtplib.SMTP("owa.telecom.na", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(sender, password)

        server.sendmail(sender, receiver, msg.as_string())
        server.quit()

        print("✅ EMAIL SENT SUCCESSFULLY")

    except Exception as e:
        print("❌ EMAIL ERROR:")
        print(e)


def send_sms_alert(message):

    account_sid = "TWILIO_ACCOUNT_SID"
    auth_token = "TWILIO_AUTH_TOKEN"

    client = Client(account_sid, auth_token)

    try:
        client.messages.create(
            body=message,
            from_="+17622164664",
            to="+18777804236"
        )

        print("📱 SMS sent")

    except Exception as e:
        print("SMS failed:", e)

import sys

def auto_train_model():

    while True:

        try:
            print("🔄 Retraining AI model...")

            subprocess.run(
                [sys.executable, "models/train_model.py"],
                check=True
            )

            print("✅ Model retrained successfully!")

        except Exception as e:
            print("❌ Retraining failed:", e)

        # every 5 minutes
        time.sleep(300)

# 🚀 Start automatic AI retraining
training_thread = threading.Thread(
    target=auto_train_model,
    daemon=True
)

# training_thread.start()

@app.route("/generate")
def generate_data():
    import pandas as pd

    data = get_snmp_metrics()

    latency = data["latency"]
    packet_loss = data["packet_loss"]
    cpu = data["cpu_usage"]
    memory = data["memory_usage"]
    link_status = data["link_status"]
    traffic = data["traffic"]
    scenario = data["scenario"]

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # 🚨 RULE-BASED (instant fibre cut detection)
    if link_status == 0 and traffic < 5:
        status = "FIBRE_CUT"
        confidence = 100.0

    else:
        # 🤖 AI Prediction
        input_data = pd.DataFrame([{
            "latency": latency,
            "packet_loss": packet_loss,
            "cpu_usage": cpu,
            "memory_usage": memory,
            "link_status": link_status,
            "traffic": traffic
        }])

        latest_model = joblib.load("models/model.pkl")

        prediction = latest_model.predict(input_data)[0]
        probs = latest_model.predict_proba(input_data)[0]


        # 🔥 Convert numeric → label
        reverse_map = {
    0: "NORMAL",
    1: "CONGESTION",
    2: "HARDWARE_FAILURE",
    3: "FIBRE_CUT",
    4: "LINK_DOWN"
}
        status = reverse_map.get(prediction, "UNKNOWN")
        confidence = max(probs) * 100

    # 🚨 Trigger alert
    trigger_alert(status)

    # ✅ Save correct data
    cursor.execute("""
        INSERT INTO network_metrics 
        (latency, packet_loss, cpu_usage, memory_usage, status, link_status, traffic, scenario, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (latency, packet_loss, cpu, memory, status, link_status, traffic, scenario, latitude,
          longitude))

    conn.commit()

    return {
    "status": status,
    "confidence": round(confidence, 2),
    "latitude": latitude,
    "longitude": longitude
}

@app.route("/latest")
def latest_data():
    cursor.execute("""
        SELECT latency, packet_loss, cpu_usage, memory_usage, status, scenario, latitude, longitude
        FROM network_metrics
        ORDER BY created_at DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    if row:
        return jsonify({
            "latency": row[0],
            "packet_loss": row[1],
            "cpu_usage": row[2],
            "memory_usage": row[3],
            "status": row[4],
            "scenario": row[5],
            "latitude": row[6],
            "longitude": row[7]
        })
    else:
        return jsonify({"message": "No data yet"})
