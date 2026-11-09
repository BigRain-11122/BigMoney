"""ETF book -- a sheet you can type, and an account that no longer matches it.

r1467 netted two sections into one order and declared the book it leaves behind. Two things
are still missing, and both only become visible once the post-execution book is written down:

  * the printed rows do not rebuild the declared book. The action list carries the two swap
    sells and the merged buy; the trim table also sells 65 / 62 / 116 / 84 / 118 lots of the
    five legs, and those sells never appear as rows. Type what is printed and the account
    still carries CNY 67,289 of the names the permission refused;
  * once the swap executes, the account no longer matches the sheet at all. The sheet says
    444 lots of 159501; the account holds none of it and 920 lots of 159513. Any next order
    computed against the previous sheet is computed against a book that does not exist.

This face writes the post-execution book down (an append-only position ledger keyed by the
decision bar) and reconciles two ways:

  * `actions + the sheet's own start book` must rebuild `holdings_after`; where it does not,
    the missing rows are named in lots and in CNY;
  * the next order must start from the ledger row for that bar, and the notional that would be
    traded on the wrong base is priced with the target weights held equal, so only the base
    moves (the selection effect is deliberately isolated out).

Usage:
    python scripts/etf_book_positions.py run
    python scripts/etf_book_positions.py --check
    python scripts/etf_book_positions.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_swap_stack as stack_face  # noqa: E402  (one reader of the sheet's order block)

STACK_FACE = os.path.join(ROOT, "results", "etf_book_swap_stack.json")
LEDGER_DIR = os.path.join(ROOT, "results", "etf_book_positions")
LEDGER = os.path.join(LEDGER_DIR, "LEDGER.json")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_positions.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_positions.md")

LOT_SHARES = 100


def _read_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def rel(p):
    if not p:
        return None
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


# --------------------------------------------------------------------------- arithmetic


def apply_actions(starts, actions):
    """The book the printed rows leave behind, from the sheet's own start book.

    A side that is neither BUY nor SELL is not guessed at: it is skipped, and the symbol then
    shows up in the reconciliation as an unexplained difference (which is the honest reading).
    """
    lots = {str(k): int(v) for k, v in (starts or {}).items()}
    for a in actions or []:
        sym = str(a.get("symbol"))
        n = int(a.get("lots") or 0)
        side = a.get("side")
        if side == "BUY":
            lots[sym] = lots.get(sym, 0) + n
        elif side == "SELL":
            lots[sym] = lots.get(sym, 0) - n
        else:
            continue
    return {k: v for k, v in lots.items() if v}


def reconcile(order, actions, holdings_after):
    """Printed rows vs declared book, per symbol, in lots and in CNY.

    Positive `delta_lots` = the printed rows leave more lots than the declared book holds, i.e.
    a sell that the sheet declares but never prints. Negative = a printed buy that the declared
    book does not contain. A symbol with no price is printed with `delta_cny=None` rather than
    silently dropped from the total (an unpriced gap is still a gap).
    """
    starts = {str(r["symbol"]): int(r.get("lots") or 0) for r in order or []}
    prices = {}
    for r in order or []:
        prices[str(r["symbol"])] = float(r.get("price") or 0.0)
    for h in holdings_after or []:
        prices.setdefault(str(h["symbol"]), float(h.get("price") or 0.0))

    printed = apply_actions(starts, actions)
    book = {str(h["symbol"]): int(h.get("lots") or 0) for h in holdings_after or []}

    rows = []
    for sym in sorted(set(printed) | set(book)):
        p = int(printed.get(sym, 0))
        b = int(book.get(sym, 0))
        if p == b:
            continue
        px = prices.get(sym)
        delta = p - b
        rows.append({
            "symbol": sym,
            "sheet_lots": int(starts.get(sym, 0)),
            "printed_lots": p,
            "book_lots": b,
            "delta_lots": delta,
            "price": px,
            "delta_cny": None if not px else round(delta * LOT_SHARES * float(px), 2),
            "reading": ("printed rows leave lots the declared book does not hold "
                        "(a sell the sheet never prints)" if delta > 0 else
                        "printed rows hold fewer lots than the declared book "
                        "(a buy the sheet never prints)"),
        })
    priced = [r["delta_cny"] for r in rows if r["delta_cny"] is not None]
    return rows, round(sum(priced), 2), len(rows) - len(priced)


def target_lots(order, nav):
    """Lot-rounded target per leg from the sheet's own weights.

    Held equal on purpose: this face isolates the BASE effect, not the selection effect.
    """
    out = {}
    for r in order or []:
        sym = str(r["symbol"])
        px = float(r.get("price") or 0.0)
        w = float(r.get("weight") or 0.0)
        if px <= 0 or w <= 0 or not nav:
            continue
        out[sym] = int((w * float(nav)) // (LOT_SHARES * px))
    return out


def base_error(order, ticket_lots, ledger_lots, nav, extra_prices=None):
    """What a next order would type if it started from the sheet instead of the account.

    `from_ticket` / `from_ledger` are the lot actions against the same target. Rows where the
    two agree are omitted; the rest are priced at the sheet's own bar prices.
    """
    tgt = target_lots(order, nav)
    prices = {}
    for r in order or []:
        prices[str(r["symbol"])] = float(r.get("price") or 0.0)
    prices.update({str(k): float(v) for k, v in (extra_prices or {}).items()})

    rows, total = [], 0.0
    for sym in sorted(set(tgt) | set(ticket_lots) | set(ledger_lots) | set(prices)):
        t = int(tgt.get(sym, 0))
        a = t - int(ticket_lots.get(sym, 0))
        b = t - int(ledger_lots.get(sym, 0))
        if a == b:
            continue
        px = prices.get(sym)
        if not px:
            rows.append({"symbol": sym, "target_lots": t, "from_ticket_lots": a,
                         "from_ledger_lots": b, "price": None, "gap_lots": abs(a - b),
                         "gap_cny": None})
            continue
        gap_cny = round(abs(a - b) * LOT_SHARES * float(px), 2)
        total += gap_cny
        rows.append({"symbol": sym, "target_lots": t, "from_ticket_lots": a,
                     "from_ledger_lots": b, "price": float(px),
                     "gap_lots": abs(a - b), "gap_cny": gap_cny})
    return rows, round(total, 2)


# --------------------------------------------------------------------------- ledger


def load_ledger():
    d = _read_json(LEDGER) or {}
    if not isinstance(d, dict):
        d = {}
    d.setdefault("schema", "etf-book-positions/v1")
    d.setdefault("rows", [])
    if not isinstance(d["rows"], list):
        d["rows"] = []
    return d


def _content(row):
    """A row's content without the write stamp, so re-running a bar is a no-op."""
    return json.dumps({k: v for k, v in row.items() if k != "written_ts"},
                      sort_keys=True, ensure_ascii=False)


