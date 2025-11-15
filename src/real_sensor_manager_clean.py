# src/real_sensor_manager_clean.py
import time
import RPi.GPIO as GPIO
from config import BOX_CONFIG, OCCUPANCY_DISTANCE_CM

class RealSensorManager:
    def __init__(self):
        print("🔧 Initializing Real Sensor Manager...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self.box_status = {}
        self.setup_pins()
    
    def setup_pins(self):
        """Setup GPIO pins for all boxes"""
        for box_num, pins in BOX_CONFIG.items():
            # Setup lock pin as OUTPUT
            GPIO.setup(pins['lock_pin'], GPIO.OUT)
            GPIO.output(pins['lock_pin'], GPIO.LOW)  # Start with lock closed
            
            # Setup ultrasonic pins
            GPIO.setup(pins['ultrasonic_trigger'], GPIO.OUT)
            GPIO.setup(pins['ultrasonic_echo'], GPIO.IN)
            
            # Initialize box status
            self.box_status[box_num] = {
                'is_open': False,
                'is_occupied': False,
                'distance': 100.0  # Start with empty (100cm)
            }
        
        print("✅ GPIO pins setup complete")
    
    def measure_distance(self, box_num):
        """Get distance from ultrasonic sensor in cm for specific box"""
        try:
            pins = BOX_CONFIG[box_num]
            trigger_pin = pins['ultrasonic_trigger']
            echo_pin = pins['ultrasonic_echo']
            
            # Send trigger pulse
            GPIO.output(trigger_pin, True)
            time.sleep(0.00001)  # 10 microseconds
            GPIO.output(trigger_pin, False)
            
            start_time = time.time()
            stop_time = time.time()
            
            # Wait for echo to go high
            timeout = time.time() + 0.1  # 100ms timeout
            while GPIO.input(echo_pin) == 0 and time.time() < timeout:
                start_time = time.time()
            
            # Wait for echo to go low
            timeout = time.time() + 0.1  # 100ms timeout
            while GPIO.input(echo_pin) == 1 and time.time() < timeout:
                stop_time = time.time()
            
            # Calculate distance
            time_elapsed = stop_time - start_time
            distance = (time_elapsed * 34300) / 2  # Speed of sound in cm/s
            
            return max(2.0, min(300.0, distance))  # Limit between 2-300cm
        
        except Exception as e:
            print(f"❌ Box {box_num} distance measurement error: {e}")
            return 100.0  # Return safe default
    
    def check_all_sensors(self):
        """Check distance for all boxes"""
        for box_num in self.box_status:
            distance = self.measure_distance(box_num)
            is_occupied = distance < OCCUPANCY_DISTANCE_CM

            self.box_status[box_num]['distance'] = distance
            self.box_status[box_num]['is_occupied'] = is_occupied

            status = "📦 PRESENT" if is_occupied else "🔄 EMPTY"
            print(f"Box {box_num}: {distance:.1f}cm → {status}")

        return self.box_status

    def open_box(self, box_num):
        """Physically open the box"""
        if box_num in BOX_CONFIG:
            GPIO.output(BOX_CONFIG[box_num]['lock_pin'], GPIO.HIGH)
            self.box_status[box_num]['is_open'] = True
            print(f"🔓 Box {box_num} OPENED")
            return True
        return False

    def close_box(self, box_num):
        """Physically close the box"""
        if box_num in BOX_CONFIG:
            GPIO.output(BOX_CONFIG[box_num]['lock_pin'], GPIO.LOW)
            self.box_status[box_num]['is_open'] = False
            print(f"🔒 Box {box_num} CLOSED")
            return True
        return False

    def open_all_boxes(self):
        print("🚪 Opening ALL boxes...")
        for box_num in BOX_CONFIG:
            self.open_box(box_num)
        print("✅ All boxes OPEN")

    def close_all_boxes(self):
        print("🔒 Closing ALL boxes...")
        for box_num in BOX_CONFIG:
            self.close_box(box_num)
        print("✅ All boxes CLOSED")

    def get_status(self):
        return self.box_status

    def cleanup(self):
        """Cleanup GPIO"""
        GPIO.cleanup()
        print("🧹 GPIO cleanup complete")
