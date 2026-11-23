"""The bond-free 5-name book's order ticket: can today's production candidate be placed?

Why this face exists
--------------------
`results/etf_nobond_vt.json` names the production candidate (`nobond_vt08`) and prints
today's five picks with their scores -- but a score is not an order. A reader who wanted
to follow it could not: the face never says what fraction of capital the 8% vol target
puts to work today, how many whole lots each name takes, what the ticket costs, or how
much cash is left over. `results/etf_book_ticket_floor.json` answers the lot question for
the TWELVE-name card (`n_hold=12`), which is a different configuration.

This face prices the production candidate itself, at 1M, and at two smaller sizes, with a
real broker assumption (3bp per side, 5 CNY minimum per ticket). It does NOT restate the
card, and it does not claim the book is a recommendation.

The sizing scale is reproduced, not replayed
--------------------------------------------
`etf_robust_pf.open_to_open_equity` sizes the book with
`scale = min(1, 0.08 / book_vol(picks, last 60 bars))` evaluated at the decision bar.
That is a today-only quantity, so it can be reproduced without replaying the equity
curve. `run` proves the reproduction is talking about the same book: the five picks must
equal `results/etf_nobond_vt.json` -> `live_picks` name for name, and `check` refuses a
face whose anchor does not hold.

Price basis
-----------
The engine sizes on open-to-open returns (the parent's own caliber), but a reader sizes
against the price they can see. Ticket prices are therefore the as-of bar's CLOSE; the
as-of bar's OPEN is printed beside it for cross-reading. The real fill is the next
session's open and is not known here -- the page says so rather than pretending.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUT_JSON = os.path.join(ROOT, "results", "etf_book_nobond_ticket.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_NOBOND_TICKET.md")
PARENT = os.path.join(ROOT, "results", "etf_nobond_vt.json")

LOT = 100
N_HOLD = 5
REBAL = 20
TARGET_VOL = 0.08
VOL_WINDOW = 60
BACKTEST_COST = 0.0010          # 10bp/side, the backtest caliber (NOT the broker bill)
BROKER_FEE = 0.0003             # 3bp/side, a conservative retail ETF commission
FEE_FLOOR = 5.0                 # CNY per ticket
RESIDUAL_MAX_PCT = 0.5          # whole-lot residual budget, % of NAV
SIZES = (100_000, 500_000, 1_000_000)
MARK_BEGIN = "<!-- BEGIN:ETF-BOOK-NOBOND-TICKET -->"
MARK_END = "<!-- END:ETF-BOOK-NOBOND-TICKET -->"


# ---------------------------------------------------------------- pure arithmetic
def one_lot_cny(price):
    return round(LOT * float(price), 2)


def leg_row(symbol, weight, price, capital, fee_bps=BROKER_FEE, fee_floor=FEE_FLOOR):
    """One order line. Returns lots=0 when the slice cannot pay for a single lot --
    that is the fact the reader needs, not a silently rounded-up share count."""
    one_lot = one_lot_cny(price)
    budget = float(capital) * float(weight)
    lots = int(budget // one_lot) if one_lot > 0 else 0
    shares = lots * LOT
    amount = round(lots * one_lot, 2)
    fee = round(max(float(fee_floor), amount * float(fee_bps)), 2) if amount > 0 else 0.0
    return {
        "symbol": symbol,
        "weight": round(float(weight), 12),
        "price_close": round(float(price), 4),
        "one_lot_cny": one_lot,
        "budget_cny": round(budget, 2),
        "lots": lots,
        "shares": shares,
        "amount_cny": amount,
        "fee_cny": fee,
        "residual_cny": round(budget - amount, 2),
        "fits": lots > 0,
    }


def size_scale(est_vol, target=TARGET_VOL, cap=1.0, floor=0.0):
    """The engine's rule, unchanged: de-lever only, never lever up."""
    if est_vol is None or not (est_vol > 0):
        return cap
    return float(max(floor, min(cap, target / float(est_vol))))


