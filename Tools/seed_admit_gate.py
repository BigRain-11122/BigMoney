"""O-20261010-1945-bm-a slice A: prereg ADMIT gate with N1_BANDS reserved-band checkpoint.

Structural fix for FE-20261010-C-02 item-1 (stop the 7th recurrence of null-base
seed collisions with engine N1 reserved bands). Live-imports
scripts/perpetual_faces.py N1_BANDS and scripts/science_gates.py SEED_REGISTRY
-- zero hardcoded interval copies, current read is authoritative.

Usage:
  python Tools/seed_admit_gate.py <base> [--span N]
  python Tools/seed_admit_gate.py --selfcheck

Exit codes:
  0 = FREE (prints the `seed_admit_gate rc0` machine record for prereg comments)
  1 = collision (prints N1_BAND_COLLISION / REGISTRY_COLLISION details)
  2 = usage or mechanism error

ADMIT convention (O-20261010-1945-bm-a): from THERMO/LHB onward every new
null-base selection must pass this gate before prereg freeze; the freeze
registration comment's "registry+rg scanned free" line must carry the
`seed_admit_gate rc0` record printed here.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_faces():
    # science_gates.py imports `from knowledge import cost_spec` at module level,
    # so both repo root (knowledge pkg) and scripts/ must be importable from any CWD.
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT))
    import science_gates as sg  # noqa: E402
    import perpetual_faces as pf  # noqa: E402

    n1_bands = getattr(pf, "N1_BANDS", None)
    seed_registry = getattr(sg, "SEED_REGISTRY", None)
    if not isinstance(n1_bands, dict) or not isinstance(seed_registry, dict):
        print("seed_admit_gate rc2 mechanism-error: N1_BANDS/SEED_REGISTRY missing or wrong type")
        raise SystemExit(2)
    return n1_bands, seed_registry


def _is_interval(iv) -> bool:
    return isinstance(iv, (tuple, list)) and len(iv) == 2 and all(isinstance(x, int) for x in iv)


def iter_band_intervals(n1_bands):
    for wave, bands in n1_bands.items():
        if not isinstance(bands, dict):
            continue
        for key, iv in bands.items():
            if _is_interval(iv):
                yield wave, key, iv[0], iv[1]


def registry_values(seed_registry):
    vals = {}
    for key, val in seed_registry.items():
        if isinstance(val, int):
            vals.setdefault(val, []).append(key)
    return vals


def check(base: int, span: int, n1_bands, seed_registry) -> list[dict]:
    collisions = []
    regvals = registry_values(seed_registry)
    for v in range(base, base + span):
        for wave, key, lo, hi in iter_band_intervals(n1_bands):
            if lo <= v <= hi:
                collisions.append({
                    "kind": "N1_BAND_COLLISION", "value": v,
                    "wave": wave, "key": key, "lo": lo, "hi": hi,
                })
        for regkey in regvals.get(v, []):
            collisions.append({
                "kind": "REGISTRY_COLLISION", "value": v, "key": regkey,
            })
    return collisions


def _fmt(c: dict) -> str:
    if c["kind"] == "N1_BAND_COLLISION":
        return (f"N1_BAND_COLLISION value={c['value']} wave={c['wave']} "
                f"key={c['key']} lo={c['lo']} hi={c['hi']}")
    return f"REGISTRY_COLLISION value={c['value']} key={c['key']}"


# Historical recurrences (6): base, expected colliding wave -- current-read asserted.
HISTORICAL = [
    (58700, 99, "sina_mf_ic_p1"),
    (94100, 137, "regime5"),
    (94200, 137, "f1_bull"),
    (94300, 138, "parking"),
    (94500, 139, "thermo"),
    (94700, 140, "lhb"),
]
CLEAN_POINT = 95000


def selfcheck() -> int:
    n1_bands, seed_registry = _load_faces()
    failures = []
    for base, wave, label in HISTORICAL:
        col = check(base, 1, n1_bands, seed_registry)
        band_waves = {c["wave"] for c in col if c["kind"] == "N1_BAND_COLLISION"}
        if not col:
            failures.append(f"{base} ({label}): expected collision, gate returned FREE")
        elif wave not in band_waves:
            failures.append(f"{base} ({label}): expected band wave {wave}, got {sorted(band_waves)}")
        else:
            print(f"selfcheck PASS {base} ({label}) collision captured, band wave={wave}")
    col_clean = check(CLEAN_POINT, 1, n1_bands, seed_registry)
    if col_clean:
        failures.append(f"{CLEAN_POINT}: expected clean point FREE, got {len(col_clean)} collision(s): "
                        + "; ".join(_fmt(c) for c in col_clean[:3]))
    else:
        print(f"selfcheck PASS {CLEAN_POINT} clean point FREE (zero false positive)")
    if failures:
        for f in failures:
            print("selfcheck FAIL " + f)
        print("seed_admit_gate selfcheck rc1")
        return 1
    print("seed_admit_gate selfcheck rc0 (6/6 historical captured + clean point free)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="prereg ADMIT gate: N1_BANDS reserved-band checkpoint")
    ap.add_argument("base", nargs="?", type=int, help="candidate seed base")
    ap.add_argument("--span", type=int, default=1, help="consumption width (default 1)")
    ap.add_argument("--selfcheck", action="store_true", help="offline self-test")
    args = ap.parse_args(argv)

    if args.selfcheck:
        return selfcheck()
    if args.base is None:
        ap.print_usage()
        print("seed_admit_gate rc2 usage: base required (or --selfcheck)")
        return 2
    if args.span < 1:
        print("seed_admit_gate rc2 usage: --span must be >= 1")
        return 2

    n1_bands, seed_registry = _load_faces()
    col = check(args.base, args.span, n1_bands, seed_registry)
    if col:
        for c in col:
            print(_fmt(c))
        print(f"seed_admit_gate rc1 base={args.base} span={args.span} collisions={len(col)} verdict=BLOCKED")
        return 1
    print(f"seed_admit_gate rc0 base={args.base} span={args.span} "
          f"checked={args.span} verdict=FREE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
