# -*- coding: utf-8 -*-
# 2026-10-11 00:5x bm-b (OS loop r852): W207 five-face freeze splice editor
# (PREPARED pre-landing, EXECUTED after the bm-c W206 five-face + W206
# finalize product land on origin -- chain-order law + tail dep assert
# require the prior wave's results file).
# Lineage: results/_w206bmc_freeze_edits.py pattern (bm-c staging commit
# 70c560a90) + r787 preflight law + r609 origin-verbatim base + r761
# programmatic quote wrapping + r909 physical-byte anchors + r838/r839
# EOL law (runtime detection, never assume) + r576/r590 anchor roll
# (upstream finalize chain head machine-read at splice time).
#
# Three documented deviations from the W206 template, all verified against
# the live repo state at staging time (r852 probe evidence
# results/_r852bmb_w207_stage_probe*.py):
#   (a) EOL: repo scripts/perpetual_faces.py + scripts/perpetual_faces_n1.py
#       are LF-only at staging time (CRLF count 0 in both, probe3/probe4);
#       the W206 template hardcodes CRLF and would fail-closed. This script
#       detects the per-file dominant EOL at execution (r838 law) and uses
#       the captured actual EOL for the close anchors.
#   (b) Parity estate: extracted from the LANDED immutable W205 block
#       (marker -> first 204-row-leg line = pure 50-row recent estate,
#       waves 138..187, probe3-verified) instead of the in-flight W206
#       block; keeps the block parity section at the empirical 50+1 size
#       (W204 and W205 blocks both 50 estate + 1 upstream row leg) and
#       decouples from upstream splice mechanics. The W206 block
#       (post-landing) remains the immediate upstream face for the
#       live-row parity leg (w206_leg, live pf import).
#   (c) Prose numbers fully receipt-derived: arithmetic-continuation
#       windows parsed from the committed ADMIT receipt legs
#       (results/_w207bmb_20261010_probe_receipt.json), upstream rows from
#       the LIVE pf import at freeze time; zero transcribed band values.
#
# Zero hardcoded band values in the splice text: every band fact is derived
# from the committed ADMIT receipt or the live pf import read at freeze
# time. CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
# ~23:1x; O-20260924-1730 claim-and-start same-round law (seat
# MSG-20261010-2335-bmb-w207-seat on origin 014a3e85e, prereg bundle
# 6fa2dae16, both landed r848/r849).
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w207bmb_20261010_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w207bmb_freeze_receipt.json")
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

# ---------- gate 0.5: W206 landed + finalize product present (chain-order precondition) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT", f"probe receipt not ADMIT: {rec.get('verdict')}"
W206 = dict(pf_mod.N1_BANDS.get(206) or {})
rec_w206 = rec["legs"]["leg0"]["w206_declared"]
assert W206.get("a") == tuple(rec_w206["A"]) and W206.get("b_exit") == tuple(rec_w206["B"]) \
    and W206.get("engine_owner") == "bm-c", \
    f"W206 row not landed as declared in the committed receipt: {W206}"
w206_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w206_results.json")
assert os.path.exists(w206_out_path), "W206 finalize product missing (n1_w206_results.json) -- chain dep not met"
w206_out = json.load(open(w206_out_path, encoding="utf-8"))
w206_led = (w206_out.get("science_gates") or {}).get("ledger") or {}
w206_total = w206_led.get("total")
w206_merged_n = None
try:
    w206_merged_n = w206_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert isinstance(w206_total, int), f"W206 ledger head not an int: {w206_total!r}"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '206: {"a"', "--", "scripts/perpetual_faces.py")
w206_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W206_PREREG.md")
w206_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W207_PREREG.md")
w207_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# ordinal faces machine-derived from the live registry (gate leg0 governs, r359 law)
owner_rows_live = sum(1 for v in pf_mod.N1_BANDS.values()
                      if isinstance(v, dict) and v.get("engine_owner"))
bmb_rows_live = sum(1 for v in pf_mod.N1_BANDS.values()
                    if isinstance(v, dict) and v.get("engine_owner") == "bm-b")
