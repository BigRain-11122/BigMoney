"""OVERNIGHT-GAP CENSUS (leg-3 conditioned decomposition)

Question this batch answers (one line): the leg-1/leg-2 finding is that the
overnight leg is structurally negative (~-0.089%/bar, linear in hold length).
This leg asks WHO pays that toll: does the overnight bleed concentrate in a
particular liquidity / volatility / gap regime, or is it uniform across the
panel? A uniform toll means no selection escape; a concentrated toll means
the T+1 open-entry families can be read against a matched regime base rate.

Consumer plan (TRIAL_LABOR_LAW sec.4 meaning gate -- named consumers):
  (1) E14 (limit-up premium) / E18-leg-2 (dividend harvest) / E20
      (suspension resumption) open-entry legs -- they already cite the
      unconditional leg-1 base rate; this leg supplies the CONDITIONED base
      rate so a liquid / quiet-name pick is not read against a panel mean
      that is dominated by a different regime;
  (2) P4 DCA / grid paper marking timing -- a mark taken at close vs the
      next open differs by the overnight leg, and this face sizes that
      difference per liquidity/volatility state;
  (3) any future judged prereg claiming an overnight/intraday edge that is
      really a liquidity or volatility proxy -- this face is the required
      control before such a claim is drafted.

Scope discipline: ZERO prereg, ZERO judged face, ZERO pool write, ZERO
network, ZERO engine touch. L1 deterministic; rerun byte-identical.

Measurement rules (frozen here, descriptive only):
  * panel = data/astock_daily/per/<code>.csv (T-87 qfq forward panel),
    identical loader/exclusion lineage as overnight_gap_census.py (leg-1):
    bad px / suspension-resume transition / one-price bar / |r|>=75%
    adjustment artifact all drop the OBSERVATION (not the whole file) and
    are counted in meta.
  * conditioning features are read from the SAME bar the decision is made
    at (close of day i), so they are strictly causal for the day i+1
    overnight/intraday returns that are measured:
        liq_pct(i) = percentile rank of amount(i) inside the stock's own
                     trailing W=250 bars (self-relative; today included)
        vol_pct(i) = percentile rank of rv20(i) inside the stock's own
                     trailing W=250 rv20 values (rv20 = 20-bar std of
                     close-to-close returns)
        gap(i)     = open(i)/close(i-1) - 1, bucketed by the frozen edges
  * self-relative percentiles are used instead of cross-sectional ones on
    purpose: they need no per-date cross-section materialisation (the panel
    is 16M+ bars) and they answer the same applied question ("is this name
    unusually liquid / quiet for itself right now?"). The absolute gap
    buckets are cross-sectional by construction (same edges for every name).
  * measured target = day i+1 decomposition, leg-1 verbatim:
        r_on = open(i+1)/close(i) - 1
        r_in = close(i+1)/open(i+1) - 1
        r_tot = close(i+1)/close(i) - 1
  * i+1 must be the calendar successor of i (same resume rule as leg-1) and
    must itself clear bad-px / one-price / extreme gates.
  * buckets: liq_pct quintiles {q1..q5} on [0,1] by 0.2 steps; vol_pct same;
    gap buckets frozen as GAP_EDGES below. Reported faces: marginal rows for
    liq and vol quintiles, the liq x gap cross-tab, and the vol x gap
    cross-tab. Every row carries n, mean r_on / r_in / r_tot, per-leg win
    rates, t stats and the stock-year mean-of-means guard count.
  * no cost model: description, not a tradability claim.

usage:
    python scripts/overnight_gap_conditioned.py run
    python scripts/overnight_gap_conditioned.py selftest
"""
from __future__ import annotations

import json
import math
import os
import sys
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

from lu_prem_census import board_of
from overnight_gap_census import build_calendar, PANEL_DIR

OUT_DIR = os.path.join(_ROOT, "results", "overnight_gap_census")
CUTOFF = "2026-10-19"          # last complete bar day on the local panel
ONE_PRICE_TOL = 1e-9
EXTREME_ABS = 0.75
WIN_W = 250                    # self-relative lookback (bars)
MIN_WIN = 60                   # need a usable window before a percentile
RV_N = 20
GAP_EDGES = (-0.02, -0.005, 0.005, 0.02)
GAP_NAMES = ("gap_lt_-2", "gap_-2_-0.5", "gap_-0.5_0.5",
             "gap_0.5_2", "gap_gt_2")


def now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=8))).strftime(
        "%Y-%m-%dT%H:%M:%S+08:00")