def upsert_row(ledger, row, stamp):
    """Append-or-replace by bar: one row per decision bar, append-only across bars."""
    rows = ledger["rows"]
    hits = [r for r in rows if r.get("bar") == row.get("bar")]
    if not hits:
        row = dict(row)
        row["written_ts"] = stamp
        rows.append(row)
        rows.sort(key=lambda r: str(r.get("bar") or ""))
        return "added"
    old = hits[0]
    if _content(old) == _content(row):
        return "kept"
    old.update(row)
    old["written_ts"] = stamp
    return "updated"


def start_inventory(ledger, bar):
    """The book a decision on `bar` must start from: the latest written row at or before it.

    No row at all is a refusal, not an empty book -- an empty book would silently order the
    whole target from cash (r1108 有产无读 / r98 未知≠空).
    """
    eligible = [r for r in ledger["rows"] if str(r.get("bar") or "") <= str(bar or "")]
    if not eligible:
        return None
    return sorted(eligible, key=lambda r: str(r.get("bar")))[-1]


# --------------------------------------------------------------------------- face


def assess(ticket, stack, ledger, stamp=None):
    book = stack_face.book_block(ticket)
    order = book.get("order") or []
    nav = float(book.get("nav") or 0.0)
    actions = (stack or {}).get("actions") or []
    after = (stack or {}).get("holdings_after") or []
    asof = (stack or {}).get("asof") or (ticket or {}).get("evidence_cutoff")

    rows, total, unpriced = reconcile(order, actions, after)

    if not ticket or not stack or not after:
        verdict = "CANNOT_VERIFY"
    elif not rows:
        verdict = "PRINTED_ROWS_REBUILD_THE_BOOK"
    elif total > 0:
        verdict = "PRINTED_ROWS_UNDERSELL_THE_BOOK"
    elif total < 0:
        verdict = "PRINTED_ROWS_OVERSELL_THE_BOOK"
    else:
        verdict = "GAPS_NOT_PRICED"

    ledger_action = None
    row = None
    if asof and stack and after and verdict != "CANNOT_VERIFY":
        row = {
            "bar": asof,
            "ticket": (stack or {}).get("ticket"),
            "k": (stack or {}).get("k_after"),
            "risk_book_cny": (stack or {}).get("risk_book_after_cny"),
            "cash_cny": (stack or {}).get("cash_cny"),
            "holdings": [{"symbol": str(h["symbol"]), "lots": int(h["lots"]),
                          "price": float(h.get("price") or 0.0),
                          "amount_cny": float(h.get("amount_cny") or 0.0)} for h in after],
            "actions": [{"side": a.get("side"), "symbol": str(a.get("symbol")),
                         "lots": int(a.get("lots") or 0)} for a in actions],
            "source_face": rel(STACK_FACE),
        }
        ledger_action = upsert_row(ledger, row, stamp) if stamp else "dry"

    # what the next order must start from (the row above, or a refusal)
    base = start_inventory(ledger, asof) if ledger is not None else None
    ticket_lots = {str(r["symbol"]): int(r.get("lots") or 0) for r in order}
    ledger_lots = ({str(h["symbol"]): int(h["lots"]) for h in (base or {}).get("holdings") or []}
                   if base else {})
    extra_prices = {str(h["symbol"]): float(h.get("price") or 0.0) for h in after}
    berr, berr_total = (base_error(order, ticket_lots, ledger_lots, nav, extra_prices)
                        if base else ([], 0.0))

    return {
        "artifact": "etf_book_positions",
        "asof": asof,
        "ticket": (stack or {}).get("ticket"),
        "sources": {"swap_stack": rel(STACK_FACE), "ledger": rel(LEDGER)},
        "verdict": verdict,
        "printed_rows": len(actions),
        "book_rows": len(after),
        "unexplained": rows,
        "unexplained_total_cny": total,
        "unexplained_unpriced_rows": unpriced,
        "ledger_action": ledger_action,
        "ledger_row": row,
        "next_order_base": None if not base else {
            "bar": base.get("bar"),
            "risk_book_cny": base.get("risk_book_cny"),
            "cash_cny": base.get("cash_cny"),
            "holdings": len(base.get("holdings") or []),
        },
        "base_divergence": berr,
        "base_divergence_total_cny": berr_total,
        "caveats": [
            "the reconciliation compares two documents, not two accounts: it says what the "
            "printed rows leave behind relative to the book the same face declares, and it "
            "cannot see whether the broker actually filled those lots",
            "the base divergence holds the target weights of THIS ticket fixed on purpose -- it "
            "isolates the starting-book effect. What the next decision bar selects is a "
            "different question and is not answered here",
            "prices are the sheet's own bar closes; a real execution will move both the share "
            "counts and the cash leg",
        ],
    }


