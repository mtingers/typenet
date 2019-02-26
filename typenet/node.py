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

    def _send_msg(self, msg):
        s = self._connect()
        msg = pickle.dumps(msg, protocol=2)
        send_msg(s, msg)
        reply = recv_msg(s)
        reply = pickle.loads(reply) #, encoding='latin1')
        if reply['s'] != 1:
            raise reply['r']
        if 'v' in reply:
            return reply['v']

    def __len__(self):
        return self._send_msg({'o':'len', 'n':self.name})

    def append_bulk(self, items):
        return self._send_msg({'o':'append_bulk', 'x':items, 'n':self.name})

    def append(self, item):
        return self._send_msg({'o':'append', 'x':item, 'n':self.name})

    def __getitem__(self, i):
        return self._send_msg({'o':'get', 'x':i, 'n':self.name})

    def __delitem__(self, i):
        return self._send_msg({'o':'delete', 'x':i, 'n':self.name})

    def __setitem__(self, i, val):
        return self._send_msg({'o':'set', 'x':i, 'v':val, 'n':self.name})

    def __contains__(self, v):
        return self._send_msg({'o':'contains', 'x':v, 'n':self.name})

    def debug_info(self):
        return  'Node(name=%s, host=%s:%s, len=%d)' % (self.name, self.host, self.port, self.__len__())

