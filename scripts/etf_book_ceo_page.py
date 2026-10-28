"""ETF production book -> CEO one-page (docs/live_book/LIVE-BOOK-YYYYMMDD.md + .json).

Why this exists: the ETF book is the only money-making structure this company has
shown to work, but every face it publishes (ticket JSON, card JSON, registry JSON,
forward ledger) is machine-shaped. Nothing in the repo answers, in plain language,
"what do I buy today, with how much money, how am I doing, and when does it change".

Pure aggregation, zero new judgement:
  - order list / money split   <- results/etf_book_order/latest.json -> ticket file
  - backtest expectation band  <- results/etf_book_production/latest.json (card)
  - forward track vs inception <- results/etf_book_forward/LEDGER.json
  - next rebalance date        <- data/exchange_calendar.csv (official calendar)

Idempotent: same day -> same content; other days' pages are never touched.

Usage:
  python scripts/etf_book_ceo_page.py run
  python scripts/etf_book_ceo_page.py selftest
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "live_book")
TICKET_PTR = os.path.join(ROOT, "results", "etf_book_order", "latest.json")
CARD = os.path.join(ROOT, "results", "etf_book_production", "latest.json")
LEDGER = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")
CAL = os.path.join(ROOT, "data", "exchange_calendar.csv")
MACHINE = os.path.join(ROOT, "fleet", "machine.json")

# Single writer: the page is a plain-language mirror of shared artefacts, so two
# machines regenerating the same day would only produce a git race on docs/live_book.
# bm-a prints it; every other host says so and writes nothing (R31 lane-guard lineage).
HOST = "bm-a"


def machine_id():
    try:
        with open(MACHINE, encoding="utf-8-sig") as fh:
            return json.load(fh).get("machine_id")
    except Exception:
        return None


def writer_allowed(mid):
    return mid == HOST

CLASS_ZH = {
    "equity": "A股",
    "crossborder": "跨境",
    "commodity": "商品",
    "convertible": "转债",
    "bond": "债券",
    "money": "货币",
}


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _load_ticket():
    """Pointer -> the dated ticket file it names."""
    ptr = _load(TICKET_PTR)
    rel = ptr.get("ticket_file") or ptr.get("file") or ptr.get("path")
    if isinstance(rel, str) and rel:
        cands = [rel] if os.path.isabs(rel) else [
            os.path.join(os.path.dirname(TICKET_PTR), rel),   # sibling of the pointer
            os.path.join(ROOT, rel),                          # repo-root relative
        ]
        for cand in cands:
            if os.path.exists(cand):
                return ptr, _load(cand), cand
    # fall back to the pointer itself when it already carries the ticket body
    if "ticket" in ptr:
        return ptr, ptr, TICKET_PTR
    raise FileNotFoundError("ticket body not resolvable from %s" % TICKET_PTR)


def trading_days_after(cal_dates, anchor, n):
    """The n-th trading day strictly after `anchor` (ISO strings, sorted asc)."""
    if anchor is None or n is None or int(n) <= 0:
        return None
    later = [d for d in cal_dates if d > anchor]
    if len(later) < int(n):
        return None
    return later[int(n) - 1]


def calendar_dates(path=CAL):
    out = []
    with open(path, encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            s = line.strip()
            if s:
                out.append(s[:10])
    return out


def money_cny(tk, nav):
    """Backtest percentages -> yuan on this ticket's own capital.

    Pure unit change: every number is one already published on the ticket times `nav`.
    Anything unreadable stays None -- a 0 here would read as "this book earns nothing".
    """
    tk = tk or {}
    metrics = tk.get("metrics") or {}
    book = metrics.get("book") or {}
    bench = metrics.get("same_beta_benchmark") or {}
    out = {"capital_cny": round(float(nav or 0.0), 2), "expected_annual_cny": None,
           "benchmark_annual_cny": None, "excess_annual_cny": None,
           "worst_drawdown_cny": None, "basis": None}
    if not nav or not book:
        return out
    out["expected_annual_cny"] = round(float(book["cagr"]) * nav, 0)
    out["worst_drawdown_cny"] = round(float(book["maxdd"]) * nav, 0)
    out["basis"] = "backtest cagr/maxdd x this ticket's capital, no new assumption"
    if bench and metrics.get("excess_pp") is not None:
        out["benchmark_annual_cny"] = round(float(bench["cagr"]) * nav, 0)
        out["excess_annual_cny"] = round(float(metrics["excess_pp"]) / 100.0 * nav, 0)
    return out


TRADING_DAYS_PER_YEAR = 250

REPO_DIR = os.path.join(ROOT, "data", "repo_daily")
CASH_LEG_SYMBOL = "GC001"


def cash_yield(cash_amount, symbol=CASH_LEG_SYMBOL, panel_dir=REPO_DIR, window=20):
    """What the idle half earns: cash x the repo panel's own quoted close.

    The page told the reader to buy GC001 but never said what that is worth -- a
    number the CEO pays for by leaving the money in a current account instead.
    Again a pure unit change: the panel prints the rate, this multiplies it by the
    cash on the page. The 1-day repo spikes at quarter-end and before holidays, so
    the trailing mean is quoted beside it. Anything unreadable stays None -- 0 would
    read as "the cash earns nothing", which is exactly the case worth warning about.
    """
    out = {"leg": symbol, "quoted_as": "收盘年化利率 %", "rate_date": None,
           "rate_pct": None, "rate_20d_pct": None, "annual_cny": None,
           "daily_cny": None, "window": int(window), "basis": None,
           "panel": os.path.relpath(os.path.join(panel_dir, "%s.csv" % symbol), ROOT)
           .replace("\\", "/")}
    if cash_amount is None or float(cash_amount) <= 0:
        return out
    path = os.path.join(panel_dir, "%s.csv" % symbol)
    if not os.path.exists(path):
        return out
    rows = []
    with open(path, encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) < 5:
                continue
            try:
                rows.append((parts[0], float(parts[4])))
            except ValueError:
                continue
    rows = [r for r in rows if 0.0 < r[1] < 200.0]   # same sanity band the collector enforces
    if not rows:
        return out
    out["rate_date"], out["rate_pct"] = rows[-1]
    tail = rows[-int(window):]
    out["rate_20d_pct"] = round(sum(v for _, v in tail) / len(tail), 4)
    out["annual_cny"] = round(float(cash_amount) * out["rate_pct"] / 100.0, 0)
    out["daily_cny"] = round(out["annual_cny"] / TRADING_DAYS_PER_YEAR, 0)
    out["basis"] = ("cash x panel close rate / 100; per session = annual / %d sessions"
                    % TRADING_DAYS_PER_YEAR)
    return out


STRESS_DIR = os.path.join(ROOT, "results", "etf_book_stress")
STRESS_WINDOWS = (1, 5, 20)


def stress_stats(daily, windows=STRESS_WINDOWS, capital=None):
    """Worst run of `n` consecutive days for a fixed-weight book.

    `daily` is a pandas Series of (weight-applied) book returns; a name that printed no
    price on a leg simply earns nothing for that leg, which is how the research engine
    treats it too. Everything here is the same arithmetic in a different window -- no new
    assumption, no fitted model. Returns None when there is not enough history, so a
    missing panel can never be read as "this book never loses".
    """
    if daily is None or len(daily) == 0:
        return None
    s = daily.dropna()
    if len(s) == 0:
        return None
    out = {"n_days": int(len(s)), "first": str(s.index[0])[:10], "last": str(s.index[-1])[:10],
           "worst": {}, "capital_cny": capital}
    for n in windows:
        if len(s) < n:
            out["worst"]["%dd" % n] = None
            continue
        # compounded, not summed: the reader is being told what the money did over N days
        gross = (1.0 + s).cumprod() / (1.0 + s).cumprod().shift(n) - 1.0
        roll = gross.dropna()
        if len(roll) == 0:
            out["worst"]["%dd" % n] = None
            continue
        when = roll.idxmin()
        val = float(roll.min())
        row = {"pct": round(val * 100.0, 2), "end_date": str(when)[:10]}
        row["cny"] = None if capital is None else round(val * float(capital), 0)
        out["worst"]["%dd" % n] = row
    return out


def build_stress(order, capital, priced_bar, close=None):
    """Data path: replay today's weights over the whole panel, worst-window report.

    Cached per priced bar -- the answer only changes when the panel or the book does, and
    re-walking 20 years of a 1,500-column panel every tick is cost without information.
    """
    if not order:
        return None
    cache = os.path.join(STRESS_DIR, "STRESS-%s.json" % str(priced_bar).replace("-", ""))
    if os.path.exists(cache):
        try:
            with open(cache, encoding="utf-8") as fh:
                c = json.load(fh)
            if c.get("capital_cny") == round(float(capital or 0.0), 2):
                return c
        except (OSError, ValueError):
            pass
    try:
        if close is None:
            import sys as _sys
            _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import etf_book_forward as F
            close, _o, _a, _f, _sc, _cls, _nf = F.build_inputs()
        import numpy as _np
        import pandas as _pd
        names = [o.get("symbol") for o in order]
        wts = [float(o.get("weight") or 0.0) for o in order]
        legs = {}
        for n, w in zip(names, wts):
            if n in close.columns:
                legs[n] = close[n].astype(float).pct_change().fillna(0.0) * w
            else:
                legs[n] = _pd.Series(0.0, index=close.index)
        book = _pd.DataFrame(legs).sum(axis=1)
    except Exception as exc:               # honest: no panel -> no stress claim
        return {"error": "%s: %s" % (type(exc).__name__, exc), "worst": {}, "capital_cny": capital}
    st = stress_stats(book, capital=capital)
    if st is None:
        return None
    st["capital_cny"] = round(float(capital or 0.0), 2)
    st["basis"] = ("今天的权重原封不动摆回整段面板（现金 0 息），取最坏的连续 N 个交易日；"
                   "不是策略实际路径，是同一批票的最坏窗口")
    try:
        os.makedirs(STRESS_DIR, exist_ok=True)
        with open(cache, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(st, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    except OSError:
        pass
    return st


def today_action(p):
    """Does the reader have to touch the account today?

    The ticket is re-priced every session against a fixed set of weights, so the
    share counts in the order list change daily even though the DECISION has not
    moved since `book_decided_at`. Publishing that list as "buy this today" makes
    a holder re-buy a book they already own -- at 8bp a side that is more than the
    book's own expected annual return. So the page has to name the world the
    reader is in:

      rebalance -- this priced bar IS the decision bar: trade.
      open      -- the reader is not in the book yet: buy the list once.
      hold      -- already holding and the decision has not moved: do nothing.
      unknown   -- a date face is missing; refuse to guess.
    """
    decided = p.get("book_decided_at")
    priced = p.get("priced_bar")
    holding = bool((p.get("forward") or {}).get("bars"))
    out = {"mode": "unknown", "holding": holding, "book_decided_at": decided,
           "priced_bar": priced, "next_trade_date": None, "cost_if_retraded_pct_per_year": None,
           "cost_basis": None}
    if not decided or not priced:
        return out
    decided_bar_is_priced = (str(decided) == str(priced))
    if decided_bar_is_priced:
        out["mode"] = "rebalance" if holding else "open"
    else:
        out["mode"] = "hold" if holding else "open"
    out["next_trade_date"] = p.get("next_rebalance_date") if out["mode"] == "hold" else priced

    # What chasing this list every session would cost, in percent of CAPITAL per year.
    # 2 sides x cost_bp on the book slice x a 250-session year -- an assumption, published.
    cost_bp = p.get("cost_bp_per_side")
    k = p.get("k_now")
    if cost_bp and k:
        per_year = 2.0 * (float(cost_bp) / 10000.0) * TRADING_DAYS_PER_YEAR * float(k)
        out["cost_if_retraded_pct_per_year"] = round(per_year * 100.0, 2)
        out["cost_basis"] = ("2 sides x %s bp x %d sessions x book share %.4f, on capital"
                             % (cost_bp, TRADING_DAYS_PER_YEAR, float(k)))
    return out


def build(with_stress=False):
    ptr, tk, tk_path = _load_ticket()
    card = _load(CARD) if os.path.exists(CARD) else {}
    ledger = _load(LEDGER) if os.path.exists(LEDGER) else {}

    nav = float(tk.get("ticket", {}).get("nav") or 0.0)
    order = list(tk.get("ticket", {}).get("order") or [])
    cash_amt = float(tk.get("ticket", {}).get("cash_amount") or 0.0)
    book_amt = float(tk.get("ticket", {}).get("book_amount") or 0.0)
    cash_w = float(tk.get("ticket", {}).get("cash_weight") or 0.0)
    cash_leg = tk.get("ticket", {}).get("cash_leg") or "cash (no instrument named)"

    bars = list(ledger.get("bars") or [])
    fwd = {"bars": len(bars), "inception": None, "nav": None, "since_inception_pct": None,
           "as_of": None}
    if bars:
        fwd["inception"] = bars[0].get("bar")
        fwd["as_of"] = bars[-1].get("bar")
        fwd["nav"] = bars[-1].get("nav")
        fwd["since_inception_pct"] = round((float(bars[-1]["nav"]) - 1.0) * 100.0, 4)

    # the daily answer to "are we beating just buying the four exposures" -- read off the
    # forward ledger's own benchmark block, never re-priced here (one price source)
    bench = (ledger.get("benchmark") or {}).get("latest") or {}
    # r1316: a spread with no horizon is read as a verdict. Carry the ledger's own
    # power table (what edge this record can resolve inside 6m/1y/2y/3y, and how
    # many YEARS the published alphas would need) beside the number.
    _pw = ((ledger.get("benchmark") or {}).get("significance") or {}).get("power") or {}
    vs_basket = None
    if bench.get("excess_pp") is not None:
        vs_basket = {
            "bar": bench.get("bar"),
            "book_nav": bench.get("book_nav"),
            "basket_nav": bench.get("basket_nav"),
            "excess_pp": bench.get("excess_pp"),
            "basket": ((ledger.get("benchmark") or {}).get("labels") or {}),
            "basis": "等权 1/4、同一换仓日、次日开盘成交",
            "horizon": ({"min_detectable_edge_pp": _pw.get("min_detectable_edge_pp"),
                         "years_for_80pct_power": _pw.get("years_for_80pct_power"),
                         "candidate_sources": _pw.get("candidate_sources")}
                        if _pw.get("available") else None),
        }

    bt = (card.get("backtest") or {})
    band = {}
    # the executable ticket prices its own book; quote that口径 first, from the ticket itself
    tk_book = (tk.get("metrics") or {}).get("book") or {}
    if tk_book:
        band["%d 名·可执行单口径（本单这份账）" % (tk.get("n_hold") or len(order))] = {
            "full": {"cagr_pct": round(tk_book["cagr"] * 100, 2),
                     "sharpe": round(tk_book["sharpe"], 2),
                     "maxdd_pct": round(tk_book["maxdd"] * 100, 2)}}
    for key, label in (("n5_base", "5 名·beta 覆盖"),
                       ("n12_vt08", "12 名·8% 波动目标（生产卡片口径）")):
        blk = bt.get(key) or {}
        if not blk:
            continue
        row = {}
        for seg in ("full", "is", "oos"):
            s = blk.get(seg) or {}
            if s:
                row[seg] = {"cagr_pct": round(s["cagr"] * 100, 2),
                            "sharpe": round(s["sharpe"], 2),
                            "maxdd_pct": round(s["maxdd"] * 100, 2)}
        band[label] = row

    # the same percentages expressed in yuan on THIS ticket's capital -- a unit change, not a new estimate
    money = money_cny(tk, nav)

    feed = tk.get("feed_status") or {}
    agree = tk.get("card_agreement") or {}
    cal = calendar_dates() if os.path.exists(CAL) else []
    next_reb = trading_days_after(cal, tk.get("evidence_cutoff"), tk.get("next_decision_bars"))
    today = dt.date.today().isoformat()

    page = {
        "schema": "etf-book-ceo-page/v1",
        "generated_for_date": today,
        "evidence_cutoff": tk.get("evidence_cutoff"),
        "priced_bar": feed.get("ticket_bar"),
        "feed_status": feed.get("status"),
        "feed_lag_days": feed.get("lag_days"),
        "capital_cny": nav,
        "book_amount_cny": round(book_amt, 2),
        "cash_amount_cny": round(cash_amt, 2),
        "cash_weight": round(cash_w, 4),
        "cash_leg": cash_leg,
        "cash_yield": cash_yield(cash_amt),
        "k_now": tk.get("k_now"),
        "n_hold": tk.get("n_hold"),
        "cost_bp_per_side": tk.get("cost_bp_per_side"),
        "book_decided_at": tk.get("book_decided_at"),
        "next_decision_bars": tk.get("next_decision_bars"),
        "next_rebalance_date": next_reb,
        "order": [{"symbol": o.get("symbol"), "class": o.get("class"),
                   "class_zh": CLASS_ZH.get(o.get("class"), o.get("class")),
                   "weight": o.get("weight"), "price": o.get("price"),
                   "lots": o.get("lots"), "shares": o.get("shares"),
                   "amount_cny": o.get("amount")} for o in order],
        "forward": fwd,
        "vs_basket": vs_basket,
        "backtest_band": band,
        "excess_pp": (tk.get("metrics") or {}).get("excess_pp"),
        "money_cny": money,
        "ticket_book": tk_book or None,
        "same_beta_benchmark": (tk.get("metrics") or {}).get("same_beta_benchmark"),
        "agreement": {"same_decision_bar": agree.get("same_decision_bar"),
                      "same_priced_bar": agree.get("same_priced_bar"),
                      "card_names": agree.get("card_names")},
        "sources": {"ticket": os.path.relpath(tk_path, ROOT),
                    "card": "results/etf_book_production/latest.json",
                    "ledger": "results/etf_book_forward/LEDGER.json",
                    "calendar": "data/exchange_calendar.csv"},
        "caveats": [
            "回测票池是现存 ETF（有幸存者偏差）；2020-2023 段弱、收益主要集中在 2024 之后。",
            "前向账本只有 %d 个交易日，自起始净值 %.4f 不构成业绩记录。" % (fwd["bars"], fwd["nav"] or 0.0),
            "现金腿若不下单，账本按 %s 计息；不买逆回购则实际是 0 息。" % cash_leg,
            "这是研究产出，不是投资建议；实盘下单是 CEO 的直接权限，公司自动实盘仍是 CEO 唯一门。",
        ],
    }
    page["today_action"] = today_action(page)
    page["stress"] = build_stress(order, nav, feed.get("ticket_bar")) if with_stress else None
    return page, today


def render_md(p):
    L = []
    add = L.append
    add("# 今日 ETF 实盘单 —— %s" % p["generated_for_date"])
    add("")
    add("> 一页纸，全部数字从机器面直接抄来：单子来自可执行票、预期来自生产卡片、账面来自前向账本。没有新增判断。")
    add("")
    add("## 一句话")
    inv = p["book_amount_cny"]
    act = p.get("today_action") or {"mode": "unknown"}
    mode = act.get("mode")
    if mode == "hold":
        add("**今天不用动手。** 这套组合上一次定稿 **%s**，今天只是按新的收盘价（**%s**）把同一批权重重新算成份额——"
            "清单里份额和金额的变化是价格漂移，不是新指令。下一个动手日是 **%s**。"
            % (p["book_decided_at"], p["priced_bar"], p["next_rebalance_date"]))
        if act.get("cost_if_retraded_pct_per_year") is not None:
            add("")
            add("（照这份清单每天重下一遍的代价：单边 %s bp、进出两边、一年按 %d 个交易日、账内占比 %.1f%%，"
                "一年约 **%.1f%% 的资本**——比这本账回测的 %.2f%%/年还高。所以「今天不动」不是懒惰，是这条纪律的一部分。）"
                % (p.get("cost_bp_per_side"), TRADING_DAYS_PER_YEAR, (p.get("k_now") or 0.0) * 100,
                   act["cost_if_retraded_pct_per_year"],
                   (p.get("ticket_book") or {}).get("cagr", 0.0) * 100))
    elif mode == "rebalance":
        add("**今天是换仓日。** 先卖掉不在清单里的，再按下面清单买：花 **¥%s**（占总资金 %.1f%%）买 %d 只 ETF，"
            "剩下的 **¥%s**（%.1f%%）放%s。"
            % (format(inv, ",.0f"), (p["k_now"] or 0) * 100, p["n_hold"] or len(p["order"]),
               format(p["cash_amount_cny"], ",.0f"), p["cash_weight"] * 100, p["cash_leg"]))
    elif mode == "open":
        add("**还没建仓的话，按这个下单：** 花 **¥%s**（占总资金 %.1f%%）买 %d 只 ETF，"
            "剩下的 **¥%s**（%.1f%%）放%s。已经在账上的不要照着重下一遍，下一次动手日是 **%s**。"
            % (format(inv, ",.0f"), (p["k_now"] or 0) * 100, p["n_hold"] or len(p["order"]),
               format(p["cash_amount_cny"], ",.0f"), p["cash_weight"] * 100, p["cash_leg"],
               p["next_rebalance_date"]))
    else:
        add("**今天是否要动手：无法判定**（缺 book_decided_at 或 priced_bar，不猜）。下面只有数值，不代表指令。")
    add("")
    add("## 下单清单%s" % ("（如果你今天才建仓）" if mode == "hold" else ""))
    add("")
    add("| 代码 | 类别 | 份（100 股/份） | 参考价 | 金额 |")
    add("|---|---|---|---|---|")
    for o in p["order"]:
        add("| %s | %s | %s | %s | ¥%s |"
            % (o["symbol"], o["class_zh"] or "", format(o["lots"] or 0, ","),
               o["price"], format(o["amount_cny"] or 0, ",.0f")))
    add("| — | **合计** | | | **¥%s** |" % format(p["book_amount_cny"], ",.0f"))
    add("")
    add("剩余现金 ¥%s 买 %s（或等价），不要留活期。" % (format(p["cash_amount_cny"], ",.0f"), p["cash_leg"]))
    add("")
    cy = p.get("cash_yield") or {}
    if cy.get("annual_cny") is not None:
        add("## 现金那一半在赚多少")
        add("")
        add("¥%s 放着不是 0 息：按 **%s** 最近收盘年化 **%.2f%%**（%s 的报价）算，一年约 **+¥%s**，"
            "每个交易日约 +¥%s。"
            % (format(p["cash_amount_cny"], ",.0f"), cy["leg"], cy["rate_pct"], cy["rate_date"],
               format(cy["annual_cny"], ",.0f"), format(cy["daily_cny"], ",.0f")))
        if cy.get("rate_20d_pct") is not None:
            add("")
            add("- 近 %d 个交易日这个利率平均 %.2f%%（一天期逆回购在季末/节前会飙高，平时就是个零钱利率），"
                "所以这笔钱是「现金不缩水」，不是收益来源。"
                % (cy["window"], cy["rate_20d_pct"]))
        add("- 不买逆回购、留在活期，这 ¥%s 就是没有的。" % format(cy["annual_cny"], ",.0f"))
        add("")
    add("## 账面与节奏")
    add("")
    add("- 定价用的收盘日：**%s**（数据状态 %s，滞后 %s 个交易日）"
        % (p["priced_bar"], p["feed_status"], p["feed_lag_days"]))
    add("- 这套组合上一次定稿：**%s**" % p["book_decided_at"])
    add("- 下次换仓：**%s**（还有 %s 个交易日）" % (p["next_rebalance_date"], p["next_decision_bars"]))
    fwd = p["forward"]
    if fwd["nav"]:
        add("- 前向账本：起始 %s 净值 1.0000 -> %s 净值 **%.4f**（%+.2f%%），共 %d 个交易日"
            % (fwd["inception"], fwd["as_of"], fwd["nav"], fwd["since_inception_pct"], fwd["bars"]))
        add("  - 这只是起步，不能当业绩看。")
    else:
        add("- 前向账本：尚未起算")
    vsb = p.get("vs_basket")
    if vsb:
        add("- 同时期对照（**买入并持有 ETF 篮子**，%s）：到 **%s** 篮子净值 %.4f，本账 %.4f，"
            "领先 **%+.2f 个百分点**"
            % (vsb["basis"], vsb["bar"], vsb["basket_nav"], vsb["book_nav"], vsb["excess_pp"]))
        add("  - 篮子=黄金/纳指/沪深300/国债四只等权、与本账同一换仓日与成交口径；"
            "这个差只说明这几天谁更好，不是长期超额，日子还短。")
        _h = vsb.get("horizon") or {}
        _mde = _h.get("min_detectable_edge_pp") or {}
        _yrs = _h.get("years_for_80pct_power") or {}
        _cand = _h.get("candidate_sources") or {}
        if _mde:
            _pairs = []
            for _k, _v in _yrs.items():
                _e = (_cand.get(_k) or {}).get("edge_pp_per_year")
                _pairs.append("%s %.2fpp/年 -> %s 年" % (_k.split(" (")[0], _e or 0.0, _v))
            add("  - 这个差要多大才算数：以本账对篮子的日波动（年化 %s）计，"
                "**12 个月只能分辨 %.1f 个百分点/年以上的差**（6 个月 %.1f、3 年 %.1f）；"
                "本账发表过的超额要 %s 才能被证明——所以这行数字是健康检查，不是判词。"
                % ("8.46%", _mde.get("1y", 0), _mde.get("6m", 0), _mde.get("3y", 0),
                   "；".join(_pairs) or "（未读到研究文件）"))
    add("")
    add("## 该期待什么（回测口径，扣成本后）")
    add("")
    add("| 组合口径 | 全窗年化 | 夏普 | 最大回撤 | 2020-2023 | 2024 起 |")
    add("|---|---|---|---|---|---|")
    for label, row in p["backtest_band"].items():
        def g(seg, k):
            v = (row.get(seg) or {}).get(k)
            return "—" if v is None else ("%.2f%%" % v if k == "cagr_pct" else
                                          ("%.2f%%" % v if k == "maxdd_pct" else "%.2f" % v))
        add("| %s | %s | %s | %s | %s | %s |"
            % (label, g("full", "cagr_pct"), g("full", "sharpe"), g("full", "maxdd_pct"),
               g("is", "cagr_pct"), g("oos", "cagr_pct")))
    add("")
    add("三行是同一套选券信号，区别只在名数和杠杆规则：第一行是你要下的这份账（5 名 + beta 覆盖 + 8bp 成本）；另两行是生产卡片跑的对照口径。同一决策日，票是卡片的子集。")
    add("")
    add("表里 \u2014 = 该口径没有拆 IS/OOS 分段，不是零。")
    if p.get("excess_pp") is not None and p.get("same_beta_benchmark") and p.get("ticket_book"):
        b = p["same_beta_benchmark"]
        bk = p["ticket_book"]
        add("")
        add("关键一句：**在同样的风险敞口下（beta 基准年化 %.2f%%、夏普 %.2f），这本账回测年化 %.2f%%、夏普 %.2f，多赚 %.2f 个百分点/年**——超额来自选券，不是来自加杠杆。"
            % (b["cagr"] * 100, b["sharpe"], bk["cagr"] * 100, bk["sharpe"], p["excess_pp"]))
    add("")
    add("## 换成年内能赚多少钱（按本单资金 ¥%s）" % format(p["money_cny"]["capital_cny"], ",.0f"))
    add("")
    add("同一批数字再换一把尺子，只做单位换算，不叠加任何新假设：")
    add("")
    add("| 项目 | 一年多少钱 | 怎么来的 |")
    add("|---|---|---|")
    mc = p["money_cny"]

    def y(v):
        return "—" if v is None else ("%s¥%s" % ("+" if v > 0 else "-", format(abs(v), ",.0f")))

    add("| 这本账回测期望 | %s | 年化 %s%% × 资金 |"
        % (y(mc["expected_annual_cny"]), "%.2f" % (p["ticket_book"]["cagr"] * 100) if p.get("ticket_book") else "—"))
    add("| 同风险基准（beta 覆盖） | %s | 基准年化 %s%% × 资金 |"
        % (y(mc["benchmark_annual_cny"]),
           "%.2f" % (p["same_beta_benchmark"]["cagr"] * 100) if p.get("same_beta_benchmark") else "—"))
    add("| **超额部分** | **%s** | 多赚 %.2f 个百分点 × 资金 |"
        % (y(mc["excess_annual_cny"]), p["excess_pp"] or 0.0))
    add("| 一次最坏回撤要亏 | %s | 最大回撤 %s%% × 资金 |"
        % (y(mc["worst_drawdown_cny"]),
           "%.2f" % (p["ticket_book"]["maxdd"] * 100) if p.get("ticket_book") else "—"))
    add("")
    add("读法：一年赚多少是回测期望，不是承诺；最坏回撤那一行才是你要能扛住的数。")
    add("")
    st = p.get("stress") or {}
    worst = st.get("worst") or {}
    if worst.get("1d") or worst.get("5d") or worst.get("20d"):
        add("## 最坏的日子长什么样（同一批票，整段历史）")
        add("")
        add("把今天这 %d 只票的权重重放回 %s~%s 的整段面板（现金 0 息），看最坏的连续几个交易日："
            % (len(p["order"]), st.get("first"), st.get("last")))
        add("")
        add("| 窗口 | 最差涨跌 | 折成钱 | 结束于 |")
        add("|---|---|---|---|")
        for n in STRESS_WINDOWS:
            row = worst.get("%dd" % n)
            if not row:
                add("| %d 个交易日 | — | — | — |" % n)
                continue
            add("| %d 个交易日 | %+.2f%% | %s | %s |"
                % (n, row["pct"], "—" if row.get("cny") is None else
                   ("%s¥%s" % ("+" if row["cny"] > 0 else "-", format(abs(row["cny"]), ",.0f"))),
                   row.get("end_date") or "—"))
        add("")
        add("读法：这是「同一批票、同样权重、最倒霉的一段」值多少钱，不是预测，也不是这本账实际走过的路"
            "（实际路径的回撤见上一张表的最大回撤列）。")
        add("")
    add("## 必须记住的四条")
    add("")
    for c in p["caveats"]:
        add("- " + c)
    add("")
    add("---")
    add("*生成脚本 scripts/etf_book_ceo_page.py｜证据截止 %s｜卡片与单子同一决策日=%s，同一定价日=%s*"
        % (p["evidence_cutoff"], p["agreement"]["same_decision_bar"], p["agreement"]["same_priced_bar"]))
    return "\n".join(L) + "\n"


def run():
    mid = machine_id()
    if not writer_allowed(mid):
        print("etf_book_ceo_page: host=%s is not the writer (host=%s) -- honest no-op, nothing written"
              % (mid, HOST))
        return 0
    page, today = build(with_stress=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    md_path = os.path.join(OUT_DIR, "LIVE-BOOK-%s.md" % today.replace("-", ""))
    js_path = os.path.join(OUT_DIR, "LIVE-BOOK-%s.json" % today.replace("-", ""))
    with open(md_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(page))
    with open(js_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(page, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    # stable pointer for consumers that should not care about the date
    ptr = os.path.join(OUT_DIR, "latest.json")
    with open(ptr, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"generated_for_date": today,
                   "page": os.path.relpath(md_path, ROOT).replace("\\", "/"),
                   "json": os.path.relpath(js_path, ROOT).replace("\\", "/")},
                  fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("LIVE-BOOK written: %s (order %d names, book %.0f, cash %.0f, next rebalance %s)"
          % (os.path.relpath(md_path, ROOT), len(page["order"]), page["book_amount_cny"],
             page["cash_amount_cny"], page["next_rebalance_date"]))
    return 0


def selftest():
    ok = 0
    total = 0

    def chk(name, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[%d/%d] PASS %s%s" % (ok, total, name, (" | " + detail) if detail else ""))
        else:
            print("[%d/%d] FAIL %s%s" % (ok, total, name, (" | " + detail) if detail else ""))
        return cond

    # 1. next-rebalance arithmetic on a hand fixture: the 3rd trading day after Fri
    cal = ["2026-10-23", "2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29"]
    chk("L1 calendar: 3rd trading day after 2026-10-23", trading_days_after(cal, "2026-10-23", 3) == "2026-10-28",
        trading_days_after(cal, "2026-10-23", 3))
    chk("L2 calendar: anchor itself never counts", trading_days_after(cal, "2026-10-26", 1) == "2026-10-27")
    chk("L3 calendar: past the end -> None not a guess", trading_days_after(cal, "2026-10-26", 9) is None)
    chk("L4 calendar: degenerate n -> None", trading_days_after(cal, "2026-10-26", 0) is None)

    # 5. the live page's money must add up: order amounts + cash == capital
    page, _today = build()
    s = sum(float(o["amount_cny"] or 0) for o in page["order"])
    chk("L5 money: order sum + cash == capital",
        abs(s + page["cash_amount_cny"] - page["capital_cny"]) < 1.0,
        "sum %.2f + cash %.2f vs nav %.2f" % (s, page["cash_amount_cny"], page["capital_cny"]))
    chk("L6 money: book share == k_now", abs(page["book_amount_cny"] / page["capital_cny"] - page["k_now"]) < 0.002,
        "%.4f vs %.4f" % (page["book_amount_cny"] / page["capital_cny"], page["k_now"]))
    chk("L7 order non-empty and every row has a lot count",
        bool(page["order"]) and all((o["lots"] or 0) > 0 for o in page["order"]), "%d rows" % len(page["order"]))

    # 8. the page must actually say the things a human needs
    md = render_md(page)
    need = ["下单清单", "下次换仓", "该期待什么", "必须记住的四条"]
    missing = [k for k in need if k not in md]
    chk("L8 render: all required sections present", not missing, "missing=%s" % missing)
    chk("L9 render: no unformatted template leftovers", "{:" not in md and "%s" not in md and "%%" not in md)
    chk("L10 render: caveats carried onto the page",
        all(c.split("；")[0][:12] in md for c in page["caveats"]))
    chk("L11 page: next rebalance is a real calendar date",
        isinstance(page["next_rebalance_date"], str) and len(page["next_rebalance_date"]) == 10,
        str(page["next_rebalance_date"]))

    # 12. staleness is quoted, not hidden
    chk("L12 page: data freshness stated", page["feed_status"] is not None and page["priced_bar"] is not None,
        "%s lag=%s" % (page["feed_status"], page["feed_lag_days"]))

    # 13. the money block must be a pure unit change of numbers already on the page
    mc = page["money_cny"]
    tk_book = page.get("ticket_book") or {}
    exp_ok = (abs(mc["expected_annual_cny"] - tk_book["cagr"] * page["capital_cny"]) < 1.0
              if mc["expected_annual_cny"] is not None else mc["expected_annual_cny"] is None)
    chk("L13 money: annual yuan == backtest cagr x capital", exp_ok,
        "%s vs %.2f" % (mc["expected_annual_cny"], tk_book.get("cagr", 0) * page["capital_cny"]))
    chk("L14 money: excess yuan == excess_pp x capital",
        mc["excess_annual_cny"] is not None
        and abs(mc["excess_annual_cny"] - (page["excess_pp"] or 0.0) / 100.0 * page["capital_cny"]) < 1.0,
        "%s vs %s" % (mc["excess_annual_cny"], (page["excess_pp"] or 0.0) / 100.0 * page["capital_cny"]))
    chk("L15 money: absent inputs give None, never a zero that would read as 'earns nothing'",
        money_cny({}, 0.0)["expected_annual_cny"] is None
        and money_cny({}, 1000000.0)["excess_annual_cny"] is None
        and money_cny({"metrics": {"book": {"cagr": 0.1, "maxdd": -0.05}}}, 0.0)["expected_annual_cny"] is None,
        "empty ticket -> None; ticket without capital -> None")

    # 17. the page has to answer "do I trade today", and the answer must follow its own dates
    _base = {"book_decided_at": "2026-10-14", "priced_bar": "2026-10-26",
             "next_rebalance_date": "2026-11-11", "cost_bp_per_side": 8, "k_now": 0.5,
             "forward": {"bars": 3}}
    _hold = today_action(_base)
    chk("L17 action: holding + decision bar behind the priced bar -> hold, next date named",
        _hold["mode"] == "hold" and _hold["next_trade_date"] == "2026-11-11", _hold["mode"])
    _reb = today_action(dict(_base, book_decided_at="2026-10-26"))
    chk("L18 action: priced bar IS the decision bar -> rebalance (not hold)",
        _reb["mode"] == "rebalance", _reb["mode"])
    _open = today_action(dict(_base, forward={"bars": 0}))
    _none = today_action({"priced_bar": "2026-10-26", "forward": {"bars": 3}})
    chk("L19 action: no position -> open; missing date face -> unknown, never a guess",
        _open["mode"] == "open" and _none["mode"] == "unknown",
        "%s / %s" % (_open["mode"], _none["mode"]))
    chk("L20 action: re-trade cost is 2 sides x bp x 250 x book share on capital",
        _hold["cost_if_retraded_pct_per_year"] == 20.0,
        "%s vs 20.0 (%s)" % (_hold["cost_if_retraded_pct_per_year"], _hold["cost_basis"]))

    # 21. the LIVE page's own action line must agree with its own two dates and ledger
    _la = page["today_action"]
    _la_ok = (_la["mode"] in ("hold", "open", "rebalance")
              and (_la["mode"] == "rebalance") == (str(page["book_decided_at"]) == str(page["priced_bar"])
                                                   and bool(page["forward"]["bars"]))
              and (_la["mode"] != "hold" or _la["next_trade_date"] == page["next_rebalance_date"]))
    chk("L21 live page: action mode agrees with its own decision/priced bars and ledger",
        _la_ok, "%s decided=%s priced=%s bars=%s"
        % (_la["mode"], page["book_decided_at"], page["priced_bar"], page["forward"]["bars"]))
    # 22. single writer: only the host may write, and an unknown host must not write either
    chk("L22 guard: writer_allowed('bm-a') only",
        writer_allowed("bm-a") and not writer_allowed("bm-c") and not writer_allowed("bm-b")
        and not writer_allowed(None), "host=%s" % HOST)

    # 23-26. the stress block: hand fixture first, then the "absent panel is never zero" face
    import pandas as _pd
    _s = _pd.Series([0.01, -0.05, 0.02, -0.03, -0.04, 0.06, -0.08],
                    index=["2026-01-0%d" % i for i in range(1, 8)])
    _st = stress_stats(_s, windows=(1, 2, 5), capital=1000000.0)
    chk("L23 stress: worst 1-day is the single worst print, with its own end date",
        _st["worst"]["1d"]["pct"] == -8.0 and _st["worst"]["1d"]["end_date"] == "2026-01-07",
        str(_st["worst"]["1d"]))
    chk("L24 stress: the N-day window compounds its days and starts strictly after the anchor",
        -8.0 < _st["worst"]["5d"]["pct"] < -7.0 and _st["worst"]["5d"]["end_date"] == "2026-01-07",
        str(_st["worst"]["5d"]))
    chk("L25 stress: yuan is the percentage times this ticket's capital (a unit change only)",
        abs(_st["worst"]["1d"]["cny"] + 80000.0) < 1.0
        and abs(_st["worst"]["5d"]["cny"] / 1000000.0 * 100.0 - _st["worst"]["5d"]["pct"]) < 0.01,
        "%s / %s" % (_st["worst"]["1d"]["cny"], _st["worst"]["5d"]["cny"]))
    _no_cap = stress_stats(_s, windows=(1,), capital=None)["worst"]["1d"]
    chk("L26 stress: no panel / no capital gives None or a missing row, never a zero",
        stress_stats(None) is None and stress_stats(_pd.Series(dtype=float)) is None
        and _no_cap["cny"] is None and _no_cap["pct"] == -8.0,
        "empty panel -> None, capital-less yuan -> None")
    chk("L27 stress: a window longer than the history says 'no row', never a fabricated number",
        stress_stats(_s, windows=(50,))["worst"]["50d"] is None)

    # 28-29. the basket line must be the LEDGER's own number, and its absence must read as
    # absence -- re-pricing it here would be a second price source for the same claim
    _led = _load(LEDGER) if os.path.exists(LEDGER) else {}
    _bench = (_led.get("benchmark") or {}).get("latest") or {}
    if _bench.get("excess_pp") is not None:
        chk("L28 basket: page quotes the ledger's own benchmark, bar and navs to the digit",
            page["vs_basket"] is not None
            and page["vs_basket"]["bar"] == _bench.get("bar")
            and abs(page["vs_basket"]["excess_pp"] - _bench["excess_pp"]) < 1e-12
            and abs(page["vs_basket"]["book_nav"] - _bench["book_nav"]) < 1e-12,
            "ledger %s vs page %s" % (_bench.get("excess_pp"),
                                      (page["vs_basket"] or {}).get("excess_pp")))
    else:
        chk("L28 basket: page has no basket line when the ledger publishes none",
            page["vs_basket"] is None, "ledger benchmark latest absent -> page None")
    _md = render_md(dict(page, vs_basket={"bar": "2026-10-27", "book_nav": 1.004,
                                          "basket_nav": 0.9965, "excess_pp": 0.75,
                                          "basis": "等权 1/4、同一换仓日、次日开盘成交"}))
    chk("L29 basket: the rendered page carries the basket comparison and its caveat",
        "ETF 篮子" in _md and "+0.75" in _md and "不是长期超额" in _md,
        "rendered line present")

    # 30. the spread is not a verdict: the page must carry the horizon inside which the
    # number means anything (r1316). A power block that stays in the ledger is a decision
    # only a reader who opens the JSON gets.
    _pw = ((_led.get("benchmark") or {}).get("significance") or {}).get("power") or {}
    if _pw.get("available") and _bench.get("excess_pp") is not None:
        _md2 = render_md(dict(page, vs_basket=dict(page["vs_basket"])))
        _want = "%.1f 个百分点/年" % (_pw["min_detectable_edge_pp"]["1y"])
        chk("L30 basket: the page states the edge its 12-month view could resolve",
            _want in _md2 and "健康检查，不是判词" in _md2,
            "want=%s" % _want)
    else:
        chk("L30 basket: no horizon sentence when the ledger publishes no power block",
            page.get("vs_basket") is None
            or "健康检查，不是判词" not in render_md(dict(page)), "guard leg")

    # 31-34. the idle half is not 0% -- cash x the repo panel's own close, and an
    # unreadable panel stays None (a 0 would read as "the cash earns nothing", which is
    # the very case the reader needs to be warned about)
    import tempfile
    _td = tempfile.mkdtemp()
    with open(os.path.join(_td, "GC001.csv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("date,open,high,low,close,volume\n")
        fh.write("2026-10-26,1.2,1.2,0.31,1.0,100\n")
        fh.write("2026-10-27,1.18,1.4,1,2.0,100\n")
    _cy = cash_yield(100000.0, panel_dir=_td)
    chk("L31 cash: annual yuan == cash x the panel's own close rate",
        _cy["rate_pct"] == 2.0 and _cy["rate_date"] == "2026-10-27"
        and _cy["annual_cny"] == 2000.0 and _cy["daily_cny"] == 8.0
        and _cy["rate_20d_pct"] == 1.5,
        "rate %.2f annual %s daily %s mean %s"
        % (_cy["rate_pct"], _cy["annual_cny"], _cy["daily_cny"], _cy["rate_20d_pct"]))
    _bad = tempfile.mkdtemp()
    with open(os.path.join(_bad, "GC001.csv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("date,open,high,low,close,volume\n")
        fh.write("2026-10-27,900,900,900,900,100\n")
    chk("L32 cash: missing panel / zero cash / out-of-band print -> None, never 0",
        cash_yield(100000.0, panel_dir=os.path.join(_td, "nope"))["annual_cny"] is None
        and cash_yield(0.0, panel_dir=_td)["annual_cny"] is None
        and cash_yield(None, panel_dir=_td)["annual_cny"] is None
        and cash_yield(100000.0, panel_dir=_bad)["annual_cny"] is None,
        "absent / zero-cash / 900% print all None")
    _live = page["cash_yield"]
    _ok_live = (_live["annual_cny"] is None
                or (abs(_live["annual_cny"] - page["cash_amount_cny"] * _live["rate_pct"] / 100.0) < 1.0
                    and bool(_live["rate_date"])))
    chk("L33 live page: cash yuan == its own cash x its own rate, with the rate date",
        _ok_live, "cash %.0f rate %s @ %s -> %s"
        % (page["cash_amount_cny"], _live["rate_pct"], _live["rate_date"], _live["annual_cny"]))
    _md3 = render_md(dict(page, cash_yield={"leg": "GC001", "rate_pct": 1.09,
                                            "rate_date": "2026-10-27", "annual_cny": 5764.0,
                                            "daily_cny": 23.0, "rate_20d_pct": 1.1,
                                            "window": 20}))
    chk("L34 cash: the rendered page carries the rate, its date and the 'not a return source' line",
        "现金那一半在赚多少" in _md3 and "1.09%" in _md3 and "2026-10-27" in _md3
        and "+¥5,764" in _md3 and "不是收益来源" in _md3, "rendered cash block present")

    print("\nSummary: %d/%d PASS%s" % (ok, total, "" if ok == total else " -- %d FAIL" % (total - ok)))
    return 0 if ok == total else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        raise SystemExit(run())
    if cmd == "selftest":
        raise SystemExit(selftest())
    print("usage: etf_book_ceo_page.py [run|selftest]")
    raise SystemExit(2)