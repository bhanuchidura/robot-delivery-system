# robot_arduino.py - RPi controls Arduino via USB
import serial
import time
import requests
import json

ROBOT_ID = "Robot_001"
FIREBASE_URL = "https://delivery-robot-p1nl-default-rtdb.europe-west1.firebasedatabase.app"

class ArduinoManager:
    def __init__(self):
        self.ser = None
        self.connect_arduino()
        
    def connect_arduino(self):
        """Connect to Arduino via USB - CH340 version"""
        try:
            print("🔌 Connecting to Arduino on /dev/ttyUSB0 (CH340)...")
            
            # CH340 needs longer timeout and delay
            self.ser = serial.Serial(
                '/dev/ttyUSB0', 
                9600, 
                timeout=2,
                write_timeout=2
            )
            
            # Wait for Arduino to reset and initialize
            print("⏳ Waiting for Arduino initialization...")
            time.sleep(3)
            
            # Clear any buffered data
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            
            # Test connection
            self.ser.write(b"PING\n")
            time.sleep(1)
            
            response = self.ser.readline().decode().strip()
            print(f"📡 Arduino response: '{response}'")
            
            if "PONG" in response or "ARDUINO" in response or "READY" in response:
                print("✅ Arduino connected successfully!")
                return
            else:
                # Try reading more data
                time.sleep(1)
                while self.ser.in_waiting > 0:
                    line = self.ser.readline().decode().strip()
                    print(f"📡 Additional: '{line}'")
                    if "ARDUINO" in line or "READY" in line:
                        print("✅ Arduino connected!")
                        return
                
                raise Exception("Arduino not responding properly")
                
        except Exception as e:
            print(f"❌ Arduino connection failed: {e}")
            raise
    
    def send_command(self, command):
        """Send command to Arduino and get ALL responses"""
        try:
            self.ser.write(f"{command}\n".encode())
            time.sleep(0.5)  # Give Arduino time to respond
            responses = []
            
            # Read all available responses
            start_time = time.time()
            while time.time() - start_time < 2:  # Read for up to 2 seconds
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode().strip()
                    if line:
                        responses.append(line)
                else:
                    time.sleep(0.1)
            
            print(f"📡 Command '{command}' got {len(responses)} responses: {responses}")
            return responses
            
        except Exception as e:
            print(f"❌ Command failed: {e}")
            return []
    
    def open_box(self, box_num):
        """Open specific box for 2 seconds"""
        print(f"🔓 Opening Box {box_num}...")
        responses = self.send_command(f"OPEN{box_num}")
        for response in responses:
            print(f"   {response}")
        return any("OPENED" in r for r in responses)
    
    def get_status(self):
        """Get status of all boxes - fixed version"""
        responses = self.send_command("STATUS")
        status = {}
        print(f"🔍 Raw STATUS responses: {responses}")  # DEBUG
        
        for response in responses:
            if response.startswith("STATUS:"):
                parts = response.split(":")
                print(f"🔍 Parsing STATUS: {parts}")  # DEBUG
                if len(parts) >= 5:
                    try:
                        box_num = int(parts[1])
                        status[box_num] = {
                            'is_open': parts[2] == "1",
                            'is_occupied': parts[3] == "1", 
                            'distance': float(parts[4]) if parts[4] != "999" else 100.0
                        }
                        print(f"✅ Parsed Box {box_num}: open={status[box_num]['is_open']}, occupied={status[box_num]['is_occupied']}, distance={status[box_num]['distance']}")
                    except Exception as e:
                        print(f"❌ Error parsing STATUS: {e}")
        return status
    
    def check_messages(self):
        """Check for any messages from Arduino"""
        messages = []
        try:
            while self.ser.in_waiting > 0:
                message = self.ser.readline().decode().strip()
                if message:
                    messages.append(message)
        except:
            pass
        return messages

