# -*- coding: utf-8 -*-
# r964 W231 tpl generator: machine-advances the committed W230 tpl
# (results/_w230bmc_prereg_derive_tpl.py) one wave. Every replacement is
# assert-verified count==1 on the source before application (zero silent
# misses); structural additions (blob row, SUB30 extract, OLD30 lvl step,
# preflight/PAIRS pointer, STALE/NEW tables, in-band asserts) are explicit.
import py_compile, sys
sys.stdout.reconfigure(encoding="utf-8")
SRC = r"results\_w230bmc_prereg_derive_tpl.py"
DST = r"results\_w231bmc_prereg_derive_tpl.py"
t = open(SRC, encoding="utf-8").read()

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"rep count {c} != {n}: {old[:70]!r}"
    t = t.replace(old, new)
    assert t.count(new) >= 1

# ---- header ----
rep("# W230 per-wave prereg derivation (bm-c r963 freeze-prep, 2026-10-13 10:4x).",
    "# W231 per-wave prereg derivation (bm-c r964 freeze-prep, 2026-10-13 12:2x).")
rep("""# Method: machine transform of the freeze-time W229 prereg blob
# (git show e485a0b3f:research/PERPETUAL_N1_W229_PREREG.md -- the exact
# pre-backfill commit face; the sec.7/8 machine-read backfill landed later in
# f4b24e865) with an explicit ordered replacement table.""",
    """# Method: machine transform of the freeze-time W230 prereg blob
# (git show 91de0ae83:research/PERPETUAL_N1_W230_PREREG.md -- the exact
# pre-backfill commit face; the sec.7/8 machine-read backfill landed later in
# ce70c5808) with an explicit ordered replacement table.""")
rep("""# _w225 SUB + _w226 SUB + _w227 SUB + _w228 SUB + _w229 SUB literals --
# FOURTEEN-LEVEL replay chain, one deeper than the W229 thirteen-level chain;""",
    """# _w225 SUB + _w226 SUB + _w227 SUB + _w228 SUB + _w229 SUB + _w230 SUB literals --
# FIFTEEN-LEVEL replay chain, one deeper than the W230 fourteen-level chain;""")
rep("""# table are machine-generated from the committed _w229 SUB new-sides by
# results/_w230bmc_subgen.py (m27 materialization; zero transcription).
# Bands/facts machine-derived from the committed ADMIT receipt
# results/_w230bmc_20261013_probe_receipt.json + n1_w229_results.json +
# _w229bmc_freeze_receipt.json -- never transcribed by eye (r587).""",
    """# table are machine-generated from the committed _w230 SUB new-sides by
# results/_w231bmc_subgen.py (m28 materialization; zero transcription).
# Bands/facts machine-derived from the committed ADMIT receipt
# results/_w231bmc_20261013_probe_receipt.json + n1_w230_results.json +
# _w230bmc_freeze_receipt.json -- never transcribed by eye (r587).""")

# ---- blob chain ----
rep("""t228 = blob("e6c8441aa", "research/PERPETUAL_N1_W228_PREREG.md")  # RAM/label face (SUB28/29 BinOps)
t = blob("e485a0b3f", "research/PERPETUAL_N1_W229_PREREG.md")    # base: freeze-time W229 face""",
    """t228 = blob("e6c8441aa", "research/PERPETUAL_N1_W228_PREREG.md")  # RAM/label face (SUB28/29 BinOps)
t229 = blob("e485a0b3f", "research/PERPETUAL_N1_W229_PREREG.md")  # RAM/label face (SUB29/30 BinOps)
t = blob("91de0ae83", "research/PERPETUAL_N1_W230_PREREG.md")    # base: freeze-time W230 face""")

