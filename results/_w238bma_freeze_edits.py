# -*- coding: utf-8 -*-
# 2026-10-14 12:3x bm-a r984 freeze window (upstream W1..W237 ALL LANDED, clean
# precondition): W238 five-face freeze splice editor -- bm-a OWN-SEAT face (seat
# MSG-20261014-0745-bma-w238-seat published=reserved by bm-a itself @ origin
# 3e551d846 r976, pre-seat probe ADMIT receipt _w238bma_20261014_probe_receipt.json
# same payload; per-wave prereg PERPETUAL_N1_W238_PREREG.md derived+landed own-seat
# r983 commit 8049952c9, zero takeover, zero DRAFT marker). Upstream chain ALL
# LANDED at this window: W1..W237 finalize products present (W237 bm-c own-wave
# closeout r990: five-face splice e4a23cc7a + engine self-burn 12/12 + finalize
# one-pass; net chain head 945,189, merged pool K=519,320, n1_w237_results.json
# machine-read) -- ZERO in-flight upstream seats, clean precondition (twenty-
# seventh consecutive fully-clean freeze window). Upstream six-gate disclosure:
# the W237 cycle ran its PRE-FINALIZE correctly (standing law since the W217
# debt); THIS W238 cycle runs PRE-FINALIZE likewise (standing law).
# Lineage: _w237bmc_freeze_edits.py template (proven live-fire freeze, committed by
# the bm-c r990 window; engine self-burn + finalize verified r990) + r787
# preflight law + r609 origin-verbatim base + r761 programmatic quote wrapping +
# r909 physical-byte anchors + r838 per-file EOL detection + family #6
# LHS/RHS/comment ATOMIC TRIPLE (the new block's w<238>/range(16,238)/
# range(17,238)/below-238 quadruple is count-asserted atomically; the W237 block's
# own w<237 face is legitimate prior-wave boundary, not stale).
# Zero hardcoded upstream band values: ALL W237 facts machine-derived from the
# LIVE pf import at freeze time (the registered W237 row -- bm-c seat honored),
# cross-checked against the committed ADMIT receipt
# (results/_w238bma_20261014_probe_receipt.json) which was derived on the
# post-W237-declared universe. If the LIVE W237 bands differ from the declared
# face, the staircase asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W237 editor): the parity estate (W138..W206 full-span
# 69 rows, r858 absorb generation, + W211..W231 legs) is extracted from the OWN
# W237 block physical bytes -- structure known exactly (bm-c's own splice
# generation, committed) -- the W237 block's own W232 + W233 + W234 + W235 + W236
# legs are excluded from the estate path and fresh W232 + W233 + W234 + W235 +
# W236 + W237 legs are appended for the W238 block parity (96 rows: estate 90
# ending W231 + W232 leg + W233 leg + W234 leg + W235 leg + W236 leg + W237 leg).
# Extraction self-asserts the 90-row cut regardless.
# Disclosed: (a) the inherited W213 leg inside the estate carries a cosmetic
# error-string face ("registered W212 row parity drift") from the r912 editor
# generation -- physical bytes preserved verbatim per extraction law, zero
# functional impact (assert target [213] is correct); (b) the W237 block's
# band-set variable naming one-behind face (w236_a holds wave-237 bands) is
# the lineage's mechanical aging face -- the W238 block follows the same
# mechanical pattern (w237_a holds wave-238 bands), zero functional impact.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w238bma_20261014_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w238bma_freeze_receipt.json")
SEAT_MSG = "MSG-20261014-0745-bma-w238-seat.md"
SEAT_ORIGIN = "3e551d846"
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

# ---------- gate 0.5: W237 five-face landed + W237 finalize product present ----------
# (chain-order precondition; W236/W235/W234/W233/W232/W231/W230/W225 finalize are
# transitive deps of the W237 freeze and are belt-and-braces checked here + enforced
# by the block's cumulative-deps assert range(17, 237) at selftest time)
W237 = dict(pf_mod.N1_BANDS.get(237) or {})
assert W237.get("engine_owner") == "bm-c", \
    f"W237 row not landed as declared (bm-c seat owner expected): {W237} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w237_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w237_results.json")
