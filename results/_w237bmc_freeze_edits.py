# -*- coding: utf-8 -*-
# 2026-10-14 08:3x bm-c r990 freeze window (upstream W1..W236 ALL LANDED, clean
# precondition): W237 five-face freeze splice editor -- bm-c OWN-SEAT face (seat
# MSG-20261014-0654-bmc-w237-seat published=reserved by bm-c itself @ origin
# 9312ef7ac r988, pre-seat probe ADMIT receipt _w237bmc_20261014_probe_receipt.json
# same payload; per-wave prereg PERPETUAL_N1_W237_PREREG.md derived+landed by the
# dead r990-predecessor window (estate absorbed this window, prereg on origin via
# the rebase-landed commit), zero takeover, zero DRAFT marker). Upstream chain ALL
# LANDED at this window: W1..W236 finalize products present (W236 bm-a own-wave
# closeout r975: five-face splice + engine self-burn 12/12 + finalize one-pass
# 16dd2cda0 07:2x five-key ALL PASS + sec78 backfill; net chain head 942,989,
# merged pool K=517,120, n1_w236_results.json machine-read) -- ZERO in-flight
# upstream seats, clean precondition (twenty-sixth consecutive fully-clean freeze
# window). Upstream six-gate disclosure: the W236 cycle ran its PRE-FINALIZE
# correctly (standing law since the W217 debt); THIS W237 cycle runs PRE-FINALIZE
# likewise (standing law).
# Lineage: _w236bma_freeze_edits.py template (proven live-fire freeze, committed by
# the bm-a r974/r975 window; engine self-burn + finalize verified r975) + r787
# preflight law + r609 origin-verbatim base + r761 programmatic quote wrapping +
# r909 physical-byte anchors + r838 per-file EOL detection + family #6
# LHS/RHS/comment ATOMIC TRIPLE (the new block's w<237>/range(16,237)/
# range(17,237)/below-237 quadruple is count-asserted atomically; the W236 block's
# own w<236 face is legitimate prior-wave boundary, not stale).
# Zero hardcoded upstream band values: ALL W236 facts machine-derived from the
# LIVE pf import at freeze time (the registered W236 row -- bm-a seat honored),
# cross-checked against the committed ADMIT receipt
# (results/_w237bmc_20261014_probe_receipt.json) which was derived on the
# post-W236-declared universe. If the LIVE W236 bands differ from the declared
# face, the staircase asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W236 editor): the parity estate (W138..W206 full-span
# 69 rows, r858 absorb generation, + W211..W231 legs) is extracted from the OWN
# W236 block physical bytes -- structure known exactly (bm-a's own splice
# generation, committed) -- the W236 block's own W232 + W233 + W234 + W235 legs
# are excluded from the estate path and fresh W232 + W233 + W234 + W235 + W236
# legs are appended for the W237 block parity (95 rows: estate 90 ending W231 +
# W232 leg + W233 leg + W234 leg + W235 leg + W236 leg). Extraction self-asserts
# the 90-row cut regardless.
# Disclosed: (a) the inherited W213 leg inside the estate carries a cosmetic
# error-string face ("registered W212 row parity drift") from the r912 editor
# generation -- physical bytes preserved verbatim per extraction law, zero
# functional impact (assert target [213] is correct); (b) the W236 block's
# band-set variable naming one-behind face (w235_a holds wave-236 bands) is
# the lineage's mechanical aging face -- the W237 block follows the same
# mechanical pattern (w236_a holds wave-237 bands), zero functional impact.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w237bmc_20261014_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w237bmc_freeze_receipt.json")
SEAT_MSG = "MSG-20261014-0654-bmc-w237-seat.md"
SEAT_ORIGIN = "9312ef7ac"
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

# ---------- gate 0.5: W236 five-face landed + W236 finalize product present ----------
# (chain-order precondition; W235/W234/W233/W232/W231/W230/W225/W224 finalize are
# transitive deps of the W237 freeze and are belt-and-braces checked here + enforced
# by the block's cumulative-deps assert range(17, 237) at selftest time)
W236 = dict(pf_mod.N1_BANDS.get(236) or {})
assert W236.get("engine_owner") == "bm-a", \
    f"W236 row not landed as declared (bm-a seat owner expected): {W236} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w236_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w236_results.json")
