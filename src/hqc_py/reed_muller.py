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
        assert(len(msg) == self.param_n1, "Message length must be PARAM_N1 bytes")
        cdws = [self.encode_1byte(msg[i:i+1]) * self.n_repeat for i in range(self.param_n1)]
        encoded = b''.join(cdws)
        assert(len(encoded) == (self.param_n1 * self.param_n2 * self.n_repeat) // 8)
        return encoded

    def decode(self, encoded_data: bytes) -> bytes:
        """
        Decodes the received word.

        Args:
            encoded_data: A byte array of size PARAM_N1 * PARAM_N2 containing the encoded message.

        Returns:
            A byte array of size PARAM_N1 storing the decoded message.
        """
        # count the number of 1s in each bit possition across the repeated codewords
        counts = [0] * 128
        for repeat in range(self.n_repeat):
            for offset in range(128):
                byte = encoded_data[repeat*16 + offset//8]
                for k in range(8):
                    counts[j*8 + k] += (byte >> k) & 1

        # hadamard transform to the counts
        transform = self._hadamard_transform(counts)

        raise NotImplementedError("ReedMuller.decode not implemented yet")