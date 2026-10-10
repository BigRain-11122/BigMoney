# -*- coding: utf-8 -*-
"""W207 pre-seat probe (bm-b, 2026-10-10 23:4x; O-20261010-2350-bm-c CEO fill-order
RE-ISSUE standing '机队CPU算力全部用于回测，排满' sec.2 @bm-b engine-in-service
seat-first mandate + O-20260924-1730 claim-and-start same-round law)
-- read-only band derivation before the seat MSG publication (r565 early-visibility
law). Machine-derived from the LIVE post-W204 universe + the DECLARED W205 and
W206 bands (r587: never transcribed).

W207 candidate = first FREE number after the bm-c W206 SEAT
(MSG-20261010-2323-bmc-w206-seat published on origin; W206 freeze gated on W205
landing -- five-face band row + per-wave prereg PENDING on origin at probe time
-- W206 bands are SEAT-DECLARED in the bm-c seat MSG and are injected into this
probe's universe with origin-text verification, honest note -- exact mirror of
the W192/r892 + W204/r837 + W206 declared-injection precedents; W205 declared
bands likewise origin-text-verified and injected, W205 seat leg4 + W206 seat
leg4 both anticipated this re-derive as MANDATORY).
Derivation faces (STAIRCASE GEOMETRY SIXTY-SEVENTH instance expected, W141 leg2
law + E36 card; anticipated verbatim by the W206 seat leg4 projection +
_w206bmc probe leg4 -- 'W207 freezer MUST re-derive on the post-W206 universe
AND reserve own-wave A when deriving B' is MANDATORY, this probe IS that
re-derive):
  A  arithmetic continuation from the declared W206 A tail -- REFUSED at
     its own start by the declared W206 B band 470_004..470_203
     (staircase A-hops-prior-B 67th); honest forward walk -> first-clean.
  B  arithmetic continuation from the declared W206 B tail -- naive lands
     INSIDE the W207 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean.
Bloodline: _w206bmc_20261010_probe.py derive machinery verbatim, W207 facts
live-registry-driven; W205+W206-declared-band injection = the leg4-mandated
post-W206 universe (probe-time honest note: N1_BANDS tail = W204 registered;
W205 five-face + prereg pending bm-a side, W206 freeze-prep pending bm-c side)."""
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
receipt = {"probe": "W207 pre-seat probe (bm-b, 2026-10-10 23:4x, O-20261010-2350-bm-c sec.2 @bm-b seat-first + O-2334 local-full-use)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- W205 + W206 declared bands: origin-text verified (both seat MSGs on origin)
w205_seat = subprocess.check_output(
    ["git", "show", "origin/main:fleet/inbox/processed/MSG-2026-10-10-1627-bma-w205-seat.md"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert "**A 465_804..467_803**" in w205_seat and \
       "**B 467_804..468_003**" in w205_seat, \
    "W205 declared bands not found in origin seat MSG text"
w206_seat = subprocess.check_output(
    ["git", "show", "origin/main:fleet/inbox/MSG-20261010-2323-bmc-w206-seat.md"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert "**A 468_004..470_003**" in w206_seat and \
       "**B 470_004..470_203**" in w206_seat, \
    "W206 declared bands not found in origin seat MSG text"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '205: {"a": (' not in out_pf, \
    "W205 five-face row ALREADY on origin -- injection premise broken, re-derive live"
assert '206: {"a": (' not in out_pf, \
    "W206 five-face row ALREADY on origin -- injection premise broken, re-derive live"
outn1_chk = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W205"' not in outn1_chk and \
       '"PERPETUAL-N1-W206"' not in outn1_chk, \
    "W205/W206 WAVE_CONFIGS ALREADY on origin -- re-derive live"
W205_DECL_A = (465_804, 467_803)
W205_DECL_B = (467_804, 468_003)
W206_DECL_A = (468_004, 470_003)
W206_DECL_B = (470_004, 470_203)

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
bands += [W205_DECL_A, W205_DECL_B]   # post-W205-declaration universe
bands += [W206_DECL_A, W206_DECL_B]   # post-W206-declaration universe (W206 seat leg4 mandate)
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (single state: N1_BANDS tail=W204, W205+W206 seat-reserved pending)
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 205))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W204_A = tuple(N1_BANDS[204]["a"])
W204_B = tuple(N1_BANDS[204]["b_exit"])
assert W204_A == (463_604, 465_603) and W204_B == (465_604, 465_803) and \
    N1_BANDS[204].get("engine_owner") == "bm-c", "leg0 failed: W204 row drift"
assert tuple(N1_BANDS[203]["a"]) == (461_404, 463_403) and \
    tuple(N1_BANDS[203]["b_exit"]) == (463_404, 463_603) and \
    N1_BANDS[203].get("engine_owner") == "bm-a", "leg0 failed: W203 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
assert len(owner_rows) == 194 and len(bmc_rows) == 36 and len(bma_rows) == 118, \
    f"leg0 ordinal drift: owner={len(owner_rows)} bmc={len(bmc_rows)} bma={len(bma_rows)}"
assert len(bmb_rows) == len(owner_rows) - len(bmc_rows) - len(bma_rows), \
    "leg0 owner-sum consistency failed"

w204_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w204_results.json"), encoding="utf-8"))
led = (w204_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 864_387 and led.get("prev_total") == 862_187, \
    f"leg0 failed: W204 ledger machine-read drift {led}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W204",
                           "owner_rows": len(owner_rows), "bmc_rows": len(bmc_rows),
                           "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
                           "ordinal": 197, "bmb_ordinal": len(bmb_rows) + 1,
                           "w204_ledger_head": led.get("total"),
                           "w205_status": ("seat-reserved bm-a 16:27 (MSG-2026-10-10-1627 on origin, processed/; "
                                           "probe receipt r956 landed); five-face band row + per-wave prereg "
                                           "PENDING on origin at probe time -- declared bands 465_804..467_803 / "
                                           "467_804..468_003 origin-text-verified and injected"),
                           "w206_status": ("seat-reserved bm-c 23:23 (MSG-20261010-2323 on origin, inbox/; "
                                           "probe receipt landed 0620f78fd); freeze gated on W205 landing -- "
                                           "five-face band row + per-wave prereg PENDING on origin at probe time -- "
                                           "declared bands 468_004..470_003 / 470_004..470_203 origin-text-verified "
                                           "and injected per the W206 seat leg4 mandate"),
                           "w205_declared": {"A": list(W205_DECL_A), "B": list(W205_DECL_B)},
                           "w206_declared": {"A": list(W206_DECL_A), "B": list(W206_DECL_B)}}
print(f"leg0: {len(N1_BANDS)} rows tail=W204, owner={len(owner_rows)} -> 197th wave, bm-b {len(bmb_rows) + 1}th owned, anchor W204 ledger head {led.get('total')}; W205+W206 five-face pending (declared bands injected)")

# --- leg 1: honest forward walk from the declared W206 tails ---------------------
ARITH_A = (W206_DECL_A[1] + 1, W206_DECL_A[1] + WIDTH_A)
ARITH_B = (W206_DECL_B[1] + 1, W206_DECL_B[1] + WIDTH_B)


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
assert fc_a[0] == W206_DECL_B[1] + 1, "leg1 staircase A base != prior-B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per W206 seat leg4 "
                              "projection + W206 probe leg4 MANDATORY re-derive)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
assert fc_a == (470_204, 472_203) and fc_b == (472_204, 472_403), \
    f"leg1 band drift vs W206 seat leg4 mandate: A {fc_a} B {fc_b}"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation REFUSED at start by declared W206 B band "
                    "470_004..470_203 (staircase A-hops-prior-B SIXTY-SEVENTH instance, E36 card; "
                    "W206 seat leg4 projection + W206 probe leg4 anticipated and MANDATED this "
                    "re-derive); honest forward walk, non-rotational r587"),
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W207-{tag}")
    for nm, db in (("W205-declared-A", W205_DECL_A), ("W205-declared-B", W205_DECL_B),
                   ("W206-declared-A", W206_DECL_A), ("W206-declared-B", W206_DECL_B)):
        if overlaps(db, band):
            conflicts.append(f"{nm} x W207-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W207-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W207-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W207-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W207-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W207-{tag}")
assert not conflicts, f"leg2 failed: W207 conflicts {conflicts}"

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

# --- leg 3: origin vacancy (W207 seat must NOT exist yet; row/configs absent) --
r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                    "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                   capture_output=True)
seats = [ln for ln in r.stdout.decode("utf-8").splitlines()
         if "w207" in ln.lower() and "seat" in ln.lower()]
assert seats == [], f"leg3 failed: W207 seats already exist: {seats}"
assert '207: {"a": (' not in out_pf, "leg3 failed: W207 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
                                cwd=ROOT, encoding="utf-8", errors="replace")
assert '"batch": "PERPETUAL-N1-W207"' not in outn1, "leg3 failed: W207 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                  "research/PERPETUAL_N1_W207_PREREG.md"], cwd=ROOT,
                                 encoding="utf-8", errors="replace").strip()
