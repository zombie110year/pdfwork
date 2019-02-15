import unittest as t
from .test_merge import TestParser, TestMergePDF

loader = t.TestLoader()
runner = t.TextTestRunner(verbosity=2)

suite = loader.loadTestsFromTestCase(TestParser)
suite.addTest(
    loader.loadTestsFromTestCase(TestMergePDF)
)

runner.run(suite)