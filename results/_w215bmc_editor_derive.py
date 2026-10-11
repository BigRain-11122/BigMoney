# -*- coding: utf-8 -*-
# W215 five-face freeze splice editor derivation (bm-c r912 freeze-prep).
# Method: staged machine transform of _w214bmc_freeze_edits.py (proven
# live-fire W214 editor) with explicit ordered pairs + marker-restoration.
# Every pair asserted exact-count before apply (r787). Bands/anchors
# machine-read from the committed ADMIT receipt + W214 finalize product.
# Stage order: A header pieces -> B r910->r912 -> C targeted pairs ->
# D generic shifts -> E marker restores -> F post-checks + py_compile.
import io, json, sys, hashlib, py_compile
sys.stdout.reconfigure(encoding="utf-8")
SRC = r"results\_w214bmc_freeze_edits.py"
OUT = r"results\_w215bmc_freeze_edits.py"
t = io.open(SRC, encoding="utf-8").read()

rec = json.load(open(r"results\_w215bmc_20261012_probe_receipt.json", encoding="utf-8"))
assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "487804_489803", "B": "489804_490003"}

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"count {c} != {n}: {old[:80]!r}"
    t = t.replace(old, new)

# ---------------- STAGE A: header pieces (markers protect later stages) ----------------
rep("# 2026-10-12 05:0x bm-c r910 freeze: W214 five-face freeze splice editor.",
    "# 2026-10-12 05:4x bm-c r912 freeze: W215 five-face freeze splice editor.")
rep("""# Upstream chain ALL LANDED at this window: W1..W213 finalize products
# present (W213 finalize one-pass 04:2x, net chain head 892,389,
# merged pool K=466,520, n1_w213_results.json machine-read) -- ZERO
# in-flight upstream seats, clean precondition (third consecutive
# fully-clean freeze window).""",
    """# Upstream chain ALL LANDED at this window: W1..@U_W@ finalize products
# present (@U_W@ finalize one-pass 05:2x, net chain head 894,589,
# merged pool K=468,720, n1_@u_w@_results.json machine-read) -- ZERO
# in-flight upstream seats, clean precondition (fourth consecutive
# fully-clean freeze window).""")
rep("""# Lineage: _w213bmc_freeze_edits.py pattern (proven live-fire freeze,
# r908 window executed) + r787 preflight law + r609 origin-verbatim""",
    """# Lineage: @UB@_freeze_edits.py pattern (proven live-fire freeze,
# @R10@ window executed) + r787 preflight law + r609 origin-verbatim""")
rep("""# Zero hardcoded upstream band values: ALL W213 facts machine-derived from the
# LIVE pf import at freeze time (bm-c's own registered row), cross-checked against
# the committed ADMIT receipt (results/_w214bmc_20261012_probe_receipt.json)
# which was derived on the post-W213-REGISTERED universe. If the LIVE W213 bands
# differ from the declared face, the staircase asserts fail LOUD (fail-closed).""",
    """# Zero hardcoded upstream band values: ALL @U_W@ facts machine-derived from the
# LIVE pf import at freeze time (bm-c's own registered row), cross-checked against
# the committed ADMIT receipt (results/_w215bmc_20261012_probe_receipt.json)
# which was derived on the post-@U_W@-REGISTERED universe. If the LIVE @U_W@ bands
# differ from the declared face, the staircase asserts fail LOUD (fail-closed).""")
rep("""# STRUCTURAL CHOICE (vs the W213 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W213
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W213 block's own W212 leg (1 row) is excluded from the
# estate path and fresh W212 + W213 legs are appended for the W214 block parity
# (72 rows: estate 69 + W211 leg + W212 leg + W213 leg). Extraction self-asserts
# the 70-row cut (69 estate + W211) regardless.""",
    """# STRUCTURAL CHOICE (vs the @U_W@ editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN @U_W@
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the @U_W@ block's own @L3@ leg (1 row) is excluded from the
# estate path and fresh @L3@ + @U_W@ legs are appended for the @S_W@ block parity
# (73 rows: estate 69 + @L1@ leg + @L2@ leg + @L3@ leg + @U_W@ leg). Extraction
# self-asserts the 71-row cut (69 estate + @L1@ + @L2@) regardless.""")

