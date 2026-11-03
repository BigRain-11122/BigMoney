"""The operator page's expectation table has three rows and three rulers.

The table under "该期待什么" prints, side by side and under one column headed
"全窗年化":

    5 名·可执行单口径   12.78%   <- the ticket: priced from 2024-01-01, next-open fill
    5 名·beta 覆盖      15.73%   <- the card's research band, from 2020-01-01, same-bar fill
    12 名·8% 波动目标    9.60%   <- the card's research band, from 2020-01-01, same-bar fill

and then says "三行是同一套选券信号，区别只在名数和杠杆规则". r1207 already showed
that the card's engine takes its signal from bar d's own close and pays the book at
bar d's open, so its rows are one bar optimistic; the ticket is causal. What no face
had measured is the OTHER two dials: the rows are priced from different start dates
and (ticket vs card) over different instrument universes.

This face prices the dials instead of describing them. One config is held fixed --
the ticket's own (5 names, beta target 0.20, repo cash leg, 8 bp) -- and that one
book is re-priced under every combination of

    universe   card classes (equity/commodity/convertible)
               ticket classes (equity/commodity/crossborder)
    window     2020-01-01 (the card's "full")  /  2024-01-01 (the ticket's)
    ordering   next-open (causal, what the ticket does)
               open-to-open on the same-bar score (what the card does)

so the reader gets, for the book he actually holds, what each ruler is worth. Two
identity arms anchor the ends: the ticket config on its own ruler must reproduce the
ticket's published 12.78%, and the card config on its own ruler must reproduce the
card's 9.60% / 18.35% -- if either drifts, nothing here is quoted.

The verdict is a property of the measurements, not of this docstring: `decide()`
reads the cells and `--check` re-derives it from the published rows.

Usage:
    python scripts/etf_book_band_ruler.py run
    python scripts/etf_book_band_ruler.py --check
    python scripts/etf_book_band_ruler.py --selftest
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_book_production as P
import etf_book_forward as FW
import etf_book_order as O
import etf_phase_beta_target as BT
import etf_phase_beta_window as BW
import etf_variants_null_rolling as V
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_composite_pf as E
from etf_asset_class import classify as classify_asset

OUT_JSON = os.path.join(ROOT, "results", "etf_book_band_ruler.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_BAND_RULER.md")
PAGE_JSON = os.path.join(ROOT, "docs", "live_book", "latest.json")

REBAL = O.REBAL
COST_BP = O.COST_BP
BETA_TARGET = 0.20
N_HOLD = 5
TICKET_INCEPTION = "2024-01-02"

# ---------------------------------------------------------------- frozen criteria
# The smallest move worth naming: a quarter of a point of annual return. Below it the
# two rulers are the same ruler and saying otherwise is noise.
TOL_PP = 0.25
# The identity arms are allowed to disagree with the published faces by an eighth of a
# point: the ticket's own accrual walks bar by bar and can accumulate a rounding step
# the engine's continuous series does not have.
IDENT_TOL_PP = 0.125
CRITERIA = {
    "tol_pp_per_year": TOL_PP,
    "identity_tol_pp": IDENT_TOL_PP,
    "held_config": {"n_hold": N_HOLD, "beta_target": BETA_TARGET, "rebal": REBAL,
                    "cost_bp_per_side": COST_BP, "cash_leg": "repo ladder (same series as the ticket)"},
    "dials": ["universe", "window", "ordering"],
    "windows": {"full": "2020-01-01..", "ticket": TICKET_INCEPTION + ".."},
    "universes": {"card": list(P.USE_CLASSES), "ticket": list(V.KEEP)},
    "verdict_rule": (
        "ROWS_NOT_COMPARABLE iff at least one dial moves the held config by >= tol_pp_per_year "
        "on at least one window; SAME_RULER if none does. The published gap between row 1 and "
        "row 3 is decomposed into these dials, and no dial's price is inferred from another."),
    "frozen": "thresholds and the dial list written before the first run; --check refuses a "
              "face that does not reproduce them",
}


# ---------------------------------------------------------------- helpers
def _pp(x):
    return None if x is None else round(100.0 * float(x), 3)


def _stats(ser, label):
    m = A.stats2(ser.dropna(), label)
    return {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}


def _cells(ser, label):
    """One priced path, read on both windows (and the card's own IS/OOS split)."""
    ser = ser.dropna()
    out = {"full": _stats(ser, label + "/full"),
           "ticket_window": _stats(ser[ser.index >= pd.Timestamp(TICKET_INCEPTION)],
                                   label + "/ticket")}
    is_end = pd.Timestamp(P.IS_END)
    out["is"] = _stats(ser[ser.index <= is_end], label + "/is")
    out["oos"] = _stats(ser[ser.index > is_end], label + "/oos")
    for k, row in out.items():
        row["cagr_pp"] = _pp(row.get("cagr"))
        row["maxdd_pp"] = _pp(row.get("maxdd"))
        row["bars"] = int(len(ser if k == "full" else
                             (ser[ser.index >= pd.Timestamp(TICKET_INCEPTION)] if k == "ticket_window"
                              else (ser[ser.index <= is_end] if k == "is" else ser[ser.index > is_end]))))
    return out


def _panel(universe):
    """The panel each family actually ranks on -- reused from its own producer, not re-cut."""
    if universe == "card":
        close, openp, amt, score, _cls, n_flip = P.prep_panel()
        return close, openp, amt, score, int(n_flip)
    close, openp, amt, feats = E.build_panel()
    classes = pd.Series(classify_asset(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    # repair BEFORE narrowing, exactly as etf_book_order.run() does: the flip repair reads
    # the whole panel, so subsetting first lands on a different path (0.20pp on the ticket).
    close, openp, _nf = A.repair_flips(close, openp)
    score = E.build_score(close[cols], amt[cols], feats)
    return close[cols], openp[cols], amt[cols], score, int(_nf)


def _book_series(panel, ordering, n_hold, vol_target=None, cost_bp=None):
    """One book return path under one fill ordering. Both use an existing engine.

    `cost_bp` is per side and belongs to the RULER, not to the book: the ticket's engine
    charges 8 bp and the card's 10 bp (P.COST), so a like-for-like cell has to say which.
    """
    close, openp, amt, score, _nf = panel
    rate = (O.COST_BP if cost_bp is None else float(cost_bp)) / 10000.0
    if ordering == "causal":
        ser, turn, _gap = E.run_next_open(close, openp, amt, None, REBAL, n_hold=n_hold,
                                          cost=rate, score=score)
        return ser, float(turn)
    ser, turn = R.open_to_open_equity(close, openp, amt, score, REBAL, n_hold,
                                      rate, vol_target=vol_target)
    return ser, float(turn)


def _overlay_path(panel, ordering, n_hold=N_HOLD, beta=BETA_TARGET, cost_bp=None):
    """The held config: book -> beta overlay -> repo cash leg. Exactly the ticket's path."""
    ser, _turn = _book_series(panel, ordering, n_hold, cost_bp=cost_bp)
    close = panel[0]
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        raise RuntimeError("no 510300 column on this panel")
    mkt = close[mkt_col]
    idx = ser.index.intersection(mkt.index)
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(mkt.reindex(idx))
    sched = O.k_schedule(rp, rm, beta)
    rates = BW.load_repo_rates()
    cash_rf, cash_missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)
    strat, bench, _kk = BT.apply_overlay(rp, rm, sched, 0.0, COST_BP, rf=cash_rf)
    if strat is None:
        raise RuntimeError("overlay produced no live window")
    live_k = O.in_force(sched, idx).dropna()
    if len(live_k):
        strat = strat[strat.index >= live_k.index[0]]
        bench = bench[bench.index >= live_k.index[0]]
    return strat, bench, bool(cash_missing)


# ---------------------------------------------------------------- verdict
def dial_prices(doc):
    """Every dial's price, read off the cells it moved. Nothing is inferred."""
    c = doc.get("cells") or {}
    out = {}

    def g(path, win="full"):
        node = c.get(path) or {}
        v = (node.get(win) or {}).get("cagr_pp")
        return v

    def delta(a, b, win="full"):
        """price of moving from ruler a to ruler b: b - a (positive = b reads higher)."""
        x, y = g(a, win), g(b, win)
        if x is None or y is None:
            return None
        return round(y - x, 3)

    def within(cell, a_win, b_win):
        node = c.get(cell) or {}
        x = (node.get(a_win) or {}).get("cagr_pp")
        y = (node.get(b_win) or {}).get("cagr_pp")
        if x is None or y is None:
            return None
        return round(y - x, 3)

    out["window"] = {"a": "2020-01-01..（表里另两行读的那一段）",
                     "b": TICKET_INCEPTION + "..（表里第一行读的那一段）",
                     "price_pp": within("held/causal/card", "full", "ticket_window"),
                     "note": "同一条定价路径，只换起点。差的是**时期**不是策略——正因为如此，"
                             "两行按两段时期读、却被放在同一个「全窗」表头下"}
    out["universe"] = {"a": "卡片类（equity/commodity/convertible）",
                       "b": "票类（equity/commodity/crossborder）",
                       "price_pp": delta("held/causal/card", "held/causal/ticket"),
                       "note": "同一本书、同一段、同一时点，只换能挑的品种类别"}
    out["ordering"] = {"a": "open-to-open（同 bar 信号）",
                       "b": "next-open（次开成交）",
                       "price_pp": delta("book/card/published", "book/card/causal"),
                       "note": "同一本书（5 名、不挂覆盖）、同一股票池、同一段，只换信号什么时候被读到。"
                               "这一格在**书层面**读，不挂 beta 覆盖：open-to-open 的净值序列比收盘口径"
                               "早一个 bar（下面「为什么覆盖只挂在次开那一侧」那张表是本面的实测），"
                               "拿它拟合 beta 会读到一个不是这本书的 beta，所以覆盖只挂在 next-open 那一侧"}
    out["cost"] = {"a": "8 bp/side（票的引擎）", "b": "10 bp/side（卡的引擎）",
                   "price_pp": delta("held/causal/card", "held/causal/card/cost10"),
                   "note": "同一本书、同一段、同一股票池、同一时点，只换每边假设的成本"}
    return out


def decide(doc):
    """ROWS_NOT_COMPARABLE iff any dial moves the held config by the frozen tolerance."""
    prices = doc.get("dial_prices") or dial_prices(doc)
    moved = {k: v for k, v in prices.items()
             if v.get("price_pp") is not None and abs(v["price_pp"]) >= TOL_PP}
    idt = doc.get("identity") or {}
    ident_ok = all(bool(v.get("pass")) for v in idt.values()) if idt else False
    if not ident_ok:
        return {"state": "IDENTITY_FAILED",
                "why": "a control arm does not reproduce the face it is a control for; "
                       "no dial price can be quoted",
                "criteria": CRITERIA["verdict_rule"]}
    if moved:
        names = "、".join("%s %+.2fpp" % (k, v["price_pp"]) for k, v in moved.items())
        return {"state": "ROWS_NOT_COMPARABLE",
                "dials_that_move": sorted(moved),
                "why": ("the table's rows are not one ruler: %s per year on the book the "
                        "operator actually holds. The gap between the top row and the card "
                        "row is the sum of these dials, not a property of the strategy."
                        % names),
                "criteria": CRITERIA["verdict_rule"]}
    return {"state": "SAME_RULER",
            "why": "no dial moves the held config by the frozen tolerance; the rows are "
                   "comparable as printed",
            "criteria": CRITERIA["verdict_rule"]}


# ---------------------------------------------------------------- run
def price_all(verbose=True):
    t0 = time.time()
    doc = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "script": "scripts/etf_book_band_ruler.py",
           "criteria": CRITERIA, "cells": {}, "panels": {}, "identity": {}}

    panels = {}
    for u in ("card", "ticket"):
        panel = _panel(u)
        panels[u] = panel
        doc["panels"][u] = {"symbols": int(panel[0].shape[1]), "bars": int(panel[0].shape[0]),
                            "first_bar": str(panel[0].index[0].date()),
                            "last_bar": str(panel[0].index[-1].date()),
                            "flips_repaired": panel[4]}
        if verbose:
            print("panel %-7s %4d symbols %5d bars -> %s"
                  % (u, panel[0].shape[1], panel[0].shape[0], doc["panels"][u]["last_bar"]),
                  flush=True)

    # the held config (book + beta overlay + repo cash), causal only -- see the alignment
    # note in dial_prices(): the open-to-open level series is labelled one bar early, so an
    # overlay fitted to it estimates beta four times too small. Not silently shifted.
    for u in ("card", "ticket"):
        strat, _bench, cash_missing = _overlay_path(panels[u], "causal")
        key = "held/causal/%s" % u
        doc["cells"][key] = _cells(strat, key)
        doc["cells"][key]["cash_leg_missing_dates"] = cash_missing
        if verbose:
            print("%-22s full %6.2f%% | 2024+ %6.2f%%"
                  % (key, doc["cells"][key]["full"]["cagr_pp"],
                     doc["cells"][key]["ticket_window"]["cagr_pp"]), flush=True)

    # the fourth dial: the card's engine charges 10 bp a side, the ticket's 8
    strat, _b, _m = _overlay_path(panels["card"], "causal", cost_bp=P.COST * 1e4)
    doc["cells"]["held/causal/card/cost10"] = _cells(strat, "held/causal/card/cost10")
    if verbose:
        print("%-22s full %6.2f%% | 2024+ %6.2f%%"
              % ("held/causal/card/cost10",
                 doc["cells"]["held/causal/card/cost10"]["full"]["cagr_pp"],
                 doc["cells"]["held/causal/card/cost10"]["ticket_window"]["cagr_pp"]), flush=True)

    # the book WITHOUT the overlay, under both fill orderings: the ordering dial lives here
    for u in ("card", "ticket"):
        for ordering in ("published", "causal"):
            ser, _turn = _book_series(panels[u], ordering, N_HOLD, cost_bp=O.COST_BP)
            key = "book/%s/%s" % (u, ordering)
            doc["cells"][key] = _cells(ser, key)
            if verbose:
                print("%-22s full %6.2f%% | 2024+ %6.2f%%"
                      % (key, doc["cells"][key]["full"]["cagr_pp"],
                         doc["cells"][key]["ticket_window"]["cagr_pp"]), flush=True)
    # the alignment fact the ordering dial has to be read with, measured not asserted
    doc["alignment"] = _alignment_note(panels["card"])

    # control: the card's own config on the card's own ruler
    ser, _turn = _book_series(panels["card"], "published", 12, vol_target=P.TARGET_VOL,
                              cost_bp=P.COST * 1e4)
    doc["cells"]["card/12/vol08"] = _cells(ser, "card/12/vol08")
    if verbose:
        print("card/12/vol08          full %6.2f%% | 2024+ %6.2f%%"
              % (doc["cells"]["card/12/vol08"]["full"]["cagr_pp"],
                 doc["cells"]["card/12/vol08"]["ticket_window"]["cagr_pp"]), flush=True)

    # ---- identity arms: each side must land on the number the live face publishes
    pub = _published_band()
    checks = []
    checks.append(_ident("ticket 12.78% reproduced on its own ruler",
                         doc["cells"]["held/causal/ticket"]["ticket_window"]["cagr_pp"],
                         pub.get("ticket_oos")))
    checks.append(_ident("card 9.60% reproduced on its own ruler",
                         doc["cells"]["card/12/vol08"]["full"]["cagr_pp"],
                         pub.get("card_full")))
    checks.append(_ident("card 18.35% (2024+) reproduced on its own ruler",
                         doc["cells"]["card/12/vol08"]["oos"]["cagr_pp"],
                         pub.get("card_oos")))
    doc["identity"] = {c.pop("what"): c for c in checks}
    doc["published_faces"] = pub
    doc["dial_prices"] = dial_prices(doc)
    doc["verdict"] = decide(doc)
    doc["elapsed_sec"] = round(time.time() - t0, 1)
    return doc


def _alignment_note(panel):
    """How far behind the market an open-to-open level series is labelled.

    Measured, because it decides whether an overlay may be fitted to that series: the
    correlation of the book's daily return against the market's at three lags. A series
    labelled correctly peaks at lag 0; one labelled a bar early peaks at +1."""
    close = panel[0]
    mkt = close[next(c for c in BT.MKT if c in close.columns)]
    out = {}
    for ordering in ("published", "causal"):
        ser, _t = _book_series(panel, ordering, N_HOLD, cost_bp=O.COST_BP)
        idx = ser.index.intersection(mkt.index)
        rp, rm = BT.rets(ser.reindex(idx)), BT.rets(mkt.reindex(idx))
        out[ordering] = {"corr_lag_m1": round(float(rp.corr(rm.shift(-1))), 4),
                         "corr_lag_0": round(float(rp.corr(rm)), 4),
                         "corr_lag_p1": round(float(rp.corr(rm.shift(1))), 4)}
    out["reading"] = ("a series labelled a bar early peaks at +1, not at 0; an overlay fitted "
                      "to it sees a beta that is not the book's beta")
    return out


def _published_band():
    """The three numbers the operator page prints, read from its own artefact.

    `docs/live_book/latest.json` is a pointer (`json` = the dated file name), so the band is
    read from the file it names -- never from a copy of the numbers in here."""
    out = {"source": os.path.relpath(PAGE_JSON, ROOT).replace(os.sep, "/")}
    try:
        with open(PAGE_JSON, encoding="utf-8") as fh:
            blk = json.load(fh)
        page = blk.get("json")
        if isinstance(page, str):
            # the pointer may hold a bare file name or a repo-relative path
            cand = page if os.path.isabs(page) else None
            if cand is None:
                rel = os.path.join(ROOT, page.replace("/", os.sep))
                cand = rel if os.path.exists(rel) else os.path.join(os.path.dirname(PAGE_JSON), page)
            out["source"] = os.path.relpath(cand, ROOT).replace(os.sep, "/")
            with open(cand, encoding="utf-8") as fh:
                page = json.load(fh)
        if not isinstance(page, dict):
            page = blk
        band = page.get("backtest_band") or {}
        out["rows"] = []
        for label, row in band.items():
            full = (row.get("full") or {}).get("cagr_pct")
            oos = (row.get("oos") or {}).get("cagr_pct")
            isr = (row.get("is") or {}).get("cagr_pct")
            out["rows"].append({"label": label, "full": full, "is": isr, "oos": oos})
            if label.startswith("5 名·可执行"):
                # r1248: this row used to print ONE number, so `full` was also the ticket's
                # own 2024+ CAGR. After the row was correctly split into 全窗 / 2020-2023 /
                # 2024+ (r1247 relabel) the arm name still quotes 12.78% -- that is the 2024+
                # column, while the 685-bar ticket window is not the 1527-bar full window.
                out["ticket"] = full
                out["ticket_oos"] = oos
            elif label.startswith("12 名"):
                out["card_full"] = full
                out["card_oos"] = oos
        out["row_labels"] = list(band.keys())
    except Exception as exc:                                     # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    return out


def _ident(what, measured, published):
    if measured is None or published is None:
        return {"what": what, "measured_pp": measured, "published_pp": published,
                "delta_pp": None, "pass": False, "why": "one side unreadable"}
    d = round(float(measured) - float(published), 3)
    return {"what": what, "measured_pp": round(float(measured), 3),
            "published_pp": round(float(published), 3), "delta_pp": d,
            "pass": bool(abs(d) <= IDENT_TOL_PP)}


# ---------------------------------------------------------------- report
def render_md(doc):
    v = doc.get("verdict") or {}
    c = doc.get("cells") or {}
    pr = doc.get("dial_prices") or {}
    pub = doc.get("published_faces") or {}
    L = []
    add = L.append
    add("# 那张「该期待什么」的表，三行不是一把尺子")
    add("")
    add("证据面：`%s` ｜ 定价截止 %s ｜ %s 秒"
        % (os.path.relpath(OUT_JSON, ROOT).replace(os.sep, "/"),
           (doc.get("panels") or {}).get("card", {}).get("last_bar") or "—",
           doc.get("elapsed_sec")))
    add("")
    add("## 判决")
    add("")
    add("**%s**" % v.get("state"))
    add("")
    if v.get("why"):
        add("- %s" % v["why"])
    add("")
    add("## 表里印的三行（原文，含各自的起点）")
    add("")
    add("| 行 | 全窗年化 | 2020-2023 | 2024 起 | 实际起点 |")
    add("|---|---|---|---|---|")
    for r in (pub.get("rows") or []):
        starts = TICKET_INCEPTION if r["label"].startswith("5 名·可执行") else "2020-01-01"
        add("| %s | **%s** | %s | %s | %s |"
            % (r["label"], _fmt(r.get("full"), pct=True), _fmt(r.get("is"), pct=True),
               _fmt(r.get("oos"), pct=True),
               starts + ("" if r.get("is") is not None else "（这一行没有 2020+ 的数）")))
    add("")
    add("读法一（按列）：第一行 12.78 压在「全窗」列，比卡片那行的 9.60 高出 3.18 个点，读者会以为"
        "“这个 5 名的账更值”。读法二（按同一段）：表里自己印着卡片那行 2024 起 = **%s**——"
        "和第一行同一段时期，反过来比第一行高。两个读法用的是同一张表的两列。"
        % _fmt(pub.get("card_oos"), pct=True))
    add("")
    add("## 同一本书，四个旋钮各值多少钱")
    add("")
    add("被固定的那本书＝可执行票自己那一本（%d 名·beta 目标 %.2f·逆回购现金腿·8bp）。"
        "然后一次只动一个旋钮；正号＝「到」那一侧读得更高。"
        % (N_HOLD, BETA_TARGET))
    add("")
    add("| 旋钮 | 从 | 到 | 值多少 |")
    add("|---|---|---|---|")
    names = {"window": "起点", "universe": "股票池", "ordering": "信号时点", "cost": "成本"}
    for k in ("window", "universe", "ordering", "cost"):
        p = pr.get(k) or {}
        val = "—" if p.get("price_pp") is None else "%+.2f pp/年" % p["price_pp"]
        add("| %s | %s | %s | **%s** |" % (names.get(k, k), p.get("a"), p.get("b"), val))
    add("")
    for k in ("window", "universe", "ordering", "cost"):
        n = (pr.get(k) or {}).get("note")
        if n:
            add("- **%s**：%s" % (names.get(k, k), n))
    add("")
    add("## 同一本书 × 各个格子")
    add("")
    add("| 格子 | 全窗(2020+) | 起点 2024+ | 最大回撤(全窗) |")
    add("|---|---|---|---|")
    rows = [("held/causal/card", "覆盖·卡片类·次开"),
            ("held/causal/ticket", "覆盖·票类·次开（＝你手上这本）"),
            ("held/causal/card/cost10", "同上但 10bp"),
            ("book/card/causal", "不挂覆盖·卡片类·次开"),
            ("book/card/published", "不挂覆盖·卡片类·同 bar"),
            ("book/ticket/causal", "不挂覆盖·票类·次开"),
            ("book/ticket/published", "不挂覆盖·票类·同 bar"),
            ("card/12/vol08", "卡片自己的 12 名·8% 波动")]
    for key, label in rows:
        row = c.get(key) or {}
        add("| %s | %s | %s | %s |"
            % (label,
               _fmt(row.get("full", {}).get("cagr_pp")),
               _fmt(row.get("ticket_window", {}).get("cagr_pp")),
               _fmt(row.get("full", {}).get("maxdd_pp"))))
    add("")
    al = doc.get("alignment") or {}
    if al.get("published"):
        add("### 为什么覆盖只挂在次开那一侧（实测，不是声明）")
        add("")
        add("| 口径 | 对市场日收益相关 lag-1 | lag 0 | lag +1 |")
        add("|---|---|---|---|")
        for o, zh in (("causal", "次开成交"), ("published", "同 bar 开盘")):
            r = al.get(o) or {}
            add("| %s | %.3f | **%.3f** | %.3f |"
                % (zh, r.get("corr_lag_m1") or 0.0, r.get("corr_lag_0") or 0.0,
                   r.get("corr_lag_p1") or 0.0))
        add("")
        add("同 bar 那条序列的峰值在 lag +1 而不是 lag 0——它的净值日期比它自己的收益早一个 bar。"
            "任何拿它去拟合 beta 的代码都会读到一个不是这本书的 beta（本面实测低估约 4 倍），"
            "所以这一面**不**把覆盖挂上去，也不悄悄挪一格去凑。")
        add("")
    add("## 身份门（对不上就不许引用）")
    add("")
    add("| 对照臂 | 本面复现 | 上场发布 | 差 | 过门 |")
    add("|---|---|---|---|---|")
    for what, r in (doc.get("identity") or {}).items():
        add("| %s | %s | %s | %s | %s |"
            % (what, _fmt(r.get("measured_pp"), pct=True), _fmt(r.get("published_pp"), pct=True),
               _fmt(r.get("delta_pp")), "PASS" if r.get("pass") else "**FAIL**"))
    add("")
    add("## 规则（跑之前冻结）")
    add("")
    add(CRITERIA["verdict_rule"])
    add("")
    add("门＝%s pp/年；身份门＝%s pp。" % (TOL_PP, IDENT_TOL_PP))
    add("")
    add("行数据：`%s::cells`。" % os.path.relpath(OUT_JSON, ROOT).replace(os.sep, "/"))
    add("")
    return "\n".join(L)


def _fmt(x, pct=False):
    if x is None:
        return "—"
    return "%.2f%%" % x if pct else "%+.2f%%" % x


def run():
    doc = price_all()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(doc))
    print("verdict: %s" % (doc["verdict"] or {}).get("state"))
    return 0