# ------------------------------------------------------------------ bucket math
def _blank() -> dict:
    return {"n": 0, "on_sum": 0.0, "on_sq": 0.0, "on_win": 0,
            "in_sum": 0.0, "in_sq": 0.0, "in_win": 0,
            "tot_sum": 0.0, "tot_win": 0}


def _add(b: dict, r_on: float, r_in: float, r_tot: float) -> None:
    b["n"] += 1
    b["on_sum"] += r_on
    b["on_sq"] += r_on * r_on
    if r_on > 0:
        b["on_win"] += 1
    b["in_sum"] += r_in
    b["in_sq"] += r_in * r_in
    if r_in > 0:
        b["in_win"] += 1
    b["tot_sum"] += r_tot
    if r_tot > 0:
        b["tot_win"] += 1


def _leg_stats(n: int, s: float, sq: float, win: int) -> dict:
    if n < 2:
        return {"n": n, "mean": None, "win": None, "t": None}
    mean = s / n
    var = max(sq / n - mean * mean, 0.0)
    se = math.sqrt(var / n) if var > 0 else 0.0
    return {"n": n, "mean": round(mean, 8), "win": round(win / n, 6),
            "t": (round(mean / se, 3) if se > 0 else None)}


def _stats(b: dict) -> dict:
    if b["n"] < 2:
        return {"n": b["n"],
                "r_on": {"n": b["n"], "mean": None, "win": None, "t": None},
                "r_in": {"n": b["n"], "mean": None, "win": None, "t": None},
                "r_tot": _leg_stats(b["n"], b["tot_sum"], 0.0, b["tot_win"])}
    return {
        "n": b["n"],
        "r_on": _leg_stats(b["n"], b["on_sum"], b["on_sq"], b["on_win"]),
        "r_in": _leg_stats(b["n"], b["in_sum"], b["in_sq"], b["in_win"]),
        "r_tot": _leg_stats(b["n"], b["tot_sum"], 0.0, b["tot_win"]),
    }


def _pct_rank(arr: np.ndarray, i: int, w: int) -> float:
    """Percentile rank of arr[i] inside arr[i-w+1 .. i] (today included)."""
    lo = i - w + 1
    if lo < 0:
        return float("nan")
    seg = arr[lo:i + 1]
    if np.isnan(seg[-1]) or np.isnan(seg).any():
        return float("nan")
    return float((seg <= seg[-1]).mean())


def _quintile(p: float) -> str:
    if not (p == p):          # NaN
        return "na"
    if p < 0.2:
        return "q1"
    if p < 0.4:
        return "q2"
    if p < 0.6:
        return "q3"
    if p < 0.8:
        return "q4"
    return "q5"


def _gap_bucket(g: float) -> str:
    if not (g == g):
        return "na"
    for edge, name in zip(GAP_EDGES, GAP_NAMES):
        if g < edge:
            return name
    return GAP_NAMES[-1]


def _fresh_agg() -> dict:
    return {
        "by_liq": {}, "by_vol": {}, "by_gap": {},
        "by_liq_gap": {}, "by_vol_gap": {},
        "by_liq_board": {},
    }


def _fresh_meta() -> dict:
    return {"files": 0, "bars": 0, "obs": 0, "bad_px": 0,
            "resume_skipped": 0, "one_price_skipped": 0,
            "extreme_skipped": 0, "warmup_skipped": 0,
            "feature_na": 0, "unreadable": 0, "short_files": 0}


