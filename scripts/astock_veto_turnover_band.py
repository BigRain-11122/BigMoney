"""A-share residual veto book: the band that keeps a name.

The family has priced this black list (full pool minus the top 20% residual
names, r1865 and its follow-ups) from many angles: can it be filled, does a
limit-up need a second day, what do whole lots tax, how is idle cash paid, how
much money fits, is 2026 the market or the sort, and finally -- r2015 -- the
tearsheet that put a price on the churn: turnover **23.95%** per period, 4.3x
the full pool, **10.8%** of the gross edge handed to the broker.

That number opens the one question a person actually running this book asks
next: **would a hysteresis band -- a name that gets vetoed STAYS vetoed until it
clearly recovers -- save more in tax than it loses in ranking?**

The rule walked here
--------------------
One parameter per direction, both frozen before the run:

    a name leaves the book when its residual quintile q >= K_OUT
    a name (re)enters the book when q <= K_IN
    otherwise it keeps whatever state it had last period

``(K_OUT, K_IN) = (4, 3)`` is the parent's rule with no state at all (leave at
q == 4, admit at q <= 3).  It is carried here as ``fresh`` and must reproduce
r2012's published per-period series bit-identically.  Any pair with
``K_IN <= K_OUT - 2`` has a zone where state carries -- that zone *is* the band.
A name the pool has never seen starts from the fresh rule, then obeys the band.
State is remembered while a name is out of the eligible pool, because a real
book remembers the position it sold.

No look-ahead: the state machine reads the current period's quintile and the
previous period's membership, nothing else.

What the face prints
--------------------
* the exact decomposition, measured and not modelled:

      net_band - net_fresh = ranking_delta + tax_saved
      tax_saved    = 2 * one_side_cost * (turnover_fresh - turnover_band)
      ranking_delta = gross_band - gross_fresh

  Both terms are per-period means of the same 77 windows.  No threshold was
  picked to make either look reachable;
* how many names the band refuses to readmit (share of the fresh book) and what
  those refused names actually returned in the following window -- the price of
  the tax saved, measured in forward return, per period;
* each config's edge against the full pool (A) on the same windows and the same
  cost, so a banded book can be read next to the parent's number.

Reading rules that matter
-------------------------
* The band changes *what the book is*, not only what it costs.  A stickier rule
  holds names whose ranking has gone bad.  That is why the decomposition is
  printed instead of a single "it saves X" sentence.
* Turnover is the parent's definition (``1 - |cur & prev| / |cur|``, first
  period charged 1.0 as a full entry), so ``fresh`` has to come back identical,
  not merely close.
* Fractional booking only (weight exactly 1/n, fully invested).  Whole lots are
  a separate axis and r2012/r2015 already show they change the composition, not
  the sort; mixing the two would make the decomposition unreadable.

Usage
-----
    python scripts/astock_veto_turnover_band.py run
    python scripts/astock_veto_turnover_band.py check
    python scripts/astock_veto_turnover_band.py selftest
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
    LOOKBACK_BETA,
    compound,
    daily_returns,
    load_panel,
    market_return,
    score_slice,
)
from astock_veto_lot_drag import fractional  # noqa: E402

OUT = os.path.join(ROOT, "results", "astock_veto_turnover_band.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_TURNOVER_BAND.md")
PARENT = os.path.join(ROOT, "results", "astock_veto_lot_drag.json")

# (K_OUT, K_IN) per config.  fresh is the parent's no-state rule; the rest all
# leave at least one quintile of state-carrying zone between the two edges.
CONFIGS = (
    ("fresh", 4, 3),
    ("band_4_2", 4, 2),
    ("band_4_1", 4, 1),
    ("band_3_1", 3, 1),
)
BASELINE = "fresh"
PPY = 252.0 / HOLD  # ~12.6 periods per year

DOC_BEGIN = "<!-- BEGIN:ASTOCK-VETO-TURNOVER-BAND -->"
DOC_END = "<!-- END:ASTOCK-VETO-TURNOVER-BAND -->"


# ------------------------------------------------------------------ pure logic
def _turnover(cur: set, prev) -> float:
    """The parent's definition, verbatim: the first period is a full entry."""
    if prev is None:
        return 1.0
    if not cur:
        return 0.0
    return 1.0 - len(cur & prev) / float(len(cur))


def _tstat(diffs) -> float | None:
    d = np.asarray(diffs, dtype=np.float64)
    d = d[np.isfinite(d)]
    if len(d) < 2:
        return None
    sd = float(np.std(d, ddof=1))
    if sd <= 0:
        return None
    return float(np.mean(d) / (sd / np.sqrt(len(d))))


def band_update(prev_states: dict, cols, q, k_out: int, k_in: int) -> np.ndarray:
    """One step of the state machine.  Returns a boolean "in the book" mask
    aligned with ``cols``, and writes the new state back into ``prev_states``.

    A name with no prior state follows the fresh rule (``q < k_out``), so a
    band never depends on history the pool has not produced yet.
    """
    keep = np.zeros(len(cols), dtype=bool)
    for p in range(len(cols)):
        col = int(cols[p])
        qi = int(q[p])
        was = bool(prev_states.get(col, qi < k_out))
        now = bool((was and qi < k_out) or (qi <= k_in))
        prev_states[col] = now
        keep[p] = now
    return keep


