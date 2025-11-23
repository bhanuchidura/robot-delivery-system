# find_arduino.py - Detect Arduino port
import serial.tools.list_ports
import time

print("🔍 SEARCHING FOR ARDUINO...")
print("=" * 40)

# List all available ports
ports = list(serial.tools.list_ports.comports())
print(f"Found {len(ports)} serial ports:")

for port in ports:
    print(f"  📍 {port.device} - {port.description}")

print("\n🔌 Testing each port...")
print("=" * 40)

for port in ports:
    print(f"Testing {port.device}...", end=" ")
    try:
        ser = serial.Serial(port.device, 9600, timeout=2)
        time.sleep(2)  # Wait for Arduino reset
        
        # Send test command
        ser.write(b"PING\n")
        time.sleep(0.5)
        
        # Read response
        response = ser.read_all().decode().strip()
        
        if response:
            print(f"✅ RESPONSE: '{response}'")
            if "ARDUINO_READY" in response or "PONG" in response:
                print(f"🎯 FOUND ARDUINO ON: {port.device}")
        else:
            print("❌ No response")
            
        ser.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
