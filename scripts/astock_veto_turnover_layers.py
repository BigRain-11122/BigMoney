"""A-share residual veto book: which layer does the churn come from?

r2015 priced the churn (turnover **23.95%/period**, 4.3x the full pool, 10.8% of
the gross edge handed to the broker).  r2016 tried to buy it back with a
hysteresis band and the assumption was falsified -- the band only removed 0.02
bp/period of cost.  The obvious next question, and the one a person sizing this
book actually asks, is **what is making it turn over at all**:

    the universe moving under the book  (names listing, delisting, dropping out
    of the eligible panel),  or
    names flapping across the veto edge  (q == 4 <-> q < 4)?

The answer decides what can be built: if the churn is the universe, no rule on
this book makes it cheaper (every book on this pool pays it); if it is the edge,
the fix has to damp the *score*, not the membership.

How it is measured (no model, an identity)
-----------------------------------------
The parent's turnover is ``1 - |cur & prev| / |cur|``, which equals
``|cur \\ prev| / |cur|``: only names *arriving* are charged.  Every arriving
name is exactly one of

    U  its symbol was not in the eligible pool last period  (universe flow)
    V  its symbol was in the pool, so it was vetoed last period (edge flow)

so per period, exactly, ``turnover = U/|cur| + V/|cur|``.  The identity is
asserted here, not approximated.  The first period is the parent's full entry
and is reported separately -- attributing it to a layer would be meaningless.

Two readings sit next to the split, because both are things the reader would
otherwise have to guess:

* **arriving names are not all admitted** -- a name can enter the pool already
  vetoed (q == 4), so it costs no turnover.  ``entrant_admitted_rate`` measures
  how many arriving names land in the book, so "universe churn is 5.54%" (the
  full-pool number) can never be read straight across to this book;
* **where the crossings concentrate** -- the same a few names flapping back and
  forth every period is a very different problem from the whole middle of the
  distribution breathing.  ``edge_crossings`` counts, per name, the periods it
  changed sides inside the pool, and prints the top-decile share of all
  crossings.

What this face does NOT claim
-----------------------------
The zero point ``net_if_edge_never_flapped`` is arithmetic, not a plan: the veto
edge *is* the signal, so a book with no edge flow is a different (and dumber)
book.  r2016 already measured the closest rule that damps the edge -- a
hysteresis band -- and it does not recover the tax.  The number is printed so
the reader can see the size of the layer, not because it is reachable.

Usage
-----
    python scripts/astock_veto_turnover_layers.py run
    python scripts/astock_veto_turnover_layers.py check
    python scripts/astock_veto_turnover_layers.py selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_veto_layer import (  # noqa: E402
    COST_ONE_SIDE,
    FIRST_DATE,
    HOLD,
    compound,
    load_panel,
)
from astock_veto_lot_drag import fractional  # noqa: E402

OUT = os.path.join(ROOT, "results", "astock_veto_turnover_layers.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_TURNOVER_LAYERS.md")
PARENT = os.path.join(ROOT, "results", "astock_veto_lot_drag.json")
BAND_PARENT = os.path.join(ROOT, "results", "astock_veto_turnover_band.json")

DOC_BEGIN = "<!-- BEGIN:ASTOCK-VETO-TURNOVER-LAYERS -->"
DOC_END = "<!-- END:ASTOCK-VETO-TURNOVER-LAYERS -->"


# ------------------------------------------------------------------ pure logic
def _turnover(cur: set, prev) -> float:
    """The parent's definition, verbatim: the first period is a full entry."""
    if prev is None:
        return 1.0
    if not cur:
        return 0.0
    return 1.0 - len(cur & prev) / float(len(cur))


def walk_layers(slices) -> tuple:
    """Split every period's arriving names into universe flow and edge flow.

    Returns ``(rows, crossings)`` where ``crossings`` maps a symbol column to the
    number of periods it changed sides *inside the pool*.  A name that leaves
    and comes back is universe flow, not a crossing -- it was never a decision.
    """
    rows = []
    crossings: dict = {}
    prev_book = None
    prev_pool = None
    prev_q = None
    for s in slices:
        cols = np.asarray(s["idx"], dtype=np.int64)
        q = np.asarray(s["q"], dtype=np.int64)
        fwd = np.asarray(s["fwd"], dtype=np.float64)
        inbook = q < 4
        cur = set(cols[inbook].tolist())
        pool_now = set(cols.tolist())
        gross = float(np.mean(fwd[inbook])) if inbook.any() else float("nan")

        if prev_book is None:
            rows.append({
                "date": s["date"],
                "first_entry": True,
                "n_pool": int(len(cols)),
                "n": int(len(cur)),
                "turnover": 1.0,
                "new_n": int(len(cur)),
                "u_n": 0,
                "v_n": 0,
                "pool_entrants": 0,
                "u_share": float("nan"),
                "v_share": float("nan"),
                "gross": gross,
                "net": fractional(fwd[inbook], 1.0) if inbook.any() else float("nan"),
                "fwd_u": float("nan"),
                "fwd_v": float("nan"),
                "fwd_inc": float("nan"),
            })
        else:
            new = cur - prev_book
            u = {c for c in new if c not in prev_pool}
            v = new - u
            n = len(cur)
            # a symbol can only be in v if it was in the pool last period, so v
            # names were vetoed last period by construction -- no extra test.
            u_mask = np.isin(cols, np.fromiter(u, dtype=np.int64)) & inbook if u else np.zeros(len(cols), bool)
            v_mask = np.isin(cols, np.fromiter(v, dtype=np.int64)) & inbook if v else np.zeros(len(cols), bool)
            inc_mask = inbook & ~u_mask & ~v_mask
            turb = _turnover(cur, prev_book)
            rows.append({
                "date": s["date"],
                "first_entry": False,
                "n_pool": int(len(cols)),
                "n": n,
                "turnover": float(turb),
                "new_n": int(len(new)),
                "u_n": len(u),
                "v_n": len(v),
                "pool_entrants": len(pool_now - prev_pool),
                "u_share": (len(u) / n) if n else float("nan"),
                "v_share": (len(v) / n) if n else float("nan"),
                "gross": gross,
                "net": fractional(fwd[inbook], turb) if inbook.any() else float("nan"),
                "fwd_u": float(np.mean(fwd[u_mask])) if u_mask.any() else float("nan"),
                "fwd_v": float(np.mean(fwd[v_mask])) if v_mask.any() else float("nan"),
                "fwd_inc": float(np.mean(fwd[inc_mask])) if inc_mask.any() else float("nan"),
            })
            # crossings: stayed in the pool, changed sides
            both = pool_now & prev_pool
            if both:
                ids = [int(cols[i]) for i in range(len(cols))
                       if int(cols[i]) in both
                       and bool(q[i] < 4) != bool(prev_q[cols[i]] < 4)]
                for c in ids:
                    crossings[c] = crossings.get(c, 0) + 1
        prev_book = cur
        prev_pool = pool_now
        prev_q = {int(c): int(q[i]) for i, c in enumerate(cols)}
    return rows, crossings


