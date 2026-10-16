# -*- coding: utf-8 -*-
# r1046 bm-c heal check v5: CRLF-normalize disk bytes, revert heal line,
# re-hash -> expect receipt n1_sha16_post (receipt hashes in-memory
# LF-string n1_t4; disk write is CRLF face).
import hashlib
import io

raw = io.open('scripts/perpetual_faces_n1.py', 'rb').read()
print('CRLF count:', raw.count(b'\r\n'), 'LF count:', raw.count(b'\n'))
lf = raw.replace(b'\r\n', b'\n')
needle = b'"69 + candidate; probe receipt leg0 bmc_ordinal=70'
pre = lf.replace(needle, b'"68 + candidate; probe receipt leg0 bmc_ordinal=70', 1)
print('lf+heal-reverted sha16 :', hashlib.sha256(pre).hexdigest()[:16])
print('lf-as-is sha16         :', hashlib.sha256(lf).hexdigest()[:16])
print('raw sha16             :', hashlib.sha256(raw).hexdigest()[:16])
print('receipt_post          : 050d7e70375727f2')
print('EXPLAINED:', hashlib.sha256(pre).hexdigest()[:16] == '050d7e70375727f2')
