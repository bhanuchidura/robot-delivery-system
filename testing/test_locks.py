# testing/test_locks.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time
from gpiozero import OutputDevice
from config import BOX_CONFIG, LOCK_ACTIVE_HIGH

def test_locks():
    print("🔓 TESTING SOLENOID LOCKS")
    print("=" * 40)
    print("⚠️  Make sure locks are connected to EXTERNAL POWER SUPPLY!")
    print("⚠️  Do not power locks directly from Raspberry Pi!")
    print()
    
    locks = {}
    
    try:
        # Initialize locks
        for box_num, config in BOX_CONFIG.items():
            locks[box_num] = OutputDevice(
                config['lock_pin'], 
                active_high=LOCK_ACTIVE_HIGH, 
                initial_value=False
            )
            print(f"🔧 Box {box_num} lock initialized on GPIO{config['lock_pin']}")
        
        input("Press Enter to start lock test...")
        
        # Test each lock individually
        for box_num in locks:
            print(f"\n🔓 Testing Box {box_num} lock:")
            
            # Open lock
            print(f"  Opening lock...")
            locks[box_num].on()
            time.sleep(2)  # Keep open for 2 seconds
            
            # Close lock
            print(f"  Closing lock...")
            locks[box_num].off()
            time.sleep(1)
            
            print(f"  ✅ Box {box_num} lock test complete")
        
        # Test all locks together
        print(f"\n🚪 Testing ALL locks together:")
        print("  Opening all locks...")
        for lock in locks.values():
            lock.on()
        time.sleep(3)
        
        print("  Closing all locks...")
        for lock in locks.values():
            lock.off()
        time.sleep(1)
        
        print("  ✅ All locks test complete")
        
    except Exception as e:
        print(f"❌ Lock test failed: {e}")
    
    finally:
        # Cleanup - ensure all locks are closed
        print("\n🧹 Cleaning up...")
        for lock in locks.values():
            lock.off()
            lock.close()
        
        print("🎯 LOCK TEST COMPLETE")

if __name__ == "__main__":
    test_locks()