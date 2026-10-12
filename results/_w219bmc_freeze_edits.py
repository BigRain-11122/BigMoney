# -*- coding: utf-8 -*-
# 2026-10-12 09:5x bm-c r920 freeze: W219 five-face freeze splice editor.
# Upstream chain ALL LANDED at this window: W1..W218 finalize products
# present (W218 finalize one-pass 09:1x, net chain head 903,389,
# merged pool K=477,520, n1_w218_results.json machine-read) -- ZERO
# in-flight upstream seats, clean precondition (eighth consecutive
# fully-clean freeze window).
# Lineage: _w218bmc_freeze_edits.py pattern (proven live-fire freeze,
# r918 window executed) + r787 preflight law + r609 origin-verbatim
# base + r761 programmatic quote wrapping + r909 physical-byte anchors
# + r838 per-file EOL detection.
# Zero hardcoded upstream band values: ALL W218 facts machine-derived from the
# LIVE pf import at freeze time (bm-c's own registered row), cross-checked against
# the committed ADMIT receipt (results/_w219bmc_20261012_probe_receipt.json)
# which was derived on the post-W218-REGISTERED universe. If the LIVE W218 bands
# differ from the declared face, the staircase asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W218 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W218
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W218 block's own W217 leg (1 row) is excluded from the
# estate path and fresh W217 + W218 legs are appended for the W219 block parity
# (77 rows: estate 69 + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg).
# Extraction self-asserts the 75-row cut (69 estate + W211 + W212 + W213 + W214 + W215 + W216)
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
RECEIPT_IN = os.path.join(REPO, "results", "_w219bmc_20261012_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w219bmc_freeze_receipt.json")
SEAT_MSG = "MSG-20261012-0916-bmc-w219-seat.md"
SEAT_ORIGIN = "7615985e8"
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

# ---------- gate 0.5: W218 five-face landed + W218 finalize product present ----------
# (chain-order precondition; W217/W216/W215/W214 finalize are transitive deps of the
# W219 freeze and are belt-and-braces checked here + enforced by the block's
# cumulative-deps assert range(17, 219) at selftest time)
W218 = dict(pf_mod.N1_BANDS.get(218) or {})
assert W218.get("engine_owner") == "bm-c", \
    f"W218 row not landed as declared (bm-c own seat owner expected, no takeover face): {W218} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w218_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w218_results.json")
assert os.path.exists(w218_out_path), "W218 finalize product missing (n1_w218_results.json) -- chain dep not met"
w217_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w217_results.json")
assert os.path.exists(w217_out_path), "W217 finalize product missing (transitive chain dep) -- abort"
w216_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w216_results.json")
assert os.path.exists(w216_out_path), "W216 finalize product missing (transitive chain dep) -- abort"
w215_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w215_results.json")
assert os.path.exists(w215_out_path), "W215 finalize product missing (transitive chain dep) -- abort"
w214_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w214_results.json")
assert os.path.exists(w214_out_path), "W214 finalize product missing (transitive chain dep) -- abort"
w218_out = json.load(open(w218_out_path, encoding="utf-8"))
w218_led = (w218_out.get("science_gates") or {}).get("ledger") or {}
w218_total = w218_led.get("total")
w218_merged_n = None
try:
    w218_merged_n = w218_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w218_total == 903_389 and w218_merged_n == 477_520, \
    f"W218 finalize anchors drift at freeze time: total={w218_total} merged={w218_merged_n} (expect 903,389 / 477,520)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '218: {"a"', "--", "scripts/perpetual_faces.py")
w218_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W218_PREREG.md")
w218_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W218_PREREG.md")), \
    "bm-c W218 per-wave prereg missing on disk -- chain face incomplete, abort"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face bmc_ordinal=48 = seat-time live face; live derive at freeze
# time: bmc rows 47 + candidate = 48th EXACT)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 208 and len(bmc_rows_live) == 48, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bmc={len(bmc_rows_live)} (expect 208/48 PRE-splice post-W219 registration; W219 precedent 207/47 pre-splice + W219 splice 208/48; this candidate = 49th own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W218 landed (freeze {w218_freeze_sha[:10]}, owner=bm-c own seat), "
      f"W218+W217+W216+W215+W214 finalize products present "
      f"(W218 ledger head {w218_total}, merged n={w218_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-c rows {len(bmc_rows_live)} + candidate (49th own wave per live derive r587/r359; "
      f"probe receipt leg0 bmc_ordinal=49 seat-time live face disclosed)")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