def load_inputs(stamp=None):
    tpath = stack_face.latest_ticket_path()
    ticket = _read_json(tpath)
    stack = _read_json(STACK_FACE)
    ledger = load_ledger()
    face = assess(ticket, stack, ledger, stamp)
    if stack is None:
        face["notes"] = ["没有已发布的净额单面（%s）：打印动作与声明账都对不出来" % rel(STACK_FACE)]
    elif ticket is None:
        face.setdefault("notes", []).append("没有在册的票面：动作的起点账读不出来")
    return face, ledger


def render_md(face):
    L = ["# ETF 复合书 · 打印的单，和账上的书", "",
         "会话 `%s`｜票 `%s`｜上游 `%s`" % (face.get("asof"), face.get("ticket"),
                                          (face.get("sources") or {}).get("swap_stack")), ""]
    v = face.get("verdict")
    head = {
        "PRINTED_ROWS_UNDERSELL_THE_BOOK":
            "**照这张单打字，账上还剩 ¥%s 的票没卖**——不是估值差，是打印出来的动作行"
            "本身没覆盖这张单自己声明的账。"
            % format(face.get("unexplained_total_cny") or 0.0, ",.0f"),
        "PRINTED_ROWS_OVERSELL_THE_BOOK":
            "**打印出来的动作比声明的账买得更多**（¥%s）：账面与纸面在买入方向分叉。"
            % format(abs(face.get("unexplained_total_cny") or 0.0), ",.0f"),
        "PRINTED_ROWS_REBUILD_THE_BOOK":
            "**打印的动作能把声明的账一本本复原**：没有漏印的腿，也没有多印的手数。",
        "GAPS_NOT_PRICED": "**手数对不上，但没有一条腿有当日价**：缺口在这里只印手数，不编金额。",
        "CANNOT_VERIFY": "**这一问答不了**：票面、净额单面或声明账缺一件，不拿缺口当零。",
    }.get(v, v or "?")
    L += [head, ""]

    if face.get("unexplained"):
        L += ["## 打印行漏了哪几笔（手数与钱）", "",
              "| 代码 | 票面起点 | 打印动作之后 | 声明的账 | 差 | 价 | 差多少钱 |",
              "|---|---|---|---|---|---|---|"]
        for r in face["unexplained"]:
            L.append("| %s | %d | %d | %d | **%+d 手** | %s | %s |"
                     % (r["symbol"], r.get("sheet_lots") or 0, r["printed_lots"],
                        r["book_lots"], r["delta_lots"],
                        "%.3f" % r["price"] if r.get("price") else "?",
                        ("**¥%s**" % format(r["delta_cny"], ",.0f"))
                        if r.get("delta_cny") is not None else "无价，不编"))
        L += ["",
              "- 合计 **¥%s**（%d 行没有当日价，未计入金额）。"
              % (format(face.get("unexplained_total_cny") or 0.0, ",.0f"),
                 face.get("unexplained_unpriced_rows") or 0),
              "- 读法：净额单只印了换票的那两笔卖和一笔合并买；额度裁剪表自己那五腿的卖出"
              "（65/62/116/84/118 手）从来没有变成动作行。顺序没错、算术没错，但**打字的人少打五笔**。",
              ""]

    base = face.get("next_order_base")
    if base:
        L += ["## 下一张单从哪本账起算", "",
              "- 已写下的执行后账：bar `%s`｜风险腿 ¥%s｜现金 ¥%s｜持仓 %d 只"
              % (base.get("bar"), format(base.get("risk_book_cny") or 0.0, ",.0f"),
                 format(base.get("cash_cny") or 0.0, ",.0f"), base.get("holdings") or 0), ""]
    elif face.get("verdict") != "CANNOT_VERIFY":
        L += ["## 下一张单从哪本账起算", "",
              "- **没有写下的执行后账**：下一张单只能退回上一张票面起算——那正是两本账分叉的入口。", ""]

    if face.get("base_divergence"):
        L += ["## 把账本改回票面的样子，要再打多少", "",
              "| 代码 | 目标手数 | 从票面起算的动作 | 从账本起算的动作 | 价 | 差多少钱 |",
              "|---|---|---|---|---|---|"]
        for r in face["base_divergence"]:
            fmt = lambda n: ("买 %d" % n) if n > 0 else (("卖 %d" % -n) if n < 0 else "不动")
            L.append("| %s | %d | %s | %s | %s | %s |"
                     % (r["symbol"], r["target_lots"], fmt(r["from_ticket_lots"]),
                        fmt(r["from_ledger_lots"]),
                        "%.3f" % r["price"] if r.get("price") else "?",
                        "**¥%s**" % format(r["gap_cny"], ",.0f") if r.get("gap_cny") else "无价"))
        L += ["",
              "- 合计 **¥%s**：换票一执行，票面与账本说的就不再是同一批票（票面还写着卖出前的两只，"
              "账本里那两只已经清零、换成了合并后的兄弟票）。这个数不是下一张单的大小，而是"
              "**把账本按票面修回去要再打出去的钱**——所以下一张单只能从账本起算。"
              % format(face.get("base_divergence_total_cny") or 0.0, ",.0f"),
              "- 「从票面起算」一列全是「不动」不是巧合：目标权重取自这张票自己，票面当然与自己一致。"
              "这一节量的是底座差，不是选股，也不是下一轮的预测。", ""]

    if face.get("notes"):
        L += ["## 读这张面时要知道的", ""]
        for n in face["notes"]:
            L.append("- %s" % n)
        L.append("")

    L += ["## 不能从这张面读出来的", ""]
    for c in face.get("caveats") or []:
        L.append("- %s" % c)
    L += ["", "- 出处：`scripts/etf_book_positions.py`；执行后账在 `%s`（按决策 bar 一行，"
          "同一 bar 重跑只更新不重复）。" % (face.get("sources") or {}).get("ledger"), ""]
    return "\n".join(L)


