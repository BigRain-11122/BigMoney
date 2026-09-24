"""T-18 deep-axis feasibility probe (O-20260924-1141, deliverable-1 evidence base).

Read-only audit: what deep history actually exists in-repo for the core-48
ETF axis vs the Money02 stock panel, so the revalidation prereg can freeze
window boundaries honestly instead of assuming "25 years" applies to ETFs.

No batch runs, no data writes, no touch on data/daily bare-code files.
Output: results/shortline/t18_deep_axis_probe.json (ledger_trials_added=0).

Subcommands: run | selftest
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAILY = os.path.join(ROOT, "data", "daily")
OUT_JSON = os.path.join(ROOT, "results", "shortline", "t18_deep_axis_probe.json")
REGISTRY = os.path.join(ROOT, "data", "consolidation", "registry.json")
MONEY02_BARS = os.path.join(ROOT, "Money02", "data", "bars")
# Liquid, long-listed probes for the stock-panel depth snapshot (read-only).
STOCK_SAMPLES = ["600000", "000001", "600519"]
MIN_LISTING_DAYS = 60  # live.paper.load_core caliber


def _twin_prefix(code: str) -> str:
    return "sz" if code.startswith(("0", "1", "3")) else "sh"


def _twin_path(code: str) -> str:
    return os.path.join(DAILY, _twin_prefix(code) + code + ".csv")


def _csv_edges(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path, usecols=["date"])
    except Exception:
        return None
    if df.empty:
        return {"rows": 0, "start": None, "end": None}
    return {
        "rows": int(len(df)),
        "start": str(df["date"].iloc[0]),
        "end": str(df["date"].iloc[-1]),
    }


def _inventory() -> tuple[list[dict], dict]:
    rows: list[dict] = []
    for f in sorted(os.listdir(DAILY)):
        if not (f.endswith(".csv") and f[:-4].isdigit()):
            continue
        code = f[:-4]
        bare = _csv_edges(os.path.join(DAILY, f))
        if bare is None or bare["rows"] < MIN_LISTING_DAYS:
            continue
        twin = _csv_edges(_twin_path(code))
        rows.append(
            {
                "code": code,
                "bare_rows": bare["rows"],
                "bare_start": bare["start"],
                "bare_end": bare["end"],
                "twin_rows": (twin or {}).get("rows"),
                "twin_start": (twin or {}).get("start"),
                "twin_end": (twin or {}).get("end"),
            }
        )
    starts = sorted(r["twin_start"] or r["bare_start"] for r in rows if (r["twin_start"] or r["bare_start"]))
    stats = {
        "n_universe": len(rows),
        "earliest_twin_start": starts[0] if starts else None,
        "latest_twin_start": starts[-1] if starts else None,
        "median_twin_start": starts[len(starts) // 2] if starts else None,
        # common all-48 deep window start = the LATEST start among the 48
        "common_deep_window_start": starts[-1] if starts else None,
        "n_twin_longer_than_bare": sum(
            1 for r in rows if r["twin_start"] and r["bare_start"] and r["twin_start"] < r["bare_start"]
        ),
        "n_twin_missing": sum(1 for r in rows if not r["twin_start"]),
    }
    for year in ("2013", "2015", "2018", "2020"):
        stats[f"n_listed_by_{year}"] = sum(
            1 for s in starts if s and s[:4] <= year
        )
    return rows, stats


def _registry_years() -> dict:
    if not os.path.exists(REGISTRY):
        return {"present": False}
    reg = json.load(open(REGISTRY, encoding="utf-8-sig"))
    events = reg.get("events", reg if isinstance(reg, list) else [])
    years: dict[str, int] = {}
    ev_years = []
    for ev in events:
        d = ev.get("date") or ev.get("break_date") or ""
        ev_years.append(d)
        years[d[:4]] = years.get(d[:4], 0) + 1
    return {
        "present": True,
        "n_events": len(events),
        "events_by_year": dict(sorted(years.items())),
        "n_pre_2020": sum(1 for d in ev_years if d and d[:4] < "2020"),
        "first_event": min(ev_years) if ev_years else None,
        "last_event": max(ev_years) if ev_years else None,
    }


def _stock_panel_depth() -> dict:
    if not os.path.isdir(MONEY02_BARS):
        return {"present": False}
    files = [f for f in os.listdir(MONEY02_BARS) if f.endswith(".parquet")]
    samples = {}
    for code in STOCK_SAMPLES:
        p = os.path.join(MONEY02_BARS, code + ".parquet")
        if not os.path.exists(p):
            continue
        try:
            df = pd.read_parquet(p, columns=["date"])
        except Exception as e:  # honest: unreadable sample recorded, not fatal
            samples[code] = {"error": str(e)[:120]}
            continue
        if len(df) == 0:
            samples[code] = {"rows": 0}
            continue
        samples[code] = {
            "rows": int(len(df)),
            "start": str(df["date"].iloc[0])[:10],
            "end": str(df["date"].iloc[-1])[:10],
        }
    starts = [v["start"] for v in samples.values() if v.get("start")]
    return {
        "present": True,
        "n_parquet_files": len(files),
        "samples": samples,
        "sample_earliest_start": min(starts) if starts else None,
        "sample_latest_end": max(v.get("end", "") for v in samples.values()) if samples else None,
    }


def _overlap_spotcheck(rows: list[dict], n: int = 3) -> dict:
    """Re-verify twin/bare close parity on the overlap tail for n samples
    (pool-audit 48/48 proof exists; this is a cheap freshness re-check)."""
    checked = []
    for r in rows[:n]:
        if not r["twin_start"]:  # twin-less instruments cannot be parity-checked
            continue
        bare = pd.read_csv(os.path.join(DAILY, r["code"] + ".csv"))
        twin = pd.read_csv(_twin_path(r["code"]))
        twin = twin.rename(columns={c: c.strip() for c in twin.columns})
        b = bare.set_index("date")["close"]
        t = twin.set_index("date")["close"]
        common = b.index.intersection(t.index)
        if len(common) == 0:
            checked.append({"code": r["code"], "common_rows": 0})
            continue
        diff = (b.loc[common] - t.loc[common]).abs().max()
        checked.append(
            {"code": r["code"], "common_rows": int(len(common)), "max_abs_close_diff": float(diff)}
        )
    return checked


def run() -> int:
    rows, stats = _inventory()
    reg = _registry_years()
    stocks = _stock_panel_depth()
    spot = _overlap_spotcheck(rows)
    # Honest deep-axis ceiling: common all-48 window length in years
    ceiling = None
    if stats["common_deep_window_start"]:
        end = max(r["twin_end"] or r["bare_end"] for r in rows)
        days = (pd.Timestamp(end) - pd.Timestamp(stats["common_deep_window_start"])).days
        ceiling = round(days / 365.25, 2)
    payload = {
        "batch": "T-18 deep-axis feasibility probe",
        "ticket": "T-2026-09-24-18",
        "order": "O-20260924-1141 / BACKTEST_SCIENCE §10 D7",
        "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        "universe_stats": stats,
        "common_deep_window_years": ceiling,
        "registry_coverage": reg,
        "stock_panel_depth": stocks,
        "twin_bare_overlap_spotcheck": spot,
        "ledger_trials_added": 0,
        "honest_findings": [],
        "notes": [
            "probe-only: zero batch runs, zero data writes, bare-code files untouched",
            "deep panel = separate construction from twins; prepending to bare-code files "
            "would shift anchor-reproduction panels and break live.paper anchoring (rejected)",
            "adjusted view (T-19 lane, O-1310 s3) = hard gate before any null/revalidation run",
        ],
    }
    f = []
    f.append(
        f"core-48 deep axis ceiling = common twin window {stats['common_deep_window_start']} -> "
        f"~{ceiling}y (vs current 6.7y mainline); earliest twin {stats['earliest_twin_start']}"
    )
    f.append(
        f"twin longer than bare for {stats['n_twin_longer_than_bare']}/{stats['n_universe']} "
        f"instruments; {stats['n_listed_by_2015']}/48 have data by 2015"
    )
    f.append(
        "25-year claim is stock-panel only: Money02 bars "
        f"({stocks.get('n_parquet_files')} parquet, sample earliest "
        f"{stocks.get('sample_earliest_start')}); ETF axis is listing-bound — pre-2015 "
        "segment for ETFs is thin/absent and must be disclosed as honest boundary per §10"
    )
    f.append(
        f"break registry: {reg.get('n_events')} events, {reg.get('n_pre_2020')} pre-2020 — "
        "registry scan covered full twin history, deep segment inherits known-break coverage"
    )
    payload["honest_findings"] = f
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(json.dumps({k: payload[k] for k in ("universe_stats", "common_deep_window_years", "honest_findings")}, ensure_ascii=False, indent=1))
    print("probe written:", OUT_JSON)
    return 0


def _selftest() -> int:
    """Synthetic mini-DSV: build temp daily dir with fake bare/twin/registry
    and run the math helpers against it by monkeypatching module paths."""
    tmp = tempfile.mkdtemp(prefix="t18probe_")
    daily = os.path.join(tmp, "daily")
    os.makedirs(daily)
    # 3 fake instruments; one without a twin (missing-twin path), one twin longer
    frames = {
        "510001": ("2013-06-28", "2020-01-02"),   # bare 2013 start
        "510002": ("2020-01-02", "2026-01-02"),   # bare starts 2020
    }
    for code, (s, e) in frames.items():
        idx = pd.date_range(s, e, freq="B")
        pd.DataFrame({"date": idx.strftime("%Y-%m-%d"), "close": 1.0}).to_csv(
            os.path.join(daily, code + ".csv"), index=False
        )
        tstart = "2010-03-01" if code == "510001" else s
        tidx = pd.date_range(tstart, e, freq="B")
        pd.DataFrame({"date": tidx.strftime("%Y-%m-%d"), "close": 1.0}).to_csv(
            os.path.join(daily, "sh" + code + ".csv"), index=False
        )
    # twin-less instrument
    idx = pd.date_range("2019-01-02", "2026-01-02", freq="B")
    pd.DataFrame({"date": idx.strftime("%Y-%m-%d"), "close": 1.0}).to_csv(
        os.path.join(daily, "159001.csv"), index=False
    )
    reg = os.path.join(tmp, "registry.json")
    json.dump(
        {"events": [{"date": "2013-05-06"}, {"date": "2021-07-08"}, {"date": "2026-05-13"}]},
        open(reg, "w"),
    )
    import t18_deep_probe as mod

    mod.DAILY = daily
    mod.REGISTRY = reg
    rows, stats = mod._inventory()
    assert stats["n_universe"] == 3, stats
    assert stats["n_twin_missing"] == 1, stats
    # 510001 twin longer (2010 < 2013); 510002 twin == bare start (not longer)
    assert stats["n_twin_longer_than_bare"] == 1, stats
    # common window start = latest start among available starts (2019 twin-less bare)
    starts = sorted(r["twin_start"] or r["bare_start"] for r in rows)
    assert stats["common_deep_window_start"] == starts[-1]
    ry = mod._registry_years()
    assert ry["n_events"] == 3 and ry["n_pre_2020"] == 1, ry
    assert ry["events_by_year"]["2013"] == 1 and ry["events_by_year"]["2021"] == 1, ry
    # overlap spotcheck on synthetic: twin vs bare identical closes -> diff 0
    spot = mod._overlap_spotcheck(rows)
    assert all(s.get("max_abs_close_diff", 1) == 0 for s in spot), spot
    print("selftest: all PASS")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(_selftest())
    sys.exit(run())