def read_published(path=OUT_JSON):
    """Reader for other faces: serve the stored verdict only if it still recomputes."""
    if not os.path.exists(path):
        return {"status": "missing", "artifact": os.path.relpath(path, ROOT)}
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    if (doc.get("criteria") or {}).get("tol_pp_per_year") != TOL_PP:
        return {"status": "drifted", "artifact": os.path.relpath(path, ROOT),
                "detail": "the stored face was frozen at a different tolerance"}
    redo = decide(dict(doc, dial_prices=dial_prices(doc)))
    stored = (doc.get("verdict") or {}).get("state")
    if redo.get("state") != stored:
        return {"status": "drifted", "artifact": os.path.relpath(path, ROOT),
                "detail": "stored verdict %s, recomputed %s" % (stored, redo.get("state"))}
    return {"status": "ok", "artifact": os.path.relpath(path, ROOT).replace(os.sep, "/"),
            "verdict": redo, "dial_prices": doc.get("dial_prices"),
            # r1216b: the operator's own row needs the middle window too. The split is
            # served through this one reader rather than re-read from the artifact by a
            # consumer, so a face that stops recomputing still refuses every cell.
            "cells": {k: {"full": v.get("full"), "ticket_window": v.get("ticket_window"),
                          "is": v.get("is"), "oos": v.get("oos")}
                      for k, v in (doc.get("cells") or {}).items()},
            "identity": doc.get("identity"),
            "evidence_cutoff": ((doc.get("panels") or {}).get("card") or {}).get("last_bar"),
            "published_faces": doc.get("published_faces")}