# ---- RAM/WIN label var rows ----
rep("""RAM_FACE_228 = ram_face(t228)
RAM_FACE_229 = ram_face(t)""",
    """RAM_FACE_228 = ram_face(t228)
RAM_FACE_229 = ram_face(t229)
RAM_FACE_230 = ram_face(t)""")
rep("""WIN_LABEL_228 = win_label(t228)
WIN_LABEL_229 = win_label(t)""",
    """WIN_LABEL_228 = win_label(t228)
WIN_LABEL_229 = win_label(t229)
WIN_LABEL_230 = win_label(t)""")
rep('| W229-face {RAM_FACE_229!r} | WIN_LABEL_REPLAY', '| W229-face {RAM_FACE_229!r} | W230-face {RAM_FACE_230!r} | WIN_LABEL_REPLAY')
rep('| WIN_LABEL_229 {WIN_LABEL_229!r}")', '| WIN_LABEL_229 {WIN_LABEL_229!r} | WIN_LABEL_230 {WIN_LABEL_230!r}")')

# ---- SUB30 extract (append after SUB29 extract) ----
rep("""SUB29 = extract_lit(r"results\\_w229bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_228": WIN_LABEL_228, "WIN_LABEL": WIN_LABEL_229,
                          "RAM_FACE_228": RAM_FACE_228, "RAM_GB": RAM_FACE_229})""",
    """SUB29 = extract_lit(r"results\\_w229bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_228": WIN_LABEL_228, "WIN_LABEL": WIN_LABEL_229,
                          "RAM_FACE_228": RAM_FACE_228, "RAM_GB": RAM_FACE_229})
SUB30 = extract_lit(r"results\\_w230bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_229": WIN_LABEL_229, "WIN_LABEL": WIN_LABEL_230,
                          "RAM_FACE_229": RAM_FACE_229, "RAM_GB": RAM_FACE_230})""")

# ---- OLD30 lvl step (append after OLD29) ----
rep('''OLD29 = lvl(OLD28, SUB29, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@L25@", "225"), ("@L26@", "226"), ("@L27@", "227"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25"), ("@T25@", "26"), ("@T26@", "27"), ("@T27@", "28")])''',
    '''OLD29 = lvl(OLD28, SUB29, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@L25@", "225"), ("@L26@", "226"), ("@L27@", "227"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25"), ("@T25@", "26"), ("@T26@", "27"), ("@T27@", "28")])
OLD30 = lvl(OLD29, SUB30, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@L25@", "225"), ("@L26@", "226"), ("@L27@", "227"), ("@L28@", "228"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25"), ("@T25@", "26"), ("@T26@", "27"), ("@T27@", "28"), ("@T28@", "29")])''')

# ---- preflight pointer ----
rep("""# preflight: every replayed W229-face block sits exactly once in the blob
for i, old in enumerate(OLD29):
    c = t.count(old)
    assert c == 1, f"preflight block[{i}] count {c} != 1 in freeze-time W229 blob"
print("preflight OK: 46/46 replayed blocks sit count==1 in the freeze-time W229 blob")""",
    """# preflight: every replayed W230-face block sits exactly once in the blob
for i, old in enumerate(OLD30):
    c = t.count(old)
    assert c == 1, f"preflight block[{i}] count {c} != 1 in freeze-time W230 blob"
print("preflight OK: 46/46 replayed blocks sit count==1 in the freeze-time W230 blob")""")

# ---- anchors block ----
rep('rec = json.load(open(r"results\\_w230bmc_20261013_probe_receipt.json", encoding="utf-8"))',
    'rec = json.load(open(r"results\\_w231bmc_20261013_probe_receipt.json", encoding="utf-8"))')
rep('assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "520804_522803", "B": "522804_523003"}',
    'assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "523004_525003", "B": "525004_525203"}')
