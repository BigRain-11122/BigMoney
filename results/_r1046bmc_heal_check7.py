# -*- coding: utf-8 -*-
# r1046 bm-c heal check v7: revert BOTH candidate heal faces (prereg prose
# + W250 law-comment roll) -> re-hash vs receipt.
import hashlib
import io

raw = io.open('scripts/perpetual_faces_n1.py', 'rb').read()
n1 = raw
# heal face A: prereg prose (W250 block)
needleA = b'"69 + candidate; probe receipt leg0 bmc_ordinal=70'
assert needleA in n1
n1 = n1.replace(needleA, b'"68 + candidate; probe receipt leg0 bmc_ordinal=70', 1)
# heal face B: W250 law-comment (LAST occurrence = W250; W249 keeps its 68)
needleB = b'#     rows 69 + candidate; own-seat face: seat published=reserved by bm-c itself'
idxB = n1.rfind(needleB)
assert idxB >= 0
n1 = n1[:idxB] + needleB.replace(b'rows 69', b'rows 68', 1) + n1[idxB + len(needleB):]
sha = hashlib.sha256(n1).hexdigest()[:16]
print('two-face-revert sha16:', sha)
print('receipt_post          : 050d7e70375727f2')
print('MATCH:', sha == '050d7e70375727f2')

# if not, also try face B alone
n1b = raw
idxB2 = n1b.rfind(needleB)
n1b = n1b[:idxB2] + needleB.replace(b'rows 69', b'rows 68', 1) + n1b[idxB2 + len(needleB):]
print('faceB-only-revert sha16:', hashlib.sha256(n1b).hexdigest()[:16])