assert os.path.exists(w236_out_path), "W236 finalize product missing (n1_w236_results.json) -- chain dep not met"
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
w225_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w225_results.json")
assert os.path.exists(w225_out_path), "W225 finalize product missing (transitive chain dep) -- abort"
w224_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w224_results.json")
assert os.path.exists(w224_out_path), "W224 finalize product missing (transitive chain dep) -- abort"
w236_out = json.load(open(w236_out_path, encoding="utf-8"))
w236_led = (w236_out.get("science_gates") or {}).get("ledger") or {}
w236_total = w236_led.get("total")
w236_merged_n = None
try:
    w236_merged_n = w236_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w236_total == 942_989 and w236_merged_n == 517_120, \
    f"W236 finalize anchors drift at freeze time: total={w236_total} merged={w236_merged_n} (expect 942,989 / 517,120)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '236: {"a"', "--", "scripts/perpetual_faces.py")
w236_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W236_PREREG.md")
w236_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W237_PREREG.md")
w237_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W237_PREREG.md")), \
    "W237 per-wave prereg missing on disk -- chain face incomplete, abort (r990 derive landed pre-freeze expected)"
with open(os.path.join(REPO, "research", "PERPETUAL_N1_W237_PREREG.md"), encoding="utf-8") as _fh:
    _pre_head = _fh.read(2000)
assert "DRAFT-NOT-FROZEN" not in _pre_head, "W237 prereg still DRAFT -- abort (freeze commit pending face)"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face owner_rows=225 / bmc_rows=64 / ordinal=227 / bmc_ordinal=65
# = seat-time PRE-W236-splice live faces; live derive at freeze time:
# W236 splice LANDED -> owner rows 226 + candidate = 227th EXACT; bm-c rows 64 +
# candidate = 65th EXACT -- bm-c own-seat continuity face, zero takeover)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 226 and len(bmc_rows_live) == 64, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bmc={len(bmc_rows_live)} (expect 226/64 PRE-splice post-W236 registration; this candidate = bm-c's 65th own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W236 landed (freeze {w236_freeze_sha[:10]}, owner=bm-a seat honored, zero takeover face), "
      f"W236+W235+W234+W233+W232+W231+W230+W225+W224 finalize products present "
      f"(W236 ledger head {w236_total}, merged n={w236_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-c rows {len(bmc_rows_live)} + candidate (65th own wave per live derive; "
      f"probe receipt leg0 owner_rows=225 / bmc_ordinal=65 = seat-time pre-splice faces disclosed honest)")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
A = rec["bands"]["A"]; B = rec["bands"]["B"]
# W237 probe receipt bands carry int-list faces + explicit lo/hi keys
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
assert (a_lo, a_hi) == (536_204, 538_203) and (b_lo, b_hi) == (538_204, 538_403), \
    f"W237 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w236_b_tail = W236["b_exit"][1]      # registered W236 row b_exit hi (pf import, live)
w236_a_tail = W236["a"][1]            # registered W236 row A hi (pf import, live)
assert w236_b_tail + 1 == a_lo and a_hi + 1 == b_lo, "staircase base relations broken"
# the REFUSED arithmetic continuation starts at prior-wave A-tail+1 (== W236 B-base),
# machine-derived from the LIVE registered row, never transcribed.
assert w236_a_tail + 1 == W236["b_exit"][0], "W236 A-tail+1 != W236 B-base (registered row in-wave relation)"
assert [w236_a_tail + 1, w236_a_tail + 2_000] == leg1["ARITH_A"], \
    f"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w236_a_tail + 1, w236_a_tail + 2_000]} != {leg1['ARITH_A']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w237bmc_20261014_probe_receipt.json")
