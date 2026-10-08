# -*- coding: utf-8 -*-
import hashlib

P = r'CODELY.md'
CAP = 30720
entry = ('- [2026-10-08 09:1x r872 bm-a] **收尾脚本旧路径轮报行坑第3例（r870/r871 行落旧面）**：'
         '一次性收尾脚本硬编码 rp="logs/iteration-loop/round_reports-bm-a.md"（r864 首例治愈后复发）；'
         '本窗双行 verbatim 复迁 ROOT（sha16 463c8a5c/ad9700ca 恒等）。'
         'How to apply：收尾/记账脚本轮报行路径必=仓根 round_reports-<id>.md（r844 律）；收尾后 grep ROOT 验行再宣称 done。\n')

b = open(P, 'rb').read()
e = entry.encode('utf-8')
assert b'r872 bm-a]' not in b, 'already appended'
new_size = len(b) + len(e)
print('old', len(b), 'entry', len(e), 'new', new_size, 'over-cap', new_size - CAP)
assert new_size <= CAP, 'CAP EXCEEDED -- need mini-split'
if not b.endswith(b'\n'):
    e = b'\n' + e
with open(P, 'ab') as f:
    f.write(e)
b2 = open(P, 'rb').read()
assert e in b2 and len(b2) == len(b) + len(e) + (0 if b.endswith(b'\n') else 0)
print('APPEND OK; sha16', hashlib.sha256(e).hexdigest()[:16], 'final', len(b2))
