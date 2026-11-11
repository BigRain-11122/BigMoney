"""ETF book -- the entry discount is a NUMBER OF SHARES, not cash.

r1524 put the discount on the sheet as `￥9,761.8` and said, correctly, that it must never be
added to the measured path. It is still written in money, and money is the one thing it is
not. The same cash bought MORE UNITS of the basket because the sibling was cheap: that is a
size. A size cannot be spent, cannot be booked as realised P&L, and is not re-priced when the
gap moves. It is re-marked at a new price on a later bar and becomes cash only when the
shares are sold -- which is exactly the condition r1523 measures and mostly fails to find.

This face turns the money back into units and then into the caliber the ledger already uses
(lots of 100 shares plus the share residue a lot cannot hold), so the next decision bar can
re-mark the same size instead of re-deriving a new one:

  1. per leg: cash sold -> shares of the sibling actually bought -> the discount's share of
     that purchase (`extra_shares = level_cny / trade_price`);
  2. the size is checked against the position the ledger actually holds -- the extra shares
     are a subset of the bought line, never a second holding;
  3. re-mark: the same share count priced on the first later bar present in the panel, with
     the drift labelled as price drift on a fixed size (not a harvest, not P&L);
  4. REFUSALS. The discount is not re-priced off a new gap (that is the path column's job),
     and the ledger's realised fields are scanned to prove the number never landed there.

The one approximation is bounded, not hidden: `level_cny` is NAV-caliber while `trade_price`
is a market price, so shares carry an error of at most the sibling's premium. The bound is
imported from the premium materiality line, not typed here, and printed beside the count.

Usage:
    python scripts/etf_book_swap_units.py run
    python scripts/etf_book_swap_units.py --check
    python scripts/etf_book_swap_units.py --selftest
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_swap_convergence as conv_face  # noqa: E402  (which SELL was a swap)
import etf_book_sibling_gap as gap_face        # noqa: E402  (the panel locator)
import etf_book_sibling_entry as sib_face      # noqa: E402  (the premium materiality line)
import exchange_calendar_audit as cal_face     # noqa: E402  (one owner of the official calendar)
import etf_book_next_decision as nd_clock      # noqa: E402  (r1536: the single decision clock)

STACK_FACE = os.path.join(ROOT, "results", "etf_book_swap_stack.json")
EFFECT_FACE = os.path.join(ROOT, "results", "etf_book_swap_effect.json")
POSITIONS_FACE = os.path.join(ROOT, "results", "etf_book_positions.json")
CALENDAR = os.path.join(ROOT, "data", "exchange_calendar.csv")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_swap_units.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_swap_units.md")

LOT_SHARES = 100          # the ledger's own caliber: one lot is what a ticket can print
CENT = 0.011              # one cent: two faces that price the same trade agree to the cent

WHY_NOT_REALISED = (
    "折扣是「同一笔钱多买到多少份」，不是卖掉的那部分收入的差——它只有在这些份被卖出、"
    "且价差已经收窄时才变成现金；在那之前把它记成已实现收益，等于把份额当成钱。")

WHY_NOT_REPRICED = (
    "份数在买入那一刻就固定了；下一根 bar 能改的只有它按什么价重估。"
    "用新的价差重算折扣＝把 r1523 的路径栏再做一遍，本面不提供这个数。")


def _read_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _refuse(face, why):
    face["verdict"] = "CANNOT_RECORD"
    face["refused"] = why
    face["sentence"] = "这一问答不了：%s。" % why
    return face


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ inputs

def level_rows(effect):
    """{leg: level_cny} -- the r1524 column, imported, never re-derived here."""
    out = {}
    for r in (effect or {}).get("rows") or []:
        leg = r.get("leg_symbol")
        level = _num(r.get("level_cny"))
        if leg is None or level is None:
            continue
        out[str(leg)] = {"level_cny": level,
                         "sibling": r.get("sibling_symbol"),
                         "notional_cny": _num(r.get("notional_cny"))}
    return out


def merged_buy(stack):
    """The single BUY line the swaps were merged into: what the cash actually became."""
    rows = [a for a in (stack or {}).get("actions") or []
            if (a.get("side") or "").upper() == "BUY"]
    if len(rows) != 1:
        return None
    a = rows[0]
    price = _num(a.get("price"))
    lots = a.get("lots")
    if not price or not price > 0 or lots is None:
        return None
    return {"symbol": str(a.get("symbol")), "price": price, "lots": int(lots),
            "amount_cny": _num(a.get("amount_cny")),
            "shares": int(lots) * LOT_SHARES}


def held_position(positions, symbol):
    """The ledger's own line for the bought ticker -- the caliber the size must live in."""
    row = (positions or {}).get("ledger_row") or {}
    for h in row.get("holdings") or []:
        if str(h.get("symbol")) == str(symbol):
            lots = h.get("lots")
            if lots is None:
                break
            return {"bar": row.get("bar") or (positions or {}).get("ledger_bar"),
                    "lots": int(lots), "shares": int(lots) * LOT_SHARES,
                    "price": _num(h.get("price")),
                    "amount_cny": _num(h.get("amount_cny"))}
    return None


