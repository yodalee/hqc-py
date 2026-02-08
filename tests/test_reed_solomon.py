import unittest

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