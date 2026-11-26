"""The ETF book's minimum executable capital, priced per book class.

Why this face exists
--------------------
`research/ETF_BOOK_LOT_LADDER.md` priced the *with-bond* book down to 20,000 CNY and
found the wall: its picks are often par-100 bond/money ETFs (511160, 511360, 511220),
one lot of which is 10,000-11,500 CNY, so five names need ~57,000 CNY before the book is
even representable -- at 20,000 CNY the account sat 71% in cash and the fee floor ate
0.80%/yr.

The production candidate (`etf_nobond_vt.nobond_vt08`, the bond-free book with the 8% vol
target) selects a different universe, and its tickets are 0.6-1.7 CNY per share: one lot is
60-170 CNY. So the same question has a different answer, and nobody had priced it. That
answer is what a reader actually needs before deciding whether this book is theirs: *how
much money does it take to hold the rule faithfully?*

Two different walls are measured here, and they bind on different books:

  * **lot bound** -- five names, one lot each: ``5 * max(price * 100)``. This is the
    with-bond book's wall and it is set by the instrument's face value.
  * **fee-floor bound** -- the broker charges ``max(5 CNY, 10bp)`` per ticket; a ticket of
    ``C/5`` carries a floor fraction ``5 / (C/5) = 25 / C``. Requiring that fraction to stay
    under a criterion ``crit`` gives ``C >= 25 / crit``. This is the bond-free book's wall
    and it is set by the broker, not the instrument.

Everything is arithmetic on two published faces plus the panel's own closes -- no second
backtester, no re-selection. The picks are read from
``results/etf_nobond_vt.json`` and ``results/etf_composite_pf.json`` and priced on their own
``as_of`` date, so a stale picks list cannot borrow today's prices and look current.

Usage
-----
    python scripts/etf_book_min_capital_by_class.py run       # write json + page
    python scripts/etf_book_min_capital_by_class.py check     # re-derive the arithmetic
    python scripts/etf_book_min_capital_by_class.py selftest  # offline invariants
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

LOT = 100
FEE_FLOOR = 5.0
COST = 0.0010          # 10bp per side: the caliber every published ETF face uses
N_HOLD = 5
FEE_CRIT = 0.0025      # a ticket may not spend more than 25bp of its own slice on the floor
RUNGS = (2500, 5000, 10000, 20000, 50000, 100000, 1000000)

BOOKS = (
    ("bond_free_production", "results/etf_nobond_vt.json"),
    ("with_bond", "results/etf_composite_pf.json"),
)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_min_capital_by_class.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_MIN_CAPITAL_BY_CLASS.md")


def ticket_cost(notional, cost=COST, fee_floor=FEE_FLOOR):
    """Commission on one ticket, imported behaviour from the published lot ladder."""
    if notional <= 0:
        return 0.0
    return max(fee_floor, notional * cost)


def lot_bound(prices):
    """Capital at which every one of the n names can hold exactly one lot."""
    return float(N_HOLD) * max(prices.values()) * LOT


def fee_bound(crit=FEE_CRIT):
    """Capital at which the per-ticket fee floor stops exceeding `crit` of its slice."""
    return FEE_FLOOR * N_HOLD / crit


def min_capital(prices, crit=FEE_CRIT):
    """max(lot bound, fee-floor bound) -- both walls must be cleared, not one."""
    lb = lot_bound(prices)
    fb = fee_bound(crit)
    if lb >= fb:
        return lb, "LOT_BOUND"
    return fb, "FEE_FLOOR_BOUND"


def allocate(prices, cap):
    """Equal-slice whole-lot allocation that is payable *including* the fee floor.

    Starts from the largest affordable lot count per name, then drops one lot from the
    biggest position until the tickets can actually be paid for. Without that step a
    nearly-fully-invested rung spends a few hundred CNY of fees it does not have, which
    is how a ladder prints a negative cash balance (r2139 first run).
    """
    n = len(prices)
    target = float(cap) / n
    lots = {}
    for sym, px in prices.items():
        lot_notional = px * LOT
        lots[sym] = int(target // lot_notional) if lot_notional > 0 else 0
    for _ in range(10000):
        notional = sum(lots[s] * prices[s] * LOT for s in lots)
        fees = sum(ticket_cost(lots[s] * prices[s] * LOT) for s in lots if lots[s] > 0)
        if notional + fees <= cap + 1e-9:
            return lots, notional, fees
        held = [s for s in lots if lots[s] > 0]
        if not held:
            return lots, 0.0, 0.0
        biggest = max(held, key=lambda s: lots[s] * prices[s] * LOT)
        lots[biggest] -= 1
    return lots, notional, fees


def ladder(prices, rungs=RUNGS, crit=FEE_CRIT):
    """For each capital rung: what the equal-slice rule can actually buy."""
    rows = []
    n = len(prices)
    target_w = 1.0 / n
    for cap in rungs:
        lots, notional, fees = allocate(prices, cap)
        filled = sum(1 for v in lots.values() if v > 0)
        weights = {s: (lots[s] * prices[s] * LOT) / cap for s in prices}
        cash = cap - notional - fees
        rows.append({
            "capital": cap,
            "names_filled": filled,
            "names": n,
            "lots": {s: lots[s] for s in prices},
            "cash_pct": round(100.0 * cash / cap, 3),
            "fee_pct_of_capital": round(100.0 * fees / cap, 4),
            "max_weight_dev_pp": round(100.0 * max(abs(w - target_w)
                                                   for w in weights.values()), 3),
            "weights": {k: round(v, 4) for k, v in weights.items()},
        })
    return rows


def judge(prices, ladder_rows, crit=FEE_CRIT):
    """Frozen before the run: the smallest rung that holds all five names *and* keeps the
    fee floor under `crit` of each slice."""
    cap, kind = min_capital(prices, crit)
    ok = [r for r in ladder_rows
          if r["capital"] >= cap and r["names_filled"] == r["names"]]
    return {
        "criterion": {"fee_crit_pct_of_slice": 100.0 * crit,
                      "fee_rule": "max(5 CNY, 10bp) per ticket",
                      "lot": LOT},
        "min_capital": round(cap, 2),
        "binding_wall": kind,
        "lot_bound": round(lot_bound(prices), 2),
        "fee_floor_bound": round(fee_bound(crit), 2),
        "first_rung_that_clears_it": (ok[0]["capital"] if ok else None),
        "verdict": ("EXECUTABLE_FROM_SMALL_ACCOUNT" if cap <= 10000 else
                    "NEEDS_A_FIVE_FIGURE_ACCOUNT"),
    }


def _prices_for(picks, as_of, panel):
    """Latest close on or before the pick's own as_of -- never a later price."""
    import pandas as pd
    cut = pd.Timestamp(as_of)
    out = {}
    dates = {}
    for sym in picks:
        ser = panel.get(sym)
        if ser is None:
            continue
        s = ser["close"].dropna()
        s = s[s.index <= cut]
        if s.empty:
            continue
        out[sym] = float(s.iloc[-1])
        dates[sym] = str(s.index[-1].date())
    return out, dates


