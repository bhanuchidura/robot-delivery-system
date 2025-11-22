# testing/test_gpio_pins_gpiozero.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gpiozero import OutputDevice, DigitalInputDevice, DigitalOutputDevice
from config import BOX_CONFIG

def test_gpio_pins_gpiozero():
    print("🔧 TESTING GPIO PINS")
    print("=" * 40)
    
    # Test only Box 1 to keep it simple
    box_num = 1
    config = BOX_CONFIG[box_num]
    
    print(f"📦 Testing Box {box_num} only:")
    
    try:
        # Test lock pin
        print(f"Testing Lock (GPIO{config['lock_pin']})...", end=" ")
        lock = OutputDevice(config['lock_pin'], active_high=False)
        lock.close()
        print("✅ OK")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    try:
        # Test trigger pin  
        print(f"Testing Trigger (GPIO{config['ultrasonic_trigger']})...", end=" ")
        trigger = DigitalOutputDevice(config['ultrasonic_trigger'])
        trigger.close()
        print("✅ OK")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    try:
        # Test echo pin
        print(f"Testing Echo (GPIO{config['ultrasonic_echo']})...", end=" ")
        echo = DigitalInputDevice(config['ultrasonic_echo'])
        echo.close()
        print("✅ OK")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    print("🎯 TEST COMPLETE")

if __name__ == "__main__":
    test_gpio_pins_gpiozero()