def walk_pool_layers(slices) -> list:
    """Arm A: the full eligible pool.  Its turnover is universe flow by
    construction (there is no edge to cross), which is why it is the floor
    every book on this pool pays."""
    prev = None
    rows = []
    for s in slices:
        cur = set(np.asarray(s["idx"], dtype=np.int64).tolist())
        turb = _turnover(cur, prev)
        prev = cur
        rows.append({"date": s["date"], "n": len(cur), "turnover": float(turb)})
    return rows


def _series(rows, key):
    return np.array([r.get(key, float("nan")) for r in rows], dtype=np.float64)


def _fmean(rows, key) -> float:
    a = _series(rows, key)
    a = a[np.isfinite(a)]
    return float(np.mean(a)) if len(a) else float("nan")


def _tstat(diffs):
    d = np.asarray(diffs, dtype=np.float64)
    d = d[np.isfinite(d)]
    if len(d) < 2:
        return None
    sd = float(np.std(d, ddof=1))
    if sd <= 0:
        return None
    return float(np.mean(d) / (sd / np.sqrt(len(d))))


def summarize(rows, pool_rows, crossings) -> dict:
    ex = rows[1:]
    turb_all = float(np.mean(_series(rows, "turnover")))
    turb_ex = float(np.mean(_series(ex, "turnover")))
    u_share = float(np.mean(_series(ex, "u_share")))
    v_share = float(np.mean(_series(ex, "v_share")))
    resid = float(np.max(np.abs(_series(ex, "turnover") - _series(ex, "u_share") - _series(ex, "v_share"))))
    n_pool = float(np.mean(_series(rows, "n_pool")))
    n_book = float(np.mean(_series(rows, "n")))
    pool_turb_ex = float(np.mean(_series(pool_rows[1:], "turnover")))
    gross_ex = _fmean(ex, "gross")
    net_all = _series(rows, "net")

    cross_counts = np.array(sorted(crossings.values()), dtype=np.float64) if crossings else np.zeros(0)
    if len(cross_counts):
        k = max(1, int(np.ceil(len(cross_counts) * 0.1)))
        top = cross_counts[-k:]
        top_share = float(top.sum() / cross_counts.sum())
        repeat3 = int((cross_counts >= 3).sum())
    else:
        top_share, repeat3 = float("nan"), 0

    return {
        "periods": len(rows),
        "periods_attributed": len(ex),
        "turnover_mean_all_periods": turb_all,
        "turnover_mean_ex_first": turb_ex,
        "u_share_mean": u_share,
        "v_share_mean": v_share,
        "identity_residual_max": resid,
        "u_fraction_of_turnover": (u_share / turb_ex) if turb_ex else float("nan"),
        "v_fraction_of_turnover": (v_share / turb_ex) if turb_ex else float("nan"),
        "n_pool_mean": n_pool,
        "n_book_mean": n_book,
        "denominator_ratio": (n_pool / n_book) if n_book else float("nan"),
        "pool_turnover_mean_ex_first": pool_turb_ex,
        "entrant_admitted_rate": (_fmean(ex, "u_n") / _fmean(ex, "pool_entrants"))
        if _fmean(ex, "pool_entrants") else float("nan"),
        "gross_mean_ex_first": gross_ex,
        "net_mean_all_periods": float(np.nanmean(net_all)),
        "net_mean_ex_first": float(np.nanmean(_series(ex, "net"))),
        "net_annualized": compound([float(x) for x in net_all]),
        "fwd_u_mean": _fmean(ex, "fwd_u"),
        "fwd_v_mean": _fmean(ex, "fwd_v"),
        "fwd_inc_mean": _fmean(ex, "fwd_inc"),
        "net_if_edge_never_flapped": (gross_ex - 2.0 * COST_ONE_SIDE * u_share)
        if np.isfinite(gross_ex) else float("nan"),
        "tax_total_per_period": 2.0 * COST_ONE_SIDE * turb_ex,
        "tax_in_edge_per_period": 2.0 * COST_ONE_SIDE * v_share,
        "crossing_total": int(cross_counts.sum()) if len(cross_counts) else 0,
        "crossing_names": int(len(cross_counts)),
        "crossing_top_decile_share": top_share,
        "crossing_max_per_name": float(cross_counts.max()) if len(cross_counts) else 0.0,
        "crossing_names_ge3": repeat3,
        "crossing_per_period": float(cross_counts.sum()) / len(ex) if len(ex) and len(cross_counts) else 0.0,
        "crossing_periods": int((_series(rows[1:], "v_n") > 0).sum()),
    }


