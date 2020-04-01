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


def byte_mapping(tree):
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
    mapping = byte_mapping(tree)
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


def compress(msg):
    '''Bla'''
    freqs = collections.Counter(msg)
    # TODO: play around with different tree buildings and mappings
    tree = huff_tree(freqs)  # priority queue
    mapping = byte_mapping(tree)
    compressed = bytearray()
    enc = ''
    for byte in msg:
        enc += mapping[byte]
    byte_arr = [enc[i:i+8] for i in range(0, len(enc), 8)]
    for e in byte_arr:
        if len(e) < 8:
            e += '0' * (8 - len(e))
        compressed.append(int(e, base=2))
    return compressed, (len(enc), tree)


def decompress(compressed, ring):
    '''Bla'''
    msg = bytearray()
    num_bits, start_tree = ring
    tree = start_tree
    for byte in compressed:
        for bit in bin(byte)[2:].zfill(8):
            if num_bits:
                num_bits -= 1
                if bit == '1':
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
