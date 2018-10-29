from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii


class Wallet:
    """Creates, loads and holds private and public keys. Manages transaction signing and verification."""

    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None
        self.node_id = node_id

    def create_keys(self):
        """Create a new pair of private and public keys."""
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def save_keys(self):
        """Saves the keys to a file (wallet.txt)."""
        if self.public_key != None and self.private_key != None:
            try:
                with open('wallet-{}.txt'.format(self.node_id), mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
                print("saved sucessfully")
                return True
            except (IOError, IndexError):
                print('Saving wallet failed...')
                return False

    def load_keys(self):
        """Loads the keys from the wallet.txt file into memory."""
        try:
            with open('wallet-{}.txt'.format(self.node_id), mode='r') as f:
                keys = f.readlines()
                public_key = keys[0][:-1]
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
            print("keys loaded")
            return True
        except (IOError, IndexError):
            print('Loading wallet failed...')
            return False

    def generate_keys(self):
        """Generate a new pair of private and public key."""
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'), binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii'))

    def sign_transaction(self, sender, recipient, amount, spread):
        """Sign a transaction and return the signature.

        Arguments:
            :sender: The sender of the transaction.
            :recipient: The recipient of the transaction.
            :amount: The amount of the transaction.
        """
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(recipient) + str(amount) + str(spread)).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

    def sign_tagsaction(self, sender, tag, spread):
        """Sign a tagsaction and return the signature.

        Arguments:
            :sender: The sender of the transaction.
            :tag: The tag.
        """
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(tag) + str(spread)).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')   

    def sign_messsaction(self, sender, recipient, message, tag, amount, spread):
        """Sign a tagsaction and return the signature.

        Arguments:
            :sender: The sender of the transaction.
            :recipient: The recipient of the messsaction.
            :message: The sender of the message.
            :amount: The sender of spread.
        """
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(recipient) + str(message) + str(tag) + str(amount) + str(spread)).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')  

    def sign_account(self, sender, pubkey, spread):
        """Sign a tagsaction and return the signature."""

        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(pubkey) + str(spread)).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')   
     
    @staticmethod
    def verify_transaction(transaction):
        """Verify the signature of a transaction.

        Arguments:
            :transaction: The transaction that should be verified.
        """
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)+str(transaction.spread)).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(transaction.signature))

    @staticmethod
    def verify_tagsaction(tagsaction):
        """Verify the signature of a tagsaction.

        Arguments:
            :tagsaction: The tagsaction that should be verified.
        """
        public_key = RSA.importKey(binascii.unhexlify(tagsaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(tagsaction.sender) + str(tagsaction.tag) + str(tagsaction.spread)).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(tagsaction.signature))

    @staticmethod
    def verify_messsaction(messsaction):
        """Verify the signature of a messsaction.

        Arguments:
            :messsaction: The messsaction that should be verified.
        """
        public_key = RSA.importKey(binascii.unhexlify(messsaction.sender))
        veri = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(messsaction.sender) + str(messsaction.recipient) + str(messsaction.message) + str(messsaction.tag) + str(messsaction.amount) + str(messsaction.spread)).encode('utf8'))
        return veri.verify(h, binascii.unhexlify(messsaction.signature))
    
    @staticmethod
    def verify_account(account):
        """Verify the signature of a account.

        Arguments:
            :account: The transaction that should be verified.
        """
        public_key = RSA.importKey(binascii.unhexlify(account.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(account.sender) + str(account.pubkey) + str(account.spread)).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(account.signature))