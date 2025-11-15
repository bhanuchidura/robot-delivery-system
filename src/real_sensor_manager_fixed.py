# src/real_sensor_manager_fixed.py - Fixed for Raspberry Pi 5
import time
from gpiozero import OutputDevice, DistanceSensor
from signal import pause
from config import BOX_CONFIG, OCCUPIED_DISTANCE_CM

class RealSensorManager:
    def __init__(self):
        self.box_status = {}
        self.locks = {}
        self.sensors = {}
        self.setup_sensors()
        
    def setup_sensors(self):
        print("🔧 REAL HARDWARE (Pi 5): Setting up physical sensors...")
        
        try:
            for box_num, config in BOX_CONFIG.items():
                # Setup lock control using gpiozero
                self.locks[box_num] = OutputDevice(config['lock_pin'], active_high=False, initial_value=False)
                
                # Setup ultrasonic sensor using gpiozero DistanceSensor
                # gpiozero uses (echo, trigger) order instead of (trigger, echo)
                self.sensors[box_num] = DistanceSensor(
                    echo=config['ultrasonic_echo'],
                    trigger=config['ultrasonic_trigger'],
                    threshold_distance=OCCUPIED_DISTANCE_CM/100  # Convert to meters
                )
                
                self.box_status[box_num] = {
                    'is_open': False,
                    'is_occupied': False,
                    'distance': 100.0
                }
                print(f"🔧 Box {box_num} - Lock:GPIO{config['lock_pin']}, Sensor:GPIO{config['ultrasonic_echo']}/{config['ultrasonic_trigger']}")
            
            print("✅ All REAL hardware initialized for Pi 5!")
            
        except Exception as e:
            print(f"❌ Hardware setup error: {e}")
            raise
    
    def measure_distance(self, box_num):
        """Measure distance using gpiozero DistanceSensor"""
        try:
            # gpiozero returns distance in meters, convert to cm
            distance_cm = self.sensors[box_num].distance * 100
            return distance_cm
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
        for sensor in self.sensors.values():
            sensor.close()
            
        print("🧹 Hardware cleanup complete")
