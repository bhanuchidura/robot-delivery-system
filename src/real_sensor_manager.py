# src/real_sensor_manager.py
import RPi.GPIO as GPIO
import time
from config import BOX_CONFIG, OCCUPIED_DISTANCE_CM

class RealSensorManager:
    def __init__(self):
        self.box_status = {}
        self.setup_sensors()
        
    def setup_sensors(self):
        print("🔧 REAL HARDWARE: Setting up physical sensors...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        for box_num, config in BOX_CONFIG.items():
            # Setup lock control
            GPIO.setup(config['lock_pin'], GPIO.OUT)
            GPIO.output(config['lock_pin'], GPIO.HIGH)  # Start locked
            
            # Setup ultrasonic sensor
            GPIO.setup(config['ultrasonic_trigger'], GPIO.OUT)
            GPIO.setup(config['ultrasonic_echo'], GPIO.IN)
            
            self.box_status[box_num] = {
                'is_open': False,
                'is_occupied': False,
                'distance': 100.0
            }
            print(f"🔧 Box {box_num} - Lock:GPIO{config['lock_pin']}, Sensor:GPIO{config['ultrasonic_trigger']}/{config['ultrasonic_echo']}")
        
        print("✅ All REAL hardware initialized!")
    
    def measure_distance(self, box_num):
        """Measure real distance using ultrasonic sensor"""
        config = BOX_CONFIG[box_num]
        
        try:
            # Send trigger pulse
            GPIO.output(config['ultrasonic_trigger'], GPIO.LOW)
            time.sleep(0.0001)
            
            GPIO.output(config['ultrasonic_trigger'], GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(config['ultrasonic_trigger'], GPIO.LOW)
            
            pulse_start = time.time()
            pulse_end = time.time()
            
            # Wait for echo
            timeout_start = time.time()
            while GPIO.input(config['ultrasonic_echo']) == 0:
                pulse_start = time.time()
                if time.time() - timeout_start > 0.1:
                    return 100.0
            
            timeout_start = time.time()
            while GPIO.input(config['ultrasonic_echo']) == 1:
                pulse_end = time.time()
                if time.time() - timeout_start > 0.1:
                    return 100.0
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = (pulse_duration * 34300) / 2
            
            if distance < 0.5 or distance > 400:
                return 100.0
                
            return distance
            
        except Exception as e:
            print(f"❌ Sensor error Box {box_num}: {e}")
            return 100.0
    
    def check_all_sensors(self):
        """Check all real sensors"""
        print("🔍 Checking REAL sensors...")
        
        for box_num in self.box_status:
            distance = self.measure_distance(box_num)
            is_occupied = distance < OCCUPIED_DISTANCE_CM
            
            self.box_status[box_num]['distance'] = distance
            self.box_status[box_num]['is_occupied'] = is_occupied
            
            status = "📦 PRESENT" if is_occupied else "🔄 EMPTY"
            print(f"Box {box_num}: {distance:.1f}cm → {status}")
        
        return self.box_status
    
    def open_box(self, box_num):
        """Physically open the box"""
        if box_num in self.box_status:
            GPIO.output(BOX_CONFIG[box_num]['lock_pin'], GPIO.LOW)  # Unlock
            self.box_status[box_num]['is_open'] = True
            print(f"🔓 Box {box_num} PHYSICALLY OPENED")
            return True
        return False
    
    def close_box(self, box_num):
        """Physically close the box"""
        if box_num in self.box_status:
            GPIO.output(BOX_CONFIG[box_num]['lock_pin'], GPIO.HIGH)  # Lock
            self.box_status[box_num]['is_open'] = False
            print(f"🔒 Box {box_num} PHYSICALLY CLOSED")
            return True
        return False
    
    def open_all_boxes(self):
        print("🚪 Opening ALL boxes physically...")
        for box_num in self.box_status:
            self.open_box(box_num)
        print("✅ All boxes PHYSICALLY OPEN")
    
    def close_all_boxes(self):
        print("🔒 Closing ALL boxes physically...")
        for box_num in self.box_status:
            self.close_box(box_num)
        print("✅ All boxes PHYSICALLY CLOSED")
    
    def get_status(self):
        return self.box_status
    
    def cleanup(self):
        """Cleanup hardware"""
        self.close_all_boxes()
        GPIO.cleanup()
        print("🧹 Hardware cleanup complete")