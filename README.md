# Lightweight Blockchain with Python

This application is developed as a university project to demonstrate the blockchain transaction flow and how it works in a high level programming language like python.

### Languages & Tools
* Python
* Flask
* RSA encryption
* SHA hashing

### Installation

1. Clone the repo _lightweight-blockchain-with-python_.
2. Install required dependancy libraries (pycryptodome, flask, flask_cors) with pip3.
3. Go inside the _lightweight-blockchain-with-python/Node-01_ folder.
4. Run `python BlockChainClient.py`
5. Browse http://127.0.0.1:4010
6. Do the same for Node-02, Node-03 folders and browse http://127.0.0.1:4020, http://127.0.0.1:4030 respectively in seperate terminals.
7. Open another terminal and go to _lightweight-blockchain-with-python/Node-01_ folder.
8. Run `python BlockChain.py`
9. It will ask you to enter "Token owner" and "Token". This Token owner is the initial owner of the token so, for example, you can give Node-01 client's Public Key which can be seen in the http://127.0.0.1:4010 browser.
10. Browse http://127.0.0.1:5010/
11. Do the same for Node-02, Node-03 folders and browse http://127.0.0.1:5020, http://127.0.0.1:5030 respectively in seperate terminals.

### Usage

* After the installation, now you have 6 terminals as 3 for clients and 3 for node servers. 
* And also, now the token owner is Node-01 as you have given Node-01 client's Public Key before as initial token.
* If you want to send that token to the Node-02 client, just put Node-02 Public Key as the Recipient Address, your token as the Token and click _Generate Transaction_ button.

### Demo

* [Click here](https://mihiran-paranamana.github.io/nft-marketplace-react-bootstrap/)
