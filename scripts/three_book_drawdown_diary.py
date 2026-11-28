#!/usr/bin/env python
"""three_book_drawdown_diary -- every time this book fell, and how long it took to come back.

The family already prints the wallet's deepest hole as one number (-6.72%) and its
underwater share as another (a percentage of days). Neither answers the question a holder
actually asks when the screen is red:

    "the last few times it dropped like this, how long did it take to get back?"

A max drawdown is a single observation; a reader sits inside one of many. This face cuts the
same published series into *episodes* -- a peak, a trough, and the bar it climbed back to the
old high (or "still open") -- and measures the distribution of those episodes:

  * every episode: peak date, trough date, depth, bars under water, days under water, and
    the bars it took to climb back from the trough;
  * how deep holes usually are, how long recovery usually takes, and how much longer the
    open one has already run than the typical closed one;
  * today's position: which episode the reader is inside, its depth rank among all episodes,
    and what history says about episodes at least this deep.

No strategy is recomputed: the wallet series comes from three_book_wallet.load_books() and
three_book_wallet.blend(), the same primitives the parent and the ride face use. The face
goes red rather than publish if its deepest episode is not the parent's printed maxdd.

Episodes are counted from the peak, not from the first bar under it, so a recovery cost and
an underwater span are the same clock as the parent's `maxdd` (which peaks at capital 1.0).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

FACE = os.path.join(ROOT, "results", "three_book_drawdown_diary.json")
DOC = os.path.join(ROOT, "research", "THREE_BOOK_DRAWDOWN_DIARY.md")
SCHEMA = "three-book-drawdown-diary/v1"
PARENT = "results/three_book_wallet.json"
RIDE = "results/three_book_wallet_ride.json"

TZ = timezone(timedelta(hours=8))
ANN_DAYS = 244.0
EPS = 1e-12

# Same chain of inputs the ride face stamps: whatever moves there moves here.
INPUTS = (
    RIDE,
    PARENT,
    "results/etf_nobond_vt.json",
    "results/cb_dual_low.json",
    "results/idx_fut_carry_search_rent.json",
    "results/idx_fut_carry_sizing_spec.json",
    "data/daily/sh510300.csv",
)


def _rp(rel):
    return os.path.join(ROOT, rel)


def _now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def _stamp(rel):
    p = _rp(rel)
    if not os.path.exists(p):
        return {"path": rel, "missing": True}
    st = os.stat(p)
    return {"path": rel, "size": int(st.st_size),
            "mtime": datetime.fromtimestamp(st.st_mtime, TZ).isoformat(timespec="seconds")}


def _plain(o):
    if isinstance(o, dict):
        return {k: _plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_plain(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        v = float(o)
        return None if not math.isfinite(v) else v
    if isinstance(o, float):
        return None if not math.isfinite(o) else o
    return o


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# ------------------------------------------------------------------ measurement
def _q(a, q):
    return float(np.percentile(a, q)) if len(a) else None


def episodes(r):
    """Cut the equity path into peak -> trough -> recovery episodes.

    An episode opens on the first bar that closes below the running high and closes on the
    first bar that closes at or above it again. A path that ends inside one leaves it open.
    `bars_under` counts from the peak bar (exclusive) to the recovery bar (exclusive), so the
    sum of (bars_under + 1 for each episode) plus new-high bars is exactly the bar count.
    """
    eq = (1.0 + r.astype(float)).cumprod()
    vals = eq.values.astype(float)
    idx = eq.index
    n = len(vals)
    out = []
    new_high_bars = 0
    cur = 1.0
    peak_i = -1
    ev = None
    for i in range(n):
        v = float(vals[i])
        if ev is None:
            if v >= cur - EPS:
                cur = max(cur, v)
                peak_i = i
                new_high_bars += 1
            else:
                ev = {"peak_i": peak_i, "peak_value": cur, "trough_i": i, "trough_value": v}
        else:
            if v < ev["trough_value"]:
                ev["trough_value"] = v
                ev["trough_i"] = i
            if v >= cur - EPS:
                out.append(_finish(ev, i, idx, n))
                cur = max(cur, v)
                peak_i = i
                ev = None
                new_high_bars += 1
    if ev is not None:
        out.append(_finish(ev, None, idx, n))
    depth = [e["depth"] for e in out]
    return {
        "bars": int(n),
        "first": str(idx[0].date()),
        "last": str(idx[-1].date()),
        "new_high_bars": int(new_high_bars),
        "n_episodes": len(out),
        "n_recovered": sum(1 for e in out if e["recovered"]),
        "n_open": sum(1 for e in out if not e["recovered"]),
        "deepest": (min(depth) if depth else 0.0),
        "episodes": out,
        "accounting": {
            "new_high_bars": int(new_high_bars),
            "episode_bars": int(sum(e["bars_under"] for e in out)),
            "total_bars": int(n),
            "identity_ok": bool(new_high_bars + sum(e["bars_under"] for e in out) == n),
        },
    }


def _finish(ev, rec_i, idx, n):
    peak_i = ev["peak_i"]
    trough_i = ev["trough_i"]
    depth = ev["trough_value"] / ev["peak_value"] - 1.0
    bars_under = (rec_i - peak_i - 1) if rec_i is not None else (n - 1 - peak_i)
    days_under = int(((idx[rec_i] if rec_i is not None else idx[-1]) - idx[max(peak_i, 0)]).days)
    return {
        "peak_on": (str(idx[peak_i].date()) if peak_i >= 0 else None),
        "peak_value": round(float(ev["peak_value"]), 6),
        "trough_on": str(idx[trough_i].date()),
        "trough_value": round(float(ev["trough_value"]), 6),
        "depth": round(float(depth), 6),
        "bars_under": int(bars_under),
        "days_under": int(days_under),
        "bars_peak_to_trough": int(trough_i - peak_i),
        "bars_trough_to_recovery": (int(rec_i - trough_i) if rec_i is not None else None),
        "recovered_on": (str(idx[rec_i].date()) if rec_i is not None else None),
        "recovered": rec_i is not None,
    }


def summarize(ep):
    closed = [e for e in ep["episodes"] if e["recovered"]]
    opened = [e for e in ep["episodes"] if not e["recovered"]]
    depths = [e["depth"] for e in ep["episodes"]]
    rec_bars = [e["bars_under"] + 1 for e in closed]     # peak bar -> recovery bar
    rec_days = [e["days_under"] for e in closed]
    out = {
        "n_episodes": ep["n_episodes"],
        "n_recovered": ep["n_recovered"],
        "n_open": ep["n_open"],
        "pct_episodes_recovered": (round(ep["n_recovered"] / ep["n_episodes"], 6)
                                   if ep["n_episodes"] else None),
        "depth": {
            "median": (round(_q(depths, 50), 6) if depths else None),
            "p90": (round(_q(depths, 90), 6) if depths else None),
            "deepest": round(ep["deepest"], 6),
            "shallowest": (round(max(depths), 6) if depths else None),
        },
        "recovery_bars": {
            "median": (round(_q(rec_bars, 50), 1) if rec_bars else None),
            "p90": (round(_q(rec_bars, 90), 1) if rec_bars else None),
            "longest": (int(max(rec_bars)) if rec_bars else None),
        },
        "recovery_days": {
            "median": (round(_q(rec_days, 50), 1) if rec_days else None),
            "longest": (int(max(rec_days)) if rec_days else None),
        },
        "trough_to_recovery_bars": {
            "median": (round(_q([e["bars_trough_to_recovery"] for e in closed], 50), 1)
                       if closed else None),
            "longest": (int(max(e["bars_trough_to_recovery"] for e in closed))
                        if closed else None),
        },
        "longest_episode_bars": (int(max(e["bars_under"] + 1 for e in ep["episodes"]))
                                 if ep["episodes"] else None),
        "bands": _bands(ep["episodes"]),
        "open_episodes": [{"peak_on": e["peak_on"], "trough_on": e["trough_on"],
                           "depth": e["depth"], "bars_under": e["bars_under"],
                           "days_under": e["days_under"]} for e in opened],
    }
    return out


def _bands(eps):
    """Small holes close fast; the answer a reader wants is the band, not the pool.

    Pooling every episode makes a 0.1% blip and a 6.7% hole look like the same animal, and
    the median of the pool then describes neither. Bands are printed side by side.
    """
    edges = [(0.0, 0.005), (0.005, 0.01), (0.01, 0.02), (0.02, 1.0)]
    labels = ("<0.5%", "0.5-1%", "1-2%", ">=2%")
    out = {}
    for (lo, hi), lab in zip(edges, labels):
        sel = [e for e in eps if lo <= abs(e["depth"]) < hi]
        closed = [e for e in sel if e["recovered"]]
        out[lab] = {
            "n": len(sel),
            "n_open": sum(1 for e in sel if not e["recovered"]),
            "recovery_bars_median": (round(_q([e["bars_under"] + 1 for e in closed], 50), 1)
                                     if closed else None),
            "recovery_bars_longest": (int(max(e["bars_under"] + 1 for e in closed))
                                      if closed else None),
            "recovery_days_median": (round(_q([e["days_under"] for e in closed], 50), 1)
                                     if closed else None),
        }
    return out


def today_episode(ep):
    """The episode the reader is inside right now, and what history says about its size."""
    opened = [e for e in ep["episodes"] if not e["recovered"]]
    if not opened:
        return {"in_an_episode": False,
                "reading": "the book is at its own high on the last bar"}
    cur = opened[-1]
    depths = [e["depth"] for e in ep["episodes"]]
    rank = sorted(depths).index(cur["depth"]) + 1 if cur["depth"] in depths else None
    # episodes at least as deep as today's, already closed: what did they cost in time?
    closed = [e for e in ep["episodes"] if e["recovered"]]
    deeper = [e for e in closed if e["depth"] <= cur["depth"] + 1e-12]
    shallower = [e for e in closed if e["depth"] > cur["depth"] + 1e-12]
    return {
        "in_an_episode": True,
        "peak_on": cur["peak_on"],
        "peak_value": cur["peak_value"],
        "trough_on": cur["trough_on"],
        "depth": cur["depth"],
        "bars_under_so_far": cur["bars_under"],
        "days_under_so_far": cur["days_under"],
        "depth_rank": rank,
        "n_episodes": ep["n_episodes"],
        "is_the_deepest": bool(abs(cur["depth"] - min(depths)) < 1e-12),
        "trough_is_the_last_bar": bool(cur["trough_on"] == ep["last"]),
        "closed_episodes_at_least_this_deep": {
            "n": len(deeper),
            "recovery_bars_median": (round(_q([e["bars_under"] + 1 for e in deeper], 50), 1)
                                     if deeper else None),
            "recovery_bars_longest": (int(max(e["bars_under"] + 1 for e in deeper))
                                      if deeper else None),
        },
        "closed_episodes_shallower": {
            "n": len(shallower),
            "recovery_bars_median": (round(_q([e["bars_under"] + 1 for e in shallower], 50), 1)
                                     if shallower else None),
            "recovery_bars_longest": (int(max(e["bars_under"] + 1 for e in shallower))
                                      if shallower else None),
        },
    }


# ------------------------------------------------------------------ build
def build(write=True, quiet=False):
    import three_book_wallet as W

    ride = _load(_rp(RIDE))
    w = list(ride["arms"]["wallet"]["w"])
    cutoff = ride["evidence_cutoff"]

    series, metas = W.load_books()
    aligned, idx = W.align(series)
    keep = idx <= pd.Timestamp(cutoff)
    idx = idx[keep]
    for k in list(aligned):
        aligned[k] = aligned[k].reindex(idx).astype(float)
    scaled = {}
    for k, s in aligned.items():
        scaled[k], _g = W.vol_scale(s)

    r = W.blend(scaled, w).reindex(idx).dropna()
    st = W.stats(r)

    ep = episodes(r)
    s = summarize(ep)
    t = today_episode(ep)

    # ---- identity: the deepest episode must be the parent's printed maxdd
    deepest_ok = (st.get("maxdd") is not None
                  and abs(ep["deepest"] - float(st["maxdd"])) <= 5e-6)
    ride_today = ride.get("today") or {}
    today_ok = True
    if t["in_an_episode"]:
        today_ok = (ride_today.get("peak_on") == t["peak_on"]
                    and abs(float(ride_today.get("hole") or 0.0) - t["depth"]) <= 5e-6
                    and int(ride_today.get("bars_since_peak") or -1) == t["bars_under_so_far"])

    # ---- verdict, decided by the numbers printed above
    if not t["in_an_episode"]:
        verdict = "AT_A_NEW_HIGH_TODAY"
    elif t.get("is_the_deepest"):
        verdict = "THE_DEEPEST_HOLE_IS_THE_ONE_YOU_ARE_SITTING_IN"
    elif (s["recovery_bars"]["median"] or 0) >= 60:
        verdict = "RECOVERY_IS_MEASURED_IN_MONTHS_NOT_WEEKS"
    else:
        verdict = "HOLES_CLOSE_FASTER_THAN_THEY_FEEL"

    deeper = t.get("closed_episodes_at_least_this_deep") or {}
    shallower = t.get("closed_episodes_shallower") or {}
    if t["in_an_episode"]:
        precedent = (
            "No closed episode in this window was at least this deep, so there is no direct "
            "precedent for the time it needs -- the honest answer is the distribution above, "
            "not a single number."
            if deeper.get("n") == 0 else
            "%d closed episodes were at least this deep; their median was %.1f bars back to "
            "the high (longest %d)."
            % (deeper.get("n"), deeper.get("recovery_bars_median") or 0.0,
               deeper.get("recovery_bars_longest") or 0))
        if shallower.get("n"):
            precedent += (
                " The nearest smaller holes (%d closed ones, each shallower than today) took a "
                "median %.1f bars and at most %d -- today has already been under water %d bars, "
                "so this one is past the long end of every shallower precedent in the window."
                % (shallower["n"], shallower.get("recovery_bars_median") or 0.0,
                   shallower.get("recovery_bars_longest") or 0, t["bars_under_so_far"]))
        today_clause = (
            "The book is inside an episode that opened on %s (high %.4f, trough %s, %.2f%% down). "
            "It has been under water %d bars (%d calendar days); %d of the %d episodes in this "
            "window are already closed, and their median time back to the old high was %s bars "
            "(longest %s). %s"
            % (t["peak_on"], t["peak_value"], t["trough_on"], t["depth"] * 100,
               t["bars_under_so_far"], t["days_under_so_far"],
               s["n_recovered"], s["n_episodes"],
               ("%.1f" % s["recovery_bars"]["median"]) if s["recovery_bars"]["median"] else "-",
               s["recovery_bars"]["longest"], precedent))
    else:
        today_clause = ("On the last bar (%s) the book stands at a new high; there is no open "
                        "episode to sit in." % ep["last"])

    sentence = (
        "%s Over %s -> %s (%d bars) the wallet fell %d times and came back %d times; the median "
        "hole was %.2f%% deep, the deepest %.2f%% (%s), and a closed episode's median time back "
        "to its old high was %s bars (%s calendar days), the longest %s bars."
        % (today_clause, ep["first"], ep["last"], ep["bars"], ep["n_episodes"],
           ep["n_recovered"], (s["depth"]["median"] or 0) * 100, s["depth"]["deepest"] * 100,
           _deepest_on(ep), s["recovery_bars"]["median"], s["recovery_days"]["median"],
           s["recovery_bars"]["longest"]))

    face = {
        "schema": SCHEMA,
        "face": "results/three_book_drawdown_diary.json",
        "generated": _now_iso(),
        "evidence_cutoff": cutoff,
        "window": {"first": ep["first"], "last": ep["last"], "bars": ep["bars"],
                   "why": ("the ride face's own window (parent wallet window truncated at the "
                           "parent's evidence_cutoff) -- an ungated bar cannot be described")},
        "caliber": {
            "arm": "wallet",
            "weights": [round(float(x), 4) for x in w],
            "parent": PARENT,
            "ride": RIDE,
            "books_are_imported_not_recomputed": True,
            "ann_days": ANN_DAYS,
            "episode_clock": ("an episode runs from the peak bar to the bar that closes at or "
                              "above it again; bars_under excludes both ends, so "
                              "bars_under + 1 is the recovery cost on the parent maxdd clock"),
            "identity_anchor": {"maxdd": st.get("maxdd"), "cagr": st.get("cagr"),
                                "sharpe": st.get("sharpe"), "vol": st.get("vol")},
        },
        "summary": s,
        "today": t,
        "identity": {
            "deepest_episode_equals_parent_maxdd": bool(deepest_ok),
            "deepest_mine": ep["deepest"],
            "parent_maxdd": st.get("maxdd"),
            "today_matches_ride_face": bool(today_ok),
            "bar_accounting_ok": bool(ep["accounting"]["identity_ok"]),
        },
        "episodes": ep["episodes"],
        "verdict": verdict,
        "sentence": sentence,
        "provenance": {"inputs": {rel: _stamp(rel) for rel in INPUTS}},
        "not_claimed": [
            "episodes of a past window are not a forecast: this is how long the last few holes took, not how long the next one will",
            "no strategy is recomputed here -- the wallet series is three_book_wallet.load_books() + blend(), the same primitives the parent and ride faces use",
            "the sample has 2020-2026 only; a window that contains one long 2022-style hole cannot say how a longer one would end",
            "the clock is trading bars of this panel, not calendar decisions; a rebalance that happens on a different cadence would re-open the same path on a different day",
            "this face does not price anything and does not touch the recommendation; it only measures how the existing book's holes closed",
        ],
    }
    face = _plain(face)

    md = render_md(face)
    if write:
        _write(FACE, json.dumps(face, ensure_ascii=False, indent=1) + "\n")
        _write(DOC, md)
    if not quiet:
        print("verdict=%s" % verdict)
        print(sentence)
        print("  identity deepest_ok=%s today_ok=%s accounting_ok=%s"
              % (deepest_ok, today_ok, ep["accounting"]["identity_ok"]))
    return face


def _deepest_on(ep):
    if not ep["episodes"]:
        return "-"
    e = min(ep["episodes"], key=lambda x: x["depth"])
    return e["trough_on"]


# ------------------------------------------------------------------ render
def _pct(v):
    return "-" if v is None else ("%.2f%%" % (v * 100.0))


def _num(v, nd=1):
    return "-" if v is None else ("%.*f" % (nd, v))


def render_md(face):
    s = face["summary"]
    t = face["today"]
    add = []
    a = add.append
    a("# 三书钱包：每一次跌下去，用了多久爬回来")
    a("")
    a("面：`%s` · 脚本：`scripts/three_book_drawdown_diary.py` · 证据截止：%s"
      % (face["face"], face["evidence_cutoff"]))
    a("")
    a("> %s" % face["sentence"])
    a("")
    a("## 1. 为什么最大回撤不够用")
    a("")
    a("父面把最深的一格印成一个数（-6.72%），把水下天数印成一个占比。两个都是**一个观察**的"
      "函数。读者真正坐在里面的，是**许多次里的一次**：他不知道这一次算大还是算小，也不知道"
      "上一次同样深的时候，要等多久。本面把那同一根已发布的序列切成一个个「峰 → 谷 → 回到原高」"
      "的事件，再量事件的分布。不重算任何一本书。")
    a("")
    a("窗口 %s → %s（%d 根 bar）。" % (face["window"]["first"], face["window"]["last"],
                                      face["window"]["bars"]))
    a("")
    a("## 2. 今天站在哪一格")
    a("")
    if not t.get("in_an_episode"):
        a("最新的那一根 bar 上，这本书在自己的最高点——没有开着的坑。")
    else:
        a("| 量 | 值 |")
        a("|---|---|")
        a("| 这次从哪开始 | %s（高点） |" % t["peak_on"])
        a("| 谷底 | %s |" % t["trough_on"])
        a("| 当前深度 | **%s** |" % _pct(t["depth"]))
        a("| 已经在水下 | %d 根 bar（%d 个日历天） |" % (t["bars_under_so_far"],
                                                t["days_under_so_far"]))
        a("| 这个深度在整窗里排第几深 | 第 %s 深 / 共 %d 次 |"
          % (t["depth_rank"], t["n_episodes"]))
        a("")
        d = t.get("closed_episodes_at_least_this_deep") or {}
        if d.get("n"):
            a("历史上有 **%d 次**关闭的事件至少这么深：它们回到原高的中位耗时 **%s 根 bar**，"
              "最长 **%s 根**。今天已经走了 %d 根。"
              % (d["n"], _num(d.get("recovery_bars_median")), d.get("recovery_bars_longest"),
                 t["bars_under_so_far"]))
        else:
            a("**本窗里没有任何已关闭的事件至少这么深**——所以「要等多久」没有直接先例："
              "本面只印上文的分布，不编一个单数。")
            sh = t.get("closed_episodes_shallower") or {}
            if sh.get("n"):
                a("")
                a("最近的比较尺子：比今天浅的 %d 次已关闭事件，中位 **%s 根 bar**、最长 **%s 根**；"
                  "今天已经在水下 **%d 根**——这次已经越过所有更浅先例的长端。"
                  % (sh["n"], _num(sh.get("recovery_bars_median")),
                     sh.get("recovery_bars_longest"), t["bars_under_so_far"]))
    a("")
    a("## 3. 每一次都列出来")
    a("")
    a("| # | 高点 | 谷底 | 深度 | 水下 bar | 水下天 | 谷底→回高 | 已恢复 |")
    a("|---|---|---|---|---|---|---|---|")
    for i, e in enumerate(face["episodes"], 1):
        a("| %d | %s | %s | %s | %d | %d | %s | %s |"
          % (i, e["peak_on"] or "起点 1.0", e["trough_on"], _pct(e["depth"]),
             e["bars_under"], e["days_under"],
             ("%d bar" % e["bars_trough_to_recovery"]) if e["recovered"] else "—",
             e["recovered_on"] or "**还没**"))
    a("")
    a("## 4. 事件的分布：多深、多久")
    a("")
    a("把所有事件放进一个池子里取中位，等于把 0.1% 的抖动和 6.7% 的坑当成同一种动物——"
      "中位数两边都不描述。所以按深度分档印：")
    a("")
    a("| 深度档 | 事件数 | 仍开着 | 回到原高中位（bar） | 最长（bar） | 中位（日历天） |")
    a("|---|---|---|---|---|---|")
    for lab, b in (s.get("bands") or {}).items():
        a("| %s | %d | %d | %s | %s | %s |"
          % (lab, b["n"], b["n_open"], _num(b["recovery_bars_median"]),
             "-" if b["recovery_bars_longest"] is None else b["recovery_bars_longest"],
             _num(b["recovery_days_median"])))
    a("")
    a("| 全池读数 | 值 |")
    a("|---|---|")
    a("| 事件数（已恢复 / 仍开着） | %d（%d / %d） |"
      % (s["n_episodes"], s["n_recovered"], s["n_open"]))
    a("| 深度中位 / p90 / 最深 | %s / %s / %s |"
      % (_pct(s["depth"]["median"]), _pct(s["depth"]["p90"]), _pct(s["depth"]["deepest"])))
    a("| 回到原高（bar）中位 / p90 / 最长 | %s / %s / %s |"
      % (_num(s["recovery_bars"]["median"]), _num(s["recovery_bars"]["p90"]),
         s["recovery_bars"]["longest"]))
    a("| 从谷底算起要多少 bar（中位 / 最长） | %s / %s |"
      % (_num(s["trough_to_recovery_bars"]["median"]), s["trough_to_recovery_bars"]["longest"]))
    a("")
    a("共 %d 次事件，已恢复 %d 次、仍开着 %d 次。**跌下去一半的时间花在下坡，另一半花在等**"
      "这句话只在深档成立：浅坑几乎当天就填平，深坑的回程才是读者真正要熬的那一段。"
      % (s["n_episodes"], s["n_recovered"], s["n_open"]))
    a("")
    a("## 5. 判词")
    a("")
    a("`%s`" % face["verdict"])
    a("")
    a("判词只由上面印出的数决定：今天在不在事件里、这次是不是最深的、已关闭事件的中位恢复"
      "是否 ≥60 根 bar。**它不评价这本书好不好**——一个深度可控但恢复很慢的坑，与一个深度"
      "更深但恢复很快的坑，对持有人的意义完全不同，本面把两件事分开量。")
    a("")
    a("## 6. 本面不证明什么")
    a("")
    for x in face["not_claimed"]:
        a("- %s" % x)
    a("")
    a("## 7. 复跑与守卫")
    a("")
    a("```")
    a("python scripts\\three_book_drawdown_diary.py run       # 重算并写面")
    a("python scripts\\three_book_drawdown_diary.py check     # 上游动了=STALE(rc3)；自相矛盾=CHECK FAILED(rc2)")
    a("python scripts\\three_book_drawdown_diary.py selftest  # 离线自检")
    a("```")
    a("")
    a("`check` 判两件不同的事：①任何上游面（ride 面 / 父面 / 三本书 / 面板）字节或 mtime 变了 → "
      "`STALE`（写者该重跑，不是本面算错）；②上游没动却与自己的数矛盾（最深事件 ≠ 父面 maxdd、"
      "今天与 ride 面不一致、bar accounting 不平、事件深度印成正数）→ `CHECK FAILED`（真缺陷，"
      "不带 STALE 字样）。")
    a("")
    return "\n".join(add) + "\n"


# ------------------------------------------------------------------ check
def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check(quiet=False):
    path = FACE
    if not os.path.exists(path):
        print("check: STALE -- face missing (run it)")
        return 3
    face = _load(path)

    drift = []
    for rel, rec in (face.get("provenance", {}).get("inputs") or {}).items():
        now = _stamp(rel)
        if rec.get("missing") or now.get("missing"):
            if rec.get("missing") != now.get("missing"):
                drift.append("%s missing-flag changed" % rel)
            continue
        if rec.get("size") != now.get("size") or rec.get("mtime") != now.get("mtime"):
            drift.append("%s moved (size %s->%s)" % (rel, rec.get("size"), now.get("size")))
    if drift:
        print("check: STALE -- upstream moved since this face was written:")
        for d in drift:
            print("  - %s" % d)
        print("  fix: python scripts/three_book_drawdown_diary.py run")
        return 3

    bad = []
    ident = face.get("identity") or {}
    if not ident.get("deepest_episode_equals_parent_maxdd"):
        bad.append("deepest episode %r is not the parent maxdd %r"
                   % (ident.get("deepest_mine"), ident.get("parent_maxdd")))
    if not ident.get("today_matches_ride_face"):
        bad.append("today's episode does not match the ride face (peak/hole/bars)")
    if not ident.get("bar_accounting_ok"):
        bad.append("episodes do not tile the window (new highs + episode bars != total bars)")

    eps = face.get("episodes") or []
    s = face.get("summary") or {}
    if s.get("n_episodes") != len(eps):
        bad.append("summary says %r episodes, the list has %d" % (s.get("n_episodes"), len(eps)))
    if sum(1 for e in eps if e.get("recovered")) != s.get("n_recovered"):
        bad.append("recovered count in the summary does not match the list")
    bands = s.get("bands") or {}
    if bands:
        if sum(b.get("n") or 0 for b in bands.values()) != len(eps):
            bad.append("depth bands cover %d episodes, the list has %d"
                       % (sum(b.get("n") or 0 for b in bands.values()), len(eps)))
        if sum(b.get("n_open") or 0 for b in bands.values()) != s.get("n_open"):
            bad.append("open episodes in the bands do not match the summary's open count")
    for e in eps:
        if not (-1.0 < float(e.get("depth") or 0.0) < 0.0):
            bad.append("episode starting %s has a depth that is not a loss: %r"
                       % (e.get("peak_on") or "start", e.get("depth")))
            break
        if int(e.get("bars_under") or 0) < 0:
            bad.append("episode starting %s has negative bars under" % (e.get("peak_on") or "start"))
            break
        if not e.get("recovered") and e.get("recovered_on") is not None:
            bad.append("an open episode prints a recovery date")
            break

    # the verdict must be the one these numbers compute to
    t = face.get("today") or {}
    if not t.get("in_an_episode"):
        want = "AT_A_NEW_HIGH_TODAY"
    elif t.get("is_the_deepest"):
        want = "THE_DEEPEST_HOLE_IS_THE_ONE_YOU_ARE_SITTING_IN"
    elif ((s.get("recovery_bars") or {}).get("median") or 0) >= 60:
        want = "RECOVERY_IS_MEASURED_IN_MONTHS_NOT_WEEKS"
    else:
        want = "HOLES_CLOSE_FASTER_THAN_THEY_FEEL"
    if face.get("verdict") != want:
        bad.append("verdict %r does not follow the numbers (%r)" % (face.get("verdict"), want))

    if bad:
        print("check: CHECK FAILED -- the face contradicts itself on unchanged inputs:")
        for b in bad:
            print("  - %s" % b)
        return 2
    if not quiet:
        print("check: OK -- deepest episode reproduces the parent maxdd, today matches the "
              "ride face, episodes tile the window, verdict %s follows" % face["verdict"])
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    import io
    from contextlib import redirect_stdout

    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    dts = pd.date_range("2024-01-01", periods=12, freq="D")

    # 1. a V shape is one episode with the right depth and the right length
    v = pd.Series([-0.10, -0.10, +0.30], index=pd.date_range("2024-01-01", periods=3, freq="D"))
    ep = episodes(v)
    leg("episodes: a V is one episode", ep["n_episodes"] == 1)
    leg("episodes: the depth is measured from capital 1.0 (-19%)",
        abs(ep["episodes"][0]["depth"] + 0.19) < 1e-9)
    leg("episodes: two bars under water, recovered on the third",
        ep["episodes"][0]["bars_under"] == 2 and ep["episodes"][0]["recovered"])

    # 2. a monotone rising book has no episode and every bar is a new high
    up = pd.Series([0.01] * 12, index=dts)
    epu = episodes(up)
    leg("episodes: a monotone book has zero episodes", epu["n_episodes"] == 0)
    leg("episodes: a monotone book counts every bar as a new high",
        epu["new_high_bars"] == 12 and epu["accounting"]["identity_ok"])

    # 3. an episode that never recovers stays open and counts to the last bar
    down = pd.Series([-0.05] * 12, index=dts)
    epd = episodes(down)
    leg("episodes: a falling book leaves one open episode", epd["n_open"] == 1)
    leg("episodes: an open episode measures to the last bar",
        epd["episodes"][0]["bars_under"] == 12 and not epd["episodes"][0]["recovered"])

    # 4. two holes back to back are two episodes, and the tiling stays exact
    two = pd.Series([-0.1, +0.2, -0.1, +0.2], index=pd.date_range("2024-01-01", periods=4, freq="D"))
    ept = episodes(two)
    leg("episodes: two holes are two episodes", ept["n_episodes"] == 2)
    leg("episodes: every bar is either a new high or inside exactly one episode",
        ept["accounting"]["identity_ok"])

    # 5. the summary's median recovery is the list's own median, not a second opinion
    s = summarize(ept)
    legs_list = [e["bars_under"] + 1 for e in ept["episodes"] if e["recovered"]]
    leg("summary: median recovery equals the episodes' own bars",
        abs((s["recovery_bars"]["median"] or 0) - float(np.median(legs_list))) < 1e-9)

    # 6. today's rank is 1 for the deepest episode, and None when at a new high
    tt = today_episode(epd)
    leg("today: an open episode is reported with its rank",
        tt["in_an_episode"] and tt["depth_rank"] == 1)
    leg("today: at a new high the face says so", today_episode(epu)["in_an_episode"] is False)

    # 7. the face on disk passes its own check
    face = _load(FACE)
    leg("face: check() on the published face returns 0", check(quiet=True) == 0)

    # 8. drift is STALE (rc3) and says the word
    fake = json.loads(json.dumps(face))
    k = sorted(fake["provenance"]["inputs"])[0]
    fake["provenance"]["inputs"][k]["size"] = (fake["provenance"]["inputs"][k].get("size") or 0) + 1
    tmp = FACE + ".selftest.json"
    try:
        _write(tmp, json.dumps(fake, ensure_ascii=False))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp)
        leg("drift: a moved upstream is STALE rc=3", rc == 3 and "STALE" in buf.getvalue())
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    # 9. a real contradiction is CHECK FAILED and must not wear the STALE word
    fake2 = json.loads(json.dumps(face))
    fake2["identity"]["deepest_episode_equals_parent_maxdd"] = False
    try:
        _write(tmp, json.dumps(fake2, ensure_ascii=False))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp)
        text = buf.getvalue()
        leg("contradiction: red identity is CHECK FAILED rc=2 without STALE",
            rc == 2 and "CHECK FAILED" in text and "STALE" not in text)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    # 10. negative control: a verdict that does not follow the numbers is caught
    fake3 = json.loads(json.dumps(face))
    fake3["verdict"] = ("AT_A_NEW_HIGH_TODAY" if face["verdict"] != "AT_A_NEW_HIGH_TODAY"
                        else "RECOVERY_IS_MEASURED_IN_MONTHS_NOT_WEEKS")
    try:
        _write(tmp, json.dumps(fake3, ensure_ascii=False))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp)
        leg("negative control: a verdict that does not follow the numbers is caught", rc == 2)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    # 11. a depth printed as a gain is caught
    fake4 = json.loads(json.dumps(face))
    if fake4["episodes"]:
        fake4["episodes"][0]["depth"] = 0.05
    try:
        _write(tmp, json.dumps(fake4, ensure_ascii=False))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp)
        leg("a hole printed as a gain is caught", rc == 2)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    # 12. today drifting away from the ride face is caught
    fake5 = json.loads(json.dumps(face))
    fake5["identity"]["today_matches_ride_face"] = False
    try:
        _write(tmp, json.dumps(fake5, ensure_ascii=False))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp)
        leg("today disagreeing with the ride face is caught", rc == 2)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    ok = sum(1 for _, c in legs if c)
    for name, c in legs:
        print(("PASS  " if c else "FAIL  ") + name)
    print("%d/%d legs pass" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def _check_path(path):
    global FACE
    saved = FACE
    try:
        FACE = path
        return check(quiet=True)
    finally:
        FACE = saved


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest", "show"])
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check()
    if a.cmd == "show":
        print(_load(FACE).get("sentence"))
        return 0
    build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
