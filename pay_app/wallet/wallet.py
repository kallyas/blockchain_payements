import binascii
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class Wallet:
    """
    CITCoin Wallet: A wallet is a private/public key pair
    """
    def __init__(self):
        self._private_key = RSA.generate(1024)
        self._public_key = self._private_key.publickey()
        self._signer = PKCS1_OAEP.new(self._private_key)


    def generate_address(self):
        """
        Generate an address for the public key
        """
        return binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')

    def sign(self, data):
        """
        Sign data with private key
        """
        h = SHA.new(data)
        return binascii.hexlify(self._signer.sign(h)).decode('ascii')

    def verify_signature(self, wallet_address, signature, data):
        """
        Verify signature of data
        """
        public_key = RSA.importKey(binascii.unhexlify(wallet_address))
        verifier = PKCS1_OAEP.new(public_key)
        h = SHA.new(data)
        return verifier.verify(h, binascii.unhexlify(signature))
