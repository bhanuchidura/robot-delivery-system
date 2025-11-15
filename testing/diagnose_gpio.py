# testing/diagnose_gpio.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import RPi.GPIO as GPIO
from config import BOX_CONFIG

def diagnose_gpio():
    print("🔍 GPIO DIAGNOSTIC TOOL")
    print("=" * 50)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(True)  # Enable warnings to see issues
    
    print("Checking GPIO pins configuration...")
    
    for box_num, config in BOX_CONFIG.items():
        print(f"\n📦 Box {box_num} Configuration:")
        print(f"  Lock Pin: GPIO{config['lock_pin']}")
        print(f"  Trigger: GPIO{config['ultrasonic_trigger']}")
        print(f"  Echo: GPIO{config['ultrasonic_echo']}")
        
        # Test each pin
        pins_to_test = [
            ('Lock', config['lock_pin']),
            ('Trigger', config['ultrasonic_trigger']),
            ('Echo', config['ultrasonic_echo'])
        ]
        
        for pin_name, pin_number in pins_to_test:
            try:
                print(f"  Testing {pin_name} (GPIO{pin_number})...")
                
                # Try to set as output first
                GPIO.setup(pin_number, GPIO.OUT)
                GPIO.output(pin_number, GPIO.LOW)
                print(f"    ✅ Can set as OUTPUT")
                
                # Clean up and try as input
                GPIO.cleanup(pin_number)
                GPIO.setup(pin_number, GPIO.IN)
                state = GPIO.input(pin_number)
                print(f"    ✅ Can set as INPUT (State: {state})")
                
                GPIO.cleanup(pin_number)
                
            except Exception as e:
                print(f"    ❌ GPIO{pin_number} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 Checking for conflicting pins...")
    
    # Check if any pins are used multiple times
    all_pins = []
    for config in BOX_CONFIG.values():
        all_pins.extend([config['lock_pin'], config['ultrasonic_trigger'], config['ultrasonic_echo']])
    
    duplicate_pins = set([x for x in all_pins if all_pins.count(x) > 1])
    if duplicate_pins:
        print(f"❌ DUPLICATE PINS FOUND: {duplicate_pins}")
    else:
        print("✅ No duplicate pins")
    
    GPIO.cleanup()
    print("🎯 DIAGNOSTIC COMPLETE")

if __name__ == "__main__":
    diagnose_gpio()