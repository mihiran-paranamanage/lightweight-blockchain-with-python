'''
title           : BlockChainMine.py
description     : BlockChain Mine process will mine blocks at every 30 mins
'''

import requests
import threading


def automine():
    threading.Timer(5.0, automine).start()

    response = requests.get("http://127.0.0.1:9000/mine", params={})
    print ()
    print (response.status_code, response.reason)
    print (response.json())


automine()
