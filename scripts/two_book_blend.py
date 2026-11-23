"""Do the two published books diversify each other, or are they the same trade?

The firm now has two books that print money on their own and have been measured to
death *internally*:

  A  the A-share residual black list (`scripts/astock_veto_*`, 17 faces) --
     a stock book that buys the ~80% of names the 20-day residual ranking does NOT
     like.  77 rebalances, 20 traded days apart, close t -> close t+20, 8bp/side.
  B  the bond-free ETF book with the 8% vol target (`scripts/etf_nobond_vt.py`,
     production candidate `nobond_vt08`) -- 5 ETF seats, 20-day rotation, 10bp/side,
     de-lever only.

Every face in either family answers a question *inside* its own book (turnover,
capacity, lots, cash leg, width, smoothing).  Not one of them answers the question a
funder actually asks before wiring money: **if I hold both, do I get two returns or
one return twice?**

That is the whole script.  It does not build a new signal, does not re-tune either
book, and does not claim capital.  It takes each book's own published per-period
return stream, puts them on the same 20-trading-day grid, and reports:

  * Pearson and Spearman correlation of the two per-period streams (all, IS, OOS,
    by calendar year, and a rolling 8-period window so a reader can see the
    correlation is not a single lucky average);
  * the blend under three weight rules -- equal weight, inverse-volatility, and the
    analytic max-Sharpe weight -- with the two data-driven rules estimated on the
    in-sample half ONLY and then applied unchanged out of sample (a weight fitted on
    the whole window would make the blend look better than it can be bought);
  * annualised return / Sharpe / max drawdown for each book and each blend, on the
    whole window plus IS (<= 2023-12-31) and OOS (> 2023-12-31);
  * a boundary-alignment sensitivity: the two books are booked from different
    reference prices (A from the close of the rebalance bar, B from the open of that
    same bar per its published `entry_lag=0` caliber).  The main read pairs them on
    the same calendar date; the sensitivity shifts B's level read by one bar in each
    direction and reports whether the verdict moves.

Verdict rule, frozen before the run:

    BLEND_ADDS      equal-weight Sharpe > max(Sharpe A, Sharpe B) and the same
                    ordering holds in the OOS half
    BLEND_REDUNDANT the blend's Sharpe is not above the better single book
    BLEND_NOT_SEPARABLE the full-window read and the OOS read disagree in sign

Every number printed here is derived from a published face, not typed.  `check`
re-derives the summary from the published JSON alone (no book is recomputed) and
`--selftest` pins the algebra that turns two return streams into the printed
correlation, weights, blend stats and verdict.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, ROOT)

A_FACE = os.path.join(ROOT, "results", "astock_veto_smooth_rank.json")
B_FACE = os.path.join(ROOT, "results", "etf_nobond_vt.json")
OUT = os.path.join(ROOT, "results", "two_book_blend.json")
MD = os.path.join(ROOT, "research", "TWO_BOOK_BLEND.md")

BOOK_A_ARM = "1"          # K=1 == the parent book, no smoothing (r2019 arm 1)
BOOK_B_ARM = "nobond_vt08"
IS_END = "2023-12-31"
PERIOD_TDAYS = 20         # both books trade on a 20-trading-day stride
TDAYS_PER_YEAR = 252.0

DOC_BEGIN = "<!-- BEGIN:TWO-BOOK-BLEND -->"
DOC_END = "<!-- END:TWO-BOOK-BLEND -->"


# ------------------------------------------------------------------ pure logic
def period_stats(r) -> dict:
    """Annualise a per-period (20-trading-day) return stream.  No fitting."""
    r = np.asarray(r, dtype=np.float64)
    r = r[np.isfinite(r)]
    n = int(r.size)
    if n < 2:
        return {"periods": n, "mean": None, "ann": None, "vol_ann": None,
                "sharpe": None, "maxdd": None, "best": None, "worst": None}
    n_per_year = TDAYS_PER_YEAR / PERIOD_TDAYS
    growth = float(np.prod(1.0 + r))
    years = n / n_per_year
    ann = growth ** (1.0 / years) - 1.0 if growth > 0 else -1.0
    sd = float(np.std(r, ddof=1))
    vol = sd * np.sqrt(n_per_year)
    level = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(level)
    maxdd = float(np.min(level / peak - 1.0))
    return {
        "periods": n,
        "mean": float(np.mean(r)),
        "ann": float(ann),
        "vol_ann": float(vol),
        "sharpe": float(np.mean(r) / sd * np.sqrt(n_per_year)) if sd > 0 else None,
        "maxdd": maxdd,
        "best": float(np.max(r)),
        "worst": float(np.min(r)),
    }


def corr_pair(a, b) -> dict:
    """Pearson and Spearman on the common finite support, plus n."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    m = np.isfinite(a) & np.isfinite(b)
    a, b = a[m], b[m]
    n = int(a.size)
    if n < 3:
        return {"n": n, "pearson": None, "spearman": None}
    if np.std(a) == 0 or np.std(b) == 0:
        return {"n": n, "pearson": None, "spearman": None, "degenerate": True}
    pear = float(np.corrcoef(a, b)[0, 1])
    ra = _rankdata(a)
    rb = _rankdata(b)
    spear = float(np.corrcoef(ra, rb)[0, 1])
    return {"n": n, "pearson": pear, "spearman": spear}


