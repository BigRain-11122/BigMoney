# -*- coding: utf-8 -*-
# r1046 bm-c heal check v4: BINARY mode (raw bytes, CRLF preserved) --
# text-mode read normalized line endings, invalidating v3 hash compare.
import hashlib
import io

raw = io.open('scripts/perpetual_faces_n1.py', 'rb').read()
needle = b'"69 + candidate; probe receipt leg0 bmc_ordinal=70'
assert needle in raw, 'healed face not found in raw bytes'
pre = raw.replace(needle, b'"68 + candidate; probe receipt leg0 bmc_ordinal=70', 1)
sha_pre = hashlib.sha256(pre).hexdigest()[:16]
sha_now = hashlib.sha256(raw).hexdigest()[:16]
print('n1_now_sha16      :', sha_now)
print('n1_pre-heal_sha16 :', sha_pre)
print('receipt_post      : 050d7e70375727f2')
print('HEAL-IS-ONLY-DELTA:', sha_pre == '050d7e70375727f2')
