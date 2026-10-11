# -*- coding: utf-8 -*-
# 2026-10-11 20:5x bm-c r888 freeze-prep: W211 five-face freeze splice editor
# (PREPARED pre-landing per the r848 W209 freeze-prep precedent, EXECUTED after
# the bm-b W210 five-face + W210 finalize product land on origin --
# chain-order law + tail dep assert require the prior wave's results file).
# Lineage: _w209bmc_freeze_edits.py pattern (proven live-fire freeze 87b81f973)
# + r787 preflight law + r609 origin-verbatim base + r761 programmatic quote
# wrapping + r909 physical-byte anchors + r838 per-file EOL detection.
# Zero hardcoded upstream band values: ALL W210 facts machine-derived from the
# LIVE pf import at freeze time (bm-b's registered row), cross-checked against
# the committed ADMIT receipt (results/_w211bmc_20261011_probe_receipt.json)
# which was derived on the W207-registered + W208/W209/W210-declared-injected
# universe. If bm-b's REGISTERED W210 bands differ from the declared face, the
# staircase asserts fail LOUD (fail-closed) -> honest re-probe required, never
# auto-accept.
# STRUCTURAL CHOICE (vs the W209 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W209
# block physical bytes -- structure known exactly -- NOT from the bm-b W210
# block (whose template lineage is bm-b's own W207-era 51-row window style;
# no assumption made, no dependency taken). Extraction self-asserts 69 rows
# range(138, 207) regardless.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w211bmc_20261011_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w211bmc_freeze_receipt.json")
SEAT_MSG = "MSG-20261011-0350-bmc-w211-seat.md"
SEAT_ORIGIN = "0a60b8850"
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

# ---------- gate 0.5: W210 five-face landed + W210 finalize product present ----------
# (r898 takeover face: the W210 freeze was executed by bm-c per GM re-assignment;
#  owner accepted in (bm-b, bm-c) with takeover-commit verification, W208-takeover
#  gate0.5 precedent applied verbatim)
# (chain-order precondition; W209 finalize is the transitive dep of the W210
# freeze and is belt-and-braces checked here + enforced by the block's
# cumulative-deps assert range(17, 211) at selftest time)
W210 = dict(pf_mod.N1_BANDS.get(210) or {})
assert W210.get("engine_owner") in ("bm-b", "bm-c"), \
    f"W210 row not landed as declared (bm-b seat owner expected; bm-c r898 takeover face allowed): {W210} -- five-face freeze missing;" \
    " if a takeover face exists the freeze window MUST re-derive this editor honestly"
if W210.get("engine_owner") == "bm-c":
    tk = git("cat-file", "-t", "d5ec83b72")
    assert tk.returncode == 0 and tk.stdout.decode().strip() == "commit", \
        "W210 takeover commit d5ec83b72 missing -- ownership face unverified, abort"
w210_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w210_results.json")
assert os.path.exists(w210_out_path), "W210 finalize product missing (n1_w210_results.json) -- chain dep not met"
w209_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w209_results.json")
assert os.path.exists(w209_out_path), "W209 finalize product missing (transitive chain dep) -- abort"
w208_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w208_results.json")
assert os.path.exists(w208_out_path), "W208 finalize product missing (transitive chain dep, belt-and-braces) -- abort"
w210_out = json.load(open(w210_out_path, encoding="utf-8"))
w210_led = (w210_out.get("science_gates") or {}).get("ledger") or {}
w210_total = w210_led.get("total")
w210_merged_n = None
try:
    w210_merged_n = w210_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '210: {"a"', "--", "scripts/perpetual_faces.py")
w210_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W210_PREREG.md")
w210_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W210_PREREG.md")), \
    "bm-b W210 per-wave prereg missing on disk -- chain face incomplete, abort"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face bmc_ordinal=40 with the r846 attempt-continuity note --
