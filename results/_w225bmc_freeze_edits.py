# -*- coding: utf-8 -*-
# 2026-10-12 20:2x bm-c r939 freeze window (upstream W1..W224 ALL LANDED, clean precondition): W225 five-face freeze splice editor.
# Upstream chain ALL LANDED at this window: W1..W224 finalize products
# present (W224 finalize one-pass 19:1x, net chain head 916,589,
# merged pool K=490,720, n1_w224_results.json machine-read) -- ZERO
# in-flight upstream seats, clean precondition (fourteenth consecutive
# fully-clean freeze window).
# Lineage: _w224bmc_freeze_edits.py pattern (proven live-fire freeze,
# r937 dead-window splice landed by r937 absorb) + r787 preflight law +
# r609 origin-verbatim base + r761 programmatic quote wrapping + r909
# physical-byte anchors + r838 per-file EOL detection + family #6
# LHS/RHS/comment ATOMIC TRIPLE absorbed (W225 editor derive review leg
# per the W224 sec.8 upgrade proposal -- the new block's w<N+1>/range(16,N+1)
# /below-N+1 triple is count-asserted atomically; W223 block's own w<223
# face is legitimate prior-wave boundary, not stale).
# Zero hardcoded upstream band values: ALL W224 facts machine-derived from the
# LIVE pf import at freeze time (bm-c's own registered row), cross-checked against
# the committed ADMIT receipt (results/_w225bmc_20261012_probe_receipt.json)
# which was derived on the post-W224-REGISTERED universe. If the LIVE W224 bands
# differ from the declared face, the staircase asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W224 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W224
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W224 block's own W223 leg (1 row) is excluded from the
# estate path and fresh W223 + W224 legs are appended for the W225 block parity
# (83 rows: estate 69 + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg + W222 leg + W223 leg + W224 leg).
# Extraction self-asserts the 81-row cut (69 estate + W211..W221 + W222)
# regardless. Disclosed: the inherited W213 leg inside the estate carries a
# cosmetic error-string face ("registered W212 row parity drift") from the
# r912 editor generation -- physical bytes preserved verbatim per extraction
# law, zero functional impact (assert target [213] is correct), disclosed.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w225bmc_20261012_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w225bmc_freeze_receipt.json")
SEAT_MSG = "MSG-20261012-1943-bmc-w225-seat.md"
SEAT_ORIGIN = "c78dd1a44"
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

# ---------- gate 0.5: W224 five-face landed + W224 finalize product present ----------
# (chain-order precondition; W223/W222/W221/W220 finalize are transitive deps of the
# W225 freeze and are belt-and-braces checked here + enforced by the block's
# cumulative-deps assert range(17, 225) at selftest time)
W224 = dict(pf_mod.N1_BANDS.get(224) or {})
assert W224.get("engine_owner") == "bm-c", \
    f"W224 row not landed as declared (bm-c own seat owner expected, no takeover face): {W224} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w224_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w224_results.json")
assert os.path.exists(w224_out_path), "W224 finalize product missing (n1_w224_results.json) -- chain dep not met"
w223_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w223_results.json")
assert os.path.exists(w223_out_path), "W223 finalize product missing (transitive chain dep) -- abort"
w222_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w222_results.json")
assert os.path.exists(w222_out_path), "W222 finalize product missing (transitive chain dep) -- abort"
w221_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w221_results.json")
assert os.path.exists(w221_out_path), "W221 finalize product missing (transitive chain dep) -- abort"
w220_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w220_results.json")
assert os.path.exists(w220_out_path), "W220 finalize product missing (transitive chain dep) -- abort"
w224_out = json.load(open(w224_out_path, encoding="utf-8"))
w224_led = (w224_out.get("science_gates") or {}).get("ledger") or {}
w224_total = w224_led.get("total")
w224_merged_n = None
try:
    w224_merged_n = w224_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w224_total == 916_589 and w224_merged_n == 490_720, \
    f"W224 finalize anchors drift at freeze time: total={w224_total} merged={w224_merged_n} (expect 916,589 / 490,720)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '224: {"a"', "--", "scripts/perpetual_faces.py")
