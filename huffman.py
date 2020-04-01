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


def byte_mapping_enc(tree):
    '''Bla'''
    assert tree  # can't compress nothing
    mapping = {}
    s = collections.deque()
    s.append(('', tree))
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
    mapping = byte_mapping_enc(tree)
    enc = ''
    for b in msg:
        enc += mapping[b]
    return enc, tree


def decode(enc, ring):
    '''Bla'''
    msg = ''
    tree = ring
    for d in enc:
        if d != '0' and d != '1':
            sys.stderr.write(f'enc must be a valid binary string\n')
            sys.exit(1)
        elif d == '0':
            tree = tree[2][0]
        else:
            tree = tree[2][1]
        if not isinstance(tree[2], tuple):
            msg += chr(tree[2])
            tree = ring
    return msg


def byte_mapping_cmp(tree):
    '''Bla'''
    assert tree  # can't compress nothing
    mapping = {}
    s = collections.deque()
    s.append(((0, 0), tree))
    # TODO: invariant
    while s:
        codeword, node = s.pop()
        # leaf
        if not isinstance(node[2], tuple):
            mapping[node[2]] = codeword
        else:
            nb, word = codeword
            nb += 1
            word <<= 0x1
            # right
            s.append(((nb, word | 0x1), node[2][1]))
            # left
            s.append(((nb, word), node[2][0]))
    return mapping


def compress(msg):
    '''Bla'''
    freqs = collections.Counter(msg)
    # TODO: play around with different tree buildings and mappings
    tree = huff_tree(freqs)  # priority queue
    mapping = byte_mapping_cmp(tree)
    compressed = bytearray()
    num_bits = buf = 0
    for byte in msg:
        width, num = mapping[byte]
        for i in range(width - 1, -1, -1):
            num_bits += 1
            buf <<= 0x1
            bit = num & (0x1 << i)
            if bit:
                buf |= 0x1
            if num_bits % 8 == 0:
                compressed.append(buf)
                buf = 0
    rem_bits = num_bits % 8
    if rem_bits:
        buf <<= (8 - rem_bits)
        compressed.append(buf)
    return compressed, (num_bits, tree)


def decompress(compressed, ring):
    '''Bla'''
    msg = bytearray()
    num_bits, start_tree = ring
    tree = start_tree
    for byte in compressed:
        for i in range(7, -1, -1):
            if num_bits:
                num_bits -= 1
                bit = byte & (0x1 << i)
                if bit:
                    tree = tree[2][1]
                else:
                    tree = tree[2][0]
                if not isinstance(tree[2], tuple):
                    msg.append(tree[2])
                    tree = start_tree
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
            with open(outfile, 'wb') as fcompressed:
                marshal.dump((pickle.dumps(decoder), compr), fcompressed)
        else:
            enc, decoder = encode(msg)
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
            msg = msg.encode()
        with open(outfile, 'wb') as fp:
            fp.write(msg)
