import unittest

from hqc_py.default_parameters import DEFAULT_PARAMETERS
from hqc_py.reed_solomon import ReedSolomon

class TestReedSolomon(unittest.TestCase):
    def test_compute_gf_exp(self):
        rs = ReedSolomon(1, 0, None) # the value is not cared for this test
        computed = rs.compute_gf_exp()
        computed_int = [int(x) for x in computed]
        self.assertEqual(computed_int, ReedSolomon.gf_exp)

    def test_compute_gf_log(self):
        rs = ReedSolomon(1, 0, None) # the value is not cared for this test
        computed = rs.compute_gf_log()
        computed_int = [int(x) for x in computed]
        self.assertEqual(computed_int, ReedSolomon.gf_log)

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

if __name__ == '__main__':
    unittest.main()