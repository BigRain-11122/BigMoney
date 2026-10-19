# -*- coding: utf-8 -*-
# r1139 bm-c: one-shot patch -- force utf-8 decoding on sixgate subprocess
# text faces (same-window pit: GBK reader-thread UnicodeDecodeError on child
# stderr byte 0xa0; verdict unaffected but evidence tails were lost).
import io

P = 'results/_r1139bmc_w282_sixgate.py'
s = io.open(P, encoding='utf-8').read()
old = "capture_output=True, text=True)"
new = "capture_output=True, text=True, encoding='utf-8', errors='replace')"
n = s.count(old)
s = s.replace(old, new)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched_sites', n, 'total_utf8_faces', s.count("errors='replace'"))