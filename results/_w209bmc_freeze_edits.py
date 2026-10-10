# -*- coding: utf-8 -*-
# 2026-10-11 03:2x bm-c: W209 five-face freeze splice editor (PREPARED pre-landing,
# EXECUTED after the bm-a W208 five-face + W208 finalize product land on origin --
# chain-order law + tail dep assert require the prior wave's results file).
# Lineage: _w206bmc_freeze_edits.py pattern (proven live-fire freeze 68ba08347)
# + r787 preflight law + r609 origin-verbatim base + r761 programmatic quote
# wrapping + r909 physical-byte anchors + r838 per-file EOL detection.
# Zero hardcoded upstream band values: ALL W208 facts machine-derived from the
# LIVE pf import at freeze time (bm-a's registered row), cross-checked against
# the committed ADMIT receipt (results/_w209bmc_20261011_probe_receipt.json)
# which was derived on the W207-registered + W208-declared-injected universe.
# If bm-a's REGISTERD W208 bands differ from the declared face, the staircase
# asserts fail LOUD (fail-closed) -> honest re-probe required, never auto-accept.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w209bmc_20261011_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w209bmc_freeze_receipt.json")
SEAT_MSG = "MSG-20261011-0301-bmc-w209-seat.md"
SEAT_ORIGIN = "e989c03eb"
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

# ---------- gate 0.5: W208 five-face landed + W208 finalize product present ----------
# (chain-order precondition; W207 finalize is the transitive dep of the W208
# freeze and is belt-and-braces checked here + enforced by the block's
# cumulative-deps assert range(17, 209) at selftest time)
W208 = dict(pf_mod.N1_BANDS.get(208) or {})
assert W208.get("engine_owner") == "bm-a", \
    f"W208 row not landed as declared (engine_owner != bm-a): {W208} -- bm-a five-face freeze missing"
w208_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w208_results.json")
assert os.path.exists(w208_out_path), "W208 finalize product missing (n1_w208_results.json) -- chain dep not met"
w207_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w207_results.json")
assert os.path.exists(w207_out_path), "W207 finalize product missing (transitive chain dep) -- abort"
w208_out = json.load(open(w208_out_path, encoding="utf-8"))
w208_led = (w208_out.get("science_gates") or {}).get("ledger") or {}
w208_total = w208_led.get("total")
w208_merged_n = None
try:
    w208_merged_n = w208_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '208: {"a"', "--", "scripts/perpetual_faces.py")
w208_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W208_PREREG.md")
w208_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face bmc_ordinal=39 is a +2 mechanical carryover vs rows+1=38 --
# live derive at freeze time governs per r587, probe face disclosed in prereg)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 198 and len(bmc_rows_live) == 37, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bmc={len(bmc_rows_live)} (expect 198/37 post-W208)"
print(f"gate0.5 OK: W208 landed (freeze {w208_freeze_sha[:10]}), W208+finalW207 finalize products present "
      f"(ledger head {w208_total}, merged n={w208_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-c rows {len(bmc_rows_live)} + candidate (38th own wave)")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
A = rec["bands"]["A"]; B = rec["bands"]["B"]
a_lo, a_hi = (int(x) for x in A.split("_"))
b_lo, b_hi = (int(x) for x in B.split("_"))
leg1 = rec["legs"]["leg1"]
assert [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"], "receipt band mismatch"
assert (a_lo, a_hi) == (474_604, 476_603) and (b_lo, b_hi) == (476_604, 476_803), \
    f"W209 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w208_b_tail = W208["b_exit"][1]      # registered W208 row b_exit hi (pf import, live)
w208_a_tail = W208["a"][1]           # registered W208 row A hi (pf import, live)
assert w208_b_tail + 1 == a_lo and a_hi + 1 == b_lo, "staircase base relations broken"
# the REFUSED arithmetic continuation starts at prior-wave A-tail+1 (== W208 B-base),
# machine-derived from the LIVE registered row, never transcribed.
assert w208_a_tail + 1 == W208["b_exit"][0], "W208 A-tail+1 != W208 B-base (registered row in-wave relation)"
assert [w208_a_tail + 1, w208_a_tail + 2_000] == leg1["ARITH_A"], \
    f"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w208_a_tail + 1, w208_a_tail + 2_000]} != {leg1['ARITH_A']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W209_PREREG.md")