def check():
    doc = read_published()
    if doc.get("status") != "ok":
        print("CHECK FAILED: %s (%s)" % (doc.get("status"), doc.get("detail")))
        return 1
    print("check OK: %s | %s"
          % (doc["verdict"]["state"],
             ", ".join("%s %+.2fpp" % (k, (v or {}).get("price_pp") or 0.0)
                       for k, v in (doc["dial_prices"] or {}).items())))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    ok = 0
    fail = []

    def chk(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append(name)

    # L1: a dial that moves the book by a point is named; the verdict is not hard-coded
    cells = {"held/causal/card": {"full": {"cagr_pp": 9.0}, "ticket_window": {"cagr_pp": 15.0}},
             "held/causal/ticket": {"full": {"cagr_pp": 10.0}, "ticket_window": {"cagr_pp": 16.0}},
             "held/causal/card/cost10": {"full": {"cagr_pp": 9.0}, "ticket_window": {"cagr_pp": 15.0}},
             "book/card/published": {"full": {"cagr_pp": 11.0}, "ticket_window": {"cagr_pp": 17.0}},
             "book/card/causal": {"full": {"cagr_pp": 9.0}, "ticket_window": {"cagr_pp": 15.0}}}
    d = {"cells": cells, "identity": {"a": {"pass": True}}}
    d["dial_prices"] = dial_prices(d)
    v = decide(d)
    chk("a one-point universe move is named", v["state"] == "ROWS_NOT_COMPARABLE"
        and "universe" in v["dials_that_move"])
    chk("the universe price is (ticket - card), not an absolute",
        abs(d["dial_prices"]["universe"]["price_pp"] - 1.0) < 1e-9)
    chk("the ordering price is read on the book, not on the overlay",
        abs(d["dial_prices"]["ordering"]["price_pp"] + 2.0) < 1e-9)

    # L2: nothing moves -> SAME_RULER (the verdict is not always the interesting word)
    same = {"held/causal/card": {"full": {"cagr_pp": 9.0}, "ticket_window": {"cagr_pp": 9.0}},
            "held/causal/ticket": {"full": {"cagr_pp": 9.0}, "ticket_window": {"cagr_pp": 9.0}},
            "held/causal/card/cost10": {"full": {"cagr_pp": 9.0}, "ticket_window": {"cagr_pp": 9.0}},
            "book/card/published": {"full": {"cagr_pp": 9.0}, "ticket_window": {"cagr_pp": 9.0}},
            "book/card/causal": {"full": {"cagr_pp": 9.0}, "ticket_window": {"cagr_pp": 9.0}}}
    d2 = {"cells": same, "identity": {"a": {"pass": True}}}
    d2["dial_prices"] = dial_prices(d2)
    chk("three identical cells read as one ruler", decide(d2)["state"] == "SAME_RULER")

    # L3: a failed control arm blocks every price (no dial is quoted off a broken control)
    d3 = dict(d2, identity={"a": {"pass": False}})
    chk("a failed identity arm refuses to quote", decide(d3)["state"] == "IDENTITY_FAILED")

    # L4: a missing cell yields None, never a zero -- "unknown" must not read as "no move"
    d4 = {"cells": {"held/causal/card": {"full": {"cagr_pp": None}}},
          "identity": {"a": {"pass": True}}}
    d4["dial_prices"] = dial_prices(d4)
    chk("an unreadable cell prices as None", d4["dial_prices"]["universe"]["price_pp"] is None)

    # L5: the tolerance is inclusive at the line, exclusive below it
    edge = dict(same)
    edge["held/causal/ticket"] = {"full": {"cagr_pp": 9.0 + TOL_PP},
                                  "ticket_window": {"cagr_pp": 9.0}}
    d5 = {"cells": edge, "identity": {"a": {"pass": True}}}
    d5["dial_prices"] = dial_prices(d5)
    chk("a move exactly at the line is named", decide(d5)["state"] == "ROWS_NOT_COMPARABLE")

    # L6: identity gate arithmetic
    chk("identity passes inside the tolerance", _ident("x", 12.78, 12.78)["pass"])
    chk("identity fails a whole point off", not _ident("x", 13.78, 12.78)["pass"])
    chk("an unreadable identity side fails closed", not _ident("x", None, 12.78)["pass"])

    # L7: the report never prints a winner from a missing cell
    md = render_md({"verdict": {"state": "SAME_RULER"}, "cells": {}, "dial_prices": {},
                    "identity": {}, "panels": {}, "elapsed_sec": 0.0})
    chk("an empty face renders dashes, not zeros", "—" in md and "0.00" not in md)

    # L8 (r1248): the ticket arm reads the column its NAME quotes. The row was split into
    # 全窗 / 2020-2023 / 2024+ in r1247; before that "full" also happened to be the 2024+
    # number, so an arm wired to `full` passed for the wrong reason and went red the moment
    # the columns became distinct. A fixture where the two columns differ pins the choice.
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _td:
        _pg = os.path.join(_td, "page.json")
        with open(_pg, "w", encoding="utf-8") as _fh:
            json.dump({"backtest_band": {
                "5 名·可执行的那一本": {"full": {"cagr_pct": 7.63}, "is": {"cagr_pct": 3.71},
                                       "oos": {"cagr_pct": 12.56}},
                "12 名·8% 波动目标": {"full": {"cagr_pct": 9.6}, "oos": {"cagr_pct": 18.33}}}},
                _fh, ensure_ascii=False)
        _keep = PAGE_JSON
        try:
            globals()["PAGE_JSON"] = _pg
            _pub = _published_band()
        finally:
            globals()["PAGE_JSON"] = _keep
    chk("the ticket arm reads the 2024+ column, not the full-window one",
        _pub.get("ticket_oos") == 12.56 and _pub.get("ticket") == 7.63
        and _ident("x", 12.56, _pub.get("ticket_oos"))["pass"]
        and not _ident("x", 12.56, _pub.get("ticket"))["pass"])

    print("selftest: %d/%d" % (ok, ok + len(fail)))
    for f in fail:
        print("  FAIL:", f)
    return 0 if not fail else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lstrip("-")
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    if cmd == "status":
        print(json.dumps(read_published(), ensure_ascii=False, indent=1)[:4000])
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))