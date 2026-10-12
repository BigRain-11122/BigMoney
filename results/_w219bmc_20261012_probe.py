# -*- coding: utf-8 -*-
"""W219 pre-seat probe (bm-c loop window r919, 2026-10-12 09:2x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law). Upstream face = W218 FULL CYCLE LANDED (r917
seat MSG-20261012-0830 + r918 prereg+five-face freeze splice 9afb0b1d7 +
engine self-burn 12/12 ledger-appended 3c58e0e77/6afa2661f + finalize one-pass
09:1x [dead-session r918 body absorbed+landed by r919 this
window]: ledger 901,189+2,200=903,389 EXACT, merged pool K=477,520,
results/perpetual_faces/n1_w218_results.json machine-read) --
SINGLE STATE: W2..W218 ALL REGISTERED, zero in-flight declared seats. This
probe IS the W219 re-derive on the post-W218-REGISTERED universe mandated by
the W218 prereg sec.5 key5 + sec.8 projection (r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W218-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W208..W218 eleven faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY SEVENTY-NINTH instance expected, W141
leg2 law + E36 card; the W218 sec.8 projection anticipated W219+ -- this
probe IS that re-derive):
  A  arithmetic continuation from the registered W218 A tail -- expected
     REFUSED at its own start by the registered W218 B band (staircase
     A-hops-prior-B 79th); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W218 B tail -- naive lands
     INSIDE the W219 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base
     == own-wave A tail+1 machine-checkable relation.
Anchor face: W218 finalize LANDED (ledger head 903,389 = prev 901,189 +
2,200; merged pool K=477,520 machine-read in leg0; five-key ALL PASS
_r919bmc_w218_fivekey_receipt.json). W219 freeze is GATED on nothing
in-flight -- upstream fully landed, clean chain-order window.
Bloodline: _w218bmc_20261012_probe.py derive machinery verbatim, W219 facts
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
receipt = {"probe": "W219 pre-seat probe (bm-c loop r919, 2026-10-12 09:2x, CEO fill-order standing + seat-first law + never-dry supply line; post-W218-REGISTERED single-state universe, upstream W218 full cycle landed r917/r918/r919-absorb)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape (post-W218 universe: tail=W218 registered) -----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 219))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W218_A = tuple(N1_BANDS[218]["a"])
W218_B = tuple(N1_BANDS[218]["b_exit"])
assert W218_A == (494_404, 496_403) and W218_B == (496_404, 496_603) and \
    N1_BANDS[218].get("engine_owner") == "bm-c", "leg0 failed: W218 row drift (bm-c r918 freeze face)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 208 and len(bmc_rows) == 48, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 208/48 post-W218-splice per the r918 freeze receipt ordinal faces)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

w218_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w218_results.json"), encoding="utf-8"))
led = (w218_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 903_389 and led.get("prev_total") == 901_189, \
    f"leg0 failed: W218 ledger machine-read drift {led}"
w218_merged_n = w218_out["null_pool_cumulative"]["merged"]["n_values"]
assert w218_merged_n == 477_520, f"leg0 failed: W218 merged pool drift {w218_merged_n}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W218-registered",
                          "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
                          "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
                          "ordinal": 209, "bmc_ordinal": 49,
                          "bmc_ordinal_note": ("bm-c attempt-continuity: W218 freeze receipt = 48th owned "
                                               "(47 live rows + W218 candidate at r918 splice); this "
                                               "candidate = 49th per the same continuity; live derive governs r359"),
                          "anchor": ("W218 finalize LANDED (ledger 903,389 = prev 901,189 + 2,200, "
                                     "K=477,520, mu=-0.09278 sigma=0.24511 machine-read; r918 freeze/burn body "
                                     "absorbed and landed by r919); upstream "
                                     "W2..W218 ALL REGISTERED single state -- W219 freeze = clean "
                                     "chain-order window, zero in-flight declared seats")}
print(f"leg0: {len(N1_BANDS)} rows tail=W218 registered, owner={owner_total} -> 209th wave, bm-c 49th owned (continuity), anchor W218 ledger head {led.get('total')} K={w218_merged_n}")

# --- W219 own vacancy on origin (both states) ----------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w219_seats = [ln for ln in all_inbox if "w219" in ln.lower() and "seat" in ln.lower()]
assert w219_seats == [], f"vacancy failed: W219 seats already exist: {w219_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '219: {"a": (' not in out_pf, "vacancy failed: W219 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W219"' not in outn1_vac, "vacancy failed: W219 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W219_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W219 per-wave prereg ALREADY on origin"
print("vacancy: W219 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the registered W218 tails ------------------
ARITH_A = (W218_A[1] + 1, W218_A[1] + WIDTH_A)
ARITH_B = (W218_B[1] + 1, W218_B[1] + WIDTH_B)


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
assert fc_a[0] == W218_B[1] + 1, "leg1 staircase A base != prior-wave B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase A-hops-prior-B SEVENTY-NINTH "
                              "instance expected per W218 sec.8 projection line)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation from registered W218 A tail REFUSED at start by "
                    "registered W218 B band (staircase A-hops-prior-B SEVENTY-NINTH instance, E36 "
                    "card, per the W218 sec.8 anticipation); honest forward walk, non-rotational r587"),
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W219-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W219-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W219-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W219-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W219-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W219-{tag}")
assert not conflicts, f"leg2 failed: W219 conflicts {conflicts}"

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

# --- leg 3: origin vacancy (recorded; W219 seat must NOT exist yet) -------------
receipt["legs"]["leg3"] = {"origin_vacancy": True}
print("leg3: origin vacancy held (no W219 seat / row / configs / prereq)")

# --- leg 4: W220+ projection (probe tail, next freezer re-derives) -------------
(fc220_a, h219a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc220_b, h219b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside220 = overlaps(fc220_b, fc220_a)
receipt["legs"]["leg4"] = {"W220p_A": f"{fc220_a[0]}..{fc220_a[1]}", "hops_A": h219a,
                           "W220p_B": f"{fc220_b[0]}..{fc220_b[1]}", "hops_B": h219b,
                           "W220p_B_lands_inside_W220p_A": inside220,
                           "note": ("W220+ naive projection on pre-W219 universe; "
                                    "the registered W219 B band will refuse the naive W220 A window "
                                    "once W219 is registered (A-hops-prior-B EIGHTIETH instance "
                                    "anticipated); W220 freezer MUST re-derive on the post-W219 universe "
                                    "AND reserve own-wave A when deriving B (W141 precedent, leg2 law, "
                                    "E36 staircase card) -- never transcribe r587)")}
print(f"leg4: W220+ projection A {fc220_a[0]}..{fc220_a[1]} hops={h219a} / B {fc220_b[0]}..{fc220_b[1]} hops={h219b} (B inside A: {inside220})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_w219bmc_20261012_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W219 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
