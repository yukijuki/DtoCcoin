from collections import OrderedDict

from utility.printable import Printable

class Tagsaction(Printable):
    """A Tagsaction which can be added to a block in the blockchain.

    Attributes:
        :sender: The sender of the coins.
        :recipient: The recipient of the coins.
        :signature: The signature of the transaction.
        :tag: The hashtag.
    """
    def __init__(self, sender, signature, tag, spread):
        self.sender = sender
        self.signature = signature
        self.tag = tag
        self.spread = spread

    def to_ordered_dict1(self):
        """Converts this transaction into a (hashable) OrderedDict."""
        return OrderedDict([('sender', self.sender), ('tag', self.tag), ('spread', self.spread)])