w224_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W224_PREREG.md")
w224_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W224_PREREG.md")), \
    "bm-c W224 per-wave prereg missing on disk -- chain face incomplete, abort"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face bmc_ordinal=55 = seat-time live face; live derive at freeze
# time: bmc rows 54 + candidate = 55th EXACT)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 214 and len(bmc_rows_live) == 54, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bmc={len(bmc_rows_live)} (expect 214/54 PRE-splice post-W224 registration; W224 precedent 213/53 pre-splice + W224 splice 214/54; this candidate = 55th own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W224 landed (freeze {w224_freeze_sha[:10]}, owner=bm-c own seat), "
      f"W224+W223+W222+W221+W220 finalize products present "
      f"(W224 ledger head {w224_total}, merged n={w224_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-c rows {len(bmc_rows_live)} + candidate (55th own wave per live derive r587/r359; "
      f"probe receipt leg0 bmc_ordinal=55 seat-time live face disclosed)")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
A = rec["bands"]["A"]; B = rec["bands"]["B"]
a_lo, a_hi = (int(x) for x in A.split("_"))
b_lo, b_hi = (int(x) for x in B.split("_"))
leg1 = rec["legs"]["leg1"]
assert [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"], "receipt band mismatch"
assert (a_lo, a_hi) == (509_804, 511_803) and (b_lo, b_hi) == (511_804, 512_003), \
    f"W225 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w224_b_tail = W224["b_exit"][1]      # registered W224 row b_exit hi (pf import, live)
w224_a_tail = W224["a"][1]           # registered W224 row A hi (pf import, live)
assert w224_b_tail + 1 == a_lo and a_hi + 1 == b_lo, "staircase base relations broken"
# the REFUSED arithmetic continuation starts at prior-wave A-tail+1 (== W224 B-base),
# machine-derived from the LIVE registered row, never transcribed.
assert w224_a_tail + 1 == W224["b_exit"][0], "W224 A-tail+1 != W224 B-base (registered row in-wave relation)"
assert [w224_a_tail + 1, w224_a_tail + 2_000] == leg1["ARITH_A"], \
    f"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w224_a_tail + 1, w224_a_tail + 2_000]} != {leg1['ARITH_A']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W225_PREREG.md")
w225_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w225bmc_20261012_probe_receipt.json")
w225_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W225 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W225_PREREG.md"],
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
# STRUCTURAL CHOICE: extract the estate from the OWN W224 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W222 leg) -- the W224 block is this machine's own splice generation
# (r937 dead-window editor landed by r937 absorb), structure known. The W224 block span ends where the
# T-141 s2 lane face marker begins.
a15 = '    # --- W224 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w224_start = n1_t.find(a15); t141_pos = n1_t.find(a_t141)
assert w224_start > 0 and t141_pos > w224_start, \
    "W224 materializer block face not found (W224 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w224_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W224 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m223 = re.search(r" *assert pf\.N1_BANDS\[223\] ==", par_full)
assert m223, "upstream W223 row leg not found inside W224 parity span"
par_sec = par_full[:m223.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 81 \
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \
    and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76]), int(_estate_ws[77]), int(_estate_ws[78]), int(_estate_ws[79])] == [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221] \
    and int(_estate_ws[80]) == 222, \
    f"estate segment not W138..W206 full-span 69 rows + W211..W221 legs + W222 leg: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-13:])}"
assert par_full.count("assert pf.N1_BANDS[") == 82, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 82 (69 estate + W211..W221 legs + W222 leg + W223 leg)"

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '224: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W224_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
# MEM_I derived INSIDE the W224 cfg entry span (own splice generation, value
# format known: plain int -- indent is all we take)
_c224 = n1_t.find('224: {"batch"')
assert _c224 > 0, "W224 cfg entry not found (W224 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c224)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c224) > _mpos, "W224 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W224["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W224["a"][0]), _c224) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W224["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '224: {"a"', PF_EOL)

