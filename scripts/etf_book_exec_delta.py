#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""etf_book_exec_delta -- the trades the sheet implies, from the book it starts from.

WHY THIS FILE EXISTS
--------------------
`ORDER-<bar>.md` prints a TARGET book (5 names x weight x NAV, whole lots) and, in
`results/etf_book_positions.json`, a CURRENT book (what the account actually holds after
the last execution). Nothing on the sheet subtracts the two. On 2026-11-10 the account held
159263 / 159513 / 159577 / 513690 while the sheet asked for 159263 / 159577 / 513690 /
159501 / 513100 -- four names against five, one held name not in the target at all, two
target names not held at all. An operator holding that account has to do the subtraction,
the lot arithmetic and the cash arithmetic by hand before placing an order, and the sheet
gives them no way to check the result.

Two sentences elsewhere on the sheet are about this exact question and cannot answer it:
r1468 prints "按票面修回来要再打 ￥313,763" without saying 313,763 of WHAT, and r1467 warns
that the trim table and the swap line both sell the same leg. So the numbers exist -- they
are just never turned into a row per name with a side, a lot count and an amount.

r1521 -- WHICH BOOK. Both of the sentences above were quoting a number that was wrong, and
this face was quoting the same one. The ticket prints an ENTRY table (5 names) and, on the
same page, a swap line that rewrites two of those legs into one sibling before anything is
sent. The account had already executed the swap, so subtracting the entry table from it
ordered the swap to be undone: sell 891 of the share just bought, buy back the two legs just
sold -- 313,763 CNY of turnover on a book that needed none. The target is now the sheet's own
POST-SWAP book (`swap_stack.holdings_after`), the entry table is kept and named beside it, and
an exit of a name the swap just bought is a refusal rather than a trade.

WHAT IT IS NOT
--------------
Not a new signal and not a re-decision. The target comes from the ticket (its own post-swap
book when the swap ran on this bar); the current book comes from the executed positions face;
this file only subtracts them, in whole lots, at the sheet's own prices, and checks that the
result reconciles the sheet's own cash line.

THE GATE (why the numbers are trustworthy)
------------------------------------------
The implied actions must carry the current book to the sheet's OWN published numbers:
  risk book after  == sum(ticket.order[].amount)          (<= 1 CNY)
  cash after       == ticket.ticket.cash_amount            (<= 1 CNY)
  current total    == positions.ledger_row.risk_book_cny   (<= 1 CNY)
If any of the three fails, the table is not the sheet's action and is refused, not printed
with a caveat. On 2026-11-10 all three hold to the cent, and risk_after also equals the sum
of the five printed rows (392,535.90 vs the 393,073.00 nominal order, the 0.05% lot
underspend the sheet already declares).