def write_out(face, ledger):
    os.makedirs(LEDGER_DIR, exist_ok=True)
    with open(LEDGER, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, ensure_ascii=False, indent=1)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(face))
    return OUT_JSON


def now_stamp():
    import datetime
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def run():
    face, ledger = load_inputs(stamp=now_stamp())
    write_out(face, ledger)
    print("verdict=%s unexplained_cny=%s rows=%d ledger=%s base_gap_cny=%s"
          % (face["verdict"], face.get("unexplained_total_cny"),
             len(face.get("unexplained") or []), face.get("ledger_action"),
             face.get("base_divergence_total_cny")))
    print("wrote %s + %s" % (rel(OUT_JSON), rel(LEDGER)))
    return 0


def check():
    if not os.path.exists(OUT_JSON):
        print("CHECK_FAIL: no face at %s" % rel(OUT_JSON))
        return 1
    published = _read_json(OUT_JSON) or {}
    fresh, _ = load_inputs(stamp=None)
    bad = []
    for key in ("verdict", "asof", "unexplained_total_cny", "base_divergence_total_cny"):
        if published.get(key) != fresh.get(key):
            bad.append(key)
    if len(published.get("unexplained") or []) != len(fresh.get("unexplained") or []):
        bad.append("unexplained_rows")
    else:
        for a, b in zip(published["unexplained"], fresh["unexplained"]):
            if (a.get("symbol"), a.get("delta_lots")) != (b.get("symbol"), b.get("delta_lots")):
                bad.append("unexplained_row")
                break
    # the ledger itself must still carry the row this face was built from
    ledger = load_ledger()
    row = start_inventory(ledger, published.get("asof"))
    if not row:
        bad.append("ledger_row_missing")
    else:
        pub_hold = {str(h["symbol"]): int(h["lots"])
                    for h in (published.get("ledger_row") or {}).get("holdings") or []}
        led_hold = {str(h["symbol"]): int(h["lots"]) for h in row.get("holdings") or []}
        if pub_hold != led_hold:
            bad.append("ledger_row_drift")
    if bad:
        print("CHECK_FAIL: %s disagree with a fresh derivation" % ", ".join(bad))
        return 1
    print("CHECK_OK: %s (%s, %d gap row(s), ledger %d bar(s))"
          % (published.get("verdict"), rel(OUT_JSON),
             len(published.get("unexplained") or []), len(ledger.get("rows") or [])))
    return 0


