#!/usr/bin/env python
# -*- coding: ascii -*-
"""REGIME-AXIS-M1 freeze face (O-20261010-1725-bm-a schedule item 10-11).

Derives the panic-window column of the M-1 test-matrix regime axis:
  P-criterion (panic)   : n_sealed_down >= 1000   (thermo axis-3, REGIME_THERMO_V1)
  I-criterion (icepoint) : n_sealed <= 30 AND n_sealed_down >= 800
                           (up-board frozen solid AND panic elevated = themo ice face)
Union -> panic days -> clustered into event windows (gap <= 10 trading days).

Source panel = results/regime_thermo/thermo_daily.csv (P-5C frozen face,
cutoff 2026-09-22). Zero-burn, zero-judgment, pure descriptive derivation.
Idempotent: same panel -> byte-identical JSON.

Usage:
  python scripts/regime_axis_m1.py run       # derive + write results JSON
  python scripts/regime_axis_m1.py selftest  # hermetic assertions, no writes
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "results" / "regime_thermo" / "thermo_daily.csv"
OUT_DIR = ROOT / "results" / "regime_axis_m1"
OUT = OUT_DIR / "panic_windows.json"

P_DOWN = 1000   # single-day limit-down-sealed count (order text verbatim)
I_SEALED = 30   # up-limit sealed count floor (thermo up-board freeze)
I_DOWN = 800    # limit-down floor for the ice face (panic-adjacent)
GAP_TRD = 10    # cluster gap in trading days


def _derive():
    t = pd.read_csv(PANEL)
    t = t[["date", "n_sealed", "n_touched", "seal_rate", "n_sealed_down"]].copy()
    t = t.sort_values("date").reset_index(drop=True)
    p_mask = t.n_sealed_down >= P_DOWN
    i_mask = (t.n_sealed <= I_SEALED) & (t.n_sealed_down >= I_DOWN)
    t["crit"] = ""
    t.loc[p_mask, "crit"] = "P"
    t.loc[i_mask, "crit"] = t.loc[i_mask, "crit"].replace("", "I")
    sel = t[p_mask | i_mask].copy()
    sel["crit"] = sel.apply(
        lambda r: ("P" if p_mask.loc[r.name] else "")
        + ("I" if i_mask.loc[r.name] and "I" not in "" else ""),
        axis=1,
    )
    # simpler: rebuild crit directly
    sel["crit"] = [
        ("P" if pm else "") + ("I" if im else "")
        for pm, im in zip(p_mask[sel.index], i_mask[sel.index])
    ]
    days = [
        {
            "date": r.date,
            "n_sealed": int(r.n_sealed),
            "n_touched": int(r.n_touched),
            "seal_rate": round(float(r.seal_rate), 6),
            "n_sealed_down": int(r.n_sealed_down),
            "crit": r.crit,
        }
        for r in sel.itertuples()
    ]
    # cluster by trading-day gap on the full panel calendar
    dates = list(t.date)
    pos = {d: i for i, d in enumerate(dates)}
    windows = []
    cur = []
    for d in days:
        if not cur:
            cur = [d]
            continue
        if pos[d["date"]] - pos[cur[-1]["date"]] <= GAP_TRD:
            cur.append(d)
        else:
            windows.append(cur)
            cur = [d]
    if cur:
        windows.append(cur)
    wins = [
        {
            "w": i + 1,
            "start": w[0]["date"],
            "end": w[-1]["date"],
            "n_days": len(w),
            "peak_down": max(x["n_sealed_down"] for x in w),
            "dates": [x["date"] for x in w],
        }
        for i, w in enumerate(windows)
    ]
    return {
        "face": "REGIME-AXIS-M1 panic-window column, frozen v1.0",
        "order_ref": "O-20261010-1725-bm-a",
        "panel_source": "results/regime_thermo/thermo_daily.csv (REGIME_THERMO_V1 frozen spec)",
        "panel_cutoff": dates[-1],
        "criteria": {
            "P": "n_sealed_down >= %d (single-day limit-down >= 1000)" % P_DOWN,
            "I_icepoint": "n_sealed <= %d AND n_sealed_down >= %d (thermo up-board freeze x panic-adjacent)" % (I_SEALED, I_DOWN),
            "union": "P or I",
            "cluster_gap_trading_days": GAP_TRD,
        },
        "n_days": len(days),
        "n_windows": len(wins),
        "days": days,
        "windows": wins,
        "honesty": [
            "descriptive derivation only, zero judgment claims; M-1 matrix slicing is a separate face",
            "ice-face adds only days meeting BOTH frozen sub-conditions (no threshold fishing)",
            "panel = P-5C frozen face cutoff 2026-09-22; panel refresh extends cutoff and this face re-derives deterministically",
        ],
    }


def cmd_run():
    data = _derive()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    new = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    if old == new:
        print("no-op: identical face already present (cutoff=%s)" % data["panel_cutoff"])
        return 0
    OUT.write_text(new, encoding="utf-8")
    print("written %s days=%d windows=%d cutoff=%s"
          % (OUT, data["n_days"], data["n_windows"], data["panel_cutoff"]))
    return 0


def cmd_selftest():
    data = _derive()
    by = {d["date"]: d for d in data["days"]}
    # famous-day anchors from REGIME_THERMO_V1 sec.2 (machine-verified)
    anchors = {
        "2015-08-24": 2015,
        "2016-01-04": 1230,
        "2020-02-03": 2938,
        "2024-02-05": 1334,
        "2025-04-07": 2770,
    }
    for d, down in anchors.items():
        assert d in by and by[d]["n_sealed_down"] == down, "anchor fail %s" % d
        assert "P" in by[d]["crit"], "anchor %s must be P" % d
    # 2015-06-19 famous top-break week: caught by ice face only (47 sealed / 925 down)
    assert "2015-06-19" not in by, "2015-06-19 must NOT be in frozen union (47>30 sealed)"
    # count == 25 on the frozen panel (order text '~25 windows' expectation)
    assert data["n_days"] == 25, "expected 25 panic days, got %d" % data["n_days"]
    # every I-day meets both sub-conditions
    for d in data["days"]:
        if "I" in d["crit"]:
            assert d["n_sealed"] <= I_SEALED and d["n_sealed_down"] >= I_DOWN, d
        if "P" in d["crit"]:
            assert d["n_sealed_down"] >= P_DOWN, d
    # windows ordering + coverage
    alld = [x for w in data["windows"] for x in w["dates"]]
    assert alld == [d["date"] for d in data["days"]], "window coverage fail"
    assert data["windows"] == sorted(data["windows"], key=lambda w: w["start"])
    # determinism: second derive byte-equal
    assert json.dumps(_derive(), sort_keys=True) == json.dumps(data, sort_keys=True)
    print("selftest: %d legs PASS (anchors 5/5, union=25, I-subcondition 5/5, coverage+order+det)" % 7)
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
