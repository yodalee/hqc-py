# class for GF2 / x^n - 1 arithmetic
class GF2:
    def __init__(self, size: int, bits: int):
        self.size = size
        self.bits = bits

    @classmethod
    def frombytes(cls, size: int, b: bytes):
        val = int.from_bytes(b, 'little')
        bits = val & ((1 << size) - 1)
        return cls(size, bits)

    def __str__(self):
        return self.bits.bin()[2:].zfill(self.size)

    def __bytes__(self):
        return self.bits.to_bytes((self.size + 7) // 8, 'little')

    def __repr__(self):
        return f"GF2({self.bits.bin()[2:]})"

    def __add__(self, other):
        if not isinstance(other, GF2) or self.size != other.size:
            raise ValueError("Incompatible types for addition")
        return GF2(self.size, self.bits ^ other.bits)

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if not isinstance(other, GF2) or self.size != other.size:
            raise ValueError("Incompatible types for multiplication")
        result = GF2(self.size, 0)
        for shift in other.tolist():
            result += (self << shift)
        return result

    def __lshift__(self, shift: int):
        shift = shift % self.size
        mask = (1 << self.size) - 1
        bits = ((self.bits << shift) & mask) | (self.bits >> (self.size - shift))
        return GF2(self.size, bits)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other):
        if not isinstance(other, GF2) or self.size != other.size:
            raise ValueError("Incompatible types for equality check")
        return self.bits == other.bits

    def at(self, index: int) -> bool:
        return (self.bits >> index) & 1 == 1

    def set(self, index: int, val: bool):
        if val:
            self.bits |= (1 << index)
        else:
            self.bits &= ~(1 << index)

    def tolist(self) -> list[int]:
        l = []
        idx = 0
        bits = self.bits
        while bits != 0:
            if bits & 1 == 1:
                l.append(idx)
            bits >>= 1
            idx += 1
        return l

    def fromlist(self, xs: list[int]):
        for offset in xs:
            self.bits |= (1 << offset)