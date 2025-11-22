# src/real_sensor_manager_simple.py - Pure gpiozero version
import time
from gpiozero import OutputDevice, DigitalInputDevice, DigitalOutputDevice
from config import BOX_CONFIG, OCCUPIED_DISTANCE_CM

class RealSensorManager:
    def __init__(self):
        self.box_status = {}
        self.locks = {}
        self.triggers = {}
        self.echos = {}
        self.last_occupancy_status = {}  # Track previous states for change detection
        self.setup_sensors()
        
    def setup_sensors(self):
        print("🔧 REAL HARDWARE: Setting up with gpiozero only...")
        
        # Clean up any existing devices first
        self.cleanup_existing()
        
        for box_num, config in BOX_CONFIG.items():
            try:
                # Setup lock control
                self.locks[box_num] = OutputDevice(
                    config['lock_pin'], 
                    active_high=False, 
                    initial_value=False
                )
                
                # Setup ultrasonic sensor pins
                self.triggers[box_num] = DigitalOutputDevice(config['ultrasonic_trigger'])
                self.echos[box_num] = DigitalInputDevice(config['ultrasonic_echo'])
                
                # Initialize status
                self.box_status[box_num] = {
                    'is_open': False,
                    'is_occupied': False,
                    'distance': 100.0,
                    'last_checked': time.time()
                }
                
                # Track previous occupancy for change detection
                self.last_occupancy_status[box_num] = False
                
                print(f"✅ Box {box_num} - Lock:GPIO{config['lock_pin']}")
                
            except Exception as e:
                print(f"❌ Box {box_num} setup failed: {e}")
                raise
        
        print("✅ All REAL hardware initialized!")
    
    def cleanup_existing(self):
        """Clean up any existing GPIO devices"""
        print("🧹 Cleaning up existing GPIO devices...")
        # Close any existing devices
        devices = [self.locks, self.triggers, self.echos]
        for device_dict in devices:
            for pin, device in list(device_dict.items()):
                try:
                    device.close()
                except:
                    pass
            device_dict.clear()
    
    def measure_distance(self, box_num):
        """Measure distance using pure gpiozero"""
        if box_num not in self.triggers or box_num not in self.echos:
            return 100.0
            
        try:
            trigger = self.triggers[box_num]
            echo = self.echos[box_num]
            
            # Ensure trigger starts low
            trigger.off()
            time.sleep(0.0005)
            
            # Send trigger pulse
            trigger.on()
            time.sleep(0.00001)
            trigger.off()
            
            pulse_start = time.time()
            pulse_end = time.time()
            
            # Wait for echo to go HIGH (with timeout)
            timeout_start = time.time()
            while not echo.is_active:
                pulse_start = time.time()
                if time.time() - timeout_start > 0.1:
                    return 100.0
            
            # Wait for echo to go LOW (with timeout)
            timeout_start = time.time()
            while echo.is_active:
                pulse_end = time.time()
                if time.time() - timeout_start > 0.1:
                    return 100.0
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = (pulse_duration * 34300) / 2
            
            # Filter unrealistic values
            if distance < 0.5 or distance > 400:
                return 100.0
                
            return distance
            
        except Exception as e:
            print(f"❌ Sensor error Box {box_num}: {e}")
            return 100.0
    
    def check_all_sensors(self):
        """Check all sensors and detect occupancy changes"""
        print("🔍 Checking REAL sensors...")
        
        status_changed = False
        current_time = time.time()
        
        for box_num in self.box_status:
            distance = self.measure_distance(box_num)
            
            # Determine occupancy: < OCCUPIED_DISTANCE_CM = package present
            is_occupied = distance < OCCUPIED_DISTANCE_CM
            
            # Check if occupancy status changed
            old_occupied = self.last_occupancy_status[box_num]
            occupancy_changed = (is_occupied != old_occupied)
            
            if occupancy_changed:
                status_changed = True
                self.last_occupancy_status[box_num] = is_occupied
                print(f"🔄 Box {box_num} occupancy CHANGED: {old_occupied} → {is_occupied}")
            
            # Always update current status
            self.box_status[box_num]['distance'] = distance
            self.box_status[box_num]['is_occupied'] = is_occupied
            self.box_status[box_num]['last_checked'] = current_time
            
            status = "📦 PRESENT" if is_occupied else "🔄 EMPTY"
            change_indicator = " (CHANGED)" if occupancy_changed else ""
            print(f"Box {box_num}: {distance:.1f}cm → {status}{change_indicator}")
        
        return self.box_status, status_changed
    
    def open_box(self, box_num):
        """Physically open the box"""
        if box_num in self.locks:
            self.locks[box_num].on()  # Energize solenoid
            self.box_status[box_num]['is_open'] = True
            print(f"🔓 Box {box_num} OPENED")
            return True
        return False
    
    def close_box(self, box_num):
        """Physically close the box"""
        if box_num in self.locks:
            self.locks[box_num].off()  # De-energize solenoid
            self.box_status[box_num]['is_open'] = False
            print(f"🔒 Box {box_num} CLOSED")
            return True
        return False
    
    def open_all_boxes(self):
        """Open all boxes"""
        print("🚪 Opening ALL boxes...")
        for box_num in self.locks:
            self.open_box(box_num)
        print("✅ All boxes OPEN")
    
    def close_all_boxes(self):
        """Close all boxes"""
        print("🔒 Closing ALL boxes...")
        for box_num in self.locks:
            self.close_box(box_num)
        print("✅ All boxes CLOSED")
    
    def get_status(self):
        """Get current box status"""
        return self.box_status
    
    def cleanup(self):
        """Safe hardware cleanup"""
        print("🧹 Cleaning up hardware...")
        self.close_all_boxes()  # Ensure all locks are closed
        
        # Close all gpiozero devices
        for device_dict in [self.locks, self.triggers, self.echos]:
            for device in device_dict.values():
                try:
                    device.close()
                except:
                    pass
        
        print("🧹 Hardware cleanup complete")
