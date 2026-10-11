# -*- coding: utf-8 -*-
# 2026-10-12 00:2x bm-c r898 TAKEOVER FREEZE: W210 five-face freeze splice editor.
# TAKEOVER FACE: the W210 seat was published=reserved by bm-b (MSG-20261011-0319-bmb,
# probe ADMIT receipt committed @ d550bf11c) but bm-b's armed M10 lane never executed
# the freeze: hb-stall 94min >> 20min GM re-assignment gate + W209 finalize landed
# 4h+ with burns_active=[] queue_next=[] (engine idle, CEO fill-order standing
# RE-ISSUED in force) -> bm-c executes per the W208 takeover r885 precedent
# (hb-stall takeover gate + CEO fill-order law + bands unchanged R250 +
# takeover notice pushed BEFORE the freeze: MSG-2026-10-12-0020 @ c64bc2287).
# Lineage: _w209bmc_freeze_edits.py pattern (proven live-fire freeze 87b81f973)
# + _w211bmc_freeze_edits.py estate-extraction structural choice
# + r787 preflight law + r609 origin-verbatim base + r761 programmatic quote
# wrapping + r909 physical-byte anchors + r838 per-file EOL detection.
# Zero hardcoded upstream band values: ALL W209 facts machine-derived from the
# LIVE pf import at freeze time (bm-c's own registered row), cross-checked against
# the committed ADMIT receipt (results/_w210bmb_20261011_probe_receipt.json)
# which was derived on the W207-registered + W208/W209-declared-injected universe.
# If the LIVE W209 bands differ from the declared face, the staircase asserts
# fail LOUD (fail-closed) -> honest re-probe required, never auto-accept.
# Honest disclosure: bm-b's seat MSG payload claimed per-wave prereg+freeze
# would be pushed -- origin never contained them (git log -S W210 research/
# zero hits, machine-checked r898); this prereg was REBUILT machine-read in the
# takeover window (upstream W209 actuals + probe receipt verbatim), not from
# any bm-b draft (none exists).
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w210bmb_20261011_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w210bmc_takeover_freeze_receipt.json")
SEAT_MSG = "MSG-20261011-0319-bmb-w210-seat.md"
SEAT_ORIGIN = "d550bf11c"
TAKEOVER_MSG = "fleet/inbox/MSG-2026-10-12-0020-bmc-ALL-w210-takeover.md"
TAKEOVER_ORIGIN = "c64bc2287"
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

# ---------- gate 0.5: W209 five-face landed + W209 finalize product present ----------
# (chain-order precondition; W208 finalize is the transitive dep of the W209
# freeze and is belt-and-braces checked here + enforced by the block's
# cumulative-deps assert range(17, 210) at selftest time)
W209 = dict(pf_mod.N1_BANDS.get(209) or {})
assert W209.get("engine_owner") == "bm-c", \
    f"W209 row not landed as expected (bm-c five-face freeze r886): {W209} -- five-face freeze missing"
w209_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w209_results.json")
assert os.path.exists(w209_out_path), "W209 finalize product missing (n1_w209_results.json) -- chain dep not met"
w208_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w208_results.json")
assert os.path.exists(w208_out_path), "W208 finalize product missing (transitive chain dep, belt-and-braces) -- abort"
w209_out = json.load(open(w209_out_path, encoding="utf-8"))
w209_led = (w209_out.get("science_gates") or {}).get("ledger") or {}
w209_total = w209_led.get("total")
w209_merged_n = None
try:
    w209_merged_n = w209_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w209_total == 883_589, f"W209 ledger head drift: {w209_total} != 883,589 (prereg anchor face)"
assert w209_merged_n == 457_720, f"W209 merged pool drift: {w209_merged_n} != 457,720 (prereg anchor face)"
# takeover notice must be on origin BEFORE the freeze (anti-double-burn face)
r = git("show", f"origin/main:{TAKEOVER_MSG}")
assert r.returncode == 0 and b"takeover" in r.stdout.lower(), \
    "W210 takeover notice missing on origin -- anti-double-burn precondition failed (push first)"
