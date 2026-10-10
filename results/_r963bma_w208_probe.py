# -*- coding: utf-8 -*-
"""W208 pre-seat probe (bm-a, 2026-10-11 01:2x; O-20261011-0012 CEO direct order
'给我利用好机队的 CPU 算力' sec.ii queue-deepen seat-chain mandate + O-20261010-2350-bm-c
RE-ISSUE sec.2 seat-first law + O-20260924-1730 claim-and-start same-round law)
-- read-only band derivation before the seat MSG publication (r565 early-visibility
law). Machine-derived from the LIVE post-W205-REGISTERED universe + the DECLARED
W206 and W207 bands (r587: never transcribed).

W208 candidate = first FREE number after the bm-b W207 SEAT
(MSG-20261010-2335-bmb-w207-seat published on origin, processed/; W206/W207
five-face band rows + per-wave preregs PENDING on origin at probe time -- both
seats' bands are SEAT-DECLARED in their origin seat MSGs and injected into this
probe's universe with origin-text verification, honest note -- exact mirror of
the W192/r892 + W204/r837 + W206/r837 declared-injection precedents; the W205
seat leg4 + W206 seat leg4 + W207 seat leg4 all mandated this re-derive).
Derivation faces (STAIRCASE GEOMETRY SIXTY-EIGHTH instance expected, W141 leg2
law + E36 card; anticipated verbatim by the W207 seat leg4 projection +
_w207bmb probe leg4 -- 'W208 freezer MUST re-derive on the post-W207 universe
AND reserve own-wave A when deriving B' is MANDATORY, this probe IS that
re-derive):
  A  arithmetic continuation from the declared W207 A tail -- REFUSED at
     its own start by the declared W207 B band 472_204..472_403
     (staircase A-hops-prior-B 68th); honest forward walk -> first-clean.
  B  arithmetic continuation from the declared W207 B tail -- naive lands
     INSIDE the W208 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean.
Bloodline: _w207bmb_20261010_probe.py derive machinery verbatim, W208 facts
live-registry-driven; W205 REGISTERED (five-face + finalize landed this window
r963 -- finalize product pushed in the same payload as this seat, honest
note) + W206/W207-declared-band injection = the leg4-mandated post-W207
universe (probe-time honest note: N1_BANDS tail = W205 registered; W206 freeze
unblocked by W205 landing this window (bm-c cron watches), W207 freeze-prep
pending bm-b side)."""
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
receipt = {"probe": "W208 pre-seat probe (bm-a, 2026-10-11 01:2x, O-20261011-0012 sec.ii seat-chain + O-20261010-2350-bm-c sec.2 seat-first + O-2334 local-full-use)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- W206 + W207 declared bands: origin-text verified (both seat MSGs on origin, processed/)
w206_seat = subprocess.check_output(
    ["git", "show", "origin/main:fleet/inbox/processed/MSG-20261010-2323-bmc-w206-seat.md"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert "**A 468_004..470_003**" in w206_seat and \
       "**B 470_004..470_203**" in w206_seat, \
    "W206 declared bands not found in origin seat MSG text"
w207_seat = subprocess.check_output(
    ["git", "show", "origin/main:fleet/inbox/processed/MSG-20261010-2335-bmb-w207-seat.md"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert "**A 470_204..472_203**" in w207_seat and \
       "**B 472_204..472_403**" in w207_seat, \
    "W207 declared bands not found in origin seat MSG text"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '206: {"a": (' not in out_pf, \
    "W206 five-face row ALREADY on origin -- injection premise broken, re-derive live"
assert '207: {"a": (' not in out_pf, \
    "W207 five-face row ALREADY on origin -- injection premise broken, re-derive live"
assert '205: {"a": (465_804, 467_803), "b_exit": (467_804, 468_003),' in out_pf, \
    "leg0 failed: W205 five-face row NOT on origin (registered-universe premise broken)"
outn1_chk = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W206"' not in outn1_chk and \
       '"PERPETUAL-N1-W207"' not in outn1_chk, \
    "W206/W207 WAVE_CONFIGS ALREADY on origin -- re-derive live"
W206_DECL_A = (468_004, 470_003)
W206_DECL_B = (470_004, 470_203)
W207_DECL_A = (470_204, 472_203)
W207_DECL_B = (472_204, 472_403)

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
bands += [W206_DECL_A, W206_DECL_B]   # post-W206-declaration universe (declared-injection)
bands += [W207_DECL_A, W207_DECL_B]   # post-W207-declaration universe (W207 seat leg4 mandate)
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (single state: N1_BANDS tail=W205 REGISTERED, W206+W207 seat-reserved pending)
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 206))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W205_A = tuple(N1_BANDS[205]["a"])
W205_B = tuple(N1_BANDS[205]["b_exit"])
assert W205_A == (465_804, 467_803) and W205_B == (467_804, 468_003) and \
    N1_BANDS[205].get("engine_owner") == "bm-a", "leg0 failed: W205 row drift"
assert tuple(N1_BANDS[204]["a"]) == (463_604, 465_603) and \
    tuple(N1_BANDS[204]["b_exit"]) == (465_604, 465_803) and \
    N1_BANDS[204].get("engine_owner") == "bm-c", "leg0 failed: W204 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
assert len(owner_rows) == 195 and len(bmc_rows) == 36 and len(bma_rows) == 119, \
    f"leg0 ordinal drift: owner={len(owner_rows)} bmc={len(bmc_rows)} bma={len(bma_rows)}"
assert len(bmb_rows) == len(owner_rows) - len(bmc_rows) - len(bma_rows), \
    "leg0 owner-sum consistency failed"

w205_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w205_results.json"), encoding="utf-8"))
led = (w205_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 868_171 and led.get("prev_total") == 865_971, \
    f"leg0 failed: W205 ledger machine-read drift {led}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W205",
                           "owner_rows": len(owner_rows), "bmc_rows": len(bmc_rows),
                           "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
                           "ordinal": 198, "bma_ordinal": len(bma_rows) + 1,
                           "w205_ledger_head": led.get("total"),
                           "w205_status": ("REGISTERED five-face (origin machine-read 205: row, "
                                           "engine_owner=bm-a) + finalize LANDED this window r963 "
                                           "(ledger 865,971+2,200=868,171 EXACT local machine-read; "
                                           "finalize product pushed in the same payload as this seat, "
                                           "honest note); W204 total 864,387 <= W205 prev 865,971 "
                                           "(delta 1,584 = interim legal appends by other batches, "
                                           "live-head derive law)"),
                           "w206_status": ("seat-reserved bm-c 23:23 (MSG-20261010-2323 on origin, "
                                           "processed/); freeze UNBLOCKED by W205 landing this window "
                                           "(bm-c cron watches); five-face band row + per-wave prereg "
                                           "PENDING on origin at probe time -- declared bands "
                                           "468_004..470_003 / 470_004..470_203 origin-text-verified "
                                           "and injected"),
                           "w207_status": ("seat-reserved bm-b 23:35 (MSG-20261010-2335 on origin, "
                                           "processed/); freeze-prep pending bm-b side -- declared "
                                           "bands 470_204..472_203 / 472_204..472_403 origin-text-"
                                           "verified and injected per the W207 seat leg4 mandate"),
                           "w206_declared": {"A": list(W206_DECL_A), "B": list(W206_DECL_B)},
                           "w207_declared": {"A": list(W207_DECL_A), "B": list(W207_DECL_B)}}
print(f"leg0: {len(N1_BANDS)} rows tail=W205, owner={len(owner_rows)} -> 198th wave, bm-a {len(bma_rows) + 1}th owned, anchor W205 ledger head {led.get('total')}; W206+W207 five-face pending (declared bands injected)")

# --- leg 1: honest forward walk from the declared W207 tails ---------------------
ARITH_A = (W207_DECL_A[1] + 1, W207_DECL_A[1] + WIDTH_A)
ARITH_B = (W207_DECL_B[1] + 1, W207_DECL_B[1] + WIDTH_B)


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
assert fc_a[0] == W207_DECL_B[1] + 1, "leg1 staircase A base != prior-B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per W207 seat leg4 "
                              "projection + W207 probe leg4 MANDATORY re-derive)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
assert fc_a == (472_404, 474_403) and fc_b == (474_404, 474_603), \
    f"leg1 band drift vs W207 seat leg4 mandate: A {fc_a} B {fc_b}"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation REFUSED at start by declared W207 B band "
                    "472_204..472_403 (staircase A-hops-prior-B SIXTY-EIGHTH instance, E36 card; "
                    "W207 seat leg4 projection + W207 probe leg4 anticipated and MANDATED this "
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W208-{tag}")
    for nm, db in (("W206-declared-A", W206_DECL_A), ("W206-declared-B", W206_DECL_B),
                   ("W207-declared-A", W207_DECL_A), ("W207-declared-B", W207_DECL_B)):
        if overlaps(db, band):
            conflicts.append(f"{nm} x W208-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W208-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W208-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W208-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W208-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W208-{tag}")
assert not conflicts, f"leg2 failed: W208 conflicts {conflicts}"

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

# --- leg 3: origin vacancy (W208 seat must NOT exist yet; row/configs absent) --
r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                    "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                   capture_output=True)
seats = [ln for ln in r.stdout.decode("utf-8").splitlines()
         if "w208" in ln.lower() and "seat" in ln.lower()]
assert seats == [], f"leg3 failed: W208 seats already exist: {seats}"
assert '208: {"a": (' not in out_pf, "leg3 failed: W208 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
                                cwd=ROOT, encoding="utf-8", errors="replace")
assert '"batch": "PERPETUAL-N1-W208"' not in outn1, "leg3 failed: W208 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                  "research/PERPETUAL_N1_W208_PREREG.md"], cwd=ROOT,
                                 encoding="utf-8", errors="replace").strip()
assert not outpre, "leg3 failed: W208 per-wave prereg ALREADY on origin"
receipt["legs"]["leg3"] = {"origin_vacancy": True}
print("leg3: origin vacancy held (no W208 seat / row / configs / prereg)")

# --- leg 4: W209+ projection (probe tail, next freezer re-derives) -------------
(fc209_a, h208a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc209_b, h208b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside209 = overlaps(fc209_b, fc209_a)
receipt["legs"]["leg4"] = {"W209p_A": f"{fc209_a[0]}..{fc209_a[1]}", "hops_A": h208a,
                           "W209p_B": f"{fc209_b[0]}..{fc209_b[1]}", "hops_B": h208b,
                           "W209p_B_lands_inside_W209p_A": inside209,
                           "note": ("W209+ naive projection on pre-W208 universe; "
                                    f"the registered W208 B band {fc_b[0]}_{fc_b[1]} will refuse the naive W209 A window "
                                    "once W208 is registered (A-hops-prior-B SIXTY-NINTH instance "
                                    "anticipated); W209 freezer MUST re-derive on the post-W208 universe "
                                    "AND reserve own-wave A when deriving B (W141 precedent, leg2 law, "
                                    "E36 staircase card) -- never transcribe r587)")}
print(f"leg4: W209+ projection A {fc209_a[0]}..{fc209_a[1]} hops={h208a} / B {fc209_b[0]}..{fc209_b[1]} hops={h208b} (B inside A: {inside209})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r963bma_w208_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W208 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
