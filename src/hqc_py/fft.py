"""Implementation of the additive FFT and its transpose.

This implementation is based on the paper from Gao and Mateer:
Shuhong Gao and Todd Mateer, Additive Fast Fourier Transforms over Finite Fields,
IEEE Transactions on Information Theory 56 (2010), 6265--6272.
http://www.math.clemson.edu/~sgao/papers/GM10.pdf

It also includes improvements proposed by Bernstein, Chou and Schwabe:
https://binary.cr.yp.to/mcbits-20130616.pdf
"""

from .GF2m import GF2m
class FFT:
    def __init__(self, n_fft: int = 8):
        # the degree m of the Galois field GF(2^m)
        self.n_fft = n_fft
        self.betas = self.compute_fft_betas(GF2m.m)
        self.betas_sums = self.compute_subset_sums(self.betas)

    @staticmethod
    def compute_fft_betas(m: int) -> list[GF2m]:
        return [GF2m(1 << i) for i in range(m - 1, 0, -1)]

    @staticmethod
    def compute_subset_sums(values: list[GF2m]) -> list[GF2m]:
        """Compute subset sums where index bits select included values."""
        set_size = len(values)
        subset_sums = [GF2m(0)] * (1 << set_size)

        for i in range(set_size):
            for j in range(1 << i):
                subset_sums[(1 << i) + j] = values[i] + subset_sums[j]

        return subset_sums

    def radix(self, f: list[GF2m], level: int) -> tuple[list[GF2m], list[GF2m]]:
        """Compute the radix conversion of a polynomial in GF(2^m)[x].

        Computes ``f0`` and ``f1`` such that
        ``f(x) = f0(x^2 - x) + x * f1(x^2 - x)``, as proposed by
        Bernstein, Chou and Schwabe:
        https://binary.cr.yp.to/mcbits-20130616.pdf

        Args:
            f: Polynomial coefficients. The input size is a power of 2.
            level: ``2**level`` is the smallest power of 2 greater than or
                equal to the number of coefficients in ``f``.

        Returns:
            A tuple ``(f0, f1)`` where each list is half the size of ``f``.
        """
        assert level >= 1, f"Radix level {level} must be at least 1"
        assert len(f) == 1 << level, f"Polynomial size {len(f)} is not {1 << level}"

        if level == 1:
            return [f[0]], [f[1]]

        # The generalized radix conversion is computed recursively.
        # The polynomial f is cut into 4 sections of Q0, Q1, R0, R1
        n = 1 << (level - 2)
        Q = [GF2m(0)] * (2 * n)
        R = [GF2m(0)] * (2 * n)
        # assume that f has 4 * n elements
        Q[:n] = f[3*n:]
        Q[n:2*n] = f[3*n:]
        R[:2*n] = f[:2*n]

        for i in range(n):
            Q[i] += f[2 * n + i]
            R[n + i] += Q[i]

        Q0, Q1 = self.radix(Q, level - 1)
        R0, R1 = self.radix(R, level - 1)
        R0.extend(Q0)
        R1.extend(Q1)
        return R0, R1

    def fft(self, f: list[GF2m], f_coeffs: int) -> list[GF2m]:
        """Evaluate f on all field elements using an additive FFT algorithm.

        `f_coeffs` is the number of coefficients of `f` (that is, deg(f) + 1).
        The FFT proceeds recursively to evaluate `f` at all subset sums of a basis.
        On the first call, the gamma subset sums are the subset sums of beta
        (except 1). The polynomial is twisted at each recursion level.

        Args:
            f: Input polynomial coefficients.
            f_coeffs: Number of coefficients in `f`.

        Returns:
            A list of the evaluations of `f` at all field elements.
        """
        raise NotImplementedError("additive FFT core is not implemented yet")