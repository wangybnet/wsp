# encoding: utf-8

import xmlrpc.client

s = xmlrpc.client.ServerProxy('http://127.0.0.1:8090', allow_none=None)
print(s.get_config())