assert os.path.exists(w237_out_path), "W237 finalize product missing (n1_w237_results.json) -- chain dep not met"
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
w225_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w225_results.json")
assert os.path.exists(w225_out_path), "W225 finalize product missing (transitive chain dep) -- abort"
w237_out = json.load(open(w237_out_path, encoding="utf-8"))
w237_led = (w237_out.get("science_gates") or {}).get("ledger") or {}
w237_total = w237_led.get("total")
w237_merged_n = None
try:
    w237_merged_n = w237_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w237_total == 945_189 and w237_merged_n == 519_320, \
    f"W237 finalize anchors drift at freeze time: total={w237_total} merged={w237_merged_n} (expect 945,189 / 519,320)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '237: {"a"', "--", "scripts/perpetual_faces.py")
w237_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W237_PREREG.md")
w237_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W238_PREREG.md")
w238_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W238_PREREG.md")), \
    "W238 per-wave prereg missing on disk -- chain face incomplete, abort (r983 derive landed pre-freeze expected)"
with open(os.path.join(REPO, "research", "PERPETUAL_N1_W238_PREREG.md"), encoding="utf-8") as _fh:
    _pre_head = _fh.read(2000)
assert "DRAFT-NOT-FROZEN" not in _pre_head, "W238 prereg still DRAFT -- abort (freeze commit pending face)"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face owner_rows=226 / bma_rows=121 / ordinal=228 / bma_ordinal=122
# = seat-time PRE-W237-splice live faces; live derive at freeze time:
# W237 splice LANDED -> owner rows 227 + candidate = 228th EXACT; bm-a rows 121 +
# candidate = 122nd EXACT -- bm-a own-seat continuity face, zero takeover)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 227 and len(bma_rows_live) == 121, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bma={len(bma_rows_live)} (expect 227/121 PRE-splice post-W237 registration; this candidate = bm-a's 122nd own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W237 landed (freeze {w237_freeze_sha[:10]}, owner=bm-c seat honored, zero takeover face), "
      f"W237+W236+W235+W234+W233+W232+W231+W230+W225 finalize products present "
      f"(W237 ledger head {w237_total}, merged n={w237_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-a rows {len(bma_rows_live)} + candidate (122nd own wave per live derive; "
      f"probe receipt leg0 owner_rows=226 / bma_ordinal=122 = seat-time pre-splice faces disclosed honest)")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
A = rec["bands"]["A"]; B = rec["bands"]["B"]
# W238 probe receipt bands carry int-list faces + explicit lo/hi keys
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
assert (a_lo, a_hi) == (538_404, 540_403) and (b_lo, b_hi) == (540_404, 540_603), \
    f"W238 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w237_b_tail = W237["b_exit"][1]      # registered W237 row b_exit hi (pf import, live)
w237_a_tail = W237["a"][1]            # registered W237 row A hi (pf import, live)
assert w237_b_tail + 1 == a_lo and a_hi + 1 == b_lo, "staircase base relations broken"
# the REFUSED arithmetic continuation starts at prior-wave A-tail+1 (== W237 B-base),
# machine-derived from the LIVE registered row, never transcribed.
assert w237_a_tail + 1 == W237["b_exit"][0], "W237 A-tail+1 != W237 B-base (registered row in-wave relation)"
assert [w237_a_tail + 1, w237_a_tail + 2_000] == leg1["ARITH_A"], \
    f"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w237_a_tail + 1, w237_a_tail + 2_000]} != {leg1['ARITH_A']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w238bma_20261014_probe_receipt.json")
w238_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W238 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W238_PREREG.md"],
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
# STRUCTURAL CHOICE: extract the estate from the OWN W237 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W231
# leg = 90 rows) -- the W237 block is bm-c's own splice generation
# (r990 window editor), structure known. The W237 block span ends
# where the T-141 s2 lane face marker begins.
a17 = '    # --- W237 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w237_start = n1_t.find(a17); t141_pos = n1_t.find(a_t141)
assert w237_start > 0 and t141_pos > w237_start, \
    "W237 materializer block face not found (W237 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w237_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W237 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m232 = re.search(r" *assert pf\.N1_BANDS\[232\] ==", par_full)
