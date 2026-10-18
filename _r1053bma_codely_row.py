#!/usr/bin/env python
# r1053 bm-a: append the two-face ack gate upgrade row to repo-root
# CODELY.md (multi-writer ledger: fresh-read-modify-write in one shot,
# per the 2026-10-06 law; replace-tool appends are forbidden here).
import io
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(BASE, 'CODELY.md')

ROW = (
    "- [2026-10-18 10:5x r1053 bm-a] \u56de\u6267\u53cc\u9762\u5751\u95f8\u5347\u7ea7"
    "\uff08\u627f r1052 \u884c\u00b7\u811a\u672c\u65ad\u8a00\u7ea7\u843d\u95f8\uff09\uff1a"
    "Tools/orders_ack_append.py \u6b63\u5178\u53cc\u9762 ack \u8ffd\u52a0\u5668\u5efa\u6210"
    "\uff08\u4e00\u6b21\u8c03\u7528\u540c\u5199 state \u6b63\u5178\u9762+heartbeat \u626b\u63cf\u9762"
    "\u00b7per-face \u5e42\u7b49\u00b7orders_ack_last \u53cc\u9762\u00b7--sync-mirrors "
    "\u516b\u955c\u50cf\u5b57\u6bb5 state\u2192heartbeat\u00b7r504 validate-then-atomic"
    "+\u5199\u540e\u91cd\u8bfb\u65ad\u8a00\u00b7R170 epoch int \u5b88\u62a4\u00b7bm-b "
    "state.json \u7279\u4f8b S5 \u6cd5\u00b7selftest 8/8\uff09"
    "+orders_ack_scan.py \u53cc\u9762\u5947\u5076\u6821\u9a8c\u95f8"
    "\uff08\u65b0 exit 4=face_divergence heart_only/state_only"
    "\u00b7state \u9762\u7f3a/\u574f=exit 4\u00b7unacked \u4f18\u5148 exit 3 \u4e0d\u53d8"
    "\u00b7selftest 17/17\u00b7loop \u63a5\u7ebf best-effort \u65e5\u5fd7\u9762\u96f6 rc "
    "\u6d88\u8d39=exit 4 additive \u5b89\u5168\uff09\uff1b\u5b9e\u5f39\u590d\u626b\u771f\u9762 "
    "CLEAN 111/111 \u96f6\u5206\u6b67\u3002How to apply\uff1a\u6b64\u540e\u4e00\u5207 "
    "closeout \u56de\u6267 append \u4e00\u5f8b\u8d70 orders_ack_append.py"
    "\uff08\u7981\u624b\u6415\u5355\u9762\u5199\uff09\uff1b\u8f6e\u9996\u626b\u63cf\u7ea2 "
    "face_divergence=\u5148\u67e5\u4e24\u9762\u5dee\u96c6\u52ff\u5f53\u771f\u503a\u91cd\u6267\u884c"
    "\uff08r1052 \u5f8b\uff09\u3002\n"
)

with io.open(PATH, encoding='utf-8') as fh:
    text = fh.read()
assert 'orders_ack_append' not in text, 'row already present'
assert text.endswith('\n'), 'ledger must end with newline before append'
text = text + ROW
with io.open(PATH, 'w', encoding='utf-8', newline='') as fh:
    fh.write(text)

with io.open(PATH, encoding='utf-8') as fh:
    check = fh.read()
assert 'orders_ack_append' in check
lines = check.count('\n')
print('CODELY-APPEND-OK bytes=%d lines=%d' % (len(check.encode("utf-8")), lines))
