# -*- coding: utf-8 -*-
# 2026-10-10 23:5x bm-c: W206 five-face freeze splice editor (PREPARED pre-landing,
# EXECUTED after the bm-a W205 five-face + W205 finalize product land on origin --
# chain-order law + tail dep assert require the prior wave's results file).
# Lineage: _r837bmc_w204_freeze_edits.py pattern + r787 preflight law + r609
# origin-verbatim base + r761 programmatic quote wrapping + r909 physical-byte
# anchors. Zero hardcoded band values: all band facts machine-derived from the
# committed ADMIT receipt (results/_w206bmc_20261010_probe_receipt.json) and the
# LIVE pf import (W205 registered row read at freeze time, never transcribed).
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w206bmc_20261010_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w206bmc_freeze_receipt.json")
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

# ---------- gate 0.5: W205 landed + finalize product present (chain-order precondition) ----------
W205 = dict(pf_mod.N1_BANDS.get(205) or {})
assert W205.get("a") == (465_804, 467_803) and W205.get("b_exit") == (467_804, 468_003) \
    and W205.get("engine_owner") == "bm-a", f"W205 row not landed as declared: {W205}"
w205_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w205_results.json")
assert os.path.exists(w205_out_path), "W205 finalize product missing (n1_w205_results.json) -- chain dep not met"
w205_out = json.load(open(w205_out_path, encoding="utf-8"))
w205_led = (w205_out.get("science_gates") or {}).get("ledger") or {}
w205_total = w205_led.get("total")
w205_merged_n = None
try:
    w205_merged_n = w205_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '205: {"a"', "--", "scripts/perpetual_faces.py")
w205_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W205_PREREG.md")
w205_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
print(f"gate0.5 OK: W205 landed (freeze {w205_freeze_sha[:10]}), finalize product present (ledger head {w205_total}, merged n={w205_merged_n})")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
A = rec["bands"]["A"]; B = rec["bands"]["B"]
a_lo, a_hi = (int(x) for x in A.split("_"))
b_lo, b_hi = (int(x) for x in B.split("_"))
leg1 = rec["legs"]["leg1"]
assert [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"], "receipt band mismatch"
assert (a_lo, a_hi) == (468_004, 470_003) and (b_lo, b_hi) == (470_004, 470_203), \
    f"W206 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w205_b_tail = W205["b_exit"][1]      # registered W205 row b_exit hi (pf import)
w205_a_tail = W205["a"][1]           # registered W205 row A hi (pf import)
pri_b_tail = a_hi                    # own-wave A tail
assert w205_b_tail + 1 == a_lo and a_hi + 1 == b_lo, "staircase base relations broken"
# MSG-20261011-0120 fix 3: the REFUSED arithmetic continuation starts at
# prior-wave A-tail+1 (== W205 B-base), machine-derived, never transcribed.
assert w205_a_tail + 1 == W205["b_exit"][0], "W205 A-tail+1 != W205 B-base"
assert [w205_a_tail + 1, w205_a_tail + 2_000] == leg1["ARITH_A"], \
    f"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w205_a_tail + 1, w205_a_tail + 2_000]} != {leg1['ARITH_A']}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W206_PREREG.md"],
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

# ---------- read files, EOL (r838 law: runtime per-file detection, MSG-20261011-0120 fix 1) ----------
pf_b = open(PF, "rb").read(); pf_t = pf_b.decode("utf-8")
n1_b = open(N1, "rb").read(); n1_t = n1_b.decode("utf-8")

def detect_eol(t):
    """r838 law: per-file runtime EOL detection (repo files are pure LF as of
    the W205 landing era; never assume CRLF -- MSG-20261011-0120 finding 1)."""
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

def fmt(n):  # 468004 -> "468_004"
    return f"{n // 1000}_{n % 1000:03d}"