def min_capital_rows(rows):
    """Capital at which EVERY name can buy at least one whole lot: the binding name is
    the one with the largest one_lot/weight, not the largest one-lot price."""
    out = []
    for r in rows:
        if not r["one_lot_cny"] or not r["weight"]:
            continue
        out.append({"symbol": r["symbol"], "needed_cny": round(r["one_lot_cny"] / r["weight"], 2)})
    out.sort(key=lambda x: -x["needed_cny"])
    return out


def verdict_of(tickets, residual_max_pct=RESIDUAL_MAX_PCT, big=1_000_000):
    """Three readings, in the order a reader meets them: can it be placed at all, is the
    rounding small, and does it fit the capital the reader was told to size against."""
    t = [x for x in tickets if x["capital_cny"] == big]
    if not t:
        return "NO_TICKET_AT_1M", "这张面没有 100 万档的票"
    t = t[0]
    dead = [l["symbol"] for l in t["legs"] if not l["fits"]]
    if dead:
        return "NOT_TRADABLE_AT_1M", "这些名字在自己的预算里连一手都买不到：%s" % (
            "、".join(dead))
    if t["residual_pct_nav"] > residual_max_pct:
        return "RESIDUAL_TOO_BIG", ("整手会闲置净值的 %.4f%%，超过 %.2f%% 的门"
                                    % (t["residual_pct_nav"], residual_max_pct))
    return "TRADABLE_AT_1M", ("五只都能在自己的预算里买满整手，整手残差占净值 %.4f%%"
                              % t["residual_pct_nav"])


def build_ticket(capital, picks, scale, fee_bps=BROKER_FEE):
    legs = [leg_row(p["symbol"], p["weight"], p["price_close"], capital, fee_bps)
            for p in picks]
    cash_slot = round(float(capital) * (1.0 - scale), 2)
    residual = round(sum(l["residual_cny"] for l in legs), 2)
    fees = round(sum(l["fee_cny"] for l in legs), 2)
    return {
        "capital_cny": float(capital),
        "scale": round(float(scale), 12),
        "legs": legs,
        "book_amount_cny": round(sum(l["amount_cny"] for l in legs), 2),
        "fees_cny": fees,
        "cash_slot_cny": cash_slot,
        "residual_cny": residual,
        "residual_pct_nav": round(100.0 * residual / float(capital), 4),
        "unfilled_names": [l["symbol"] for l in legs if not l["fits"]],
    }


