# -*- coding: utf-8 -*-
# r772 bm-a: verify band-string integrity inside the WAVE_CONFIGS entry fragments
import io
import re

t = io.open(r'results/_r772bma_w157_src_entry.txt', encoding='utf-8', newline='').read()
for pat in ['357_804..359_803', '357_804..358_003', '358_004..360_003', '358_004..358_203',
            '360_004..360_203', '358_003+1', '360_003+1', 'n1w156', 'MSG-2026-10-06-1009',
            'ffce2936f', 'dde679c63', '737,011', '338,920', 'ONE HUNDRED-AND-FORTY-SIXTH',
            'seventy-second', 'fifteenth', 'arc generator', 'finalize window']:
    c = t.count(pat)
    print(f'{pat!r}: {c}')
# split-fragment check: any fragment ending/starting mid-band?
for m in re.finditer(r'"[^"]*(?:35[0-9]_80[0-9]|[0-9]{3}_[0-9]{3})[^"]*"', t):
    s = m.group(0)
    if '\\"' not in s:
        pass
frags = re.findall(r'"([^"]*)"', t)
print('fragments:', len(frags))
for i, f in enumerate(frags):
    if re.search(r'(?:^|[^\d])\d{3}_\d{3}', f) or f.endswith(tuple('0123456789')) and re.search(r'\d{3}_\d', f):
        pass
# find fragments that START or END with partial band digits
sus = [(i, f) for i, f in enumerate(frags) if re.match(r'^\d{1,2}_\d{3}', f) or re.search(r'\d{3}_\d{1,2}$', f)]
print('suspicious boundary fragments:', sus[:10])
