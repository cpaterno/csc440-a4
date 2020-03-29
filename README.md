# csc440-a4
Python implementation of Huffman Encoding (greedy algorithm)


## Algorithm
- [ ] `encode`(msg) -> (enc, ring) and `compress`(msg) -> (compressed, ring)
    - [x] create frequency table of bytes: counts
    - [x] build tree from priority queue of nodes (count, byte)
    - [x] create mapping from byte to codeword
    - [x] create enc/compressed from msg and tree
    - [x] create ring as tuple (numbits, tree) 
    - [x] enc is a regular string (encode only)
    - [ ] compressed is a bytearray, therefore shift bits in (compress only)
- [ ] `decode`(enc, ring) -> msg  and `decompress`(compressed, ring) -> msg
    - [ ] error check to ensure enc is a string of 1s and 0s (decode only)
    - [ ] create msg from enc/compressed and ring
    - [ ] bitshifting required (decompress only)