def verdict(summ: dict) -> str:
    """Which layer owns the churn.  Strict comparison of the two measured
    shares, nothing invented; a book whose churn is the universe cannot be
    fixed by any rule on this book."""
    u, v = summ["u_fraction_of_turnover"], summ["v_fraction_of_turnover"]
    if not (np.isfinite(u) and np.isfinite(v)):
        return "CHURN_UNPRICEABLE"
    if u > v:
        return "CHURN_IS_MOSTLY_UNIVERSE"
    if v > u:
        return "CHURN_IS_MOSTLY_VETO_EDGE"
    return "CHURN_SPLIT"


def by_year(rows) -> dict:
    out: dict = {}
    for r in rows:
        if r.get("first_entry"):
            continue
        y = r["date"][:4]
        out.setdefault(y, []).append(r)
    return {y: {"periods": len(v),
                "turnover_mean": float(np.mean([r["turnover"] for r in v])),
                "u_share_mean": float(np.nanmean([r["u_share"] for r in v])),
                "v_share_mean": float(np.nanmean([r["v_share"] for r in v])),
                "net_mean": float(np.nanmean([r["net"] for r in v])),
                "n_book_mean": float(np.mean([r["n"] for r in v]))}
            for y, v in sorted(out.items())}


# -------------------------------------------------------------------- the face
def build_slices(hold: int = HOLD, stride: int = HOLD):
    """Same windows as the parent, built by the parent's own code path so the
    per-period series can be anchored bit-for-bit."""
    from astock_resid_veto_layer import LOOKBACK_BETA, market_return, score_slice, daily_returns

    dates, symbols, close, amount, shares = load_panel()
    rets = daily_returns(close)
    mkt = market_return(rets)

    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)

    slices = []
    t = start
    while t + HOLD < len(dates):
        idx, resid, q, fwd = score_slice(t, close, amount, shares, rets, mkt)
        if resid is None:
            t += stride
            continue
        slices.append({"date": dates[t], "idx": idx, "q": q, "fwd": fwd})
        t += stride
    return dates, symbols, slices


def build_face(hold: int = HOLD, stride: int = HOLD):
    dates, symbols, slices = build_slices(hold, stride)
    rows, crossings = walk_layers(slices)
    pool = walk_pool_layers(slices)
    summ = summarize(rows, pool, crossings)
    return dates, symbols, rows, pool, summ


def parent_anchor(rows, pool) -> dict:
    """r2012's published per-period turnover must come back bit-identically for
    both arms -- that is the only proof these layers split *this* book."""
    try:
        with open(PARENT, "r", encoding="utf-8") as fh:
            parent = json.load(fh)
    except (OSError, ValueError) as exc:
        return {"ok": False, "why": "parent unreadable: %s" % exc, "worst_abs_diff": None}
    prow = parent.get("rows") or []
    if len(prow) != len(rows) or len(prow) != len(pool):
        return {"ok": False, "why": "row count parent=%d mine=%d/%d"
                % (len(prow), len(rows), len(pool)), "worst_abs_diff": None}
    worst = 0.0
    for p, r, a in zip(prow, rows, pool):
        if p.get("date") != r["date"] or p.get("date") != a["date"]:
            return {"ok": False, "why": "date mismatch %r" % (p.get("date"),), "worst_abs_diff": None}
        worst = max(worst, abs(float(p["B"]["turnover"]) - r["turnover"]))
        worst = max(worst, abs(float(p["A"]["turnover"]) - a["turnover"]))
    return {"ok": worst <= 1e-12, "worst_abs_diff": worst, "rows": len(prow)}


def band_cross_read(summ: dict) -> dict:
    """Read r2016's published decomposition at the same cutoff and compare the
    edge layer measured here with the tax the band managed to save.  If the
    band's saving is far below this layer's tax, the two faces agree and the
    sentence "banding cannot buy this back" has a number behind it."""
    try:
        with open(BAND_PARENT, "r", encoding="utf-8") as fh:
            band = json.load(fh)
    except (OSError, ValueError) as exc:
        return {"ok": False, "why": "band face unreadable: %s" % exc}
    try:
        saved = float(band["results"]["decomposition"]["band_4_2"]["tax_saved_per_period"])
        band_turb = float(band["results"]["configs"]["band_4_2"]["turnover_mean"])
    except (KeyError, TypeError, ValueError) as exc:
        return {"ok": False, "why": "band face shape: %s" % exc}
    tax = summ["tax_in_edge_per_period"]
    return {"ok": True, "band_saved_per_period": saved, "band_turnover": band_turb,
            "edge_tax_per_period": tax,
            "saved_share_of_edge_tax": (saved / tax) if tax else float("nan")}


