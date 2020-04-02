#!/usr/bin/env python3
import os
import sys
import marshal
import collections
import heapq

try:
    import cPickle as pickle
except:
    import pickle


def huff_tree(freqs):
    '''Given a frequency table of bytes output a huffman tree
    Format: (count, index, subtree)
    '''
    assert len(freqs)  # can't compress nothing
    # list of nodes -> (count, index, symbol), index is added to break ties
    nodes = [(y, i, x) for i, (x, y) in enumerate(freqs.most_common())]
    heapq.heapify(nodes)
    idx = len(nodes)
    # TODO: Invariant
    while len(nodes) > 1:
        first = heapq.heappop(nodes)
        second = heapq.heappop(nodes)
        new_node = (first[0] + second[0], idx, (first, second))
        idx += 1
        heapq.heappush(nodes, new_node)
    return nodes[0]


def byte_mapping(tree):
    '''Bla'''
    assert tree  # can't compress nothing
    s = collections.deque()
    s.append(('', tree))
    mapping = {}
    # TODO: invariant
    while s:
        codeword, node = s.pop()
        # leaf
        if not isinstance(node[2], tuple):
            mapping[node[2]] = codeword
        else:
            # right
            s.append((codeword + '1', node[2][1]))
            # left
            s.append((codeword + '0', node[2][0]))
    return mapping


def encode(msg):
    '''Bla'''
    freqs = collections.Counter(msg)
    # TODO: play around with different tree buildings and mappings
    tree = huff_tree(freqs)  # priority queue
    mapping = byte_mapping(tree)
    enc = ''
    for b in msg:
        enc += mapping[b]
    rev_mapping = {v: k for k, v in mapping.items()}
    return enc, rev_mapping


def decode(enc, ring):
    '''Bla'''
    msg = word = ''
    for d in enc:
        if d != '0' and d != '1':
            sys.stderr.write(f'enc must be a valid binary string\n')
            sys.exit(1)
        word += d
        if word in ring:
            msg += chr(ring[word])
            word = ''
    return msg


def compress(msg):
    '''Bla'''
    freqs = collections.Counter(msg)
    # TODO: play around with different tree buildings and mappings
    tree = huff_tree(freqs)  # priority queue
    mapping = byte_mapping(tree)
    enc = ''
    for byte in msg:
        enc += mapping[byte]
    rem_bits = len(enc) % 8
    padding = 0
    if rem_bits:
        padding = 8 - rem_bits
        enc += '0' * padding
    compressed = bytes([int(enc[i:i + 8], 2) for i in range(0, len(enc), 8)])
    rev_mapping = {v: k for k, v in mapping.items()}
    return compressed, (padding, rev_mapping)


def decompress(compressed, ring):
    '''Bla'''
    enc = word = ''
    for byte in compressed:
        enc += bin(byte)[2:].zfill(8)
    padding, mapping = ring
    enc = enc[:len(enc) - padding]
    msg = bytearray()
    for bit in enc:
        word += bit
        if word in mapping:
            msg.append(mapping[word])
            word = ''
    return msg


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
        else:
            compr, decoder = encode(msg)
        with open(outfile, 'wb') as fcompressed:
            marshal.dump((pickle.dumps(decoder), compr), fcompressed)
    else:
        with open(infile, 'rb') as fp:
            pickle_rick, compr = marshal.load(fp)
            decoder = pickle.loads(pickle_rick)
        if decompressing:
            msg = decompress(compr, decoder)
        else:
            msg = decode(compr, decoder)
            msg = msg.encode()
        with open(outfile, 'wb') as fp:
            fp.write(msg)
