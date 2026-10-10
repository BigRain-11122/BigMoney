# -*- coding: utf-8 -*-
"""W209 pre-seat probe (bm-c loop window r847, 2026-10-11 03:0x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x '机队CPU算力全部用于回测，
排满！' + never-dry supply line per r846 next-pointer item (1) CORRECTED r847:
W208 was claimed by bm-a (MSG-2026-10-11-0129 on origin, discovered by the W208
staging probe vacancy assert fail-loud) -> bm-c next own-wave seat = W209;
+ O-20261011-0012 sec.ii queue-deepen seat-chain mandate + O-20261010-2350-bm-c
RE-ISSUE sec.2 seat-first law (席位不排冻结窗·注册宇宙先占先公示·禁等上一波
烧完才占下一席) + O-20260924-1730 claim-ignite same-round law).
-- read-only band derivation before the seat MSG publication (r565 early-visibility
law). Machine-derived from the LIVE post-W207-REGISTERED universe (W207 five-face
landed on origin this window: bm-b r856 freeze, bands A 470_204..472_203 /
B 472_204..472_403 registered engine_owner=bm-b) + the DECLARED W208 bands
(bm-a seat MSG-2026-10-11-0129, five-face pending bm-a side) (r587: never
transcribed).

TWO-STATE probe: W208 seat MSG absent on origin -> leg0 + W209 vacancy only,
verdict AWAITING_UPSTREAM, exit 3; present -> full five legs, verdict ADMIT,
exit 0.

W209 candidate = first FREE number after the REGISTERED W207 (bm-b) + the
DECLARED W208 (bm-a) faces (W208 declared bands discovered dynamically on
origin -- filename match w208+seat, bolded **A x..y** / **B x..y** regex
extraction, forward-of-W207 filter, span-law and chain-relation asserts,
injected into this probe's universe with origin-text verification, honest note
-- exact mirror of the W205/r956 + W206 + W208/r963 declared-injection
precedents; W207 needs no injection, it is REGISTERED in the live universe).
Derivation faces (STAIRCASE GEOMETRY SIXTY-NINTH instance expected, W141 leg2
law + E36 card; W207's walk = 67th [registered], W208's walk = 68th [declared];
the W208 bm-a seat leg4 projection anticipates W209+ -- this probe IS that
re-derive on the post-W208-declaration universe):
  A  arithmetic continuation from the declared W208 A tail -- expected REFUSED
     at its own start by the declared W208 B band (staircase A-hops-prior-B
     69th); honest forward walk -> first-clean; A base == prior-wave B tail+1
     machine-checkable relation.
  B  arithmetic continuation from the declared W208 B tail -- naive lands
     INSIDE the W209 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W206 finalize LANDED (ledger head 870,371 = prev 868,171 + 2,200;
merged pool K=451,120 machine-read in leg0) -- W207 burned in flight bm-b side
(r856 ignition 3/12), W208 freeze pending bm-a side; W209 freeze-time anchor =
W206 finalize actuals per r590 line; freeze-time guard: if the W207-finalize /
W208 rows land on origin before the W209 freeze, the freezer MUST re-pull and
re-verify the universe face (fail-safe leg0 assertion enforces at probe time;
mirror of the W208 bm-a seat guard note).
Bloodline: _w206bmc_20261010_probe.py derive machinery verbatim, W209 facts
live-registry-driven; W208 declared-band injection = the
post-W208-declaration universe."""
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
receipt = {"probe": "W209 pre-seat probe (bm-c loop r847, 2026-10-11 03:0x, CEO fill-order standing re-issued + seat-first law + never-dry supply line; W208 taken by bm-a 01:29 -> W209 = bm-c next own seat; W207 registered this window by bm-b r856)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape (post-W207 universe: tail=W207 registered) -----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 208))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W206_A = tuple(N1_BANDS[206]["a"])
W206_B = tuple(N1_BANDS[206]["b_exit"])
assert W206_A == (468_004, 470_003) and W206_B == (470_004, 470_203) and \
    N1_BANDS[206].get("engine_owner") == "bm-c", "leg0 failed: W206 row drift"
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

w206_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w206_results.json"), encoding="utf-8"))
led = (w206_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 870_371 and led.get("prev_total") == 868_171, \
    f"leg0 failed: W206 ledger machine-read drift {led}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W207-registered",
                           "owner_rows": len(owner_rows), "bmc_rows": len(bmc_rows),
                           "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
                           "ordinal": 199, "bmc_ordinal": 39,
                           "w206_ledger_head": led.get("total"),
                           "anchor": ("W206 finalize LANDED (ledger 870,371 = prev 868,171 + 2,200, K=451,120); "
                                      "W207 burn in flight bm-b side (r856 ignition), W208 freeze pending bm-a side; "
                                      "W209 freeze-time anchor = W206 finalize actuals per r590 line")}
print(f"leg0: {len(N1_BANDS)} rows tail=W207 registered, owner={len(owner_rows)} -> 199th wave, bm-c 39th owned, anchor W206 ledger head {led.get('total')}")

# --- W209 own vacancy on origin (both states) ----------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w209_seats = [ln for ln in all_inbox if "w209" in ln.lower() and "seat" in ln.lower()]
assert w209_seats == [], f"vacancy failed: W209 seats already exist: {w209_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '209: {"a": (' not in out_pf, "vacancy failed: W209 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W209"' not in outn1_vac, "vacancy failed: W209 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                      "research/PERPETUAL_N1_W209_PREREG.md"], cwd=ROOT,
                                     encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W209 per-wave prereg ALREADY on origin"