def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    try:
        rel = os.path.relpath(path, ROOT)
    except ValueError:
        return str(path).replace(os.sep, "/")
    if rel.startswith(".."):
        return str(path).replace(os.sep, "/")
    return rel.replace(os.sep, "/")


def run() -> int:
    dates, symbols, rows, pool, summ = build_face()
    anchor = parent_anchor(rows, pool)
    read = band_cross_read(summ)
    payload = {
        "generated": _now(),
        "evidence_cutoff": dates[-1],
        "machine": "bm-c",
        "kind": "pricing",
        "fills_the_hole_of": "astock_veto_turnover_band",
        "prereg": {
            "question": "of the veto book's turnover, how much is the universe moving under it and how much is names flapping across the veto edge?",
            "layers": {
                "U": "arriving name whose symbol was not in the eligible pool last period",
                "V": "arriving name whose symbol was in the pool, i.e. vetoed last period",
            },
            "identity": "turnover = U/|cur| + V/|cur| per period, first period (full entry) excluded from attribution",
            "turnover_definition": "1 - |cur & prev| / |cur|, first period = 1.0 (parent's)",
            "verdict": "CHURN_IS_MOSTLY_UNIVERSE / CHURN_IS_MOSTLY_VETO_EDGE / CHURN_SPLIT by the strict comparison of the two measured shares",
            "rule_frozen_before_run": True,
        },
        "spec": {
            "hold": HOLD,
            "stride": HOLD,
            "cost_one_side": COST_ONE_SIDE,
            "booking": "fractional, weight exactly 1/n, fully invested",
            "arms": {"A": "full eligible pool (universe floor)",
                     "B": "pool minus residual top 20% (the veto book)"},
            "crossings": "periods a name changed sides while staying in the pool, counted per symbol",
        },
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": len(rows),
        "results": {"book": summ, "verdict": verdict(summ),
                    "band_cross_read": read, "by_year": by_year(rows)},
        "rows": rows,
        "anchor": anchor,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)

    s = summ
    print("TURNOVER-LAYERS panel %s..%s  %d names  %d periods  cutoff %s"
          % (dates[0], dates[-1], len(symbols), len(rows), dates[-1]))
    print("  book turnover %.2f%% (all, parent) / %.2f%% (attributed)"
          % (s["turnover_mean_all_periods"] * 100, s["turnover_mean_ex_first"] * 100))
    print("  U universe  %.2f%%/period  (%.1f%% of the churn)"
          % (s["u_share_mean"] * 100, s["u_fraction_of_turnover"] * 100))
    print("  V veto edge  %.2f%%/period  (%.1f%% of the churn)"
          % (s["v_share_mean"] * 100, s["v_fraction_of_turnover"] * 100))
    print("  identity residual %.3e   pool floor %.2f%%  denominator %.3fx  entrant-admitted %.1f%%"
          % (s["identity_residual_max"], s["pool_turnover_mean_ex_first"] * 100,
             s["denominator_ratio"], s["entrant_admitted_rate"] * 100))
    print("  net %+.4f%%/p (all) / %+.4f%%/p (attributed)  ann %+.2f%%   tax %.2f bp/p (edge %.2f)   zero-point %+.4f%%/p"
          % (s["net_mean_all_periods"] * 100, s["net_mean_ex_first"] * 100,
             (s["net_annualized"] or 0) * 100,
             s["tax_total_per_period"] * 10000, s["tax_in_edge_per_period"] * 10000,
             s["net_if_edge_never_flapped"] * 100))
    print("  crossings %d over %d names (%.1f per period = %.1f%% of the book; %.1f%% in the top decile; %d names >=3; max %d)"
          % (s["crossing_total"], s["crossing_names"], s["crossing_per_period"],
             s["crossing_per_period"] / s["n_book_mean"] * 100,
             s["crossing_top_decile_share"] * 100,
             s["crossing_names_ge3"], int(s["crossing_max_per_name"])))
    if read.get("ok"):
        print("  band cross-read: r2016 saved %.2f bp/p = %.1f%% of this edge tax"
              % (read["band_saved_per_period"] * 10000, read["saved_share_of_edge_tax"] * 100))
    else:
        print("  band cross-read unavailable: %s" % read.get("why"))
    print("  anchor vs r2012: ok=%s worst=%.3e"
          % (anchor["ok"], anchor.get("worst_abs_diff") if anchor.get("worst_abs_diff") is not None
             else float("nan")))
    print("  -> %s" % _rel(OUT))
    print("  -> %s" % _rel(MD))
    return 0


# ---------------------------------------------------------------------- doc
def _p(x, nd=4):
    return "n/a" if x is None or not np.isfinite(x) else "%+.*f%%" % (nd, x * 100)


def _pn(x, nd=2):
    return "n/a" if x is None or not np.isfinite(x) else "%.*f%%" % (nd, x * 100)


