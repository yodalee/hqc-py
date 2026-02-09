import unittest

from hqc_py.default_parameters import DEFAULT_PARAMETERS
from hqc_py.reed_muller import ReedMuller

class TestReedMuller(unittest.TestCase):
    def test_encode1b_zero(self):
        rm1 = ReedMuller(n_repeat = 3)
        m = b'\x00'
        encoded = rm1.encode_1byte(m)
        self.assertEqual(encoded, b'\x00' * 16)

    def test_encode1b_ff(self):
        rm1 = ReedMuller(n_repeat = 3)
        m = b'\xff'
        encoded = rm1.encode_1byte(m)
        golden = bytes.fromhex("69969669966969969669699669969669")
        self.assertEqual(encoded, golden)

    def test_encode1b(self):
        rm1 = ReedMuller(n_repeat = 3)
        m = b'\x8b\xf4'
        encoded = rm1.encode(m)
        golden = bytes.fromhex(
            "99669966996699669966996699669966" * 3 +  \
            "0f0ff0f0f0f00f0ff0f00f0f0f0ff0f0" * 3)
        self.assertEqual(encoded, golden)

if __name__ == '__main__':
    unittest.main()