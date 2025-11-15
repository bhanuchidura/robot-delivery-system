# run_real_simple.py - Simple version for Pi 5
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🤖 STARTING REAL HARDWARE MODE (Pi 5 SIMPLE)")

try:
    from real_sensor_manager_simple import RealSensorManager as SensorManager
    from firebase_manager import FirebaseManager
    from config import ROBOT_ID, SENSOR_CHECK_INTERVAL, FIREBASE_UPDATE_INTERVAL

    class RobotController:
        def __init__(self):
            print(f"🔧 Initializing REAL HARDWARE for {ROBOT_ID}...")
            self.sensor_manager = SensorManager()
            self.firebase_manager = FirebaseManager()
            self.running = False
            self.last_firebase_update = 0
            
        def execute_command(self, command):
            print(f"🎯 Executing: {command}")
            
            if command == 'OPEN_ALL':
                self.sensor_manager.open_all_boxes()
            elif command == 'CLOSE_ALL':
                self.sensor_manager.close_all_boxes()
            elif command == 'STOP':
                print("🛑 EMERGENCY STOP")
            elif command == 'GO':
                print("🟢 GO")
            else:
                print(f"❓ Unknown: {command}")
        
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
                    print("📡 Firebase updated")
                else:
                    print("❌ Firebase update failed")
                    
            except Exception as e:
                print(f"❌ Firebase error: {e}")
        
        def start(self):
            print("=" * 50)
            print(f"🤖 REAL HARDWARE - {ROBOT_ID} (Pi 5)")
            print("=" * 50)
            self.running = True
            
            try:
                # Initial setup
                self.sensor_manager.check_all_sensors()
                self.update_firebase()
                
                # Main loop
                while self.running:
                    # Check sensors
                    self.sensor_manager.check_all_sensors()
                    
                    # Update Firebase
                    current_time = time.time()
                    if current_time - self.last_firebase_update >= FIREBASE_UPDATE_INTERVAL:
                        self.update_firebase()
                        self.last_firebase_update = current_time
                    
                    # Check commands
                    command = self.firebase_manager.check_commands()
                    if command:
                        self.execute_command(command)
                    
                    time.sleep(SENSOR_CHECK_INTERVAL)
                    
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                print(f"💥 Hardware error: {e}")
                self.stop()
        
        def stop(self):
            print("🛑 Stopping hardware...")
            self.running = False
            self.sensor_manager.cleanup()
            print("✅ Hardware stopped")

    # Start real hardware
    robot = RobotController()
    robot.start()
    
except KeyboardInterrupt:
    print("👋 Hardware stopped by user")
except Exception as e:
    print(f"💥 Hardware error: {e}")
