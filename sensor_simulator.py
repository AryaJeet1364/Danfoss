import random

# Ambient temperatures for zones
AMBIENT = {
    "Freezer": -10.0,
    "Cooler": 10.0,
    "Packing": 25.0
}

# Initial zone temperatures
ZONE_STATE = {
    "Freezer": -16.5,
    "Cooler": 5.5,
    "Packing": 19.0
}

# Thermal inertia (bigger = slower change)
THERMAL_MASS = {
    "Freezer": 0.98,
    "Cooler": 0.96,
    "Packing": 0.94
}

def load_profile(cycle):
    if 20 <= cycle <= 40:
        return 1.2   # morning activity
    elif 60 <= cycle <= 80:
        return 1.5   # afternoon peak
    else:
        return 0.9   # steady operation

def read_sensors(cycle):
    data = {}
    load = load_profile(cycle)

    for zone in ZONE_STATE:
        noise = random.uniform(-0.3, 0.3)

        # Drift toward ambient (thermal equilibrium)
        ambient_pull = (AMBIENT[zone] - ZONE_STATE[zone]) * (1 - THERMAL_MASS[zone])

        # Load disturbance (doors, people, goods)
        load_gain = random.uniform(0.3, 0.8) * load

        ZONE_STATE[zone] += ambient_pull + load_gain + noise

        # Hard physical limits (safety)
        if zone == "Freezer":
            ZONE_STATE[zone] = min(max(ZONE_STATE[zone], -30), 0)
        elif zone == "Cooler":
            ZONE_STATE[zone] = min(max(ZONE_STATE[zone], -2), 15)
        else:
            ZONE_STATE[zone] = min(max(ZONE_STATE[zone], 10), 35)

        data[zone] = round(ZONE_STATE[zone], 2)

    return data