w237_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W237 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W237_PREREG.md"],
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
# STRUCTURAL CHOICE: extract the estate from the OWN W236 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W231
# leg = 90 rows) -- the W236 block is bm-a's own splice generation
# (r974/r975 window editor), structure known. The W236 block span ends
# where the T-141 s2 lane face marker begins.
a16 = '    # --- W236 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w236_start = n1_t.find(a16); t141_pos = n1_t.find(a_t141)
assert w236_start > 0 and t141_pos > w236_start, \
    "W236 materializer block face not found (W236 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w236_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W236 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m232 = re.search(r" *assert pf\.N1_BANDS\[232\] ==", par_full)
assert m232, "upstream W232 row leg not found inside W236 parity span"
par_sec = par_full[:m232.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 90 \
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \
    and [int(_estate_ws[69 + i]) for i in range(11)] == [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221] \
    and [int(_estate_ws[80 + i]) for i in range(9)] == [222, 223, 224, 225, 226, 227, 228, 229, 230] \
    and int(_estate_ws[89]) == 231, \
    f"estate segment not W138..W206 full-span 69 rows + W211..W230 legs + W231 leg: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"
assert par_full.count("assert pf.N1_BANDS[") == 94, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 94 (69 estate + W211..W230 legs + W231 leg + W232 leg + W233 leg + W234 leg + W235 leg)"

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '236: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W236_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
# MEM_I derived INSIDE the W236 cfg entry span (own splice generation, value
# format known: plain int -- indent is all we take)
_c236 = n1_t.find('236: {"batch"')
assert _c236 > 0, "W236 cfg entry not found (W236 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c236)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c236) > _mpos, "W236 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W236["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W236["a"][0]), _c236) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W236["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '236: {"a"', PF_EOL)

# ---------- W236 row owner line (physical bytes; comment text is own generation) ----------
w236_row_start = pf_t.find('    236: {"a"')
assert w236_row_start > 0, "W236 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w236_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w236_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-a"' in w236_own_line, \
    f"W236 owner line unexpected bytes: {w236_own_line!r}"
ROWC_I = w236_own_line[:len(w236_own_line) - len(w236_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W237 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat",
"    # MSG-20261014-0654-bmc-w237-seat published=reserved by bm-c itself @",
"    # origin " + SEAT_ORIGIN + " (r988, zero takeover); prereg + ADMIT probe",
"    # receipt frozen commit " + w237_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W237_PREREG.md",
"    # r990 own-seat derive landed pre-freeze [dead-window estate absorbed,",
"    # rebase-landed on origin], probe",
"    # results/_w237bmc_20261014_probe_receipt.json @ " + w237_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-a W236 five-face (freeze " + w236_freeze_sha[:10] + ") + W236",
"    # finalize product landed (n1_w236_results.json present, ledger",
"    # head " + str(w236_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W237 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w237bmc_20261014_probe_receipt.json: A = FIRST-CLEAN",
"    # past the registered W236 B band (arithmetic continuation",
"    # " + fmt(w236_a_tail + 1) + ".." + fmt(w236_a_tail + 2_000) + " REFUSED at its own start by the W236 B band",
"    # " + fmt(W236["b_exit"][0]) + ".." + fmt(w236_b_tail) + ", exactly as the W236 seat leg4",
"    # projection anticipated);",
"    # honest forward walk hops=1 -> " + fmt(a_lo) + ".." + fmt(a_hi) + ", non-rotational",
"    # r587 forward-monotone walk; A base == prior-wave B tail+1",
"    # (" + fmt(w236_b_tail) + "+1) machine-checkable -- A-hops-prior-B staircase",
"    # NINETY-SEVENTH instance, E36 card (probe receipt leg1 A_semantics",
"    # machine-read ordinal, never transcribed);",
"    # B = FIRST-CLEAN past the own-wave A window (arithmetic",
"    # continuation " + fmt(a_lo) + ".." + fmt(a_lo + 199) + " CLEAN on the registered",
"    # universe but lands INSIDE the W237 A band window " + fmt(a_lo) + ".." + fmt(a_hi) + " --",
"    # same-freeze mutual exclusion (W141 precedent, leg2 law) --",
"    # the walk with the own-wave A window reserved jumps to",
"    # " + fmt(b_lo) + " -> " + fmt(b_lo) + ".." + fmt(b_hi) + ", hops=1, non-rotational",
"    # r587 forward-monotone walk; B base == own-wave A tail+1",
"    # (" + fmt(a_hi) + "+1) machine-checkable);",
"    # single-window derive (r812 merged the gate legs INTO the",
"    # pre-seat probe; dual-window parity N/A honest); scan face =",
"    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1",
"    # used-seed band + probe cluster 95_000..95_003 + cross-face",
"    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/",
"    # N2-W15 probe points.",
"    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):",
"    # " + gate_lines[0] + ";",
"    # " + gate_lines[1] + ".",
"    # W238+ projection (gate-derived pre-seat probe leg4, pre-W237",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W238p_A"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " /",
"    # B naive first-clean " + rec["legs"]["leg4"]["W238p_B"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " -- naive B lands",
"    # INSIDE the naive A window and the registered W237 B band",
"    # " + fmt(b_lo) + ".." + fmt(b_hi) + " will refuse the naive W238 A window; W238 freezer",
"    # MUST re-derive on the post-W237 universe AND reserve the",
"    # own-wave A window when deriving B (W141 precedent, leg2 law,",
"    # E36 staircase card, NINETY-EIGHTH instance anticipated; never transcribe r587).",
])
pf_row = (f'{ROW_I}237: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'237: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w236_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w236_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W236 finalize ALL LANDED (W236 finalize product present at splice, "
            f"net chain head {w236_total} machine-read, merged pool K={w236_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition; "
            f"downstream W238 seat NOT yet published (queue-deepen seat-chain mandate "
            f"O-20261011-0012 sec.ii -- next seat publication follows per seat-first law)")
cfg_lines = [
 f'{CFG_I}237: {{"batch": "PERPETUAL-N1-W237",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W237_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND THIRTY-SEVENTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W236 row five-face freeze (bm-a own seat executed at the r974/r975 window; engine self-burn 12/12; finalize one-pass r975 07:2x, ledger 940,789+2,200=942,989 / K=517,120 machine-read), ",
 f"{w236_freeze_sha[:10]} (prereg {w236_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W236 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261014-0654-bmc-w237-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg ",
 "r990 own-seat derive landed pre-freeze [dead-window estate absorbed, rebase-landed] -- zero takeover face, bm-c own-seat ",
 "continuity, ",
 f"prereg {w237_prereg_sha[:10]} @ receipt {w237_receipt_sha[:10]}) -- this freeze splice editor derived from the committed W236 editor template in this same freeze window; ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W236 five-face + W236 finalize product landed ",
 "(executed in the bm-c loop freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c (bm-c OWN-SEAT face -- bm-c's SIXTY-FIFTH ",
 "owned claim per machine-derive (engine_owner==bm-c rows ",
 f"{len(bmc_rows_live)} + candidate; probe receipt leg0 owner_rows=225 / bmc_ordinal=65 = seat-time pre-splice ",
 "live faces disclosed honest, live derive governs ",
 "r587/r359 -- zero takeover, own-seat continuity)), ",
 "wave 237: ",
 "A = FIRST-CLEAN past the registered W236 B band (the ",
 f"arithmetic continuation {fmt(w236_a_tail + 1)}..{fmt(w236_a_tail + 2_000)} is REFUSED at its ",
 f"own start by the W236 B band {fmt(W236['b_exit'][0])}..{fmt(w236_b_tail)}, exactly as ",
 "the W236 seat leg4 succession ",
 "projection notes anticipated; honest forward walk hops=1 -> ",
 f"{fmt(a_lo)}..{fmt(a_hi)}; A base == prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase NINETY-SEVENTH ",
 "instance, E36 card (probe receipt leg1 machine-read ordinal); ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN ",
 "past the own-wave A window (the arithmetic continuation ",
 f"{fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the registered universe but lands ",
 f"INSIDE the W237 A band window {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual ",
 "exclusion, W141 precedent, leg2 law -- the walk with the ",
 f"own-wave A window reserved jumps to {fmt(b_lo)}, first-clean ",
 f"{fmt(b_lo)}..{fmt(b_hi)} hops=1, non-rotational r587 forward-monotone walk; ",
 "B base == own-wave A tail+1 machine-checkable; cross-window ",
 "convergence with the W236 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W236 universe ",
 "re-derive + own-wave A reservation); ADMIT receipt ",
 "results/_w237bmc_20261014_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W238+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W238p_A']} CLEAN / B naive first-clean ",
 f"{rec['legs']['leg4']['W238p_B']} CLEAN -- naive B lands INSIDE the naive A window and ",
 f"the registered W237 B band {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W238 A window; ",
 "W238+ freezer MUST re-derive on the post-W237 universe AND ",
 "reserve the own-wave A window when deriving B (W141 precedent, ",
 "leg2 law, E36 staircase card, NINETY-EIGHTH instance anticipated) -- ",
 "downstream W238 seat publication pending per seat-first law; " + fin_face + " -- the finalize ",
 "merge loop still derives the wave set from registry keys at ",
 "run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W237 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past the registered W236 B band; arithmetic {fmt(w236_a_tail + 1)}..{fmt(w236_a_tail + 2_000)} REFUSED at own start by the W236 B band {fmt(W236["b_exit"][0])}..{fmt(w236_b_tail)}; hops=1; A-hops-prior-B staircase NINETY-SEVENTH instance, E36 card; ordinal machine-read NINETY-SEVENTH per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W237 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN past the own-wave A window; arithmetic {fmt(a_lo)}..{fmt(a_lo + 199)} lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w237", "out_name": "n1_w237_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]
cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('237: {"batch": "PERPETUAL-N1-W237"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W237 materializer face (bm-c loop five-face freeze splice --",
 "    #     OWN-SEAT face under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's sixty-fifth owned per machine-derive (engine_owner==bm-c",
 f"    #     rows {len(bmc_rows_live)} + candidate; own-seat face: seat published=reserved by bm-c itself",
 "    #     (r988 MSG-20261014-0654-bmc-w237-seat @ origin 9312ef7ac; probe leg0",
 "    #     owner_rows=225 / bmc_ordinal=65 = seat-time pre-splice faces;",
 "    #     live derive at freeze governs);",
 "    #     wave 237 = first free number after the",
 "    #     REGISTERED W236 row (five-face freeze " + w236_freeze_sha[:10] + "; bm-a own seat executed at",
 "    #     the r974/r975 window; engine",
 "    #     self-burn 12/12 + finalize one-pass r975 07:2x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held) honest note)",
 "    #     -- SINGLE STATE zero seat gap (W2..W236 all registered). Seat",
 "    #     published=reserved MSG-20261014-0654-bmc-w237-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg",
 f"    #     r990 own-seat derive landed pre-freeze commit {w237_prereg_sha[:10]} [dead-window estate absorbed,",
 "    #     rebase-landed on origin]; this freeze splice editor",
 "    #     derived from the committed W236 editor template in this same freeze",
 "    #     window; deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W236 five-face + W236 finalize",
 "    #     product landed; zero --no-verify; the W237 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND THIRTY-SEVENTH engine wave BY",
 f"    #     MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w237bmc_20261014_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W237 bands were never assigned).",
 "    _set_wave(237)",
 "    try:",
 '        assert WAVE_CONFIGS[236]["a_seed_base"] == pf.N1_BANDS[236]["a"][0], \\',
 '            "W237 upstream W236 mirror drift (a)"',
 "        assert WAVE_CONFIGS[236][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[236]["b_exit"][0], "W237 upstream W236 mirror drift (b)"',
 "        assert WAVE_CONFIGS[236].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[236].get("engine_owner") == "bm-a", \\',
 '            "W237 upstream W236 engine_owner mirror drift (law-mirror parity; bm-a upstream seat face)"',
 "        w236_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w236_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w236_a & w236_b), "W237 A/B band overlap"',
 "        assert not (w236_a & reg_ints) and not (w236_b & reg_ints), \\",
 '            "W237 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w236_a), ("B", w236_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W237 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W237 {nm} hits W1"',
 '            assert not (band & probes), f"W237 {nm} hits probe seeds"',
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
tail = [
 "        # prior-wave disjointness W2..W236 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 237):",
 '            assert not (w236_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W237 A hits W{wprev}\"",
 '            assert not (w236_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W237 B hits W{wprev}\"",
 "        n3r1_used237 = set(range(70_000, 70_006))",
 "        assert not (w236_a & n3r1_used237) and not (w236_b & n3r1_used237), \\",
 '            "W237 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w236_a & lfc_actual12) and not (w236_b & lfc_actual12), \\",
 '            "W237 bands must clear the lfc actual draw range"',
 "        assert not (w236_a & options_actual12) and \\",
 "            not (w236_b & options_actual12), \\",
 '            "W237 bands must clear the options_wave2 actual draw range"',
 "        # band facts (law sec.4 W237 row): A = FIRST-CLEAN past",
 "        # the registered W236 B band (the arithmetic continuation",
 f"        # {fmt(w236_a_tail + 1)}..{fmt(w236_a_tail + 2_000)} is REFUSED at its own start by the W236 B band",
 f"        # {fmt(W236['b_exit'][0])}..{fmt(w236_b_tail)}, exactly as the W236 seat leg4",
 "        # succession projection notes anticipated; honest",
 f"        # forward walk hops=1 lands {fmt(a_lo)}..{fmt(a_hi)}; A base ==",
 f"        # prior-wave B tail+1 ({fmt(w236_b_tail)}+1) machine-checkable --",
 "        # A-hops-prior-B staircase NINETY-SEVENTH instance, E36 card;",
 "        # non-rotational r587 forward-monotone walk);",
 "        # B = FIRST-CLEAN past the own-wave A window (the",
 f"        # arithmetic continuation {fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the",
 f"        # registered universe but lands INSIDE the W237 A band window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual exclusion (W141 precedent,",
 "        # leg2 law) -- the walk with the own-wave A window reserved",
 f"        # jumps to {fmt(b_lo)} and lands {fmt(b_lo)}..{fmt(b_hi)}, hops=1,",
 "        # non-rotational r587 forward-monotone walk; B base ==",
 f"        # own-wave A tail+1 ({fmt(a_hi)}+1) machine-checkable;",
 "        # cross-window convergence with the W236 seat leg4",
 "        # succession projection notes -- all MANDATORY notes",
 "        # honored (post-W236 universe re-derive + own-wave A",
 "        # reservation when deriving B);",
 f'        assert WAVE_CONFIGS[237]["a_seed_base"] == {a_lo} == {w236_b_tail} + 1, (',
 '            "W237 A must be the first-clean window past the registered "',
 '            "W236 B band tail (arithmetic continuation REFUSED at its own "',
 '            "start by the W236 B band, exactly as the W236 seat leg4 "',
 '            "succession projection notes anticipated; honest forward walk "',
 '            "hops=1; A base == prior-wave B tail+1 machine-checkable "',
 '            "= A-hops-prior-B staircase NINETY-SEVENTH instance, E36 card")',
 f"        arith_a237 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a237 & reg_ints), \\",
 '            "W237 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
 f'        assert WAVE_CONFIGS[237]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
 '            "W237 B must be the first-clean window past the own-wave A "',
 '            "band tail (arithmetic continuation CLEAN on the registered "',
 '            "universe but lands INSIDE the W237 A band window; "',
 '            "same-freeze mutual exclusion (W141 precedent, leg2 law) -- "',
 '            "the walk with the own-wave A window reserved jumps, "',
 '            "first-clean hops=1, non-rotational r587 forward-monotone "',
 '            "walk; B base == own-wave A tail+1 machine-checkable)")',
 f"        arith_b237 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b237 & reg_ints), \\",
 '            "W237 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
 "        assert not (arith_b237 & arith_a237), \\",
 '            "W237 A/B same-freeze mutual exclusion (B hops past own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W237-SHARD-0\",",
 '                                          "n1w237-0of12"), "W237 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W237-SHARD-11",',
 '                                           "n1w237-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w237\") and OUT.endswith(",
 '            "n1_w237_results.json"), "W237 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 237):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W237 shard dir collides with W{wprev}"',
 "        # W237 finalize cumulative deps: W17..W236 outputs ALL PRESENT",
 f"        # (landed net chain head {w236_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 237):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W237 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 237 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W236 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 237) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 237)], \\",
 '            "W237 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W236 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W237_PREREG.md")), \\',
 '            "W237 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w232_leg) + EOL + EOL.join(w233_leg) + EOL + EOL.join(w234_leg) + EOL + EOL.join(w235_leg) + EOL + EOL.join(w236_leg) + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (carried forward): the new
# block's LHS w<237> / RHS range(16,237)+range(17,237) / comment below-237 MUST move together.
assert block.count("if w < 237)") == 3, f"family-6 triple: w<237 count {block.count('if w < 237)')} != 3"
assert block.count("if w < 236)") == 0, "family-6 triple: stale w<236 leaked into the W237 block"
assert block.count("range(16, 237)") == 1 and block.count("range(17, 237)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 237 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W237 materializer face [same guard set, dep=W17..W236 "',
 f'          "outputs ALL PRESENT (landed net chain head {w236_total} = W236 bm-a finalize one-pass, K={w236_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND THIRTY-SEVENTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-c\'s sixty-fifth owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 64 + candidate; OWN-SEAT face: seat published by bm-c itself, "',
 '          "probe leg0 owner_rows=225 / bmc_ordinal=65 = seat-time pre-splice faces disclosed honest, "',
 '          "live derive at freeze governs), "',
 '          "A=FIRST-CLEAN past the registered W236 B band (staircase "',
 '          "NINETY-SEVENTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
 '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
 '          "mutual exclusion, hops=1), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w237bmc_20261014_probe_receipt.json, law sec.4 W237 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]
old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W237"') == 1
assert n1_t4.count("# --- W237 materializer face") == 1     # block header
assert n1_t4.count('"+ W237 materializer face') == 1        # print fragment
assert n1_t4.count('237: {"batch": "PERPETUAL-N1-W237"') == 1
assert pf_t2.count(ROW_I + '237: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W237-SHARD-0"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[236] == {{"a": ({fmt(pf_mod.N1_BANDS[236]["a"][0])}, {fmt(pf_mod.N1_BANDS[236]["a"][1])}),') == 1
# the W235 leg now lives in BOTH the kept W236 block and the new W237 block (2);
# the W232/W233/W234 legs likewise exist in the kept W233..W236 blocks (multiple)
assert n1_t4.count(f'assert pf.N1_BANDS[235] == {{"a": ({fmt(pf_mod.N1_BANDS[235]["a"][0])}, {fmt(pf_mod.N1_BANDS[235]["a"][1])}),') == 2
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
  "machine": "bm-c", "wave": 237,
  "phase": "five-face freeze chain-order splice (bm-c own-seat freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w237bmc_20261014_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "w236_upstream": {"freeze_sha": w236_freeze_sha, "prereg_sha": w236_prereg_sha,
                    "ledger_total": w236_total, "merged_n": w236_merged_n,
                    "engine_owner": "bm-a (upstream seat honored)",
                    "repair_chain_note": "W236 bm-a own-wave closeout r975 (five-face splice + engine self-burn 12/12 + finalize one-pass 16dd2cda0 + five-key ALL PASS + sec78 backfill; six-gate PRE-FINALIZE correct phase -- standing law held)"},
  "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                    "inherited": False,
                    "note": "seat published=reserved by bm-c itself (MSG-20261014-0654-bmc-w237-seat pushed to origin 9312ef7ac r988 BEFORE this freeze per r565 law); zero takeover -- wave 237 engine_owner=bm-c, bm-c's 65th own wave per live derive (probe leg0 owner_rows=225 / bmc_ordinal=65 = seat-time pre-splice faces disclosed honest, live derive governs r587/r359; freeze-time live face owner rows 226 + candidate = 227th EXACT)"},
  "w235_transitive": {"finalize_product": "results/perpetual_faces/n1_w235_results.json present (belt-and-braces gate; ledger 940,789 / K=514,920)"},
  "w234_transitive": {"finalize_product": "results/perpetual_faces/n1_w234_results.json present (belt-and-braces gate; ledger 938,589 / K=512,720)"},
  "w233_transitive": {"finalize_product": "results/perpetual_faces/n1_w233_results.json present (belt-and-braces gate; ledger 936,389 / K=510,520)"},
  "w232_transitive": {"finalize_product": "results/perpetual_faces/n1_w232_results.json present (belt-and-braces gate; ledger 934,189 / K=508,320)"},
  "w231_transitive": {"finalize_product": "results/perpetual_faces/n1_w231_results.json present (belt-and-braces gate)"},
  "w230_transitive": {"finalize_product": "results/perpetual_faces/n1_w230_results.json present (belt-and-braces gate)"},
  "w225_transitive": {"finalize_product": "results/perpetual_faces/n1_w225_results.json present (belt-and-braces gate; ledger 918,789 / K=492,920)"},
  "w224_transitive": {"finalize_product": "results/perpetual_faces/n1_w224_results.json present (belt-and-braces gate; ledger 916,589 / K=490,720)"},
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w237_prereg_sha, "probe_receipt_sha": w237_receipt_sha,
                    "note": "prereg derived+committed by the dead r990-predecessor window (estate absorbed this window, rebase-landed on origin; zero takeover; freeze-time live derive bmc rows 64 + candidate 65th EXACT per r587/r359); splice editor derived from the committed W236 editor template by count-asserted ordered transform in this same freeze window; upstream W236 already landed (clean-precondition twenty-sixth consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bma_rows_live": len(bma_rows_live),
                    "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmc_ordinal_face": 65,
                    "note": "post-W236 registration: bm-c rows 64 + candidate = 65th owned (live derive at freeze time governs per r587/r359; probe leg0 owner_rows=225 / bmc_ordinal=65 = seat-time pre-splice faces -- zero takeover, own-seat continuity)"},
  "parity_section": {"source": "OWN W236 block physical bytes (bm-a own splice generation, structure known exactly)",
                    "bytes": len(par_sec),
                    "row_asserts": par_sec.count("assert pf.N1_BANDS["),
                    "note": "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W231 legs -> W237 block = 95 rows ending at W236 (estate 90 + fresh W232 leg + W233 leg + W234 leg + W235 leg + W236 leg); disclosed: (a) inherited W213 leg error-string face (\"registered W212 row parity drift\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) W236 block's band-set variable one-behind naming face (w235_a holds wave-236 bands) = lineage mechanical aging face -- W237 block follows the same pattern (w236_a holds wave-237 bands), zero functional impact"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W236 editor family-6 gate carried forward: new block LHS w<237 x3 / RHS range(16,237)+range(17,237) / comment below-237 count-asserted ATOMICALLY before splice; W236 block's own w<236 face = legitimate prior-wave boundary (not stale)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1, "w223_block_kept": 1, "w224_block_kept": 1, "w225_block_kept": 1, "w226_block_kept": 1, "w227_block_kept": 1, "w228_block_kept": 1, "w229_block_kept": 1, "w230_block_kept": 1, "w231_block_kept": 1, "w232_block_kept": 1, "w233_block_kept": 1, "w234_block_kept": 1, "w235_block_kept": 1, "w236_block_kept": 1},
}
open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w236_upstream", "own_seat_face")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> engine self-ignite W237 burn (12 shards) -> PRE-FINALIZE six-gate (standing law) -> finalize one-pass")
