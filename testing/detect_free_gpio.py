# testing/detect_free_gpio.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import RPi.GPIO as GPIO

def detect_free_gpio():
    print("🔍 DETECTING FREE GPIO PINS")
    print("=" * 50)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)  # Reduce warning noise
    
    # Common GPIO pins on Raspberry Pi (avoid power/reserved pins)
    all_gpio_pins = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
    
    free_pins = []
    busy_pins = []
    
    print("Testing GPIO pins for availability...")
    print()
    
    for pin in all_gpio_pins:
        try:
            # Try to set as output
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            
            # Try to set as input
            GPIO.setup(pin, GPIO.IN)
            state = GPIO.input(pin)
            
            # If we got here, pin is free
            free_pins.append(pin)
            print(f"GPIO{pin}: ✅ FREE")
            
        except Exception as e:
            busy_pins.append(pin)
            print(f"GPIO{pin}: ❌ BUSY - {str(e)[:50]}...")
        
        finally:
            try:
                GPIO.cleanup(pin)
            except:
                pass
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"✅ FREE Pins ({len(free_pins)}): {free_pins}")
    print(f"❌ BUSY Pins ({len(busy_pins)}): {busy_pins}")
    
    # Suggest new configuration
    if len(free_pins) >= 9:  # Need 9 pins for 3 boxes
        print("\n🎯 SUGGESTED NEW CONFIG:")
        suggested_config = {
            1: {
                'lock_pin': free_pins[0],
                'ultrasonic_trigger': free_pins[1],
                'ultrasonic_echo': free_pins[2]
            },
            2: {
                'lock_pin': free_pins[3],
                'ultrasonic_trigger': free_pins[4],
                'ultrasonic_echo': free_pins[5]
            },
            3: {
                'lock_pin': free_pins[6],
                'ultrasonic_trigger': free_pins[7],
                'ultrasonic_echo': free_pins[8]
            }
        }
        print("Update your config.py with these pins:")
        for box_num, pins in suggested_config.items():
            print(f"  Box {box_num}: Lock={pins['lock_pin']}, Trigger={pins['ultrasonic_trigger']}, Echo={pins['ultrasonic_echo']}")
    
    GPIO.cleanup()
    return free_pins, busy_pins

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("❌ Run with sudo for accurate detection!")
        print("sudo python3 detect_free_gpio.py")
    else:
        detect_free_gpio()
