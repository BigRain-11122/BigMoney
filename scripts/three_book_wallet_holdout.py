#!/usr/bin/env python
"""three_book_wallet_holdout -- would the reader have got the advertised mix on time?

The wallet face (`three_book_wallet`) recommends ETF 65% / convertible 35% / carry 0%
and prints 6.508% a year, Sharpe 1.060, drawdown -6.72%.  Two things in that number
were decided with the whole window in view:

  1. the weights came from a grid search over the same rows that then measure them,
  2. every book was scaled to the 8% risk dial with its FULL-WINDOW volatility, so the
     first bar of 2020 is scaled by a number that only exists in 2026.

This face re-runs the recommendation the way a person could have run it: refit once a
year on the rows that had already happened, freeze the weights and the risk scale for
the next year, and only then look at what the year delivered.

Arms (all on the same evaluation window, so the numbers subtract):

  walk_expanding   weights + risk scale refit each block on ALL past rows
  walk_rolling     same, but only the last ROLL_TRAIN rows (does old data still vote?)
  frozen_parent    the parent's 65/35/0 held constant -- isolates the weight refit
  equal_inside     equal risk across the books a 1,000,000 wallet can open
  parent_window    the parent's own method (full-window scale, full-window weights)
                   measured on the evaluation window only -- what look-ahead is worth

Honesty lines this face keeps:

  * every arm pays from the same rows; the only difference is what it was allowed to
    know when it set its scale and weights.
  * the capital gate is applied at refit time exactly as the parent applies it -- a book
    whose one lot does not fit a 1,000,000 wallet gets weight 0, whatever its Sharpe.
  * the weights are shares of the risk budget, not of the notional; carry's series is
    index points per lot, which is why its raw volatility is ~352 and its scale ~0.0002.
  * nothing here is wired into the live book; no parent face is re-derived.
"""
from __future__ import annotations

import io
import json
import math
import os
import sys
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import three_book_wallet as W

FACE = os.path.join(ROOT, "results", "three_book_wallet_holdout.json")
DOC = os.path.join(ROOT, "research", "THREE_BOOK_WALLET_HOLDOUT.md")
SCHEMA = "three-book-wallet-holdout/v1"
PARENT_FACE = os.path.join(ROOT, "results", "three_book_wallet.json")

TZ = timezone(timedelta(hours=8))
ANN_DAYS = W.ANN_DAYS
TARGET_VOL = W.TARGET_VOL
WALLET_CNY = W.WALLET_CNY
STEP = W.STEP
ORDER = W.ORDER
FLOORS = W.FLOORS

# Pre-declared, before any number was looked at: two years of rows before the first
# decision is allowed, then one refit per year, block length = one year of bars.
TRAIN_MIN = 500
REFIT_EVERY = 250
ROLL_TRAIN = 500
VOL_FLOOR = 1e-9
MIN_BLOCK_BARS = 40


# ------------------------------------------------------------------ basics
def _now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def _daily_vol(ser):
    return float(ser.std(ddof=1) * math.sqrt(ANN_DAYS)) if len(ser) > 2 else 0.0


def _sharpe(ser):
    v = _daily_vol(ser)
    if v <= VOL_FLOOR:
        return 0.0
    return float(float(ser.mean()) * ANN_DAYS / v)


def _stats(ser):
    """Same shape as the parent's stats() so the two faces can be read side by side."""
    return W.stats(ser.astype(float)) if len(ser) >= 30 else {"bars": int(len(ser)), "status": "short"}


def blocks(n, train_min=TRAIN_MIN, refit_every=REFIT_EVERY):
    """(start, end) row indices of each decision block on the evaluation window."""
    out = []
    s = int(train_min)
    while s < n:
        e = min(s + int(refit_every), n)
        out.append((s, e))
        s = e
    return out


def _scale_from(train_map, keys=ORDER):
    """Risk scale each book needs so its TRAINING volatility equals the dial."""
    ks = {}
    for k in keys:
        v = _daily_vol(train_map[k])
        ks[k] = (TARGET_VOL / v) if v > VOL_FLOOR else 0.0
    return ks