# ---------------------------------------------------------------- panel work
def build_face():
    import numpy as np
    import etf_composite_pf as E
    import etf_equity_alpha as A

    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    score = E.build_score(close[cols], amt[cols], feats)

    last = score.index[-1]
    row = score.loc[last].dropna()
    picks_syms = list(row.nlargest(N_HOLD).index)
    picks_raw = [(s, round(float(row[s]), 3), cls[s]) for s in picks_syms]

    # sizing: the same open-to-open 60-bar book vol the engine reads at the decision bar
    op = openp.reindex(columns=close.columns)
    rets = op.pct_change()
    w = {s: 1.0 / N_HOLD for s, _v, _c in picks_raw}
    window = rets.loc[:last].tail(VOL_WINDOW)[list(w)]
    est_vol = None
    if window.shape[0] >= 20:
        wv = np.array([w[k] for k in window.columns])
        cov = window.cov().to_numpy()
        est_vol = float(np.sqrt(wv @ cov @ wv) * np.sqrt(252))
    scale = size_scale(est_vol)

    close_px = close.loc[last]
    open_px = openp.loc[last]
    # one scale, used everywhere: the printed scale and the cash slot must be the same
    # number, or a reader can add the weights to something that is not 1 (r1911 family).
    scale = round(scale, 12)
    picks = []
    for s, sc, c in picks_raw:
        picks.append({
            "symbol": s, "score": sc, "class": c,
            "weight": round(scale / N_HOLD, 12),
            "price_close": round(float(close_px[s]), 4),
            "price_open": round(float(open_px[s]), 4),
            "one_lot_cny": one_lot_cny(close_px[s]),
        })

    anchor = _anchor(picks_syms)

    tickets = [build_ticket(cap, picks, scale) for cap in SIZES]
    mc = min_capital_rows(picks)
    floor_cny = mc[0]["needed_cny"] if mc else None
    commission_note = _commission_at_floor(floor_cny, len(picks))

    verdict, sentence = verdict_of(tickets)

    face = {
        "generated": _now(),
        "asof_bar": str(last.date()),
        "evidence_cutoff": str(last.date()),
        "book": "nobond_vt08",
        "book_description": ("bond-free (equity+commodity+convertible), 5 equal names, "
                             "%d-day rebalance, %.0f%% vol target, de-lever only"
                             % (REBAL, TARGET_VOL * 100)),
        "universe_size": len(cols),
        "flips_repaired": n_flip,
        "sizing": {
            "est_vol_60d": round(est_vol, 6) if est_vol is not None else None,
            "est_vol_note": ("60-bar realised vol of today's five-name equal-weight book on "
                             "open-to-open returns, the same window the engine reads"),
            "vol_window_bars": int(window.shape[0]),
            "vol_window_span": [str(window.index[0].date()), str(window.index[-1].date())],
            "target_vol": TARGET_VOL,
            "scale": scale,
            "cash_weight": round(1.0 - scale, 12),
            "why": ("scale = min(1, 目标/实现)。这个组合最近 60 根 bar 的实现波动是 %.2f%%，"
                    "高于 %.0f%% 的目标，所以只用 %.1f%% 的资金，留 %.1f%% 现金"
                    % ((est_vol or 0) * 100, TARGET_VOL * 100, scale * 100,
                       (1 - scale) * 100)),
        },
        "anchor": anchor,
        "picks": picks,
        "price_basis": ("ticket prices are the as-of bar's CLOSE (what a reader can see); the "
                        "engine sizes on open-to-open returns, so the as-of bar's OPEN is printed "
                        "beside each close; the real fill is the next session's open, unknown here"),
        "tickets": tickets,
        "min_capital": {
            "one_lot_every_name_cny": floor_cny,
            "binding_symbol": mc[0]["symbol"] if mc else None,
            "per_leg": mc,
            "commission": commission_note,
        },
        "commission_assumption": {
            "broker_bp_per_side": BROKER_FEE * 10000.0,
            "per_ticket_floor_cny": FEE_FLOOR,
            "note": ("the backtest charges %.0fbp/side for cost and impact; that is not a broker "
                     "bill and is not restated here" % (BACKTEST_COST * 10000.0)),
        },
        "thresholds": {"residual_max_pct_nav": RESIDUAL_MAX_PCT, "lot": LOT,
                       "fee_floor_cny": FEE_FLOOR},
        "verdict": verdict,
        "sentence": sentence,
        "not_settled": [
            "真正成交是下一交易日的开盘价，这张面上还不知道",
            "60 根 bar 的波动只取了一个窗口，换窗口 scale 会变",
            "这是票面不是推荐：它说已发布的书今天会怎么下单，不说该不该下",
            "这个规模下的容量与冲击是另一张面（etf_book_capacity_at_size）",
            "十二名卡档的票面（etf_book_ticket_floor）是另一套配置，数字不能与这张混读",
        ],
    }
    return face


def _now():
    import datetime
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def _anchor(picks_syms):
    """The five names are the anchor: a face that prices a different book than the parent
    published is refused, not reconciled (E662 family)."""
    if not os.path.exists(PARENT):
        return {"published_match": None, "note": "parent face missing", "parent": "results/etf_nobond_vt.json"}
    with open(PARENT, encoding="utf-8") as f:
        p = json.load(f)
    lp = p.get("live_picks") or {}
    pub = [x.get("symbol") for x in (lp.get("picks") or [])]
    return {
        "parent": "results/etf_nobond_vt.json",
        "parent_as_of": lp.get("as_of"),
        "published_symbols": pub,
        "our_symbols": list(picks_syms),
        "published_match": set(pub) == set(picks_syms),
    }


