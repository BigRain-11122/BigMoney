# -*- coding: utf-8 -*-
# r963 bm-c: template census-gap probe (dead-window census supplement) + editor stale-list verification
import re, json
t = open('results/_w229bmc_freeze_edits.py', encoding='utf-8', newline='').read()
e = open('results/_w229bmc_derive_editor.py', encoding='utf-8', newline='').read()
out = {}
for tok in ['n1_w228', 'n1_w228_results', 'n1_w229_results', '4e30ddf69', '6744db794',
            '48c321706', '1e5ed3326', '842f817ad', 'r959-continuation', 'r959 window',
            'dead r959 window', '2ae8553e6', 'f4b24e865', 'n1_w230', '9b44d37d1',
            'e485a0b3f', 'c9e9e83b8', '03bca8089', '95e210be1', 'e3665b334', 'b5d62792d',
            'r961', 'r962', 'r963', '6744db794 x-guard']:
    out[tok] = t.count(tok.rstrip(' x-guard'))
m = re.search(r'stale = \[(.*?)\]\n# kept-line', e, re.S)
stale_block = m.group(1) if m else 'NOT FOUND'
out['editor_stale_has_48c321706'] = '48c321706' in stale_block
out['editor_stale_has_1e5ed3326'] = '1e5ed3326' in stale_block
for pat in ['count("1e5ed3326")', 'count("r956 dead window")', 'count("4e30ddf69")',
            'count("842f817ad")', 'count("48c321706")', 'count("2ae8553e6")']:
    out['editor_has ' + pat] = pat in e
print(json.dumps(out, indent=1))
open('results/_r963bmc_census_gaps.json', 'w', encoding='utf-8').write(json.dumps(out, indent=1))
