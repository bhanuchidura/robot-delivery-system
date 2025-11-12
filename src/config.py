# src/config.py
ROBOT_ID = "Robot_001"
FIREBASE_URL = "https://delivery-robot-p1nl-default-rtdb.europe-west1.firebasedatabase.app"

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

OCCUPIED_DISTANCE_CM = 2.0
SENSOR_CHECK_INTERVAL = 1
FIREBASE_UPDATE_INTERVAL = 2