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
    # list of nodes -> (count, index, byte), index is added to break ties
    nodes = [(y, i, x) for i, (x, y) in enumerate(freqs.most_common())]
    # min priority queue where priority is count
    heapq.heapify(nodes)
    idx = len(nodes)
    # INVARIANT: At every iteration there is one less subtree 
    # INITIALIZATION: The queue is filled with a forest of trees, 
    #                 1 tree for each leaf
    # MAINTENANCE: 2 subtrees are merged into a bigger subtree
    # TERMINATION: There is only 1 subtree in the queue 
    while len(nodes) > 1:
        first = heapq.heappop(nodes)
        second = heapq.heappop(nodes)
        new_node = (first[0] + second[0], idx, (first, second))
        idx += 1
        heapq.heappush(nodes, new_node)
    return nodes[0]


def byte_mapping(tree):
    '''Given a huffman tree, create a mapping from bytes
    to codewords, where codewords are strings representing
    a binary path from root to each leaf (byte), visited
    through iterative preorder traversal'''
    assert tree  # can't compress nothing
    s = collections.deque()
    s.append(('', tree))
    mapping = {}
    # INVARIANT: Left subtrees are always processed before right subtrees
    # INITIALIZATION: Trivially true, root added to stack
    # MAINTENANCE: A subtree is removed and if not at a leaf, 
    #              the right subtree is added before
    #              the left subtree to the stack
    # TERMINATION: All nodes are visited (taken off the stack)
    while s:
        # get next node off the stack
        codeword, node = s.pop()
        # leaf
        if not isinstance(node[2], tuple):
            mapping[node[2]] = codeword
        else:
            # right subtree
            s.append((codeword + '1', node[2][1]))
            # left subtree
            s.append((codeword + '0', node[2][0]))
    return mapping


def encode(msg):
    '''Given a msg of bytes, output the string (enc)
    representing the Huffman Encoding of that given message,
    and a decoder ring to decode the encoding
    '''
    # compute frequency of bytes
    freqs = collections.Counter(msg)
    # build tree
    tree = huff_tree(freqs)
    # create mapping for encoding
    mapping = byte_mapping(tree)
    # build up the encoded string
    enc = ''.join([mapping[b] for b in msg])
    # create mapping for decoding
    rev_mapping = {v: k for k, v in mapping.items()}
    return enc, rev_mapping


def decode(enc, ring):
    '''Given an encoded bit string (enc) and a decoder ring,
    output the decoded message as a string (msg)
    '''
    # build up decoded string
    msg = word = ''
    for d in enc:
        if d != '0' and d != '1':
            sys.stderr.write(f'enc must be a valid bit string\n')
            sys.exit(1)
        # check decoder ring if current substring (word) maps to a byte
        word += d
        if word in ring:
            msg += chr(ring[word])  # need to decode bytes to add to string
            word = ''
    return msg


def compress(msg):
    '''Given a msg of bytes, output the encoded, compressed bytes
    representing the Huffman Encoding of that given message, and 
    a decoder ring to decompress the compression
    NOTE: In Python string manipulation is faster than bit twiddling
    '''
    # compute frequency of bytes
    freqs = collections.Counter(msg)
    # build tree
    tree = huff_tree(freqs)
    # create mapping for encoding
    mapping = byte_mapping(tree)
    # build up the encoded string
    enc = ''.join([mapping[b] for b in msg])
    rem_bits = len(enc) % 8
    # add 0s to the end of enc for padding
    padding = 0
    if rem_bits:
        padding = 8 - rem_bits
        enc += '0' * padding
    # convert enc to bytes
    compressed = bytes([int(enc[i:i + 8], 2) for i in range(0, len(enc), 8)])
    # create mapping for decoding
    rev_mapping = {v: k for k, v in mapping.items()}
    return compressed, (padding, rev_mapping)


def decompress(compressed, ring):
    '''Given an encoded, compressed bytes and a decoder ring,
    output the uncompressed bytes
    NOTE: In Python string manipulation is faster than bit twiddling
    '''
    # build up encoded string from bytes
    enc = word = ''
    for byte in compressed:
        enc += bin(byte)[2:].zfill(8)
    padding, mapping = ring
    # removed padded 0s
    enc = enc[:len(enc) - padding]
    # build up uncompressed bytes
    msg = bytearray()
    for bit in enc:
        word += bit
        # check decoder ring if current substring (word) maps to a byte
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
