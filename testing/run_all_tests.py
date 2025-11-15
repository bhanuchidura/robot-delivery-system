# testing/run_all_tests.py
import sys
import os
import time

# Add src to path to import config and managers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_all_tests():
    print("🚀 RUNNING COMPLETE TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("GPIO Pins", "test_gpio_pins.py"),
        ("Ultrasonic Sensors", "test_ultrasonic.py"), 
        ("Solenoid Locks", "test_locks.py"),
        ("Firebase Connection", "test_firebase.py"),
        ("All Sensors", "test_all_sensors.py")
    ]
    
    results = []
    
    for test_name, test_file in tests:
        print(f"\n🎯 RUNNING: {test_name}")
        print("-" * 30)
        
        try:
            # Import and run the test module
            module_name = test_file.replace('.py', '')
            module = __import__(module_name)
            
            # Get the test function (assuming it's named test_* or the module name)
            test_func = getattr(module, f"test_{module_name}", None)
            if not test_func:
                test_func = getattr(module, module_name, None)
            
            if test_func and callable(test_func):
                success = test_func()
                results.append((test_name, success))
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"   {status} - {test_name}")
            else:
                print(f"   ❌ SKIP - No test function found in {test_file}")
                results.append((test_name, False))
                
        except Exception as e:
            print(f"   ❌ ERROR - {test_name}: {e}")
            results.append((test_name, False))
        
        time.sleep(1)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🚀 ALL TESTS PASSED! Your system is ready.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")

if __name__ == "__main__":
    run_all_tests()