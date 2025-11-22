# run_robot.py - Simple version without aggressive GPIO reset
import time
from gpiozero import OutputDevice, DigitalInputDevice, DigitalOutputDevice

# Direct configuration
ROBOT_ID = "Robot_001"
FIREBASE_URL = "https://delivery-robot-p1nl-default-rtdb.europe-west1.firebasedatabase.app"

# Box configuration
BOX_CONFIG = {
    1: {
        'lock_pin': 17,           # GPIO17 - Physical Pin 11
        'ultrasonic_trigger': 23, # GPIO23 - Physical Pin 16  
        'ultrasonic_echo': 24,    # GPIO24 - Physical Pin 18
    }
}

OCCUPIED_DISTANCE_CM = 2.0
SENSOR_CHECK_INTERVAL = 2
FIREBASE_UPDATE_INTERVAL = 3

class RealSensorManager:
    def __init__(self):
        self.box_status = {}
        self.locks = {}
        self.triggers = {}
        self.echos = {}
        self.last_occupancy_status = {}
        self.setup_sensors()
        
    def setup_sensors(self):
        print("🔧 REAL HARDWARE: Setting up Box 1 only...")
        
        # Start with just Box 1
        box_num = 1
        config = BOX_CONFIG[box_num]
        
        try:
            # Setup lock control
            print(f"Setting up Lock (GPIO{config['lock_pin']})...", end=" ")
            self.locks[box_num] = OutputDevice(
                config['lock_pin'], 
                active_high=False, 
                initial_value=False
            )
            print("✅")
            
            # Setup ultrasonic sensor pins
            print(f"Setting up Trigger (GPIO{config['ultrasonic_trigger']})...", end=" ")
            self.triggers[box_num] = DigitalOutputDevice(config['ultrasonic_trigger'])
            print("✅")
            
            print(f"Setting up Echo (GPIO{config['ultrasonic_echo']})...", end=" ")
            self.echos[box_num] = DigitalInputDevice(config['ultrasonic_echo'])
            print("✅")
            
            # Initialize status
            self.box_status[box_num] = {
                'is_open': False,
                'is_occupied': False,
                'distance': 100.0,
                'last_checked': time.time()
            }
            
            # Track previous occupancy for change detection
            self.last_occupancy_status[box_num] = False
            
            print(f"🎯 Box {box_num} setup complete!")
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            print("💡 Try: sudo pkill -f python3 && sleep 2")
            raise
        
        print("✅ Hardware initialized!")
    
    def measure_distance(self, box_num):
        """Measure distance using pure gpiozero"""
        if box_num not in self.triggers or box_num not in self.echos:
            return 100.0
            
        try:
            trigger = self.triggers[box_num]
            echo = self.echos[box_num]
            
            # Ensure trigger starts low
            trigger.off()
            time.sleep(0.0005)
            
            # Send trigger pulse
            trigger.on()
            time.sleep(0.00001)
            trigger.off()
            
            pulse_start = time.time()
            pulse_end = time.time()
            
            # Wait for echo to go HIGH (with timeout)
            timeout_start = time.time()
            while not echo.is_active:
                pulse_start = time.time()
                if time.time() - timeout_start > 0.1:
                    return 100.0
            
            # Wait for echo to go LOW (with timeout)
            timeout_start = time.time()
            while echo.is_active:
                pulse_end = time.time()
                if time.time() - timeout_start > 0.1:
                    return 100.0
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = (pulse_duration * 34300) / 2
            
            # Filter unrealistic values
            if distance < 0.5 or distance > 400:
                return 100.0
                
            return distance
            
        except Exception as e:
            print(f"❌ Sensor error Box {box_num}: {e}")
            return 100.0
    
    def check_all_sensors(self):
        """Check all sensors"""
        print("🔍 Checking sensors...")
        
        status_changed = False
        current_time = time.time()
        
        for box_num in self.box_status:
            distance = self.measure_distance(box_num)
            
            # Determine occupancy: < OCCUPIED_DISTANCE_CM = package present
            is_occupied = distance < OCCUPIED_DISTANCE_CM
            
            # Check if occupancy status changed
            old_occupied = self.last_occupancy_status[box_num]
            occupancy_changed = (is_occupied != old_occupied)
            
            if occupancy_changed:
                status_changed = True
                self.last_occupancy_status[box_num] = is_occupied
            
            # Always update current status
            self.box_status[box_num]['distance'] = distance
            self.box_status[box_num]['is_occupied'] = is_occupied
            self.box_status[box_num]['last_checked'] = current_time
            
            status = "📦 PRESENT" if is_occupied else "🔄 EMPTY"
            print(f"Box {box_num}: {distance:.1f}cm → {status}")
        
        return self.box_status, status_changed
    
    def open_box(self, box_num):
        """Physically open the box"""
        if box_num in self.locks:
            self.locks[box_num].on()
            self.box_status[box_num]['is_open'] = True
            print(f"🔓 Box {box_num} OPENED")
            return True
        return False
    
    def close_box(self, box_num):
        """Physically close the box"""
        if box_num in self.locks:
            self.locks[box_num].off()
            self.box_status[box_num]['is_open'] = False
            print(f"🔒 Box {box_num} CLOSED")
            return True
        return False
    
    def get_status(self):
        return self.box_status
    
    def cleanup(self):
        """Safe hardware cleanup"""
        print("🧹 Cleaning up hardware...")
        for box_num in self.locks:
            self.close_box(box_num)
        
        # Close all gpiozero devices
        for device_dict in [self.locks, self.triggers, self.echos]:
            for device in device_dict.values():
                try:
                    device.close()
                except:
                    pass
        
        print("🧹 Hardware cleanup complete")

