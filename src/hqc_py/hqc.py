import hashlib
import math
from .shake_wrapper import hqc_xof, ShakeWrapper
from .GF2 import GF2

align_up = lambda x, align: align * math.ceil(x / align)

class Hqc:
    def __init__(self, parameter_set):
        self.n1 = parameter_set["n1"]
        self.n2 = parameter_set["n2"]
        self.n = parameter_set["n"]
        self.k = parameter_set["k"]
        self.w = parameter_set["w"]
        self.we = parameter_set["we"]

        self.len_seed = 32
        self.domain_sep = {'G': b'\x00', 'H': b'\x01', 'I': b'\x02', 'J': b'\x03'}

    def hash_g(self, input_data: bytes) -> bytes:
        """
        Hash function G: SHA3_512 with domain separation G
        """
        return hashlib.sha3_512(input_data + self.domain_sep['G']).digest()

    def hash_h(self, input_data: bytes) -> bytes:
        """
        Hash function H: SHA3_512 with domain separation H
        """
        return hashlib.sha3_512(input_data + self.domain_sep['H']).digest()

    def hash_i(self, input_data: bytes) -> bytes:
        """
        Hash function I: SHA3_256 with domain separation I
        """
        return hashlib.sha3_256(input_data + self.domain_sep['I']).digest()

    def hash_j(self, input_data: bytes) -> bytes:
        """
        Hash function J: SHA3_256 with domain separation J
        """
        return hashlib.sha3_256(input_data + self.domain_sep['J']).digest()

    def sample_fixed_weight_vect(self, xof: ShakeWrapper) -> GF2:
        """
        Sample a vector of fixed weight self.w over GF(2) of length self.n.
        """
        buflen = 3 * self.w
        blocklen = align_up(buflen, 8)
        buf = xof.read(blocklen)
        pos = 0
        result = GF2(self.n, 0)
        i = 0
        while i < self.w:
            if pos == buflen:
                # consume up a block, request another block
                buf = xof.read(blocklen)
                pos = 0

            val = int.from_bytes(buf[pos:pos+3], 'little') % self.n
            pos += 3

            if not result.at(val):
                result.set(val, True)
                i += 1
        return result

    def sample_vect(self, xof: ShakeWrapper) -> GF2:
        buflen = align_up(self.n, 8)
        buf = xof.read(buflen)
        return GF2.frombytes(self.n, buf)

    def pke_keygen(self, seed: bytes) -> tuple[bytes, bytes]:
        """
        Generate a public/secret key pair from a seed.
        Returns (pk, sk) as (bytes, bytes).
        """
        # Compute dkpke and ekpke seeds
        buf = self.hash_i(seed)
        dkpke = buf[:self.len_seed]
        seed_ek = buf[self.len_seed:]

        # Compute decryption key dkpke
        xof = hqc_xof(dkpke)
        y = self.sample_fixed_weight_vect(xof)
        x = self.sample_fixed_weight_vect(xof)

        # Compute encryption key ekpke
        xof = hqc_xof(seed_ek)
        h = self.sample_vect(xof)
        s = x + h * y
        ekpke = seed_ek + bytes(s)

        return ekpke, dkpke

    def pke_encrypt(self, pk: bytes, message: bytes, seed: bytes) -> bytes:
        """
        Encrypt a message using the public key and a seed.
        Returns ciphertext as bytes.
        """
        ct = b''
        return ct

    def pke_decrypt(self, sk: bytes, ct: bytes) -> bytes:
        """
        Decrypt a ciphertext using the secret key.
        Returns message as bytes.
        """
        message = b''
        return message

    def kem_keygen(self, seed_kem: bytes) -> tuple[bytes, bytes]:
        """
        Generate a public/secret key pair from a seed.
        Returns (pk, sk) as (bytes, bytes).
        """
        # Compute seedPKE and randomness σ
        xof = hqc_xof(seed_kem)
        seed_pke = xof.read(self.len_seed)
        sigma = xof.read(self.k)

        #Compute HQC-PKE keypair
        ek_pke, dk_pke = self.pke_keygen(seed_pke)

        #Compute HQC-KEM keypair
        ek_kem = ek_pke
        dk_kem = ek_kem + dk_pke + sigma + seed_kem
        return ek_kem, dk_kem

    def kem_encaps(self, sk: bytes) -> tuple[bytes, bytes]:
        """
        Encapsulate using the secret key.
        Returns (ct, ss) as (bytes, bytes).
        """
        # TODO: Implement encapsulation logic
        ct = b''  # placeholder
        ss = b''  # placeholder
        return ct, ss

    def kem_decaps(self, sk: bytes, ct: bytes) -> bytes:
        """
        Decapsulate using the secret key and ciphertext.
        Returns ss as bytes.
        """
        # TODO: Implement decapsulation logic
        ss = b''  # placeholder
        return ss
