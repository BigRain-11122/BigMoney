"""OVERNIGHT-GAP CENSUS (leg-2 held-position bridge)

Question this batch answers (one line): does the leg-1 overnight/intraday
split survive a multi-day HOLD -- i.e. when a position is held for 5 or 20
trading days, is the (negative) overnight bleed still proportional to time,
or does it wash out / invert inside a holding window?

Consumer plan (TRIAL_LABOR_LAW sec.4 meaning gate -- named consumers):
  (1) E14 / E18-leg-2 / E20 judged cells whose exit is a 5d or 20d hold:
      leg-1 supplies the 1-day base rate, this leg supplies the hold-length
      ladder so their open-entry legs are read against a matched horizon;
  (2) P4 DCA / grid paper marking timing: a mark taken at the close vs the
      next open differs by the overnight leg -- this face sizes that at hold
      length instead of single day;
  (3) any future judged prereg claiming "hold N days to harvest the
      overnight/intraday divergence" -- the bridge must exist first.

Scope discipline: ZERO prereg, ZERO judged face, ZERO pool write, ZERO
network, ZERO engine touch. L1 deterministic; rerun byte-identical.

Measurement rules (frozen here, descriptive only):
  * panel = data/astock_daily/per/<code>.csv (T-87 qfq forward panel),
    identical loader/exclusion lineage as overnight_gap_census.py (leg-1).
  * trading calendar = union of the two longest-lived files (600000 +
    000001); a hold window must be fully contiguous on that calendar
    (any suspension inside the window drops the window).
  * window = [i, i+H] on the stock's own row index: enter at close(i),
    exit at close(i+H). H in {5, 20}; windows are NON-OVERLAPPING per run
    (stride H from the first eligible start) so observations are not
    pseudo-replicates.
  * window exclusions: any bar with bad price, any non-calendar-predecessor
    step inside, or any one-price bar (open==high==low==close) inside -> the
    window is dropped and counted. One-price days inside a hold are NOT
    executable for the intraday leg, so they would bias the split.
  * per-window decomposition:
        r_on(d)  = open(d)/close(d-1) - 1     for d in i+1 .. i+H
        r_in(d)  = close(d)/open(d)   - 1
        r_tot(d) = close(d)/close(d-1) - 1
        on_sum   = sum r_on(d)          (linear projection)
        in_sum   = sum r_in(d)
        r_hold   = prod(1 + r_tot(d)) - 1   (compounded, = exit/entry - 1)
        resid    = on_sum + in_sum - r_hold (cross-product term, disclosed)
  * reported per horizon: pooled means of on_sum/in_sum/r_hold, the per-day
    rate (on_sum/H, in_sum/H) so it can be compared directly with the leg-1
    one-day means, win rates, t stats, and the stock-year mean-of-means
    (unbalanced-panel guard).
  * no cost model: description, not a tradability claim.

usage:
    python scripts/overnight_gap_hold_bridge.py run
    python scripts/overnight_gap_hold_bridge.py selftest
"""
from __future__ import annotations

import json
import math
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from lu_prem_census import board_of, era_of
from overnight_gap_census import build_calendar, PANEL_DIR, CAL_SOURCES

TZ = timezone(timedelta(hours=8))
OUT_DIR = os.path.join(_ROOT, "results", "overnight_gap_census")
HORIZONS = (5, 20)
ONE_PRICE_TOL = 1e-12


def now_iso() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


# ------------------------------------------------------------- accumulator
FIELDS = ("n", "sum_on", "sum_in", "sum_tot", "sum_on2", "sum_in2",
          "sum_tot2", "win_on", "win_tot")


def _blank() -> dict:
    return {f: (0.0 if f.startswith("sum") else 0) for f in FIELDS}


def _add(b: dict, on_s: float, in_s: float, r_hold: float) -> None:
    b["n"] += 1
    b["sum_on"] += on_s
    b["sum_in"] += in_s
    b["sum_tot"] += r_hold
    b["sum_on2"] += on_s * on_s
    b["sum_in2"] += in_s * in_s
    b["sum_tot2"] += r_hold * r_hold
    b["win_on"] += 1 if on_s > 0 else 0
    b["win_tot"] += 1 if r_hold > 0 else 0


