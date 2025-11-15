import time
from gpiozero import OutputDevice
import RPi.GPIO as GPIO
from config import BOX_CONFIG, OCCUPIED_DISTANCE_CM, LOCK_ACTIVE_HIGH, LOCK_INITIAL_STATE

class RealSensorManager:
    def __init__(self):
        self.box_status = {}
        self.locks = {}
        self.last_occupancy_status = {}
        self.setup_sensors()
        
    def setup_sensors(self):
        print("🔧 REAL HARDWARE: Setting up sensors...")
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        for box_num, config in BOX_CONFIG.items():
            self.locks[box_num] = OutputDevice(
                config['lock_pin'], 
                active_high=LOCK_ACTIVE_HIGH, 
                initial_value=LOCK_INITIAL_STATE
            )
            
            GPIO.setup(config['ultrasonic_trigger'], GPIO.OUT)
            GPIO.setup(config['ultrasonic_echo'], GPIO.IN)
            GPIO.output(config['ultrasonic_trigger'], False)
            
            self.box_status[box_num] = {
                'is_open': False,
                'is_occupied': False,
                'distance': 100.0,
                'last_checked': time.time()
            }
            
            self.last_occupancy_status[box_num] = False
            print(f"🔧 Box {box_num} - Lock:GPIO{config['lock_pin']}")
        
        print("✅ Hardware initialized!")
    
    def measure_distance(self, box_num):
        config = BOX_CONFIG[box_num]
        
        try:
            GPIO.output(config['ultrasonic_trigger'], False)
            time.sleep(0.0005)
            
            GPIO.output(config['ultrasonic_trigger'], True)
            time.sleep(0.00001)
            GPIO.output(config['ultrasonic_trigger'], False)
            
            pulse_start = time.time()
            pulse_end = time.time()
            
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
            
            pulse_duration = pulse_end - pulse_start
            distance = (pulse_duration * 34300) / 2
            
            if distance < 2.0 or distance > 400.0:
                return 100.0
                
            return distance
            
        except Exception as e:
            print(f"❌ Sensor error Box {box_num}: {e}")
            return 100.0
    
    def check_all_sensors(self):
        print("🔍 Checking sensors...")
        
        status_changed = False
        current_time = time.time()
        
        for box_num in self.box_status:
            distance = self.measure_distance(box_num)
            is_occupied = distance < OCCUPIED_DISTANCE_CM
            
            old_occupied = self.last_occupancy_status[box_num]
            occupancy_changed = (is_occupied != old_occupied)
            
            if occupancy_changed:
                status_changed = True
                self.last_occupancy_status[box_num] = is_occupied
                print(f"🔄 Box {box_num} occupancy CHANGED: {old_occupied} → {is_occupied}")
            
            self.box_status[box_num]['distance'] = distance
            self.box_status[box_num]['is_occupied'] = is_occupied
            self.box_status[box_num]['last_checked'] = current_time
            
            status = "📦 PRESENT" if is_occupied else "🔄 EMPTY"
            change_indicator = " (CHANGED)" if occupancy_changed else ""
            print(f"Box {box_num}: {distance:.1f}cm → {status}{change_indicator}")
        
        return self.box_status, status_changed
    
    def open_box(self, box_num):
        if box_num in self.locks:
            self.locks[box_num].on()
            self.box_status[box_num]['is_open'] = True
            print(f"🔓 Box {box_num} OPENED")
            return True
        return False
    
    def close_box(self, box_num):
        if box_num in self.locks:
            self.locks[box_num].off()
            self.box_status[box_num]['is_open'] = False
            print(f"🔒 Box {box_num} CLOSED")
            return True
        return False
    
    def open_all_boxes(self):
        print("🚪 Opening ALL boxes...")
        for box_num in self.locks:
            self.open_box(box_num)
        print("✅ All boxes OPEN")
    
    def close_all_boxes(self):
        print("🔒 Closing ALL boxes...")
        for box_num in self.locks:
            self.close_box(box_num)
        print("✅ All boxes CLOSED")
    
    def get_status(self):
        return self.box_status
    
    def cleanup(self):
        print("🧹 Cleaning up hardware...")
        self.close_all_boxes()
        for lock in self.locks.values():
            lock.close()
        GPIO.cleanup()
        print("✅ Hardware cleanup complete")