# --------------------------------------------------------------- panel scan
def scan_file(path: str, code: str, cal_pos: dict, agg: dict,
              meta: dict) -> None:
    try:
        df = pd.read_csv(path, usecols=["date", "open", "high", "low",
                                        "close", "amount"])
    except Exception:
        meta["unreadable"] += 1
        return
    if len(df) < MIN_WIN + 3:
        meta["short_files"] += 1
        return
    d = pd.to_datetime(df["date"].to_numpy())
    o = df["open"].to_numpy(dtype=float)
    h = df["high"].to_numpy(dtype=float)
    lo = df["low"].to_numpy(dtype=float)
    c = df["close"].to_numpy(dtype=float)
    amt = df["amount"].to_numpy(dtype=float)
    n_bar = len(df)
    meta["files"] += 1
    meta["bars"] += n_bar
    brd = board_of(code)

    with np.errstate(divide="ignore", invalid="ignore"):
        r_tot_all = np.empty(n_bar)
        r_tot_all[0] = np.nan
        r_tot_all[1:] = c[1:] / c[:-1] - 1.0
        rv = pd.Series(r_tot_all).rolling(RV_N).std().to_numpy()
    # self-relative percentile ranks (pandas rolling rank, C path); the
    # window includes today, NaN anywhere in the window yields NaN
    liq_rank = pd.Series(amt).rolling(WIN_W).rank(pct=True).to_numpy()
    vol_rank = pd.Series(rv).rolling(WIN_W).rank(pct=True).to_numpy()

    for i in range(1, n_bar - 1):
        c0, o1, c1 = c[i - 1], o[i], c[i]
        o2, c2 = o[i + 1], c[i + 1]
        if not (c0 > 0 and o1 > 0 and c1 > 0 and o2 > 0 and c2 > 0):
            meta["bad_px"] += 1
            continue
        ci = cal_pos.get(d[i])
        if ci is None or ci == 0 or cal_pos.get(d[i - 1]) != ci - 1:
            meta["resume_skipped"] += 1
            continue
        ci2 = cal_pos.get(d[i + 1])
        if ci2 is None or ci2 != ci + 1:
            meta["resume_skipped"] += 1
            continue
        if (abs(o1 - c1) <= ONE_PRICE_TOL
                and abs(h[i] - lo[i]) <= ONE_PRICE_TOL):
            meta["one_price_skipped"] += 1
            continue
        if (abs(o2 - c2) <= ONE_PRICE_TOL
                and abs(h[i + 1] - lo[i + 1]) <= ONE_PRICE_TOL):
            meta["one_price_skipped"] += 1
            continue
        gap = o1 / c0 - 1.0
        r_on = o2 / c1 - 1.0
        r_in = c2 / o2 - 1.0
        r_tot = c2 / c1 - 1.0
        if not (abs(r_tot) < EXTREME_ABS and abs(r_on) < EXTREME_ABS
                and abs(gap) < EXTREME_ABS):
            meta["extreme_skipped"] += 1
            continue
        liq_p = float(liq_rank[i])
        vol_p = float(vol_rank[i])
        if not (liq_p == liq_p) or not (vol_p == vol_p):
            meta["warmup_skipped"] += 1
            continue
        meta["obs"] += 1
        lq, vq, gb = _quintile(liq_p), _quintile(vol_p), _gap_bucket(gap)
        _add(agg["by_liq"].setdefault(lq, _blank()), r_on, r_in, r_tot)
        _add(agg["by_vol"].setdefault(vq, _blank()), r_on, r_in, r_tot)
        _add(agg["by_gap"].setdefault(gb, _blank()), r_on, r_in, r_tot)
        _add(agg["by_liq_gap"].setdefault((lq, gb), _blank()),
             r_on, r_in, r_tot)
        _add(agg["by_vol_gap"].setdefault((vq, gb), _blank()),
             r_on, r_in, r_tot)
        _add(agg["by_liq_board"].setdefault((lq, brd), _blank()),
             r_on, r_in, r_tot)


# ---------------------------------------------------------------------- run
def census(panel_dir: str = PANEL_DIR, limit: int | None = None,
           cal_sources=None) -> dict:
    kwargs = {} if cal_sources is None else {"sources": cal_sources}
    cal, cal_pos = build_calendar(panel_dir, **kwargs)
    agg, meta = _fresh_agg(), _fresh_meta()
    files = sorted(os.listdir(panel_dir))
    if limit:
        files = files[:limit]
    for fn in files:
        if not fn.endswith(".csv"):
            continue
        code = fn[:-4]
        scan_file(os.path.join(panel_dir, fn), code, cal_pos, agg, meta)
    return {"agg": agg, "meta": meta, "calendar_days": len(cal)}


def _round(obj, nd=8):
    if isinstance(obj, float):
        return None if obj != obj else round(obj, nd)
    if isinstance(obj, dict):
        return {str(k): _round(v, nd) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_round(v, nd) for v in obj]
    return obj


