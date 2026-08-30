import unittest

from hqc_py.fft import FFT
from hqc_py.GF2m import GF2m

class TestFFT(unittest.TestCase):
    def test_compute_fft_betas_m8(self):
        fft = FFT()
        expected = [128, 64, 32, 16, 8, 4, 2]
        self.assertEqual(fft.betas, expected)

    def test_compute_subset_sums(self):
        fft = FFT()
        expected = [0, 128, 64, 192, 32, 160, 96, 224, \
                    16, 144, 80, 208, 48, 176, 112, 240, \
                    8, 136, 72, 200, 40, 168, 104, 232, \
                    24, 152, 88, 216, 56, 184, 120, 248, \
                    4, 132, 68, 196, 36, 164, 100, 228, \
                    20, 148, 84, 212, 52, 180, 116, 244, \
                    12, 140, 76, 204, 44, 172, 108, 236, \
                    28, 156, 92, 220, 60, 188, 124, 252, \
                    2, 130, 66, 194, 34, 162, 98, 226, \
                    18, 146, 82, 210, 50, 178, 114, 242, \
                    10, 138, 74, 202, 42, 170, 106, 234, \
                    26, 154, 90, 218, 58, 186, 122, 250, \
                    6, 134, 70, 198, 38, 166, 102, 230, \
                    22, 150, 86, 214, 54, 182, 118, 246, \
                    14, 142, 78, 206, 46, 174, 110, 238, \
                    30, 158, 94, 222, 62, 190, 126, 254]
        self.assertEqual(fft.betas_sums, expected)

    def test_radix_level_2(self):
        fft = FFT()
        f = list(map(lambda v: GF2m(v), [11, 22, 33, 44]))
        f0, f1 = fft.radix(f, 2)
        self.assertEqual(f0, [GF2m(11), GF2m(33) + GF2m(44)])
        self.assertEqual(f1, [GF2m(22) + GF2m(33) + GF2m(44), GF2m(44)])

    def test_fft_constant(self):
        fft = FFT(4)
        f = [GF2m(42)] + [GF2m(0)] * ((1 << 4) - 1)
        w = fft.fft(f, 1)
        self.assertEqual(w, [GF2m(42)] * (1 << GF2m.m))

if __name__ == '__main__':
    unittest.main()