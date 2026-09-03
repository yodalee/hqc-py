
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
        syndromes = [GF2m(0)] * (2 * self.delta)
        for i in range(2 * self.delta):
            for j in range(1, self.n):
                idx = ((i+1) * j) % 255
                alpha = GF2m.gf_exp[idx]
                syndromes[i] += GF2m(codeword[j]) * GF2m(alpha)
            syndromes[i] += GF2m(codeword[0])
        return syndromes

    def _compute_elp(self, syndromes: List[GF2m]) -> Tuple[int, List[GF2m]]:
        """
        Compute the error-locator polynomial ``sigma`` (ELP).

        This is intended to be a constant-time implementation of Berlekamp's
        algorithm (see Lin and Costello, Chapter 6, BCH Codes).

        Notes:
            - ``p`` denotes the rho and is initialized at -1.
            - ``X_sigma_p`` means the ``X^(mu-rho) * sigma_prev(X)``.
            - ``sigma and ``X_sigma_p`` are updated in place.
            - ``X_sigma_p`` must be updated.
            - Correct decoding requires ``deg(sigma) <= self.delta``.
              Only the first ``self.delta + 1`` coefficients are meaningful.

        Args:
            syndromes: Array of size at least ``2 * self.delta`` containing
                the syndromes.

        Returns:
            The degree of ``sigma`` and the polynomial coefficients.
        """
        # Start with Sigma_0 = 1 and update the coefficients in place.
        sigma = [GF2m(1)] + [GF2m(0)] * (self.delta)
        deg_sigma = 0

        # Start with previous degree of 0 and x times sigma (X_sigma_prev) = x
        deg_sigma_prev = 0
        X_sigma_prev = [GF2m(0), GF2m(1)] + [GF2m(0)] * (self.delta - 1)

        d = syndromes[0]
        d_prev = GF2m(1)
        pp = -1 # 2*rho

        for mu in range(self.delta * 2):
            # Backup sigma in case we need it to update X_sigma_p
            sigma_copy = sigma.copy()
            deg_sigma_copy = deg_sigma

            dd = d * d_prev.inverse()
            for i in range(1, min(mu+2, self.delta + 1)):
                sigma[i] += dd * X_sigma_prev[i]

            deg_X = mu - pp
            candidate_deg = deg_X + deg_sigma_prev

            # the degree of ELP has increased
            degree_increased = d != GF2m(0) and candidate_deg > deg_sigma

            if degree_increased:
                deg_sigma = candidate_deg

            if mu == self.delta * 2 - 1:
                break

            if degree_increased:
                pp = mu
                d_prev = d
                deg_sigma_prev = deg_sigma_copy
                # X_sigma_p = x * sigma_copy
                for i in range(self.delta, 0, -1):
                    X_sigma_prev[i] = sigma_copy[i - 1]
            else:
                # keep the existing reference polynomial and multiply
                # X_sigma_p by x
                for i in range(self.delta, 0, -1):
                    X_sigma_prev[i] = X_sigma_prev[i - 1]

            # Compute the discrepancy for the next iteration
            #
            # d = Syndrome[mu + 1] + sigma[1] * Syndrome[mu] + sigma[2] * Syndrome[mu - 1] + ...
            d = syndromes[mu + 1]
            for i in range(1, min(mu+2, self.delta + 1)):
                d += sigma[i] * syndromes[(mu + 1) - i]

        return sigma

    def _compute_roots(self, sigma: List[GF2m]) -> List[GF2m]:
        """
        Compute the roots of the error-locator polynomial.

        Args:
            sigma: Error-locator polynomial coefficients.

        Returns:
            A list of error locations.
        """
        return []

    def _compute_z_poly(self, sigma: List[GF2m],  syndromes: List[GF2m]) -> List[GF2m]:
        """
        Compute the error-evaluator polynomial ``z(x)``.

        Args:
            sigma: Error-locator polynomial coefficients of size 2^PARAM_FFT.
            syndromes: syndromes of size 2 * PARAM_DELTA.

        Returns:
            The array of size PARAM_DELTA + 1, coefficients of ``z(x)``.
        """
        deg = len(sigma) - 1
        z = [GF2m(1)] + [GF2m(0)] * self.delta

        # non-constant implementation
        # assign z with index smaller then syndrome degree to ELP, otherwise assign to 0
        for i in range(1, self.delta + 1):
            if i <= deg:
                z[i] = sigma[i]
        z[1] += syndromes[0]

        for i in range(2, self.delta + 1):
            if i <= deg:
                z[i] += syndromes[i - 1]
                for j in range(1, i):
                    z[i] += sigma[j] * syndromes[i - j - 1]
        return z

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
        sigma = self._compute_elp(syndromes)

        # 3. compute the error polynomial error
        error = self._compute_roots(sigma)

        # 4. Compute the polynomial z(x)
        z = self._compute_z_poly(sigma, syndromes)

        # 5. Compute the error values
        error_values = self._compute_error_values(z, error)

        # 6. Correct the errors
        corrected_data = self._correct_errors(encoded_data, error_values)
        return corrected_data[:self.n]
