import hashlib

class ShakeWrapper:
    def __init__(self, algorithm, block_length: int, suffix: bytes = b""):
        self.algorithm = algorithm
        self.block_length = block_length
        self.buf = b""
        self.len_buf = 0
        self.suffix = suffix

    def absorb(self, data: bytes):
        # initialize the buffer, reset indexer
        self.pos = 0

        # Set the reading method from hashlib digest
        self.xof_read = self.algorithm(data + self.suffix).digest

        # Start by requesting 5 blocks from the XOF
        self.buf = self.xof_read(self.block_length)
        self.len_buf = self.block_length

    def read(self, length: int) -> bytes:
        while self.pos + length > self.len_buf:
            # not enough data in the buffer, request more from XOF
            self.len_buf *= 2
            self.buf = self.xof_read(self.len_buf)

        send = self.buf[self.pos:self.pos + length]
        self.pos += length

        return send

    def __call__(self, data: bytes):
        self.absorb(data)
        return self

hqc_prng = ShakeWrapper(hashlib.shake_256, 168, b'\x00')
hqc_xof = ShakeWrapper(hashlib.shake_256, 136, b'\x01')