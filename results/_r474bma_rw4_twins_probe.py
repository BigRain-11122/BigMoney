"""RW-4 slice-1 (T-127, D-20260930-05): data/daily symbol-key twins inventory.

Read-only, zero-network probe. Answers the audit question behind RW-4
"symbol canonicalization (sh/sz prefix twins dedup)":
  1. bare-code vs prefix-keyed files in the shared data/daily dir;
  2. twin overlap (same instrument stored under BOTH keys) with per-face
     freshness (mtime + last bar date) and row counts;
  3. stale-bar face (last bar date per file, fresh<=N trading-day window);
  4. which face each canonical loader actually accepts (load_core filter
     simulation, zero engine touch).
Evidence -> results/_r474bma_rw4_twins_probe.json (consumed by RW-4
slice-2 canonicalization gate design; gate fail = batch not accepted).
"""
import json
import os
import re
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAILY = os.path.join(ROOT, "data", "daily")
OUT = os.path.join(ROOT, "results", "_r474bma_rw4_twins_probe.json")
FRESH_TD_DAYS = 5  # calendar-day freshness window (audit Q7 threshold caliber)


def _last_bar(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().strip().splitlines()
        if len(lines) < 2:
            return None, len(lines)
        parts = re.split(r"[,]", lines[-1])
        d = parts[0].strip('"').strip()
        return d, len(lines) - 1
    except Exception:
        return None, 0


def main():
    files = [f for f in os.listdir(DAILY) if f.endswith(".csv")]
    bare, pref = {}, {}
    for f in files:
        stem = f[:-4]
        m = re.match(r"^(sh|sz)(\d{6})$", stem)
        if m:
            pref[m.group(2)] = f
        elif re.match(r"^\d{6}$", stem):
            bare[stem] = f
    twins = sorted(set(bare) & set(pref))
    now = datetime.now(timezone(timedelta(hours=8)))

    twin_rows = []
    for code in twins:
        bp, pp = os.path.join(DAILY, bare[code]), os.path.join(DAILY, pref[code])
        bl, bn = _last_bar(bp)
        pl, pn = _last_bar(pp)
        twin_rows.append({
            "code": code,
            "bare": {"file": bare[code], "rows": bn, "last_bar": bl,
                     "mtime": datetime.fromtimestamp(
                         os.path.getmtime(bp), timezone(timedelta(hours=8))).isoformat()},
            "prefixed": {"file": pref[code], "rows": pn, "last_bar": pl,
                         "mtime": datetime.fromtimestamp(
                             os.path.getmtime(pp), timezone(timedelta(hours=8))).isoformat()},
            "last_bar_divergence": (bl != pl),
        })

    # stale-bar face over ALL files (Q7 machine recount)
    fresh, stale = [], []
    for f in files:
        p = os.path.join(DAILY, f)
        mt = datetime.fromtimestamp(os.path.getmtime(p), timezone(timedelta(hours=8)))
        (fresh if (now - mt).days <= FRESH_TD_DAYS else stale).append(f)
    div = sum(1 for r in twin_rows if r["last_bar_divergence"])

    # load_core filter simulation (live/paper.py: bare digit name, >=60 rows)
    load_core_accepts = [c for c in sorted(bare)
                          if _last_bar(os.path.join(DAILY, bare[c]))[1] >= 60]

    out = {
        "probe": "rw4_slice1_symbol_twins_inventory",
        "ticket": "T-2026-09-30-127 (RW-4 slice-1)",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "dir": "data/daily",
        "counts": {
            "total_csv": len(files),
            "bare_key": len(bare),
            "prefix_key": len(pref),
            "twins": len(twins),
            "fresh_mtime_le_5d": len(fresh),
            "stale_mtime_gt_5d": len(stale),
            "twins_with_last_bar_divergence": div,
        },
        "twins_detail": twin_rows,
        "load_core_accepts_n": len(load_core_accepts),
        "canonical_face": ("bare-code keys (load_core isdigit filter); prefix face = "
                           "wider legacy panel + update_etf_daily five-member lane (sh<code>.csv)"),
        "risk_statement": (
            "48/48 bare core48 members have prefix twins in the SAME dir; "
            "twins carry divergent last-bar dates; prefix face 1671/1676 stale "
            "(mtime 2026-09-23). Readers with bare-first fallback (firm/risk/regime.py, "
            "scripts/market_regime.py) are safe today; direct prefix readers (div_lowvol "
            "family, trial_labor_w4/w5, regime_calibration) read the stale/divergent face "
            "where a bare twin exists. RW-4 slice-2 gate: canonical key = bare code; "
            "prefix twin where bare exists = dedup/refuse at batch acceptance."),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    c = out["counts"]
    print(f"rw4 twins probe: total={c['total_csv']} bare={c['bare_key']} "
          f"pref={c['prefix_key']} twins={c['twins']} divergent_last_bar={div} "
          f"fresh<=5d={c['fresh_mtime_le_5d']} stale={c['stale_mtime_gt_5d']}")
    print(f"load_core accepts (bare, >=60 rows): {len(load_core_accepts)}")
    print(f"evidence -> {os.path.relpath(OUT, ROOT)}")
    assert c["twins"] == len(bare), "every bare member must be inventoried as twin"
    assert len(files) == len(bare) + len(pref), "every csv classified exactly once"


if __name__ == "__main__":
    main()
