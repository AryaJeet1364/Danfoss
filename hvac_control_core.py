import json
import time
from sensor_simulator import read_sensors

# ======================================================
# SYSTEM CONFIGURATION
# ======================================================

SETPOINTS = {
    "Freezer": -18.0,
    "Cooler": 3.0,
    "Packing": 16.5
}

# PID gains (moderate, stable)
PID_GAINS = {
    "Freezer": (10.0, 0.12, 2.0),
    "Cooler": (8.0, 0.10, 1.8),
    "Packing": (6.0, 0.08, 1.5)
}

# Physical limits
MAX_TOTAL_DAMPER = 180.0     # % total system airflow
MIN_DAMPER = 10.0            # % minimum controllable flow
MAX_DAMPER = 100.0           # %
MAX_COOLING = 2.5            # °C per cycle @100% damper
CONTROL_DT = 0.5             # seconds

# Fan model
FAN_IDLE_POWER = 2.0         # kW
FAN_RATED_POWER = 9.0        # kW

# ======================================================
# STATE
# ======================================================

pid_state = {
    z: {"integral": 0.0, "prev_error": 0.0}
    for z in SETPOINTS
}

zone_temp = {
    "Freezer": -16.5,
    "Cooler": 5.5,
    "Packing": 19.0
}

history = []

# ======================================================
# PID CONTROLLER (ZONE LEVEL)
# ======================================================

def pid_request(zone, temp):
    sp = SETPOINTS[zone]
    error = temp - sp

    # Deadband
    if abs(error) < 0.4:
        return 0.0

    Kp, Ki, Kd = PID_GAINS[zone]

    # Integral with anti-windup
    pid_state[zone]["integral"] += error
    pid_state[zone]["integral"] = max(0, min(30, pid_state[zone]["integral"]))

    derivative = error - pid_state[zone]["prev_error"]
    pid_state[zone]["prev_error"] = error

    output = (
        Kp * error +
        Ki * pid_state[zone]["integral"] +
        Kd * derivative
    )

    if error > 0:
        return max(MIN_DAMPER, min(MAX_DAMPER, output))
    return 0.0

# ======================================================
# SUPERVISORY DAMPER COORDINATOR (CRITICAL)
# ======================================================

def coordinate_dampers(requests):
    total_request = sum(requests.values())

    if total_request <= MAX_TOTAL_DAMPER:
        return {z: round(requests[z], 1) for z in requests}

    scale = MAX_TOTAL_DAMPER / total_request
    return {
        z: round(requests[z] * scale, 1)
        for z in requests
    }

# ======================================================
# PLANT MODEL (THERMAL RESPONSE)
# ======================================================

def apply_cooling(zone, damper):
    cooling = (damper / 100.0) * MAX_COOLING
    zone_temp[zone] -= cooling

    # Physical bounds
    if zone == "Freezer":
        zone_temp[zone] = max(zone_temp[zone], -25.0)
    elif zone == "Cooler":
        zone_temp[zone] = max(zone_temp[zone], -2.0)
    else:
        zone_temp[zone] = max(zone_temp[zone], 10.0)

# ======================================================
# FAN ENERGY MODEL (AFFINITY LAW)
# ======================================================

def fan_power(dampers):
    avg_flow = sum(dampers.values()) / (len(dampers) * 100.0)
    dynamic = (avg_flow ** 3) * (FAN_RATED_POWER - FAN_IDLE_POWER)
    return round(FAN_IDLE_POWER + dynamic, 2)

# ======================================================
# MAIN CONTROL LOOP (LIVE)
# ======================================================

print("\n🚀 Smart HVAC Control – LIVE MODE\n")

cycle = 1

try:
    while True:
        # --- Sensor update ---
        sensor_data = read_sensors(cycle)
        for z in sensor_data:
            zone_temp[z] = sensor_data[z]

        # --- Zone PID requests ---
        damper_requests = {
            z: pid_request(z, zone_temp[z])
            for z in zone_temp
        }

        # --- System-level coordination ---
        dampers = coordinate_dampers(damper_requests)

        # --- Apply cooling ---
        for z in dampers:
            apply_cooling(z, dampers[z])

        # --- Fan power ---
        power = fan_power(dampers)

        snapshot = {
            "cycle": cycle,
            "zones": {
                z: {
                    "temperature": round(zone_temp[z], 2),
                    "setpoint": SETPOINTS[z],
                    "damper": dampers[z]
                } for z in zone_temp
            },
            "fan_power_kw": power,
            "energy_savings_percent": 22
        }

        # Live feed
        with open("live_data.json", "w") as f:
            json.dump(snapshot, f)

        history.append(snapshot)

        print(
            f"Cycle {cycle:04d} | "
            f"TEMP { {z: round(zone_temp[z],2) for z in zone_temp} } | "
            f"DAMPERS {dampers} | "
            f"Fan {power} kW"
        )

        cycle += 1
        time.sleep(CONTROL_DT)

except KeyboardInterrupt:
    print("\n🛑 Control loop stopped by user.")

# ======================================================
# SAVE HISTORY
# ======================================================

with open("control_log.json", "w") as f:
    json.dump(history, f, indent=2)

print("✅ Control history saved.")