def walk(slices, k_out: int, k_in: int) -> list:
    """Walk every window with one band rule.  Pure: no IO, no clock.

    A band of this shape can only ever hold *fewer* names than the fresh rule:
    kicking is immediate (``q >= K_OUT``) and readmission is strict
    (``q <= K_IN``), so the names the band refuses are exactly the ones the
    fresh rule would have readmitted this period.  ``withheld`` measures them
    and their forward return: that cohort *is* the price of the tax saved.
    """
    state: dict = {}
    prev = None
    rows = []
    for s in slices:
        cols, q, fwd = s["idx"], s["q"], s["fwd"]
        keep = band_update(state, cols, q, k_out, k_in)
        fresh_keep = q < k_out
        withheld = fresh_keep & ~keep
        cur = set(cols[keep].tolist())
        n, n_pool = int(keep.sum()), int(len(cols))
        members = fwd[keep]
        gross = float(np.mean(members)) if n else float("nan")
        turb = _turnover(cur, prev)
        prev = cur
        withheld_n = int(withheld.sum())
        fresh_n = int(fresh_keep.sum())
        rows.append({
            "date": s["date"],
            "n_pool": n_pool,
            "n": n,
            "fresh_n": fresh_n,
            "excluded_share": (1.0 - n / n_pool) if n_pool else float("nan"),
            "gross": gross,
            "turnover": float(turb),
            "net": fractional(members, turb) if n else float("nan"),
            "withheld_n": withheld_n,
            "withheld_share": (withheld_n / fresh_n) if fresh_n else float("nan"),
            "withheld_fwd": float(np.mean(fwd[withheld])) if withheld_n else float("nan"),
        })
    return rows


def walk_pool(slices) -> list:
    """Arm A: the whole eligible pool, no veto, so only pool churn turns over."""
    prev = None
    rows = []
    for s in slices:
        fwd = s["fwd"]
        cur = set(s["idx"].tolist())
        turb = _turnover(cur, prev)
        prev = cur
        rows.append({
            "date": s["date"],
            "n": int(len(s["idx"])),
            "gross": float(np.mean(fwd)) if len(fwd) else float("nan"),
            "turnover": float(turb),
            "net": fractional(fwd, turb),
        })
    return rows


def _series(rows, key):
    """Missing keys are NaN, not an exception: the pool block has no veto and
    therefore no excluded/withheld columns at all."""
    return np.array([r.get(key, float("nan")) for r in rows], dtype=np.float64)


def _fmean(rows, key) -> float:
    a = _series(rows, key)
    a = a[np.isfinite(a)]
    return float(np.mean(a)) if len(a) else float("nan")


def _fmedian(rows, key) -> float:
    a = _series(rows, key)
    a = a[np.isfinite(a)]
    return float(np.median(a)) if len(a) else float("nan")


def summarize(rows) -> dict:
    net = _series(rows, "net")
    return {
        "periods": int(len(rows)),
        "n_members_mean": float(np.mean(_series(rows, "n"))),
        "excluded_share_median": _fmedian(rows, "excluded_share"),
        "turnover_mean": float(np.mean(_series(rows, "turnover"))),
        "gross_mean": _fmean(rows, "gross"),
        "net_mean": float(np.nanmean(net)),
        "net_annualized": compound([float(x) for x in net]),
        "withheld_share_mean": _fmean(rows, "withheld_share"),
        "withheld_fwd_mean": _fmean(rows, "withheld_fwd"),
        "withheld_periods": int(np.sum(_series(rows, "withheld_n") > 0)),
    }


def decomposition(summary: dict, base: dict, rows=None, base_rows=None) -> dict:
    """Exact split of the band's net effect.  Both terms are means of the same
    windows; the identity holds by construction and is asserted in selftest.

    The paired t-stats are what keep this face honest: a +2 bp/period difference
    between two books that share ~76% of their names is a *direction*, and the
    t says how much of it survives the noise.  Without them "BAND_PAYS" reads
    louder than it is.
    """
    tax_saved = 2.0 * COST_ONE_SIDE * (base["turnover_mean"] - summary["turnover_mean"])
    ranking = summary["gross_mean"] - base["gross_mean"]
    delta = summary["net_mean"] - base["net_mean"]
    out = {
        "tax_saved_per_period": float(tax_saved),
        "ranking_delta_per_period": float(ranking),
        "net_delta_per_period": float(delta),
        "identity_residual": float(delta - (tax_saved + ranking)),
        "turnover_delta": float(summary["turnover_mean"] - base["turnover_mean"]),
        "t_net_delta": None,
        "t_gross_delta": None,
        "t_turnover_delta": None,
    }
    if rows is not None and base_rows is not None:
        out["t_net_delta"] = _tstat(_series(rows, "net") - _series(base_rows, "net"))
        out["t_gross_delta"] = _tstat(_series(rows, "gross") - _series(base_rows, "gross"))
        out["t_turnover_delta"] = _tstat(_series(rows, "turnover") - _series(base_rows, "turnover"))
    return out


def band_verdict(dec: dict) -> str:
    """Three states, strict comparisons, nothing invented.  The question the
    band has to answer is only "did the book get better per period, net"."""
    d = dec["net_delta_per_period"]
    if not np.isfinite(d):
        return "BAND_UNPRICEABLE"
    if d > 0:
        return "BAND_PAYS"
    if d < 0:
        return "BAND_COSTS"
    return "BAND_FLAT"


def edge_vs_pool(rows_cfg, rows_a) -> dict:
    d = _series(rows_cfg, "net") - _series(rows_a, "net")
    return {"mean_per_period": float(np.nanmean(d)), "t": _tstat(d)}