MODES
-----
  run       write results/etf_book_exec_delta.json (+ .md) for the newest ticket.
  check     re-derive every published number from the ticket and refuse a drift.
  selftest  offline legs over synthetic tickets (the face's own contract).

Exit codes: 0 ok / 2 cannot build (no ticket, unreadable ticket) /
            3 refused (the sheet carries no target, or no book to start from).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_exec_delta.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_exec_delta.md")
POS_FACE = os.path.join(ROOT, "results", "etf_book_positions.json")

LOT = 100
TOL = 1.0        # per row: lots x price vs the row's money (prices print to 3dp)
SUM_TOL = 0.05   # side totals and the cash identity are cents, not yuan


def _ticket_path(path=None):
    if path:
        return path
    hits = sorted(glob.glob(os.path.join(TICKET_DIR, "TICKET-*.json")))
    return hits[-1] if hits else None


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _refused(bar, why):
    return {"artifact": "etf_book_exec_delta", "bar": bar, "verdict": "CANNOT_SUBTRACT",
            "refused": why, "rows": [], "gross_buy_cny": 0.0, "gross_sell_cny": 0.0,
            "turnover_cny": 0.0, "net_cash_cny": 0.0, "target_total_cny": 0.0,
            "current_total_cny": 0.0, "cash_before_cny": None, "cash_after_cny": None,
            "sheet_cash_cny": None, "cash_recon_cny": None, "unpriced_rows": [],
            "current_rows": 0, "target_rows": 0, "held_not_in_target": [],
            "in_target_not_held": [], "target_source": None, "target_note": None,
            "swap_bought": [], "entry_sheet_moved": {}, "entry_rows": 0,
            "entry_book_cny": 0.0, "swap_book_cny": None,
            "current_bar": None, "current_book_from": None, "declaration": None,
            "ledger_row_risk_book_cny": None, "mark": None,
            "cash_recon_ex_mark_cny": None}


ENTRY = "entry_sheet"
SWAP = "swap_stack.holdings_after"


def _lots_map(rows):
    return {str(r["symbol"]): int(r.get("lots") or 0) for r in rows if r.get("symbol")}


def resolve_target(ticket, bar, order):
    """WHICH book is the executable one on this bar -- the entry sheet or the swap book?

    The entry sheet is what the account would buy if it opened today; the swap line
    (r1466/r1467) rewrites some of those legs into one sibling before anything is sent.
    Subtracting the raw entry sheet from a book that has already executed the swap
    describes a trade that undoes the sheet's own instruction: on 2026-11-10 this face
    printed "sell 891 of 159513, buy 372 / 355" while the swap section of the same page
    said the exact opposite -- a 313,763 CNY round trip, paying the shelf twice for
    nothing.

    So: when the swap face is on this bar and it actually moved the book, the target is
    its own post-trade book. Otherwise the entry sheet stands, and a swap face from
    another bar is named rather than mixed in (two bars cannot be subtracted).
    """
    sw = ticket.get("swap_stack") or {}
    sw_bar = sw.get("asof")
    post = [h for h in (sw.get("holdings_after") or []) if h.get("symbol")]
    if not post:
        return order, ENTRY, None, {}
    if not (sw_bar and bar and str(sw_bar) == str(bar)):
        return order, ENTRY, (
            "换票面是 %s 的、本单是 %s 的——两本不同 bar 不能相减，本节按入场表算"
            % (sw_bar, bar)), {}
    entry, postm = _lots_map(order), _lots_map(post)
    if entry == postm:
        return order, ENTRY, None, {}
    moved = {s: {"entry_lots": entry.get(s, 0), "executed_lots": postm.get(s, 0)}
             for s in sorted(set(entry) | set(postm))
             if entry.get(s, 0) != postm.get(s, 0)}
    rows = [{"symbol": str(h["symbol"]), "price": h.get("price"),
             "lots": int(h.get("lots") or 0), "amount": float(h.get("amount_cny") or 0.0)}
            for h in post]
    return rows, SWAP, None, moved


def compute(ticket):
    """Subtract the executed book from the sheet's target, in whole lots.

    Returns None only when the sheet has no target at all; every other "cannot" is a
    published face that says why (a face that prints nothing is unreadable, not safe).
    """
    bar = ticket.get("as_of") or ticket.get("evidence_cutoff")
    tk = ticket.get("ticket") or {}
    order = [r for r in (tk.get("order") or []) if r.get("symbol")]
    if not order:
        return None
    pos = ticket.get("positions") or {}
    led = pos.get("ledger_row") or {}
    lb, tb = pos.get("ledger_bar"), pos.get("ticket_bar")
    holdings = [h for h in (led.get("holdings") or []) if h.get("symbol")]
    if not holdings:
        return _refused(bar, "账上没有可减的持仓行（positions.ledger_row.holdings 缺失）")
    if lb and tb and str(lb) != str(tb):
        return _refused(bar, "账上这一本停在 %s、票面是 %s 的，两根 bar 不能相减" % (lb, tb))
    # A positions face that reconciled against an OLDER sheet agrees with itself
    # (ledger_bar == ticket_bar) and would still subtract a book this sheet never saw.
    if tb and bar and str(tb) != str(bar):
        return _refused(bar, "账本上一次对的是 %s 的票面、本单是 %s 的" % (tb, bar))
    # r1562: the row this face subtracts must be a book somebody bought. positions writes
    # it from the sheet's own `holdings_after`, so when the swing replaces the sleeve and
    # prints no trades the row is the target wearing the account's clothes -- subtracting
    # it from that same target returns 0 everywhere and the sheet says "already on target"
    # on a bar that needed nine trades (11-11: 4 out, 5 in, 153% turnover).
    # r1563: so don't refuse and don't subtract the declaration -- subtract the newest row a
    # trade list can actually reach (positions.account_row), and name the row it came from.
    # The operator holding the last bought book is exactly who needs this table.
    _tr = pos.get("transition") or {}
    declared = str(_tr.get("status") or "").startswith("UNEXPLAINED")
    declaration = None
    if declared:
        _acct = pos.get("account_row") or {}
        _holdings = [h for h in (_acct.get("holdings") or []) if h.get("symbol")]
        if not _holdings:
            return _refused(
                bar,
                "账本 %s 那一行记的是票面的目标、不是买进来的账：票面只印了 %d 条动作，"
                "却换出 %d 只（%s）、换进 %d 只（%s）、改了 %d 只的手数，约 %s 元没有动作支撑。"
                "按这一行相减只会得到 0——那是票面跟自己减；而账本里又找不到更早的一本真账，"
                "本节没有可减的起点"
                % ((pos.get("ledger_bar") or bar), int(_tr.get("actions") or 0),
                   len(_tr.get("vanished") or []),
                   "、".join(_tr.get("vanished") or []) or "无",
                   len(_tr.get("appeared") or []),
                   "、".join(_tr.get("appeared") or []) or "无",
                   len(_tr.get("lots_changed") or []),
                   "未知" if _tr.get("cny_moved") is None
                   else "{:,.0f}".format(float(_tr.get("cny_moved")))))
        led = _acct
        holdings = _holdings
        declaration = {"bar": pos.get("ledger_bar") or bar,
                       "from_bar": _tr.get("from_bar"),
                       "actions": int(_tr.get("actions") or 0),
                       "status": _tr.get("status"),
                       "vanished": list(_tr.get("vanished") or []),
                       "appeared": list(_tr.get("appeared") or []),
                       "lots_changed": list(_tr.get("lots_changed") or []),
                       "cny_moved": _tr.get("cny_moved")}

    target_rows, target_source, swap_note, moved = resolve_target(ticket, bar, order)
    target = {r["symbol"]: r for r in target_rows}
    have = {h["symbol"]: h for h in holdings}
    sw = ticket.get("swap_stack") or {}
    swap_used = target_source == SWAP
    swap_bought = (sorted(str(a.get("symbol")) for a in (sw.get("actions") or [])
                          if str(a.get("side") or "").upper() == "BUY")
                   if (sw.get("asof") and bar and str(sw["asof"]) == str(bar)) else [])

    rows, unpriced = [], []
    for sym in sorted(set(target) | set(have)):
        t = target.get(sym) or {}
        c = have.get(sym) or {}
        price = t.get("price") or c.get("price")
        tlots = int(t.get("lots") or 0) if t else 0
        clots = int(c.get("lots") or 0) if c else 0
        dlots = tlots - clots
        px = float(price) if price else None
        if dlots != 0 and (px is None or px <= 0):
            unpriced.append(sym)
            amount = None
        else:
            amount = abs(dlots) * LOT * px if px else 0.0
        rows.append({"symbol": sym, "price": None if px is None else round(px, 6),
                     "current_lots": clots, "target_lots": tlots, "delta_lots": dlots,
                     "side": ("SELL" if dlots < 0 else "BUY" if dlots > 0 else "HOLD"),
                     "amount_cny": None if amount is None else round(amount, 2),
                     "held": sym in have, "in_target": sym in target})

    # Actionable order: sells first (their cash funds the buys), then holds, then buys.
    rows.sort(key=lambda r: ({"SELL": 0, "HOLD": 1, "BUY": 2}[r["side"]],
                             -(r["amount_cny"] or 0.0), r["symbol"]))

    def total(side):
        return round(sum(r["amount_cny"] or 0.0 for r in rows if r["side"] == side), 2)

    gross_sell, gross_buy = total("SELL"), total("BUY")
    net_cash = round(gross_buy - gross_sell, 2)
    cash_before = led.get("cash_cny")
    cash_after = None if cash_before is None else round(float(cash_before) - net_cash, 2)
    # The cash/book line this face must land on belongs to the same book it subtracts.
    sheet_cash = sw.get("cash_cny") if swap_used else tk.get("cash_amount")
    recon = (None if (cash_after is None or sheet_cash is None)
             else round(cash_after - float(sheet_cash), 2))
    # r1563: when the account sits on an older bar its kept legs still carry THAT bar's
    # price, while the target book is priced on this one. The difference is a mark, not a
    # cash error: sell the old book at the sheet's own prices and the identity closes to the
    # cent (11-11: 677 lots of 513690 moved 1.160 -> 1.155 = -338.50, exactly the gap).
    # Measure the mark and gate on the residual -- never on a relaxed tolerance.
    mark = None
    if str(led.get("bar") or "") != str(bar or ""):
        drift, mrows = 0.0, []
        for sym in sorted(set(target) & set(have)):
            tp = target[sym].get("price")
            cp = have[sym].get("price")
            keep = min(int(target[sym].get("lots") or 0), int(have[sym].get("lots") or 0))
            if not tp or not cp or keep <= 0:
                continue
            d = keep * LOT * (float(tp) - float(cp))
            drift += d
            mrows.append({"symbol": sym, "lots": keep,
                          "account_price": round(float(cp), 6),
                          "sheet_price": round(float(tp), 6),
                          "mark_cny": round(d, 2)})
        mark = {"account_bar": led.get("bar"), "bar": bar, "rows": mrows,
                "drift_cny": round(drift, 2),
                "note": ("账上那本按 %s 的价、票面按 %s 的价：保留腿重估的差额单列，"
                         "不并进现金对账" % (led.get("bar"), bar))}
    recon_ex = (None if (recon is None or mark is None)
                else round(float(recon) - float(mark["drift_cny"]), 2))
    current_total = round(sum(float(h.get("amount_cny") or 0.0) for h in holdings), 2)
    target_total = round(sum(float(t.get("amount") or 0.0) for t in target_rows), 2)
    sheet_book = (sw.get("risk_book_after_cny") if swap_used
                  else (tk.get("book_weight") and round(
                      float(tk["book_weight"]) * float(tk.get("nav") or 0.0), 2)))

    if unpriced:
        verdict = "UNPRICED"
    elif gross_buy == 0 and gross_sell == 0:
        verdict = "ALREADY_ON_TARGET"
    elif cash_after is not None and cash_after < 0:
        verdict = "CASH_SHORT"
    elif gross_sell == 0:
        verdict = "BUY_ONLY"
    elif gross_buy == 0:
        verdict = "SELL_DOWN_ONLY"
    else:
        verdict = "SHEET_IMPLIES_A_SWAP"

    return {
        "artifact": "etf_book_exec_delta", "bar": bar, "verdict": verdict, "refused": None,
        "ticket_file": None,
        "rows": rows,
        "gross_sell_cny": gross_sell, "gross_buy_cny": gross_buy,
        "turnover_cny": round(gross_buy + gross_sell, 2), "net_cash_cny": net_cash,
        "target_total_cny": target_total, "current_total_cny": current_total,
        "target_source": target_source, "target_note": swap_note,
        "swap_bought": swap_bought, "entry_sheet_moved": moved,
        "entry_rows": len(order),
        "entry_book_cny": round(sum(float(r.get("amount") or 0.0) for r in order), 2),
        "swap_book_cny": None if not swap_used else round(float(sheet_book or 0.0), 2),
        "sheet_book_cny": sheet_book,
        "cash_before_cny": None if cash_before is None else round(float(cash_before), 2),
        "cash_after_cny": cash_after, "sheet_cash_cny": None if sheet_cash is None else round(float(sheet_cash), 2),
        "cash_recon_cny": recon,
        "ledger_risk_book_cny": None if led.get("risk_book_cny") is None else round(float(led["risk_book_cny"]), 2),
        # r1563: WHICH row this table subtracts from, and what it is not.
        "current_bar": led.get("bar"),
        "current_book_from": {
            "bar": led.get("bar"),
            "kind": str(led.get("kind") or "execution"),
            "source": "book_before_declaration" if declared else "ledger_row",
            "declared_bar": pos.get("ledger_bar") or bar,
        },
        "declaration": declaration,
        "mark": mark,
        "cash_recon_ex_mark_cny": recon_ex,
        "ledger_row_risk_book_cny": None if (pos.get("ledger_row") or {}).get("risk_book_cny")
        is None else round(float((pos.get("ledger_row") or {}).get("risk_book_cny")), 2),
        "unpriced_rows": unpriced,
        "current_rows": len(holdings), "target_rows": len(order),
        "held_not_in_target": sorted(s for s in have if s not in target),
        "in_target_not_held": sorted(s for s in target if s not in have),
        "turnover_share_of_book_pct": None if not current_total else round(
            (gross_buy + gross_sell) / current_total * 100.0, 2),
    }


def same_bar_positions(ticket, path=None):
    """The account statement that is ON THE TICKET'S OWN BAR, from disk, if there is one.

    The ticket carries a snapshot of `results/etf_book_positions.json` taken while it was
    being built. On 2026-11-12 that snapshot was the 11-11 statement (written 16:31) while
    the account's own 11-12 row settled at 16:53 -- the snapshot's `ledger_bar` then read
    11-12 (the row the NEXT sheet starts from) against a row still dated 11-11, and this
    section refused with "two bars cannot be subtracted" on a sheet that implied eight
    trades. Both books are real; only one of them is the bar this sheet decides from.

    So: use the statement only when it is the same bar as the sheet (asof and ticket_bar
    both on it). Anything else keeps the embedded snapshot, and either way the face says
    which of the two it subtracted.
    """
    bar = str(ticket.get("as_of") or ticket.get("evidence_cutoff") or "")
    if not bar:
        return None
    try:
        pos = _load(path or POS_FACE)
    except Exception:
        return None
    if not isinstance(pos, dict):
        return None
    if str(pos.get("asof") or "") != bar or str(pos.get("ticket_bar") or "") != bar:
        return None
    if not (pos.get("ledger_row") or {}).get("holdings"):
        return None
    return pos


def compute_for_ticket(ticket, positions_path=None, prefer_live=True):
    """Compute on the sheet's own bar, and name which statement was subtracted.

    One resolver for the page, the published face and the check leg: the same ticket must
    give the same table no matter who asks for it (a second copy of this choice is how the
    page and the face came to disagree on 11-11).
    """
    live = same_bar_positions(ticket, positions_path) if prefer_live else None
    if live is not None:
        t = dict(ticket)
        t["positions"] = live
        face = compute(t)
        if face is not None and not face.get("refused"):
            face["positions_source"] = "face@%s" % live.get("asof")
            return face
    face = compute(ticket)
    if face is not None:
        face["positions_source"] = "ticket_embedded"
    return face


def verify(face, bar=None, ticket_file=None):
    """Is this the sheet's action, and does it reconcile? Returns (bad, mism)."""
    if not face:
        return ["面不存在"], []
    if face.get("refused"):
        return ["算不出来：%s" % face["refused"]], []
    rows = face.get("rows") or []
    if not rows:
        return ["面里没有逐名行"], []
    bad = []
    for r in rows:
        d, cny, px = r.get("delta_lots"), r.get("amount_cny"), r.get("price")
        if d in (None, 0):
            continue
        if px is None or float(px) <= 0 or cny is None:
            bad.append("%s 有手数没有价" % r.get("symbol"))
            continue
        if abs(float(cny) - abs(int(d)) * LOT * float(px)) > TOL:
            bad.append("%s 手数×价 ≠ 金额" % r.get("symbol"))
    for side, key in (("SELL", "gross_sell_cny"), ("BUY", "gross_buy_cny")):
        tot = sum(float(r["amount_cny"] or 0.0) for r in rows if r["side"] == side)
        if abs(tot - float(face.get(key) or 0.0)) > SUM_TOL:
            bad.append("%s 逐名合计 %.2f ≠ 面自己 %s" % (side, tot, face.get(key)))
    cb, ca, net = face.get("cash_before_cny"), face.get("cash_after_cny"), face.get("net_cash_cny")
    if cb is not None and ca is not None and net is not None:
        if abs((float(cb) - float(net)) - float(ca)) > SUM_TOL:
            bad.append("现金恒等式不成立：%.2f - %.2f ≠ %.2f" % (cb, net, ca))
    rec = face.get("cash_recon_ex_mark_cny")
    if rec is None:
        rec = face.get("cash_recon_cny")
    if rec is not None and abs(float(rec)) > SUM_TOL:
        bad.append("动作后的现金 %.2f 与票面自己写的 %.2f 对不上（差 %.2f，已扣保留腿价差 %s）"
                   % (ca, face.get("sheet_cash_cny"), rec,
                      "未单列" if face.get("mark") is None
                      else "%+.2f" % (float(face.get("cash_recon_cny") or 0.0)
                                      - float(rec))))
    lrb, cur = face.get("ledger_risk_book_cny"), face.get("current_total_cny")
    if lrb is not None and cur is not None and abs(float(lrb) - float(cur)) > SUM_TOL:
        bad.append("账上逐名合计 %.2f ≠ 账本自己的风险腿 %.2f" % (cur, lrb))
    # r1563: a table that starts from an older bar must SAY it does. A book one bar back
    # wearing today's label is the same defect as a target wearing the account's clothes.
    cbf = face.get("current_book_from") or {}
    cbar = face.get("current_bar")
    if cbf:
        if face.get("bar") and cbar and str(cbar) != str(face["bar"]):
            if cbf.get("source") != "book_before_declaration" or not face.get("declaration"):
                bad.append("相减的账停在 %s，却没说是声明之前的那一本" % cbar)
            if not str((face.get("declaration") or {}).get("status") or "").startswith(
                    "UNEXPLAINED"):
                bad.append("声明块没有说是哪一种对不上")
        elif cbf.get("source") != "ledger_row":
            bad.append("相减的就是本 bar 的账本行，却标成 %r" % (cbf.get("source"),))
    # The two sections of one page must not order opposite trades on the same bar.
    ts = face.get("target_source")
    if ts is not None and ts not in (ENTRY, SWAP):
        bad.append("目标来路 %r 不是认得的两种之一（入场表 / 换票后账）" % ts)
    sb = face.get("swap_book_cny")
    if ts == SWAP and sb is not None and abs(float(sb) - float(face.get("target_total_cny") or 0.0)) > SUM_TOL:
        bad.append("相减用的换票后账 %.2f ≠ 换票面自己写的执行后账 %.2f"
                   % (float(face.get("target_total_cny") or 0.0), float(sb)))
    exit_swapped = sorted(set(face.get("held_not_in_target") or []) & set(face.get("swap_bought") or []))
    if exit_swapped:
        bad.append("票面换票刚买进的 %s 又被整只卖出——两节自相矛盾"
                   % "、".join(exit_swapped))
    mism = []
    if bar and face.get("bar") and str(face["bar"]) != str(bar):
        mism.append("面是 %s 的、这一张是 %s 的" % (face["bar"], bar))
    if ticket_file and face.get("ticket_file") and face["ticket_file"] != ticket_file:
        mism.append("面来自 %s、这一张是 %s" % (face["ticket_file"], ticket_file))
    return bad, mism


def _money(x):
    return format(float(x), ",.2f")


def positions_source_note(face):
    """WHICH statement this table subtracted, in one line the reader can check.

    r1590: the face has carried `positions_source` since r1521 (the statement on the
    sheet's own bar, or the snapshot embedded in the ticket), and the sheet printed
    neither -- so the one choice that decides every row of the action table was visible
    only to whoever opened the JSON. E281 family: a field nobody prints is not a
    disclosure. The raw token rides along in backticks so a leg can pin the page to the
    face instead of trusting the prose.
    """
    src = (face or {}).get("positions_source")
    if not src:
        return None
    if str(src).startswith("face@"):
        return ("- 相减用的账：**盘上账本面**（`results/etf_book_positions.json`，asof %s）"
                "——不是票面构建那一刻的内嵌快照。｜`positions_source=%s`"
                % (str(src)[len("face@"):], src))
    return ("- 相减用的账：**票面内嵌快照**（票面构建那一刻的账）——盘上没有与本单同 bar"
            " 的账本面，本节因此减的是那一刻那本账。｜`positions_source=%s`" % src)


# r1589: the fields `run()` stamps on the face after computing it. They describe the
# envelope (which ticket file, which cutoff the run recorded), not the subtraction, so
# they are the ONLY keys this comparison may skip.
ENVELOPE_KEYS = ("ticket_file", "evidence_cutoff")


def drift(old, fresh):
    """Every published number, re-derived: the ONE definition of 'the same face'.

    r1590: `check()` compared eight keys plus the rows, while the smoke leg compared the
    whole dict -- so a ticket-only stamp (`ticket_file`) and an envelope field
    (`evidence_cutoff`) made the leg red by construction, and it stayed red for as long
    as nobody looked. Two versions of the same question is how a leg comes to measure
    something the module never promised. Both readers call this now.

    r1589: and the fix may not be weaker than the leg it replaced. A hand-listed nine
    keys silently stopped covering whatever the face grew next -- `declaration` (the
    per-bar action reconciliation, the reason this face exists), `mark`, `unpriced_rows`
    and `cash_recon_cny` were all published and all compared by nothing, i.e. a sheet
    could have drifted on the one block a reader checks by hand while this gate stayed
    green. The comparison is now "everything the face publishes, minus the two envelope
    stamps", so a new field is covered the moment it is written instead of the moment
    somebody remembers to add it to a list.
    """
    old, fresh = old or {}, fresh or {}
    bad = []
    for k in sorted((set(old) | set(fresh)) - set(ENVELOPE_KEYS)):
        if old.get(k) != fresh.get(k):
            bad.append("%s %r != %r" % (k, fresh.get(k), old.get(k)))
    return bad


def sentence(face):
    if not face:
        return "这张票面没有目标，本面不出数。"
    if face.get("refused"):
        return "这张单算不出要下的动作：%s。" % face["refused"]
    v = face["verdict"]
    if v == "ALREADY_ON_TARGET":
        if face.get("target_source") == SWAP:
            return ("账上 %d 只已经在票面换票之后的账上——入场表 %d 只里被换掉的那几只"
                    "（%s）不用再买回来，这张单不需要再动一手。"
                    % (face["current_rows"], face.get("entry_rows") or 0,
                       "、".join(sorted((face.get("entry_sheet_moved") or {})))))
        return ("账上 %d 只与票面 %d 只已经逐名对齐，这张单不需要下单。"
                % (face["current_rows"], face["target_rows"]))
    if v == "UNPRICED":
        return ("这张单有 %d 只手数没有价（%s），不能折成钱，本面拒印金额。"
                % (len(face["unpriced_rows"]), "、".join(face["unpriced_rows"])))
    parts = []
    if face["gross_sell_cny"]:
        parts.append("卖 **%s 元**" % _money(face["gross_sell_cny"]))
    if face["gross_buy_cny"]:
        parts.append("买 **%s 元**" % _money(face["gross_buy_cny"]))
    head = ("账上 %d 只 → 票面 %d 只：今天要 %s，合计动 **%s 元**"
            "（相当于账上风险腿的 %.1f%%）。"
            % (face["current_rows"], face["target_rows"], "、".join(parts),
               _money(face["turnover_cny"]), face["turnover_share_of_book_pct"] or 0.0))
    if v == "CASH_SHORT":
        return head + " 账上现金不够：动作后现金会是 **%s 元**。" % _money(face["cash_after_cny"])
    if face.get("cash_recon_cny") is not None and abs(face["cash_recon_cny"]) <= SUM_TOL:
        head += (" 账上现金 %s → 动作后 **%s**，与票面自己写的现金 **%s** 对得上。"
                 % (_money(face["cash_before_cny"]), _money(face["cash_after_cny"]),
                    _money(face["sheet_cash_cny"])))
    return head


def md_lines(face, heading="## 这张单实际要下的动作（r1516）"):
    if not face:
        return ["", heading, "- 这张票面没有目标，算不出动作。", ""]
    if face.get("refused"):
        _L = ["", heading, "- **算不出来**：%s。" % face["refused"]]
        _s = positions_source_note(face)
        if _s:
            _L.append(_s)
        return _L + ["- 读法：本面只做减法，不猜账。「算不出来」与「不用下单」是两件事，"
                     "缺的是账上那一行，不是动作本身。", ""]
    L = ["", heading, "- %s" % sentence(face)]
    _src = positions_source_note(face)
    if _src:
        L.append(_src)
    _dec = face.get("declaration") or {}
    if _dec:
        L.append("- **账本 %s 那一行不是买进来的账**：票面这一天只印了 %d 条动作，"
                 "却换出 %d 只（%s）、换进 %d 只（%s）、改了 %d 只的手数（约 %s 元）。"
                 "本节因此从 **%s 那一本**相减——那是最后一本有人买进来的账。"
                 % (_dec.get("bar"), int(_dec.get("actions") or 0),
                    len(_dec.get("vanished") or []), "、".join(_dec.get("vanished") or []) or "无",
                    len(_dec.get("appeared") or []), "、".join(_dec.get("appeared") or []) or "无",
                    len(_dec.get("lots_changed") or []),
                    "未知" if _dec.get("cny_moved") is None
                    else _money(_dec.get("cny_moved")),
                    (face.get("current_book_from") or {}).get("bar")))
        L.append("- 读法：这张表是「拿着 %s 那本真账的人今天该下的单」；"
                 "票面目标与账本那一行谁写错了不归本节裁定，本节只保证不拿目标减目标。"
                 % ((face.get("current_book_from") or {}).get("bar")))
    if face.get("target_source") == SWAP:
        moved = face.get("entry_sheet_moved") or {}
        if moved:
            L.append("- 这一节相减用的「票面」是**换票之后的账**（r1467）：%s。"
                     % "；".join("%s 入场 %d 手 → 换票后 %d 手"
                                 % (s, v["entry_lots"], v["executed_lots"])
                                 for s, v in sorted(moved.items())))
            L.append("- 所以这里的 0 手不是「没算」：按入场表再减一遍会印出与上面换票节"
                     "方向相反的动作表（卖回换票刚买的那只），那是票面自己跟自己打架。")
    elif face.get("target_note"):
        L.append("- %s。" % face["target_note"])
    if face.get("mark"):
        _mk = face["mark"]
        L.append("- 价差单列（不是现金差）：账上那一本按 **%s** 的收盘价、票面按 **%s** 的价。"
                 "两边都持有的那几只按手数重估，合计 **%s 元**（%s）；"
                 "扣掉它，动作后的现金与票面自己写的现金差 **%s 元**。"
                 % (_mk.get("account_bar"), _mk.get("bar"), _money(_mk.get("drift_cny")),
                    "；".join("%s %d 手 %.3f→%.3f" % (r["symbol"], r["lots"],
                                                      r["account_price"], r["sheet_price"])
                             for r in _mk.get("rows") or []) or "无重叠持有腿",
                    "无" if face.get("cash_recon_ex_mark_cny") is None
                    else _money(face.get("cash_recon_ex_mark_cny"))))
    if face.get("held_not_in_target"):
        L.append("- 账上有、票面没有 **%s**：这些是整只退出（不是减仓），卖出金额算在下面。"
                 % "、".join(face["held_not_in_target"]))
    if face.get("in_target_not_held"):
        L.append("- 票面有、账上没有 **%s**：这些是整只新建，手数从 0 起算。"
                 % "、".join(face["in_target_not_held"]))
    # r1521b: a zero-action sheet still prints the rows. "Nothing to do" is a claim about
    # four specific names x lots, and the reader can only check it if the lots are on the
    # page -- skipping the table made the strongest statement on the sheet the only one
    # nothing beside it could verify (the smoke leg re-derives each row and refused).
    if face["verdict"] == "UNPRICED":
        L.append("")
        return L
    L += ["", "| 代码 | 价 | 账上 | 票面 | 差额 | 动作 | 金额 |", "|---|---|---|---|---|---|---|"]
    for r in face["rows"]:
        px = "-" if r["price"] is None else "%.3f" % r["price"]
        amt = "-" if r["amount_cny"] is None else _money(r["amount_cny"])
        L.append("| %s | %s | %d | %d | %+d | %s | %s |"
                 % (r["symbol"], px, r["current_lots"], r["target_lots"], r["delta_lots"],
                    {"SELL": "卖", "BUY": "买", "HOLD": "不动"}[r["side"]], amt))
    L += ["",
          "- 口径：差额按整手算，价用票面自己的参考价（账上有、票面没有的名用账本自己的价）；"
          "卖出排在买入前面，因为卖出的钱当天可用于买入。",
          "- 对账（这一节不是文案，是三条恒等式）：账上风险腿 %s → 票面 %s（票面名义 %s）；"
          "现金 %s → %s，与票面自己写的 %s 差 %s；账上逐名合计与账本风险腿 %s 一致。"
          % (_money(face["current_total_cny"]), _money(face["target_total_cny"]),
             _money(face["sheet_book_cny"] or 0.0),
             _money(face["cash_before_cny"] or 0.0), _money(face["cash_after_cny"] or 0.0),
             _money(face["sheet_cash_cny"] or 0.0), _money(face["cash_recon_cny"] or 0.0),
             _money(face["ledger_risk_book_cny"] or 0.0)),
          "- 判定 **%s**｜出处 results/etf_book_exec_delta.json（同一份题面另存为文件）。"
          % face["verdict"], ""]
    return L


def render_md(face):
    if not face:
        return "# 这张单要下的动作\n\n这张票面没有目标。\n"
    body = md_lines(face, heading="# 这张单要下的动作（%s）" % face.get("bar"))[1:]
    return "\n".join(body)


def run(path=None):
    tp = _ticket_path(path if isinstance(path, str) else None)
    if not tp or not os.path.exists(tp):
        print("no ticket to subtract")
        return 2
    tk = _load(tp)
    face = compute_for_ticket(tk)
    if not face:
        print("ticket carries no target -- nothing to execute")
        return 3
    face["ticket_file"] = os.path.basename(tp)
    face["evidence_cutoff"] = face.get("bar")
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face) + "\n")
    print(sentence(face))
    bad, _ = verify(face)
    if bad:
        print("REFUSED " + "; ".join(bad))
        return 3
    print("wrote %s" % os.path.relpath(OUT_JSON, ROOT))
    return 0