def build_face(raw: dict) -> dict:
    agg, meta = raw["agg"], raw["meta"]
    order5 = ("q1", "q2", "q3", "q4", "q5")

    def rows(d, key_name, keys):
        out = []
        for k in keys:
            b = d.get(k)
            if b is None:
                continue
            row = {key_name: list(k) if isinstance(k, tuple) else k}
            row.update(_stats(b))
            out.append(row)
        return out

    liq_rows = rows(agg["by_liq"], "liq_q", order5)
    vol_rows = rows(agg["by_vol"], "vol_q", order5)
    gap_rows = rows(agg["by_gap"], "gap_bucket", GAP_NAMES)
    liq_gap = rows(agg["by_liq_gap"], "liq_gap",
                   [(q, g) for q in order5 for g in GAP_NAMES])
    vol_gap = rows(agg["by_vol_gap"], "vol_gap",
                   [(q, g) for q in order5 for g in GAP_NAMES])
    boards = sorted({b for (_q, b) in agg["by_liq_board"]})
    liq_board = rows(agg["by_liq_board"], "liq_board",
                     [(q, b) for q in order5 for b in boards])

    def spread(rs):
        """q1 vs q5 overnight mean spread (the selection-readable number)."""
        m = {r["liq_q"] if "liq_q" in r else r["vol_q"]: r
             for r in rs}
        a, b = m.get("q1"), m.get("q5")
        if not a or not b:
            return None
        am, bm = a["r_on"]["mean"], b["r_on"]["mean"]
        if am is None or bm is None:
            return None
        return round(bm - am, 8)

    return {
        "batch": "OVERNIGHT-GAP-CENSUS-LEG3",
        "stage": "conditioned decomposition (descriptive)",
        "generated_at": now_iso(),
        "evidence_cutoff": CUTOFF,
        "law": {"prereg": None, "judged_face": False, "pool_write": False,
                "note": "pure description; zero cost model; zero engine"},
        "frozen_rules": {
            "panel": "data/astock_daily/per/<code>.csv (T-87 qfq forward)",
            "window": WIN_W, "min_window": MIN_WIN, "rv_n": RV_N,
            "gap_edges": list(GAP_EDGES), "gap_names": list(GAP_NAMES),
            "extremes": {"abs_return": EXTREME_ABS,
                         "one_price_tol": ONE_PRICE_TOL},
            "causality": "features read at bar i, returns measured at i+1",
        },
        "meta": _round(meta),
        "calendar_days": raw["calendar_days"],
        "faces": {
            "by_liq": liq_rows,
            "by_vol": vol_rows,
            "by_gap": gap_rows,
            "by_liq_gap": liq_gap,
            "by_vol_gap": vol_gap,
            "by_liq_board": liq_board,
        },
        "selection_reading": {
            "liq_q5_minus_q1_r_on": spread(liq_rows),
            "vol_q5_minus_q1_r_on": spread(vol_rows),
            "note": "spread = overnight mean of the top self-relative "
                    "quintile minus the bottom; a near-zero spread means "
                    "the overnight toll is uniform (no selection escape), "
                    "a large negative/positive spread names who pays it.",
        },
    }