class FirebaseManager:
    def __init__(self):
        self.base_url = FIREBASE_URL
        self.robot_id = ROBOT_ID
        self.last_is_open_states = {}
    
    def update_robot_status(self, compartments_data):
        """Simple Firebase update"""
        try:
            updates = {}
            updates[f'robots/{self.robot_id}/last_updated'] = time.time()
            updates[f'robots/{self.robot_id}/battery_level'] = 85
            
            # Update compartments as array indexes 1, 2, 3
            for box_num, sensor_data in compartments_data.items():
                index = int(box_num)
                updates[f'robots/{self.robot_id}/compartments/{index}/is_occupied'] = sensor_data['is_occupied']
                updates[f'robots/{self.robot_id}/compartments/{index}/distance_cm'] = sensor_data['distance_cm']
                updates[f'robots/{self.robot_id}/compartments/{index}/ultrasonic_status'] = sensor_data['ultrasonic_status']
                updates[f'robots/{self.robot_id}/compartments/{index}/last_checked'] = sensor_data['last_checked']
            
            # CORRECT URL - only ONE .json at the end
            url = f"{self.base_url}/.json"
            print(f"📡 Updating Firebase...")
            
            response = requests.patch(url, json=updates, timeout=10)
            
            # Add debug prints
            print(f"📊 Sending sensor data:")
            for box_num, sensor_data in compartments_data.items():
                print(f"   Box {box_num}: occupied={sensor_data['is_occupied']}, distance={sensor_data['distance_cm']}cm")
            
            print(f"📦 Updates being sent: {updates}")


            if response.status_code == 200:
                print("✅ Firebase updated successfully")
                return True
            else:
                print(f"❌ Firebase update failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Firebase error: {e}")
            return False

    
    def check_is_open_changes(self, current_physical_states):
        """Check if frontend wants to open/close boxes - handle array structure"""
        try:
            # Get current Firebase data
            url = f"{self.base_url}/robots/{self.robot_id}.json"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                return []
            
            robot_data = response.json()
            if not robot_data or 'compartments' not in robot_data:
                return []
            
            compartments_data = robot_data['compartments']
            actions = []
            
            # Handle both array and object structures
            if isinstance(compartments_data, list):
                # Array structure (index 1, 2, 3)
                for index in range(1, 4):  # Check indexes 1, 2, 3
                    if index < len(compartments_data) and compartments_data[index]:
                        comp_data = compartments_data[index]
                        if 'is_open' in comp_data:
                            firebase_is_open = comp_data['is_open']
                            physical_is_open = current_physical_states.get(index, False)
                            last_known_state = self.last_is_open_states.get(index)
                            
                            print(f"🔍 Box {index}: Firebase={firebase_is_open}, Physical={physical_is_open}, Last={last_known_state}")
                            
                            # If Firebase state changed AND doesn't match physical state
                            if (firebase_is_open != last_known_state and 
                                firebase_is_open != physical_is_open):
                                
                                if firebase_is_open:
                                    actions.append(('OPEN', index))
                                    print(f"🎯 Frontend requested: OPEN Box {index}")
                                else:
                                    actions.append(('CLOSE', index))
                                    print(f"🎯 Frontend requested: CLOSE Box {index}")
                            
                            # Update last known state
                            self.last_is_open_states[index] = firebase_is_open
            else:
                # Object structure (fallback)
                for box_num_str, comp_data in compartments_data.items():
                    if not comp_data or 'is_open' not in comp_data:
                        continue
                        
                    box_num = int(box_num_str)
                    firebase_is_open = comp_data['is_open']
                    physical_is_open = current_physical_states.get(box_num, False)
                    last_known_state = self.last_is_open_states.get(box_num)
                    
                    print(f"🔍 Box {box_num}: Firebase={firebase_is_open}, Physical={physical_is_open}, Last={last_known_state}")
                    
                    if (firebase_is_open != last_known_state and 
                        firebase_is_open != physical_is_open):
                        
                        if firebase_is_open:
                            actions.append(('OPEN', box_num))
                            print(f"🎯 Frontend requested: OPEN Box {box_num}")
                        else:
                            actions.append(('CLOSE', box_num))
                            print(f"🎯 Frontend requested: CLOSE Box {box_num}")
                    
                    self.last_is_open_states[box_num] = firebase_is_open
            
            return actions

        except Exception as e:
            print(f"❌ Error checking Firebase: {e}")
            return []



def main():
    print("🤖 ARDUINO ROBOT STARTING...")
    print("=" * 40)
    
    try:
        arduino = ArduinoManager()
        firebase = FirebaseManager()
        
        print("✅ System ready!")
        print("📡 Listening for sensor changes and Firebase commands...")
        
        last_firebase_update = 0
        firebase_update_interval = 10  # Update every 10 seconds
        
        while True:
            current_time = time.time()
            
            # 1. Check for messages from Arduino (sensor changes)
            messages = arduino.check_messages()
            for msg in messages:
                print(f"🔔 Arduino: {msg}")
                if "OCCUPANCY:" in msg:
                    # Force Firebase update when occupancy changes
                    last_firebase_update = 0
            
            # 2. Get current physical status
            status = arduino.get_status()
            
            # 3. Check if frontend wants to open boxes
            current_states = {box_num: data['is_open'] for box_num, data in status.items()}
            actions = firebase.check_is_open_changes(current_states)
            
            # 4. Execute any open/close commands from frontend
            for action, box_num in actions:
                if action == 'OPEN':
                    arduino.open_box(box_num)
                    # Update status after opening
                    status = arduino.get_status()
            
            # 5. Update Firebase periodically or when changes occur
            if current_time - last_firebase_update >= firebase_update_interval or actions:
                # DEBUG: Check what status contains
                print(f"🔍 Current status from Arduino: {status}")
                
                # Prepare compartment data - use same indexes as array (1, 2, 3)
                compartments_data = {}
                for box_num, data in status.items():
                    compartments_data[box_num] = {  # This will be 1, 2, 3
                        'is_occupied': data['is_occupied'],
                        'distance_cm': data['distance'],
                        'ultrasonic_status': data['distance'] != 100.0,
                        'last_checked': time.time()
                    }
                
                # DEBUG: Check what we're sending
                print(f"🔍 Prepared compartment data: {compartments_data}")
                    # NOTE: We don't include 'is_open' here - let frontend control that
                
                if firebase.update_robot_status(compartments_data):
                    print("📡 Firebase updated")
                    last_firebase_update = current_time
                else:
                    print("❌ Firebase update failed")
            
            time.sleep(2)  # Main loop delay
            
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    main()
