import binascii
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

class Wallet:
    """
    CITCoin Wallet: A wallet is a private/public key pair
    """
    def __init__(self):
        self._private_key = RSA.generate(1024, Crypto.Random.new().read)
        self._public_key = self._private_key.publickey()
        self._signer = PKCS1_v1_5.new(self._private_key)


    def generate_address(self):
        """
        Generate an address for the public key
        """
        public_key = binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')
        private_key = binascii.hexlify(self._private_key.exportKey(format='DER')).decode('ascii')
        return {'public_key': public_key, 'private_key': private_key}

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
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(data)
        return verifier.verify(h, binascii.unhexlify(signature))
