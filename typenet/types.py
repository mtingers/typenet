from .node import Node
from threading import Lock
from time import sleep

class NoIndexNode(Exception):
    pass

class NoPartitionNode(Exception):
    pass

class UnsupportedDelete(Exception):
    pass

class List(object):
    def __init__(self, name, nodes=[], partition_size=10000, max_connection_retry=100):
        # nodes str pairs: "host:port"
        self.node_conf = nodes
        self.name = name
        self.nodes = []
        self.connections = []
        for node in nodes:
            (host, port) = node.strip().split(':')
            port = int(port)
            self.nodes.append(Node(name, host, port, max_retry=max_connection_retry))
        self.count = 0
        self.connection_time = None
        self.node_position = 0
        self.nitems = [0]*len(nodes)
        self.partitions = {}
        self.partition_size = partition_size
        self.partition_split = int(partition_size / len(nodes))
        self.p_offset = 0
        for node in range(len(nodes)):
            self.partitions[node] = []
        # pre-allocate partition offsets to a large number
        for i in range(20):
            for node in range(len(nodes)):
                self.partitions[node].append((self.p_offset, (self.p_offset+self.partition_split)-1))
                self.p_offset += self.partition_split
        # set count to sum of all nodes length
        for node in self.nodes:
            self.count += len(node)
        self.iter_i = 0
        if self.p_offset <= self.count:
            self._extend()
        self._lock = Lock()

    def _extend(self):
        for i in range(20):
            for node in range(len(self.nodes)):
                self.partitions[node].append((self.p_offset, (self.p_offset+self.partition_split)-1))
                self.p_offset += self.partition_split

    def _index_to_node(self, index, override_count=None):
        if index < 0:
            if override_count:
                index = (override_count + index)
            else:
                index = (self.count + index)
        offset = 0
        index = int(index)
        for node, p in self.partitions.items():
            for start, end in p:
                if start <= index <= end:
                    return node
        raise NoIndexNode('Could not find node for index: %d' % (index))

    def _get_data_index_and_node(self, i):
        original_index = i
        if i < 0:
            i = (self.count + i)
        node = self._index_to_node(i)
        part = None
        part_idx = -1
        for start, end in self.partitions[node]:
            part_idx += 1
            if start <= i <= end:
                part = (start, end)
                node_idx = (i - part[0])
                if part_idx > 0:
                    part_offset = (self.partition_split * part_idx)
                    node_idx += part_offset
                return (node_idx, self.nodes[node])
        raise NoPartitionNode('Could not find partition for index: %d' % (original_index))

    def _get_slice(self, i):
        start = i.start
        stop = i.stop
        if stop is None:
            stop = self.count
        step = i.step
        if stop < 0:
            stop = self.count + stop

        r = range(stop)
        data = []
        for idx in r[start:stop:step]:
            data.append(self._get_item(idx))
        return data

    def _get_item(self, i):
        (data_idx, node) = self._get_data_index_and_node(i)
        return node[data_idx]

    def __getitem__(self, i):
        if isinstance(i, slice):
            return self._get_slice(i)
        return self._get_item(i)

    def __delitem__(self, i):
        if i < 0:
            i = (self.count + i)
        if i != self.count-1:
            raise UnsupportedDelete('%s only supports deletion of the last item.' % (self.__class__.__name__))
        (data_idx, node) = self._get_data_index_and_node(i)
        del(node[data_idx])
        self.count -= 1

    def __setitem__(self, i, val):
        (data_idx, node) = self._get_data_index_and_node(i)
        node[data_idx] = val

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        r = self.__class__.__name__
        r += '(name=%s, nodes=%s, partition_size=%d, len=%d)' % (
            self.name, self.node_conf, self.partition_size, self.count)
        return r

    def __len__(self):
        count = 0
        for node in self.nodes:
            count += len(node)
        self.count = count
        return self.count

    def __iter__(self):
        return self

    def __contains__(self, v):
        for node in self.nodes:
            if v in node:
                return True
        return False

    def __next__(self):
        if self.iter_i > self.count-1:
            self.iter_i = 0
            raise StopIteration
        self.iter_i += 1
        return self[self.iter_i-1]

    def next(self):
        return self.__next__()

    def append_bulk(self, items):
        # Get all the nodes for each chunk of items
        # since items may overflow the partition if too large or
        # on the border
        nodes = {}
        prev_node = -1
        c = self.count

        # Extend the partitions to handle this bulk append
        while self.p_offset <= c+len(items):
            self._extend()

        for i in range(len(items)):
            node = self._index_to_node(self.count+i) #, override_count=self.count+i)
            if not node in nodes:
                nodes[node] = []
            if node != prev_node:
                nodes[node].append({'start':i, 'end':i+1})
            nodes[node][-1]['end'] = i+1
            prev_node = node

        for node, s in nodes.items():
            for ss in s:
                self.nodes[node].append_bulk(items[ss['start']:ss['end']])
                self.count += ss['end'] - ss['start']

    def append(self, item):
        node = self._index_to_node(self.count)
        self.nodes[node].append(item)
        self.count += 1
        if self.p_offset <= self.count:
            self._extend()

    def node_debug(self):
        out = '---- node info ----\n'
        for i in self.nodes:
            out += i.debug_info()
            out += '\n'
        return out.strip()

    # Provides a means for thread/process safety
    # This is actually multiple layers of locks
    # One local thread lock, one remote lock
    # The first node in the list acts as the lock server
    def lock(self):
        self._lock.acquire()
        # This is a remote spin lock
        while 1:
            status = self.nodes[0].lock()
            if status is True:
                break
            sleep(0.066)
        self.__len__()

    def unlock(self):
        self._lock.release()
        status = self.nodes[0].unlock()
        if status is False:
            print('WARNING: node unlock() call returned False. Something else unlocked it!')

