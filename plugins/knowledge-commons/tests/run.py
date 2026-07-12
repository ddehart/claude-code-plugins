#!/usr/bin/env python3
"""Run the knowledge-commons test suite.

    python3 plugins/knowledge-commons/tests/run.py

No dependencies. Stdlib unittest, Python 3.9 floor. PyYAML, if it happens to be installed,
is used only as a differential oracle for the vendored parser -- never at runtime.
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    """Discover and run every test."""
    sys.path.insert(0, HERE)
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=HERE, top_level_dir=HERE)
    runner = unittest.TextTestRunner(verbosity=2)
    return 0 if runner.run(suite).wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