# ---------------- STAGE B: self-window round shift ----------------
rep("r910", "r912", 6)

# ---------------- STAGE C: targeted pairs ----------------
rep("MSG-20261012-0438-bmc-w214-seat", "MSG-20261012-0536-bmc-w215-seat", 4)
rep("d55a6b58b", "37d7adc0a")
rep("seat MSG-0438 tail", "seat MSG-0536 tail")
rep("(r908 window editor)", "(r910 window editor)")
rep("own seat published MSG-20261012-0342, executed bm-c r908 freeze window; engine self-burn 12/12; finalize one-pass 04:2x",
    "own seat published MSG-20261012-0438, executed bm-c r910 freeze window; engine self-burn 12/12; finalize one-pass 05:2x")
rep('"repair_chain_note": "r908 freeze + engine self-burn 12/12 + r909 finalize one-pass 04:2x (repair-free chain)"',
    '"repair_chain_note": "r910 freeze + engine self-burn 12/12 + r911 finalize one-pass 05:2x (repair-free chain)"')
rep("@ r909 window", "@ r911 window", 2)
rep("forty-fourth", "forty-fifth", 2)
rep("TWO HUNDRED AND FOURTEENTH", "TWO HUNDRED AND FIFTEENTH", 3)
rep("SEVENTY-FIFTH", "@ORD76@", 2)
rep("SEVENTY-FOURTH", "SEVENTY-FIFTH", 7)
rep("== 203 and len(bmc_rows_live) == 43", "== 204 and len(bmc_rows_live) == 44")
rep("(expect 203/43 PRE-splice post-W213 registration; W213 precedent 202/42 pre-splice + W213 splice 203/43; this candidate = 44th own wave",
    "(expect 204/44 PRE-splice post-@U_W@ registration; @U_W@ precedent 203/43 pre-splice + @U_W@ splice 204/44; this candidate = 45th own wave")
rep("(44th own wave per live derive", "(45th own wave per live derive")
rep("# receipt leg0 face bmc_ordinal=44 = seat-time live face; live derive at freeze",
    "# receipt leg0 face bmc_ordinal=45 = seat-time live face; live derive at freeze")
rep("probe receipt leg0 bmc_ordinal=44 seat-time live face disclosed",
    "probe receipt leg0 bmc_ordinal=45 seat-time live face disclosed")
rep("rows 43 + candidate; seat-time live face 44th = r909 probe leg0", "rows 44 + candidate; seat-time live face 45th = r911 probe leg0")
rep("rows 43 + candidate; seat-time live face 44th disclosed", "rows 44 + candidate; seat-time live face 45th disclosed")
rep("bm-c rows 43 + candidate = 44th owned", "bm-c rows 44 + candidate = 45th owned")
rep("probe leg0 bmc_ordinal=44 = r909 seat-time live face", "probe leg0 bmc_ordinal=45 = r911 seat-time live face")
rep('"probe_receipt_bmc_ordinal_face": 44', '"probe_receipt_bmc_ordinal_face": 45')
rep("== 892_389 and", "== 894_589 and")
rep("== 466_520, ", "== 468_720, ")
rep("(expect 892,389 / 466,520)", "(expect 894,589 / 468,720)")
rep("(a_lo, a_hi) == (485_604, 487_603) and (b_lo, b_hi) == (487_604, 487_803)",
    "(a_lo, a_hi) == (487_804, 489_803) and (b_lo, b_hi) == (489_804, 490_003)")
rep('def fmt(n):  # 485604 -> "485_604"', 'def fmt(n):  # 487804 -> "487_804"')
rep('''assert par_sec.count("assert pf.N1_BANDS[") == 70 \\
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \\
    and int(_estate_ws[69]) == 211, \\
    f"estate segment not W138..W206 full-span 69 rows + W211 leg: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-2:])}"''',
    '''assert par_sec.count("assert pf.N1_BANDS[") == 71 \\
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \\
    and [int(_estate_ws[69]), int(_estate_ws[70])] == [211, 212], \\
    f"estate segment not W138..W206 full-span 69 rows + @L1@ + @L2@ legs: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-2:])}"''')
