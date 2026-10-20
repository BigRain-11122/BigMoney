"""OVERNIGHT-GAP CENSUS (leg-1 descriptive probe)

Question this batch answers (one line): on the local A-share daily panel,
how much of the close-to-close return is earned OVERNIGHT
(close(T) -> open(T+1)) versus INTRADAY (open(T+1) -> close(T+1)), and does
that split hold across years, boards and eras?

Consumer plan (TRIAL_LABOR_LAW sec.4 meaning gate -- named consumers):
  (1) execution-timing base rate for the T+1 open-entry family -- E14
      (limit-up premium), E18-leg-2 (dividend harvest), E20 (suspension
      resumption) all report open-entry legs; this census supplies the
      unconditional overnight/intraday decomposition those legs are read
      against;
  (2) cash-leg / DCA timing (P4) and grid paper timing decisions that turn
      on when in the session a position is marked;
  (3) input face for any future judged prereg claiming "overnight-only"
      capture -- the base rate must exist before such a claim is drafted.

Scope discipline: ZERO prereg, ZERO judged face, ZERO pool write, ZERO
network, ZERO engine touch. L1 deterministic; rerun byte-identical.
Grammar/dedup: no prior unconditional overnight/intraday decomposition in
this repo (E30's gap leg is event-conditional limit-up only; a158_truegap_ic
is a predictor IC face, not a return decomposition).

Measurement rules (frozen here, descriptive only):
  * panel = data/astock_daily/per/<code>.csv (T-87 qfq forward panel).
  * trading calendar = union of the two longest-lived files
    (600000 + 000001); a bar whose previous row is NOT the calendar
    predecessor is a suspension-resume transition -> excluded from the
    overnight leg (reseal after a gap is not an overnight move) and
    counted in meta.resume_skipped.
  * one-price bars (open == high == low == close) are unexecutable on the
    overnight leg -> excluded, counted in meta.one_price_skipped.
  * returns:
        r_on  = open(T+1)/close(T) - 1
        r_in  = close(T+1)/open(T) - 1
        r_tot = close(T+1)/close(T) - 1
    (r_on and r_in compound to r_tot; the sum is only a linear projection,
    disclosed as such).
  * prices are qfq, so r_tot is a dividend-adjusted total-ish return; the
    overnight leg of an ex-dividend day therefore absorbs the cash
    adjustment. Disclosed, not corrected (sidecars are cash-only per
    r1067 and cannot reconstruct raw close).
  * no cost model: this is a description, not a tradability claim.
  * aggregation reports BOTH observation-weighted (pooled) and
    stock-year mean-of-means (unbalanced panel guard).

usage:
    python scripts/overnight_gap_census.py run        # full census
    python scripts/overnight_gap_census.py selftest   # hermetic 12 legs
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

from lu_prem_census import board_of, era_of   # single-source lineage faces

TZ = timezone(timedelta(hours=8))
PANEL_DIR = os.path.join(_ROOT, "data", "astock_daily", "per")
OUT_DIR = os.path.join(_ROOT, "results", "overnight_gap_census")
CUTOFF_EXPECTED = "2026-10-19"
CAL_SOURCES = ("600000.csv", "000001.csv")
ONE_PRICE_TOL = 1e-12


def now_iso() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


# ---------------------------------------------------------------- calendar
def build_calendar(panel_dir: str, sources=CAL_SOURCES):
    """Union of the longest-lived files -> market trading calendar (sorted)."""
    days = set()
    for name in sources:
        p = os.path.join(panel_dir, name)
        if not os.path.exists(p):
            continue
        try:
            d = pd.read_csv(p, usecols=["date"])["date"]
        except Exception:
            continue
        days.update(pd.to_datetime(d).tolist())
    cal = sorted(days)
    pos = {d: i for i, d in enumerate(cal)}
    return cal, pos


# ------------------------------------------------------------- accumulator
FIELDS = ("n", "sum_on", "sum_in", "sum_tot", "sum_on2", "sum_tot2",
          "win_on", "win_tot")


def _blank() -> dict:
    return {f: (0.0 if f.startswith("sum") else 0) for f in FIELDS}


def _add(bucket: dict, r_on: float, r_in: float, r_tot: float) -> None:
    bucket["n"] += 1
    bucket["sum_on"] += r_on
    bucket["sum_in"] += r_in
    bucket["sum_tot"] += r_tot
    bucket["sum_on2"] += r_on * r_on
    bucket["sum_tot2"] += r_tot * r_tot
    bucket["win_on"] += 1 if r_on > 0 else 0
    bucket["win_tot"] += 1 if r_tot > 0 else 0


def _stats(b: dict) -> dict:
    n = b["n"]
    if n <= 0:
        return {"n": 0}
    m_on = b["sum_on"] / n
    m_in = b["sum_in"] / n
    m_tot = b["sum_tot"] / n
    v_on = max(b["sum_on2"] / n - m_on * m_on, 0.0)
    v_tot = max(b["sum_tot2"] / n - m_tot * m_tot, 0.0)
    se_on = math.sqrt(v_on / n) if n > 1 else float("nan")
    se_tot = math.sqrt(v_tot / n) if n > 1 else float("nan")
    return {
        "n": n,
        "on_mean": m_on,
        "in_mean": m_in,
        "tot_mean": m_tot,
        "on_share_of_linear_total": (m_on / m_tot) if m_tot else None,
        "on_sd": math.sqrt(v_on),
        "on_t": (m_on / se_on) if se_on else None,
        "tot_t": (m_tot / se_tot) if se_tot else None,
        "on_win": b["win_on"] / n,
        "tot_win": b["win_tot"] / n,
    }


# ------------------------------------------------------------------- scan
def scan_file(path: str, code: str, cal_pos: dict, agg: dict, meta: dict,
              stock_year: dict) -> None:
    try:
        df = pd.read_csv(path, usecols=["date", "open", "high", "low", "close"])
    except Exception as exc:     # unreadable file: count, never crash census
        meta["unreadable"] += 1
        if len(meta["unreadable_head"]) < 20:
            meta["unreadable_head"].append({"code": code, "err": str(exc)[:80]})
        return
    if len(df) < 3:
        meta["short_files"] += 1
        return
    d = pd.to_datetime(df["date"].to_numpy())
    o = df["open"].to_numpy(dtype=float)
    h = df["high"].to_numpy(dtype=float)
    lo = df["low"].to_numpy(dtype=float)
    c = df["close"].to_numpy(dtype=float)
    brd = board_of(code)
    n_bar = len(df)
    meta["bars"] += n_bar

    for i in range(1, n_bar):
        c0, o1, c1 = c[i - 1], o[i], c[i]
        if not (c0 > 0 and o1 > 0 and c1 > 0):
            meta["bad_px"] += 1
            continue
        ci = cal_pos.get(d[i])
        if ci is None or ci == 0 or cal_pos.get(d[i - 1]) != ci - 1:
            meta["resume_skipped"] += 1
            continue
        if (abs(o1 - c1) <= ONE_PRICE_TOL and abs(h[i] - lo[i]) <= ONE_PRICE_TOL):
            meta["one_price_skipped"] += 1
            continue
        r_on = o1 / c0 - 1.0
        r_in = c1 / o1 - 1.0
        r_tot = c1 / c0 - 1.0
        if not (abs(r_tot) < 0.75 and abs(r_on) < 0.75):   # adjustment artifact
            meta["extreme_skipped"] += 1
            continue
        meta["obs"] += 1
        yr = int(d[i].year)
        _add(agg["all"], r_on, r_in, r_tot)
        _add(agg["by_year"].setdefault(yr, _blank()), r_on, r_in, r_tot)
        _add(agg["by_board"].setdefault(brd, _blank()), r_on, r_in, r_tot)
        key = (era_of(yr), brd)
        _add(agg["by_era_board"].setdefault(key, _blank()), r_on, r_in, r_tot)
        sy = stock_year.get((code, yr))
        if sy is None:
            stock_year[(code, yr)] = [1, r_on, r_tot]
        else:
            sy[0] += 1
            sy[1] += r_on
            sy[2] += r_tot


def _fresh_agg() -> dict:
    return {"all": _blank(), "by_year": {}, "by_board": {}, "by_era_board": {}}


def _fresh_meta() -> dict:
    return {"files": 0, "bars": 0, "obs": 0, "bad_px": 0, "resume_skipped": 0,
            "one_price_skipped": 0, "extreme_skipped": 0, "unreadable": 0,
            "short_files": 0, "unreadable_head": []}


def census(panel_dir: str = PANEL_DIR, cal_sources=CAL_SOURCES,
           limit: int | None = None) -> dict:
    cal, pos = build_calendar(panel_dir, cal_sources)
    files = sorted(f for f in os.listdir(panel_dir) if f.endswith(".csv")) \
        if os.path.isdir(panel_dir) else []
    if limit:
        files = files[:limit]
    agg = _fresh_agg()
    meta = _fresh_meta()
    meta["calendar_days"] = len(cal)
    meta["calendar_first"] = cal[0].strftime("%Y-%m-%d") if cal else None
    meta["calendar_last"] = cal[-1].strftime("%Y-%m-%d") if cal else None
    stock_year: dict = {}
    for name in files:
        code = os.path.splitext(name)[0]
        meta["files"] += 1
        scan_file(os.path.join(panel_dir, name), code, pos, agg, meta, stock_year)

    # stock-year mean-of-means (unbalanced-panel guard, prospectively equal
    # to the pooled figure only when every stock contributes equally)
    sy_on = [v[1] / v[0] for v in stock_year.values() if v[0] > 0]
    sy_tot = [v[2] / v[0] for v in stock_year.values() if v[0] > 0]
    stock_year_face = {
        "n_stock_year_cells": len(sy_on),
        "on_mean_of_means": float(np.mean(sy_on)) if sy_on else None,
        "tot_mean_of_means": float(np.mean(sy_tot)) if sy_tot else None,
    }
    return {
        "ts": now_iso(),
        "probe": "overnight_gap_census",
        "leg": "leg-1 (unconditional close->open vs open->close decomposition)",
        "panel_dir": os.path.relpath(panel_dir, _ROOT).replace("\\", "/"),
        "meta": meta,
        "agg": agg,
        "stock_year": stock_year_face,
    }


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
    agg = raw["agg"]
    meta = raw["meta"]
    face = {
        "ts": raw["ts"],
        "probe": raw["probe"],
        "law_ref": "TRIAL_LABOR_LAW §2 cheap-census-first (leg-1 descriptive; "
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
            "obs_used": meta["obs"],
            "resume_skipped": meta["resume_skipped"],
            "one_price_skipped": meta["one_price_skipped"],
            "extreme_skipped": meta["extreme_skipped"],
            "bad_px": meta["bad_px"],
            "unreadable": meta["unreadable"],
            "short_files": meta["short_files"],
            "unreadable_head": meta["unreadable_head"],
            "usable_share_of_bars": (meta["obs"] / meta["bars"])
            if meta["bars"] else None,
        },
        "definition": {
            "r_on": "open(T+1)/close(T) - 1",
            "r_in": "close(T+1)/open(T) - 1",
            "r_tot": "close(T+1)/close(T) - 1",
            "aggregation": "equal-weight across stock-day observations "
                           "(pooled) plus stock-year mean-of-means",
            "cost_face": "none -- descriptive only, not a tradability claim",
        },
        "overall": _stats(agg["all"]),
        "stock_year_face": raw["stock_year"],
        "by_year": {str(k): _stats(v) for k, v in sorted(agg["by_year"].items())},
        "by_board": {k: _stats(v) for k, v in sorted(agg["by_board"].items())},
        "by_era_board": {"%s|%s" % k: _stats(v)
                         for k, v in sorted(agg["by_era_board"].items())},
        "disclosures": [
            "qfq panel: r_tot is dividend-adjusted; an ex-dividend day's cash "
            "adjustment lands inside the overnight leg (sidecars are cash-only "
            "per r1067, raw close not reconstructable) -- not corrected here",
            "suspension-resume transitions excluded from the overnight leg "
            "(calendar-predecessor rule); the resumed bar's intraday leg is "
            "also dropped to keep the two legs on the same observation set",
            "one-price bars (open==high==low==close) excluded: overnight leg is "
            "unexecutable, limit boards would bias the split",
            "|r_tot|>=75% rows dropped as adjustment/price artifacts",
            "stock-year mean-of-means reported alongside pooled means: the "
            "panel is unbalanced across listings/delistings",
            "no cost model, no position sizing, no long-short construction",
        ],
    }
    return face


def write_outputs(face: dict, out_dir: str = OUT_DIR) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    fpath = os.path.join(out_dir, "CENSUS-%s.json" % face["evidence_cutoff"])
    with open(fpath, "w", encoding="utf-8") as fh:
        json.dump(_round(face), fh, ensure_ascii=False, indent=1, sort_keys=True)
    with open(os.path.join(out_dir, "latest.json"), "w", encoding="utf-8") as fh:
        json.dump(_round(face), fh, ensure_ascii=False, indent=1, sort_keys=True)

    years = face["by_year"]
    with open(os.path.join(out_dir, "by_year.csv"), "w", encoding="utf-8",
              newline="") as fh:
        fh.write("year,n,on_mean,in_mean,tot_mean,on_share,on_win,tot_win,on_t\n")
        for y in sorted(years, key=int):
            s = years[y]
            fh.write("%s,%d,%.6f,%.6f,%.6f,%s,%.4f,%.4f,%s\n" % (
                y, s["n"], s["on_mean"], s["in_mean"], s["tot_mean"],
                "" if s.get("on_share_of_linear_total") is None
                else "%.4f" % s["on_share_of_linear_total"],
                s["on_win"], s["tot_win"],
                "" if s.get("on_t") is None else "%.2f" % s["on_t"]))
    with open(os.path.join(out_dir, "by_board.csv"), "w", encoding="utf-8",
              newline="") as fh:
        fh.write("board,n,on_mean,in_mean,tot_mean,on_share,on_win,tot_win\n")
        for b in sorted(face["by_board"]):
            s = face["by_board"][b]
            fh.write("%s,%d,%.6f,%.6f,%.6f,%s,%.4f,%.4f\n" % (
                b, s["n"], s["on_mean"], s["in_mean"], s["tot_mean"],
                "" if s.get("on_share_of_linear_total") is None
                else "%.4f" % s["on_share_of_linear_total"],
                s["on_win"], s["tot_win"]))
    return {"face": fpath,
            "by_year": os.path.join(out_dir, "by_year.csv"),
            "by_board": os.path.join(out_dir, "by_board.csv")}


# --------------------------------------------------------------- selftest
def _syn_file(path: str, rows) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("date,open,high,low,close\n")
        for r in rows:
            fh.write(",".join(str(x) for x in r) + "\n")


def selftest() -> int:
    tmp = tempfile.mkdtemp(prefix="ogc_selftest_")
    legs: list[tuple[str, bool]] = []
    try:
        pdir = os.path.join(tmp, "per")
        os.makedirs(pdir)
        # calendar: 4 days; 600000 carries the calendar, 000001 mirrors it
        days = ["2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07"]
        _syn_file(os.path.join(pdir, "600000.csv"), [
            (days[0], 10.0, 10.1, 9.9, 10.0),
            (days[1], 10.5, 10.6, 10.4, 11.0),      # r_on=+5%, r_in=+4.762%
            (days[2], 11.0, 11.0, 11.0, 11.0),      # one-price -> excluded
            (days[3], 10.0, 10.2, 9.8, 10.0),       # r_on=-9.09%, r_in=0
        ])
        _syn_file(os.path.join(pdir, "000001.csv"), [
            (days[0], 10.0, 10.1, 9.9, 10.0),
            (days[1], 10.0, 10.2, 9.9, 10.2),       # r_on=0, r_in=+2%
            (days[2], 10.2, 10.3, 10.1, 10.2),      # r_on=0, r_in=0
            (days[3], 10.2, 10.3, 10.0, 10.1),      # r_on=0, r_in=-0.98%
        ])
        # 688001: suspended bar (skips 2020-01-03) -> resume transition excluded
        _syn_file(os.path.join(pdir, "688001.csv"), [
            (days[0], 20.0, 20.2, 19.8, 20.0),
            (days[2], 21.0, 21.2, 20.8, 21.0),      # prev row != calendar pred
            (days[3], 21.0, 21.5, 20.9, 21.4),
        ])
        raw = census(panel_dir=pdir, limit=None)
        face = build_face(raw)
        ov = face["overall"]

        # leg1: calendar built from the two source files
        legs.append(("L1 calendar 4 days",
                     face["universe"]["calendar_days"] == 4))
        # leg2: 600000 excluded one-price bar -> 2 usable obs
        b_main = face["by_board"].get("main", {})
        legs.append(("L2 main board pooled from 3 files (600000 2 + 000001 3)",
                     b_main.get("n") == 5))
        # leg3: r_on mean == (0.05 + (-0.090909091) + 0 + 0 + 0)/5
        exp_on = (0.05 + (10.0 / 11.0 - 1.0)) / 5.0
        legs.append(("L3 overnight mean exact",
                     abs(b_main["on_mean"] - exp_on) < 1e-12))
        # leg4: r_in mean on the same set
        exp_in = ((11.0 / 10.5 - 1.0) + (10.0 / 10.0 - 1.0)
                  + (10.2 / 10.0 - 1.0) + (10.2 / 10.2 - 1.0)
                  + (10.1 / 10.2 - 1.0)) / 5.0
        legs.append(("L4 intraday mean exact",
                     abs(b_main["in_mean"] - exp_in) < 1e-12))
        # leg5: star board resume bar excluded -> only the 01-07 bar lands
        star = face["by_board"].get("star", {})
        legs.append(("L5 star board 1 obs (resume skipped)",
                     star.get("n") == 1
                     and face["coverage"]["resume_skipped"] == 1))
        # leg6: one-price bar excluded exactly once
        legs.append(("L6 one-price excluded once",
                     face["coverage"]["one_price_skipped"] == 1))
        # leg7: the two legs COMPOUND (not add) to the total; the pooled
        # residual must equal the mean cross-product r_on*r_in exactly
        resid = b_main["on_mean"] + b_main["in_mean"] - b_main["tot_mean"]
        exp_resid = -(0.05 * (11.0 / 10.5 - 1.0)) / 5.0
        legs.append(("L7 compound identity residual == -mean(r_on*r_in)",
                     abs(resid - exp_resid) < 1e-12))
        # leg8: board classification single-source (lu_prem_census)
        legs.append(("L8 board_of/era_of single-source",
                     board_of("688001") == "star"
                     and board_of("300001") == "chinext"
                     and era_of(2020) == "2017-2020"))
        # leg9: by_year buckets present for 2020 only
        legs.append(("L9 by_year key set == {2020}",
                     list(face["by_year"].keys()) == ["2020"]))
        # leg10: stock-year mean-of-means is balanced here -> equals pooled
        sy = face["stock_year_face"]
        legs.append(("L10 stock-year mean-of-means == pooled on balanced panel",
                     abs(sy["on_mean_of_means"] - ov["on_mean"]) < 1e-12))
        # leg11: determinism (second run byte-identical face body)
        raw2 = census(panel_dir=pdir, limit=None)
        f2 = json.loads(json.dumps(_round(build_face(raw2))))
        f1 = json.loads(json.dumps(_round(face)))
        f1.pop("ts")
        f2.pop("ts")
        legs.append(("L11 deterministic rerun", f1 == f2))
        # leg12: writers emit the three expected artifacts
        out = write_outputs(face, out_dir=os.path.join(tmp, "out"))
        legs.append(("L12 artifacts written",
                     all(os.path.exists(p) for p in out.values())))
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
        print("usage: overnight_gap_census.py [run|selftest]")
        return 2
    if not os.path.isdir(PANEL_DIR):
        print("FAIL panel dir absent: %s" % PANEL_DIR)
        return 2
    raw = census()
    face = build_face(raw)
    paths = write_outputs(face)
    ov = face["overall"]
    print("panel files=%d bars=%d obs=%d (usable %.2f%%)"
          % (face["universe"]["files"], face["universe"]["bars"],
             face["coverage"]["obs_used"],
             100.0 * (face["coverage"]["usable_share_of_bars"] or 0.0)))
    print("overnight mean=%.6f/obs  intraday mean=%.6f/obs  total=%.6f/obs"
          % (ov["on_mean"], ov["in_mean"], ov["tot_mean"]))
    print("overnight share of linear total=%s  overnight win=%.4f  total win=%.4f"
          % ("n/a" if ov.get("on_share_of_linear_total") is None
             else "%.4f" % ov["on_share_of_linear_total"],
             ov["on_win"], ov["tot_win"]))
    print("stock-year mean-of-means: overnight=%s total=%s (n=%d)"
          % (None if face["stock_year_face"]["on_mean_of_means"] is None
             else round(face["stock_year_face"]["on_mean_of_means"], 6),
             None if face["stock_year_face"]["tot_mean_of_means"] is None
             else round(face["stock_year_face"]["tot_mean_of_means"], 6),
             face["stock_year_face"]["n_stock_year_cells"]))
    print("cutoff=%s -> %s" % (face["evidence_cutoff"], paths["face"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))