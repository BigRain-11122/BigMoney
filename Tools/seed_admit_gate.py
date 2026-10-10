#!/usr/bin/env python
# seed_admit_gate.py -- prereg ADMIT-time seed-base collision gate.
# Law: O-20261010-1945 item A (FE-20261010-C-02 remediation 1, structural
# stop to the 7th recurrence). Live-fire root cause: the prereg ADMIT pick
# convention checked only "registry + rg scanned free" (SEED_REGISTRY
# in-registry machine-read) and never the pf.N1_BANDS reserved domain --
# the 94k strip took five same-pocket hits (regime5 94_100 -> f1_bull
# 94_200 -> parking 94_300 -> thermo 94_500 -> lhb 94_700) before W204
# five-face freezes stalled on the chain selftest.
# ADMIT convention upgrade (machine-readable voucher): from THERMO/LHB
# onward, every new prereg null-base pick passes this gate BEFORE freeze;
# the freeze registration note's "registry+rg scanned free" line must also
# attach a "seed_admit_gate rc0" record for the chosen base (and span when
# the family consumes a contiguous strip wider than one int).
# Faces (single-source live imports, NO hardcoded interval copies):
#   N1_BANDS      -- scripts/perpetual_faces.py  (frozen law sec.4 band
#                   ledger: wave -> {a:(lo,hi), b_exit:(lo,hi), engine_owner})
#   SEED_REGISTRY -- scripts/science_gates.py  (prereg seed family bases;
#                   the sole non-int entry is the 'policy' prose key)
# Intervals are inclusive [lo, hi] (live-verified: 58_700 in W99 b_exit
# (58_551, 58_750); 94_100/94_200 in W137 b_exit (94_001, 94_200)).
# Commands:
#   <base> [--span N]   admit-check ints base..base+span-1 (span default 1)
#   --selfcheck         hermetic legs: the six historical collisions must be
#                       captured (each on BOTH faces) + the documented clean
#                       point 95_000 must read FREE per live tables
# Exit codes: 0 = FREE (all checked ints clear both faces);
#             1 = collision (per-int detail lines printed);
#             2 = mechanism fault (bad args / import failure).
# Zero writes; stdout only. ASCII source law (r823).
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

BAND_KEYS = ("a", "b_exit")  # interval keys; engine_owner is a string tag

# The six adjudicated historical collisions (O-20261010-1906 table 3;
# W99 r719 / W137..W138 r874 / W139..W140 r874-mirror r957 7464be852).
# These are assertion facts about documented events, not interval copies.
HISTORICAL_COLLISIONS = [
    # (seed, expected N1 wave, expected SEED_REGISTRY key)
    (58_700, 99, "sina_mf_ic_p1"),
    (94_100, 137, "regime5_validation_p1_null_base"),
    (94_200, 137, "f1_bull_cond_p1_null_base"),
    (94_300, 138, "parking_p1_null_base"),
    (94_500, 139, "thermo_overlay_p1_nulls"),
    (94_700, 140, "lhb_thermo_ic_p1_nulls"),
]

CLEAN_POINT = 95_000  # per O-1945: free per live read at freeze time


def load_faces():
    """Live-import both registries (single-source law). Returns
    (band_intervals, registry_values) where band_intervals is a sorted list
    of (wave, key, lo, hi) and registry_values is a list of (key, value)."""
    try:
        import perpetual_faces as pf
        from science_gates import SEED_REGISTRY
    except Exception as exc:  # mechanism fault face
        print("SEED_ADMIT FAULT import_failure=%r" % (exc,))
        raise SystemExit(2)
    bands = []
    for wave, row in sorted(pf.N1_BANDS.items()):
        for key, val in row.items():
            if key not in BAND_KEYS:
                continue
            lo, hi = val
            bands.append((int(wave), key, int(lo), int(hi)))
    regs = []
    for key, val in SEED_REGISTRY.items():
        if isinstance(val, bool) or not isinstance(val, int):
            continue  # skip the 'policy' prose key and any non-int residue
        regs.append((key, int(val)))
    return bands, regs


def check_int(seed, bands, regs):
    """Return the collision detail dicts for one int (empty = free)."""
    cols = []
    for wave, key, lo, hi in bands:
        if lo <= seed <= hi:
            cols.append({"face": "N1_BAND_COLLISION", "seed": seed,
                         "wave": wave, "key": key, "lo": lo, "hi": hi})
    for key, val in regs:
        if seed == val:
            cols.append({"face": "REGISTRY_COLLISION", "seed": seed,
                         "key": key, "value": val})
    return cols


