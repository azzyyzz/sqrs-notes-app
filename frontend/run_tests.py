import os
import sys
import unittest
import coverage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

cov = coverage.Coverage(
    data_file='.coverage',
    include=['app.py'],
    omit=['*/tests/*', '*/__pycache__/*'],
)

cov.start()

from tests.test_auth import TestAuth
from tests.test_notes import TestNotes
from tests.test_utils import TestUtils


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAuth))
    suite.addTest(unittest.makeSuite(TestNotes))
    suite.addTest(unittest.makeSuite(TestUtils))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite())

    cov.stop()
    cov.save()

    print("\nCoverage Report:")
    try:
        cov.report()
    except Exception as e:
        print(f"Error generating coverage report: {e}")

    sys.exit(not result.wasSuccessful())