"""_r472bmb_w14_identity.py -- W14 runner mechanical identity surgery
(tl13 -> tl14 rename face ONLY; r445/r464 precedent).

Laws: draft name carries NO formal runner path (runner_exists gate must
not fire on a partial build -- W13 Slice-A r464 law); every rename is
count-verified; zero semantic edits in this pass (pure identity tokens).

Identity tokens (Wave/RES dir/batch/file names/seed keys/seed literal
values/null-cell ids) ONLY -- axis names (sumn etc.) are frozen lineage
faces and are NOT renamed.  Section payloads (RESI/CNT kit, grammar
builder, exclusion loader, reform judge face, selftest legs) land as
separate follow-up edits per the slice plan.
"""
import os
import sys

SRC = "scripts/trial_labor_w13.py"
DST = "results/_r472bmb_w14_runner_draft.py"

text = open(SRC, encoding="utf-8").read()
orig = text
log = []


def rep(old, new, expect_min=1, name=""):
    global text
    n = text.count(old)
    if n < expect_min:
        print(f"IDENTITY-FAIL [{name}]: found {n} < {expect_min} of {old[:60]!r}")
        sys.exit(1)
    text = text.replace(old, new)
    log.append((name or old[:40], n))


# --- wave / batch / dir / file identity ---
rep("TRIAL_LABOR_W13", "TRIAL_LABOR_W14", 5, "WAVE token")
rep('WAVE = "TRIAL_LABOR_W14"', 'WAVE = "TRIAL_LABOR_W14"', 1, "WAVE const")
rep("trial_labor_w13", "trial_labor_w14", 6, "res-dir/seed-key token")
rep("w13_", "w14_", 8, "product file prefix")
rep("W13-NULL-", "W14-NULL-", 1, "null cell id")
rep("TRIAL_LAB_W13_SCREEN", "TRIAL_LAB_W14_SCREEN", 1, "screen batch")
rep("TRIAL_LAB_W13_JUDGE", "TRIAL_LAB_W14_JUDGE", 1, "judge batch")
rep("research/TRIAL_LABOR_W14_PREREG.md",
    "research/TRIAL_LABOR_W14_PREREG.md", 1, "prereg path")

# --- seed berth literals (values carried in derivation strings) ---
rep("20323000", "20327500", 2, "gen berth")
rep("20323500", "20328000", 2, "scrnull berth")
rep("20324000", "20328500", 3, "unc berth (incl dual-nulls seed comment)")

# --- raw cap O-1132 (5,000 -> 10,000: A 500 + B 9,500) ---
rep("N_B = 4500", "N_B = 9500", 1, "N_B cap")
rep('N_B = 4500', 'N_B = 9500', 0, "N_B cap dup guard")
rep("# family B raw draws (machinery round-robin)",
    "# family B raw draws (machinery round-robin; O-1132 10,000-cap: "
    "A500 + B9500)", 1, "N_B comment")

# --- frozen sha16 placeholder (measured + pinned post-build) ---
rep('FROZEN_SHA16 = "868cd0c6413636e6"',
    'FROZEN_SHA16 = "@@W14_SHA16@@"', 1, "sha pin placeholder")

# --- prior-wave sha dict: add the W13 entry ---
rep('''    "W12": tl12.FROZEN_SHA16,    # 67c86c9cf4ef1ca7
}''',
    '''    "W12": tl12.FROZEN_SHA16,    # 67c86c9cf4ef1ca7
    "W13": tl13.FROZEN_SHA16,    # 868cd0c6413636e6
}''', 1, "prior sha dict +W13")

# --- module docstring: blank out for the payload pass ---
head, sep, rest = text.partition('"""\nfrom __future__ import annotations')
if not sep:
    print("IDENTITY-FAIL: docstring terminator anchor absent")
    sys.exit(1)
text = '"""W14 runner docstring payload placeholder (replaced by the '
text += 'section pass).\n"""\nfrom __future__ import annotations' + rest
log.append(("docstring blanked", 1))

open(DST, "w", encoding="utf-8", newline="\n").write(text)
print(f"identity surgery OK: {len(orig)} -> {len(text)} bytes, "
      f"{len(log)} rename steps")
for name, n in log:
    print(f"  [{name}] x{n}")