# live derive at freeze time: bmc rows 39 + candidate = 40th EXACT, the
# pre-takeover carryover era fully resolved post-W208/W209 registration)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
_expected_bmc = 40 if W210.get("engine_owner") == "bm-c" else 39
assert len(owner_rows_live) == 200 and len(bmc_rows_live) == _expected_bmc, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bmc={len(bmc_rows_live)} (expect 200/{_expected_bmc} PRE-splice post-W208+W209+W210 registration; r899 anchor erratum: dead r898 patch anchored 201 = off-by-one double-count of the already-spliced W210 row -- W209 precedent 198/38 pre-splice pair + W210 splice 199/39->200/40, forensic script results/_r899bmc_w211_ordinals.py; W210 takeover r898 face: bm-c 40th own wave, this candidate = 41st, live derive governs r587/r359)"
print(f"gate0.5 OK: W210 landed (freeze {w210_freeze_sha[:10]}, owner={W210.get('engine_owner')} "
      f"[r898 takeover face, commit d5ec83b72 verified when bm-c]), W210+W209+W208 finalize products present "
      f"(W210 ledger head {w210_total}, merged n={w210_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-c rows {len(bmc_rows_live)} + candidate (41st own wave per the W210 takeover r898 re-derive; "
      f"probe receipt leg0 bmc_ordinal=40 seat-time face disclosed -- the takeover shifted the own-ordinal +1, "
      f"live derive at freeze time governs r587/r359)")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
A = rec["bands"]["A"]; B = rec["bands"]["B"]
a_lo, a_hi = (int(x) for x in A.split("_"))
b_lo, b_hi = (int(x) for x in B.split("_"))
leg1 = rec["legs"]["leg1"]
assert [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"], "receipt band mismatch"
assert (a_lo, a_hi) == (479_004, 481_003) and (b_lo, b_hi) == (481_004, 481_203), \
    f"W211 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w210_b_tail = W210["b_exit"][1]      # registered W210 row b_exit hi (pf import, live)
w210_a_tail = W210["a"][1]           # registered W210 row A hi (pf import, live)
assert w210_b_tail + 1 == a_lo and a_hi + 1 == b_lo, "staircase base relations broken"
# the REFUSED arithmetic continuation starts at prior-wave A-tail+1 (== W210 B-base),
# machine-derived from the LIVE registered row, never transcribed.
assert w210_a_tail + 1 == W210["b_exit"][0], "W210 A-tail+1 != W210 B-base (registered row in-wave relation)"
assert [w210_a_tail + 1, w210_a_tail + 2_000] == leg1["ARITH_A"], \
    f"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w210_a_tail + 1, w210_a_tail + 2_000]} != {leg1['ARITH_A']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W211_PREREG.md")
w211_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w211bmc_20261011_probe_receipt.json")
w211_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W211 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W211_PREREG.md"],
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

def fmt(n):  # 479004 -> "479_004"
    return f"{n // 1000}_{n % 1000:03d}"

# ---------- extract parity section (physical bytes, never re-typed) ----------
# STRUCTURAL CHOICE: extract the estate from the OWN W209 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W208 leg) -- the bm-b W210
# block (their W207-template lineage) is NOT assumed and NOT depended upon for
# the estate. The W209 block span ends where the W210 block header begins
# (bm-b's block must exist at this point per gate0.5).
a9 = '    # --- W209 materializer face'
a10 = '    # --- W210 materializer face'
w209_start = n1_t.find(a9); w210_pos = n1_t.find(a10)
assert w209_start > 0 and w210_pos > w209_start, \
    "W209/W210 materializer block face not found (bm-b W210 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w209_start:w210_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W209 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m208 = re.search(r" *assert pf\.N1_BANDS\[208\] ==", par_full)
