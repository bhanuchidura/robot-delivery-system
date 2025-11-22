# test_ultrasonic.py - Test ultrasonic sensor with current GPIO pins
from gpiozero import DigitalInputDevice, DigitalOutputDevice
import time

print("🔊 TESTING ULTRASONIC SENSOR")
print("=" * 50)

# Current GPIO pins from your config
TRIG_PIN = 23  # GPIO5 - Physical Pin 29
ECHO_PIN = 24  # GPIO6 - Physical Pin 31

try:
    # Setup pins
    trigger = DigitalOutputDevice(TRIG_PIN)
    echo = DigitalInputDevice(ECHO_PIN)
    
    print(f"✅ Sensor connected:")
    print(f"   TRIG: GPIO{TRIG_PIN} (Pin 29)")
    print(f"   ECHO: GPIO{ECHO_PIN} (Pin 31)")
    print(f"   VCC: 5V (Pin 2)")
    print(f"   GND: GND (Pin 6)")
    print()
    
    def measure_distance():
        # Ensure trigger starts low
        trigger.off()
        time.sleep(0.0005)
        
        # Send 10μs pulse
        trigger.on()
        time.sleep(0.00001)  # 10 microseconds
        trigger.off()
        
        pulse_start = time.time()
        pulse_end = time.time()
        
        # Wait for echo to go HIGH (with timeout)
        timeout_start = time.time()
        while not echo.is_active:
            pulse_start = time.time()
            if time.time() - timeout_start > 0.1:
                return None  # Timeout
        
        # Wait for echo to go LOW (with timeout)
        timeout_start = time.time()
        while echo.is_active:
            pulse_end = time.time()
            if time.time() - timeout_start > 0.1:
                return None  # Timeout
        
        # Calculate distance in cm
        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration * 34300) / 2  # Speed of sound
        
        # Validate reading
        if 0.5 <= distance <= 400:
            return distance
        else:
            return None
    
    print("📏 Taking 10 distance measurements...")
    print("   Place your hand in front of the sensor to test")
    print()
    
    successful_readings = 0
    
    for i in range(10):
        distance = measure_distance()
        
        if distance is not None:
            successful_readings += 1
            if distance < 2.0:
                status = "📦 PACKAGE DETECTED"
            elif distance < 10.0:
                status = "👋 HAND CLOSE"
            elif distance < 30.0:
                status = "🖐️ HAND NEAR"
            else:
                status = "🔄 EMPTY"
            
            print(f"   {i+1:2d}. {distance:5.1f} cm - {status}")
        else:
            print(f"   {i+1:2d}. ❌ NO READING")
        
        time.sleep(1)  # Wait 1 second between measurements
    
    print()
    print("=" * 50)
    print(f"📊 RESULTS: {successful_readings}/10 successful readings")
    
    if successful_readings >= 8:
        print("✅ ULTRASONIC SENSOR IS WORKING PERFECTLY!")
    elif successful_readings >= 5:
        print("⚠️  Sensor is working but has some issues")
    else:
        print("❌ Sensor has problems - check wiring")
    
    # Close devices
    trigger.close()
    echo.close()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("Check your wiring:")
    print("  - VCC to 5V (Pin 2)")
    print("  - GND to GND (Pin 6)") 
    print("  - TRIG to GPIO5 (Pin 29)")
    print("  - ECHO to GPIO6 (Pin 31)")
