"""ETF book -- two sections on one sheet, one book underneath.

r1455 put a permission trim on the sheet. r1466 put a swap trigger on the same sheet. Both
are true, and both are printed as if the other were not there:

  * the trim table sells 65 lots of 159501 (444 -> 379) to obey the floor;
  * the swap line sells "the 159501 leg" -- CNY 91,863.6, which is the *untrimmed* 444 lots.

Read side by side, the sheet sells 65 + 444 = 509 lots of a ticker the book holds 444 of.
Sequenced correctly (trim, then swap what is left) the two are consistent, but nothing on the
page says so, and the swap's CNY benefit is quoted on the size the permission already refused.

So the desk's next question is not economic, it is arithmetical:

    I have two sections and one book. What do I actually type?

This face answers with one netted order:

  * every actionable swap is re-sized on the *trimmed* lot count (not the ordered one), so its
    benefit is repriced on the book that is allowed to exist;
  * the whole action list is netted per ticker (sell here, buy there), lot-rounded at the
    sibling's price, and the integer-lot residue is printed instead of disappearing;
  * two swaps that point at the same sibling are merged into one buy, and the merged name's
    share of the risk book is printed next to the number of distinct baskets it still carries.

Usage:
    python scripts/etf_book_swap_stack.py run
    python scripts/etf_book_swap_stack.py --check
    python scripts/etf_book_swap_stack.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_sibling_gap as gap_face  # noqa: E402  (one implementation of the panel reads)

ORDER_DIR = os.path.join(ROOT, "results", "etf_book_order")
LATEST = os.path.join(ORDER_DIR, "latest.json")
SWAP_FACE = os.path.join(ROOT, "results", "etf_book_swap_trigger.json")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_swap_stack.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_swap_stack.md")

LOT_SHARES = 100  # one lot is 100 shares on this board

# A verdict that tells the desk to swap now. NOT_ACTIONABLE / CANNOT_VERIFY are words, not
# trades, and they must not be re-sized here -- an upstream refusal may not be revived
# downstream (r1466 rule 3).
ACTIONABLE = ("ACT_ON_THIS_BAR", "ACT_ON_ANY_BAR", "WINDOW_ALWAYS_OPEN")


def _read_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def latest_ticket_path():
    """The sheet in force, as the order module itself points at it."""
    ptr = _read_json(LATEST)
    name = (ptr or {}).get("file")
    if name:
        p = os.path.join(ORDER_DIR, os.path.basename(str(name)))
        if os.path.exists(p):
            return p
    return None


def trim_targets(perm):
    """{symbol: lots the permission allows} -- absent trim means the ordered size stands."""
    legs = ((perm or {}).get("trim") or {}).get("legs") or []
    out = {}
    for r in legs:
        sym = r.get("symbol")
        tgt = r.get("lots_target")
        if sym is None or tgt is None:
            continue
        out[str(sym)] = int(tgt)
    return out


def trim_sells(perm):
    """{symbol: lots the trim table already sells} -- what is printed in the other section."""
    legs = ((perm or {}).get("trim") or {}).get("legs") or []
    out = {}
    for r in legs:
        sym = r.get("symbol")
        sell = r.get("lots_sell")
        if sym is None or not sell:
            continue
        out[str(sym)] = int(sell)
    return out


def sibling_price(symbol, asof, finder=None):
    """The sibling's own close on the ticket's priced bar, or None.

    Read from the same local board the gap face reads; a panel whose last bar is not the
    priced bar is refused rather than silently priced on a stale tick (r1290 class).
    """
    finder = finder or gap_face.find_daily
    path = finder(symbol)
    if not path:
        return None, "no local daily panel for %s" % symbol
    try:
        close = gap_face.load_close(path)
    except OSError as exc:                                          # noqa: BLE001
        return None, "panel unreadable: %r" % (exc,)
    if not close:
        return None, "panel carries no closes"
    last = max(close)
    if asof and last != asof:
        return None, "sibling panel ends at %s, ticket is priced at %s" % (last, asof)
    return float(close[last]), ""


def net_order(order, targets, swaps, prices):
    """One executable action list per ticker, from two sections that each ignore the other.

    `order`: the ticket's ordered legs (symbol, price, lots). `targets`: what the permission
    allows per leg. `swaps`: actionable pairs. `prices`: {sibling: price}. Pure arithmetic --
    the selftest feeds it fixtures instead of a ticket.
    """
    held = {str(r["symbol"]): r for r in order or []}
    rows, residue, notes = [], 0.0, []

    # 1. what the trim alone would leave, per leg
    post = {}
    for sym, r in held.items():
        ordered = int(r.get("lots") or 0)
        post[sym] = int(targets.get(sym, ordered))

    # 2. swaps re-sized on the trimmed count, merged per sibling
    buy_by_sibling = {}
    for sw in swaps or []:
        leg = str(sw["leg_symbol"])
        sib = str(sw["sibling_symbol"])
        if leg not in held:
            notes.append("换出腿 %s 不在本单里：上游换票面与票面不同源，这一对不执行" % leg)
            continue
        px = float(held[leg].get("price") or 0.0)
        lots_sell = post.get(leg, 0)
        if lots_sell <= 0 or px <= 0:
            notes.append("%s → %s：本单里这只腿没有可卖的整数手，跳过" % (leg, sib))
            continue
        proceeds = lots_sell * LOT_SHARES * px
        rows.append({"side": "SELL", "symbol": leg, "lots": lots_sell,
                     "price": px, "amount_cny": round(proceeds, 2),
                     "why": "swap %s → %s (r1466 verdict %s), sized on the trimmed %d lots"
                            % (leg, sib, sw.get("verdict"), lots_sell)})
        post[leg] = 0
        acc = buy_by_sibling.setdefault(sib, {"proceeds": 0.0, "from": []})
        acc["proceeds"] += proceeds
        acc["from"].append(leg)

    for sib, acc in sorted(buy_by_sibling.items()):
        px = prices.get(sib)
        if not px:
            notes.append("%s：没有同 bar 的收盘价，卖出款留在现金腿（不按旧价买）" % sib)
            residue += acc["proceeds"]
            continue
        per_lot = LOT_SHARES * float(px)
        lots_buy = int(acc["proceeds"] // per_lot)
        spent = lots_buy * per_lot
        residue += acc["proceeds"] - spent
        rows.append({"side": "BUY", "symbol": sib, "lots": lots_buy, "price": float(px),
                     "amount_cny": round(spent, 2),
                     "why": "merged buy for %s" % " + ".join(acc["from"])})
        post[sib] = post.get(sib, 0) + lots_buy

    # 3. the book that actually exists after the sheet is executed
    prices_all = {str(r["symbol"]): float(r.get("price") or 0.0) for r in order or []}
    prices_all.update({k: float(v) for k, v in (prices or {}).items()})
    holdings = []
    for sym, lots in sorted(post.items()):
        if lots <= 0:
            continue
        if sym not in prices_all:
            notes.append("%s：没有同日收盘价，账面权重算不出来" % sym)
            continue
        amt = lots * LOT_SHARES * prices_all[sym]
        holdings.append({"symbol": sym, "lots": int(lots), "price": prices_all[sym],
                         "amount_cny": round(amt, 2)})
    return rows, holdings, round(residue, 2), notes


def oversell_scan(order, perm, swaps):
    """Does the sheet, read top to bottom, sell more of a leg than the book holds?

    The swap line is priced on the ordered size (the gap face quotes the whole leg's amount),
    so a leg that the trim table already sells is sold twice: `sections_add_up_to` uses the
    ordered lots, which is what a reader following both sections would type.
    """
    held = {str(r["symbol"]): int(r.get("lots") or 0) for r in order or []}
    sells = trim_sells(perm)
    swapped = {str(s.get("leg_symbol")) for s in swaps or []
               if s.get("verdict") in ACTIONABLE}
    out = []
    for sym, s in sorted(sells.items()):
        if sym not in held:
            continue
        out.append({"symbol": sym, "trim_sells": s, "held": held[sym],
                    "swapped": sym in swapped,
                    "swap_sells_as_printed": held[sym] if sym in swapped else 0})
    return out


def book_block(ticket):
    """The order payload, whichever shape the sheet carries it in.

    The published ticket nests it under `ticket`; an older/flat shape puts the same fields on
    the top level. Both are read here so the face does not go blind on a shape change (and a
    truly unreadable sheet still yields an empty block, never a guessed one).
    """
    if not ticket:
        return {}
    inner = ticket.get("ticket")
    if isinstance(inner, dict) and inner.get("order"):
        return inner
    if ticket.get("order"):
        return ticket
    return {}


def assess(ticket, perm, swaps, prices, asof):
    book = book_block(ticket)
    order = book.get("order") or []
    nav = float(book.get("nav") or 0.0)
    targets = trim_targets(perm)
    k_now = float(book.get("beta_k") or (ticket or {}).get("k_now") or 0.0)

    actionable = [s for s in swaps or [] if s.get("verdict") in ACTIONABLE]
    rows, holdings, residue, notes = net_order(order, targets, actionable, prices)

    risk_before = sum(int(r.get("lots") or 0) * LOT_SHARES * float(r.get("price") or 0.0)
                      for r in order)
    risk_after = sum(h["amount_cny"] for h in holdings)
    k_after = (risk_after / nav) if nav else None
    floor = (perm or {}).get("permitted_k")
    ceiling = (perm or {}).get("ceiling_k")

    # repricing: the swap line is quoted on the size the permission refused
    repriced, dropped = [], 0.0
    held = {str(r["symbol"]): int(r.get("lots") or 0) for r in order}
    for s in actionable:
        leg = str(s["leg_symbol"])
        ordered = held.get(leg)
        trimmed = targets.get(leg, ordered) if ordered is not None else None
        if not ordered or not trimmed:
            continue
        share = trimmed / float(ordered)
        before = float(s.get("one_off_gain_cny") or 0.0) + float(s.get("repeatable_gain_cny") or 0.0)
        after = before * share
        dropped += before - after
        repriced.append({"leg": leg, "sibling": s["sibling_symbol"],
                         "ordered_lots": ordered, "trimmed_lots": trimmed,
                         "share": round(share, 4),
                         "gain_published_cny": round(before, 2),
                         "gain_on_trimmed_book_cny": round(after, 2),
                         "overstated_cny": round(before - after, 2)})

    # does merging two legs into one ticker change how many baskets the book carries?
    index_of = {str(s["leg_symbol"]): s.get("index") for s in swaps or [] if s.get("index")}
    baskets_after = set()
    for h in holdings:
        baskets_after.add(index_of.get(h["symbol"]) or h["symbol"])
    baskets_before = set(index_of.get(str(r["symbol"])) or str(r["symbol"]) for r in order)

    sib_share = None
    if holdings and risk_after:
        widest = max(holdings, key=lambda h: h["amount_cny"])
        sib_share = {"symbol": widest["symbol"],
                     "share_of_risk_book": round(widest["amount_cny"] / risk_after, 4)}

    over = oversell_scan(order, perm, actionable)
    oversell = []
    for row in over:
        sections = row["trim_sells"] + row["swap_sells_as_printed"]
        oversell.append({"symbol": row["symbol"], "held": row["held"],
                         "trim_sells": row["trim_sells"],
                         "swapped": row.get("swapped", False),
                         "swap_sells": row["swap_sells_as_printed"],
                         "sections_add_up_to": sections,
                         "as_printed_excess": sections - row["held"]})

    if not ticket:
        verdict = "CANNOT_VERIFY"
    elif not rows:
        verdict = "NOTHING_TO_NET"
    elif any(o["as_printed_excess"] > 0 for o in oversell):
        verdict = "TWO_SECTIONS_OVERSELL_THE_LEG"
    elif residue > 0:
        verdict = "NETTED_WITH_RESIDUE"
    else:
        verdict = "NETTED_CLEAN"

    return {
        "artifact": "etf_book_swap_stack",
        "asof": asof,
        "ticket": os.path.basename(latest_ticket_path() or "") or None,
        "sources": {"swap_trigger": rel(SWAP_FACE), "order_ticket": rel(latest_ticket_path())},
        "verdict": verdict,
        "k_ordered": round(k_now, 6),
        "k_after": None if k_after is None else round(k_after, 6),
        "floor_k": None if floor is None else float(floor),
        "ceiling_k": None if ceiling is None else float(ceiling),
        "within_permission": (None if k_after is None or floor is None
                              else bool(k_after <= float(floor) + 1e-6)),
        "risk_book_before_cny": round(risk_before, 2),
        "risk_book_after_cny": round(risk_after, 2),
        "cash_cny": round(nav - risk_after, 2) if nav else None,
        "lot_residue_cny": residue,
        "actions": rows,
        "holdings_after": holdings,
        "widest_name": sib_share,
        "baskets": {"before": sorted(baskets_before), "after": sorted(baskets_after),
                    "n_before": len(baskets_before), "n_after": len(baskets_after)},
        "oversell": oversell,
        "swap_repricing": repriced,
        "overstated_total_cny": round(dropped, 2),
        "notes": notes,
        "caveats": [
            "the merged name's share is a share of the risk book, not of NAV: it carries the "
            "same basket as the two legs it replaced, so the number of independent baskets is "
            "printed beside it and is what the concentration reading should use",
            "swap benefits are re-scaled linearly with notional (the gap face prices them as a "
            "percentage of the traded amount); fees, tracking difference and FX-hedge policy "
            "between the two tickers are still not priced",
            "the netted order is lot-rounded at the sibling's close on the priced bar; intraday "
            "execution will move both the proceeds and the bought lots",
        ],
    }


def rel(p):
    if not p:
        return None
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def load_inputs():
    tpath = latest_ticket_path()
    ticket = _read_json(tpath)
    perm = (ticket or {}).get("permission")
    sw = _read_json(SWAP_FACE)
    pairs = (sw or {}).get("pairs") or []
    asof = (ticket or {}).get("evidence_cutoff") or (sw or {}).get("session")
    prices, why = {}, {}
    for s in pairs:
        if s.get("verdict") not in ACTIONABLE:
            continue
        sib = str(s.get("sibling_symbol"))
        if sib in prices or sib in why:
            continue
        px, msg = sibling_price(sib, asof)
        if px is None:
            why[sib] = msg
        else:
            prices[sib] = px
    face = assess(ticket, perm, pairs, prices, asof)
    if why:
        face["unpriced_siblings"] = why
    if sw is None:
        face["verdict"] = "CANNOT_VERIFY"
        face["notes"].append("没有已发布的换票触发面（%s）：要换什么、换到哪只票都读不出来"
                             % rel(SWAP_FACE))
    return face


def render_md(face):
    L = ["# ETF 复合书 · 一张单两段话，一本书", "",
         "会话 `%s`｜票 `%s`｜上游 `%s`" % (face.get("asof"), face.get("ticket"),
                                          (face.get("sources") or {}).get("swap_trigger")), ""]
    v = face.get("verdict")
    headline = {
        "TWO_SECTIONS_OVERSELL_THE_LEG":
            "**这张单两段话卖同一只票**：额度表卖一部分、换票线卖整只腿，两段相加超过账面手数。"
            "按顺序执行（先裁后换）是对的，但纸面没说顺序，照着两段一起下单就是超卖。",
        "NETTED_WITH_RESIDUE":
            "**两段合成一笔**：换票在裁剪后手数上重算，整手取整剩下的零头留在现金腿。",
        "NETTED_CLEAN": "**两段合成一笔，且整手正好对齐**：没有零头留下。",
        "NOTHING_TO_NET": "**今天没有要合并的动作**：换票面没有 actionable 的对，本单只有额度裁剪。",
        "CANNOT_VERIFY": "**这一问答不了**：票面或换票面读不出来，不给净额单。",
    }.get(v, v or "?")
    L += [headline, ""]

    if face.get("actions"):
        L += ["## 你到底要下单的是什么（净额单）", "",
              "| 方向 | 代码 | 价 | 手数 | 金额 | 为什么 |",
              "|---|---|---|---|---|---|"]
        for r in face["actions"]:
            L.append("| **%s** | %s | %.3f | %d | ¥%s | %s |"
                     % (r["side"], r["symbol"], r["price"], r["lots"],
                        format(r["amount_cny"], ",.0f"), r["why"]))
        L.append("")

    if face.get("oversell"):
        L += ["## 两段话卖同一只票，加到多少", "",
              "| 代码 | 账面手数 | 额度表卖 | 换票线卖 | 两段相加 | 照两段下单会多卖 |",
              "|---|---|---|---|---|---|"]
        for o in face["oversell"]:
            if o.get("swapped"):
                last = (("**%+d 手**" % o["as_printed_excess"]) if o["as_printed_excess"]
                        else "0（正好）")
            else:
                last = "—（这只腿只有额度表卖，与换票无关）"
            L.append("| %s | %d | %d | %s | %s | %s |"
                     % (o["symbol"], o["held"], o["trim_sells"],
                        ("%d" % o["swap_sells"]) if o.get("swapped") else "—",
                        ("%d" % o["sections_add_up_to"]) if o.get("swapped") else "—", last))
        L += ["", "- 读法：额度表的「卖出手数」是按**裁剪后**的账算的，换票线的金额是"
              "按**未裁剪**的账算的；两张纸各说各的，谁也没错，但一起念就是超卖。"
              "顺序只有一种：先按额度裁，再拿剩下的整只腿去换。", ""]

    if face.get("swap_repricing"):
        L += ["## 换票的钱是照着哪一版账算的（重算）", "",
              "| 换出腿 | 换到 | 下单手数 | 裁剪后手数 | 占比 | 票面收益 | 裁剪后账面收益 | 高估 |",
              "|---|---|---|---|---|---|---|---|"]
        for r in face["swap_repricing"]:
            L.append("| %s | %s | %d | %d | %.1f%% | ¥%s | ¥%s | **¥%s** |"
                     % (r["leg"], r["sibling"], r["ordered_lots"], r["trimmed_lots"],
                        100.0 * r["share"], format(r["gain_published_cny"], ",.0f"),
                        format(r["gain_on_trimmed_book_cny"], ",.0f"),
                        format(r["overstated_cny"], ",.0f")))
        L += ["", "- 读法：换票面的收益按**下单量**定价，额度裁掉的那一部分不会再交易，"
              "所以它的收益也不会发生。合计高估 ¥%s——这才是你这张单真能拿到的数。"
              % format(face.get("overstated_total_cny") or 0.0, ",.0f"), ""]

    if face.get("holdings_after"):
        L += ["## 执行完之后这本书长什么样", "",
              "| 代码 | 手数 | 价 | 金额 | 占风险腿 |", "|---|---|---|---|---|"]
        risk = face.get("risk_book_after_cny") or 0.0
        for h in face["holdings_after"]:
            L.append("| %s | %d | %.3f | ¥%s | %.1f%% |"
                     % (h["symbol"], h["lots"], h["price"], format(h["amount_cny"], ",.0f"),
                        100.0 * h["amount_cny"] / risk if risk else 0.0))
        w = face.get("widest_name") or {}
        L += ["",
              "- 风险腿 ¥%s（k=%s）；额度下限 k=%s → %s；现金 ¥%s"
              % (format(risk, ",.0f"),
                 "?" if face.get("k_after") is None else "%.6f" % face["k_after"],
                 "?" if face.get("floor_k") is None else "%.6f" % face["floor_k"],
                 "**在额度内**" if face.get("within_permission") else "**超出额度**",
                 format(face.get("cash_cny") or 0.0, ",.0f")),
              "- 整手取整零头 ¥%s 留在现金腿，不重分配。" % format(face.get("lot_residue_cny") or 0.0, ",.0f"),
              "- 最宽的一只是 **%s**，占风险腿 **%.1f%%**：这个数字看着刺眼，但它是把两只"
              "同一篮子的票合并的结果——独立篮子数 %d → %d（%s），集中度要用篮子数读，不是票数。"
              % (w.get("symbol") or "?", 100.0 * (w.get("share_of_risk_book") or 0.0),
                 (face.get("baskets") or {}).get("n_before") or 0,
                 (face.get("baskets") or {}).get("n_after") or 0,
                 "未变" if (face.get("baskets") or {}).get("n_before") == (face.get("baskets") or {}).get("n_after")
                 else "变了"), ""]

    if face.get("notes"):
        L += ["## 读这张面时要知道的", ""]
        for n in face["notes"]:
            L.append("- %s" % n)
        L.append("")
    if face.get("unpriced_siblings"):
        L += ["- 没有同 bar 收盘价的兄弟票：%s"
              % "；".join("%s（%s）" % (k, v) for k, v in face["unpriced_siblings"].items()), ""]

    L += ["## 不能从这张面读出来的", ""]
    for cav in face.get("caveats") or []:
        L.append("- %s" % cav)
    L += ["", "- 出处：`scripts/etf_book_swap_stack.py`；上游 `%s`（换票面）与票面 permission 块"
          "（同一份裁剪算术，不另算一遍）。" % (face.get("sources") or {}).get("swap_trigger"), ""]
    return "\n".join(L)


def write_out(face):
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(face))
    return OUT_JSON


def run():
    face = load_inputs()
    write_out(face)
    print("verdict=%s k_after=%s floor=%s residue=%s actions=%d"
          % (face["verdict"], face.get("k_after"), face.get("floor_k"),
             face.get("lot_residue_cny"), len(face.get("actions") or [])))
    print("wrote %s" % rel(OUT_JSON))
    return 0


def check():
    if not os.path.exists(OUT_JSON):
        print("CHECK_FAIL: no face at %s" % rel(OUT_JSON))
        return 1
    published = _read_json(OUT_JSON)
    fresh = load_inputs()
    bad = []
    for key in ("verdict", "k_after", "floor_k", "risk_book_after_cny", "lot_residue_cny",
                "overstated_total_cny"):
        if (published or {}).get(key) != fresh.get(key):
            bad.append(key)
    if len(published.get("actions") or []) != len(fresh.get("actions") or []):
        bad.append("actions")
    else:
        for a, b in zip(published["actions"], fresh["actions"]):
            if (a.get("symbol"), a.get("side"), a.get("lots")) != (b.get("symbol"),
                                                                   b.get("side"), b.get("lots")):
                bad.append("action_row")
                break
    if bad:
        print("CHECK_FAIL: %s disagree with a fresh derivation" % ", ".join(bad))
        return 1
    print("CHECK_OK: %s (%s, %d action(s))" % (published.get("verdict"),
                                               rel(OUT_JSON), len(published.get("actions") or [])))
    return 0


def _fixture_ticket():
    return {"nav": 1000000.0, "beta_k": 0.46, "evidence_cutoff": "2026-11-06",
            "permission": {"permitted_k": 0.393073, "ceiling_k": 0.544424,
                           "trim": {"legs": [
                               {"symbol": "A", "price": 2.0, "lots_now": 444,
                                "lots_target": 379, "lots_sell": 65, "sell_cny": 13000.0},
                               {"symbol": "B", "price": 2.0, "lots_now": 400,
                                "lots_target": 364, "lots_sell": 36, "sell_cny": 7200.0},
                           ]}},
            "order": [{"symbol": "A", "price": 2.0, "lots": 444},
                      {"symbol": "B", "price": 2.0, "lots": 400},
                      {"symbol": "C", "price": 1.0, "lots": 800}]}


def selftest():
    ok, total = 0, 0

    def chk(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s" % name)

    t = _fixture_ticket()
    sw = [{"leg_symbol": "A", "sibling_symbol": "S", "verdict": "ACT_ON_THIS_BAR",
           "one_off_gain_cny": 5000.0, "repeatable_gain_cny": 500.0, "index": "NDX"},
          {"leg_symbol": "B", "sibling_symbol": "S", "verdict": "WINDOW_ALWAYS_OPEN",
           "one_off_gain_cny": 3000.0, "repeatable_gain_cny": 900.0, "index": "NDX"}]
    prices = {"S": 1.5}

    face = assess(t, t["permission"], sw, prices, "2026-11-06")
    # A: 379 lots * 200 = 75,800 -> /150 = 505 lots exactly, residue 0
    # B: 364 lots * 200 = 72,800 -> 485 lots = 72,750, residue 50
    chk("sells are sized on the trimmed lots", [r["lots"] for r in face["actions"]
                                                if r["side"] == "SELL"] == [379, 364])
    chk("two legs into one sibling become one buy",
        len([r for r in face["actions"] if r["side"] == "BUY"]) == 1)
    chk("merged buy adds both proceeds",
        [r["lots"] for r in face["actions"] if r["side"] == "BUY"] == [990])
    chk("lot residue is printed, not dropped", face["lot_residue_cny"] == 100.0)
    chk("oversell is caught when two sections touch one leg",
        face["verdict"] == "TWO_SECTIONS_OVERSELL_THE_LEG")
    chk("oversell row counts both sections",
        face["oversell"][0]["as_printed_excess"] == 65)
    chk("repricing marks the swap benefit as overstated",
        round(face["overstated_total_cny"], 2) ==
        round((5500.0 + 3900.0) - (5500.0 * 379 / 444 + 3900.0 * 364 / 400), 2))
    chk("k_after is inside the floor", face["within_permission"] is True)
    chk("baskets are unchanged when two legs share one index",
        face["baskets"]["n_before"] == face["baskets"]["n_after"] == 2)

    # a leg that the sheet holds no lots of must not be sold
    face2 = assess(t, t["permission"], [{"leg_symbol": "Z", "sibling_symbol": "S",
                                         "verdict": "ACT_ON_THIS_BAR"}], prices, "2026-11-06")
    chk("an unknown leg is skipped, not invented", not face2["actions"])
    chk("skipping it is voiced", any("不在本单里" in n for n in face2["notes"]))
    chk("no actionable swap reads as nothing to net", face2["verdict"] == "NOTHING_TO_NET")

    # an unpriced sibling keeps the proceeds as cash rather than buying at an old price
    face3 = assess(t, t["permission"], sw, {}, "2026-11-06")
    chk("an unpriced sibling is not bought", not [r for r in face3["actions"]
                                                  if r["side"] == "BUY"])
    chk("its proceeds land in the residue", face3["lot_residue_cny"] > 0)

    # absent ticket -> cannot verify, never "nothing to do"
    face4 = assess(None, None, sw, prices, "2026-11-06")
    chk("an unreadable sheet cannot be verified", face4["verdict"] == "CANNOT_VERIFY")

    # no trim at all: the ordered size stands
    bare = {"nav": 1000000.0, "beta_k": 0.46, "evidence_cutoff": "2026-11-06",
            "permission": {"permitted_k": 0.39}, "order": [{"symbol": "A", "price": 2.0,
                                                            "lots": 444}]}
    face5 = assess(bare, bare["permission"], sw, prices, "2026-11-06")
    chk("without a trim the ordered lots are sold", [r["lots"] for r in face5["actions"]
                                                     if r["side"] == "SELL"] == [444])
    chk("without a trim nothing is flagged as an oversell", not face5["oversell"])

    # a sibling panel that is not the priced bar must be refused
    px, why = sibling_price("A", "2026-11-07",
                            finder=lambda s: os.path.join(ROOT, "data", "daily", "sz159501.csv"))
    chk("a stale sibling panel is refused", px is None and "ends at" in why)

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="net the permission trim and the swap into one order")
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "selftest"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.check or a.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())