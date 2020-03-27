#!/usr/bin/env python3
import os
import sys
import marshal
import array

try:
    import cPickle as pickle
except:
    import pickle


def encode(msg):
    '''Bla'''
    raise NotImplementedError


def decode(msg, decoderRing):
    '''Bla'''
    raise NotImplementedError


def compress(msg):
    '''Bla'''
    # Initializes an array to hold the compressed message.
    compressed = array.array('B')
    raise NotImplementedError


def decompress(msg, decoderRing):
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
        fp = open(infile, 'rb')
        msg = fp.read()
        fp.close()
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
