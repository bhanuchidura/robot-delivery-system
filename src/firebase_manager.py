# src/firebase_manager.py
import requests
import time

# Import config directly (will work when run from run_robot.py)
from config import FIREBASE_URL, ROBOT_ID

class FirebaseManager:
    def __init__(self):
        self.base_url = FIREBASE_URL
        self.robot_id = ROBOT_ID
        
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
    
    def check_commands(self):
        try:
            commands = self.get_data(f"robot_commands/{self.robot_id}")
            
            if commands and 'current_command' in commands:
                command = commands['current_command']
                if command:
                    print(f"Received command: {command}")
                    self.send_data("", f"robot_commands/{self.robot_id}/current_command")
                    return command
                    
            return None
            
        except Exception as e:
            print(f"Error checking commands: {e}")
            return None