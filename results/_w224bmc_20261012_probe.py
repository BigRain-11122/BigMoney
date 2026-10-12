# -*- coding: utf-8 -*-
"""W224 pre-seat probe (bm-c loop window r935, 2026-10-12 17:5x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law). Upstream face = W223 FULL CYCLE LANDED (r932 seat
8f2d79147 + r933 per-wave prereg derive b7d46427d + r934 dead-window five-face
freeze splice 448c4d8c2 pushed 17:4x + engine self-burn 12/12 batched
ledger appends 7b4236f85/0a8e2ba00 [shard-9/10 landed by r935 estate] +
PRE-FINALIZE six-gate ALL GREEN _r934bmc_w223_sixgate_receipt.json
17:24:44 [correct phase 3rd consecutive; boundary-pair-scan gate leg
in-force first landing = W222 sec.8 escalation proposal] + finalize
one-pass 17:2x: ledger 912,189+2,200=914,389 EXACT, merged pool K=488,520,
results/perpetual_faces/n1_w223_results.json machine-read) --
SINGLE STATE: W2..W223 ALL REGISTERED, zero in-flight declared seats. This
probe IS the W224 re-derive on the post-W223-REGISTERED universe mandated by
the W223 probe leg4 + W223 seat MSG projection (r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W223-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W209..W223 fifteen faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY EIGHTY-FOURTH instance expected, W141
leg2 law + E36 card; the W223 seat MSG leg4 projection anticipated W224+ --
this probe IS that re-derive):
  A  arithmetic continuation from the registered W223 A tail -- expected
     REFUSED at its own start by the registered W223 B band (staircase
     A-hops-prior-B 83rd); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W223 B tail -- naive lands
     INSIDE the W224 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base
     == own-wave A tail+1 machine-checkable relation.
Anchor face: W223 finalize LANDED (ledger head 914,389 = prev 912,189 + 2,200; merged pool K=488,520 machine-read in leg0; five-key ALL PASS _r934bmc_w223_fivekey_receipt.json). W224 freeze is GATED on nothing
in-flight -- upstream fully landed, clean chain-order window.
Bloodline: _w223bmc_20261012_probe.py derive machinery verbatim, W224 facts
live-registry-driven; single-state universe (no declared-injection legs)."""
import re
import subprocess
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000
WIDTH_A = 2_000
WIDTH_B = 200

N3R1_USED = (71_000, 71_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
CROSSFACE_PROBE_POINTS = (95_004, 95_006)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
receipt = {"probe": "W224 pre-seat probe (bm-c loop r935 window, 2026-10-12 17:5x, CEO fill-order standing + seat-first law + never-dry supply line; post-W223-REGISTERED single-state universe, upstream W223 full cycle landed r932 seat/r933 prereg/r934 dead-window splice+burn+finalize/r935 absorb)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape (post-W223 universe: tail=W223 registered) -----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 224))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W223_A = tuple(N1_BANDS[223]["a"])
W223_B = tuple(N1_BANDS[223]["b_exit"])
assert W223_A == (505_404, 507_403) and W223_B == (507_404, 507_603) and \
    N1_BANDS[223].get("engine_owner") == "bm-c", "leg0 failed: W223 row drift (bm-c r934 splice face)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 213 and len(bmc_rows) == 53, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 213/53 post-W223-splice per the r934 splice receipt ordinal faces)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

w223_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w223_results.json"), encoding="utf-8"))
led = (w223_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 914_389 and led.get("prev_total") == 912_189, \
    f"leg0 failed: W223 ledger machine-read drift {led}"
w223_merged_n = w223_out["null_pool_cumulative"]["merged"]["n_values"]
assert w223_merged_n == 488_520, f"leg0 failed: W223 merged pool drift {w223_merged_n}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W223-registered",
                          "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
                          "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
                          "ordinal": 214, "bmc_ordinal": 54,
                          "bmc_ordinal_note": ("bm-c attempt-continuity: W223 freeze receipt = 53rd owned "
                                               "(52 live rows + W223 candidate at r934 splice); this "
                                               "candidate = 54th per the same continuity; live derive governs r359"),
                          "anchor": ("W223 finalize LANDED (ledger 914,389 = prev 912,189 + 2,200, "
                                     "K=488,520, mu=-0.0928 sigma=0.2451 machine-read; r934 dead-window body "
                                     "(splice+burn+six-gate+finalize) landed by r935 absorb; PRE-FINALIZE six-gate all-green "
                                     "correct-phase 3rd consecutive; W224 burn window = PRE-FINALIZE standing law); upstream "
                                     "W2..W223 ALL REGISTERED single state -- W224 freeze = clean "
                                     "chain-order window, zero in-flight declared seats")}
print(f"leg0: {len(N1_BANDS)} rows tail=W223 registered, owner={owner_total} -> 213th wave, bm-c 54th owned (continuity), anchor W223 ledger head {led.get('total')} K={w223_merged_n}")

# --- W224 own vacancy on origin (both states) ----------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w224_seats = [ln for ln in all_inbox if "w224" in ln.lower() and "seat" in ln.lower()]
assert w224_seats == [], f"vacancy failed: W224 seats already exist: {w224_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '224: {"a": (' not in out_pf, "vacancy failed: W224 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W224"' not in outn1_vac, "vacancy failed: W224 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W224_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W224 per-wave prereg ALREADY on origin"
print("vacancy: W224 origin vacancy held (no seat / row / configs / prereg)")

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the registered W223 tails ------------------
ARITH_A = (W223_A[1] + 1, W223_A[1] + WIDTH_A)
ARITH_B = (W223_B[1] + 1, W223_B[1] + WIDTH_B)


def first_clean(lo, width, trace=None, extra_bands=()):
    hops = 0
    prev_lo = lo
    while True:
        hi = lo + width - 1
        bad_pts = [p for p in points if lo <= p <= hi]
        bad_bands = [b for b in list(bands) + list(extra_bands) + actual
                     if overlaps((lo, hi), b)]
        if not bad_pts and not bad_bands:
            return (lo, hi), hops
        jump = max([p + 1 for p in bad_pts] + [b[1] + 1 for b in bad_bands])
        assert jump > prev_lo, f"non-rotational violation: jump {jump} <= {prev_lo}"
        if trace is not None:
            trace.append({"hop": hops + 1, "window": [lo, hi], "jump_to": jump})
        lo = jump
        prev_lo = lo
        hops += 1


(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A)
b_trace = []
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace,
                             extra_bands=(fc_a,))
(fc_b_naive, hops_b_naive) = first_clean(ARITH_B[0], WIDTH_B)
assert fc_a[0] == W223_B[1] + 1, "leg1 staircase A base != prior-wave B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase A-hops-prior-B EIGHTY-FOURTH "
                               "instance expected per W223 seat MSG leg4 projection line)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation from registered W223 A tail REFUSED at start by "
                    "registered W223 B band (staircase A-hops-prior-B EIGHTY-FOURTH instance, E36 "
                    "card, per the W223 seat MSG leg4 anticipation); honest forward walk, non-rotational r587"),
    "B_semantics": ("B naive first-clean lands INSIDE own-wave A window -- same-freeze mutual "
                    "exclusion (W141 precedent, leg2 law); reserved walk past own-A, hops machine-counted"),
}
print(f"leg1: A {fc_a[0]}..{fc_a[1]} hops={hops_a} + B {fc_b[0]}..{fc_b[1]} hops={hops_b} (naive B {fc_b_naive[0]}..{fc_b_naive[1]} inside own-A; staircase held)")

