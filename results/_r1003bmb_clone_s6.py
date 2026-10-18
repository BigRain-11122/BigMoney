# -*- coding: utf-8 -*-
import io

src = io.open(r'Tools\_r991bmb_s6.py', encoding='utf-8').read()
t = src.replace('r991', 'r1003')
t = t.replace('37 standing legs (clone of _r946bmb_s6.py recipe',
              '38 legs (clone of _r991bmb_s6.py recipe per r836 clone law')
old_note = ('newbar-gated family removed (live_paper/t35_open_fill_verify/t24_prospect_paper/'
            't24_prospect_promotion) because Saturday 2026-10-17 has no new bar '
            '(r990 precedent: live.paper family skipped no-new-bar).')
new_note = ('newbar-gated family removed (Sunday 2026-10-18 no new bar, r990/r1002 precedent); '
            'attrition_scan appended (r1002 43-leg parity minus orphan/smoke/d19/sat/idle '
            'run in-round already).')
t = t.replace(old_note, new_note)
anchor = '    ("token_meter", [PY, "scripts/token_meter.py"]),'
addition = anchor + '\n    ("attrition_scan", [PY, "scripts/attrition_ledger_guard.py", "scan"]),'
assert anchor in t, 'token_meter anchor missing'
t = t.replace(anchor, addition)
io.open(r'Tools\_r1003bmb_s6.py', 'w', encoding='utf-8', newline='').write(t)
print('driver written', len(t), 'legs attrition added:', addition in t)
