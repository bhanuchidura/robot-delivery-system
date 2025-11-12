# test_system.py - Place this in the main project folder (same level as src folder)
import sys
import os

# Add the src folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from robot_controller import RobotController

if __name__ == "__main__":
    print("Testing Robot Delivery System...")
    robot = RobotController()
    
    try:
        robot.start()
    except KeyboardInterrupt:
        print("Test interrupted")
    except Exception as e:
        print(f"Test error: {e}")
    finally:
        robot.stop()