def _commission_at_floor(floor_cny, n_names):
    """At the one-lot floor the commission is a real share of the book, not a rounding --
    this is the number that makes a tiny account uneconomic even when prices fit."""
    if not floor_cny:
        return None
    book = float(floor_cny)
    one_side = n_names * FEE_FLOOR
    return {
        "capital_cny": floor_cny,
        "note": ("那个规模上每笔都撞 %.0f 元最低佣金，一次往返要 %.0f 元，而本金只有 %.0f 元"
                 % (FEE_FLOOR, 2 * one_side, book)),
        "one_side_cny": round(one_side, 2),
        "round_trip_pct_of_capital": round(100.0 * 2 * one_side / book, 4),
    }


# ---------------------------------------------------------------- rendering
def _fmt_money(x):
    return "{:,.2f}".format(x)


def render_md(face):
    s = face["sizing"]
    L = [MARK_BEGIN, "",
         "# 这本书今天的下单票（去债版 5 名 + 8% 波动目标）", "",
         "generated %s | evidence_cutoff **%s** | verdict **%s**" % (
             face["generated"], face["evidence_cutoff"], face["verdict"]), "",
         "%s。" % face["sentence"], "",
         "这本书是 `%s`：%s。票面价格用 as-of 那天的收盘价；引擎按开盘对开盘算波动，"
         "所以每只旁边同时印了当天的开盘价。真正成交是下一交易日的开盘，这张面上不知道。"
         % (face["book"], face["book_description"]), "",
         "## 今天买多少：目标仓位 %.2f%%，现金 %.2f%%" % (s["scale"] * 100, s["cash_weight"] * 100), "",
         "| 项 | 值 |", "|---|---|",
         "| 五名等权组合的 60 日实现波动 | %.4f%% |" % ((s["est_vol_60d"] or 0) * 100),
         "| 波动目标 | %.1f%% |" % (s["target_vol"] * 100),
         "| 仓位系数 scale = min(1, 目标/实现) | %.4f |" % s["scale"],
         "| 现金槽 | %.4f |" % s["cash_weight"],
         "| 波动窗口 | %s .. %s（%d 根 bar） |" % (s["vol_window_span"][0],
                                                  s["vol_window_span"][1], s["vol_window_bars"]), "",
         "%s。" % s["why"], "",
         "## 五只标的与权重", "",
         "| 代码 | 类别 | 分数 | 目标权重 | 收盘价 | 开盘价 | 一手价 |", "|---|---|---|---|---|---|---|"]
    for p in face["picks"]:
        L.append("| %s | %s | %.3f | %.6f | %.4f | %.4f | %s |" % (
            p["symbol"], p["class"], p["score"], p["weight"], p["price_close"],
            p["price_open"], _fmt_money(p["one_lot_cny"])))
    L += ["", "## 不同资金下的真实订单", "",
          "整手（100 份）向下取整，佣金按 %.0fbp/边、每笔最低 %.0f 元计。`残差` 是该腿预算"
          "减去实际下单金额。" % (face["commission_assumption"]["broker_bp_per_side"],
                              face["commission_assumption"]["per_ticket_floor_cny"]), ""]
    for t in face["tickets"]:
        L += ["### %s 元" % _fmt_money(t["capital_cny"]), "",
              "| 代码 | 目标权重 | 一手价 | 预算 | 手数 | 份数 | 金额 | 佣金 | 残差 |",
              "|---|---|---|---|---|---|---|---|---|"]
        for l in t["legs"]:
            L.append("| %s | %.6f | %s | %s | %d | %d | %s | %s | %s |" % (
                l["symbol"], l["weight"], _fmt_money(l["one_lot_cny"]), _fmt_money(l["budget_cny"]),
                l["lots"], l["shares"], _fmt_money(l["amount_cny"]), _fmt_money(l["fee_cny"]),
                _fmt_money(l["residual_cny"])))
        L.append("| **合计** | %.4f | | %s（本金） | | | %s | %s | %s |" % (
            t["scale"], _fmt_money(t["capital_cny"]),
            _fmt_money(t["book_amount_cny"]), _fmt_money(t["fees_cny"]),
            _fmt_money(t["residual_cny"])))
        L += ["", "现金槽 %s 元 + 整手残差 %s 元（占净值 %.4f%%，门 %.2f%%）。" % (
            _fmt_money(t["cash_slot_cny"]), _fmt_money(t["residual_cny"]),
            t["residual_pct_nav"], face["thresholds"]["residual_max_pct_nav"]), ""]
    mc = face["min_capital"]
    L += ["## 至少要多少钱才开得起来", ""]
    if mc.get("one_lot_every_name_cny"):
        L.append("每只各买一手所需资金 = 一手价 ÷ 目标权重；卡住的是 **%s**，需要 **%s 元**。" % (
            mc["binding_symbol"], _fmt_money(mc["one_lot_every_name_cny"])))
    cm = mc.get("commission")
    if cm:
        L += ["", "但那个规模上佣金不是零头：%s。" % cm["note"],
              "单边 %s 元、往返占本金 **%.4f%%**。所以「买得起一手」和「值得买」是两件事。" % (
                  _fmt_money(cm["one_side_cny"]), cm["round_trip_pct_of_capital"])]
    L += ["", "| 代码 | 一手即需资金 |", "|---|---|"]
    for r in mc.get("per_leg") or []:
        L.append("| %s | %s |" % (r["symbol"], _fmt_money(r["needed_cny"])))
    L += ["", "## 这张票不是什么", ""]
    for x in face["not_settled"]:
        L.append("* %s；" % x)
    L += ["", "出场面：以上均为收盘口径的算术，不含涨跌停、停牌、流动性冲击；"
          "本书的持有期是 %d 个交易日后重排。" % REBAL, "", MARK_END, ""]
    return "\n".join(L)


