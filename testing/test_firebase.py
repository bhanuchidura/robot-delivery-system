# testing/test_firebase.py
import time
from firebase_manager import FirebaseManager

def test_firebase():
    print("🌐 TESTING FIREBASE CONNECTION")
    print("=" * 40)
    
    fb = FirebaseManager()
    
    try:
        # Test 1: Read current robot status
        print("1. Reading robot status...")
        robot_data = fb.get_data(f"robots/{fb.robot_id}")
        if robot_data:
            print(f"   ✅ Robot data found: {robot_data.get('name', 'Unknown')}")
        else:
            print("   ❌ No robot data found")
        
        # Test 2: Send test data
        print("2. Sending test data...")
        test_compartments = {
            1: {'is_open': False, 'is_occupied': True, 'distance_cm': 15.5, 'ultrasonic_status': True, 'last_checked': time.time()},
            2: {'is_open': False, 'is_occupied': False, 'distance_cm': 85.2, 'ultrasonic_status': True, 'last_checked': time.time()},
            3: {'is_open': True, 'is_occupied': True, 'distance_cm': 8.7, 'ultrasonic_status': True, 'last_checked': time.time()}
        }
        
        success = fb.update_robot_status(test_compartments, "TESTING")
        if success:
            print("   ✅ Test data sent successfully")
        else:
            print("   ❌ Failed to send test data")
        
        # Test 3: Check commands
        print("3. Checking for commands...")
        command = fb.check_commands()
        if command:
            print(f"   ✅ Command received: {command}")
        else:
            print("   ✅ No commands (this is normal)")
        
        # Test 4: Test individual data sending
        print("4. Testing individual data paths...")
        test_data = {"test_timestamp": time.time(), "message": "Firebase test successful"}
        success = fb.send_data(test_data, f"test/{fb.robot_id}")
        if success:
            print("   ✅ Individual data send successful")
        else:
            print("   ❌ Individual data send failed")
        
    except Exception as e:
        print(f"❌ Firebase test failed: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎯 FIREBASE TEST COMPLETE")
    return True

if __name__ == "__main__":
    test_firebase()