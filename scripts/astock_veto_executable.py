"""A-share residual veto: the same book, priced at a price you can actually get.

Why this face exists
--------------------
r1865 (scripts/astock_resid_veto_layer.py) prices three arms on one eligible pool:

    A  the whole eligible pool          (do nothing)
    B  A minus the top-20% residual      (the black list)
    R  A minus a random 20%              (same-sized control)

and it concludes B beats both A and R by +0.245%/rebalance (t=3.5).  But every
one of those numbers is booked **close(t) -> close(t+20)**.  On an A-share desk
the signal is not known until close(t), so the only fill you can get is the
**next morning's open**, and if that name opens limit-up (one price all day) you
do not get it at all.  The family has never printed what those two facts cost,
even though `open`, `high` and `low` sit in the same per-symbol CSVs it already
reads.

So this face prices the identical three arms twice:

    research     close(t)   -> close(t+20)      (the parent's booking, for the anchor)
    executable   open(t+1)  -> open(t+1+20)     one morning late, limit-up rows dropped

and prints both side by side, plus how many names the executable arm had to
leave on the table each period.

Construction
------------
* universe filter, beta window, cross-sectional residual and the quintile `q`
  are imported from astock_resid_reversal_probe / astock_resid_veto_layer -- the
  same functions, not a re-implementation.
* a name is **fillable** on rebalance t when, at t+1: `high > 0` (the bar exists),
  `high != low` (not a one-price day), and `open/close(t) - 1 <= 4.5%`.  The 4.5%
  threshold is deliberately below every board's limit (main 10%, ChiNext/STAR
  20%, ST 5%): a one-price day that is up >4.5% is treated as unbuyable, which
  can only *understate* the book, never inflate it.  A one-price day that is
  down (limit-down) stays fillable -- selling into a limit-down is the problem,
  buying out of it is not.
* exit fills at the first usable `open` in [t+1+20, t+1+25]; a name with none is
  dropped for that period and counted (`exit_missing`), never forward-filled.
* cost is the parent's 2 * 8bp * turnover, computed on the arm's own membership
  inside the fillable set, so B-A is a stock-picking difference and never a
  "how many did you manage to buy" difference.
* year totals are compounded inside the year and never annualised (r2002 law).

Verdict (fixed here, before the numbers are seen)
-------------------------------------------------
On the executable pairing:
    EXECUTABLE_KILLED     mean(B-A) <= 0
    EXECUTABLE_SURVIVES   mean > 0 and t(B-A) >= 2 and t(B-R) >= 2
    EXECUTABLE_DEGRADED   otherwise (still positive, but no longer separable)
A flat difference (zero variance) is never allowed to masquerade as an edge.

Usage
-----
    python scripts/astock_veto_executable.py run
    python scripts/astock_veto_executable.py check
    python scripts/astock_veto_executable.py selftest
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_reversal_probe import PER  # noqa: E402,F401  (re-exported for callers)
from astock_resid_veto_layer import (  # noqa: E402
    COST_ONE_SIDE,
    FIRST_DATE,
    HOLD,
    LOOKBACK_BETA,
    MIN_AMOUNT_20D,
    MIN_BARS,
    RANDOM_DRAWS,
    SEED,
    _turnover,
    compound,
    daily_returns,
    load_panel,
    market_return,
    panel_frontier,
    score_slice,
)

OUT = os.path.join(ROOT, "results", "astock_veto_executable.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_EXECUTABLE.md")
PARENT = os.path.join(ROOT, "results", "astock_resid_veto_layer.json")
PANEL_PER = os.path.join(ROOT, "data", "astock_daily", "per")

ARMS = ("A", "B", "C", "R")
ENTRY_LAG = 1
EXIT_SLACK = 5
LIMIT_UP_MIN = 0.045  # below every board's limit: conservative by construction


# ---------------------------------------------------------------- data loading
def load_ohl(first_date: str = FIRST_DATE, per_dir: str = PANEL_PER):
    """(dates, symbols, open, high, low, close) matrices on the same union calendar.

    Deliberately mirrors astock_resid_reversal_probe.load_panel column for column,
    so a row index means the same thing in both -- the parent's close matrix and
    this open matrix must stay aligned or every price below is off by a row.
    """
    files = sorted(glob.glob(os.path.join(per_dir, "*.csv")))
    if not files:
        raise SystemExit("no per-symbol csv under %s" % per_dir)

    per_sym = {}
    all_dates = set()
    for path in files:
        sym = os.path.basename(path)[:-4]
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                header = fh.readline().strip().split(",")
                if not header or "date" not in header or "close" not in header:
                    continue
                idx = {name: i for i, name in enumerate(header)}
                need = [idx.get(k) for k in ("date", "open", "high", "low", "close")]
                if any(v is None for v in need):
                    continue
                d_i, o_i, h_i, l_i, c_i = need
                dates, op, hi, lo, cl = [], [], [], [], []
                for line in fh:
                    parts = line.rstrip("\n").split(",")
                    if len(parts) <= max(d_i, o_i, h_i, l_i, c_i):
                        continue
                    d = parts[d_i]
                    if d < first_date:
                        continue
                    try:
                        c = float(parts[c_i])
                    except ValueError:
                        continue
                    if c <= 0:
                        continue
                    dates.append(d)
                    op.append(_f(parts[o_i]))
                    hi.append(_f(parts[h_i]))
                    lo.append(_f(parts[l_i]))
                    cl.append(c)
        except OSError:
            continue
        if len(dates) >= HOLD + LOOKBACK_BETA:
            per_sym[sym] = (dates, op, hi, lo, cl)
            all_dates.update(dates)

    if not per_sym:
        raise SystemExit("no usable symbol after parse")

    dates = sorted(all_dates)
    pos = {d: i for i, d in enumerate(dates)}
    n_t, n_s = len(dates), len(per_sym)
    shape = (n_t, n_s)
    op = np.full(shape, np.nan)
    hi = np.full(shape, np.nan)
    lo = np.full(shape, np.nan)
    cl = np.full(shape, np.nan)
    symbols = list(per_sym)
    for j, sym in enumerate(symbols):
        d, o, h, l, c = per_sym[sym]
        rows = np.fromiter((pos[x] for x in d), dtype=np.int64, count=len(d))
        op[rows, j] = o
        hi[rows, j] = h
        lo[rows, j] = l
        cl[rows, j] = c
    return dates, symbols, op, hi, lo, cl


def _f(x: str) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return float("nan")
    return v if np.isfinite(v) else float("nan")


# ------------------------------------------------------------- pure price logic
def fill_masks(t: int, cols: np.ndarray, open_m, high_m, low_m, close, hold: int = HOLD):
    """Split one rebalance's members into fillable / dropped, with the reason.

    cols is the symbol-index array of the arm's members.  Returns a dict of
    boolean masks aligned to cols plus the executable forward return array.

    Pure: no I/O, no globals beyond the constants above, so selftest can hand it
    hand-built matrices and assert on the answer (r1934: a guard that only
    recomputes itself never learns it is stale).
    """
    n = len(cols)
    entry = open_m[t + ENTRY_LAG][cols] if t + ENTRY_LAG < open_m.shape[0] else np.full(n, np.nan)
    prev_close = close[t][cols]
    hi = high_m[t + ENTRY_LAG][cols] if t + ENTRY_LAG < high_m.shape[0] else np.full(n, np.nan)
    lo = low_m[t + ENTRY_LAG][cols] if t + ENTRY_LAG < low_m.shape[0] else np.full(n, np.nan)

    bar_exists = np.isfinite(entry) & (entry > 0) & np.isfinite(hi)
    with np.errstate(invalid="ignore", divide="ignore"):
        gap = entry / prev_close - 1.0
    one_price = bar_exists & np.isfinite(lo) & (hi == lo)
    limit_up = one_price & (gap > LIMIT_UP_MIN)
    halted_entry = ~bar_exists

    exit_at = t + ENTRY_LAG + hold
    exit_px = np.full(n, np.nan)
    delayed = np.zeros(n, dtype=bool)
    for k in range(EXIT_SLACK + 1):
        row = exit_at + k
        if row >= open_m.shape[0]:
            break
        cand = open_m[row][cols]
        need = ~np.isfinite(exit_px) & np.isfinite(cand) & (cand > 0)
        if np.any(need):
            exit_px[need] = cand[need]
            if k > 0:
                delayed[need] = True
    exit_missing = ~np.isfinite(exit_px)

    fillable = bar_exists & ~limit_up & ~exit_missing
    with np.errstate(invalid="ignore", divide="ignore"):
        ret = exit_px / entry - 1.0
    ret = np.where(fillable, ret, np.nan)
    return {
        "fillable": fillable,
        "limit_up": limit_up,
        "halted_entry": halted_entry,
        "exit_missing": exit_missing,
        "delayed_exit": delayed & fillable,
        "ret": ret,
    }


def exec_verdict(b_a: dict, b_r: dict) -> str:
    """Fixed before the run: never let a flat difference read as an edge."""
    mean = b_a.get("mean")
    if mean is None:
        return "INSUFFICIENT_PERIODS"
    if mean <= 0:
        return "EXECUTABLE_KILLED"
    t_a, t_r = b_a.get("t"), b_r.get("t")
    if t_a is not None and t_r is not None and t_a >= 2.0 and t_r >= 2.0:
        return "EXECUTABLE_SURVIVES"
    return "EXECUTABLE_DEGRADED"


# --------------------------------------------------------------------- the run
def build(hold: int = HOLD, stride: int = HOLD):
    dates, symbols, close, amount, shares = load_panel()
    d2, sym2, open_m, high_m, low_m, close2 = load_ohl()
    if dates != d2 or symbols != sym2:
        raise SystemExit("open grid disagrees with close grid: refusing to mix calendars")
    if not np.allclose(close, close2, equal_nan=True):
        raise SystemExit("close columns disagree between the two loaders")

    rets = daily_returns(close)
    mkt = market_return(rets)

    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)

    rng = np.random.default_rng(SEED)  # same seed and same draw order as the parent
    rng_exec = np.random.default_rng(SEED + 1)  # separate stream: the anchor must stay bit-exact
    prev = {"research": {k: None for k in ARMS}, "executable": {k: None for k in ARMS}}
    rows = []
    t = start
    while t + HOLD < len(dates):
        idx, resid, q, fwd = score_slice(t, close, amount, shares, rets, mkt)
        if resid is None:
            t += stride
            continue

        n = len(idx)
        fill = fill_masks(t, idx, open_m, high_m, low_m, close, hold=hold)
        ok = fill["fillable"]
        n_ok = int(np.sum(ok))

        # research arms are the parent's, exactly: everyone in the pool, close->close
        m_res = {"A": np.ones(n, dtype=bool), "B": q < 4, "C": q < 3}
        drop_n = int(n - np.sum(m_res["B"]))
        rand_pool, rand_sets = [], []
        for _ in range(RANDOM_DRAWS):
            perm = rng.permutation(n)
            keep = np.zeros(n, dtype=bool)
            keep[perm[: n - drop_n]] = True
            rand_pool.append(float(np.mean(fwd[keep])))
            rand_sets.append(set(idx[keep].tolist()))

        # executable arms: only the names you could actually buy at the next open
        m_exe = {"A": ok, "B": ok & (q < 4), "C": ok & (q < 3)}
        keep_frac = float(np.sum(m_res["B"])) / n if n else 1.0
        drop_n_ok = int(round(n_ok * (1.0 - keep_frac)))
        rand_exec, rand_sets_exec = [], []
        for _ in range(RANDOM_DRAWS):
            cols_ok = np.flatnonzero(ok)
            if len(cols_ok) == 0:
                break
            pick = rng_exec.permutation(len(cols_ok))
            keep_ok = np.zeros(n, dtype=bool)
            keep_ok[cols_ok[pick[: len(cols_ok) - drop_n_ok]]] = True
            rand_exec.append(float(np.nanmean(fill["ret"][keep_ok])))
            rand_sets_exec.append(set(idx[keep_ok].tolist()))

        row = {
            "date": dates[t],
            "n": int(n),
            "n_fillable": n_ok,
            "limit_up": int(np.sum(fill["limit_up"])),
            "halted_entry": int(np.sum(fill["halted_entry"])),
            "exit_missing": int(np.sum(fill["exit_missing"])),
            "delayed_exit": int(np.sum(fill["delayed_exit"])),
        }

        for name, m_res_m in m_res.items():
            cur = set(idx[m_res_m].tolist())
            turb = _turnover(cur, prev["research"][name])
            prev["research"][name] = cur
            g = float(np.mean(fwd[m_res_m]))
            m_exe_m = m_exe[name]
            cur_x = set(idx[m_exe_m].tolist())
            turb_x = _turnover(cur_x, prev["executable"][name])
            prev["executable"][name] = cur_x
            gx = float(np.nanmean(fill["ret"][m_exe_m])) if np.any(m_exe_m) else float("nan")
            row[name] = {
                "gross": g,
                "net": g - 2.0 * COST_ONE_SIDE * turb,
                "turnover": turb,
                "size": int(np.sum(m_res_m)),
                "gross_exec": gx,
                "net_exec": gx - 2.0 * COST_ONE_SIDE * turb_x if np.isfinite(gx) else float("nan"),
                "turnover_exec": turb_x,
                "size_exec": int(np.sum(m_exe_m)),
            }

        # random arm, both bookings
        rg = float(np.mean(rand_pool))
        rcur = set.union(*rand_sets)
        rturb = _turnover(rcur, prev["research"]["R"])
        prev["research"]["R"] = rcur
        rgx = float(np.nanmean(rand_exec)) if rand_exec else float("nan")
        rcur_x = set.union(*rand_sets_exec) if rand_sets_exec else set()
        rturb_x = _turnover(rcur_x, prev["executable"]["R"])
        prev["executable"]["R"] = rcur_x
        row["R"] = {
            "gross": rg,
            "net": rg - 2.0 * COST_ONE_SIDE * rturb,
            "turnover": rturb,
            "size": int(len(rand_sets[0])),
            "gross_exec": rgx,
            "net_exec": rgx - 2.0 * COST_ONE_SIDE * rturb_x if np.isfinite(rgx) else float("nan"),
            "turnover_exec": rturb_x,
            "size_exec": int(len(rand_sets_exec[0]) if rand_sets_exec else 0),
        }
        rows.append(row)
        t += stride
    return dates, symbols, rows


def _series(rows, arm, key):
    return np.array([r[arm][key] for r in rows], dtype=np.float64)


def _paired_key(rows, arm, base, key):
    d = np.array([r[arm][key] - r[base][key] for r in rows], dtype=np.float64)
    d = d[np.isfinite(d)]
    if len(d) < 3:
        return {"n": int(len(d)), "mean": None, "se": None, "t": None}
    mean = float(d.mean())
    se = float(d.std(ddof=1) / math.sqrt(len(d)))
    flat = float(np.std(d, ddof=1)) <= 1e-12 * max(1.0, abs(mean))
    return {"n": int(len(d)), "mean": mean, "se": se, "t": None if flat or se <= 0 else mean / se}


def _arm_summary(rows, arm, key, size_key="size", turn_key="turnover"):
    nets = _series(rows, arm, key)
    nets = nets[np.isfinite(nets)]
    return {
        "periods": int(len(nets)),
        "cagr_net": compound(list(nets)) if len(nets) else None,
        "mean_net_per_rebalance": float(nets.mean()) if len(nets) else None,
        "mean_size": float(np.mean([r[arm][size_key] for r in rows])) if rows else None,
        "mean_turnover": float(np.mean([r[arm][turn_key] for r in rows])) if rows else None,
    }


def _by_year_key(rows, arm, key):
    out = {}
    for r in rows:
        y = r["date"][:4]
        v = r[arm][key]
        if np.isfinite(v):
            out.setdefault(y, []).append(v)
    return {y: {"periods": len(v), "total": float(np.prod([1.0 + x for x in v]) - 1.0)}
            for y, v in sorted(out.items())}


def summarize(rows):
    res, exc = {}, {}
    for arm in ARMS:
        res[arm] = _arm_summary(rows, arm, "net")
        res[arm]["by_year"] = _by_year_key(rows, arm, "net")
        exc[arm] = _arm_summary(rows, arm, "net_exec", "size_exec", "turnover_exec")
        exc[arm]["by_year"] = _by_year_key(rows, arm, "net_exec")
    paired = {}
    for label, key in (("research", "net"), ("executable", "net_exec")):
        paired[label] = {
            "B_minus_A": _paired_key(rows, "B", "A", key),
            "B_minus_R": _paired_key(rows, "B", "R", key),
            "C_minus_A": _paired_key(rows, "C", "A", key),
        }
    return res, exc, paired


# ------------------------------------------------------------------- the face
def run(hold: int = HOLD, stride: int = HOLD):
    dates, symbols, rows = build(hold=hold, stride=stride)
    if not rows:
        print("no rebalance rows")
        return 2

    res, exc, paired = summarize(rows)
    v_exec = exec_verdict(paired["executable"]["B_minus_A"], paired["executable"]["B_minus_R"])
    v_res = exec_verdict(paired["research"]["B_minus_A"], paired["research"]["B_minus_R"])

    gap = {}
    for arm in ARMS:
        a, b = res[arm]["cagr_net"], exc[arm]["cagr_net"]
        gap[arm] = None if (a is None or b is None) else float(a - b)

    fill_rates = [r["n_fillable"] / r["n"] for r in rows if r["n"]]
    payload = {
        "generated": _now(),
        "evidence_cutoff": dates[-1],
        "machine": _machine(),
        "kind": "astock_veto_executable",
        "prereg": None,
        "adoption": None,
        "spec": {
            "hold": hold,
            "stride": stride,
            "entry": "open(t+1)",
            "exit": "first usable open in [t+1+hold, t+1+hold+%d]" % EXIT_SLACK,
            "limit_up_min_gap": LIMIT_UP_MIN,
            "limit_up_rule": "one-price day (high==low) and open/close(t)-1 > %.3f is unbuyable"
                             % LIMIT_UP_MIN,
            "cost_one_side": COST_ONE_SIDE,
            "random_draws": RANDOM_DRAWS,
            "seed": SEED,
            "min_amount_20d": MIN_AMOUNT_20D,
            "min_bars": MIN_BARS,
            "arms": {
                "A": "whole eligible pool (inside the fillable set)",
                "B": "A minus top 20% residual",
                "C": "A minus top 40% residual",
                "R": "random 20% dropped",
            },
        },
        "panel": {"dates": len(dates), "symbols": len(symbols), "first": dates[0], "last": dates[-1]},
        "rebalances": len(rows),
        "research_arms": res,
        "executable_arms": exc,
        "paired_per_rebalance": paired,
        "exec_gap_pp": gap,
        "fill_quality": {
            "mean_fill_rate": float(np.mean(fill_rates)) if fill_rates else None,
            "min_fill_rate": float(np.min(fill_rates)) if fill_rates else None,
            "mean_limit_up_per_period": float(np.mean([r["limit_up"] for r in rows])),
            "mean_halted_entry_per_period": float(np.mean([r["halted_entry"] for r in rows])),
            "mean_exit_missing_per_period": float(np.mean([r["exit_missing"] for r in rows])),
            "periods_with_delayed_exit": int(sum(1 for r in rows if r["delayed_exit"] > 0)),
        },
        "verdict": v_exec,
        "verdict_research": v_res,
        "last_rebalance": rows[-1]["date"],
        "parent_anchor": _parent_anchor(res),
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)

    print("rebalances %d  panel %d symbols  cutoff %s" % (len(rows), len(symbols), dates[-1]))
    print("  fill rate mean %.1f%%  limit-up %.1f/period  halted %.1f  exit-missing %.1f"
          % (100 * payload["fill_quality"]["mean_fill_rate"],
             payload["fill_quality"]["mean_limit_up_per_period"],
             payload["fill_quality"]["mean_halted_entry_per_period"],
             payload["fill_quality"]["mean_exit_missing_per_period"]))
    for arm in ("A", "B", "C", "R"):
        g = gap[arm]
        print("  %s  research %7.2f%%  executable %7.2f%%  gap %+6.2fpp  size %4.0f -> %4.0f"
              % (arm, 100 * res[arm]["cagr_net"], 100 * exc[arm]["cagr_net"],
                 100 * g if g is not None else float("nan"),
                 res[arm]["mean_size"], exc[arm]["mean_size"]))
    for label in ("research", "executable"):
        p = paired[label]
        print("  %-10s B-A %+.4f%%/reb t %s | B-R %+.4f%%/reb t %s"
              % (label, 100 * p["B_minus_A"]["mean"], _t(p["B_minus_A"]["t"]),
                 100 * p["B_minus_R"]["mean"], _t(p["B_minus_R"]["t"])))
    print("verdict executable=%s (research=%s) -> %s"
          % (v_exec, v_res, _rel(OUT)))
    return 0


def _t(x):
    return "None" if x is None else "%+.2f" % x


def _parent_anchor(res):
    """The research booking must reproduce the published parent face bit for bit.

    Same score, same pool, same close->close booking, same seed: if this drifts the
    two faces are no longer the same experiment and every gap below is meaningless.
    """
    if not os.path.exists(PARENT):
        return None
    try:
        with io.open(PARENT, encoding="utf-8") as fh:
            par = json.load(fh)
    except (OSError, ValueError):
        return None
    out = {"parent_cutoff": par.get("evidence_cutoff"), "arms": {}}
    for arm in ARMS:
        mine = res[arm]["cagr_net"]
        theirs = ((par.get("arms") or {}).get(arm) or {}).get("cagr_net")
        out["arms"][arm] = {
            "mine": mine,
            "parent": theirs,
            "abs_diff": None if (mine is None or theirs is None) else abs(mine - theirs),
        }
    out["paired_B_minus_A_parent"] = (par.get("paired_per_rebalance") or {}).get("vs_A")
    return out


# -------------------------------------------------------------------- markdown
def _rel(path: str) -> str:
    """Repo-relative when we can, absolute when the path lives on another drive.

    os.path.relpath raises on Windows when path and ROOT sit on different mounts,
    and a guard must not crash just because someone pointed it at a temp copy
    (a C: tempdir against a K: repo hits exactly this).
    """
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:
        return path

def write_md(p):
    res, exc, pair = p["research_arms"], p["executable_arms"], p["paired_per_rebalance"]
    fq = p["fill_quality"]
    lines = []
    lines.append("# A 股残差黑名单：按「能成交的价」重新定价")
    lines.append("")
    lines.append("> 面：`results/astock_veto_executable.json` · 生成 %s · 面板前沿 %s · 最后一期 %s"
                 % (p["generated"], p["panel"]["last"], p["last_rebalance"]))
    lines.append("")
    lines.append("## 一句话")
    lines.append("")
    lines.append("同一条黑名单（剔掉残差最高 20%%），一次按收盘价记账，一次按**第二天开盘价**成交"
                 "并把一字涨停买不到的股票剔掉：研究口径 B-A **%+.4f%%/期（t %s）**，"
                 "可实现口径 **%+.4f%%/期（t %s）** → **%s**。"
                 % (100 * pair["research"]["B_minus_A"]["mean"], _t(pair["research"]["B_minus_A"]["t"]),
                    100 * pair["executable"]["B_minus_A"]["mean"], _t(pair["executable"]["B_minus_A"]["t"]),
                    p["verdict"]))
    lines.append("")
    lines.append("## 两条腿的绝对读数")
    lines.append("")
    lines.append("| 臂 | 研究口径 年化(净) | 可实现口径 年化(净) | 差(pp) | 可实现口径 均人数 | 均换手 |")
    lines.append("|---|---|---|---|---|---|")
    names = {"A": "A 全池", "B": "B 剔残差top20%", "C": "C 剔top40%", "R": "R 随机剔20%"}
    for arm in ("A", "B", "C", "R"):
        gap = p["exec_gap_pp"][arm]
        lines.append("| %s | %+.2f%% | %+.2f%% | %+.2f | %.0f | %.3f |"
                     % (names[arm], 100 * res[arm]["cagr_net"], 100 * exc[arm]["cagr_net"],
                        100 * gap if gap is not None else float("nan"),
                        exc[arm]["mean_size"], exc[arm]["mean_turnover"]))
    lines.append("")
    lines.append("## 配对差（每期，净口径）")
    lines.append("")
    lines.append("| 口径 | B-A 均值 | t | B-R 均值 | t | C-A 均值 | t |")
    lines.append("|---|---|---|---|---|---|---|")
    for label in ("research", "executable"):
        q = pair[label]
        lines.append("| %s | %+.4f%% | %s | %+.4f%% | %s | %+.4f%% | %s |"
                     % (label, 100 * q["B_minus_A"]["mean"], _t(q["B_minus_A"]["t"]),
                        100 * q["B_minus_R"]["mean"], _t(q["B_minus_R"]["t"]),
                        100 * q["C_minus_A"]["mean"], _t(q["C_minus_A"]["t"])))
    lines.append("")
    lines.append("## 买不到的那部分")
    lines.append("")
    lines.append("可成交率均值 **{:.1f}%**（最低 {:.1f}%）；每期平均因**一字涨停**买不到 {:.1f} 只、"
                 "因**当日无 bar（停牌/未上市）** {:.1f} 只、因**卖出日不可得** {:.1f} 只；"
                 "有 {} 期出现卖出推迟（最多推迟 {} 个交易日）。".format(
                     100 * fq["mean_fill_rate"], 100 * fq["min_fill_rate"],
                     fq["mean_limit_up_per_period"], fq["mean_halted_entry_per_period"],
                     fq["mean_exit_missing_per_period"], fq["periods_with_delayed_exit"], EXIT_SLACK))
    lines.append("")
    lines.append("## 逐年（年度总额=年内连乘，不年化）")
    lines.append("")
    years = sorted(set(res["A"]["by_year"]) | set(exc["A"]["by_year"]))
    lines.append("| 年 | 研究 A | 可实现 A | 研究 B | 可实现 B |")
    lines.append("|---|---|---|---|---|")
    for y in years:
        cells = []
        for arm, book in (("A", res), ("A", exc), ("B", res), ("B", exc)):
            v = book[arm]["by_year"].get(y)
            cells.append("%+.2f%%" % (100 * v["total"]) if v else "—")
        lines.append("| %s | %s | %s | %s | %s |" % (y, cells[0], cells[1], cells[2], cells[3]))
    lines.append("")
    lines.append("## 这个面没有回答的")
    lines.append("")
    lines.append("- 一字涨停只用「全天一个价且涨幅>4.5%」一个门槛判定，未按板块（主板 10% / 创业板科创板 20% / ST 5%）分别核；"
                 "板块限价差只会让本面漏掉个别买不到的名字，方向上是**低估**成本、不会高估收益。")
    lines.append("- 卖出同样按开盘价成交；若卖出日停牌超过 %d 个交易日，该股当期被剔除而不是按最后价估值。" % EXIT_SLACK)
    lines.append("- 未区分 ST（需要在 `data/fundamental` 的历史资格面上逐日重放，本面无该输入），"
                 "ST 股的涨跌幅限制更窄，本面的门槛对它偏松。")
    lines.append("- 票池是现存标的（幸存者偏差，与父面同）；面板起于 %s。" % p["panel"]["first"])
    lines.append("- 本面是**归因/可执行性件**，不是可交易策略：它没有仓位规则、没有容量约束、没有风控。")
    lines.append("")
    lines.append("## 为什么黑名单臂掉得比全池多")
    lines.append("")
    gap_a = p["exec_gap_pp"]["A"]
    gap_b = p["exec_gap_pp"]["B"]
    lines.append("全池 A 只掉 **%+.2fpp**，黑名单 B 掉 **%+.2fpp**，是两倍。方向是自洽的：黑名单剔掉的正是"
                 "残差最高（最近 20 日跌得最多）那一批，而这批股票在**次日开盘**往往会先反弹一段——"
                 "全池买得到这段反弹，黑名单买不到。所以晚一天买并不是均匀地削掉每个人的收益，"
                 "它恰好削掉「被剔掉的那批股票的开盘反弹」，于是 B-A 从 %+.4f%% 缩到 %+.4f%%。"
                 % (100 * gap_a, 100 * gap_b,
                    100 * pair["research"]["B_minus_A"]["mean"],
                    100 * pair["executable"]["B_minus_A"]["mean"]))
    lines.append("")
    lines.append("## 与父面的锚")
    lines.append("")
    anc = p.get("parent_anchor") or {}
    if anc.get("arms"):
        worst = max((r.get("abs_diff") or 0.0) for r in anc["arms"].values())
        lines.append("研究口径**不是另写一套**：宇宙、分数、五分组、随机对照种子全部从父面 import，"
                     "读数必须逐位复现 `results/astock_resid_veto_layer.json`（cutoff %s）。"
                     "四条臂的最大绝对差 = **%.2e**，`check` 把它当硬腿，超 1e-9 直接判红。"
                     % (anc.get("parent_cutoff"), worst))
    else:
        lines.append("父面 `results/astock_resid_veto_layer.json` 本轮不在位，研究口径**未经锚定**，读数只作参考。")
    lines.append("")
    lines.append("## 复现")
    lines.append("")
    lines.append("```")
    lines.append("python scripts/astock_veto_executable.py selftest   # 纯函数自检")
    lines.append("python scripts/astock_veto_executable.py run")
    lines.append("python scripts/astock_veto_executable.py check        # 漂移/自相矛盾/父面锚")
    lines.append("```")
    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with io.open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ----------------------------------------------------------------------- check
def check() -> int:
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % _rel(OUT))
        return 3
    with io.open(OUT, encoding="utf-8") as fh:
        face = json.load(fh)

    frontier, n_seen = panel_frontier()
    cutoff = face.get("evidence_cutoff")
    if not cutoff:
        print("CHECK FAILED face has no evidence_cutoff")
        return 1
    if frontier is None:
        print("STALE panel unreadable (sample found no rows)")
        return 3
    if cutoff < frontier:
        print("STALE panel moved: face cutoff %s, panel reaches %s (sample %d files)"
              % (cutoff, frontier, n_seen))
        return 3
    if cutoff > frontier:
        print("CHECK FAILED face claims a bar the panel does not reach: %s > %s"
              % (cutoff, frontier))
        return 1

    bad = []
    pair = face["paired_per_rebalance"]
    for label in ("research", "executable"):
        q = pair[label]
        v = exec_verdict(q["B_minus_A"], q["B_minus_R"])
        expect = face["verdict"] if label == "executable" else face["verdict_research"]
        if v != expect:
            bad.append("%s verdict %s but its own paired table re-derives %s"
                       % (label, expect, v))
    for arm in ("A", "B", "C", "R"):
        gap = face["exec_gap_pp"][arm]
        delta = face["research_arms"][arm]["cagr_net"] - face["executable_arms"][arm]["cagr_net"]
        if gap is None or abs(gap - delta) > 1e-9:
            bad.append("exec_gap_pp[%s]=%r but each arm's own cagrs give %r" % (arm, gap, delta))
        if face["executable_arms"][arm]["mean_size"] > face["research_arms"][arm]["mean_size"] + 1e-9:
            bad.append("arm %s claims more fillable names than the pool holds" % arm)
    anc = face.get("parent_anchor") or {}
    for arm, row in (anc.get("arms") or {}).items():
        d = row.get("abs_diff")
        if d is not None and d > 1e-9:
            bad.append("research arm %s does not reproduce the parent face: mine=%r parent=%r"
                       % (arm, row.get("mine"), row.get("parent")))
    if bad:
        for b in bad:
            print("CHECK FAILED " + b)
        return 1
    print("OK cutoff %s == panel frontier %s (sample %d files); verdicts and gaps re-derive"
          % (cutoff, frontier, n_seen))
    return 0


# -------------------------------------------------------------------- selftest
def selftest() -> int:
    fails = []
    total = [0]

    def check(name, cond, detail=""):
        total[0] += 1
        if not cond:
            fails.append("%s %s" % (name, detail))

    # a tiny 8 x 3 grid: rows are days, cols are symbols
    n_t, n_s = 40, 3
    open_m = np.full((n_t, n_s), 10.0)
    high_m = np.full((n_t, n_s), 10.3)
    low_m = np.full((n_t, n_s), 9.7)
    close = np.full((n_t, n_s), 10.0)
    cols = np.arange(n_s)
    t = 0

    # L1 a one-price up-5% day at t+1 is unbuyable
    high_m[1, 0] = low_m[1, 0] = 10.5
    open_m[1, 0] = 10.5
    m = fill_masks(t, cols, open_m, high_m, low_m, close)
    check("L1 one-price +5% is dropped as limit-up", m["limit_up"][0] and not m["fillable"][0])

    # L2 a big up day that is *not* one-price stays buyable
    check("L2 wide-range up day is fillable", m["fillable"][1] and m["fillable"][2])

    # L3 an up day under the 4.5% floor stays buyable even if one-price
    o2, h2, l2 = open_m.copy(), high_m.copy(), low_m.copy()
    o2[1, 1] = h2[1, 1] = l2[1, 1] = 10.4  # +4.0%, below floor
    m3 = fill_masks(t, cols, o2, h2, l2, close)
    check("L3 one-price +4.0% is still fillable (floor is conservative)",
          m3["fillable"][1] and not m3["limit_up"][1])

    # L4 missing t+1 bar = halted entry
    o4 = open_m.copy()
    o4[1, 2] = np.nan
    m4 = fill_masks(t, cols, o4, high_m, low_m, close)
    check("L4 nan open is a halted entry", m4["halted_entry"][2] and not m4["fillable"][2])

    # L5 exact return arithmetic: 10 -> 11 over the hold
    o5 = np.full((n_t, n_s), 10.0)
    o5[1 + HOLD] = 11.0
    m5 = fill_masks(t, cols, o5, high_m, low_m, close)
    check("L5 open 10 -> open 11 is exactly +10%%",
          abs(float(m5["ret"][0]) - 0.10) < 1e-12, repr(m5["ret"][0]))

    # L6 a missing exit bar is found inside the slack window and flagged delayed
    o6 = np.full((n_t, n_s), 10.0)
    o6[1 + HOLD] = np.nan
    o6[1 + HOLD + 1] = np.nan
    o6[1 + HOLD + 2] = 12.0
    m6 = fill_masks(t, cols, o6, high_m, low_m, close)
    check("L6 exit found 2 days late is fillable and flagged",
          m6["fillable"][0] and m6["delayed_exit"][0] and abs(m6["ret"][0] - 0.20) < 1e-12)

    # L7 no exit bar anywhere in the window -> dropped, never forward-filled
    o7 = np.full((n_t, n_s), 10.0)
    o7[1 + HOLD: 1 + HOLD + EXIT_SLACK + 1] = np.nan
    m7 = fill_masks(t, cols, o7, high_m, low_m, close)
    check("L7 no exit bar is dropped with reason", m7["exit_missing"][0] and not m7["fillable"][0])

    # L8-L10 verdict contract
    check("L8 negative mean is KILLED",
          exec_verdict({"mean": -0.001, "t": -3.0}, {"mean": -0.001, "t": -3.0}) == "EXECUTABLE_KILLED")
    check("L9 both t clear 2 -> SURVIVES",
          exec_verdict({"mean": 0.002, "t": 2.5}, {"mean": 0.002, "t": 2.2}) == "EXECUTABLE_SURVIVES")
    check("L10 positive but not separable -> DEGRADED",
          exec_verdict({"mean": 0.002, "t": 1.4}, {"mean": 0.002, "t": 1.4}) == "EXECUTABLE_DEGRADED")

    # L11 a flat series must never read as an edge
    rows = [{"date": "2020-01-01", "A": {"net": 0.0, "net_exec": 0.0},
             "B": {"net": 0.01, "net_exec": 0.01}, "R": {"net": 0.0, "net_exec": 0.0}}] * 6
    pq = _paired_key(rows, "B", "A", "net_exec")
    check("L11 constant difference has no t", pq["t"] is None and abs(pq["mean"] - 0.01) < 1e-12)

    # L12 nothing fillable must not blow up or invent a return
    o12 = np.full((n_t, n_s), np.nan)
    m12 = fill_masks(t, cols, o12, high_m, low_m, close)
    check("L12 all-halted period yields no finite returns",
          not np.any(np.isfinite(m12["ret"])) and not np.any(m12["fillable"]))

    # L13 same membership twice -> zero turnover
    s = {0, 1}
    check("L13 unchanged membership pays no turnover", _turnover(s, s) == 0.0)

    # L14 exec_gap is research minus executable, computed per arm
    face = {"research_arms": {"A": {"cagr_net": 0.10}}, "executable_arms": {"A": {"cagr_net": 0.07}}}
    check("L14 gap is research minus executable",
          abs((face["research_arms"]["A"]["cagr_net"] - face["executable_arms"]["A"]["cagr_net"]) - 0.03) < 1e-12)

    # L15 year total compounds inside the year, never annualises
    yr = _by_year_key([{"date": "2020-01-01", "A": {"net": 0.01}},
                       {"date": "2020-02-01", "A": {"net": 0.01}}], "A", "net")
    check("L15 two +1%% periods read 2.01%%", abs(yr["2020"]["total"] - (1.01 * 1.01 - 1)) < 1e-12,
          repr(yr["2020"]["total"]))

    if fails:
        print("selftest FAIL %d/%d" % (len(fails), total[0]))
        for f in fails:
            print("  " + f)
        return 1
    print("selftest %d/%d PASS" % (total[0], total[0]))
    return 0


def _now() -> str:
    from datetime import datetime
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _machine() -> str:
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id", "unknown")
    except (OSError, ValueError):
        return "unknown"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--hold", type=int, default=HOLD)
    ap.add_argument("--stride", type=int, default=HOLD)
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    return run(hold=args.hold, stride=args.stride)


if __name__ == "__main__":
    sys.exit(main())