def check(path=None):
    tp = _ticket_path(path if isinstance(path, str) else None)
    if not tp:
        print("CHECK_FAIL no ticket")
        return 2
    fresh = compute_for_ticket(_load(tp))
    if not os.path.exists(OUT_JSON):
        print("CHECK_FAIL no face on disk")
        return 2
    old = _load(OUT_JSON)
    bad = drift(old, fresh)
    if bad:
        print("CHECK_FAIL " + "; ".join(bad))
        return 3
    print("CHECK_OK rows=%d turnover=%.2f verdict=%s"
          % (len(old["rows"]), old["turnover_cny"], old["verdict"]))
    return 0


def _fixture(order_rows, holdings, cash=100000.0, bar="2026-01-01", cash_amount=None):
    tk_order = [{"symbol": s, "price": p, "lots": l, "shares": l * LOT,
                 "amount": round(l * LOT * p, 2), "weight": 0.0, "class": "equity"}
                for s, l, p in order_rows]
    book = round(sum(r["amount"] for r in tk_order), 2)
    hold = [{"symbol": s, "lots": l, "price": p, "amount_cny": round(l * LOT * p, 2)}
            for s, l, p in holdings]
    risk = round(sum(h["amount_cny"] for h in hold), 2)
    return {"as_of": bar,
            "ticket": {"nav": risk + cash, "order": tk_order,
                       "cash_amount": (round(cash - (book - risk), 2)
                                       if cash_amount is None else cash_amount),
                       "beta_k": 0.5, "book_weight": 0.5, "cash_weight": 0.5},
            "positions": {"ledger_bar": bar, "ticket_bar": bar,
                          "ledger_row": {"bar": bar, "cash_cny": cash,
                                         "risk_book_cny": risk, "holdings": hold}}}


