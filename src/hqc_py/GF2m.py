# Galois field implementation for GF(2^m)

class GF2m:
    def __init__(self, bits=0):
        if bits >= 256:
            raise ValueError("Bits must be less than 256 for GF(2^8)")
        self.bits = bits
        # Irreducible polynomial (x^8 + x^4 + x^3 + x + 1) for GF(2^8)
        self.q = 0x11D

    def __str__(self):
        return bin(self.bits)[2:].zfill(8)

    def __bytes__(self):
        return self.bits.to_bytes((8 + 7) // 8, 'little')

    def __repr__(self):
        return f"GF2m({bin(self.bits)[2:]})"

    def reduce(self, n: int):
        """
        Reduce a polynomial modulo 0x11D in GF(2^8).

        This function performs modular reduction of a 16-bit polynomial `x`
        by the irreducible polynomial 0x11D
        (i.e., x^8 + x^4 + x^3 + x^2 + 1), used in GF(2^8).

        It assumes the input polynomial has degree ≤ 14 and uses a fixed
        number of reduction steps and fixed feedback tap positions
        ({4, 3, 2}) to produce a result of degree < 8.

        Args:
            n (int): 16-bit input polynomial to reduce (deg(x) ≤ 14).

        Returns:
            int: Reduced 8-bit polynomial modulo 0x11D (deg(x) < 8).
        """
        reduction_steps = 2  # Fixed number of reduction steps for degree ≤ 14
        reduction_tap = [4, 3, 2] # Number of feedback positions
        for _ in range(reduction_steps): # Perform at most 2 reductions for degree ≤ 14
            mod = n >> 8
            n &= 0xFF # Keep only the lower 8 bits
            n ^= mod  # XOR with no shift

            for dist in reversed(reduction_tap):
                n ^= (mod << dist)
        return n

    def __mul__(self, other):
        """
        Multiply two elements in GF(2^m).

        Args:
            other (GF2m): Another element of GF(2^m) to multiply with.
        Raises:
            ValueError: If the types or field sizes are incompatible.
        Returns:
            GF2m: The product of the two elements in GF(2^m).
        """
        if not isinstance(other, GF2m):
            raise ValueError("Incompatible types for multiplication")
        a = self.bits
        b = other.bits
        assert(self.bits < 256 and other.bits < 256)
        result = 0
        while b > 0:
            if b & 1:
                result ^= a
            a <<= 1
            b >>= 1

        return GF2m(self.reduce(result))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        """
        Add two elements in GF(2^m).

        Args:
            other (GF2m): Another element of GF(2^m) to multiply with.
        Raises:
            ValueError: If the types or field sizes are incompatible.
        Returns:
            GF2m: The product of the two elements in GF(2^m).
        """
        if not isinstance(other, GF2m):
            raise ValueError("Incompatible types for addition")
        return GF2m(self.bits ^ other.bits)

    def __radd__(self, other):
        return self.__add__(other)
