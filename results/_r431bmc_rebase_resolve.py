# -*- coding: utf-8 -*-
# r431 bm-c rebase pick-2 conflict resolver (research/pit-git.md tail append race:
# origin-side bm-a r643 pair x my r431 trio on shared tail anchor).
# Law: r423 clean-side/union (append-only file -> union both sides), r630 marker-surgery
# (no checkout --ours/--skip: strip markers keep both blocks), byte-exact logical lines.
import sys

P = r'K:\Fluxgroup\FluxGroup\quant\bigmoney\research\pit-git.md'
raw = open(P, 'rb').read()
text = raw.decode('utf-8')
lines = text.split('\n')

starts = [i for i, l in enumerate(lines) if l.startswith('<<<<<<< ')]
mids = [i for i, l in enumerate(lines) if l.startswith('||||||| ')]
seps = [i for i, l in enumerate(lines) if l.rstrip('\r') == '=======']
ends = [i for i, l in enumerate(lines) if l.startswith('>>>>>>> ')]
assert len(starts) == 1 and len(mids) == 1 and len(seps) == 1 and len(ends) == 1, (starts, mids, seps, ends)
s, m, p, e = starts[0], mids[0], seps[0], ends[0]

ours_head = lines[s + 1:m]      # origin side: bm-a r643 entry + direct-write receipt
base_mid = lines[m + 1:p]       # merge base tail (expected: no unique content)
mine = lines[p + 1:e]           # my r431 receipt + blank + r423 entry

print('ours(HEAD) lines=%d base lines=%d mine lines=%d' % (len(ours_head), len(base_mid), len(mine)))
assert any('r643 bm-a' in l for l in ours_head), 'origin side r643 missing'
assert any('增量回扫行（r431 bm-c' in l for l in mine), 'my r431 receipt missing'
assert any('r423 bm-c' in l for l in mine), 'my r423 entry missing'

# union, chronological: my r431 (21:4x) first, then bm-a r643 (21:5x)
merged = mine + ours_head
new_lines = lines[:s] + merged + lines[e + 1:]
new_text = '\n'.join(new_lines)

# post-assertions: zero LINE-ANCHORED markers anywhere in file (mid-line documented
# marker patterns inside pit text are legitimate content -- r423/r643 quote them)
import re as _re
resid = [l for l in new_lines if _re.match(r'^(<<<<<<<|\|\|\|\|\|\|\||=======$|>>>>>>>)', l.rstrip('\r'))]
assert not resid, 'residual line-anchored markers: %r' % resid[:2]
assert new_text.count('增量回扫行（r431 bm-c') == 1
assert new_text.count('- [2026-10-03 18:0x r423 bm-c]') == 1
assert new_text.count('- [2026-10-03 21:5x r643 bm-a]') == 1
assert new_text.count('Direct-write line (r643 bm-a') == 1
new_text.encode('utf-8')  # strict round-trip face

open(P, 'wb').write(new_text.encode('utf-8'))
print('RESOLVED: union applied (mine=%d + ours=%d lines), markers=0, needles 4/4 unique' % (len(mine), len(ours_head)))