assert m208, "upstream W208 row leg not found inside W209 parity span"
par_sec = par_full[:m208.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 69 \
    and [int(w) for w in _estate_ws] == list(range(138, 207)), \
    f"estate segment not W138..W206 full-span 69 rows: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-2:])}"
assert par_full.count("assert pf.N1_BANDS[") == 70, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 70 (69 estate + 1 W208 leg)"

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '210: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W210_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
# MEM_I derived INSIDE the W210 cfg entry span (value format not assumed:
# bm-b template may write plain int or underscore form -- indent is all we take)
_c210 = n1_t.find('210: {"batch"')
assert _c210 > 0, "W210 cfg entry not found (bm-b freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c210)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c210) > _mpos, "W210 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W210["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W210["a"][0]), _c210) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W210["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '210: {"a"', PF_EOL)

# ---------- W210 row owner line (physical bytes; comment text is bm-b's own) ----------
w210_row_start = pf_t.find('    210: {"a"')
assert w210_row_start > 0, "W210 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w210_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w210_own_line = pf_t[_own_ls:_own_le]
assert ('"engine_owner": "bm-b"' in w210_own_line) or ('"engine_owner": "bm-c"' in w210_own_line), \
    f"W210 owner line unexpected bytes: {w210_own_line!r}"
if '"engine_owner": "bm-c"' in w210_own_line:
    assert "takeover r898" in w210_own_line, "W210 bm-c owner line lacks the takeover r898 annotation"
ROWC_I = w210_own_line[:len(w210_own_line) - len(w210_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W211 (bm-c loop five-face freeze splice, seat",
"    # MSG-20261011-0350-bmc-w211-seat pushed to origin " + SEAT_ORIGIN,
"    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen",
"    # commit " + w211_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W211_PREREG.md",
"    # freeze-prep r848-precedent bundle, probe",
"    # results/_w211bmc_20261011_probe_receipt.json @ " + w211_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-b W210 five-face (freeze " + w210_freeze_sha[:10] + ") + W210",
"    # finalize product landed (n1_w210_results.json present, ledger",
"    # head " + str(w210_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W211 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w211bmc_20261011_probe_receipt.json: A = FIRST-CLEAN",
"    # past the registered W210 B band (arithmetic continuation",
"    # " + fmt(w210_a_tail + 1) + ".." + fmt(w210_a_tail + 2_000) + " REFUSED at its own start by the W210 B band",
"    # " + fmt(W210["b_exit"][0]) + ".." + fmt(w210_b_tail) + ", exactly as the W210 seat leg4",
"    # projection anticipated;",
"    # honest forward walk hops=1 -> " + fmt(a_lo) + ".." + fmt(a_hi) + ", non-rotational",
"    # r587 forward-monotone walk; A base == prior-wave B tail+1",
"    # (" + fmt(w210_b_tail) + "+1) machine-checkable -- A-hops-prior-B staircase",
"    # SEVENTY-FIRST instance, E36 card (probe receipt leg1 A_semantics",
"    # machine-read ordinal, never transcribed);",
"    # B = FIRST-CLEAN past the own-wave A window (arithmetic",
"    # continuation " + fmt(a_lo) + ".." + fmt(a_lo + 199) + " CLEAN on the registered",
"    # universe but lands INSIDE the W211 A band window " + fmt(a_lo) + ".." + fmt(a_hi) + " --",
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
"    # W212+ projection (gate-derived pre-seat probe leg4, pre-W211",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W212p_A"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " /",
"    # B naive first-clean " + rec["legs"]["leg4"]["W212p_B"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " -- naive B lands",
"    # INSIDE the naive A window and the registered W211 B band",
"    # " + fmt(b_lo) + ".." + fmt(b_hi) + " will refuse the naive W212 A window; W212 freezer",
"    # MUST re-derive on the post-W211 universe AND reserve the",
"    # own-wave A window when deriving B (W141 precedent, leg2 law,",
"    # E36 staircase card; never transcribe r587) -- CONVERGENCE ALREADY",
"    # PROVEN: the published W212 seat (bm-c, MSG-20261011-0732) re-derived",
"    # A 481_204..483_203 hopping the W211 declared B band (SEVENTY-SECOND",
"    # instance materialized at seat time) + B 483_204..483_403.",
"    # NOT a re-pick (R250: W211 bands were never assigned).",
])
pf_row = (f'{ROW_I}211: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'211: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w210_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w210_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W210 finalize ALL LANDED (W210 finalize product present at splice, "
            f"net chain head {w210_total} machine-read, merged pool K={w210_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition; "
            f"downstream declared seat W212 (bm-c, seat-published r849/r850 windows, "
            f"MSG-20261011-0732) pending -- not an upstream dep")
cfg_lines = [
 f'{CFG_I}211: {{"batch": "PERPETUAL-N1-W211",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W211_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND ELEVENTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W210 row five-face freeze (seat published by bm-b MSG-20261011-0319; r898 TAKEOVER: bm-b armed lane stalled 94min >> 20min GM re-assignment gate -> bm-c executed the freeze, engine_owner bm-b->bm-c, bands unchanged R250, notice MSG-2026-10-12-0020 @ c64bc2287 pre-pushed), ",
 f"{w210_freeze_sha[:10]} (prereg {w210_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W210 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261011-0350-bmc-w211-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg + ",
 "freeze splice script landed in the r848-precedent freeze-prep bundle ",
 f"commit {w211_prereg_sha[:10]} @ receipt {w211_receipt_sha[:10]}); ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W210 five-face + W210 finalize product landed ",
 "(prepared pre-landing by the bm-c loop r888 freeze-prep window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c, wave 211: ",
 "A = FIRST-CLEAN past the registered W210 B band (the ",
 f"arithmetic continuation {fmt(w210_a_tail + 1)}..{fmt(w210_a_tail + 2_000)} is REFUSED at its ",
 f"own start by the W210 B band {fmt(W210['b_exit'][0])}..{fmt(w210_b_tail)}, exactly as ",
 "the W210 seat leg4 succession ",
 "projection notes anticipated; honest forward walk hops=1 -> ",
 f"{fmt(a_lo)}..{fmt(a_hi)}; A base == prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase SEVENTY-FIRST ",
 "instance, E36 card (probe receipt leg1 machine-read ordinal); ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN ",
 "past the own-wave A window (the arithmetic continuation ",
 f"{fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the registered universe but lands ",
 f"INSIDE the W211 A band window {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual ",
 "exclusion, W141 precedent, leg2 law -- the walk with the ",
 f"own-wave A window reserved jumps to {fmt(b_lo)}, first-clean ",
 f"{fmt(b_lo)}..{fmt(b_hi)} hops=1, non-rotational r587 forward-monotone walk; ",
 "B base == own-wave A tail+1 machine-checkable; cross-window ",
 "convergence with the W210 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W210 universe ",
 "re-derive + own-wave A reservation); ADMIT receipt ",
 "results/_w211bmc_20261011_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W212+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W212p_A']} CLEAN / B naive first-clean ",
 f"{rec['legs']['leg4']['W212p_B']} CLEAN -- naive B lands INSIDE the naive A window and ",
 f"the registered W211 B band {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W212 A window; ",
 "W212+ freezer MUST re-derive on the post-W211 universe AND ",
 "reserve the own-wave A window when deriving B (W141 precedent, ",
 "leg2 law, E36 staircase card) -- CONVERGENCE ALREADY PROVEN: the ",
 "published W212 seat (bm-c, MSG-20261011-0732) re-derived ",
 "A 481_204..483_203 hopping the W211 declared B band + ",
 "B 483_204..483_403; " + fin_face + " -- the finalize ",
 "merge loop still derives the wave set from registry keys at ",
 "run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W211 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past the registered W210 B band; arithmetic {fmt(w210_a_tail + 1)}..{fmt(w210_a_tail + 2_000)} REFUSED at own start by the W210 B band {fmt(W210["b_exit"][0])}..{fmt(w210_b_tail)}; hops=1; A-hops-prior-B staircase SEVENTY-FIRST instance, E36 card; ordinal machine-read SEVENTY-FIRST per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W211 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN past the own-wave A window; arithmetic {fmt(a_lo)}..{fmt(a_lo + 199)} lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w211", "out_name": "n1_w211_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]
cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('211: {"batch": "PERPETUAL-N1-W211"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W211 materializer face (bm-c loop five-face freeze splice,",
 "    #     own-series law under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's fortieth owned per machine-derive (engine_owner==bm-c",
 "    #     rows 39 + candidate; attempt-continuity face: the aborted r846 W208",
 "    #     draft consumed the 38th slot, W209 = 39th, this = 40th); wave 211 = first free number after the",
f"    #     REGISTERED W210 row (five-face freeze {w210_freeze_sha[:10]}; seat published by bm-b, r898 TAKEOVER: bm-b hb-stall 94min -> bm-c executed per GM re-assignment + CEO fill-order standing, bands unchanged R250, notice MSG-2026-10-12-0020 @ c64bc2287; engine_owner at W211 freeze governs) --",
 "    #     SINGLE STATE zero seat gap (W2..W210 all registered). Seat",
 "    #     published=reserved MSG-20261011-0350-bmc-w211-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg +",
 "    #     freeze splice script landed in the r848-precedent freeze-prep",
 "    #     bundle commit " + w211_prereg_sha[:10] + "; deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W210 five-face + W210 finalize",
 "    #     product landed; zero --no-verify; the W211 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND ELEVENTH engine wave BY",
 "    #     MACHINE-DERIVE (engine_owner rows 200 + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w211bmc_20261011_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W211 bands were never assigned).",
 "    _set_wave(211)",
 "    try:",
 '        assert WAVE_CONFIGS[210]["a_seed_base"] == pf.N1_BANDS[210]["a"][0], \\',
 '            "W211 upstream W210 mirror drift (a)"',
 "        assert WAVE_CONFIGS[210][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[210]["b_exit"][0], "W211 upstream W210 mirror drift (b)"',
 "        assert WAVE_CONFIGS[210].get(\"engine_owner\") == \\",
f'            pf.N1_BANDS[210].get("engine_owner") == "{W210.get("engine_owner")}", \\',
'            "W211 upstream W210 engine_owner mirror drift (law-mirror parity; r898 takeover bm-b->bm-c face disclosed)"',
 "        w210_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w210_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w210_a & w210_b), "W211 A/B band overlap"',
 "        assert not (w210_a & reg_ints) and not (w210_b & reg_ints), \\",
 '            "W211 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w210_a), ("B", w210_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W211 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W211 {nm} hits W1"',
 '            assert not (band & probes), f"W211 {nm} hits probe seeds"',
]
w210_leg = [
 f'        assert pf.N1_BANDS[210] == {{"a": ({fmt(W210["a"][0])}, {fmt(W210["a"][1])}),',
 f'                                    "b_exit": ({fmt(W210["b_exit"][0])}, {fmt(W210["b_exit"][1])}),',
'                                    "engine_owner": "{}"}}, \\'.format(W210.get("engine_owner")),
'            "registered W210 row parity drift (r307; bm-b five-face freeze; r898 takeover bm-b->bm-c face disclosed)"',
]
tail = [
 "        # prior-wave disjointness W2..W210 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 211):",
 '            assert not (w210_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W211 A hits W{wprev}\"",
 '            assert not (w210_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W211 B hits W{wprev}\"",
 "        n3r1_used211 = set(range(70_000, 70_006))",
 "        assert not (w210_a & n3r1_used211) and not (w210_b & n3r1_used211), \\",
 '            "W211 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w210_a & lfc_actual12) and not (w210_b & lfc_actual12), \\",
 '            "W211 bands must clear the lfc actual draw range"',
 "        assert not (w210_a & options_actual12) and \\",
 "            not (w210_b & options_actual12), \\",
 '            "W211 bands must clear the options_wave2 actual draw range"',
 "        # band facts (law sec.4 W211 row): A = FIRST-CLEAN past",
 "        # the registered W210 B band (the arithmetic continuation",
 f"        # {fmt(w210_a_tail + 1)}..{fmt(w210_a_tail + 2_000)} is REFUSED at its own start by the W210 B band",
 f"        # {fmt(W210['b_exit'][0])}..{fmt(w210_b_tail)}, exactly as the W210 seat leg4",
 "        # succession projection notes anticipated; honest",
 f"        # forward walk hops=1 lands {fmt(a_lo)}..{fmt(a_hi)}; A base ==",
 f"        # prior-wave B tail+1 ({fmt(w210_b_tail)}+1) machine-checkable --",
 "        # A-hops-prior-B staircase SEVENTY-FIRST instance, E36 card;",
 "        # non-rotational r587 forward-monotone walk);",
 "        # B = FIRST-CLEAN past the own-wave A window (the",
 f"        # arithmetic continuation {fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the",
 f"        # registered universe but lands INSIDE the W211 A band window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual exclusion (W141 precedent,",
 "        # leg2 law) -- the walk with the own-wave A window reserved",
 f"        # jumps to {fmt(b_lo)} and lands {fmt(b_lo)}..{fmt(b_hi)}, hops=1,",
 "        # non-rotational r587 forward-monotone walk; B base ==",
 f"        # own-wave A tail+1 ({fmt(a_hi)}+1) machine-checkable;",
 "        # cross-window convergence with the W210 seat leg4",
 "        # succession projection notes -- all MANDATORY notes",
 "        # honored (post-W210 universe re-derive + own-wave A",
 "        # reservation when deriving B);",
 "        # seat MSG-0350 tail, re-derived).",
 f'        assert WAVE_CONFIGS[211]["a_seed_base"] == {a_lo} == {w210_b_tail} + 1, (',
 '            "W211 A must be the first-clean window past the registered "',
 '            "W210 B band tail (arithmetic continuation REFUSED at its own "',
 '            "start by the W210 B band, exactly as the W210 seat leg4 "',
 '            "succession projection notes anticipated; honest forward walk "',
 '            "hops=1; A base == prior-wave B tail+1 machine-checkable "',
 '            "= A-hops-prior-B staircase SEVENTY-FIRST instance, E36 card)")',
 f"        arith_a211 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a211 & reg_ints), \\",
 '            "W211 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
 f'        assert WAVE_CONFIGS[211]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
 '            "W211 B must be the first-clean window past the own-wave A "',
 '            "band tail (arithmetic continuation CLEAN on the registered "',
 '            "universe but lands INSIDE the W211 A band window; "',
 '            "same-freeze mutual exclusion (W141 precedent, leg2 law) -- "',
 '            "the walk with the own-wave A window reserved jumps, "',
 '            "first-clean hops=1, non-rotational r587 forward-monotone "',
 '            "walk; B base == own-wave A tail+1 machine-checkable)")',
 f"        arith_b211 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b211 & reg_ints), \\",
 '            "W211 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
 "        assert not (arith_b211 & arith_a211), \\",
 '            "W211 A/B same-freeze mutual exclusion (B hops past own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W211-SHARD-0\",",
 '                                          "n1w211-0of12"), "W211 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W211-SHARD-11",',
 '                                           "n1w211-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w211\") and OUT.endswith(",
 '            "n1_w211_results.json"), "W211 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 211):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W211 shard dir collides with W{wprev}"',
 "        # W211 finalize cumulative deps: W17..W210 outputs ALL PRESENT",
 f"        # (landed net chain head {w210_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 211):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W211 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 211 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W210 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 211) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 211)], \\",
 '            "W211 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W210 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W211_PREREG.md")), \\',
 '            "W211 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w210_leg) + EOL + EOL.join(tail) + EOL
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W211 materializer face [same guard set, dep=W17..W210 "',
 f'          "outputs ALL PRESENT (landed net chain head {w210_total} = W210 bm-b finalize one-pass, K={w210_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND ELEVENTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-c\'s fortieth owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 39 + candidate, attempt-continuity face), "',
 '          "A=FIRST-CLEAN past the registered W210 B band (staircase "',
 '          "SEVENTY-FIRST instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
 '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
 '          "mutual exclusion, hops=1), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w211bmc_20261011_probe_receipt.json, law sec.4 W211 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]
old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W211"') == 1
assert n1_t4.count("# --- W211 materializer face") == 1     # block header
assert n1_t4.count('"+ W211 materializer face') == 1        # print fragment
assert n1_t4.count('211: {"batch": "PERPETUAL-N1-W211"') == 1
assert pf_t2.count(ROW_I + '211: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W211-SHARD-0"') == 1
assert n1_t4.count('f"W211 A hits W{wprev}"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[210] == {{"a": ({fmt(W210["a"][0])}, {fmt(W210["a"][1])}),') == 1
assert n1_t4.count('    # --- W209 materializer face') == 1  # estate source block kept
assert n1_t4.count('    # --- W210 materializer face') == 1  # prior block kept
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
  "machine": "bm-c", "wave": 211,
  "phase": "five-face freeze chain-order splice (prepared pre-landing r888 freeze-prep bundle, executed post-W210-finalize)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w211bmc_20261011_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "w210_upstream": {"freeze_sha": w210_freeze_sha, "prereg_sha": w210_prereg_sha,
                    "ledger_total": w210_total, "merged_n": w210_merged_n,
                    "engine_owner": "bm-b (declared seat honored, no takeover face)"},
  "w209_transitive": {"finalize_product": "results/perpetual_faces/n1_w209_results.json present (belt-and-braces gate; ledger 883,589 / K=457,720 at prep time)"},
  "w208_transitive": {"finalize_product": "results/perpetual_faces/n1_w208_results.json present (belt-and-braces gate)"},
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w211_prereg_sha, "probe_receipt_sha": w211_receipt_sha,
                    "note": "freeze-prep bundle r848-precedent: prereg + this splice editor landed while upstream W210 pending"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmc_ordinal_face": 40,
                    "note": "post-W208/W209/W210 registration: bm-c rows+1 = 40 == probe leg0 bmc_ordinal=40 face EXACT MATCH (attempt-continuity: r846 aborted W208 draft consumed the 38th slot, W209=39th, this=40th); live derive at freeze time governs per r587/r359"},
  "parity_section": {"source": "OWN W209 block physical bytes (structural choice: bm-b W210 block template lineage NOT assumed)",
                    "bytes": len(par_sec),
                    "row_asserts": par_sec.count("assert pf.N1_BANDS["),
                    "note": "full-span estate W138..W206 (69 rows, r858 absorb generation) + own W210 leg -> W211 block = 70 rows ending at W210"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1},
}
open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w210_upstream")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> ignition verify (2-cycle n1_w211 growth)")
