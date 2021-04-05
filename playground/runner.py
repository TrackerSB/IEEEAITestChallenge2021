import unittest
from unittest.suite import TestSuite
from unittest.loader import TestLoader
from test_case_01 import TestCase01
from test_simulation import TestSimulation

if __name__ == "__main__":
    suite = TestSuite()
    loader = TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestCase01))
    suite.addTests(loader.loadTestsFromTestCase(TestSimulation))
    # run the suite
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
