# Robot Delivery System

A Raspberry Pi-based delivery robot system with 3 compartments.

## Quick Start
```bash
# On Raspberry Pi
git clone <your-repo-url>
cd robot-delivery-system
python3 src/robot_controller.py


### 4. `src/config.py`
```python
# Robot Identification
ROBOT_ID = "Robot_001"

# Firebase Configuration
FIREBASE_URL = "https://delivery-robot-p1nl-default-rtdb.europe-west1.firebasedatabase.app"

# GPIO Pin Configuration
BOX_CONFIG = {
    1: {
        'lock_pin': 17,
        'ultrasonic_trigger': 23,
        'ultrasonic_echo': 24,
    },
    2: {
        'lock_pin': 27,
        'ultrasonic_trigger': 25, 
        'ultrasonic_echo': 8,
    },
    3: {
        'lock_pin': 22,
        'ultrasonic_trigger': 7,
        'ultrasonic_echo': 1,
    }
}

# Sensor Settings
OCCUPIED_DISTANCE_CM = 2.0
SENSOR_CHECK_INTERVAL = 1
FIREBASE_UPDATE_INTERVAL = 2