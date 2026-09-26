# r275 bm-b: T-83 ticket close-out splice (byte-level, r266 mixed-escape-face law).
# The ticket file carries per-field heterogeneous escape faces (bm-a r266 splice
# precedent), so a JSON round-trip rewrite is FORBIDDEN (it silently re-encodes
# untouched fields). Splice only: status line swap + two new fields before '}'.
import json

p = 'fleet/tasks/T-2026-09-26-83-P1.json'
raw = open(p, 'rb').read()
assert raw.count(b'"status": "claimed"') == 1, 'status line not unique'
raw = raw.replace(b'"status": "claimed"', b'"status": "done"')

ref = (' "result_ref": "all four slices delivered + post_review all YES ('
       'S1 nine-layer research/AUDIT-20260926-FULL.md + snapshot governance_audit_20260926.json bm-b r267; '
       'S2 detector scripts/governance_audit_s2.py selftest 9/9 bm-b r268; '
       'S3 GM seven deliverables firm/JUDGMENT_MATRIX+ACCOUNT_LIFECYCLE+DOC_HIERARCHY+'
       'research/ORDERS_INDEX+AUDIT-20260926-S2-ADJUDICATION+STRATEGY_LIBRARY section-0 bm-a r269/r270; '
       'S4 quarterly wiring bm-a r266, 2027-01-01 next instance) '
       '-- final review 21:56: S1/S2/S4/S3-GM-DELIVERABLES/S3-GM-SLICE2 all YES, 0 NO",\n'
       ' "done_at": "2026-09-26 22:20"\n').encode('utf-8')
i = raw.rindex(b'\n}')
raw = raw[:i] + b',\n' + ref + b'}' + raw[i + 2:]
open(p, 'wb').write(raw)
json.loads(raw.decode('utf-8-sig'))
print('VALID JSON, spliced')
