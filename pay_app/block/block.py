import hashlib
import json


class Block:
    def __init__(self, index, data, timestamp, previous_hash):
        self.index = index
        self.data = data
        self.timestamp = str(timestamp)
        self.previous_hash = previous_hash
        self.nonce = 0

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def __repr__(self):
        """
        A function that returns a string representation of the Block
        """
        return "Block: " + json.dumps(self.__dict__, sort_keys=True)

    def to_dict(self):
        """
        A function that returns a dictionary representation of the Block
        """
        return self.__dict__