def selftest():
    ok = []

    def leg(name, cond):
        ok.append((name, bool(cond)))

    # A hold-2 / target-2 book whose actions are exactly one exit and one entry.
    f = compute(_fixture([("B", 10, 2.0), ("C", 5, 1.0)], [("A", 10, 2.0), ("C", 5, 1.0)],
                         cash=80000.0))
    leg("L1 a swap sheet is named as a swap", f["verdict"] == "SHEET_IMPLIES_A_SWAP")
    rows = {r["symbol"]: r for r in f["rows"]}
    leg("L2 the held-only name is sold in full, at the book's own price",
        rows["A"]["side"] == "SELL" and rows["A"]["delta_lots"] == -10
        and abs(rows["A"]["amount_cny"] - 2000.0) < TOL)
    leg("L3 the target-only name is built from zero",
        rows["B"]["side"] == "BUY" and rows["B"]["delta_lots"] == 10
        and abs(rows["B"]["amount_cny"] - 2000.0) < TOL)
    leg("L4 untouched name stays HOLD with zero money",
        rows["C"]["side"] == "HOLD" and rows["C"]["amount_cny"] == 0.0)
    leg("L5 sells are printed before buys (their cash funds them)",
        [r["side"] for r in f["rows"]][:1] == ["SELL"]
        and [r["side"] for r in f["rows"]][-1] == "BUY")
    leg("L6 cash identity holds on a fixture that reconciles",
        abs((f["cash_before_cny"] - f["net_cash_cny"]) - f["cash_after_cny"]) < TOL)
    leg("L7 the same book on both sides needs no trades",
        compute(_fixture([("A", 10, 2.0)], [("A", 10, 2.0)], cash=5000.0))["verdict"]
        == "ALREADY_ON_TARGET")
    leg("L8 buying more of a held name is BUY_ONLY, not a swap",
        compute(_fixture([("A", 20, 2.0)], [("A", 10, 2.0)], cash=5000.0))["verdict"]
        == "BUY_ONLY")
    leg("L9 selling part of a held name is SELL_DOWN_ONLY",
        compute(_fixture([("A", 5, 2.0)], [("A", 10, 2.0)], cash=5000.0))["verdict"]
        == "SELL_DOWN_ONLY")
    leg("L10 a book that ends up overdrawn is CASH_SHORT",
        compute(_fixture([("A", 100, 2.0)], [("A", 1, 2.0)], cash=100.0))["verdict"]
        == "CASH_SHORT")
    leg("L11 no holdings -> refused face, not a zero trade",
        compute({"as_of": "2026-01-01", "ticket": {"order": [{"symbol": "A", "lots": 1, "price": 1.0}],
                                                   "nav": 100.0},
                 "positions": {"ledger_row": {}}})["verdict"] == "CANNOT_SUBTRACT")
    _diffbar = _fixture([("A", 10, 2.0)], [("A", 10, 2.0)], cash=5000.0)
    _diffbar["positions"]["ledger_bar"] = "2025-12-31"
    leg("L12 two different bars are refused, not subtracted",
        compute(_diffbar)["verdict"] == "CANNOT_SUBTRACT")
    leg("L13 an unpriced row is listed and the money is refused, never zeroed",
        compute(_fixture([("B", 10, 2.0)], [("A", 10, 2.0)], cash=5000.0).copy()
                | {"positions": {"ledger_bar": "2026-01-01", "ticket_bar": "2026-01-01",
                                 "ledger_row": {"bar": "2026-01-01", "cash_cny": 5000.0,
                                                "risk_book_cny": 2000.0,
                                                "holdings": [{"symbol": "A", "lots": 10,
                                                              "price": None,
                                                              "amount_cny": 2000.0}]}}}
                )["unpriced_rows"] == ["A"])
    # a positions face that agrees with itself but reconciled against an OLDER sheet
    _oldface = _fixture([("A", 10, 2.0)], [("A", 10, 2.0)], cash=5000.0)
    _oldface["positions"]["ticket_bar"] = "2025-12-31"
    leg("L13b a book reconciled against an older sheet is refused, not silently reused",
        compute(_oldface)["verdict"] == "CANNOT_SUBTRACT")

    # gate legs: the fixture reconciles, so verify must be silent on it; each tamper must speak
    good = compute(_fixture([("B", 10, 2.0)], [("A", 10, 2.0)], cash=80000.0))
    leg("L14 verify passes a table that reconciles to the sheet's own cash",
        verify(good) == ([], []))
    _bad = json.loads(json.dumps(good))
    _bad["rows"][0]["amount_cny"] = _bad["rows"][0]["amount_cny"] + 50.0
    leg("L15 verify refuses a row whose lots x price is not its money",
        any("手数×价" in b for b in verify(_bad)[0]))
    _bad2 = json.loads(json.dumps(good))
    _bad2["gross_sell_cny"] = _bad2["gross_sell_cny"] + 1.0
    leg("L16 verify refuses a side total that its own rows do not sum to",
        any("逐名合计" in b for b in verify(_bad2)[0]))
    _bad3 = json.loads(json.dumps(good))
    _bad3["sheet_cash_cny"] = _bad3["sheet_cash_cny"] + 100.0
    _bad3["cash_recon_cny"] = round(_bad3["cash_after_cny"] - _bad3["sheet_cash_cny"], 2)
    leg("L17 verify refuses an action that does not land on the sheet's cash line",
        any("票面自己写的" in b for b in verify(_bad3)[0]))
    leg("L18 another bar's table is a mismatch, not a broken one",
        verify(good, bar="2026-01-02")[0] == []
        and any("这一张是 2026-01-02 的" in m for m in verify(good, bar="2026-01-02")[1]))
    leg("L19 a refused face cannot be printed as a table",
        verify(compute({"as_of": "b", "ticket": {"order": [{"symbol": "A", "lots": 1,
                                                            "price": 1.0}], "nav": 1.0},
                        "positions": {"ledger_row": {}}}))[0] != [])
    leg("L20 the sentence carries the turnover and the cash line, not just the verdict",
        "合计动" in sentence(good) and "对得上" in sentence(good))
    leg("L21 a zero-trade sentence does not claim an order",
        "不需要下单" in sentence(compute(_fixture([("A", 10, 2.0)], [("A", 10, 2.0)],
                                                 cash=5000.0))))

    # --- the swap book is the executable target (2026-11-10 live case) -------------
    def _swap_fixture(swap_bar="2026-01-01"):
        f = _fixture([("A", 10, 2.0), ("B", 10, 1.0)], [("C", 16, 1.85)],
                     cash=50000.0, bar="2026-01-01")
        f["swap_stack"] = {
            "asof": swap_bar,
            "holdings_after": [{"symbol": "C", "lots": 16, "price": 1.85,
                                "amount_cny": round(16 * LOT * 1.85, 2)}],
            "cash_cny": 50000.0,
            "risk_book_after_cny": round(16 * LOT * 1.85, 2),
            "actions": [{"side": "SELL", "symbol": "A", "lots": 10},
                        {"side": "SELL", "symbol": "B", "lots": 10},
                        {"side": "BUY", "symbol": "C", "lots": 16}],
        }
        return f

    _sf = compute(_swap_fixture())
    leg("L22 a book already on the swap's post-trade book has nothing to trade",
        _sf["verdict"] == "ALREADY_ON_TARGET" and _sf["turnover_cny"] == 0.0
        and _sf["target_source"] == SWAP)
    leg("L23 without the swap face the same ticket orders the reversal "
        "(that is the defect this block exists for)",
        compute({k: v for k, v in _swap_fixture().items() if k != "swap_stack"})
        ["turnover_cny"] > 0.0)
    leg("L24 the subtracted book is the swap face's own post-trade book, to the cent",
        abs(_sf["target_total_cny"] - _sf["swap_book_cny"]) <= SUM_TOL)
    leg("L25 verify passes the swap book that reconciles",
        verify(_sf) == ([], []))
    _bad4 = json.loads(json.dumps(_sf))
    _bad4["swap_book_cny"] = _bad4["swap_book_cny"] + 10.0
    leg("L26 verify refuses a swapped target that is not the swap face's own book",
        any("换票面自己写的执行后账" in b for b in verify(_bad4)[0]))
    _bad5 = json.loads(json.dumps(_sf))
    _bad5["held_not_in_target"] = ["C"]
    leg("L27 an exit of the name the swap just bought is a refusal, not a trade",
        any("两节自相矛盾" in b for b in verify(_bad5)[0]))
    _fb = compute(_swap_fixture(swap_bar="2025-12-31"))
    leg("L28 a swap face from another bar is named, never mixed in",
        _fb["target_source"] == ENTRY and "不同 bar" in (_fb.get("target_note") or "")
        and _fb["turnover_cny"] > 0.0)
    leg("L29 the zero-trade sentence says which book the account is already on",
        "换票之后的账" in sentence(_sf))
    # r1521b: "nothing to trade" is a claim about specific names x lots; the rows must be
    # printed or the reader has no way to check the strongest sentence on the sheet.
    _md30 = "\n".join(md_lines(_sf))
    leg("L30 a zero-action sheet still prints a row per name (the claim is checkable)",
        "| 159263 |" not in _md30 and all(
            "| %s |" % r["symbol"] in _md30 for r in _sf["rows"]) and len(_sf["rows"]) > 0)
    # r1562: the account row is written from the sheet's own target, so a rebalance that
    # prints no trades makes the subtraction a tautology. The refusal has to name the names.
    _rep = _fixture([("B", 10, 2.0), ("C", 5, 1.0)], [("A", 10, 2.0)], cash=80000.0)
    _rep["positions"]["transition"] = {
        "bar": "2026-01-01", "from_bar": "2025-12-31", "actions": 0,
        "status": "UNEXPLAINED_TARGET_WITHOUT_TRADES",
        "vanished": ["A"], "appeared": ["B"], "lots_changed": [], "cny_moved": 2000.0}
    _fr = compute(_rep)
    leg("L31 a ledger row the sheet's own trades cannot reach is refused, not subtracted to 0",
        _fr["verdict"] == "CANNOT_SUBTRACT" and "不是买进来的账" in (_fr.get("refused") or "")
        and "A" in (_fr.get("refused") or "") and "B" in (_fr.get("refused") or ""))
    leg("L32 an explained row is still subtracted normally",
        compute(_fixture([("B", 10, 2.0)], [("A", 10, 2.0)], cash=90000.0))["verdict"]
        != "CANNOT_SUBTRACT")
    # r1563: a refusal that names the names is only half a product -- the operator holding the
    # last bought book needs the table. When positions publishes that book (account_row), the
    # subtraction starts there and the declaration is printed beside it.
    _decl = _fixture([("B", 10, 2.0), ("C", 5, 1.0)], [("A", 10, 2.0)], cash=80000.0)
    _decl["positions"]["transition"] = {
        "bar": "2026-01-01", "from_bar": "2025-12-31", "actions": 0,
        "status": "UNEXPLAINED_TARGET_WITHOUT_TRADES",
        "vanished": ["A"], "appeared": ["B"], "lots_changed": [], "cny_moved": 2000.0}
    _decl["positions"]["account_row"] = {
        "bar": "2025-12-31", "kind": "execution", "source": "book_before_declaration",
        "risk_book_cny": 2000.0, "cash_cny": 80000.0,
        "holdings": [{"symbol": "A", "lots": 10, "price": 2.0, "amount_cny": 2000.0}],
        "actions": [{"side": "BUY", "symbol": "A", "lots": 10}]}
    _fd = compute(_decl)
    leg("L33 a declaration is subtracted from the last bought book, not from itself",
        _fd["verdict"] == "SHEET_IMPLIES_A_SWAP"
        and (_fd.get("current_book_from") or {}).get("source") == "book_before_declaration"
        and _fd.get("current_bar") == "2025-12-31")
    _fdr = {r["symbol"]: r for r in _fd["rows"]}
    leg("L34 and the table sells what that book holds, not what the target holds",
        _fdr["A"]["side"] == "SELL" and _fdr["A"]["delta_lots"] == -10
        and _fdr["B"]["side"] == "BUY" and _fdr["B"]["delta_lots"] == 10)
    leg("L35 the declared-book table passes its own gates and names the declaration",
        verify(_fd) == ([], []) and (_fd.get("declaration") or {}).get("bar") == "2026-01-01")
    _fdmd = "\n".join(md_lines(_fd))
    leg("L36 the sheet says which bar the table starts from",
        "2025-12-31 那一本" in _fdmd and "不是买进来的账" in _fdmd)
    _fdbad = json.loads(json.dumps(_fd))
    _fdbad["current_book_from"]["source"] = "ledger_row"
    leg("L37 a table from an older bar labelled as today's row is refused",
        any("没说是声明之前" in b for b in verify(_fdbad)[0]))
    # r1563: the kept leg carries the OLD bar's price, so the cash line closes only after the
    # mark is measured. The gate goes on the residual, never on a looser tolerance.
    _mk = _fixture([("A", 10, 2.5), ("B", 10, 1.0)], [("A", 10, 2.0)], cash=50000.0)
    _mk["positions"]["transition"] = {
        "bar": "2026-01-01", "from_bar": "2025-12-31", "actions": 0,
        "status": "UNEXPLAINED_TARGET_WITHOUT_TRADES", "vanished": [], "appeared": ["B"],
        "lots_changed": [], "cny_moved": 1000.0}
    _mk["positions"]["account_row"] = {
        "bar": "2025-12-31", "kind": "execution", "source": "book_before_declaration",
        "risk_book_cny": 2000.0, "cash_cny": 50000.0,
        "holdings": [{"symbol": "A", "lots": 10, "price": 2.0, "amount_cny": 2000.0}],
        "actions": []}
    _fm = compute(_mk)
    _fm_ex = _fm.get("cash_recon_ex_mark_cny")
    leg("L38 the kept leg's price move is measured, not folded into the cash gap",
        abs(float((_fm.get("mark") or {}).get("drift_cny") or 0.0) - 500.0) <= SUM_TOL
        and abs(float(_fm.get("cash_recon_cny") or 0.0) - 500.0) <= SUM_TOL
        and _fm_ex is not None and abs(float(_fm_ex)) <= SUM_TOL)
    leg("L39 so the table still passes its gates with the mark disclosed",
        verify(_fm) == ([], []))
    _fm_no = json.loads(json.dumps(_fm))
    _fm_no["mark"] = None
    _fm_no.pop("cash_recon_ex_mark_cny", None)
    leg("L40 an unexplained gap of the same size is still refused",
        any("对不上" in b for b in verify(_fm_no)[0]))

    # r1585: the ticket's embedded statement can be a bar behind the sheet (11-12 sheet
    # built 16:31 on the 11-11 statement; the account's 11-12 row settled at 16:53). The
    # same ticket must then subtract the sheet's own bar and SAY which statement it used.
    with tempfile.TemporaryDirectory() as td:
        _live = _fixture([("B", 10, 2.0)], [("A", 10, 2.0)], cash=80000.0, bar="2026-01-02")
        _live["positions"]["asof"] = "2026-01-02"
        _lp = os.path.join(td, "pos_2026-01-02.json")
        with open(_lp, "w", encoding="utf-8") as fh:
            json.dump(_live["positions"], fh)
        _tmpl = _fixture([("B", 10, 2.0)], [("A", 10, 2.0)], cash=80000.0, bar="2026-01-01")
        _sheet = {"as_of": "2026-01-02", "ticket": _tmpl["ticket"],
                  "positions": _tmpl["positions"], "swap_stack": {}}
        _emb = compute_for_ticket(_sheet, positions_path=_lp, prefer_live=False)
        leg("L41 the embedded statement, one bar behind the sheet, is refused",
            _emb["verdict"] == "CANNOT_SUBTRACT"
            and _emb["positions_source"] == "ticket_embedded")
        _use = compute_for_ticket(_sheet, positions_path=_lp)
        leg("L42 the statement on the sheet's own bar is the one subtracted, and named",
            _use["positions_source"] == "face@2026-01-02"
            and _use["verdict"] == "SHEET_IMPLIES_A_SWAP" and verify(_use) == ([], []))
        _gone = compute_for_ticket(_sheet, positions_path=os.path.join(td, "absent.json"))
        leg("L43 without a statement on this bar the face falls back and says so",
            _gone["positions_source"] == "ticket_embedded")
        _offbar = _fixture([("B", 10, 2.0)], [("A", 10, 2.0)], cash=80000.0,
                           bar="2025-12-31")
        _op = os.path.join(td, "pos_2025-12-31.json")
        with open(_op, "w", encoding="utf-8") as fh:
            json.dump(_offbar["positions"], fh)
        leg("L44 a statement from another bar is never mixed in",
            compute_for_ticket(_sheet, positions_path=_op)["positions_source"]
            == "ticket_embedded")
        # r1590: the choice above decides every row of the action table and was printed
        # nowhere. The page must carry it, in the reader's language AND as the raw token,
        # and a face that never made the choice must not have one invented for it.
        _pg_face = "\n".join(md_lines(_use))
        _pg_emb = "\n".join(md_lines(_gone))
        leg("L45 the page names the statement it subtracted, both branches",
            positions_source_note(_use) in _pg_face
            and positions_source_note(_gone) in _pg_emb
            and positions_source_note(_use) != positions_source_note(_gone)
            and "positions_source=face@2026-01-02" in _pg_face
            and "positions_source=ticket_embedded" in _pg_emb
            and "盘上账本面" in _pg_face and "票面内嵌快照" in _pg_emb)
        leg("L46 a face that made no such choice prints no source line",
            positions_source_note(_emb) in _pg_emb
            and positions_source_note({"positions_source": None}) is None
            and positions_source_note(None) is None)
        # L47/L48: one comparison, two readers. The envelope stamps a ticket-only field
        # (ticket_file) and run()'s own cutoff must not make a face "drift"; a changed
        # subtraction source or a changed row must.
        _stamped = dict(_use, ticket_file="TICKET-2026-01-02.json",
                        evidence_cutoff=_use.get("bar"))
        leg("L47 ticket-only stamps are not drift", drift(_stamped, _use) == [])
        _flipped = dict(_use, positions_source="ticket_embedded")
        _rows = json.loads(json.dumps(_use))
        _rows["rows"][0]["delta_lots"] = int(_rows["rows"][0]["delta_lots"]) + 1
        leg("L48 a changed source or a changed row still drifts",
            bool(drift(_flipped, _use)) and bool(drift(_rows, _use))
            and any("positions_source" in b for b in drift(_flipped, _use)))
        # r1589: the coverage leg. `declaration` is the block a reader checks by hand and
        # it sat outside the old nine-key list, so this leg would have passed while the
        # action reconciliation drifted. It fires on a field nobody listed -- i.e. it
        # proves the comparison is "everything published", not "everything remembered".
        _decl = json.loads(json.dumps(_fd))
        _decl["declaration"]["cny_moved"] = float(_decl["declaration"]["cny_moved"]) + 1.0
        leg("L49 a drift in a field nobody hand-listed still drifts",
            bool(drift(_decl, _fd)) and any("declaration" in b for b in drift(_decl, _fd)))

    bad = [n for n, v in ok if not v]
    for n, v in ok:
        print("%s %s" % ("[ok]" if v else "[FAIL]", n))
    print("selftest %d/%d" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--ticket", default=None)
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check(a.ticket)
    return run(a.ticket)


if __name__ == "__main__":
    sys.exit(main())