def _load_panel():
    import etf_composite_pf as E
    return E._dedupe(E._load_prices())


def _read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def _pick_list(face):
    lp = face.get("live_picks") or {}
    out = []
    for p in lp.get("picks") or []:
        out.append(p.get("symbol") if isinstance(p, dict) else p)
    return [s for s in out if s], lp.get("as_of") or face.get("evidence_cutoff")


def build(panel=None):
    panel = _load_panel() if panel is None else panel
    books = []
    for name, path in BOOKS:
        face = _read(path)
        picks, as_of = _pick_list(face)
        prices, price_dates = _prices_for(picks, as_of, panel)
        rows = ladder(prices)
        j = judge(prices, rows)
        books.append({
            "book": name,
            "face": path,
            "picks_as_of": as_of,
            "picks": [{"symbol": s, "close": round(prices[s], 4),
                       "close_date": price_dates[s],
                       "one_lot_cny": round(prices[s] * LOT, 2)}
                      for s in prices],
            "missing_from_panel": [s for s in picks if s not in prices],
            "min_capital": j,
            "ladder": rows,
        })
    cheap = min(books, key=lambda b: b["min_capital"]["min_capital"])
    pricey = max(books, key=lambda b: b["min_capital"]["min_capital"])
    face = {
        "evidence_cutoff": max(b["picks_as_of"] for b in books),
        "books": books,
        "readout": {
            "cheapest_book": cheap["book"],
            "cheapest_min_capital": cheap["min_capital"]["min_capital"],
            "priciest_book": pricey["book"],
            "priciest_min_capital": pricey["min_capital"]["min_capital"],
            "ratio": round(pricey["min_capital"]["min_capital"]
                           / max(cheap["min_capital"]["min_capital"], 1.0), 2),
            "same_rule": "one lot of each of the five names, fee floor 5 CNY per ticket",
            "why": ("卡人的是标的自家的面值：面值 100 元的债/货币 ETF 一手就 1.0-1.14 万元，"
                    "五只要 5.7 万；权益类 ETF 一手只要 60-170 元，于是它卡的不是整手而是"
                    "券商 5 元票底——同一条规则，两本书的可执行门槛差 5.7 倍"),
            "not_a_recommendation": ("this face prices representability, not edge: a book you "
                                     "can hold is not a book that will make money"),
        },
    }
    return face


