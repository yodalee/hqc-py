
from typing import List, Tuple
from .GF2m import GF2m

import math

class ReedSolomon:
    def __init__(self, n: int, k: int, generator_polynomial: List[int]):
        if n < k:
            raise ValueError("n must be greater than or equal to k")
        self.n = n
        self.k = k
        self.generator_polynomial = generator_polynomial
        # derived parameters
        self.g = n - k + 1
        self.delta = (n - k) // 2
        self.n_fft = math.ceil(math.log2(k))

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

    def _compute_syndromes(self, codeword: bytes) -> List[GF2m]:
        """
        Compute ``2 * self.delta`` syndromes for a received codeword.

        Each syndrome is evaluated as ``S_i = r(alpha^i)`` for
        ``i = 1 .. 2 * self.delta``, where ``r(x)`` is the received
        polynomial and ``alpha`` is the field primitive element.

        Args:
            codeword: Received vector of size ``self.n``.

        Returns:
            A list of ``2 * self.delta`` syndrome values in ``GF(2^m)``.
        """
        return []

    def _compute_elp(self, syndromes: List[GF2m]) -> Tuple[int, List[GF2m]]:
        """
        Compute the error-locator polynomial ``sigma`` (ELP).

        This is intended to be a constant-time implementation of Berlekamp's
        algorithm (see Lin and Costello, Chapter 6, BCH Codes).

        Notes:
            - ``p`` denotes ``rho`` and is initialized at ``-1``.
            - ``X_sigma_p`` represents ``X^(mu-rho) * sigma_p(X)``.
            - ``sigma`` and ``X_sigma_p`` are updated in place.
            - ``sigma_copy`` is used as temporary storage when
              ``X_sigma_p`` must be updated.
            - Correct decoding requires ``deg(sigma) <= self.delta``.
              Only the first ``self.delta + 1`` coefficients are meaningful.

        Args:
            syndromes: Array of size at least ``2 * self.delta`` containing
                the syndromes.

        Returns:
            The degree of ``sigma`` and the polynomial coefficients.
        """
        return 0, []

    def _compute_roots(self, sigma: List[GF2m]) -> List[GF2m]:
        """
        Compute the roots of the error-locator polynomial.

        Args:
            sigma: Error-locator polynomial coefficients.

        Returns:
            A list of error locations.
        """
        return []

    def _compute_z_poly(self, sigma: List[GF2m], deg: int, syndromes: List[GF2m]) -> List[GF2m]:
        """
        Compute the error-evaluator polynomial ``z(x)``.

        Args:
            sigma: Error-locator polynomial coefficients.
            deg: Degree of ``sigma``.
            syndromes: Computed syndrome values.

        Returns:
            The coefficients of ``z(x)``.
        """
        return []

    def _compute_error_values(self, z: List[GF2m], error: List[GF2m]) -> List[GF2m]:
        """
        Compute the error magnitude for each located error position.

        Args:
            z: Error-evaluator polynomial coefficients.
            error: Error locations.

        Returns:
            The values to subtract from the received word.
        """
        return []

    def _correct_errors(self, encoded_data: bytes, error_values: List[GF2m]) -> bytes:
        """
        Apply error correction to the received codeword.

        Args:
            encoded_data: Received Reed-Solomon codeword.
            error_values: Error magnitudes.

        Returns:
            The corrected codeword.
        """
        return b""

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
        assert len(encoded_data) == self.n, f"Encoded data length must be {self.n} bytes"
        # 1. Compute the syndromes
        syndromes = self._compute_syndromes(encoded_data)

        # 2. Compute the error locator polynomial sigma
        # Sigma's degree is at most PARAM_DELTA but the FFT requires the extra room
        deg, sigma = self._compute_elp(syndromes)

        # 3. compute the error polynomial error
        error = self._compute_roots(sigma)

        # 4. Compute the polynomial z(x)
        z = self._compute_z_poly(sigma, deg, syndromes)

        # 5. Compute the error values
        error_values = self._compute_error_values(z, error)

        # 6. Correct the errors
        corrected_data = self._correct_errors(encoded_data, error_values)
        return corrected_data[:self.n]
