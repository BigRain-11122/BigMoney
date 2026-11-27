#!/usr/bin/env python
"""three_book_wallet_ride -- what holding the wallet actually feels like.

The family already prints the wallet's point estimate: ETF 65% / convertible 35% /
carry 0%, 6.51% a year, Sharpe 1.060, worst year -4.03%. Every reader of that page asks
the same next question, and no face answers it:

    "if I start today, what will I most likely see in a year -- and how bad does it get
     before then?"

A Sharpe ratio is a ratio of two sums; it does not say what the path looks like. This
face re-reads the same three published series (never re-derives a strategy) and measures
the ride instead of the average:

  * every start date, held H bars (60 / 120 / 250 / 500), the distribution of outcomes:
    median, p10, p90, min, max, and the share of starts that lose money;
  * the underwater experience: how many days sit below the previous peak, the longest
    such spell in bars and calendar days, the deepest hole and how long it took to climb
    back out.

Four arms, same rows, same window:

  wallet          the published recommendation [0.65, 0.35, 0.00]
  carry_alone     [0, 0, 1] -- the best single Sharpe of the three (1.445)
  etf_cb_equal    [0.50, 0.50, 0] -- two books at equal risk inside the gate
  ungated         the parent's best_ignoring_gate mix (what the gate blocks)

Honesty this face refuses to bury:
  * every arm carries its own realised vol, so absolute ranges are NOT comparable across
    arms; the comparable reading is range width in the arm's own annual sigmas, which is
    printed beside every row;
  * the whole exercise is within-sample on 2020-2026; the distribution of a past window
    is not a forecast, it is the shape a person would have had to sit through;
  * the wallet arm's numbers must reproduce the parent face's published best_inside_gate
    to the last printed digit -- if they do not, this face is quoting another ruler and
    goes red instead of publishing.
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

FACE = os.path.join(ROOT, "results", "three_book_wallet_ride.json")
DOC = os.path.join(ROOT, "research", "THREE_BOOK_WALLET_RIDE.md")
SCHEMA = "three-book-wallet-ride/v1"
PARENT = "results/three_book_wallet.json"

TZ = timezone(timedelta(hours=8))
ANN_DAYS = 244.0
SEED_CNY = 1_000_000.0
HOLDS = (60, 120, 250, 500)
HANDS = {60: "3m", 120: "6m", 250: "1y", 500: "2y"}

# The parents this face reads through three_book_wallet.load_books(): the same list the
# parent itself stamps, so a panel that moves shows up here as STALE, not as a new verdict.
INPUTS = (
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


# ------------------------------------------------------------------ measurement
def hold_runs(r, h):
    """Total return of every H-bar holding period that this series actually contains.

    The first start is bar 0 (capital 1.0 is the peak before any bar), so a window whose
    H-th bar is the last bar is included -- dropping it would quietly delete the most
    recent start date, which is the one a reader is standing on.
    """
    v = (1.0 + np.asarray(r.values, dtype=float))
    n = len(v)
    if n < h:
        return np.array([])
    c = np.concatenate([[1.0], np.cumprod(v)])
    starts = np.arange(0, n - h + 1)
    return c[starts + h] / c[starts] - 1.0


def _q(a, q):
    return float(np.percentile(a, q)) if len(a) else None


def outcome_band(r, h):
    runs = hold_runs(r, h)
    if len(runs) == 0:
        return {"starts": 0, "status": "short"}
    return {
        "starts": int(len(runs)),
        "median": round(_q(runs, 50), 6),
        "p10": round(_q(runs, 10), 6),
        "p90": round(_q(runs, 90), 6),
        "min": round(float(runs.min()), 6),
        "max": round(float(runs.max()), 6),
        "pct_losing": round(float((runs < 0).mean()), 6),
        "median_cny_on_seed": round(SEED_CNY * _q(runs, 50), 0),
        "p10_cny_on_seed": round(SEED_CNY * _q(runs, 10), 0),
        "p90_cny_on_seed": round(SEED_CNY * _q(runs, 90), 0),
    }


def now_block(r):
    """Where the book stands on the last bar -- the one number a reader acts on today."""
    eq = (1.0 + r.astype(float)).cumprod()
    peak = eq.cummax().clip(lower=1.0)
    hole = eq / peak - 1.0
    highs = np.flatnonzero(np.isclose(eq.values, peak.values, rtol=0.0, atol=1e-12))
    pi = int(highs[-1]) if len(highs) else -1
    return {
        "last_bar": str(eq.index[-1].date()),
        "equity": round(float(eq.iloc[-1]), 6),
        "peak": round(float(peak.iloc[-1]), 6),
        "hole": round(float(hole.iloc[-1]), 6),
        "peak_on": (str(eq.index[pi].date()) if pi >= 0 else None),
        "bars_since_peak": int(len(eq) - 1 - pi) if pi >= 0 else None,
        "days_since_peak": (int((eq.index[-1] - eq.index[pi]).days) if pi >= 0 else None),
        "at_the_deepest_point": bool(abs(float(hole.iloc[-1]) - float(hole.min())) < 1e-12),
    }


def underwater(r):
    """How the path feels: time below the previous high, and the deepest hole in it."""
    eq = (1.0 + r.astype(float)).cumprod()
    peak = pd.concat([pd.Series([1.0]), eq]).cummax().iloc[1:]
    hole = eq / peak - 1.0
    below = (hole < -1e-12).values
    n = len(hole)
    days_below = int(below.sum())
    # longest consecutive run of bars under the old high
    best_len, best_start, cur, cur_start = 0, None, 0, None
    for i in range(n):
        if below[i]:
            if cur == 0:
                cur_start = i
            cur += 1
            if cur > best_len:
                best_len, best_start = cur, cur_start
        else:
            cur = 0
    idx = hole.index
    spell_start = str(idx[best_start].date()) if best_start is not None else None
    spell_end = str(idx[best_start + best_len - 1].date()) if best_start is not None else None
    deepest_at = int(np.argmin(hole.values))
    deepest = float(hole.values[deepest_at])
    # how long after the deepest point the book printed a new high again
    recover_at = None
    for i in range(deepest_at + 1, n):
        if not below[i]:
            recover_at = i
            break
    return {
        "bars": int(n),
        "pct_days_below_peak": round(days_below / n, 6) if n else None,
        "longest_spell_bars": int(best_len),
        "longest_spell_days": (int((idx[best_start + best_len - 1] - idx[best_start]).days)
                               if best_start is not None else None),
        "longest_spell_from": spell_start,
        "longest_spell_to": spell_end,
        "deepest": round(deepest, 6),
        "deepest_on": str(idx[deepest_at].date()),
        "bars_to_recover": (int(recover_at - deepest_at) if recover_at is not None else None),
        "days_to_recover": (int((idx[recover_at] - idx[deepest_at]).days)
                            if recover_at is not None else None),
        "recovered": recover_at is not None,
    }


def band_in_sigmas(band, vol):
    """Range width measured in the arm's own annual sigmas -- the only cross-arm reading.

    Absolute ranges are not comparable across arms (each carries its own vol), so every
    row prints this beside its raw percentiles.
    """
    if not band or band.get("status") == "short" or not vol or vol <= 0:
        return None
    return round((band["p90"] - band["p10"]) / vol, 4)


# ------------------------------------------------------------------ build
def build(write=True, quiet=False):
    import three_book_wallet as W

    pub = {}
    with open(_rp(PARENT), encoding="utf-8") as fh:
        pub = json.load(fh)
    cutoff = pub["evidence_cutoff"]
    best = pub["best_inside_gate"]
    ungated = pub.get("best_ignoring_gate") or {}

    series, metas = W.load_books()
    aligned, idx = W.align(series)
    # Read the parent's window, not today's panel: a bar past the parent's cutoff has not
    # been through the parent's own gate yet, and mixing it in here would silently change
    # the recommendation this face is describing.
    keep = idx <= pd.Timestamp(cutoff)
    idx = idx[keep]
    for k in list(aligned):
        aligned[k] = aligned[k].reindex(idx).astype(float)

    scaled, gains = {}, {}
    for k, s in aligned.items():
        scaled[k], gains[k] = W.vol_scale(s)

    arms = {
        "wallet": list(best["w"]),
        "carry_alone": [0.0, 0.0, 1.0],
        "etf_cb_equal": [0.5, 0.5, 0.0],
    }
    if ungated.get("w"):
        arms["ungated"] = list(ungated["w"])

    out_arms = {}
    for name, w in arms.items():
        r = W.blend(scaled, w).reindex(idx).dropna()
        st = W.stats(r)
        bands = {}
        for h in HOLDS:
            b = outcome_band(r, h)
            b["range_in_own_sigmas"] = band_in_sigmas(b, st.get("vol"))
            bands[HANDS[h]] = b
        out_arms[name] = {
            "w": [round(x, 4) for x in w],
            "label": {
                "wallet": "the published recommendation",
                "carry_alone": "the best single Sharpe of the three",
                "etf_cb_equal": "two books at equal risk inside the gate",
                "ungated": "what the gate blocks (parent best_ignoring_gate)",
            }[name],
            "bars": int(len(r)),
            "cagr": st.get("cagr"),
            "vol": st.get("vol"),
            "sharpe": st.get("sharpe"),
            "maxdd": st.get("maxdd"),
            "worst_year": st.get("worst_year"),
            "neg_years": st.get("neg_years"),
            "pos_months_pct": st.get("pos_months_pct"),
            "hold": bands,
            "underwater": underwater(r),
            "now": now_block(r),
        }

    # ---- identity gate: the wallet arm must be the parent's own printed number
    wl = out_arms["wallet"]
    checks = {
        "cagr": (wl["cagr"], best["cagr"]),
        "sharpe": (wl["sharpe"], best["sharpe"]),
        "vol": (wl["vol"], best["vol"]),
        "maxdd": (wl["maxdd"], best["maxdd"]),
    }
    identity = {k: {"mine": v[0], "published": v[1],
                    "diff": (round(v[0] - v[1], 8) if v[0] is not None else None),
                    "ok": (v[0] is not None and abs(v[0] - v[1]) <= 5e-6)}
                for k, v in checks.items()}
    bars_match = (int(len(idx)) == int(pub["window"]["bars"]))

    y = out_arms["wallet"]["hold"]["1y"]
    two = out_arms["wallet"]["hold"]["2y"]
    uw = out_arms["wallet"]["underwater"]
    nowt = out_arms["wallet"]["now"]

    today_clause = (
        "On the last bar (%s) the book stands %.2f%% below its own high of %.4f set on %s "
        "(%d days ago)%s. "
        % (nowt["last_bar"], nowt["hole"] * 100, nowt["peak"], nowt["peak_on"],
           nowt["days_since_peak"] or 0,
           " -- which is the deepest hole in the whole window, so the worst day of this "
           "book's published life is today" if nowt["at_the_deepest_point"] else ""))

    ratio = None
    if y["p10"] and y["p10"] > 0:
        ratio = round(y["p90"] / y["p10"], 4)

    if y["pct_losing"] <= 0.0:
        verdict = "NO_START_LOST_MONEY_OVER_A_YEAR"
    elif ratio is not None and ratio >= 3.0:
        verdict = "A_YEAR_IS_A_RANGE_NOT_A_NUMBER"
    else:
        verdict = "A_YEAR_IS_MOSTLY_A_NARROW_BAND"

    # ---- the cross-arm reading: does the wallet narrow the band, in its own sigmas?
    sig = {}
    for name in out_arms:
        b = out_arms[name]["hold"]["1y"]
        sig[name] = b.get("range_in_own_sigmas")
    narrower = None
    if sig.get("wallet") is not None and sig.get("carry_alone") is not None:
        narrower = round(sig["carry_alone"] - sig["wallet"], 4)

    sentence = (
        today_clause +
        "Held for a year from every one of %d start dates on the parent's own window, the "
        "recommended wallet returns a median %.2f%% and a middle 80%% between %.2f%% and "
        "%.2f%% on a %.0f seed (%+.0f / %+.0f / %+.0f CNY); %.1f%% of starts end below their "
        "own start, the worst ends at %.2f%%. The path matters more than the average: the book "
        "sits below its previous high on %.0f%% of days, its longest such spell runs %d bars "
        "(%d calendar days, %s to %s), and the deepest hole is %.2f%% on %s"
        "%s. Over two years the median is %.2f%% with %.1f%% of starts losing."
        % (y["starts"], y["median"] * 100, y["p10"] * 100, y["p90"] * 100, SEED_CNY,
           y["median_cny_on_seed"], y["p10_cny_on_seed"], y["p90_cny_on_seed"],
           y["pct_losing"] * 100, y["min"] * 100,
           uw["pct_days_below_peak"] * 100, uw["longest_spell_bars"],
           uw["longest_spell_days"] or 0, uw["longest_spell_from"], uw["longest_spell_to"],
           uw["deepest"] * 100, uw["deepest_on"],
           (", taking %d bars (%d days) to climb back" % (uw["bars_to_recover"], uw["days_to_recover"] or 0)
            if uw["recovered"] else ", never fully recovered inside this window"),
           two["median"] * 100, two["pct_losing"] * 100)
    )

    face = {
        "schema": SCHEMA,
        "face": "results/three_book_wallet_ride.json",
        "generated": _now_iso(),
        "evidence_cutoff": cutoff,
        "window": {
            "first": str(idx[0].date()), "last": str(idx[-1].date()),
            "bars": int(len(idx)),
            "why": ("the parent wallet face's own window, truncated at its evidence_cutoff -- "
                    "a bar the parent has not gated yet cannot be described by this face"),
        },
        "caliber": {
            "seed_cny": SEED_CNY,
            "holds": {HANDS[h]: h for h in HOLDS},
            "scaled_to_8pct_vol_factor": {k: round(v, 6) for k, v in gains.items()},
            "books_are_imported_not_recomputed": True,
            "parent": PARENT,
            "ann_days": ANN_DAYS,
        },
        "arms": out_arms,
        "identity_vs_parent": identity,
        "identity_bars_match": bool(bars_match),
        "today": nowt,
        "band_in_own_sigmas_1y": sig,
        "carry_alone_minus_wallet_sigmas": narrower,
        "verdict": verdict,
        "verdict_detail": {
            "p90_over_p10_1y": ratio,
            "pct_losing_1y": y["pct_losing"],
            "why": ("losing starts exist and the middle 80% is wider than 3x" if verdict == "A_YEAR_IS_A_RANGE_NOT_A_NUMBER"
                    else "no start lost money over a year in this window" if verdict == "NO_START_LOST_MONEY_OVER_A_YEAR"
                    else "some starts lose, but the band is narrow"),
        },
        "sentence": sentence,
        "provenance": {"inputs": {rel: _stamp(rel) for rel in INPUTS}},
        "not_claimed": [
            "the distribution of a past window is not a forecast: this is the shape a person would have sat through, 2020-2026",
            "no strategy is recomputed here -- all three books come from three_book_wallet.load_books(), same primitives the parent uses",
            "the arms carry different realised vol, so their absolute ranges are not comparable; range_in_own_sigmas is the only cross-arm reading printed",
            "carry is the hedged excess, gross of the hedge leg's cost; a real hedge needs a second account (parent caliber, not re-estimated)",
            "no rebalancing cost beyond what each book already books; the wallet's weights are held, not traded",
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
        for k, v in identity.items():
            print("  identity %-7s mine=%.6f published=%.6f %s"
                  % (k, v["mine"] or 0.0, v["published"], "OK" if v["ok"] else "RED"))
    return face


# ------------------------------------------------------------------ render
def _pct(v):
    return "-" if v is None else ("%.2f%%" % (v * 100.0))


def _cny(v):
    return "-" if v is None else ("{:+,.0f}".format(float(v)))


def render_md(face):
    a = face["arms"]
    w = a["wallet"]
    uw = w["underwater"]
    lines = []
    add = lines.append
    add("# 三书钱包：持有它到底是什么感觉")
    add("")
    add("面：`%s` · 脚本：`scripts/three_book_wallet_ride.py` · 证据截止：%s"
        % (face["face"], face["evidence_cutoff"]))
    add("")
    add("> %s" % face["sentence"])
    add("")
    add("## 1. 父面给了数，没给路")
    add("")
    add("`three_book_wallet` 印的是 6.51%/年、夏普 1.060、最差年 -4.03%——三个都是「全窗平均」的"
        "函数。读者真正要问的是另一句：**我从今天开始拿，一年后最可能看到多少，最差呢，中间熬不熬得住。**"
        "本面不重算任何一本书，只把父面那三条已发布的序列按 65/35/0 拼起来，把路径量一遍。")
    add("")
    add("窗口 %s → %s（%d 根 bar）。四条臂、同一批行、同一把尺。" % (
        face["window"]["first"], face["window"]["last"], face["window"]["bars"]))
    add("")
    t = face["today"]
    add("## 2. 今天这只钱包站在哪里")
    add("")
    add("| 量 | 值 |")
    add("|---|---|")
    add("| 最新 bar | %s |" % t["last_bar"])
    add("| 净值（起点=1） | %.4f |" % t["equity"])
    add("| 自身的最高点 | %.4f（%s） |" % (t["peak"], t["peak_on"]))
    add("| 现在离开前高 | **%.2f%%**（%d 个日历天、%d 根 bar） |"
        % (t["hole"] * 100, t["days_since_peak"] or 0, t["bars_since_peak"] or 0))
    add("")
    if t["at_the_deepest_point"]:
        add("**这一格是整窗最深的那一格**：这本书自 2020-01-06 发布以来的最大回撤，就是它今天的样子。"
            "读者不需要等到某个未来的坏日子才体会 -6.72%——它正在发生。")
    else:
        add("今天不是最深的一格（整窗最深 %.2f%% 在 %s）。" % (uw["deepest"] * 100, uw["deepest_on"]))
    add("")
    add("## 3. 持有一年，结果是区间不是数字")
    add("")
    add("| 臂 | 权重 ETF/转债/carry | 年化 | 夏普 | 波动 | 1 年起数 | 中位 | p10 | p90 | 亏钱起点 | 最差 |")
    add("|---|---|---|---|---|---|---|---|---|---|---|")
    for k in ("wallet", "carry_alone", "etf_cb_equal", "ungated"):
        if k not in a:
            continue
        arm = a[k]
        b = arm["hold"]["1y"]
        add("| %s | %.0f%% / %.0f%% / %.0f%% | %s | %.3f | %.2f%% | %d | %s | %s | %s | %.1f%% | %s |"
            % (k, arm["w"][0] * 100, arm["w"][1] * 100, arm["w"][2] * 100,
               _pct(arm["cagr"]), arm["sharpe"] or 0.0, (arm["vol"] or 0.0) * 100,
               b["starts"], _pct(b["median"]), _pct(b["p10"]), _pct(b["p90"]),
               b["pct_losing"] * 100, _pct(b["min"])))
    add("")
    add("**四条臂的波动不一样，所以上表的区间不能横向相减。** 唯一能横着读的是「区间宽度按各自年化波动"
        "折算成几个 sigma」——同一条风险单位下，谁的带子更窄：")
    add("")
    add("| 臂 | 1 年区间宽度（自身 sigma） |")
    add("|---|---|")
    for k, v in face["band_in_own_sigmas_1y"].items():
        add("| %s | %s |" % (k, "-" if v is None else "%.2f" % v))
    add("")
    add("## 4. 换一个持有期，带子怎么变")
    add("")
    add("| 持有期 | 中位 | p10 | p90 | 亏钱起点 | 最差 | 最好 |")
    add("|---|---|---|---|---|---|---|")
    for hand in ("3m", "6m", "1y", "2y"):
        b = w["hold"][hand]
        add("| %s | %s | %s | %s | %.1f%% | %s | %s |"
            % (hand, _pct(b["median"]), _pct(b["p10"]), _pct(b["p90"]),
               b["pct_losing"] * 100, _pct(b["min"]), _pct(b["max"])))
    add("")
    add("## 5. 一百万放进这只钱包，一年后大概看到什么")
    add("")
    b = w["hold"]["1y"]
    add("| 读数 | 金额（元，对 1,000,000 本金） |")
    add("|---|---|")
    add("| p10（十次里最差那次附近） | %s |" % _cny(b["p10_cny_on_seed"]))
    add("| 中位 | %s |" % _cny(b["median_cny_on_seed"]))
    add("| p90（十次里最好那次附近） | %s |" % _cny(b["p90_cny_on_seed"]))
    add("")
    add("## 6. 路有多长：水下时间与爬坑")
    add("")
    add("| 量 | 值 |")
    add("|---|---|")
    add("| 处于前高之下的日子占比 | %.1f%% |" % (uw["pct_days_below_peak"] * 100))
    add("| 最长一段水下 | %d 根 bar（%d 个日历天） |" % (uw["longest_spell_bars"], uw["longest_spell_days"] or 0))
    add("| 那一段 | %s → %s |" % (uw["longest_spell_from"], uw["longest_spell_to"]))
    add("| 最深的坑 | %.2f%%（%s） |" % (uw["deepest"] * 100, uw["deepest_on"]))
    add("| 从坑底爬回前高 | %s |"
        % ("%d 根 bar（%d 天）" % (uw["bars_to_recover"], uw["days_to_recover"] or 0)
           if uw["recovered"] else "本窗内没有再回前高"))
    add("")
    add("## 7. 判词")
    add("")
    add("`%s`" % face["verdict"])
    add("")
    add("依据：1 年期 %.1f%% 的起点是亏的，p90/p10 = %s。这与父面「夏普 1.060」并不矛盾——"
        "夏普是对数收益的比值，区间是路径的形状；同一本书可以既有不错的夏普，又有很宽的带子。"
        % (b["pct_losing"] * 100,
           ("%.2f" % face["verdict_detail"]["p90_over_p10_1y"])
           if face["verdict_detail"]["p90_over_p10_1y"] else "不可算（p10 ≤ 0）"))
    add("")
    add("## 8. 本面不证明什么")
    add("")
    for s in face["not_claimed"]:
        add("- %s" % s)
    add("")
    add("## 9. 复跑与守卫")
    add("")
    add("```")
    add("python scripts\\three_book_wallet_ride.py run       # 重算并写面")
    add("python scripts\\three_book_wallet_ride.py check     # 上游动了=STALE(rc3)；自相矛盾=CHECK FAILED(rc2)")
    add("python scripts\\three_book_wallet_ride.py selftest  # 离线自检")
    add("```")
    add("")
    add("`check` 的三件事：①任何上游面（父面 / 三本书 / 面板）字节或 mtime 变了 → `STALE`；"
        "②钱包臂必须逐位复现父面 `best_inside_gate`（cagr/sharpe/vol/maxdd 容差 5e-6）——"
        "不等说明引用了另一把尺子，=`CHECK FAILED`（不带 STALE 字样）；③bar 数必须等于父面窗口 bar 数。")
    add("")
    return "\n".join(lines) + "\n"


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# ------------------------------------------------------------------ check
def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check(quiet=False):
    global FACE
    path = FACE
    if not os.path.exists(path):
        if not quiet:
            print("check: face missing -> STALE (run it)")
        return 3
    face = _load(path)

    # 1. drift: any input file changed size or mtime since this face was written
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
        # A drift message is a contract word: the chain leg only pays for a re-write when
        # the text says STALE (r1850), so it is printed even in quiet mode.
        print("check: STALE -- upstream moved since this face was written:")
        for d in drift:
            print("  - %s" % d)
        print("  fix: python scripts/three_book_wallet_ride.py run")
        return 3

    # 2. self-consistency: no drift, so any disagreement is a real defect
    bad = []
    for k, v in (face.get("identity_vs_parent") or {}).items():
        if not v.get("ok"):
            bad.append("wallet %s = %r, parent publishes %r" % (k, v.get("mine"), v.get("published")))
    if not face.get("identity_bars_match"):
        bad.append("window bars %r != parent window bars" % (face.get("window", {}).get("bars")))
    for name, arm in (face.get("arms") or {}).items():
        for hand, b in (arm.get("hold") or {}).items():
            if b.get("starts", 0) <= 0:
                bad.append("%s/%s has no start dates" % (name, hand))
            elif not (b["min"] <= b["p10"] <= b["median"] <= b["p90"] <= b["max"] + 1e-12):
                bad.append("%s/%s percentiles are not ordered" % (name, hand))
            elif not (0.0 <= b["pct_losing"] <= 1.0):
                bad.append("%s/%s pct_losing out of range" % (name, hand))
        u = arm.get("underwater") or {}
        if u.get("bars") and not (0.0 <= (u.get("pct_days_below_peak") or 0.0) <= 1.0):
            bad.append("%s underwater share out of range" % name)
        if u.get("deepest") is not None and u["deepest"] > 0:
            bad.append("%s deepest hole is printed as a gain" % name)
    # the verdict must be the one these numbers compute to
    y = face["arms"]["wallet"]["hold"]["1y"]
    ratio = (y["p90"] / y["p10"]) if y["p10"] and y["p10"] > 0 else None
    if y["pct_losing"] <= 0.0:
        want = "NO_START_LOST_MONEY_OVER_A_YEAR"
    elif ratio is not None and ratio >= 3.0:
        want = "A_YEAR_IS_A_RANGE_NOT_A_NUMBER"
    else:
        want = "A_YEAR_IS_MOSTLY_A_NARROW_BAND"
    if face.get("verdict") != want:
        bad.append("verdict %r does not follow the numbers (%r)" % (face.get("verdict"), want))
    if bad:
        print("check: CHECK FAILED -- the face contradicts itself on unchanged inputs:")
        for b in bad:
            print("  - %s" % b)
        return 2
    if not quiet:
        print("check: OK -- no upstream drift; wallet arm reproduces the parent's published "
              "best_inside_gate; verdict %s follows from the printed numbers" % face["verdict"])
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    import io
    from contextlib import redirect_stdout

    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # 1. hold_runs counts the starts a series really has, including the one starting at bar 0
    r = pd.Series([0.01] * 10, index=pd.date_range("2024-01-01", periods=10, freq="D"))
    runs = hold_runs(r, 4)
    leg("hold_runs: every start is counted, bar 0 included", len(runs) == 7)
    leg("hold_runs: a constant +1%% series compounds exactly", abs(runs[0] - (1.01 ** 4 - 1)) < 1e-12)

    # 2. a losing series must be honest about it
    rl = pd.Series([-0.01] * 10, index=pd.date_range("2024-01-01", periods=10, freq="D"))
    b = outcome_band(rl, 4)
    leg("outcome_band: a falling series reports 100% losing starts", b["pct_losing"] == 1.0)

    # 3. short series are named, not silently zeroed
    short = pd.Series([0.01] * 3, index=pd.date_range("2024-01-01", periods=3, freq="D"))
    leg("outcome_band: a series shorter than the hold says so", outcome_band(short, 4).get("status") == "short")

    # 4. underwater: a V shape has one spell of the right length and the right depth
    v = pd.Series([-0.10, -0.10, +0.30], index=pd.date_range("2024-01-01", periods=3, freq="D"))
    u = underwater(v)
    leg("underwater: the deepest hole is -19%%, not -10%%", abs(u["deepest"] + 0.19) < 1e-9)
    leg("underwater: the spell is the two bars under the peak", u["longest_spell_bars"] == 2)

    # 5. a never-declining series has no underwater days
    up = pd.Series([0.01] * 20, index=pd.date_range("2024-01-01", periods=20, freq="D"))
    leg("underwater: a monotone book shows zero days below peak",
        underwater(up)["pct_days_below_peak"] == 0.0)

    # 6. band_in_sigmas refuses to divide by a zero vol
    leg("band_in_sigmas: zero vol yields None, not infinity",
        band_in_sigmas({"p10": 0.0, "p90": 1.0, "status": "ok"}, 0.0) is None)

    # 7. the face on disk passes its own check
    face = _load(FACE)
    leg("face: check() on the published face returns 0", check(quiet=True) == 0)

    # 8. drift is STALE (rc3) and says so
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
    fake2["identity_vs_parent"]["sharpe"]["ok"] = False
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

    # 10. negative control: change one printed number and the verdict must stop matching
    fake3 = json.loads(json.dumps(face))
    fake3["verdict"] = "A_YEAR_IS_A_RANGE_NOT_A_NUMBER" if face["verdict"] != "A_YEAR_IS_A_RANGE_NOT_A_NUMBER" else "NO_START_LOST_MONEY_OVER_A_YEAR"
    try:
        _write(tmp, json.dumps(fake3, ensure_ascii=False))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp)
        leg("negative control: a verdict that does not follow the numbers is caught", rc == 2)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    # 11. unordered percentiles are caught
    fake4 = json.loads(json.dumps(face))
    h = sorted(fake4["arms"]["wallet"]["hold"])[0]
    fake4["arms"]["wallet"]["hold"][h]["median"] = fake4["arms"]["wallet"]["hold"][h]["max"] + 0.5
    try:
        _write(tmp, json.dumps(fake4, ensure_ascii=False))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp)
        leg("percentiles out of order are caught", rc == 2)
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