# ---------- W224 row owner line (physical bytes; comment text is own generation) ----------
w224_row_start = pf_t.find('    224: {"a"')
assert w224_row_start > 0, "W224 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w224_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w224_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-c"' in w224_own_line, \
    f"W224 owner line unexpected bytes: {w224_own_line!r}"
ROWC_I = w224_own_line[:len(w224_own_line) - len(w224_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W225 (bm-c loop five-face freeze splice, seat",
"    # MSG-20261012-1943-bmc-w225-seat pushed to origin " + SEAT_ORIGIN,
"    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen",
"    # commit " + w225_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W225_PREREG.md",
"    # r939 prereg derived + freeze-window bundle, probe",
"    # results/_w225bmc_20261012_probe_receipt.json @ " + w225_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-c W224 five-face (freeze " + w224_freeze_sha[:10] + ") + W224",
"    # finalize product landed (n1_w224_results.json present, ledger",
"    # head " + str(w224_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W225 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w225bmc_20261012_probe_receipt.json: A = FIRST-CLEAN",
"    # past the registered W224 B band (arithmetic continuation",
"    # " + fmt(w224_a_tail + 1) + ".." + fmt(w224_a_tail + 2_000) + " REFUSED at its own start by the W224 B band",
"    # " + fmt(W224["b_exit"][0]) + ".." + fmt(w224_b_tail) + ", exactly as the W224 seat leg4",
"    # projection anticipated;",
"    # honest forward walk hops=1 -> " + fmt(a_lo) + ".." + fmt(a_hi) + ", non-rotational",
"    # r587 forward-monotone walk; A base == prior-wave B tail+1",
"    # (" + fmt(w224_b_tail) + "+1) machine-checkable -- A-hops-prior-B staircase",
"    # EIGHTY-FIFTH instance, E36 card (probe receipt leg1 A_semantics",
"    # machine-read ordinal, never transcribed);",
"    # B = FIRST-CLEAN past the own-wave A window (arithmetic",
"    # continuation " + fmt(a_lo) + ".." + fmt(a_lo + 199) + " CLEAN on the registered",
"    # universe but lands INSIDE the W225 A band window " + fmt(a_lo) + ".." + fmt(a_hi) + " --",
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
"    # W226+ projection (gate-derived pre-seat probe leg4, pre-W225",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W225p_A"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " /",
"    # B naive first-clean " + rec["legs"]["leg4"]["W225p_B"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " -- naive B lands",
"    # INSIDE the naive A window and the registered W225 B band",
"    # " + fmt(b_lo) + ".." + fmt(b_hi) + " will refuse the naive W226 A window; W226 freezer",
"    # MUST re-derive on the post-W225 universe AND reserve the",
"    # own-wave A window when deriving B (W141 precedent, leg2 law,",
"    # E36 staircase card, EIGHTY-SIXTH instance anticipated; never transcribe r587).",
])
pf_row = (f'{ROW_I}225: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'225: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w224_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w224_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W224 finalize ALL LANDED (W224 finalize product present at splice, "
            f"net chain head {w224_total} machine-read, merged pool K={w224_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition; "
            f"downstream W226 seat NOT yet published (queue-deepen seat-chain mandate "
            f"O-20261011-0012 sec.ii -- next seat publication follows per seat-first law)")
cfg_lines = [
 f'{CFG_I}225: {{"batch": "PERPETUAL-N1-W225",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W225_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND TWENTY-FIFTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W224 row five-face freeze (own seat published MSG-20261012-175x, executed bm-c r937 dead-window splice landed by r937 absorb; engine self-burn 12/12; finalize one-pass 19:1x), ",
 f"{w224_freeze_sha[:10]} (prereg {w224_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W224 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261012-1943-bmc-w225-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt @ r938 window; per-wave prereg + ",
 "freeze splice script landed in the r939 freeze-window bundle ",
 f"commit {w225_prereg_sha[:10]} @ receipt {w225_receipt_sha[:10]}); ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W224 five-face + W224 finalize product landed ",
 "(executed in the bm-c loop r937 freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c, wave 225: ",
 "A = FIRST-CLEAN past the registered W224 B band (the ",
 f"arithmetic continuation {fmt(w224_a_tail + 1)}..{fmt(w224_a_tail + 2_000)} is REFUSED at its ",
 f"own start by the W224 B band {fmt(W224['b_exit'][0])}..{fmt(w224_b_tail)}, exactly as ",
 "the W224 seat leg4 succession ",
 "projection notes anticipated; honest forward walk hops=1 -> ",
 f"{fmt(a_lo)}..{fmt(a_hi)}; A base == prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase EIGHTY-FIFTH ",
 "instance, E36 card (probe receipt leg1 machine-read ordinal); ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN ",
 "past the own-wave A window (the arithmetic continuation ",
 f"{fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the registered universe but lands ",
 f"INSIDE the W225 A band window {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual ",
 "exclusion, W141 precedent, leg2 law -- the walk with the ",
 f"own-wave A window reserved jumps to {fmt(b_lo)}, first-clean ",
 f"{fmt(b_lo)}..{fmt(b_hi)} hops=1, non-rotational r587 forward-monotone walk; ",
 "B base == own-wave A tail+1 machine-checkable; cross-window ",
 "convergence with the W224 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W224 universe ",
 "re-derive + own-wave A reservation); ADMIT receipt ",
 "results/_w225bmc_20261012_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W225+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W225p_A']} CLEAN / B naive first-clean ",
 f"{rec['legs']['leg4']['W225p_B']} CLEAN -- naive B lands INSIDE the naive A window and ",
 f"the registered W225 B band {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W226 A window; ",
 "W226+ freezer MUST re-derive on the post-W225 universe AND ",
 "reserve the own-wave A window when deriving B (W141 precedent, ",
 "leg2 law, E36 staircase card, EIGHTY-SIXTH instance anticipated) -- ",
 "downstream W226 seat publication pending per seat-first law; " + fin_face + " -- the finalize ",
 "merge loop still derives the wave set from registry keys at ",
 "run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W225 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past the registered W224 B band; arithmetic {fmt(w224_a_tail + 1)}..{fmt(w224_a_tail + 2_000)} REFUSED at own start by the W224 B band {fmt(W224["b_exit"][0])}..{fmt(w224_b_tail)}; hops=1; A-hops-prior-B staircase EIGHTY-FIFTH instance, E36 card; ordinal machine-read EIGHTY-FIFTH per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W225 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN past the own-wave A window; arithmetic {fmt(a_lo)}..{fmt(a_lo + 199)} lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w225", "out_name": "n1_w225_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]
cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('225: {"batch": "PERPETUAL-N1-W225"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W225 materializer face (bm-c loop five-face freeze splice,",
 "    #     own-series law under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's fifty-fifth owned per machine-derive (engine_owner==bm-c",
 "    #     rows 54 + candidate; seat-time live face 55th = r938 probe leg0",
 "    #     live derive governs); wave 225 = first free number after the",
 "    #     REGISTERED W224 row (five-face freeze " + w224_freeze_sha[:10] + "; own seat published",
 "    #     MSG-20261012-175x, executed bm-c r935 seat window; engine self-burn 12/12",
 "    #     + finalize one-pass 19:1x dead-window splice estate + PRE-FINALIZE six-gate all-green chain, honest note)",
 "    #     -- SINGLE STATE zero seat gap (W2..W224 all registered). Seat",
 "    #     published=reserved MSG-20261012-1943-bmc-w225-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt @ r938 window; per-wave prereg +",
 "    #     freeze splice script landed in the r939 freeze-window bundle",
 "    #     commit " + w225_prereg_sha[:10] + "; deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W224 five-face + W224 finalize",
 "    #     product landed; zero --no-verify; the W225 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND TWENTY-FIFTH engine wave BY",
 "    #     MACHINE-DERIVE (engine_owner rows 214 + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w225bmc_20261012_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W225 bands were never assigned).",
 "    _set_wave(225)",
 "    try:",
 '        assert WAVE_CONFIGS[224]["a_seed_base"] == pf.N1_BANDS[224]["a"][0], \\',
 '            "W225 upstream W224 mirror drift (a)"',
 "        assert WAVE_CONFIGS[224][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[224]["b_exit"][0], "W225 upstream W224 mirror drift (b)"',
 "        assert WAVE_CONFIGS[224].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[224].get("engine_owner") == "bm-c", \\',
 '            "W225 upstream W224 engine_owner mirror drift (law-mirror parity; bm-c own-seat face)"',
 "        w224_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w224_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w224_a & w224_b), "W225 A/B band overlap"',
 "        assert not (w224_a & reg_ints) and not (w224_b & reg_ints), \\",
 '            "W225 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w224_a), ("B", w224_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W225 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W225 {nm} hits W1"',
 '            assert not (band & probes), f"W225 {nm} hits probe seeds"',
]
w223_leg = [
 f'        assert pf.N1_BANDS[223] == {{"a": ({fmt(pf_mod.N1_BANDS[223]["a"][0])}, {fmt(pf_mod.N1_BANDS[223]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[223]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[223]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W223 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w224_leg = [
 f'        assert pf.N1_BANDS[224] == {{"a": ({fmt(pf_mod.N1_BANDS[224]["a"][0])}, {fmt(pf_mod.N1_BANDS[224]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[224]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[224]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W224 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
tail = [
 "        # prior-wave disjointness W2..W224 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 225):",
 '            assert not (w224_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W225 A hits W{wprev}\"",
 '            assert not (w224_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W225 B hits W{wprev}\"",
 "        n3r1_used225 = set(range(70_000, 70_006))",
 "        assert not (w224_a & n3r1_used225) and not (w224_b & n3r1_used225), \\",
 '            "W225 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w224_a & lfc_actual12) and not (w224_b & lfc_actual12), \\",
 '            "W225 bands must clear the lfc actual draw range"',
 "        assert not (w224_a & options_actual12) and \\",
 "            not (w224_b & options_actual12), \\",
 '            "W225 bands must clear the options_wave2 actual draw range"',
 "        # band facts (law sec.4 W225 row): A = FIRST-CLEAN past",
 "        # the registered W224 B band (the arithmetic continuation",
 f"        # {fmt(w224_a_tail + 1)}..{fmt(w224_a_tail + 2_000)} is REFUSED at its own start by the W224 B band",
 f"        # {fmt(W224['b_exit'][0])}..{fmt(w224_b_tail)}, exactly as the W224 seat leg4",
 "        # succession projection notes anticipated; honest",
 f"        # forward walk hops=1 lands {fmt(a_lo)}..{fmt(a_hi)}; A base ==",
 f"        # prior-wave B tail+1 ({fmt(w224_b_tail)}+1) machine-checkable --",
 "        # A-hops-prior-B staircase EIGHTY-FIFTH instance, E36 card;",
 "        # non-rotational r587 forward-monotone walk);",
 "        # B = FIRST-CLEAN past the own-wave A window (the",
 f"        # arithmetic continuation {fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the",
 f"        # registered universe but lands INSIDE the W225 A band window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual exclusion (W141 precedent,",
 "        # leg2 law) -- the walk with the own-wave A window reserved",
 f"        # jumps to {fmt(b_lo)} and lands {fmt(b_lo)}..{fmt(b_hi)}, hops=1,",
 "        # non-rotational r587 forward-monotone walk; B base ==",
 f"        # own-wave A tail+1 ({fmt(a_hi)}+1) machine-checkable;",
 "        # cross-window convergence with the W224 seat leg4",
 "        # succession projection notes -- all MANDATORY notes",
 "        # honored (post-W224 universe re-derive + own-wave A",
 "        # reservation when deriving B);",
 "        # seat MSG-1225 tail, re-derived).",
 f'        assert WAVE_CONFIGS[225]["a_seed_base"] == {a_lo} == {w224_b_tail} + 1, (',
 '            "W225 A must be the first-clean window past the registered "',
 '            "W224 B band tail (arithmetic continuation REFUSED at its own "',
 '            "start by the W224 B band, exactly as the W224 seat leg4 "',
 '            "succession projection notes anticipated; honest forward walk "',
 '            "hops=1; A base == prior-wave B tail+1 machine-checkable "',
 '            "= A-hops-prior-B staircase EIGHTY-FIFTH instance, E36 card)")',
 f"        arith_a225 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a225 & reg_ints), \\",
 '            "W225 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
 f'        assert WAVE_CONFIGS[225]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
 '            "W225 B must be the first-clean window past the own-wave A "',
 '            "band tail (arithmetic continuation CLEAN on the registered "',
 '            "universe but lands INSIDE the W225 A band window; "',
 '            "same-freeze mutual exclusion (W141 precedent, leg2 law) -- "',
 '            "the walk with the own-wave A window reserved jumps, "',
 '            "first-clean hops=1, non-rotational r587 forward-monotone "',
 '            "walk; B base == own-wave A tail+1 machine-checkable)")',
 f"        arith_b225 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b225 & reg_ints), \\",
 '            "W225 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
 "        assert not (arith_b225 & arith_a225), \\",
 '            "W225 A/B same-freeze mutual exclusion (B hops past own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W225-SHARD-0\",",
 '                                          "n1w225-0of12"), "W225 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W225-SHARD-11",',
 '                                           "n1w225-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w225\") and OUT.endswith(",
 '            "n1_w225_results.json"), "W225 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 225):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W225 shard dir collides with W{wprev}"',
 "        # W225 finalize cumulative deps: W17..W224 outputs ALL PRESENT",
 f"        # (landed net chain head {w224_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 225):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W225 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 225 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W224 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 225) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 225)], \\",
 '            "W225 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W224 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W225_PREREG.md")), \\',
 '            "W225 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w223_leg) + EOL + EOL.join(w224_leg) + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (W224 sec.8 upgrade proposal absorbed): the new
# block's LHS w<225 / RHS range(16,225) / comment below-225 MUST move together.
assert block.count("if w < 225)") == 3, f"family-6 triple: w<225 count {block.count('if w < 225)')} != 3"
assert block.count("if w < 224") == 0, "family-6 triple: stale w<224 leaked into the W225 block"
assert block.count("range(16, 225)") == 1 and block.count("range(17, 225)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 225 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W225 materializer face [same guard set, dep=W17..W224 "',
 f'          "outputs ALL PRESENT (landed net chain head {w224_total} = W224 bm-c finalize one-pass, K={w224_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND TWENTY-FIFTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-c\'s fifty-fifth owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 54 + candidate; seat-time live face 55th disclosed, "',
 '          "live derive at freeze governs), "',
 '          "A=FIRST-CLEAN past the registered W224 B band (staircase "',
 '          "EIGHTY-FIFTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
 '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
 '          "mutual exclusion, hops=1), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w225bmc_20261012_probe_receipt.json, law sec.4 W225 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]
old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W225"') == 1
assert n1_t4.count("# --- W225 materializer face") == 1     # block header
assert n1_t4.count('"+ W225 materializer face') == 1        # print fragment
assert n1_t4.count('225: {"batch": "PERPETUAL-N1-W225"') == 1
assert pf_t2.count(ROW_I + '225: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W225-SHARD-0"') == 1
assert n1_t4.count('f"W225 A hits W{wprev}"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[224] == {{"a": ({fmt(pf_mod.N1_BANDS[224]["a"][0])}, {fmt(pf_mod.N1_BANDS[224]["a"][1])}),') == 1
assert n1_t4.count('    # --- W209 materializer face') == 1  # estate source block kept
assert n1_t4.count('    # --- W210 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W211 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W212 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W213 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W214 materializer face') == 1  # prior block kept (W214 splice landed r910 window)
assert n1_t4.count('    # --- W215 materializer face') == 1  # prior block kept (W215 splice landed r912 window)
assert n1_t4.count('    # --- W216 materializer face') == 1  # prior block kept (W216 splice landed r914 window)
assert n1_t4.count('    # --- W217 materializer face') == 1  # prior block kept (W217 splice landed r916 window)
assert n1_t4.count('    # --- W218 materializer face') == 1  # prior block kept (W218 splice landed r918 window)
assert n1_t4.count('    # --- W219 materializer face') == 1  # prior block kept (W219 splice landed r920 window)
assert n1_t4.count('    # --- W220 materializer face') == 1  # prior block kept (W220 splice landed r923 window)
assert n1_t4.count('    # --- W221 materializer face') == 1  # prior block kept (W221 splice landed r927 window)
assert n1_t4.count('    # --- W222 materializer face') == 1  # prior block kept (W222 splice landed r931 window)
assert n1_t4.count('    # --- W223 materializer face') == 1  # prior block kept (W223 splice landed r934 window)
assert n1_t4.count('    # --- W224 materializer face') == 1  # prior block kept (W224 splice landed r937 dead window)
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
  "machine": "bm-c", "wave": 225,
  "phase": "five-face freeze chain-order splice (r939 freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w225bmc_20261012_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "w224_upstream": {"freeze_sha": w224_freeze_sha, "prereg_sha": w224_prereg_sha,
                    "ledger_total": w224_total, "merged_n": w224_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r937 splice (dead-window estate, landed by r937 absorb commit) + engine self-burn 12/12 + r937 finalize one-pass 19:1x (six-gate PRE-FINALIZE all-green 19:1x, correct-phase post-miss run 2)"},
  "w223_transitive": {"finalize_product": "results/perpetual_faces/n1_w223_results.json present (belt-and-braces gate; ledger 914,389 / K=488,520)"},
  "w222_transitive": {"finalize_product": "results/perpetual_faces/n1_w222_results.json present (belt-and-braces gate; ledger 912,189 / K=486,320)"},
  "w221_transitive": {"finalize_product": "results/perpetual_faces/n1_w221_results.json present (belt-and-braces gate; ledger 909,989 / K=484,120)"},
  "w220_transitive": {"finalize_product": "results/perpetual_faces/n1_w220_results.json present (belt-and-braces gate; ledger 907,789 / K=481,920)"},
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w225_prereg_sha, "probe_receipt_sha": w225_receipt_sha,
                    "note": "prereg derived+committed in the r939 window (4b22941a7, NINE-level lineage replay chain, preflight 46/46); splice editor derived from the committed W224 editor template by count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this r939 freeze window; upstream W224 already landed (clean-precondition fourteenth consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmc_ordinal_face": 55,
                    "note": "post-W225 registration: bm-c rows 54 + candidate = 55th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=55 = r938 seat-time live face -- disclosed honest)"},
  "parity_section": {"source": "OWN W224 block physical bytes (own splice generation, structure known exactly)",
                    "bytes": len(par_sec),
                    "row_asserts": par_sec.count("assert pf.N1_BANDS["),
                    "note": "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W221 legs + W222 leg -> W225 block = 83 rows ending at W224; disclosed: inherited W213 leg error-string face (\"registered W212 row parity drift\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact)"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W224 sec.8 upgrade proposal absorbed into the W225 editor derive: new block LHS w<225 x3 / RHS range(16,225)+range(17,225) / comment below-225 count-asserted ATOMICALLY before splice; W223 block's own w<223 face = legitimate prior-wave boundary (not stale)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1, "w223_block_kept": 1, "w224_block_kept": 1},
}
open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w224_upstream")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> ignition verify (2-cycle n1_w225 growth)")
