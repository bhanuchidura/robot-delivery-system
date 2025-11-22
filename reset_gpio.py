# reset_gpio.py - Force reset all GPIO
import os
import time

print("🔄 RESETTING GPIO BUSY STATE")

# 1. Kill all Python processes
print("1. Killing Python processes...")
os.system('sudo pkill -f python3')
time.sleep(2)

# 2. Clean GPIO via sysfs
print("2. Cleaning GPIO pins...")
for pin in range(0, 40):
    try:
        with open('/sys/class/gpio/unexport', 'w') as f:
            f.write(str(pin))
    except:
        pass

# 3. Use gpio command if available
print("3. Using gpio command...")
os.system('sudo gpio cleanup 2>/dev/null')

# 4. Wait
print("4. Waiting for cleanup...")
time.sleep(3)

print("✅ GPIO RESET COMPLETE")
