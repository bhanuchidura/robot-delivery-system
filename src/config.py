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
        'ultrasonic_trigger': 22,
        'ultrasonic_echo': 10,
    },
    3: {
        'lock_pin': 9,
        'ultrasonic_trigger': 11,
        'ultrasonic_echo': 5,
    }
}

# OCCUPANCY: < 30cm = Package Present, > 30cm = Empty
OCCUPIED_DISTANCE_CM = 30.0
SENSOR_CHECK_INTERVAL = 2
FIREBASE_UPDATE_INTERVAL = 30

# SOLENOID LOCK SAFETY
LOCK_ACTIVE_HIGH = False   # False = GPIO.LOW unlocks, GPIO.HIGH locks
LOCK_INITIAL_STATE = False # Start with locks CLOSED