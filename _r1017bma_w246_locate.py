# -*- coding: utf-8 -*-
# r1017 bm-a: precise occurrence locator for W246 gen vmap construction
import io
T = io.open('results/_w245bma_freeze_edits.py', encoding='utf-8', newline='').read()
lines = T.splitlines()
targets = ['r1010', 'r1011', 'arith_a244', 'arith_b244', '542_001', '542_200', '555_501',
           '557_500', '245: {{"a"', '245: {{"batch"', '244: {{"', 'W246+', 'W246p_', 'n1_w244',
           'n1w245', 'n1_w245', 'owner_rows=234', 'bma_rows=126', 'rows 126', 'rows 234',
           '235th', 'probe_receipt_bma_ordinal_face', 'sixth consecutive', 'seventh consecutive',
           'takeover lane disclosed (GM re-assignment', 'zero takeover', 'w<245', 'w<244',
           'if w < 245)', 'if w < 244)', 'below 245', '07:4x', '12:4x', 'thirty-third', 'thirty-fourth',
           'ONE HUNDRED AND TWENTY-SIXTH', 'one hundred and twenty-seventh', 'TWO HUNDRED AND FORTY-FIFTH',
           '961,135', '534,720', '961_135', '534_720', '6473fb7f8', '260ffd3f8', '2b0947947',
           'arith_a245', 'arith_b245', '127th', 'bma_ordinal=127', 'estate 90', '102', '103',
           'N3-R1', 'n3r1_used', 'w243_a ', 'w243_b ', 'twelve legs', 'W232..W243', 'W232..W244',
           'W246 seat', 'downstream W245', '963,335', '536,920']
out = []
for t in targets:
    hits = [i for i, l in enumerate(lines) if t in l]
    out.append('%-46r n=%d lines=%s' % (t, len(hits), hits[:12]))
io.open('_r1017bma_locate_out.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done', len(out))
