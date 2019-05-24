from __future__ import annotations
import re
import binascii
import numpy as np

MERSENNE_PRIME = (1<<61)-1
MAX_HASH = (1<<32)-1
HASH_RANGE = (1<<32)


class MinHash(object):
    def __init__(self, num_perm: int = 128, seed: int = 1):
        if HASH_RANGE < num_perm:
            raise ValueError()

        self.seed = seed
        self.hashvalues = np.ones(num_perm, dtype=np.uint64) * MAX_HASH

        generator = np.random.RandomState(self.seed)
        self.permutations = np.array([
            (generator.randint(1, MERSENNE_PRIME, dtype=np.uint64),
             generator.randint(0, MERSENNE_PRIME, dtype=np.uint64))
            for _ in range(num_perm)
        ], dtype=np.uint64).T
        
    def hashfunc(self, b: bytes):
        return binascii.crc32(b) & MAX_HASH

    def update(self, s: str):
        shingles = self.shingling(s)
        for shingle in shingles:
            hv = self.hashfunc(shingle)
            a, b = self.permutations
            phv = np.bitwise_and((a * hv + b) % MERSENNE_PRIME, np.uint64(MAX_HASH))
            self.hashvalues = np.minimum(phv, self.hashvalues)

    def shingling(self, s: str, n: int = 3):
        s = re.sub(r'([^\w ])+', '', s.lower())
        res = []
        for i in range(len(s)):
            shingle = s[i:i+n]
            if len(shingle) == n:
                res.append('_'.join(shingle).encode('utf-8'))
        return res

    def jaccard(self, other: MinHash):
        if other.seed != self.seed:
            raise ValueError()

        if len(self.hashvalues) != len(other.hashvalues):
            raise ValueError()
        
        return np.float(np.count_nonzero(self.hashvalues == other.hashvalues)) /\
               np.float(len(self.hashvalues))


if __name__ == '__main__':
    h1 = MinHash()
    h1.update('there is an apple')

    h2 = MinHash()
    h2.update('there are apples')

    h3 = MinHash()
    h3.update('here comes the challenger')

    print(h1.jaccard(h2))
    print(h1.jaccard(h3))