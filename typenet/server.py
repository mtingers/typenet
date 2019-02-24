import pickle
import socket
import select
from pprint import pprint
from .util import send_msg, recv_msg

class TypeNetServer(object):
    def __init__(self, host, port):
        self.port = port
        self.host = host
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.s.bind((host, port))
        self.s.listen(16)
        self.nodes = {}
        self.clients = []
        self.inputs = [self.s]
        self.outputs = []
        self.message_queues = {}

    def _handle_msg(self, conn):
        msg = recv_msg(conn)
        msg = pickle.loads(msg) #, encoding='latin1')
        node_name = msg['n']
        if not node_name in self.nodes:
            self.nodes[node_name] = []

        reply = {'s':1,}
        try:
            if msg['o'] == 'append':
                self.nodes[node_name].append(msg['x'])
            elif msg['o'] == 'delete':
                del(self.nodes[node_name][msg['x']])
            elif msg['o'] == 'set':
                self.nodes[node_name][msg['x']] = msg['v']
            elif msg['o'] == 'get':
                reply['v'] = self.nodes[node_name][msg['x']]
            elif msg['o'] == 'len':
                reply['v'] = len(self.nodes[node_name])
            elif msg['o'] == 'contains':
                if msg['x'] in self.nodes[node_name]:
                    reply['v'] = True
                else:
                    reply['v'] = False
            else:
                print('Unknown msg: %s' % (msg))
        except Exception as e:
            print('ERROR: %s' % (e))
            print('----debug----')
            pprint(msg)
            print(len(self.nodes[node_name]))
            reply['r'] = e
            reply['s'] = 0
        send_msg(conn, pickle.dumps(reply, protocol=2))

    def _run(self):
        while self.inputs:
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)
            for s in readable:
                if s is self.s:
                    connection, client_address = self.s.accept()
                    self.inputs.append(connection)
                else:
                    try:
                        self._handle_msg(s)
                    except Exception as e:
                        if s in self.outputs:
                            self.outputs.remove(s)
                        self.inputs.remove(s)
                        s.close()
            for s in exceptional:
                self.inputs.remove(s)
                if s in outputs:
                    self.outputs.remove(s)
                s.close()

    def run(self):
        while 1:
            try:
                self._run()
            except Exception as e:
                raise



