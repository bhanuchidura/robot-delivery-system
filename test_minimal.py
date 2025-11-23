# test_minimal.py - Absolute simplest test
import time
import gpiozero

print("🤖 MINIMAL GPIO TEST")
print("=" * 30)

try:
    # Reset GPIO first
    print("Resetting GPIO...")
    gpiozero.Device.pin_factory.reset()
    
    # Test ONE device at a time
    print("Testing Trigger (GPIO23)...")
    trigger = gpiozero.DigitalOutputDevice(23)
    print("✅ Trigger OK")
    trigger.close()
    
    time.sleep(1)
    
    print("Testing Echo (GPIO24)...")
    echo = gpiozero.DigitalInputDevice(24)
    print("✅ Echo OK") 
    echo.close()
    
    time.sleep(1)
    
    print("Testing Lock (GPIO17)...")
    lock = gpiozero.OutputDevice(17, active_high=False)
    print("✅ Lock OK")
    lock.close()
    
    print("🎯 ALL GPIO PINS WORK!")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
