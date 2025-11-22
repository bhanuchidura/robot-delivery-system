# test_all_sensors.py - Pure gpiozero version
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time
from gpiozero import OutputDevice, DigitalInputDevice, DigitalOutputDevice
from config import BOX_CONFIG, OCCUPIED_DISTANCE_CM

class SimpleSensorManager:
    def __init__(self):
        self.box_status = {}
        self.locks = {}
        self.triggers = {}
        self.echos = {}
        self.setup_sensors()
        
    def setup_sensors(self):
        print("🔧 REAL HARDWARE: Setting up with gpiozero only...")
        
        # Clean up any existing devices first
        self.cleanup()
        
        for box_num, config in BOX_CONFIG.items():
            try:
                # Setup lock
                self.locks[box_num] = OutputDevice(config['lock_pin'], active_high=False, initial_value=False)
                
                # Setup ultrasonic sensors
                self.triggers[box_num] = DigitalOutputDevice(config['ultrasonic_trigger'])
                self.echos[box_num] = DigitalInputDevice(config['ultrasonic_echo'])
                
                self.box_status[box_num] = {
                    'is_open': False,
                    'is_occupied': False,
                    'distance': 100.0
                }
                print(f"✅ Box {box_num} - Lock:GPIO{config['lock_pin']}")
                
            except Exception as e:
                print(f"❌ Box {box_num} setup failed: {e}")
                raise
        
        print("✅ All hardware initialized!")
    
    def measure_distance(self, box_num):
        """Measure distance using pure gpiozero"""
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
            
            # Wait for echo to go HIGH
            timeout_start = time.time()
            while not echo.is_active:
                pulse_start = time.time()
                if time.time() - timeout_start > 0.1:
                    return 100.0
            
            # Wait for echo to go LOW
            timeout_start = time.time()
            while echo.is_active:
                pulse_end = time.time()
                if time.time() - timeout_start > 0.1:
                    return 100.0
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = (pulse_duration * 34300) / 2
            
            if distance < 0.5 or distance > 400:
                return 100.0
                
            return distance
            
        except Exception as e:
            print(f"❌ Sensor error Box {box_num}: {e}")
            return 100.0
    
    def check_all_sensors(self):
        """Check all sensors"""
        print("🔍 Checking sensors...")
        
        for box_num in self.box_status:
            distance = self.measure_distance(box_num)
            is_occupied = distance < OCCUPIED_DISTANCE_CM
            
            self.box_status[box_num]['distance'] = distance
            self.box_status[box_num]['is_occupied'] = is_occupied
            
            status = "📦 PRESENT" if is_occupied else "🔄 EMPTY"
            print(f"Box {box_num}: {distance:.1f}cm → {status}")
        
        return self.box_status
    
    def open_box(self, box_num):
        """Open the box"""
        if box_num in self.locks:
            self.locks[box_num].on()
            self.box_status[box_num]['is_open'] = True
            print(f"🔓 Box {box_num} OPENED")
            return True
        return False
    
    def close_box(self, box_num):
        """Close the box"""
        if box_num in self.locks:
            self.locks[box_num].off()
            self.box_status[box_num]['is_open'] = False
            print(f"🔒 Box {box_num} CLOSED")
            return True
        return False
    
    def open_all_boxes(self):
        print("🚪 Opening ALL boxes...")
        for box_num in self.locks:
            self.open_box(box_num)
        print("✅ All boxes OPEN")
    
    def close_all_boxes(self):
        print("🔒 Closing ALL boxes...")
        for box_num in self.locks:
            self.close_box(box_num)
        print("✅ All boxes CLOSED")
    
    def get_status(self):
        return self.box_status
    
    def cleanup(self):
        """Cleanup hardware"""
        print("🧹 Cleaning up hardware...")
        
        # Close all devices
        for device_dict in [self.locks, self.triggers, self.echos]:
            for device in device_dict.values():
                try:
                    device.close()
                except:
                    pass
        
        print("🧹 Hardware cleanup complete")

def test_all_sensors():
    print("🔍 COMPREHENSIVE SENSOR TEST")
    print("=" * 50)
    print("This test will check all sensors and locks together")
    print("Place packages in different boxes to test detection")
    print()
    
    sensor_manager = None
    
    try:
        sensor_manager = SimpleSensorManager()
        
        print("1. Initial sensor check:")
        box_status = sensor_manager.check_all_sensors()
        print("   ✅ Initial check complete")
        
        print("\n2. Testing lock controls:")
        input("   Press Enter to OPEN all locks...")
        sensor_manager.open_all_boxes()
        time.sleep(3)
        
        input("   Press Enter to CLOSE all locks...")
        sensor_manager.close_all_boxes()
        time.sleep(2)
        
        print("\n3. Final sensor check:")
        box_status = sensor_manager.check_all_sensors()
        
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
    
    print("\n" + "=" * 50)
    print("🎯 COMPREHENSIVE TEST COMPLETE")

if __name__ == "__main__":
    test_all_sensors()
