import random


# ---------------------------------------------------------
# Simulated Network Devices
# ---------------------------------------------------------

NETWORK_DEVICES = [
    {
        "device_name": "WHK-CORE-R1",
        "device_type": "Router",
        "ip_address": "10.0.0.1",
        "location_name": "Windhoek Core",
        "latitude": -22.5609,
        "longitude": 17.0658
    },
    {
        "device_name": "WHK-CORE-R2",
        "device_type": "Router",
        "ip_address": "10.0.0.2",
        "location_name": "Windhoek Core",
        "latitude": -22.5609,
        "longitude": 17.0658
    },
    {
        "device_name": "OSH-EDGE-R1",
        "device_type": "Router",
        "ip_address": "10.0.10.1",
        "location_name": "Oshakati",
        "latitude": -17.7883,
        "longitude": 15.7044
    },
    {
        "device_name": "SWK-EDGE-R1",
        "device_type": "Router",
        "ip_address": "10.0.20.1",
        "location_name": "Swakopmund",
        "latitude": -22.6792,
        "longitude": 14.5253
    }
]


# ---------------------------------------------------------
# Simulated Network Links
# ---------------------------------------------------------

NETWORK_LINKS = [
    {
        "link_name": "WHK-R1-R2",
        "source_device": "WHK-CORE-R1",
        "source_interface": "Gi0/1",
        "destination_device": "WHK-CORE-R2",
        "destination_interface": "Gi0/1",
        "bandwidth_capacity": 1000
    },
    {
        "link_name": "WHK-R2-OSH-R1",
        "source_device": "WHK-CORE-R2",
        "source_interface": "Gi0/2",
        "destination_device": "OSH-EDGE-R1",
        "destination_interface": "Gi0/1",
        "bandwidth_capacity": 1000
    },
    {
        "link_name": "WHK-R1-SWK-R1",
        "source_device": "WHK-CORE-R1",
        "source_interface": "Gi0/2",
        "destination_device": "SWK-EDGE-R1",
        "destination_interface": "Gi0/1",
        "bandwidth_capacity": 1000
    }
]


# ---------------------------------------------------------
# Get Random Device
# ---------------------------------------------------------

def get_random_device():

    return random.choice(NETWORK_DEVICES)


# ---------------------------------------------------------
# Get Random Link
# ---------------------------------------------------------

def get_random_link():

    return random.choice(NETWORK_LINKS)


# ---------------------------------------------------------
# Generate Simulated SNMP Metrics
# ---------------------------------------------------------

def get_snmp_metrics():

    scenario = random.choices(
        [
            "NORMAL",
            "CONGESTION",
            "HARDWARE_FAILURE",
            "FIBRE_CUT",
            "LINK_DOWN"
        ],
        weights=[
            0.50,
            0.20,
            0.10,
            0.10,
            0.10
        ],
        k=1
    )[0]


    # -----------------------------------------------------
    # NORMAL
    # -----------------------------------------------------

    if scenario == "NORMAL":

        device = get_random_device()
        link = get_random_link()

        latency = random.randint(20, 60)

        jitter = round(
            random.uniform(1, 8),
            2
        )

        packet_loss = round(
            random.uniform(0, 1),
            2
        )

        bandwidth = random.randint(
            100,
            600
        )

        cpu_usage = random.randint(
            30,
            60
        )

        memory_usage = random.randint(
            40,
            70
        )

        link_status = 1

        traffic = random.randint(
            100,
            700
        )


    # -----------------------------------------------------
    # CONGESTION
    # -----------------------------------------------------

    elif scenario == "CONGESTION":

        device = get_random_device()
        link = get_random_link()

        latency = random.randint(
            80,
            180
        )

        jitter = round(
            random.uniform(20, 60),
            2
        )

        packet_loss = round(
            random.uniform(2, 8),
            2
        )

        bandwidth = random.randint(
            800,
            980
        )

        cpu_usage = random.randint(
            70,
            95
        )

        memory_usage = random.randint(
            70,
            95
        )

        link_status = 1

        traffic = random.randint(
            800,
            1000
        )


    # -----------------------------------------------------
    # HARDWARE FAILURE
    # -----------------------------------------------------

    elif scenario == "HARDWARE_FAILURE":

        device = get_random_device()
        link = random.choice(NETWORK_LINKS)

        latency = random.randint(
            100,
            250
        )

        jitter = round(
            random.uniform(30, 100),
            2
        )

        packet_loss = round(
            random.uniform(5, 20),
            2
        )

        bandwidth = random.randint(
            50,
            400
        )

        cpu_usage = random.randint(
            90,
            100
        )

        memory_usage = random.randint(
            90,
            100
        )

        link_status = 1

        traffic = random.randint(
            50,
            400
        )


    # -----------------------------------------------------
    # FIBRE CUT
    # -----------------------------------------------------

    elif scenario == "FIBRE_CUT":

        link = get_random_link()

        # The affected device is the source device
        device = next(
            d for d in NETWORK_DEVICES
            if d["device_name"] == link["source_device"]
        )

        latency = random.randint(
            300,
            1000
        )

        jitter = random.randint(
            100,
            300
        )

        packet_loss = 100

        bandwidth = 0

        cpu_usage = random.randint(
            10,
            40
        )

        memory_usage = random.randint(
            20,
            50
        )

        link_status = 0

        traffic = random.randint(
            0,
            5
        )


    # -----------------------------------------------------
    # LINK DOWN
    # -----------------------------------------------------

    elif scenario == "LINK_DOWN":

        link = get_random_link()

        device = next(
            d for d in NETWORK_DEVICES
            if d["device_name"] == link["source_device"]
        )

        latency = random.randint(
            200,
            500
        )

        jitter = random.randint(
            50,
            150
        )

        packet_loss = 100

        bandwidth = 0

        cpu_usage = random.randint(
            30,
            70
        )

        memory_usage = random.randint(
            40,
            80
        )

        link_status = 0

        # Keep some traffic so the simulator
        # can distinguish LINK_DOWN from FIBRE_CUT
        traffic = random.randint(
            10,
            50
        )


    # -----------------------------------------------------
    # Return Complete Network Event
    # -----------------------------------------------------

    return {

        # Network performance
        "latency": latency,
        "jitter": jitter,
        "packet_loss": packet_loss,
        "bandwidth": bandwidth,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "link_status": link_status,
        "traffic": traffic,

        # Fault scenario
        "scenario": scenario,

        # Device information
        "device_name": device["device_name"],
        "device_type": device["device_type"],
        "ip_address": device["ip_address"],

        # Interface
        "interface_name": link["source_interface"],

        # Link
        "link_name": link["link_name"],

        # Location
        "location_name": device["location_name"],
        "latitude": device["latitude"],
        "longitude": device["longitude"]
    }