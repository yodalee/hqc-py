import unittest
from hqc_py import Hqc1, Hqc3, Hqc5

import re
from typing import List, Dict

def parse_rsp_file(filepath: str) -> List[Dict[str, bytes]]:
    """
    Parse a NIST KAT .rsp file into a list of dicts with all data in bytes format.
    Each block is separated by a blank line and contains fields like count, seed, pk, sk, ct, ss.
    """
    vectors = []
    with open(filepath, 'r') as f:
        content = f.read()
    blocks = re.split(r'\n\s*\n', content)
    for block in blocks:
        entry = {}
        for line in block.strip().splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # count is an integer, others are hex to bytes
                if key == 'count':
                    entry[key] = int(value)
                else:
                    entry[key] = bytes.fromhex(value)
        if entry:
            vectors.append(entry)
    return vectors

class TestHqc_KAT(unittest.TestCase):
    """
    Test HQC test vectors generated from C ref
    https://gitlab.com/pqc-hqc/hqc
    """
    file_map = {
        0: "assets/PQCkemKAT_2321.rsp",
        1: "assets/PQCkemKAT_4602.rsp",
        2: "assets/PQCkemKAT_7333.rsp"
    }

    def generic_keygen_kat(self, Hqc, index):
        kat_file = self.file_map[index]
        vectors = parse_rsp_file("assets/PQCkemKAT_2321.rsp")

    def generic_encap_kat(self, Hqc, index):
        kat_file = self.file_map[index]
        vectors = parse_rsp_file("assets/PQCkemKAT_2321.rsp")

    def generic_decap_kat(self, Hqc, index):
        kat_file = self.file_map[index]
        vectors = parse_rsp_file("assets/PQCkemKAT_2321.rsp")

    def test_Hqc_1_keygen(self):
        self.generic_keygen_kat(Hqc1, 0)

    def test_Hqc_3_keygen(self):
        self.generic_keygen_kat(Hqc3, 1)

    def test_Hqc_5_keygen(self):
        self.generic_keygen_kat(Hqc5, 2)

    def test_Hqc_1_encap(self):
        self.generic_encap_kat(Hqc1, 0)

    def test_Hqc_3_encap(self):
        self.generic_encap_kat(Hqc3, 1)

    def test_Hqc_5_encap(self):
        self.generic_encap_kat(Hqc5, 2)

    def test_Hqc_1_decap(self):
        self.generic_decap_kat(Hqc1, 0)

    def test_Hqc_3_decap(self):
        self.generic_decap_kat(Hqc3, 1)

    def test_Hqc_5_decap(self):
        self.generic_decap_kat(Hqc5, 2)