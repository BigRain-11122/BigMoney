# -*- coding: utf-8 -*-
"""r865 bm-a W182 pre-seat probe -- read-only band derivation before the seat
MSG publication (r565 early-visibility law). Machine-derived from the LIVE
post-W181-registration universe (r587: never transcribed).

W182 candidate = first FREE number after the REGISTERED W181 row (bm-a r863
freeze landed + burn 12/12 + r864 finalize one-pass EXACT, ledger head
804,518 machine-read, pool K per n1_w181_results.json). Derivation faces
(STAIRCASE GEOMETRY FORTY-SECOND instance expected, W141 leg2 law + E36 card;
anticipated verbatim by the r862 W181 probe leg4 + W181 seat MSG leg4 --
"W182 freezer MUST re-derive on the post-W181 universe AND reserve own-wave A
when deriving B" is MANDATORY, this probe IS that re-derive):
  A  arithmetic continuation from the registered W181 A tail (live-registry
     read) -- expected REFUSED at its own start by the registered W181 B band
     415_004..415_203 (staircase A-hops-prior-B 42nd); honest forward walk ->
     first-clean, hops counted.
  B  arithmetic continuation from the registered W181 B tail -- naive lands
     INSIDE the W182 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean.
Bloodline: r862 _r862bma_w181_probe.py derive machinery verbatim, W182 facts
live-registry-driven."""
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
receipt = {"probe": "r865 W182 pre-seat probe", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

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

# --- leg 0: registry shape (single state: W181 registered, tail=W181) ----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 182))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W181_A = tuple(N1_BANDS[181]["a"])
W181_B = tuple(N1_BANDS[181]["b_exit"])
assert W181_A == (413_004, 415_003) and W181_B == (415_004, 415_203) and \
    N1_BANDS[181].get("engine_owner") == "bm-a", "leg0 failed: W181 row drift"
assert tuple(N1_BANDS[180]["a"]) == (410_804, 412_803) and \
    tuple(N1_BANDS[180]["b_exit"]) == (412_804, 413_003), "leg0 W180 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 171 and len(bma_rows) == 97, "leg0 ordinal drift"
# W181 finalize product machine-read (r587 never-transcribe face)
w181_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w181_results.json"), encoding="utf-8"))
led = (w181_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 804_518 and led.get("prev_total") == 802_318, \
    f"leg0 failed: W181 ledger machine-read drift {led}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W181",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 172, "bma_ordinal": 98,
                           "w181_ledger_head": led.get("total")}
print(f"leg0: {len(N1_BANDS)} rows tail=W181, owner={len(owner_rows)} -> 172nd wave, bm-a 98th owned, W181 ledger head {led.get('total')}")

# --- leg 1: honest forward walk from the live-registry W181 tails -------------
ARITH_A = (W181_A[1] + 1, W181_A[1] + WIDTH_A)
ARITH_B = (W181_B[1] + 1, W181_B[1] + WIDTH_B)


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
assert fc_a[0] == W181_B[1] + 1, "leg1 staircase A base != prior-B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per r862 W181 probe leg4 "
                               "W182+ MANDATORY re-derive)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation REFUSED at start by registered W181 B band "
                     "415_004..415_203 (staircase A-hops-prior-B FORTY-SECOND instance, E36 card; "
                     "r862 W181 probe leg4 + W181 seat MSG leg4 anticipated + MANDATED "
                     "this re-derive); honest forward walk, non-rotational r587"),
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W182-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W182-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W182-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W182-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W182-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W182-{tag}")
assert not conflicts, f"leg2 failed: W182 conflicts {conflicts}"

# --- leg 3: origin vacancy (W182 seat must NOT exist yet; row/configs absent) --
r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                    "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                   capture_output=True)
seats = [ln for ln in r.stdout.decode("utf-8").splitlines()
         if "w182" in ln.lower() and "seat" in ln.lower()]
assert seats == [], f"leg3 failed: W182 seats already exist: {seats}"
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                              cwd=ROOT, encoding="utf-8", errors="replace")
assert '182: {"a": (' not in out, "leg3 failed: W182 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
                                cwd=ROOT, encoding="utf-8", errors="replace")
assert '"batch": "PERPETUAL-N1-W182"' not in outn1, "leg3 failed: W182 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                  "research/PERPETUAL_N1_W182_PREREG.md"], cwd=ROOT,
                                 encoding="utf-8", errors="replace").strip()
assert not outpre, "leg3 failed: W182 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0}
receipt["legs"]["leg3"] = {"origin_vacancy": True}

# --- leg 4: W183+ projection (probe tail, next freezer re-derives) -------------
(fc183_a, h182a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc183_b, h182b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside182 = overlaps(fc183_b, fc183_a)
receipt["legs"]["leg4"] = {"W183p_A": f"{fc183_a[0]}..{fc183_a[1]}", "hops_A": h182a,
                           "W183p_B": f"{fc183_b[0]}..{fc183_b[1]}", "hops_B": h182b,
                           "W183p_B_lands_inside_W183p_A": inside182,
                           "note": ("W183+ naive projection on pre-W182 universe; "
                                    "W182-B-refuses-W183-A staircase anticipated once W182 B registered; "
                                    "W183 freezer MUST re-derive on the post-W182 universe AND reserve "
                                    "own-wave A when deriving B (W141 precedent, leg2 law, E36 staircase card) "
                                    "-- never transcribe r587")}
print(f"leg4: W183+ projection A {fc183_a[0]}..{fc183_a[1]} hops={h182a} / B {fc183_b[0]}..{fc183_b[1]} hops={h182b} (B inside A: {inside182})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r865bma_w182_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W182 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