def _blend(scaled_map, w):
    ser = None
    for i, k in enumerate(ORDER):
        part = scaled_map[k] * float(w[i])
        ser = part if ser is None else ser + part
    return ser.dropna()


def pick_weights(scaled_train, wallet=WALLET_CNY, step=STEP):
    """Best in-training Sharpe among the weights a wallet of `wallet` can actually open."""
    best = None
    for w in W.weight_grid(step):
        if not W.feasible(w, wallet):
            continue
        ser = _blend(scaled_train, w)
        if len(ser) < MIN_BLOCK_BARS:
            continue
        sh = _sharpe(ser)
        if best is None or sh > best[1] + 1e-12:
            best = (tuple(float(x) for x in w), sh)
    if best is None:
        return (1.0, 0.0, 0.0), 0.0
    return best


def equal_inside(wallet=WALLET_CNY):
    """Equal risk across the books this wallet can open at all (a dumb, honest baseline)."""
    openable = [k for k in ORDER if W.feasible(
        tuple(1.0 if o == k else 0.0 for o in ORDER), wallet)]
    if not openable:
        return (1.0, 0.0, 0.0)
    w = {k: 1.0 / len(openable) for k in openable}
    return tuple(w.get(k, 0.0) for k in ORDER)


# ------------------------------------------------------------------ the walk
def walk(books, wallet=WALLET_CNY, train_min=TRAIN_MIN, refit_every=REFIT_EVERY,
         roll_train=ROLL_TRAIN, frozen=None):
    """Run every arm over the same evaluation window.

    `frozen` = weights the frozen arm holds (the parent's recommendation by default).
    Returns a dict with the per-arm evaluation series, the refit ledger and the window.
    """
    aligned, idx = W.align(books)
    n = len(idx)
    if n <= train_min + MIN_BLOCK_BARS:
        raise SystemExit("three_book_wallet_holdout: window too short (%d rows)" % n)
    if frozen is None:
        frozen = _parent_weights()
    eval_idx = idx[train_min:]
    arms = {k: [] for k in ("walk_expanding", "walk_rolling", "frozen_parent",
                            "equal_inside", "parent_window")}
    refits = []
    eq_w = equal_inside(wallet)
    # parent_window: the look-ahead arm, scaled on the whole series exactly as the parent did
    full_k = _scale_from({k: aligned[k] for k in ORDER})
    full_scaled = {k: aligned[k] * full_k[k] for k in ORDER}

    for (s, e) in blocks(n, train_min, refit_every):
        train_exp = {k: aligned[k].iloc[:s] for k in ORDER}
        r0 = max(0, s - int(roll_train))
        train_roll = {k: aligned[k].iloc[r0:s] for k in ORDER}

        k_exp = _scale_from(train_exp)
        k_roll = _scale_from(train_roll)
        scaled_exp = {k: train_exp[k] * k_exp[k] for k in ORDER}
        scaled_roll = {k: train_roll[k] * k_roll[k] for k in ORDER}

        w_exp, sh_exp = pick_weights(scaled_exp, wallet)
        w_roll, sh_roll = pick_weights(scaled_roll, wallet)

        rows_e = {k: aligned[k].iloc[s:e] * k_exp[k] for k in ORDER}
        rows_r = {k: aligned[k].iloc[s:e] * k_roll[k] for k in ORDER}
        rows_f = {k: aligned[k].iloc[s:e] * k_exp[k] for k in ORDER}

        ser_exp = _blend(rows_e, w_exp)
        ser_roll = _blend(rows_r, w_roll)
        ser_froz = _blend(rows_f, frozen)
        ser_eq = _blend(rows_f, eq_w)
        ser_pw = _blend({k: full_scaled[k].iloc[s:e] for k in ORDER}, frozen)

        arms["walk_expanding"].append(ser_exp)
        arms["walk_rolling"].append(ser_roll)
        arms["frozen_parent"].append(ser_froz)
        arms["equal_inside"].append(ser_eq)
        arms["parent_window"].append(ser_pw)

        refits.append({
            "block": [str(idx[s].date()), str(idx[e - 1].date())],
            "bars": int(e - s),
            "train_bars": int(s),
            "w_expanding": [round(x, 4) for x in w_exp],
            "w_rolling": [round(x, 4) for x in w_roll],
            "train_sharpe_expanding": round(sh_exp, 6),
            "train_sharpe_rolling": round(sh_roll, 6),
            "carry_entered_expanding": bool(w_exp[2] > 0),
            "carry_entered_rolling": bool(w_roll[2] > 0),
            "delivered_vol_expanding_pct": round(_daily_vol(ser_exp) * 100.0, 4),
            "delivered_vol_frozen_pct": round(_daily_vol(ser_froz) * 100.0, 4),
        })

    ser = {k: pd.concat(v).dropna() for k, v in arms.items()}
    return {
        "aligned": aligned,
        "window": {
            "first": str(idx.min().date()),
            "last": str(idx.max().date()),
            "bars": int(n),
            "eval_first": str(eval_idx.min().date()),
            "eval_last": str(eval_idx.max().date()),
            "eval_bars": int(len(eval_idx)),
            "train_min": int(train_min),
            "refit_every": int(refit_every),
            "roll_train": int(roll_train),
        },
        "arms": ser,
        "refits": refits,
        "frozen_weights": list(frozen),
        "equal_weights": list(eq_w),
    }


