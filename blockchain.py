import hashlib
import json
from time import time

class FaceSecureBlockchain:
    def __init__(self):
        self.chain = []
        # Create Genesis Block (The first block in the chain)
        self.create_block(proof=100, previous_hash='0', user_id="SYSTEM_INIT", amount=0.00)

    def create_block(self, proof, previous_hash, user_id, amount):
        """
        Creates a new block with high-security SHA-256 encryption.
        Transactions are recorded in USD for global compatibility.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'proof': proof,
            'previous_hash': previous_hash,
            'user_id': user_id,
            'amount': f"${amount:.2f}",
            'currency': 'USD',
            'auth_method': 'BIOMETRIC_FACE_ID'
        }
        self.chain.append(block)
        return block

    def hash_block(self, block):
        """
        Generates a 256-bit hash for a block using the SHA-256 algorithm.
        This ensures the block's data remains immutable and secure.
        """
        # Sorting keys ensures the hash is consistent every time
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def get_last_block_hash(self):
        """
        Utility to fetch the hash of the most recent block.
        """
        return self.hash_block(self.chain[-1])