assert m232, "upstream W232 row leg not found inside W237 parity span"
par_sec = par_full[:m232.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 90 \
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \
    and [int(_estate_ws[69 + i]) for i in range(11)] == [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221] \
    and [int(_estate_ws[80 + i]) for i in range(9)] == [222, 223, 224, 225, 226, 227, 228, 229, 230] \
    and int(_estate_ws[89]) == 231, \
    f"estate segment not W138..W206 full-span 69 rows + W211..W230 legs + W231 leg: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"
assert par_full.count("assert pf.N1_BANDS[") == 95, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 95 (69 estate + W211..W230 legs + W231 leg + W232 leg + W233 leg + W234 leg + W235 leg + W236 leg)"

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '237: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W237_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
# MEM_I derived INSIDE the W237 cfg entry span (own splice generation, value
# format known: plain int -- indent is all we take)
_c237 = n1_t.find('237: {"batch"')
assert _c237 > 0, "W237 cfg entry not found (W237 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c237)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c237) > _mpos, "W237 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W237["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W237["a"][0]), _c237) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W237["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '237: {"a"', PF_EOL)

# ---------- W237 row owner line (physical bytes; comment text is own generation) ----------
w237_row_start = pf_t.find('    237: {"a"')
assert w237_row_start > 0, "W237 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w237_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w237_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-c"' in w237_own_line, \
    f"W237 owner line unexpected bytes: {w237_own_line!r}"
ROWC_I = w237_own_line[:len(w237_own_line) - len(w237_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W238 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat",
"    # MSG-20261014-0745-bma-w238-seat published=reserved by bm-a itself @",
"    # origin " + SEAT_ORIGIN + " (r976, zero takeover); prereg + ADMIT probe",
"    # receipt frozen commit " + w238_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W238_PREREG.md",
"    # r983 own-seat derive landed pre-freeze, probe",
"    # results/_w238bma_20261014_probe_receipt.json @ " + w238_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-c W237 five-face (freeze " + w237_freeze_sha[:10] + ") + W237",
"    # finalize product landed (n1_w237_results.json present, ledger",
"    # head " + str(w237_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W238 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w238bma_20261014_probe_receipt.json: A = FIRST-CLEAN",
"    # past the registered W237 B band (arithmetic continuation",
"    # " + fmt(w237_a_tail + 1) + ".." + fmt(w237_a_tail + 2_000) + " REFUSED at its own start by the W237 B band",
"    # " + fmt(W237["b_exit"][0]) + ".." + fmt(w237_b_tail) + ", exactly as the W237 seat leg4",
"    # projection anticipated);",
"    # honest forward walk hops=1 -> " + fmt(a_lo) + ".." + fmt(a_hi) + ", non-rotational",
"    # r587 forward-monotone walk; A base == prior-wave B tail+1",
"    # (" + fmt(w237_b_tail) + "+1) machine-checkable -- A-hops-prior-B staircase",
"    # NINETY-EIGHTH instance, E36 card (probe receipt leg1 A_semantics",
"    # machine-read ordinal, never transcribed);",
"    # B = FIRST-CLEAN past the own-wave A window (arithmetic",
"    # continuation " + fmt(a_lo) + ".." + fmt(a_lo + 199) + " CLEAN on the registered",
"    # universe but lands INSIDE the W238 A band window " + fmt(a_lo) + ".." + fmt(a_hi) + " --",
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
"    # W239+ projection (gate-derived pre-seat probe leg4, pre-W238",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W239p_A_naive"] + " REFUSED by live",
"    # SEED_REGISTRY points " + str(rec["legs"]["leg4"]["W239p_A_naive_refusers_seeds"]) + " (NEW FACE: first live-seed refusal",
"    # above the registered tail) -> honest walk first-clean",
"    # " + rec["legs"]["leg4"]["W239p_A_first_clean"] + " hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " /",
"    # B naive first-clean " + rec["legs"]["leg4"]["W239p_B_naive"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " -- naive B lands",
"    # INSIDE the naive A window and the registered W238 B band",
"    # " + fmt(b_lo) + ".." + fmt(b_hi) + " will refuse the naive W239 A window; W239 freezer",
"    # MUST re-derive on the post-W238 universe AND reserve the",
"    # own-wave A window when deriving B (W141 precedent, leg2 law,",
"    # E36 staircase card, NINETY-NINTH instance anticipated; never transcribe r587).",
])
pf_row = (f'{ROW_I}238: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-a"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'238: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w237_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w237_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W237 finalize ALL LANDED (W237 finalize product present at splice, "
            f"net chain head {w237_total} machine-read, merged pool K={w237_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition; "
            f"downstream W239 seat NOT yet published (queue-deepen seat-chain mandate "
            f"O-20261011-0012 sec.ii -- next seat publication follows per seat-first law)")
cfg_lines = [
 f'{CFG_I}238: {{"batch": "PERPETUAL-N1-W238",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W238_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND THIRTY-EIGHTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W237 row five-face freeze (bm-c own seat executed at the r990 window; engine self-burn 12/12; finalize one-pass r990 08:5x, ledger 942,989+2,200=945,189 / K=519,320 machine-read), ",
 f"{w237_freeze_sha[:10]} (prereg {w237_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W237 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261014-0745-bma-w238-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg ",
 "r983 own-seat derive landed pre-freeze -- zero takeover face, bm-a own-seat ",
 "continuity, ",
 f"prereg {w238_prereg_sha[:10]} @ receipt {w238_receipt_sha[:10]}) -- this freeze splice editor derived from the committed W237 editor template in this same freeze window; ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W237 five-face + W237 finalize product landed ",
 "(executed in the bm-a loop freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-a (bm-a OWN-SEAT face -- bm-a's ONE HUNDRED AND ",
 "TWENTY-SECOND owned claim per machine-derive (engine_owner==bm-a rows ",
 f"{len(bma_rows_live)} + candidate; probe receipt leg0 owner_rows=226 / bma_ordinal=122 = seat-time pre-splice ",
 "live faces disclosed honest, live derive governs ",
 "r587/r359 -- zero takeover, own-seat continuity)), ",
 "wave 238: ",
 "A = FIRST-CLEAN past the registered W237 B band (the ",
 f"arithmetic continuation {fmt(w237_a_tail + 1)}..{fmt(w237_a_tail + 2_000)} is REFUSED at its ",
 f"own start by the W237 B band {fmt(W237['b_exit'][0])}..{fmt(w237_b_tail)}, exactly as ",
 "the W237 seat leg4 succession ",
 "projection notes anticipated; honest forward walk hops=1 -> ",
 f"{fmt(a_lo)}..{fmt(a_hi)}; A base == prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase NINETY-EIGHTH ",
 "instance, E36 card (probe receipt leg1 machine-read ordinal); ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN ",
 "past the own-wave A window (the arithmetic continuation ",
 f"{fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the registered universe but lands ",
 f"INSIDE the W238 A band window {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual ",
 "exclusion, W141 precedent, leg2 law -- the walk with the ",
 f"own-wave A window reserved jumps to {fmt(b_lo)}, first-clean ",
 f"{fmt(b_lo)}..{fmt(b_hi)} hops=1, non-rotational r587 forward-monotone walk; ",
 "B base == own-wave A tail+1 machine-checkable; cross-window ",
 "convergence with the W237 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W237 universe ",
 "re-derive + own-wave A reservation); ADMIT receipt ",
 "results/_w238bma_20261014_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W239+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W239p_A_naive']} REFUSED by live SEED_REGISTRY points ",
 f"{rec['legs']['leg4']['W239p_A_naive_refusers_seeds']} -> honest walk first-clean ",
 f"{rec['legs']['leg4']['W239p_A_first_clean']} CLEAN; B naive first-clean ",
 f"{rec['legs']['leg4']['W239p_B_naive']} CLEAN -- naive B lands INSIDE the naive A window and ",
 f"the registered W238 B band {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W239 A window; ",
 "W239+ freezer MUST re-derive on the post-W238 universe AND ",
 "reserve the own-wave A window when deriving B (W141 precedent, ",
 "leg2 law, E36 staircase card, NINETY-NINTH instance anticipated) -- ",
 "downstream W239 seat publication pending per seat-first law; " + fin_face + " -- the finalize ",
 "merge loop still derives the wave set from registry keys at ",
 "run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W238 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past the registered W237 B band; arithmetic {fmt(w237_a_tail + 1)}..{fmt(w237_a_tail + 2_000)} REFUSED at own start by the W237 B band {fmt(W237["b_exit"][0])}..{fmt(w237_b_tail)}; hops=1; A-hops-prior-B staircase NINETY-EIGHTH instance, E36 card; ordinal machine-read NINETY-EIGHTH per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W238 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN past the own-wave A window; arithmetic {fmt(a_lo)}..{fmt(a_lo + 199)} lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w238", "out_name": "n1_w238_results.json",',
 f'{MEM_I}"engine_owner": "bm-a"}},',
]

cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('238: {"batch": "PERPETUAL-N1-W238"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W238 materializer face (bm-a loop five-face freeze splice --",
 "    #     OWN-SEAT face under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-a's one hundred and twenty-second owned per machine-derive (engine_owner==bm-a",
 f"    #     rows {len(bma_rows_live)} + candidate; own-seat face: seat published=reserved by bm-a itself",
 "    #     (r976 MSG-20261014-0745-bma-w238-seat @ origin 3e551d846; probe leg0",
 "    #     owner_rows=226 / bma_ordinal=122 = seat-time pre-splice faces;",
 "    #     live derive at freeze governs);",
 "    #     wave 238 = first free number after the",
 "    #     REGISTERED W237 row (five-face freeze " + w237_freeze_sha[:10] + "; bm-c own seat executed at",
 "    #     the r990 window; engine",
 "    #     self-burn 12/12 + finalize one-pass r990 08:5x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held) honest note)",
 "    #     -- SINGLE STATE zero seat gap (W2..W237 all registered). Seat",
 "    #     published=reserved MSG-20261014-0745-bma-w238-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg",
 f"    #     r983 own-seat derive landed pre-freeze commit {w238_prereg_sha[:10]}; this freeze splice editor",
 "    #     derived from the committed W237 editor template in this same freeze",
 "    #     window; deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W237 five-face + W237 finalize",
 "    #     product landed; zero --no-verify; the W238 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND THIRTY-EIGHTH engine wave BY",
 f"    #     MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w238bma_20261014_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W238 bands were never assigned).",
 "    _set_wave(238)",
 "    try:",
 '        assert WAVE_CONFIGS[237]["a_seed_base"] == pf.N1_BANDS[237]["a"][0], \\',
 '            "W238 upstream W237 mirror drift (a)"',
 "        assert WAVE_CONFIGS[237][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[237]["b_exit"][0], "W238 upstream W237 mirror drift (b)"',
 "        assert WAVE_CONFIGS[237].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[237].get("engine_owner") == "bm-c", \\',
 '            "W238 upstream W237 engine_owner mirror drift (law-mirror parity; bm-c upstream seat face)"',
 "        w237_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w237_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w237_a & w237_b), "W238 A/B band overlap"',
 "        assert not (w237_a & reg_ints) and not (w237_b & reg_ints), \\",
 '            "W238 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w237_a), ("B", w237_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W238 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W238 {nm} hits W1"',
 '            assert not (band & probes), f"W238 {nm} hits probe seeds"',
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
tail = [
 "        # prior-wave disjointness W2..W237 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 238):",
 '            assert not (w237_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W238 A hits W{wprev}\"",
 '            assert not (w237_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W238 B hits W{wprev}\"",
 "        n3r1_used238 = set(range(70_000, 70_006))",
 "        assert not (w237_a & n3r1_used238) and not (w237_b & n3r1_used238), \\",
 '            "W238 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w237_a & lfc_actual12) and not (w237_b & lfc_actual12), \\",
 '            "W238 bands must clear the lfc actual draw range"',
 "        assert not (w237_a & options_actual12) and \\",
 "            not (w237_b & options_actual12), \\",
 '            "W238 bands must clear the options_wave2 actual draw range"',
 "        # band facts (law sec.4 W238 row): A = FIRST-CLEAN past",
 "        # the registered W237 B band (the arithmetic continuation",
 f"        # {fmt(w237_a_tail + 1)}..{fmt(w237_a_tail + 2_000)} is REFUSED at its own start by the W237 B band",
 f"        # {fmt(W237['b_exit'][0])}..{fmt(w237_b_tail)}, exactly as the W237 seat leg4",
 "        # succession projection notes anticipated; honest",
 f"        # forward walk hops=1 lands {fmt(a_lo)}..{fmt(a_hi)}; A base ==",
 f"        # prior-wave B tail+1 ({fmt(w237_b_tail)}+1) machine-checkable --",
 "        # A-hops-prior-B staircase NINETY-EIGHTH instance, E36 card;",
 "        # non-rotational r587 forward-monotone walk);",
 "        # B = FIRST-CLEAN past the own-wave A window (the",
 f"        # arithmetic continuation {fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the",
 f"        # registered universe but lands INSIDE the W238 A band window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual exclusion (W141 precedent,",
 "        # leg2 law) -- the walk with the own-wave A window reserved",
 f"        # jumps to {fmt(b_lo)} and lands {fmt(b_lo)}..{fmt(b_hi)}, hops=1,",
 "        # non-rotational r587 forward-monotone walk; B base ==",
 f"        # own-wave A tail+1 ({fmt(a_hi)}+1) machine-checkable;",
 "        # cross-window convergence with the W237 seat leg4",
 "        # succession projection notes -- all MANDATORY notes",
 "        # honored (post-W236 universe re-derive + own-wave A",
 "        # reservation when deriving B);",
 f'        assert WAVE_CONFIGS[238]["a_seed_base"] == {a_lo} == {w237_b_tail} + 1, (',
 '            "W238 A must be the first-clean window past the registered "',
 '            "W237 B band tail (arithmetic continuation REFUSED at its own "',
 '            "start by the W237 B band, exactly as the W237 seat leg4 "',
 '            "succession projection notes anticipated; honest forward walk "',
 '            "hops=1; A base == prior-wave B tail+1 machine-checkable "',
 '            "= A-hops-prior-B staircase NINETY-EIGHTH instance, E36 card")',
 f"        arith_a238 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a237 & reg_ints), \\",
 '            "W238 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
 f'        assert WAVE_CONFIGS[238]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
 '            "W238 B must be the first-clean window past the own-wave A "',
 '            "band tail (arithmetic continuation CLEAN on the registered "',
 '            "universe but lands INSIDE the W238 A band window; "',
 '            "same-freeze mutual exclusion (W141 precedent, leg2 law) -- "',
 '            "the walk with the own-wave A window reserved jumps, "',
 '            "first-clean hops=1, non-rotational r587 forward-monotone "',
 '            "walk; B base == own-wave A tail+1 machine-checkable)")',
 f"        arith_b238 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b237 & reg_ints), \\",
 '            "W238 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
 "        assert not (arith_b238 & arith_a238), \\",
 '            "W238 A/B same-freeze mutual exclusion (B hops past own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W238-SHARD-0\",",
 '                                          "n1w238-0of12"), "W238 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W238-SHARD-11",',
 '                                           "n1w238-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w238\") and OUT.endswith(",
 '            "n1_w238_results.json"), "W238 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 238):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W238 shard dir collides with W{wprev}"',
 "        # W238 finalize cumulative deps: W17..W237 outputs ALL PRESENT",
 f"        # (landed net chain head {w237_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 238):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W238 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 238 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W237 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 238) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 238)], \\",
 '            "W238 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W237 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W238_PREREG.md")), \\',
 '            "W238 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w232_leg) + EOL + EOL.join(w233_leg) + EOL + EOL.join(w234_leg) + EOL + EOL.join(w235_leg) + EOL + EOL.join(w236_leg) + EOL + EOL.join(w237_leg) + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (carried forward): the new
# block's LHS w<237> / RHS range(16,237)+range(17,237) / comment below-237 MUST move together.
assert block.count("if w < 238)") == 3, f"family-6 triple: w<238 count {block.count('if w < 238)')} != 3"
assert block.count("if w < 237)") == 0, "family-6 triple: stale w<237 leaked into the W238 block"
assert block.count("range(16, 238)") == 1 and block.count("range(17, 238)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 238 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W238 materializer face [same guard set, dep=W17..W237 "',
 f'          "outputs ALL PRESENT (landed net chain head {w237_total} = W237 bm-c finalize one-pass, K={w237_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND THIRTY-EIGHTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-a\'s one hundred and twenty-second owned claim per "',
 '          "machine-derive (engine_owner==bm-a rows 121 + candidate; OWN-SEAT face: seat published by bm-a itself, "',
 '          "probe leg0 owner_rows=226 / bma_ordinal=122 = seat-time pre-splice faces disclosed honest, "',
 '          "live derive at freeze governs), "',
 '          "A=FIRST-CLEAN past the registered W237 B band (staircase "',
 '          "NINETY-EIGHTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
 '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
 '          "mutual exclusion, hops=1), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w238bma_20261014_probe_receipt.json, law sec.4 W238 row, "',
 '          "bm-a loop CEO fill-order RE-ISSUE 23:1x] "',
]

old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W238"') == 1
assert n1_t4.count("# --- W238 materializer face") == 1     # block header
assert n1_t4.count('"+ W238 materializer face') == 1        # print fragment
assert n1_t4.count('238: {"batch": "PERPETUAL-N1-W238"') == 1
assert pf_t2.count(ROW_I + '238: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-a"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W238-SHARD-0"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[237] == {{"a": ({fmt(pf_mod.N1_BANDS[237]["a"][0])}, {fmt(pf_mod.N1_BANDS[237]["a"][1])}),') == 1
# the W236 leg now lives in BOTH the kept W237 block and the new W238 block (2);
# the W235 leg lives in the kept W236 + kept W237 + new W238 blocks (3); the
# W232/W233/W234 legs likewise exist in multiple kept blocks
assert n1_t4.count(f'assert pf.N1_BANDS[236] == {{"a": ({fmt(pf_mod.N1_BANDS[236]["a"][0])}, {fmt(pf_mod.N1_BANDS[236]["a"][1])}),') == 2
assert n1_t4.count(f'assert pf.N1_BANDS[235] == {{"a": ({fmt(pf_mod.N1_BANDS[235]["a"][0])}, {fmt(pf_mod.N1_BANDS[235]["a"][1])}),') == 3
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
  "machine": "bm-a", "wave": 238,
  "phase": "five-face freeze chain-order splice (bm-a own-seat freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w238bma_20261014_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "w237_upstream": {"freeze_sha": w237_freeze_sha, "prereg_sha": w237_prereg_sha,
                    "ledger_total": w237_total, "merged_n": w237_merged_n,
                    "engine_owner": "bm-c (upstream seat honored)",
                    "repair_chain_note": "W237 bm-c own-wave closeout r990 (five-face splice e4a23cc7a + engine self-burn 12/12 + finalize one-pass + five-key ALL PASS + sec78 backfill; six-gate PRE-FINALIZE correct phase -- standing law held)"},
  "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                    "inherited": False,
                    "note": "seat published=reserved by bm-a itself (MSG-20261014-0745-bma-w238-seat pushed to origin 3e551d846 r976 BEFORE this freeze per r565 law); zero takeover -- wave 238 engine_owner=bm-a, bm-a's 122nd own wave per live derive (probe leg0 owner_rows=226 / bma_ordinal=122 = seat-time pre-splice faces disclosed honest, live derive governs r587/r359; freeze-time live face owner rows 227 + candidate = 228th EXACT)"},
  "w236_transitive": {"finalize_product": "results/perpetual_faces/n1_w236_results.json present (belt-and-braces gate; ledger 942,989 / K=517,120)"},
  "w235_transitive": {"finalize_product": "results/perpetual_faces/n1_w235_results.json present (belt-and-braces gate; ledger 940,789 / K=514,920)"},
  "w234_transitive": {"finalize_product": "results/perpetual_faces/n1_w234_results.json present (belt-and-braces gate; ledger 938,589 / K=512,720)"},
  "w233_transitive": {"finalize_product": "results/perpetual_faces/n1_w233_results.json present (belt-and-braces gate; ledger 936,389 / K=510,520)"},
  "w232_transitive": {"finalize_product": "results/perpetual_faces/n1_w232_results.json present (belt-and-braces gate; ledger 934,189 / K=508,320)"},
  "w231_transitive": {"finalize_product": "results/perpetual_faces/n1_w231_results.json present (belt-and-braces gate)"},
  "w230_transitive": {"finalize_product": "results/perpetual_faces/n1_w230_results.json present (belt-and-braces gate)"},
  "w225_transitive": {"finalize_product": "results/perpetual_faces/n1_w225_results.json present (belt-and-braces gate; ledger 918,789 / K=492,920)"},
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w238_prereg_sha, "probe_receipt_sha": w238_receipt_sha,
                    "note": "prereg derived+committed by the bm-a r983 window (own-seat derive landed pre-freeze, on origin via the r983 push; zero takeover; freeze-time live derive bma rows 121 + candidate 122nd EXACT per r587/r359); splice editor derived from the committed W237 editor template by count-asserted ordered transform in this same freeze window; upstream W237 already landed (clean-precondition twenty-seventh consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bma_rows_live": len(bma_rows_live),
                    "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bma_own_ordinal": len(bma_rows_live) + 1,
                    "probe_receipt_bma_ordinal_face": 122,
                    "note": "post-W237 registration: bm-a rows 121 + candidate = 122nd owned (live derive at freeze time governs per r587/r359; probe leg0 owner_rows=226 / bma_ordinal=122 = seat-time pre-splice faces -- zero takeover, own-seat continuity)"},
  "parity_section": {"source": "OWN W237 block physical bytes (bm-c own splice generation, structure known exactly)",
                    "bytes": len(par_sec),
                    "row_asserts": par_sec.count("assert pf.N1_BANDS["),
                    "note": "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W231 legs -> W238 block = 96 rows ending at W237 (estate 90 + fresh W232 leg + W233 leg + W234 leg + W235 leg + W236 leg + W237 leg); disclosed: (a) inherited W213 leg error-string face (\"registered W212 row parity drift\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) W237 block's band-set variable one-behind naming face (w236_a holds wave-237 bands) = lineage mechanical aging face -- W238 block follows the same pattern (w237_a holds wave-238 bands), zero functional impact"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W237 editor family-6 gate carried forward: new block LHS w<238 x3 / RHS range(16,238)+range(17,238) / comment below-238 count-asserted ATOMICALLY before splice; W237 block's own w<237 face = legitimate prior-wave boundary (not stale)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1, "w223_block_kept": 1, "w224_block_kept": 1, "w225_block_kept": 1, "w226_block_kept": 1, "w227_block_kept": 1, "w228_block_kept": 1, "w229_block_kept": 1, "w230_block_kept": 1, "w231_block_kept": 1, "w232_block_kept": 1, "w233_block_kept": 1, "w234_block_kept": 1, "w235_block_kept": 1, "w236_block_kept": 1, "w237_block_kept": 1},
}

open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w237_upstream", "own_seat_face")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> engine self-ignite W238 burn (12 shards) -> PRE-FINALIZE six-gate (standing law) -> finalize one-pass")
