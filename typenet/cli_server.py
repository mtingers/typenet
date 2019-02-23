#!/usr/bin/env python
#
# A simple server example that takes an ip/hostname and port argument
# to bind to and listen on.
#

import sys
from server import TypeNetServer

def usage():
    print('%s <listen-host> <listen-port>' % (sys.argv[0]))
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()

    host = sys.argv[1]
    port = int(sys.argv[2])

    server = TypeNetServer(host, port)
    server.run()

