# -*- coding: utf-8 -*-
# 2026-10-14 13:5x bm-c r996-continuation freeze window (upstream W1..W238 ALL
# LANDED, clean precondition): W239 five-face freeze splice editor -- bm-c
# OWN-SEAT face (seat MSG-20261014-0914-bmc-w239-seat published=reserved by
# bm-c itself @ origin 603ff65d9 r991, pre-seat probe ADMIT receipt
# _w239bmc_20261014_probe_receipt.json same payload; per-wave prereg
# PERPETUAL_N1_W239_PREREG.md derived+landed by the dead r996 session commit
# 97a7ff0e6 [estate absorbed by THIS r996-continuation window per the bm-c
# absorb precedent lineage, 24th generation], zero takeover, zero DRAFT
# marker). Upstream chain ALL LANDED at this window: W1..W238 finalize
# products present (W238 bm-a own-wave closeout r985: five-face splice
# 50fa77623 + engine self-burn 12/12 + finalize one-pass; net chain head
# 947,935, merged pool K=521,520, n1_w238_results.json machine-read) -- ZERO
# in-flight upstream seats, clean precondition (twenty-eighth consecutive
# fully-clean freeze window). Upstream six-gate disclosure: the W238 cycle ran
# its PRE-FINALIZE correctly (standing law since the W217 debt); THIS W239
# cycle runs PRE-FINALIZE likewise (standing law).
# Lineage: _w238bma_freeze_edits.py template (proven live-fire freeze,
# committed by the bm-a r984/r985 window; engine self-burn + finalize
# verified r985) + r787 preflight law + r609 origin-verbatim base + r761
# programmatic quote wrapping + r909 physical-byte anchors + r838 per-file
# EOL detection + family #6 LHS/RHS/comment ATOMIC TRIPLE (the new block's
# w<239>/range(16,239)/range(17,239)/below-239 quadruple is count-asserted
# atomically; the W238 block's own w<238 face is legitimate prior-wave
# boundary, not stale) + E63 heal (arith_a239/arith_b239 define+assert
# consistent -- the W238 template's one-behind assert drift NOT carried).
# Zero hardcoded upstream band values: ALL W238 facts machine-derived from the
# LIVE pf import at freeze time (the registered W238 row -- bm-a seat honored),
# cross-checked against the committed ADMIT receipt
# (results/_w239bmc_20261014_probe_receipt.json) which was derived on the
# post-W238-DECLARED universe. If the LIVE W238 bands differ from the declared
# face, the staircase asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W238 editor): the parity estate (W138..W206
# full-span 69 rows, r858 absorb generation, + W211..W231 legs) is extracted
# from the OWN W238 block physical bytes -- structure known exactly (bm-a's
# own splice generation, committed) -- the W238 block's own W232 + W233 + W234
# + W235 + W236 + W237 legs are excluded from the estate path and fresh W232 +
# W233 + W234 + W235 + W236 + W237 + W238 legs are appended for the W239 block
# parity (97 rows: estate 90 ending W231 + W232 leg + W233 leg + W234 leg +
# W235 leg + W236 leg + W237 leg + W238 leg). Extraction self-asserts the
# 90-row cut regardless.
# Disclosed: (a) the inherited W213 leg inside the estate carries a cosmetic
# error-string face ("registered W212 row parity drift") from the r912 editor
# generation -- physical bytes preserved verbatim per extraction law, zero
# functional impact (assert target [213] is correct); (b) the W238 block's
# band-set variable naming one-behind face (w237_a holds wave-238 bands) is
# the lineage's mechanical aging face -- the W239 block follows the same
# mechanical pattern (w238_a holds wave-239 bands), zero functional impact;
# (c) the W238 template's tail comment "post-W236 universe re-derive" stale
# face and family-6 comment one-behind face are corrected in this generation.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w239bmc_20261014_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w239bmc_freeze_receipt.json")
SEAT_MSG = "MSG-20261014-0914-bmc-w239-seat.md"
SEAT_ORIGIN = "603ff65d9"
PY = sys.executable

def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True)

# ---------- gate 0: fresh origin, working == origin (r609 law) ----------
git("fetch", "origin")
r = git("rev-parse", "HEAD"); head = r.stdout.decode().strip()
ro = git("rev-parse", "origin/main"); omain = ro.stdout.decode().strip()
anc = git("merge-base", "--is-ancestor", "origin/main", "HEAD")
assert anc.returncode == 0, f"origin/main {omain} not contained in HEAD {head} -- rebase first (r609)"
for path in ("scripts/perpetual_faces.py", "scripts/perpetual_faces_n1.py"):
    b = git("show", f"origin/main:{path}")
    w = open(os.path.join(REPO, path), "rb").read()
    assert b.stdout.replace(b"\r\n", b"\n") == w.replace(b"\r\n", b"\n"), \
        f"working {path} != origin blob (content, EOL-normalized) -- stale base (r609 abort)"

sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "research"))
import perpetual_faces as pf_mod

# ---------- gate 0.5: W238 five-face landed + W238 finalize product present ----------
# (chain-order precondition; W237/W236/W235/W234/W233/W232/W231/W230 finalize are
# transitive deps of the W238 freeze and are belt-and-braces checked here + enforced
# by the block's cumulative-deps assert range(17, 239) at selftest time)
W238 = dict(pf_mod.N1_BANDS.get(238) or {})
assert W238.get("engine_owner") == "bm-a", \
    f"W238 row not landed as declared (bm-a seat owner expected): {W238} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w238_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w238_results.json")