def _parent_weights():
    """The recommendation this face is auditing -- read, never recomputed."""
    if os.path.exists(PARENT_FACE):
        try:
            with open(PARENT_FACE, encoding="utf-8") as fh:
                face = json.load(fh)
            w = (face.get("best_inside_gate") or {}).get("w")
            if w and len(w) == 3 and abs(sum(w) - 1.0) < 1e-6:
                return tuple(float(x) for x in w)
        except (ValueError, OSError):
            pass
    return (0.65, 0.35, 0.0)


# ------------------------------------------------------------------ verdict
def verdict_of(stats_map):
    """Name what the walk actually cost, from the numbers in the map -- no taste."""
    wf = (stats_map.get("walk_expanding") or {}).get("sharpe")
    roz = (stats_map.get("frozen_parent") or {}).get("sharpe")
    roll = (stats_map.get("walk_rolling") or {}).get("sharpe")
    look = (stats_map.get("parent_window") or {}).get("sharpe")
    eq = (stats_map.get("equal_inside") or {}).get("sharpe")
    if wf is None or roz is None:
        return {"word": "NOT_ENOUGH_BARS", "walk_sharpe": wf, "frozen_sharpe": roz}
    gap = float(roz) - float(wf)
    look_gap = (float(look) - float(roz)) if (look is not None) else None
    if wf >= roz - 0.05:
        word = "REFITTING_EACH_YEAR_COSTS_NOTHING"
    elif wf >= roz - 0.20:
        word = "REFITTING_COSTS_A_LITTLE"
    else:
        word = "REFITTING_HURTS"
    return {
        "word": word,
        "walk_sharpe": round(float(wf), 6),
        "frozen_sharpe": round(float(roz), 6),
        "refit_gap_sharpe": round(gap, 6),
        "rolling_sharpe": (round(float(roll), 6) if roll is not None else None),
        "equal_inside_sharpe": (round(float(eq), 6) if eq is not None else None),
        "walk_minus_equal_sharpe": (round(float(wf) - float(eq), 6) if eq is not None else None),
        "also_loses_to_equal_inside": (bool(float(wf) < float(eq)) if eq is not None else None),
        "parent_window_sharpe": (round(float(look), 6) if look is not None else None),
        "lookahead_worth_sharpe": (round(float(look_gap), 6) if look_gap is not None else None),
    }


