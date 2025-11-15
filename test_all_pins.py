# test_all_pins.py - Test which pins are available
from gpiozero import OutputDevice, DigitalInputDevice, DigitalOutputDevice
import time

# Pins we want to use
test_pins = [17, 27, 9, 23, 22, 11, 24, 10, 5]

print("Testing GPIO pin availability...")

for pin in test_pins:
    try:
        # Test as output first
        device = OutputDevice(pin)
        print(f"✅ GPIO{pin} - Output OK")
        device.close()
        
        # Test as input
        input_dev = DigitalInputDevice(pin)
        print(f"✅ GPIO{pin} - Input OK") 
        input_dev.close()
        
    except Exception as e:
        print(f"❌ GPIO{pin} - Busy: {e}")

print("Pin test complete")