assert os.path.exists(w238_out_path), "W238 finalize product missing (n1_w238_results.json) -- chain dep not met"
w237_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w237_results.json")
assert os.path.exists(w237_out_path), "W237 finalize product missing (transitive chain dep) -- abort"
w236_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w236_results.json")
assert os.path.exists(w236_out_path), "W236 finalize product missing (transitive chain dep) -- abort"
w235_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w235_results.json")
assert os.path.exists(w235_out_path), "W235 finalize product missing (transitive chain dep) -- abort"
w234_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w234_results.json")
assert os.path.exists(w234_out_path), "W234 finalize product missing (transitive chain dep) -- abort"
w233_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w233_results.json")
assert os.path.exists(w233_out_path), "W233 finalize product missing (transitive chain dep) -- abort"
w232_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w232_results.json")
assert os.path.exists(w232_out_path), "W232 finalize product missing (transitive chain dep) -- abort"
w231_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w231_results.json")
assert os.path.exists(w231_out_path), "W231 finalize product missing (transitive chain dep) -- abort"
w230_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w230_results.json")
assert os.path.exists(w230_out_path), "W230 finalize product missing (transitive chain dep) -- abort"
w238_out = json.load(open(w238_out_path, encoding="utf-8"))
w238_led = (w238_out.get("science_gates") or {}).get("ledger") or {}
w238_total = w238_led.get("total")
w238_merged_n = None
try:
    w238_merged_n = w238_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w238_total == 947_935 and w238_merged_n == 521_520, \
    f"W238 finalize anchors drift at freeze time: total={w238_total} merged={w238_merged_n} (expect 947,935 / 521,520)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '238: {"a"', "--", "scripts/perpetual_faces.py")
w238_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W238_PREREG.md")
w238_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W239_PREREG.md")
w239_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W239_PREREG.md")), \
    "W239 per-wave prereg missing on disk -- chain face incomplete, abort (r996 dead-session derive landed pre-freeze expected)"
with open(os.path.join(REPO, "research", "PERPETUAL_N1_W239_PREREG.md"), encoding="utf-8") as _fh:
    _pre_head = _fh.read(2000)
assert "DRAFT-NOT-FROZEN" not in _pre_head, "W239 prereg still DRAFT -- abort (freeze commit pending face)"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face owner_rows=227 / bmc_rows=65 / ordinal=229 / bmc_ordinal=66
# = seat-time PRE-W238-splice live faces; live derive at freeze time:
# W238 splice LANDED -> owner rows 228 + candidate = 229th EXACT; bm-c rows 65 +
# candidate = 66th EXACT -- bm-c own-seat continuity face, zero takeover)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 228 and len(bmc_rows_live) == 65, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bmc={len(bmc_rows_live)} (expect 228/65 PRE-splice post-W238 registration; this candidate = bm-c's 66th own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W238 landed (freeze {w238_freeze_sha[:10]}, owner=bm-a seat honored, zero takeover face), "
      f"W238+W237+W236+W235+W234+W233+W232+W231+W230 finalize products present "
      f"(W238 ledger head {w238_total}, merged n={w238_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-c rows {len(bmc_rows_live)} + candidate (66th own wave per live derive; "
      f"probe receipt leg0 owner_rows=227 / bmc_ordinal=66 = seat-time pre-splice faces disclosed honest)")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
A = rec["bands"]["A"]; B = rec["bands"]["B"]
# W239 probe receipt bands carry int-list faces + explicit lo/hi keys
if isinstance(A, str):
    a_lo, a_hi = (int(x) for x in A.split("_"))
    b_lo, b_hi = (int(x) for x in B.split("_"))
else:
    a_lo, a_hi = int(A[0]), int(A[1])
    b_lo, b_hi = int(B[0]), int(B[1])
    a_lo = rec["bands"].get("a_lo", a_lo); a_hi = rec["bands"].get("a_hi", a_hi)
    b_lo = rec["bands"].get("b_lo", b_lo); b_hi = rec["bands"].get("b_hi", b_hi)
leg1 = rec["legs"]["leg1"]
assert [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"], "receipt band mismatch"
assert (a_lo, a_hi) == (542_501, 544_500) and (b_lo, b_hi) == (540_604, 540_803), \
    f"W239 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w238_b_tail = W238["b_exit"][1]      # registered W238 row b_exit hi (pf import, live)
w238_a_tail = W238["a"][1]            # registered W238 row A hi (pf import, live)
# W239 NEW FACE (seed-hop decoupled, probe receipt leg1 relation_asserts):
# B keeps the staircase base (prior-wave B tail+1 EXACT); A seed-hops past
# live SEED_REGISTRY points far above it (first live-seed refusal above the
# registered tail) -- A base >= prior-B tail+1 with a live-seed gap, NOT the
# equality face; machine-derived from the LIVE registered row, never transcribed.
assert w238_b_tail + 1 == b_lo, "B staircase base relation broken (B == prior-wave B tail+1 EXACT)"
assert a_lo > w238_b_tail + 1, "A seed-hop face violated: A base must sit ABOVE prior-B tail+1 (live-seed gap)"
assert b_hi < a_lo, "seed-decoupled A/B gap face violated: B window must sit entirely below own-A"
assert leg1.get("hops_A") == 2 and leg1.get("hops_B") == 0, "hop-count drift vs probe receipt leg1"
assert w238_a_tail + 1 == W238["b_exit"][0], "W238 A-tail+1 != W238 B-base (registered row in-wave relation)"
assert [w238_a_tail + 1, w238_a_tail + 2_000] == leg1["ARITH_A"], \
    f"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w238_a_tail + 1, w238_a_tail + 2_000]} != {leg1['ARITH_A']}"
assert [w238_b_tail + 1, w238_b_tail + 200] == leg1["ARITH_B"], \
    f"B-continuation drift vs probe receipt leg1 ARITH_B: {[w238_b_tail + 1, w238_b_tail + 200]} != {leg1['ARITH_B']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w239bmc_20261014_probe_receipt.json")