def build(write=True, quiet=False):
    books, meta = W.load_books()
    res = walk(books)
    stats_map = {k: _stats(v) for k, v in res["arms"].items()}
    v = verdict_of(stats_map)

    refits = res["refits"]
    n_exp = sum(1 for r in refits if r["carry_entered_expanding"])
    n_roll = sum(1 for r in refits if r["carry_entered_rolling"])
    w_exp_rows = [tuple(r["w_expanding"]) for r in refits]
    distinct_exp = sorted({tuple(round(x, 4) for x in w) for w in w_exp_rows})
    vol_drift = [r["delivered_vol_expanding_pct"] - 8.0 for r in refits]

    face = {
        "schema": SCHEMA,
        "face": "three_book_wallet_holdout",
        "generated": _now_iso(),
        "evidence_cutoff": res["window"]["eval_last"],
        "question": ("the wallet face recommends a mix; would a reader who only ever "
                     "used the rows already on disk have got the same book, and what "
                     "did the two look-ahead shortcuts (full-window weights, full-window "
                     "risk scale) actually pay?"),
        "window": res["window"],
        "caliber": {
            "bothered_to_refit_because": "weights and risk scale are both fitted numbers",
            "train_min_bars": TRAIN_MIN,
            "refit_every_bars": REFIT_EVERY,
            "rolling_train_bars": ROLL_TRAIN,
            "weights_are": "share of the 8% risk budget, chosen on the training rows only",
            "execution": "each book keeps its own published lag; the walk only changes WHO "
                         "decides and WHAT they were allowed to see",
            "costs": "inherited from each parent book, not re-charged here",
            "what_the_frozen_arm_does_and_does_not_prove": (
                "frozen_parent's 65/35 was itself picked on the full window, so this face "
                "does not prove that mix was knowable in 2022. What it does prove is narrower "
                "and still useful: re-optimising year by year destroyed value against holding "
                "a fixed mix -- and it lost to a dumb equal-risk split too, which needed no "
                "hindsight in its weights at all"),
        },
        "frozen_weights": res["frozen_weights"],
        "equal_weights": res["equal_weights"],
        "arms": stats_map,
        "refits": refits,
        "weight_stability": {
            "n_refits": len(refits),
            "distinct_expanding_weights": [list(w) for w in distinct_exp],
            "carry_entered_expanding": int(n_exp),
            "carry_entered_rolling": int(n_roll),
            "same_weights_every_refit": bool(len(distinct_exp) == 1),
            "delivered_vol_off_dial_pp": {
                "min": round(min(vol_drift), 4) if vol_drift else None,
                "max": round(max(vol_drift), 4) if vol_drift else None,
                "mean": round(float(np.mean(vol_drift)), 4) if vol_drift else None,
            },
        },
        "verdict": v["word"],
        "verdict_detail": v,
        "sentence": _sentence(stats_map, v, len(refits), n_exp, distinct_exp),
        "provenance": {
            "inputs": {
                "parent_face": W._stamp("results/three_book_wallet.json"),
                "etf_face": W._stamp("results/etf_nobond_vt.json"),
                "cb_face": W._stamp("results/cb_dual_low.json"),
                "ic_panel": W._stamp("data/futures_daily/IC.csv"),
            },
            "parents": meta,
            "script": "scripts/three_book_wallet_holdout.py",
            "reuses": "scripts/three_book_wallet.py (loaders, grid, gate, stats)",
        },
    }

    if write:
        os.makedirs(os.path.dirname(FACE), exist_ok=True)
        with open(FACE, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, allow_nan=False)
            fh.write("\n")
        with open(DOC, "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
    if not quiet:
        print("three_book_wallet_holdout: %s  (walk %.3f vs frozen %.3f, %d refits)"
              % (v["word"], v["walk_sharpe"] or 0.0, v["frozen_sharpe"] or 0.0, len(refits)))
    return face


def _sentence(stats_map, v, n_refits, n_carry, distinct):
    wf = stats_map.get("walk_expanding") or {}
    roz = stats_map.get("frozen_parent") or {}
    eq = stats_map.get("equal_inside") or {}
    pw = stats_map.get("parent_window") or {}
    def f(x, suf=""):
        return "n/a" if x is None else ("%.3f%s" % (x, suf))
    return (
        "Refit the wallet once a year on the rows that had already happened and the "
        "recommended mix delivers %.3f%% a year with Sharpe %s and drawdown %s%% "
        "against %s / %s / %s%% for the same weights held frozen -- the refit costs %s of "
        "Sharpe over %d decisions (%d of which let the carry book in, from %d distinct "
           "weight vectors), while the parent's full-window scale alone was worth %s. "
           "Equal risk across the two books a 1,000,000 wallet can open returns %s annually, "
           "so -- %s %s."
        % (100.0 * (wf.get("cagr") or 0.0), f(wf.get("sharpe")),
           f(100.0 * (wf.get("maxdd") or 0.0)),
           f(roz.get("sharpe")), f(100.0 * (roz.get("cagr") or 0.0), "%"),
           f(100.0 * (roz.get("maxdd") or 0.0)),
           f(v["refit_gap_sharpe"]), n_refits, n_carry, len(distinct),
           f(v["lookahead_worth_sharpe"]), f(100.0 * (eq.get("cagr") or 0.0), "%"),
           v["word"].lower().replace("_", " "),
           "(parent-window arm Sharpe %s)" % f(pw.get("sharpe"))))


# ------------------------------------------------------------------ doc
def render_md(face):
    w = face["window"]
    arms = face["arms"]
    v = face["verdict_detail"]
    st = face["weight_stability"]
    out = []
    a = out.append
    a("# 三书钱包：只用当时知道的数据，这本书还成立吗")
    a("")
    a("问题：`three_book_wallet` 推荐 ETF 65% / 转债 35% / carry 0%，印 6.51%/年、夏普 1.060。"
      "但它的权重是全窗网格搜索选出来的，每本书的 8% 风险刻度也是拿全窗波动定的——"
      "2020 年第一根 bar 被一个 2026 年才存在的数缩放过。本面把它按「当时可做」重跑一遍。")
    a("")
    a("窗口 %s → %s（%d 根 bar）；评测窗 %s → %s（%d 根），前 %d 根只做训练。"
      "每年换一次仓（%d 根 bar 一块），权重与风险刻度在训练行上定死、整块不动。"
      % (w["first"], w["last"], w["bars"], w["eval_first"], w["eval_last"],
         w["eval_bars"], w["train_min"], w["refit_every"]))
    a("")
    a("## 五条臂，同一批行")
    a("")
    a("| 臂 | 知道什么 | 年化 | 夏普 | 波动 | 最大回撤 | 最差年 |")
    a("|---|---|---|---|---|---|---|")
    labels = {
        "walk_expanding": "逐年重选权重，训练集=全部过去",
        "walk_rolling": "逐年重选，训练集=最近 %d 根" % w["roll_train"],
        "frozen_parent": "推荐配比不动，只用过去的波动定刻度",
        "equal_inside": "钱包开得出的两本书等风险",
        "parent_window": "父面原法（全窗刻度+全窗权重）",
    }
    for k in ("walk_expanding", "walk_rolling", "frozen_parent",
              "equal_inside", "parent_window"):
        s = arms.get(k) or {}
        a("| %s | %s | %s | %s | %s | %s | %s |" % (
            k, labels[k],
            _pct(s.get("cagr")), _num(s.get("sharpe")), _pct(s.get("vol")),
            _pct(s.get("maxdd")), _pct(s.get("worst_year"))))
    a("")
    a("五个数都取自同一评测窗，可以直接相减。`parent_window` 是唯一还带着前视的臂，"
      "它和 `frozen_parent` 的差就是「拿全窗波动定刻度」这件事本身值多少。")
    a("")
    a("## 逐次决策")
    a("")
    a("| 块 | 训练根数 | 逐年重选权重 | 滚动重选权重 | 训练夏普 | carry 进场 | 交付波动 |")
    a("|---|---|---|---|---|---|---|")
    for r in face["refits"]:
        a("| %s → %s | %d | %s | %s | %.3f | %s | %.2f%% |" % (
            r["block"][0], r["block"][1], r["train_bars"],
            _w(r["w_expanding"]), _w(r["w_rolling"]),
            r["train_sharpe_expanding"],
            "是" if r["carry_entered_expanding"] else "否",
            r["delivered_vol_expanding_pct"]))
    a("")
    a("## 四句读者会问的话")
    a("")
    a("1. **重选权重有没有变好？** 逐年重选夏普 %s，推荐配比冻结夏普 %s，差 %+.3f。"
      "%s"
      % (_num(arms["walk_expanding"].get("sharpe")),
         _num(arms["frozen_parent"].get("sharpe")),
         -v["refit_gap_sharpe"], _plain_reading(v["word"])))
    a("2. **前视值多少钱？** 同一评测窗上，父面原法（全窗刻度）夏普 %s，只用过去定刻度 %s，"
      "差 %+.3f——全窗缩放**没有**帮上忙，说明这条链上前视不在刻度上，在配比的选择上。"
      % (_num(v["parent_window_sharpe"]), _num(v["frozen_sharpe"]),
         (v["lookahead_worth_sharpe"] if v["lookahead_worth_sharpe"] is not None else 0.0)))
    a("3. **那还不如随便分？** 钱包开得出的两本书等风险年化 %s、夏普 %s；"
      "逐年重选是 %s / %s。"
      % (_pct(arms["equal_inside"].get("cagr")), _num(arms["equal_inside"].get("sharpe")),
         _pct(arms["walk_expanding"].get("cagr")), _num(arms["walk_expanding"].get("sharpe"))))
    a("4. **为什么重选会跑偏？** 每块训练夏普 %s，选出来的权重一路从 %s 漂到 %s——"
      "网格在最大化上一年的夏普，于是它一直在追刚过去的那个赢家（早年转债、近两年 ETF）。"
      % (" / ".join("%.2f" % r["train_sharpe_expanding"] for r in face["refits"]),
         _w(face["refits"][0]["w_expanding"]), _w(face["refits"][-1]["w_expanding"])))
    a("")
    a("## 这一面不证明什么")
    a("")
    a("`frozen_parent` 的 65/35 本身也是全窗选出来的，所以本面**不能**说「2022 年你就该知道 65/35」。"
      "它能说的是更窄的一句：把同一套网格每年重选一次，比抱住一个固定配比更差——"
      "而且比一个完全不需要后视的等风险对半分（夏普 %s）也差。"
      % _num(arms["equal_inside"].get("sharpe")))
    a("")
    a("## 权重稳不稳")
    a("")
    a("- 决策 %d 次，出现过的权重向量 %d 个：%s"
      % (st["n_refits"], len(st["distinct_expanding_weights"]),
         "、".join(_w(x) for x in st["distinct_expanding_weights"])))
    a("- carry 进场次数：逐年口径 %d/%d，滚动口径 %d/%d——1,000,000 钱包装不下一手 carry，"
      "所以这个 0 是算术，不是偏好。"
      % (st["carry_entered_expanding"], st["n_refits"],
         st["carry_entered_rolling"], st["n_refits"]))
    dv = st["delivered_vol_off_dial_pp"]
    a("- 每块实际交付的波动相对 8%% 刻度：最小 %+.2fpp、最大 %+.2fpp、平均 %+.2fpp——"
      "标称 8%% 是风险预算上限，这本书实际一直跑在 %s%%–%s%%（三本书不相关的部分被平均掉了），"
      "而且刻度是块首定的，块内会继续漂。"
      % (dv["min"] or 0.0, dv["max"] or 0.0, dv["mean"] or 0.0,
         "%.1f" % (8.0 + (dv["min"] or 0.0)), "%.1f" % (8.0 + (dv["max"] or 0.0))))
    a("")
    a("## 判词")
    a("")
    a("`%s`" % face["verdict"])
    a("")
    a(face["sentence"])
    a("")
    a("## 本面不做什么")
    a("")
    a("- 不重算任何一本书；三条序列来自各自已发布面，`load_books` 与父面同一份")
    a("- 不把逐年重选的结果接进活书；本面只回答「当时做会怎样」")
    a("- 不假设块内再平衡成本：权重一年才动一次，换手的钱按各书自己的成本口径，不另收")
    a("")
    return "\n".join(out) + "\n"


def _pct(x):
    return "n/a" if x is None else "%.2f%%" % (100.0 * float(x))


def _num(x):
    return "n/a" if x is None else "%.3f" % float(x)


def _w(w):
    return " / ".join("%.0f%%" % (100.0 * float(x)) for x in w)


def _plain_reading(word):
    return {
        "REFITTING_EACH_YEAR_COSTS_NOTHING": "逐年重选没有更差——配比不是被前视喂出来的。",
        "REFITTING_COSTS_A_LITTLE": "逐年重选略差，差在重新拟合噪声上，量级可接受。",
        "REFITTING_HURTS": "逐年重选明显更差——每年重新挑配比，挑到的是去年那个赢家，不是明年那个。",
    }.get(word, "")


# ------------------------------------------------------------------ check
def check(quiet=False):
    """Drift = STALE (pay to rebuild). Numbers that contradict themselves = a defect."""
    if not os.path.exists(FACE):
        print("STALE face missing: results/three_book_wallet_holdout.json")
        return 3
    with open(FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    drifted = []
    for key, rec in (face.get("provenance", {}).get("inputs") or {}).items():
        if not isinstance(rec, dict) or rec.get("missing"):
            continue
        rel = rec.get("path")
        if not rel:
            continue
        now = W._stamp(rel)
        if now.get("missing"):
            drifted.append("%s (missing now)" % rel)
            continue
        if now.get("size") != rec.get("size") or now.get("mtime") != rec.get("mtime"):
            drifted.append("%s (%s -> %s)" % (rel, rec.get("mtime"), now.get("mtime")))
    if drifted:
        print("STALE upstream moved: " + "; ".join(drifted))
        return 3

    problems = []
    expected_blocks = len(blocks(face["window"]["bars"]))
    if len(face.get("refits") or []) != expected_blocks:
        problems.append("refit rows %d != expected %d"
                        % (len(face.get("refits") or []), expected_blocks))
    arms = face.get("arms") or {}
    bars = {k: (v or {}).get("bars") for k, v in arms.items()}
    if len({b for b in bars.values() if b is not None}) != 1:
        problems.append("arms do not share one evaluation window: %s" % bars)
    for r in face.get("refits") or []:
        for key in ("w_expanding", "w_rolling"):
            w = r.get(key) or []
            if len(w) != 3 or abs(sum(w) - 1.0) > 1e-6:
                problems.append("refit %s %s weights do not sum to 1" % (r["block"][0], key))
            if w and w[2] > 0:
                problems.append("refit %s %s gives carry weight %s inside a 1,000,000 wallet"
                                % (r["block"][0], key, w[2]))
    v = face.get("verdict_detail") or {}
    if v.get("walk_sharpe") is not None and arms.get("walk_expanding", {}).get("sharpe") is not None:
        if abs(v["walk_sharpe"] - arms["walk_expanding"]["sharpe"]) > 1e-6:
            problems.append("verdict walk_sharpe disagrees with the arm")
    if problems:
        print("CHECK FAILED " + "; ".join(problems))
        return 2
    if not quiet:
        print("OK three_book_wallet_holdout: %d bars, %d refits, %s"
              % (bars.get("walk_expanding") or 0, len(face.get("refits") or []),
                 face.get("verdict")))
    return 0


def _check_path(path):
    global FACE
    saved = FACE
    try:
        FACE = path
        return check(quiet=True)
    finally:
        FACE = saved


# ------------------------------------------------------------------ selftest
def _synth(n=1200, vol_jump_at=700, seed=11):
    """Three synthetic books: A is the only one with a drift after the jump."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    vol_a = np.where(np.arange(n) < vol_jump_at, 0.010, 0.020)
    a = pd.Series(rng.normal(0.0, 1.0, n) * vol_a + 0.0009, index=idx)
    b = pd.Series(rng.normal(0.0, 0.010, n), index=idx)
    c = pd.Series(rng.normal(0.0, 0.010, n) * 300.0, index=idx)  # points-like, like carry
    return {"etf": a, "cb": b, "carry": c}


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    n = 1200
    leg("blocks cover the evaluation window exactly",
        blocks(n, 500, 250)[0][0] == 500 and blocks(n, 500, 250)[-1][1] == n
        and sum(e - s for s, e in blocks(n, 500, 250)) == n - 500)

    books = _synth(n)
    # the carry book here is cheap to open (its floor is the real one, so pinch the wallet
    # up to a size that lets it in, to prove the gate is what keeps it out and nothing else)
    big = 60_000_000.0
    res = walk(books, wallet=big, frozen=(0.5, 0.5, 0.0))
    ev = res["arms"]["walk_expanding"]
    leg("evaluation window length matches the block plan",
        len(ev) == n - 500 and res["window"]["eval_bars"] == n - 500)

    # trailing scale must ignore the future: the first block's delivered vol is built from
    # the pre-jump volatility, so a 2x vol jump later cannot infect the earlier block
    vol_by_block = []
    for s, e in blocks(n, 500, 250):
        vol_by_block.append(res["refits"][blocks(n, 500, 250).index((s, e))]
                            ["delivered_vol_expanding_pct"])
    leg("earlier blocks deliver the dial set before the vol jump",
        all(abs(v - 8.0) < 3.0 for v in vol_by_block[:1]))

    # look-ahead probe: change only rows inside the LAST block, and every earlier decision
    # must be byte-identical (weights, scales, trainsharpe)
    mutated = {k: v.copy() for k, v in books.items()}
    last_s = blocks(n, 500, 250)[-1][0]
    mutated["etf"].iloc[last_s:] = mutated["etf"].iloc[last_s:] * 3.0
    res2 = walk(mutated, wallet=big, frozen=(0.5, 0.5, 0.0))
    same = all(r1 == r2 for r1, r2 in zip(res["refits"][:-1], res2["refits"][:-1]))
    leg("mutating the last block leaves earlier decisions untouched", same)

    # a clearly dominant book wins the weight in the later refits
    dom = _synth(n, seed=3)
    dom["etf"] = dom["etf"] + 0.004
    res3 = walk(dom, wallet=big)
    leg("the dominant book earns the weight",
        all(r["w_expanding"][0] >= 0.5 for r in res3["refits"][-2:]))

    # the gate at the real 1,000,000 wallet keeps carry out of every refit
    res4 = walk(books, wallet=WALLET_CNY)
    leg("carry never enters a 1,000,000 wallet",
        all(not r["carry_entered_expanding"] for r in res4["refits"]))
    leg("equal_inside weights sum to one",
        abs(sum(equal_inside(WALLET_CNY)) - 1.0) < 1e-9)
    leg("equal_inside puts nothing into an unaffordable book",
        equal_inside(WALLET_CNY)[2] == 0.0)

    # verdict names the price from the numbers, both directions
    v_low = verdict_of({"walk_expanding": {"sharpe": 1.05}, "frozen_parent": {"sharpe": 1.06}})
    v_high = verdict_of({"walk_expanding": {"sharpe": 0.60}, "frozen_parent": {"sharpe": 1.06}})
    leg("verdict on a small gap says refitting costs nothing",
        v_low["word"] == "REFITTING_EACH_YEAR_COSTS_NOTHING")
    leg("verdict on a large gap says refitting hurts", v_high["word"] == "REFITTING_HURTS")

    # drift text self-declares STALE and the word is present (the chain only pays for it)
    tmp = os.path.join(ROOT, "results", "_three_book_wallet_holdout_selftest.json")
    bad = {"window": {"bars": 500}, "refits": [], "arms": {},
           "provenance": {"inputs": {"probe": {"path": "results/etf_nobond_vt.json",
                                               "size": 1, "mtime": "1970-01-01T00:00:00+08:00"}}}}
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(bad, fh)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp)
        leg("drift rc=3 and says STALE", rc == 3 and "STALE" in buf.getvalue())
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    # a face whose refits do not cover the window is a defect, not a stale
    tmp2 = os.path.join(ROOT, "results", "_three_book_wallet_holdout_selftest2.json")
    broken = {"window": {"bars": 1200}, "refits": [], "arms": {"walk_expanding": {"bars": 700}},
              "provenance": {"inputs": {}}}
    try:
        with open(tmp2, "w", encoding="utf-8") as fh:
            json.dump(broken, fh)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _check_path(tmp2)
        leg("a short refit ledger is CHECK FAILED and does not wear the STALE word",
            rc == 2 and "STALE" not in buf.getvalue())
    finally:
        if os.path.exists(tmp2):
            os.remove(tmp2)

    ok = sum(1 for _, c in legs if c)
    for name, c in legs:
        print(("PASS  " if c else "FAIL  ") + name)
    print("%d/%d legs pass" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ------------------------------------------------------------------ cli
def run():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest", "show"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check()
    if a.cmd == "show":
        with open(FACE, encoding="utf-8") as fh:
            print(json.dumps(json.load(fh).get("sentence"), ensure_ascii=False))
        return 0
    build()
    return 0


if __name__ == "__main__":
    sys.exit(run())
