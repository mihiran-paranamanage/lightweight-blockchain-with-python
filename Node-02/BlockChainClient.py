'''
title           : BlockchainClient.py
description     : A blockchain client implemenation, with the following features
                  - Wallets generation using Public/Private key encryption (based on RSA algorithm)
                  - Generation of transactions with RSA encryption
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


main_node = "127.0.0.1:5020"
client_port = 4020


class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.value = value

    def __getattr__(self, attr):
        return self.data[attr]

    def to_dict(self):
        return OrderedDict({'sender_address': self.sender_address,
                            'recipient_address': self.recipient_address,
                            'value': self.value})

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')


# Instantiate the Node
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('./make_transaction.html')

@app.route('/wallet/new', methods=['GET'])
def new_wallet():
	random_gen = Crypto.Random.new().read
	private_key = RSA.generate(1024, random_gen)
	public_key = private_key.publickey()

	private_key = binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii')
	public_key = binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')

	response = {'private_key': private_key, 'public_key': public_key}
	return jsonify(response), 200

@app.route('/transaction/generate', methods=['GET'])
def generate_transaction():
    data = request.args
    response2 = ''
    response3 = ''

    transaction = Transaction(data['sender_address'], data['sender_private_key'], data['recipient_address'], data['value'])

    transaction_dict = transaction.to_dict()
    signature = transaction.sign_transaction()

    response = requests.get("http://"+ main_node +"/nodes/get")
    print(response.json()['nodes'])

    for node in response.json()['nodes']:
        response2 = requests.get("http://" + node + "/transactions/new", params={'sender_address': transaction_dict['sender_address'], 'recipient_address': transaction_dict['recipient_address'], 'value': transaction_dict['value'], 'signature': signature})
        if(response2.json()['action'] == 'success'):
            response3 = response2

    if response3:
        return jsonify(response3.json()), 200
    return jsonify(response2.json()), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=client_port, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
