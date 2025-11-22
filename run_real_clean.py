# run_real_clean.py - Updated for new sensor manager
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🤖 STARTING REAL HARDWARE MODE (Pure gpiozero Version)")

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
                self.update_firebase(force=True, reason="open_all_command")
            elif command == 'CLOSE_ALL':
                self.sensor_manager.close_all_boxes()
                self.update_firebase(force=True, reason="close_all_command")
            elif command == 'STOP':
                print("🛑 EMERGENCY STOP")
                self.stop()
            elif command == 'GO':
                print("🟢 GO - Continuing operation")
            else:
                print(f"❓ Unknown command: {command}")
        
        def update_firebase(self, force=False, reason="auto"):
            """Update Firebase only when needed"""
            try:
                current_time = time.time()
                
                # Get current status
                box_status = self.sensor_manager.get_status()
                
                # Prepare compartment data for Firebase
                compartments_data = {}
                for box_num, status in box_status.items():
                    compartments_data[box_num] = {
                        'is_open': status['is_open'],  # Lock state
                        'is_occupied': status['is_occupied'],  # Package presence
                        'distance_cm': status['distance'],
                        'ultrasonic_status': True,
                        'last_checked': status['last_checked']
                    }
                
                # Update Firebase if forced OR interval passed
                if force or (current_time - self.last_firebase_update >= FIREBASE_UPDATE_INTERVAL):
                    success = self.firebase_manager.update_robot_status(compartments_data)
                    
                    if success:
                        self.last_firebase_update = current_time
                        print(f"📡 Firebase updated ({reason})")
                    else:
                        print(f"❌ Firebase update failed ({reason})")
                    
                    return success
                else:
                    print(f"⏳ Skipping Firebase update - {int(FIREBASE_UPDATE_INTERVAL - (current_time - self.last_firebase_update))}s remaining")
                    return True
                    
            except Exception as e:
                print(f"❌ Firebase error: {e}")
                return False
        
        def start(self):
            print("=" * 50)
            print(f"🤖 REAL HARDWARE - {ROBOT_ID}")
            print("=" * 50)
            self.running = True
            
            try:
                # Initial setup
                print("🔄 Initial sensor check...")
                box_status, status_changed = self.sensor_manager.check_all_sensors()
                
                # Force initial Firebase update
                self.update_firebase(force=True, reason="initial_setup")
                
                # Main loop
                while self.running:
                    # Check sensors
                    box_status, status_changed = self.sensor_manager.check_all_sensors()
                    
                    # Update Firebase if occupancy changed
                    if status_changed:
                        self.update_firebase(force=True, reason="occupancy_changed")
                    else:
                        # Periodic update (respects interval)
                        self.update_firebase(force=False, reason="periodic_check")
                    
                    # Check for frontend commands
                    command = self.firebase_manager.check_commands()
                    if command:
                        self.execute_command(command)
                    
                    time.sleep(SENSOR_CHECK_INTERVAL)
                    
            except KeyboardInterrupt:
                print("\n🛑 Received interrupt signal...")
                self.stop()
            except Exception as e:
                print(f"💥 Hardware error: {e}")
                self.stop()
        
        def stop(self):
            print("🛑 Stopping hardware...")
            self.running = False
            # Final update and cleanup
            self.update_firebase(force=True, reason="shutdown")
            self.sensor_manager.cleanup()
            print("✅ Hardware stopped cleanly")

    # Start the robot
    robot = RobotController()
    robot.start()
    
except KeyboardInterrupt:
    print("👋 Hardware stopped by user")
except Exception as e:
    print(f"💥 Hardware initialization error: {e}")