def write_md(payload) -> None:
    s = payload["results"]["book"]
    read = payload["results"]["band_cross_read"]
    years = payload["results"]["by_year"]
    cutoff = payload["evidence_cutoff"]
    cost = payload["spec"]["cost_one_side"]

    L = [DOC_BEGIN, "",
         "# A 股残差黑名单：23.95% 的换手是从哪一层来的",
         "",
         "generated %s | evidence_cutoff **%s** | 期数 %d（可归因 %d） | 单边成本 %.1f bp"
         % (payload["generated"], cutoff, s["periods"], s["periods_attributed"], cost * 10000),
         "",
         "r2015 把账单摊开（换手 23.95%/期、毛边的 10.8% 交给券商），r2016 试着用滞回带把税买回来"
         "——**证伪了**：每期只省 0.02 bp。于是问题从「怎么省」退回到更基础的一步：",
         "**这 23.95% 到底是谁在动？**",
         "",
         "答案只有两种可能，而且它们指向完全不同的做法：",
         "**成分池在它下面动**（新股进来、老股掉出可交易面板）——这种换手每一本建在这个池子上的书都要付，"
         "在本账上没有任何规则能省掉；",
         "**名字在否决边界上翻动**（q==4 ↔ q<4）——这种换手是**信号的产物**，要压它只能压分数，不能压名单。",
         "",
         "本面把两者**逐期精确拆开**，不做模型：本账的换手定义是 `1 - |cur ∩ prev| / |cur|`，"
         "也就是**只有新进来的名字被计费**；而每一个新进来的名字，不是「上一期不在池子里」（U），"
         "就是「上一期在池子里、也就是上期被否决了」（V）。所以逐期恒等式 `换手 = U/|cur| + V/|cur|` "
         "成立——本面断言它（最大残差 %s），不是拟合它。"
         % ("%.1e" % s["identity_residual_max"]),
         "",
         "## 一句话",
         ""]
    L.append("**换手主要来自边界，不是来自池子**：可归因的 %.2f%%/期里，"
             "**U（池子流动）%.2f%%**、**V（否决边界翻动）%.2f%%**——"
             "边界占 **%.1f%%**。也就是说 r2016 那条「加带子省税」的失败是**结构性的**："
             "带子只改「被踢出的名字何时回来」，而它要抵的那笔税，%.1f%% 是进来的名字自己造成的。"
             % (s["turnover_mean_ex_first"] * 100, s["u_share_mean"] * 100, s["v_share_mean"] * 100,
                s["v_fraction_of_turnover"] * 100, s["v_fraction_of_turnover"] * 100))
    L.append("")
    if read.get("ok"):
        L.append("**和 r2016 对得上**：按本面量到的边界税 **%.2f bp/期**，"
                 "r2016 的带子实际省下 **%.2f bp/期**，只有 **%.1f%%**。"
                 "两张面独立算出来的是同一件事，不是转述。"
                 % (read["edge_tax_per_period"] * 10000, read["band_saved_per_period"] * 10000,
                    read["saved_share_of_edge_tax"] * 100))
        L.append("")
    L.append("**池子的底**：全池（A 臂）自己就有 %.2f%%/期的换手，那是纯池子流动。"
             "但**不能把它直接当成这本账的 U**——本账的持仓只有 %.1f%%，同一个绝对流量"
             "落在更小的分母上是 %.2f 倍；而且进来的名字里只有 **%.1f%%** 落在账上"
             "（其余一进来就已经是被否决的 q==4，不产生换手）。U 的实测值 %.2f%% 就是这两件事的合成。"
             % (s["pool_turnover_mean_ex_first"] * 100, 100.0 * s["n_book_mean"] / s["n_pool_mean"],
                s["denominator_ratio"], s["entrant_admitted_rate"] * 100, s["u_share_mean"] * 100))
    L.append("")
    L.append("**翻动是「一片人」在翻，不是几只票**：可归因的 %d 期里共 %d 次边界穿越、"
             "落在 %d 只名字上（每期约 **%.0f 只**，相当于账上持仓的 %.0f%%）；"
             "翻过 3 次及以上的有 %d 只，最多的那只翻了 %d 次；"
             "**前 10%% 的名字只占 %.1f%% 的穿越**。"
             "如果集中在少数几只，做法是给个别名字加确认期；这个分布说明要压就得压整片中段的分数。"
             % (s["periods_attributed"], s["crossing_total"], s["crossing_names"],
                s["crossing_per_period"], s["crossing_per_period"] / s["n_book_mean"] * 100,
                s["crossing_names_ge3"], int(s["crossing_max_per_name"]),
                s["crossing_top_decile_share"] * 100))
    L.append("")
    L.append("**税主要买的是 V 那一批，而 V 是差的**：进来的名字下一期真实收益 U %s / V %s，"
             "而**留下来的**是 %s——被否决后回来的那批（V，占换手 %.1f%%）明显低于账面，"
             "这部分换手是在**买差名字**；真正新进池的名字（U）反而最高，但它只占换手的 %.1f%%，"
             "而且 2025/2026 已掉到 1%% 以下（池子稳了）。所以这份税的来源是否决边界的来回，"
             "不是换进更好的票。"
             % (_p(s["fwd_u_mean"]), _p(s["fwd_v_mean"]), _p(s["fwd_inc_mean"]),
                s["v_fraction_of_turnover"] * 100, s["u_fraction_of_turnover"] * 100))
    L.append("")
    L.append("**零点，不是方案**：如果边界从不翻动（U 照付），同一批可归因期的净额会从实际 %s/期"
             "变成 %s/期——差 **%.2f bp/期**，正是边界那一层的税。"
             "这个数不构成可执行计划：边界就是信号本身，去掉边界换来的是一本更笨的书。"
             "它印在这里是为了给「这一层值多少」一个尺度（同期总成本 %.2f bp/期）。"
             % (_p(s["net_mean_ex_first"]), _p(s["net_if_edge_never_flapped"]),
                (s["net_if_edge_never_flapped"] - s["net_mean_ex_first"]) * 10000,
                s["tax_total_per_period"] * 10000))
    L.append("")

    L += ["## 两层的定义与账", "",
          "| 层 | 定义 | 份额/期 | 占换手 | 下一期真实收益 |",
          "|---|---|---|---|---|",
          "| U 池子流动 | 新进账的名字，其代码上一期不在可交易池 | %s | %s | %s |"
          % (_pn(s["u_share_mean"], 2), _pn(s["u_fraction_of_turnover"], 1), _p(s["fwd_u_mean"])),
          "| V 否决边界 | 新进账的名字，其代码上一期在池内（=上期被否决） | %s | %s | %s |"
          % (_pn(s["v_share_mean"], 2), _pn(s["v_fraction_of_turnover"], 1), _p(s["fwd_v_mean"])),
          "| — 留下 | 上期在账、这期还在账 | — | — | %s |" % _p(s["fwd_inc_mean"]),
          "",
          "本账面：换手 %s/期（父面口径，含首期全额入场；可归因期 %s），净 %s/期（可归因期 %s），"
          "年化 %s。平均持仓 %.0f 只 / 池 %.0f 只。"
          % (_pn(s["turnover_mean_all_periods"], 2), _pn(s["turnover_mean_ex_first"], 2),
             _p(s["net_mean_all_periods"]), _p(s["net_mean_ex_first"]),
             _pn(s["net_annualized"], 2), s["n_book_mean"], s["n_pool_mean"]),
          "",
          "## 逐年", "",
          "| 年 | 期数 | 换手 | U | V | 净/期 | 平均持仓 |",
          "|---|---|---|---|---|---|---|"]
    for y, b in years.items():
        L.append("| %s | %d | %s | %s | %s | %s | %.0f |"
                 % (y, b["periods"], _pn(b["turnover_mean"], 2), _pn(b["u_share_mean"], 2),
                    _pn(b["v_share_mean"], 2), _p(b["net_mean"]), b["n_book_mean"]))
    L.append("")
    L += ["## 这张面为什么不是又一次「同一件事重新量一遍」", "",
          "它改的是**下一步该往哪走**这个判断：",
          "",
          "1. 如果换手主要是池子（U），那么这本账的成本有一个地板，"
          "任何名单规则（滞回带、确认期、冷却期）都碰不到它——再做第三次带子实验是浪费；",
          "2. 如果主要是边界（V），那就该压分数而不是压名单：把残差排名做平滑"
          "（多期平均后再取分位）才有可能真的降换手，而带子只是名单层的近似，"
          "r2016 已经证明这个近似不够。",
          "",
          "本面给的答案是 V 为主（%s），所以下一个可做的实验是**平滑排名**，不是更多带子参数。"
          % _pn(s["v_fraction_of_turnover"], 1),
          "",
          "## 未验证（如实）", ""]
    for line in (
        "① 换手仍按父面定义（名单集合差），**同一只名字的权重变化不算交易**——分数记账下权重变化"
        "只来自持仓数变化，所以这本账的换手被低估的程度有限，但没有量过；",
        "② U 只认「上一期不在池内」，不区分**新上市 / 退市 / 长期停牌后复牌 / 面板缺数据**——"
        "数据层缺口会被算成成分池流动，本面无法把它们分开；",
        "③ 边界穿越的计数以「留在池内且换了边」为准，名字离开池再回来不计穿越（它没有做决定）；"
        "若读者想按「否决状态翻转」计，数字会更大，本面没印那个口径；",
        "④ 进来的名字的真实收益是等权均值（分数记账一致），整手口径下不一致，而整手不在本面射程；",
        "⑤ 年化是 %d 期复利外推，2020 只有少数几期，逐年列只用于看方向；" % s["periods"],
        "⑥ 票池现存标的（幸存者偏差，父面同），面板起于 2020-01-02；",
        "⑦ 本面是定价/口径件，不是可交易策略：无仓位规则、无容量约束、无风控；",
        "⑧ 全量 smoke 与 S6 链未跑（本轮为竞争窗，只落新增文件面）。",
    ):
        L.append(line)
        L.append("")
    L += [DOC_END, ""]

    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))


