from datetime import datetime
import hashlib
from urllib.parse import urlparse
from uuid import uuid4
import requests
import binascii
from typing import OrderedDict
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


from pay_app.block.block import Block
from pay_app.transactions.transactions import Transaction

DIFFICULTY = 2
SENDER_ADDR = 'CIT COIN'


class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()
        self.node_id = str(uuid4()).replace('-', '')
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], datetime.now(), "0", "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block.to_dict())

    @property
    def last_block(self):
        return self.chain[-1]

    def register_node(self, address):
        """
        A function to add a new node to the list of nodes
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def add_block(self, prev_hash, nonce):
        block = Block(len(self.chain)+1, self.transactions, datetime.now(), nonce, prev_hash)
        block.hash = block.compute_hash()
        self.transactions = []
        self.chain.append(block.to_dict())
        return block.to_dict()

    def proof_of_work(self):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        last_block = self.chain[-1]
        prev_hash = last_block['hash']

        nonce = 0
        while self.is_valid_proof(self.transactions, prev_hash, nonce) is False:
            nonce += 1
        return nonce
        

    def add_new_transaction(self, transaction):
        self.transactions.append(transaction)

    @classmethod
    def is_valid_proof(self, transactions, last_hash, nonce, difficulty=DIFFICULTY):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        guess = (str(transactions)+str(last_hash)+str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0'*difficulty

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block.hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        """
        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get('http://{}/chain'.format(node))

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.check_chain_validity(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def verify_transaction_signature(self, sender_address, signature, data):
        """
        Verify the signature of transaction
        """
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(data).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))

    def mine(self, sender_address, recepient_address, ammount, signature=""):
        nonce = self.proof_of_work()
        data = {
            "sender_address": sender_address,
            "recipient_address": recepient_address,
            "ammount": ammount,
            "signature": signature,
            "nonce": nonce
        }
        if sender_address == SENDER_ADDR:
            self.transactions.append(OrderedDict(data))
            return len(self.chain) + 1
        else:
            transaction_verify = self.verify_transaction_signature(
                sender_address, signature, data)
            if transaction_verify:
                self.transactions.append(OrderedDict(data))
                return len(self.chain) + 1
            else:
                return False
