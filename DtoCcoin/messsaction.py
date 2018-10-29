from collections import OrderedDict

from utility.printable import Printable

class Messsaction(Printable):
    """A transaction which can be added to a block in the blockchain.

    Attributes:
        :sender: The sender of the coins.
        :recipient: The recipient of the coins.
        :signature: The signature of the transaction.
        :message: The advertising message.
        :amount: The amount of coins sent.
    """
    def __init__(self, sender, recipient, signature, message, tag, amount, spread):
        self.sender = sender
        self.recipient = recipient
        self.signature = signature
        self.message = message
        self.tag = tag
        self.amount = amount
        self.spread = spread

    def to_ordered_dict2(self):
        """Converts this transaction into a (hashable) OrderedDict."""
        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('message', self.message), ('tag', self.tag), ('amount', self.amount), ('spread', self.spread)])