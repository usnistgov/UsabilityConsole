import unittest


def setUpModule():
    print("2.setUpModule()")


def tearDownModule():
    print("2.tearDownModule()")

class DummyTest2(unittest.TestCase):
    # once per class
    @classmethod
    def setUpClass(cls):
        print("2.setUpClass()")

    # once per class
    @classmethod
    def tearDownClass(cls):
        print("2.tearDownClass()")

    # once per test
    def setUp(self):
        print("2.setUp()")

    # once per test
    def tearDown(self):
        print("2.tearDown()")

    def test_dummy(self):
        print("2.test_dummy()")
        self.assertTrue(True)

    def test_dummy2(self):
        print("2.test_dummy2()")
        self.assertTrue(True)