# --- leg 2: full reserved universe conflict scan ------------------------------
conflicts = []
for tag, band in (("A", fc_a), ("B", fc_b)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} x W224-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W224-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W224-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W224-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W224-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W224-{tag}")
assert not conflicts, f"leg2 failed: W224 conflicts {conflicts}"

# --- seed_admit_gate (O-20261010-1945-bm-a ADMIT convention upgrade) ------------
gate_lines = []
for base, span in ((fc_a[0], WIDTH_A), (fc_b[0], WIDTH_B)):
    g = subprocess.run([sys.executable, os.path.join(ROOT, "Tools", "seed_admit_gate.py"),
                        str(base), "--span", str(span)],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", creationflags=CREAT)
    assert g.returncode == 0, f"seed_admit_gate FAIL base={base}: {g.stdout} {g.stderr}"
    gate_lines.append(g.stdout.strip().splitlines()[-1] if g.stdout.strip() else f"rc0 base={base} span={span}")
receipt["legs"]["leg2"] = {"conflicts": 0, "seed_admit_gate": gate_lines}
print("leg2: conflicts=0; seed_admit_gate:", " | ".join(gate_lines))

# --- leg 3: origin vacancy (recorded; W224 seat must NOT exist yet) -------------
receipt["legs"]["leg3"] = {"origin_vacancy": True}
print("leg3: origin vacancy held (no W224 seat / row / configs / prereq)")

# --- leg 4: W224+ projection (probe tail, next freezer re-derives) -------------
(fc223_a, h222a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc223_b, h222b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside223 = overlaps(fc223_b, fc223_a)
receipt["legs"]["leg4"] = {"W224p_A": f"{fc223_a[0]}..{fc223_a[1]}", "hops_A": h222a,
                           "W224p_B": f"{fc223_b[0]}..{fc223_b[1]}", "hops_B": h222b,
                           "W224p_B_lands_inside_W224p_A": inside223,
                           "note": ("W224+ naive projection on pre-W224 universe; "
                                    "the registered W224 B band will refuse the naive W224 A window "
                                    "once W224 is registered (A-hops-prior-B EIGHTY-FIFTH instance "
                                    "anticipated); W224 freezer MUST re-derive on the post-W224 universe "
                                    "AND reserve own-wave A when deriving B (W141 precedent, leg2 law, "
                                    "E36 staircase card) -- never transcribe r587)")}
print(f"leg4: W224+ projection A {fc223_a[0]}..{fc223_a[1]} hops={h222a} / B {fc223_b[0]}..{fc223_b[1]} hops={h222b} (B inside A: {inside223})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_w224bmc_20261012_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W224 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
