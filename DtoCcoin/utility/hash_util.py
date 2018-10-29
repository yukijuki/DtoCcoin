import hashlib as hl
import json

# __all__ = ['hash_string_256', 'hash_block']

def hash_string_256(string):
    """Create a SHA256 hash for a given input string.

    Arguments:
        :string: The string which should be hashed.
    """
    return hl.sha256(string).hexdigest()


def hash_block(block):
    """Hashes a block and returns a string representation of it.

    Arguments:
        :block: The block that should be hashed.
    """
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    hashable_block['tagsactions'] = [tx1.to_ordered_dict1() for tx1 in hashable_block['tagsactions']]
    hashable_block['messsactions'] = [tx2.to_ordered_dict2() for tx2 in hashable_block['messsactions']]
    hashable_block['account'] = [tx3.to_ordered_dict3() for tx3 in hashable_block['account']]

    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())