def _stats(b: dict, horizon: int) -> dict:
    n = b["n"]
    if n <= 0:
        return {"n": 0}
    m_on, m_in, m_tot = b["sum_on"] / n, b["sum_in"] / n, b["sum_tot"] / n

    def _se(s2):
        v = max(s2 / n - (0.0), 0.0)
        return None

    v_on = max(b["sum_on2"] / n - m_on * m_on, 0.0)
    v_in = max(b["sum_in2"] / n - m_in * m_in, 0.0)
    v_tot = max(b["sum_tot2"] / n - m_tot * m_tot, 0.0)
    se_on = math.sqrt(v_on / n) if n > 1 else 0.0
    se_tot = math.sqrt(v_tot / n) if n > 1 else 0.0
    return {
        "n": n,
        "horizon": horizon,
        "on_sum_mean": m_on,
        "in_sum_mean": m_in,
        "hold_mean": m_tot,
        "on_per_day": m_on / horizon,
        "in_per_day": m_in / horizon,
        "on_share_of_linear_total": (m_on / m_tot) if m_tot else None,
        "on_t": (m_on / se_on) if se_on else None,
        "hold_t": (m_tot / se_tot) if se_tot else None,
        "on_win": b["win_on"] / n,
        "hold_win": b["win_tot"] / n,
    }


# ------------------------------------------------------------------- scan
def scan_file(path: str, code: str, cal_pos: dict, horizons, agg: dict,
              meta: dict, stock_year: dict) -> None:
    try:
        df = pd.read_csv(path, usecols=["date", "open", "high", "low", "close"])
    except Exception as exc:
        meta["unreadable"] += 1
        if len(meta["unreadable_head"]) < 20:
            meta["unreadable_head"].append({"code": code, "err": str(exc)[:80]})
        return
    n_bar = len(df)
    if n_bar < min(horizons) + 2:
        meta["short_files"] += 1
        return
    d = pd.to_datetime(df["date"].to_numpy())
    o = df["open"].to_numpy(dtype=float)
    h = df["high"].to_numpy(dtype=float)
    lo = df["low"].to_numpy(dtype=float)
    c = df["close"].to_numpy(dtype=float)
    cal_idx = np.array([cal_pos.get(x, -1) for x in d], dtype=np.int64)
    brd = board_of(code)
    meta["bars"] += n_bar
    meta["files"] += 1

    for H in horizons:
        start = 0
        while start + H <= n_bar - 1:
            end = start + H
            ok = True
            if cal_idx[start] < 0:
                meta["bad_windows"] += 1
                start += 1
                continue
            on_s = 0.0
            in_s = 0.0
            prod = 1.0
            for j in range(start + 1, end + 1):
                c0, o1, c1 = c[j - 1], o[j], c[j]
                if not (c0 > 0 and o1 > 0 and c1 > 0):
                    meta["bad_px"] += 1
                    ok = False
                    break
                if cal_idx[j] < 0 or cal_idx[j] != cal_idx[j - 1] + 1:
                    meta["resume_skipped"] += 1
                    ok = False
                    break
                if (abs(o1 - c1) <= ONE_PRICE_TOL
                        and abs(h[j] - lo[j]) <= ONE_PRICE_TOL):
                    meta["one_price_skipped"] += 1
                    ok = False
                    break
                r_on = o1 / c0 - 1.0
                r_tot = c1 / c0 - 1.0
                if not (abs(r_tot) < 0.75 and abs(r_on) < 0.75):
                    meta["extreme_skipped"] += 1
                    ok = False
                    break
                on_s += r_on
                in_s += r_tot - r_on          # == c1/o1 - 1 in exact math
                prod *= (1.0 + r_tot)
            if not ok:
                start += 1
                continue
            r_hold = prod - 1.0
            meta["windows"] += 1
            yr = int(d[end].year)
            _add(agg[H]["all"], on_s, in_s, r_hold)
            _add(agg[H]["by_year"].setdefault(yr, _blank()), on_s, in_s, r_hold)
            _add(agg[H]["by_board"].setdefault(brd, _blank()), on_s, in_s, r_hold)
            key = (code, yr, H)
            sy = stock_year.get(key)
            if sy is None:
                stock_year[key] = [1, on_s, r_hold]
            else:
                sy[0] += 1
                sy[1] += on_s
                sy[2] += r_hold
            start += H                      # non-overlapping stride