r = git("log", "--format=%H", "-S", '209: {"a"', "--", "scripts/perpetual_faces.py")
w209_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W209_PREREG.md")
w209_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# live ordinal derive (r359 law: gate machine output governs; probe receipt leg0
# face bmb_ordinal=42 is the bm-b seat-time face -- TAKEOVER re-derives the own
# ordinal honestly: live at freeze time governs per r587/r359)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
bmb_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-b"]
assert len(owner_rows_live) == 199 and len(bmc_rows_live) == 39 and len(bmb_rows_live) == 41, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bmc={len(bmc_rows_live)} bmb={len(bmb_rows_live)} (expect 199/39/41 post-W208+W209 registration)"
print(f"gate0.5 OK: W209 landed (freeze {w209_freeze_sha[:10]}, owner=bm-c), W209+W208 finalize products present "
      f"(W209 ledger head {w209_total}, merged n={w209_merged_n}); takeover notice on origin {TAKEOVER_ORIGIN[:10]}; "
      f"owner rows {len(owner_rows_live)} + candidate, bm-c rows {len(bmc_rows_live)} + candidate "
      f"(TAKEOVER: 40th own wave per live derive, discloses the bm-b seat-time bmb_ordinal=42 face honestly)")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
A = rec["bands"]["A"]; B = rec["bands"]["B"]
a_lo, a_hi = (int(x) for x in A.split("_"))
b_lo, b_hi = (int(x) for x in B.split("_"))
leg1 = rec["legs"]["leg1"]
assert [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"], "receipt band mismatch"
assert (a_lo, a_hi) == (476_804, 478_803) and (b_lo, b_hi) == (478_804, 479_003), \
    f"W210 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w209_b_tail = W209["b_exit"][1]      # registered W209 row b_exit hi (pf import, live)
w209_a_tail = W209["a"][1]           # registered W209 row A hi (pf import, live)
assert w209_b_tail + 1 == a_lo and a_hi + 1 == b_lo, "staircase base relations broken"
# the REFUSED arithmetic continuation starts at prior-wave A-tail+1 (== W209 B-base),
# machine-derived from the LIVE registered row, never transcribed.
assert w209_a_tail + 1 == W209["b_exit"][0], "W209 A-tail+1 != W209 B-base (registered row in-wave relation)"
assert [w209_a_tail + 1, w209_a_tail + 2_000] == leg1["ARITH_A"], \
    f"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w209_a_tail + 1, w209_a_tail + 2_000]} != {leg1['ARITH_A']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W210_PREREG.md")
w210_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w210bmb_20261011_probe_receipt.json")
w210_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W210 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W210_PREREG.md"],
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

def fmt(n):  # 476804 -> "476_804"
    return f"{n // 1000}_{n % 1000:03d}"

# ---------- extract parity section (physical bytes, never re-typed) ----------
# STRUCTURAL CHOICE (same as the W211 editor): extract the estate from the OWN
# W209 block (bytes known exactly: full-span estate W138..W206 69 rows + own
# W208 leg) -- zero structural assumptions about anything else. The W209
# block span ends where the T-141 lane header begins (the W210 block does NOT
# exist yet at this splice: bm-b never landed it, this takeover freeze CREATES it).
a9 = '    # --- W209 materializer face'
a4 = '    # --- T-141 s2 lane face'
w209_start = n1_t.find(a9); t141_pos = n1_t.find(a4)
assert w209_start > 0 and t141_pos > w209_start, \
    "W209 block / T-141 header face not found (W209 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w209_start:t141_pos]
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

CFG_I  = line_indent(n1_t, '209: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W209_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
# MEM_I derived INSIDE the W209 cfg entry span (value format not assumed:
# int or underscore form -- indent is all we take)
_c209 = n1_t.find('209: {"batch"')
assert _c209 > 0, "W209 cfg entry not found (W209 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c209)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c209) > _mpos, "W209 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W209["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W209["a"][0]), _c209) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W209["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '209: {"a"', PF_EOL)

# ---------- W209 row owner line (physical bytes; comment is bm-c's own r886 text) ----------
w209_row_start = pf_t.find('    209: {"a"')
assert w209_row_start > 0, "W209 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w209_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w209_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-c"},' in w209_own_line, \
    f"W209 owner line unexpected bytes: {w209_own_line!r}"
