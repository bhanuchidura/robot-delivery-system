# src/firebase_manager.py - Simple version without circular imports
import requests
import time

# Direct configuration (no imports from config)
FIREBASE_URL = "https://delivery-robot-p1nl-default-rtdb.europe-west1.firebasedatabase.app"
ROBOT_ID = "Robot_001"

class FirebaseManager:
    def __init__(self):
        self.base_url = FIREBASE_URL
        self.robot_id = ROBOT_ID
        self.last_is_open_states = {}  # Track previous states to detect changes

    def send_data(self, data, path):
        try:
            url = f"{self.base_url}/{path}.json"
            response = requests.put(url, json=data, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Firebase error: {e}")
            return False

    def get_data(self, path):
        try:
            url = f"{self.base_url}/{path}.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Firebase read error: {e}")
            return None

    def update_robot_status(self, compartments_data, robot_status="IDLE"):
        try:
            robot_data = {
                'name': f"Delivery Robot {self.robot_id}",
                'status': robot_status,
                'last_updated': time.time(),
                'battery_level': 85,
            }

            success1 = self.send_data(robot_data, f"robots/{self.robot_id}")
            success2 = self.send_data(compartments_data, f"robots/{self.robot_id}/compartments")

            return success1 and success2

        except Exception as e:
            print(f"Error updating Firebase: {e}")
            return False

    def check_is_open_changes(self, current_physical_states):
        """Check if frontend changed is_open for any box and return actions needed"""
        try:
            # Get current Firebase states
            firebase_data = self.get_data(f"robots/{self.robot_id}/compartments")
            
            if not firebase_data:
                return []

            actions = []
            
            for box_num, box_data in firebase_data.items():
                if not box_data or 'is_open' not in box_data:
                    continue
                    
                firebase_is_open = box_data['is_open']
                physical_is_open = current_physical_states.get(int(box_num), False)
                last_known_state = self.last_is_open_states.get(int(box_num))
                
                print(f"🔍 Box {box_num}: Firebase={firebase_is_open}, Physical={physical_is_open}, Last={last_known_state}")
                
                # If Firebase state changed AND doesn't match physical state
                if (firebase_is_open != last_known_state and 
                    firebase_is_open != physical_is_open):
                    
                    if firebase_is_open:
                        actions.append(('OPEN', int(box_num)))
                        print(f"🎯 Frontend requested: OPEN Box {box_num}")
                    else:
                        actions.append(('CLOSE', int(box_num)))
                        print(f"🎯 Frontend requested: CLOSE Box {box_num}")
                
                # Update last known state
                self.last_is_open_states[int(box_num)] = firebase_is_open
            
            return actions

        except Exception as e:
            print(f"❌ Error checking is_open changes: {e}")
            return []