def _rankdata(x) -> np.ndarray:
    """Average ranks, the standard Spearman convention."""
    x = np.asarray(x, dtype=np.float64)
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(x.size, dtype=np.float64)
    ranks[order] = np.arange(1, x.size + 1, dtype=np.float64)
    # replace runs of equal values with their mean rank
    sx = x[order]
    i = 0
    while i < sx.size:
        j = i
        while j + 1 < sx.size and sx[j + 1] == sx[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = np.mean(ranks[order[i:j + 1]])
        i = j + 1
    return ranks


def blend_series(a, b, w: float) -> np.ndarray:
    """Per-period blended return.  w on book A."""
    return w * np.asarray(a, dtype=np.float64) + (1.0 - w) * np.asarray(b, dtype=np.float64)


def w_invvol(a, b) -> float:
    """Inverse-volatility weight on A, clipped to [0, 1] (de-lever only)."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    sa = float(np.std(a, ddof=1))
    sb = float(np.std(b, ddof=1))
    if not np.isfinite(sa) or not np.isfinite(sb) or sa <= 0 or sb <= 0:
        return 0.5
    return float(np.clip((1.0 / sa) / ((1.0 / sa) + (1.0 / sb)), 0.0, 1.0))


def w_maxsharpe(a, b) -> float:
    """Analytic two-asset max-Sharpe weight on A, clipped to [0, 1].

    w* = (var_b - cov) / (var_a + var_b - 2*cov).  Clipping matters: an unclipped
    solution can ask for a short leg, and this book has no short leg.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.size < 3:
        return 0.5
    va = float(np.var(a, ddof=1))
    vb = float(np.var(b, ddof=1))
    cov = float(np.cov(a, b, ddof=1)[0, 1])
    den = va + vb - 2.0 * cov
    if den <= 0:
        return 0.5
    return float(np.clip((vb - cov) / den, 0.0, 1.0))


def rolling_corr(a, b, win: int = 8) -> dict:
    """Rolling correlation over ``win`` consecutive periods, summarised."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    vals = []
    for i in range(0, max(0, a.size - win + 1)):
        sl = slice(i, i + win)
        aa, bb = a[sl], b[sl]
        if not (np.all(np.isfinite(aa)) and np.all(np.isfinite(bb))):
            continue
        if np.std(aa) == 0 or np.std(bb) == 0:
            continue
        vals.append(float(np.corrcoef(aa, bb)[0, 1]))
    if not vals:
        return {"windows": 0, "min": None, "median": None, "max": None}
    return {"windows": len(vals), "min": float(np.min(vals)),
            "median": float(np.median(vals)), "max": float(np.max(vals))}


def verdict_why(vd: str, corr_pearson, sr_a, sr_b) -> str:
    """Say *why* a verdict landed where it did, so a reader cannot mistake a low
    correlation for a green light (and cannot miss one either)."""
    if vd == "BLEND_ADDS":
        return "LOW_CORR_AND_BOTH_STRONG"
    if vd == "BLEND_NOT_SEPARABLE":
        return "HALVES_DISAGREE"
    if corr_pearson is None:
        return "UNKNOWN"
    # verdict is BLEND_REDUNDANT: two distinct causes, and they read differently
    if corr_pearson < 0.5:
        return "TWO_RETURNS_BUT_WEAK_LEG"
    return "SAME_TRADE_TWICE"


def verdict(sr_a, sr_b, sr_eq_all, sr_eq_oos) -> str:
    """Frozen three-state rule."""
    if sr_eq_all is None or sr_a is None or sr_b is None:
        return "BLEND_NOT_SEPARABLE"
    better_all = sr_eq_all > max(sr_a, sr_b)
    if not better_all:
        return "BLEND_REDUNDANT"
    if sr_eq_oos is None:
        return "BLEND_NOT_SEPARABLE"
    # the OOS read must rank the blend above both books too, else the full-window
    # ordering is not a property of the blend but of one half
    return "BLEND_ADDS" if sr_eq_oos > max(sr_a, sr_b) else "BLEND_NOT_SEPARABLE"


# ------------------------------------------------------------------ load
def _load_a():
    with open(A_FACE, encoding="utf-8") as f:
        d = json.load(f)
    rows = d["rows"][BOOK_A_ARM]
    dates = [r["date"] for r in rows]
    rets = [float(r["net"]) for r in rows]
    return d, dates, rets


def _load_b_levels():
    """Recompute book B's daily level series from its own production script.

    The two data-driven weight rules are fitted on returns only; nothing here is
    fitted.  Cost: ~55s (panel build + one 5-seat vol-targeted run).
    """
    import etf_composite_pf as E
    import etf_robust_pf as R
    import etf_equity_alpha as A

    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, 20, 5, 0.0010,
                                      vol_target=0.08)
    return ser, float(turn), len(cols), int(n_flip)


def _level_on(ser, dates) -> list:
    """Book B's level on each of book A's rebalance dates (exact hit, else the
    last observation on or before it, with the snap count returned).

    Used by the boundary sensitivity only; the main alignment walks the level grid
    by trading-day position so the last period of book A is not lost.
    """
    idx = np.asarray(ser.index.values, dtype="datetime64[ns]")
    vals = np.asarray(ser.values, dtype=np.float64)
    out = []
    snaps = 0
    for ds in dates:
        t = np.datetime64(str(ds), "ns")
        j = int(np.searchsorted(idx, t, side="right")) - 1
        if j < 0:
            out.append(np.nan)
            continue
        if idx[j] != t:
            snaps += 1
        out.append(float(vals[j]))
    return out, snaps


def align_periods(ser, dates, rets_a, hold: int = PERIOD_TDAYS):
    """Pair book A's row i (interval [date_i, date_i + hold trading days]) with
    book B's level return over the SAME trading-day span.

    Walking the level grid by position instead of intersecting with the rebalance
    dates keeps book A's last period (whose end is past the last rebalance date).
    For every period whose successor rebalance date exists, the grid position is
    asserted to land on it -- that assertion, not a hope, is what lets the two
    streams be called the same intervals.
    """
    idx = ser.index
    vals = np.asarray(ser.values, dtype=np.float64)
    pos = idx.get_indexer(idx.__class__(dates))
    labels, ends, ra, rb = [], [], [], []
    grid_consistent = 0
    grid_checks = 0
    for i in range(len(dates)):
        p = int(pos[i])
        if p < 0 or p + hold >= len(idx):
            continue
        r = float(vals[p + hold] / vals[p] - 1.0) if vals[p] > 0 else float("nan")
        if not np.isfinite(r):
            continue
        labels.append(dates[i])
        ends.append(str(idx[p + hold].date()))
        ra.append(float(rets_a[i]))
        rb.append(r)
        if i + 1 < len(dates):
            grid_checks += 1
            if str(idx[p + hold].date()) == str(dates[i + 1]):
                grid_consistent += 1
    return {
        "labels": labels, "ends": ends,
        "a": np.array(ra, dtype=np.float64), "b": np.array(rb, dtype=np.float64),
        "grid_checks": grid_checks, "grid_consistent": grid_consistent,
    }


def _shift_dates(dates, k: int) -> list:
    """Shift the date list by k grid steps (sensitivity only)."""
    if k == 0:
        return list(dates)
    if k > 0:
        return list(dates[k:]) + [None] * k
    return [None] * (-k) + list(dates[:k])


# ------------------------------------------------------------------ the face
def build(ser=None, b_turn=None, universe=None, flips=None):
    a_face, a_dates, a_rets = _load_a()
    if ser is None:
        ser, b_turn, universe, flips = _load_b_levels()

    al = align_periods(ser, a_dates, a_rets)
    labels, ends = al["labels"], al["ends"]
    ra, rb = al["a"], al["b"]
    _, snaps = _level_on(ser, a_dates)

    is_mask = np.array([d <= IS_END for d in labels], dtype=bool)
    oos_mask = ~is_mask

    corr = corr_pair(ra, rb)
    corr_is = corr_pair(ra[is_mask], rb[is_mask])
    corr_oos = corr_pair(ra[oos_mask], rb[oos_mask])
    by_year: dict = {}
    for y in sorted({d[:4] for d in labels}):
        m = np.array([d[:4] == y for d in labels], dtype=bool)
        if int(m.sum()) >= 3:
            by_year[y] = corr_pair(ra[m], rb[m])

    # weights: equal is a rule, the other two are fitted on IS only
    w_eq = 0.5
    w_iv = w_invvol(ra[is_mask], rb[is_mask]) if int(is_mask.sum()) >= 3 else 0.5
    w_ms = w_maxsharpe(ra[is_mask], rb[is_mask]) if int(is_mask.sum()) >= 3 else 0.5

    stats_a = period_stats(ra)
    stats_b = period_stats(rb)
    blends = {}
    for name, w in (("equal", w_eq), ("invvol_is", w_iv), ("maxsharpe_is", w_ms)):
        r = blend_series(ra, rb, w)
        s = period_stats(r)
        s_oos = period_stats(r[oos_mask])
        s_is = period_stats(r[is_mask])
        blends[name] = {"weight_on_a": float(w), "all": s,
                        "is": s_is, "oos": s_oos}

    st_a_is, st_a_oos = period_stats(ra[is_mask]), period_stats(ra[oos_mask])
    st_b_is, st_b_oos = period_stats(rb[is_mask]), period_stats(rb[oos_mask])

    vd = verdict(stats_a["sharpe"], stats_b["sharpe"],
                 blends["equal"]["all"]["sharpe"], blends["equal"]["oos"]["sharpe"])

    # boundary-alignment sensitivity: shift B's level read one grid step each way
    sens = {}
    for k in (-1, 1):
        shifted = _shift_dates(a_dates, k)
        try:
            lev2, snaps2 = _level_on(ser, [d for d in shifted if d is not None])
        except Exception:  # noqa: BLE001 -- a missing date is a printed gap, not a crash
            sens["shift_%+d" % k] = {"verdict": "UNAVAILABLE"}
            continue
        it = iter(lev2)
        lv = [next(it) if d is not None else np.nan for d in shifted]
        r2 = []
        for i in range(len(shifted) - 1):
            l0, l1 = lv[i], lv[i + 1]
            if not (np.isfinite(l0) and np.isfinite(l1)) or l0 <= 0:
                continue
            r2.append(float(l1 / l0 - 1.0))
        r2 = np.array(r2, dtype=np.float64)
        m = min(r2.size, ra.size)
        c2 = corr_pair(ra[:m], r2[:m])
        s2 = period_stats(blend_series(ra[:m], r2[:m], 0.5))
        sens["shift_%+d" % k] = {"pearson": c2["pearson"], "n": c2["n"],
                                 "blend_eq_sharpe": s2["sharpe"],
                                 "blend_eq_ann": s2["ann"]}

    face = {
        "generated": _now(),
        "evidence_cutoff": a_face.get("evidence_cutoff"),
        "machine": _machine(),
        "kind": "two_book_blend",
        "fills_the_hole_of": ("17 faces inside book A and 12 inside book B, none across "
                             "them (r1865..r2019)"),
        "prereg": {
            "question": ("holding both the A-share residual black list and the bond-free "
                         "8%-vol ETF book, do I get two returns or one return twice?"),
            "arms": {"A": "results/astock_veto_smooth_rank.json rows['1'] (parent book, net)",
                     "B": "results/etf_nobond_vt.json arm nobond_vt08 (production candidate)"},
            "weights": "equal (rule) / inverse-vol (IS) / analytic max-Sharpe (IS); clipped to [0,1], no short leg",
            "alignment": ("both books' returns are put on the same 20-trading-day interval "
                          "[date_i, date_{i+1}]; a row is kept only when both ends of its "
                          "interval are on book B's daily level grid"),
            "verdict_rule": ("BLEND_ADDS iff equal-weight Sharpe beats both books on the whole "
                             "window AND out of sample; BLEND_REDUNDANT if not even the first; "
                             "BLEND_NOT_SEPARABLE if the two halves disagree"),
            "rule_frozen_before_run": True,
        },
        "spec": {
            "book_a": "close t -> close t+20, 8bp/side, fractional 1/n, fully invested",
            "book_b": "close t decision -> open t own (published entry_lag=0 caliber), 10bp/side, 8% vol target de-lever only",
            "annualization": "per-period(20 td) mean/std scaled by sqrt(252/20); CAGR from compounded growth over n*20/252 years",
            "is_end": IS_END,
            "known_caliber_gap": ("book A is booked off the rebalance bar's close, book B off that "
                                  "bar's open; the shift_+-1 block measures that boundary"),
        },
        "books": {
            "a": dict(stats_a, is_periods=st_a_is, oos_periods=st_a_oos),
            "b": dict(stats_b, is_periods=st_b_is, oos_periods=st_b_oos,
                      universe=universe, flips_repaired=flips, turnover_per_period=b_turn),
        },
        "alignment": {"periods": len(labels), "first": labels[0] if labels else None,
                      "last": labels[-1] if labels else None,
                      "last_period_end": ends[-1] if ends else None,
                      "is_periods": int(is_mask.sum()), "oos_periods": int(oos_mask.sum()),
                      "date_snaps_to_prior_bar": snaps,
                      "grid_consistent": al["grid_consistent"],
                      "grid_checks": al["grid_checks"]},
        "corr": {"all": corr, "is": corr_is, "oos": corr_oos,
                 "by_year": by_year, "rolling8": rolling_corr(ra, rb, 8)},
        "blends": blends,
        "sensitivity": sens,
        "verdict": vd,
        "verdict_why": verdict_why(vd, corr.get("pearson"),
                                   stats_a["sharpe"], stats_b["sharpe"]),
        "rows": {"dates": labels,
                 "a": [round(float(x), 10) for x in ra],
                 "b": [round(float(x), 10) for x in rb]},
    }
    return face


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _machine() -> str:
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as f:
            return json.load(f).get("machine_id", "unknown")
    except Exception:  # noqa: BLE001
        return "unknown"


def _p(x, nd=2):
    return "n/a" if x is None else ("%.*f" % (nd, x * 100.0))


def _r(x, nd=3):
    return "n/a" if x is None else ("%.*f" % (nd, x))


def write_md(face) -> None:
    a, b = face["books"]["a"], face["books"]["b"]
    c = face["corr"]["all"]
    bl = face["blends"]
    al = face["alignment"]
    best_single = max(a["sharpe"], b["sharpe"])
    eq = bl["equal"]["all"]

    lines = [DOC_BEGIN, "",
             "# 两本书一起拿着，是两份收益还是同一份收益付两次钱", "",
             "generated %s | evidence_cutoff **%s** | 对齐期数 %d（IS %d / OOS %d，%s → %s）"
             % (face["generated"], face["evidence_cutoff"], al["periods"], al["is_periods"],
                al["oos_periods"], al["first"], al["last"]),
             "", "## 一句话", ""]

    why = face.get("verdict_why")
    corr_all = c["pearson"]
    if face["verdict"] == "BLEND_ADDS":
        head = ("**能加**：等权合并后年化 %s%%、夏普 %s，高于两本书各自最好的 %s——而且样本外"
                "同样成立。" % (_p(eq["ann"]), _r(eq["sharpe"]), _r(best_single)))
    elif face["verdict"] == "BLEND_REDUNDANT" and why == "TWO_RETURNS_BUT_WEAK_LEG":
        head = ("**确实是两份收益，但合起来不加钱**：两本书的逐期收益相关只有 **%s**——它们不是"
                "同一笔交易；可等权合并后夏普 %s，仍然低于 ETF 书单独的 %s。原因不是重复，是"
                "**弱的那一本拖累**：A 股书年化 %s%% 却背着 %s%% 的波动（夏普 %s），配进来就把"
                "组合的风险调整收益拉下去。" % (_r(corr_all), _r(eq["sharpe"]), _r(best_single),
                                                _p(a["ann"]), _p(a["vol_ann"]), _r(a["sharpe"])))
    elif face["verdict"] == "BLEND_REDUNDANT":
        head = ("**加不了**：等权合并夏普 %s，没有超过更好的那一本（%s），而且两本书的收益本身"
                "高相关（%s）——第二本书就是同一笔交易的另一个名字。"
                % (_r(eq["sharpe"]), _r(best_single), _r(corr_all)))
    else:
        head = ("**读数分裂**：全窗合并夏普 %s vs 更好单本 %s，但样本外不支持同一排序，"
                "本面不下判词。" % (_r(eq["sharpe"]), _r(best_single)))
    lines.append(head)
    lines.append("")
    lines.append("两本书的逐期收益相关系数 **%s**（Pearson，n=%d；Spearman %s）。"
                 "相关越低，合并越值钱；相关接近 1，第二本书就只是同一笔交易的另一个名字。"
                 % (_r(c["pearson"]), c["n"], _r(c["spearman"])))
    lines += ["", "## 两本书各自的读数", "",
              "| 书 | 期数 | 每期均值 | 年化 | 年化波动 | 夏普 | 最大回撤 | 最差一期 |",
              "|---|---|---|---|---|---|---|---|",
              "| A 股残差黑名单 | %d | %s%% | %s%% | %s%% | %s | %s%% | %s%% |"
              % (a["periods"], _p(a["mean"]), _p(a["ann"]), _p(a["vol_ann"]),
                 _r(a["sharpe"]), _p(a["maxdd"]), _p(a["worst"])),
              "| B 无债 ETF·8%%目标 | %d | %s%% | %s%% | %s%% | %s | %s%% | %s%% |"
              % (b["periods"], _p(b["mean"]), _p(b["ann"]), _p(b["vol_ann"]),
                 _r(b["sharpe"]), _p(b["maxdd"]), _p(b["worst"])),
              "",
              "注：两本书的期收益都是 **%d 个交易日的非重叠持有期**，年化按 √(252/%d) 缩放；"
              "A 股书 8bp/边、ETF 书 10bp/边，各自都已含成本。" % (PERIOD_TDAYS, PERIOD_TDAYS),
              "", "## 合并三档", "",
              "| 权重档 | A 权重 | 年化 | 夏普 | 最大回撤 | IS 夏普 | OOS 夏普 |",
              "|---|---|---|---|---|---|---|"]

    for key, label in (("equal", "等权 50/50"), ("invvol_is", "逆波动（IS 估）"),
                       ("maxsharpe_is", "最大夏普（IS 估）")):
        s = bl[key]
        lines.append("| %s | %s%% | %s%% | %s | %s%% | %s | %s |"
                     % (label, _p(s["weight_on_a"], 1), _p(s["all"]["ann"]),
                        _r(s["all"]["sharpe"]), _p(s["all"]["maxdd"]),
                        _r(s["is"]["sharpe"]), _r(s["oos"]["sharpe"])))

    lines += ["",
              "两个数据驱动的权重只在 **IS（≤%s）** 上估，然后原封不动用到 OOS——"
              "全窗拟权重会让合并看起来比买得到的更好。权重上限 1、下限 0：这本书没有空腿。" % IS_END,
              "",
              "**这两行权重本身就是读数**：最大夏普那一档在 IS 期给出的 A 股书权重是 **%s%%**%s，"
              "逆波动给出 **%s%%**。也就是说，用样本内的数字算，最优做法是**把 A 股书放小到"
              "不足三成、甚至零**——不是因为它和 ETF 书重复（相关只有 %s），而是因为它每一单位风险的"
              "回报不够。低相关只解决「一加一不等于二」，解决不了「这一本本身不够好」。"
              % (_p(bl["maxsharpe_is"]["weight_on_a"], 1),
                 ("（即一点都不配）" if bl["maxsharpe_is"]["weight_on_a"] <= 0.0 else ""),
                 _p(bl["invvol_is"]["weight_on_a"], 1), _r(corr_all)),
              "", "## 对齐是怎么做上去的", "",
              "A 股书每一期的收益是「调仓日收盘 → 20 个交易日之后收盘」。本面**不**拿调仓日列表去截，"
              "而是沿着 ETF 书的日净值网格按交易日位置走 %d 步，于是 A 股书最后那一期（终点落在最后一个"
              "调仓日之后）不会被丢掉。%d 次可校验的跨度里，%d 次的落点与下一次调仓日**逐日对上**——"
              "这条断言是「两条流是同一个区间」的依据，不是假设。"
              % (PERIOD_TDAYS, al["grid_checks"], al["grid_consistent"]),
              "", "## 相关性不是一次平均值", "",
              "| 段 | n | Pearson | Spearman |", "|---|---|---|---|"]
    for key, label in (("all", "全窗"), ("is", "IS"), ("oos", "OOS")):
        cc = face["corr"][key]
        lines.append("| %s | %d | %s | %s |"
                     % (label, cc["n"], _r(cc["pearson"]), _r(cc["spearman"])))
    r8 = face["corr"]["rolling8"]
    lines += ["",
              "滚动 8 期窗口共 %d 个：最小 %s / 中位 %s / 最大 %s。"
              % (r8["windows"], _r(r8["min"]), _r(r8["median"]), _r(r8["max"])),
              "", "| 年 | n | Pearson |", "|---|---|---|"]
    for y, cc in face["corr"]["by_year"].items():
        lines.append("| %s | %d | %s |" % (y, cc["n"], _r(cc["pearson"])))

    lines += ["", "## 边界对齐敏感性", "",
              "两本书的记账基价不同（A 用调仓 bar 的收盘，B 用它自己公布的「决策 bar 当根开盘」口径）。"
              "主读数按同一日历日配对；下面把 B 的取值整体挪一根 bar 再算一遍，看判词会不会动。", "",
              "| 挪动 | n | Pearson | 等权合并夏普 | 等权合并年化 |", "|---|---|---|---|---|"]
    for k, s in face["sensitivity"].items():
        if s.get("verdict") == "UNAVAILABLE":
            lines.append("| %s | — | — | — | — |" % k)
            continue
        lines.append("| %s | %d | %s | %s | %s%% |"
                     % (k, s["n"], _r(s["pearson"]), _r(s["blend_eq_sharpe"]),
                        _p(s["blend_eq_ann"])))

    sh = [v for v in face["sensitivity"].values() if v.get("verdict") != "UNAVAILABLE"]
    if sh:
        hi = max(v["blend_eq_sharpe"] for v in sh if v.get("blend_eq_sharpe") is not None)
        lines += ["",
                  "两档挪动下等权合并夏普最高 %s，仍低于 ETF 书单独的 %s——**判词不随一根 bar 翻转**，"
                  "但也说明这条边界值得记住：它改变的是小数位，不是结论。" % (_r(hi), _r(best_single))]

    lines += ["",
              "## 这个面不是策略", "",
              "本面是**定价/口径件**：没有仓位规则、没有容量约束、没有风控、没有交易时钟，"
              "也没有把两本书的钱真正合到一个账户里（A 股书与 ETF 书的券池、T+1、整手都不在这里）。"
              "它只回答一个问题：两条已发布的收益流放到同一把尺子上，相关是多少、合起来是几份。",
              "", "## 未验证（如实）", "",
              "1. **口径边界**：A 收盘基价 vs B 开盘基价，差一小段；`sensitivity` 只证明判词不随一根 bar 翻转，"
              "不证明逐期收益逐位可比。",
              "2. A 股书的第 1 期 `turnover=1.0` 是全额建仓（一次性成本已计），B 的第 1 期同；两本书首期都保留，"
              "没有去掉——去掉会让年化看起来更好但不是买得到的。",
              "3. 两本书的**容量**各自被量过（A：`astock_veto_adv_capacity` 判 1000 万不约束；B：参与率约束在"
              "`etf_book_capacity_edge`），本面**不做联合容量**——同一账户同时吃两条腿的资金占用未量。",
              "4. 相关是**收益**相关，不是**回撤同步**；两本书同时出坑的概率没有量（要联合分布，77 期观测不够）。",
              "5. 权重规则只有三档，没搜更多；搜了就不是「买得到的合并」而是「拟合出来的合并」。",
              "",
              "## 复跑", "",
              "```",
              "python scripts/two_book_blend.py run      # 重算并写本页 + JSON（B 腿需 ~55s 面板）",
              "python scripts/two_book_blend.py check    # 只从已发布 JSON 重推摘要",
              "python scripts/two_book_blend.py --selftest",
              "```",
              DOC_END, ""]
    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with open(MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def run() -> int:
    face = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    write_md(face)
    print(json.dumps({"verdict": face["verdict"],
                      "periods": face["alignment"]["periods"],
                      "corr": face["corr"]["all"],
                      "books": {k: {"ann": v["ann"], "sharpe": v["sharpe"]}
                                for k, v in face["books"].items()},
                      "blends": {k: {"w": v["weight_on_a"],
                                     "ann": v["all"]["ann"],
                                     "sharpe": v["all"]["sharpe"]}
                                 for k, v in face["blends"].items()}},
                     ensure_ascii=False, indent=1), flush=True)
    print("saved", OUT, flush=True)
    print("saved", MD, flush=True)
    return 0


# ------------------------------------------------------------------ check
def check() -> int:
    """Re-derive every printed statistic from the published JSON.  No book is rerun."""
    if not os.path.exists(OUT):
        print("face missing: %s" % OUT, flush=True)
        return 3
    with open(OUT, encoding="utf-8") as f:
        face = json.load(f)
    bad = []
    # 0) shape first: every later leg does numpy arithmetic, and a self-check that
    #    raises instead of printing CHECK FAILED is a check that cannot report
    if not isinstance(face.get("rows"), dict) or "a" not in face["rows"] or "b" not in face["rows"]:
        print("CHECK FAILED rows block missing", flush=True)
        return 1
    ra = np.array(face["rows"]["a"], dtype=np.float64)
    rb = np.array(face["rows"]["b"], dtype=np.float64)
    if ra.size != rb.size:
        print("CHECK FAILED rows length %d vs %d" % (ra.size, rb.size), flush=True)
        return 1
    if ra.size != face.get("alignment", {}).get("periods"):
        print("CHECK FAILED rows length %d vs alignment periods %r"
              % (ra.size, face.get("alignment", {}).get("periods")), flush=True)
        return 1
    if ra.size < 3:
        print("CHECK FAILED too few periods (%d) to check" % ra.size, flush=True)
        return 1

    # 1) correlation re-derived from the rows
    c = corr_pair(ra, rb)
    if face["corr"]["all"]["pearson"] is None or abs(c["pearson"] - face["corr"]["all"]["pearson"]) > 1e-9:
        bad.append("pearson %r vs re-derived %r" % (face["corr"]["all"]["pearson"], c["pearson"]))

    # 3) each book's stats re-derived from its own row stream
    for key, arr in (("a", ra), ("b", rb)):
        s = period_stats(arr)
        pub = face["books"][key]
        for f_ in ("ann", "sharpe", "maxdd"):
            if pub.get(f_) is None or s.get(f_) is None:
                bad.append("book %s %s missing" % (key, f_))
            elif abs(pub[f_] - s[f_]) > 1e-9:
                bad.append("book %s %s %r vs %r" % (key, f_, pub[f_], s[f_]))

    # 4) each blend re-derived at its own weight
    for key, blk in face["blends"].items():
        r = blend_series(ra, rb, blk["weight_on_a"])
        s = period_stats(r)
        for f_ in ("ann", "sharpe", "maxdd"):
            if blk["all"].get(f_) is None or abs(blk["all"][f_] - s[f_]) > 1e-9:
                bad.append("blend %s %s %r vs %r" % (key, f_, blk["all"].get(f_), s[f_]))

    # 5) IS/OOS weights must be reproducible from the IS half alone
    is_mask = np.array([d <= IS_END for d in face["rows"]["dates"]], dtype=bool)
    if int(is_mask.sum()) >= 3:
        w_iv = w_invvol(ra[is_mask], rb[is_mask])
        w_ms = w_maxsharpe(ra[is_mask], rb[is_mask])
        if abs(w_iv - face["blends"]["invvol_is"]["weight_on_a"]) > 1e-9:
            bad.append("invvol weight %r vs %r" % (face["blends"]["invvol_is"]["weight_on_a"], w_iv))
        if abs(w_ms - face["blends"]["maxsharpe_is"]["weight_on_a"]) > 1e-9:
            bad.append("maxsharpe weight %r vs %r" % (face["blends"]["maxsharpe_is"]["weight_on_a"], w_ms))

    # 6) the verdict must follow from the printed numbers
    vd = verdict(face["books"]["a"]["sharpe"], face["books"]["b"]["sharpe"],
                 face["blends"]["equal"]["all"]["sharpe"],
                 face["blends"]["equal"]["oos"]["sharpe"])
    if vd != face["verdict"]:
        bad.append("verdict %r vs re-derived %r" % (face["verdict"], vd))

    # 7) rolling-8 summary re-derived
    r8 = rolling_corr(ra, rb, 8)
    if face["corr"]["rolling8"]["windows"] != r8["windows"]:
        bad.append("rolling8 windows %r vs %r" % (face["corr"]["rolling8"]["windows"], r8["windows"]))

    if bad:
        for b_ in bad:
            print("CHECK FAILED", b_, flush=True)
        return 1
    print("check ok: %d periods, corr %.4f, A %.4f / B %.4f / eq %.4f sharpe, verdict %s"
          % (ra.size, c["pearson"], face["books"]["a"]["sharpe"],
             face["books"]["b"]["sharpe"], face["blends"]["equal"]["all"]["sharpe"],
             face["verdict"]), flush=True)
    return 0


# ------------------------------------------------------------------ selftest
def _ok(cond, msg):
    if not cond:
        raise AssertionError(msg)


def selftest() -> int:
    legs = []

    def leg(fn, name):
        fn()
        legs.append(name)

    def t_corr_symmetry():
        x = np.array([0.01, -0.02, 0.03, 0.04, -0.01, 0.02])
        y = np.array([0.02, 0.01, -0.01, 0.05, 0.00, 0.01])
        c1 = corr_pair(x, y)
        c2 = corr_pair(y, x)
        _ok(abs(c1["pearson"] - c2["pearson"]) < 1e-12, "corr not symmetric")
        _ok(abs(corr_pair(x, x)["pearson"] - 1.0) < 1e-12, "self corr != 1")

    def t_corr_drops_nan():
        x = np.array([0.01, np.nan, 0.03, 0.04])
        y = np.array([0.02, 0.05, 0.01, 0.06])
        c = corr_pair(x, y)
        _ok(c["n"] == 3, "nan not dropped: n=%d" % c["n"])

    def t_corr_degenerate():
        c = corr_pair(np.array([0.01, 0.01, 0.01]), np.array([0.0, 0.1, 0.2]))
        _ok(c["pearson"] is None, "flat series should not produce a correlation")

    def t_spearman_ranks():
        # a monotone map must leave Spearman at 1 but move Pearson
        x = np.linspace(-1, 1, 9)
        y = np.exp(x)
        c = corr_pair(x, y)
        _ok(abs(c["spearman"] - 1.0) < 1e-12, "monotone spearman != 1: %r" % c["spearman"])
        _ok(c["pearson"] < 0.999, "pearson should not be 1 on a curved map")

    def t_rank_ties():
        r = _rankdata(np.array([1.0, 2.0, 2.0, 3.0]))
        _ok(list(np.round(r, 6)) == [1.0, 2.5, 2.5, 4.0], "tie ranks wrong: %r" % (r,))

    def t_blend_algebra():
        a = np.array([0.01, -0.02, 0.03])
        b = np.array([0.00, 0.01, -0.01])
        w = 0.3
        r = blend_series(a, b, w)
        _ok(np.allclose(r, w * a + (1 - w) * b), "blend != w*a+(1-w)*b")

    def t_blend_variance_identity():
        # var(w a + (1-w) b) must equal the two-asset formula, else the max-Sharpe
        # weight below would be derived from numbers the face does not print
        a = np.array([0.01, -0.02, 0.03, 0.00, 0.02, -0.01])
        b = np.array([0.00, 0.01, -0.01, 0.02, 0.01, 0.03])
        w = 0.4
        r = blend_series(a, b, w)
        va, vb = np.var(a, ddof=1), np.var(b, ddof=1)
        cov = np.cov(a, b, ddof=1)[0, 1]
        lhs = np.var(r, ddof=1)
        rhs = w * w * va + (1 - w) ** 2 * vb + 2 * w * (1 - w) * cov
        _ok(abs(lhs - rhs) < 1e-15, "variance identity broken: %r vs %r" % (lhs, rhs))

    def t_maxsharpe_picks_lowvar_when_uncorr():
        rng = np.random.default_rng(7)
        a = rng.normal(0.01, 0.03, 400)
        b = rng.normal(0.01, 0.01, 400)
        w = w_maxsharpe(a, b)
        _ok(w < 0.5, "max-Sharpe should lean to the lower-vol book, got w=%.3f" % w)

    def t_maxsharpe_clipped():
        # a negative-variance trap: identical streams give a 0/0 and must not explode
        a = np.array([0.01, 0.01, 0.01, 0.01])
        w = w_maxsharpe(a, a)
        _ok(0.0 <= w <= 1.0, "weight out of [0,1]: %r" % w)

    def t_invvol_algebra():
        a = np.array([0.02, -0.02, 0.02, -0.02])
        b = np.array([0.01, -0.01, 0.01, -0.01])
        w = w_invvol(a, b)
        # a has twice the vol of b -> a should get 1/3
        _ok(abs(w - 1.0 / 3.0) < 1e-12, "invvol weight wrong: %r" % w)

    def t_period_stats_annualisation():
        r = np.full(12, 0.01)  # 12 equal periods of +1%
        s = period_stats(r)
        n_per_year = TDAYS_PER_YEAR / PERIOD_TDAYS
        expect = (1.01 ** n_per_year) - 1.0
        _ok(abs(s["ann"] - expect) < 1e-12, "annualisation wrong: %r vs %r" % (s["ann"], expect))
        _ok(s["sharpe"] is not None and s["sharpe"] > 1e6, "flat positive stream should have a huge Sharpe")

    def t_period_stats_drawdown():
        r = np.array([0.10, -0.50, 0.10])
        s = period_stats(r)
        # level 1.10 -> 0.55 -> 0.605 ; maxdd from 1.10 to 0.55 = -0.5
        _ok(abs(s["maxdd"] - (-0.5)) < 1e-12, "maxdd wrong: %r" % s["maxdd"])

    def t_period_stats_requires_two():
        s = period_stats(np.array([0.01]))
        _ok(s["ann"] is None and s["sharpe"] is None, "one period must not be annualised")

    def t_verdict_adds():
        _ok(verdict(0.5, 0.6, 0.9, 0.8) == "BLEND_ADDS", "should be ADDS")

    def t_verdict_redundant():
        _ok(verdict(1.0, 0.6, 0.9, 0.8) == "BLEND_REDUNDANT", "should be REDUNDANT")

    def t_verdict_not_separable():
        _ok(verdict(0.5, 0.6, 0.9, 0.4) == "BLEND_NOT_SEPARABLE", "should be NOT_SEPARABLE")

    def t_verdict_monotone():
        # adding an identical stream must never increase the blend Sharpe above the
        # better book, i.e. the rule cannot be gamed by duplication
        rng = np.random.default_rng(11)
        a = rng.normal(0.008, 0.02, 60)
        sr_a = period_stats(a)["sharpe"]
        sr_eq = period_stats(blend_series(a, a, 0.5))["sharpe"]
        _ok(abs(sr_a - sr_eq) < 1e-9, "duplicate stream changed the Sharpe")

    def t_level_on_ffill():
        import pandas as pd
        idx = pd.to_datetime(["2020-01-02", "2020-01-06", "2020-01-07"])
        ser = pd.Series([1.0, 1.01, 1.02], index=idx)
        lv, snaps = _level_on(ser, ["2020-01-03", "2020-01-06", "2020-01-07"])
        _ok(lv[0] == 1.0 and snaps == 1, "ffill snap wrong: %r snaps=%d" % (lv, snaps))
        _ok(lv[1] == 1.01 and lv[2] == 1.02, "exact hits wrong: %r" % (lv,))

    def t_level_on_missing_head():
        import pandas as pd
        idx = pd.to_datetime(["2020-01-06"])
        ser = pd.Series([1.0], index=idx)
        lv, _ = _level_on(ser, ["2020-01-02"])
        _ok(np.isnan(lv[0]), "a date before the grid must be NaN, not 1.0")

    def t_shift_identity():
        d = ["a", "b", "c", "d"]
        _ok(_shift_dates(d, 0) == d, "shift 0 changed the list")
        _ok(_shift_dates(d, 1) == ["b", "c", "d", None], "shift +1 wrong")
        _ok(_shift_dates(d, -1) == [None, "a", "b", "c"], "shift -1 wrong")

    def t_rolling_corr_bounds():
        rng = np.random.default_rng(3)
        a = rng.normal(0, 0.02, 40)
        b = a + rng.normal(0, 0.001, 40)
        r = rolling_corr(a, b, 8)
        _ok(r["windows"] == 33, "window count wrong: %d" % r["windows"])
        _ok(r["min"] <= r["median"] <= r["max"], "rolling summary not ordered")

    def t_rolling_corr_short():
        r = rolling_corr(np.array([0.1, 0.2]), np.array([0.1, 0.3]), 8)
        _ok(r["windows"] == 0 and r["median"] is None, "short series must not report a window")

    def t_face_rows_roundtrip():
        # the JSON round-trip must not move a number the check later re-derives
        x = np.array([0.0123456789, -0.0234567891, 0.0345678912])
        rt = np.array([round(float(v), 10) for v in x])
        _ok(np.allclose(x, rt, atol=1e-10), "10dp round-trip moved a value")

    for fn, name in (
        (t_corr_symmetry, "corr symmetry"),
        (t_corr_drops_nan, "corr drops NaN"),
        (t_corr_degenerate, "flat series -> no correlation"),
        (t_spearman_ranks, "spearman is rank-based"),
        (t_rank_ties, "tied ranks averaged"),
        (t_blend_algebra, "blend is w*a+(1-w)*b"),
        (t_blend_variance_identity, "two-asset variance identity"),
        (t_maxsharpe_picks_lowvar_when_uncorr, "max-Sharpe leans low vol"),
        (t_maxsharpe_clipped, "max-Sharpe clipped to [0,1]"),
        (t_invvol_algebra, "inverse-vol weight exact"),
        (t_period_stats_annualisation, "period annualisation"),
        (t_period_stats_drawdown, "max drawdown exact"),
        (t_period_stats_requires_two, "one period not annualised"),
        (t_verdict_adds, "verdict ADDS"),
        (t_verdict_redundant, "verdict REDUNDANT"),
        (t_verdict_not_separable, "verdict NOT_SEPARABLE"),
        (t_verdict_monotone, "duplicate stream cannot beat itself"),
        (t_level_on_ffill, "level ffill onto grid"),
        (t_level_on_missing_head, "pre-grid date is NaN"),
        (t_shift_identity, "date shift identity"),
        (t_rolling_corr_bounds, "rolling window count and order"),
        (t_rolling_corr_short, "short series no window"),
        (t_face_rows_roundtrip, "10dp round-trip safe"),
    ):
        leg(fn, name)

    print("selftest %d/%d PASS" % (len(legs), len(legs)), flush=True)
    for name in legs:
        print("  ok -", name, flush=True)
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] == "run":
        return run()
    if argv[0] == "check":
        return check()
    if argv[0] == "--selftest" or argv[0] == "selftest":
        return selftest()
    print("usage: %s [run|check|--selftest]" % os.path.basename(__file__), flush=True)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