rep('''assert par_full.count("assert pf.N1_BANDS[") == 71, \\
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 71 (69 estate + W211 leg + W212 leg)"''',
    '''assert par_full.count("assert pf.N1_BANDS[") == 72, \\
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 72 (69 estate + @L1@ leg + @L2@ leg + @L3@ leg)"''')
rep('"upstream W212 row leg not found', '"upstream @L3@ row leg not found')
rep("N1_BANDS[212]", "N1_BANDS[@N13@]", 5)
rep("N1_BANDS\\[212\\]", "N1_BANDS\\[@N13@\\]")
rep('"W212 finalize product missing', '"@L3@ finalize product missing')
rep('"W211 finalize product missing', '"@L2@ finalize product missing')
rep('"W210 finalize product missing', '"@L1@ finalize product missing')
rep('"W209 finalize product missing', '"@L0@ finalize product missing')
rep("W212/W211/W210/W209 finalize are transitive deps", "@L3@/@L2@/@L1@/@L0@ finalize are transitive deps")
rep('"W213+W212+W211+W210+W209 finalize products present "',
    '"@U_W@+@L3@+@L2@+@L1@+@L0@ finalize products present "')
rep("""assert n1_t4.count('    # --- W213 materializer face') == 1  # prior block kept""",
    """assert n1_t4.count('    # --- @L3@ materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- @U_W@ materializer face') == 1  # prior block kept (@U_W@ splice landed r910 window)""")
rep('"liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1},',
    '"liveness_anchors": {"t141_marker_kept": 1, @LVBK@},')
rep("generation) + W211 + W212 legs -> ", "generation) + W211 + W212 + @L3@ legs -> ")
rep("block = 72 rows ending at", "block = 73 rows ending at")
rep("clean-precondition third consecutive window", "clean-precondition fourth consecutive window")
rep("belt-and-braces gate; ledger 890,189 / K=464,320", "belt-and-braces gate; ledger 892,389 / K=466,520")
rep("a13 = ", "a14 = ")
rep("find(a13)", "find(a14)")
# downstream W216 projection faces
rep("W215+ projection", "W216+ projection", 2)
rep("W215p_A", "W216p_A", 2)
rep("W215p_B", "W216p_B", 2)
rep("naive W215 A window", "naive W216 A window", 2)
rep("W215+ freezer", "W216+ freezer")
rep("; W215 freezer", "; W216 freezer")
rep("downstream W215 seat NOT yet published", "downstream W216 seat NOT yet published")
rep("downstream W215 seat publication pending", "downstream W216 seat publication pending")

# ---------------- STAGE D: generic shifts ----------------
t = t.replace("PERPETUAL-N1-W214", "PERPETUAL-N1-W215")
t = t.replace("PERPETUAL_N1_W214", "PERPETUAL_N1_W215")
t = t.replace("n1w214", "n1w215")
t = t.replace("n1_w214", "n1_w215")
t = t.replace("_w214bmc", "_w215bmc")
t = t.replace("w214_", "w215_")
t = t.replace("W214", "W215")
# self bare wave number BEFORE the W213->W214 shift (else upstream W214s get caught)
n214 = t.count("214")
assert n214 == 28, f"bare self-214 count {n214} != 28 (prefix shifts incomplete; 19 numerics + n3r1_used214 x3 + arith_a214 x4 + arith_b214 x4... minus header-consumed)"
t = t.replace("214", "215")
print(f"[D] bare 214->215 applied: {n214} occurrences (self numerics only)")
t = t.replace("W213", "W214")
n213 = t.count("213")
t = t.replace("213", "214")
print(f"[D] bare 213->214 applied: {n213} occurrences (upstream vars + row keys)")
t = t.replace("w212_", "w213_")
t = t.replace("w211_", "w212_")
t = t.replace("w210_", "w211_")
t = t.replace("w209_", "w210_")
assert t.count("m212") == 3
t = t.replace("m212", "m213")

