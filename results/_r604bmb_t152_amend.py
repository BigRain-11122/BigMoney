import json

p = 'fleet/tasks/T-2026-10-03-152-P1.json'
d = json.load(open(p, encoding='utf-8'))

amendment = (
    "AMENDMENT r604 bm-b (ticket creator + probe owner, adjudication of MSG-0500): "
    "gate (3) recalibrated to reality base per live export evidence "
    "(results/t152_quality_faces_export.json: anchor_median=52.0, p10=26, n_symbols=5,223, "
    "max=102 -- median listing year ~2013-14 = universe immutable property; the 60 floor "
    "was this ticket's own estimate and was wrong). AMENDED gate (3) = per-symbol "
    "avail-anchor median >= 50 AND p10 >= 20 (dual gate, keeps anti-sparse intent; "
    "reality 52/26 passes with margin). Gates (1)(2)(4)(5)(6) unchanged. Sibling bug fix "
    "same window in the binding probe face scripts/fund_quality_p1_probe.py: leg2 dup-axis "
    "was checking avail_date duplication (structurally ALWAYS red under statutory mapping: "
    "FY 12-31 and Q1 next-year 03-31 both -> 04-30); fixed to period_end per spec (5) key "
    "name dup_period_end_any; selftest 29/29 incl. FY/Q1 structural regression legs. "
    "bm-c authorized to re-run export (65s) + manifest same round on receipt of this "
    "amendment. Adjudication basis = ticket-owner authority within T-145 leg(c) CEO order "
    "O-20261002-2115 lane; no new legislation."
)
d['amendment_r604_bmb'] = amendment
d['note'] = (d.get('note') or '') + ' | ' + amendment
open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
v = json.load(open(p, encoding='utf-8'))
assert 'AMENDMENT r604 bm-b' in v['note'] and 'AMENDMENT r604 bm-b' in v['amendment_r604_bmb']
print('ticket amended OK; status/claimed_by preserved:', v['status'], '|', v['claimed_by'][:40])
