#!/usr/bin/env python

import sys
sys.path.insert(0, './')
from typenet.types import List

tn_list = List('foobar', nodes=['127.0.0.1:4444', '127.0.0.1:4445'], partition_size=10000)

print('len: %d' % (len(tn_list)))

print('creating list...')
for i in range(199919):
    item = 'test:'+str(i)
    tn_list.append(item)


print('len: %d' % (len(tn_list)))
print('testing list is valid...')
for i,n in enumerate(tn_list):
    item = 'test:'+str(i)
    if n != item:
        print('%d: n != item: %s != %s' % (i, n, item))
        sys.exit(1)
print('iterating over list...')
it = []
for i in tn_list:
    it.append(i)

print('deleting list...')
while 1:
    l = len(tn_list)
    if l < 1: break
    del(tn_list[-1])

print('len: %d' % (len(tn_list)))