def write(face):
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(render(face))
    print("saved", OUT_JSON)
    print("saved", OUT_MD)


def render(face):
    L = []
    L.append("# ETF 书：按书种拆开的最小可执行资本\n")
    L.append("> evidence_cutoff=%s；规则=五只各买一手（100 份），券商佣金 max(5 元, 10bp)/票；"
             "判据=每票佣金不超过其自身切片（资本/5）的 25bp。\n"
             % face["evidence_cutoff"])
    L.append("## 这一面回答什么\n")
    L.append("`research/ETF_BOOK_LOT_LADDER.md` 把**带债书**压到 2 万档，发现它被整手卡住："
             "511160/511360/511220 这类面值 100 元、价格 102-114 元的债/货币 ETF，一手就是 1.0-1.1 万，"
             "五只要 5.7 万才「能表示成这本书」。生产候选是**去债书**（`nobond_vt08`），"
             "它选的票一手只要 60-170 元——同一个问题，答案差 5.7 倍，而此前没人量过。\n")
    L.append("两道墙必须分开看：\n")
    L.append("- **整手墙**＝`5 × max(价×100)`：由标的自身价格决定，带债书撞的是这道。")
    L.append("- **票底墙**＝`5 元 ÷ 切片`：由券商最低佣金决定，去债书撞的是这道（一手才 118 元，"
             "5 元佣金就是 4.2%）。\n")
    L.append("## 读数\n")
    L.append("| 书 | 票面日 | 最小资本 | 卡在哪道墙 | 整手墙 | 票底墙(25bp) | 判词 |")
    L.append("|---|---|---:|---|---:|---:|---|")
    for b in face["books"]:
        m = b["min_capital"]
        L.append("| %s | %s | %s 元 | %s | %s 元 | %s 元 | %s |"
                 % (b["book"], b["picks_as_of"], fmt(m["min_capital"]), m["binding_wall"],
                    fmt(m["lot_bound"]), fmt(m["fee_floor_bound"]), m["verdict"]))
    r = face["readout"]
    L.append("")
    L.append("**两张票面差 %s 倍。** %s。\n" % (r["ratio"], r["why"]))
    for b in face["books"]:
        L.append("### %s（票面日 %s）\n" % (b["book"], b["picks_as_of"]))
        L.append("| 标的 | 收盘 | 收盘日 | 一手(元) |")
        L.append("|---|---:|---|---:|")
        for p in b["picks"]:
            L.append("| %s | %s | %s | %s |"
                     % (p["symbol"], p["close"], p["close_date"], fmt(p["one_lot_cny"])))
        L.append("")
        L.append("| 资本 | 填满只数 | 现金占比 | 佣金占资本 | 最大权重偏离 |")
        L.append("|---:|---|---:|---:|---:|")
        for row in b["ladder"]:
            L.append("| %s | %d/%d | %s%% | %s%% | %spp |"
                     % (fmt(row["capital"]), row["names_filled"], row["names"],
                        row["cash_pct"], row["fee_pct_of_capital"], row["max_weight_dev_pp"]))
        L.append("")
    L.append("## 这张面没有回答的\n")
    L.append("- **能持有不等于能赚**：本面只量代表性（一手/佣金），不含收益、回撤、容量。")
    L.append("- 带债书的票面日是 %s、去债书是 %s：两本书不在同一天比，"
             "因为两本都只公布了自己最近一次的选票；价格各按自己的票面日取。"
             % (face["books"][1]["picks_as_of"], face["books"][0]["picks_as_of"]))
    L.append("- 券商佣金可以谈到万分之一并免 5 元底，那时去债书的票底墙消失，最小资本退化成"
             "整手墙（几百元）；本面用最常见的一档。")
    L.append("- 整手墙按「五只各一手」算，不考虑同一只 ETF 的其它份额类别更便宜。\n")
    L.append("## 复算\n")
    L.append("```")
    L.append("python scripts/etf_book_min_capital_by_class.py run       # 重出件（读面板 ~25s）")
    L.append("python scripts/etf_book_min_capital_by_class.py check     # 从已发布面重算算术")
    L.append("python scripts/etf_book_min_capital_by_class.py selftest  # 离线不变量")
    L.append("```")
    return "\n".join(L) + "\n"


