import random
import unittest
from itertools import zip_longest

from hqc_py.default_parameters import DEFAULT_PARAMETERS
from hqc_py.reed_solomon import ReedSolomon
from hqc_py.GF2m import GF2m


def to_gf2m(values):
    return [GF2m(v) for v in values]

def equal_poly(poly1, poly2):
    """Check if two polynomials are equal, also check trailing zero"""
    for c0, c1 in zip_longest(poly1, poly2, fillvalue=GF2m(0)):
        if c0 != c1:
            return False
    return True

class TestReedSolomon(unittest.TestCase):
    def setUp(self):
        self.rs1 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-1"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-1"]["k"],
            generator_polynomial=DEFAULT_PARAMETERS["HQC-1"]["generator_polynomial"])
        self.rs3 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-3"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-3"]["k"],
            generator_polynomial=DEFAULT_PARAMETERS["HQC-3"]["generator_polynomial"])
        self.rs5 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-5"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-5"]["k"],
            generator_polynomial=DEFAULT_PARAMETERS["HQC-5"]["generator_polynomial"])

    def test_compute_generator_polynomial_hqc1(self):
        poly = self.rs1.compute_generator_polynomial()
        assert poly == DEFAULT_PARAMETERS["HQC-1"]["generator_polynomial"]

    def test_compute_generator_polynomial_hqc3(self):
        poly = self.rs3.compute_generator_polynomial()
        assert poly == DEFAULT_PARAMETERS["HQC-3"]["generator_polynomial"]

    def test_compute_generator_polynomial_hqc5(self):
        poly = self.rs5.compute_generator_polynomial()
        assert poly == DEFAULT_PARAMETERS["HQC-5"]["generator_polynomial"]

    def test_derived_parameters(self):
        self.assertEqual(self.rs1.delta, 15)
        self.assertEqual(self.rs1.n_fft, 4)
        self.assertEqual(self.rs3.delta, 16)
        self.assertEqual(self.rs3.n_fft, 5)
        self.assertEqual(self.rs5.delta, 29)
        self.assertEqual(self.rs5.n_fft, 5)

    def test_encode_hqc1(self):
        m = bytes.fromhex("3deca12f8963918f537c67f2571fffde")
        golden = bytes.fromhex(
            "8bf45f90b6d430ebbe5d73be57ae6300b4977457e5ea394927e8947ca946" \
            "3deca12f8963918f537c67f2571fffde")
        encoded = self.rs1.encode(m)
        self.assertEqual(encoded, golden)

    def test_encode_hqc3(self):
        m = bytes.fromhex("3deca12f8963918f537c67f2571fffde4bb80684d826860c")
        golden = bytes.fromhex(
            "0d5a8f9575cbaa0d424dfc2c3f9bccf334dacc29086e1d92e30a74cd2661f121" \
            "3deca12f8963918f537c67f2571fffde4bb80684d826860c")
        encoded = self.rs3.encode(m)
        self.assertEqual(encoded, golden)

    def test_encode_hqc5(self):
        m = bytes.fromhex(
            "3deca12f8963918f537c67f2571fffde4bb80684d826860c7515ce86e35571f5")
        golden = bytes.fromhex(
            "c5518ddd1dceaaa04ec1375c25491f9376083f91799ab10a27628f20a7b48343e457ad30c20d1188004e6a6a05cffb998e2e936af4bc1576187d" \
            "3deca12f8963918f537c67f2571fffde4bb80684d826860c7515ce86e35571f5")
        encoded = self.rs5.encode(m)
        self.assertEqual(encoded, golden)

    def test_compute_syndrome_hqc1(self):
        """Test the syndrome computation. The cases comes from KAT tests in C code"""
        cdw = bytes.fromhex(
            "1eb41c69532920ae35bb8c860ed3fa803b676e4a09918c8b925e5c074b221fdd3cbf3a73b96eb96448ae2a49505f")
        golden = [
            235, 4, 143, 159, 153, 223, 129, 218, 228, 171, 28,
            138, 250, 232, 39, 160, 60, 134, 118, 84, 145,
            220, 162, 245, 71, 180, 181, 95, 177, 208]
        self.assertEqual(len(cdw), self.rs1.n)
        self.assertEqual(self.rs1._compute_syndromes(cdw), golden)

    def test_compute_elp_hqc1(self):
        syndromes = to_gf2m([
            235, 4, 143, 159, 153, 223, 129, 218, 228, 171, 28,
            138, 250, 232, 39, 160, 60, 134, 118, 84, 145,
            220, 162, 245, 71, 180, 181, 95, 177, 208])
        golden = [1, 234]
        elp = self.rs1._compute_elp(syndromes)
        self.assertTrue(equal_poly(elp, golden))

    def test_compute_syndrome_hqc3(self):
        cdw = bytes.fromhex(
            "0d5a8f9575cbaa0d424dfc2c3f9bccf334dacc29086e1d92e30a74cd2661f1213deca12f8963918f537c67f2571fffde4bb80684d826860c")
        golden = [GF2m(0)] * (2 * self.rs3.delta)
        self.assertEqual(len(cdw), self.rs3.n)
        self.assertEqual(self.rs3._compute_syndromes(cdw), golden)

    def test_compute_syndrome_hqc5(self):
        cdw = bytes.fromhex(
            "2cbb13d087a4458c3c9c4262a85602f5b0feef96df321a8dd2c2e16bbd6ac14f4e744a98473c83c71ec83cc6cefd40b3a22cc8d6920e9de5d7cd7d1300b768bbd74b4174138124a0597e1368486a3afebba6763da68b72fbc767")
        golden = [
            166, 245, 1, 143, 70, 101, 217, 59, 168, 252,
            130, 195, 44, 58, 39, 186, 231, 26, 23, 146,
            219, 56, 36, 54, 45, 181, 97, 223, 62, 33,
            191, 110, 89, 251, 8, 12, 10, 15, 134, 197,
            41, 179, 100, 86, 125, 205, 37, 185, 107, 208,
            184, 228, 150, 221, 61, 173, 117, 193]
        self.assertEqual(len(cdw), self.rs5.n)
        self.assertEqual(self.rs5._compute_syndromes(cdw), golden)

    def test_compute_elp_hqc5(self):
        syndromes = to_gf2m([
            166, 245, 1, 143, 70, 101, 217, 59, 168, 252,
            130, 195, 44, 58, 39, 186, 231, 26, 23, 146,
            219, 56, 36, 54, 45, 181, 97, 223, 62, 33,
            191, 110, 89, 251, 8, 12, 10, 15, 134, 197,
            41, 179, 100, 86, 125, 205, 37, 185, 107, 208,
            184, 228, 150, 221, 61, 173, 117,193])
        golden = [1, 143]
        elp = self.rs5._compute_elp(syndromes)
        self.assertTrue(equal_poly(elp, golden))

    def test_compute_z_hqc1(self):
        syndromes = to_gf2m([
            54, 153, 63, 195, 193, 213, 147, 4, 103, 215, 79, 66, 136, 161, 138, 107, 93, 193, 239, 145, 50, 175, 166, 136, 231, 192, 110, 83, 120, 19
        ])
        elp = to_gf2m([
            1, 137, 74, 139, 12, 91, 36, 202, 34, 138, 88, 160, 153, 167, 118, 68
        ])
        z = self.rs1._compute_z_poly(elp, syndromes)
        golden = [
            1, 191, 74, 94, 12, 150, 36, 209, 34, 160, 88, 84, 153, 148, 118, 174
        ]
        self.assertTrue(equal_poly(z, golden))

    def test_compute_z_hqc3(self):
        syndromes = to_gf2m([
            240, 11, 155, 159, 145, 16, 74, 123, 132, 114, 231, 254, 200, 57, 30, 229, 53, 26, 162, 169, 158, 176, 7, 2, 166, 155, 196, 109, 12, 247, 58, 99
        ])
        elp = to_gf2m([
            1, 115, 152, 220, 63, 105, 89, 96, 209, 10, 156, 171, 195, 76, 249, 146, 81
        ])
        z = self.rs3._compute_z_poly(elp, syndromes)
        golden = [1, 131, 152, 180, 63, 154, 89, 199, 209, 66, 156, 232, 195, 13, 249, 88, 81]
        self.assertTrue(equal_poly(z, golden))


    def test_compute_z_hqc5(self):
        syndromes = to_gf2m([
          126, 115, 27, 84, 156, 97, 242, 206, 247, 85, \
          153, 121, 135, 216, 133, 35, 53, 78, 119, 51, \
          178, 195, 237, 54, 186, 52, 247, 101, 215, 231, \
          98, 241, 249, 183, 18, 82, 10, 63, 144, 15, \
          224, 131, 130, 4, 149, 210, 17, 153, 136, 50, \
          234, 74, 149, 78, 179, 18, 231, 145
        ])
        elp = to_gf2m([
            1, 131, 200, 154, 140, 122, 187, 199, 81, 56, \
            46, 99, 64, 10, 138, 114, 228, 191, 199, 156, \
            237, 8, 223, 137, 67, 29, 5, 193, 174, 86
        ])
        z = self.rs5._compute_z_poly(elp, syndromes)
        golden = [
            1, 253, 200, 251, 140, 222, 187, 83, 81, 78, \
            46, 216, 64, 66, 138, 125, 228, 108, 199, 197, \
            237, 163, 223, 191, 67, 217, 5, 109, 174, 20
        ]
        self.assertTrue(equal_poly(z, golden))

    def _assert_error_correction_for_level(self, rs, iterations=5):
        for _ in range(iterations):
            rng = random.Random()
            msg = bytes(rng.randrange(256) for _ in range(rs.k))
            encoded = rs.encode(msg)

            for error_count in range(1, rs.delta + 1):
                rng = random.Random()
                positions = set()
                while len(positions) < error_count:
                    positions.add(rng.randrange(rs.n))

                corrupted = bytearray(encoded)
                for pos in positions:
                    corrupted[pos] = (~corrupted[pos]) & 0xFF

                decoded = rs.decode(bytes(corrupted))
                self.assertEqual(decoded[-rs.k:], msg)

    def test_decode_error_correction_hqc1(self):
        self._assert_error_correction_for_level(self.rs1, iterations=5)

    def test_decode_error_correction_hqc3(self):
        self._assert_error_correction_for_level(self.rs3, iterations=5)

    def test_decode_error_correction_hqc5(self):
        self._assert_error_correction_for_level(self.rs5, iterations=5)

if __name__ == '__main__':
    unittest.main()