# ---------- extract parity section (physical bytes, never re-typed; MSG-20261011-0120 fix 2) ----------
a6 = '    # --- W205 materializer face'
a4 = '    # --- T-141 s2 lane face'
w205_start = n1_t.find(a6); t141_pos = n1_t.find(a4)
assert w205_start > 0 and t141_pos > w205_start, "W205 materializer block not found (bm-a freeze not landed?)"
blk = n1_t[w205_start:t141_pos]
par_marker = "        # registered row parity (r307 pinned constants, recent estate)"
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state: all", blk)
assert n1_t.count(par_marker) >= 1 and m_disj, "parity markers not found in W205 block"
# marker->disj span = 50 recent estate rows + 1 upstream W204 row leg = 51 asserts
# (bm-b r852 empirical finding). Cut the PURE estate segment at the W204-leg
# assert line start (exactly the 50 estate rows) so the W206 block re-grows to
# 50 estate + own w205_leg = 51, generation-stable structure.
par_full = blk[blk.find(par_marker):m_disj.start()]
m204 = re.search(r" *assert pf\.N1_BANDS\[204\] ==", par_full)
assert m204, "upstream W204 row leg not found inside W205 parity span"
par_sec = par_full[:m204.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
assert par_sec.count("assert pf.N1_BANDS[") == 50, \
    f"estate segment row asserts {par_sec.count('assert pf.N1_BANDS[')} != 50 (bm-b r852 finding: 50 estate rows)"
assert par_full.count("assert pf.N1_BANDS[") == 51, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 51 (50 estate + 1 W204 leg)"

# ---------- indent extraction (physical, not assumed; per-file EOL, MSG-20261011-0120 fix 1) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '205: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W205_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
MEM_I  = line_indent(n1_t, '"a_seed_base": 465_804', EOL)
ROW_I  = line_indent(pf_t,  '205: {"a"', PF_EOL)
ROWC_I = line_indent(pf_t,  '"engine_owner": "bm-a"},', PF_EOL)

# ---------- pf comment + row ----------
pf_comment = EOL.join([
"    # W206 (bm-c interactive five-face freeze splice, seat",
"    # MSG-20261010-2323-bmc-w206-seat pushed to origin e25629f7",
"    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen",
"    # commit 0620f78 (prereg research/PERPETUAL_N1_W206_PREREG.md,",
"    # probe results/_w206bmc_20261010_probe_receipt.json);",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
f"    # splice AFTER the bm-a W205 five-face (freeze {w205_freeze_sha[:10]}) + W205",
"    # finalize product landed (n1_w205_results.json present, ledger",
f"    # head {w205_total} machine-read at freeze time); zero --no-verify;",
"    # the W206 seat MSG sits in fleet/inbox/processed/ at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w206bmc_20261010_probe_receipt.json: A = FIRST-CLEAN",
"    # past the registered W205 B band (arithmetic continuation",
f"    # {fmt(w205_a_tail + 1)}..{fmt(469_803)} REFUSED at its own start by the W205 B band",
f"    # {fmt(W205['b_exit'][0])}..{fmt(w205_b_tail)}, exactly as the W205 seat leg4",
"    # projection + r956 W205 probe leg4 anticipated;",
f"    # honest forward walk hops=1 -> {fmt(a_lo)}..{fmt(a_hi)}, non-rotational",
"    # r587 forward-monotone walk; A base == prior-wave B tail+1",
f"    # ({fmt(w205_b_tail)}+1) machine-checkable -- A-hops-prior-B staircase",
"    # SIXTY-SIXTH instance, E36 card (probe receipt leg1 A_semantics",
"    # machine-read ordinal, never transcribed);",
"    # B = FIRST-CLEAN past the own-wave A window (arithmetic",
f"    # continuation {fmt(a_lo)}..{fmt(a_lo+199)} CLEAN on the registered",
f"    # universe but lands INSIDE the W206 A band window {fmt(a_lo)}..{fmt(a_hi)} --",
"    # same-freeze mutual exclusion (W141 precedent, leg2 law) --",
"    # the walk with the own-wave A window reserved jumps to",
f"    # {fmt(b_lo)} -> {fmt(b_lo)}..{fmt(b_hi)}, hops=1, non-rotational",
"    # r587 forward-monotone walk; B base == own-wave A tail+1",
f"    # ({fmt(a_hi)}+1) machine-checkable);",
"    # single-window derive (r812 merged the gate legs INTO the",
"    # pre-seat probe; dual-window parity N/A honest); scan face =",
"    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1",
"    # used-seed band + probe cluster 95_000..95_003 + cross-face",
"    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/",
"    # N2-W15 probe points.",
"    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):",
f"    # {gate_lines[0]};",
f"    # {gate_lines[1]}.",
"    # W207+ projection (gate-derived pre-seat probe leg4, pre-W206",
f"    # universe): A first-clean {fmt(470_004)}..{fmt(472_003)} CLEAN hops=0 /",
f"    # B first-clean {fmt(470_204)}..{fmt(470_403)} CLEAN hops=0 -- naive B lands",
f"    # INSIDE the naive A window and the registered W206 B band",
f"    # {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W207 A window; W207 freezer",
"    # MUST re-derive on the post-W206 universe AND reserve the",
"    # own-wave A window when deriving B (W141 precedent, leg2 law,",
"    # E36 staircase card; never transcribe r587).",
"    # NOT a re-pick (R250: W206 bands were never assigned).",
])
pf_row = (f'{ROW_I}206: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'206: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, ('         "engine_owner": "bm-a"},' + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = ('         "engine_owner": "bm-a"},' + PF_EOL
          + pf_comment + EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W205 finalize ALL LANDED (W205 finalize product present at splice, "
            f"net chain head {w205_total} machine-read, merged pool K={w205_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition")
cfg_lines = [
 f'{CFG_I}206: {{"batch": "PERPETUAL-N1-W206",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W206_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND SIXTH ENGINE-OWNED WAVE ",
 "BY MACHINE-DERIVE (engine_owner rows 195 + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W205 row bm-a five-face freeze ",
 f"{w205_freeze_sha[:10]} (prereg {w205_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W205 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261010-2323-bmc-w206-seat PUSHED to origin e25629f7 ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG; prereg + pre-seat probe script + probe receipt ",
 "frozen commit 0620f78); ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W205 five-face + W205 finalize product landed ",
 "(prepared pre-landing by the bm-c interactive window under ",
 "the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c, wave 206: ",
 "A = FIRST-CLEAN past the registered W205 B band (the ",
 f"arithmetic continuation {fmt(w205_a_tail + 1)}..{fmt(469_803)} is REFUSED at its ",
 f"own start by the W205 B band {fmt(W205['b_exit'][0])}..{fmt(w205_b_tail)}, exactly as ",
 "the W205 seat leg4 + r956 probe leg4 succession ",
 "projection notes anticipated; honest forward walk hops=1 -> ",
 f"{fmt(a_lo)}..{fmt(a_hi)}; A base == prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase SIXTY-SIXTH ",
 "instance, E36 card (probe receipt leg1 machine-read ordinal); ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN ",
 "past the own-wave A window (the arithmetic continuation ",
 f"{fmt(a_lo)}..{fmt(a_lo+199)} is CLEAN on the registered universe but lands ",
 f"INSIDE the W206 A band window {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual ",
 "exclusion, W141 precedent, leg2 law -- the walk with the ",
 f"own-wave A window reserved jumps to {fmt(b_lo)}, first-clean ",
 f"{fmt(b_lo)}..{fmt(b_hi)} hops=1, non-rotational r587 forward-monotone walk; ",
 "B base == own-wave A tail+1 machine-checkable; cross-window ",
 "convergence with the W205 seat leg4 + r956 probe leg4 + ",
 "W206 pre-seat probe leg4 succession projection notes -- all ",
 "MANDATORY notes honored (post-W205 universe re-derive + ",
 "own-wave A reservation); ADMIT receipt ",
 "results/_w206bmc_20261010_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W207+ projection per this window gate: ",
 f"A first-clean {fmt(470_004)}..{fmt(472_003)} CLEAN / B first-clean ",
 f"{fmt(470_204)}..{fmt(470_403)} CLEAN -- naive B lands INSIDE the naive A window and ",
 f"the registered W206 B band {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W207 A window; ",
 "W207+ freezer MUST re-derive on the post-W206 universe AND ",
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
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W206 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past the registered W205 B band; arithmetic {fmt(w205_a_tail + 1)}..{fmt(469_803)} REFUSED at own start by the W205 B band {fmt(W205["b_exit"][0])}..{fmt(w205_b_tail)}; hops=1; A-hops-prior-B staircase SIXTY-SIXTH instance, E36 card; ordinal machine-read SIXTY-SIXTH per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W206 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN past the own-wave A window; arithmetic {fmt(a_lo)}..{fmt(a_lo+199)} lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w206", "out_name": "n1_w206_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]
cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('206: {"batch": "PERPETUAL-N1-W206"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W206 materializer face (bm-c interactive five-face freeze splice,",
 "    #     own-series law under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20261009-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's thirty-seventh owned per machine-derive (engine_owner==bm-c",
 "    #     rows 36 + candidate); wave 206 = first free number after the",
 f"    #     REGISTERED W205 row (bm-a five-face freeze {w205_freeze_sha[:10]}) --",
 "    #     SINGLE STATE zero seat gap (W2..W205 all registered). Seat",
 "    #     published=reserved MSG-20261010-2323-bmc-w206-seat pushed",
 "    #     to origin e25629f7 BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG; prereg + pre-seat probe script + probe receipt",
 "    #     frozen commit 0620f78; deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W205 five-face + W205 finalize",
 "    #     product landed; zero --no-verify; the W206 seat MSG sits in",
 "    #     fleet/inbox/processed/ at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND SIXTH engine wave BY",
 "    #     MACHINE-DERIVE (engine_owner rows 195 + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w206bmc_20261010_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W206 bands were never assigned).",
 "    _set_wave(206)",
 "    try:",
 '        assert WAVE_CONFIGS[205]["a_seed_base"] == pf.N1_BANDS[205]["a"][0], \\',
 '            "W206 A band drift vs law mirror"',
 "        assert WAVE_CONFIGS[205][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[205]["b_exit"][0], "W206 B band drift vs law mirror"',
 "        assert WAVE_CONFIGS[205].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[205].get("engine_owner") == "bm-a", \\',
 '            "W206 engine_owner drift (law mirror parity)"',
 "        w205_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w205_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w205_a & w205_b), "W206 A/B band overlap"',
 "        assert not (w205_a & reg_ints) and not (w205_b & reg_ints), \\",
 '            "W206 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w205_a), ("B", w205_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W206 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W206 {nm} hits W1"',
 '            assert not (band & probes), f"W206 {nm} hits probe seeds"',
]
w205_leg = [
 f'        assert pf.N1_BANDS[205] == {{"a": ({fmt(W205["a"][0])}, {fmt(W205["a"][1])}),',
 f'                                    "b_exit": ({fmt(W205["b_exit"][0])}, {fmt(W205["b_exit"][1])}),',
 '                                    "engine_owner": "bm-a"}, \\',
 '            "registered W205 row parity drift (r307; bm-a five-face freeze)"',
]
tail = [
 "        # prior-wave disjointness W2..W205 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 206):",
 '            assert not (w205_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W206 A hits W{wprev}\"",
 '            assert not (w205_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W206 B hits W{wprev}\"",
 "        n3r1_used205 = set(range(70_000, 70_006))",
 "        assert not (w205_a & n3r1_used205) and not (w205_b & n3r1_used205), \\",
 '            "W206 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w205_a & lfc_actual12) and not (w205_b & lfc_actual12), \\",
 '            "W206 bands must clear the lfc actual draw range"',
 "        assert not (w205_a & options_actual12) and \\",
 "            not (w205_b & options_actual12), \\",
 '            "W206 bands must clear the options_wave2 actual draw range"',
 "        # band facts (law sec.4 W206 row): A = FIRST-CLEAN past",
 "        # the registered W205 B band (the arithmetic continuation",
 f"        # {fmt(w205_a_tail + 1)}..{fmt(469_803)} is REFUSED at its own start by the W205 B band",
 f"        # {fmt(W205['b_exit'][0])}..{fmt(w205_b_tail)}, exactly as the W205 seat leg4 + r956 probe",
 "        # leg4 succession projection notes anticipated; honest",
 f"        # forward walk hops=1 lands {fmt(a_lo)}..{fmt(a_hi)}; A base ==",
 f"        # prior-wave B tail+1 ({fmt(w205_b_tail)}+1) machine-checkable --",
 "        # A-hops-prior-B staircase SIXTY-SIXTH instance, E36 card;",
 "        # non-rotational r587 forward-monotone walk);",
 "        # B = FIRST-CLEAN past the own-wave A window (the",
 f"        # arithmetic continuation {fmt(a_lo)}..{fmt(a_lo+199)} is CLEAN on the",
 f"        # registered universe but lands INSIDE the W206 A band window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual exclusion (W141 precedent,",
 "        # leg2 law) -- the walk with the own-wave A window reserved",
 f"        # jumps to {fmt(b_lo)} and lands {fmt(b_lo)}..{fmt(b_hi)}, hops=1,",
 "        # non-rotational r587 forward-monotone walk; B base ==",
 f"        # own-wave A tail+1 ({fmt(a_hi)}+1) machine-checkable;",
 "        # cross-window convergence with the W205 seat leg4 + r956",
 "        # probe leg4 + W206 pre-seat probe leg4 succession",
 "        # projection notes -- all MANDATORY notes honored (post-W205",
 "        # universe re-derive + own-wave A reservation when deriving B);",
 "        # seat MSG-2323 tail, re-derived).",
 f'        assert WAVE_CONFIGS[206]["a_seed_base"] == {a_lo} == {w205_b_tail} + 1, (',
 '            "W206 A must be the first-clean window past the registered "',
 '            "W205 B band tail (arithmetic continuation REFUSED at its own "',
 '            "start by the W205 B band, exactly as the W205 seat leg4 + "',
 '            "r956 probe leg4 succession projection notes anticipated; "',
 '            "honest forward walk hops=1; A base == prior-wave B tail+1 "',
 '            "machine-checkable = A-hops-prior-B staircase SIXTY-SIXTH "',
 '            "instance, E36 card)")',
 f"        arith_a205 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a205 & reg_ints), \\",
 '            "W206 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
 f'        assert WAVE_CONFIGS[206]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
 '            "W206 B must be the first-clean window past the own-wave A "',
 '            "band tail (arithmetic continuation CLEAN on the registered "',
 '            "universe but lands INSIDE the W206 A band window; "',
 '            "same-freeze mutual exclusion (W141 precedent, leg2 law) -- "',
 '            "the walk with the own-wave A window reserved jumps, "',
 '            "first-clean hops=1, non-rotational r587 forward-monotone "',
 '            "walk; B base == own-wave A tail+1 machine-checkable)")',
 f"        arith_b205 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b205 & reg_ints), \\",
 '            "W206 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
 "        assert not (arith_b205 & arith_a205), \\",
 '            "W206 A/B same-freeze mutual exclusion (B hops past own A)"',
 '        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W206-SHARD-0",',
 '                                          "n1w206-0of12"), "W206 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W206-SHARD-11",',
 '                                           "n1w206-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w206\") and OUT.endswith(",
 '            "n1_w206_results.json"), "W206 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 206):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W206 shard dir collides with W{wprev}"',
 "        # W206 finalize cumulative deps: W17..W205 outputs ALL PRESENT",
 f"        # (landed net chain head {w205_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 206):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W206 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 206 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W205 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 206) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 206)], \\",
 '            "W206 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W205 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W206_PREREG.md")), \\',
 '            "W206 per-wave prereg missing (materializer requirement)"',
 '        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"',
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w205_leg) + EOL + EOL.join(tail) + EOL
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W206 materializer face [same guard set, dep=W17..W205 "',
 f'          "outputs ALL PRESENT (landed net chain head {w205_total} = W205 bm-a finalize one-pass, K={w205_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND SIXTH "',
 '          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 195 "',
 '          "+ candidate) bm-c\'s thirty-seventh owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 36 + candidate), "',
 '          "A=FIRST-CLEAN past the registered W205 B band (staircase "',
 '          "SIXTY-SIXTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
 '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
 '          "mutual exclusion, hops=1), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w206bmc_20261010_probe_receipt.json, law sec.4 W206 row, "',
 '          "bm-c interactive CEO fill-order RE-ISSUE 23:1x] "',
]
old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W206"') == 1
assert n1_t4.count("# --- W206 materializer face") == 1     # block header
assert n1_t4.count('"+ W206 materializer face') == 1        # print fragment
assert n1_t4.count('206: {"batch": "PERPETUAL-N1-W206"') == 1
assert pf_t2.count('    206: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W206-SHARD-0"') == 1
assert n1_t4.count('f"W206 A hits W{wprev}"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[205] == {{"a": ({fmt(W205["a"][0])}, {fmt(W205["a"][1])}),') == 1
assert n1_t4.count('    # --- W205 materializer face') == 1  # prior block kept
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
  "machine": "bm-c", "wave": 206,
  "phase": "five-face freeze chain-order splice (prepared pre-landing, executed post-W205-finalize)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w206bmc_20261010_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "w205_upstream": {"freeze_sha": w205_freeze_sha, "prereg_sha": w205_prereg_sha,
                    "ledger_total": w205_total, "merged_n": w205_merged_n},
  "seat": "fleet/inbox/processed/MSG-20261010-2323-bmc-w206-seat.md (origin e25629f7)",
  "prereg_bundle": "origin 0620f78",
  "parity_section": {"source": "W205 block physical bytes", "bytes": len(par_sec),
                     "row_asserts": par_sec.count("assert pf.N1_BANDS[")},
  "eol": {"n1_crlf": True, "pf_crlf": True},
  "liveness_anchors": {"t141_marker_kept": 1, "w205_block_kept": 1},
}
open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w205_upstream")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest -> pathspec commit+push -> ignition verify (2-cycle n1_w206 growth)")