assert not outpre, "leg3 failed: W207 per-wave prereg ALREADY on origin"
receipt["legs"]["leg3"] = {"origin_vacancy": True}
print("leg3: origin vacancy held (no W207 seat / row / configs / prereg)")

# --- leg 4: W208+ projection (probe tail, next freezer re-derives) -------------
(fc208_a, h207a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc208_b, h207b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside208 = overlaps(fc208_b, fc208_a)
receipt["legs"]["leg4"] = {"W208p_A": f"{fc208_a[0]}..{fc208_a[1]}", "hops_A": h207a,
                           "W208p_B": f"{fc208_b[0]}..{fc208_b[1]}", "hops_B": h207b,
                           "W208p_B_lands_inside_W208p_A": inside208,
                           "note": ("W208+ naive projection on pre-W207 universe; "
                                    "the registered W207 B band 472_204..472_403 will refuse the naive W208 A window "
                                    "once W207 is registered (A-hops-prior-B SIXTY-EIGHTH instance "
                                    "anticipated); W208 freezer MUST re-derive on the post-W207 universe "
                                    "AND reserve own-wave A when deriving B (W141 precedent, leg2 law, "
                                    "E36 staircase card) -- never transcribe r587)")}
print(f"leg4: W208+ projection A {fc208_a[0]}..{fc208_a[1]} hops={h207a} / B {fc208_b[0]}..{fc208_b[1]} hops={h207b} (B inside A: {inside208})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_w207bmb_20261010_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W207 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
