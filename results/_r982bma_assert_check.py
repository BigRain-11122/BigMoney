# -*- coding: utf-8 -*-
"""r982: full-scan validate ALL derive_v2 count-assertions (incl. compound) vs dbg_out."""
import io, re

src = io.open('results/_r980bma_w238_derive_v2.py', encoding='utf-8').read()
dbg = io.open('results/_r980bma_dbg_out.md', encoding='utf-8').read()
for i, line in enumerate(src.split('\n'), 1):
    if 'assert' not in line or 'out.count(' not in line:
        continue
    for m in re.finditer(r"out\.count\('(.+?)'\)\s*==\s*(\d+)", line):
        s, n = m.group(1), int(m.group(2))
        actual = dbg.count(s)
        flag = '' if actual == n else '  <<< MISMATCH'
        print('L%d expect=%d actual=%d %r%s' % (i, n, actual, s[:40], flag))
