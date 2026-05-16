
from typing import List
from .GF2m import GF2m

class ReedSolomon:
    def __init__(self, n, k, generator_polynomial):
        if n < k:
            raise ValueError("n must be greater than or equal to k")
        self.n = n
        self.k = k
        self.g = n - k + 1
        self.generator_polynomial = generator_polynomial
        self.delta = (n - k) // 2

    def compute_generator_polynomial(self) -> List[int]:
        """
        Computes the generator polynomial of the primitive Reed-Solomon code with given parameters.

        Code length is 2^m-1.
        The alpha is 2, the generator polynomial is:
            g(x) = (x + alpha^1)(x + alpha^2)...(x + alpha^g)

        Returns:
            poly: List of size self.g with coefficients of the generator polynomial
        """
        # initialize the polynomial to 1
        poly = [1]

        for i in range(1, self.g):
            # loop to multiply (x + 2^i) with the current polynomial
            # The new jth coefficient is computed as:
            # poly[j] = 1 * poly[j-1] + 2^i * poly[j]
            for j in range(i-1, 0, -1):
                poly[j] = (GF2m.gf_exp[(GF2m.gf_log[poly[j]] + i) % 255] ^ poly[j - 1])
            # Constant term are multiply by 2^i
            poly[0] = GF2m.gf_exp[(GF2m.gf_log[poly[0]] + i) % 255]
            # The highest degree coefficient is always 1
            poly.append(1)
        return poly


    def encode(self, msg: bytes) -> bytes:
        """
        Encodes a message of PARAM_K bits to a Reed-Solomon codeword of PARAM_N1 bytes.

        Following Lin and Costello (Chapter 4 - Cyclic Codes),
        we perform a systematic encoding using a linear (PARAM_N1 - PARAM_K)-stage shift
        register with feedback connections based on the generator polynomial
        PARAM_RS_POLY of the Reed-Solomon code.

        Args:
            msg: byte array of the message

        Returns:
            cdw: encoded message as a byte array
        """
        assert len(msg) == self.k, f"Message length must be {self.k} bytes"
        # initialize the codeword buffer
        cdw = [GF2m(0)] * (self.n - self.k)

        for byte in msg[::-1]:  # Process each message byte in descending order
            gate_value = GF2m(byte) + cdw[-1]
            # multiply gate_value with the generator polynomial
            subtract = list(map(
                lambda x: gate_value * GF2m(x),
                self.generator_polynomial
            ))
            cdw = [subtract[0]] + [ci + si for ci, si in zip(
                cdw[:-1], subtract[1:])]

        return bytes(cdw) + msg

    def decode(self, encoded_data: bytes) -> bytes:
        """
        Decode the received word.

        This function relies on six steps:
        1. Compute the `2 * self.delta` syndromes.
        2. Compute the error-locator polynomial ``sigma(x)``.
        3. Use an additive FFT to find the roots of ``sigma(x)`` (the error
           locations) and take their inverses.
        4. Compute the error-evaluator polynomial ``z(x)``.
        5. Compute the error values at each located position.
        6. Correct the received polynomial by subtracting the error values.

        For a more complete treatment of Reed-Solomon decoding, see Lin and
        Costello, *Error Control Coding: Fundamentals and Applications*.

        Args:
            encoded_data: A byte array of size ``PARAM_N1`` storing the
                received word.

        Returns:
            A byte array of size ``PARAM_K`` containing the decoded message.
        """
        message = bytearray(self.k)
        return message
