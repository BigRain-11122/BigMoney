"""r442 bm-b patch-2: L9a stale mom=none law -> W11 real law (W10 rows
carry real mom values; std=none at 13 for ALL prior rows) + L10b probe
key missing the std slot (13-long axis -> IndexError in _excluded_w11)."""
import io

p = 'scripts/trial_labor_w11.py'
src = io.open(p, encoding='utf-8').read()
edits = [
    # L9a: W1-W9 sources mom=none; W10 sources real mom; ALL std=none
    ('    _ok("L9a exclusion loader: every row a 14-tuple axis with "\n'
     '        "mom=none + disclosure keys present (20 sources)",\n'
     '        all(len(r["axis"]) == 14 and r["axis"][12] == "none"\n'
     '            for r in rows10)\n'
     '        and {"w1_screen_survivors", "mass_screen_survivors",\n'
     '             "w9_screen_survivors", "w9_judge_products",\n'
     '             "judged_supply_weighting"} <= set(disc10))',
     '    _ok("L9a exclusion loader: every row a 14-tuple axis, std=none "\n'
     '        "at 13 for ALL rows + mom at 12 inside the frozen binary "\n'
     '        "domain + W10 real-mom rows present (20 sources; W1-W9 "\n'
     '        "sources mom=none, W10 survivors/judged carry real values)",\n'
     '        all(len(r["axis"]) == 14 and r["axis"][13] == "none"\n'
     '            and r["axis"][12] in AXIS_MOM for r in rows10)\n'
     '        and any(r["axis"][12] == "mom_oversold"\n'
     '                for r in rows10)\n'
     '        and {"w1_screen_survivors", "mass_screen_survivors",\n'
     '             "w9_screen_survivors", "w9_judge_products",\n'
     '             "w10_screen_survivors", "w10_judge_products",\n'
     '             "judged_supply_weighting"} <= set(disc10))'),
    # L10b: constructed new-syntax key must be a full fourteen-tuple
    ('    miss = _excluded_w11({**hit_key,\n'
     '                          "axis": [*hit_key["axis"][:12],\n'
     '                                   "mom_oversold"]}, rows10)',
     '    miss = _excluded_w11({**hit_key,\n'
     '                          "axis": [*hit_key["axis"][:12],\n'
     '                                   "mom_oversold", "none"]},\n'
     '                         rows10)'),
]
for i, (old, new) in enumerate(edits, 1):
    n = src.count(old)
    assert n == 1, f"E{i}: found {n} occurrences (expected 1)"
    src = src.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='\n').write(src)
print(f"patch-2: all {len(edits)} edits applied cleanly")
