

# run_tests.py
"""Script to run all tests"""
import unittest
import sys

if __name__ == '__main__':
    # Discover and run all tests
    loader = unittest.TestLoader()
    tests = loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(tests)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


