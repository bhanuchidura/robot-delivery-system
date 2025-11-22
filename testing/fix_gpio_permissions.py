# testing/fix_gpio_permissions.py
import os
import subprocess

def fix_gpio_permissions():
    print("🔧 FIXING GPIO PERMISSIONS")
    print("=" * 50)
    
    current_user = subprocess.getoutput('whoami')
    print(f"Current user: {current_user}")
    
    # Check if user is in GPIO group
    groups = subprocess.getoutput('groups')
    print(f"Current groups: {groups}")
    
    if 'gpio' not in groups:
        print(f"\n❌ User '{current_user}' is not in 'gpio' group")
        print("Adding user to gpio group...")
        
        # Try to add user to gpio group
        try:
            os.system(f'sudo usermod -a -G gpio {current_user}')
            print("✅ User added to gpio group")
            print("🔁 Please LOGOUT and LOGIN again, or RESTART your Pi")
            return False
        except Exception as e:
            print(f"❌ Failed to add to gpio group: {e}")
            return False
    else:
        print("✅ User is already in gpio group")
    
    # Check GPIO device permissions
    print("\n📁 Checking GPIO device permissions:")
    gpio_devices = subprocess.getoutput('ls -la /dev/gpiochip*')
    print(gpio_devices)
    
    # Check if we can access /sys/class/gpio
    print("\n🔍 Checking /sys/class/gpio access:")
    if os.path.exists('/sys/class/gpio'):
        export_status = subprocess.getoutput('ls -la /sys/class/gpio/')
        print(export_status)
    else:
        print("❌ /sys/class/gpio not found")
    
    print("\n" + "=" * 50)
    print("If permissions are still not working, try:")
    print("1. sudo reboot")
    print("2. Or run scripts with: sudo python3 script.py")
    
    return True

if __name__ == "__main__":
    fix_gpio_permissions()
