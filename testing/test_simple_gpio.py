# testing/test_simple_gpio.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import RPi.GPIO as GPIO
from config import BOX_CONFIG

def test_simple_gpio():
    print("🔧 SIMPLE GPIO TEST")
    print("=" * 40)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(True)
    
    print("Testing basic GPIO functionality...")
    
    # Test only a few common pins to avoid conflicts
    test_pins = [17, 27, 22, 23, 24, 10, 9, 11, 5]
    
    for pin in test_pins:
        try:
            print(f"Testing GPIO{pin}...", end=" ")
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            GPIO.cleanup(pin)
            print("✅ OK")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print("\n" + "=" * 40)
    print("Now testing your configured pins...")
    
    for box_num, config in BOX_CONFIG.items():
        print(f"\n📦 Box {box_num}:")
        for pin_name, pin_number in [('Lock', config['lock_pin']), 
                                   ('Trigger', config['ultrasonic_trigger']), 
                                   ('Echo', config['ultrasonic_echo'])]:
            try:
                GPIO.setup(pin_number, GPIO.OUT)
                GPIO.output(pin_number, GPIO.LOW)
                GPIO.cleanup(pin_number)
                print(f"  {pin_name} GPIO{pin_number} ✅ OK")
            except Exception as e:
                print(f"  {pin_name} GPIO{pin_number} ❌ FAILED: {e}")
    
    GPIO.cleanup()
    print("\n🎯 SIMPLE GPIO TEST COMPLETE")

if __name__ == "__main__":
    test_simple_gpio()