w239_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W239 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W239_PREREG.md"],
                   cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                   errors="replace")
assert g.returncode == 0, f"banned gate FAIL: {g.stdout} {g.stderr}"
gate_lines = []
for base, span in ((a_lo, 2_000), (b_lo, 200)):
    g2 = subprocess.run([PY, os.path.join(REPO, "Tools", "seed_admit_gate.py"),
                         str(base), "--span", str(span)],
                        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                        errors="replace")
    assert g2.returncode == 0, f"seed_admit_gate FAIL base={base}: {g2.stdout} {g2.stderr}"
    gate_lines.append(g2.stdout.strip().splitlines()[-1] if g2.stdout.strip()
                      else f"rc0 base={base} span={span}")
print("gates OK:", " | ".join(gate_lines))

# ---------- read files, EOL (r838 law: runtime per-file detection) ----------
pf_b = open(PF, "rb").read(); pf_t = pf_b.decode("utf-8")
n1_b = open(N1, "rb").read(); n1_t = n1_b.decode("utf-8")

def detect_eol(t):
    """r838 law: per-file runtime EOL detection, never assume a single convention."""
    crlf = t.count("\r\n")
    lf = t.count("\n") - crlf
    return "\r\n" if crlf > lf else "\n"

EOL = detect_eol(n1_t); PF_EOL = detect_eol(pf_t)
assert pf_t.count(PF_EOL) > 0 and n1_t.count(EOL) > 0, \
    f"EOL detection degenerate: pf={PF_EOL!r} n1={EOL!r}"

def must(t, s, n, what):
    c = t.count(s)
    assert c == n, f"anchor {what}: count {c} != {n}"
    return s

def fmt(n):  # 501004 -> "501_004"
    return f"{n // 1000}_{n % 1000:03d}"

# ---------- extract parity section (physical bytes, never re-typed) ----------
# STRUCTURAL CHOICE: extract the estate from the OWN W238 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W231
# leg = 90 rows) -- the W238 block is bm-a's own splice generation
# (r984/r985 window editor), structure known. The W238 block span ends
# where the T-141 s2 lane face marker begins.
a18 = '    # --- W238 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w238_start = n1_t.find(a18); t141_pos = n1_t.find(a_t141)
assert w238_start > 0 and t141_pos > w238_start, \
    "W238 materializer block face not found (W238 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w238_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W238 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m232 = re.search(r" *assert pf\.N1_BANDS\[232\] ==", par_full)
