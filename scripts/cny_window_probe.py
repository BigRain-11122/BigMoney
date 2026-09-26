"""CNY closure window extraction probe -- CNY_WINDOW_P1 prereg sec.2 face.

Zoo sec.8 family #38 (holiday effect) evidence-upgrade: derives Spring
Festival market closures from the IN-REPO trading panel (510300 calendar
face) and freezes the concrete PRE/POST window bar dates the batch
consumes. Deterministic, zero network -- calendar facts, not results.

Detection rule (frozen in research/shortline/CNY_WINDOW_PREREG.md sec.3
BEFORE any evaluation run; window-shopping red line):
  per calendar year Y -- among consecutive-trading-day calendar gaps with
  >= 5 non-trading days whose first non-trading day falls in [Jan 15,
  Mar 1], the CNY closure = the longest such gap (ties -> start nearest
  Feb 10). Known CNY dates (public calendar facts) must fall inside each
  detected bracket (validation gate); 2020 COVID extension disclosed,
  NOT excluded (no post-hoc surgery).

Windows consumed by the batch (mask semantics = p1_strategy_screen family
precedent: entry at close of bar before window -> engine T+1 open):
  PRE-5  = last 5 trading bars ending at the last bar before closure.
  POST-5 = first 5 trading bars starting at the reopen bar.

Usage:
  python scripts/cny_window_probe.py            -> results/cny_window_probe.json
  python scripts/cny_window_probe.py selftest   -> offline self-check
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

PANEL = os.path.join("data", "daily", "510300.csv")
OUT = os.path.join("results", "cny_window_probe.json")

# Public calendar facts (CNY day of year 2020-2026) -- validation anchors.
KNOWN_CNY = {
    2020: "2020-01-25", 2021: "2021-02-12", 2022: "2022-02-01",
    2023: "2023-01-22", 2024: "2024-02-10", 2025: "2025-01-29",
    2026: "2026-02-17",
}
MIN_GAP_DAYS = 5          # non-trading days; official CNY closure is 7-9
BRACKET_START = (1, 15)   # Jan 15
BRACKET_END = (3, 1)       # Mar 1 (covers CNY days Jan 21 - Feb 20 range)
TIE_ANCHOR = (2, 10)      # ties resolved nearest to Feb 10
WINDOW_BARS = 5           # PRE-5 / POST-5, frozen


def _in_bracket(d) -> bool:
    return ((BRACKET_START[0], BRACKET_START[1]) <= (d.month, d.day)
            <= (BRACKET_END[0], BRACKET_END[1]))


def detect_events(dates: pd.DatetimeIndex) -> list[dict]:
    """One pass over consecutive-bar calendar gaps -> CNY events per year."""
    ds = pd.DatetimeIndex(dates).sort_values()
    events = []
    for i in range(len(ds) - 1):
        d1, d2 = ds[i], ds[i + 1]
        gap_days = (d2 - d1).days - 1        # non-trading days in between
        first_off = d1 + pd.Timedelta(days=1)
        if gap_days >= MIN_GAP_DAYS and _in_bracket(first_off):
            events.append({"year": first_off.year, "gap_days": gap_days,
                           "last_pre_bar": d1, "reopen_bar": d2,
                           "closure_start": first_off,
                           "closure_end": d2 - pd.Timedelta(days=1)})
    # longest gap per year wins; ties -> start nearest Feb 10 (deterministic)
    best: dict[int, dict] = {}
    for e in events:
        y = e["year"]
        key = (e["gap_days"],
               -abs((e["closure_start"].month - TIE_ANCHOR[0]) * 31
                    + e["closure_start"].day - TIE_ANCHOR[1]))
        if y not in best or key > best[y]["_key"]:
            best[y] = {**e, "_key": key}
    return [{k: v for k, v in e.items() if k != "_key"}
            for _, e in sorted(best.items())]


def build_windows(ds: pd.DatetimeIndex, events: list[dict]) -> list[dict]:
    """Attach frozen PRE-5/POST-5 bar lists to each event."""
    pos = {d: i for i, d in enumerate(ds)}
    out = []
    for e in events:
        i_last, i_re = pos[e["last_pre_bar"]], pos[e["reopen_bar"]]
        if i_last < WINDOW_BARS - 1 or i_re + WINDOW_BARS > len(ds):
            raise ValueError(f"insufficient bars around {e['year']} event "
                             f"(panel edge) -- probe refuses silently-truncated windows")
        e["pre5"] = [str(d.date()) for d in ds[i_last - WINDOW_BARS + 1: i_last + 1]]
        e["post5"] = [str(d.date()) for d in ds[i_re: i_re + WINDOW_BARS]]
        out.append(e)
    return out


def _validate(events: list[dict]) -> dict:
    per_year = {}
    for e in events:
        known = KNOWN_CNY.get(e["year"])
        inside = (known is not None
                  and e["closure_start"] <= pd.Timestamp(known) <= e["closure_end"])
        per_year[e["year"]] = {"known_cny_day": known,
                               "cny_day_inside_bracket": bool(inside)}
    return {"per_year": per_year,
            "all_pass": all(v["cny_day_inside_bracket"] for v in per_year.values())
            and len(per_year) == len(KNOWN_CNY)}


def run_probe(panel: str = PANEL) -> dict:
    df = pd.read_csv(panel, parse_dates=["date"])
    ds = pd.DatetimeIndex(df["date"]).sort_values()
    events = build_windows(ds, detect_events(ds))
    payload = {
        "probe": "cny_window_probe",
        "panel": {"face": panel, "first": str(ds[0].date()),
                  "last": str(ds[-1].date()), "n_bars": len(ds)},
        "rule": {"min_gap_days": MIN_GAP_DAYS,
                 "bracket": "Jan15-Mar1(first non-trading day)",
                 "tie_anchor": "Feb10", "window_bars": WINDOW_BARS},
        "events": [{**{k: (str(v.date()) if isinstance(v, pd.Timestamp) else v)
                       for k, v in e.items()},
                    "covid_extension": e["year"] == 2020}
                   for e in events],
        "validation": _validate(events),
        "n_events": len(events),
    }
    return payload


def selftest() -> int:
    ok = lambda name, cond: print(f"  [{'PASS' if cond else 'FAIL'}] {name}") \
        or (0 if cond else 1)
    print("cny_window_probe selftest:")
    fails = 0
    # F1 clean branch: synthetic 3-year calendar with a planted 8-day Feb gap
    days = pd.date_range("2023-01-02", "2023-03-31", freq="D")
    cal = pd.DatetimeIndex([d for d in days if d.weekday() < 5])
    cal = cal[~((cal >= "2023-01-23") & (cal <= "2023-01-30"))]  # 8-day closure
    ev = detect_events(cal)
    fails += ok("F1 single event detected", len(ev) == 1
                and ev[0]["gap_days"] >= MIN_GAP_DAYS)
    wv = build_windows(cal, ev)
    fails += ok("F1 pre5 ends at last pre bar",
                len(wv[0]["pre5"]) == WINDOW_BARS
                and wv[0]["pre5"][-1] == str(pd.Timestamp("2023-01-20").date()))
    fails += ok("F1 post5 starts at reopen",
                wv[0]["post5"][0] == str(pd.Timestamp("2023-01-31").date()))
    # F2 national-day gap excluded by bracket (Oct gap must not fire)
    cal2 = pd.DatetimeIndex([d for d in pd.date_range("2024-01-02", "2024-11-30", freq="D")
                             if d.weekday() < 5])
    cal2 = cal2[~((cal2 >= "2024-02-09") & (cal2 <= "2024-02-16"))]   # CNY 8d
    cal2 = cal2[~((cal2 >= "2024-10-01") & (cal2 <= "2024-10-07"))]   # NatDay 7d
    ev2 = detect_events(cal2)
    fails += ok("F2 oct gap excluded by bracket",
                len(ev2) == 1 and ev2[0]["year"] == 2024)
    # F3 dirty branch: no gap >= 5 in bracket -> zero events, honest
    cal3 = pd.DatetimeIndex([d for d in pd.date_range("2025-01-02", "2025-03-14", freq="D")
                             if d.weekday() < 5])
    fails += ok("F3 no-gap year -> 0 events", len(detect_events(cal3)) == 0)
    # F4 live panel probe + validation gate all-pass
    p = run_probe()
    fails += ok("F4 live panel validation all_pass",
                p["validation"]["all_pass"] and p["n_events"] == len(KNOWN_CNY))
    fails += ok("F4 2020 covid extension flagged",
                any(e["covid_extension"] for e in p["events"]))
    print(f"  selftest {'PASS' if fails == 0 else 'FAIL'} ({fails} fail)")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "selftest":
        return selftest()
    payload = run_probe()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(f"probe -> {OUT}: n_events={payload['n_events']} "
          f"validation_all_pass={payload['validation']['all_pass']}")
    return 0 if payload["validation"]["all_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
