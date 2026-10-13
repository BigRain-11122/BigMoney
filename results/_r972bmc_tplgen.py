# -*- coding: utf-8 -*-
# r972 W233 tpl generator: machine-advances the committed W232 tpl
# (results/_w232bmc_prereg_derive_tpl.py) one wave. Every replacement is
# assert-verified count==1 on the source before application (zero silent
# misses); structural additions (blob row, SUB32 extract, OLD32 lvl step,
# preflight/PAIRS pointer, anchors block, shift block) are explicit.
import sys
sys.stdout.reconfigure(encoding="utf-8")
SRC = r"results\_w232bmc_prereg_derive_tpl.py"
DST = r"results\_w233bmc_prereg_derive_tpl.py"
t = open(SRC, encoding="utf-8").read()

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"rep count {c} != {n}: {old[:70]!r}"
    t = t.replace(old, new)
    assert t.count(new) >= 1

# ---- header ----
rep("# W232 per-wave prereg derivation (bm-c r967 freeze-prep, 2026-10-13 13:4x).",
    "# W233 per-wave prereg derivation (bm-c r972 freeze-prep, 2026-10-13 17:5x).")
rep("""# Method: machine transform of the freeze-time W231 prereg blob
# (git show aebe0a5ac:research/PERPETUAL_N1_W231_PREREG.md -- the exact
# pre-backfill commit face; the sec.7/8 machine-read backfill landed later in
# 0636c1d12) with an explicit ordered replacement table.""",
    """# Method: machine transform of the freeze-time W232 prereg blob
# (git show a3a7aa632:research/PERPETUAL_N1_W232_PREREG.md -- the exact
# pre-backfill commit face; the sec.7/8 machine-read backfill landed later in
# 59856ff28) with an explicit ordered replacement table.""")
rep("""# _w225 SUB + _w226 SUB + _w227 SUB + _w228 SUB + _w229 SUB + _w230 SUB + _w231 SUB literals --
# SIXTEEN-LEVEL replay chain, one deeper than the W231 fifteen-level chain;""",
    """# _w225 SUB + _w226 SUB + _w227 SUB + _w228 SUB + _w229 SUB + _w230 SUB + _w231 SUB + _w232 SUB literals --
# SEVENTEEN-LEVEL replay chain, one deeper than the W232 sixteen-level chain;""")
rep("""# table are machine-generated from the committed _w231 SUB new-sides by
# results/_w232bmc_subgen.py (m29 materialization; zero transcription).
# Bands/facts machine-derived from the committed ADMIT receipt
# results/_w232bmc_20261013_probe_receipt.json + n1_w231_results.json +
# _w231bmc_freeze_receipt.json -- never transcribed by eye (r587).""",
    """# table are machine-generated from the committed _w232 SUB new-sides by
# results/_w233bmc_subgen.py (m30 materialization; zero transcription).
# Bands/facts machine-derived from the committed ADMIT receipt
# results/_w233bmc_20261013_probe_receipt.json + n1_w232_results.json +
# _w232bmc_freeze_receipt.json -- never transcribed by eye (r587).""")

# ---- blob chain ----
rep("""t230 = blob("91de0ae83", "research/PERPETUAL_N1_W230_PREREG.md")  # RAM/label face (SUB30/31 BinOps)
t = blob("aebe0a5ac", "research/PERPETUAL_N1_W231_PREREG.md")    # base: freeze-time W231 face""",
    """t230 = blob("91de0ae83", "research/PERPETUAL_N1_W230_PREREG.md")  # RAM/label face (SUB30/31 BinOps)
t231 = blob("aebe0a5ac", "research/PERPETUAL_N1_W231_PREREG.md")  # RAM/label face (SUB31/32 BinOps)
t = blob("a3a7aa632", "research/PERPETUAL_N1_W232_PREREG.md")    # base: freeze-time W232 face""")