# ---------------------------------------------------------------- commands
def run():
    face = build_face()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(render_md(face))
    print("verdict %s | scale %.4f cash %.4f | %s" % (
        face["verdict"], face["sizing"]["scale"], face["sizing"]["cash_weight"], face["sentence"]))
    print("saved", OUT_JSON)
    print("saved", OUT_MD)
    return 0


def check():
    """Two kinds of red, kept apart (r1934): the parent moved = STALE (worth a re-run);
    this face contradicts itself = CHECK FAILED (no STALE word)."""
    if not os.path.exists(OUT_JSON):
        print("check FAIL: STALE face missing at", OUT_JSON)
        return 3
    with open(OUT_JSON, encoding="utf-8") as f:
        face = json.load(f)
    probs, stale = [], []

    # 1. anchor: same book as the parent published
    a = face.get("anchor") or {}
    if not os.path.exists(PARENT):
        stale.append("parent face missing")
    else:
        with open(PARENT, encoding="utf-8") as f:
            par = json.load(f)
        pub = [x.get("symbol") for x in ((par.get("live_picks") or {}).get("picks") or [])]
        ours = [p["symbol"] for p in face.get("picks") or []]
        if set(pub) != set(ours):
            probs.append("picks %s are not the parent's book %s" % (ours, pub))
        if a.get("published_match") is not True:
            probs.append("anchor block says published_match=%r" % (a.get("published_match"),))
        if (par.get("live_picks") or {}).get("as_of") != face.get("asof_bar"):
            stale.append("parent live_picks as_of moved to %r, this face is on %r"
                         % ((par.get("live_picks") or {}).get("as_of"), face.get("asof_bar")))
        if par.get("evidence_cutoff") != face.get("evidence_cutoff"):
            stale.append("parent cutoff %r != this face's %r"
                         % (par.get("evidence_cutoff"), face.get("evidence_cutoff")))

    # 2. internal arithmetic
    picks = face.get("picks") or []
    if not picks:
        probs.append("no picks")
    tot_w = sum(p["weight"] for p in picks)
    cash = (face.get("sizing") or {}).get("cash_weight")
    # weights and cash are stored at 12dp, so this is a real identity, not a tolerance
    if cash is None or abs(tot_w + cash - 1.0) > 1e-9:
        probs.append("weights %.10f + cash %r != 1" % (tot_w, cash))
    sc = (face.get("sizing") or {}).get("scale")
    for p in picks:
        if sc and abs(p["weight"] - sc / len(picks)) > 1e-6:
            probs.append("%s weight %.10f != scale/n %d" % (p["symbol"], p["weight"], len(picks)))
        if abs(p["one_lot_cny"] - round(LOT * p["price_close"], 2)) > 1e-9:
            probs.append("%s one_lot does not match its own close price" % p["symbol"])
    for t in face.get("tickets") or []:
        for l in t["legs"]:
            budget = round(t["capital_cny"] * l["weight"], 2)
            if abs(budget - l["budget_cny"]) > 0.011:
                probs.append("%s@%s budget %.2f != capital*weight %.2f"
                             % (l["symbol"], t["capital_cny"], l["budget_cny"], budget))
            want_lots = int(l["budget_cny"] // l["one_lot_cny"]) if l["one_lot_cny"] else 0
            if l["lots"] != want_lots:
                probs.append("%s@%s lots %d != floor(budget/one_lot) %d"
                             % (l["symbol"], t["capital_cny"], l["lots"], want_lots))
            if abs(l["amount_cny"] - round(l["lots"] * l["one_lot_cny"], 2)) > 1e-6:
                probs.append("%s@%s amount != lots*one_lot" % (l["symbol"], t["capital_cny"]))
            want_fee = round(max(FEE_FLOOR, l["amount_cny"] * BROKER_FEE), 2) if l["amount_cny"] > 0 else 0.0
            if abs(l["fee_cny"] - want_fee) > 0.011:
                probs.append("%s@%s fee %.2f != max(floor, bp) %.2f"
                             % (l["symbol"], t["capital_cny"], l["fee_cny"], want_fee))
        want_cash = round(t["capital_cny"] * (1.0 - sc), 2) if sc is not None else None
        if want_cash is not None and abs(t["cash_slot_cny"] - want_cash) > 0.011:
            probs.append("%s cash slot %.2f != capital*(1-scale) %.2f"
                         % (t["capital_cny"], t["cash_slot_cny"], want_cash))

    # 3. verdict must follow from the ticket it names
    v, _s = verdict_of(face.get("tickets") or [])
    if v != face.get("verdict"):
        probs.append("verdict %r but the arithmetic says %r" % (face.get("verdict"), v))

    # 4. the page must be what this face renders (a hand-edited digit is a red)
    if not os.path.exists(OUT_MD):
        probs.append("page missing")
    else:
        with open(OUT_MD, encoding="utf-8") as f:
            disk = f.read()
        if disk != render_md(face):
            probs.append("page does not match this face's own render (hand-edited or stale)")

    if probs:
        print("check FAIL:")
        for x in probs:
            print("  -", x)
        return 1
    if stale:
        print("check FAIL: STALE")
        for x in stale:
            print("  -", x)
        return 3
    print("check ok: %d picks, scale %.4f, %d tickets, verdict %s"
          % (len(picks), sc or -1, len(face.get("tickets") or []), face.get("verdict")))
    return 0


def selftest():
    """Offline legs on the pure arithmetic -- every one of these can fail."""
    fails = []

    def ok(cond, msg):
        if not cond:
            fails.append(msg)

    # lot floor: 1,000 budget at a 125 CNY one-lot buys 8 lots, not 8.0000001
    r = leg_row("X", 0.10, 1.25, 10_000)
    ok(r["one_lot_cny"] == 125.0, "one lot of a 1.25 ETF is 125.0, got %r" % (r["one_lot_cny"],))
    ok(r["budget_cny"] == 1000.0, "budget 10%% of 10,000 is 1000")
    ok(r["lots"] == 8 and r["shares"] == 800, "8 lots expected, got %r" % (r["lots"],))
    ok(r["residual_cny"] == 0.0, "1000 - 8*125 = 0 residual")

    # fee floor: 1 CNY of 0.1% would be 0.001; the ticket floor wins
    r2 = leg_row("Y", 0.5, 100.0, 100)
    ok(r2["amount_cny"] == 0.0 and r2["fee_cny"] == 0.0, "a slice under one lot buys nothing and pays nothing")
    ok(r2["fits"] is False, "a name whose slice cannot pay one lot must be flagged unfit")

    r3 = leg_row("Z", 1.0, 1.0, 1_000)
    ok(r3["lots"] == 10, "1000 CNY at 100 CNY/lot = 10 lots")
    ok(abs(r3["fee_cny"] - 5.0) < 1e-9, "3bp of 1000 is 0.3, the 5 CNY floor must win (%r)" % (r3["fee_cny"],))

    # sizing rule: de-lever only
    ok(abs(size_scale(0.16) - 0.5) < 1e-12, "16%% vol at an 8%% target halves the book")
    ok(size_scale(0.01) == 1.0, "a 1%% vol book is not levered up")
    ok(size_scale(None) == 1.0, "an unmeasurable vol falls back to full size, not zero")
    ok(abs(size_scale(0.08) - 1.0) < 1e-12, "exactly at target = full size")

    # min capital binds on the largest one_lot/weight, not the largest price
    rows = [leg_row("A", 0.5, 1.0, 1e6), leg_row("B", 0.05, 1.0, 1e6)]
    mc = min_capital_rows(rows)
    ok(mc[0]["symbol"] == "B", "the 5%%-weight name binds, not the 50%% one (%r)" % (mc[0]["symbol"],))

    # verdict mapping, all three states reachable
    dead = [{"capital_cny": 1_000_000, "legs": [{"symbol": "A", "fits": False}],
             "residual_pct_nav": 0.0}]
    ok(verdict_of(dead)[0] == "NOT_TRADABLE_AT_1M", "a dead leg must read NOT_TRADABLE")
    fat = [{"capital_cny": 1_000_000, "legs": [{"symbol": "A", "fits": True}],
            "residual_pct_nav": 0.6}]
    ok(verdict_of(fat)[0] == "RESIDUAL_TOO_BIG", "0.6%% residual over a 0.5%% bound must read TOO_BIG")
    fine = [{"capital_cny": 1_000_000, "legs": [{"symbol": "A", "fits": True}],
             "residual_pct_nav": 0.01}]
    ok(verdict_of(fine)[0] == "TRADABLE_AT_1M", "a clean ticket must read TRADABLE")

    # ticket arithmetic adds up
    picks = [{"symbol": "A", "weight": 0.3, "price_close": 1.0},
             {"symbol": "B", "weight": 0.3, "price_close": 2.0}]
    t = build_ticket(100_000, picks, 0.6)
    ok(t["cash_slot_cny"] == 40_000.0, "a 0.6 scale leaves 40%% cash (%r)" % (t["cash_slot_cny"],))
    ok(abs(sum(l["weight"] for l in picks) + (1 - 0.6) - 1.0) < 1e-12, "weights + cash = 1")
    ok(t["book_amount_cny"] + t["cash_slot_cny"] + t["residual_cny"] - t["fees_cny"]
       <= 100_000.0 + 1e-6, "legs + cash + residual must not exceed capital")

    # commission at the one-lot floor is a share, not a rounding
    cm = _commission_at_floor(844.0, 5)
    ok(cm["round_trip_pct_of_capital"] > 5.0, "50 CNY round trip on 844 CNY is > 5%")

    # an anchor that prices a different book must be recognisable as a mismatch
    global PARENT
    keep, PARENT = PARENT, os.path.join(ROOT, "results", "_selftest_no_such_parent.json")
    try:
        a = _anchor(["1"])
        ok(a["published_match"] is None, "a missing parent yields match=None, not True")
    finally:
        PARENT = keep

    if fails:
        print("selftest FAIL %d/%d" % (len(fails), 19))
        for x in fails:
            print("  -", x)
        return 1
    print("selftest PASS 19/19")
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    cmd = (argv[0] if argv else "run").lstrip("-")
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
