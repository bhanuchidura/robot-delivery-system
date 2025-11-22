# test_commands.py - Debug command detection
import sys
import os
# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from firebase_manager import FirebaseManager
import time

def test_command_detection():
    print("🔍 TESTING COMMAND DETECTION")
    print("=" * 50)
    
    fb = FirebaseManager()
    
    # Test 1: Check current Firebase structure
    print("1. Checking current Firebase structure...")
    commands_data = fb.get_data(f"robot_commands/{fb.robot_id}")
    print(f"   Current commands data: {commands_data}")
    
    # Test 2: Send a test command
    print("\n2. Sending test command...")
    test_sent = fb.send_data("OPEN_ALL", f"robot_commands/{fb.robot_id}/current_command")
    print(f"   Command sent: {test_sent}")
    
    # Test 3: Check if we can read it back
    print("\n3. Reading command back...")
    for i in range(3):
        command = fb.check_commands()
        print(f"   Attempt {i+1}: {command}")
        time.sleep(1)
    
    # Test 4: Clear command
    print("\n4. Clearing command...")
    cleared = fb.send_data("", f"robot_commands/{fb.robot_id}/current_command")
    print(f"   Command cleared: {cleared}")
    
    print("\n🎯 Command test complete")

if __name__ == "__main__":
    test_command_detection()
