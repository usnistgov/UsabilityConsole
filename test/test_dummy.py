import unittest


# def setUpModule():
#     print("setUpModule()")
#
#
# def tearDownModule():
#     print("tearDownModule()")

class DummyTest(unittest.TestCase):
    # once per class
    @classmethod
    def setUpClass(cls):
        print("setUpClass()")

    # once per class
    @classmethod
    def tearDownClass(cls):
        print("tearDownClass()")

    # once per test
    def setUp(self):
        print("setUp()")

    # once per test
    def tearDown(self):
        print("tearDown()")

    def test_dummy(self):
        print("test_dummy()")
        self.assertTrue(True)

    def test_dummy2(self):
        print("test_dummy2()")
        self.assertTrue(True)
