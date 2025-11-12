# run_robot.py - Place this in the main project folder
import sys
import os

# Add the src folder to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Starting Robot Delivery System...")

try:
    from robot_controller import RobotController
    
    robot = RobotController()
    robot.start()
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all files are in the correct locations")
except KeyboardInterrupt:
    print("System stopped by user")
except Exception as e:
    print(f"Error: {e}")