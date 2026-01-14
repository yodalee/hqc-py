class Hqc:
    def __init__(self, parameter_set):
        self.n1 = parameter_set["n1"]
        self.n2 = parameter_set["n2"]
        self.n = parameter_set["n"]
        self.k = parameter_set["k"]
        self.w = parameter_set["w"]
        self.we = parameter_set["we"]

    def keygen(self, seed: bytes) -> tuple[bytes, bytes]:
        """
        Generate a public/secret key pair from a seed.
        Returns (pk, sk) as (bytes, bytes).
        """
        # TODO: Implement key generation logic
        pk = b''  # placeholder
        sk = b''  # placeholder
        return pk, sk

    def encaps(self, sk: bytes) -> tuple[bytes, bytes]:
        """
        Encapsulate using the secret key.
        Returns (ct, ss) as (bytes, bytes).
        """
        # TODO: Implement encapsulation logic
        ct = b''  # placeholder
        ss = b''  # placeholder
        return ct, ss

    def decaps(self, sk: bytes, ct: bytes) -> bytes:
        """
        Decapsulate using the secret key and ciphertext.
        Returns ss as bytes.
        """
        # TODO: Implement decapsulation logic
        ss = b''  # placeholder
        return ss
