from uuid import uuid4

from blockchain import Blockchain
from utility.verification import Verification
from wallet import Wallet

class Node:
    """The node which runs the local blockchain instance.
    
    Attributes:
        :id: The id of the node.
        :blockchain: The blockchain which is run by this node.
    """
    def __init__(self):
        # self.id = str(uuid4())
        self.wallet = Wallet("node")
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key, "node")

    def get_transaction_value(self):
        """ Returns the input of the user (a new transaction amount) as a float. """
        # Get the user input, transform it from a string to a float and store it in user_input
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Your transaction amount please: '))
        tx_spread = float(input('Your transaction spread please: '))       
        return tx_recipient, tx_amount, tx_spread
    
    def get_pubkey(self):
        """ Returns the pubkey that is supposed to be the private account. """
        # Get the user input, transform it from a string to a float and store it in user_input
        tx_recipient = input('Enter the Pubkey: ')
        spread_amount = float(input('Your transaction spread please: '))
        return tx_recipient, spread_amount

    def get_tagsaction_value(self):
        """ Returns the input of the user (a new tagsaction tag)"""
        # Get the user input, transform it from a string to a float and store it in user_input
        tag = input('Enter any type of tag: ')
        tag_amount = float(input('Your transaction spread please: '))
        return tag, tag_amount

    def get_messsactions_value(self):
        """ Returns the input of the user (a new message)"""
        # Get the user input, transform it from a string to a float and store it in user_input
        tag = input('Enter any type of tag: ')
        message = input('Enter any type of message: ')
        spend_amount = float(input('Your transaction amount please: '))
        spread_amount = float(input('Your transaction spread please: '))
        return tag, message, spend_amount, spread_amount
    
    def get_user_choice(self):
        """Prompts the user for its choice and return it."""
        user_input = input('Your choice: ')
        return user_input

    def print_blockchain_elements(self):
        """ Output all blocks of the blockchain. """
        # Output the blockchain list to the console
        for block in self.blockchain.chain:
            print('Outputting Block')
            print(block)
        else:
            print('-' * 20)

    def listen_for_input(self):
        """Starts the node and waits for user input."""
        waiting_for_input = True

        # A while loop for the user input interface
        # It's a loop that exits once waiting_for_input becomes False or when break is called
        while waiting_for_input:
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain blocks')
            print('4: check the transaction validity')
            print('5: Create wallet')
            print('6: Load wallet')
            print('7: Save keys')
            print('8: Send messages')
            print('9: Create a tag')
            print('d: Create a private account')
            print('f: メッセージの表示')
            print('q: Quit')
            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount, spread = tx_data
                # Add the transaction amount to the blockchain
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount, spread)
                if self.blockchain.add_transaction(self.wallet.public_key, recipient, signature, amount, spread):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                if not self.blockchain.mine_block():
                    print('Mining failed. Got no wallet?')
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                self.blockchain.check()
            elif user_choice == '5':
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key, "node")
            elif user_choice == '6':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key, "node")
            elif user_choice == '7':
                self.wallet.save_keys()
            elif user_choice == '8':
                info = self.get_messsactions_value()
                hashtg, message, amount, spread= info
                self.blockchain.get_tag_holders(hashtg)
                recipient = len(self.blockchain.open_recipients)
                signature = self.wallet.sign_messsaction(self.wallet.public_key, recipient, message, hashtg, amount, spread)
                if self.blockchain.add_messsaction(self.wallet.public_key, recipient, signature, message, hashtg, amount, spread):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
            elif user_choice == '9':
                print(self.blockchain.show_tag())
                tag_data = self.get_tagsaction_value()
                tag, spread = tag_data
                # Add the tagsaction amount to the blockchain
                signature = self.wallet.sign_tagsaction(self.wallet.public_key, tag, spread)
                if self.blockchain.add_tagsaction(self.wallet.public_key, signature, tag, spread):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
            elif user_choice == 'd':
                tag_data = self.get_pubkey()
                pubkey, spread = tag_data
                signature = self.wallet.sign_account(self.wallet.public_key, pubkey, spread)
                if self.blockchain.add_account(self.wallet.public_key, pubkey, signature, spread):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')  
            elif user_choice == 'f':
                print(self.blockchain.recieve_message)    
            elif user_choice == 'q':
                # This will lead to the loop to exist because it's running condition becomes False
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list!')
                
            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print('Invalid blockchain!')
                # Break out of the loop
                break
            print('Balance of {}: {:6.2f}'.format(self.wallet.public_key, self.blockchain.get_balance()))
        else:
            print('User left!')

        print('Done!')

if __name__ == '__main__':
    node = Node()
    node.listen_for_input()
