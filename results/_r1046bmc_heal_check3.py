# -*- coding: utf-8 -*-
# r1046 bm-c heal check v3: revert disclosed "rows 68->69" face and re-hash.
# Proves the heal is the ONLY delta between landed blob and receipt sha.
import hashlib
import io

t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
needle = '"69 + candidate; probe receipt leg0 bmc_ordinal=70'
assert needle in t, 'healed face not found'
pre = t.replace(needle, '"68 + candidate; probe receipt leg0 bmc_ordinal=70', 1)
sha_pre = hashlib.sha256(pre.encode('utf-8')).hexdigest()[:16]
sha_now = hashlib.sha256(t.encode('utf-8')).hexdigest()[:16]
print('n1_now_sha16      :', sha_now)
print('n1_pre-heal_sha16 :', sha_pre)
print('receipt_post      : 050d7e70375727f2')
print('HEAL-IS-ONLY-DELTA:', sha_pre == '050d7e70375727f2')
print('LANDED==RECEIPT+HEAL:', sha_pre == '050d7e70375727f2' and sha_now == '22a957f851fd3adc')
