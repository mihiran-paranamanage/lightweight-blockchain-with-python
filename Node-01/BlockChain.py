'''
title           : blockchain.py
description     : A blockchain implemenation
'''

from collections import OrderedDict
import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import threading
import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS


main_node = "127.0.0.1:5010"
main_node_port = 5010
MINING_DIFFICULTY = 2


class Blockchain:

    def __init__(self):
        #initial_token_owner = "30819f300d06092a864886f70d010101050003818d003081890281810093e23f8d9adc728b0154c366f0c76d18c9174111f59884a7eed710eef2496fdf4d97121b853c37f5c94d32492438d4b4bdf74f9d70b3ea81a9d1b3e3e6321ddfaffdb77b294e42bb38d3a65ab785fbbe2f5af4f5725ca5f90173a008f80d12e7eb055965a099b6399a451f953bded98664915f7617c7371d1575d7196603126f0203010001"
        #token = "SWITCHON"

        initial_token_owner = input('Token owner: ')
        token = input('Token: ')
        
        genesis_transaction = OrderedDict({'sender_address': "00", 
                                    'recipient_address': initial_token_owner,
                                    'value': token})
        self.transactions = []
        self.transactions.append(genesis_transaction)
        
        self.chain = []
        self.nodes = set()

        #Create genesis block
        genesis_block = self.create_block(0, '00')
        self.chain.append(genesis_block)


    def register_node(self, node_url):
        """
        Add a new node to the list of nodes
        """
        #Checking node_url has valid format
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def verify_transaction_sender(self, transaction):
        """
        Check that the provided sender corresponds to transaction
        have the token
        """
        for chain_block in reversed(self.chain):
            for chain_transaction in reversed(chain_block['transactions']):
                if chain_transaction['value']==transaction['value']:
                    
                    if chain_transaction['recipient_address']==transaction['sender_address']:
                        return 1
                    else:
                        return 0
        return -1


    def verify_transaction_signature(self, sender_address, signature, transaction):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        """
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        authenticated = verifier.verify(h, binascii.unhexlify(signature))
        print ("authenticated: ", authenticated)
        
        if authenticated:
            validated = self.verify_transaction_sender(transaction)
            print ("validated: ", validated)
            return validated

        return -2


    def submit_transaction(self, sender_address, recipient_address, value, signature):
        """
        Add a transaction to transactions array if the signature verified
        """
        transaction = OrderedDict({'sender_address': sender_address, 
                                    'recipient_address': recipient_address,
                                    'value': value})

        #Manages transactions from wallet to another wallet
        transaction_verification = self.verify_transaction_signature(sender_address, signature, transaction)
        if transaction_verification==1:
            self.transactions.append(transaction)
            if len(self.transactions) > 0:
                mine()
            return transaction_verification
        else:
            return transaction_verification


    def create_block(self, nonce, previous_hash):
        """
        Add a block of transactions to the blockchain
        """
        block = {'block_number': len(self.chain) + 1,
                'timestamp': time(),
                'transactions': self.transactions,
                'nonce': nonce,
                'previous_hash': previous_hash}
            
        # Reset the current list of transactions
        self.transactions = []

        # Add block to the blockchain
        self.chain.append(block)
        
        return block


    def hash(self, block):
        """
        Create a SHA-256 hash of a block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()


    def proof_of_work(self):
        """
        Proof of work algorithm
        """
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        nonce = 0
        while self.valid_proof(self.transactions, last_hash, nonce) is False:
            nonce += 1

        return nonce


    def valid_proof(self, transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
        """
        Check if a hash value satisfies the mining conditions. This function is used within the proof_of_work function.
        """
        guess = (str(transactions)+str(last_hash)+str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0'*difficulty


    def valid_chain(self, chain):
        """
        check if a bockchain is valid
        """
        return True


    def resolve_conflicts(self):
        """
        Resolve conflicts between blockchain's nodes
        by replacing our chain with the longest one in the network.
        """
        threading.Timer(10.0, self.resolve_conflicts).start()
        
        nodes = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in nodes:            
            response = requests.get('http://' + node + '/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

# Instantiate the Node
app = Flask(__name__)
CORS(app)

# Instantiate the Blockchain
blockchain = Blockchain()

# Synchronize nodes
blockchain.resolve_conflicts()

# Register Main Node
blockchain.register_node(main_node)


@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/configure')
def configure():
    return render_template('./configure.html')


@app.route('/transactions/new', methods=['GET'])
def new_transaction():
    data = request.args

    # Check that the required fields are in the data
    required = ['sender_address', 'recipient_address', 'value', 'signature']

    if not all(k in data for k in required):
        response = {'action': 'warning', 'message': 'Missing Values!'}

        return jsonify(response), 406

    transaction_result = blockchain.submit_transaction(data['sender_address'], data['recipient_address'], data['value'], data['signature'])

    if transaction_result==1:
        response = {'action': 'success', 'message': 'Action will be added to Blockchain'}
        return jsonify(response), 200

    elif transaction_result==0:
        response = {'action': 'danger', 'message': 'Action is not Authorized !'}
        return jsonify(response), 406

    elif transaction_result==-1:
        response = {'action': 'warning', 'message': 'Token does not exist !'}
        return jsonify(response), 406

    elif transaction_result==-2:
        response = {'action': 'danger', 'message': 'Action Authentication Failed !'}
        return jsonify(response), 406


@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    #Get transactions from transactions pool
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200   


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.chain[-1]
    nonce = blockchain.proof_of_work()

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(nonce, previous_hash)

    response = {
        'message': "New Block Forged",
        'block_number': block['block_number'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form
    nodes = values.get('nodes').replace(" ", "").split(',')

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': [node for node in blockchain.nodes],
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


@app.route('/nodes/get', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=main_node_port, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)







