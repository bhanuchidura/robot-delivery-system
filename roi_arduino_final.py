# rpi_arduino_final.py - Fixed version
import serial
import time
import requests

# Configuration
FIREBASE_URL = "https://delivery-robot-p1nl-default-rtdb.europe-west1.firebasedatabase.app"
ROBOT_ID = "Robot_001"
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600
OCCUPANCY_THRESHOLD = 30

class ArduinoManager:
    def __init__(self):
        self.ser = None
        self.current_occupancy = {1: False, 2: False, 3: False}
        self.current_locks = {1: False, 2: False, 3: False}
        self.connected = self.connect_arduino()
        
    def connect_arduino(self):
        """Connect to Arduino - accept any data as 'ready'"""
        try:
            print(f"🔌 Connecting to {SERIAL_PORT}...")
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)  # Wait for Arduino reset
            
            print("✅ Serial port opened, checking Arduino...")
            
            # Clear any existing data
            self.ser.reset_input_buffer()
            
            # Wait for any data from Arduino (consider it "ready")
            start_time = time.time()
            while time.time() - start_time < 10:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode().strip()
                    print(f"📥 Arduino sent: '{line}'")
                    if "ARDUINO_READY" in line or "DIST:" in line:
                        print("🎯 Arduino communication established!")
                        return True
                    else:
                        print(f"📥 (Other message): {line}")
                print(".", end="", flush=True)
                time.sleep(0.5)
            
            print("\n⚠️  Arduino connected but no expected data")
            print("💡 Continuing anyway...")
            return True  # Continue even if no ready message
            
        except Exception as e:
            print(f"❌ Serial connection failed: {e}")
            return False
    
    def send_command(self, command):
        """Send command to Arduino"""
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(f"{command}\n".encode())
                print(f"📤 Sent: {command}")
                return True
            except Exception as e:
                print(f"❌ Send failed: {e}")
        return False
    
    def read_serial(self):
        """Read data from Arduino"""
        if self.ser and self.ser.in_waiting:
            try:
                line = self.ser.readline().decode().strip()
                if line:
                    return line
            except Exception as e:
                print(f"❌ Read error: {e}")
        return None
    
    def process_sensor_data(self, data_string):
        """Process sensor data and return changes only"""
        if not data_string.startswith("DIST:"):
            return None
            
        try:
            distances_str = data_string.replace("DIST:", "")
            distances = distances_str.split(",")
            
            changes = {}
            
            for i, dist_str in enumerate(distances, 1):
                distance = int(dist_str) if dist_str.isdigit() else 400
                new_occupied = distance < OCCUPANCY_THRESHOLD
                old_occupied = self.current_occupancy[i]
                
                if new_occupied != old_occupied:
                    changes[i] = new_occupied
                    self.current_occupancy[i] = new_occupied
                    status = "📦 OCCUPIED" if new_occupied else "🔄 EMPTY"
                    print(f"🔄 Box {i} changed: {distance}cm → {status}")
            
            return changes if changes else None
            
        except Exception as e:
            print(f"❌ Sensor data error: {e}")
            return None
    
    def handle_lock_response(self, response):
        """Update lock states based on Arduino responses"""
        if "LOCK_1_OPENED" in response:
            self.current_locks[1] = True
            print("🔓 Box 1 opened")
        elif "LOCK_1_CLOSED" in response:
            self.current_locks[1] = False
            print("🔒 Box 1 closed")
        elif "LOCK_2_OPENED" in response:
            self.current_locks[2] = True
            print("🔓 Box 2 opened")
        elif "LOCK_2_CLOSED" in response:
            self.current_locks[2] = False
            print("🔒 Box 2 closed")
        elif "LOCK_3_OPENED" in response:
            self.current_locks[3] = True
            print("🔓 Box 3 opened")
        elif "LOCK_3_CLOSED" in response:
            self.current_locks[3] = False
            print("🔒 Box 3 closed")
        elif "ALL_LOCKS_OPENED" in response:
            self.current_locks[1] = True
            self.current_locks[2] = True
            self.current_locks[3] = True
            print("🔓 All boxes opened")
        elif "ALL_LOCKS_CLOSED" in response:
            self.current_locks[1] = False
            self.current_locks[2] = False
            self.current_locks[3] = False
            print("🔒 All boxes closed")
    
    def get_current_status(self):
        """Get current status for Firebase"""
        return {
            1: {'is_open': self.current_locks[1], 'is_occupied': self.current_occupancy[1]},
            2: {'is_open': self.current_locks[2], 'is_occupied': self.current_occupancy[2]},
            3: {'is_open': self.current_locks[3], 'is_occupied': self.current_occupancy[3]}
        }
    
    def get_current_lock_states(self):
        return {1: self.current_locks[1], 2: self.current_locks[2], 3: self.current_locks[3]}
    
    def open_box(self, box_num):
        return self.send_command(f"OPEN_{box_num}")
    
    def close_box(self, box_num):
        return self.send_command(f"CLOSE_{box_num}")
    
    def open_all_boxes(self):
        return self.send_command("OPEN_ALL")
    
    def close_all_boxes(self):
        return self.send_command("CLOSE_ALL")
    
    def cleanup(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

class FirebaseManager:
    def __init__(self):
        self.base_url = FIREBASE_URL
        self.robot_id = ROBOT_ID
        self.last_is_open_states = {1: False, 2: False, 3: False}
    
    def update_firebase(self, compartments_data):
        """Update Firebase with current status"""
        try:
            robot_data = {
                'name': f"Delivery Robot {self.robot_id}",
                'status': "OPERATIONAL",
                'last_updated': time.time(),
                'battery_level': 85,
            }
            
            url1 = f"{self.base_url}/robots/{self.robot_id}.json"
            url2 = f"{self.base_url}/robots/{self.robot_id}/compartments.json"
            
            response1 = requests.put(url1, json=robot_data, timeout=5)
            response2 = requests.put(url2, json=compartments_data, timeout=5)
            
            success = response1.status_code == 200 and response2.status_code == 200
            if success:
                print("📡 Firebase updated")
            return success
            
        except Exception as e:
            print(f"❌ Firebase error: {e}")
            return False
    
    def check_lock_commands(self, current_physical_states):
        """Check if frontend changed is_open for any box - FIXED"""
        try:
            url = f"{self.base_url}/robots/{self.robot_id}/compartments.json"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                return []
            
            firebase_data = response.json()
            
            # Handle case where firebase_data might be a list or None
            if not firebase_data or not isinstance(firebase_data, dict):
                return []
            
            commands = []
            
            for box_num, box_data in firebase_data.items():
                if not box_data or not isinstance(box_data, dict) or 'is_open' not in box_data:
                    continue
                    
                try:
                    box_num = int(box_num)
                except:
                    continue
                    
                firebase_state = box_data['is_open']
                physical_state = current_physical_states.get(box_num, False)
                last_state = self.last_is_open_states.get(box_num)
                
                if (firebase_state != last_state and 
                    firebase_state != physical_state):
                    
                    if firebase_state:
                        commands.append(('OPEN', box_num))
                        print(f"🎯 Frontend: OPEN Box {box_num}")
                    else:
                        commands.append(('CLOSE', box_num))
                        print(f"🎯 Frontend: CLOSE Box {box_num}")
                    
                    self.last_is_open_states[box_num] = firebase_state
            
            return commands
            
        except Exception as e:
            print(f"❌ Firebase check error: {e}")
            return []

def main():
    print("🤖 ARDUINO NANO + RPi 5 - FINAL VERSION")
    print("=" * 50)
    
    arduino = ArduinoManager()
    firebase = FirebaseManager()
    
    if not arduino.connected:
        print("❌ Failed to connect to Arduino")
        return
    
    try:
        print("🔄 Starting main loop...")
        while True:
            # Read from Arduino
            data = arduino.read_serial()
            if data:
                print(f"📥 From Arduino: {data}")
                
                # Process sensor data
                occupancy_changes = arduino.process_sensor_data(data)
                if occupancy_changes:
                    current_status = arduino.get_current_status()
                    firebase.update_firebase(current_status)
                
                # Handle lock responses
                arduino.handle_lock_response(data)
            
            # Check Firebase for lock commands
            current_lock_states = arduino.get_current_lock_states()
            commands = firebase.check_lock_commands(current_lock_states)
            
            # Execute lock commands
            for action, box_num in commands:
                if action == 'OPEN':
                    arduino.open_box(box_num)
                else:
                    arduino.close_box(box_num)
                
                # Update Firebase after lock action
                current_status = arduino.get_current_status()
                firebase.update_firebase(current_status)
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping system...")
    except Exception as e:
        print(f"💥 System error: {e}")
    finally:
        arduino.cleanup()
        print("✅ System stopped")

if __name__ == "__main__":
    main()