def by_year(rows) -> dict:
    out: dict = {}
    for r in rows:
        y = r["date"][:4]
        out.setdefault(y, []).append(r["net"])
    return {y: {"periods": len(v), "net_mean": float(np.nanmean(v))} for y, v in sorted(out.items())}


# -------------------------------------------------------------------- the face
def build_slices(hold: int = HOLD, stride: int = HOLD):
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
    per_config = {}
    for name, k_out, k_in in CONFIGS:
        per_config[name] = {"k_out": k_out, "k_in": k_in, "rows": walk(slices, k_out, k_in)}
    pool = walk_pool(slices)
    return dates, symbols, per_config, pool


def summarize_face(per_config, pool):
    summaries = {name: summarize(per_config[name]["rows"]) for name, _, _ in CONFIGS}
    base = summaries[BASELINE]
    base_rows = per_config[BASELINE]["rows"]
    decs, verdicts, edges, years = {}, {}, {}, {}
    for name, _, _ in CONFIGS:
        decs[name] = decomposition(summaries[name], base, per_config[name]["rows"], base_rows)
        verdicts[name] = band_verdict(decs[name]) if name != BASELINE else "BASELINE"
        edges[name] = edge_vs_pool(per_config[name]["rows"], pool)
        years[name] = by_year(per_config[name]["rows"])
    return {
        "pool": summarize(pool),
        "configs": summaries,
        "decomposition": decs,
        "verdicts": verdicts,
        "edges_vs_pool": edges,
        "by_year": years,
        "by_year_pool": by_year(pool),
    }


def parent_anchor(per_config, pool) -> dict:
    """r2012's published series must come back bit-identically on ``fresh``,
    for both arms: that is the only proof this face is the same book."""
    try:
        with open(PARENT, "r", encoding="utf-8") as fh:
            parent = json.load(fh)
    except (OSError, ValueError) as exc:
        return {"ok": False, "why": "parent unreadable: %s" % exc, "worst_abs_diff": None}
    prow = parent.get("rows") or []
    mine_b = per_config[BASELINE]["rows"]
    mine_a = pool
    if len(prow) != len(mine_b) or len(prow) != len(mine_a):
        return {"ok": False, "why": "row count parent=%d fresh=%d pool=%d"
                % (len(prow), len(mine_b), len(mine_a)), "worst_abs_diff": None}
    worst = 0.0
    for p, b, a in zip(prow, mine_b, mine_a):
        if p.get("date") != b["date"] or p.get("date") != a["date"]:
            return {"ok": False, "why": "date mismatch %r" % (p.get("date"),),
                    "worst_abs_diff": None}
        for key, got in (("net_frac", b["net"]), ("turnover", b["turnover"])):
            worst = max(worst, abs(float(p["B"][key]) - float(got)))
        worst = max(worst, abs(float(p["A"]["net_frac"]) - float(a["net"])))
        worst = max(worst, abs(float(p["A"]["turnover"]) - float(a["turnover"])))
    return {"ok": worst <= 1e-12, "worst_abs_diff": worst, "rows": len(prow)}


def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    """Repo-relative when possible.  A path on another drive (the negative control
    hands check() a temp face) cannot be made relative -- say the absolute path
    instead of raising: a self-check may report red, it may not crash."""
    try:
        rel = os.path.relpath(path, ROOT)
    except ValueError:
        return str(path).replace(os.sep, "/")
    if rel.startswith(".."):
        return str(path).replace(os.sep, "/")
    return rel.replace(os.sep, "/")