rep("""w229 = json.load(open(r"results\\perpetual_faces\\n1_w229_results.json", encoding="utf-8"))
led = w229["science_gates"]["ledger"]
assert led["total"] == 927589 and led["prev_total"] == 925389 and led["batch_trials"] == 2200
merged = w229["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 501720
w229only = w229["null_pool_cumulative"]["w229_only"]
A_p95 = w229["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w229["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 925389
assert kl["line_pre_w229"] == 1.1919 and kl["line_merged_501720"] == 1.1919
se_mu = w229["null_pool_cumulative"]["se_mu_at_k501720"]
assert se_mu == 0.000346""",
    """w230 = json.load(open(r"results\\perpetual_faces\\n1_w230_results.json", encoding="utf-8"))
led = w230["science_gates"]["ledger"]
assert led["total"] == 929789 and led["prev_total"] == 927589 and led["batch_trials"] == 2200
merged = w230["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 503920
w230only = w230["null_pool_cumulative"]["w230_only"]
A_p95 = w230["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w230["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 927589
assert kl["line_pre_w230"] == 1.192 and kl["line_merged_503920"] == 1.1919
se_mu = w230["null_pool_cumulative"]["se_mu_at_k503920"]
assert se_mu == 0.000345""")
rep("""assert leg1["A"] == [520804, 522803] and leg1["B"] == [522804, 523003]
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [520604, 522603] and leg1["B_naive_first_clean"] == [520804, 521003]
assert leg4["W230p_A"] == "522804..524803" and leg4["W230p_B"] == "523004..523203"
assert leg4["W230p_B_lands_inside_W230p_A"] is True""",
    """assert leg1["A"] == [523004, 525003] and leg1["B"] == [525004, 525203]
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [522804, 524803] and leg1["B_naive_first_clean"] == [523004, 523203]
assert leg4["W231p_A"] == "525004..527003" and leg4["W231p_B"] == "525204..525403"
assert leg4["W231p_B_lands_inside_W231p_A"] is True""")
rep("""assert leg0["rows"] == 227 and leg0["owner_rows"] == 219 and leg0["bmc_rows"] == 59 \\
       and leg0["bmc_ordinal"] == 60 and leg0["ordinal"] == 220
assert "attempt-continuity" in leg0["bmc_ordinal_note"] and "59th owned" in leg0["bmc_ordinal_note"]
fr = json.load(open(r"results\\_w229bmc_freeze_receipt.json", encoding="utf-8"))
assert fr["ordinal_faces"]["bmc_own_ordinal"] == 59  # "59th owned 承袭" prose anchor""",
    """assert leg0["rows"] == 228 and leg0["owner_rows"] == 220 and leg0["bmc_rows"] == 60 \\
       and leg0["bmc_ordinal"] == 61 and leg0["ordinal"] == 221
assert "attempt-continuity" in leg0["bmc_ordinal_note"] and "60th owned" in leg0["bmc_ordinal_note"]
fr = json.load(open(r"results\\_w230bmc_freeze_receipt.json", encoding="utf-8"))
assert fr["ordinal_faces"]["bmc_own_ordinal"] == 60  # "60th owned 承袭" prose anchor""")
rep("""assert fmt8(merged["mu"]) == "\\u2212" + "0.09270128", fmt8(merged["mu"])
assert fmt8(w229only["mu"]) == "\\u2212" + "0.08818286", fmt8(w229only["mu"])
assert f"{merged['sigma']:.8f}" == "0.24507549", f"{merged['sigma']:.8f}"
assert f"{abs(w229only['mu'] - merged['mu']):.4f}" == "0.0045", f"{abs(w229only['mu'] - merged['mu']):.4f}"
assert f"{A_p95:.4f}" == "0.3199", f"{A_p95:.4f}"
assert f"{kl['line_merged_501720']:.4f}" == "1.1919"
assert f"{kl['line_delta_k_lift']:+.4f}" == "+0.0000"  # ASCII f-string face; prose token uses + sign (zero-lift face)""",
    """assert fmt8(merged["mu"]) == "\\u2212" + "0.09269286", fmt8(merged["mu"])
assert fmt8(w230only["mu"]) == "\\u2212" + "0.090772", fmt8(w230only["mu"])
assert f"{merged['sigma']:.8f}" == "0.24504776", f"{merged['sigma']:.8f}"
assert f"{abs(w230only['mu'] - merged['mu']):.4f}" == "0.0019", f"{abs(w230only['mu'] - merged['mu']):.4f}"
assert f"{A_p95:.4f}" == "0.3069", f"{A_p95:.4f}"
assert f"{kl['line_merged_503920']:.4f}" == "1.1919"
assert f"{kl['line_delta_k_lift']:+.4f}" == "-0.0001"  # ASCII f-string face; prose token uses U+2212 sign (W230 face -0.0001)""")

