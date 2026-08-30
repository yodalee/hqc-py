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

    def fft(self, f: list[int], f_coeffs: int) -> list[int]:
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