assert owner_rows_live == 196, f"owner rows live = {owner_rows_live} (expected 196 post-W206)"
assert bmb_rows_live == 40, f"bm-b rows live = {bmb_rows_live} (expected 40)"
assert rec["legs"]["leg0"]["ordinal"] == owner_rows_live + 1 == 197, "ordinal drift vs receipt"
assert rec["legs"]["leg0"]["bmb_ordinal"] == bmb_rows_live + 1 == 41, "bmb ordinal drift vs receipt"
assert "SIXTY-SEVENTH" in rec["legs"]["leg1"]["A_semantics"], "staircase ordinal word drift vs receipt"
print(f"gate0.5 OK: W206 landed (freeze {w206_freeze_sha[:10]}), finalize product present "
      f"(ledger head {w206_total}, merged n={w206_merged_n}); ordinals live-derived "
      f"(197th engine-owned, bm-b 41st owned)")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
A = rec["bands"]["A"]; B = rec["bands"]["B"]
a_lo, a_hi = (int(x) for x in A.split("_"))
b_lo, b_hi = (int(x) for x in B.split("_"))
leg1 = rec["legs"]["leg1"]
assert [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"], "receipt band mismatch"
assert (a_lo, a_hi) == (470_204, 472_203) and (b_lo, b_hi) == (472_204, 472_403), \
    f"W207 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w206_b_tail = W206["b_exit"][1]      # registered W206 row b_exit hi (live pf import)
pri_a_tail = a_hi                     # own-wave A tail
assert w206_b_tail + 1 == a_lo and a_hi + 1 == b_lo, "staircase base relations broken"
arithA = leg1["ARITH_A"]; arithB = leg1["ARITH_B"]
assert arithA == [W206["a"][1] + 1, W206["a"][1] + 2000], f"arith A window drift vs receipt: {arithA}"
assert arithB == [a_lo, a_lo + 199], f"naive B window drift vs receipt: {arithB}"
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, "hops drift vs receipt"
assert leg1["B_naive_first_clean"] == arithB, "naive B face drift vs receipt"
leg4 = rec["legs"]["leg4"]
def parse_win(s):
    lo, hi = s.split("..")
    return int(lo), int(hi)
p_a = parse_win(leg4["W208p_A"]); p_b = parse_win(leg4["W208p_B"])
assert p_a == (b_lo, b_lo + 1999), f"W208+ A projection drift vs receipt: {p_a}"
assert p_b == (b_hi + 1, b_hi + 200), f"W208+ B projection drift vs receipt: {p_b}"
assert leg4["W208p_B_lands_inside_W208p_A"] is True

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W207_PREREG.md"],
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

# ---------- read files, EOL (runtime detection, r838/r839 law) ----------
pf_b = open(PF, "rb").read(); pf_t = pf_b.decode("utf-8")
n1_b = open(N1, "rb").read(); n1_t = n1_b.decode("utf-8")
def detect_eol(t):
    crlf = t.count("\r\n"); lf = t.count("\n") - crlf
    return ("\r\n" if crlf >= lf else "\n"), crlf, lf
EOL, n1_crlf, n1_lf = detect_eol(n1_t)
PF_EOL, pf_crlf, pf_lf = detect_eol(pf_t)
print(f"EOL detected: n1 CRLF={n1_crlf} LF={n1_lf} -> {EOL!r}; pf CRLF={pf_crlf} LF={pf_lf} -> {PF_EOL!r}")
assert (n1_crlf > 0) or (n1_lf > 0), "n1 has no line terminators at all"
assert (pf_crlf > 0) or (pf_lf > 0), "pf has no line terminators at all"

def must(t, s, n, what):
    c = t.count(s)
    assert c == n, f"anchor {what}: count {c} != {n}"
    return s

def fmt(n):  # 470204 -> "470_204"
    return f"{n // 1000}_{n % 1000:03d}"

# ---------- parity estate extraction (physical bytes, from the LANDED W205 block) ----------
i205 = n1_t.find("    # --- W205 materializer face")
assert i205 > 0, "W205 materializer block not found (bm-a W205 freeze not landed?)"
it141 = n1_t.find("    # --- T-141 s2 lane face", i205)
assert it141 > i205, "T-141 marker not found after the W205 block"
i206m = n1_t.find("    # --- W206 materializer face", i205)
blk_end = i206m if 0 < i206m < it141 else it141
blk205 = n1_t[i205:blk_end]
par_marker = "        # registered row parity (r307 pinned constants, recent estate)"
k = blk205.find(par_marker)
leg204 = blk205.find("        assert pf.N1_BANDS[204] == {")
assert k > 0 and leg204 > k, "parity markers not found in the W205 block"
estate = blk205[k:leg204]
waves = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", estate)
assert estate.count("assert pf.N1_BANDS[") == 50, \
    f"parity estate size drift: {len(waves)} asserts (expected 50 rows 138..187)"
assert len(set(waves)) == 50 and max(int(w) for w in waves) < 204, \
    "parity estate composition drift (upstream row legs must not be extracted)"
assert estate.endswith(EOL), "estate does not end with the detected line terminator"
print(f"estate OK: 50 pinned rows {waves[0]}..{waves[-1]}, "
      f"{len(estate)} physical bytes from the landed W205 block")

# ---------- indent extraction (physical, not assumed; EOL-length-aware) ----------
def line_indent(t, needle):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(EOL, 0, i) + len(EOL)
    line = t[ls:t.find(EOL, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '206: {"batch"')
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W206_PREREG.md')
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "')
MEM_I  = line_indent(n1_t, '"a_seed_base": 468004')  # r856: landed bm-c W206 cfg entry uses no-underscore int literal (physical-byte anchor align, r909 law; audit probe results/_r856bmb_w207_anchor_audit.py)
ROW_I  = line_indent(pf_t,  '206: {"a"')
ROWC_I = line_indent(pf_t,  '"engine_owner": "bm-c"},')

# ---------- pf comment + row ----------
pf_comment = EOL.join([
"    # W207 (bm-b OS-loop five-face freeze splice, seat",
"    # MSG-20261010-2335-bmb-w207-seat pushed to origin 014a3e85e",
"    # pre-freeze r565 law; prereg + banned-gate ADMIT frozen",
"    # commit 6fa2dae16 (prereg research/PERPETUAL_N1_W207_PREREG.md,",
"    # probe results/_w207bmb_20261010_probe_receipt.json);",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
f"    # splice AFTER the bm-c W206 five-face (freeze {w206_freeze_sha[:10]}) + W206",
"    # finalize product landed (n1_w206_results.json present, ledger",
f"    # head {w206_total} machine-read at freeze time); zero --no-verify;",
"    # the W207 seat MSG sits in fleet/inbox/processed/ at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w207bmb_20261010_probe_receipt.json: A = FIRST-CLEAN",
"    # past the registered W206 B band (arithmetic continuation",
f"    # {fmt(arithA[0])}..{fmt(arithA[1])} REFUSED at its own start by the W206 B band",
f"    # {fmt(W206['b_exit'][0])}..{fmt(w206_b_tail)}, exactly as the W206 seat leg4",
"    # projection + W206 probe leg4 anticipated;",
f"    # honest forward walk hops=1 -> {fmt(a_lo)}..{fmt(a_hi)}, non-rotational",
"    # r587 forward-monotone walk; A base == prior-wave B tail+1",
f"    # ({fmt(w206_b_tail)}+1) machine-checkable -- A-hops-prior-B staircase",
"    # SIXTY-SEVENTH instance, E36 card (probe receipt leg1 A_semantics",
"    # machine-read ordinal, never transcribed);",
"    # B = FIRST-CLEAN past the own-wave A window (arithmetic",
f"    # continuation {fmt(arithB[0])}..{fmt(arithB[1])} CLEAN on the registered",
f"    # universe but lands INSIDE the W207 A band window {fmt(a_lo)}..{fmt(a_hi)} --",
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
"    # W208+ projection (gate-derived pre-seat probe leg4, pre-W207",
f"    # universe): A first-clean {fmt(p_a[0])}..{fmt(p_a[1])} CLEAN hops=0 /",
f"    # B first-clean {fmt(p_b[0])}..{fmt(p_b[1])} CLEAN hops=0 -- naive B lands",
"    # INSIDE the naive A window and the registered W207 B band",
f"    # {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W208 A window; W208 freezer",
"    # MUST re-derive on the post-W207 universe AND reserve the",
"    # own-wave A window when deriving B (W141 precedent, leg2 law,",
"    # E36 staircase card; never transcribe r587).",
"    # NOT a re-pick (R250: W207 bands were never assigned).",
])
pf_row = (f'{ROW_I}207: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + EOL + f'{ROWC_I}"engine_owner": "bm-b"}},' + EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(EOL)[0].strip() == \
    f'207: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = None
for cand in (PF_EOL, ("\r\n" if PF_EOL == "\n" else "\n")):
    s = ('         "engine_owner": "bm-c"},' + cand + '}'
         + cand + '# v1 + ext(wave-1) in-use bands')
    if pf_t.count(s) == 1:
        old_pf = s
        break
assert old_pf, "pf close anchor (W206 owner line + dict close + tail comment) not found under either EOL convention"
new_pf = ('         "engine_owner": "bm-c"},' + PF_EOL
          + pf_comment + EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W206 finalize ALL LANDED (W206 finalize product present at splice, "
            f"net chain head {w206_total} machine-read, merged pool K={w206_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition")
cfg_lines = [
 f'{CFG_I}207: {{"batch": "PERPETUAL-N1-W207",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W207_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND SEVENTH ENGINE-OWNED WAVE ",
 "BY MACHINE-DERIVE (engine_owner rows 196 + candidate), ",
 "own-series continuation per O-20261001-2355 sec.2 (first-free-",
 "number law after the REGISTERED W206 row bm-c five-face freeze ",
 f"{w206_freeze_sha[:10]} (prereg {w206_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W206 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261010-2335-bmb-w207-seat PUSHED to origin 014a3e85e ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG; prereg + banned-gate ADMIT frozen commit 6fa2dae16); ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W206 five-face + W206 finalize product landed ",
 "(prepared pre-landing by the bm-b OS loop r852 staging window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-b, wave 207: ",
 "A = FIRST-CLEAN past the registered W206 B band (the ",
 f"arithmetic continuation {fmt(arithA[0])}..{fmt(arithA[1])} is REFUSED at its ",
 f"own start by the W206 B band {fmt(W206['b_exit'][0])}..{fmt(w206_b_tail)}, exactly as ",
 "the W206 seat leg4 + W206 probe leg4 succession ",
 "projection notes anticipated; honest forward walk hops=1 -> ",
 f"{fmt(a_lo)}..{fmt(a_hi)}; A base == prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase SIXTY-SEVENTH ",
 "instance, E36 card (probe receipt leg1 machine-read ordinal); ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN ",
 "past the own-wave A window (the arithmetic continuation ",
 f"{fmt(arithB[0])}..{fmt(arithB[1])} is CLEAN on the registered universe but lands ",
 f"INSIDE the W207 A band window {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual ",
 "exclusion, W141 precedent, leg2 law -- the walk with the ",
 f"own-wave A window reserved jumps to {fmt(b_lo)}, first-clean ",
 f"{fmt(b_lo)}..{fmt(b_hi)} hops=1, non-rotational r587 forward-monotone walk; ",
 "B base == own-wave A tail+1 machine-checkable; cross-window ",
 "convergence with the W206 seat leg4 + W206 probe leg4 + ",
 "W207 pre-seat probe leg4 succession projection notes -- all ",
 "MANDATORY notes honored (post-W206 universe re-derive + ",
 "own-wave A reservation); ADMIT receipt ",
 "results/_w207bmb_20261010_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W208+ projection per this window gate: ",
 f"A first-clean {fmt(p_a[0])}..{fmt(p_a[1])} CLEAN / B first-clean ",
 f"{fmt(p_b[0])}..{fmt(p_b[1])} CLEAN -- naive B lands INSIDE the naive A window and ",
 f"the registered W207 B band {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W208 A window; ",
 "W208+ freezer MUST re-derive on the post-W207 universe AND ",
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
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W207 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past the registered W206 B band; arithmetic {fmt(arithA[0])}..{fmt(arithA[1])} REFUSED at own start by the W206 B band {fmt(W206["b_exit"][0])}..{fmt(w206_b_tail)}; hops=1; A-hops-prior-B staircase SIXTY-SEVENTH instance, E36 card; ordinal machine-read SIXTY-SEVENTH per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W207 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN past the own-wave A window; arithmetic {fmt(arithB[0])}..{fmt(arithB[1])} lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w207", "out_name": "n1_w207_results.json",',
 f'{MEM_I}"engine_owner": "bm-b"}},',
]
cfg_block = EOL.join(cfg_lines)
old_cfg = None
for cand in (EOL, ("\r\n" if EOL == "\n" else "\n")):
    s = ('                       }' + cand + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
    if n1_t.count(s) == 1:
        old_cfg = s
        break
assert old_cfg, "n1 cfg close anchor not found under either EOL convention"
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('207: {"batch": "PERPETUAL-N1-W207"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W207 materializer face (bm-b OS-loop five-face freeze splice,",
 "    #     own-series law under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20261009-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-b's forty-first owned per machine-derive (engine_owner==bm-b",
 "    #     rows 40 + candidate); wave 207 = first free number after the",
 f"    #     REGISTERED W206 row (bm-c five-face freeze {w206_freeze_sha[:10]}) --",
 "    #     SINGLE STATE zero seat gap (W2..W206 all registered). Seat",
 "    #     published=reserved MSG-20261010-2335-bmb-w207-seat pushed",
 "    #     to origin 014a3e85e BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG; prereg + banned-gate ADMIT frozen commit 6fa2dae16;",
 "    #     deletion-set EMPTY; delivery window = chain-order splice",
 "    #     after the W206 five-face + W206 finalize product landed;",
 "    #     zero --no-verify; the W207 seat MSG sits in",
 "    #     fleet/inbox/processed/ at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND SEVENTH engine wave BY",
 "    #     MACHINE-DERIVE (engine_owner rows 196 + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w207bmb_20261010_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W207 bands were never assigned).",
 "    _set_wave(207)",
 "    try:",
 '        assert WAVE_CONFIGS[206]["a_seed_base"] == pf.N1_BANDS[206]["a"][0], \\',
 '            "W207 A band drift vs law mirror"',
 '        assert WAVE_CONFIGS[206]["b_exit_seed_base"] == \\',
 '            pf.N1_BANDS[206]["b_exit"][0], "W207 B band drift vs law mirror"',
 '        assert WAVE_CONFIGS[206].get("engine_owner") == \\',
 '            pf.N1_BANDS[206].get("engine_owner") == "bm-c", \\',
 '            "W207 engine_owner drift (law mirror parity)"',
 "        w206_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w206_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w206_a & w206_b), "W207 A/B band overlap"',
 "        assert not (w206_a & reg_ints) and not (w206_b & reg_ints), \\",
 '            "W207 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w206_a), ("B", w206_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W207 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W207 {nm} hits W1"',
 '            assert not (band & probes), f"W207 {nm} hits probe seeds"',
]
w206_leg = [
 f'        assert pf.N1_BANDS[206] == {{"a": ({fmt(W206["a"][0])}, {fmt(W206["a"][1])}),',
 f'                                    "b_exit": ({fmt(W206["b_exit"][0])}, {fmt(W206["b_exit"][1])}),',
 '                                    "engine_owner": "bm-c"}, \\',
 '            "registered W206 row parity drift (r307; bm-c five-face freeze)"',
]
tail = [
 "        # prior-wave disjointness W2..W206 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 207):",
 '            assert not (w206_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W207 A hits W{wprev}\"",
 '            assert not (w206_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W207 B hits W{wprev}\"",
 "        n3r1_used206 = set(range(70_000, 70_006))",
 "        assert not (w206_a & n3r1_used206) and not (w206_b & n3r1_used206), \\",
 '            "W207 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w206_a & lfc_actual12) and not (w206_b & lfc_actual12), \\",
 '            "W207 bands must clear the lfc actual draw range"',
 "        assert not (w206_a & options_actual12) and \\",
 "            not (w206_b & options_actual12), \\",
 '            "W207 bands must clear the options_wave2 actual draw range"',
 "        # band facts (law sec.4 W207 row): A = FIRST-CLEAN past",
 "        # the registered W206 B band (the arithmetic continuation",
 f"        # {fmt(arithA[0])}..{fmt(arithA[1])} is REFUSED at its own start by the W206 B band",
 f"        # {fmt(W206['b_exit'][0])}..{fmt(w206_b_tail)}, exactly as the W206 seat leg4 + W206 probe",
 "        # leg4 succession projection notes anticipated; honest",
 f"        # forward walk hops=1 lands {fmt(a_lo)}..{fmt(a_hi)}; A base ==",
 f"        # prior-wave B tail+1 ({fmt(w206_b_tail)}+1) machine-checkable --",
 "        # A-hops-prior-B staircase SIXTY-SEVENTH instance, E36 card;",
 "        # non-rotational r587 forward-monotone walk);",
 "        # B = FIRST-CLEAN past the own-wave A window (the",
 f"        # arithmetic continuation {fmt(arithB[0])}..{fmt(arithB[1])} is CLEAN on the",
 f"        # registered universe but lands INSIDE the W207 A band window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual exclusion (W141 precedent,",
 "        # leg2 law) -- the walk with the own-wave A window reserved",
 f"        # jumps to {fmt(b_lo)} and lands {fmt(b_lo)}..{fmt(b_hi)}, hops=1,",
 "        # non-rotational r587 forward-monotone walk; B base ==",
 f"        # own-wave A tail+1 ({fmt(a_hi)}+1) machine-checkable;",
 "        # cross-window convergence with the W206 seat leg4 + W206",
 "        # probe leg4 + W207 pre-seat probe leg4 succession",
 "        # projection notes -- all MANDATORY notes honored (post-W206",
 "        # universe re-derive + own-wave A reservation when deriving B);",
 "        # seat MSG-2335 tail, re-derived).",
 f'        assert WAVE_CONFIGS[207]["a_seed_base"] == {a_lo} == {w206_b_tail} + 1, (',
 '            "W207 A must be the first-clean window past the registered "',
 '            "W206 B band tail (arithmetic continuation REFUSED at its own "',
 '            "start by the W206 B band, exactly as the W206 seat leg4 + "',
 '            "W206 probe leg4 succession projection notes anticipated; "',
 '            "honest forward walk hops=1; A base == prior-wave B tail+1 "',
 '            "machine-checkable = A-hops-prior-B staircase SIXTY-SEVENTH "',
 '            "instance, E36 card)")',
 f"        arith_a206 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a206 & reg_ints), \\",
 '            "W207 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
 f'        assert WAVE_CONFIGS[207]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
 '            "W207 B must be the first-clean window past the own-wave A "',
 '            "band tail (arithmetic continuation CLEAN on the registered "',
 '            "universe but lands INSIDE the W207 A band window; "',
 '            "same-freeze mutual exclusion (W141 precedent, leg2 law) -- "',
 '            "the walk with the own-wave A window reserved jumps, "',
 '            "first-clean hops=1, non-rotational r587 forward-monotone "',
 '            "walk; B base == own-wave A tail+1 machine-checkable)")',
 f"        arith_b206 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b206 & reg_ints), \\",
 '            "W207 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
 "        assert not (arith_b206 & arith_a206), \\",
 '            "W207 A/B same-freeze mutual exclusion (B hops past own A)"',
 '        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W207-SHARD-0",',
 '                                          "n1w207-0of12"), "W207 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W207-SHARD-11",',
 '                                           "n1w207-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w207\") and OUT.endswith(",
 '            "n1_w207_results.json"), "W207 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 207):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W207 shard dir collides with W{wprev}"',
 "        # W207 finalize cumulative deps: W17..W206 outputs ALL PRESENT",
 f"        # (landed net chain head {w206_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 207):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W207 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 207 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W206 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 207) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 207)], \\",
 '            "W207 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W206 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W207_PREREG.md")), \\',
 '            "W207 per-wave prereg missing (materializer requirement)"',
 '        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"',
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + estate + EOL.join(w206_leg) + EOL + EOL.join(tail) + EOL
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W207 materializer face [same guard set, dep=W17..W206 "',
 f'          "outputs ALL PRESENT (landed net chain head {w206_total} = W206 bm-c finalize one-pass, K={w206_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND SEVENTH "',
 '          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 196 "',
 '          "+ candidate) bm-b\'s forty-first owned claim per "',
 '          "machine-derive (engine_owner==bm-b rows 40 + candidate), "',
 '          "A=FIRST-CLEAN past the registered W206 B band (staircase "',
 '          "SIXTY-SEVENTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
 '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
 '          "mutual exclusion, hops=1), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w207bmb_20261010_probe_receipt.json, law sec.4 W207 row, "',
 '          "bm-b OS-loop r852 staging window, CEO fill-order standing + RE-ISSUE 23:1x] "',
]
old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W207"') == 1
assert n1_t4.count("# --- W207 materializer face") == 1     # block header
assert n1_t4.count('"+ W207 materializer face') == 1        # print fragment
assert n1_t4.count('207: {"batch": "PERPETUAL-N1-W207"') == 1
assert pf_t2.count('    207: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-b"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W207-SHARD-0"') == 1
assert n1_t4.count('f"W207 A hits W{wprev}"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[206] == {{"a": ({fmt(W206["a"][0])}, {fmt(W206["a"][1])}),') == 1
assert n1_t4.count('    # --- W205 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W206 materializer face') == 1  # prior block kept
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
  "machine": "bm-b", "wave": 207,
  "phase": "five-face freeze chain-order splice (prepared pre-landing r852, executed post-W206-finalize)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w207bmb_20261010_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "w206_upstream": {"freeze_sha": w206_freeze_sha, "prereg_sha": w206_prereg_sha,
                    "ledger_total": w206_total, "merged_n": w206_merged_n},
  "w207_prereg_sha": w207_prereg_sha,
  "seat": "fleet/inbox/processed/MSG-20261010-2335-bmb-w207-seat.md (origin 014a3e85e)",
  "prereg_bundle": "origin 6fa2dae16",
  "ordinals": {"engine_owned_ordinal": owner_rows_live + 1, "bmb_owned_ordinal": bmb_rows_live + 1,
               "staircase_instance": "SIXTY-SEVENTH (E36 card, receipt leg1 machine-read)"},
  "parity_estate": {"source": "landed W205 block physical bytes (marker -> 204-row-leg)",
                    "bytes": len(estate), "rows": 50,
                    "window": f"{waves[0]}..{waves[-1]}"},
  "eol": {"n1_crlf": n1_crlf > 0, "pf_crlf": pf_crlf > 0,
          "detected_n1": EOL, "detected_pf": PF_EOL},
  "liveness_anchors": {"t141_marker_kept": 1, "w205_block_kept": 1, "w206_block_kept": 1},
}
open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w206_upstream", "ordinals")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (pf + n1) -> pathspec commit+push "
      "(scripts/perpetual_faces.py + scripts/perpetual_faces_n1.py + "
      "results/_w207bmb_freeze_receipt.json) -> ignition verify (2-cycle n1_w207 growth, r325 law)")
