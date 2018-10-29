"""Provides verification helper methods."""

from utility.hash_util import hash_string_256, hash_block
from wallet import Wallet

class Verification:
    """A helper class which offer various static and class-based verification and validation methods."""
    @staticmethod
    def valid_proof(transactions, tagsactions, messsactions, account, last_hash, proof):
        """Validate a proof of work number and see if it solves the puzzle algorithm (two leading 0s)

        Arguments:
            :transactions: The transactions of the block for which the proof is created.
            :last_hash: The previous block's hash which will be stored in the current block.
            :proof: The proof number we're testing.
        """
        # Create a string with all the hash inputs
        guess = (str([tx.to_ordered_dict() for tx in transactions])
               + str([tx.to_ordered_dict1() for tx in tagsactions])
               + str([tx.to_ordered_dict2() for tx in messsactions])
               + str([tx.to_ordered_dict3() for tx in account]) 
               + str(last_hash) + str(proof)).encode()
        # Hash the string
        # IMPORTANT: This is NOT the same hash as will be stored in the previous_hash. It's a not a block's hash. It's only used for the proof-of-work algorithm.
        guess_hash = hash_string_256(guess)
        # Only a hash (which is based on the above inputs) which starts with two 0s is treated as valid
        # This condition is of course defined by you. You could also require 10 leading 0s - this would take significantly longer (and this allows you to control the speed at which new blocks can be added)
        return guess_hash[0:2] == '00'
        
    @classmethod
    def verify_chain(cls, blockchain):
        """ Verify the current blockchain and return True if it's valid, False otherwise."""
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                print("previous hash not right")
                return False
            if not cls.valid_proof(block.transactions[:-1], block.tagsactions, block.messsactions, block.account, block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        """Verify a transaction by checking whether the sender has sufficient coins.

        Arguments:
            :transaction: The transaction that should be verified.
        """
        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return sender_balance >= transaction.amount and sender_balance >= transaction.spread and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @staticmethod
    def verify_tagsaction(tagsaction, get_balance, check_funds=True):
        """Verify a transaction by checking whether the sender has sufficient coins.

        Arguments:
            :transaction: The transaction that should be verified.
        """
        if check_funds:
            sender_balance = get_balance(tagsaction.sender)
            return sender_balance >= tagsaction.spread and Wallet.verify_tagsaction(tagsaction)
        else:
            return Wallet.verify_tagsaction(tagsaction)

    @staticmethod
    def verify_messsaction(messsaction, get_balance, check_funds=True):
        """Verify a transaction by checking whether the sender has sufficient coins.

        Arguments:
            :transaction: The transaction that should be verified.
        """
        if check_funds:
            sender_balance = get_balance(messsaction.sender)
            return sender_balance >= messsaction.spread and sender_balance >= messsaction.amount and Wallet.verify_messsaction(messsaction)
        else:
            return Wallet.verify_messsaction(messsaction)

    @staticmethod
    def verify_account(account, get_balance, check_funds=True):
        """Verify a transaction by checking whether the sender has sufficient coins.

        Arguments:
            :transaction: The transaction that should be verified.
        """
        if check_funds:
            sender_balance = get_balance(account.sender)
            return sender_balance >= account.spread and Wallet.verify_account(account)
        else:
            return Wallet.verify_account(account)

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        """Verifies all open transactions."""
        return all([cls.verify_tagsaction(tx, get_balance, False) for tx in open_transactions])
        

    @classmethod
    def verify_tagsactions(cls, open_tagsactions, get_balance):
        """Verifies all open tagsactions."""
        return all([cls.verify_tagsaction(tx1, get_balance, False) for tx1 in open_tagsactions])

    @classmethod
    def verify_messsactions(cls, open_messsactions, get_balance):
        """Verifies all open tagsactions."""
        return all([cls.verify_messsaction(tx1, get_balance, False) for tx1 in open_messsactions])