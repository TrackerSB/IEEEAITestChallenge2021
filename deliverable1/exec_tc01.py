from unittest import TextTestRunner
from unittest.suite import TestSuite
from unittest.loader import TestLoader
from test_case_01 import TestCase01

if __name__ == "__main__":
    suite = TestSuite()
    loader = TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestCase01))

    # run the suite
    debug_enabled = False
    if debug_enabled:
        """
        NOTE Using buffer=False and failfast=True together ensures that any exception occurring during test runs is printed
        to stderr immediately instead of being hold back until all test cases finished.
        However at least failfast has to be disabled if test cases contain tests that are expected to fail.
        """
        failfast = True
        buffer = False
    else:
        failfast = False
        buffer = True
    runner = TextTestRunner(failfast=failfast, buffer=buffer, verbosity=2)
    runner.run(suite)

