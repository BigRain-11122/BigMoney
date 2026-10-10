# -*- coding: utf-8 -*-
"""W212 pre-seat probe (bm-c loop window r859, 2026-10-11 07:3x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x '机队CPU算力全部用于回测，
排满！' + never-dry supply line per the W211 r849 seat-chain continuation:
W208 claimed by bm-a (MSG-2026-10-11-0129, five-face pending bm-a side, machine
dark since 2026-10-10 21:52 -- stall notice MSG-20261011-0535 r853, no answer),
W209 = bm-c own seat published r847 (MSG-20261011-0301), W210 = bm-b seat
r857 (MSG-20261011-0319), W211 = bm-c own seat published r849
(MSG-20261011-0350) -> W212 = bm-c next own seat;
+ O-20261011-0012 sec.ii queue-deepen seat-chain mandate + O-20261010-2350-bm-c
RE-ISSUE sec.2 seat-first law (席位不排冻结窗·注册宇宙先占先公示·禁等上一波
烧完才占下一席) + O-20260924-1730 claim-ignite same-round law).
-- read-only band derivation before the seat MSG publication (r565 early-visibility
law). Machine-derived from the LIVE post-W207-REGISTERED universe (W207 five-face
+ finalize landed on origin: bm-b r856 freeze + r857 finalize, bands A 470_204..472_203
/ B 472_204..472_403 registered engine_owner=bm-b, ledger head 872,571, K=453,320)
+ the DECLARED W208 bands (bm-a seat MSG-2026-10-11-0129, five-face pending bm-a
side) + the DECLARED W209 bands (bm-c seat MSG-20261011-0301, five-face pending
bm-c side) + the DECLARED W210 bands (bm-b seat MSG-20261011-0319, seat-reserved
only, freeze gated on W209) + the DECLARED W211 bands (bm-c seat
MSG-20261011-0350, seat-reserved, freeze gated on W210) (r587: never transcribed).

TWO-STATE probe: any of the W208/W209/W210/W211 seat MSGs absent on origin ->
leg0 + W212 vacancy only, verdict AWAITING_UPSTREAM, exit 3; all present -> full
five legs, verdict ADMIT, exit 0.

W212 candidate = first FREE number after the REGISTERED W207 (bm-b) + the
DECLARED W208 (bm-a) + DECLARED W209 (bm-c) + DECLARED W210 (bm-b) + DECLARED
W211 (bm-c) faces (declared bands discovered dynamically on origin -- filename
match wNNN+seat, bolded **A x..y** / **B x..y** regex extraction, forward-of-
prior-tail filter, span-law and chain-relation asserts, injected into this
probe's universe with origin-text verification, honest note -- exact mirror of
the W205/r956 + W206 + W208/r963 + W209/r847 + W210/r857 + W211/r849
declared-injection precedents; W207 needs no injection, it is REGISTERED in the
live universe).
Derivation faces (STAIRCASE GEOMETRY SEVENTY-SECOND instance expected, W141 leg2
law + E36 card; W209's walk = 69th [declared], W210's = 70th, W211's = 71st
[declared]; the W211 bm-c seat leg4 projection anticipates W212+ -- this probe
IS that re-derive on the post-W211-declaration universe):
  A  arithmetic continuation from the declared W211 A tail -- expected REFUSED
     at its own start by the declared W211 B band (staircase A-hops-prior-B
     72nd); honest forward walk -> first-clean; A base == prior-wave B tail+1
     machine-checkable relation.
  B  arithmetic continuation from the declared W211 B tail -- naive lands
     INSIDE the W212 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W207 finalize LANDED (ledger head 872,571 = prev 870,371 + 2,200;
merged pool K=453,320 machine-read in leg0) -- W208 freeze pending bm-a side
(machine dark, stall notice unanswered), W209 freeze pending bm-c side, W210
seat-reserved bm-b, W211 seat-reserved bm-c; W212 freeze is GATED on W211
freeze+finalize (M9 chain-order); W212 freeze-time anchor per r590 line = W211
finalize actuals (pending); freeze-time guard: if the W208/W209/W210/W211 rows
land on origin before the W212 freeze, the freezer MUST re-pull and re-verify
the universe face (fail-safe leg0 assertion enforces at probe time; mirror of
the W208/W209/W210/W211 seat guard notes).
Bloodline: _w211bmc_20261011_probe.py derive machinery verbatim, W212 facts
live-registry-driven; W208+W209+W210+W211 declared-band injection = the
post-W211-declaration universe."""
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
receipt = {"probe": "W212 pre-seat probe (bm-c loop r859, 2026-10-11 07:3x, CEO fill-order standing re-issued + seat-first law + never-dry supply line; W208 declared bm-a + W209 declared bm-c + W210 declared bm-b + W211 declared bm-c injected; W207 registered + finalized by bm-b r856/r857)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape (post-W207 universe: tail=W207 registered) -----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 208))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W207_A = tuple(N1_BANDS[207]["a"])
W207_B = tuple(N1_BANDS[207]["b_exit"])
assert W207_A == (470_204, 472_203) and W207_B == (472_204, 472_403) and \
    N1_BANDS[207].get("engine_owner") == "bm-b", "leg0 failed: W207 row drift (bm-b r856 freeze face)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
assert len(owner_rows) == 197 and len(bmc_rows) == 37 and \
    len(bma_rows) == 119 and len(bmb_rows) == 41, \
    f"leg0 ordinal drift: owner={len(owner_rows)} bmc={len(bmc_rows)} bma={len(bma_rows)} bmb={len(bmb_rows)}"

w207_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w207_results.json"), encoding="utf-8"))
led = (w207_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 872_571 and led.get("prev_total") == 870_371, \
    f"leg0 failed: W207 ledger machine-read drift {led}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W207-registered",
                           "owner_rows": len(owner_rows), "bmc_rows": len(bmc_rows),
                           "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
                           "ordinal": 202, "bmc_ordinal": 41,
                           "bmc_ordinal_note": ("bm-c attempt-continuity: W211 MSG prose = 40th owned "
                                                "(W209 MSG prose = 39th with the aborted r846 W208 draft "
                                                "consuming the 38th slot); this candidate = 41st per the same continuity"),
                           "anchor": ("W207 finalize LANDED (ledger 872,571 = prev 870,371 + 2,200, K=453,320); "
                                      "W208 freeze pending bm-a side (machine dark since 2026-10-10 21:52, "
                                      "stall notice MSG-20261011-0535 unanswered), W209 freeze pending bm-c side, "
                                      "W210 seat-reserved bm-b side, W211 seat-reserved bm-c side; "
                                      "W212 freeze GATED on W211 freeze+finalize (M9 chain-order); "
                                      "W212 freeze-time anchor per r590 line = W211 finalize actuals (pending)")}
print(f"leg0: {len(N1_BANDS)} rows tail=W207 registered, owner={len(owner_rows)} -> 202nd wave, bm-c 41st owned (continuity), anchor W207 ledger head {led.get('total')}")

# --- W212 own vacancy on origin (both states) ----------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w212_seats = [ln for ln in all_inbox if "w212" in ln.lower() and "seat" in ln.lower()]
assert w212_seats == [], f"vacancy failed: W212 seats already exist: {w212_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '212: {"a": (' not in out_pf, "vacancy failed: W212 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W212"' not in outn1_vac, "vacancy failed: W212 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                      "research/PERPETUAL_N1_W212_PREREG.md"], cwd=ROOT,
                                     encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W212 per-wave prereg ALREADY on origin"