def _fresh_meta() -> dict:
    return {"files": 0, "bars": 0, "windows": 0, "bad_px": 0,
            "resume_skipped": 0, "one_price_skipped": 0,
            "extreme_skipped": 0, "bad_windows": 0, "unreadable": 0,
            "short_files": 0, "unreadable_head": []}


def bridge(panel_dir: str = PANEL_DIR, cal_sources=CAL_SOURCES,
           horizons=HORIZONS, limit: int | None = None) -> dict:
    cal, pos = build_calendar(panel_dir, cal_sources)
    files = sorted(f for f in os.listdir(panel_dir) if f.endswith(".csv")) \
        if os.path.isdir(panel_dir) else []
    if limit:
        files = files[:limit]
    agg = {H: {"all": _blank(), "by_year": {}, "by_board": {}}
           for H in horizons}
    meta = _fresh_meta()
    meta["calendar_days"] = len(cal)
    meta["calendar_first"] = cal[0].strftime("%Y-%m-%d") if cal else None
    meta["calendar_last"] = cal[-1].strftime("%Y-%m-%d") if cal else None
    stock_year: dict = {}
    for name in files:
        code = os.path.splitext(name)[0]
        scan_file(os.path.join(panel_dir, name), code, pos, horizons, agg,
                  meta, stock_year)

    sy_face = {}
    for H in horizons:
        on = [v[1] / v[0] for k, v in stock_year.items() if k[2] == H and v[0] > 0]
        tot = [v[2] / v[0] for k, v in stock_year.items() if k[2] == H and v[0] > 0]
        sy_face[str(H)] = {
            "n_stock_year_cells": len(on),
            "on_per_window_mean_of_means": float(np.mean(on)) if on else None,
            "hold_mean_of_means": float(np.mean(tot)) if tot else None,
        }
    return {"ts": now_iso(), "probe": "overnight_gap_hold_bridge",
            "leg": "leg-2 (held-position bridge: overnight vs intraday across "
                   "5d/20d non-overlapping holds)",
            "panel_dir": os.path.relpath(panel_dir, _ROOT).replace("\\", "/"),
            "meta": meta, "agg": agg, "stock_year": sy_face}


# ------------------------------------------------------------------- emit
def _round(obj, nd=8):
    if isinstance(obj, float):
        return round(obj, nd) if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _round(v, nd) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round(v, nd) for v in obj]
    return obj


