# test_gpio_simple.py - Test individual GPIO pins
from gpiozero import OutputDevice, DigitalInputDevice, DigitalOutputDevice
import time

print("🔧 TESTING GPIO PINS INDIVIDUALLY")
print("=" * 40)

# Test pins one by one
test_pins = [
    (17, "Lock 1"),
    (27, "Lock 2"), 
    (9, "Lock 3"),
    (23, "Trigger 1"),
    (22, "Trigger 2"),
    (11, "Trigger 3"),
    (24, "Echo 1"),
    (10, "Echo 2"),
    (5, "Echo 3")
]

for pin, name in test_pins:
    print(f"Testing {name} (GPIO{pin})...", end=" ")
    try:
        if "Lock" in name:
            device = OutputDevice(pin, active_high=False)
        elif "Trigger" in name:
            device = DigitalOutputDevice(pin)
        else:  # Echo
            device = DigitalInputDevice(pin)
        
        device.close()
        print("✅ OK")
    except Exception as e:
        print(f"❌ {e}")

print("🎯 GPIO test complete")
