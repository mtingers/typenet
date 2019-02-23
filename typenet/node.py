import time
import pickle
import socket
from .util import send_msg, recv_msg

class ServerConnectionFailure(Exception):
   pass

class Node(object):
    def __init__(self, name, host, port, max_retry=100):
        self.name = name
        self.host = host
        self.port = port
        self.sock = None
        self.max_retry = max_retry

    def _connect(self):
        if self.sock is not None:
            return self.sock
        tries = 0
        while 1:
            if tries > self.max_retry:
                raise ServerConnectionFailure('Failed to connect to server %s:%s in %d attempts' % (
                    self.host, self.port, tries))
            try:
                self.sock = socket.create_connection((self.host, self.port), timeout=5)
                return self.sock
            except Exception as e:
                print('WARNING: connect(%s:%s) failed. Retrying. Error=%s' % (self.host, self.port, e))
                time.sleep(0.33)
            tries += 1

    def __len__(self):
        s = self._connect()
        msg = pickle.dumps({'o':'len', 'n':self.name}, protocol=2)
        send_msg(s, msg)
        reply = recv_msg(s)
        reply = pickle.loads(reply) #, encoding='latin1')
        if reply['s'] != 1:
            raise reply['r']
        return reply['v']

    def append(self, item):
        s = self._connect()
        msg = pickle.dumps({'o':'append', 'x':item, 'n':self.name}, protocol=2)
        send_msg(s, msg)
        reply = recv_msg(s)
        reply = pickle.loads(reply) #, encoding='latin1')
        if reply['s'] != 1:
            raise reply['r']

    def __getitem__(self, i):
        s = self._connect()
        msg = pickle.dumps({'o':'get', 'x':i, 'n':self.name}, protocol=2)
        send_msg(s, msg)
        reply = recv_msg(s)
        reply = pickle.loads(reply) #, encoding='latin1')
        if reply['s'] != 1:
            raise reply['r']
        return reply['v']

    def __delitem__(self, i):
        s = self._connect()
        msg = pickle.dumps({'o':'delete', 'x':i, 'n':self.name}, protocol=2)
        send_msg(s, msg)
        reply = recv_msg(s)
        reply = pickle.loads(reply) #, encoding='latin1')
        if reply['s'] != 1:
            raise reply['r']

    def __setitem__(self, i, val):
        s = self._connect()
        msg = pickle.dumps({'o':'set', 'x':i, 'v':val, 'n':self.name}, protocol=2)
        send_msg(s, msg)
        reply = recv_msg(s)
        reply = pickle.loads(reply) #, encoding='latin1')
        if reply['s'] != 1:
            raise reply['r']