print("vacancy: W212 origin vacancy held (no seat / row / configs / prereg)")

# --- upstream W208 + W209 + W210 + W211 seat discovery on origin (declared faces)
w208_seats = [ln for ln in all_inbox if "w208" in ln.lower() and "seat" in ln.lower()]
w209_seats = [ln for ln in all_inbox if "w209" in ln.lower() and "seat" in ln.lower()]
w210_seats = [ln for ln in all_inbox if "w210" in ln.lower() and "seat" in ln.lower()]
w211_seats = [ln for ln in all_inbox if "w211" in ln.lower() and "seat" in ln.lower()]
missing = [n for n, s in ((208, w208_seats), (209, w209_seats), (210, w210_seats),
                          (211, w211_seats)) if not s]
if missing:
    receipt["legs"]["upstream"] = {"seats_on_origin": False, "missing": missing,
                                   "note": ("AWAITING_UPSTREAM: seat MSG(s) not yet on origin; "
                                            "this probe staged+verified leg0/vacancy faces; "
                                            "re-run on landing -> ADMIT")}
    receipt["verdict"] = "AWAITING_UPSTREAM"
    receipt["bands"] = None
    json.dump(receipt, open(os.path.join(ROOT, "results",
                                         "_w212bmc_20261011_probe_receipt.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"W212 PRE-SEAT PROBE AWAITING_UPSTREAM (exit 3): leg0+vacancy PASS, missing seat(s) {missing}; receipt written")
    sys.exit(3)
assert len(w208_seats) == 1, f"W208 seat files ambiguous ({len(w208_seats)}): {w208_seats}"
assert "bma" in w208_seats[0].lower(), f"W208 seat not a bm-a publication: {w208_seats[0]}"
assert len(w209_seats) == 1, f"W209 seat files ambiguous ({len(w209_seats)}): {w209_seats}"
assert "bmc" in w209_seats[0].lower(), f"W209 seat not a bm-c publication: {w209_seats[0]}"
assert len(w210_seats) == 1, f"W210 seat files ambiguous ({len(w210_seats)}): {w210_seats}"
assert "bmb" in w210_seats[0].lower(), f"W210 seat not a bm-b publication: {w210_seats[0]}"
assert len(w211_seats) == 1, f"W211 seat files ambiguous ({len(w211_seats)}): {w211_seats}"
assert "bmc" in w211_seats[0].lower(), f"W211 seat not a bm-c publication: {w211_seats[0]}"
w208_seat_text = subprocess.check_output(
    ["git", "show", f"origin/main:{w208_seats[0]}"],
    cwd=ROOT, encoding="utf-8", errors="replace")
w209_seat_text = subprocess.check_output(
    ["git", "show", f"origin/main:{w209_seats[0]}"],
    cwd=ROOT, encoding="utf-8", errors="replace")
w210_seat_text = subprocess.check_output(
    ["git", "show", f"origin/main:{w210_seats[0]}"],
    cwd=ROOT, encoding="utf-8", errors="replace")
w211_seat_text = subprocess.check_output(
    ["git", "show", f"origin/main:{w211_seats[0]}"],
    cwd=ROOT, encoding="utf-8", errors="replace")


def _n(s):
    return int(s.replace("_", ""))


def _bands(text, floor):
    ca = [(_n(m.group(1)), _n(m.group(2)))
          for m in re.finditer(r"\*\*A (\d[\d_]*)\.\.(\d[\d_]*)\*\*", text)]
    cb = [(_n(m.group(1)), _n(m.group(2)))
          for m in re.finditer(r"\*\*B (\d[\d_]*)\.\.(\d[\d_]*)\*\*", text)]
    ca = [t for t in ca if t[0] > floor]
    cb = [t for t in cb if t[0] > floor]
    assert ca and cb, f"declared band extraction empty (floor={floor})"
    return ca[0], cb[0]


W208_DECL_A, W208_DECL_B = _bands(w208_seat_text, W207_B[1])
W209_DECL_A, W209_DECL_B = _bands(w209_seat_text, W208_DECL_B[1])
W210_DECL_A, W210_DECL_B = _bands(w210_seat_text, W209_DECL_B[1])
W211_DECL_A, W211_DECL_B = _bands(w211_seat_text, W210_DECL_B[1])
for nm, a, b in (("W208-declared", W208_DECL_A, W208_DECL_B),
                 ("W209-declared", W209_DECL_A, W209_DECL_B),
                 ("W210-declared", W210_DECL_A, W210_DECL_B),
                 ("W211-declared", W211_DECL_A, W211_DECL_B)):
    assert a[1] == a[0] + WIDTH_A - 1 and b[1] == b[0] + WIDTH_B - 1, \
        f"{nm} span law violated: A {a} B {b}"
    assert b[0] == a[1] + 1, \
        f"{nm} own-A reservation law violated: B {b} != A tail+1 {a[1] + 1}"
assert W208_DECL_A[0] == W207_B[1] + 1, \
    f"W208 A base chain relation violated: {W208_DECL_A} != W207 registered B tail+1 {W207_B[1] + 1}"
assert W209_DECL_A[0] == W208_DECL_B[1] + 1, \
    f"W209 A base chain relation violated: {W209_DECL_A} != W208 B tail+1 {W208_DECL_B[1] + 1}"
assert W210_DECL_A[0] == W209_DECL_B[1] + 1, \
    f"W210 A base chain relation violated: {W210_DECL_A} != W209 B tail+1 {W209_DECL_B[1] + 1}"
assert W211_DECL_A[0] == W210_DECL_B[1] + 1, \
    f"W211 A base chain relation violated: {W211_DECL_A} != W210 B tail+1 {W210_DECL_B[1] + 1}"
assert W208_DECL_A[0] > W207_B[1], \
    f"upstream chain forward-monotone violated: W208 A {W208_DECL_A} not beyond W207 registered B tail {W207_B[1]}"
for nm, band in (("W208-declared-A", W208_DECL_A), ("W208-declared-B", W208_DECL_B),
                 ("W209-declared-A", W209_DECL_A), ("W209-declared-B", W209_DECL_B),
                 ("W210-declared-A", W210_DECL_A), ("W210-declared-B", W210_DECL_B),
                 ("W211-declared-A", W211_DECL_A), ("W211-declared-B", W211_DECL_B)):
    for wnum, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            assert not overlaps(tuple(cfg[key]), band), \
                f"{nm} overlaps registered W{wnum}.{key}: upstream seat dirty"
assert '208: {"a": (' not in out_pf, \
    "W208 five-face row ALREADY on origin -- injection premise broken, re-derive live"
assert '209: {"a": (' not in out_pf, \
    "W209 five-face row ALREADY on origin -- injection premise broken, re-derive live"
assert '210: {"a": (' not in out_pf, \
    "W210 five-face row ALREADY on origin -- injection premise broken, re-derive live"
assert '211: {"a": (' not in out_pf, \
    "W211 five-face row ALREADY on origin -- injection premise broken, re-derive live"
assert '"PERPETUAL-N1-W208"' not in outn1_vac, \
    "W208 WAVE_CONFIGS ALREADY on origin -- re-derive live"
assert '"PERPETUAL-N1-W209"' not in outn1_vac, \
    "W209 WAVE_CONFIGS ALREADY on origin -- re-derive live"
assert '"PERPETUAL-N1-W210"' not in outn1_vac, \
    "W210 WAVE_CONFIGS ALREADY on origin -- re-derive live"
assert '"PERPETUAL-N1-W211"' not in outn1_vac, \
    "W211 WAVE_CONFIGS ALREADY on origin -- re-derive live"
print(f"upstream: W208 seat {w208_seats[0]} DECL A {W208_DECL_A[0]}..{W208_DECL_A[1]} / B {W208_DECL_B[0]}..{W208_DECL_B[1]}; W209 seat {w209_seats[0]} DECL A {W209_DECL_A[0]}..{W209_DECL_A[1]} / B {W209_DECL_B[0]}..{W209_DECL_B[1]}; W210 seat {w210_seats[0]} DECL A {W210_DECL_A[0]}....{W210_DECL_A[1]} / B {W210_DECL_B[0]}..{W210_DECL_B[1]}; W211 seat {w211_seats[0]} DECL A {W211_DECL_A[0]}..{W211_DECL_A[1]} / B {W211_DECL_B[0]}..{W211_DECL_B[1]} -- origin-text-verified, injected (W207 = registered face)")

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
bands += [W208_DECL_A, W208_DECL_B, W209_DECL_A, W209_DECL_B,
          W210_DECL_A, W210_DECL_B, W211_DECL_A, W211_DECL_B]   # post-W211-declaration universe (declared-injection precedent)
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the declared W211 tails --------------------
ARITH_A = (W211_DECL_A[1] + 1, W211_DECL_A[1] + WIDTH_A)
ARITH_B = (W211_DECL_B[1] + 1, W211_DECL_B[1] + WIDTH_B)


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
assert fc_a[0] == W211_DECL_B[1] + 1, "leg1 staircase A base != prior-wave B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase A-hops-prior-B SEVENTY-SECOND "
                              "instance expected per W211 bm-c seat leg4 projection line)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation from declared W211 A tail REFUSED at start by "
                    "declared W211 B band (staircase A-hops-prior-B SEVENTY-SECOND instance, E36 "
                    "card, per the W211 seat leg4 anticipation); honest forward walk, non-rotational r587"),
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W212-{tag}")
    for nm, db in (("W208-declared-A", W208_DECL_A), ("W208-declared-B", W208_DECL_B),
                   ("W209-declared-A", W209_DECL_A), ("W209-declared-B", W209_DECL_B),
                   ("W210-declared-A", W210_DECL_A), ("W210-declared-B", W210_DECL_B),
                   ("W211-declared-A", W211_DECL_A), ("W211-declared-B", W211_DECL_B)):
        if overlaps(db, band):
            conflicts.append(f"{nm} x W212-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W212-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W212-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W212-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W212-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W212-{tag}")
assert not conflicts, f"leg2 failed: W212 conflicts {conflicts}"

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

# --- leg 3: origin vacancy (recorded; W212 seat must NOT exist yet) -------------
receipt["legs"]["leg3"] = {"origin_vacancy": True,
                           "w208_seat_path": w208_seats[0],
                           "w209_seat_path": w209_seats[0],
                           "w210_seat_path": w210_seats[0],
                           "w211_seat_path": w211_seats[0]}
print("leg3: origin vacancy held (no W212 seat / row / configs / prereg)")

# --- leg 4: W213+ projection (probe tail, next freezer re-derives) -------------
(fc213_a, h212a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc213_b, h212b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside213 = overlaps(fc213_b, fc213_a)
receipt["legs"]["leg4"] = {"W213p_A": f"{fc213_a[0]}..{fc213_a[1]}", "hops_A": h212a,
                           "W213p_B": f"{fc213_b[0]}..{fc213_b[1]}", "hops_B": h212b,
                           "W213p_B_lands_inside_W213p_A": inside213,
                           "note": ("W213+ naive projection on pre-W212 universe; "
                                    "the registered W212 B band will refuse the naive W213 A window "
                                    "once W212 is registered (A-hops-prior-B SEVENTY-THIRD instance "
                                    "anticipated); W213 freezer MUST re-derive on the post-W212 universe "
                                    "AND reserve own-wave A when deriving B (W141 precedent, leg2 law, "
                                    "E36 staircase card) -- never transcribe r587)")}
print(f"leg4: W213+ projection A {fc213_a[0]}..{fc213_a[1]} hops={h212a} / B {fc213_b[0]}..{fc213_b[1]} hops={h212b} (B inside A: {inside213})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_w212bmc_20261011_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W212 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
