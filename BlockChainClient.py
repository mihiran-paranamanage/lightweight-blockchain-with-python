'''
title           : blockchain_client.py
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

import requests


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


def new_wallet():
	random_gen = Crypto.Random.new().read
	private_key = RSA.generate(1024, random_gen)
	public_key = private_key.publickey()

	return binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'), binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')

def generate_transaction(sender_address, sender_private_key, recipient_address, value):  
    transaction = Transaction(sender_address, sender_private_key, recipient_address, value)

    transaction_dict = transaction.to_dict()
    signature = transaction.sign_transaction()

    return transaction_dict, signature


wallet_exist = 0

while True:
    
    if (wallet_exist==0):
        print ("\nWallet Generation\n")
        permission_wallet = input('Would you like to generate a wallet ? (y/n) : ')
        if (permission_wallet=='y'):
            private_key, public_key = new_wallet()
            print ("\nPrivate Key : " + private_key)
            print ("\nPublic Key : " + public_key)
            wallet_exist = 1
        else:
            print ("\nBye !\n")
            break

    print ("\nTransactions\n")
    permission_trans = input('Do you need to make a transaction ? (y/n) : ')
    if (permission_trans=='y'):
        sender_address = public_key
        sender_private_key = private_key
        recipient_address = input('Recipient Address : ')
        value = input('Value : ')
        transaction_dict, signature = generate_transaction(sender_address, sender_private_key, recipient_address, value)
        print ("\nTransaction : " + str(transaction_dict))
        print ("\nSignature : " + signature)
        response = requests.get("http://127.0.0.1:9000/transactions/new", params={'sender_address': transaction_dict['sender_address'], 'recipient_address': transaction_dict['recipient_address'], 'value': transaction_dict['value'], 'signature': signature})
        print ()
        print (response.status_code, response.reason)
        print (response.json())
    else:
        print ("\nBye !\n")
        break
    