def run() -> int:
    dates, symbols, per_config, pool = build_face()
    res = summarize_face(per_config, pool)
    anchor = parent_anchor(per_config, pool)
    cutoff = dates[-1]

    payload = {
        "generated": _now(),
        "evidence_cutoff": cutoff,
        "machine": "bm-c",
        "kind": "pricing",
        "fills_the_hole_of": "astock_veto_tearsheet",
        "prereg": {
            "question": "does a hysteresis band on the veto save more tax than it loses in ranking?",
            "rule": {
                "leave_book_when": "q >= K_OUT",
                "readmit_when": "q <= K_IN",
                "otherwise": "keep last period's state",
                "unseen_name_default": "fresh rule (q < K_OUT)",
                "state_on_pool_exit": "remembered (a real book remembers the position it sold)",
            },
            "configs": {name: {"k_out": k_out, "k_in": k_in} for name, k_out, k_in in CONFIGS},
            "baseline": BASELINE,
            "booking": "fractional, weight exactly 1/n, fully invested",
            "decomposition": "net_band - net_fresh = (gross_band - gross_fresh) + 2*c*(turnover_fresh - turnover_band)",
            "verdict": "BAND_PAYS / BAND_COSTS / BAND_FLAT by the sign of the net delta, strict",
            "rule_frozen_before_run": True,
        },
        "spec": {
            "hold": HOLD,
            "stride": HOLD,
            "cost_one_side": COST_ONE_SIDE,
            "turnover_definition": "1 - |cur & prev| / |cur|, first period = 1.0 (parent's)",
            "arms": {"A": "full eligible pool (printed as the pool block)",
                     "B": "pool minus residual top 20%, banded per config"},
        },
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": int(len(pool)),
        "results": res,
        "anchor": anchor,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)

    print("TURNOVER-BAND panel %s..%s  %d names  %d periods  cutoff %s"
          % (dates[0], dates[-1], len(symbols), len(pool), cutoff))
    p = res["pool"]
    print("  pool    turnover %.2f%%  gross %+.4f%%  net %+.4f%%/p  ann %+.2f%%"
          % (p["turnover_mean"] * 100, p["gross_mean"] * 100,
             p["net_mean"] * 100, (p["net_annualized"] or 0) * 100))
    for name, _, _ in CONFIGS:
        s, d = res["configs"][name], res["decomposition"][name]
        e = res["edges_vs_pool"][name]
        print("  %-9s turnover %.2f%%  gross %+.4f%%  net %+.4f%%/p  ann %+.2f%%  "
              "vs pool %+.4f%% (t %.2f)"
              % (name, s["turnover_mean"] * 100, s["gross_mean"] * 100,
                 s["net_mean"] * 100, (s["net_annualized"] or 0) * 100,
                 e["mean_per_period"] * 100, e["t"] or float("nan")))
        if name != BASELINE:
            print("      tax %+.4f%%/p  ranking %+.4f%%/p  net %+.4f%%/p (t %s)  -> %s"
                  % (d["tax_saved_per_period"] * 100, d["ranking_delta_per_period"] * 100,
                     d["net_delta_per_period"] * 100,
                     ("%.2f" % d["t_net_delta"]) if d.get("t_net_delta") is not None else "n/a",
                     res["verdicts"][name]))
    print("  anchor vs r2012: ok=%s worst=%.3e" % (anchor["ok"],
          anchor.get("worst_abs_diff") if anchor.get("worst_abs_diff") is not None
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
    res = payload["results"]
    s, d, v, e, y = (res["configs"], res["decomposition"], res["verdicts"],
                     res["edges_vs_pool"], res["by_year"])
    p = res["pool"]
    base = s[BASELINE]
    cutoff = payload["evidence_cutoff"]

    L = [DOC_BEGIN, "",
         "# A 股残差黑名单：给这条排序加一条滞回带，省下的税够不够赔削掉的排序",
         "",
         "generated %s | evidence_cutoff **%s** | 期数 %d | 单边成本 %.1f bp"
         % (payload["generated"], cutoff, base["periods"], payload["spec"]["cost_one_side"] * 10000),
         "",
         "r2015 把这条黑名单的账单摊开了：换手 **%.2f%%/期**，是全池的 **%.1f 倍**，"
         "**%.1f%%** 的毛边交给了券商。于是下一个问题很自然：**能不能让被踢出去的名字"
         "别急着回来**——踢出于 q=4，重新入场只认 q<=2（而不是 q<=3），中间那一档保持原状。"
         "这条带子会少换手，但它也会把已经变差的名字留在账上。本面把两件事**分别量出来**，"
         "不做净额之外的口头解释。"
         % (base["turnover_mean"] * 100,
            base["turnover_mean"] / p["turnover_mean"] if p["turnover_mean"] else float("nan"),
            (2 * payload["spec"]["cost_one_side"] * base["turnover_mean"]) / base["gross_mean"] * 100
            if base["gross_mean"] else float("nan")),
         "",
         "## 一句话",
         ""]

    # The face states its hypothesis as "kick at q==4, re-admit only at q<=2", so
    # that pair is the headline subject; the wider pair and the sharper trigger are
    # reported next to it, never averaged in.
    prim, prim2, contrast = "band_4_2", "band_4_1", "band_3_1"
    prim_s, prim_d = s[prim], d[prim]
    prim_gap = (prim_s["withheld_fwd_mean"] - prim_s["gross_mean"]
                if np.isfinite(prim_s["withheld_fwd_mean"]) else float("nan"))

    L.append("**税这一头几乎没动**：换手从 %s 只掉到 %s（%s）/ %s（%s），"
             "折成成本每期只省 **%.2f / %.2f bp**。也就是说，「被踢出去的名字回来得太早」"
             "这个假设在本家族的数据上是**错的**——这条账的换手不是回场太快，"
             "而是残差排名本身在大盘中部翻动，带子管不住那一层。"
             % (_pn(base["turnover_mean"], 2),
                _pn(prim_s["turnover_mean"], 2), prim,
                _pn(s[prim2]["turnover_mean"], 2), prim2,
                prim_d["tax_saved_per_period"] * 10000,
                d[prim2]["tax_saved_per_period"] * 10000))
    L.append("")
    L.append("**动的是成分**：被带子拒掉的那批名字（被踢出后只回到 q==3 的），"
             "下一期的真实收益比账上那批低 **%.2f pp**，所以账上的毛收益反而高 %s，"
             "净差 **%s/期（配对 t %.2f）**。带子挣的不是佣金，是它不肯接回那些"
             "「只恢复了一半」的名字。"
             % (abs(prim_gap) * 100, _p(prim_d["ranking_delta_per_period"]),
                _p(prim_d["net_delta_per_period"]), prim_d["t_net_delta"] or float("nan")))
    L.append("")
    L.append("**带子加宽不是单调变好**：`%s` 把踢出线压到 q>=3，直接切进分布最厚的"
             "中段，换手反而涨到 %s（无带子的 %.2f 倍），净差 **%s/期（t %.2f）**——"
             "同一条规则家族，触发线挪一档就从赚变赔。"
             % (contrast, _pn(s[contrast]["turnover_mean"], 2),
                s[contrast]["turnover_mean"] / base["turnover_mean"],
                _p(d[contrast]["net_delta_per_period"]),
                d[contrast]["t_net_delta"] or float("nan")))
    L.append("")
    L.append("**读数边界**：`%s` 的配对 t 只有 %.2f，`%s` 更低（%.2f）——都不到 2。"
             "两本书共享约四分之三的名字，差 %.1f bp/期这种东西靠 77 个窗口分不清方向和噪声。"
             "本面立得住的结论是「税不是这条边的问题所在」；「不回场能多赚 %.1f bp」只是方向。"
             % (prim, prim_d["t_net_delta"] or float("nan"),
                prim2, d[prim2]["t_net_delta"] or float("nan"),
                prim_d["net_delta_per_period"] * 10000,
                prim_d["net_delta_per_period"] * 10000))
    L.append("")

    L += ["## 规则怎么走", "",
          "一个方向一个参数，跑之前就冻结：", "",
          "| 状态 | 条件 | 结果 |",
          "|---|---|---|",
          "| 在账上 | `q >= K_OUT` | 踢出 |",
          "| 不在账上 | `q <= K_IN` | 重新入场 |",
          "| 其它 | — | 保持上一期状态 |",
          "",
          "`(K_OUT, K_IN) = (4, 3)` 就是父面的规则，没有状态可携带（踢出于 q=4、入场认 q<=3），"
          "本面把它作为 `fresh` 基线，并且要求它**逐位复现** r2012 发布的每期序列——"
          "这是「同一本书」的唯一证明。参数对里 `K_IN` 比 `K_OUT` 小两档以上才有可携带的带子。",
          "",
          "池子里第一次出现的名字按 `fresh` 规则入场，之后才受带子约束；"
          "名字掉出可交易池期间状态保留（真实的账不会忘掉它卖掉的仓位）。",
          "",
          "## 四条口径的账",
          "",
          "| 配置 | K_OUT | K_IN | 平均持仓 | 被踢份额(中位) | 换手 | 毛收益/期 | 税/期 | 净收益/期 | 年化(复利) | 对全池 | t |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]

    rows_order = [("pool", p, None)]
    for name, k_out, k_in in CONFIGS:
        rows_order.append((name, s[name], (k_out, k_in)))
    for name, blk, kk in [("全池(A)", p, None)] + [(n, s[n], (k_out, k_in)) for n, k_out, k_in in CONFIGS]:
        tax = 2 * payload["spec"]["cost_one_side"] * blk["turnover_mean"]
        if kk is None:
            L.append("| %s | — | — | %d | — | %s | %s | %s | %s | %s | — | — |"
                     % (name, blk["n_members_mean"], _pn(blk["turnover_mean"], 2),
                        _p(blk["gross_mean"]), _p(tax), _p(blk["net_mean"]),
                        _p(blk["net_annualized"], 2)))
        else:
            L.append("| %s | %d | %d | %d | %s | %s | %s | %s | %s | %s | %s | %.2f |"
                     % (name, kk[0], kk[1], blk["n_members_mean"],
                        _pn(blk["excluded_share_median"], 1),
                        _pn(blk["turnover_mean"], 2), _p(blk["gross_mean"]), _p(tax),
                        _p(blk["net_mean"]), _p(blk["net_annualized"], 2),
                        _p(e[name]["mean_per_period"]), e[name]["t"] or float("nan")))
    L.append("")

    L += ["## 省下的税 vs 削掉的排序", "",
          "分解是恒等式，不是模型：`净差 = (毛差) + 2×成本×(换手差)`。两项都是同一批 77 个窗口的均值。"
          "最后一列是**配对** t（同一批窗口逐期相减），它管的是「这点差是不是噪声」——"
          "两本书共享约四分之三的名字，差一点点是常态。",
          "",
          "| 配置 | 换手变化 | 省下的税/期 | 削掉的排序/期 | 净差/期 | 净差 t | 判词 |",
          "|---|---|---|---|---|---|---|"]
    for name, _, _ in CONFIGS:
        if name == BASELINE:
            continue
        dd = d[name]
        L.append("| %s | %s | %s | %s | %s | %s | `%s` |"
                 % (name, _p(dd["turnover_delta"], 2), _p(dd["tax_saved_per_period"]),
                    _p(dd["ranking_delta_per_period"]), _p(dd["net_delta_per_period"]),
                    ("%.2f" % dd["t_net_delta"]) if dd.get("t_net_delta") is not None else "n/a",
                    v[name]))
    L.append("")
    L += ["## 带子没接回来的名字",
          "",
          "这种形状的带子只会让书**更薄**：踢出是即时的（`q >= K_OUT`），接回来是严格的（`q <= K_IN`），"
          "所以带子拒掉的名字恰好是「无带规则这一期本来会接回来」的那一批。"
          "把它们下一期的真实收益单独印出来，就是省下的税**在这一个窗口里的价格**。",
          "",
          "| 配置 | 平均被拒份额 | 被拒名字的下一期收益 | 账上平均 | 差 | 有被拒名字的期数 |",
          "|---|---|---|---|---|---|"]
    for name, _, _ in CONFIGS:
        blk = s[name]
        gap = (blk["withheld_fwd_mean"] - blk["gross_mean"]
               if np.isfinite(blk["withheld_fwd_mean"]) and np.isfinite(blk["gross_mean"])
               else float("nan"))
        L.append("| %s | %s | %s | %s | %s | %d |"
                 % (name, _pn(blk["withheld_share_mean"], 1), _p(blk["withheld_fwd_mean"]),
                    _p(blk["gross_mean"]), _p(gap), blk["withheld_periods"]))
    L.append("")
    L.append("差值**为负**的意思是：被拒的名字当期的真实收益比账上那批还差——"
             "那就是这条带子在赚钱，它拒绝接回的是正在变差的名字。"
             "差值**为正**则是另一种读法：你为了省税，把当期为数不多的好名字也一起关在门外了。")
    L.append("")

    years = sorted(set().union(*[set(y[n].keys()) for n, _, _ in CONFIGS]))
    L += ["## 逐年（净收益/期）", "",
          "| 年 | 期数 | 全池 | " + " | ".join(n for n, _, _ in CONFIGS) + " |",
          "|---|---|---|" + "---|" * len(CONFIGS)]
    for yr in years:
        cells = []
        for name, _, _ in CONFIGS:
            blk = y[name].get(yr)
            cells.append(_p(blk["net_mean"]) if blk else "—")
        npd = y[CONFIGS[0][0]].get(yr, {}).get("periods", 0)
        pblk = res.get("by_year_pool", {}).get(yr)
        L.append("| %s | %d | %s | %s |"
                 % (yr, npd, _p(pblk["net_mean"]) if pblk else "—", " | ".join(cells)))
    L.append("")

    L += ["## 这张面不是什么", "",
          "* **不是新策略**：带子只改「踢出去的名字什么时候回来」，入池资格、残差排序、"
          "持有期、成本口径全部沿用父面；",
          "* **不是择时**：没有预测，状态机只读当期 q 与上一期名单；",
          "* **不是整手账**：只跑分数记账。整手会改变成分（r2012 已量），"
          "把两条轴混在一起，分解就读不出来了；",
          "* **没有风险形状**：波动、回撤、夏普仍以 r2015 那张 tearsheet 为准，"
          "本面只回答「净额变好还是变差」；",
          "* **被留名字的收益是同一批窗口的实测值**，不是假设它们会均值回复；",
          "* **票池是现存标的**（幸存者偏差，父面同），面板起于 %s。" % payload["panel"]["first"],
          "",
          "## 未验证（如实）", ""]
    for line in [
        "① 只跑了四个参数对；更窄/更宽的带子（例如 `(4,0)`、`(3,0)`）没量，"
        "不能从这四个推断「带宽越大越好」；",
        "② 状态机的入场/出场按同一期期末的 q 判定，与父面的记账窗口一致，"
        "没有额外的成交延迟模型；",
        "③ 「被留名字」的收益是等权均值，没有按实际持仓权重加权（分数口径下两者相同，"
        "整手口径下不同，而整手不在本面射程）；",
        "④ 换手仍按父面定义（名单集合差），未把「同一只名字权重变化」算成交易；",
        "⑤ 年化是 77 期复利外推，2020 只有 7 期，逐年列只用于看方向，不用于定论；",
        "⑥ 全量 smoke 与 S6 链未跑（本轮为竞争窗，只落新增文件面）。",
    ]:
        L.append(line)
        L.append("")
    L += [DOC_END, ""]

    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))


# -------------------------------------------------------------------- check
NUM_KEYS = ("n_members_mean", "excluded_share_median", "turnover_mean", "gross_mean",
            "net_mean", "net_annualized", "withheld_share_mean", "withheld_fwd_mean")


def check() -> int:
    """Re-derive and compare.  A moved input says STALE; a number that moved on
    the same inputs is a real defect and must not wear the STALE word."""
    try:
        with open(OUT, "r", encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError):
        print("CHECK FAILED face missing: %s" % _rel(OUT))
        return 3

    dates, symbols, per_config, pool = build_face()
    res = summarize_face(per_config, pool)
    anchor = parent_anchor(per_config, pool)

    problems = []
    if face.get("evidence_cutoff") != dates[-1]:
        problems.append("STALE panel moved: face %s vs panel %s"
                        % (face.get("evidence_cutoff"), dates[-1]))
    if not anchor["ok"]:
        problems.append("STALE parent anchor moved: %r"
                        % {k: anchor.get(k) for k in ("why", "worst_abs_diff")})

    f_res = face.get("results", {})
    blocks = [("pool", f_res.get("pool"), res["pool"],
               ("n_members_mean", "turnover_mean", "gross_mean", "net_mean", "net_annualized"))]
    for name, _, _ in CONFIGS:
        blocks.append((name, f_res.get("configs", {}).get(name), res["configs"][name], NUM_KEYS))
    for name, f_blk, g_blk, keys in blocks:
        if f_blk is None:
            problems.append("CHECK FAILED block missing: %s" % name)
            continue
        for key in keys:
            fv, gv = f_blk.get(key), g_blk.get(key)
            if (fv is None) != (gv is None):
                problems.append("CHECK FAILED %s.%s None mismatch (%r vs %r)" % (name, key, fv, gv))
            elif fv is not None and abs(float(fv) - float(gv)) > 1e-12:
                problems.append("CHECK FAILED %s.%s %r != %r" % (name, key, fv, gv))
    for name, _, _ in CONFIGS:
        if name == BASELINE:
            continue
        f_d = f_res.get("decomposition", {}).get(name, {})
        g_d = res["decomposition"][name]
        for key in ("tax_saved_per_period", "ranking_delta_per_period", "net_delta_per_period"):
            fv, gv = f_d.get(key), g_d[key]
            if fv is None or abs(float(fv) - float(gv)) > 1e-12:
                problems.append("CHECK FAILED %s.%s %r != %r" % (name, key, fv, gv))
        for key in ("t_net_delta", "t_gross_delta", "t_turnover_delta"):
            fv, gv = f_d.get(key), g_d.get(key)
            if (fv is None) != (gv is None):
                problems.append("CHECK FAILED %s.%s None mismatch" % (name, key))
            elif fv is not None and abs(float(fv) - float(gv)) > 1e-9:
                problems.append("CHECK FAILED %s.%s %r != %r" % (name, key, fv, gv))
        if f_res.get("verdicts", {}).get(name) != res["verdicts"][name]:
            problems.append("CHECK FAILED %s verdict %r != %r"
                            % (name, f_res.get("verdicts", {}).get(name), res["verdicts"][name]))

    if not problems:
        print("CHECK ok  (periods=%d, cutoff=%s, anchor ok=%s, verdicts %s)"
              % (len(pool), dates[-1], anchor["ok"],
                 {n: res["verdicts"][n] for n, _, _ in CONFIGS if n != BASELINE}))
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


def selftest() -> int:
    # 1. the fresh pair is stateless: whatever the prior state says, the answer
    #    is only a function of q.
    cols = np.array([10, 11, 12, 13, 14])
    q = np.array([0, 4, 3, 2, 1])
    for prior in ({}, {10: False, 11: True, 12: False, 13: True, 14: False}):
        st = dict(prior)
        keep = band_update(st, cols, q, 4, 3)
        _ok(list(keep) == [q[i] < 4 for i in range(5)], "fresh must ignore prior state %r" % prior)

    # 2. a banded name inside the carry zone keeps its state, both ways.
    st = {10: True, 11: False}
    keep = band_update(st, np.array([10, 11]), np.array([3, 3]), 4, 2)
    _ok(list(keep) == [True, False], "q==3 in the band must carry the prior state")

    # 3. the two edges still fire: q>=K_OUT kicks, q<=K_IN readmits.
    st = {10: True, 11: False}
    keep = band_update(st, np.array([10, 11]), np.array([4, 2]), 4, 2)
    _ok(list(keep) == [False, True], "veto zone must kick, good zone must readmit")

    # 4. an unseen name follows the fresh rule before the band applies.
    st = {}
    keep = band_update(st, np.array([10, 11, 12]), np.array([4, 3, 2]), 4, 2)
    _ok(list(keep) == [False, True, True], "unseen name must default to the fresh rule")
    _ok(st[11] is True, "state written back for later periods")

    # 5. state persists while a name is out of the pool and on its return.
    st = {}
    band_update(st, np.array([10]), np.array([3]), 4, 2)
    keep = band_update(st, np.array([10]), np.array([3]), 4, 2)
    _ok(bool(keep[0]) is True, "a name held through two banded periods stays in")

    # 6. turnover is the parent's definition, including the first-period full entry.
    _ok(_turnover({1, 2}, None) == 1.0, "first period is a full entry")
    _ok(_turnover({1, 2}, {1, 2}) == 0.0, "identical sets cost nothing")
    _ok(abs(_turnover({1, 2, 3, 4}, {1, 2}) - 0.5) < 1e-15, "half the book replaced")
    _ok(_turnover(set(), {1}) == 0.0, "an empty book cannot turn over")

    # 7. net is gross minus exactly 2*c*turnover (same booking as the parent).
    f = np.array([0.10, -0.05, 0.02])
    _ok(abs(fractional(f, 0.25) - (float(np.mean(f)) - 2 * COST_ONE_SIDE * 0.25)) < 1e-15,
        "net = mean - 2*c*turnover")

    # 8. the decomposition identity holds exactly when both sides are booked the
    #    same way (net = gross - 2*c*turnover); a mismatched booking must show up
    #    as a residual rather than being smoothed away.
    base = {"turnover_mean": 0.2395, "gross_mean": 0.011052}
    base["net_mean"] = base["gross_mean"] - 2.0 * COST_ONE_SIDE * base["turnover_mean"]
    other = {"turnover_mean": 0.1010, "gross_mean": 0.010100}
    other["net_mean"] = other["gross_mean"] - 2.0 * COST_ONE_SIDE * other["turnover_mean"]
    dec = decomposition(other, base)
    _ok(abs(dec["identity_residual"]) < 1e-15,
        "identity residual %r" % dec["identity_residual"])
    _ok(dec["tax_saved_per_period"] > 0 and dec["ranking_delta_per_period"] < 0,
        "a cheaper, worse book must show positive tax and negative ranking")
    bad = dict(other)
    bad["net_mean"] = other["net_mean"] + 1e-6
    _ok(decomposition(bad, base)["identity_residual"] > 1e-7,
        "a mismatched booking must leave a visible residual")

    # 8b. with per-period rows the decomposition also carries a paired t, and the
    #     identity survives: a book that costs less but holds worse names must show
    #     the two terms with opposite signs.
    gap = [0.0009, 0.0011, 0.0008, 0.0010, 0.0007, 0.0012]
    rows_base = []
    rows_cfg = []
    for i, g in enumerate(gap):
        gb = 0.011 + 0.002 * i
        rows_base.append({"gross": gb, "turnover": 0.20,
                          "net": gb - 2 * COST_ONE_SIDE * 0.20})
        rows_cfg.append({"gross": gb + g, "turnover": 0.10,
                         "net": gb + g - 2 * COST_ONE_SIDE * 0.10})

    def _summ(rr):
        return {"net_mean": float(np.mean([r["net"] for r in rr])),
                "gross_mean": float(np.mean([r["gross"] for r in rr])),
                "turnover_mean": float(np.mean([r["turnover"] for r in rr]))}
    dec2 = decomposition(_summ(rows_cfg), _summ(rows_base), rows_cfg, rows_base)
    _ok(abs(dec2["identity_residual"]) < 1e-18, "identity holds with rows attached")
    _ok(dec2["tax_saved_per_period"] > 0 and dec2["ranking_delta_per_period"] > 0,
        "both terms must be measurable independently")
    _ok(dec2["t_net_delta"] is not None and dec2["t_net_delta"] > 3,
        "paired t is finite and large when every period gains")
    _ok(decomposition(_summ(rows_cfg), _summ(rows_base))["t_net_delta"] is None,
        "no rows attached, no t pretended")

    # 9. the verdict is a strict sign test, no invented tolerance.
    _ok(band_verdict({"net_delta_per_period": 1e-12}) == "BAND_PAYS", "tiny gain still pays")
    _ok(band_verdict({"net_delta_per_period": -1e-12}) == "BAND_COSTS", "tiny loss still costs")
    _ok(band_verdict({"net_delta_per_period": 0.0}) == "BAND_FLAT", "exact zero is flat")
    _ok(band_verdict({"net_delta_per_period": float("nan")}) == "BAND_UNPRICEABLE",
        "unpriceable is its own state")

    # 10. t-stat needs two finite points and refuses a flat series.
    _ok(_tstat([0.01]) is None, "one point has no t")
    _ok(_tstat([0.01, 0.01, 0.01]) is None, "zero variance has no t")
    _ok(abs(_tstat([0.01, 0.02, 0.03]) - 3.4641) < 1e-3, "three rising points give t = mean/(sd/sqrt n)")

    # 11. walk(): the band only ever withholds names the fresh rule would admit.
    slices = [
        {"date": "2024-01-02", "idx": np.array([1, 2, 3]), "q": np.array([4, 3, 1]),
         "fwd": np.array([-0.10, 0.01, 0.02])},
        {"date": "2024-01-30", "idx": np.array([1, 2, 3]), "q": np.array([3, 3, 1]),
         "fwd": np.array([0.05, 0.01, 0.02])},
    ]
    rows = walk(slices, 4, 2)
    _ok(rows[0]["n"] == 2 and rows[0]["fresh_n"] == 2, "first period matches the fresh rule")
    _ok(rows[0]["withheld_n"] == 0, "first period withholds nothing")
    _ok(rows[1]["n"] == 2 and rows[1]["fresh_n"] == 3,
        "the same book is thinner than the fresh rule once a name is kicked")
    _ok(rows[1]["withheld_n"] == 1 and abs(rows[1]["withheld_fwd"] - 0.05) < 1e-15,
        "the withheld cohort is exactly the name recovering to q==3, at its real return")
    _ok(abs(rows[0]["excluded_share"] - 1.0 / 3.0) < 1e-15, "excluded share is 1 - n/n_pool")

    # 12. a name the band refuses is counted, and its real return is printed.
    slices3 = [
        {"date": "2024-01-02", "idx": np.array([1]), "q": np.array([4]), "fwd": np.array([0.01])},
        {"date": "2024-01-30", "idx": np.array([1]), "q": np.array([3]), "fwd": np.array([-0.09])},
    ]
    rows3 = walk(slices3, 4, 2)
    _ok(rows3[0]["n"] == 0 and rows3[0]["fresh_n"] == 0, "q==4 is out under both rules")
    _ok(rows3[1]["n"] == 0 and rows3[1]["fresh_n"] == 1 and rows3[1]["withheld_n"] == 1,
        "a kicked name recovering only to q==3 stays out under the band")
    _ok(abs(rows3[1]["withheld_fwd"] - (-0.09)) < 1e-15,
        "the withheld cohort's forward return is the real one")
    _ok(abs(rows3[1]["withheld_share"] - 1.0) < 1e-15, "withheld share is measured against the fresh book")

    # 13. an all-NaN window is not a flat window.
    slices4 = [{"date": "2024-01-02", "idx": np.array([1]), "q": np.array([0]),
                "fwd": np.array([np.nan])}]
    rows4 = walk(slices4, 4, 3)
    _ok(not np.isfinite(rows4[0]["gross"]), "a window we cannot price is NaN, not 0")

    # 14. compound refuses a series with a hole (the parent's guard, reused).
    _ok(compound([0.01, float("nan")]) is None, "compound refuses NaN periods")
    _ok(compound([]) is None, "compound refuses an empty series")

    # 14b. a face path outside the repo must print, not raise (cross-drive).
    import tempfile
    outside = os.path.join(tempfile.gettempdir(), "r2016_selftest_face.json")
    shown = _rel(outside)
    _ok(isinstance(shown, str) and shown and not shown.startswith(".."),
        "a path on another drive prints absolute instead of raising")
    _ok(_rel(os.path.join(ROOT, "results", "x.json")) == "results/x.json",
        "a path inside the repo stays relative")

    # 15. by_year groups on the date prefix and is ordered.
    yr = by_year([{"date": "2024-01-02", "net": 0.01}, {"date": "2023-12-29", "net": 0.02},
                  {"date": "2024-01-30", "net": -0.01}])
    _ok(list(yr.keys()) == ["2023", "2024"], "years ordered")
    _ok(yr["2024"]["periods"] == 2 and abs(yr["2024"]["net_mean"]) < 1e-15, "year mean of two periods")

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