ROWC_I = w209_own_line[:len(w209_own_line) - len(w209_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W210 (bm-c loop TAKEOVER five-face freeze splice, seat",
"    # MSG-20261011-0319-bmb-w210-seat published by bm-b, pushed to origin " + SEAT_ORIGIN,
"    # pre-freeze r565 law; prereg REBUILT machine-read in the takeover window (bm-b",
"    # payload claim never landed on origin, disclosed); ADMIT probe receipt frozen",
"    # commit " + w210_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W210_PREREG.md,",
"    # probe results/_w210bmb_20261011_probe_receipt.json @ " + w210_receipt_sha[:10] + ");",
"    # TAKEOVER r898: bm-b hb-stall 94min >> 20min GM re-assignment gate + W209",
"    # finalize landed 4h+ with the armed lane unexecuted (engine idle, burns_active=[],",
"    # CEO fill-order standing RE-ISSUED 2026-10-10 ~23:1x) -> bm-c executes per the",
"    # W208 takeover r885 precedent; takeover notice MSG-2026-10-12-0020 pushed to",
"    # origin " + TAKEOVER_ORIGIN + " BEFORE this freeze (anti-double-burn, bm-b armed-lane",
"    # yield requested); engine_owner bm-b -> bm-c, bands UNCHANGED R250;",
"    # deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-c W209 five-face (freeze " + w209_freeze_sha[:10] + ") + W209",
"    # finalize product landed (n1_w209_results.json present, ledger",
"    # head " + str(w209_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W210 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w210bmb_20261011_probe_receipt.json: A = FIRST-CLEAN",
"    # past the registered W209 B band (arithmetic continuation",
"    # " + fmt(w209_a_tail + 1) + ".." + fmt(w209_a_tail + 2_000) + " REFUSED at its own start by the W209 B band",
"    # " + fmt(W209["b_exit"][0]) + ".." + fmt(w209_b_tail) + ", exactly as the W209 seat leg4",
"    # projection anticipated;",
"    # honest forward walk hops=1 -> " + fmt(a_lo) + ".." + fmt(a_hi) + ", non-rotational",
"    # r587 forward-monotone walk; A base == prior-wave B tail+1",
"    # (" + fmt(w209_b_tail) + "+1) machine-checkable -- A-hops-prior-B staircase",
"    # SEVENTIETH instance, E36 card (probe receipt leg1 A_semantics",
"    # machine-read ordinal, never transcribed);",
"    # B = FIRST-CLEAN past the own-wave A window (arithmetic",
"    # continuation " + fmt(a_lo) + ".." + fmt(a_lo + 199) + " CLEAN on the registered",
"    # universe but lands INSIDE the W210 A band window " + fmt(a_lo) + ".." + fmt(a_hi) + " --",
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
"    # W211+ projection (gate-derived pre-seat probe leg4, pre-W210",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W211p_A"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " /",
"    # B naive first-clean " + rec["legs"]["leg4"]["W211p_B"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " -- naive B lands",
"    # INSIDE the naive A window and the registered W210 B band",
"    # " + fmt(b_lo) + ".." + fmt(b_hi) + " will refuse the naive W211 A window; W211 freezer",
"    # MUST re-derive on the post-W210 universe AND reserve the",
"    # own-wave A window when deriving B (W141 precedent, leg2 law,",
"    # E36 staircase card; never transcribe r587) -- CONVERGENCE ALREADY",
"    # PROVEN: the published W211 seat (bm-c, MSG-20261011-0350) re-derived",
"    # A 479_004..481_003 hopping the W210 declared B band (SEVENTY-FIRST",
"    # instance materialized at seat time) + B 481_004..481_203.",
"    # NOT a re-pick (R250: W210 bands were never assigned).",
])
pf_row = (f'{ROW_I}210: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},  # takeover r898: bm-b hb-stall 94min '
          + '-> bm-c per CEO fill-order standing; bands unchanged R250 (bm-b probe ADMIT verbatim, seat MSG-20261011-0319)' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'210: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w209_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w209_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W209 finalize ALL LANDED (W209 finalize product present at splice, "
            f"net chain head {w209_total} machine-read, merged pool K={w209_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition; "
            f"downstream declared seat W211 (bm-c, seat-published r849, "
            f"MSG-20261011-0350) pending -- not an upstream dep")
cfg_lines = [
 f'{CFG_I}210: {{"batch": "PERPETUAL-N1-W210",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W210_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND TENTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "TAKEOVER FACE: seat published=reserved by bm-b (MSG-20261011-0319, "
 "probe ADMIT receipt @ " + w210_receipt_sha[:10] + "), bm-b armed lane "
 "stalled (hb-stall 94min >> 20min GM re-assignment gate; W209 finalize "
 "landed 4h+ unexecuted; engine idle) -> bm-c executes per the W208 "
 "takeover r885 precedent + CEO fill-order standing 2026-10-08 ~23:5x "
 "RE-ISSUED 2026-10-10 ~23:1x + O-20260924-1730 claim-and-start same-round "
 "law; takeover notice MSG-2026-10-12-0020 pushed to origin "
 + TAKEOVER_ORIGIN[:10] + " BEFORE this freeze (anti-double-burn, bm-b "
 "armed-lane yield requested); engine_owner bm-b -> bm-c, bands UNCHANGED "
 "R250 (bm-b probe ADMIT verbatim, never re-derived); prereg REBUILT "
 "machine-read in the takeover window (bm-b payload claim never landed "
 "on origin, git -S machine-checked, disclosed); own-series continuation "
 "per O-20260101-2355 sec.2 (first-free-number law after the REGISTERED "
 f"W209 row bm-c five-face freeze {w209_freeze_sha[:10]} (prereg {w209_prereg_sha[:10]}), "
 "SINGLE STATE zero seat gap W2..W209 all registered; " + fin_face + "; "
 "deletion-set EMPTY; delivery window = chain-order splice after the "
 "W209 five-face + W209 finalize product landed; zero merge at freeze "
 "delivery, zero --no-verify; single-window derive -- r812 merged the "
 "gate legs INTO the pre-seat probe; parity N/A honest), "
 "engine_owner=bm-c, wave 210: "
 "A = FIRST-CLEAN past the registered W209 B band (the "
 f"arithmetic continuation {fmt(w209_a_tail + 1)}..{fmt(w209_a_tail + 2_000)} is REFUSED at its "
 f"own start by the W209 B band {fmt(W209['b_exit'][0])}..{fmt(w209_b_tail)}, exactly as "
 "the W209 seat leg4 succession "
 "projection notes anticipated; honest forward walk hops=1 -> "
 f"{fmt(a_lo)}..{fmt(a_hi)}; A base == prior-wave B tail+1 "
 "machine-checkable = A-hops-prior-B staircase SEVENTIETH "
 "instance, E36 card (probe receipt leg1 machine-read ordinal); "
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN "
 "past the own-wave A window (the arithmetic continuation "
 f"{fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the registered universe but lands "
 f"INSIDE the W210 A band window {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual "
 "exclusion, W141 precedent, leg2 law -- the walk with the "
 f"own-wave A window reserved jumps to {fmt(b_lo)}, first-clean "
 f"{fmt(b_lo)}..{fmt(b_hi)} hops=1, non-rotational r587 forward-monotone walk; "
 "B base == own-wave A tail+1 machine-checkable; cross-window "
 "convergence with the W209 seat leg4 succession projection "
 "notes -- all MANDATORY notes honored (post-W209 universe "
 "re-derive + own-wave A reservation); ADMIT receipt "
 "results/_w210bmb_20261011_probe_receipt.json + "
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a "
 "ADMIT convention); W211+ projection per this window gate: "
 f"A naive first-clean {rec['legs']['leg4']['W211p_A']} CLEAN / B naive first-clean "
 f"{rec['legs']['leg4']['W211p_B']} CLEAN -- naive B lands INSIDE the naive A window and "
 f"the registered W210 B band {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W211 A window; "
 "W211+ freezer MUST re-derive on the post-W210 universe AND "
 "reserve the own-wave A window when deriving B (W141 precedent, "
 "leg2 law, E36 staircase card) -- CONVERGENCE ALREADY PROVEN: the "
 "published W211 seat (bm-c, MSG-20261011-0350) re-derived A "
 "479_004..481_003 hopping the W210 declared B band + B "
 "481_004..481_203; " + fin_face + " -- the finalize "
 "merge loop still derives the wave set from registry keys at "
 "run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W210 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past the registered W209 B band; arithmetic {fmt(w209_a_tail + 1)}..{fmt(w209_a_tail + 2_000)} REFUSED at own start by the W209 B band {fmt(W209["b_exit"][0])}..{fmt(w209_b_tail)}; hops=1; A-hops-prior-B staircase SEVENTIETH instance, E36 card; ordinal machine-read SEVENTIETH per probe receipt; TAKEOVER r898 bands unchanged R250)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W210 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN past the own-wave A window; arithmetic {fmt(a_lo)}..{fmt(a_lo + 199)} lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w210", "out_name": "n1_w210_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},  # takeover r898: bm-b -> bm-c per GM re-assignment gate; bands unchanged R250',
]
cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('210: {"batch": "PERPETUAL-N1-W210"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W210 materializer face (bm-c loop TAKEOVER five-face freeze splice,",
 "    #     own-series law under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's fortieth owned per machine-derive (engine_owner==bm-c",
 "    #     rows 39 + candidate; TAKEOVER FACE: seat published=reserved by bm-b",
 "    #     03:19 (MSG-20261011-0319, probe ADMIT receipt @ " + w210_receipt_sha[:10] + "), bm-b",
 "    #     hb-stall 94min >> 20min GM re-assignment gate + armed lane unexecuted",
 "    #     4h+ past the W209 finalize landing -> engine_owner bm-b->bm-c per the",
 "    #     W208 takeover r885 precedent; takeover notice MSG-2026-10-12-0020",
 "    #     pushed to origin " + TAKEOVER_ORIGIN + " BEFORE this freeze (anti-double-burn);",
 "    #     bands UNCHANGED R250 (bm-b probe ADMIT verbatim); prereg REBUILT",
 "    #     machine-read in the takeover window (bm-b payload claim never landed",
 "    #     on origin, git -S machine-checked, disclosed); wave 210 = first free",
 f"    #     number after the REGISTERED W209 row (bm-c five-face freeze {w209_freeze_sha[:10]}) --",
 "    #     SINGLE STATE zero seat gap (W2..W209 all registered).",
 "    #     TWO HUNDRED AND TENTH engine wave BY",
 "    #     MACHINE-DERIVE (engine_owner rows 199 + candidate; gate",
 "    #     leg0 machine output governs per r359 law; probe receipt leg0",
 "    #     bmb_ordinal=42 seat-time face disclosed, takeover re-derives own",
 "    #     ordinal honestly per r587/r359).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w210bmb_20261011_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W210 bands were never assigned).",
 "    _set_wave(210)",
 "    try:",
 '        assert WAVE_CONFIGS[209]["a_seed_base"] == pf.N1_BANDS[209]["a"][0], \\',
 '            "W210 upstream W209 mirror drift (a)"',
 "        assert WAVE_CONFIGS[209][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[209]["b_exit"][0], "W210 upstream W209 mirror drift (b)"',
 "        assert WAVE_CONFIGS[209].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[209].get("engine_owner") == "bm-c", \\',
 '            "W210 upstream W209 engine_owner mirror drift (law-mirror parity)"',
 "        w209_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w209_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w209_a & w209_b), "W210 upstream W209 A/B band overlap"',
 '        assert not (w209_a & reg_ints) and not (w209_b & reg_ints), \\',
 '            "W210 upstream W209 hits SEED_REGISTRY"',
 "        w210_a = {476_804 + j for j in range(A_N)}",
 "        w210_b = {478_804 + j for j in range(B_N)}",
 '        assert not (w210_a & w210_b), "W210 A/B band overlap"',
 "        assert not (w210_a & reg_ints) and not (w210_b & reg_ints), \\",
 '            "W210 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w210_a), ("B", w210_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W210 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W210 {nm} hits W1"',
 '            assert not (band & probes), f"W210 {nm} hits probe seeds"',
]
w209_leg = [
 f'        assert pf.N1_BANDS[209] == {{"a": ({fmt(W209["a"][0])}, {fmt(W209["a"][1])}),',
 f'                                    "b_exit": ({fmt(W209["b_exit"][0])}, {fmt(W209["b_exit"][1])}),',
 '                                    "engine_owner": "bm-c"}, \\',
 '            "registered W209 row parity drift (r307; bm-c five-face freeze r886)"',
]
tail = [
 "        # prior-wave disjointness W2..W209 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 210):",
 '            assert not (w210_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W210 A hits W{wprev}\"",
 '            assert not (w210_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W210 B hits W{wprev}\"",
 "        n3r1_used210 = set(range(70_000, 70_006))",
 "        assert not (w210_a & n3r1_used210) and not (w210_b & n3r1_used210), \\",
 '            "W210 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w210_a & lfc_actual12) and not (w210_b & lfc_actual12), \\",
 '            "W210 bands must clear the lfc actual draw range"',
 "        assert not (w210_a & options_actual12) and \\",
 "            not (w210_b & options_actual12), \\",
 '            "W210 bands must clear the options_wave2 actual draw range"',
 "        # band facts (law sec.4 W210 row): A = FIRST-CLEAN past",
 "        # the registered W209 B band (the arithmetic continuation",
 f"        # {fmt(w209_a_tail + 1)}..{fmt(w209_a_tail + 2_000)} is REFUSED at its own start by the W209 B band",
 f"        # {fmt(W209['b_exit'][0])}..{fmt(w209_b_tail)}, exactly as the W209 seat leg4",
 "        # succession projection notes anticipated; honest",
 f"        # forward walk hops=1 lands {fmt(a_lo)}..{fmt(a_hi)}; A base ==",
 f"        # prior-wave B tail+1 ({fmt(w209_b_tail)}+1) machine-checkable --",
 "        # A-hops-prior-B staircase SEVENTIETH instance, E36 card;",
 "        # non-rotational r587 forward-monotone walk);",
 "        # B = FIRST-CLEAN past the own-wave A window (the",
 f"        # arithmetic continuation {fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the",
 f"        # registered universe but lands INSIDE the W210 A band window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual exclusion (W141 precedent,",
 "        # leg2 law) -- the walk with the own-wave A window reserved",
 f"        # jumps to {fmt(b_lo)} and lands {fmt(b_lo)}..{fmt(b_hi)}, hops=1,",
 "        # non-rotational r587 forward-monotone walk; B base ==",
 f"        # own-wave A tail+1 ({fmt(a_hi)}+1) machine-checkable;",
 "        # cross-window convergence with the W209 seat leg4",
 "        # succession projection notes -- all MANDATORY notes",
 "        # honored (post-W209 universe re-derive + own-wave A",
 "        # reservation when deriving B); takeover face: bands",
 "        # unchanged R250 vs the bm-b seat ADMIT receipt;",
 "        # seat MSG-0319 tail, re-derived).",
 f'        assert WAVE_CONFIGS[210]["a_seed_base"] == {a_lo} == {w209_b_tail} + 1, (',
 '            "W210 A must be the first-clean window past the registered "',
 '            "W209 B band tail (arithmetic continuation REFUSED at its own "',
 '            "start by the W209 B band, exactly as the W209 seat leg4 "',
 '            "succession projection notes anticipated; honest forward walk "',
 '            "hops=1; A base == prior-wave B tail+1 machine-checkable "',
 '            "= A-hops-prior-B staircase SEVENTIETH instance, E36 card")',
 f"        arith_a210 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a210 & reg_ints), \\",
 '            "W210 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
 f'        assert WAVE_CONFIGS[210]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
 '            "W210 B must be the first-clean window past the own-wave A "',
 '            "band tail (arithmetic continuation CLEAN on the registered "',
 '            "universe but lands INSIDE the W210 A band window; "',
 '            "same-freeze mutual exclusion (W141 precedent, leg2 law) -- "',
 '            "the walk with the own-wave A window reserved jumps, "',
 '            "first-clean hops=1, non-rotational r587 forward-monotone "',
 '            "walk; B base == own-wave A tail+1 machine-checkable")',
 f"        arith_b210 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b210 & reg_ints), \\",
 '            "W210 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
 "        assert not (arith_b210 & arith_a210), \\",
 '            "W210 A/B same-freeze mutual exclusion (B hops past own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W210-SHARD-0\",",
 '                                          "n1w210-0of12"), "W210 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W210-SHARD-11",',
 '                                           "n1w210-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w210\") and OUT.endswith(",
 '            "n1_w210_results.json"), "W210 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 210):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W210 shard dir collides with W{wprev}"',
 "        # W210 finalize cumulative deps: W17..W209 outputs ALL PRESENT",
 f"        # (landed net chain head {w209_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 210):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W210 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 210 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W209 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 210) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 210)], \\",
 '            "W210 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W209 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W210_PREREG.md")), \\',
 '            "W210 per-wave prereg missing (materializer requirement)"',
 '        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"',
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w209_leg) + EOL + EOL.join(tail) + EOL
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W210 materializer face [same guard set, dep=W17..W209 "',
 f'          "outputs ALL PRESENT (landed net chain head {w209_total} = W209 bm-c finalize one-pass r886, K={w209_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND TENTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-c\'s fortieth owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 39 + candidate) TAKEOVER FACE: seat registered by bm-b, "',
 '          "engine_owner bm-b->bm-c per GM re-assignment (hb-stall 94min >> 20min gate; CEO fill-order standing; "',
 '          "takeover notice MSG-2026-10-12-0020 @ c64bc2287 pre-pushed; bands unchanged R250), "',
 '          "A=FIRST-CLEAN past the registered W209 B band (staircase "',
 '          "SEVENTIETH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
 '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
 '          "mutual exclusion, hops=1), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w210bmb_20261011_probe_receipt.json, law sec.4 W210 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]
old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W210"') == 1
assert n1_t4.count("# --- W210 materializer face") == 1     # block header
assert n1_t4.count('"+ W210 materializer face') == 1        # print fragment
assert n1_t4.count('210: {"batch": "PERPETUAL-N1-W210"') == 1
assert pf_t2.count('    210: {"a"') == 1
assert pf_t2.count('    209: {"a"') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('    # --- W209 materializer face') == 1  # prior block kept
assert n1_t4.count('"PERPETUAL-N1-W210-SHARD-0"') == 1
assert n1_t4.count('f"W210 A hits W{wprev}"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[209] == {{"a": ({fmt(W209["a"][0])}, {fmt(W209["a"][1])}),') == 1
assert pf_t2.count("takeover r898") == 1  # the new W210 row owner comment
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
  "machine": "bm-c", "wave": 210,
  "phase": "five-face freeze chain-order splice -- TAKEOVER FACE (bm-b armed lane stalled, executed by bm-c per GM re-assignment + CEO fill-order standing, W208 takeover r885 precedent)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w210bmb_20261011_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "w209_upstream": {"freeze_sha": w209_freeze_sha, "prereg_sha": w209_prereg_sha,
                    "ledger_total": w209_total, "merged_n": w209_merged_n},
  "w208_transitive": {"finalize_product": "results/perpetual_faces/n1_w208_results.json present (belt-and-braces gate)"},
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "takeover": {
    "seat_registered_by": "bm-b r857 (probe ADMIT receipt @ d550bf11c)",
    "gate": "hb-stall 94min >> 20min GM re-assignment gate (fleet/machines/bm-b.json last_seen 2026-10-11T22:47:19+08:00, r898 fresh read) + armed lane unexecuted 4h+ past W209 finalize (10-11 19:56) with engine idle (burns_active=[] queue_next=[])",
    "law": "GM re-assignment + CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x + O-20260924-1730 same-round claim-and-start",
    "precedent": "W208 takeover r885 (bm-a->bm-c, commit 4682d6b19, bands unchanged R250, broadcast MSG-20261011-1931-bmc)",
    "notice": "MSG-2026-10-12-0020-bmc-ALL-w210-takeover pushed to origin " + TAKEOVER_ORIGIN + " BEFORE the freeze (anti-double-burn; bm-b armed-lane yield requested)",
    "bands_unchanged": "R250 respected: bm-b probe ADMIT bands verbatim (476_804..478_803 / 478_804..479_003), zero re-derive",
    "prereg_rebuild": "bm-b seat MSG payload claimed per-wave prereg+freeze pushed -- origin never contained them (git log -S W210 research/ zero hits, machine-checked); prereg REBUILT machine-read in the takeover window (upstream W209 actuals + probe receipt verbatim)",
  },
  "prereg_bundle": {"prereg_sha": w210_prereg_sha, "probe_receipt_sha": w210_receipt_sha},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bmc_rows_live": len(bmc_rows_live),
                    "bmb_rows_live": len(bmb_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmb_ordinal_face": 42,
                    "note": "TAKEOVER re-derive: bm-c rows+1 = 40th own wave per live derive (r587/r359 governs); the bm-b seat-time probe leg0 bmb_ordinal=42 face disclosed honestly -- the seat was bm-b's 42nd at publish time, ownership transferred r898"},
  "parity_section": {"source": "W209 block physical bytes (own block, structure known)", "bytes": len(par_sec),
                     "row_asserts": par_sec.count("assert pf.N1_BANDS["),
                     "note": "r858 absorb generation full-span estate W138..W206 (69 rows); W210 block re-grows to 70 rows ending at W209 (w209_leg)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1},
}
open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w209_upstream")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> ignition verify (2-cycle n1_w210 growth)")
