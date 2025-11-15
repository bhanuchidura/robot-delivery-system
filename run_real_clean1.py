# run_real_clean.py - SIMPLE FIXED VERSION
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🤖 STARTING REAL HARDWARE - SIMPLE VERSION")

try:
    from real_sensor_manager_clean import RealSensorManager as SensorManager
    from firebase_manager import FirebaseManager
    from config import ROBOT_ID, SENSOR_CHECK_INTERVAL, FIREBASE_UPDATE_INTERVAL

    class RobotController:
        def __init__(self):
            print(f"🔧 Starting robot: {ROBOT_ID}")
            self.sensor_manager = SensorManager()
            self.firebase_manager = FirebaseManager()
            self.running = False
            
            # Track previous sensor states
            self.last_occupied_state = {
                1: False,
                2: False, 
                3: False
            }
            
            # Track when we last updated Firebase
            self.last_update_time = 0
        
        def check_occupancy(self, distance_cm):
            """Check if compartment is occupied based on distance"""
            # If distance is under 50cm, compartment is OCCUPIED (True)
            # If distance is over 50cm, compartment is EMPTY (False)
            if distance_cm < 50:
                return True  # Occupied
            else:
                return False  # Empty
        
        def update_firebase(self):
            """Update Firebase only if occupancy state changed"""
            try:
                print("📡 Checking sensors...")
                box_status = self.sensor_manager.get_status()
                
                has_changes = False
                compartments_data = {}
                
                for box_num, status in box_status.items():
                    # Get current distance from sensor
                    current_distance = status['distance']
                    
                    # Check if occupied based on distance
                    is_occupied_now = self.check_occupancy(current_distance)
                    
                    # Get previous state
                    was_occupied_before = self.last_occupied_state.get(box_num, False)
                    
                    print(f"📦 Box {box_num}: Distance={current_distance}cm, Occupied={is_occupied_now} (was {was_occupied_before})")
                    
                    # Only update if state changed OR it's been more than 30 seconds
                    current_time = time.time()
                    state_changed = (is_occupied_now != was_occupied_before)
                    time_to_update = (current_time - self.last_update_time) > 30
                    
                    if state_changed or time_to_update:
                        has_changes = True
                        self.last_occupied_state[box_num] = is_occupied_now
                        
                        # Prepare data for Firebase
                        compartments_data[box_num] = {
                            'is_occupied': is_occupied_now,
                            'is_open': False,  # You can change this if you have door sensors
                            'distance_cm': current_distance,
                            'ultrasonic_status': True,
                            'last_checked': time.time()
                        }
                        
                        if state_changed:
                            print(f"🔄 Box {box_num} state CHANGED: {was_occupied_before} -> {is_occupied_now}")
                    
                    else:
                        # No change, use previous state
                        compartments_data[box_num] = {
                            'is_occupied': was_occupied_before,
                            'is_open': False,
                            'distance_cm': current_distance,
                            'ultrasonic_status': True,
                            'last_checked': time.time()
                        }
                
                # Update Firebase if we have changes or it's time
                if has_changes or time_to_update:
                    print("🔄 Updating Firebase with changes...")
                    success = self.firebase_manager.update_robot_status(compartments_data)
                    
                    if success:
                        print("✅ Firebase updated successfully!")
                        self.last_update_time = current_time
                    else:
                        print("❌ Firebase update failed")
                else:
                    print("⏭️ No changes detected - skipping Firebase update")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        def start(self):
            print("=" * 50)
            print(f"🤖 ROBOT {ROBOT_ID} - READY")
            print("=" * 50)
            self.running = True
            
            try:
                # Initial sensor check
                print("🔧 First sensor check...")
                self.sensor_manager.check_all_sensors()
                
                # Force first Firebase update
                self.update_firebase()
                
                loop_count = 0
                # Main loop
                while self.running:
                    loop_count += 1
                    print(f"\n🔄 Loop #{loop_count}")
                    
                    # Check sensors and update if needed
                    self.sensor_manager.check_all_sensors()
                    self.update_firebase()
                    
                    # Wait before next check
                    time.sleep(SENSOR_CHECK_INTERVAL)
                    
            except KeyboardInterrupt:
                print("\n🛑 Stopping...")
                self.stop()
            except Exception as e:
                print(f"💥 Error: {e}")
                self.stop()
        
        def stop(self):
            print("🛑 Cleaning up...")
            self.running = False
            self.sensor_manager.cleanup()
            print("✅ Stopped")

    # Start the robot
    robot = RobotController()
    robot.start()
    
except KeyboardInterrupt:
    print("👋 Stopped by user")
except Exception as e:
    print(f"💥 Startup failed: {e}")
