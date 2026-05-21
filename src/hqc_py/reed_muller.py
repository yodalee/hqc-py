from typing import List

class ReedMuller:
    def __init__(self, n_repeat: int, param_n1: int):
        assert(n_repeat > 0)
        assert(param_n1 > 0)

        self.n_repeat = n_repeat
        # The length of input message to be encoded
        self.param_n1 = param_n1
        # The length of encoded message in bits
        self.param_n2 = 128

    def encode_1byte(self, msg: bytes) -> bytes:
        """
        Encode a single byte into a single codeword using RM(1,7).

        Encoding matrix of this code:
        Bit pattern (note that bits are numbered big endian):
        0(LSB) aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa
        1      cccccccc cccccccc cccccccc cccccccc
        2      f0f0f0f0 f0f0f0f0 f0f0f0f0 f0f0f0f0
        3      ff00ff00 ff00ff00 ff00ff00 ff00ff00
        4      ffff0000 ffff0000 ffff0000 ffff0000
        5      ffffffff 00000000 ffffffff 00000000
        6      ffffffff ffffffff 00000000 00000000
        7(MSB) ffffffff ffffffff ffffffff ffffffff

        The codeword is computed as the XOR of the rows of the encoding matrix corresponding to the bits set in the message byte.

        Args:
            msg: A message as a byte array.
        Returns:
            An RM(1,7) codeword as a byte array, length 2^7 = 128 bits
        """
        assert(len(msg) == 1)
        cdw = 0
        msg_int = int.from_bytes(msg, byteorder='big')
        matrix = [
            0xaaaaaaaa_aaaaaaaa_aaaaaaaa_aaaaaaaa,
            0xcccccccc_cccccccc_cccccccc_cccccccc,
            0xf0f0f0f0_f0f0f0f0_f0f0f0f0_f0f0f0f0,
            0xff00ff00_ff00ff00_ff00ff00_ff00ff00,
            0xffff0000_ffff0000_ffff0000_ffff0000,
            0xffffffff_00000000_ffffffff_00000000,
            0xffffffff_ffffffff_00000000_00000000,
            0xffffffff_ffffffff_ffffffff_ffffffff,
        ]
        for i, row in enumerate(matrix):
            if msg_int & (1 << i) != 0:
                cdw ^= row
        return cdw.to_bytes(16, byteorder='little')

    def encode(self, msg: bytes) -> bytes:
        """
        Encodes the received word.

        The message consists of N1 bytes, and each byte is encoded into PARAM_N2
        bits, or MULTIPLICITY repeats of 128 bits.

        Args:
            msg: A byte array of size PARAM_N1 storing the message.

        Returns:
            A byte array of size PARAM_N2 containing the encoded message.
        """
        assert(len(msg) == self.param_n1), "Message length must be PARAM_N1 bytes"
        cdws = [self.encode_1byte(msg[i:i+1]) * self.n_repeat for i in range(self.param_n1)]
        encoded = b''.join(cdws)
        assert(len(encoded) == (self.param_n1 * self.param_n2 * self.n_repeat) // 8)
        return encoded

    def _collect_bits(self, encoded_data: bytes) -> List[int]:
        """
        Add repeated codewords into an expanded bit-count vector.

        It counts how many times each of the 128 bit positions is set across all
        repeated codewords.

        Args:
            encoded_data: A byte array of size ``PARAM_N2 * n_repeat / 8``
                containing one repeated RM(1,7) codeword stream.

        Returns:
            A list of 128 integers where each entry is the number of 1s seen at
            that bit position across all repeats.
        """
        expected_length = (self.param_n2 * self.n_repeat) // 8
        assert len(encoded_data) == expected_length, (
            f"Encoded data length must be {expected_length} bytes"
        )

        # start collect
        counts = [0] * self.param_n2
        bytes_per_codeword = self.param_n2 // 8

        for repeat in range(self.n_repeat):
            base = repeat * bytes_per_codeword
            for byte_offset in range(bytes_per_codeword):
                value = encoded_data[base + byte_offset]
                bit_base = byte_offset * 8
                for bit in range(8):
                    counts[bit_base + bit] += (value >> bit) & 1

        return counts

    def _hadamard_transform(self, counts: List[int]) -> List[int]:
        """
        Performs the Hadamard transform on the input counts.

        Args:
            counts: A list of 128 integers representing the counts of 1s in each bit position.

        Returns:
            A list of 128 integers representing the Hadamard transform of the input counts.
        """
        assert len(counts) == 128, "Input to Hadamard transform must be of length 128"
        transform = counts.copy()

        for _ in range(7): # 7 = log2(128)
            for i in range(64):
                transform[i] = counts[2 * i] + counts[2 * i + 1]
                transform[i + 64] = counts[2 * i] - counts[2 * i + 1]
            counts = transform.copy()
        return transform

    def _find_peak(self, transform: List[int]) -> int:
        """
        Finds the index of the maximum value in the Hadamard transform.

        Args:
            transform: A list of 128 integers representing the Hadamard transform.

        Returns:
            The index of the maximum value in the transform, which corresponds to the decoded message byte.
        """
        idx, value = max(enumerate(transform), key=lambda pair: abs(pair[1]))
        return idx | 0x80 if value > 0 else idx

    def decode(self, encoded_data: bytes) -> bytes:
        """
        Decode the received word.

        Decoding uses the fast Hadamard transform. For a complete treatment of
        Reed-Muller decoding, see MacWilliams and Sloane, *The Theory of
        Error-Correcting Codes*.

        Args:
            encoded_data: A byte array of size ``PARAM_N1 * PARAM_N2 * n_repeat / 8``
            storing the received codeword stream.

        Returns:
            A byte array containing the decoded message.
        """
        # check the input length
        expected_length = (self.param_n1 * self.param_n2 * self.n_repeat) // 8
        assert len(encoded_data) == expected_length, f"Encoded data length must be {expected_length} bytes"
        chunk_length = self.param_n2 * self.n_repeat // 8

        message = bytearray(self.param_n1)

        for i in range(self.param_n1):
            start = i * chunk_length
            end = start + chunk_length
            chunk = encoded_data[start:end]
            counts = self._collect_bits(chunk)
            transform = self._hadamard_transform(counts)
            transform[0] -= 64 * self.n_repeat
            message[i] = self._find_peak(transform)

        return bytes(message)