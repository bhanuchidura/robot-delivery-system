# src/real_sensor_manager_simple.py - Simple version for Pi 5
import time
from gpiozero import OutputDevice
import RPi.GPIO as GPIO
from config import BOX_CONFIG, OCCUPIED_DISTANCE_CM

class RealSensorManager:
    def __init__(self):
        self.box_status = {}
        self.locks = {}
        self.setup_sensors()
        
    def setup_sensors(self):
        print("🔧 REAL HARDWARE (Pi 5): Setting up physical sensors...")
        
        # Setup GPIO for sensors (using RPi.GPIO just for reading)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        for box_num, config in BOX_CONFIG.items():
            # Setup lock control using gpiozero (reliable)
            self.locks[box_num] = OutputDevice(config['lock_pin'], active_high=False, initial_value=False)
            
            # Setup ultrasonic sensor pins using RPi.GPIO
            GPIO.setup(config['ultrasonic_trigger'], GPIO.OUT)
            GPIO.setup(config['ultrasonic_echo'], GPIO.IN)
            GPIO.output(config['ultrasonic_trigger'], False)
            
            self.box_status[box_num] = {
                'is_open': False,
                'is_occupied': False,
                'distance': 100.0
            }
            print(f"🔧 Box {box_num} - Lock:GPIO{config['lock_pin']}")
        
        print("✅ All REAL hardware initialized!")
    
    def measure_distance(self, box_num):
        """Measure distance using basic GPIO"""
        config = BOX_CONFIG[box_num]
        
        try:
            # Send trigger pulse
            GPIO.output(config['ultrasonic_trigger'], True)
            time.sleep(0.00001)
            GPIO.output(config['ultrasonic_trigger'], False)
            
            pulse_start = time.time()
            pulse_end = time.time()
            
            # Wait for echo to go HIGH
            timeout_start = time.time()
            while GPIO.input(config['ultrasonic_echo']) == 0:
                pulse_start = time.time()
                if time.time() - timeout_start > 0.1:
                    return 100.0
            
            # Wait for echo to go LOW
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
        if box_num in self.locks:
            self.locks[box_num].on()  # Turn on to unlock
            self.box_status[box_num]['is_open'] = True
            print(f"🔓 Box {box_num} PHYSICALLY OPENED")
            return True
        return False
    
    def close_box(self, box_num):
        """Physically close the box"""
        if box_num in self.locks:
            self.locks[box_num].off()  # Turn off to lock
            self.box_status[box_num]['is_open'] = False
            print(f"🔒 Box {box_num} PHYSICALLY CLOSED")
            return True
        return False
    
    def open_all_boxes(self):
        print("🚪 Opening ALL boxes physically...")
        for box_num in self.locks:
            self.open_box(box_num)
        print("✅ All boxes PHYSICALLY OPEN")
    
    def close_all_boxes(self):
        print("🔒 Closing ALL boxes physically...")
        for box_num in self.locks:
            self.close_box(box_num)
        print("✅ All boxes PHYSICALLY CLOSED")
    
    def get_status(self):
        return self.box_status
    
    def cleanup(self):
        """Cleanup hardware"""
        print("🧹 Cleaning up hardware...")
        self.close_all_boxes()
        
        # Close all gpiozero devices
        for lock in self.locks.values():
            lock.close()
            
        GPIO.cleanup()
        print("🧹 Hardware cleanup complete")