def fmt(v):
    return format(float(v), ",.0f") if float(v) >= 1000 else format(float(v), ".2f")


def selftest():
    legs = []

    def chk(name, cond):
        legs.append((name, bool(cond)))

    chk("ticket floor: a 100 CNY ticket pays the 5 CNY floor",
        abs(ticket_cost(100.0) - 5.0) < 1e-9)
    chk("ticket floor: a 10,000 CNY ticket pays 10 bp (above the floor)",
        abs(ticket_cost(10000.0) - 10.0) < 1e-9)
    chk("no ticket, no fee", ticket_cost(0.0) == 0.0)

    cheap = {s: 1.0 for s in ("a", "b", "c", "d", "e")}
    cap, kind = min_capital(cheap)
    chk("cheap picks are fee-floor bound", kind == "FEE_FLOOR_BOUND")
    chk("fee-floor bound = 5 * 5 / 0.0025 = 10,000",
        abs(cap - 10000.0) < 1e-9)

    pricey = {s: 114.0 for s in ("a", "b", "c", "d", "e")}
    cap2, kind2 = min_capital(pricey)
    chk("par-100 picks are lot bound", kind2 == "LOT_BOUND")
    chk("lot bound = 5 * 11,400 = 57,000", abs(cap2 - 57000.0) < 1e-9)

    rows = ladder(cheap)
    chk("a rung never spends fees it does not have (no negative cash)",
        all(r["cash_pct"] >= 0.0 for r in rows))
    chk("the floor dominates at small capital (2,500 CNY pays >=0.5% in commission)",
        rows[0]["fee_pct_of_capital"] >= 0.5)
    chk("the proportional 10bp commission dominates at 1,000,000 CNY",
        0.09 <= rows[-1]["fee_pct_of_capital"] <= 0.11)
    chk("floor-driven fee share never rises while the floor still binds",
        all(rows[i]["fee_pct_of_capital"] >= rows[i + 1]["fee_pct_of_capital"]
            for i in range(len(rows) - 1)
            if rows[i]["fee_pct_of_capital"] > 0.11))
    chk("at 2,500 CNY a 1.00 CNY lot is affordable five times",
        rows[0]["names_filled"] == 5)
    j = judge(cheap, rows)
    chk("judge names the first rung that clears the criterion",
        j["first_rung_that_clears_it"] is not None
        and j["first_rung_that_clears_it"] >= j["min_capital"])

    tiny = {s: 0.6 for s in ("a", "b", "c", "d", "e")}
    cap3, kind3 = min_capital(tiny)
    chk("a 60 CNY lot does not move the wall (fee floor still binds)",
        kind3 == "FEE_FLOOR_BOUND" and abs(cap3 - 10000.0) < 1e-9)

    ok = sum(1 for _n, c in legs if c)
    for n, c in legs:
        print(("PASS  " if c else "FAIL  ") + n)
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def check():
    """Re-derive every printed number from the published face.  Never rebuild the panel.

    A face that lost a book, whose min_capital does not equal max(lot, fee) of its own
    printed prices, or whose verdict contradicts that number, is refused."""
    if not os.path.exists(OUT_JSON):
        print("check FAIL: no face at", OUT_JSON)
        return 1
    face = _read("results/etf_book_min_capital_by_class.json")
    probs = []
    for b in face.get("books") or []:
        prices = {p["symbol"]: float(p["close"]) for p in b.get("picks") or []}
        if not prices:
            probs.append("%s: no priced picks" % b.get("book"))
            continue
        m = b["min_capital"]
        if abs(m["lot_bound"] - lot_bound(prices)) > 0.02:
            probs.append("%s: lot_bound %.2f != 5*max lot %.2f"
                         % (b["book"], m["lot_bound"], lot_bound(prices)))
        want = max(m["lot_bound"], m["fee_floor_bound"])
        if abs(m["min_capital"] - want) > 0.02:
            probs.append("%s: min_capital %.2f != max(lot, fee) %.2f"
                         % (b["book"], m["min_capital"], want))
        want_kind = "LOT_BOUND" if m["lot_bound"] >= m["fee_floor_bound"] else "FEE_FLOOR_BOUND"
        if m["binding_wall"] != want_kind:
            probs.append("%s: binding_wall %r should be %r"
                         % (b["book"], m["binding_wall"], want_kind))
        want_verdict = ("EXECUTABLE_FROM_SMALL_ACCOUNT" if m["min_capital"] <= 10000
                        else "NEEDS_A_FIVE_FIGURE_ACCOUNT")
        if m["verdict"] != want_verdict:
            probs.append("%s: verdict %r should be %r"
                         % (b["book"], m["verdict"], want_verdict))
        for row in b.get("ladder") or []:
            filled = sum(1 for v in row["weights"].values() if v > 0)
            if filled != row["names_filled"]:
                probs.append("%s: rung %s says %d filled but %d weights are non-zero"
                             % (b["book"], row["capital"], row["names_filled"], filled))
            if row["cash_pct"] < -1e-6:
                probs.append("%s: rung %s spends more than its capital"
                             % (b["book"], row["capital"]))
    books = {b.get("book") for b in face.get("books") or []}
    for name, _p in BOOKS:
        if name not in books:
            probs.append("book %r missing from the face" % name)
    if probs:
        print("check FAIL:")
        for x in probs:
            print("  -", x)
        return 1
    cheap = min(face["books"], key=lambda b: b["min_capital"]["min_capital"])
    print("check ok: %d books, cheapest %s at %.0f CNY, ratio %.2fx"
          % (len(face["books"]), cheap["book"], cheap["min_capital"]["min_capital"],
             (face.get("readout") or {}).get("ratio") or 0.0))
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    cmd = (argv[0] if argv else "run").lstrip("-").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd in ("run", ""):
        face = build()
        write(face)
        for b in face["books"]:
            m = b["min_capital"]
            print("%-22s as_of=%s min=%.0f CNY (%s) lot=%.0f fee=%.0f"
                  % (b["book"], b["picks_as_of"], m["min_capital"], m["binding_wall"],
                     m["lot_bound"], m["fee_floor_bound"]))
        r = face["readout"]
        print("cheapest %s at %.0f vs %s at %.0f -> %.2fx"
              % (r["cheapest_book"], r["cheapest_min_capital"],
                 r["priciest_book"], r["priciest_min_capital"], r["ratio"]))
        return 0
    print("usage: run | check | selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
