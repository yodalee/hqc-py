import unittest

from hqc_py.default_parameters import DEFAULT_PARAMETERS
from hqc_py.reed_muller import ReedMuller

class TestReedMuller(unittest.TestCase):
    def test_encode1b_zero(self):
        rm1 = ReedMuller(n_repeat = 3, param_n1 = 1)
        m = b'\x00'
        encoded = rm1.encode_1byte(m)
        self.assertEqual(encoded, b'\x00' * 16)

    def test_encode1b_ff(self):
        rm1 = ReedMuller(n_repeat = 3, param_n1 = 1)
        m = b'\xff'
        encoded = rm1.encode_1byte(m)
        golden = bytes.fromhex("69969669966969969669699669969669")
        self.assertEqual(encoded, golden)

    def test_encode1b(self):
        rm1 = ReedMuller(n_repeat = 3, param_n1 = 2)
        m = b'\x8b\xf4'
        encoded = rm1.encode(m)
        golden = bytes.fromhex(
            "99669966996699669966996699669966" * 3 +  \
            "0f0ff0f0f0f00f0ff0f00f0f0f0ff0f0" * 3)
        self.assertEqual(encoded, golden)

    def test_decode1b_zero(self):
        rm1 = ReedMuller(n_repeat = 3, param_n1 = 1)
        m = b'\x00'
        encoded = rm1.encode(m)
        decoded = rm1.decode(encoded)
        self.assertEqual(decoded, m)

    def test_decode1b_ff(self):
        rm1 = ReedMuller(n_repeat = 3, param_n1 = 1)
        m = b'\xff'
        encoded = rm1.encode(m)
        decoded = rm1.decode(encoded)
        self.assertEqual(decoded, m)

    def test_decode1b(self):
        rm1 = ReedMuller(n_repeat = 3, param_n1 = 2)
        m = b'\x8b\xf4'
        encoded = rm1.encode(m)
        decoded = rm1.decode(encoded)
        self.assertEqual(decoded, m)

    def test_decode1b_with_error(self):
        rm1 = ReedMuller(n_repeat = 3, param_n1 = 2)
        m = b'\x8b\xf4'
        golden = bytearray(rm1.encode(m))
        # introduce a 1-bit error
        golden[0] ^= 0x01
        decoded = rm1.decode(bytes(golden))
        self.assertEqual(decoded, m)

    def test_decode1b_with_error2(self):
        rm1 = ReedMuller(n_repeat = 3, param_n1 = 2)
        m = b'\x8b\xf4'
        golden = bytearray(rm1.encode(m))
        # introduce a 2-bit error
        golden[0] ^= 0x01
        golden[1] ^= 0x01
        decoded = rm1.decode(bytes(golden))
        self.assertEqual(decoded, m)

    def test_decode1b_with_31bit_errors(self):
        """This is the maximum number of errors that can be corrected for n_repeat=1, param_n1=1."""
        rm1 = ReedMuller(n_repeat=1, param_n1=1)
        m = b'\x8b'
        golden = bytearray(rm1.encode(m))

        # Introduce 31-bit errors
        for i in range(31):
            golden[i % len(golden)] ^= (1 << (i % 8))

        decoded = rm1.decode(bytes(golden))
        self.assertEqual(decoded, m)

if __name__ == '__main__':
    unittest.main()