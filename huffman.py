#!/usr/bin/env python3
import os
import sys
import marshal
import array
import collections
import heapq
#from time import time

try:
    import cPickle as pickle
except:
    import pickle

#_________________________________TREE OPTIONS________________________________#

def huff_tree_pq(freqs):
    '''Given a frequency table of bytes output a huffman tree
    Format: (count, index, subtree)
    '''
    assert len(freqs)  # can't compress nothing
    # list of nodes -> (count, index, symbol), index is added to break ties
    nodes = [(y, i, x) for i, (x, y) in enumerate(freqs.most_common())]
    idx = len(nodes)
    heapq.heapify(nodes)
    # TODO: Invariant
    while len(nodes) > 1:
        first = heapq.heappop(nodes)
        second = heapq.heappop(nodes)
        new_node = (first[0] + second[0], idx, (first, second))
        idx += 1
        heapq.heappush(nodes, new_node)
    return nodes[0]


def huff_tree_rs(freqs):
    '''Given a frequency table of bytes output a huffman tree
    Format: (count, subtree)
    '''
    assert len(freqs)  # can't compress nothing
    # list of nodes -> (count, symbol), reverse sorted
    nodes = [(y, x) for x, y in freqs.most_common()]
    # TODO: Invariant
    while len(nodes) > 1:
        first = nodes.pop()
        second = nodes.pop()
        new_node = (first[0] + second[0], (first, second))
        nodes.append(new_node)
        nodes.sort(key=lambda k: k[0], reverse=True)
    return nodes[0]


def huff_tree_rs2(freqs):
    '''Given a frequency table of bytes output a huffman tree
    Format: (subtree, count)
    '''
    assert len(freqs)  # can't compress nothing
    # list of nodes -> (symbol, count), reverse sorted by count
    nodes = freqs.most_common()
    # TODO: Invariant
    while len(nodes) > 1:
        first = nodes.pop()
        second = nodes.pop()
        new_node = ((first, second), first[1] + second[1])
        nodes.append(new_node)
        nodes.sort(key=lambda k: k[1], reverse=True)
    return nodes[0]


#_________________________________TREE OPTIONS________________________________#


#_____________________________TRAVERSAL OPTIONS_______________________________#

def mapping_enc_rc_rs(tree, mapping, codeword=''):
    # TODO: Invariant
    '''Bla'''
    if not isinstance(tree[1], tuple):
        mapping[tree[1]] = codeword
    else:
        mapping_enc_rc_rs(tree[1][0], mapping, codeword + '0')
        mapping_enc_rc_rs(tree[1][1], mapping, codeword + '1')
    return None


def mapping_enc_it_rs(tree):
    '''Bla'''
    mapping = {}
    s = collections.deque()
    s.append(('1', tree[1][1]))
    s.append(('0', tree[1][0]))
    # TODO: invariant
    while s:
        codeword, node = s.pop()
        # leaf
        if not isinstance(node[1], tuple):
            mapping[node[1]] = codeword
        else:
            # right
            s.append((codeword + '1', node[1][1]))
            # left
            s.append((codeword + '0', node[1][0]))
    return mapping

#_____________________________TRAVERSAL OPTIONS_______________________________#


def encode(msg):
    '''Bla'''
    freqs = collections.Counter(msg)
    # TODO: play around with different tree buildings and mappings
    tree = huff_tree_rs(freqs)  # pure Daniels notation
    mapping = {}
    mapping_enc_rc_rs(tree, mapping)
    enc = ''
    for b in msg:
        enc += mapping[b]
    return enc, (len(enc), tree)


def decode(msg, ring):
    '''Bla'''
    raise NotImplementedError


def compress(msg):
    '''Bla'''
    # Initializes an array to hold the compressed message.
    compressed = array.array('B')
    raise NotImplementedError


def decompress(msg, ring):
    '''Bla'''
    # Represent the message as an array
    byte_array = array.array('B', msg)
    raise NotImplementedError


def usage():
    '''Tell user how to run program and exit to stderr'''
    sys.stderr.write(f'Usage: {sys.argv[0]} [-c|-d|-v|-w] infile outfile\n')
    sys.exit(1)
    return None


if __name__ == '__main__':
    if len(sys.argv) != 4:
        usage()

    opt = sys.argv[1]
    compressing = decompressing = encoding = decoding = False
    if opt == "-c":
        compressing = True
    elif opt == "-d":
        decompressing = True
    elif opt == "-v":
        encoding = True
    elif opt == "-w":
        decoding = True
    else:
        usage()
    infile = sys.argv[2]
    outfile = sys.argv[3]
    assert os.path.exists(infile)

    if compressing or encoding:
        with open(infile, 'rb') as fp:
            msg = fp.read()
        if compressing:
            compr, decoder = compress(msg)
            with open(outfile, 'wb') as fcompressed:
                marshal.dump((pickle.dumps(decoder), compr), fcompressed)
        else:
            enc, decoder = encode(msg)
            print(msg)
            with open(outfile, 'wb') as fcompressed:
                marshal.dump((pickle.dumps(decoder), enc), fcompressed)
    else:
        with open(infile, 'rb') as fp:
            pickle_rick, compr = marshal.load(fp)
            decoder = pickle.loads(pickle_rick)
        if decompressing:
            msg = decompress(compr, decoder)
        else:
            msg = decode(compr, decoder)
        with open(outfile, 'wb') as fp:
            fp.write(msg)