# ---- RAM/WIN label var rows ----
rep("""RAM_FACE_230 = ram_face(t230)
RAM_FACE_231 = ram_face(t)""",
    """RAM_FACE_230 = ram_face(t230)
RAM_FACE_231 = ram_face(t231)
RAM_FACE_232 = ram_face(t)""")
rep("""WIN_LABEL_230 = win_label(t230)
WIN_LABEL_231 = win_label(t)""",
    """WIN_LABEL_230 = win_label(t230)
WIN_LABEL_231 = win_label(t231)
WIN_LABEL_232 = win_label(t)""")
rep('| W229-face {RAM_FACE_229!r} | W230-face {RAM_FACE_230!r} | W231-face {RAM_FACE_231!r} | WIN_LABEL_REPLAY',
    '| W229-face {RAM_FACE_229!r} | W230-face {RAM_FACE_230!r} | W231-face {RAM_FACE_231!r} | W232-face {RAM_FACE_232!r} | WIN_LABEL_REPLAY')
rep('| WIN_LABEL_229 {WIN_LABEL_229!r} | WIN_LABEL_230 {WIN_LABEL_230!r} | WIN_LABEL_231 {WIN_LABEL_231!r}")',
    '| WIN_LABEL_229 {WIN_LABEL_229!r} | WIN_LABEL_230 {WIN_LABEL_230!r} | WIN_LABEL_231 {WIN_LABEL_231!r} | WIN_LABEL_232 {WIN_LABEL_232!r}")')

# ---- SUB32 extract (append after SUB31 extract) ----
rep("""SUB31 = extract_lit(r"results\\_w231bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_230": WIN_LABEL_230, "WIN_LABEL": WIN_LABEL_231,
                          "RAM_FACE_230": RAM_FACE_230, "RAM_GB": RAM_FACE_231})""",
    """SUB31 = extract_lit(r"results\\_w231bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_230": WIN_LABEL_230, "WIN_LABEL": WIN_LABEL_231,
                          "RAM_FACE_230": RAM_FACE_230, "RAM_GB": RAM_FACE_231})
SUB32 = extract_lit(r"results\\_w232bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_231": WIN_LABEL_231, "WIN_LABEL": WIN_LABEL_232,
                          "RAM_FACE_231": RAM_FACE_231, "RAM_GB": RAM_FACE_232})""")

# ---- OLD32 lvl step (append after OLD31) ----
OLD31_LINE = '''OLD31 = lvl(OLD30, SUB31, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@L25@", "225"), ("@L26@", "226"), ("@L27@", "227"), ("@L28@", "228"), ("@L29@", "229"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25"), ("@T25@", "26"), ("@T26@", "27"), ("@T27@", "28"), ("@T28@", "29"), ("@T29@", "30")])'''
OLD32_LINE = OLD31_LINE + '''
OLD32 = lvl(OLD31, SUB32, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@L25@", "225"), ("@L26@", "226"), ("@L27@", "227"), ("@L28@", "228"), ("@L29@", "229"), ("@L30@", "230"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25"), ("@T25@", "26"), ("@T26@", "27"), ("@T27@", "28"), ("@T28@", "29"), ("@T29@", "30"), ("@T30@", "31")])'''
rep(OLD31_LINE, OLD32_LINE)

# ---- preflight pointer ----
rep("""# preflight: every replayed W231-face block sits exactly once in the blob
for i, old in enumerate(OLD31):
    c = t.count(old)
    assert c == 1, f"preflight block[{i}] count {c} != 1 in freeze-time W231 blob"
print("preflight OK: 46/46 replayed blocks sit count==1 in the freeze-time W231 blob")""",
    """# preflight: every replayed W232-face block sits exactly once in the blob
for i, old in enumerate(OLD32):
    c = t.count(old)
    assert c == 1, f"preflight block[{i}] count {c} != 1 in freeze-time W232 blob"
print("preflight OK: 46/46 replayed blocks sit count==1 in the freeze-time W232 blob")""")

# ---- anchors block ----
rep('rec = json.load(open(r"results\\_w232bmc_20261013_probe_receipt.json", encoding="utf-8"))',
    'rec = json.load(open(r"results\\_w233bmc_20261013_probe_receipt.json", encoding="utf-8"))')
rep('assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "525204_527203", "B": "527204_527403"}',
    'assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "527404_529403", "B": "529404_529603"}')
