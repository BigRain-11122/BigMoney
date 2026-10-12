# -*- coding: utf-8 -*-
# r942 ground truth dump: exact template lines for every territory the W226 derive
# editor's pairs/asserts touch. Zero mutation -- read-only.
import io, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
T = io.open(os.path.join(HERE, "_w225bmc_freeze_edits.py"), encoding="utf-8", newline="").read()

def dump(pat, label, ctx=170):
    print(f"##### {label} / pattern={pat!r}")
    for m in re.finditer(pat, T, re.S):
        a, b = max(0, m.start() - ctx), min(len(T), m.end() + ctx)
        print(f"@{m.start()}:")
        print(T[a:b])
        print("-----")

dump(r"executed bm-c r93", "seat execution prose (r935/r937/r939 lineages)")
dump(r"sec\.8 upgrade proposal", "sec.8 note")
dump(r'r938 seat-time live face', "seat-time live face")
dump(r"prereg derived\+committed", "prereg derived+committed")
dump(r"r939 freeze-window bundle", "freeze-window bundle")
dump(r'19:1x', "19:1x finalize prose")
dump(r'"batch": "PERPETUAL-N1-W22\d"', "batch name asserts/inserts", 120)
dump(r"assert pf\.N1_BANDS\[22\d\] ==", "N1_BANDS runtime asserts", 100)
dump(r"finalize one-pass 19:1x", "finalize one-pass prose", 200)

# census file content (dead session's prep evidence)
c = os.path.join(HERE, "_r942bmc_editor_census.py")
print("##### CENSUS FILE (_r942bmc_editor_census.py)")
print(io.open(c, encoding="utf-8", newline="").read())