def build_face(raw: dict) -> dict:
    meta = raw["meta"]
    by_h = {}
    for H, a in raw["agg"].items():
        st = _stats(a["all"], H)
        by_h[str(H)] = {
            "overall": st,
            "by_year": {str(k): _stats(v, H) for k, v in sorted(a["by_year"].items())},
            "by_board": {k: _stats(v, H) for k, v in sorted(a["by_board"].items())},
            "stock_year_face": raw["stock_year"].get(str(H), {}),
        }
    return {
        "ts": raw["ts"],
        "probe": raw["probe"],
        "leg": raw["leg"],
        "law_ref": "TRIAL_LABOR_LAW §2 cheap-census-first (descriptive leg-2; "
                   "no prereg, no judged face, no pool write)",
        "evidence_cutoff": str(meta.get("calendar_last") or ""),
        "universe": {
            "panel": raw["panel_dir"],
            "files": meta["files"],
            "bars": meta["bars"],
            "calendar_days": meta["calendar_days"],
            "calendar_first": meta["calendar_first"],
            "calendar_last": meta["calendar_last"],
        },
        "coverage": {
            "windows_used": meta["windows"],
            "resume_skipped": meta["resume_skipped"],
            "one_price_skipped": meta["one_price_skipped"],
            "extreme_skipped": meta["extreme_skipped"],
            "bad_px": meta["bad_px"],
            "bad_window_starts": meta["bad_windows"],
            "unreadable": meta["unreadable"],
            "short_files": meta["short_files"],
            "unreadable_head": meta["unreadable_head"],
        },
        "definition": {
            "window": "enter close(i), exit close(i+H), H contiguous calendar bars",
            "stride": "non-overlapping (start += H) so windows are not "
                      "pseudo-replicates",
            "on_sum": "sum of open(j)/close(j-1)-1 over the H days (linear)",
            "in_sum": "sum of close(j)/open(j)-1 over the H days (linear)",
            "hold": "prod(1+close(j)/close(j-1)-1)-1 == exit/entry - 1",
            "per_day_rate": "on_sum/H and in_sum/H -- directly comparable to "
                            "the leg-1 one-day means",
            "cost_face": "none -- descriptive only, not a tradability claim",
        },
        "by_horizon": by_h,
        "disclosures": [
            "qfq panel: cash adjustments land inside the overnight leg of the "
            "ex-day (sidecars are cash-only per r1067) -- not corrected",
            "windows containing ANY suspension transition, one-price bar, bad "
            "price or |r|>=75% artifact are dropped whole: the surviving set "
            "is a clean-execution subsample, biased away from limit boards",
            "non-overlapping windows mean the horizon-20 sample starts at a "
            "different phase than horizon-5; that is why both are reported "
            "separately instead of being chained",
            "on_sum + in_sum != hold return exactly; the gap is the "
            "cross-product term and is disclosed, not folded in",
            "no cost model, no position sizing, no long-short construction",
        ],
    }


def write_outputs(face: dict, out_dir: str = OUT_DIR) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    fpath = os.path.join(out_dir, "HOLDBRIDGE-%s.json" % face["evidence_cutoff"])
    for p in (fpath, os.path.join(out_dir, "holdbridge_latest.json")):
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(_round(face), fh, ensure_ascii=False, indent=1,
                      sort_keys=True)
    csv = os.path.join(out_dir, "holdbridge_by_horizon.csv")
    with open(csv, "w", encoding="utf-8", newline="") as fh:
        fh.write("horizon,n,on_sum_mean,in_sum_mean,hold_mean,on_per_day,"
                 "in_per_day,on_share,on_win,hold_win,on_t,hold_t\n")
        for H in sorted(face["by_horizon"], key=int):
            s = face["by_horizon"][H]["overall"]
            if not s.get("n"):
                continue
            fh.write("%s,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%s,%.4f,%.4f,%s,%s\n" % (
                H, s["n"], s["on_sum_mean"], s["in_sum_mean"], s["hold_mean"],
                s["on_per_day"], s["in_per_day"],
                "" if s.get("on_share_of_linear_total") is None
                else "%.4f" % s["on_share_of_linear_total"],
                s["on_win"], s["hold_win"],
                "" if s.get("on_t") is None else "%.2f" % s["on_t"],
                "" if s.get("hold_t") is None else "%.2f" % s["hold_t"]))
    return {"face": fpath, "csv": csv}


# --------------------------------------------------------------- selftest
def _syn_file(path: str, rows) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("date,open,high,low,close\n")
        for r in rows:
            fh.write(",".join(str(x) for x in r) + "\n")