# --------------------------------------------------------------------------- selftest


def _fixture(order, actions, after):
    return ({"ticket": {"order": order, "nav": 1000000.0}},
            {"asof": "2026-11-06", "ticket": "T.json", "actions": actions,
             "holdings_after": after, "risk_book_after_cny": 392400.9, "cash_cny": 607599.1,
             "k_after": 0.392401})


def selftest():
    ok, total = 0, 0

    def chk(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s" % name)

    order = [{"symbol": "A", "price": 2.0, "lots": 100, "weight": 0.2},
             {"symbol": "B", "price": 1.0, "lots": 200, "weight": 0.2}]
    after = [{"symbol": "A", "lots": 50, "price": 2.0, "amount_cny": 10000.0},
             {"symbol": "B", "lots": 200, "price": 1.0, "amount_cny": 20000.0}]

    # 1. rows that rebuild the declared book
    rows, tot, unp = reconcile(order, [{"side": "SELL", "symbol": "A", "lots": 50}], after)
    chk("a complete action list rebuilds the book", rows == [] and tot == 0.0)

    # 2. an unprinted sell is named in lots and CNY
    rows, tot, unp = reconcile(order, [], after)
    chk("a missing sell is reported", [r["symbol"] for r in rows] == ["A"])
    chk("its lots are sized", rows[0]["delta_lots"] == 50)
    chk("its money is sized", tot == 10000.0)
    chk("it reads as an unprinted sell", "never prints" in rows[0]["reading"])

    # 3. an unprinted buy is the other sign, not folded into the same total
    rows2, tot2, _ = reconcile(order, [{"side": "SELL", "symbol": "A", "lots": 50}],
                               [{"symbol": "A", "lots": 100, "price": 2.0},
                                {"symbol": "B", "lots": 200, "price": 1.0}])
    chk("an unprinted buy is negative", tot2 == -10000.0)
    chk("it reads as a buy", "fewer lots" in rows2[0]["reading"])

    # 4. an unpriced leg stays a row and is excluded from the money total
    rows3, tot3, unp3 = reconcile([{"symbol": "C", "lots": 10}], [],
                                  [{"symbol": "C", "lots": 0}])
    chk("an unpriced gap is still a row", len(rows3) == 1 and unp3 == 1)
    chk("an unpriced gap is not counted as money", tot3 == 0.0)

    # 5. verdicts
    face, _ = (None, None)
    t, s = _fixture(order, [{"side": "SELL", "symbol": "A", "lots": 50}], after)
    led = {"schema": "x", "rows": []}
    f = assess(t, s, led)
    chk("a rebuilding sheet says so", f["verdict"] == "PRINTED_ROWS_REBUILD_THE_BOOK")
    t2, s2 = _fixture(order, [], after)
    f2 = assess(t2, s2, {"schema": "x", "rows": []})
    chk("an under-sold sheet says so", f2["verdict"] == "PRINTED_ROWS_UNDERSELL_THE_BOOK")
    chk("its total is the missing money", f2["unexplained_total_cny"] == 10000.0)
    f3 = assess(t2, None, {"schema": "x", "rows": []})
    chk("a missing stack face cannot be verified", f3["verdict"] == "CANNOT_VERIFY")

    # 6. ledger: one row per bar, re-run is a no-op, a change updates in place
    led = {"schema": "x", "rows": []}
    st = {"asof": "2026-11-06", "ticket": "T", "k_after": 0.39, "risk_book_after_cny": 1.0,
          "cash_cny": 2.0, "holdings_after": after, "actions": []}
    f = assess(t2, st, led, stamp="t1")
    chk("the first run adds a row", f["ledger_action"] == "added" and len(led["rows"]) == 1)
    f = assess(t2, st, led, stamp="t2")
    chk("an identical re-run keeps it", f["ledger_action"] == "kept" and len(led["rows"]) == 1)
    st2 = dict(st)
    st2["holdings_after"] = [{"symbol": "A", "lots": 40, "price": 2.0},
                             {"symbol": "B", "lots": 200, "price": 1.0}]
    f = assess(t2, st2, led, stamp="t3")
    chk("a changed book updates in place", f["ledger_action"] == "updated"
        and len(led["rows"]) == 1 and f["ledger_action"] == "updated")

    # 7. the next order's base is the written row, and a missing row is a refusal
    base = start_inventory(led, "2026-11-06")
    chk("the written row is the base", base is not None and base["bar"] == "2026-11-06")
    chk("an earlier bar cannot borrow a later row", start_inventory(led, "2026-11-05") is None)
    chk("an empty ledger refuses rather than reading as an empty book",
        start_inventory({"rows": []}, "2026-11-06") is None)

    # 8. base divergence: only the base moves, target held equal
    led_rows = [{"symbol": "A", "lots": 0}, {"symbol": "B", "lots": 200}]
    berr, btot = base_error(order, {"A": 100, "B": 200}, {"A": 0, "B": 200}, 1000000.0)
    chk("only the moved symbol is reported", [r["symbol"] for r in berr] == ["A"])
    chk("the ledger base asks for the whole target",
        berr[0]["from_ledger_lots"] == berr[0]["target_lots"])
    chk("the ticket base is short by exactly the gap",
        berr[0]["from_ticket_lots"] + berr[0]["gap_lots"] == berr[0]["from_ledger_lots"])
    chk("the gap is priced at the sheet's own bar price",
        btot == round(berr[0]["gap_lots"] * LOT_SHARES * 2.0, 2))
    berr2, btot2 = base_error(order, {"A": 100}, {"A": 100}, 1000000.0)
    chk("equal bases produce no divergence", berr2 == [] and btot2 == 0.0)

    # 9. an unknown side is never guessed into a buy or a sell
    chk("an unknown side is skipped, not invented",
        apply_actions({"A": 10}, [{"side": "TRIM", "symbol": "A", "lots": 5}]) == {"A": 10})

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="write the executed book down and reconcile it")
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