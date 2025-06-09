"""
Main test runner for the Pepper Robot and Flask Server integration system.
This script discovers and runs all tests in the test directory.
"""

import unittest
import sys
import os

def run_all_tests():
    """
    Discover and run all tests in the test directory.
    
    Returns:
        True if all tests pass, False otherwise
    """
    # Get the directory containing this script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Discover all tests in the test directory
    test_suite = unittest.defaultTestLoader.discover(test_dir, pattern="test_*.py")
    
    # Create a test runner
    test_runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = test_runner.run(test_suite)
    
    # Return True if all tests pass, False otherwise
    return result.wasSuccessful()

def run_specific_test(test_name):
    """
    Run a specific test module.
    
    Args:
        test_name: Name of the test module to run (without .py extension)
        
    Returns:
        True if all tests pass, False otherwise
    """
    # Import the test module
    try:
        test_module = __import__(test_name)
    except ImportError:
        print(f"Error: Test module '{test_name}' not found.")
        return False
    
    # Create a test suite from the module
    test_suite = unittest.defaultTestLoader.loadTestsFromModule(test_module)
    
    # Create a test runner
    test_runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = test_runner.run(test_suite)
    
    # Return True if all tests pass, False otherwise
    return result.wasSuccessful()

if __name__ == "__main__":
    # Check if a specific test was requested
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Run all tests
        success = run_all_tests()
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)