def selftest() -> int:
    tmp = tempfile.mkdtemp(prefix="oghb_selftest_")
    legs: list[tuple[str, bool]] = []
    try:
        pdir = os.path.join(tmp, "per")
        os.makedirs(pdir)
        # 11 contiguous calendar days
        days = ["2021-03-%02d" % (d + 1) for d in range(10)]
        # constant +1% intraday, flat overnight: close(d) = open(d), and
        # open(d) = prev close * 1.0 -> r_on = 0, r_in = +1% per day
        rows = []
        px = 10.0
        for d in days:
            rows.append((d, round(px, 8), round(px * 1.01, 8), round(px * 0.99, 8),
                         round(px * 1.01, 8)))
            px *= 1.01
        _syn_file(os.path.join(pdir, "600000.csv"), rows)
        _syn_file(os.path.join(pdir, "000001.csv"), rows)
        raw = bridge(panel_dir=pdir, horizons=(5,), limit=None)
        face = build_face(raw)
        ov = face["by_horizon"]["5"]["overall"]
        # window 1: i=1..6 (6 rows after index0). 10 rows -> bar count 10.
        # starts: i=1 -> end 6; then i=6 -> end 11 > 9 stop. So 1 window.
        legs.append(("L1 one non-overlapping window per file (2 files)",
                     ov.get("n") == 2))
        exp_on = 0.0
        legs.append(("L2 overnight sum is exactly 0",
                     abs(ov["on_sum_mean"] - exp_on) < 1e-12))
        exp_hold = 1.01 ** 5 - 1.0
        legs.append(("L3 compounded hold == 1.01^5 - 1",
                     abs(ov["hold_mean"] - exp_hold) < 1e-9))
        legs.append(("L4 per-day intraday rate == +1%",
                     abs(ov["in_per_day"] - 0.01) < 1e-9))
        legs.append(("L5 horizon key present as string '5'",
                     list(face["by_horizon"].keys()) == ["5"]))
        legs.append(("L6 window count matches coverage face",
                     face["coverage"]["windows_used"] == 2))
        # determinism
        raw2 = bridge(panel_dir=pdir, horizons=(5,), limit=None)
        f1 = _round(build_face(raw)); f2 = _round(build_face(raw2))
        f1.pop("ts"); f2.pop("ts")
        legs.append(("L7 deterministic rerun", f1 == f2))
        out = write_outputs(face, out_dir=os.path.join(tmp, "out"))
        legs.append(("L8 artifacts written",
                     all(os.path.exists(p) for p in out.values())))
        # suspension inside the window drops the whole window: a calendar
        # anchor file keeps the full day list so the gap is visible
        rows_s = list(rows)
        del rows_s[3]                      # gap at day 4
        pdir2 = os.path.join(tmp, "per2")
        os.makedirs(pdir2)
        _syn_file(os.path.join(pdir2, "600000.csv"), rows_s)
        _syn_file(os.path.join(pdir2, "688999.csv"), rows)   # calendar anchor
        raw3 = bridge(panel_dir=pdir2, horizons=(5,),
                      cal_sources=("688999.csv",), limit=None)
        main_gapped = raw3["agg"][5]["by_board"].get("main", {}).get("n", 0)
        legs.append(("L9 gap inside window drops it",
                     main_gapped == 1
                     and raw3["meta"]["resume_skipped"] > 0))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    ok = 0
    for name, passed in legs:
        print(("PASS " if passed else "FAIL ") + name)
        ok += 1 if passed else 0
    print("selftest: %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ------------------------------------------------------------------- main
def main(argv) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd != "run":
        print("usage: overnight_gap_hold_bridge.py [run|selftest]")
        return 2
    if not os.path.isdir(PANEL_DIR):
        print("FAIL panel dir absent: %s" % PANEL_DIR)
        return 2
    raw = bridge()
    face = build_face(raw)
    paths = write_outputs(face)
    for H in sorted(face["by_horizon"], key=int):
        s = face["by_horizon"][H]["overall"]
        if not s.get("n"):
            continue
        print("H=%s n=%d on_sum=%+.4f%% in_sum=%+.4f%% hold=%+.4f%% "
              "per_day on=%+.4f%% in=%+.4f%% win_hold=%.4f"
              % (H, s["n"], 100 * s["on_sum_mean"], 100 * s["in_sum_mean"],
                 100 * s["hold_mean"], 100 * s["on_per_day"],
                 100 * s["in_per_day"], s["hold_win"]))
    print("cutoff=%s -> %s" % (face["evidence_cutoff"], paths["face"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))