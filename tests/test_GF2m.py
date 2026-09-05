import unittest
from hqc_py.GF2m import GF2m

class TestGF2m(unittest.TestCase):
    def test_equality_with_gf2m(self):
        self.assertTrue(GF2m(42) == GF2m(42))
        self.assertFalse(GF2m(42) == GF2m(43))

    def test_equality_with_int(self):
        self.assertTrue(GF2m(42) == 42)
        self.assertFalse(GF2m(42) == 41)

    def test_hash_consistency_with_equality(self):
        self.assertEqual(hash(GF2m(42)), hash(GF2m(42)))
        self.assertEqual(len({GF2m(42), GF2m(42), GF2m(43)}), 2)

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

    def test_square(self):
        values = [0, 1, 2, 3, 7, 31, 127, 255]
        for value in values:
            a = GF2m(value)
            self.assertEqual(a.square().bits, (a * a).bits)

    def test_inverse(self):
        values = [1, 2, 3, 5, 7, 13, 31, 127, 255]
        for value in values:
            a = GF2m(value)
            inv = a.inverse()
            self.assertEqual((a * inv).bits, 1)
            self.assertEqual((inv * a).bits, 1)

    def test_zero_inverse(self):
        self.assertEqual(GF2m(0).inverse(), GF2m(0))