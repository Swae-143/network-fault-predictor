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

def trigger_alert(
    status,
    confidence,
    device_name,
    device_type,
    ip_address,
    interface_name,
    link_name,
    location_name
):

    current_time = datetime.datetime.now()

    asset_info = f"""
Device: {device_name}
Device Type: {device_type}
IP Address: {ip_address}
Interface: {interface_name}
Link: {link_name}
Location: {location_name}
AI Confidence: {confidence:.2f}%
"""

    email_sent = False
    sms_sent = False

    # 🚨 Fibre cut
    if status == "FIBRE_CUT":

        print(f"[CRITICAL 🚨] Fibre cut detected at {current_time}")
        print(asset_info)

        email_sent = send_email_alert(
            "🚨 Fibre Cut Detected",
            f"""
A fibre cut has been detected.

{asset_info}

Immediate engineer response is required.
"""
        )

        sms_sent = send_sms_alert(
            f"🚨 FIBRE CUT\n"
            f"Device: {device_name}\n"
            f"Interface: {interface_name}\n"
            f"Location: {location_name}\n"
            f"AI Confidence: {confidence:.1f}%"
        )

    # 🚨 Hardware failure
    elif status == "HARDWARE_FAILURE":

        print(f"[CRITICAL 🚨] Hardware failure detected at {current_time}")
        print(asset_info)

        email_sent = send_email_alert(
            "🚨 Hardware Failure Detected",
            f"""
A hardware failure has been detected.

{asset_info}

Immediate technical investigation is required.
"""
        )

        sms_sent = send_sms_alert(
            f"🚨 HARDWARE FAILURE\n"
            f"Device: {device_name}\n"
            f"Interface: {interface_name}\n"
            f"Location: {location_name}\n"
            f"AI Confidence: {confidence:.1f}%"
        )

    # 🚨 Link down
    elif status == "LINK_DOWN":

        print(f"[CRITICAL 🚨] Link Down Detected at {current_time}")
        print(asset_info)

        email_sent = send_email_alert(
            "🚨 Network Link Down",
            f"""
A network link has been detected as DOWN.

{asset_info}

Please investigate the affected connection.
"""
        )

        sms_sent = send_sms_alert(
            f"🚨 LINK DOWN\n"
            f"Device: {device_name}\n"
            f"Interface: {interface_name}\n"
            f"Link: {link_name}\n"
            f"Location: {location_name}\n"
            f"AI Confidence: {confidence:.1f}%"
        )

    # ⚠️ Congestion
    elif status == "CONGESTION":

        print(f"[WARNING ⚠️] Network congestion detected at {current_time}")
        print(asset_info)

        email_sent = send_email_alert(
            "⚠️ Network Congestion Detected",
            f"""
Network congestion has been detected.

{asset_info}

Please monitor the affected network segment.
"""
        )

        sms_sent = send_sms_alert(
            f"⚠️ CONGESTION\n"
            f"Device: {device_name}\n"
            f"Interface: {interface_name}\n"
            f"Location: {location_name}\n"
            f"AI Confidence: {confidence:.1f}%"
        )

    # ✅ Normal
    elif status == "NORMAL":

        print(
            f"[OK ✅] Network healthy | "
            f"{device_name} | "
            f"{location_name}"
        )

    return email_sent, sms_sent

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

        server.sendmail(
            sender,
            receiver,
            msg.as_string()
        )

        server.quit()

        print("✅ EMAIL SENT SUCCESSFULLY")

        return True

    except Exception as e:

        print("❌ EMAIL ERROR:")
        print(e)

        return False

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

        return True

    except Exception as e:

        print("SMS failed:", e)

        return False
    
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

    # -----------------------------------------------------
    # Get simulated network metrics
    # -----------------------------------------------------

    data = get_snmp_metrics()

    latency = data["latency"]
    jitter = data["jitter"]
    packet_loss = data["packet_loss"]
    bandwidth = data["bandwidth"]

    cpu = data["cpu_usage"]
    memory = data["memory_usage"]

    link_status = data["link_status"]
    traffic = data["traffic"]

    scenario = data["scenario"]

    # Device information
    device_name = data["device_name"]
    device_type = data["device_type"]
    ip_address = data["ip_address"]

    # Interface / link
    interface_name = data["interface_name"]
    link_name = data["link_name"]

    # Location
    location_name = data["location_name"]
    latitude = data["latitude"]
    longitude = data["longitude"]


    # -----------------------------------------------------
    # Fibre cut detection
    # -----------------------------------------------------

    if link_status == 0 and traffic < 5:

        status = "FIBRE_CUT"
        confidence = 100.0


    # -----------------------------------------------------
    # Link down detection
    # -----------------------------------------------------

    elif link_status == 0 and traffic >= 5:

        status = "LINK_DOWN"
        confidence = 100.0


    # -----------------------------------------------------
    # AI Classification
    # -----------------------------------------------------

    else:

        input_data = pd.DataFrame([{

            "latency": latency,
            "jitter": jitter,
            "packet_loss": packet_loss,
            "bandwidth": bandwidth,

            "cpu_usage": cpu,
            "memory_usage": memory,

            "link_status": link_status,
            "traffic": traffic

        }])


        # Load latest trained model
        latest_model = joblib.load(
            "models/model.pkl"
        )


        prediction = latest_model.predict(
            input_data
        )[0]


        probs = latest_model.predict_proba(
            input_data
        )[0]


        # -------------------------------------------------
        # Model label mapping
        # -------------------------------------------------

        reverse_map = {

            0: "NORMAL",

            1: "CONGESTION",

            2: "HARDWARE_FAILURE",

            3: "FIBRE_CUT",

            4: "LINK_DOWN"

        }


        status = reverse_map.get(
            prediction,
            "UNKNOWN"
        )


        confidence = float(max(probs) * 100)


    # -----------------------------------------------------
    # Store event in PostgreSQL
    # ----------------------------------------------------

    confidence = float(confidence)

    try:
        cursor.execute("""
        INSERT INTO network_metrics
        (
            latency,
            packet_loss,
            cpu_usage,
            memory_usage,
            status,
            confidence,
            link_status,
            traffic,
            scenario,
            latitude,
            longitude,
            jitter,
            bandwidth,
            device_name,
            device_type,
            ip_address,
            interface_name,
            link_name,
            location_name
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """,(
        latency,
        packet_loss,
        cpu,
        memory,
        status,
        confidence,
        link_status,
        traffic,
        scenario,
        latitude,
        longitude,
        jitter,
        bandwidth,
        device_name,
        device_type,
        ip_address,
        interface_name,
        link_name,
        location_name
        ))

        conn.commit()

    except Exception as e:
      conn.rollback()

      print("========================================")
      print("❌ DATABASE INSERT ERROR")
      print(e)
      print("========================================")

      return jsonify({
        "error": str(e)
      }), 500


    # ============================================================
    # RESOLVE OPEN EVENT WHEN DEVICE/LINK RETURNS TO NORMAL
    # ============================================================

    if status == "NORMAL":
        cursor.execute("""
            SELECT id
            FROM network_events
            WHERE device_name = %s
              AND interface_name = %s
              AND link_name = %s
              AND event_state = 'OPEN'
            ORDER BY event_time DESC
            LIMIT 1
        """, (
            device_name,
            interface_name,
            link_name
        ))

        open_event = cursor.fetchone()

        if open_event:
            event_id = open_event[0]

            cursor.execute("""
                UPDATE network_events
                SET
                    event_state = 'RESOLVED',
                    resolved_at = CURRENT_TIMESTAMP,
                    last_seen = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (event_id,))

            conn.commit()

            print(
                f"✅ EVENT RESOLVED | "
                f"{device_name} | "
                f"{interface_name} | "
                f"{location_name}"
            )

    # -----------------------------------------------------
    # Event tracking and deduplication
    # -----------------------------------------------------

    if status != "NORMAL":

        # Check whether this exact fault is already OPEN
        cursor.execute("""
            SELECT id
            FROM network_events
            WHERE status = %s
              AND device_name = %s
              AND interface_name = %s
              AND link_name = %s
              AND event_state = 'OPEN'
            ORDER BY event_time DESC
            LIMIT 1
        """, (
            status,
            device_name,
            interface_name,
            link_name
        ))

        existing_event = cursor.fetchone()


        # -------------------------------------------------
        # Existing incident
        # -------------------------------------------------

        if existing_event:

            event_id = existing_event[0]

            cursor.execute("""
                UPDATE network_events
                SET
                    last_seen = CURRENT_TIMESTAMP,
                    confidence = %s,
                    latency = %s,
                    jitter = %s,
                    packet_loss = %s,
                    bandwidth = %s,
                    cpu_usage = %s,
                    memory_usage = %s,
                    link_status = %s,
                    traffic = %s
                WHERE id = %s
            """, (
                confidence,
                latency,
                jitter,
                packet_loss,
                bandwidth,
                cpu,
                memory,
                link_status,
                traffic,
                event_id
            ))

            conn.commit()

            print(
                f"🔄 EXISTING EVENT UPDATED | "
                f"{status} | "
                f"{device_name} | "
                f"{interface_name}"
            )


        # -------------------------------------------------
        # New incident
        # -------------------------------------------------

        else:

            cursor.execute("""
                INSERT INTO network_events
                (
                    status,
                    confidence,

                    device_name,
                    device_type,
                    ip_address,

                    interface_name,
                    link_name,

                    location_name,
                    latitude,
                    longitude,

                    latency,
                    jitter,
                    packet_loss,
                    bandwidth,

                    cpu_usage,
                    memory_usage,

                    link_status,
                    traffic,

                    scenario,

                    event_state,
                    last_seen
                )

                VALUES
                (
                    %s,
                    %s,

                    %s,
                    %s,
                    %s,

                    %s,
                    %s,

                    %s,
                    %s,
                    %s,

                    %s,
                    %s,
                    %s,
                    %s,

                    %s,
                    %s,

                    %s,
                    %s,

                    %s,

                    'OPEN',
                    CURRENT_TIMESTAMP
                )
                        """, (
                status,
                confidence,

                device_name,
                device_type,
                ip_address,

                interface_name,
                link_name,

                location_name,
                latitude,
                longitude,

                latency,
                jitter,
                packet_loss,
                bandwidth,

                cpu,
                memory,

                link_status,
                traffic,

                scenario
            ))

            conn.commit()

            # -------------------------------------------------
            # Send alerts ONLY for a NEW incident
            # -------------------------------------------------

            email_sent, sms_sent = trigger_alert(
                status=status,
                confidence=confidence,
                device_name=device_name,
                device_type=device_type,
                ip_address=ip_address,
                interface_name=interface_name,
                link_name=link_name,
                location_name=location_name
            )

            # -------------------------------------------------
            # Record alert delivery status
            # -------------------------------------------------

            cursor.execute("""
                UPDATE network_events
                SET
                    alert_email_sent = %s,
                    alert_sms_sent = %s
                WHERE id = (
                    SELECT id
                    FROM network_events
                    WHERE status = %s
                      AND device_name = %s
                      AND interface_name = %s
                      AND link_name = %s
                      AND event_state = 'OPEN'
                    ORDER BY event_time DESC
                    LIMIT 1
                )
            """, (
                email_sent,
                sms_sent,
                status,
                device_name,
                interface_name,
                link_name
            ))

            conn.commit()

            print(
                f"🚨 NEW EVENT LOGGED | "
                f"{status} | "
                f"{device_name} | "
                f"{interface_name} | "
                f"{location_name}"
            )

            print(
                f"📧 Email alert sent: {email_sent} | "
                f"📱 SMS alert sent: {sms_sent}"
            )
           
    return jsonify({

        "status": status,

        "confidence": round(
            confidence,
            2
        ),

        # Metrics
        "latency": latency,
        "jitter": jitter,
        "packet_loss": packet_loss,
        "bandwidth": bandwidth,

        "cpu_usage": cpu,
        "memory_usage": memory,

        "link_status": link_status,
        "traffic": traffic,

        # Device
        "device_name": device_name,
        "device_type": device_type,
        "ip_address": ip_address,

        # Interface / Link
        "interface_name": interface_name,
        "link_name": link_name,

        # Location
        "location_name": location_name,
        "latitude": latitude,
        "longitude": longitude,

        # Scenario
        "scenario": scenario

    })

@app.route("/latest")
def latest_data():

    latest_cursor = conn.cursor()

    try:

        latest_cursor.execute("""
            SELECT
                latency,
                packet_loss,
                cpu_usage,
                memory_usage,
                status,
                confidence,
                link_status,
                traffic,
                scenario,
                latitude,
                longitude,
                jitter,
                bandwidth,
                device_name,
                device_type,
                ip_address,
                interface_name,
                link_name,
                location_name,
                created_at

            FROM network_metrics

            ORDER BY created_at DESC

            LIMIT 1
        """)

        row = latest_cursor.fetchone()

        if row:

            return jsonify({

                # Core metrics
                "latency": row[0],
                "packet_loss": row[1],
                "cpu_usage": row[2],
                "memory_usage": row[3],

                # Fault
                "status": row[4],
                "confidence": row[5],
                "link_status": row[6],
                "traffic": row[7],
                "scenario": row[8],

                # Location
                "latitude": row[9],
                "longitude": row[10],

                # Additional metrics
                "jitter": row[11],
                "bandwidth": row[12],

                # Device
                "device_name": row[13],
                "device_type": row[14],
                "ip_address": row[15],

                # Interface / Link
                "interface_name": row[16],
                "link_name": row[17],

                # Location name
                "location_name": row[18],

                # Timestamp
                "created_at": row[19]

            })

        else:

            return jsonify({
                "message": "No data yet"
            })

    finally:

        latest_cursor.close()