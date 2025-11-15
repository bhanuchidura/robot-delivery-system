# testing/test_ultrasonic_safe.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import RPi.GPIO as GPIO
import time
from config import BOX_CONFIG, OCCUPIED_DISTANCE_CM

def safe_measure_distance(box_num):
    """Safe distance measurement with error handling"""
    config = BOX_CONFIG[box_num]
    
    try:
        # Setup pins fresh each time
        GPIO.setup(config['ultrasonic_trigger'], GPIO.OUT)
        GPIO.setup(config['ultrasonic_echo'], GPIO.IN)
        
        # Ensure trigger starts low
        GPIO.output(config['ultrasonic_trigger'], False)
        time.sleep(0.1)  # Longer stabilization
        
        # Send trigger pulse
        GPIO.output(config['ultrasonic_trigger'], True)
        time.sleep(0.00001)  # 10 microseconds
        GPIO.output(config['ultrasonic_trigger'], False)
        
        start_time = time.time()
        stop_time = time.time()
        
        # Wait for echo to go high (with timeout)
        timeout = time.time() + 0.1  # 100ms timeout
        while GPIO.input(config['ultrasonic_echo']) == 0:
            start_time = time.time()
            if time.time() > timeout:
                return None
        
        # Wait for echo to go low (with timeout)
        timeout = time.time() + 0.1  # 100ms timeout
        while GPIO.input(config['ultrasonic_echo']) == 1:
            stop_time = time.time()
            if time.time() > timeout:
                return None
        
        # Calculate distance
        elapsed = stop_time - start_time
        distance = (elapsed * 34300) / 2  # Speed of sound in cm/s
        
        # Validate distance
        if 2.0 <= distance <= 400.0:
            return distance
        else:
            return None
            
    except Exception as e:
        print(f"    Measurement error: {e}")
        return None
    finally:
        # Clean up these pins
        GPIO.cleanup(config['ultrasonic_trigger'])
        GPIO.cleanup(config['ultrasonic_echo'])

def test_ultrasonic_safe():
    print("📡 SAFE ULTRASONIC SENSOR TEST")
    print("=" * 50)
    print("This version handles GPIO errors more gracefully")
    print()
    
    # Initialize GPIO once
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(True)
    
    print("Testing each ultrasonic sensor...")
    print("Place an object close to sensors (within 30cm) to test detection")
    print()
    
    successful_boxes = 0
    
    for box_num in BOX_CONFIG:
        print(f"📦 Testing Box {box_num}:")
        print(f"  Trigger: GPIO{BOX_CONFIG[box_num]['ultrasonic_trigger']}")
        print(f"  Echo: GPIO{BOX_CONFIG[box_num]['ultrasonic_echo']}")
        
        measurements = []
        
        for i in range(3):  # Fewer measurements for stability
            print(f"    Measurement {i+1}...", end=" ")
            distance = safe_measure_distance(box_num)
            
            if distance is not None:
                measurements.append(distance)
                status = "📦 PRESENT" if distance < OCCUPIED_DISTANCE_CM else "🔄 EMPTY"
                print(f"{distance:.1f}cm - {status}")
            else:
                print("❌ FAILED")
            
            time.sleep(0.5)  # Longer delay between measurements
        
        if measurements:
            avg_distance = sum(measurements) / len(measurements)
            detection_rate = (len(measurements) / 3) * 100
            print(f"  📊 Average: {avg_distance:.1f}cm, Success: {detection_rate:.0f}%")
            successful_boxes += 1
        else:
            print("  ❌ All measurements failed")
        
        print()
    
    # Final cleanup
    GPIO.cleanup()
    
    print("=" * 50)
    print(f"🎯 TEST COMPLETE: {successful_boxes}/{len(BOX_CONFIG)} boxes working")
    
    if successful_boxes == len(BOX_CONFIG):
        print("✅ All ultrasonic sensors are working!")
    else:
        print("⚠️  Some sensors have issues. Check wiring and GPIO pins.")

if __name__ == "__main__":
    test_ultrasonic_safe()