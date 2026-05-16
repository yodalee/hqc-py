import unittest

from hqc_py.default_parameters import DEFAULT_PARAMETERS
from hqc_py.reed_solomon import ReedSolomon


class TestReedSolomon(unittest.TestCase):

    def test_compute_generator_polynomial_hqc1(self):
        rs1 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-1"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-1"]["k"],
            generator_polynomial=None)
        poly = rs1.compute_generator_polynomial()
        assert len(poly) == rs1.g

    def test_compute_generator_polynomial_hqc3(self):
        rs3 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-3"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-3"]["k"],
             generator_polynomial=None)
        poly = rs3.compute_generator_polynomial()
        assert len(poly) == rs3.g

    def test_compute_generator_polynomial_hqc5(self):
        rs5 = ReedSolomon(
            n = DEFAULT_PARAMETERS["HQC-5"]["n1"],
            k = DEFAULT_PARAMETERS["HQC-5"]["k"],
            generator_polynomial=None)
        poly = rs5.compute_generator_polynomial()
        assert len(poly) == rs5.g

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

if __name__ == '__main__':
    unittest.main()