import unittest
from hqc_py.GF2 import GF2

class TestGF2(unittest.TestCase):
    def test_addition(self):
        a = GF2(4, 0b1010)
        b = GF2(4, 0b1100)
        c = a + b
        self.assertEqual(c.tolist(), [1, 2])

    def test_multiplication(self):
        a = GF2(4, 0b1010)
        b = GF2(4, 0b1100)
        c = a * b
        self.assertEqual(c.tolist(), [0, 1, 2, 3])
        c = b * a
        self.assertEqual(c.tolist(), [0, 1, 2, 3])

    def test_equality(self):
        a = GF2(4, 0b1010)
        b = GF2(4, 0b1010)
        self.assertTrue(a == b)
        b = GF2(4, 0b1100)
        self.assertFalse(a == b)

    def test_lshift(self):
        a = GF2(4, 0b1010)
        self.assertEqual((a << 1).tolist(), [0, 2])

    def test_tolist(self):
        a = GF2(4, 0b1010)
        self.assertEqual(a.tolist(), [1, 3])