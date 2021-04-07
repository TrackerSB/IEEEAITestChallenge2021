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
    NOTE Using buffer=False and failfast=True together ensures that any exception occurring during test runs is printed
    to stderr immediately instead of being hold back until all test cases finished.
    However at least failfast has to be disabled if test cases contain tests that are expected to fail.
    """
    runner = TextTestRunner(failfast=True, buffer=False, verbosity=2)
    runner.run(suite)
