import unittest
from hqc_py import Hqc1
from hqc_py.shake_wrapper import hqc_prng, hqc_xof

class TestHQC_hash(unittest.TestCase):

    def test_hash_g(self):
        result = Hqc1.hash_g(bytes.fromhex('000102030405060708090a0b0c0d0e0f'))
        expected = bytes.fromhex(
            '3c337c1902c794e04d41cf57475cbdfd4fc9ff2b1f3f33bebef38024d04fca96' \
            '42943ea990dcfd2b89a5568e97b0fa26dfcc65bd4e0829c6658eaab7812aa4eb')
        self.assertEqual(result, expected)

    def test_hash_h(self):
        result = Hqc1.hash_h(bytes.fromhex('000102030405060708090a0b0c0d0e0f'))
        expected = bytes.fromhex(
            '464c3d3551df28d44c76a6a88593473c5628c5a4d6b776ef02d3b7bce762037d')
        self.assertEqual(result, expected)

    def test_hash_i(self):
        result = Hqc1.hash_i(bytes.fromhex('000102030405060708090a0b0c0d0e0f'))
        expected = bytes.fromhex('' \
            'ad4466f97852f8cf77ae37cb38770f2dfd66e953d3305bc399ce5a5a0f87a591' \
            'c6a9da4f4327c493f5d8987c169b08c998c636d9948c2de73cd35b6b09d96562')
        self.assertEqual(result, expected)

    def test_hash_j(self):
        result = Hqc1.hash_j(bytes.fromhex('000102030405060708090a0b0c0d0e0f'))
        expected = bytes.fromhex('076d0f3ed0647731e4125ef05a2aec10a615cc8cd4226df5e4e1f40ab554b809')
        self.assertEqual(result, expected)

class TestShakeWrapper(unittest.TestCase):
    def test_hqc_prng(self):
        prng = hqc_prng(bytes.fromhex('000102030405060708090a0b0c0d0e0f'))
        output = prng.read(32)
        expected = bytes.fromhex('c731cc093d41e16e750eb0c35ba53e38fed6aa601470f3c6e31703c3249babca')
        self.assertEqual(output, expected)

        output = prng.read(32)
        expected = bytes.fromhex('c06fa71c04d3008c8cbb61042ee91306b71ddd5a5eb87361cf2b44d685363aea')
        self.assertEqual(output, expected)

    def test_hqc_xof(self):
        xof = hqc_xof(bytes.fromhex('000102030405060708090a0b0c0d0e0f'))
        output = xof.read(32)
        expected = bytes.fromhex('37c91a89ec9f30f995fe70e5da53752cf0d20803bc595bfa9bae2842dc160df3')
        self.assertEqual(output, expected)

        output = xof.read(32)
        expected = bytes.fromhex('63b59ed20b4db6b13ba93f653138f37ae2e73362799e86c899eef5faf0741e45')
        self.assertEqual(output, expected)