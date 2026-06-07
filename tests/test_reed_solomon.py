import unittest

from hqc_py.default_parameters import DEFAULT_PARAMETERS
from hqc_py.reed_solomon import ReedSolomon
from hqc_py.GF2m import GF2m


class TestReedSolomon(unittest.TestCase):
    def test_compute_generator_polynomial_hqc1(self):
        rs1 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-1"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-1"]["k"],
            generator_polynomial=None)
        poly = rs1.compute_generator_polynomial()
        assert poly == DEFAULT_PARAMETERS["HQC-1"]["generator_polynomial"]

    def test_compute_generator_polynomial_hqc3(self):
        rs3 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-3"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-3"]["k"],
            generator_polynomial=None)
        poly = rs3.compute_generator_polynomial()
        assert poly == DEFAULT_PARAMETERS["HQC-3"]["generator_polynomial"]

    def test_compute_generator_polynomial_hqc5(self):
        rs5 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-5"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-5"]["k"],
            generator_polynomial=None)
        poly = rs5.compute_generator_polynomial()
        assert poly == DEFAULT_PARAMETERS["HQC-5"]["generator_polynomial"]

    def test_derived_parameters(self):
        rs1 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-1"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-1"]["k"],
            generator_polynomial=None)
        self.assertEqual(rs1.delta, 15)
        self.assertEqual(rs1.n_fft, 4)

        rs3 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-3"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-3"]["k"],
             generator_polynomial=None)
        self.assertEqual(rs3.delta, 16)
        self.assertEqual(rs3.n_fft, 5)

        rs5 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-5"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-5"]["k"],
            generator_polynomial=None)
        self.assertEqual(rs5.delta, 29)
        self.assertEqual(rs5.n_fft, 5)

    def test_encode_hqc1(self):
        rs1 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-1"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-1"]["k"],
            generator_polynomial = DEFAULT_PARAMETERS["HQC-1"]["generator_polynomial"]
        )
        m = bytes.fromhex("3deca12f8963918f537c67f2571fffde")
        golden = bytes.fromhex(
            "8bf45f90b6d430ebbe5d73be57ae6300b4977457e5ea394927e8947ca946" \
            "3deca12f8963918f537c67f2571fffde")
        encoded = rs1.encode(m)
        self.assertEqual(encoded, golden)

    def test_encode_hqc3(self):
        rs3 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-3"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-3"]["k"],
            generator_polynomial = DEFAULT_PARAMETERS["HQC-3"]["generator_polynomial"]
        )
        m = bytes.fromhex("3deca12f8963918f537c67f2571fffde4bb80684d826860c")
        golden = bytes.fromhex(
            "0d5a8f9575cbaa0d424dfc2c3f9bccf334dacc29086e1d92e30a74cd2661f121" \
            "3deca12f8963918f537c67f2571fffde4bb80684d826860c")
        encoded = rs3.encode(m)
        self.assertEqual(encoded, golden)

    def test_encode_hqc5(self):
        rs5 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-5"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-5"]["k"],
            generator_polynomial = DEFAULT_PARAMETERS["HQC-5"]["generator_polynomial"]
        )
        m = bytes.fromhex(
            "3deca12f8963918f537c67f2571fffde4bb80684d826860c7515ce86e35571f5")
        golden = bytes.fromhex(
            "c5518ddd1dceaaa04ec1375c25491f9376083f91799ab10a27628f20a7b48343e457ad30c20d1188004e6a6a05cffb998e2e936af4bc1576187d" \
            "3deca12f8963918f537c67f2571fffde4bb80684d826860c7515ce86e35571f5")
        encoded = rs5.encode(m)
        self.assertEqual(encoded, golden)
    
    def test_compute_syndrome_hqc1(self):
        """Test the syndrome computation. The cases comes from KAT tests in C code"""
        rs1 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-1"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-1"]["k"],
            generator_polynomial = DEFAULT_PARAMETERS["HQC-1"]["generator_polynomial"]
        )
        cdw = bytes.fromhex(
            "1eb41c69532920ae35bb8c860ed3fa803b676e4a09918c8b925e5c074b221fdd3cbf3a73b96eb96448ae2a49505f")
        golden = [
            235, 4, 143, 159, 153, 223, 129, 218, 228, 171, 28,
            138, 250, 232, 39, 160, 60, 134, 118, 84, 145,
            220, 162, 245, 71, 180, 181, 95, 177, 208]
        self.assertEqual(len(cdw), rs1.n)
        self.assertEqual(rs1._compute_syndromes(cdw), golden)

    def test_compute_syndrome_hqc3(self):
        rs3 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-3"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-3"]["k"],
            generator_polynomial = DEFAULT_PARAMETERS["HQC-3"]["generator_polynomial"]
        )
        cdw = bytes.fromhex(
            "0d5a8f9575cbaa0d424dfc2c3f9bccf334dacc29086e1d92e30a74cd2661f1213deca12f8963918f537c67f2571fffde4bb80684d826860c")
        golden = [GF2m(0)] * (2 * rs3.delta)
        self.assertEqual(len(cdw), rs3.n)
        self.assertEqual(rs3._compute_syndromes(cdw), golden)

    def test_compute_syndrome_hqc5(self):
        rs5 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-5"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-5"]["k"],
            generator_polynomial = DEFAULT_PARAMETERS["HQC-5"]["generator_polynomial"]
        )
        cdw = bytes.fromhex(
            "2cbb13d087a4458c3c9c4262a85602f5b0feef96df321a8dd2c2e16bbd6ac14f4e744a98473c83c71ec83cc6cefd40b3a22cc8d6920e9de5d7cd7d1300b768bbd74b4174138124a0597e1368486a3afebba6763da68b72fbc767")
        golden = [
            166, 245, 1, 143, 70, 101, 217, 59, 168, 252,
            130, 195, 44, 58, 39, 186, 231, 26, 23, 146,
            219, 56, 36, 54, 45, 181, 97, 223, 62, 33,
            191, 110, 89, 251, 8, 12, 10, 15, 134, 197,
            41, 179, 100, 86, 125, 205, 37, 185, 107, 208,
            184, 228, 150, 221, 61, 173, 117, 193]
        self.assertEqual(len(cdw), rs5.n)
        self.assertEqual(rs5._compute_syndromes(cdw), golden)

if __name__ == '__main__':
    unittest.main()