# ---- freeze-window live label ----
rep("""# freeze-window label (live honesty): this derivation runs in r963, 2026-10-13""",
    """# freeze-window label (live honesty): this derivation runs in r964, 2026-10-13""")
rep('print(f"freeze-window label: r963 {WIN_LABEL}")',
    'print(f"freeze-window label: r964 {WIN_LABEL}")')

# ---- PAIRS build pointer ----
rep("""# ---------- build + apply W230 pairs ----------
PAIRS = []
for i, old in enumerate(OLD29):""",
    """# ---------- build + apply W231 pairs ----------
PAIRS = []
for i, old in enumerate(OLD30):""")

# ---- generic shift block ----
rep("""# ---- generic wave-token shifts (after targeted pairs) ----
# Pairs covered every W229 self face (each count==1 asserted). Remaining
# "W229" tokens = pair-written legit refs (chain W229 leg, refusing band,
# W229 finalize keys, W1..W229 scope) which must STAY W229 -- mask, then age
# one-wave-older W228 refs to W229, then restore. @L28@/@T28@ hold heritage
# tokens immune.
t = t.replace("n1_w229_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W229", "PERPETUAL-N1-W230")
t = t.replace("PERPETUAL_N1_W229", "PERPETUAL_N1_W230")
t = t.replace("n1_w229", "n1_w230")
t = t.replace("_w229bmc", "_w230bmc")
t = t.replace("W229", "@U_W@")
t = t.replace("W228", "W229")
t = t.replace("n1_w228", "n1_w229")
t = t.replace("PERPETUAL_N1_W228", "PERPETUAL_N1_W229")
t = t.replace("_w228bmc", "_w229bmc")
t = t.replace("@u_w@", "w229")
t = t.replace("@U_W@", "W229")
t = t.replace("@L28@", "228")
t = t.replace("@T28@", "29")""",
    """# ---- generic wave-token shifts (after targeted pairs) ----
# Pairs covered every W230 self face (each count==1 asserted). Remaining
# "W230" tokens = pair-written legit refs (chain W230 leg, refusing band,
# W230 finalize keys, W1..W230 scope) which must STAY W230 -- mask, then age
# one-wave-older W229 refs to W230, then restore. @L29@/@T29@ hold heritage
# tokens immune.
t = t.replace("n1_w230_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W230", "PERPETUAL-N1-W231")
t = t.replace("PERPETUAL_N1_W230", "PERPETUAL_N1_W231")
t = t.replace("n1_w230", "n1_w231")
t = t.replace("_w230bmc", "_w231bmc")
t = t.replace("W230", "@U_W@")
t = t.replace("W229", "W230")
t = t.replace("n1_w229", "n1_w230")
t = t.replace("PERPETUAL_N1_W229", "PERPETUAL_N1_W230")
t = t.replace("_w229bmc", "_w230bmc")
t = t.replace("@u_w@", "w230")
t = t.replace("@U_W@", "W230")
t = t.replace("@L29@", "229")
t = t.replace("@T29@", "30")""")

print("phase A OK: header/blobs/extracts/OLD30/anchors/shift advanced")
open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print("tpl written + py_compile OK:", DST, "bytes:", len(t.encode("utf-8")))
