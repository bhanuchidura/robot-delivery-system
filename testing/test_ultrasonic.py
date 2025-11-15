# testing/test_ultrasonic.py
import RPi.GPIO as GPIO
import time
from config import BOX_CONFIG, OCCUPIED_DISTANCE_CM

def measure_distance(box_num):
    config = BOX_CONFIG[box_num]
    
    try:
        # Send trigger pulse
        GPIO.output(config['ultrasonic_trigger'], False)
        time.sleep(0.0005)
        
        GPIO.output(config['ultrasonic_trigger'], True)
        time.sleep(0.00001)
        GPIO.output(config['ultrasonic_trigger'], False)
        
        pulse_start = time.time()
        pulse_end = time.time()
        
        # Wait for echo
        timeout_start = time.time()
        while GPIO.input(config['ultrasonic_echo']) == 0:
            pulse_start = time.time()
            if time.time() - timeout_start > 0.1:
                return None
        
        timeout_start = time.time()
        while GPIO.input(config['ultrasonic_echo']) == 1:
            pulse_end = time.time()
            if time.time() - timeout_start > 0.1:
                return None
        
        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration * 34300) / 2
        
        if distance < 2.0 or distance > 400.0:
            return None
            
        return distance
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_ultrasonic_sensors():
    print("📡 TESTING ULTRASONIC SENSORS")
    print("=" * 40)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup pins
    for box_num, config in BOX_CONFIG.items():
        GPIO.setup(config['ultrasonic_trigger'], GPIO.OUT)
        GPIO.setup(config['ultrasonic_echo'], GPIO.IN)
        GPIO.output(config['ultrasonic_trigger'], False)
    
    print("🔍 Taking 5 measurements for each sensor...")
    print("Place an object in front of sensors to test detection")
    print()
    
    for box_num in BOX_CONFIG:
        print(f"📦 Box {box_num}:")
        measurements = []
        
        for i in range(5):
            distance = measure_distance(box_num)
            if distance is not None:
                measurements.append(distance)
                status = "📦 PRESENT" if distance < OCCUPIED_DISTANCE_CM else "🔄 EMPTY"
                print(f"  Measurement {i+1}: {distance:.1f}cm - {status}")
            else:
                print(f"  Measurement {i+1}: ❌ FAILED")
            time.sleep(0.5)
        
        if measurements:
            avg_distance = sum(measurements) / len(measurements)
            print(f"  📊 Average: {avg_distance:.1f}cm")
        print()
    
    print("=" * 40)
    print("🎯 ULTRASONIC TEST COMPLETE")
    GPIO.cleanup()

if __name__ == "__main__":
    test_ultrasonic_sensors()