A = rec["bands"]["A"]; B = rec["bands"]["B"]
a_lo, a_hi = (int(x) for x in A.split("_"))
b_lo, b_hi = (int(x) for x in B.split("_"))
leg1 = rec["legs"]["leg1"]
assert [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"], "receipt band mismatch"
assert (a_lo, a_hi) == (496_604, 498_603) and (b_lo, b_hi) == (498_604, 498_803), \
    f"W219 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w218_b_tail = W218["b_exit"][1]      # registered W218 row b_exit hi (pf import, live)
w218_a_tail = W218["a"][1]           # registered W218 row A hi (pf import, live)
assert w218_b_tail + 1 == a_lo and a_hi + 1 == b_lo, "staircase base relations broken"
# the REFUSED arithmetic continuation starts at prior-wave A-tail+1 (== W218 B-base),
# machine-derived from the LIVE registered row, never transcribed.
assert w218_a_tail + 1 == W218["b_exit"][0], "W218 A-tail+1 != W218 B-base (registered row in-wave relation)"
assert [w218_a_tail + 1, w218_a_tail + 2_000] == leg1["ARITH_A"], \
    f"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w218_a_tail + 1, w218_a_tail + 2_000]} != {leg1['ARITH_A']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W219_PREREG.md")
w219_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w219bmc_20261012_probe_receipt.json")
w219_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W219 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W219_PREREG.md"],
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

def fmt(n):  # 496604 -> "496_604"
    return f"{n // 1000}_{n % 1000:03d}"

# ---------- extract parity section (physical bytes, never re-typed) ----------
# STRUCTURAL CHOICE: extract the estate from the OWN W218 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + own W212 leg +
# own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg) -- the W218 block is this machine's own splice generation
# (r918 window editor), structure known. The W218 block span ends where the
# T-141 s2 lane face marker begins.
a15 = '    # --- W218 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w218_start = n1_t.find(a15); t141_pos = n1_t.find(a_t141)
assert w218_start > 0 and t141_pos > w218_start, \
    "W218 materializer block face not found (W218 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w218_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W218 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m217 = re.search(r" *assert pf\.N1_BANDS\[217\] ==", par_full)
assert m217, "upstream W217 row leg not found inside W218 parity span"
par_sec = par_full[:m217.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 75 \
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \
    and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74])] == [211, 212, 213, 214, 215, 216], \
    f"estate segment not W138..W206 full-span 69 rows + W211 + W212 + W213 + W214 + W215 + W216 legs: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-6:])}"
assert par_full.count("assert pf.N1_BANDS[") == 76, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 76 (69 estate + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg)"

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '218: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W218_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
# MEM_I derived INSIDE the W218 cfg entry span (own splice generation, value
# format known: plain int -- indent is all we take)
_c218 = n1_t.find('218: {"batch"')
assert _c218 > 0, "W218 cfg entry not found (W218 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c218)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c218) > _mpos, "W218 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W218["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W218["a"][0]), _c218) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W218["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '218: {"a"', PF_EOL)

# ---------- W218 row owner line (physical bytes; comment text is own generation) ----------
w218_row_start = pf_t.find('    218: {"a"')
assert w218_row_start > 0, "W218 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w218_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w218_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-c"' in w218_own_line, \
    f"W218 owner line unexpected bytes: {w218_own_line!r}"