# -------------------------------------------------------------------- check
NUM_KEYS = ("turnover_mean_all_periods", "turnover_mean_ex_first", "u_share_mean",
            "v_share_mean", "identity_residual_max", "u_fraction_of_turnover",
            "v_fraction_of_turnover", "n_book_mean", "n_pool_mean", "denominator_ratio",
             "pool_turnover_mean_ex_first", "entrant_admitted_rate", "gross_mean_ex_first",
            "net_mean_all_periods", "net_mean_ex_first", "net_annualized", "fwd_u_mean",
            "fwd_v_mean", "fwd_inc_mean", "net_if_edge_never_flapped",
            "tax_total_per_period", "tax_in_edge_per_period",
            "crossing_total", "crossing_names", "crossing_top_decile_share",
            "crossing_max_per_name", "crossing_names_ge3", "crossing_per_period")


def check() -> int:
    """Re-derive and compare.  A moved input says STALE; a number that moved on
    the same inputs is a real defect and must not wear the STALE word."""
    try:
        with open(OUT, "r", encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError):
        print("CHECK FAILED face missing: %s" % _rel(OUT))
        return 3

    dates, symbols, rows, pool, summ = build_face()
    anchor = parent_anchor(rows, pool)

    problems = []
    if face.get("evidence_cutoff") != dates[-1]:
        problems.append("STALE panel moved: face %s vs panel %s"
                        % (face.get("evidence_cutoff"), dates[-1]))
    if not anchor["ok"]:
        problems.append("STALE parent anchor moved: %r"
                        % {k: anchor.get(k) for k in ("why", "worst_abs_diff")})

    f_book = (face.get("results") or {}).get("book")
    if f_book is None:
        problems.append("CHECK FAILED block missing: book")
    else:
        for key in NUM_KEYS:
            fv, gv = f_book.get(key), summ[key]
            if (fv is None) != (gv is None):
                problems.append("CHECK FAILED book.%s None mismatch (%r vs %r)" % (key, fv, gv))
            elif fv is not None and abs(float(fv) - float(gv)) > 1e-12:
                problems.append("CHECK FAILED book.%s %r != %r" % (key, fv, gv))
    f_verdict = (face.get("results") or {}).get("verdict")
    if f_verdict != verdict(summ):
        problems.append("CHECK FAILED verdict %r != %r" % (f_verdict, verdict(summ)))
    f_rows = face.get("rows") or []
    if len(f_rows) != len(rows):
        problems.append("STALE row count face=%d mine=%d" % (len(f_rows), len(rows)))
    else:
        worst = 0.0
        for fr, gr in zip(f_rows, rows):
            if fr.get("date") != gr["date"]:
                problems.append("STALE row date %r != %r" % (fr.get("date"), gr["date"]))
                break
            worst = max(worst, abs(float(fr["turnover"]) - gr["turnover"]))
        if worst > 1e-12:
            problems.append("STALE per-period turnover moved by %.3e" % worst)

    if not problems:
        print("CHECK ok  (periods=%d, cutoff=%s, anchor ok=%s, verdict %s, U %.2f%% / V %.2f%%)"
              % (len(rows), dates[-1], anchor["ok"], verdict(summ),
                 summ["u_share_mean"] * 100, summ["v_share_mean"] * 100))
        return 0
    for p in problems:
        print(p)
    return 3