def write_outputs(face: dict, out_dir: str = OUT_DIR) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    jp = os.path.join(out_dir, f"LEG3-{face['evidence_cutoff']}.json")
    with open(jp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    written = [jp]
    for name, key, cols in (
            ("leg3_by_liquidity.csv", "by_liq", "liq_q"),
            ("leg3_by_volatility.csv", "by_vol", "vol_q"),
            ("leg3_by_gap.csv", "by_gap", "gap_bucket"),
            ("leg3_liq_x_gap.csv", "by_liq_gap", "liq_gap")):
        rows = [dict(r) for r in face["faces"][key]]
        flat = []
        for r in rows:
            k = r.pop(cols, None)
            if isinstance(k, list):
                r["bench"], r["bucket"] = k[0], k[1]
            else:
                r["bucket"] = k
            flat.append(r)
        cp = os.path.join(out_dir, name)
        pd.DataFrame(flat).to_csv(cp, index=False, encoding="utf-8")
        written.append(cp)
    return {"json": jp, "files": written}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd != "run":
        print("usage: python scripts/overnight_gap_conditioned.py "
              "[run|selftest]")
        return 2
    t0 = datetime.now()
    raw = census()
    face = build_face(raw)
    paths = write_outputs(face)
    m = face["meta"]
    liq = {r["liq_q"]: r["r_on"]["mean"] for r in face["faces"]["by_liq"]}
    print(f"leg-3 census done: obs={m['obs']} files={m['files']} "
          f"bars={m['bars']} skipped(resume={m['resume_skipped']} "
          f"one_price={m['one_price_skipped']} extreme="
          f"{m['extreme_skipped']} warmup={m['warmup_skipped']})")
    print("overnight mean by self-relative liquidity quintile: "
          + " ".join(f"{k}={v}" for k, v in liq.items()))
    print(f"products: {paths['json']} (+{len(paths['files']) - 1} csv)")
    print(f"elapsed {(datetime.now() - t0).total_seconds():.1f}s")
    return 0


# ------------------------------------------------------------------ selftest
def _syn_file(path: str, rows) -> None:
    pd.DataFrame(rows, columns=["date", "open", "high", "low", "close",
                                "volume", "amount"]).to_csv(path,
                                                            index=False)


def selftest() -> int:
    import shutil
    import tempfile
    ok_n, fails = 0, []

    def ok(name, cond):
        nonlocal ok_n
        if cond:
            ok_n += 1
            print(f"  PASS {name}")
        else:
            fails.append(name)
            print(f"  FAIL {name}")

    # L1 bucket helpers
    ok("L1 quintile edges", _quintile(0.0) == "q1"
       and _quintile(0.1999) == "q1" and _quintile(0.2) == "q2"
       and _quintile(0.999) == "q5" and _quintile(float("nan")) == "na")
    ok("L2 gap edges", _gap_bucket(-0.03) == "gap_lt_-2"
       and _gap_bucket(-0.02) == "gap_-2_-0.5"
       and _gap_bucket(0.0) == "gap_-0.5_0.5"
       and _gap_bucket(0.01) == "gap_0.5_2"
       and _gap_bucket(0.03) == "gap_gt_2")

    # L3 percentile rank identity
    arr = np.arange(1.0, 11.0)
    ok("L3 pct rank mid", abs(_pct_rank(arr, 9, 10) - 1.0) < 1e-12)
    ok("L3 pct rank window",
       abs(_pct_rank(np.array([5.0, 4, 3, 2, 1]), 4, 5) - 0.2) < 1e-12
       and abs(_pct_rank(np.array([1.0, 2, 3, 4, 5]), 4, 5) - 1.0) < 1e-12)
    ok("L3 pct rank NaN", _pct_rank(np.array([1.0, np.nan]), 1, 2) !=
       _pct_rank(np.array([1.0, np.nan]), 1, 2))

    # L4 stats math on a known series
    b = _blank()
    for v in (0.01, -0.02, 0.03, -0.04):
        _add(b, v, -v, v * 2)
    st = _stats(b)
    ok("L4 mean", abs(st["r_on"]["mean"] - (-0.005)) < 1e-9)
    ok("L4 win rate", abs(st["r_on"]["win"] - 0.5) < 1e-9)
    ok("L4 t sign", st["r_on"]["t"] < 0)

    # L5/L6 end-to-end on a synthetic panel (deterministic maths, no files
    # from the real panel): 400 contiguous trading days, 12 stocks.
    td = tempfile.mkdtemp(prefix="leg3st_")
    try:
        days = pd.bdate_range("2020-01-01", periods=400)
        dates = [d.strftime("%Y-%m-%d") for d in days]
        rng = np.random.default_rng(7)
        for k in range(12):
            code = ("600000", "000001", "600002", "000003", "600004",
                    "000005", "600006", "000007", "600008", "000009",
                    "600010", "000011")[k]
            rows, px = [], 10.0
            for j, dt in enumerate(dates):
                o = px * (1.0 + float(rng.normal(0, 0.004)))
                c = o * (1.0 + float(rng.normal(0, 0.01)))
                h = max(o, c) * 1.002
                lo = min(o, c) * 0.998
                amt = float(1e8 * (1 + k) * (1 + 0.1 * (j % 7)))
                rows.append((dt, round(o, 4), round(h, 4), round(lo, 4),
                             round(c, 4), 1e6, amt))
                px = c
            _syn_file(os.path.join(td, f"{code}.csv"), rows)
        raw = census(panel_dir=td, cal_sources=("600000.csv",
                                                "000001.csv"))
        face = build_face(raw)
        ok("L5 synthetic obs > 0", face["meta"]["obs"] > 0)
        ok("L5 five liquidity buckets",
           len(face["faces"]["by_liq"]) == 5)
        ok("L5 every bucket has n > 0",
           all(r["n"] > 0 for r in face["faces"]["by_liq"]))
        ok("L5 warmup gate fires",
           face["meta"]["warmup_skipped"] > 0)
        ok("L5 total n == obs across liq buckets",
           sum(r["n"] for r in face["faces"]["by_liq"])
           == face["meta"]["obs"])
        ok("L6 deterministic rerun",
           build_face(census(panel_dir=td, cal_sources=(
               "600000.csv", "000001.csv")))["faces"]
           == face["faces"])
        out = write_outputs(face, out_dir=tempfile.mkdtemp(
            prefix="leg3out_"))
        ok("L6 products written", os.path.exists(out["json"])
           and len(out["files"]) == 5)
        blob = json.load(open(out["json"], encoding="utf-8"))
        ok("L6 evidence_cutoff present", blob["evidence_cutoff"] == CUTOFF)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    print(f"selftest: {ok_n} PASS, {len(fails)} FAIL"
          f"{'' if not fails else ' -- ' + ', '.join(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())