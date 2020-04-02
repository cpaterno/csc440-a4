# csc440-a4
Python implementation of Huffman Encoding (greedy algorithm)


## Algorithm
- [x] `encode`(msg) -> (enc, ring) and `compress`(msg) -> (compressed, ring)
    - [x] create frequency table of bytes: counts
    - [x] build tree from priority queue of nodes (count, idx, byte)
    - [x] create mapping from byte to codeword
    - [x] create enc/compressed from msg and tree
    - [x] enc is a regular string (encode only)
    - [x] compressed is a bytearray (compress only)
    - [x] create ring as reverse mapping (encode only)
    - [x] create ring as tuple (padding, reverse mapping) (compress only) 
- [x] `decode`(enc, ring) -> msg  and `decompress`(compressed, ring) -> msg
    - [x] error check to ensure enc is a string of 1s and 0s (decode only)
    - [x] create msg from enc/compressed and ring
