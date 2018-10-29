from functools import reduce
import hashlib as hl

import json
import pickle
import requests

# Import two functions from our hash_util.py file. Omit the ".py" in the import
from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction
from tagsaction import Tagsaction
from messsaction import Messsaction
from account import Account
from wallet import Wallet


print(__name__)

class Blockchain:
    """The Blockchain class manages the chain of blocks as well as open transactions and the node on which it's running.
    
    Attributes:
        :chain: The list of blocks
        :open_transactions (private): The list of open transactions
        :hosting_node: The connected node (which runs the blockchain).
    """
    def __init__(self, hosting_node_id, node_id):
        """The constructor of the Blockchain class."""
        # Our starting block for the blockchain
        genesis_block = Block(0, '', [], [], [], [], 100, 0)
        # Initializing our (empty) blockchain list
        self.chain = [genesis_block]
        # Unhandled transactions
        self.__open_transactions = []
        self.__open_tagsactions = []
        self.__open_messsactions = []
        self.open_recipients = []
        self.__open_account = []
        self.hosting_node = hosting_node_id
        self.node_id = node_id
        self.__peer_nodes = set()
        self.load_data()
        

    # This turns the chain attribute into a property with a getter (the method below) and a setter (@chain.setter)
    @property
    def chain(self):
        return self.__chain[:]

    # The setter for the chain property
    @chain.setter 
    def chain(self, val):
        self.__chain = val


    def get_open_transactions(self):
        """Returns a copy of the open transactions list."""
        return self.__open_transactions[:]

    def get_open_tagsactions(self):
        """Returns a copy of the open tagsactions list."""
        return self.__open_tagsactions[:]
    
    def get_open_messsactions(self):
        """Returns a copy of the open messsactions list."""
        return self.__open_messsactions[:]   

    def get_open_account(self):
        """Returns a copy of the open messsactions list."""
        return self.__open_account[:]   


    def load_data(self):
        """Initialize blockchain + open transactions data from a file."""
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as f:
                # file_content = pickle.loads(f.read())
                file_content = f.readlines()
                # blockchain = file_content['chain']
                # open_transactions = file_content['ot']
                blockchain = json.loads(file_content[0][:-1])
                # We need to convert  the loaded data because Transactions should use OrderedDict
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount'], tx['spread']) for tx in block['transactions']]
                    converted_tag = [Tagsaction(
                        tx['sender'], tx['signature'], tx['tag'], tx['spread']) for tx in block['tagsactions']]
                    converted_message = [Messsaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['message'], tx['tag'], tx['amount'], tx['spread']) for tx in block['messsactions']]
                    converted_account = [Account(
                        tx['sender'], tx['pubkey'], tx['signature'], tx['spread']) for tx in block['account']]

                    updated_block = Block(
                        block['index'], block['previous_hash'], converted_tx, converted_tag, converted_message, converted_account, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain

                open_transactions = json.loads(file_content[1][:-1])
                # We need to convert  the loaded data because Transactions should use OrderedDict
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount'], tx['spread'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                
                open_tagsactions = json.loads(file_content[2][:-1])
                # We need to convert  the loaded data because Tagsaction should use OrderedDict
                updated_tagsactions = []
                for tag in open_tagsactions:
                    updated_tagsaction = Tagsaction(
                        tag['sender'], tag['signature'], tag['tag'], tag['spread'])
                    updated_tagsactions.append(updated_tagsaction)
                self.__open_tagsactions = updated_tagsactions

                open_messsactions = json.loads(file_content[3][:-1])
                # We need to convert  the loaded data because Messsaction should use OrderedDict
                updated_messsactions = []
                for mes in open_messsactions:
                    updated_messsaction = Messsaction(
                        mes['sender'], mes['recipient'], mes['signature'], mes['message'], mes['tag'], mes['amount'], mes['spread'])
                    updated_messsactions.append(updated_messsaction)
                self.__open_messsactions = updated_messsactions

                open_account = json.loads(file_content[4][:-1])
                # We need to convert  the loaded data because Account should use OrderedDict
                updated_accounts = []
                for mes in open_account:
                    updated_account = Account(
                        mes['sender'], mes['pubkey'], mes['signature'], mes['spread'])
                    updated_accounts.append(updated_account)
                self.__open_account = updated_accounts

                peer_nodes = json.loads(file_content[5])
                self.__peer_nodes = set(peer_nodes)                         

        except (IOError, IndexError):
            pass
        finally:
            print('Cleanup!')

    def save_data(self):
        """Save blockchain + open transactions snapshot to a file."""
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
                saveable_chain = [block.__dict__ for block in 
                [Block(block_el.index, block_el.previous_hash, 
                [tx.__dict__ for tx in block_el.transactions], 
                [tx1.__dict__ for tx1 in block_el.tagsactions],
                [tx2.__dict__ for tx2 in block_el.messsactions],
                [tx3.__dict__ for tx3 in block_el.account],
                block_el.proof, 
                block_el.timestamp) for block_el in self.__chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')

                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                f.write('\n')

                saveable_tag = [tag.__dict__ for tag in self.__open_tagsactions]
                f.write(json.dumps(saveable_tag))
                f.write('\n')

                saveable_mes = [mes.__dict__ for mes in self.__open_messsactions]
                f.write(json.dumps(saveable_mes))
                f.write('\n')

                saveable_acc = [acc.__dict__ for acc in self.__open_account]
                f.write(json.dumps(saveable_acc))
                f.write('\n')

                f.write(json.dumps(list(self.__peer_nodes)))
        except IOError:
            print('Saving failed!')

    def proof_of_work(self):
        """Generate a proof of work for the open transactions, the hash of the previous block and a random number (which is guessed until it fits)."""
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        # Try different PoW numbers and return the first valid one
        while not Verification.valid_proof(self.__open_transactions, self.__open_tagsactions, self.__open_messsactions, self.__open_account, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self, sender=None):
        """Calculate and return the balance for a participant.
        """
        if sender == None:
            if self.hosting_node == None:
                return None
            participant = self.hosting_node
        else:
            participant = sender
        #transaction amount sent
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount
                          for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        print("transaction amount")
        print(tx_sender)       
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                             if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

        #tagsaction spread sent
        tx_sender1 = [[tx.spread for tx in block.tagsactions
                      if tx.sender == participant] for block in self.__chain]
        open_tx_sender1 = [tx.spread
                          for tx in self.__open_tagsactions if tx.sender == participant]
        tx_sender1.append(open_tx_sender1)
        print("tagsaction spread")
        print(tx_sender1)
        amount_sent1 = reduce(lambda tx_sum1, tx_amt1: tx_sum1 + sum(tx_amt1)
                             if len(tx_amt1) > 0 else tx_sum1 + 0, tx_sender1, 0)

        #messsaction amount sent
        tx_sender2 = [[tx.amount for tx in block.messsactions
                      if tx.sender == participant] for block in self.__chain]
        open_tx_sender2 = [tx.amount
                          for tx in self.__open_messsactions if tx.sender == participant]
        tx_sender2.append(open_tx_sender2)
        print("messsaction amount")
        print(tx_sender2)
        amount_sent2 = reduce(lambda tx_sum2, tx_amt2: tx_sum2 + sum(tx_amt2)
                             if len(tx_amt2) > 0 else tx_sum2 + 0, tx_sender2, 0)
        print("messsaction amount total CHECK HERE")
        print(amount_sent2)

        #transaction spread sent
        tx_sender3 = [[tx.spread for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]
        open_tx_sender3 = [tx.spread
                          for tx in self.__open_transactions if tx.sender == participant]
        tx_sender3.append(open_tx_sender3)
        print("transaction spread")
        print(tx_sender3)       
        amount_sent3 = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                             if len(tx_amt) > 0 else tx_sum + 0, tx_sender3, 0)

        #messsaction spread sent
        tx_sender4 = [[tx.spread for tx in block.messsactions
                      if tx.sender == participant] for block in self.__chain]
        open_tx_sender4 = [tx.spread
                          for tx in self.__open_messsactions if tx.sender == participant]
        tx_sender4.append(open_tx_sender4)
        print("messsaction spread")
        print(tx_sender4)
        amount_sent4 = reduce(lambda tx_sum2, tx_amt2: tx_sum2 + sum(tx_amt2)
                             if len(tx_amt2) > 0 else tx_sum2 + 0, tx_sender4, 0)
        print("messsaction spread total CHECK HERE")
        print(amount_sent4)

        #account spread sent
        tx_sender5 = [[tx.spread for tx in block.account
                      if tx.sender == participant] for block in self.__chain]
        open_tx_sender5 = [tx.spread
                          for tx in self.__open_account if tx.sender == participant]
        tx_sender5.append(open_tx_sender5)
        print("Account spread")
        print(tx_sender5)
        amount_sent5 = reduce(lambda tx_sum2, tx_amt2: tx_sum2 + sum(tx_amt2)
                             if len(tx_amt2) > 0 else tx_sum2 + 0, tx_sender5, 0)
        print("Account amount total")
        print(amount_sent5)




        # This fetches received coin amounts of every transactions that were already included in blocks of the blockchain
        print("___Total amount recieved___")


        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant] for block in self.__chain]
        print('transactions amount recieved')
        print(tx_recipient)
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                                 if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
            

        #identify the message sender and sende it to those who r tagged
        thetag = [tx.tag for block in self.__chain for tx in block.tagsactions if tx.sender == participant]
        print('1')
        print(thetag)
        
        mess_sender = [tx.sender for block in self.__chain for tx in block.messsactions if tx.tag in thetag]
        print('2')        
        print(mess_sender)
        
        tx_recipient1 = [tx.amount/tx.recipient for block in self.__chain for tx in block.messsactions if tx.sender in mess_sender]
        print('3')        
        print(tx_recipient1)

        amount_received1 = reduce(lambda tx_sum, tx_amt: tx_sum + (tx_amt)
                                if tx_amt > 0 else tx_sum + 0, tx_recipient1, 0)
        print("amount recieved")
        print(amount_received1)

        
        received_total = amount_received + amount_received1 
        sent_total = amount_sent + amount_sent1 + amount_sent2 + amount_sent3 + amount_sent4 + amount_sent5
        print("Final result checking")
        print("recived total amount")
        print(received_total)
        print("recived total amount")
        print(sent_total)
        # Return the total balance
        return received_total - sent_total 


    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    # This function accepts two arguments.
    # One required one (transaction_amount) and one optional one (last_transaction)
    # The optional one is optional because it has a default value => [1]

    def add_transaction(self, sender, recipient, signature, amount, spread, is_recieving=False):
        """ Append a new value as well as the last blockchain value to the blockchain.

        Arguments:
            :sender: The sender of the coins.
            :recipient: The recipient of the coins.
            :amount: The amount of coins sent with the transaction (default = 1.0)
        """

        #if self.hosting_node == None:
        #    return False

        transaction = Transaction(sender, recipient, signature, amount, spread)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_recieving:
                for node in self.__peer_nodes:
                    url = "http://{}/broadcast-transaction".format(node)
                    try:
                        response = requests.post(url, json={"sender": sender, "recipient": recipient, "amount": amount, "spread": spread, "signature": signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print("Transaction declined, needs resolving")
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def add_messsaction(self, sender, recipient, signature, message, tag, amount, spread, is_recieving=False):
        """ Append a new value as well as the last blockchain value to the blockchain.

        Arguments:
            :sender: The sender of the coins.
            :recipient: The recipient of the coins.
            :amount: The amount of coins sent with the transaction (default = 1.0)
        """
        #if self.hosting_node == None:
        #    return False

        messsaction = Messsaction(sender, recipient, signature, message, tag, amount, spread)

        if Verification.verify_messsaction(messsaction, self.get_balance):
            self.__open_messsactions.append(messsaction)
            self.save_data()
            if not is_recieving:
                for node in self.__peer_nodes:
                    url = "http://{}/broadcast-messsaction".format(node)
                    try:
                        response = requests.post(url, json={'sender': sender,
                    'recipient': recipient,
                    'message': message,
                    'tag': tag,
                    'amount':amount,
                    'spread': spread,
                    'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print("Messsaction declined, needs resolving")
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False   

    def check(self):       
        tag_user = [[tx.tag for tx in block.tagsactions if tx.sender == self.hosting_node] for block in self.__chain]
        print('messsaction tag sender')
        print(tag_user)
        
        mess_sender = [[tx.sender for tx in block.messsactions if tx.tag in tag_user] for block in self.__chain]
        tx_recipient1 = [[tx.amount for tx in block.messsactions if tx.sender in mess_sender] for block in self.__chain]

        print('messsaction amount recieved')        
        print(tx_recipient1)
        amount_received1 = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                                if len(tx_amt) > 0 else tx_sum + 0, tx_recipient1, 0)
        print("amount recieved")
        print(amount_received1)

    def add_tagsaction(self, sender, signature, tag, spread, is_recieving=False):
        """ Append a new value as well as the last blockchain value to the blockchain.

        Arguments:
            :sender: The sender of the coins.
            :tag: The tag.
            :amount: The amount of coins sent with the transaction (default = 1.0)
        """
        #if self.hosting_node == None:
        #    return False
        
        hashtag = Tagsaction(sender, signature, tag, spread)
        if Verification.verify_tagsaction(hashtag, self.get_balance):
            self.__open_tagsactions.append(hashtag)
            self.save_data()
            if not is_recieving:
                for node in self.__peer_nodes:
                    url = "http://{}/broadcast-tagsaction".format(node)
                    try:
                        response = requests.post(url, json={
                    'sender': sender,
                    'tag': tag,
                    'spread': spread,
                    'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print("Tagsaction declined, needs resolving")
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False    

    def add_account(self, sender, pubkey, signature, spread, is_recieving=False):
        """ Add a private account.

        Arguments:
            :sender: The sender of the coins.
            :tag: The tag.
            :amount: The amount of coins sent with the transaction (default = 1.0)
        """
        #if self.hosting_node == None:
        #    return False
        
        account = Account(sender, pubkey, signature, spread)
        if Verification.verify_account(account, self.get_balance):
            self.__open_account.append(account)
            self.save_data()
            if not is_recieving:
                for node in self.__peer_nodes:
                    url = "http://{}/broadcast-account".format(node)
                    try:
                        response = requests.post(url, json={
                    'sender': sender,
                    'pubkey': pubkey,
                    'spread': spread,
                    'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print("Account creation declined, needs resolving")
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False        

    def show_tag(self):
        """ Get all the tags from blockchain"""
        hashtag = [[tx.tag for tx in block.tagsactions] for block in self.__chain]
        return hashtag   
    
    def get_tag_holders(self, hashtag):
        tag_sender = [[tx.sender for tx in block.tagsactions if tx.tag == hashtag] for block in self.__chain]
        tagon = list(filter(None, tag_sender))
        print("tag holder")
        print(tagon)
        private_account = [[tx.pubkey for tx in block.account] for block in self.__chain]
        print("private account")
        print(private_account)
        for taggy in tagon:    
            if taggy not in private_account:
                print(taggy)
                self.open_recipients.append(taggy)

    
    def recieve_message(self):
        """show_message = [[tx.message for tx in block.messsactions] for block in self.__chain]
        message = list(filter(None, show_message))
        return message"""

    def mine_block(self):
        """Create a new block and add open transactions to it."""
        # Fetch the currently last block of the blockchain
        if self.hosting_node == None:
            return None
        last_block = self.__chain[-1]
        # Hash the last block (=> to be able to compare it to the stored hash value)
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()

        # The reward we give to miners (for creating a new block)
        spready = [tx.spread for tx in self.__open_transactions]
        print("open transaction spread total")
        print(spready)
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, spready, 0)
        print(amount_received)

        
        spready1 = [tx1.spread for tx1 in self.__open_tagsactions]
        amount_received1 = reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, spready1, 0)
        print("open tagsaction spread total")
        print(spready1)
        print(amount_received1)

        spready2 = [tx2.spread for tx2 in self.__open_messsactions]
        amount_received2 = reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, spready2, 0)
        print("open messsaction spread total")
        print(spready2)

        spready3 = [tx3.spread for tx3 in self.__open_account]
        amount_received3 = reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, spready3, 0)
        print("open account spread total")
        print(spready2)

        MIMNING_SPREAD = amount_received + amount_received1 + amount_received2 + amount_received3
        print("MINING SPREAD")
        print(MIMNING_SPREAD)
        
        MINING_REWARD = 10 +  MIMNING_SPREAD
        # Miners should be rewarded, so let's create a reward transaction
        # reward_transaction = {
        #     'sender': 'MINING',
        #     'recipient': owner,
        #     'amount': MINING_REWARD
        # }
        reward_transaction = Transaction('MINING', self.hosting_node, '', MINING_REWARD, 0)

        # Copy transaction instead of manipulating the original open_transactions list
        # This ensures that if for some reason the mining should fail, we don't have the reward transaction stored in the open transactions
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)
        
        copied_tagsactions = self.__open_tagsactions[:]
        for tag in copied_tagsactions:
            if not Wallet.verify_tagsaction(tag):
                return None

        copied_messsactions = self.__open_messsactions[:]
        for mes in copied_messsactions:
            if not Wallet.verify_messsaction(mes):
                return None

        copied_account = self.__open_account[:]
        for acc in copied_account:
            if not Wallet.verify_account(acc):
                return None

        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, copied_tagsactions, copied_messsactions, copied_account, proof)

        self.__chain.append(block)
        self.__open_transactions = []
        self.__open_tagsactions = []
        self.__open_messsactions = []
        self.__open_account = []
        self.save_data()
        for node in self.__peer_nodes:
            url = "http://{}/broadcast-block".format(node)
            converted_block = block.__dict__.copy()
            converted_block["transactions"] = [tx.__dict__ for tx in converted_block["transactions"]]
            converted_block["tagsactions"] = [tx.__dict__ for tx in converted_block["tagsactions"]]
            converted_block["messsactions"] = [tx.__dict__ for tx in converted_block["messsactions"]]
            converted_block["account"] = [tx.__dict__ for tx in converted_block["account"]]
        
            try:
                response = requests.post(url, json={"sender": converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print("Transaction declined, needs resolving")
            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_block(self, block):
        transactions = [Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount'], tx['spread']) for tx in block['transactions']]
        tagsactions = [Tagsaction(
                        tx['sender'], tx['signature'], tx['tag'], tx['spread']) for tx in block['tagsactions']]
        messsactions = [Messsaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['message'], tx['tag'], tx['amount'], tx['spread']) for tx in block['messsactions']]
        account = [Account(
                        tx['sender'], tx['pubkey'], tx['signature'], tx['spread']) for tx in block['account']]

        proof_is_valid = Verification.valid_proof(
            transactions[:-1], tagsactions, messsactions, account, block["previous_hash"], block["proof"])
        hashes_match = hash_block(self.chain[-1]) == block["previous_hash"]
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(block["index"], block["previous_hash"], transactions, tagsactions, messsactions, account, block["proof"], block["timestamp"])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        stored_tagsactions = self.__open_tagsactions[:]
        stored_messsactions = self.__open_messsactions[:]
        stored_account = self.__open_account[:]

        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] and opentx.signature == itx['signature'] and opentx.amount == itx['amount'] and opentx.spread == itx['spread']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')

        for itx in block['tagsactions']:
            for opentx in stored_tagsactions:
                if opentx.sender == itx['sender'] and opentx.signature == itx['signature'] and opentx.tag == itx['tag'] and opentx.spread == itx['spread']:
                    try:
                        self.__open_tagsactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')

        for itx in block['messsactions']:
            for opentx in stored_messsactions:
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] and opentx.signature == itx['signature'] and opentx.message == itx['message'] and opentx.tag == itx['tag'] and opentx.amount == itx['amount'] and opentx.spread == itx['spread']:
                    try:
                        self.__open_messsactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')

        for itx in block['account']:
            for opentx in stored_account:
                if opentx.sender == itx['sender'] and opentx.pubkey == itx['pubkey'] and opentx.signature == itx['signature'] and opentx.spread == itx['spread']:
                    try:
                        self.__open_account.remove(opentx)
                    except ValueError:
                        print('Item was already removed')

        self.save_data()
        return True

    def add_peer_node(self, node):
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        return list(self.__peer_nodes)