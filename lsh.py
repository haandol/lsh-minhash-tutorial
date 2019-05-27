from minhash import MinHash
from collections import defaultdict


class LSH(object):
    def __init__(self, b: int = 32, num_perm: int = 128):
        self.num_perm = num_perm
        self.b = b
        self.r = self.num_perm // self.b
        self.hashtables = [defaultdict(set) for i in range(self.b)]
        self.hashranges = [(i*self.r, (i+1)*self.r) for i in range(self.b)]
        self.keys = defaultdict(set)

    def _H(self, hashvalues):
        return bytes(hashvalues.byteswap().data)

    def insert(self, key: str, minhash: MinHash):
        if len(minhash.hashvalues) != self.num_perm:
            raise ValueError()

        Hs = [self._H(minhash.hashvalues[start:end])
              for start, end in self.hashranges]
        for data in Hs:
            self.keys[key].add(data)
        for H, hashtable in zip(Hs, self.hashtables):
            hashtable[H].add(key)

    def query(self, minhash: MinHash):
        if len(minhash.hashvalues) != self.num_perm:
            raise ValueError()
        
        candidates = set()
        for (start, end), hashtable in zip(self.hashranges, self.hashtables):
            H = self._H(minhash.hashvalues[start:end])
            for key in hashtable.get(H, []):
                candidates.add(key)
        return list(candidates)


if __name__ == '__main__':
    m1 = MinHash()
    m1.update('there is an apple')

    m2 = MinHash()
    m2.update('there are apples')

    m3 = MinHash()
    m3.update('there are grapes')

    lsh = LSH()
    lsh.insert('m1', m1)
    lsh.insert('m2', m2)
    print(lsh.hashtables)
    print(lsh.query(m3))