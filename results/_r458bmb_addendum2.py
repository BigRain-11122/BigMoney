import io

# 1. fix stale freeze-hash refs (c88e7dea4 -> b809b59d1)
for p, expect in (('logs/iteration-loop/round_reports.md', 3), ('state.json', 1)):
    s = io.open(p, encoding='utf-8').read()
    n = s.count('c88e7dea4')
    assert n == expect, (p, n, expect)
    s = s.replace('c88e7dea4', 'b809b59d1')
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print(p, 'refs fixed:', n)

ADDENDUM2 = (
    "\n2026-09-30T11:3x+08:00 | r458 ADDENDUM-2 bm-b | second rebase receipt: first push post-rebase rejected "
    "again (fleet high-traffic window: bm-c r266 runner-build + 2 carry commits landed) -> fetch-verify then "
    "rebase #2 onto bm-c tip 99f7f8820: batch-3 (_r458bmb_resolve3.py, 3 UU on r457 replay: compute_audit union "
    "201+207->208 + regime union 3+3->3 + fundamental_status take-m MANUAL truth-wins SECOND adjudication "
    "(origin 11:28 bm-c pre-fix rc2 face vs mine 10:55 post-fix rc0 face; fix rides this chain)) + freeze "
    "replayed clean again (hash drift c88e7dea4 -> b809b59d1, refs fixed) + batch-4 (resolver2 rerun, 19 UU on "
    "closing replay: ALL take-c legal = bm-c 11:26-11:28 same-day idempotent regen faces newer than my "
    "11:18-11:21 faces; marks union 21+22->22) + ONE truth-override post-batch: fundamental_b_layer_filter "
    "restored to my 11:21 face (content check: eligibility_rows 11635 / eligibility_asof 2026-09-30 10:55:14 "
    "== tree's post-fix eligibility.csv; bm-c 11:28 face was pre-fix-derived vs data files this chain carries "
    "-- same truth-wins class as fundamental_status, documented); pushing now, third rejection = fallback "
    "branch machine/bm-b-r458 per protocol\n"
)

p = 'logs/iteration-loop/round_reports.md'
with io.open(p, 'a', encoding='utf-8', newline='') as f:
    f.write(ADDENDUM2)
print('addendum-2 appended')
