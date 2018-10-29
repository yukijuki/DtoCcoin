from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('UI', "node.html")


@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys(): 
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving the keys failed.'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Loading the keys failed.'
        }
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message': 'Fetched balance successfully.',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'messsage': 'Loading balance failed.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route("/broadcast-transaction", methods=["POST"])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {"message": "no data found."}
        return jsonify(response), 400
    required = ["sender", "recipient", "amount", "spread", "signature"]
    if not all(key in values for key in required):
        response = {"message": "some data is missing"}
        return jsonify(response), 400
    success = blockchain.add_transaction(
    values["sender"], values["recipient"], values["signature"], values["amount"], values["spread"], is_recieving=True)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': values["sender"],
                'recipient': values["recipient"],
                'amount': values["amount"],
                'spread': values["spread"],
                'signature': values["signature"]
            },
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500

@app.route("/broadcast-tagsaction", methods=["POST"])
def broadcast_tagsaction():
    values = request.get_json()
    if not values:
        response = {"message": "no data found."}
        return jsonify(response), 400
    required = ["sender", "signature", "tag", "spread"]
    if not all(key in values for key in required):
        response = {"message": "some data is missing"}
        return jsonify(response), 400
    success = blockchain.add_tagsaction(
    values["sender"], values["signature"], values["tag"], values["spread"], is_recieving=True)
    if success:
        response = {
            'message': 'Successfully added tagsaction.',
            'tagsaction': {
                'sender': values["sender"],
                'tag': values["tag"],
                'spread': values["spread"],
                'signature': values["signature"]
            },
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a tagsaction failed.'
        }
        return jsonify(response), 500

@app.route("/broadcast-messsaction", methods=["POST"])
def broadcast_messsaction():
    values = request.get_json()
    if not values:
        response = {"message": "no data found."}
        return jsonify(response), 400
    required = ["sender", "recipient", "signature", "message", "tag", "amount", "spread"]
    if not all(key in values for key in required):
        response = {"message": "some data is missing"}
        return jsonify(response), 400
    success = blockchain.add_messsaction(
    values["sender"], values["recipient"], values["signature"], values["message"], values["tag"], values["amount"], values["spread"], is_recieving=True)
    if success:
        response = {
            'message': 'Successfully added messsaction.',
            'messsaction': {
                'sender': values["sender"],
                'recipient': values["recipient"],
                'signature': values["signature"],
                'message': values["message"],
                'tag': values["tag"],
                'amount': values["amount"],
                'spread': values["spread"]
            },
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a messsaction failed.'
        }
        return jsonify(response), 500    

@app.route("/broadcast-account", methods=["POST"])
def broadcast_account():
    values = request.get_json()
    if not values:
        response = {"message": "no data found."}
        return jsonify(response), 400
    required = ["sender", "pubkey", "signature", "spread"]
    if not all(key in values for key in required):
        response = {"message": "some data is missing"}
        return jsonify(response), 400
    success = blockchain.add_account(
    values["sender"], values["pubkey"], values["signature"], values["spread"], is_recieving=True)
    if success:
        response = {
            'message': 'Successfully added messsaction.',
            'messsaction': {
                'sender': values["sender"],
                'pubkey': values["pubkey"],
                'signature': values["signature"],
                'spread': values["spread"]
            },
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a messsaction failed.'
        }
        return jsonify(response), 500    

@app.route("/broadcast-block", methods=["POST"])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {"message": "no data found."}
        return jsonify(response), 400
    if "block" not in values:
        response = {"message": "some data is missing"}
        return jsonify(response), 400
    block = values["block"]
    if block["index"] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {"message": "Block added"}
            return jsonify(response), 201
        else:
            response = {"message": "Block seems invalid."}
            return jsonify(response), 500
    elif block["index"] > blockchain.chain[-1].index:
        pass
    else:
        response = {"message": "blockchain seems to be shorter, block not added"}
        return jsonify(response), 409


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400

    required_fields = ['recipient', 'amount', 'spread']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing.'
        }
        return jsonify(response), 400
    recipient = values['recipient']
    amount = values['amount']
    spread = values['spread']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount, spread)
    success = blockchain.add_transaction(wallet.public_key, recipient, signature, amount, spread)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'spread': spread,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500

