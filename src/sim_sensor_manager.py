# src/sim_sensor_manager.py
import time
import random
from config import BOX_CONFIG, OCCUPIED_DISTANCE_CM

class SimSensorManager:
    def __init__(self):
        self.box_status = {}
        self.setup_sensors()
        
    def setup_sensors(self):
        print("💻 SIMULATION MODE: Setting up virtual sensors...")
        
        for box_num in BOX_CONFIG:
            self.box_status[box_num] = {
                'is_open': False,
                'is_occupied': False,
                'distance': 5.0
            }
            print(f"📦 Virtual Box {box_num} initialized")
        
        print("✅ All virtual sensors ready!")
    
    def measure_distance(self, box_num):
        # Simulate distance based on package presence
        if self.box_status[box_num]['is_occupied']:
            return random.uniform(0.5, 1.9)  # Package present
        else:
            return random.uniform(3.0, 10.0) # No package
    
    def check_all_sensors(self):
        """Check all virtual sensors"""
        print("🔍 Checking virtual sensors...")
        
        for box_num in self.box_status:
            distance = self.measure_distance(box_num)
            is_occupied = distance < OCCUPIED_DISTANCE_CM
            
            self.box_status[box_num]['distance'] = distance
            self.box_status[box_num]['is_occupied'] = is_occupied
            
            status = "📦 PRESENT" if is_occupied else "🔄 EMPTY"
            print(f"Box {box_num}: {distance:.1f}cm → {status}")
        
        return self.box_status
    
    def open_box(self, box_num):
        if box_num in self.box_status:
            self.box_status[box_num]['is_open'] = True
            print(f"🔓 Virtual Box {box_num} OPENED")
            return True
        return False
    
    def close_box(self, box_num):
        if box_num in self.box_status:
            self.box_status[box_num]['is_open'] = False
            print(f"🔒 Virtual Box {box_num} CLOSED")
            return True
        return False
    
    def open_all_boxes(self):
        print("🚪 Opening ALL virtual boxes...")
        for box_num in self.box_status:
            self.open_box(box_num)
        print("✅ All virtual boxes OPEN")
    
    def close_all_boxes(self):
        print("🔒 Closing ALL virtual boxes...")
        for box_num in self.box_status:
            self.close_box(box_num)
        print("✅ All virtual boxes CLOSED")
    
    def get_status(self):
        return self.box_status
    
    def cleanup(self):
        print("🧹 Virtual system cleanup complete")