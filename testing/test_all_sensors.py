# testing/test_all_sensors.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time
from real_sensor_manager_simple import RealSensorManager

def test_all_sensors():
    print("🔍 COMPREHENSIVE SENSOR TEST")
    print("=" * 40)
    print("This test will check all sensors and locks together")
    print("Place packages in different boxes to test detection")
    print()
    
    sensor_manager = None
    
    try:
        sensor_manager = RealSensorManager()
        
        print("1. Initial sensor check:")
        box_status, status_changed = sensor_manager.check_all_sensors()
        print("   ✅ Initial check complete")
        
        print("\n2. Testing lock controls:")
        input("   Press Enter to OPEN all locks...")
        sensor_manager.open_all_boxes()
        time.sleep(3)
        
        input("   Press Enter to CLOSE all locks...")
        sensor_manager.close_all_boxes()
        time.sleep(2)
        
        print("\n3. Final sensor check:")
        box_status, status_changed = sensor_manager.check_all_sensors()
        
        print("\n4. Individual box control test:")
        for box_num in [1, 2, 3]:
            print(f"   Testing Box {box_num}...")
            sensor_manager.open_box(box_num)
            time.sleep(1)
            sensor_manager.close_box(box_num)
            time.sleep(1)
        
        print("\n📊 FINAL STATUS:")
        for box_num, status in box_status.items():
            lock_state = "OPEN" if status['is_open'] else "CLOSED"
            occupancy = "OCCUPIED" if status['is_occupied'] else "EMPTY"
            print(f"   Box {box_num}: {lock_state}, {occupancy}, {status['distance']:.1f}cm")
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
    
    finally:
        if sensor_manager:
            sensor_manager.cleanup()
    
    print("\n" + "=" * 40)
    print("🎯 COMPREHENSIVE TEST COMPLETE")

if __name__ == "__main__":
    test_all_sensors()