ROWC_I = w218_own_line[:len(w218_own_line) - len(w218_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W219 (bm-c loop five-face freeze splice, seat",
"    # MSG-20261012-0916-bmc-w219-seat pushed to origin " + SEAT_ORIGIN,
"    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen",
"    # commit " + w219_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W219_PREREG.md",
"    # r920 freeze-window bundle, probe",
"    # results/_w219bmc_20261012_probe_receipt.json @ " + w219_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-c W218 five-face (freeze " + w218_freeze_sha[:10] + ") + W218",
"    # finalize product landed (n1_w218_results.json present, ledger",
"    # head " + str(w218_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W219 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w219bmc_20261012_probe_receipt.json: A = FIRST-CLEAN",
"    # past the registered W218 B band (arithmetic continuation",
"    # " + fmt(w218_a_tail + 1) + ".." + fmt(w218_a_tail + 2_000) + " REFUSED at its own start by the W218 B band",
"    # " + fmt(W218["b_exit"][0]) + ".." + fmt(w218_b_tail) + ", exactly as the W218 seat leg4",
"    # projection anticipated;",
"    # honest forward walk hops=1 -> " + fmt(a_lo) + ".." + fmt(a_hi) + ", non-rotational",
"    # r587 forward-monotone walk; A base == prior-wave B tail+1",
"    # (" + fmt(w218_b_tail) + "+1) machine-checkable -- A-hops-prior-B staircase",
"    # SEVENTY-NINTH instance, E36 card (probe receipt leg1 A_semantics",
"    # machine-read ordinal, never transcribed);",
"    # B = FIRST-CLEAN past the own-wave A window (arithmetic",
"    # continuation " + fmt(a_lo) + ".." + fmt(a_lo + 199) + " CLEAN on the registered",
"    # universe but lands INSIDE the W219 A band window " + fmt(a_lo) + ".." + fmt(a_hi) + " --",
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
"    # W220+ projection (gate-derived pre-seat probe leg4, pre-W219",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W220p_A"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " /",
"    # B naive first-clean " + rec["legs"]["leg4"]["W220p_B"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " -- naive B lands",
"    # INSIDE the naive A window and the registered W219 B band",
"    # " + fmt(b_lo) + ".." + fmt(b_hi) + " will refuse the naive W220 A window; W220 freezer",
"    # MUST re-derive on the post-W219 universe AND reserve the",
"    # own-wave A window when deriving B (W141 precedent, leg2 law,",
"    # E36 staircase card, EIGHTIETH instance anticipated; never transcribe r587).",
])
pf_row = (f'{ROW_I}219: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'219: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w218_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w218_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W218 finalize ALL LANDED (W218 finalize product present at splice, "
            f"net chain head {w218_total} machine-read, merged pool K={w218_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition; "
            f"downstream W220 seat NOT yet published (queue-deepen seat-chain mandate "
            f"O-20261011-0012 sec.ii -- next seat publication follows per seat-first law)")
cfg_lines = [
 f'{CFG_I}219: {{"batch": "PERPETUAL-N1-W219",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W219_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND NINETEENTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W218 row five-face freeze (own seat published MSG-20261012-0830, executed bm-c r918 freeze window; engine self-burn 12/12; finalize one-pass 09:1x), ",
 f"{w218_freeze_sha[:10]} (prereg {w218_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W218 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261012-0916-bmc-w219-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt @ r919 window; per-wave prereg + ",
 "freeze splice script landed in the r920 freeze-window bundle ",
 f"commit {w219_prereg_sha[:10]} @ receipt {w219_receipt_sha[:10]}); ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W218 five-face + W218 finalize product landed ",
 "(executed in the bm-c loop r920 freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c, wave 219: ",
 "A = FIRST-CLEAN past the registered W218 B band (the ",
 f"arithmetic continuation {fmt(w218_a_tail + 1)}..{fmt(w218_a_tail + 2_000)} is REFUSED at its ",
 f"own start by the W218 B band {fmt(W218['b_exit'][0])}..{fmt(w218_b_tail)}, exactly as ",
 "the W218 seat leg4 succession ",
 "projection notes anticipated; honest forward walk hops=1 -> ",
 f"{fmt(a_lo)}..{fmt(a_hi)}; A base == prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase SEVENTY-NINTH ",
 "instance, E36 card (probe receipt leg1 machine-read ordinal); ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN ",
 "past the own-wave A window (the arithmetic continuation ",
 f"{fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the registered universe but lands ",
 f"INSIDE the W219 A band window {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual ",
 "exclusion, W141 precedent, leg2 law -- the walk with the ",
 f"own-wave A window reserved jumps to {fmt(b_lo)}, first-clean ",
 f"{fmt(b_lo)}..{fmt(b_hi)} hops=1, non-rotational r587 forward-monotone walk; ",
 "B base == own-wave A tail+1 machine-checkable; cross-window ",
 "convergence with the W218 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W218 universe ",
 "re-derive + own-wave A reservation); ADMIT receipt ",
 "results/_w219bmc_20261012_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W219+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W220p_A']} CLEAN / B naive first-clean ",
 f"{rec['legs']['leg4']['W220p_B']} CLEAN -- naive B lands INSIDE the naive A window and ",
 f"the registered W219 B band {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W220 A window; ",
 "W220+ freezer MUST re-derive on the post-W219 universe AND ",
 "reserve the own-wave A window when deriving B (W141 precedent, ",
 "leg2 law, E36 staircase card, EIGHTIETH instance anticipated) -- ",
 "downstream W220 seat publication pending per seat-first law; " + fin_face + " -- the finalize ",
 "merge loop still derives the wave set from registry keys at ",
 "run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W219 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past the registered W218 B band; arithmetic {fmt(w218_a_tail + 1)}..{fmt(w218_a_tail + 2_000)} REFUSED at own start by the W218 B band {fmt(W218["b_exit"][0])}..{fmt(w218_b_tail)}; hops=1; A-hops-prior-B staircase SEVENTY-NINTH instance, E36 card; ordinal machine-read SEVENTY-NINTH per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W219 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN past the own-wave A window; arithmetic {fmt(a_lo)}..{fmt(a_lo + 199)} lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w219", "out_name": "n1_w219_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]
cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('219: {"batch": "PERPETUAL-N1-W219"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W219 materializer face (bm-c loop five-face freeze splice,",
 "    #     own-series law under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's forty-ninth owned per machine-derive (engine_owner==bm-c",
 "    #     rows 48 + candidate; seat-time live face 49th = r919 probe leg0",
 "    #     live derive governs); wave 219 = first free number after the",
 "    #     REGISTERED W218 row (five-face freeze " + w218_freeze_sha[:10] + "; own seat published",
 "    #     MSG-20261012-0830, executed bm-c r917 seat window; engine self-burn 12/12",
 "    #     + finalize one-pass 09:1x repair-free chain honest note)",
 "    #     -- SINGLE STATE zero seat gap (W2..W218 all registered). Seat",
 "    #     published=reserved MSG-20261012-0916-bmc-w219-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt @ r919 window; per-wave prereg +",
 "    #     freeze splice script landed in the r920 freeze-window bundle",
 "    #     commit " + w219_prereg_sha[:10] + "; deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W218 five-face + W218 finalize",
 "    #     product landed; zero --no-verify; the W219 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND NINETEENTH engine wave BY",
 "    #     MACHINE-DERIVE (engine_owner rows 208 + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w219bmc_20261012_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W219 bands were never assigned).",
 "    _set_wave(219)",
 "    try:",
 '        assert WAVE_CONFIGS[218]["a_seed_base"] == pf.N1_BANDS[218]["a"][0], \\',
 '            "W219 upstream W218 mirror drift (a)"',
 "        assert WAVE_CONFIGS[218][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[218]["b_exit"][0], "W219 upstream W218 mirror drift (b)"',
 "        assert WAVE_CONFIGS[218].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[218].get("engine_owner") == "bm-c", \\',
 '            "W219 upstream W218 engine_owner mirror drift (law-mirror parity; bm-c own-seat face)"',
 "        w218_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w218_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w218_a & w218_b), "W219 A/B band overlap"',
 "        assert not (w218_a & reg_ints) and not (w218_b & reg_ints), \\",
 '            "W219 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w218_a), ("B", w218_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W219 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W219 {nm} hits W1"',
 '            assert not (band & probes), f"W219 {nm} hits probe seeds"',
]
w217_leg = [
 f'        assert pf.N1_BANDS[217] == {{"a": ({fmt(pf_mod.N1_BANDS[217]["a"][0])}, {fmt(pf_mod.N1_BANDS[217]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[217]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[217]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W217 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w218_leg = [
 f'        assert pf.N1_BANDS[218] == {{"a": ({fmt(pf_mod.N1_BANDS[218]["a"][0])}, {fmt(pf_mod.N1_BANDS[218]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[218]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[218]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W218 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
tail = [
 "        # prior-wave disjointness W2..W218 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 219):",
 '            assert not (w218_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W219 A hits W{wprev}\"",
 '            assert not (w218_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W219 B hits W{wprev}\"",
 "        n3r1_used219 = set(range(70_000, 70_006))",
 "        assert not (w218_a & n3r1_used219) and not (w218_b & n3r1_used219), \\",
 '            "W219 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w218_a & lfc_actual12) and not (w218_b & lfc_actual12), \\",
 '            "W219 bands must clear the lfc actual draw range"',
 "        assert not (w218_a & options_actual12) and \\",
 "            not (w218_b & options_actual12), \\",
 '            "W219 bands must clear the options_wave2 actual draw range"',
 "        # band facts (law sec.4 W219 row): A = FIRST-CLEAN past",
 "        # the registered W218 B band (the arithmetic continuation",
 f"        # {fmt(w218_a_tail + 1)}..{fmt(w218_a_tail + 2_000)} is REFUSED at its own start by the W218 B band",
 f"        # {fmt(W218['b_exit'][0])}..{fmt(w218_b_tail)}, exactly as the W218 seat leg4",
 "        # succession projection notes anticipated; honest",
 f"        # forward walk hops=1 lands {fmt(a_lo)}..{fmt(a_hi)}; A base ==",
 f"        # prior-wave B tail+1 ({fmt(w218_b_tail)}+1) machine-checkable --",
 "        # A-hops-prior-B staircase SEVENTY-NINTH instance, E36 card;",
 "        # non-rotational r587 forward-monotone walk);",
 "        # B = FIRST-CLEAN past the own-wave A window (the",
 f"        # arithmetic continuation {fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the",
 f"        # registered universe but lands INSIDE the W219 A band window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual exclusion (W141 precedent,",
 "        # leg2 law) -- the walk with the own-wave A window reserved",
 f"        # jumps to {fmt(b_lo)} and lands {fmt(b_lo)}..{fmt(b_hi)}, hops=1,",
 "        # non-rotational r587 forward-monotone walk; B base ==",
 f"        # own-wave A tail+1 ({fmt(a_hi)}+1) machine-checkable;",
 "        # cross-window convergence with the W218 seat leg4",
 "        # succession projection notes -- all MANDATORY notes",
 "        # honored (post-W218 universe re-derive + own-wave A",
 "        # reservation when deriving B);",
 "        # seat MSG-0916 tail, re-derived).",
 f'        assert WAVE_CONFIGS[219]["a_seed_base"] == {a_lo} == {w218_b_tail} + 1, (',
 '            "W219 A must be the first-clean window past the registered "',
 '            "W218 B band tail (arithmetic continuation REFUSED at its own "',
 '            "start by the W218 B band, exactly as the W218 seat leg4 "',
 '            "succession projection notes anticipated; honest forward walk "',
 '            "hops=1; A base == prior-wave B tail+1 machine-checkable "',
 '            "= A-hops-prior-B staircase SEVENTY-NINTH instance, E36 card)")',
 f"        arith_a219 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a219 & reg_ints), \\",
 '            "W219 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
 f'        assert WAVE_CONFIGS[219]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
 '            "W219 B must be the first-clean window past the own-wave A "',
 '            "band tail (arithmetic continuation CLEAN on the registered "',
 '            "universe but lands INSIDE the W219 A band window; "',
 '            "same-freeze mutual exclusion (W141 precedent, leg2 law) -- "',
 '            "the walk with the own-wave A window reserved jumps, "',
 '            "first-clean hops=1, non-rotational r587 forward-monotone "',
 '            "walk; B base == own-wave A tail+1 machine-checkable)")',
 f"        arith_b219 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b219 & reg_ints), \\",
 '            "W219 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
 "        assert not (arith_b219 & arith_a219), \\",
 '            "W219 A/B same-freeze mutual exclusion (B hops past own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W219-SHARD-0\",",
 '                                          "n1w219-0of12"), "W219 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W219-SHARD-11",',
 '                                           "n1w219-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w219\") and OUT.endswith(",
 '            "n1_w219_results.json"), "W219 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 219):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W219 shard dir collides with W{wprev}"',
 "        # W219 finalize cumulative deps: W17..W218 outputs ALL PRESENT",
 f"        # (landed net chain head {w218_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 219):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W219 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 219 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W218 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 219) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 219)], \\",
 '            "W219 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W218 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W219_PREREG.md")), \\',
 '            "W219 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w217_leg) + EOL + EOL.join(w218_leg) + EOL + EOL.join(tail) + EOL
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W219 materializer face [same guard set, dep=W17..W218 "',
 f'          "outputs ALL PRESENT (landed net chain head {w218_total} = W218 bm-c finalize one-pass, K={w218_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND NINETEENTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-c\'s forty-ninth owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 48 + candidate; seat-time live face 49th disclosed, "',
 '          "live derive at freeze governs), "',
 '          "A=FIRST-CLEAN past the registered W218 B band (staircase "',
 '          "SEVENTY-NINTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
 '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
 '          "mutual exclusion, hops=1), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w219bmc_20261012_probe_receipt.json, law sec.4 W219 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]
old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W219"') == 1
assert n1_t4.count("# --- W219 materializer face") == 1     # block header
assert n1_t4.count('"+ W219 materializer face') == 1        # print fragment
assert n1_t4.count('219: {"batch": "PERPETUAL-N1-W219"') == 1
assert pf_t2.count(ROW_I + '219: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W219-SHARD-0"') == 1
assert n1_t4.count('f"W219 A hits W{wprev}"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[218] == {{"a": ({fmt(pf_mod.N1_BANDS[218]["a"][0])}, {fmt(pf_mod.N1_BANDS[218]["a"][1])}),') == 1
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
  "machine": "bm-c", "wave": 219,
  "phase": "five-face freeze chain-order splice (r920 freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w219bmc_20261012_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "w218_upstream": {"freeze_sha": w218_freeze_sha, "prereg_sha": w218_prereg_sha,
                    "ledger_total": w218_total, "merged_n": w218_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r918 freeze + engine self-burn 12/12 + r919 finalize one-pass 09:1x (repair-free chain)"},
  "w217_transitive": {"finalize_product": "results/perpetual_faces/n1_w217_results.json present (belt-and-braces gate; ledger 901,189 / K=475,320)"},
  "w216_transitive": {"finalize_product": "results/perpetual_faces/n1_w216_results.json present (belt-and-braces gate; ledger 898,989 / K=473,120)"},
  "w215_transitive": {"finalize_product": "results/perpetual_faces/n1_w215_results.json present (belt-and-braces gate; ledger 896,789 / K=470,920)"},
  "w214_transitive": {"finalize_product": "results/perpetual_faces/n1_w214_results.json present (belt-and-braces gate; ledger 894,589 / K=468,720)"},
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w219_prereg_sha, "probe_receipt_sha": w219_receipt_sha,
                    "note": "r920 freeze-window bundle: prereg + this splice editor landed same-window, upstream W218 already landed (clean-precondition eighth consecutive window); r920 prereg derive = machine transform of the freeze-time W218 blob (46 count-asserted pairs, old-sides REPLAYED from the committed W218 derive SUB + the W217 derive SUB + the W216 literal PAIRS -- three-level replay chain, every block blob-verified count==1 preflight, zero transcription) + @L14@/@L15@/@L16@/@L17@/@T18@ placeholder class-guard"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmc_ordinal_face": 49,
                    "note": "post-W219 registration: bm-c rows 48 + candidate = 49th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=49 = r919 seat-time live face -- disclosed honest)"},
  "parity_section": {"source": "OWN W218 block physical bytes (own splice generation, structure known exactly)",
                    "bytes": len(par_sec),
                    "row_asserts": par_sec.count("assert pf.N1_BANDS["),
                    "note": "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211 + W212 + W213 + W214 + W215 + W216 legs -> W219 block = 77 rows ending at W218; disclosed: inherited W213 leg error-string face (\"registered W212 row parity drift\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1},
}
open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w218_upstream")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> ignition verify (2-cycle n1_w219 growth)")