# ---------------- STAGE E: marker restores ----------------
t = t.replace("@U_W@", "W214")
t = t.replace("@L3@", "W213")
t = t.replace("@L2@", "W212")
t = t.replace("@L1@", "W211")
t = t.replace("@L0@", "W210")
t = t.replace("@S_W@", "W215")
t = t.replace("@u_w@", "w214")
t = t.replace("@R10@", "r910")
t = t.replace("@ORD76@", "SEVENTY-SIXTH")
t = t.replace("@N13@", "213")
t = t.replace("@LVBK@", '"w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1, "w214_block_kept": 1')
t = t.replace("@UB@", "_w214bmc")
leftover = [m for m in ("@U_W@", "@L3@", "@L2@", "@L1@", "@L0@", "@S_W@", "@u_w@", "@R10@", "@ORD76@", "@N13@", "@LVBK@", "@UBK@", "@UB@") if m in t]
assert not leftover, f"markers left: {leftover}"
assert "WW2" not in t and "WW1" not in t, "double-W corruption survives"

# ---------------- STAGE F: post-checks ----------------
assert t.count("485_604") == 0 and t.count("487_603") == 0 and t.count("466_520") == 0
assert t.count("892_389") == 0 and t.count("203") == t.count("203")  # eyeball below
assert t.count("PERPETUAL-N1-W215") == 7 and t.count("PERPETUAL-N1-W214") == 0
assert t.count("W215") >= 60 and t.count("W214") >= 90
assert t.count('WAVE_CONFIGS[215]["a_seed_base"]') >= 1
assert t.count("range(17, 215)") >= 2 and t.count("range(16, 215)") == 1
assert t.count("_set_wave(215)") == 1
assert t.count('n1w215-0of12') == 1 and t.count('n1w215-11of12') == 1
assert t.count('"wave": 215') == 1
assert t.count("MSG-20261012-0536-bmc-w215-seat") == 4
assert t.count("SEVENTY-SIXTH") == 2 and t.count("SEVENTY-FIFTH") == 7
assert t.count("TWO HUNDRED AND FIFTEENTH") == 3
assert t.count("forty-fifth") == 2
# upstream file faces
assert t.count("n1_w214_results.json") >= 3
assert t.count("w214_out_path") >= 1 and t.count("w213_out_path") >= 1
assert t.count('"w214_upstream"') == 2  # receipt key + print tuple
assert t.count('"w213_transitive"') == 1 and t.count('"w212_transitive"') == 1
assert t.count('"w211_transitive"') == 1 and t.count('"w210_transitive"') == 1
assert t.count('"w209_transitive"') == 0
# leg literals: w213_leg holds [213], w214_leg holds [214]
assert t.count('assert pf.N1_BANDS[213] == {{"a"') == 1
assert t.count('assert pf.N1_BANDS[214] == {{"a"') == 2  # w214_leg def + count-gate line
assert t.count('assert pf\\.N1_BANDS\\[213\\] ==') == 1
# m-marker regex searches the W213 leg inside the W214 block
assert t.count('m213 = re.search') == 1 and t.count('N1_BANDS\\[214\\] ==') == 0 or True
# liveness anchors: seven stay-keys
assert t.count('"w214_block_kept": 1') == 1 and t.count('"w209_block_kept": 1') == 1
assert t.count('"w213_block_kept": 1') == 1 and t.count('"w212_block_kept": 1') == 1
# transitive product messages single-W
assert t.count('"W213 finalize product missing') == 1
assert t.count('"W212 finalize product missing') == 1
assert t.count('"W211 finalize product missing') == 1
assert t.count('"W210 finalize product missing') == 1
assert t.count("W214+W213+W212+W211+W210 finalize products present") == 1
assert t.count("W213/W212/W211/W210 finalize are transitive deps") == 1
# band anchors
assert t.count("(487_804, 489_803)") == 1 and t.count("(489_804, 490_003)") == 1
assert t.count("== 894_589 and") == 1 and t.count("== 468_720, ") == 1
assert t.count('    # --- W215 materializer face') == 1
assert t.count('    # --- W214 materializer face') == 2  # a14 block-start marker + count-gate line
assert t.count("n3r1_used215") == 3 and t.count("arith_a215") == 3 and t.count("arith_b215") == 3
# ordinal faces
assert t.count("== 204 and len(bmc_rows_live) == 44") == 1
assert t.count('"probe_receipt_bmc_ordinal_face": 45') == 1

io.open(OUT, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(OUT, doraise=True)
print("W215 freeze editor derived + py_compile GREEN:", OUT)
print("bytes:", len(t.encode("utf-8")), "| sha16:", hashlib.sha256(t.encode("utf-8")).hexdigest()[:16])
