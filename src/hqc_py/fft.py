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

    def _fft_recursive(self, f: list[GF2m], f_coeffs: int, m: int, m_f: int, betas: list[GF2m]) -> list[GF2m]:
        """Recursive FFT evaluation of a polynomial in GF(2^m)[x].

        Args:
            f: Polynomial coefficients. The input size is a power of 2.
            f_coeffs: Number of coefficients in ``f`` (that is, deg(f) + 1).
            m: Number of betas (the degree of the Galois field GF(2^m)).
            m_f: Number of coefficients of f (degree + 1)
            deltas: Precomputed values for the FFT.

        returns:
            A list of the evaluations of ``f`` at all subset sums of a basis.
        """
        # terminal condition
        if m_f == 1:
            w = [GF2m(0)] * (1 << m)
            tmp = [GF2m(0)] * m
            for i in range(m):
                tmp[i] = betas[i] * f[1]

            w[0] = f[0]
            x = 1
            for j in range(m):
                for k in range(x):
                    w[x + k] = w[k] + tmp[j]
                x *= 2
            return w

        # Compute g
        if betas[m - 1] != 1:
            beta_m_pow = GF2m(1)
            x = 1 << m_f
            for i in range(1, x):
                beta_m_pow = beta_m_pow * betas[m - 1]
                f[i] = beta_m_pow * f[i]

        # Step 3
        f0, f1 = self.radix(f, m_f)

        # Step 4
        gammas = [GF2m(0)] * (GF2m.m - 2)
        deltas = [GF2m(0)] * (GF2m.m - 2)
        for i in range(m-1):
            gammas[i] = betas[i] * betas[m - 1].inverse();
            deltas[i] = gammas[i].square() + gammas[i]

        gammas_sums = self.compute_subset_sums(gammas)

        # Step 5
        u = self._fft_recursive(f0, (f_coeffs + 1) // 2, m - 1, m_f - 1, deltas)

        k = 1 << (m - 1)
        w = [GF2m(0)] * (1 << m)
        if (f_coeffs <= 3): # 3-coefficent polynomial f case: f1 is constant
            w[0] = u[0]
            w[k] = u[0] + f1[0]
            for i in range(1, k):
                w[i]     = u[i] + (gammas_sums[i] * f1[0])
                w[k + i] = w[i] + f1[0]
        else:
            w[k:] = self._fft_recursive(f1, f_coeffs // 2, m - 1, m_f - 1, betas)
            w[0] = u[0]
            w[k] += u[0]
            for i in range(1, k):
                w[i]      = u[i] + (gammas_sums[i] * f1[0])
                w[k + i] += w[i]
        return w

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
            A list with length of 2^m (256) in default cases
        """
        assert len(f) == 1 << self.n_fft

        # 1. The betas and betas_sums are precomputed for the FFT.
        # 2. beta_m = 1, nothing to do.
        # 3. Radix the input f
        f0, f1 = self.radix(f, self.n_fft)

        # 4. Compute the gammas and deltas
        deltas = [GF2m(0)] * (GF2m.m - 1)
        for i in range(GF2m.m - 1):
            deltas[i] = self.betas[i].square() + self.betas[i]

        # 5. Recursive fft
        u = self._fft_recursive(f0, (f_coeffs + 1) // 2, GF2m.m - 1, self.n_fft - 1, deltas)
        v = self._fft_recursive(f1, f_coeffs // 2, GF2m.m - 1, self.n_fft - 1, deltas)

        # check root
        k = 1 << (GF2m.m - 1)
        w = ([GF2m(0)] * k) + v

        # Check if 0 is root
        w[0] = u[0]

        # Check if 1 is root
        w[k] += u[0]

        # Find other roots
        for i in range(1, k):
            w[i] = u[i] + self.betas_sums[i] * v[i]
            w[k+i] += w[i]

        return w