@app.route('/tagsaction', methods=['POST'])
def add_tagsaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400

    required_fields = ['tag', 'spread']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing.'
        }
        return jsonify(response), 400
    tag = values['tag']
    spread = values['spread']
    signature = wallet.sign_tagsaction(wallet.public_key, tag, spread)
    success = blockchain.add_tagsaction(wallet.public_key, signature, tag, spread)
    if success:
        response = {
            'message': 'Successfully added tagsaction.',
            'tagsaction': {
                'sender': wallet.public_key,
                'tag': tag,
                'spread': spread,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a tagsaction failed.'
        }
        return jsonify(response), 500

@app.route('/messsaction', methods=['POST'])
def add_messsaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400

    required_fields = ['message', 'tag', 'amount', 'spread']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing.'
        }
        return jsonify(response), 400
    message = values['message']
    tag = values['tag']
    amount = values['amount']
    spread = values['spread']
    #show all the tag hodlers who are supposed to be sent the messages 
    blockchain.get_tag_holders(tag)
    #number of those who tagged themselves 
    recipient = len(blockchain.open_recipients)

    signature = wallet.sign_messsaction(wallet.public_key, recipient, message, tag, amount, spread)
    success = blockchain.add_messsaction(wallet.public_key, recipient, signature, message, tag, amount, spread)
    if success:
        response = {
            'message': 'Successfully added messsaction.',
            'messsaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'message': message,
                'tag': tag,
                'amount':amount,
                'spread': spread,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a messsaction failed.'
        }
        return jsonify(response), 500

@app.route('/account', methods=['POST'])
def add_account():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400

    required_fields = ['pubkey', 'spread']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing.'
        }
        return jsonify(response), 400
    pubkey = values['pubkey']
    spread = values['spread']
    signature = wallet.sign_account(wallet.public_key, pubkey, spread)
    success = blockchain.add_account(wallet.public_key, pubkey, signature, spread)
    if success:
        response = {
            'message': 'Successfully added account.',
            'account': {
                'sender': wallet.public_key,
                'pubkey': pubkey,
                'signature': signature,
                'spread': spread
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a account failed.'
        }
        return jsonify(response), 500

@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block()
    if block != None:
        dict_block = block.__dict__.copy()

        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
        dict_block['tagsactions'] = [
            tx.__dict__ for tx in dict_block['tagsactions']]
        dict_block['messsactions'] = [
            tx.__dict__ for tx in dict_block['messsactions']]
        dict_block['account'] = [
            tx.__dict__ for tx in dict_block['account']]

        response = {
            'message': 'Block added successfully.',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/transactions', methods=['GET'])
def get_open_transaction():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200

@app.route('/tagsactions', methods=['GET'])
def get_open_tagsaction():
    tagsactions = blockchain.get_open_tagsactions()
    dict_tagsactions = [tx.__dict__ for tx in tagsactions]
    return jsonify(dict_tagsactions), 200

@app.route('/messsactions', methods=['GET'])
def get_open_messsaction():
    messsactions = blockchain.get_open_messsactions()
    dict_messsactions = [tx.__dict__ for tx in messsactions]
    return jsonify(dict_messsactions), 200

@app.route('/account', methods=['GET'])
def get_open_account():
    account = blockchain.get_open_account()
    dict_account = [tx.__dict__ for tx in account]
    return jsonify(dict_account), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
        dict_block['tagsactions'] = [
            tx.__dict__ for tx in dict_block['tagsactions']]
        dict_block['messsactions'] = [
            tx.__dict__ for tx in dict_block['messsactions']]
        dict_block['account'] = [
            tx.__dict__ for tx in dict_block['account']]
    return jsonify(dict_chain), 200

@app.route("/node", methods=["POST"])
def add_node():
    values =request.get_json()
    if not values:
        response = {
            "message": "no data attached"

        }
        return jsonify(response), 400
    if "node" not in values:
        response = {
            "message": "no node data found"
        }
        return jsonify(response), 400
    node = values.get("node")
    blockchain.add_peer_node(node)
    response = {
        "message": "Node added successfully",
        "all_nodes": blockchain.get_peer_nodes()
    }
    return jsonify(response), 201

@app.route("/node/<node_url>", methods=["DELETE"])
def remove_node(node_url):
    if node_url == "" or node_url == None:
        response = {
            "message": "no node found"
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        "message": "Node removed",
        "all_nodes": blockchain.get_peer_nodes()
    }
    return jsonify(response), 201

@app.route("/nodes", methods=["GET"])
def get_nodes():
    nodes = blockchain.get_peer_nodes()
    response = {
        "all_nodes": nodes
    }
    return jsonify(response), 200

    
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port)