rep('''w231 = json.load(open(r"results\\perpetual_faces\\n1_w231_results.json", encoding="utf-8"))
led = w231["science_gates"]["ledger"]
assert led["total"] == 931989 and led["prev_total"] == 929789 and led["batch_trials"] == 2200
merged = w231["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 506120
w231only = w231["null_pool_cumulative"]["w231_only"]
A_p95 = w231["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w231["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == 0.0001 and kl["n_eff_held_equal"] == 929789
assert kl["line_pre_w231"] == 1.192 and kl["line_merged_506120"] == 1.1921
se_mu = w231["null_pool_cumulative"]["se_mu_at_k506120"]
assert se_mu == 0.000344''',
    '''w232 = json.load(open(r"results\\perpetual_faces\\n1_w232_results.json", encoding="utf-8"))
led = w232["science_gates"]["ledger"]
assert led["total"] == 934189 and led["prev_total"] == 931989 and led["batch_trials"] == 2200
merged = w232["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 508320
w232only = w232["null_pool_cumulative"]["w232_only"]
A_p95 = w232["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w232["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == 0.0001 and kl["n_eff_held_equal"] == 931989
assert kl["line_pre_w232"] == 1.1922 and kl["line_merged_508320"] == 1.1923
se_mu = w232["null_pool_cumulative"]["se_mu_at_k508320"]
assert se_mu == 0.000344''')
rep('''assert leg1["A"] == [525204, 527203] and leg1["B"] == [527204, 527403]
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [525004, 527003] and leg1["B_naive_first_clean"] == [525204, 525403]
assert leg4["W232p_A"] == "527204..529203" and leg4["W232p_B"] == "527404..527603"
assert leg4["W232p_B_lands_inside_W232p_A"] is True''',
    '''assert leg1["A"] == [527404, 529403] and leg1["B"] == [529404, 529603]
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [527204, 529203] and leg1["B_naive_first_clean"] == [527404, 527603]
assert leg4["W233p_A"] == "529404..531403" and leg4["W233p_B"] == "529604..529803"
assert leg4["W233p_B_lands_inside_W233p_A"] is True''')
rep('''assert leg0["rows"] == 229 and leg0["owner_rows"] == 221 and leg0["bmc_rows"] == 61 \\
       and leg0["bmc_ordinal"] == 62 and leg0["ordinal"] == 222
assert "attempt-continuity" in leg0["bmc_ordinal_note"] and "61st owned" in leg0["bmc_ordinal_note"]
fr = json.load(open(r"results\\_w231bmc_freeze_receipt.json", encoding="utf-8"))
assert fr["ordinal_faces"]["bmc_own_ordinal"] == 61  # "61st owned 承袭" prose anchor''',
    '''assert leg0["rows"] == 230 and leg0["owner_rows"] == 222 and leg0["bmc_rows"] == 62 \\
       and leg0["bmc_ordinal"] == 63 and leg0["ordinal"] == 223
assert "attempt-continuity" in leg0["bmc_ordinal_note"] and "62nd owned" in leg0["bmc_ordinal_note"]
fr = json.load(open(r"results\\_w232bmc_freeze_receipt.json", encoding="utf-8"))
assert fr["ordinal_faces"]["bmc_own_ordinal"] == 62  # "62nd owned 承袭" prose anchor''')
rep('''assert fmt8(merged["mu"]) == "\\u2212" + "0.09268999", fmt8(merged["mu"])
assert fmt8(w231only["mu"]) == "\\u2212" + "0.09203368", fmt8(w231only["mu"])
assert f"{merged['sigma']:.8f}" == "0.24507072", f"{merged['sigma']:.8f}"
assert f"{abs(w231only['mu'] - merged['mu']):.4f}" == "0.0007", f"{abs(w231only['mu'] - merged['mu']):.4f}"
assert f"{A_p95:.4f}" == "0.3251", f"{A_p95:.4f}"
assert f"{kl['line_merged_506120']:.4f}" == "1.1921"
assert f"{kl['line_delta_k_lift']:+.4f}" == "+0.0001"  # ASCII f-string face; prose token uses ASCII + sign (W231 face +0.0001)''',
    '''assert fmt8(merged["mu"]) == "\\u2212" + "0.09274288", fmt8(merged["mu"])
assert fmt8(w232only["mu"]) == "\\u2212" + "0.10490950", fmt8(w232only["mu"])
assert f"{merged['sigma']:.8f}" == "0.24508296", f"{merged['sigma']:.8f}"
assert f"{abs(w232only['mu'] - merged['mu']):.4f}" == "0.0122", f"{abs(w232only['mu'] - merged['mu']):.4f}"
assert f"{A_p95:.4f}" == "0.3063", f"{A_p95:.4f}"
assert f"{kl['line_merged_508320']:.4f}" == "1.1923"
assert f"{kl['line_delta_k_lift']:+.4f}" == "+0.0001"  # ASCII f-string face; prose token uses ASCII + sign (W232 face +0.0001)''')

