# src/robot_controller.py
import time

# Import directly (will work when run from run_robot.py)
from sensor_manager import SensorManager
from firebase_manager import FirebaseManager
from config import SENSOR_CHECK_INTERVAL, FIREBASE_UPDATE_INTERVAL

class RobotController:
    def __init__(self):
        print("Initializing Robot Delivery System...")
        self.sensor_manager = SensorManager()
        self.firebase_manager = FirebaseManager()
        self.running = False
        self.last_firebase_update = 0
        
    def execute_command(self, command):
        if command == 'OPEN_ALL':
            self.sensor_manager.open_all_boxes()
        elif command == 'CLOSE_ALL':
            self.sensor_manager.close_all_boxes()
        elif command == 'STOP':
            print("EMERGENCY STOP executed")
        elif command == 'GO':
            print("GO command executed")
        else:
            print(f"Unknown command: {command}")
    
    def update_firebase(self):
        try:
            box_status = self.sensor_manager.get_status()
            
            compartments_data = {}
            for box_num, status in box_status.items():
                compartments_data[box_num] = {
                    'is_open': status['is_open'],
                    'is_occupied': status['is_occupied'],
                    'distance_cm': status['distance'],
                    'ultrasonic_status': True,
                    'last_checked': time.time()
                }
            
            success = self.firebase_manager.update_robot_status(compartments_data)
            
            if success:
                print("Firebase updated successfully")
            else:
                print("Failed to update Firebase")
                
        except Exception as e:
            print(f"Error updating Firebase: {e}")
    
    def start(self):
        print("=" * 50)
        print("ROBOT DELIVERY SYSTEM - STARTING")
        print("=" * 50)
        self.running = True
        
        try:
            # Initial update
            self.sensor_manager.check_all_sensors()
            self.update_firebase()
            
            # Main loop
            while self.running:
                # Check sensors
                self.sensor_manager.check_all_sensors()
                
                # Update Firebase periodically
                current_time = time.time()
                if current_time - self.last_firebase_update >= FIREBASE_UPDATE_INTERVAL:
                    self.update_firebase()
                    self.last_firebase_update = current_time
                
                # Check for commands
                command = self.firebase_manager.check_commands()
                if command:
                    self.execute_command(command)
                
                time.sleep(SENSOR_CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"Fatal error: {e}")
            self.stop()
    
    def stop(self):
        print("Stopping robot controller...")
        self.running = False
        self.sensor_manager.close_all_boxes()
        self.sensor_manager.cleanup()
        print("Robot controller stopped safely")