w209_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w209bmc_20261011_probe_receipt.json")
w209_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W209 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W209_PREREG.md"],
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

def fmt(n):  # 474604 -> "474_604"
    return f"{n // 1000}_{n % 1000:03d}"

# ---------- extract parity section (physical bytes, never re-typed) ----------
a6 = '    # --- W208 materializer face'
a4 = '    # --- T-141 s2 lane face'
w208_start = n1_t.find(a6); t141_pos = n1_t.find(a4)
assert w208_start > 0 and t141_pos > w208_start, "W208 materializer block not found (bm-a freeze not landed?)"
blk = n1_t[w208_start:t141_pos]
par_marker = "        # registered row parity (r307 pinned constants, recent estate)"
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state: all", blk)
assert n1_t.count(par_marker) >= 1 and m_disj, "parity markers not found in W208 block"
# marker->disj span = 50 recent estate rows + 1 upstream W207 row leg = 51 asserts
# (bm-b r852 empirical finding, generation-stable structure). Cut the PURE estate
# segment at the W207-leg assert line start (exactly the 50 estate rows) so the
# W209 block re-grows to 50 estate + own w208_leg = 51.
par_full = blk[blk.find(par_marker):m_disj.start()]
m207 = re.search(r" *assert pf\.N1_BANDS\[207\] ==", par_full)
assert m207, "upstream W207 row leg not found inside W208 parity span"
par_sec = par_full[:m207.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
assert par_sec.count("assert pf.N1_BANDS[") == 50, \
    f"estate segment row asserts {par_sec.count('assert pf.N1_BANDS[')} != 50 (generation-stable law)"
assert par_full.count("assert pf.N1_BANDS[") == 51, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 51 (50 estate + 1 W207 leg)"

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '208: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W208_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W208["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '208: {"a"', PF_EOL)
ROWC_I = line_indent(pf_t,  '"engine_owner": "bm-a"},', PF_EOL)

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W209 (bm-c loop five-face freeze splice, seat",
"    # MSG-20261011-0301-bmc-w209-seat pushed to origin " + SEAT_ORIGIN,
"    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen",
"    # commit " + w209_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W209_PREREG.md,",
"    # probe results/_w209bmc_20261011_probe_receipt.json @ " + w209_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-a W208 five-face (freeze " + w208_freeze_sha[:10] + ") + W208",
"    # finalize product landed (n1_w208_results.json present, ledger",
"    # head " + str(w208_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W209 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w209bmc_20261011_probe_receipt.json: A = FIRST-CLEAN",
"    # past the registered W208 B band (arithmetic continuation",
"    # " + fmt(w208_a_tail + 1) + ".." + fmt(w208_a_tail + 2_000) + " REFUSED at its own start by the W208 B band",
"    # " + fmt(W208["b_exit"][0]) + ".." + fmt(w208_b_tail) + ", exactly as the W208 seat leg4",
"    # projection anticipated;",
"    # honest forward walk hops=1 -> " + fmt(a_lo) + ".." + fmt(a_hi) + ", non-rotational",
"    # r587 forward-monotone walk; A base == prior-wave B tail+1",
"    # (" + fmt(w208_b_tail) + "+1) machine-checkable -- A-hops-prior-B staircase",
"    # SIXTY-NINTH instance, E36 card (probe receipt leg1 A_semantics",
"    # machine-read ordinal, never transcribed);",
"    # B = FIRST-CLEAN past the own-wave A window (arithmetic",
"    # continuation " + fmt(a_lo) + ".." + fmt(a_lo + 199) + " CLEAN on the registered",
"    # universe but lands INSIDE the W209 A band window " + fmt(a_lo) + ".." + fmt(a_hi) + " --",
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
"    # W210+ projection (gate-derived pre-seat probe leg4, pre-W209",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W210p_A"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " /",
"    # B naive first-clean " + rec["legs"]["leg4"]["W210p_B"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " -- naive B lands",
"    # INSIDE the naive A window and the registered W209 B band",
"    # " + fmt(b_lo) + ".." + fmt(b_hi) + " will refuse the naive W210 A window; W210 freezer",
"    # MUST re-derive on the post-W209 universe AND reserve the",
"    # own-wave A window when deriving B (W141 precedent, leg2 law,",
"    # E36 staircase card; never transcribe r587).",
"    # NOT a re-pick (R250: W209 bands were never assigned).",
])
pf_row = (f'{ROW_I}209: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'209: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, ('         "engine_owner": "bm-a"},' + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = ('         "engine_owner": "bm-a"},' + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W208 finalize ALL LANDED (W208 finalize product present at splice, "
            f"net chain head {w208_total} machine-read, merged pool K={w208_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition")
cfg_lines = [
 f'{CFG_I}209: {{"batch": "PERPETUAL-N1-W209",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W209_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND NINTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W208 row bm-a five-face freeze ",
 f"{w208_freeze_sha[:10]} (prereg {w208_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W208 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261011-0301-bmc-w209-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG; prereg + pre-seat probe script + probe receipt ",
 "frozen commit " + w209_prereg_sha[:10] + " @ receipt " + w209_receipt_sha[:10] + "); ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W208 five-face + W208 finalize product landed ",
 "(prepared pre-landing by the bm-c loop window under ",
 "the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c, wave 209: ",
 "A = FIRST-CLEAN past the registered W208 B band (the ",
 f"arithmetic continuation {fmt(w208_a_tail + 1)}..{fmt(w208_a_tail + 2_000)} is REFUSED at its ",
 f"own start by the W208 B band {fmt(W208['b_exit'][0])}..{fmt(w208_b_tail)}, exactly as ",
 "the W208 seat leg4 succession ",
 "projection notes anticipated; honest forward walk hops=1 -> ",
 f"{fmt(a_lo)}..{fmt(a_hi)}; A base == prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase SIXTY-NINTH ",
 "instance, E36 card (probe receipt leg1 machine-read ordinal); ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN ",
 "past the own-wave A window (the arithmetic continuation ",
 f"{fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the registered universe but lands ",
 f"INSIDE the W209 A band window {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual ",
 "exclusion, W141 precedent, leg2 law -- the walk with the ",
 f"own-wave A window reserved jumps to {fmt(b_lo)}, first-clean ",
 f"{fmt(b_lo)}..{fmt(b_hi)} hops=1, non-rotational r587 forward-monotone walk; ",
 "B base == own-wave A tail+1 machine-checkable; cross-window ",
 "convergence with the W208 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W208 universe ",
 "re-derive + own-wave A reservation); ADMIT receipt ",
 "results/_w209bmc_20261011_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W210+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W210p_A']} CLEAN / B naive first-clean ",
 f"{rec['legs']['leg4']['W210p_B']} CLEAN -- naive B lands INSIDE the naive A window and ",
 f"the registered W209 B band {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W210 A window; ",
 "W210+ freezer MUST re-derive on the post-W209 universe AND ",
 "reserve the own-wave A window when deriving B (W141 precedent, ",
 "leg2 law, E36 staircase card); " + fin_face + " -- the finalize ",
 "merge loop still derives the wave set from registry keys at ",
 "run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W209 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past the registered W208 B band; arithmetic {fmt(w208_a_tail + 1)}..{fmt(w208_a_tail + 2_000)} REFUSED at own start by the W208 B band {fmt(W208["b_exit"][0])}..{fmt(w208_b_tail)}; hops=1; A-hops-prior-B staircase SIXTY-NINTH instance, E36 card; ordinal machine-read SIXTY-NINTH per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W209 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN past the own-wave A window; arithmetic {fmt(a_lo)}..{fmt(a_lo + 199)} lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w209", "out_name": "n1_w209_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]
cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('209: {"batch": "PERPETUAL-N1-W209"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W209 materializer face (bm-c loop five-face freeze splice,",
 "    #     own-series law under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's thirty-eighth owned per machine-derive (engine_owner==bm-c",
 "    #     rows 37 + candidate); wave 209 = first free number after the",
 f"    #     REGISTERED W208 row (bm-a five-face freeze {w208_freeze_sha[:10]}) --",
 "    #     SINGLE STATE zero seat gap (W2..W208 all registered). Seat",
 "    #     published=reserved MSG-20261011-0301-bmc-w209-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG; prereg + pre-seat probe script + probe receipt",
 "    #     frozen commit " + w209_prereg_sha[:10] + "; deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W208 five-face + W208 finalize",
 "    #     product landed; zero --no-verify; the W209 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND NINTH engine wave BY",
 "    #     MACHINE-DERIVE (engine_owner rows 198 + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w209bmc_20261011_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W209 bands were never assigned).",
 "    _set_wave(209)",
 "    try:",
 '        assert WAVE_CONFIGS[208]["a_seed_base"] == pf.N1_BANDS[208]["a"][0], \\',
 '            "W209 A band drift vs law mirror"',
 "        assert WAVE_CONFIGS[208][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[208]["b_exit"][0], "W209 B band drift vs law mirror"',
 "        assert WAVE_CONFIGS[208].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[208].get("engine_owner") == "bm-a", \\',
 '            "W209 engine_owner drift (law mirror parity)"',
 "        w208_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w208_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w208_a & w208_b), "W209 A/B band overlap"',
 "        assert not (w208_a & reg_ints) and not (w208_b & reg_ints), \\",
 '            "W209 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w208_a), ("B", w208_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W209 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W209 {nm} hits W1"',
 '            assert not (band & probes), f"W209 {nm} hits probe seeds"',
]
w208_leg = [
 f'        assert pf.N1_BANDS[208] == {{"a": ({fmt(W208["a"][0])}, {fmt(W208["a"][1])}),',
 f'                                    "b_exit": ({fmt(W208["b_exit"][0])}, {fmt(W208["b_exit"][1])}),',
 '                                    "engine_owner": "bm-a"}, \\',
 '            "registered W208 row parity drift (r307; bm-a five-face freeze)"',
]
tail = [
 "        # prior-wave disjointness W2..W208 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 209):",
 '            assert not (w208_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W209 A hits W{wprev}\"",
 '            assert not (w208_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W209 B hits W{wprev}\"",
 "        n3r1_used209 = set(range(70_000, 70_006))",
 "        assert not (w208_a & n3r1_used209) and not (w208_b & n3r1_used209), \\",
 '            "W209 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w208_a & lfc_actual12) and not (w208_b & lfc_actual12), \\",
 '            "W209 bands must clear the lfc actual draw range"',
 "        assert not (w208_a & options_actual12) and \\",
 "            not (w208_b & options_actual12), \\",
 '            "W209 bands must clear the options_wave2 actual draw range"',
 "        # band facts (law sec.4 W209 row): A = FIRST-CLEAN past",
 "        # the registered W208 B band (the arithmetic continuation",
 f"        # {fmt(w208_a_tail + 1)}..{fmt(w208_a_tail + 2_000)} is REFUSED at its own start by the W208 B band",
 f"        # {fmt(W208['b_exit'][0])}..{fmt(w208_b_tail)}, exactly as the W208 seat leg4",
 "        # succession projection notes anticipated; honest",
 f"        # forward walk hops=1 lands {fmt(a_lo)}..{fmt(a_hi)}; A base ==",
 f"        # prior-wave B tail+1 ({fmt(w208_b_tail)}+1) machine-checkable --",
 "        # A-hops-prior-B staircase SIXTY-NINTH instance, E36 card;",
 "        # non-rotational r587 forward-monotone walk);",
 "        # B = FIRST-CLEAN past the own-wave A window (the",
 f"        # arithmetic continuation {fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the",
 f"        # registered universe but lands INSIDE the W209 A band window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual exclusion (W141 precedent,",
 "        # leg2 law) -- the walk with the own-wave A window reserved",
 f"        # jumps to {fmt(b_lo)} and lands {fmt(b_lo)}..{fmt(b_hi)}, hops=1,",
 "        # non-rotational r587 forward-monotone walk; B base ==",
 f"        # own-wave A tail+1 ({fmt(a_hi)}+1) machine-checkable;",
 "        # cross-window convergence with the W208 seat leg4",
 "        # succession projection notes -- all MANDATORY notes",
 "        # honored (post-W208 universe re-derive + own-wave A",
 "        # reservation when deriving B);",
 "        # seat MSG-0301 tail, re-derived).",
 f'        assert WAVE_CONFIGS[209]["a_seed_base"] == {a_lo} == {w208_b_tail} + 1, (',
 '            "W209 A must be the first-clean window past the registered "',
 '            "W208 B band tail (arithmetic continuation REFUSED at its own "',
 '            "start by the W208 B band, exactly as the W208 seat leg4 "',
 '            "succession projection notes anticipated; honest forward walk "',
 '            "hops=1; A base == prior-wave B tail+1 machine-checkable "',
 '            "= A-hops-prior-B staircase SIXTY-NINTH instance, E36 card)")',
 f"        arith_a209 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a209 & reg_ints), \\",
 '            "W209 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
 f'        assert WAVE_CONFIGS[209]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
 '            "W209 B must be the first-clean window past the own-wave A "',
 '            "band tail (arithmetic continuation CLEAN on the registered "',
 '            "universe but lands INSIDE the W209 A band window; "',
 '            "same-freeze mutual exclusion (W141 precedent, leg2 law) -- "',
 '            "the walk with the own-wave A window reserved jumps, "',
 '            "first-clean hops=1, non-rotational r587 forward-monotone "',
 '            "walk; B base == own-wave A tail+1 machine-checkable)")',
 f"        arith_b209 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b209 & reg_ints), \\",
 '            "W209 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
 "        assert not (arith_b209 & arith_a209), \\",
 '            "W209 A/B same-freeze mutual exclusion (B hops past own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W209-SHARD-0\",",
 '                                          "n1w209-0of12"), "W209 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W209-SHARD-11",',
 '                                           "n1w209-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w209\") and OUT.endswith(",
 '            "n1_w209_results.json"), "W209 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 209):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W209 shard dir collides with W{wprev}"',
 "        # W209 finalize cumulative deps: W17..W208 outputs ALL PRESENT",
 f"        # (landed net chain head {w208_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 209):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W209 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 209 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W208 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 209) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 209)], \\",
 '            "W209 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W208 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W209_PREREG.md")), \\',
 '            "W209 per-wave prereg missing (materializer requirement)"',
 '        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"',
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w208_leg) + EOL + EOL.join(tail) + EOL
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W209 materializer face [same guard set, dep=W17..W208 "',
 f'          "outputs ALL PRESENT (landed net chain head {w208_total} = W208 bm-a finalize one-pass, K={w208_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND NINTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-c\'s thirty-eighth owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 37 + candidate), "',
 '          "A=FIRST-CLEAN past the registered W208 B band (staircase "',
 '          "SIXTY-NINTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
 '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
 '          "mutual exclusion, hops=1), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w209bmc_20261011_probe_receipt.json, law sec.4 W209 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]
old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W209"') == 1
assert n1_t4.count("# --- W209 materializer face") == 1     # block header
assert n1_t4.count('"+ W209 materializer face') == 1        # print fragment
assert n1_t4.count('209: {"batch": "PERPETUAL-N1-W209"') == 1
assert pf_t2.count('    209: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W209-SHARD-0"') == 1
assert n1_t4.count('f"W209 A hits W{wprev}"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[208] == {{"a": ({fmt(W208["a"][0])}, {fmt(W208["a"][1])}),') == 1
assert n1_t4.count('    # --- W208 materializer face') == 1  # prior block kept
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
  "machine": "bm-c", "wave": 209,
  "phase": "five-face freeze chain-order splice (prepared pre-landing, executed post-W208-finalize)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w209bmc_20261011_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "w208_upstream": {"freeze_sha": w208_freeze_sha, "prereg_sha": w208_prereg_sha,
                    "ledger_total": w208_total, "merged_n": w208_merged_n},
  "w207_transitive": {"finalize_product": "results/perpetual_faces/n1_w207_results.json present (belt-and-braces gate)"},
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w209_prereg_sha, "probe_receipt_sha": w209_receipt_sha},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmc_ordinal_face": 39,
                    "note": "probe leg0 bmc_ordinal=39 face = +2 mechanical carryover vs rows+1=38 convention (W207 precedent bmb_ordinal=rows+1); live derive at freeze time governs per r587/r359, disclosed in prereg sec.0"},
  "parity_section": {"source": "W208 block physical bytes", "bytes": len(par_sec),
                     "row_asserts": par_sec.count("assert pf.N1_BANDS[")},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {"t141_marker_kept": 1, "w208_block_kept": 1},
}
open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w208_upstream")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> ignition verify (2-cycle n1_w209 growth)")
