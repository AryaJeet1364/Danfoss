# 🏭 Smart Multi-Zone HVAC Control System

## 📌 Overview
This project implements a smart, energy-aware HVAC control system for a multi-zone cold-storage facility. It demonstrates how zone-level control logic, supervisory airflow coordination, and real-time monitoring can be combined to maintain strict temperature setpoints while minimizing fan energy consumption.

**Status:** The system is currently in the development phase. It is fully simulated—running entirely on Python with a live HTML dashboard—providing a proof-of-concept for the control logic before hardware integration.

---

## 🎯 Objectives
* **Precision Control:** Maintain temperature setpoints in three independent zones.
* **Intelligence:** Allocate cooling capacity dynamically based on zone priority.
* **Efficiency:** Reduce fan energy consumption using nonlinear affinity law logic.
* **Visibility:** Visualize system behavior live through a simulated BMS interface.

---

## 🧊 Controlled Zones

| Zone | Target Setpoint | Cooling Type |

|------|-----------------|--------------|

| **Freezer** | -18 °C  | Constant Low-Temperature |

| **Cooler** | 2–4 °C | High-Turnover |

| **Packing Area** | 15–18 °C | Comfort / Process |



---

## 🧠 System Architecture



The system follows a modular data pipeline:
1. **`sensor_simulator.py`**: Generates noisy, realistic thermal data.
2. **`hvac_control_core.py`**: Processes logic and calculates actuator states.
3. **`live_data.json`**: Acts as a real-time data bridge (Middleware).
4. **`dashboard_demo.html`**: Provides the Human-Machine Interface (HMI).

---

## 🔧 Components

### 1️⃣ Sensor Simulator (`sensor_simulator.py`)
Replaces physical sensors by modeling:
* **Thermal Inertia:** Temperatures don't jump; they drift based on physics.
* **Ambient Coupling:** Zones gain heat from the "outside" environment.
* **Random Noise:** Mimics real-world sensor fluctuations.

### 2️⃣ HVAC Control Core (`hvac_control_core.py`)
The "Brain" of the operation. It implements:
* **Proportional Logic:** Adjusts fan speed based on the gap between current temp and setpoint.
* **Supervisory Coordination:** Manages dampers to ensure the most critical zones (Freezer) get priority airflow.
* **Energy Modeling:** Calculates fan power using the **Fan Affinity Law**, where power scales with the cube of airflow (P ∝ airflow³).


### 3️⃣ Live Dashboard (`dashboard_demo.html`)
A mock Industrial Control Center showing:
* Real-time Temperature & Setpoint tracking.
* Visual Damper positions (Open/Closed).
* Live Fan Power % and System Health status.

---

## ▶️ How to Run the Demo

### 1. Start the Control Loop
Run the core logic script in your terminal:
```bash
python hvac_control_core.py
```

### 2. Start the Local Server
In a new terminal window, start a simple server to host the dashboard:
```bash
python -m http.server 8000
```

### 3. Open the Dashboard
Navigate to the following URL in your web browser:
```bash
http://localhost:8000/dashboard_demo.html
```