# ---- freeze-window live label ----
rep("""# freeze-window label (live honesty): this derivation runs in r967, 2026-10-13""",
    """# freeze-window label (live honesty): this derivation runs in r972, 2026-10-13""")
rep('print(f"freeze-window label: r967 {WIN_LABEL}")',
    'print(f"freeze-window label: r972 {WIN_LABEL}")')

# ---- PAIRS build pointer ----
rep("""# ---------- build + apply W232 pairs ----------
PAIRS = []
for i, old in enumerate(OLD31):""",
    """# ---------- build + apply W233 pairs ----------
PAIRS = []
for i, old in enumerate(OLD32):""")

# ---- generic shift block ----
rep("""# ---- generic wave-token shifts (after targeted pairs) ----
# Pairs covered every W231 self face (each count==1 asserted). Remaining
# "W231" tokens = pair-written legit refs (chain W231 leg, refusing band,
# W231 finalize keys, W1..W231 scope) which must STAY W231 -- mask, then age
# one-wave-older W230 refs to W231, then restore. @L30@/@T30@ hold heritage
# tokens immune.
t = t.replace("n1_w231_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W231", "PERPETUAL-N1-W232")
t = t.replace("PERPETUAL_N1_W231", "PERPETUAL_N1_W232")
t = t.replace("n1_w231", "n1_w232")
t = t.replace("_w231bmc", "_w232bmc")
t = t.replace("W231", "@U_W@")
t = t.replace("W230", "W231")
t = t.replace("n1_w230", "n1_w231")
t = t.replace("PERPETUAL_N1_W230", "PERPETUAL_N1_W231")
t = t.replace("_w230bmc", "_w231bmc")
t = t.replace("@u_w@", "w231")
t = t.replace("@U_W@", "W231")
t = t.replace("@L30@", "230")
t = t.replace("@T30@", "31")""",
    """# ---- generic wave-token shifts (after targeted pairs) ----
# Pairs covered every W232 self face (each count==1 asserted). Remaining
# "W232" tokens = pair-written legit refs (chain W232 leg, refusing band,
# W232 finalize keys, W1..W232 scope) which must STAY W232 -- mask, then age
# one-wave-older W231 refs to W232, then restore. @L31@/@T31@ hold heritage
# tokens immune.
t = t.replace("n1_w232_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W232", "PERPETUAL-N1-W233")
t = t.replace("PERPETUAL_N1_W232", "PERPETUAL_N1_W233")
t = t.replace("n1_w232", "n1_w233")
t = t.replace("_w232bmc", "_w233bmc")
t = t.replace("W232", "@U_W@")
t = t.replace("W231", "W232")
t = t.replace("n1_w231", "n1_w232")
t = t.replace("PERPETUAL_N1_W231", "PERPETUAL_N1_W232")
t = t.replace("_w231bmc", "_w232bmc")
t = t.replace("@u_w@", "w232")
t = t.replace("@U_W@", "W232")
t = t.replace("@L31@", "231")
t = t.replace("@T31@", "32")""")

print("phase A OK: header/blobs/extracts/OLD32/anchors/shift advanced")
open(DST, "w", encoding="utf-8", newline="").write(t)
assert t.count("@@SUB_BLOCK@@") == 1, "SUB marker lost"
print("tpl written:", DST, "bytes:", len(t.encode("utf-8")))
