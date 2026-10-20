"""W22 CONFIRM supply forecast (descriptive, L1 deterministic, zero network).

Why this exists (TRIAL_LABOR_LAW sec.4 meaning gate -- named consumers):
  (1) W22_CONFIRM_P1 (research/W22-CONFIRM-P1.md) stops only after every cell
      has >= 12 forward pre-holiday windows.  Nothing in the repo says how long
      that takes, so the supply floor (audit: ready < 3) cannot plan around it.
  (2) the CEO process face asks for "what + when" -- this face supplies the
      when for the frozen W22 confirmation without touching its judgement.

Scope discipline: ZERO judgement, ZERO prereg edit, ZERO pool write, ZERO
network, ZERO engine touch.  Read-only over:
  * the local trading calendar (data/daily/sh510300.csv first column)
  * the frozen confirm state (results/trial_labor_w22_confirm/w22_confirm_state.json)

Holiday-break definition is NOT re-derived here: it is imported from
scripts/seasonal_calendar_census.py (HOLIDAY_GAP_DAYS=4 / annotate_calendar),
the same definition the E23 census and W22 grammar were built on.  A
pre-holiday window is the last trading day before such a break (hol_pre1).

Forecast method is deliberately crude and disclosed as such: remaining windows
divided by the recent per-year pre-holiday window count from the observed
calendar.  It is a supply-planning estimate, never a claim about returns.

Usage:
    python scripts/w22_window_forecast.py run [--write]
    python scripts/w22_window_forecast.py selftest
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.seasonal_calendar_census import (  # noqa: E402
    HOLIDAY_GAP_DAYS,
    annotate_calendar,
)

CALENDAR_CSV = os.path.join(_ROOT, "data", "daily", "sh510300.csv")
STATE_JSON = os.path.join(
    _ROOT, "results", "trial_labor_w22_confirm", "w22_confirm_state.json"
)
OUT_JSON = os.path.join(
    _ROOT, "results", "trial_labor_w22_confirm", "w22_window_forecast.json"
)
RECENT_YEARS = 5


def load_calendar(path: str = CALENDAR_CSV) -> list:
    """Trading days from the local bar panel (first CSV column, header-safe)."""
    days = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if i == 0:
                continue
            tok = line.split(",", 1)[0].strip()
            if len(tok) >= 10 and tok[4] == "-" and tok[7] == "-":
                days.append(dt.date.fromisoformat(tok[:10]))
    days.sort()
    return days


def windows_from_calendar(cal: list) -> dict:
    """Pre-holiday windows (hol_pre1 days) and the break list behind them."""
    _, breaks = annotate_calendar(cal)
    windows = [dt.date.fromisoformat(b["before"]) for b in breaks]
    return {"breaks": breaks, "windows": windows}


def per_year_counts(windows: list) -> dict:
    counts: dict = {}
    for d in windows:
        counts[str(d.year)] = counts.get(str(d.year), 0) + 1
    return dict(sorted(counts.items()))


def forecast(
    cal: list,
    state: dict,
    today: dt.date | None = None,
) -> dict:
    """Build the forecast face.  `today` only labels the estimate, it never
    gates the numbers (all inputs are dated)."""
    today = today or dt.date.today()
    wf = windows_from_calendar(cal)
    windows = wf["windows"]
    fence = dt.date.fromisoformat(state["fence"])
    min_windows = int(state["min_forward_windows"])
    forward = [d for d in windows if d > fence]

    cells = state.get("cells", {})
    accrued = {k: int(v.get("forward_windows", 0)) for k, v in cells.items()}
    # both cells accrue on the same hol_pre1 days -> binding constraint = min
    accrued_min = min(accrued.values()) if accrued else 0
    remaining = max(0, min_windows - accrued_min)

    by_year = per_year_counts(windows)
    full_years = len(by_year)
    full_rate = (sum(by_year.values()) / full_years) if full_years else 0.0
    recent = {k: v for k, v in by_year.items() if int(k) > today.year - RECENT_YEARS}
    recent_rate = (sum(recent.values()) / len(recent)) if recent else 0.0
    rate = recent_rate or full_rate

    years_needed = (remaining / rate) if (remaining and rate) else 0.0
    expected = None
    if remaining and rate:
        expected = dt.date(today.year, today.month, today.day) + dt.timedelta(
            days=int(round(years_needed * 365.25))
        )

    return {
        "batch": "W22_WINDOW_FORECAST",
        "role": "descriptive supply forecast for W22_CONFIRM_P1 (no judgement)",
        "evidence_cutoff": cal[-1].isoformat() if cal else None,
        "fence": state["fence"],
        "min_forward_windows": min_windows,
        "holiday_gap_days": HOLIDAY_GAP_DAYS,
        "calendar_days": len(cal),
        "calendar_start": cal[0].isoformat() if cal else None,
        "cells": {
            k: {"forward_windows": accrued.get(k, 0), "remaining": max(0, min_windows - accrued.get(k, 0))}
            for k in cells
        },
        "binding_remaining_windows": remaining,
        "forward_windows_observed": len(forward),
        "windows_per_year": {
            "recent_%dy" % RECENT_YEARS: round(recent_rate, 3),
            "full_history": round(full_rate, 3),
            "by_year": by_year,
        },
        "years_needed_estimate": round(years_needed, 2),
        "expected_completion_estimate": expected.isoformat() if expected else None,
        "assumptions": [
            "pre-holiday window = last trading day before a >=%d calendar-day market break (imported definition, E23 lineage)" % HOLIDAY_GAP_DAYS,
            "forward accrual rate = recent observed windows/year; holiday schedule varies, so the estimate is a band centre, not a promise",
            "both cells accrue on the same hol_pre1 days, so the binding constraint is the per-cell window count",
            "estimate only: no return claim, no prereg edit, no stop-rule change",
        ],
    }


def _selftest() -> int:
    cal = [
        dt.date(2025, 12, 29), dt.date(2025, 12, 30), dt.date(2025, 12, 31),
        dt.date(2026, 1, 5), dt.date(2026, 1, 6), dt.date(2026, 1, 7),
        dt.date(2026, 1, 8), dt.date(2026, 1, 9),
        dt.date(2026, 1, 12), dt.date(2026, 1, 13), dt.date(2026, 4, 2),
        dt.date(2026, 4, 7), dt.date(2026, 4, 8), dt.date(2026, 4, 9),
    ]
    wf = windows_from_calendar(cal)
    checks = []
    # three breaks: year-end (12-31 -> 01-05), mid-January (01-13 -> 04-02),
    # and Qingming (04-02 -> 04-07); each gives exactly one pre-holiday day
    checks.append(("break count 3", len(wf["breaks"]) == 3))
    checks.append((
        "window = day before break",
        wf["windows"] == [dt.date(2025, 12, 31), dt.date(2026, 1, 13), dt.date(2026, 4, 2)],
    ))
    checks.append(("by_year split", per_year_counts(wf["windows"]) == {"2025": 1, "2026": 2}))
    state = {
        "fence": "2025-12-31",
        "min_forward_windows": 3,
        "cells": {"hol_pre1@h3": {"forward_windows": 0, "h": 3}, "hol_pre1@h4": {"forward_windows": 1, "h": 4}},
    }
    face = forecast(cal, state, today=dt.date(2026, 5, 1))
    checks.append(("fence excludes equal day", face["forward_windows_observed"] == 2))
    checks.append(("binding = min cell", face["binding_remaining_windows"] == 3))
    checks.append(("rate positive", face["windows_per_year"]["full_history"] > 0))
    checks.append(("estimate present", face["expected_completion_estimate"] is not None))
    checks.append(("no judgement keys", not any(k in face for k in ("verdict", "p_value", "excess"))))
    ok = 0
    for name, good in checks:
        print(("PASS " if good else "FAIL ") + name)
        ok += int(bool(good))
    print("selftest %d/%d" % (ok, len(checks)))
    return 0 if ok == len(checks) else 1


def _run(write: bool) -> int:
    cal = load_calendar()
    if not cal:
        print("FAIL no calendar rows")
        return 2
    with open(STATE_JSON, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    face = forecast(cal, state)
    face["generated"] = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
    print(json.dumps({k: v for k, v in face.items() if k != "windows_per_year"}, ensure_ascii=False, indent=1))
    print("windows_per_year:", json.dumps(face["windows_per_year"], ensure_ascii=False))
    if write:
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        print("wrote", os.path.relpath(OUT_JSON, _ROOT))
    return 0


def main(argv: list) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return _selftest()
    if cmd in ("run", "--write"):
        return _run("--write" in argv)
    print("usage: w22_window_forecast.py [run [--write] | selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))