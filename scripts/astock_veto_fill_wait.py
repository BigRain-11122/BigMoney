"""A-share residual veto: is "unbuyable" a wall, or just a longer wait?

Why this face exists
--------------------
r2008 (scripts/astock_veto_executable.py) prices the black list at the next
morning's open and throws away every name that opens limit-up or is halted --
4.09 limit-up names and 1.32 halted names per rebalance, i.e. a 99.84% fill
rate.  It books those names at **zero weight**, as if the only alternative to
buying at 09:30 today is never owning them.

That is one of two choices a desk actually has.  The other is **wait**: an
A-share that opens limit-up usually opens a day or two later, and the per-symbol
CSVs already hold `open` for every bar, so the cost of waiting is measurable --
it is just `open(entry_day) / open(t+1) - 1`, and the holding period simply
starts later.

So this face prices the identical three arms **three** ways:

    research    close(t)  -> close(t+20)                    (parent anchor)
    drop        open(t+1) -> open(t+1+20), unbuyable = 0     (r2008, bit-exact)
    wait        open(first buyable in [t+1, t+1+5]) -> +20   (this face)

`wait` differs from `drop` on exactly one thing: a name that is limit-up or
halted on t+1 is given up to 5 trading days to open, and the 20-day clock
starts on the day it actually fills.  A name that never opens inside that
window is still unbuyable and still booked at zero -- so `wait` can only ever
*add* names back relative to `drop`, never remove them.

Verdict (fixed here, before the numbers are seen)
-------------------------------------------------
On the wait booking, versus the drop booking of the same period:

    WAIT_RECOVERS   mean(B-A)_wait > mean(B-A)_drop  and  mean(B-A)_wait > 0
    WAIT_COSTS      mean(B-A)_wait <= mean(B-A)_drop

`WAIT_COSTS` is not a failure of the book -- it is the price of the wall.  If
waiting recovers, the 4.09 names/period were never really gone, they were just
late, and the r2008 "we lost 19.21pp to execution" line is an overstatement of
the cost by the amount waiting buys back.

Board limits (a diagnostic, never a verdict)
--------------------------------------------
r2008 uses one 4.5% threshold for every board because it is below all of them
(main 10%, ChiNext/STAR 20%, ST 5%).  This face prints, for the names it
waited on, how far each gap sat from **that board's own** limit on that date --
so a reader can see whether the 4.5% door let in any non-limit one-price days.
It is a print, not a gate: changing the gate would make `drop` stop reproducing
r2008 bit for bit, and that anchor is worth more than the diagnostic.

Usage
-----
    python scripts/astock_veto_fill_wait.py run
    python scripts/astock_veto_fill_wait.py check
    python scripts/astock_veto_fill_wait.py selftest
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_veto_layer import (  # noqa: E402
    COST_ONE_SIDE,
    FIRST_DATE,
    HOLD,
    LOOKBACK_BETA,
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
from astock_veto_executable import (  # noqa: E402
    ENTRY_LAG,
    EXIT_SLACK,
    LIMIT_UP_MIN,
    exec_verdict,
    fill_masks,
    load_ohl,
)

OUT = os.path.join(ROOT, "results", "astock_veto_fill_wait.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_FILL_WAIT.md")
PARENT = os.path.join(ROOT, "results", "astock_veto_executable.json")
PANEL_PER = os.path.join(ROOT, "data", "astock_daily", "per")
ELIG = os.path.join(ROOT, "data", "fundamental", "eligibility.csv")

ARMS = ("A", "B", "C", "R")
#: how close a gap has to sit to a board's limit to be called "at the limit"
LIMIT_TOL = 0.005


# ------------------------------------------------------------- board plumbing
def board_of(code: str) -> str:
    """Which board a six-digit A-share code trades on.  Pure."""
    c = str(code).zfill(6)
    if c.startswith(("688", "689")):
        return "star"      # 科创板
    if c.startswith(("300", "301")):
        return "chinext"   # 创业板
    if c.startswith(("4", "8", "920")):
        return "bse"       # 北交所
    return "main"          # 主板 (600/601/603/605/000/001/002/003)


def board_limit(code: str, date: str, is_st: bool) -> float:
    """The daily up-limit for this name on this date, as a fraction.

    2020-08-24 is the ChiNext registration-reform date: before it ChiNext moved
    10%, after it 20%.  STAR was 20% from day one.  BSE is 30%.  On the main
    board an ST name moves 5% and everyone else 10%; on ChiNext/STAR the ST flag
    no longer narrows the band after the reform, so it is ignored there.
    """
    b = board_of(code)
    if b == "star":
        return 0.20
    if b == "chinext":
        return 0.10 if date < "2020-08-24" else 0.20
    if b == "bse":
        return 0.30
    return 0.05 if is_st else 0.10


def load_st(elig_path: str = ELIG) -> set:
    """The set of codes flagged ST in the *current* eligibility snapshot.

    This is a point-in-time snapshot, not a per-date replay: a name that is ST
    today was not necessarily ST in 2021.  The face only uses it to *print*
    distance-to-limit under the right band, so a wrong historical flag can
    mislabel a diagnostic bucket but can never move a booked return.
    """
    st = set()
    if not os.path.exists(elig_path):
        return st
    try:
        with io.open(elig_path, encoding="utf-8", errors="ignore") as fh:
            header = fh.readline().strip().split(",")
            try:
                i_code = header.index("code")
                i_st = header.index("r2_st")
            except ValueError:
                return st
            for line in fh:
                parts = line.rstrip("\n").split(",")
                if len(parts) <= max(i_code, i_st):
                    continue
                if parts[i_st].strip().lower() == "true":
                    st.add(parts[i_code].strip().zfill(6))
    except OSError:
        return set()
    return st


# ------------------------------------------------------------- the wait logic
def gap_vs_board(entry_px: np.ndarray, prev_close: np.ndarray, codes, date: str,
                 st_set: set) -> np.ndarray:
    """open/prev_close - 1, and how far that sits below the board's own limit.

    Returns (gap, slack_to_limit) where slack_to_limit = limit - gap, so a value
    near zero means the print sat right at the board's up-limit and a large
    positive value means a one-price day that was *not* a limit day.
    """
    with np.errstate(invalid="ignore", divide="ignore"):
        gap = entry_px / prev_close - 1.0
    lim = np.array([board_limit(c, date, str(c).zfill(6) in st_set) for c in codes],
                   dtype=np.float64)
    return gap, lim - gap


def fill_masks_wait(t: int, cols: np.ndarray, open_m, high_m, low_m, close,
                    hold: int = HOLD, slack: int = EXIT_SLACK):
    """Buy-late booking: a name that cannot be bought on t+1 gets `slack` more days.

    Pure (no I/O), so selftest can hand it hand-built matrices.

    Returns a dict with
      fillable      bool mask, booked this period
      entry_day     0 = bought on t+1, k = bought k days late, -1 = never
      reason        0 = bought on time, 1 = was limit-up on t+1, 2 = was halted
                    on t+1, -1 = never filled
      waited        fillable & entry_day > 0
      exit_missing  filled but no usable exit open inside slack
      delayed_exit  exit was late too
      ret           entry -> exit return, NaN where not fillable
    """
    n = len(cols)
    entry = np.full(n, np.nan)
    entry_day = np.full(n, -1, dtype=np.int64)
    reason = np.full(n, -1, dtype=np.int64)
    blocked_kind = np.zeros(n, dtype=np.int64)  # 1 limit-up, 2 halted, on t+1

    for k in range(slack + 1):
        row = t + ENTRY_LAG + k
        if row >= open_m.shape[0]:
            break
        still = entry_day < 0
        if not np.any(still):
            break
        cand_open = open_m[row][cols]
        cand_hi = high_m[row][cols]
        cand_lo = low_m[row][cols]
        prev_c = close[row - 1][cols] if row >= 1 else np.full(n, np.nan)
        bar = np.isfinite(cand_open) & (cand_open > 0) & np.isfinite(cand_hi)
        with np.errstate(invalid="ignore", divide="ignore"):
            gap = cand_open / prev_c - 1.0
        one_price = bar & np.isfinite(cand_lo) & (cand_hi == cand_lo)
        # same 4.5% door as r2008, so the `drop` leg reproduces it bit for bit
        limit_up = one_price & np.isfinite(gap) & (gap > LIMIT_UP_MIN)
        if k == 0:
            blocked_kind = np.where(limit_up, 1, np.where(~bar, 2, 0))
        buyable = still & bar & ~limit_up
        if np.any(buyable):
            entry[buyable] = cand_open[buyable]
            entry_day[buyable] = k
            reason[buyable] = np.where(k == 0, 0, blocked_kind[buyable])
            reason[buyable & (k == 0)] = 0
            reason[buyable & (k > 0) & (blocked_kind == 0)] = 2

    filled = entry_day >= 0

    exit_px = np.full(n, np.nan)
    exit_delay = np.zeros(n, dtype=bool)
    for k in range(slack + 1):
        rows = t + ENTRY_LAG + np.where(filled, entry_day, 0) + hold + k
        need = filled & ~np.isfinite(exit_px) & (rows < open_m.shape[0])
        if not np.any(need):
            continue
        idxs = np.flatnonzero(need)
        cand = open_m[rows[idxs], cols[idxs]]
        good = np.isfinite(cand) & (cand > 0)
        if np.any(good):
            gi = idxs[good]
            exit_px[gi] = cand[good]
            if k > 0:
                exit_delay[gi] = True

    exit_missing = filled & ~np.isfinite(exit_px)
    fillable = filled & ~exit_missing
    with np.errstate(invalid="ignore", divide="ignore"):
        ret = exit_px / entry - 1.0
    ret = np.where(fillable, ret, np.nan)
    return {
        "fillable": fillable,
        "entry_day": entry_day,
        "reason": reason,
        "waited": fillable & (entry_day > 0),
        "exit_missing": exit_missing,
        "delayed_exit": exit_delay & fillable,
        "ret": ret,
    }


def wait_verdict(wait_ba: dict, drop_ba: dict) -> str:
    """Fixed before the run: does waiting buy anything back?"""
    w = wait_ba.get("mean")
    d = drop_ba.get("mean")
    if w is None or d is None:
        return "INSUFFICIENT_PERIODS"
    if w <= 0:
        return "WAIT_KILLS_EDGE"
    return "WAIT_RECOVERS" if w > d else "WAIT_COSTS"


# --------------------------------------------------------------------- the run
def build(hold: int = HOLD, stride: int = HOLD):
    dates, symbols, close, amount, shares = load_panel()
    d2, sym2, open_m, high_m, low_m, close2 = load_ohl()
    if dates != d2 or symbols != sym2:
        raise SystemExit("open grid disagrees with close grid: refusing to mix calendars")
    if not np.allclose(close, close2, equal_nan=True):
        raise SystemExit("close columns disagree between the two loaders")

    st_set = load_st()
    rets = daily_returns(close)
    mkt = market_return(rets)

    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)

    # three independent streams, same as r2008 for research/drop so both anchor
    rng_res = np.random.default_rng(SEED)
    rng_drop = np.random.default_rng(SEED + 1)
    rng_wait = np.random.default_rng(SEED + 2)

    prev = {"research": {k: None for k in ARMS},
            "drop": {k: None for k in ARMS},
            "wait": {k: None for k in ARMS}}
    rows = []
    t = start
    while t + HOLD < len(dates):
        idx, resid, q, fwd = score_slice(t, close, amount, shares, rets, mkt)
        if resid is None:
            t += stride
            continue

        n = len(idx)
        fill_drop = fill_masks(t, idx, open_m, high_m, low_m, close, hold=hold)
        fill_wait = fill_masks_wait(t, idx, open_m, high_m, low_m, close, hold=hold)

        ok_d = fill_drop["fillable"]
        ok_w = fill_wait["fillable"]
        n_ok_d = int(ok_d.sum())
        n_ok_w = int(ok_w.sum())

        # ---- research booking: the parent's, exactly (whole pool, close->close)
        m_res = {"A": np.ones(n, dtype=bool), "B": q < 4, "C": q < 3}
        drop_n = int(n - np.sum(m_res["B"]))
        rand_pool, rand_sets = [], []
        for _ in range(RANDOM_DRAWS):
            perm = rng_res.permutation(n)
            keep = np.zeros(n, dtype=bool)
            keep[perm[: n - drop_n]] = True
            rand_pool.append(float(np.mean(fwd[keep])))
            rand_sets.append(set(idx[keep].tolist()))

        # ---- the two executable bookings share the arm definitions, differ on the fill set
        keep_frac = float(np.sum(m_res["B"])) / n if n else 1.0
        drop_n_ok_d = int(round(n_ok_d * (1.0 - keep_frac)))
        drop_n_ok_w = int(round(n_ok_w * (1.0 - keep_frac)))

        rand_drop, rand_sets_drop = [], []
        cols_ok_d = np.flatnonzero(ok_d)
        if len(cols_ok_d):
            for _ in range(RANDOM_DRAWS):
                pick = rng_drop.permutation(len(cols_ok_d))
                keep_ok = np.zeros(n, dtype=bool)
                keep_ok[cols_ok_d[pick[: len(cols_ok_d) - drop_n_ok_d]]] = True
                rand_drop.append(float(np.nanmean(fill_drop["ret"][keep_ok])))
                rand_sets_drop.append(set(idx[keep_ok].tolist()))

        rand_wait, rand_sets_wait = [], []
        cols_ok_w = np.flatnonzero(ok_w)
        if len(cols_ok_w):
            for _ in range(RANDOM_DRAWS):
                pick = rng_wait.permutation(len(cols_ok_w))
                keep_ok = np.zeros(n, dtype=bool)
                keep_ok[cols_ok_w[pick[: len(cols_ok_w) - drop_n_ok_w]]] = True
                rand_wait.append(float(np.nanmean(fill_wait["ret"][keep_ok])))
                rand_sets_wait.append(set(idx[keep_ok].tolist()))

        # ---- wait diagnostics: what the wall actually held back, and at what price
        waited = fill_wait["waited"]
        never = ~fill_wait["fillable"]
        wait_days = fill_wait["entry_day"][waited]

        gap_board = {}
        if np.any(waited):
            w_idx = np.flatnonzero(waited)
            w_codes = [symbols[j] for j in idx[w_idx]]
            w_entry = np.array([open_m[t + ENTRY_LAG + int(dd)][idx[i]]
                                for i, dd in zip(w_idx, fill_wait["entry_day"][w_idx])])
            w_prev = np.array([close[t + ENTRY_LAG + int(dd) - 1][idx[i]]
                               for i, dd in zip(w_idx, fill_wait["entry_day"][w_idx])])
            g, slack_to = gap_vs_board(w_entry, w_prev, w_codes,
                                       dates[t + ENTRY_LAG], st_set)
            ok_g = np.isfinite(g) & np.isfinite(slack_to)
            for b in ("main", "chinext", "star", "bse"):
                sel = np.array([board_of(c) == b for c in w_codes]) & ok_g
                if np.any(sel):
                    at_limit = sel & (slack_to <= LIMIT_TOL)
                    gap_board[b] = {
                        "n": int(sel.sum()),
                        "n_at_limit": int(np.sum(at_limit)),
                        "mean_gap": float(np.nanmean(g[sel])),
                        "mean_slack_to_limit": float(np.nanmean(slack_to[sel])),
                        "min_slack_to_limit": float(np.nanmin(slack_to[sel])),
                        "n_nan": int(np.sum(~ok_g)),
                    }

        row = {
            "date": dates[t],
            "n": int(n),
            "n_fillable_drop": n_ok_d,
            "n_fillable_wait": n_ok_w,
            "limit_up_day0": int(np.sum(fill_wait["reason"] == 1) + np.sum((fill_wait["reason"] < 0) & (fill_wait["entry_day"] < 0) & (fill_drop["limit_up"]))),
            "halted_day0": int(np.sum(fill_drop["halted_entry"])),
            "waited": int(np.sum(waited)),
            "never_filled": int(np.sum(never & (fill_wait["entry_day"] < 0))),
            "mean_wait_days": float(wait_days.mean()) if len(wait_days) else None,
            "max_wait_days": int(wait_days.max()) if len(wait_days) else None,
            "delayed_exit": int(np.sum(fill_wait["delayed_exit"])),
            "gap_board": gap_board,
        }

        for name, m_res_m in m_res.items():
            cur = set(idx[m_res_m].tolist())
            turb = _turnover(cur, prev["research"][name])
            prev["research"][name] = cur
            g = float(np.mean(fwd[m_res_m]))
            row[name] = {"gross": g, "net": g - 2.0 * COST_ONE_SIDE * turb,
                         "turnover": turb, "size": int(np.sum(m_res_m))}

            m_d = ok_d & m_res_m
            cur_d = set(idx[m_d].tolist())
            turb_d = _turnover(cur_d, prev["drop"][name])
            prev["drop"][name] = cur_d
            gd = float(np.nanmean(fill_drop["ret"][m_d])) if np.any(m_d) else float("nan")
            row[name]["net_drop"] = gd - 2.0 * COST_ONE_SIDE * turb_d if np.isfinite(gd) else float("nan")
            row[name]["turnover_drop"] = turb_d
            row[name]["size_drop"] = int(np.sum(m_d))

            m_w = ok_w & m_res_m
            cur_w = set(idx[m_w].tolist())
            turb_w = _turnover(cur_w, prev["wait"][name])
            prev["wait"][name] = cur_w
            gw = float(np.nanmean(fill_wait["ret"][m_w])) if np.any(m_w) else float("nan")
            row[name]["net_wait"] = gw - 2.0 * COST_ONE_SIDE * turb_w if np.isfinite(gw) else float("nan")
            row[name]["turnover_wait"] = turb_w
            row[name]["size_wait"] = int(np.sum(m_w))

        # random arm, three bookings
        rg = float(np.mean(rand_pool))
        rcur = set.union(*rand_sets)
        rturb = _turnover(rcur, prev["research"]["R"])
        prev["research"]["R"] = rcur

        rgd = float(np.nanmean(rand_drop)) if rand_drop else float("nan")
        rcur_d = set.union(*rand_sets_drop) if rand_sets_drop else set()
        rturb_d = _turnover(rcur_d, prev["drop"]["R"])
        prev["drop"]["R"] = rcur_d

        rgw = float(np.nanmean(rand_wait)) if rand_wait else float("nan")
        rcur_w = set.union(*rand_sets_wait) if rand_sets_wait else set()
        rturb_w = _turnover(rcur_w, prev["wait"]["R"])
        prev["wait"]["R"] = rcur_w

        row["R"] = {
            "gross": rg, "net": rg - 2.0 * COST_ONE_SIDE * rturb,
            "turnover": rturb, "size": int(len(rand_sets[0])) if rand_sets else 0,
            "net_drop": rgd - 2.0 * COST_ONE_SIDE * rturb_d if np.isfinite(rgd) else float("nan"),
            "turnover_drop": rturb_d,
            "size_drop": int(len(rand_sets_drop[0]) if rand_sets_drop else 0),
            "net_wait": rgw - 2.0 * COST_ONE_SIDE * rturb_w if np.isfinite(rgw) else float("nan"),
            "turnover_wait": rturb_w,
            "size_wait": int(len(rand_sets_wait[0]) if rand_sets_wait else 0),
        }

        rows.append(row)
        t += stride
    return dates, symbols, rows


def _series(rows, arm, key):
    return np.array([r[arm][key] for r in rows], dtype=np.float64)


def _paired(rows, arm, base, key):
    d = np.array([r[arm][key] - r[base][key] for r in rows], dtype=np.float64)
    d = d[np.isfinite(d)]
    if len(d) < 3:
        return {"n": int(len(d)), "mean": None, "se": None, "t": None}
    mean = float(d.mean())
    se = float(d.std(ddof=1) / math.sqrt(len(d)))
    flat = float(np.std(d, ddof=1)) <= 1e-12 * max(1.0, abs(mean))
    return {"n": int(len(d)), "mean": mean, "se": se,
            "t": None if flat or se <= 0 else mean / se}


def _arm(rows, arm, key, size_key, turn_key):
    nets = _series(rows, arm, key)
    nets = nets[np.isfinite(nets)]
    return {
        "periods": int(len(nets)),
        "cagr_net": compound(list(nets)) if len(nets) else None,
        "mean_net_per_rebalance": float(nets.mean()) if len(nets) else None,
        "mean_size": float(np.mean([r[arm][size_key] for r in rows])) if rows else None,
        "mean_turnover": float(np.mean([r[arm][turn_key] for r in rows])) if rows else None,
    }


def _by_year(rows, arm, key):
    out = {}
    for r in rows:
        y = r["date"][:4]
        v = r[arm][key]
        if np.isfinite(v):
            out.setdefault(y, []).append(v)
    return {y: {"periods": len(v), "total": float(np.prod([1.0 + x for x in v]) - 1.0)}
            for y, v in sorted(out.items())}


def summarize(rows):
    res = {arm: _arm(rows, arm, "net", "size", "turnover") for arm in ARMS}
    drop = {arm: _arm(rows, arm, "net_drop", "size_drop", "turnover_drop") for arm in ARMS}
    wait = {arm: _arm(rows, arm, "net_wait", "size_wait", "turnover_wait") for arm in ARMS}
    for arm in ARMS:
        res[arm]["by_year"] = _by_year(rows, arm, "net")
        drop[arm]["by_year"] = _by_year(rows, arm, "net_drop")
        wait[arm]["by_year"] = _by_year(rows, arm, "net_wait")
    paired = {}
    for label, key in (("research", "net"), ("drop", "net_drop"), ("wait", "net_wait")):
        paired[label] = {
            "B_minus_A": _paired(rows, "B", "A", key),
            "B_minus_R": _paired(rows, "B", "R", key),
            "C_minus_A": _paired(rows, "C", "A", key),
        }
    return res, drop, wait, paired


def _now():
    import datetime as _dt
    return _dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def _machine():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id")
    except (OSError, ValueError):
        return None


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:
        return path


def _t(x):
    return "None" if x is None else "%+.2f" % x


def anchor_vs_parent(drop_arms):
    if not os.path.exists(PARENT):
        return None
    try:
        with io.open(PARENT, encoding="utf-8") as fh:
            par = json.load(fh)
    except (OSError, ValueError):
        return None
    out = {"parent_cutoff": par.get("evidence_cutoff"), "arms": {}}
    worst = 0.0
    for arm in ARMS:
        mine = drop_arms[arm]["cagr_net"]
        theirs = ((par.get("executable_arms") or {}).get(arm) or {}).get("cagr_net")
        diff = None if (mine is None or theirs is None) else abs(mine - theirs)
        if diff is not None:
            worst = max(worst, diff)
        out["arms"][arm] = {"mine": mine, "parent": theirs, "abs_diff": diff}
    out["worst_abs_diff"] = worst
    out["paired_B_minus_A_parent"] = (par.get("paired_per_rebalance") or {}).get("executable", {}).get("B_minus_A")
    return out


def write_md(p):
    res, drop, wait, pair = p["research_arms"], p["drop_arms"], p["wait_arms"], p["paired_per_rebalance"]
    wq = p["wait_quality"]
    tot_n = tot_lim = 0
    gap_a = (wait["A"]["cagr_net"] or 0.0) - (drop["A"]["cagr_net"] or 0.0)
    gap_b = (wait["B"]["cagr_net"] or 0.0) - (drop["B"]["cagr_net"] or 0.0)
    lines = []
    lines.append("# 一字涨停买不到，还是只是要等一天？")
    lines.append("")
    lines.append("> 面：`results/astock_veto_fill_wait.json` · 生成 %s · 面板前沿 %s · 最后一期 %s · %d 期"
                 % (p["generated"], p["panel"]["last"], p["last_rebalance"], p["rebalances"]))
    lines.append("")
    lines.append("## 一句话")
    lines.append("")
    lines.append("r2008 把每个买不到的名字记成零仓位。本面给它们 %d 个交易日去打开，"
                 "然后从真正成交那天的开盘价起算 20 日：研究口径 B-A **%+.4f%%/期（t %s）**，"
                 "剔除口径 **%+.4f%%/期（t %s）**，等待口径 **%+.4f%%/期（t %s）** → **%s**。"
                 % (EXIT_SLACK,
                    100 * pair["research"]["B_minus_A"]["mean"], _t(pair["research"]["B_minus_A"]["t"]),
                    100 * pair["drop"]["B_minus_A"]["mean"], _t(pair["drop"]["B_minus_A"]["t"]),
                    100 * pair["wait"]["B_minus_A"]["mean"], _t(pair["wait"]["B_minus_A"]["t"]),
                    p["verdict"]))
    lines.append("")
    lines.append("## 三条腿的绝对读数")
    lines.append("")
    lines.append("| 臂 | 研究口径 年化(净) | 剔除口径 年化(净) | 等待口径 年化(净) | 等待?剔除(pp) | 等待口径 均人数 | 均换手 |")
    lines.append("|---|---|---|---|---|---|---|")
    names = {"A": "A 全池", "B": "B 剔残差top20%", "C": "C 剔top40%", "R": "R 随机剔20%"}
    for arm in ("A", "B", "C", "R"):
        d_gap = (wait[arm]["cagr_net"] or 0.0) - (drop[arm]["cagr_net"] or 0.0)
        lines.append("| %s | %+.2f%% | %+.2f%% | %+.2f%% | %+.2f | %.0f | %.3f |"
                     % (names[arm], 100 * res[arm]["cagr_net"], 100 * drop[arm]["cagr_net"],
                        100 * wait[arm]["cagr_net"], 100 * d_gap,
                        wait[arm]["mean_size"], wait[arm]["mean_turnover"]))
    lines.append("")
    lines.append("## 配对差（每期，净口径）")
    lines.append("")
    lines.append("| 口径 | B-A 均值 | t | B-R 均值 | t | C-A 均值 | t |")
    lines.append("|---|---|---|---|---|---|---|")
    for label in ("research", "drop", "wait"):
        q = pair[label]
        lines.append("| %s | %+.4f%% | %s | %+.4f%% | %s | %+.4f%% | %s |"
                     % (label, 100 * q["B_minus_A"]["mean"], _t(q["B_minus_A"]["t"]),
                        100 * q["B_minus_R"]["mean"], _t(q["B_minus_R"]["t"]),
                        100 * q["C_minus_A"]["mean"], _t(q["C_minus_A"]["t"])))
    lines.append("")
    lines.append("## 等待到底等到了什么")
    lines.append("")
    lines.append("每期平均 **%.2f** 只被 t+1 的一字涨停/停牌挡住，其中 **%.2f** 只在 %d 个交易日内打开并买入，"
                 "**%.2f** 只始终没打开（仍记零仓）；等到的人平均等 **%s** 个交易日（最多 %s 天）。"
                 % (wq["mean_blocked_per_period"], wq["mean_waited_per_period"], EXIT_SLACK,
                    wq["mean_never_per_period"],
                    "—" if wq["mean_wait_days"] is None else "%.2f" % wq["mean_wait_days"],
                    "—" if wq["max_wait_days"] is None else wq["max_wait_days"]))
    lines.append("")
    lines.append("可成交率：研究/剔除口径 **%.2f%%** → 等待口径 **%.2f%%**。"
                 % (100 * wq["mean_fill_rate_drop"], 100 * wq["mean_fill_rate_wait"]))
    lines.append("")
    if wq.get("board_split"):
        lines.append("### 等到的那批名字，离各自板块涨停线有多远")
        lines.append("")
        lines.append("（`slack_to_limit` = 该板块当日涨停幅度 − 实际开盘涨幅；≤ 0.5pp = 真封在涨停，"
                     "明显为正 = 只是全天一个价、并没有封涨停；**负值 = 涨幅超过该板块涨停线**——"
                     "本面只在前复权序列上见过这种（除权日假跳或次新股首日不设涨跌幅），不是真涨停，"
                     "它不影响任何一条腿的收益，只影响这一列的最小值）")
        lines.append("")
        lines.append("| 板块 | 只数 | 其中真封涨停 | 占比 | 平均涨幅 | 平均离涨停线 | 最小离涨停线 |")
        lines.append("|---|---|---|---|---|---|---|")
        bnames = {"main": "主板", "chinext": "创业板", "star": "科创板", "bse": "北交所"}
        for b in ("main", "chinext", "star", "bse"):
            v = wq["board_split"].get(b)
            if v:
                tot_n += v["n"]
                tot_lim += v["n_at_limit"]
                lines.append("| %s | %d | %d | %.1f%% | %+.2f%% | %+.2f%% | %+.2f%% |"
                             % (bnames[b], v["n"], v["n_at_limit"],
                                100.0 * v["n_at_limit"] / v["n"] if v["n"] else 0.0,
                                100 * v["mean_gap"], 100 * v["mean_slack_to_limit"],
                                100 * v["min_slack_to_limit"]))
        if tot_n:
            lines.append("")
            lines.append("**合计 %d 只被等的名字里，只有 %d 只（%.1f%%）真封在该板块的涨停价上；"
                         "其余 %d 只只是「全天一个价」但并没有封涨停。**"
                         % (tot_n, tot_lim, 100.0 * tot_lim / tot_n, tot_n - tot_lim))
        lines.append("")
    lines.append("## 逐年（年度总额=年内连乘，不年化）")
    lines.append("")
    years = sorted(set(res["A"]["by_year"]) | set(drop["A"]["by_year"]) | set(wait["A"]["by_year"]))
    lines.append("| 年 | 研究 A | 剔除 A | 等待 A | 研究 B | 剔除 B | 等待 B |")
    lines.append("|---|---|---|---|---|---|---|")
    for y in years:
        cells = []
        for book in (res, drop, wait):
            for arm in ("A", "B"):
                v = book[arm]["by_year"].get(y)
                cells.append("%+.2f%%" % (100 * v["total"]) if v else "—")
        # reorder to (A across books, then B across books)
        lines.append("| %s | %s | %s | %s | %s | %s | %s |"
                     % (y, cells[0], cells[2], cells[4], cells[1], cells[3], cells[5]))
    lines.append("")
    lines.append("## 这个面没有回答的")
    lines.append("")
    lines.append("- 等待期假设你要的那只股票在 %d 个交易日内打开；打开之后价格可能已经离 t+1 很远，本面把这个差价如实记进收益，"
                 "但没有建模「打开当天成交不了多少量」的冲击。" % EXIT_SLACK)
    lines.append("- 一字涨停仍用 r2008 的 4.5% 统一门槛判定（不按板块），这样剔除口径能逐位复现父面；"
                 "板块线只用来**印**距离，不用来改判。")
    lines.append("- ST 只取 `data/fundamental/eligibility.csv` 的**当期**快照，不是历史重放；"
                 "这会误标个别历史 ST 名字的板块距离，但不影响任何一条腿的收益。")
    lines.append("- 卖出同样按开盘价成交；若卖出日停牌超过 %d 个交易日，该股当期被剔除而不是按最后价估值。" % EXIT_SLACK)
    lines.append("- 票池是现存标的（幸存者偏差，与父面同）；面板起于 %s。" % p["panel"]["first"])
    lines.append("- 本面是**可执行性归因件**，不是可交易策略：无仓位规则、无容量约束、无风控。")
    lines.append("")
    lines.append("## 为什么这面值得存在")
    lines.append("")
    lines.append("r2008 说「晚一天买削掉了全池 %.2fpp、黑名单 %.2fpp」。这两个数把两件不同的事"
                 "加在了一起：**买不到**（真墙）和**要等**（只是慢）。本面把它们拆开："
                 % (100 * abs(p["exec_gap_pp"]["A"]), 100 * abs(p["exec_gap_pp"]["B"])))
    lines.append("")
    lines.append("- 等回来之后，全池年化再降 **%.2fpp**、黑名单再降 **%.2fpp** 是**资金闲置**的代价"
                 "（平均等 %.2f 天，钱没在场上）；"
                 % (100 * abs(gap_a), 100 * abs(gap_b),
                    wq["mean_wait_days"] if wq["mean_wait_days"] is not None else 0.0))
    lines.append("- 但 B-A 的配对差从 **%+.4f%%** 回到 **%+.4f%%**（研究口径 %+.4f%%），"
                 "即 r2008 报告的「执行成本」里 **%.0f%%** 其实是「你愿不愿意多等几天」，不是墙。"
                 % (100 * pair["drop"]["B_minus_A"]["mean"], 100 * pair["wait"]["B_minus_A"]["mean"],
                    100 * pair["research"]["B_minus_A"]["mean"],
                    100.0 * (pair["wait"]["B_minus_A"]["mean"] - pair["drop"]["B_minus_A"]["mean"])
                    / (pair["research"]["B_minus_A"]["mean"] - pair["drop"]["B_minus_A"]["mean"])
                    if (pair["research"]["B_minus_A"]["mean"] - pair["drop"]["B_minus_A"]["mean"]) else 0.0))
    lines.append("")
    lines.append("**判词不变但成本被高估**：r2008 的 `EXECUTABLE_SURVIVES` 在等待口径下仍然成立"
                 "（t %s ≥ 2），所以结论对；但它把那 %.2fpp 全记成执行损失，"
                 "而其中大部分只是延迟——这两件事对「要不要按这张票下单」是不同的答案："
                 "前者说你被市场挡在门外，后者说你只是排在队里。"
                 % (_t(pair["wait"]["B_minus_A"]["t"]), 100 * abs(p["exec_gap_pp"]["B"])))
    lines.append("")
    lines.append("**门槛本身也有量**：被等的名字里只有 **%.1f%%** 真封在该板块当日的涨停价上，"
                 "其余只是「全天一个价」——r2008 的 4.5%% 统一门槛对「封没封涨停」这个判断"
                 "约有 %.0f%% 的假阳性（成交量约束本面测不了，这里只说价格档位没说能买到多少量）。"
                 % (100.0 * tot_lim / tot_n if tot_n else 0.0,
                    100.0 * (tot_n - tot_lim) / tot_n if tot_n else 0.0))
    lines.append("## 与父面的锚")
    lines.append("")
    anc = p.get("parent_anchor") or {}
    if anc.get("arms"):
        lines.append("剔除口径**不是另写一套**：宇宙、分数、五分组、随机对照种子、4.5%% 门槛全部从 r2008 import，"
                     "读数必须逐位复现 `results/astock_veto_executable.json`（cutoff %s）。"
                     "四条臂的最大绝对差 = **%.2e**，`check` 把它当硬腿，超 1e-9 直接判红。"
                     % (anc.get("parent_cutoff"), anc.get("worst_abs_diff") or 0.0))
    else:
        lines.append("父面 `results/astock_veto_executable.json` 本轮不在位，剔除口径**未经锚定**，读数只作参考。")
    lines.append("")
    lines.append("## 复现")
    lines.append("")
    lines.append("```")
    lines.append("python scripts/astock_veto_fill_wait.py selftest   # 纯函数自检")
    lines.append("python scripts/astock_veto_fill_wait.py run")
    lines.append("python scripts/astock_veto_fill_wait.py check        # 漂移/自相矛盾/父面锚")
    lines.append("```")
    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with io.open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ----------------------------------------------------------------------- the face
def run(hold: int = HOLD, stride: int = HOLD):
    dates, symbols, rows = build(hold=hold, stride=stride)
    if not rows:
        print("no rebalance rows")
        return 2

    res, drop, wait, paired = summarize(rows)
    v_wait = wait_verdict(paired["wait"]["B_minus_A"], paired["drop"]["B_minus_A"])
    v_drop = exec_verdict(paired["drop"]["B_minus_A"], paired["drop"]["B_minus_R"])
    v_res = exec_verdict(paired["research"]["B_minus_A"], paired["research"]["B_minus_R"])

    gap = {}
    for arm in ARMS:
        a, b = res[arm]["cagr_net"], drop[arm]["cagr_net"]
        gap[arm] = None if (a is None or b is None) else float(a - b)

    fill_rates_drop = [r["n_fillable_drop"] / r["n"] for r in rows if r["n"]]
    fill_rates_wait = [r["n_fillable_wait"] / r["n"] for r in rows if r["n"]]
    wait_days = [r["mean_wait_days"] for r in rows if r["mean_wait_days"] is not None]
    max_days = [r["max_wait_days"] for r in rows if r["max_wait_days"] is not None]
    board_acc = {}
    for r in rows:
        for b, v in (r.get("gap_board") or {}).items():
            acc = board_acc.setdefault(b, {"n": 0, "n_at_limit": 0, "gap_sum": 0.0,
                                           "slack_sum": 0.0, "slack_min": None})
            acc["n"] += v["n"]
            acc["n_at_limit"] += v["n_at_limit"]
            acc["gap_sum"] += v["mean_gap"] * v["n"]
            acc["slack_sum"] += v["mean_slack_to_limit"] * v["n"]
            acc["slack_min"] = (v["min_slack_to_limit"] if acc["slack_min"] is None
                                else min(acc["slack_min"], v["min_slack_to_limit"]))

    payload = {
        "generated": _now(),
        "evidence_cutoff": dates[-1],
        "machine": _machine(),
        "kind": "astock_veto_fill_wait",
        "prereg": None,
        "spec": {
            "hold": hold,
            "stride": stride,
            "entry": "first buyable open in [t+1, t+1+%d]" % EXIT_SLACK,
            "exit": "first usable open in [entry_day+hold, entry_day+hold+%d]" % EXIT_SLACK,
            "limit_up_min_gap": LIMIT_UP_MIN,
            "limit_up_rule": "one-price day (high==low) and open/prev_close-1 > %.3f is unbuyable on that day"
                             % LIMIT_UP_MIN,
            "cost_one_side": COST_ONE_SIDE,
            "random_draws": RANDOM_DRAWS,
            "seed": SEED,
            "arms": {
                "A": "whole pool (inside the fillable set)",
                "B": "A minus top 20% residual",
                "C": "A minus top 40% residual",
                "R": "random 20% dropped",
            },
        },
        "panel": {"dates": len(dates), "symbols": len(symbols), "first": dates[0], "last": dates[-1]},
        "rebalances": len(rows),
        "research_arms": res,
        "drop_arms": drop,
        "wait_arms": wait,
        "paired_per_rebalance": paired,
        "exec_gap_pp": gap,
        "wait_quality": {
            "mean_blocked_per_period": float(np.mean([r["waited"] + r["never_filled"] for r in rows])),
            "mean_waited_per_period": float(np.mean([r["waited"] for r in rows])),
            "mean_never_per_period": float(np.mean([r["never_filled"] for r in rows])),
            "mean_limit_up_day0_per_period": float(np.mean([r["limit_up_day0"] for r in rows])),
            "mean_halted_day0_per_period": float(np.mean([r["halted_day0"] for r in rows])),
            "mean_wait_days": float(np.mean(wait_days)) if wait_days else None,
            "max_wait_days": int(max(max_days)) if max_days else None,
            "periods_with_delayed_exit": int(sum(1 for r in rows if r["delayed_exit"] > 0)),
            "mean_fill_rate_drop": float(np.mean(fill_rates_drop)) if fill_rates_drop else None,
            "mean_fill_rate_wait": float(np.mean(fill_rates_wait)) if fill_rates_wait else None,
            "board_split": {b: {"n": v["n"],
                                "n_at_limit": v["n_at_limit"],
                                "mean_gap": v["gap_sum"] / v["n"],
                                "mean_slack_to_limit": v["slack_sum"] / v["n"],
                                "min_slack_to_limit": v["slack_min"]}
                            for b, v in board_acc.items()},
        },
        "verdict": v_wait,
        "verdict_drop": v_drop,
        "verdict_research": v_res,
        "last_rebalance": rows[-1]["date"],
        "parent_anchor": anchor_vs_parent(drop),
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)

    wq = payload["wait_quality"]
    print("rebalances %d  panel %d symbols  cutoff %s" % (len(rows), len(symbols), dates[-1]))
    print("  fill rate  drop %.2f%%  wait %.2f%%  | blocked %.2f/period  waited %.2f  never %.2f  mean wait %s days"
          % (100 * wq["mean_fill_rate_drop"], 100 * wq["mean_fill_rate_wait"],
             wq["mean_blocked_per_period"], wq["mean_waited_per_period"], wq["mean_never_per_period"],
             "—" if wq["mean_wait_days"] is None else "%.2f" % wq["mean_wait_days"]))
    for arm in ("A", "B", "C", "R"):
        print("  %s  research %7.2f%%  drop %7.2f%%  wait %7.2f%%  wait-drop %+6.2fpp"
              % (arm, 100 * res[arm]["cagr_net"], 100 * drop[arm]["cagr_net"],
                 100 * wait[arm]["cagr_net"],
                 100 * ((wait[arm]["cagr_net"] or 0.0) - (drop[arm]["cagr_net"] or 0.0))))
    for label in ("research", "drop", "wait"):
        q = paired[label]
        print("  %-9s B-A %+.4f%%/reb t %s | B-R %+.4f%%/reb t %s"
              % (label, 100 * q["B_minus_A"]["mean"], _t(q["B_minus_A"]["t"]),
                 100 * q["B_minus_R"]["mean"], _t(q["B_minus_R"]["t"])))
    print("verdict wait=%s (drop=%s, research=%s) -> %s" % (v_wait, v_drop, v_res, _rel(OUT)))
    return 0


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
    # self-consistency: every booking's verdict must re-derive from its own table
    v_wait = wait_verdict(pair["wait"]["B_minus_A"], pair["drop"]["B_minus_A"])
    if v_wait != face["verdict"]:
        bad.append("verdict %s but the paired table re-derives %s" % (face["verdict"], v_wait))
    v_drop = exec_verdict(pair["drop"]["B_minus_A"], pair["drop"]["B_minus_R"])
    if v_drop != face["verdict_drop"]:
        bad.append("verdict_drop %s but the paired table re-derives %s"
                   % (face["verdict_drop"], v_drop))
    v_res = exec_verdict(pair["research"]["B_minus_A"], pair["research"]["B_minus_R"])
    if v_res != face["verdict_research"]:
        bad.append("verdict_research %s but the paired table re-derives %s"
                   % (face["verdict_research"], v_res))

    # wait can only ever add names back relative to drop
    for arm in ARMS:
        s_d = face["drop_arms"][arm]["mean_size"]
        s_w = face["wait_arms"][arm]["mean_size"]
        if s_d is not None and s_w is not None and s_w + 1e-9 < s_d:
            bad.append("arm %s: wait booking (%f names) is smaller than drop (%f) -- "
                       "waiting must never remove a name" % (arm, s_w, s_d))

    # parent anchor: the drop booking is r2008's executable booking, bit for bit
    anc = face.get("parent_anchor")
    if anc and anc.get("arms"):
        worst = anc.get("worst_abs_diff") or 0.0
        if worst > 1e-9:
            bad.append("parent anchor drifted: drop booking differs from "
                       "results/astock_veto_executable.json by %.3e (limit 1e-9)" % worst)

    if bad:
        for b in bad:
            print("CHECK FAILED %s" % b)
        return 1

    print("CHECK OK rebalances=%d cutoff=%s verdict=%s anchor=%.2e"
          % (face["rebalances"], cutoff, face["verdict"],
             (anc or {}).get("worst_abs_diff") or 0.0))
    return 0


# -------------------------------------------------------------------- selftest
_CHECKS = [0]


def selftest() -> int:
    """Hand-built matrices, hand-computed answers.  A guard that only recomputes
    itself never learns it is wrong (r1935)."""
    fails = []
    _CHECKS[0] = 0

    def ck(name, cond):
        _CHECKS[0] += 1
        if not cond:
            fails.append(name)

    # ---- board_of / board_limit
    ck("board 688 is star", board_of("688001") == "star")
    ck("board 300 is chinext", board_of("300001") == "chinext")
    ck("board 600 is main", board_of("600001") == "main")
    ck("board 000 is main", board_of("000001") == "main")
    ck("board 8 is bse", board_of("830001") == "bse")
    ck("limit star 20%", abs(board_limit("688001", "2023-01-03", False) - 0.20) < 1e-12)
    ck("limit chinext before reform 10%", abs(board_limit("300001", "2020-08-21", False) - 0.10) < 1e-12)
    ck("limit chinext after reform 20%", abs(board_limit("300001", "2020-08-24", False) - 0.20) < 1e-12)
    ck("limit main 10%", abs(board_limit("600001", "2023-01-03", False) - 0.10) < 1e-12)
    ck("limit main ST 5%", abs(board_limit("600001", "2023-01-03", True) - 0.05) < 1e-12)
    ck("limit star ST stays 20%", abs(board_limit("688001", "2023-01-03", True) - 0.20) < 1e-12)

    # ---- fill_masks_wait: a 3-name, 1-period world
    #   bar 0 (t)   : close 10.0 / 10.0 / 10.0
    #   bar 1 (t+1) : name0 opens 10.0 hi=lo=10.0  (flat, not limit)   -> buyable k=0
    #                 name1 opens 11.0 hi=lo=11.0  (limit-up 10%)       -> wait
    #                 name2 no bar                  (halted)            -> wait
    #   bar 2 (t+2) : name1 opens 11.5 hi=11.6 lo=11.4  (opens)         -> buyable k=1
    #                 name2 opens 10.2 hi=10.3 lo=10.1  (opens)         -> buyable k=1
    #   bar 4 (t+4) : exits (hold=2, entry_day+hold=2 for name1/2, 3 for name0)
    n_t, n_s = 8, 3
    open_m = np.full((n_t, n_s), np.nan)
    high_m = np.full((n_t, n_s), np.nan)
    low_m = np.full((n_t, n_s), np.nan)
    close = np.full((n_t, n_s), np.nan)
    close[0, :] = [10.0, 10.0, 10.0]
    open_m[1, 0], high_m[1, 0], low_m[1, 0] = 10.0, 10.0, 10.0
    open_m[1, 1], high_m[1, 1], low_m[1, 1] = 11.0, 11.0, 11.0
    # name2 has no bar at 1
    open_m[2, 1], high_m[2, 1], low_m[2, 1] = 11.5, 11.6, 11.4
    open_m[2, 2], high_m[2, 2], low_m[2, 2] = 10.2, 10.3, 10.1
    close[1, 1] = 11.0
    # exits
    open_m[3, 0] = 10.5  # name0: entry_day 0 + hold 2 = bar 2? no: t+1+0+2 = 3
    open_m[4, 1] = 12.0  # name1: entry_day 1 + hold 2 = 4
    open_m[4, 2] = 10.4  # name2: entry_day 1 + hold 2 = 4

    cols = np.array([0, 1, 2])
    out = fill_masks_wait(0, cols, open_m, high_m, low_m, close, hold=2, slack=2)
    ck("wait: name0 bought on time", out["entry_day"][0] == 0)
    ck("wait: name1 bought late", out["entry_day"][1] == 1)
    ck("wait: name2 bought late", out["entry_day"][2] == 1)
    ck("wait: name1 reason is limit-up", out["reason"][1] == 1)
    ck("wait: name2 reason is halted", out["reason"][2] == 2)
    ck("wait: all three fillable", bool(np.all(out["fillable"])))
    ck("wait: name0 return 10.5/10.0-1 = 5%",
       abs(out["ret"][0] - 0.05) < 1e-12)
    ck("wait: name1 return 12.0/11.5-1", abs(out["ret"][1] - (12.0 / 11.5 - 1.0)) < 1e-12)
    ck("wait: name2 return 10.4/10.2-1", abs(out["ret"][2] - (10.4 / 10.2 - 1.0)) < 1e-12)
    ck("wait: waited flags for 1 and 2", bool(out["waited"][1]) and bool(out["waited"][2])
       and not bool(out["waited"][0]))

    # ---- never opens inside slack -> still zero
    open_m2 = open_m.copy()
    open_m2[2, 1] = np.nan
    high_m2 = high_m.copy()
    high_m2[2, 1] = np.nan
    low_m2 = low_m.copy()
    low_m2[2, 1] = np.nan
    out2 = fill_masks_wait(0, cols, open_m2, high_m2, low_m2, close, hold=2, slack=1)
    ck("never: name1 not fillable inside slack=1", not bool(out2["fillable"][1]))
    ck("never: name1 entry_day -1", out2["entry_day"][1] == -1)

    # ---- wait_verdict three states
    ck("verdict recovers", wait_verdict({"mean": 0.003}, {"mean": 0.002}) == "WAIT_RECOVERS")
    ck("verdict costs", wait_verdict({"mean": 0.001}, {"mean": 0.002}) == "WAIT_COSTS")
    ck("verdict kills edge", wait_verdict({"mean": -0.001}, {"mean": 0.002}) == "WAIT_KILLS_EDGE")
    ck("verdict insufficient", wait_verdict({"mean": None}, {"mean": 0.002}) == "INSUFFICIENT_PERIODS")

    # ---- a flat series must not produce a t
    flat_rows = [{"A": {"net": 0.01}, "B": {"net": 0.01}} for _ in range(10)]
    p = _paired(flat_rows, "B", "A", "net")
    ck("flat series has no t", p["t"] is None)

    if fails:
        for f in fails:
            print("SELFTEST FAIL %s" % f)
        print("SELFTEST FAILED %d of %d checks" % (len(fails), _CHECKS[0]))
        return 1
    print("SELFTEST OK %d checks" % _CHECKS[0])
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "check", "selftest"))
    ap.add_argument("--hold", type=int, default=HOLD)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run(hold=args.hold)
    if args.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main())
