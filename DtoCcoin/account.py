from collections import OrderedDict

from utility.printable import Printable

class Account(Printable):

    def __init__(self, sender, pubkey, signature, spread):
        self.sender = sender
        self.pubkey = pubkey
        self.signature = signature
        self.spread = spread

    def to_ordered_dict3(self):
        """Converts this transaction into a (hashable) OrderedDict."""
        return OrderedDict([('sender', self.sender), ('pubkey', self.pubkey), ('spread', self.spread)])