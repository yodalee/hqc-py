import unittest
from hqc_py.GF2m import GF2m

class TestGF2m(unittest.TestCase):
    def test_compute_gf_exp(self):
        from hqc_py.GF2m import GF2m
        # The value is not cared for this test
        computed = []
        val = GF2m(1)
        computed.append(int(val))
        for _ in range(257):
            val = val * GF2m(2)
            computed.append(int(val))
        self.assertEqual(computed, GF2m.gf_exp)

    def test_compute_gf_log(self):
        from hqc_py.GF2m import GF2m
        alpha = GF2m(1)
        computed = [0] * 256
        for i in range(255):
            computed[int(alpha)] = i
            alpha = alpha * GF2m(2)
        self.assertEqual(computed, GF2m.gf_log)

    def test_gfmul_small(self):
        a = GF2m(0b1010)
        b = GF2m(0b1100)
        c = a * b
        self.assertEqual(c.bits, 0b1111000)
        c = b * a
        self.assertEqual(c.bits, 0b1111000)

    def test_gfmul_real(self):
        # generated from test_kat_hqc_1
        # first 16 multiplication in reed_solomon_encode function
        a = 222
        bs = [89, 69, 153, 116, 176, 117, 111, 75, 73, 233, 242, 233, 65, 210, 21, 139]
        gs = [152, 24, 46, 101, 140, 187, 197, 88, 249, 20, 180, 20, 71, 118, 224, 238]

        for b, g in zip(bs, gs):
            c = GF2m(a) * GF2m(b)
            self.assertEqual(c.bits, g)

    def test_gfadd(self):
        a = GF2m(0b1010)
        b = GF2m(0b1100)
        c = a + b
        self.assertEqual(c.bits, 0b0110)