def check_range(base, span, bands, regs):
    """Check base..base+span-1 inclusive; return all collision details."""
    cols = []
    for seed in range(base, base + span):
        cols.extend(check_int(seed, bands, regs))
    return cols


def print_collisions(cols):
    for c in cols:
        if c["face"] == "N1_BAND_COLLISION":
            print("N1_BAND_COLLISION seed=%d wave=%d key=%s lo=%d hi=%d"
                  % (c["seed"], c["wave"], c["key"], c["lo"], c["hi"]))
        else:
            print("REGISTRY_COLLISION seed=%d key=%s value=%d"
                  % (c["seed"], c["key"], c["value"]))


def run_admit(base, span):
    bands, regs = load_faces()
    cols = check_range(base, span, bands, regs)
    if cols:
        print_collisions(cols)
        print("SEED_ADMIT COLLISION base=%d span=%d collisions=%d"
              % (base, span, len(cols)))
        return 1
    print("SEED_ADMIT FREE base=%d span=%d checked=%d" % (base, span, span))
    return 0


def run_selfcheck():
    """Hermetic read-only legs. rc0 = PASS, rc1 = leg failure, rc2 = fault."""
    bands, regs = load_faces()
    fails = 0
    # Leg 1: the six historical collisions must each be captured on BOTH
    # faces (band hit at the documented wave + registry hit at the
    # documented key) -- i.e. each historic seed must yield rc1 verdict.
    for seed, wave, regkey in HISTORICAL_COLLISIONS:
        cols = check_int(seed, bands, regs)
        band_hits = [c for c in cols
                     if c["face"] == "N1_BAND_COLLISION" and c["wave"] == wave]
        reg_hits = [c for c in cols
                    if c["face"] == "REGISTRY_COLLISION" and c["key"] == regkey]
        if len(band_hits) == 1 and len(reg_hits) == 1:
            print("selftest: historic collision captured seed=%d wave=%d "
                  "key=%s ... PASS" % (seed, wave, regkey))
        else:
            print("selftest: historic collision MISS seed=%d expected "
                  "wave=%d key=%s got=%s ... FAIL" % (seed, wave, regkey, cols))
            fails += 1
    # Leg 2: documented clean point reads FREE per live tables (order text:
    # if the pf band table shows it unoccupied then PASS, live read rules).
    cols = check_int(CLEAN_POINT, bands, regs)
    if cols:
        print("selftest: clean point %d not free ... FAIL %s"
              % (CLEAN_POINT, cols))
        fails += 1
    else:
        print("selftest: clean point %d FREE ... PASS" % CLEAN_POINT)
    # Leg 3: span arithmetic -- a span crossing a wave boundary must report
    # exactly the covered ints. 94_600 is the last int of W139 b_exit
    # (94_401..94_600); 94_601 is the first int of W140 b_exit
    # (94_601..94_800). Neither is a registry value, so only band faces hit.
    probe = check_range(94_600, 2, bands, regs)
    seeds_hit = sorted({c["seed"] for c in probe})
    if seeds_hit == [94_600, 94_601]:
        print("selftest: span boundary reach 94_600..94_601 ... PASS")
    else:
        print("selftest: span boundary reach got %s ... FAIL" % (seeds_hit,))
        fails += 1
    if fails:
        print("SELFTEST FAIL legs_failed=%d" % fails)
        return 1
    print("selftest: all legs PASS (6 historic + clean point + span reach)")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="prereg ADMIT seed-base collision gate "
                    "(N1_BANDS reserved domain + SEED_REGISTRY)")
    ap.add_argument("base", nargs="?", type=int,
                    help="candidate seed family base (int)")
    ap.add_argument("--span", type=int, default=1,
                    help="consumption width: ints base..base+span-1 "
                         "(default 1)")
    ap.add_argument("--selfcheck", action="store_true",
                    help="run hermetic selftest legs")
    args = ap.parse_args()
    if args.selfcheck:
        raise SystemExit(run_selfcheck())
    if args.base is None:
        print("SEED_ADMIT FAULT missing base argument")
        raise SystemExit(2)
    if args.span < 1:
        print("SEED_ADMIT FAULT span must be >= 1 (got %d)" % args.span)
        raise SystemExit(2)
    raise SystemExit(run_admit(args.base, args.span))


if __name__ == "__main__":
    main()