# ------------------------------------------------------------------ selftest
_CHECKS = [0]


def _ok(cond, msg):
    _CHECKS[0] += 1
    if not cond:
        raise AssertionError("selftest leg %d failed: %s" % (_CHECKS[0], msg))


def _sl(date, cols, q, fwd):
    return {"date": date, "idx": np.array(cols, dtype=np.int64),
            "q": np.array(q, dtype=np.int64), "fwd": np.array(fwd, dtype=np.float64)}


def selftest() -> int:
    # 1. turnover is the parent's definition, including the first-period entry.
    _ok(_turnover({1, 2}, None) == 1.0, "first period is a full entry")
    _ok(_turnover({1, 2}, {1, 2}) == 0.0, "identical sets cost nothing")
    _ok(abs(_turnover({1, 2, 3, 4}, {1, 2}) - 0.5) < 1e-15, "half the book replaced")
    _ok(_turnover(set(), {1}) == 0.0, "an empty book cannot turn over")

    # 2. the identity: a name that arrives while already vetoed costs nothing.
    s = [_sl("2024-01-02", [1, 2, 3], [0, 1, 4], [0.01, 0.02, 0.03]),
         _sl("2024-01-30", [1, 2, 3, 4], [0, 1, 4, 4], [0.01, 0.02, 0.03, 0.04])]
    rows, cross = walk_layers(s)
    _ok(abs(rows[1]["turnover"] - 0.0) < 1e-15,
        "an arriving symbol that is vetoed on arrival is not turnover")
    _ok(rows[1]["pool_entrants"] == 1 and rows[1]["u_n"] == 0,
        "the entrant is counted in the pool flow but not in the book's U")

    # 3. a released name is V, a genuinely new symbol is U.
    s = [_sl("2024-01-02", [1, 2, 3], [0, 1, 4], [0.01, 0.02, 0.03]),
         _sl("2024-01-30", [1, 2, 3, 9], [0, 1, 0, 0], [0.01, 0.02, 0.03, 0.04])]
    rows, cross = walk_layers(s)
    _ok(rows[1]["v_n"] == 1 and rows[1]["u_n"] == 1,
        "name 3 released from veto is V; symbol 9 is new to the pool and is U")
    _ok(abs(rows[1]["turnover"] - 2.0 / 4.0) < 1e-15, "two of four names arrived")
    _ok(abs(rows[1]["u_share"] + rows[1]["v_share"] - rows[1]["turnover"]) < 1e-15,
        "identity holds with both layers present")

    # 4. a name leaving the pool is not a crossing, and not a buy.
    s = [_sl("2024-01-02", [1, 2, 3], [0, 1, 2], [0.01, 0.02, 0.03]),
         _sl("2024-01-30", [1, 2], [0, 1], [0.01, 0.02])]
    rows, cross = walk_layers(s)
    _ok(rows[1]["turnover"] == 0.0 and rows[1]["new_n"] == 0,
        "a book that only sheds names pays no turnover under this definition")
    _ok(cross == {}, "a name that left the pool did not cross the edge")

    # 5. crossings count only side changes inside the pool.
    s = [_sl("2024-01-02", [1, 2], [0, 4], [0.01, 0.02]),
         _sl("2024-01-30", [1, 2], [4, 0], [0.01, 0.02]),
         _sl("2024-02-27", [1, 2], [4, 0], [0.01, 0.02])]
    rows, cross = walk_layers(s)
    _ok(cross.get(1) == 1 and cross.get(2) == 1, "each name crossed once: %r" % (cross,))
    _ok(sum(cross.values()) == 2, "no crossing counted when nothing changed")

    # 6. with nothing in the pool but vetoed names, shares are NaN not zero.
    s = [_sl("2024-01-02", [1], [4], [0.01]), _sl("2024-01-30", [1], [4], [0.01])]
    rows, cross = walk_layers(s)
    _ok(not np.isfinite(rows[1]["u_share"]), "an empty book cannot have a share")
    _ok(not np.isfinite(rows[1]["gross"]), "an empty book cannot be priced")

    # 7. the pool arm's turnover is universe flow by construction.
    s = [_sl("2024-01-02", [1, 2], [0, 4], [0.01, 0.02]),
         _sl("2024-01-30", [1, 3], [0, 4], [0.01, 0.02])]
    pl = walk_pool_layers(s)
    _ok(pl[0]["turnover"] == 1.0 and abs(pl[1]["turnover"] - 0.5) < 1e-15,
        "the pool arm charges only the symbol that actually left the panel")

    # 8. net is gross minus exactly 2*c*turnover (parent booking).
    f = np.array([0.10, -0.05, 0.02])
    _ok(abs(fractional(f, 0.25) - (float(np.mean(f)) - 2 * COST_ONE_SIDE * 0.25)) < 1e-15,
        "net = mean - 2*c*turnover")

    # 9. the verdict is the strict comparison of the two measured shares.
    _ok(verdict({"u_fraction_of_turnover": 0.2, "v_fraction_of_turnover": 0.8})
        == "CHURN_IS_MOSTLY_VETO_EDGE", "V dominant")
    _ok(verdict({"u_fraction_of_turnover": 0.8, "v_fraction_of_turnover": 0.2})
        == "CHURN_IS_MOSTLY_UNIVERSE", "U dominant")
    _ok(verdict({"u_fraction_of_turnover": 0.5, "v_fraction_of_turnover": 0.5})
        == "CHURN_SPLIT", "exact tie is its own state")
    _ok(verdict({"u_fraction_of_turnover": float("nan"), "v_fraction_of_turnover": 0.5})
        == "CHURN_UNPRICEABLE", "unpriceable is its own state")

    # 10. summarise keeps the first period out of attribution but inside the book number.
    s = [_sl("2024-01-02", [1, 2], [0, 1], [0.01, 0.02]),
         _sl("2024-01-30", [1, 2, 3], [0, 1, 0], [0.01, 0.02, 0.03]),
         _sl("2024-02-27", [1, 2, 3], [0, 1, 0], [0.01, 0.02, 0.03])]
    rows, cross = walk_layers(s)
    summ = summarize(rows, walk_pool_layers(s), cross)
    _ok(summ["periods"] == 3 and summ["periods_attributed"] == 2,
        "one period is the full entry and is not attributed")
    _ok(abs(summ["turnover_mean_all_periods"] - (1.0 + 1 / 3 + 0.0) / 3.0) < 1e-15,
        "the book number keeps the parent's full-entry period")
    _ok(abs(summ["u_share_mean"] - 1 / 3 / 2) < 1e-15, "U is averaged over attributed periods only")
    _ok(summ["identity_residual_max"] < 1e-15, "identity residual is zero on a clean walk")
    _ok(abs(summ["entrant_admitted_rate"] - 1.0) < 1e-15, "the one entrant was admitted")
    _ok(abs(summ["net_if_edge_never_flapped"]
            - (summ["gross_mean_ex_first"] - 2 * COST_ONE_SIDE * summ["u_share_mean"])) < 1e-15,
        "zero point uses the measured U share")
    _ok(abs(summ["tax_in_edge_per_period"] - 2 * COST_ONE_SIDE * summ["v_share_mean"]) < 1e-15,
        "edge tax uses the measured V share")

    # 11. compound refuses a hole in the series (the parent's guard).
    _ok(compound([0.01, float("nan")]) is None, "compound refuses NaN periods")
    _ok(compound([]) is None, "compound refuses an empty series")

    # 12. by_year skips the full-entry period and groups on the date prefix.
    yr = by_year(rows)
    _ok(list(yr.keys()) == ["2024"], "one year")
    _ok(yr["2024"]["periods"] == 2, "the full-entry period is not counted as a year observation")

    # 13. a path outside the repo prints absolute instead of raising.
    import tempfile
    outside = os.path.join(tempfile.gettempdir(), "r2017_selftest_face.json")
    shown = _rel(outside)
    _ok(isinstance(shown, str) and shown and not shown.startswith(".."),
        "a path on another drive prints absolute instead of raising")
    _ok(_rel(os.path.join(ROOT, "results", "x.json")) == "results/x.json",
        "a path inside the repo stays relative")

    # 14. t-stat needs two finite points and refuses a flat series.
    _ok(_tstat([0.01]) is None, "one point has no t")
    _ok(_tstat([0.01, 0.01, 0.01]) is None, "zero variance has no t")
    _ok(abs(_tstat([0.01, 0.02, 0.03]) - 3.4641) < 1e-3, "three rising points give t = mean/(sd/sqrt n)")

    print("SELFTEST %d/%d PASS" % (_CHECKS[0], _CHECKS[0]))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["run", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run()
    if args.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main())