assert m232, "upstream W232 row leg not found inside W238 parity span"
par_sec = par_full[:m232.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 90 \
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \
    and [int(_estate_ws[69 + i]) for i in range(11)] == [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221] \
    and [int(_estate_ws[80 + i]) for i in range(9)] == [222, 223, 224, 225, 226, 227, 228, 229, 230] \
    and int(_estate_ws[89]) == 231, \
    f"estate segment not W138..W206 full-span 69 rows + W211..W230 legs + W231 leg: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"
assert par_full.count("assert pf.N1_BANDS[") == 96, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 96 (69 estate + W211..W230 legs + W231 leg + W232 leg + W233 leg + W234 leg + W235 leg + W236 leg + W237 leg)"

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '238: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W238_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
# MEM_I derived INSIDE the W238 cfg entry span (own splice generation, value
# format known: plain int -- indent is all we take)
_c238 = n1_t.find('238: {"batch"')
assert _c238 > 0, "W238 cfg entry not found (W238 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c238)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c238) > _mpos, "W238 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W238["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W238["a"][0]), _c238) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W238["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '238: {"a"', PF_EOL)

# ---------- W238 row owner line (physical bytes; comment text is own generation) ----------
w238_row_start = pf_t.find('    238: {"a"')
assert w238_row_start > 0, "W238 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w238_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w238_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-a"' in w238_own_line, \
    f"W238 owner line unexpected bytes: {w238_own_line!r}"
ROWC_I = w238_own_line[:len(w238_own_line) - len(w238_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W239 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat",
"    # MSG-20261014-0914-bmc-w239-seat published=reserved by bm-c itself @",
"    # origin " + SEAT_ORIGIN + " (r991, zero takeover); prereg + ADMIT probe",
"    # receipt frozen commit " + w239_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W239_PREREG.md",
"    # r996 dead-session derive landed pre-freeze [estate absorbed by the",
"    # r996-continuation window], probe",
"    # results/_w239bmc_20261014_probe_receipt.json @ " + w239_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-a W238 five-face (freeze " + w238_freeze_sha[:10] + ") + W238",
"    # finalize product landed (n1_w238_results.json present, ledger",
"    # head " + str(w238_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W239 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w239bmc_20261014_probe_receipt.json: A = FIRST-CLEAN",
"    # past the prior-wave B tail AND live SEED_REGISTRY points -- NEW FACE",
"    # (arithmetic continuation " + fmt(w238_a_tail + 1) + ".." + fmt(w238_a_tail + 2_000) + " REFUSED at its",
"    # own start by the W238 B band " + fmt(W238["b_exit"][0]) + ".." + fmt(w238_b_tail) + " AND live",
"    # seeds 541_500/542_000, exactly as the W238 seat leg4 projection",
"    # anticipated); honest forward walk hop 1 -> 542_001 (window 542_001..544_000",
"    # REFUSED at 542_500), hop 2 -> first-clean " + fmt(a_lo) + ".." + fmt(a_hi) + ", hops=2,",
"    # non-rotational r587 forward-monotone walk; A base >= prior-wave B",
"    # tail+1 (" + fmt(w238_b_tail) + "+1) machine-checkable -- A-hops-prior-B",
"    # staircase GE face (E36 card, probe receipt leg1 A_semantics",
"    # machine-read, never transcribed);",
"    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail",
"    # (" + fmt(w238_b_tail + 1) + ".." + fmt(w238_b_tail + 200) + " CLEAN on the",
"    # registered universe, hops=0, NO own-A reservation jump needed -- own-A",
"    # seed-hopped FAR past the staircase base: first seed-decoupled A/B gap",
"    # face; B base == prior-wave B tail+1 (" + fmt(w238_b_tail) + "+1) machine-checkable;",
"    # B window sits entirely below the own-A window " + fmt(a_lo) + ".." + fmt(a_hi) + ");",
"    # single-window derive (r812 merged the gate legs INTO the",
"    # pre-seat probe; dual-window parity N/A honest); scan face =",
"    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1",
"    # used-seed band + probe cluster 95_000..95_003 + cross-face",
"    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/",
"    # N2-W15 probe points.",
"    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):",
"    # " + gate_lines[0] + ";",
"    # " + gate_lines[1] + ".",
"    # W240+ projection (gate-derived pre-seat probe leg4, pre-W239",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W240p_A_naive"] + " REFUSED by live",
"    # SEED_REGISTRY points " + str(rec["legs"]["leg4"]["W240p_A_naive_refusers_seeds"]) + " -> honest walk first-clean",
"    # " + rec["legs"]["leg4"]["W240p_A_first_clean"] + " hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " /",
"    # B naive first-clean " + rec["legs"]["leg4"]["W240p_B_naive"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " -- B lands OUTSIDE",
"    # the naive A window (seed-gap face: W239 A/B decoupled); W240 freezer",
"    # MUST re-derive on the post-W239 universe AND re-read the live trace",
"    # (do NOT assume the staircase A-base==prior-B-tail+1 equality -- the",
"    # W240 seat is ALREADY published by bm-a @ origin 39a30b6a0, queue-depth",
"    # supply, its freeze waits-upstream on THIS W239 finalize); never transcribe r587.",
])
pf_row = (f'{ROW_I}239: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'239: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w238_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w238_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W238 finalize ALL LANDED (W238 finalize product present at splice, "
            f"net chain head {w238_total} machine-read, merged pool K={w238_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition; "
            f"downstream W240 seat ALREADY published by bm-a @ origin 39a30b6a0 (r986, "
            f"queue-depth supply depth-3 face, seat-first law held -- W240 freeze waits-upstream "
            f"on THIS W239 finalize)")
cfg_lines = [
 f'{CFG_I}239: {{"batch": "PERPETUAL-N1-W239",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W239_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND THIRTY-NINTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W238 row five-face freeze (bm-a own seat executed at the r984/r985 window; engine self-burn 12/12; finalize one-pass r985, ledger 945,735+2,200=947,935 / K=521,520 machine-read), ",
 f"{w238_freeze_sha[:10]} (prereg {w238_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W238 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261014-0914-bmc-w239-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg ",
 "r996 dead-session derive landed pre-freeze [estate absorbed by the r996-continuation window] -- zero takeover face, bm-c own-seat ",
 "continuity, ",
 f"prereg {w239_prereg_sha[:10]} @ receipt {w239_receipt_sha[:10]}) -- this freeze splice editor derived from the committed W238 editor template in this same freeze window; ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W238 five-face + W238 finalize product landed ",
 "(executed in the bm-c loop freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c (bm-c OWN-SEAT face -- bm-c's SIXTY-SIXTH ",
 "owned claim per machine-derive (engine_owner==bm-c rows ",
 f"{len(bmc_rows_live)} + candidate; probe receipt leg0 owner_rows=227 / bmc_ordinal=66 = seat-time pre-splice ",
 "live faces disclosed honest, live derive governs ",
 "r587/r359 -- zero takeover, own-seat continuity)), ",
 "wave 239: ",
 "A = FIRST-CLEAN past the prior-wave B tail AND live SEED_REGISTRY ",
 "points (the arithmetic continuation ",
 f"{fmt(w238_a_tail + 1)}..{fmt(w238_a_tail + 2_000)} is REFUSED at its own start by the ",
 f"W238 B band {fmt(W238['b_exit'][0])}..{fmt(w238_b_tail)} AND live seeds 541_500/542_000 ",
 "-- NEW FACE, first live-seed refusal above the registered tail, exactly as ",
 "the W238 seat leg4 succession ",
 "projection notes anticipated; honest forward walk hop 1 -> 542_001, hop 2 -> ",
 f"{fmt(a_lo)}..{fmt(a_hi)} hops=2; A base >= prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase GE face, E36 card (probe ",
 "receipt leg1 machine-read relation_asserts); ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN arithmetic ",
 "continuation of the prior-wave B tail (the continuation ",
 f"{fmt(w238_b_tail + 1)}..{fmt(w238_b_tail + 200)} is CLEAN on the registered universe ",
 "hops=0, NO own-A reservation jump needed -- own-A seed-hopped FAR past the ",
 f"staircase base, first seed-decoupled A/B gap face; B base == prior-wave B ",
 "tail+1 machine-checkable; B window sits entirely below the own-A window ",
 f"{fmt(a_lo)}..{fmt(a_hi)}; cross-window convergence with the W238 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W238 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",
 "results/_w239bmc_20261014_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W240+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W240p_A_naive']} REFUSED by live SEED_REGISTRY points ",
 f"{rec['legs']['leg4']['W240p_A_naive_refusers_seeds']} -> honest walk first-clean ",
 f"{rec['legs']['leg4']['W240p_A_first_clean']} CLEAN; B naive first-clean ",
 f"{rec['legs']['leg4']['W240p_B_naive']} CLEAN -- B lands OUTSIDE the naive A window (seed-gap face: ",
 "W239 A/B decoupled); W240 freezer MUST re-derive on the post-W239 universe AND ",
 "re-read the live trace (do NOT assume the staircase A-base==prior-B-tail+1 ",
 "equality; W240 seat ALREADY published by bm-a @ 39a30b6a0, freeze waits-upstream) -- ",
 "the finalize ",
 "merge loop still derives the wave set from registry keys at ",
 "run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W239 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past prior-wave B tail AND live seeds; arithmetic {fmt(w238_a_tail + 1)}..{fmt(w238_a_tail + 2_000)} REFUSED at own start by the W238 B band {fmt(W238["b_exit"][0])}..{fmt(w238_b_tail)} + live seeds 541_500/542_000; hops=2; A-hops-prior-B staircase GE face, E36 card; relation machine-read per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W239 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN arithmetic continuation of the prior-wave B tail; {fmt(w238_b_tail + 1)}..{fmt(w238_b_tail + 200)} CLEAN hops=0, no own-A reservation jump needed; first seed-decoupled A/B gap face; B base == prior-B tail+1; B window entirely below own-A)',
 f'{MEM_I}"shard_subdir": "n1_w239", "out_name": "n1_w239_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]

cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('239: {"batch": "PERPETUAL-N1-W239"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W239 materializer face (bm-c loop five-face freeze splice --",
 "    #     OWN-SEAT face under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's sixty-sixth owned per machine-derive (engine_owner==bm-c",
 f"    #     rows {len(bmc_rows_live)} + candidate; own-seat face: seat published=reserved by bm-c itself",
 "    #     (r991 MSG-20261014-0914-bmc-w239-seat @ origin 603ff65d9; probe leg0",
 "    #     owner_rows=227 / bmc_ordinal=66 = seat-time pre-splice faces;",
 "    #     live derive at freeze governs);",
 "    #     wave 239 = first free number after the",
 "    #     REGISTERED W238 row (five-face freeze " + w238_freeze_sha[:10] + "; bm-a own seat executed at",
 "    #     the r984/r985 window; engine",
 "    #     self-burn 12/12 + finalize one-pass r985",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held) honest note)",
 "    #     -- SINGLE STATE zero seat gap (W2..W238 all registered). Seat",
 "    #     published=reserved MSG-20261014-0914-bmc-w239-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg",
 f"    #     r996 dead-session derive landed pre-freeze commit {w239_prereg_sha[:10]} [estate absorbed by the",
 "    #     r996-continuation window]; this freeze splice editor",
 "    #     derived from the committed W238 editor template in this same freeze",
 "    #     window (E63 heal: arith_a239/arith_b239 define+assert consistent);",
 "    #     deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W238 five-face + W238 finalize",
 "    #     product landed; zero --no-verify; the W239 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND THIRTY-NINTH engine wave BY",
 f"    #     MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w239bmc_20261014_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W239 bands were never assigned).",
 "    _set_wave(239)",
 "    try:",
 '        assert WAVE_CONFIGS[238]["a_seed_base"] == pf.N1_BANDS[238]["a"][0], \\',
 '            "W239 upstream W238 mirror drift (a)"',
 "        assert WAVE_CONFIGS[238][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[238]["b_exit"][0], "W239 upstream W238 mirror drift (b)"',
 "        assert WAVE_CONFIGS[238].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[238].get("engine_owner") == "bm-a", \\',
 '            "W239 upstream W238 engine_owner mirror drift (law-mirror parity; bm-a upstream seat face)"',
 "        w238_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w238_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w238_a & w238_b), "W239 A/B band overlap"',
 "        assert not (w238_a & reg_ints) and not (w238_b & reg_ints), \\",
 '            "W239 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w238_a), ("B", w238_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W239 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W239 {nm} hits W1"',
 '            assert not (band & probes), f"W239 {nm} hits probe seeds"',
]

w232_leg = [
 f'        assert pf.N1_BANDS[232] == {{"a": ({fmt(pf_mod.N1_BANDS[232]["a"][0])}, {fmt(pf_mod.N1_BANDS[232]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[232]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[232]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W232 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w233_leg = [
 f'        assert pf.N1_BANDS[233] == {{"a": ({fmt(pf_mod.N1_BANDS[233]["a"][0])}, {fmt(pf_mod.N1_BANDS[233]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[233]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[233]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W233 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w234_leg = [
 f'        assert pf.N1_BANDS[234] == {{"a": ({fmt(pf_mod.N1_BANDS[234]["a"][0])}, {fmt(pf_mod.N1_BANDS[234]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[234]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[234]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W234 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w235_leg = [
 f'        assert pf.N1_BANDS[235] == {{"a": ({fmt(pf_mod.N1_BANDS[235]["a"][0])}, {fmt(pf_mod.N1_BANDS[235]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[235]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[235]["b_exit"][1])}),',
'                                    "engine_owner": "bm-a"}, \\',
'            "registered W235 row parity drift (r307; bm-a five-face freeze; takeover-window splice face disclosed)"',
]
w236_leg = [
 f'        assert pf.N1_BANDS[236] == {{"a": ({fmt(pf_mod.N1_BANDS[236]["a"][0])}, {fmt(pf_mod.N1_BANDS[236]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[236]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[236]["b_exit"][1])}),',
'                                    "engine_owner": "bm-a"}, \\',
'            "registered W236 row parity drift (r307; bm-a five-face freeze; own-seat face disclosed)"',
]
w237_leg = [
 f'        assert pf.N1_BANDS[237] == {{"a": ({fmt(pf_mod.N1_BANDS[237]["a"][0])}, {fmt(pf_mod.N1_BANDS[237]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[237]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[237]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W237 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w238_leg = [
 f'        assert pf.N1_BANDS[238] == {{"a": ({fmt(pf_mod.N1_BANDS[238]["a"][0])}, {fmt(pf_mod.N1_BANDS[238]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[238]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[238]["b_exit"][1])}),',
'                                    "engine_owner": "bm-a"}, \\',
'            "registered W238 row parity drift (r307; bm-a five-face freeze; own-seat face disclosed)"',
]
tail = [
 "        # prior-wave disjointness W2..W238 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 239):",
 '            assert not (w238_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W239 A hits W{wprev}\"",
 '            assert not (w238_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W239 B hits W{wprev}\"",
 "        n3r1_used239 = set(range(70_000, 70_006))",
 "        assert not (w238_a & n3r1_used239) and not (w238_b & n3r1_used239), \\",
 '            "W239 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w238_a & lfc_actual12) and not (w238_b & lfc_actual12), \\",
 '            "W239 bands must clear the lfc actual draw range"',
 "        assert not (w238_a & options_actual12) and \\",
 "            not (w238_b & options_actual12), \\",
 '            "W239 bands must clear the options_wave2 actual draw range"',
  "        # band facts (law sec.4 W239 row): A = FIRST-CLEAN past the",
 "        # prior-wave B tail AND live SEED_REGISTRY points (the arithmetic",
 f"        # continuation {fmt(w238_a_tail + 1)}..{fmt(w238_a_tail + 2_000)} is REFUSED at its own",
 f"        # start by the W238 B band {fmt(W238['b_exit'][0])}..{fmt(w238_b_tail)} AND live seeds",
 "        # 541_500/542_000 -- NEW FACE, first live-seed refusal above the",
 "        # registered tail, exactly as the W238 seat leg4 succession",
 "        # projection notes anticipated; honest forward walk hop 1 ->",
 f"        # 542_001, hop 2 -> {fmt(a_lo)}..{fmt(a_hi)} hops=2, non-rotational",
 "        # r587 forward-monotone walk; A base >= prior-wave B tail+1",
 f"        # ({fmt(w238_b_tail)}+1) machine-checkable -- A-hops-prior-B staircase",
 "        # GE face, E36 card);",
 "        # B = FIRST-CLEAN arithmetic continuation of the prior-wave B",
 f"        # tail ({fmt(w238_b_tail + 1)}..{fmt(w238_b_tail + 200)} CLEAN on the registered",
 "        # universe, hops=0, NO own-A reservation jump needed -- own-A",
 "        # seed-hopped FAR past the staircase base: first seed-decoupled",
 "        # A/B gap face; B base == prior-wave B tail+1",
 f"        # ({fmt(w238_b_tail)}+1) machine-checkable; B window sits entirely below",
 f"        # the own-A window {fmt(a_lo)}..{fmt(a_hi)}; cross-window convergence with",
 "        # the W238 seat leg4 succession projection notes -- all",
 "        # MANDATORY notes honored (post-W238 universe re-derive +",
 "        # live-trace re-read, no staircase-equality assumption);",
 f'        assert WAVE_CONFIGS[239]["a_seed_base"] == {a_lo} >= {w238_b_tail} + 1, (',
 '            "W239 A must be the first-clean window past the prior-wave B "',
 '            "tail AND live seed points (arithmetic continuation REFUSED at "',
 '            "its own start by the W238 B band and live seeds, exactly as "',
 '            "the W238 seat leg4 succession projection notes anticipated; "',
 '            "honest forward walk hops=2; A base >= prior-wave B tail+1 "',
 '            "machine-checkable = A-hops-prior-B staircase GE face, E36 card")',
 f"        arith_a239 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a239 & reg_ints), \\",
 '            "W239 A window must be CLEAN (first-clean ADMIT face past prior-wave B + live seeds)"',
 f'        assert WAVE_CONFIGS[239]["b_exit_seed_base"] == {b_lo} == {w238_b_tail} + 1, (',
 '            "W239 B keeps the staircase base (FIRST-CLEAN arithmetic "',
 '            "continuation of the prior-wave B tail, hops=0, no own-A "',
 '            "reservation jump needed -- first seed-decoupled A/B gap face; "',
 '            "B base == prior-wave B tail+1 machine-checkable)")',
 f"        arith_b239 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b239 & reg_ints), \\",
 '            "W239 B window must be CLEAN (first-clean ADMIT face, staircase-base continuation)"',
 "        assert not (arith_b239 & arith_a239), \\",
 '            "W239 A/B same-freeze mutual exclusion (seed-decoupled gap face: B below own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W239-SHARD-0\",",
 '                                          "n1w239-0of12"), "W239 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W239-SHARD-11",',
 '                                           "n1w239-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w239\") and OUT.endswith(",
 '            "n1_w239_results.json"), "W239 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 239):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W239 shard dir collides with W{wprev}"',
 "        # W239 finalize cumulative deps: W17..W238 outputs ALL PRESENT",
 f"        # (landed net chain head {w238_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 239):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W239 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 239 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W238 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 239) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 239)], \\",
 '            "W239 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W238 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W239_PREREG.md")), \\',
 '            "W239 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w232_leg) + EOL + EOL.join(w233_leg) + EOL + EOL.join(w234_leg) + EOL + EOL.join(w235_leg) + EOL + EOL.join(w236_leg) + EOL + EOL.join(w237_leg) + EOL + EOL.join(w238_leg) + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (carried forward): the new
# block's LHS w<239> / RHS range(16,239)+range(17,239) / comment below-239 MUST move together.
assert block.count("if w < 239)") == 3, f"family-6 triple: w<239 count {block.count('if w < 239)')} != 3"
assert block.count("if w < 238)") == 0, "family-6 triple: stale w<238 leaked into the W239 block"
assert block.count("range(16, 239)") == 1 and block.count("range(17, 239)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 239 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W239 materializer face [same guard set, dep=W17..W238 "',
 f'          "outputs ALL PRESENT (landed net chain head {w238_total} = W238 bm-a finalize one-pass, K={w238_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND THIRTY-NINTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-c\'s sixty-sixth owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 65 + candidate; OWN-SEAT face: seat published by bm-c itself, "',
 '          "probe leg0 owner_rows=227 / bmc_ordinal=66 = seat-time pre-splice faces disclosed honest, "',
 '          "live derive at freeze governs), "',
 '          "A=FIRST-CLEAN past prior-wave B tail AND live seeds (seed-hop NEW FACE, "',
 '          "hops=2, staircase GE face, E36 card) + B=staircase-base continuation "',
 '          "(prior-B-tail+1 EXACT, hops=0, first seed-decoupled A/B gap face), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w239bmc_20261014_probe_receipt.json, law sec.4 W239 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]

old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W239"') == 1
assert n1_t4.count("# --- W239 materializer face") == 1     # block header
assert n1_t4.count('"+ W239 materializer face') == 1        # print fragment
assert n1_t4.count('239: {"batch": "PERPETUAL-N1-W239"') == 1
assert pf_t2.count(ROW_I + '239: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W239-SHARD-0"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[238] == {{"a": ({fmt(pf_mod.N1_BANDS[238]["a"][0])}, {fmt(pf_mod.N1_BANDS[238]["a"][1])}),') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[237] == {{"a": ({fmt(pf_mod.N1_BANDS[237]["a"][0])}, {fmt(pf_mod.N1_BANDS[237]["a"][1])}),') == 2
# the W237 leg now lives in BOTH the kept W238 block and the new W239 block (2);
# the W236 leg lives in the kept W237 + kept W238 + new W239 blocks (3); the
# W235 leg lives in kept W236 + W237 + W238 + new W239 (4); the W232/W233/W234
# legs likewise exist in multiple kept blocks
assert n1_t4.count(f'assert pf.N1_BANDS[236] == {{"a": ({fmt(pf_mod.N1_BANDS[236]["a"][0])}, {fmt(pf_mod.N1_BANDS[236]["a"][1])}),') == 3
assert n1_t4.count(f'assert pf.N1_BANDS[235] == {{"a": ({fmt(pf_mod.N1_BANDS[235]["a"][0])}, {fmt(pf_mod.N1_BANDS[235]["a"][1])}),') == 4
assert n1_t4.count('    # --- W209 materializer face') == 1  # estate source block kept
assert n1_t4.count('    # --- W210 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W211 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W212 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W213 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W214 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W215 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W216 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W217 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W218 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W219 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W220 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W221 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W222 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W223 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W224 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W225 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W226 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W227 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W228 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W229 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W230 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W231 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W232 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W233 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W234 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W235 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W236 materializer face') == 1  # prior block kept (W236 splice landed bm-a r974/r975 window)
assert n1_t4.count('    # --- W237 materializer face') == 1  # prior block kept (W237 splice landed bm-c r990 window)
assert n1_t4.count('    # --- W238 materializer face') == 1  # prior block kept (W238 splice landed bm-a r984/r985 window)
# no start>end malformed windows in inserted prose (r773 law)
for seg in (pf_comment, cfg_block, block, EOL.join(pr)):
    for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", seg):
        lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
        assert lo <= hi, f"malformed window {m.group(0)} in inserted prose"

# ---------- write + AST gate ----------
open(PF, "wb").write(pf_t2.encode("utf-8"))
open(N1, "wb").write(n1_t4.encode("utf-8"))
import py_compile
py_compile.compile(PF, doraise=True)
py_compile.compile(N1, doraise=True)

# ---------- receipt ----------
receipt = {
  "machine": "bm-c", "wave": 239,
  "phase": "five-face freeze chain-order splice (bm-c own-seat freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w239bmc_20261014_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "band_semantics": {"A": "FIRST-CLEAN past prior-wave B tail AND live SEED_REGISTRY points (hops=2 seed-hop NEW FACE; staircase GE face)",
                     "B": "FIRST-CLEAN arithmetic continuation of prior-wave B tail (hops=0, B base == prior-B tail+1 EXACT; first seed-decoupled A/B gap face)"},
  "w238_upstream": {"freeze_sha": w238_freeze_sha, "prereg_sha": w238_prereg_sha,
                    "ledger_total": w238_total, "merged_n": w238_merged_n,
                    "engine_owner": "bm-a (upstream seat honored)",
                    "repair_chain_note": "W238 bm-a own-wave closeout r985 (five-face splice 50fa77623 + engine self-burn 12/12 + finalize one-pass + five-key ALL PASS + sec78 backfill; six-gate PRE-FINALIZE 13th consecutive correct phase -- standing law held)"},
  "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                    "inherited": False,
                    "note": "seat published=reserved by bm-c itself (MSG-20261014-0914-bmc-w239-seat pushed to origin 603ff65d9 r991 BEFORE this freeze per r565 law); zero takeover -- wave 239 engine_owner=bm-c, bm-c's 66th own wave per live derive (probe leg0 owner_rows=227 / bmc_ordinal=66 = seat-time pre-splice faces disclosed honest, live derive governs r587/r359; freeze-time live face owner rows 228 + candidate = 229th EXACT)"},
  "w237_transitive": {"finalize_product": "results/perpetual_faces/n1_w237_results.json present (belt-and-braces gate; ledger 945,189 / K=519,320)"},
  "w236_transitive": {"finalize_product": "results/perpetual_faces/n1_w236_results.json present (belt-and-braces gate; ledger 942,989 / K=517,120)"},
  "w235_transitive": {"finalize_product": "results/perpetual_faces/n1_w235_results.json present (belt-and-braces gate; ledger 940,789 / K=514,920)"},
  "w234_transitive": {"finalize_product": "results/perpetual_faces/n1_w234_results.json present (belt-and-braces gate; ledger 938,589 / K=512,720)"},
  "w233_transitive": {"finalize_product": "results/perpetual_faces/n1_w233_results.json present (belt-and-braces gate; ledger 936,389 / K=510,520)"},
  "w232_transitive": {"finalize_product": "results/perpetual_faces/n1_w232_results.json present (belt-and-braces gate; ledger 934,189 / K=508,320)"},
  "w231_transitive": {"finalize_product": "results/perpetual_faces/n1_w231_results.json present (belt-and-braces gate; ledger 931,989 / K=506,120)"},
  "w230_transitive": {"finalize_product": "results/perpetual_faces/n1_w230_results.json present (belt-and-braces gate)"},
  "downstream_seat": "W240 seat ALREADY published by bm-a @ origin 39a30b6a0 (r986, queue-depth supply depth-3; W240 freeze waits-upstream on THIS W239 finalize, seat-first law held)",
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w239_prereg_sha, "probe_receipt_sha": w239_receipt_sha,
                    "note": "prereg derived+committed by the dead r996 session (47 SUB pairs from the frozen W238 template 8049952c9; estate absorbed by THIS r996-continuation window per the bm-c absorb precedent lineage 24th generation; zero takeover; freeze-time live derive bmc rows 65 + candidate 66th EXACT per r587/r359); splice editor derived from the committed W238 editor template by count-asserted ordered transform in this same freeze window (E63 heal: arith_a239/arith_b239 define+assert consistent -- the W238 template one-behind assert drift NOT carried); upstream W238 already landed (clean-precondition twenty-eighth consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bma_rows_live": len(bma_rows_live),
                    "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmc_ordinal_face": 66,
                    "note": "post-W238 registration: bm-c rows 65 + candidate = 66th owned (live derive at freeze time governs per r587/r359; probe leg0 owner_rows=227 / bmc_ordinal=66 = seat-time pre-splice faces -- zero takeover, own-seat continuity)"},
  "parity_section": {"source": "OWN W238 block physical bytes (bm-a own splice generation, structure known exactly)",
                    "bytes": len(par_sec),
                    "row_asserts": par_sec.count("assert pf.N1_BANDS["),
                    "note": "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W231 legs -> W239 block = 97 rows ending at W238 (estate 90 + fresh W232 leg + W233 leg + W234 leg + W235 leg + W236 leg + W237 leg + W238 leg); disclosed: (a) inherited W213 leg error-string face (\"registered W212 row parity drift\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) W238 block's band-set variable one-behind naming face (w237_a holds wave-238 bands) = lineage mechanical aging face -- W239 block follows the same pattern (w238_a holds wave-239 bands), zero functional impact"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W238 editor family-6 gate carried forward: new block LHS w<239 x3 / RHS range(16,239)+range(17,239) / comment below-239 count-asserted ATOMICALLY before splice; W238 block's own w<238 face = legitimate prior-wave boundary (not stale); E63 heal applied (arith define/assert consistent)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1, "w223_block_kept": 1, "w224_block_kept": 1, "w225_block_kept": 1, "w226_block_kept": 1, "w227_block_kept": 1, "w228_block_kept": 1, "w229_block_kept": 1, "w230_block_kept": 1, "w231_block_kept": 1, "w232_block_kept": 1, "w233_block_kept": 1, "w234_block_kept": 1, "w235_block_kept": 1, "w236_block_kept": 1, "w237_block_kept": 1, "w238_block_kept": 1},
}

open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w238_upstream", "own_seat_face")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> engine self-ignite W239 burn (12 shards) -> PRE-FINALIZE six-gate (standing law) -> finalize one-pass")
