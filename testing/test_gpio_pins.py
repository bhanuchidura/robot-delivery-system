# testing/test_gpio_pins.py
import RPi.GPIO as GPIO
import time
from config import BOX_CONFIG

def test_gpio_pins():
    print("🔧 TESTING GPIO PINS")
    print("=" * 40)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Test each pin configuration
    for box_num, config in BOX_CONFIG.items():
        print(f"\n📦 Testing Box {box_num}:")
        
        # Test lock pin
        try:
            GPIO.setup(config['lock_pin'], GPIO.OUT)
            GPIO.output(config['lock_pin'], GPIO.LOW)
            print(f"  ✅ Lock Pin GPIO{config['lock_pin']} - OK")
        except Exception as e:
            print(f"  ❌ Lock Pin GPIO{config['lock_pin']} - FAILED: {e}")
        
        # Test trigger pin
        try:
            GPIO.setup(config['ultrasonic_trigger'], GPIO.OUT)
            GPIO.output(config['ultrasonic_trigger'], GPIO.LOW)
            print(f"  ✅ Trigger Pin GPIO{config['ultrasonic_trigger']} - OK")
        except Exception as e:
            print(f"  ❌ Trigger Pin GPIO{config['ultrasonic_trigger']} - FAILED: {e}")
        
        # Test echo pin
        try:
            GPIO.setup(config['ultrasonic_echo'], GPIO.IN)
            state = GPIO.input(config['ultrasonic_echo'])
            print(f"  ✅ Echo Pin GPIO{config['ultrasonic_echo']} - OK (State: {state})")
        except Exception as e:
            print(f"  ❌ Echo Pin GPIO{config['ultrasonic_echo']} - FAILED: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 GPIO TEST COMPLETE")
    GPIO.cleanup()

if __name__ == "__main__":
    test_gpio_pins()