import hashlib
import math
from .shake_wrapper import hqc_xof, ShakeWrapper
from .GF2 import GF2
from .reed_solomon import ReedSolomon
from .reed_muller import ReedMuller

align_up = lambda x, align: align * math.ceil(x / align)

class Hqc:
    def __init__(self, parameter_set):
        self.n1 = parameter_set["n1"]
        self.n2 = parameter_set["n2"]
        self.n = parameter_set["n"]
        self.k = parameter_set["k"]
        self.w = parameter_set["w"]
        self.we = parameter_set["we"]
        self.len_security_bytes = parameter_set["len_security_bytes"]

        self.len_salt = 16
        self.len_seed = 32
        self.domain_sep = {'G': b'\x00', 'H': b'\x01', 'I': b'\x02', 'J': b'\x03'}
        self.rs = ReedSolomon(
            n = self.n1,
            k = self.k,
            generator_polynomial = parameter_set["generator_polynomial"]
        )
        self.rm = ReedMuller(n_repeat = parameter_set["n_repeat"])

    def hash_g(self, input_data: bytes) -> bytes:
        """
        Hash function G: SHA3_512 with domain separation G
        """
        return hashlib.sha3_512(input_data + self.domain_sep['G']).digest()

    def hash_h(self, input_data: bytes) -> bytes:
        """
        Hash function H: SHA3_256 with domain separation H
        """
        return hashlib.sha3_256(input_data + self.domain_sep['H']).digest()

    def hash_i(self, input_data: bytes) -> bytes:
        """
        Hash function I: SHA3_512 with domain separation I
        """
        return hashlib.sha3_512(input_data + self.domain_sep['I']).digest()

    def hash_j(self, input_data: bytes) -> bytes:
        """
        Hash function J: SHA3_256 with domain separation J
        """
        return hashlib.sha3_256(input_data + self.domain_sep['J']).digest()

    def sample_fixed_weight_vect1(self, xof: ShakeWrapper) -> GF2:
        """
        Sample a vector of fixed weight self.w over GF(2) of length self.n.
        """
        # constant
        reject_threshold = ((1 << 24) // self.n) * self.n
        len_bytes = 3 * self.w
        len_squeeze = align_up(len_bytes, 8)

        # initialize buffer and result GF2
        buf = xof.read(len_squeeze)
        result = GF2(self.n, 0)

        pos = 0
        i = 0
        while i < self.w:
            if pos == len_bytes:
                # consume up a block, request another block
                buf = xof.read(len_squeeze)
                pos = 0

            val = int.from_bytes(buf[pos:pos+3], 'big')
            pos += 3

            if val >= reject_threshold:
                continue
            val = val % self.n
            if result.at(val):
                continue
            result.set(val, True)
            i += 1
        return result

    def sample_fixed_weight_vect2(self, xof: ShakeWrapper) -> GF2:
        """
        Sample a vector of fixed weight self.we over GF(2) of length self.n.
        """
        # constant
        len_bytes = 4 * self.we
        len_squeeze = align_up(len_bytes, 8)

        # initialize buffer and result GF2
        buf = xof.read(len_squeeze)
        result = GF2(self.n, 0)

        values = []
        for i in range(self.we):
            # generate value
            u32 = int.from_bytes(buf[4*i:4*i+4], 'little')
            val = i + ((u32 * (self.n - i)) >> 32)
            values.append(val)

        for i in range(self.we-1, -1, -1):
            # deduplicate values, replace with 0-w-1
            idx = i if result.at(values[i]) else values[i]
            result.set(idx, True)
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
        y = self.sample_fixed_weight_vect1(xof)
        x = self.sample_fixed_weight_vect1(xof)

        # Compute encryption key ekpke
        xof = hqc_xof(seed_ek)
        h = self.sample_vect(xof)
        s = x + h * y
        ekpke = seed_ek + bytes(s)

        return ekpke, dkpke

    def pke_encrypt(self, ek: bytes, message: bytes, theta: bytes) -> bytes:
        """
        Encrypt a message using the public key and a seed.
        Returns ciphertext as bytes.
        """
        # retrieve h, and s from seed in ek
        seed = ek[:self.len_seed]
        s = GF2.frombytes(self.n, ek[self.len_seed:])
        xof = hqc_xof(seed)
        h = self.sample_vect(xof)

        # Generate r1, r2, e
        xof = hqc_xof(theta)
        r2 = self.sample_fixed_weight_vect2(xof)
        e = self.sample_fixed_weight_vect2(xof)
        r1 = self.sample_fixed_weight_vect2(xof)

        # Compute u = r1 + r2 * h
        u = r1 + h * r2

        # Compute v = encode(message) + Truncate(s.r2 + e)
        term = s * r2 + e
        truncate = GF2(self.n1 * self.n2, term.bits)
        v = GF2.frombytes(self.n1 * self.n2, self.rm.encode(self.rs.encode(message))) + truncate
        return bytes(u) + bytes(v)

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
        sigma = xof.read(self.len_security_bytes)

        #Compute HQC-PKE keypair
        ek_pke, dk_pke = self.pke_keygen(seed_pke)

        #Compute HQC-KEM keypair
        ek_kem = ek_pke
        dk_kem = ek_kem + dk_pke + sigma + seed_kem
        return ek_kem, dk_kem

    def kem_encaps(self, ek_kem: bytes, m: bytes, salt: bytes) -> tuple[bytes, bytes]:
        """
        Encapsulate the message m using the encapsulation key and add the salt
        Returns (ct, ss) as (bytes, bytes).
        """
        # Compute seedPKE and randomness σ
        hash_ek_kem = self.hash_h(ek_kem)
        k_theta = self.hash_g(hash_ek_kem + m + salt)
        theta = k_theta[self.len_seed:]
        ct = self.pke_encrypt(ek_kem, m, theta)
        ss = k_theta[:32]

        return ct + salt, ss

    def kem_decaps(self, sk: bytes, ct: bytes) -> bytes:
        """
        Decapsulate using the secret key and ciphertext.
        Returns ss as bytes.
        """
        # TODO: Implement decapsulation logic
        ss = b''  # placeholder
        return ss