# Import FirebaseManager
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from firebase_manager import FirebaseManager

class RobotController:
    def __init__(self):
        print(f"🔧 Initializing REAL HARDWARE for {ROBOT_ID}...")
        self.sensor_manager = RealSensorManager()
        self.firebase_manager = FirebaseManager()
        self.running = False
        self.last_firebase_update = 0
        
    def execute_lock_action(self, action, box_num):
        """Execute lock action from frontend"""
        if action == 'OPEN':
            success = self.sensor_manager.open_box(box_num)
            if success:
                print(f"✅ Executed: OPEN Box {box_num}")
        elif action == 'CLOSE':
            success = self.sensor_manager.close_box(box_num)
            if success:
                print(f"✅ Executed: CLOSE Box {box_num}")
        return success
    
    def start(self):
        print("=" * 50)
        print(f"🤖 REAL HARDWARE - {ROBOT_ID}")
        print("=" * 50)
        self.running = True
        
        try:
            # Initial setup
            print("🔄 Initial sensor check...")
            box_status, status_changed = self.sensor_manager.check_all_sensors()
            
            # Initialize last known states with current physical states
            current_states = {box_num: status['is_open'] for box_num, status in box_status.items()}
            for box_num, is_open in current_states.items():
                self.firebase_manager.last_is_open_states[box_num] = is_open
            
            # Force initial Firebase update
            self.update_firebase(force=True, reason="initial_setup")
            
            # Main loop
            while self.running:
                # Check sensors
                box_status, status_changed = self.sensor_manager.check_all_sensors()
                
                # Get current physical lock states
                current_physical_states = {box_num: status['is_open'] for box_num, status in box_status.items()}
                
                # Check if frontend changed any is_open states
                actions = self.firebase_manager.check_is_open_changes(current_physical_states)
                
                # Execute any actions from frontend
                for action, box_num in actions:
                    self.execute_lock_action(action, box_num)
                    # Update Firebase immediately after executing action
                    self.update_firebase(force=True, reason=f"executed_{action}_{box_num}")
                
                # Update Firebase if occupancy changed or time interval reached
                if status_changed or actions:
                    self.update_firebase(force=True, reason="status_changed")
                else:
                    self.update_firebase(force=False, reason="periodic_check")
                
                time.sleep(SENSOR_CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal...")
            self.stop()
        except Exception as e:
            print(f"💥 Hardware error: {e}")
            self.stop()
    
    def update_firebase(self, force=False, reason="auto"):
        """Update Firebase with current physical status"""
        try:
            current_time = time.time()
            
            # Get current physical status from sensors
            box_status = self.sensor_manager.get_status()
            
            # Prepare compartment data for Firebase
            compartments_data = {}
            for box_num, status in box_status.items():
                compartments_data[box_num] = {
                    'is_open': status['is_open'],        # Physical lock state
                    'is_occupied': status['is_occupied'], # Sensor detection
                    'distance_cm': status['distance'],
                    'ultrasonic_status': True,
                    'last_checked': time.time()
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
                remaining = int(FIREBASE_UPDATE_INTERVAL - (current_time - self.last_firebase_update))
                print(f"⏳ Skipping Firebase update - {remaining}s remaining")
                return True
                
        except Exception as e:
            print(f"❌ Firebase error: {e}")
            return False
    
    def stop(self):
        print("🛑 Stopping hardware...")
        self.running = False
        # Final update and cleanup
        self.update_firebase(force=True, reason="shutdown")
        self.sensor_manager.cleanup()
        print("✅ Hardware stopped cleanly")

if __name__ == "__main__":
    print("🤖 STARTING ROBOT...")
    
    try:
        robot = RobotController()
        robot.start()
    except KeyboardInterrupt:
        print("👋 Hardware stopped by user")
    except Exception as e:
        print(f"💥 Hardware initialization error: {e}")
