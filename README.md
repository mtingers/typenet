# TypeNet
TypeNet: Types distributed over a network

# Introduction
1. A client/server model for storing Python objects/types across a network.
2. Provides a simple entry point mimicking standard types (e.g. list).
3. Can be used as a message passing interface to share Python objects/types over a network.

# Install
```
python setup.py install
```

# Types
Supported types:
1. List -- Acts like the default python list type
2. Dict -- Coming soon, not yet implemented

# Examples

## Server
Before TypeNet can be used, servers must be started that the client can connect to.
NOTE: A mix of python2 and python3 servers are compatible and can be run together.

```bash
# Launch server 1
user@node01:~$ typenet-server 0.0.0.0 4444
```
```bash
# Launch server 2
user@node02:~$ typenet-server 0.0.0.0 4445
```

## Client
The client is designed to work like normal/local types through the use of Python's
dunder methods. Here is a simple example that can be compared to a standard list:

```python
from typenet.types import List
li = List('list-test', nodes=['node01:4444', 'node02:4445'], partition_size=10000)
li.append(0)
li.append(1)
li.append(2)
li.append('test')

print(li[0])    # -> 0
print(li[-1])   # -> 'test'

# Slices are allowed
print(li[0:2])  # -> [0, 1]

# Iterate over items
for i in li:
    print(i)
    # -> 0
    # -> 1
    # -> 2
    # -> test

del(li[-1])     # Delete last item

# NOTE: List only supports deleting the last item at this time
del(li[0])      # -> typenet.types.UnsupportedDelete: List only supports deletion of the last item.
```

The following example dumps the list of nodes and the length of their local list.
```python
# Example node stats dump
>>> from typenet.types import List
>>> 
>>> li = List('list-test', nodes=['node01:4444', 'node02:4445'], partition_size=100)
>>> for i in range(10000):
...     li.append(i)
... 

>>> 
>>> print(li.node_debug())
---- node info ----
Node(name=list-test, host=node01:4444, len=5000)
Node(name=list-test, host=node02:4445, len=5000)
```

# TODO and Known Issues

## TODO
1. Add TLS/SSL support with authentication.
2. Add server config file.
3. Add server module import list. For example, class Foo() cannot be pickled across the network unless the servers import the same Foo on startup.
4. Add systemd init scripts.
5. Add allowed IP list in server config.
6. Add dict type
7. Add sort method. sorted() does work but not recommended since it returns a list (defeating the purpose of a distributed list).

## Known Issues
1. Servers are subject to pickle attacks. Todo items #1 and #5 will help improve security in the future.
2. Servers currently accept any connections and connections are not encrypted. Do not use on an open network in the current state.
3. It is not recommended to write to TypeNet servers from multiple locations/processes/threads at this time unless you do your own coordination.
