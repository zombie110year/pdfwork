import unittest as t
from .test_merge import TestParser

loader = t.TestLoader()
runner = t.TextTestRunner(verbosity=2)

suite = loader.loadTestsFromTestCase(TestParser)

runner.run(suite)