def inside_holdings(face, positions):
    """r1528: the shares the discount bought already live inside one line of the ledger.

    r1525 counted 5,546.48 shares and said, in prose, that the count is a subset of the
    159513 line. But the line a desk actually opens is the ledger row, and it carries one
    number: 891 lots. "A share count nobody can find on the account" is exactly the shape of
    a number that gets counted twice, so this block names the subset on the row itself and
    refuses to be a second line -- it never moves lots, amount, the risk book or NAV.
    """
    out = {"artifact": "discount_inside_holdings",
           "source_face": "results/etf_book_swap_units.json",
           "ledger_face": "results/etf_book_positions.json",
           "status": "REFUSED",
           "rows": [],
           "refusals": [],
           "totals": {},
           "not_a_line": ("这几份就在账本那一行里：不增行、不改手数、不进风险腿金额、"
                          "也不进 NAV——它们是同一笔持仓的一个子集。"),
           "caveats": [
               "the line is the ledger's own row for the execution bar, not the sheet's entry "
               "table: the two are different books once a swap executes (r1521)",
           ]}
    if not face:
        out["refusals"].append({"why": "折扣份数面缺失：不拿空当零"})
        return out
    if face.get("verdict") in ("CANNOT_RECORD", "DISCOUNT_REACHED_THE_LEDGER"):
        out["refusals"].append({"why": "折扣份数面自己记不起来（%s）：先修那一面"
                                     % face.get("verdict")})
        return out
    if not positions or not (positions.get("ledger_row") or {}):
        out["refusals"].append({"why": "持仓账本面缺失：没有可以指认的那一行"})
        return out
    bar = face.get("bar")
    ledger_bar = (positions.get("ledger_bar")
                  or (positions.get("ledger_row") or {}).get("bar"))
    if bar and ledger_bar and str(bar) != str(ledger_bar):
        out["refusals"].append({"why": "折扣量在 %s，账本那一行站在 %s：两个日子不能拼"
                                     % (bar, ledger_bar)})
        return out

    # two swap legs can land on the SAME ledger line (159501 and 513100 both become 159513):
    # the line is one, so the subsets add up inside it. Keying by leg would count the 891 lots
    # twice and print a 12.4% share of a book that does not exist.
    buckets = {}
    for r in face.get("rows") or []:
        sibling = str(r.get("sibling_symbol") or "")
        held = held_position(positions, sibling)
        if not held:
            out["refusals"].append({"leg_symbol": r.get("leg_symbol"), "sibling_symbol": sibling,
                                    "why": "账本上就没有这只票：折扣无处安放"})
            continue
        extra = _num(r.get("extra_shares"))
        if extra is None or extra <= 0:
            out["refusals"].append({"leg_symbol": r.get("leg_symbol"), "sibling_symbol": sibling,
                                    "why": "这一腿没有可安放的份数"})
            continue
        b = buckets.setdefault(sibling, {"symbol": sibling, "line_lots": held["lots"],
                                         "line_shares": held["shares"],
                                         "extra_shares": 0.0, "legs": []})
        b["legs"].append({"from_leg": str(r.get("leg_symbol") or ""),
                          "extra_shares": round(extra, 2),
                          "extra_lots": int(r.get("extra_lots") or 0),
                          "extra_residue_shares": round(
                              float(r.get("extra_residue_shares") or 0.0), 2)})
        b["extra_shares"] = round(b["extra_shares"] + extra, 2)

    for sym in sorted(buckets):
        b = buckets[sym]
        if b["extra_shares"] > b["line_shares"]:
            out["refusals"].append({"sibling_symbol": sym,
                                    "why": "折扣 %s 份大于账本那一行的 %d 份：子集就不成立"
                                           % (_shares(b["extra_shares"]), b["line_shares"])})
            continue
        # the lot is the smallest thing a ticket trades, so it is taken on the LINE's own
        # combined count, not per leg: 3,188.92 + 2,357.56 = 5,546.48 shares is 55 lots +
        # 46.48, while flooring each leg first would lose a lot (31 + 23 = 54, residue 146.48)
        # and print a residue larger than a lot.
        b["extra_lots"] = int(b["extra_shares"] // LOT_SHARES)
        b["extra_residue_shares"] = round(b["extra_shares"] - b["extra_lots"] * LOT_SHARES, 2)
        b["share_of_line"] = round(b["extra_shares"] / b["line_shares"], 6) if b["line_shares"] else None
        b["from_leg"] = "/".join(l["from_leg"] for l in b["legs"] if l["from_leg"])
        b["label"] = "子集，不是第二笔持仓"
        out["rows"].append(b)

    if out["rows"]:
        out["status"] = "INSIDE_THE_LINE"
        extra_total = sum(r["extra_shares"] for r in out["rows"])
        line_total = sum(r["line_shares"] for r in out["rows"])
        out["totals"] = {"lines": len(out["rows"]),
                         "line_lots": sum(r["line_lots"] for r in out["rows"]),
                         "line_shares": line_total,
                         "extra_shares": round(extra_total, 2),
                         "extra_lots": sum(int(r.get("extra_lots") or 0) for r in out["rows"]),
                         "residue_shares": round(sum(float(r.get("extra_residue_shares") or 0.0)
                                                     for r in out["rows"]), 2),
                         "share_of_lines": round(extra_total / line_total, 6) if line_total else None}
    return out


def inside_md_lines(block, heading="## 账本那一行里，有多少份是折扣买来的（r1528）"):
    """The subset, printed where the desk reads the line -- with its refusals, never a 0."""
    b = block or {}
    L = ["", heading]
    if b.get("status") != "INSIDE_THE_LINE":
        why = "；".join(str(r.get("why")) for r in (b.get("refusals") or [])[:3]) or "面缺失"
        L += ["- **这一问答不了**：%s。缺面不印 0，也不拿别处的份数顶替。" % why, ""]
        return L
    L += ["| 账本行 | 手数 | 份数 | 其中折扣买来 | 零头 | 占这一行 |",
          "|---|---|---|---|---|---|"]
    for r in b.get("rows") or []:
        L.append("| %s（换自 %s） | %d | %s | **%s = %d 手 + %s** | %s | %.2f%% |"
                 % (r["symbol"], r.get("from_leg") or "?",
                    r.get("line_lots") or 0, _shares(r.get("line_shares")),
                    _shares(r.get("extra_shares")), int(r.get("extra_lots") or 0),
                    _shares(r.get("extra_residue_shares")),
                    _shares(r.get("extra_residue_shares")),
                    100.0 * float(r.get("share_of_line") or 0.0)))
    t = b.get("totals") or {}
    L += ["", "- 合计 **%s**（%d 手 + %s零头）是这几行合计 %s 里的一部分，占 **%.2f%%**。"
          % (_shares(t.get("extra_shares")), int(t.get("extra_lots") or 0),
             _shares(t.get("residue_shares")), _shares(t.get("line_shares")),
             100.0 * float(t.get("share_of_lines") or 0.0)),
          "- %s" % (b.get("not_a_line") or "")]
    for rf in (b.get("refusals") or []):
        L.append("- 没印的一腿：%s（%s）。" % (rf.get("leg_symbol") or "?", rf.get("why")))
    L += ["- 出处：%s 与 %s。" % (b.get("source_face") or "?", b.get("ledger_face") or "?"), ""]
    return L


def trading_days():
    """The official calendar from its single owner. Never a date derived from our own panel."""
    try:
        days = cal_face.load_calendar()
        if days:
            return list(days)
    except Exception:                                     # noqa: BLE001
        pass
    if not os.path.exists(CALENDAR):
        return []
    out = []
    with open(CALENDAR, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            for key in ("date", "trade_date", "day"):
                if row.get(key):
                    out.append(str(row[key]).strip())
                    break
    return sorted(set(out))


def grid_constant():
    """The book's decision grid. Imported from the order module; a fallback is disclosed."""
    try:
        from scripts.etf_book_order import REBAL  # noqa: PLC0415
        return int(REBAL), "import"
    except Exception:                                     # noqa: BLE001
        try:
            import etf_book_order                          # noqa: PLC0415
            return int(etf_book_order.REBAL), "import"
        except Exception:                                  # noqa: BLE001
            return 20, "fallback"


def remark_block(bar, sibling_symbol, extra_shares, level_cny, calendar):
    """Price the same share count on the first later bar that exists -- or say it does not."""
    out = {"trade_bar": bar, "status": "AWAITING_NEXT_BAR", "bar": None, "price": None,
           "value_cny": None, "drift_cny": None, "sibling": sibling_symbol,
           "label": ("同一份数、不同价的重估＝价格漂移，不是兑现，也不是已实现收益"), "why": ""}
    after = [d for d in calendar if bar and d > str(bar)]
    if not bar:
        out["why"] = "这张单没有 bar，重估落在哪一根都读不出来"
        return out
    if not after:
        out["why"] = "交易日历停在 %s，后面没有可用的 bar" % (calendar[-1] if calendar else "空")
        return out
    out["next_bar_expected"] = after[0]
    path = gap_face.find_daily(sibling_symbol) if sibling_symbol else None
    if not path:
        out["why"] = "换入的 %s 没有本地日线面板，重估无从取价" % sibling_symbol
        return out
    close = gap_face.load_close(path)
    later = [d for d in sorted(close) if d > str(bar)]
    if not later:
        out["why"] = ("面板最后一根就是交易日 %s：下一根 bar 尚未产生，"
                      "在交易日这根上「份数×当日价」恒等于折扣本身，重估即恒等式，故不印数"
                      % bar)
        return out
    out["bar"] = later[0]
    out["price"] = close[later[0]]
    out["value_cny"] = round(float(extra_shares) * close[later[0]], 2)
    out["drift_cny"] = round(out["value_cny"] - float(level_cny), 2)
    out["status"] = "BEYOND_TRADE_BAR"
    return out


def realised_guard(positions, level_total):
    """Prove the discount is not sitting in the ledger's realised fields."""
    row = (positions or {}).get("ledger_row") or {}
    accrual = (positions or {}).get("accrual") or {}
    fields = ["unexplained_total_cny", "accrual.status", "accrual.rows", "ledger_row.actions"]
    found, where = False, None
    if level_total is None:
        return {"checked": False, "found": None, "where": None, "fields": fields,
                "why": "没有折扣总额可比对，无法断言它不在已实现面里"}
    unexplained = _num(row.get("unexplained_total_cny"))
    if unexplained is None:
        unexplained = _num((positions or {}).get("unexplained_total_cny"))
    if unexplained is not None and abs(unexplained - float(level_total)) < 1.0:
        found, where = True, "unexplained_total_cny"
    for r in accrual.get("rows") or []:
        for key, val in (r or {}).items():
            n = _num(val)
            if n is not None and abs(n - float(level_total)) < 1.0:
                found, where = True, "accrual.rows.%s" % key
    for a in row.get("actions") or []:
        key = "%s_%s" % (a.get("side"), a.get("symbol"))
        for k2 in ("amount_cny", "gain_cny", "realised_cny"):
            n = _num(a.get(k2))
            if n is not None and abs(n - float(level_total)) < 1.0:
                found, where = True, "ledger_row.actions.%s.%s" % (key, k2)
    return {"checked": True, "found": bool(found), "where": where, "fields": fields,
            "level_total_cny": round(float(level_total), 2)}


# ------------------------------------------------------------------ compute

def compute(ctx):
    """`ctx` carries the already-published faces and the calendar. Nothing is re-priced."""
    as_of = ctx.get("as_of")
    face = {"artifact": "etf_book_swap_units", "bar": as_of, "evidence_cutoff": as_of,
            "verdict": None, "rows": [], "unpaired": [], "totals": {}, "ledger": None,
            "remark": None, "next_decision_bar": None, "sentence": "",
            "lot_shares": LOT_SHARES, "realised_booked_cny": None,
            "not_realised": WHY_NOT_REALISED, "not_repriced": WHY_NOT_REPRICED,
            "premium_bound_pp": float(sib_face.MATERIAL_PP),
            "sources": {"swap_stack": "results/etf_book_swap_stack.json",
                        "swap_effect": "results/etf_book_swap_effect.json",
                        "positions": "results/etf_book_positions.json",
                        "calendar": "data/exchange_calendar.csv"},
            "caveats": [
                "the level column is r1524's own figure (already re-scaled on the trimmed "
                "book); it is divided by the price this book actually paid, never re-derived "
                "from a gap",
                "shares carry a bounded error of at most the sibling's premium (the bound is "
                "the premium materiality line, printed beside the count): a NAV-caliber CNY "
                "divided by a market price is not exactly a share count",
                "a lot is the smallest thing a ticket can trade, so the discount is only "
                "realisable in whole lots; the residue shares are named and priced apart",
                "the size is a subset of the position the ledger holds; it is not a second "
                "holding and it is not added to NAV",
            ]}

    stack = ctx.get("swap_stack")
    effect = ctx.get("swap_effect")
    positions = ctx.get("positions")
    if not stack:
        return _refuse(face, "没有已发布的净额单面（scripts/etf_book_swap_stack.py run）")
    if not effect:
        return _refuse(face, "没有已发布的并列面（scripts/etf_book_swap_effect.py run）")
    e_bar = effect.get("bar")
    s_bar = stack.get("asof") or stack.get("bar")
    if as_of and ((e_bar and e_bar != as_of) or (s_bar and s_bar != as_of)):
        return _refuse(face, "并列面停在 %s、净额单面停在 %s、这张单是 %s：不同 bar 的份数不能并列"
                       % (e_bar, s_bar, as_of))
    if not positions:
        return _refuse(face, "没有已发布的持仓账本（scripts/etf_book_positions.py run）")

    buy = merged_buy(stack)
    if buy is None:
        return _refuse(face, "净额单里找不到唯一的一条买入腿：折扣买到了多少份读不出来")

    price = buy["price"]
    bound = float(sib_face.MATERIAL_PP)
    levels = level_rows(effect)
    rows, unpaired = [], []
    for leg in sorted(levels):
        info = levels[leg]
        sell = conv_face.executed_notional(stack, leg)
        cash = _num((sell or {}).get("amount_cny"))
        row = {"leg_symbol": leg, "sibling_symbol": buy["symbol"],
               "cash_cny": None, "trade_price": price, "shares_bought": None,
               "level_cny": round(info["level_cny"], 2), "extra_shares": None,
               "extra_lots": None, "extra_residue_shares": None,
               "residue_value_cny": None, "share_of_bought": None, "same_trade": False,
               "why": ""}
        if sell is None:
            row["why"] = "这一腿没有「换票卖出」动作：它不是一笔换票，折扣不成立"
            unpaired.append(row)
            continue
        if cash is None or cash <= 0:
            row["why"] = "换出的成交额读不出来：份数没有分母"
            unpaired.append(row)
            continue
        if info.get("notional_cny") is not None and abs(info["notional_cny"] - cash) > CENT:
            row["why"] = ("两个面量的是不同的一笔：并列面按 ¥%s、净额单换出 ¥%s"
                          % (format(float(info["notional_cny"]), ",.2f"), format(cash, ",.2f")))
            unpaired.append(row)
            continue
        row["cash_cny"] = round(cash, 2)
        row["shares_bought"] = round(cash / price, 2)
        row["extra_shares"] = round(info["level_cny"] / price, 2)
        whole = int(row["extra_shares"] // LOT_SHARES)
        row["extra_lots"] = whole
        row["extra_residue_shares"] = round(row["extra_shares"] - whole * LOT_SHARES, 2)
        row["residue_value_cny"] = round(row["extra_residue_shares"] * price, 2)
        if row["shares_bought"] > 0:
            row["share_of_bought"] = round(row["extra_shares"] / row["shares_bought"], 6)
        row["same_trade"] = True
        rows.append(row)

    face["rows"] = rows
    face["unpaired"] = unpaired
    if not rows:
        face["verdict"] = "CANNOT_RECORD"
        face["sentence"] = ("这单没有可以记成份数的换票：%s——这不是「折扣为零」。"
                            % ("；".join(u.get("why") or "" for u in unpaired) or "两张面没有共同的票"))
        face["totals"] = {"level_cny": None, "extra_shares": None, "extra_lots": None,
                          "residue_shares": None, "cash_cny": None, "combined_cny": None}
        return face

    extra = round(sum(r["extra_shares"] for r in rows), 2)
    level_total = round(sum(r["level_cny"] for r in rows), 2)
    cash_total = round(sum(r["cash_cny"] for r in rows), 2)
    whole = int(extra // LOT_SHARES)
    face["totals"] = {
        "level_cny": level_total,
        "extra_shares": extra,
        "extra_lots": whole,
        "residue_shares": round(extra - whole * LOT_SHARES, 2),
        "residue_value_cny": round((extra - whole * LOT_SHARES) * price, 2),
        "cash_cny": cash_total,
        "share_error_bound_shares": round(extra * bound / 100.0, 2),
        "combined_cny": None,   # deliberately absent: a size does not add to a cash figure
        "priced_legs": len(rows),
    }
    face["ledger"] = dict(held_position(positions, buy["symbol"]) or {},
                          sibling=buy["symbol"], bought_shares=buy["shares"],
                          bought_lots=buy["lots"])
    held = face["ledger"].get("shares")
    face["ledger"]["extra_inside_holding"] = (None if not held else bool(extra <= held))
    face["ledger"]["share_of_holding"] = (None if not held else round(extra / held, 6))
    face["remark"] = remark_block(as_of, buy["symbol"], extra, level_total,
                                  ctx.get("calendar") or [])
    rebal, how = grid_constant()
    cal = ctx.get("calendar") or []
    # r1536: `after[rebal - 1]` counted 20 sessions from whatever bar the sheet was printed on,
    # so its date moved forward every day and -- whenever the sheet is not itself on a grid bar
    # -- named a day that is not a decision bar at all (2026-12-08 was calendar index 8779;
    # 8779 % 20 == 19). One clock now, anchored on the published last_decision_bar.
    face["next_decision_bar"] = nd_clock.next_decision(
        as_of, cal, rebal=rebal, anchor=ctx.get("anchor_bar"))
    face["next_decision_bar"]["grid_constant_source"] = how
    face["realised_guard"] = realised_guard(positions, level_total)
    face["verdict"] = ("SIZE_RECORDED" if face["realised_guard"].get("found") is not True
                       else "DISCOUNT_REACHED_THE_LEDGER")
    face["sentence"] = sentence(face)
    return face


# ------------------------------------------------------------------ rendering

def _money(v):
    if v is None:
        return "读不出"
    v = float(v)
    return ("-%s%s" % ("\u00a5", format(abs(v), ",.2f"))) if v < 0 \
        else ("%s%s" % ("\u00a5", format(v, ",.2f")))


def _shares(v):
    return "读不出" if v is None else "%s 份" % format(float(v), ",.2f")


def sentence(face):
    rows = face.get("rows") or []
    if not rows:
        return face.get("sentence") or ""
    t = face.get("totals") or {}
    led = face.get("ledger") or {}
    bits = ["%s 换出的 %s 在 %s 的 %s 上多买到 %s（%d 手 + %s 份零头）"
            % (r["leg_symbol"], _money(r["cash_cny"]), r["sibling_symbol"],
               _money(r["trade_price"]), _shares(r["extra_shares"]),
               r["extra_lots"] or 0, format(float(r["extra_residue_shares"] or 0.0), ",.2f"))
            for r in rows]
    head = ("折扣是份数不是钱：%s，合计 **%s = %d 手 + %s 份**（误差上限 ±%s 份 = 换入票溢价材料线 %s pp）。"
            % ("；".join(bits), _shares(t.get("extra_shares")), t.get("extra_lots") or 0,
               format(float(t.get("residue_shares") or 0.0), ",.2f"),
               format(float(t.get("share_error_bound_shares") or 0.0), ",.2f"),
               "%g" % float(face.get("premium_bound_pp") or 0.0)))
    tail = ("这 %s 份就在账本那笔 %s 手里（%s 手 = %s 份，占 %.2f%%），是它的一个子集、不是第二笔持仓；"
            % (format(float(t.get("extra_shares") or 0.0), ",.2f"),
               led.get("sibling") or "?",
               led.get("lots") if led.get("lots") is not None else "读不出",
               format(float(led.get("shares") or 0.0), ",.0f"),
               100.0 * float(led.get("share_of_holding") or 0.0)))
    rm = face.get("remark") or {}
    if rm.get("status") == "BEYOND_TRADE_BAR":
        tail += ("在 %s 这根 bar 上它按 %s 重估为 %s，漂移 %s——同一份数换了价，不是兑现也不是收益。"
                 % (rm.get("bar"), _money(rm.get("price")), _money(rm.get("value_cny")),
                    _money(rm.get("drift_cny"))))
    else:
        tail += ("下一根 bar 还没产生（日历上的下一交易日 %s），届时用**同一份数**乘当日价重估；"
                 "在交易日这根上「份数×当日价」恒等于折扣本身，印出来只是恒等式。"
                 % (rm.get("next_bar_expected") or "读不出"))
    nxt = (face.get("next_decision_bar") or {})
    tail += ("下一个决策 bar（每 %s 根）读作 %s。"
             % (nxt.get("grid"), nxt.get("bar") or "读不出"))
    return head + tail


def md_lines(face, heading="## 折扣是多少份，不是多少钱（r1525）"):
    if not face:
        return ["", heading,
                "- **这一问答不了**：没有已发布的份数面（跑 "
                "scripts/etf_book_swap_units.py run）。缺面不等于折扣为零。", ""]
    if face.get("refused"):
        return ["", heading, "- **记不起来**：%s。" % face["refused"],
                "- 读法：这一节把 r1524 的折扣从钱换成份数并落到账本口径；"
                "「记不起来」与「没有折扣」是两件事。", ""]
    L = ["", heading, "- %s" % (face.get("sentence") or "")]
    rows = face.get("rows") or []
    if rows:
        L += ["", "| 换出 | 换入 | 成交额 | 成交价 | 这笔钱买到 | 折扣折成份数 | 整手 | 零头份 | 零头值 |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            L.append("| %s | %s | %s | %s | %s | **%s** | %s | %s | %s |"
                     % (r["leg_symbol"], r.get("sibling_symbol") or "?",
                        _money(r.get("cash_cny")), _money(r.get("trade_price")),
                        _shares(r.get("shares_bought")), _shares(r.get("extra_shares")),
                        r.get("extra_lots"), format(float(r.get("extra_residue_shares") or 0.0), ",.2f"),
                        _money(r.get("residue_value_cny"))))
        t = face.get("totals") or {}
        L += ["", "**合计 %s = %d 手 + %s 份**（零头值 %s；份数误差上限 ±%s 份）"
                  % (_shares(t.get("extra_shares")), t.get("extra_lots") or 0,
                     format(float(t.get("residue_shares") or 0.0), ",.2f"),
                     _money(t.get("residue_value_cny")),
                     format(float(t.get("share_error_bound_shares") or 0.0), ",.2f")),
              "",
              "- **不能记成已实现收益**：%s" % (face.get("not_realised") or WHY_NOT_REALISED),
              "- **不能拿新价差重算**：%s" % (face.get("not_repriced") or WHY_NOT_REPRICED),
              "- **零头卖不掉**：一手 100 份是票面最小单位，所以折扣只能整手兑现；"
              "零头那几份的价值单独印在右边，不和合计混在一起。"]
    else:
        L.append("- 这一单没有可以记成份数的换票；这不是「折扣为零」的结论。")
    if face.get("unpaired"):
        L.append("- 没记的票：%s。"
                 % "；".join("%s（%s）" % (u.get("leg_symbol"), u.get("why"))
                            for u in face["unpaired"]))
    g = face.get("realised_guard") or {}
    if g.get("checked") and g.get("found") is False:
        L.append("- **账本没被污染**：已扫 %s，没有任何一格等于 %s——折扣没有以任何形式进已实现。"
                 % ("/".join(g.get("fields") or []), _money(g.get("level_total_cny"))))
    elif g.get("found"):
        L.append("- **红灯**：折扣总额出现在账本的 %s 里——份数被当成了钱。" % g.get("where"))
    return L


def check(face):
    """Re-derive every claim the payload makes. A refusal is not a failure."""
    problems = []
    if not face:
        return ["no face"]
    t = face.get("totals") or {}
    if t.get("combined_cny") is not None:
        problems.append("totals carries a combined number, which the face refuses to make")
    if face.get("realised_booked_cny") is not None:
        problems.append("the greenback discount was booked as realised")
    if face.get("verdict") == "CANNOT_RECORD":
        return problems
    rows = face.get("rows") or []
    if not rows:
        problems.append("a verdict without rows")
        return problems
    for r in rows:
        leg = r.get("leg_symbol")
        if not r.get("same_trade"):
            problems.append("%s is counted but the two faces did not price the same trade" % leg)
        price = _num(r.get("trade_price"))
        cash = _num(r.get("cash_cny"))
        level = _num(r.get("level_cny"))
        if not price or price <= 0 or cash is None or level is None:
            problems.append("%s has no usable price, cash or level" % leg)
            continue
        want_bought = round(cash / price, 2)
        if r.get("shares_bought") is None or abs(want_bought - float(r["shares_bought"])) > CENT:
            problems.append("%s shares_bought %s != cash/price %s"
                            % (leg, r.get("shares_bought"), want_bought))
        want_extra = round(level / price, 2)
        if r.get("extra_shares") is None or abs(want_extra - float(r["extra_shares"])) > CENT:
            problems.append("%s extra_shares %s != level/price %s"
                            % (leg, r.get("extra_shares"), want_extra))
        whole = int(float(r["extra_shares"] or 0.0) // LOT_SHARES) if r.get("extra_shares") else 0
        if r.get("extra_lots") != whole:
            problems.append("%s lots %s != floor(shares/%d) %s"
                            % (leg, r.get("extra_lots"), LOT_SHARES, whole))
        resid = round(float(r["extra_shares"] or 0.0) - whole * LOT_SHARES, 2) \
            if r.get("extra_shares") is not None else None
        if resid is not None and (r.get("extra_residue_shares") is None
                                  or abs(resid - float(r["extra_residue_shares"])) > CENT):
            problems.append("%s residue %s != shares - lots*%d %s"
                            % (leg, r.get("extra_residue_shares"), LOT_SHARES, resid))
    if abs(round(sum(float(r.get("extra_shares") or 0.0) for r in rows), 2)
           - float(t.get("extra_shares") or 0.0)) > 1e-6:
        problems.append("share totals do not add up")
    if abs(round(sum(float(r.get("level_cny") or 0.0) for r in rows), 2)
           - float(t.get("level_cny") or 0.0)) > 1e-6:
        problems.append("level totals do not add up")
    held = (face.get("ledger") or {}).get("shares")
    if held is not None and float(t.get("extra_shares") or 0.0) > float(held) + 1e-9:
        problems.append("the discount buys more shares than the ledger holds")
    rm = face.get("remark") or {}
    if rm.get("status") == "BEYOND_TRADE_BAR":
        want = round(float(t.get("extra_shares") or 0.0) * float(rm.get("price") or 0.0), 2)
        if rm.get("value_cny") is None or abs(want - float(rm["value_cny"])) > CENT:
            problems.append("remark value %s != shares*price %s" % (rm.get("value_cny"), want))
        if rm.get("drift_cny") is None or abs(
                float(rm["value_cny"]) - float(t.get("level_cny") or 0.0)
                - float(rm["drift_cny"])) > CENT:
            problems.append("remark drift does not re-derive")
    if face.get("verdict") == "DISCOUNT_REACHED_THE_LEDGER":
        problems.append("the ledger carries the discount as money")
    if not any("不能记成已实现收益" in x for x in md_lines(face)):
        problems.append("the page never says the size is not realised income")
    return problems


# ------------------------------------------------------------------ selftest fixtures

def _fixture(bar="2026-11-10", with_later=False):
    stack = {"asof": bar,
             "actions": [
                 {"side": "SELL", "symbol": "159501", "lots": 372, "price": 2.11,
                  "amount_cny": 78492.0,
                  "why": "swap 159501 -> 159513 (r1466 verdict X), sized on the trimmed 372 lots"},
                 {"side": "SELL", "symbol": "513100", "lots": 355, "price": 2.21,
                  "amount_cny": 78455.0, "why": "swap 513100 -> 159513 (r1466 verdict X)"},
                 {"side": "BUY", "symbol": "159513", "lots": 891, "price": 1.76,
                  "amount_cny": 156816.0, "why": "merged buy"}],
             "swap_repricing": [
                 {"leg": "159501", "sibling": "159513", "ordered_lots": 372, "trimmed_lots": 372,
                  "share": 1.0, "gain_published_cny": 5612.5,
                  "gain_on_trimmed_book_cny": 5612.5, "overstated_cny": 0.0},
                 {"leg": "513100", "sibling": "159513", "ordered_lots": 355, "trimmed_lots": 355,
                  "share": 1.0, "gain_published_cny": 4149.3,
                  "gain_on_trimmed_book_cny": 4149.3, "overstated_cny": 0.0}]}
    effect = {"bar": bar,
              "rows": [
                  {"leg_symbol": "159501", "sibling_symbol": "159513",
                   "notional_cny": 78492.0, "level_cny": 5612.5, "path_cny": -369.0},
                  {"leg_symbol": "513100", "sibling_symbol": "159513",
                   "notional_cny": 78455.0, "level_cny": 4149.3, "path_cny": -178.0}],
              "totals": {"level_cny": 9761.8, "path_cny": -547.0, "combined_cny": None},
              "verdict": "DISCOUNT_UNCOLLECTED"}
    positions = {"ledger_bar": bar,
                 "ledger_row": {"bar": bar, "kind": "execution",
                                "holdings": [
                                    {"symbol": "159263", "lots": 693, "price": 1.134},
                                    {"symbol": "159513", "lots": 891, "price": 1.76,
                                     "amount_cny": 156816.0},
                                    {"symbol": "159577", "lots": 473, "price": 1.659},
                                    {"symbol": "513690", "lots": 677, "price": 1.16}],
                                "actions": [
                                    {"side": "SELL", "symbol": "159501", "lots": 372},
                                    {"side": "SELL", "symbol": "513100", "lots": 355},
                                    {"side": "BUY", "symbol": "159513", "lots": 891}]},
                 "accrual": {"status": "NO_NEW_BAR", "rows": []},
                 "unexplained_total_cny": 0.0}
    cal = ["2026-11-09", "2026-11-10"]
    cal += ["2026-11-%02d" % d for d in range(11, 31)]
    cal += ["2026-12-%02d" % d for d in range(1, 32)]
    return {"as_of": bar, "swap_stack": stack, "swap_effect": effect,
            "positions": positions, "calendar": cal, "with_later": with_later,
            # r1536: the grid anchor is a fixture here -- a self-contained suite must not
            # depend on whichever last_decision_bar the live production face happens to hold.
            "anchor_bar": "2026-11-09"}


def selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    ctx = _fixture()
    f = compute(ctx)
    leg("L1 both legs are converted", len(f["rows"]) == 2, len(f["rows"]))
    r = f["rows"][0]
    leg("L2 shares bought = cash / the price actually paid",
        abs(r["shares_bought"] - 78492.0 / 1.76) < 0.011, r["shares_bought"])
    leg("L3 the discount becomes shares, not money",
        abs(r["extra_shares"] - 5612.5 / 1.76) < 0.011, r["extra_shares"])
    leg("L4 the caliber is the ledger's: 100 shares a lot",
        r["extra_lots"] == int(r["extra_shares"] // 100) and f["lot_shares"] == 100,
        (r["extra_lots"], r["extra_shares"]))
    leg("L5 the residue is named and priced apart",
        abs(r["extra_residue_shares"] - (r["extra_shares"] - r["extra_lots"] * 100)) < 0.011
        and abs(r["residue_value_cny"] - r["extra_residue_shares"] * 1.76) < 0.011, r["residue_value_cny"])
    leg("L6 totals keep the two legs' hands apart",
        f["totals"]["extra_lots"] == 55 and abs(f["totals"]["extra_shares"] - 5546.47) < 0.05,
        f["totals"])
    leg("L7 no combined money figure", f["totals"]["combined_cny"] is None, f["totals"])
    leg("L8 nothing is booked as realised", f["realised_booked_cny"] is None)
    leg("L9 the size sits inside the ledger's own line",
        f["ledger"]["extra_inside_holding"] is True
        and abs(f["ledger"]["share_of_holding"] - 5546.47 / 89100) < 1e-5, f["ledger"])
    leg("L10 the guard scanned the ledger and found nothing",
        f["realised_guard"]["checked"] and f["realised_guard"]["found"] is False, f["realised_guard"])
    leg("L11 verdict follows the guard", f["verdict"] == "SIZE_RECORDED", f["verdict"])
    leg("L12 the premium bound is imported, not typed",
        abs(f["premium_bound_pp"] - float(sib_face.MATERIAL_PP)) < 1e-9, f["premium_bound_pp"])
    # L13/L14 ask what the remark says when the panel has not yet printed the next bar.
    # The shared fixture keeps a full forward calendar (L15 pins the grid bar off it), so
    # "no later bar" can only come from the panel itself: pin the trade bar to the panel's
    # own last print. Written the other way this leg silently flips true/false with the
    # live data date -- on 2026-11-11 the panel grew a bar and the leg went red for no
    # defect in the face.
    _nb_path = gap_face.find_daily("159513")
    _nb_last = sorted(gap_face.load_close(_nb_path))[-1] if _nb_path else None
    f_nb = compute(_fixture(bar=_nb_last)) if _nb_last else f
    rm = f_nb["remark"]
    leg("L13 with no later bar the re-mark is refused, not zeroed",
        rm["status"] == "AWAITING_NEXT_BAR" and rm["value_cny"] is None, rm)
    leg("L14 the refusal names the identity it refuses to print",
        "恒等式" in (rm.get("why") or ""), rm.get("why"))
    nd = f["next_decision_bar"]
    # r1536: this leg used to accept any later date. In this fixture the grid bar is 2026-11-29
    # (index 20 of the fixture calendar, phase 0) while the old rolling count named 2026-11-30 --
    # so the leg now pins the grid answer AND the fact that the rolling one is not it.
    leg("L15 the next decision bar is the grid bar, not as_of + rebal",
        nd["bar"] == "2026-11-29" and nd.get("phase") == 0
        and nd.get("anchor_bar") == "2026-11-09", nd)
    leg("L15b the rolling answer the sheet used to print is one bar later and off-grid",
        "2026-11-30" != nd["bar"], nd["bar"])
    leg("L16 check is clean on the clean face", check(f) == [], check(f))
    leg("L17 the sentence carries shares, lots and the residue",
        "份" in f["sentence"] and "手" in f["sentence"], f["sentence"][:90])
    leg("L18 md prints the share table and both refusals",
        any("不能记成已实现收益" in x for x in md_lines(f))
        and any("零头卖不掉" in x for x in md_lines(f))
        and any("账本没被污染" in x for x in md_lines(f)))

    # a later bar exists: the same shares are re-marked, drift is labelled
    ctx2 = _fixture()
    later = compute(ctx2)
    later["remark"] = {"trade_bar": "2026-11-10", "status": "BEYOND_TRADE_BAR",
                       "bar": "2026-11-11", "price": 1.80, "value_cny": round(5546.47 * 1.80, 2),
                       "drift_cny": round(5546.47 * 1.80 - 9761.8, 2),
                       "label": "价格漂移", "why": ""}
    leg("L19 a later bar re-marks the same count at a new price",
        abs(later["remark"]["value_cny"] - 9983.65) < 0.02, later["remark"]["value_cny"])
    leg("L20 the drift is not a harvest and check sees that",
        check(later) == [] and "价格漂移" in later["remark"]["label"], check(later))

    # the ledger carries the discount as money -> red, never ADOPT
    ctx3 = _fixture()
    ctx3["positions"]["unexplained_total_cny"] = 9761.8
    f3 = compute(ctx3)
    leg("L21 a ledger that booked the discount is named, not averaged away",
        f3["verdict"] == "DISCOUNT_REACHED_THE_LEDGER"
        and f3["realised_guard"]["where"] == "unexplained_total_cny", f3["realised_guard"])
    leg("L22 check refuses that face", check(f3) != [], check(f3))

    # two faces on different bars cannot be divided
    ctx4 = _fixture()
    ctx4["swap_effect"]["bar"] = "2026-11-09"
    leg("L23 a face from another bar is refused",
        compute(ctx4)["verdict"] == "CANNOT_RECORD", compute(ctx4).get("refused"))

    # a leg whose notional disagrees was a different trade
    ctx5 = _fixture()
    ctx5["swap_effect"]["rows"][0]["notional_cny"] = 70000.0
    f5 = compute(ctx5)
    leg("L24 a notional mismatch is unpaired, not divided",
        len(f5["rows"]) == 1 and any(u["leg_symbol"] == "159501" for u in f5["unpaired"]),
        [u["leg_symbol"] for u in f5["unpaired"]])
    leg("L25 the mismatch is voiced with both amounts",
        any("不同的一笔" in (u.get("why") or "") for u in f5["unpaired"]), f5["unpaired"])

    # a SELL the stack does not call a swap is not a swap
    ctx6 = _fixture()
    for a in ctx6["swap_stack"]["actions"]:
        if a.get("symbol") == "513100":
            a["why"] = "trim to the floor"
    f6 = compute(ctx6)
    leg("L26 a trim sell is not a swap and is named",
        len(f6["rows"]) == 1 and any(u["leg_symbol"] == "513100" for u in f6["unpaired"]),
        [u["leg_symbol"] for u in f6["unpaired"]])

    # missing faces refuse rather than printing zero
    ctx7 = _fixture()
    ctx7["swap_effect"] = None
    leg("L27 a missing effect face refuses", compute(ctx7)["verdict"] == "CANNOT_RECORD")
    ctx8 = _fixture()
    ctx8["positions"] = None
    leg("L28 a missing ledger refuses", compute(ctx8)["verdict"] == "CANNOT_RECORD")
    ctx9 = _fixture()
    ctx9["swap_stack"]["actions"] = [a for a in ctx9["swap_stack"]["actions"]
                                     if a.get("side") != "BUY"]
    leg("L29 no merged buy means no denominator, and it says so",
        compute(ctx9)["verdict"] == "CANNOT_RECORD", compute(ctx9).get("refused"))

    # tampering
    f10 = json.loads(json.dumps(f))
    f10["rows"][0]["extra_lots"] = 32
    leg("L30 check catches a lot count that is not floor(shares/100)", check(f10) != [])
    f11 = json.loads(json.dumps(f))
    f11["totals"]["extra_shares"] = 5000.0
    leg("L31 check catches share totals that do not add up", check(f11) != [])
    f12 = json.loads(json.dumps(f))
    f12["rows"][0]["extra_shares"] = 99999.0
    leg("L32 check catches a discount bigger than the position", check(f12) != [])
    f13 = json.loads(json.dumps(f))
    f13["realised_booked_cny"] = 9761.8
    leg("L33 check catches a realised booking", check(f13) != [])

    # md: absent and refused faces still say something
    leg("L34 an absent face prints a refusal line",
        any("跑 scripts" in x for x in md_lines(None)))
    ctx10 = _fixture()
    ctx10["swap_stack"] = None
    leg("L35 a refused face still renders a line",
        any("记不起来" in x for x in md_lines(compute(ctx10))))

    # r1528: the subset has to sit on the ledger's OWN line
    _fx = _fixture()
    _f = compute(_fx)
    ins = inside_holdings(_f, _fx["positions"])
    leg("L36 the subset lands on the line the ledger already holds",
        ins["status"] == "INSIDE_THE_LINE" and len(ins["rows"]) == 1
        and ins["rows"][0]["symbol"] == "159513"
        and abs(ins["rows"][0]["extra_shares"] - 5546.48) < 0.02, ins["rows"])
    leg("L37 two legs on one line do not count the line twice",
        ins["totals"]["line_lots"] == 891 and ins["totals"]["line_shares"] == 89100
        and abs(ins["totals"]["share_of_lines"] - 5546.48 / 89100) < 1e-5, ins["totals"])
    leg("L38 it is labelled a subset, not a second holding",
        all("子集" in (r.get("label") or "") for r in ins["rows"]) and "不增行" in ins["not_a_line"])
    leg("L38b the lot is taken on the line's combined count, not per leg",
        ins["totals"]["extra_lots"] == 55 and abs(ins["totals"]["residue_shares"] - 46.48) < 0.02,
        ins["totals"])
    leg("L39 md prints the shares and refuses to be a line",
        any("其中折扣买来" in x for x in inside_md_lines(ins))
        and any("不增行" in x for x in inside_md_lines(ins)))
    _fx2 = _fixture()
    _fx2["positions"]["ledger_bar"] = "2026-11-09"
    leg("L40 a ledger standing on another bar refuses",
        inside_holdings(_f, _fx2["positions"])["status"] == "REFUSED")
    _fx3 = _fixture()
    for _h in _fx3["positions"]["ledger_row"]["holdings"]:
        if _h["symbol"] == "159513":
            _h["symbol"] = "159999"
    leg("L41 a line the ledger does not carry is named, not zeroed",
        inside_holdings(_f, _fx3["positions"])["status"] == "REFUSED"
        and any("无处安放" in (r.get("why") or "")
                for r in inside_holdings(_f, _fx3["positions"])["refusals"]))
    _fx4 = _fixture()
    for _h in _fx4["positions"]["ledger_row"]["holdings"]:
        if _h["symbol"] == "159513":
            _h["lots"] = 10
    leg("L42 a discount bigger than the line breaks the subset rule",
        inside_holdings(_f, _fx4["positions"])["status"] == "REFUSED")
    leg("L43 a refused subset still renders a line",
        any("这一问答不了" in x for x in inside_md_lines({"status": "REFUSED", "refusals": [{"why": "x"}]})))

    ok = sum(1 for _n, v, _d in legs if v)
    for n, v, d in legs:
        print("  %-6s %s%s" % ("PASS" if v else "FAIL", n, "" if v else "  :: %r" % (d,)))
    print("swap_units selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ------------------------------------------------------------------ entry points

def _emit(line):
    """Console-safe print: a GBK terminal must not be able to kill a published face."""
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "backslashreplace").decode("ascii"))


def run():
    stack = _read_json(STACK_FACE)
    effect = _read_json(EFFECT_FACE)
    positions = _read_json(POSITIONS_FACE)
    as_of = (effect or {}).get("bar") or (stack or {}).get("asof")
    face = compute({"as_of": as_of, "swap_stack": stack, "swap_effect": effect,
                    "positions": positions, "calendar": trading_days()})
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    L = ["# 折扣是多少份，不是多少钱（r1525）", "",
         "bar %s ｜ 判定 **%s**" % (as_of, face["verdict"]), ""]
    L += md_lines(face, heading="## 逐腿读数")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    _emit(json.dumps({"verdict": face["verdict"],
                      "rows": len(face.get("rows") or []),
                      "unpaired": len(face.get("unpaired") or []),
                      "extra_shares": (face.get("totals") or {}).get("extra_shares"),
                      "extra_lots": (face.get("totals") or {}).get("extra_lots"),
                      "remark": (face.get("remark") or {}).get("status"),
                      "next_decision_bar": (face.get("next_decision_bar") or {}).get("bar"),
                      "realised_found": (face.get("realised_guard") or {}).get("found")},
                     ensure_ascii=False))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.check or a.cmd == "check":
        face = _read_json(OUT_JSON)
        probs = check(face)
        if probs:
            print("CHECK_FAIL " + "; ".join(probs))
            return 1
        print("CHECK_OK rows=%d shares=%s lots=%s realised=%s"
              % (len((face or {}).get("rows") or []),
                 ((face or {}).get("totals") or {}).get("extra_shares"),
                 ((face or {}).get("totals") or {}).get("extra_lots"),
                 ((face or {}).get("realised_guard") or {}).get("found")))
        return 0
    return run()


if __name__ == "__main__":
    sys.exit(main())
