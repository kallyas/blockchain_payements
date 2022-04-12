import binascii
from typing import OrderedDict
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class Transaction:
    def __init__(self, sender_address, sender_private_key, recipient_address, amount):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.amount = amount

    def __repr__(self):
        return f'Transaction: {self.sender_address} is sending {self.amount} to {self.recipient_address}'

    def to_dict(self):
        return OrderedDict({
            'sender_address': self.sender_address,
            'recipient_address': self.recipient_address,
            'amount': self.amount
        })

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')

    def verify_transaction_signature(self, sender_address, signature, data):
        """
        Verify the signature of transaction
        """
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(data).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))
