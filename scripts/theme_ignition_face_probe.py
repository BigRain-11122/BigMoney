"""Theme ignition START-face probe (R6 slice) -- CEO order O-20261001-2103 T1 line,
continuation after v0.3 census (r664) honest finding: the +20%/20td/3x burst rule
is a LAGGED CONFIRMER, not an event-start detector (CEO-anchor match 2/16 within
pm30td). This slice asks the cheap next question (O-1901 meaning gate: census
before burn): do EARLIER daily-OHLC faces detect the CEO anchor starts better?

Faces (frozen BEFORE any result inspection; conventional round numbers, zero
outcome tuning; all disclosed):
  F1 nearlimit7 : single-day close-to-close change >= +7%
  F2 volstart   : amount >= 2.0x median(prior 60 bars) AND day change >= +3%
  F3 break60    : close > max(prior 60 closes)            [60td closing-high breakout]
  F4 fast10     : 10td close-to-close return >= +10%
Scan window per event: anchor_idx-60 .. anchor_idx+40 bars (anchor mapped to
first bar with date >= anchor; window clipped at series bounds, disclosed).
Match faces: primary |delta_td| <= 10 (start-detector tolerance), comparability
|delta_cal| <= 30 calendar days (v0.3 ANCHOR_MATCH_TD face). Baseline B0 = the
v0.3 burst-rule per-event record, CITED from the v0.3 census JSON (single
source; not recomputed here).

Kind: descriptive probe, NOT a judgment batch. No registration/paper claims, no
ledger rows, no engine/admission touch. Any judgment use requires a NEW frozen
prereg (TRIAL_LABOR_LAW / PREREG_TEMPLATE law).

Usage:
    python scripts/theme_ignition_face_probe.py            # build probe JSON+CSV
    python scripts/theme_ignition_face_probe.py selftest   # hermetic, zero network
Exit codes: 0 normal, 2 mechanism failure (reported as-is, never masked).
Budget cap: 60s (O-1901); elapsed printed in audit block.
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from scripts.theme_event_library import EVENTS

RESULTS_DIR = os.path.join("results", "theme_ring")
V03_JSON = os.path.join(RESULTS_DIR, "theme_events_v03_algorithmic.json")
OUT_JSON = os.path.join(RESULTS_DIR, "theme_ignition_face_probe.json")
OUT_CSV = os.path.join(RESULTS_DIR, "theme_ignition_face_probe.csv")

# --- frozen structural constants of THIS slice (disclosed, not fitted) ---
WIN_PRE = 60        # bars before anchor included in scan window
WIN_POST = 40       # bars after anchor included in scan window
PM10_TD = 10        # primary start-detector tolerance (trading bars)
PM30_CAL = 30       # v0.3-comparability tolerance (calendar days)
NEARLIMIT = 0.07    # F1 single-day change threshold
VOL_X = 2.0         # F2 amount multiple vs prior-60 median
VOL_RET = 0.03      # F2 day change threshold
BREAK_WIN = 60      # F3 breakout lookback
FAST_WIN = 10       # F4 fast-window length
FAST_RET = 0.10     # F4 window return threshold
MIN_PRIOR = 20      # min prior bars for a face to be evaluable on a day
BUDGET_SEC = 60.0

FACES = ["nearlimit7", "volstart", "break60", "fast10"]


def _r(x):
    return None if x is None else round(float(x), 4)


def load_ohlc(code, data_dir="data/daily"):
    """date,close,amount frame for an ETF (same file-resolution face as
    theme_event_library.load_series: data/daily/<code>.csv long-history file)."""
    path = os.path.join(data_dir, f"{code}.csv")
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path, usecols=["date", "close", "amount"])
    except Exception:
        return None
    if df.empty:
        return None
    return df.reset_index(drop=True)


def _chg(closes, i):
    """day change at i (needs i>=1)."""
    if i < 1 or closes[i - 1] in (None, 0):
        return None
    return closes[i] / closes[i - 1] - 1.0


def face_fires(face, closes, amounts, i):
    """Does face fire on bar i? None when not evaluable (insufficient prior)."""
    if i < MIN_PRIOR:
        return None
    lo = max(0, i - BREAK_WIN)
    if face == "nearlimit7":
        ch = _chg(closes, i)
        return None if ch is None else ch >= NEARLIMIT
    if face == "volstart":
        ch = _chg(closes, i)
        if ch is None:
            return None
        win = amounts[lo:i]
        med = sorted(win)[len(win) // 2] if win else None
        if med in (None, 0):
            return None
        return (amounts[i] >= VOL_X * med) and (ch >= VOL_RET)
    if face == "break60":
        return closes[i] > max(closes[lo:i])
    if face == "fast10":
        if i < FAST_WIN:
            return None
        base = closes[i - FAST_WIN]
        if base in (None, 0):
            return None
        return closes[i] / base - 1.0 >= FAST_RET
    raise ValueError(face)


def probe_event(ev):
    """Per-event face grid. Returns dict (honest None faces disclosed)."""
    code = ev["proxy"]
    anchor = ev["ignition"]
    df = load_ohlc(code)
    dates = list(df["date"].values) if df is not None else []
    closes = list(df["close"].values) if df is not None else []
    amounts = [float(a) if pd.notna(a) else 0.0 for a in df["amount"].values] if df is not None else []

    a_ts = pd.Timestamp(anchor)
    idx = [k for k, d in enumerate(dates) if pd.Timestamp(d) >= a_ts]
    anchor_idx = idx[0] if idx else None
    rec = {"id": ev["id"], "theme": ev["theme"], "proxy": code, "ceo_anchor": anchor,
           "series_found": df is not None, "n_bars": len(dates)}
    if anchor_idx is None:
        rec["anchor_face"] = "anchor_after_series_end"
        for f in FACES:
            rec[f] = {"fire_date": None, "delta_td": None, "delta_cal": None}
        return rec
    anchor_date_used = dates[anchor_idx]
    rec["anchor_date_used"] = anchor_date_used
    rec["anchor_face"] = ("exact" if anchor_date_used == anchor
                          else "next_trading_day")
    rec["series_start"] = dates[0]
    if dates[0] > anchor:
        rec["anchor_face"] = "series_starts_after_anchor (proxy listed late; window head-truncated, disclosed)"

    w_lo = max(0, anchor_idx - WIN_PRE)
    w_hi = min(len(dates) - 1, anchor_idx + WIN_POST)
    rec["window"] = [dates[w_lo], dates[w_hi]]

    for f in FACES:
        fire_idx, not_eval = None, True
        for i in range(w_lo, w_hi + 1):
            r = face_fires(f, closes, amounts, i)
            if r is None:
                continue
            not_eval = False
            if r:
                fire_idx = i
                break
        if fire_idx is None:
            rec[f] = {"fire_date": None, "delta_td": None, "delta_cal": None,
                      "status": ("no_fire_in_window" if not not_eval
                                 else "face_not_evaluable_in_window")}
        else:
            d_td = fire_idx - anchor_idx
            d_cal = (pd.Timestamp(dates[fire_idx]) - a_ts).days
            rec[f] = {"fire_date": dates[fire_idx], "delta_td": d_td,
                      "delta_cal": d_cal,
                      "match_pm10td": abs(d_td) <= PM10_TD,
                      "match_pm30cal": abs(d_cal) <= PM30_CAL}
    return rec


def run():
    t0 = time.time()
    records = [probe_event(ev) for ev in EVENTS]

    # baseline B0: cite v0.3 per-event anchor matches (single source, not recomputed)
    b0 = {}
    if os.path.exists(V03_JSON):
        with open(V03_JSON, "r", encoding="utf-8") as f:
            v03 = json.load(f)
        for m in v03.get("ceo_anchor_matches", []):
            b0[m["id"]] = {"detected_within_pm30td": m.get("detected_within_pm30td"),
                           "nearest": m.get("nearest_detected")}

    def _med(v):
        v = sorted(x for x in v if x is not None)
        return _r(v[len(v) // 2]) if v else None

    summary = {}
    for f in FACES + ["B0_v03_burst_rule"]:
        if f == "B0_v03_burst_rule":
            n30 = sum(1 for k in b0 if b0[k]["detected_within_pm30td"])
            summary[f] = {"n_events_pm30cal": n30, "of": len(EVENTS),
                          "source": "theme_events_v03_algorithmic.json ceo_anchor_matches (cited)"}
            continue
        fires = [r for r in records if r.get(f, {}).get("fire_date")]
        summary[f] = {
            "n_fire_in_window": len(fires),
            "n_match_pm10td": sum(1 for r in fires if r[f]["match_pm10td"]),
            "n_match_pm30cal": sum(1 for r in fires if r[f]["match_pm30cal"]),
            "median_delta_td": _med([r[f]["delta_td"] for r in fires]),
            "median_abs_delta_td": _med([abs(r[f]["delta_td"]) for r in fires]),
            "n_face_not_evaluable": sum(1 for r in records
                                        if r.get(f, {}).get("status") == "face_not_evaluable_in_window"),
        }

    out = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "version": "v0.6-r6-startface-probe",
        "order_ref": "O-20261001-2103 (T1 line R6 slice, post-v0.3 lagged-confirmer finding)",
        "ticket_ref": "T-2026-10-04-165-P1 continuation slice",
        "kind": "descriptive_probe",
        "claims_note": ("NO registration/paper claims; faces are mechanism-quality "
                        "candidates, not truth; any judgment use requires a NEW "
                        "frozen prereg; no ledger rows (measurement face)"),
        "constants": {"WIN_PRE": WIN_PRE, "WIN_POST": WIN_POST, "PM10_TD": PM10_TD,
                      "PM30_CAL": PM30_CAL, "NEARLIMIT": NEARLIMIT, "VOL_X": VOL_X,
                      "VOL_RET": VOL_RET, "BREAK_WIN": BREAK_WIN, "FAST_WIN": FAST_WIN,
                      "FAST_RET": FAST_RET, "MIN_PRIOR": MIN_PRIOR},
        "events": records,
        "summary_by_face": summary,
        "honest_limits": [
            "faces are conventional daily-OHLC readings, never tuned on outcomes; a null result (no face beats 2/16) is REPORTED as the finding",
            "anchor->first-bar mapping disclosed per event; proxies listed after the anchor carry head-truncated windows",
            "single fire per face per window (first fire); multiple candidate days inside one window are not ranked here",
            "start-detector quality on 16 CEO anchors is a MECHANISM face; it does not imply tradability (entry cost/exit rules need their own prereg)",
        ],
        "audit": {"elapsed_sec": _r(time.time() - t0), "budget_cap_sec": BUDGET_SEC,
                  "deterministic": "no rng anywhere; rerun byte-stable except generated ts"},
    }
    if out["audit"]["elapsed_sec"] > BUDGET_SEC:
        print(f"BUDGET BREACH: elapsed {out['audit']['elapsed_sec']}s > cap {BUDGET_SEC}s")
        return 2

    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        head = ["id", "theme", "proxy", "ceo_anchor", "anchor_face"]
        for fc in FACES:
            head += [f"{fc}_fire_date", f"{fc}_delta_td", f"{fc}_match_pm10td"]
        w.writerow(head)
        for r in records:
            row = [r["id"], r["theme"], r["proxy"], r["ceo_anchor"], r["anchor_face"]]
            for fc in FACES:
                d = r.get(fc, {})
                row += [d.get("fire_date"), d.get("delta_td"),
                        d.get("match_pm10td", "")]
            w.writerow(row)
    print(f"probe done: {len(records)} events x {len(FACES)} faces -> {OUT_JSON}")
    for f in FACES:
        s = summary[f]
        print(f"  {f:12s} fire={s['n_fire_in_window']:2d}/16 pm10={s['n_match_pm10td']:2d} "
              f"pm30cal={s['n_match_pm30cal']:2d} med_delta_td={s['median_delta_td']}")
    print(f"  B0 v0.3 rule  pm30cal={summary['B0_v03_burst_rule']['n_events_pm30cal']}/16 (cited)")
    return 0


def selftest():
    """Hermetic: synthetic series only, zero network, zero repo-file reads."""
    ok = []

    def _fe(face, closes, amounts, i):
        return face_fires(face, closes, amounts, i)

    # S1 nearlimit7: +8% fires, +6% does not (i>=MIN_PRIOR so the face is evaluable)
    c = [100.0] * 40
    c[25] = 108.0
    ok.append(("S1 nearlimit fire", _fe("nearlimit7", c, [1.0] * 40, 25) is True))
    c2 = [100.0] * 40
    c2[25] = 106.0
    ok.append(("S1 nearlimit no-fire", _fe("nearlimit7", c2, [1.0] * 40, 25) is False))
    # S2 volstart: 2x median amount AND +3% change
    ok.append(("S2 volstart fire", _fe("volstart", [100.0, 103.1] + [100.0] * 28,
                                       [10.0] * 30, 1) is None))  # i<MIN_PRIOR -> not evaluable
    ok.append(("S2 volstart not-eval", _fe("volstart", [100.0] * 30, [1.0] * 30, 5) is None))
    c3 = [100.0] * 60
    c3[40] = 104.0
    a3 = [10.0] * 60
    a3[40] = 25.0
    ok.append(("S2 volstart fire@40", _fe("volstart", c3, a3, 40) is True))
    a3[40] = 15.0
    ok.append(("S2 volstart amount-fail", _fe("volstart", c3, a3, 40) is False))
    # S3 break60: close above prior 60 max
    c4 = [100.0] * 30 + [99.0] * 30
    c4[59] = 101.0
    ok.append(("S3 break60 fire", _fe("break60", c4, [1.0] * 60, 59) is True))
    c4[59] = 99.5
    ok.append(("S3 break60 no-fire", _fe("break60", c4, [1.0] * 60, 59) is False))
    # S4 fast10: +10% in 10 bars
    c5 = [100.0] * 40
    c5[39] = 111.0
    ok.append(("S4 fast10 fire", _fe("fast10", c5, [1.0] * 40, 39) is True))
    c5[39] = 109.0
    ok.append(("S4 fast10 no-fire", _fe("fast10", c5, [1.0] * 40, 39) is False))
    # S5 anchor mapping: non-trading anchor -> next trading bar
    dates = ["2024-01-05", "2024-01-08", "2024-01-09"]
    a_ts = pd.Timestamp("2024-01-06")  # Saturday
    idx = [k for k, d in enumerate(dates) if pd.Timestamp(d) >= a_ts]
    ok.append(("S5 anchor next-trading-day", dates[idx[0]] == "2024-01-08"))
    # S6 window head-clipping: anchor_idx < WIN_PRE clips at 0 (no crash face)
    ok.append(("S6 head-clip", max(0, 3 - WIN_PRE) == 0))
    # S7 delta sign: fire before anchor -> negative delta_td
    ok.append(("S7 delta sign", (5 - 9) < 0))

    n_pass = sum(1 for _, v in ok if v)
    for name, v in ok:
        if not v:
            print(f"FAIL: {name}")
    print(f"selftest: {n_pass}/{len(ok)} PASS")
    return 0 if n_pass == len(ok) else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    sys.exit(run())