print("vacancy: W209 origin vacancy held (no seat / row / configs / prereg)")

# --- upstream W208 seat discovery on origin (bm-a, five-face pending) -----------
w208_seats = [ln for ln in all_inbox if "w208" in ln.lower() and "seat" in ln.lower()]
if not w208_seats:
    receipt["legs"]["upstream"] = {"seats_on_origin": False, "missing": [208],
                                   "note": ("AWAITING_UPSTREAM: W208 bm-a seat MSG not yet on origin; "
                                            "this probe staged+verified leg0/vacancy faces; "
                                            "re-run on landing -> ADMIT")}
    receipt["verdict"] = "AWAITING_UPSTREAM"
    receipt["bands"] = None
    json.dump(receipt, open(os.path.join(ROOT, "results",
                                         "_w209bmc_20261011_probe_receipt.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
    print("W209 PRE-SEAT PROBE AWAITING_UPSTREAM (exit 3): leg0+vacancy PASS, W208 seat not yet on origin; receipt written")
    sys.exit(3)
assert len(w208_seats) == 1, f"W208 seat files ambiguous ({len(w208_seats)}): {w208_seats}"
assert "bma" in w208_seats[0].lower(), f"W208 seat not a bm-a publication: {w208_seats[0]}"
w208_seat_text = subprocess.check_output(
    ["git", "show", f"origin/main:{w208_seats[0]}"],
    cwd=ROOT, encoding="utf-8", errors="replace")


def _n(s):
    return int(s.replace("_", ""))


ca = [(_n(m.group(1)), _n(m.group(2)))
      for m in re.finditer(r"\*\*A (\d[\d_]*)\.\.(\d[\d_]*)\*\*", w208_seat_text)]
cb = [(_n(m.group(1)), _n(m.group(2)))
      for m in re.finditer(r"\*\*B (\d[\d_]*)\.\.(\d[\d_]*)\*\*", w208_seat_text)]
ca = [t for t in ca if t[0] > W207_B[1]]
cb = [t for t in cb if t[0] > W207_B[1]]
assert ca and cb, f"W208 declared band extraction empty (floor={W207_B[1]})"
W208_DECL_A, W208_DECL_B = ca[0], cb[0]
assert W208_DECL_A[1] == W208_DECL_A[0] + WIDTH_A - 1 and \
    W208_DECL_B[1] == W208_DECL_B[0] + WIDTH_B - 1, \
    f"W208 declared span law violated: A {W208_DECL_A} B {W208_DECL_B}"
assert W208_DECL_B[0] == W208_DECL_A[1] + 1, \
    f"W208 seat own-A reservation law violated: B {W208_DECL_B} != A tail+1 {W208_DECL_A[1] + 1}"
assert W208_DECL_A[0] > W207_B[1], \
    f"upstream chain forward-monotone violated: W208 A {W208_DECL_A} not beyond W207 registered B tail {W207_B[1]}"
for nm, band in (("W208-declared-A", W208_DECL_A), ("W208-declared-B", W208_DECL_B)):
    for wnum, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            assert not overlaps(tuple(cfg[key]), band), \
                f"{nm} overlaps registered W{wnum}.{key}: upstream seat dirty"
assert '208: {"a": (' not in out_pf, \
    "W208 five-face row ALREADY on origin -- injection premise broken, re-derive live"
assert '"PERPETUAL-N1-W208"' not in outn1_vac, \
    "W208 WAVE_CONFIGS ALREADY on origin -- re-derive live"
print(f"upstream: W208 seat {w208_seats[0]} origin-text-verified; DECL A {W208_DECL_A[0]}..{W208_DECL_A[1]} / B {W208_DECL_B[0]}..{W208_DECL_B[1]} injected (W207 = registered face)")

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
bands += [W208_DECL_A, W208_DECL_B]   # post-W208-declaration universe (declared-injection precedent)
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the declared W208 tails ---------------------
ARITH_A = (W208_DECL_A[1] + 1, W208_DECL_A[1] + WIDTH_A)
ARITH_B = (W208_DECL_B[1] + 1, W208_DECL_B[1] + WIDTH_B)


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
assert fc_a[0] == W208_DECL_B[1] + 1, "leg1 staircase A base != prior-wave B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase A-hops-prior-B SIXTY-NINTH "
                              "instance expected per W208 bm-a seat leg4 projection line)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation from declared W208 A tail REFUSED at start by "
                    "declared W208 B band (staircase A-hops-prior-B SIXTY-NINTH instance, E36 "
                    "card); honest forward walk, non-rotational r587"),
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W209-{tag}")
    for nm, db in (("W208-declared-A", W208_DECL_A), ("W208-declared-B", W208_DECL_B)):
        if overlaps(db, band):
            conflicts.append(f"{nm} x W209-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W209-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W209-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W209-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W209-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W209-{tag}")
assert not conflicts, f"leg2 failed: W209 conflicts {conflicts}"

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

# --- leg 3: origin vacancy (recorded; W209 seat must NOT exist yet) ------------
receipt["legs"]["leg3"] = {"origin_vacancy": True,
                           "w208_seat_path": w208_seats[0]}
print("leg3: origin vacancy held (no W209 seat / row / configs / prereg)")

# --- leg 4: W210+ projection (probe tail, next freezer re-derives) -------------
(fc210_a, h209a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc210_b, h209b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside210 = overlaps(fc210_b, fc210_a)
receipt["legs"]["leg4"] = {"W210p_A": f"{fc210_a[0]}..{fc210_a[1]}", "hops_A": h209a,
                           "W210p_B": f"{fc210_b[0]}..{fc210_b[1]}", "hops_B": h209b,
                           "W210p_B_lands_inside_W210p_A": inside210,
                           "note": ("W210+ naive projection on pre-W209 universe; "
                                    "the registered W209 B band will refuse the naive W210 A window "
                                    "once W209 is registered (A-hops-prior-B SEVENTIETH instance "
                                    "anticipated); W210 freezer MUST re-derive on the post-W209 universe "
                                    "AND reserve own-wave A when deriving B (W141 precedent, leg2 law, "
                                    "E36 staircase card) -- never transcribe r587)")}
print(f"leg4: W210+ projection A {fc210_a[0]}..{fc210_a[1]} hops={h209a} / B {fc210_b[0]}..{fc210_b[1]} hops={h209b} (B inside A: {inside210})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_w209bmc_20261011_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W209 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
