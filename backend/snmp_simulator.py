import random

def get_snmp_metrics():

    scenario = random.choices(
        [
            "NORMAL",
            "CONGESTION",
            "HARDWARE_FAILURE",
            "FIBRE_CUT",
            "LINK_DOWN"
        ],

        # probabilities
        weights=[
            0.4,   # NORMAL
            0.2,   # CONGESTION
            0.15,  # HARDWARE_FAILURE
            0.15,  # FIBRE_CUT
            0.1    # LINK_DOWN
        ],

        k=1
    )[0]

    if scenario == "NORMAL":
        return {
            "latency": random.randint(20, 60),
            "packet_loss": round(random.uniform(0, 1), 2),
            "cpu_usage": random.randint(30, 60),
            "memory_usage": random.randint(40, 70),
            "link_status": 1,
            "traffic": random.randint(100, 1000),
            "scenario": "NORMAL"
        }

    elif scenario == "CONGESTION":
        return {
            "latency": random.randint(80, 150),
            "packet_loss": round(random.uniform(2, 6), 2),
            "cpu_usage": random.randint(70, 95),
            "memory_usage": random.randint(70, 95),
            "link_status": 1,
            "traffic": random.randint(900, 1500),
            "scenario": "CONGESTION"
        }

    elif scenario == "HARDWARE_FAILURE":
        return {
            "latency": random.randint(100, 200),
            "packet_loss": round(random.uniform(5, 15), 2),
            "cpu_usage": random.randint(90, 100),
            "memory_usage": random.randint(90, 100),
            "link_status": 1,
            "traffic": random.randint(200, 500),
            "scenario": "HARDWARE_FAILURE"
        }

    elif scenario == "FIBRE_CUT":
        return {
        "latency": random.randint(300, 1000),
        "packet_loss": 100,
        "cpu_usage": random.randint(10, 40),
        "memory_usage": random.randint(20, 50),
        "link_status": 0,
        "traffic": random.randint(0, 5),
        "scenario": "FIBRE_CUT",

        "latitude": -22.5609,
        "longitude": 17.0658
    }

    elif scenario == "LINK_DOWN":
        return {
        "latency": random.randint(150, 400),
        "packet_loss": random.randint(70, 100),
        "cpu_usage": random.randint(20, 60),
        "memory_usage": random.randint(30, 70),

        # link unavailable
        "link_status": 0,

        # some unstable traffic may still exist
        "traffic": random.randint(10, 100),

        "scenario": "LINK_DOWN"
    }