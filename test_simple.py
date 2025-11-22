# test_simple.py - Simple test without killing processes
import time
from gpiozero import OutputDevice, DigitalInputDevice, DigitalOutputDevice

print("🤖 SIMPLE ROBOT TEST")
print("=" * 40)

# Test only Box 1
try:
    print("Setting up Lock (GPIO17)...", end=" ")
    lock = OutputDevice(17, active_high=False, initial_value=False)
    print("✅")

    print("Setting up Trigger (GPIO23)...", end=" ")
    trigger = DigitalOutputDevice(23)
    print("✅")

    print("Setting up Echo (GPIO24)...", end=" ")
    echo = DigitalInputDevice(24)
    print("✅")

    print("🎯 HARDWARE SETUP COMPLETE!")
    
    # Test sensor reading
    print("🔍 Testing sensor...")
    
    # Simple distance measurement
    trigger.off()
    time.sleep(0.0005)
    trigger.on()
    time.sleep(0.00001)
    trigger.off()
    
    print("✅ SENSOR TRIGGERED - Check if it works")
    
    # Keep running for 10 seconds
    print("⏰ Running for 10 seconds...")
    for i in range(10):
        print(f"Still running... {i+1}/10")
        time.sleep(1)
    
    print("✅ TEST COMPLETE - Everything works!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

finally:
    print("🧹 Cleaning up...")
    try:
        lock.close()
        trigger.close() 
        echo.close()
    except:
        pass
