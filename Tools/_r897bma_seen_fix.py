# -*- coding: utf-8 -*-
# r897 fix: last_decisions_seen narrative (PS-join artifact correction)
import json
ST = 'state-bm-a.json'
with open(ST, encoding='utf-8') as fh:
    st = json.load(fh)
st['last_decisions_seen'] = ("r897: DEC 83813196 python-canonical UNCHANGED (02:5x PS-join hash "
    "48aeaf1f = bad-provenance artifact family r813/r828, content re-verified byte-identical); "
    "D-20261009-01-03 + D-20261009-02 dispatch rows explicitly re-adjudicated this round "
    "(01-03 = bm-c in-progress yield + stall-watch; 02 = bm-a living first-proof QA pack)")
with open(ST, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(st, fh, ensure_ascii=False, indent=2)
chk = json.load(open(ST, encoding='utf-8'))
assert chk['round_no'] == 897
print('fixed ok:', chk['last_decisions_seen'][:80])
