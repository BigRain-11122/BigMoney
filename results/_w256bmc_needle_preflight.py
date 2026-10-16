# -*- coding: utf-8 -*-
# r1058 bm-c: needle pre-flight probe for the W256 derive editor
# (counts every planned needle against results/_w255bmc_freeze_edits.py
#  -- the committed SRC at blob 6c6397d375d7f5a475b7579ef320c280d6d4d4f7).
# Needle law: needle = age(prev_new) where age = P2(W256->W257) +
# P3(255->256) + P4(254->255) applied to the W255 editor's NEW literals.
import io, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w255bmc_freeze_edits.py")
GIT = "C:/Program Files/Git/cmd/git.exe"

blob_wt = subprocess.run([GIT, "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
blob_head = subprocess.run([GIT, "rev-parse", "HEAD:results/_w255bmc_freeze_edits.py"], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert blob_wt == blob_head == "6c6397d375d7f5a475b7579ef320c280d6d4d4f7", f"SRC drift {blob_wt} vs {blob_head}"

def age(s):
    s = s.replace("W256", "W257")
    s = s.replace("255", "256")
    s = s.replace("254", "255")
    return s

t0 = io.open(SRC, encoding="utf-8").read()

# simulate P1 (structural, pre-blanket) + P2/P3/P4 blankets exactly as the editor will run them
t = t0
t = t.replace("(251, 250, 249, 248, 247, 246, 245, 244, 243, 242)",
              "(252, 251, 250, 249, 248, 247, 246, 245, 244, 243)")
t = t.replace("range(209, 256)", "range(209, 257)")
t = t.replace('def fmt(n):  # 576301 -> "576_301"', 'def fmt(n):  # 578501 -> "578_501"')
t = t.replace("W256", "W257")
t = t.replace("255", "256")
t = t.replace("254", "255")

# (label, raw-needle-or-prev-new, is_age_applied)  -> count in T0 (post-blanket simulation)
NEEDLES = [
    # P1
    ("P1-transitive-deps", "(251, 250, 249, 248, 247, 246, 245, 244, 243, 242)", False),
    ("P1-liveness-range", "range(209, 256)", False),
    ("P1-fmt-comment", 'def fmt(n):  # 576301 -> "576_301"', False),
    # P5a (age of prev_new)
    ("P5a-ledger-int", "983_135", False),
    ("P5a-k-int", "556_720", False),
    ("P5a-ledger-prose", "983,135", False),
    ("P5a-k-prose", "556,720", False),
    ("P5a-ordinal", "bmc_ordinal=75", False),
    ("P5a-seventy", "SEVENTY-FIFTH", False),
    ("P5a-250th", "TWO HUNDRED AND FIFTY-FIFTH", False),
    ("P5a-finface", "forty-third consecutive", False),
    ("P5a-ownwave", "75th own wave", False),
    ("P5a-seat-msg", "MSG-20261016-22xx-bmc-w255-seat", True),
    ("P5a-seat-origin", "cb79242ed", False),
    ("P5a-prereg-commit", "72d292ea3", False),
    ("P5a-header-window", "2026-10-17 02:0x bm-c r1057 freeze window", False),
    ("P5a-closeout-window", "W254 finalize one-pass bm-c r1055 window closeout 21:3x", True),
    ("P5a-splice-window", "r1055 splice window", False),
    ("P5a-r1055-rest", "r1055", False),
    ("P5a-prereg-window", "r1056", False),
    ("P5a-authored-time", "authored 01:14", False),
    ("P5a-aging-deps-cmt", "transitive window W242..W251 checked", False),
    ("P5a-aging-rows-heal", "engine_owner==bm-c rows 74 + candidate", False),
    # P5b
    ("P5b-hdr-ownlegs", "# block's own W239..W253 legs (15 rows) do NOT enter the estate path;", False),
    ("P5b-hdr-freshlegs", "# after extraction, fresh W239..W254 legs (16 rows) are added,", True),
    ("P5b-hdr-parity-count", "# parity = 113 rows (W138..W206 + W211..W254). Zero assumption zero risk.", True),
    ("P5b-ext-excl", "# block's own W239..W253 legs (15) are EXCLUDED from the estate path per the", False),
    ("P5b-ext-fresh", "# prereg mandate; the W255 block appends fresh W239..W254 legs (16,", True),
    ("P5b-ext-parcount", "# machine-derived from the LIVE pf registry at freeze time) -> 113 parity", False),
    ("P5b-parfull-111", '== 112', False),
    ("P5b-parfull-msg", "!= 112 (69 estate + W211..W253 legs 43)", False),
    ("P5b-legs-42", '== 43', False),
    ("P5b-legs-range", "list(range(211, 254))", False),
    ("P5b-legs-msg", "legs segment not W211..W253 forty-three legs", False),
    ("P5b-dropped-14", '== 15', False),
    ("P5b-dropped-range", "list(range(239, 254))", False),
    ("P5b-dropped-msg", "dropped segment not W239..W253 fifteen legs", False),
    ("P5b-split-cmt", "# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W254\n# block's own W239..W253 legs (15) are excluded from the estate path", True),
    ("P5b-rcpt-fresh", '"fresh_legs_row_asserts": 16,', False),
    ("P5b-rcpt-total", '+ legs_kept.count("assert pf.N1_BANDS[") + 16,', False),
    ("P5b-ownlegs-mat", "\"    #     physical bytes; the W254 block's own W239..W253 legs (15) are\",", True),
    ("P5b-freshlegs-mat", '"    #     W239..W254 legs (16) added, machine-derived from the live pf",', True),
    ("P5b-parcount-mat", '"    #     registry at freeze time -> 113 parity rows (W138..W206+W211..W254).",', True),
    ("P5b-rcpt-note-excl", "own W239..W253 legs (15) EXCLUDED", False),
    ("P5b-rcpt-note-fresh", "fresh W239..W254 legs (16) machine-derived", True),
    ("P5b-rcpt-note-block", "W255 block = 113 rows", True),
    ("P5b-rcpt-note-e63", "E63 7th-gen", False),
    ("P5b-rcpt-note-b", "(w244_a holds wave-254 bands)", True),
    # P5c
    ("P5c-band-drift", 'assert (a_lo, a_hi) == (576_301, 578_300) and (b_lo, b_hi) == (578_301, 578_500), \\', False),
    # P5d
    ("P5d-ord-gate", 'assert len(owner_rows_live) == 244 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 74, \\', False),
    ("P5d-ord-err", "(expect 244/129/74 PRE-splice post-W254 registration", True),
    ("P5d-leg0-prose", "# receipt leg0 face owner_rows=244 / bmc_rows=74 /", False),
    ("P5d-ord-owner-prose", "-> owner rows 244 + candidate = 245th EXACT; bm-c rows 74 +", False),
    ("P5d-ord-bmc-prose", "# candidate = 75th EXACT -- bm-c own-seat continuity face (bm-c published the", False),
    ("P5d-rcpt-244rd", "freeze-time live face owner rows 244 + candidate = 245th EXACT", False),
    ("P5d-bundle-74th", "freeze-time live derive bmc rows 74 + candidate 75th EXACT per r587/r359", False),
    ("P5d-rcpt-73rd-owned", "post-W254 registration: bm-c rows 74 + candidate = 75th owned", True),
    ("P5d-rcpt-ordface", '"probe_receipt_bmc_ordinal_face": 75,', False),
    ("P5d-print-deps", 'f"W255+W250..W241 finalize products present "', True),
]

print(f"SRC blob verified {blob_wt[:16]}")
fails = 0
for label, needle, apply_age in NEEDLES:
    n = age(needle) if apply_age else needle
    c = t.count(n)
    print(f"{label}: {c}x  {n[:76]!r}")
print(f"total bytes {len(t.encode('utf-8'))}")
