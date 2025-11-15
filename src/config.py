ROBOT_ID = "Robot_001"
FIREBASE_URL = "https://delivery-robot-p1nl-default-rtdb.europe-west1.firebasedatabase.app"

BOX_CONFIG = {
    1: {
        'lock_pin': 17,           # GPIO17 - Safe
        'ultrasonic_trigger': 23, # GPIO23 - Safe  
        'ultrasonic_echo': 24,    # GPIO24 - Safe
    },
    2: {
        'lock_pin': 27,           # GPIO27 - Safe
        'ultrasonic_trigger': 22, # GPIO22 - Safe (changed from 25)
        'ultrasonic_echo': 10,    # GPIO10 - Safe (changed from 8)
    },
    3: {
        'lock_pin': 9,            # GPIO9 - Safe (changed from 22)
        'ultrasonic_trigger': 11, # GPIO11 - Safe (changed from 7)
        'ultrasonic_echo': 5,     # GPIO5 - Safe (changed from 1)
    }
}

OCCUPIED_DISTANCE_CM = 50.0
SENSOR_CHECK_INTERVAL = 2
FIREBASE_UPDATE_INTERVAL = 30
