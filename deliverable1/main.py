from unittest import TextTestRunner
from unittest.suite import TestSuite
from unittest.loader import TestLoader
from test_case_01 import TestCase01
from test_case_06 import TestCase06
from test_simulation import TestSimulation

if __name__ == "__main__":
    suite = TestSuite()
    loader = TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestCase01))
    suite.addTests(loader.loadTestsFromTestCase(TestCase06))

    # run the suite
    """
    NOTE buffer=False ensure that any error occurring during test runs is printed to stderr immediately instead of
    being printed after all test cases finished.
    """
    runner = TextTestRunner(buffer=False, verbosity=2)
    runner.run(suite)
