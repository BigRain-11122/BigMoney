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
import etf_book_sibling_gap as gap_face  # noqa: E402  (one reader of the daily panels)
import etf_book_swap_units as units_face  # noqa: E402  (r1528: the discount's share count)

STACK_FACE = os.path.join(ROOT, "results", "etf_book_swap_stack.json")
LEDGER_DIR = os.path.join(ROOT, "results", "etf_book_positions")
LEDGER = os.path.join(LEDGER_DIR, "LEDGER.json")
UNITS_FACE = os.path.join(ROOT, "results", "etf_book_swap_units.json")
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
    d.setdefault("restatements", [])
    if not isinstance(d["restatements"], list):
        d["restatements"] = []
    return d


def _content(row):
    """A row's content without the write stamp, so re-running a bar is a no-op."""
    return json.dumps({k: v for k, v in row.items() if k != "written_ts"},
                      sort_keys=True, ensure_ascii=False)


def _book_snapshot(row):
    """The numbers a reader would quote for this bar, in the order they would quote them."""
    lots = {}
    for h in (row.get("holdings") or []):
        try:
            lots[str(h.get("symbol"))] = int(h.get("lots") or 0)
        except (TypeError, ValueError):
            continue
    return {"k": row.get("k"),
            "risk_book_cny": row.get("risk_book_cny"),
            "cash_cny": row.get("cash_cny"),
            "lots": dict(sorted(lots.items()))}


def _restatement(old, row, stamp):
    """r1474: replacing a bar's row is a restatement, and a restatement nobody prints is
    not a disclosure (E281/r1371 lineage: the reader only holds the printed sheet)."""
    before, after = _book_snapshot(old), _book_snapshot(row)
    delta, lots_changed = {}, []
    for key in ("k", "risk_book_cny", "cash_cny"):
        b, a = before.get(key), after.get(key)
        if b is None or a is None:
            delta[key] = None
        else:
            delta[key] = round(float(a) - float(b), 6)
    for sym in sorted(set(before["lots"]) | set(after["lots"])):
        b, a = before["lots"].get(sym), after["lots"].get(sym)
        if b != a:
            lots_changed.append({"symbol": sym, "before": b, "after": a})
    return {"bar": old.get("bar"),
            "previous_written_ts": old.get("written_ts"),
            "written_ts": stamp,
            "before": before,
            "after": after,
            "delta": delta,
            "lots_changed": lots_changed}


def upsert_row(ledger, row, stamp):
    """Append-or-replace by bar: one row per decision bar, append-only across bars.

    A bar that is already written is a settled bar. Replacing it with the same numbers is a
    no-op; replacing it with different numbers is a restatement and is recorded, because the
    alternative is that the printed sheet quietly changes under a reader who already acted
    on it. A restatement is only recorded for a real change -- logging every re-run would
    bury the one that matters.
    """
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
    ledger.setdefault("restatements", []).append(_restatement(old, row, stamp))
    # r1518: replace the row whole instead of merging field by field. Merging let a row
    # keep the other fact's keys after a bar changed kind: a mark-only valuation row
    # superseded by the executed book still carried `nav_cny`/`from_bar`, and the
    # reverse kept a `k`/`ticket` pair that no longer described the book on disk.
    new = dict(row)
    new["written_ts"] = stamp
    rows[rows.index(old)] = new
    rows.sort(key=lambda r: str(r.get("bar") or ""))
    return "updated"


def restatement_report(ledger, bar=None, page_md=None):
    """What a reader of this bar must be told: recorded restatements, and what the trail
    cannot see.

    Three separate facts, never merged:
      a. restatements this ledger recorded (each with both numbers);
      b. whether the trail reaches back far enough to cover this bar at all -- it starts
         with this version, so an earlier rewrite is *not* evidence of no rewrite;
      c. the CEO page's own account block for the same bar, if it says anything, because a
         number printed elsewhere and left to disagree is the reader's problem, not ours.
    """
    recs = [r for r in (ledger or {}).get("restatements") or []
            if bar is None or r.get("bar") == bar]
    out = {"bar": bar, "count": len(recs), "records": recs,
           "trail_starts_with_this_version": True,
           "trail_covers_bar": True if recs else None}
    page = None
    if page_md:
        page = _page_account_block(page_md, bar)
    out["page_block"] = page
    if page and page.get("lots"):
        ledger_lots = {}
        latest = None
        for r in (ledger or {}).get("rows") or []:
            if r.get("bar") == bar:
                latest = r
        if latest is not None:
            ledger_lots = _book_snapshot(latest)["lots"]
        diff = []
        for sym in sorted(set(page["lots"]) | set(ledger_lots)):
            a, b = page["lots"].get(sym), ledger_lots.get(sym)
            if a != b:
                diff.append({"symbol": sym, "page_lots": a, "ledger_lots": b})
        out["page_vs_ledger_lots"] = diff
        ledger_cash = _book_snapshot(latest)["cash_cny"] if latest is not None else None
        page_cash = page.get("cash_cny")
        cash_gap = None
        if page_cash is not None and ledger_cash is not None:
            cash_gap = round(float(page_cash) - float(ledger_cash), 2)
        out["page_vs_ledger_cash"] = {"page": page_cash, "ledger": ledger_cash,
                                      "page_minus_ledger": cash_gap}
        out["page_vs_ledger_agree"] = ((not diff) and cash_gap == 0.0
                                      if cash_gap is not None else None)
    return out


def _read_json_page():
    """Today's CEO page text, or nothing. Read-only: bm-a is the page's single writer."""
    import glob
    hits = sorted(glob.glob(os.path.join(ROOT, "docs", "live_book", "LIVE-BOOK-*.md")))
    if not hits:
        return None
    try:
        with open(hits[-1], encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _page_account_block(md_text, bar):
    """Read the CEO page's own 'what the account holds' block for `bar`, or nothing.

    Read-only and deliberately narrow: this never edits the page (bm-a is its single
    writer), it only lets this face say whether the two published numbers agree.
    """
    import re
    if not md_text:
        return None
    idx = md_text.find("账上现在拿的是什么")
    if idx < 0:
        return None
    head = md_text[idx:idx + 400]
    m = re.search(r"（(\d{4}-\d{2}-\d{2})\s*收盘）", head)
    if not m or (bar and m.group(1) != bar):
        return {"bar": m.group(1) if m else None, "same_bar": False}
    lots, cash = {}, None
    mc = re.search(r"现金\s*￥([\d,]+)", head)
    if mc:
        cash = float(mc.group(1).replace(",", ""))
    seg = md_text[idx:idx + 2000]
    for mm in re.finditer(r"^\|\s*(\d{6})\s*\|\s*(\d+)\s*\|", seg, re.M):
        lots[mm.group(1)] = int(mm.group(2))
    return {"bar": m.group(1), "same_bar": True, "lots": lots, "cash_cny": cash}


def latest_execution_row(ledger):
    """The most recent row that records an actual book; valuations are marks of that book."""
    rows = [r for r in ledger["rows"] if str(r.get("kind") or "execution") == "execution"]
    if not rows:
        return None
    return sorted(rows, key=lambda r: str(r.get("bar") or ""))[-1]


def start_inventory(ledger, bar):
    """The book a decision on `bar` must start from: the latest written row at or before it.

    No row at all is a refusal, not an empty book -- an empty book would silently order the
    whole target from cash (r1108 有产无读 / r98 未知≠空).
    """
    eligible = [r for r in ledger["rows"] if str(r.get("bar") or "") <= str(bar or "")]
    if not eligible:
        return None
    # r1518: if one bar somehow holds both kinds, the executed book is the account at that
    # close -- the valuation row there was that same book marked forward before the trade
    # existed, so it must not win a tie.
    return sorted(eligible, key=lambda r: (str(r.get("bar") or ""),
                                           1 if str(r.get("kind") or "execution")
                                           != "valuation" else 0))[-1]


def previous_row(ledger, bar):
    """The account a trade on `bar` starts from: the newest row strictly BEFORE it."""
    eligible = [r for r in (ledger or {}).get("rows") or []
                if str(r.get("bar") or "") < str(bar or "")]
    if not eligible:
        return None
    return sorted(eligible, key=lambda r: (str(r.get("bar") or ""),
                                           1 if str(r.get("kind") or "execution")
                                           != "valuation" else 0))[-1]


def account_row_for(ledger, bar):
    """r1563: the newest row up to `bar` whose own actions carry the previous row onto it.

    A decision bar always lands a row, and that row is the sheet's TARGET. When the sheet
    prints no trades -- because its swap/trim netting had nothing to do on this bar while the
    sleeve was replaced anyway -- the row is a declaration wearing the account's clothes. The
    next subtraction then runs target-minus-target and prints "nothing to do" on a bar that
    needs nine trades (2026-11-11: 4 out, 5 in, one lot change, 667,376 CNY of turnover).
    Walking back to the newest row a trade list can actually reach is what keeps the next
    subtraction an account question instead of an identity (r1562 measured the mismatch;
    this names the row the reader should subtract from).
    """
    rows = [r for r in (ledger or {}).get("rows") or []
            if str(r.get("bar") or "") <= str(bar or "")
            and str(r.get("kind") or "") != "valuation"]
    rows.sort(key=lambda r: str(r.get("bar") or ""))
    for i in range(len(rows) - 1, -1, -1):
        r = rows[i]
        if i == 0:
            return r
        prev = rows[i - 1]
        start = {str(h["symbol"]): int(h.get("lots") or 0)
                 for h in prev.get("holdings") or [] if h.get("symbol")}
        got = {str(h["symbol"]): int(h.get("lots") or 0)
               for h in r.get("holdings") or [] if h.get("symbol")}
        if not (r.get("actions") or []):
            # printed no trades: it is the account only if the book did not move
            if start == got:
                return r
            continue
        # printed trades: an account, even when the list does not close to the lot
        # (that mismatch is what book_transition measures; skipping it would walk back
        # past a bar somebody did trade on)
        return r
    return None


def book_transition(ledger, bar, actions, after):
    """r1562: can the row written for `bar` explain the book it claims?

    ``holdings_after`` is the TARGET this sheet orders. The account that target lands on is
    the previous row plus the actions the sheet prints. On 2026-11-11 the 20-bar rebalance
    replaced the whole sleeve (4 names out, 5 in, 153% turnover) and printed no trades, so
    the ledger row simply declared the new book. The next sheet then subtracted that target
    from itself and told the operator "already on target, nothing to do" on a bar that
    needed nine trades -- an identity that is true by construction and says nothing.

    Measuring the difference is the only honest way to say which case it is: EXPLAINED when
    the actions carry the account onto the target, UNEXPLAINED_* when they do not (and the
    row must not be read as an execution).
    """
    prev = previous_row(ledger, bar)
    target = {str(h["symbol"]): int(h.get("lots") or 0) for h in after or [] if h.get("symbol")}
    out = {"bar": bar, "from_bar": (prev or {}).get("bar"), "actions": len(actions or []),
           "status": None, "vanished": [], "appeared": [], "lots_changed": [],
           "cny_moved": None}
    if prev is None:
        out["status"] = "FIRST_ROW"
        return out
    start = {str(h["symbol"]): int(h.get("lots") or 0)
             for h in prev.get("holdings") or [] if h.get("symbol")}
    expected = apply_actions(start, actions or [])
    expected = {k: v for k, v in expected.items() if v}
    prices = {str(h["symbol"]): float(h.get("price") or 0.0) for h in after or []
              if h.get("symbol")}
    for h in prev.get("holdings") or []:
        prices.setdefault(str(h["symbol"]), float(h.get("price") or 0.0))
    out["vanished"] = sorted(s for s in expected if s not in target)
    out["appeared"] = sorted(s for s in target if s not in expected)
    out["lots_changed"] = [{"symbol": s, "expected_lots": expected[s],
                            "target_lots": target[s]}
                           for s in sorted(set(expected) & set(target))
                           if expected[s] != target[s]]
    moved = 0.0
    for s in set(expected) | set(target):
        d = int(target.get(s, 0)) - int(expected.get(s, 0))
        if d:
            moved += abs(d) * LOT_SHARES * float(prices.get(s) or 0.0)
    out["cny_moved"] = round(moved, 2)
    if not (out["vanished"] or out["appeared"] or out["lots_changed"]):
        out["status"] = "EXPLAINED"
    elif not (actions or []):
        out["status"] = "UNEXPLAINED_TARGET_WITHOUT_TRADES"
    else:
        out["status"] = "UNEXPLAINED_LOTS"
    return out


def account_base_after_accrual(ledger, base, accrual):
    """r1512: the account as it stands once the accrual has written its rows.

    `assess` used to resolve `next_order_base` BEFORE the accrual ran, so the very face that
    wrote the 11-10 valuation row still told the next sheet to start from the 11-09 execution
    row (risk leg 392,587 while 400,023 sat on disk). A write its own producer never reads is
    not a write. Returns (row, source); `source` says which kind of row the base is.
    """
    if not base:
        return None, None
    last = (accrual or {}).get("last") or {}
    bar = last.get("bar") if isinstance(last, dict) else None
    if ledger is None or not bar:
        return base, "execution_row"
    nb = start_inventory(ledger, bar)
    if not nb or str(nb.get("bar") or "") < str(base.get("bar") or ""):
        return base, "execution_row"
    return nb, ("accrued_valuation"
                if str(nb.get("kind") or "execution") == "valuation" else "execution_row")


def pin_episode_ticket(stack, latest_path):
    """r1512: the sheet that belongs to the swap episode, and whether it is the newest one.

    `latest.json` moves every time a new sheet is priced; the swap face only refreshes when a
    swap exists. On a quiet bar the two point at different decisions, and reconciling them
    printed a −6,396 "oversell" that never happened. Returns (path, pinned, same).
    """
    pinned = None
    if stack and stack.get("ticket") and latest_path:
        cand = os.path.join(os.path.dirname(latest_path), os.path.basename(str(stack["ticket"])))
        if os.path.exists(cand):
            pinned = cand
    path = pinned or latest_path
    same = bool(pinned and latest_path and os.path.abspath(pinned) == os.path.abspath(latest_path))
    return path, pinned is not None, same


# --------------------------------------------------------------------------- accrual
#
# r1469: a ledger row is written only when a swap executes. Between two decision bars the
# book earns and loses money nobody records -- so the next order starts from the last
# execution, not from the account as it stands. Two things move between bars and only two:
# the marks of the holdings, and the cash leg (the sheet says cash sits in 1-day repo, so a
# Friday-to-Monday step earns three calendar days). Both are accrued here, one row per bar.


def rf_step(rate_pct, gap_days):
    """One bar's cash return as a fraction, from the rate quoted on the PRIOR bar.

    Same arithmetic as `etf_phase_beta_window.repo_daily_cash` (1-day repo pays calendar
    days). An absent or non-finite quote returns None and accrues nothing -- it is counted by
    the caller, never charged as a guessed rate.
    """
    try:
        r = float(rate_pct)
    except (TypeError, ValueError):
        return None
    if r != r or not (r > 0):
        return None
    return r / 100.0 * max(int(gap_days), 1) / 365.0


def price_steps(holdings, closes_by_symbol, start_bar, end_bar=None, calendar_gap=None):
    """Bar-by-bar marks for a fixed lot book, from the first panel day after `start_bar`.

    A symbol with no print on a given day carries its last known close and is named in
    `stale` -- a suspension is not a zero, and a missing panel is not a flat price.
    """
    syms = [str(h["symbol"]) for h in holdings or []]
    series = {s: (closes_by_symbol or {}).get(s) or {} for s in syms}
    all_days = sorted({d for s in syms for d in series[s]})
    days = [d for d in all_days if str(d) > str(start_bar)
            and (end_bar is None or str(d) <= str(end_bar))]
    last = {}
    for h in holdings or []:
        sym = str(h["symbol"])
        px = float(h.get("price") or 0.0)
        before = [d for d in series[sym] if str(d) <= str(start_bar)]
        if before:
            px = float(series[sym][max(before)])
        if px > 0:
            last[sym] = px

    out, prev_day = [], str(start_bar)
    for d in days:
        marks, stale = {}, []
        for sym in syms:
            px = series[sym].get(d)
            if px is None:
                stale.append(sym)
            else:
                last[sym] = float(px)
                px = float(px)
            marks[sym] = float(last.get(sym) or 0.0)
        gap = None
        if calendar_gap is not None:
            gap = calendar_gap(prev_day, d)
        out.append({"bar": d, "marks": marks, "stale": stale, "gap_days": gap})
        prev_day = d
    return out


def priced_boundary(closes_by_symbol, holdings):
    """The last bar this book can be VALUED on, plus what stops it after that.

    A bar counts only when every held leg printed a close on it. A suspension is not a zero and
    a missing panel is not a flat price: the accrual walks the union of *any* leg printing, so
    one leg still trading would otherwise carry a stale mark for the halted one and the row
    would read as a valuation. The book therefore stops at the last fully priced bar and the
    legs missing past it are named.
    """
    syms = sorted({str(h["symbol"]) for h in holdings or []})
    if not syms:
        return None, {}
    series = {s: (closes_by_symbol or {}).get(s) or {} for s in syms}
    days = sorted({d for s in syms for d in series[s]})
    last_full, blockers = None, {}
    for d in days:
        miss = [s for s in syms if d not in series[s]]
        if miss:
            if last_full is not None and str(d) > str(last_full):
                blockers[str(d)] = miss
            continue
        if last_full is None or str(d) > str(last_full):
            last_full = d
    return last_full, blockers


def accrue_rows(row, steps, rates=None):
    """Valuation rows from an execution (or prior valuation) row and a list of bar steps.

    `rates` maps a bar to the annualised cash yield quoted on the PREVIOUS bar; a bar with no
    quote accrues nothing and is counted in `rf_missing`.
    """
    holdings = [{"symbol": str(h["symbol"]), "lots": int(h.get("lots") or 0)}
                for h in (row.get("holdings") or [])]
    cash = float(row.get("cash_cny") or 0.0)
    opening = row.get("nav_cny")
    if opening is None and row.get("risk_book_cny") is not None:
        opening = float(row.get("risk_book_cny") or 0.0) + cash
    prev_nav = float(opening) if opening else None
    first_nav = prev_nav
    out, rf_missing = [], 0
    for st in steps or []:
        risk = sum(int(h["lots"]) * LOT_SHARES * float((st["marks"] or {}).get(h["symbol"]) or 0.0)
                   for h in holdings)
        step = rf_step((rates or {}).get(st["bar"]), st.get("gap_days") or 1)
        if step is None:
            rf_missing += 1
            step = 0.0
        cash = cash * (1.0 + step)
        nav = risk + cash
        ret = (nav / prev_nav - 1.0) if prev_nav else None
        out.append({
            "bar": st["bar"],
            "kind": "valuation",
            "from_bar": str(row.get("bar")),
            "holdings": [{"symbol": h["symbol"], "lots": h["lots"],
                          "price": float((st["marks"] or {}).get(h["symbol"]) or 0.0),
                          "amount_cny": round(h["lots"] * LOT_SHARES
                                              * float((st["marks"] or {}).get(h["symbol"]) or 0.0), 2)}
                         for h in holdings],
            "risk_book_cny": round(risk, 2),
            "cash_cny": round(cash, 2),
            "nav_cny": round(nav, 2),
            "ret": None if ret is None else round(ret, 8),
            "cum_ret": None if not first_nav else round(nav / first_nav - 1.0, 8),
            "rf_step": round(step, 10),
            "stale_price_symbols": list(st.get("stale") or []),
            "source_face": row.get("source_face"),
        })
        prev_nav = nav
    return out, rf_missing


def _calendar_gap(a, b):
    import datetime
    try:
        da = datetime.date.fromisoformat(str(a)[:10])
        db = datetime.date.fromisoformat(str(b)[:10])
    except ValueError:
        return 1
    return max((db - da).days, 1)


def accrue(ledger, stamp=None, upto=None, closes_by_symbol=None, rates=None):
    """Advance the written book to the newest panel bar; idempotent per bar."""
    base = latest_execution_row(ledger)
    if not base:
        return {"status": "NO_BOOK", "rows": 0, "written": 0}
    if closes_by_symbol is None or rates is None:
        return {"status": "NO_INPUTS", "rows": 0, "written": 0}
    steps = price_steps(base.get("holdings") or [], closes_by_symbol, base.get("bar"),
                        upto, _calendar_gap)
    # r1518: a bar that carries an execution is already the account at that close (the sheet
    # prices the executed book on its own bar). Writing a valuation over it replaced the
    # trade with a mark of the book that existed before the trade -- two facts, one key, the
    # last writer won. The execution always wins; the skipped bars are named, not dropped.
    exec_bars = {str(r.get("bar")) for r in ledger.get("rows") or []
                 if str(r.get("kind") or "execution") == "execution"}
    skipped = [st["bar"] for st in steps if str(st["bar"]) in exec_bars]
    steps = [st for st in steps if str(st["bar"]) not in exec_bars]
    rows, rf_missing = accrue_rows(base, steps, rates)
    counts = {"added": 0, "kept": 0, "updated": 0}
    if stamp:
        for r in rows:
            counts[upsert_row(ledger, r, stamp)] += 1
    return {
        "status": "NO_NEW_BAR" if not rows else "ACCRUED",
        "from_bar": base.get("bar"),
        "rows": len(rows),
        "written": counts["added"] + counts["updated"],
        "kept": counts["kept"],
        "skipped_execution_bars": skipped,
        "rf_missing_bars": rf_missing,
        "last": rows[-1] if rows else None,
        "rows_detail": [{k: r[k] for k in ("bar", "risk_book_cny", "cash_cny", "nav_cny",
                                           "ret", "cum_ret", "rf_step")} for r in rows],
    }


def load_panel_and_rates(holdings, panel_finder=None, panel_loader=None,
                         rate_loader=None):
    """Closes per symbol from the board's own daily files, plus the repo quotes."""
    closes, missing = {}, []
    for h in holdings or []:
        sym = str(h["symbol"])
        try:
            path = (panel_finder or gap_face.find_daily)(sym)
            closes[sym] = (panel_loader or gap_face.load_close)(path) if path else {}
        except (OSError, ValueError):
            closes[sym] = {}
        if not closes[sym]:
            missing.append(sym)
    try:
        rs = (rate_loader or _default_rate_loader)()
        rates = {str(i)[:10]: float(v) for i, v in rs.items()} if rs is not None else {}
    except (OSError, ValueError, KeyError):
        rates = {}
    return closes, rates, missing


def _default_rate_loader():
    import etf_phase_beta_window as bw
    return bw.load_repo_rates()


def _execution_order_book_tail(path=None):
    """The ticket generator's own normalised book (nav ~1.0, k as a fraction of NAV).

    It is a strategy account, not the executed account: it carries the un-trimmed exposure.
    Printed side by side, the two say how far the sheet's base is from the book's.
    """
    p = path or os.path.join(ROOT, "results", "etf_book_order", "ledger.jsonl")
    if not os.path.exists(p):
        return None
    last = None
    try:
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    last = line
    except OSError:
        return None
    if not last:
        return None
    try:
        row = json.loads(last)
    except ValueError:
        return None
    return {"source": rel(p), "bar": row.get("date"),
            "nav_units": row.get("nav"), "k": row.get("k"), "rf": row.get("rf")}


REPLAY_DAYS = 20


def replay(base_row, closes_by_symbol, rates, window=REPLAY_DAYS):
    """Run the same accrual engine BACKWARDS over the ledger row's own lots.

    It is a check of the machinery, not a book's P&L: the account only started on the
    execution bar, so what this answers is "if these lots had been held for the last N bars,
    this engine would have marked them like this". The identity it must satisfy is the useful
    part -- the final mark-to-market legs must equal the amount the ledger row already carries,
    because it is the same lots at the same closes.
    """
    holdings = [{"symbol": str(h["symbol"]), "lots": int(h.get("lots") or 0)}
                for h in (base_row.get("holdings") or [])]
    if not holdings or not base_row.get("bar"):
        return None
    days = sorted({d for s in (closes_by_symbol or {}).values() if isinstance(s, dict)
                   for d in s})
    days = [d for d in days if str(d) <= str(base_row.get("bar"))]
    if len(days) < 2:
        return None
    start = days[-min(window + 1, len(days))]
    steps = price_steps(holdings, closes_by_symbol, start, base_row.get("bar"), _calendar_gap)
    if not steps:
        return None
    rows, rf_missing = accrue_rows(
        {"bar": start, "holdings": holdings, "cash_cny": float(base_row.get("cash_cny") or 0.0),
         "risk_book_cny": None, "source_face": base_row.get("source_face")}, steps, rates)
    last = rows[-1]
    identity_delta = round(last["risk_book_cny"] - float(base_row.get("risk_book_cny") or 0.0), 2)
    # r1483 (T29): the identity only means something when the execution bar itself is priced.
    # With a leg unprinted on that bar the replay can only mark to an older day, and the gap it
    # prints is the distance between the fill price and that older close -- not an engine error.
    bar = str(base_row.get("bar"))
    missing_on_bar = [h["symbol"] for h in holdings
                      if not ((closes_by_symbol or {}).get(h["symbol"]) or {}).get(bar)]
    priced = not missing_on_bar
    priced_days = [d for d in days
                   if all(d in ((closes_by_symbol or {}).get(h["symbol"]) or {})
                          for h in holdings)]
    return {
        "start_bar": start,
        "bars": len(rows),
        # no cum_ret here on purpose: the opening nav of this replay is unknown (the cash leg
        # is the execution-day cash), so a cumulative return would be a fabricated number
        "legs_first_bar": rows[0]["risk_book_cny"],
        "legs_last_bar": last["risk_book_cny"],
        "legs_ret": round(last["risk_book_cny"] / rows[0]["risk_book_cny"] - 1.0, 8),
        "cash_interest_cny": round(last["cash_cny"] - float(base_row.get("cash_cny") or 0.0), 2),
        "identity_delta_cny": identity_delta,
        "identity_status": "PRICED_BAR" if priced else "UNPRICED_BAR",
        "identity_holds": (abs(identity_delta) <= 0.01) if priced else None,
        "base_bar_missing_closes": missing_on_bar,
        "base_bar_last_priced_day": priced_days[-1] if priced_days else None,
        "rf_missing_bars": rf_missing,
        "stale_bars": sum(1 for s in steps if s.get("stale")),
    }


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
    transition = None
    if asof and stack and after and verdict != "CANNOT_VERIFY":
        row = {
            "bar": asof,
            "kind": "execution",
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
        transition = (book_transition(ledger, asof, actions, after)
                      if ledger is not None else None)

    # r1563: which row may the next face subtract from. `ledger_row` above is the book this
    # sheet's target lands on; it is only an ACCOUNT when the sheet's own trade list carries
    # the previous row onto it. Publish the row a reader should start from, and say which one
    # it is -- a target wearing the account's clothes makes the next subtraction an identity.
    account_row = None
    _acct = (account_row_for(ledger, asof) if (ledger is not None and asof) else None)
    if _acct or row:
        _src = _acct or row
        declared = bool(transition) and str(transition.get("status") or "").startswith(
            "UNEXPLAINED")
        account_row = {
            "bar": _src.get("bar"),
            "kind": str(_src.get("kind") or "execution"),
            "source": "book_before_declaration" if declared else "ledger_row",
            "risk_book_cny": _src.get("risk_book_cny"),
            "cash_cny": _src.get("cash_cny"),
            "holdings": [{"symbol": str(h["symbol"]), "lots": int(h.get("lots") or 0),
                          "price": float(h.get("price") or 0.0),
                          "amount_cny": float(h.get("amount_cny") or 0.0)}
                         for h in _src.get("holdings") or [] if h.get("symbol")],
            "actions": _src.get("actions") or [],
        }

    # what the next order must start from (the row above, or a refusal)
    base = start_inventory(ledger, asof) if ledger is not None else None
    # r1521: the sheet's own instruction is not its entry table -- the swap line rewrites it
    # before anything is sent (r1467), and `after` is the book that executing the sheet leaves
    # behind. Comparing the account against the entry table charged the operator 313,763 CNY
    # to undo the swap the same sheet had just ordered, on a page whose r1516 delta (fixed in
    # the same round) already read 0. Two sections of one sheet cannot disagree about which
    # book exists.
    entry_lots = {str(r["symbol"]): int(r.get("lots") or 0) for r in order}
    ticket_lots = ({str(h["symbol"]): int(h["lots"]) for h in after} if after else entry_lots)
    base_source = "swap_stack.holdings_after" if (after and ticket_lots != entry_lots) else "entry_sheet"
    ledger_lots = ({str(h["symbol"]): int(h["lots"]) for h in (base or {}).get("holdings") or []}
                   if base else {})
    extra_prices = {str(h["symbol"]): float(h.get("price") or 0.0) for h in after}
    berr, berr_total = (base_error(order, ticket_lots, ledger_lots, nav, extra_prices)
                        if base else ([], 0.0))

    # r1469: between execution bars the book earns and loses money nobody records. Advance the
    # written book one row per bar (marks + 1-day repo on the cash leg), so the next order can
    # start from the account as it stands rather than from the last execution.
    accrual = {"status": "NO_BOOK"}
    replay_row = None
    settlement = None
    if base:
        syms = sorted({str(h["symbol"]) for h in (base.get("holdings") or [])}
                      | {str(h["symbol"]) for h in (row or {}).get("holdings") or []})
        closes, rates, panel_missing = load_panel_and_rates([{"symbol": s} for s in syms])
        held = (row or {}).get("holdings") or base.get("holdings") or []
        boundary, blockers = priced_boundary(closes, held)
        bar = str((row or {}).get("bar") or base.get("bar"))
        missing_on_bar = [h["symbol"] for h in held
                          if not ((closes.get(str(h["symbol"])) or {}).get(bar))]
        priced = not missing_on_bar
        settlement = {
            "bar": bar,
            "priced": priced,
            "last_fully_priced_bar": boundary,
            "missing_closes_on_bar": missing_on_bar,
            "blocked_bars_after_boundary": blockers,
            "ledger_bars_past_boundary": [
                {"bar": str(r.get("bar")), "kind": r.get("kind") or "execution"}
                for r in (ledger or {}).get("rows") or []
                if str(r.get("bar")) > str(boundary or bar)],
            "reading": ("every held leg printed a close on this bar"
                        if priced else
                        "this bar has no close for some held leg; the book records the "
                        "execution here but records no valuation past the last priced bar"),
        }
        if not priced or boundary is None:
            # the book has no valued starting point on this bar: a later fully priced day
            # would make the first row's return a fill-to-close gap wearing a daily number
            accrual = {"status": "NO_PRICED_BAR", "rows": 0, "written": 0,
                       "from_bar": base.get("bar")}
        else:
            accrual = accrue(ledger, stamp=stamp, upto=boundary,
                             closes_by_symbol=closes, rates=rates)
        accrual["panel_missing_symbols"] = panel_missing
        accrual["repo_quotes"] = len(rates)
        accrual["rate_latest_bar"] = max(rates) if rates else None
        accrual["rate_latest"] = rates[max(rates)] if rates else None
        accrual["valued_upto_bar"] = boundary
        replay_row = replay(base, closes, rates) if closes else None

    account_base, account_base_source = account_base_after_accrual(ledger, base, accrual)

    # r1564: how did the bar the next sheet starts from get written? On 2026-11-11 the sleeve
    # was replaced (4 out, 5 in, one lot change, 667,376 CNY) with zero printed action rows, so
    # that row is a TARGET somebody typed, not a fill. The page already said so in the
    # bar-to-bar section and then called the same row an 执行行 two sections lower -- the reader
    # cannot hold both. `arrival` is the one word both sections read.
    arrival = None
    if account_base:
        _ab_bar = str(account_base.get("bar") or "")
        _tr_bar = str((transition or {}).get("bar") or "")
        _tr_status = str((transition or {}).get("status") or "")
        if transition and _tr_bar == _ab_bar:
            if _tr_status == "UNEXPLAINED_TARGET_WITHOUT_TRADES":
                arrival = "declared"
            elif _tr_status == "EXPLAINED":
                arrival = "traded"
        if arrival is None and (account_base.get("actions") or []):
            arrival = "traded"

    # the ticket side keeps its own normalised engine book; the two must not be conflated
    eng = _execution_order_book_tail()
    eng_gap = None
    if eng and (stack or {}).get("k_after") is not None and eng.get("k") is not None:
        total_nav = (float((stack or {}).get("risk_book_after_cny") or 0.0)
                     + float((stack or {}).get("cash_cny") or 0.0))
        gap_k = float(eng["k"]) - float((stack or {}).get("k_after"))
        eng_gap = {"book_k": (stack or {}).get("k_after"), "engine_k": eng.get("k"),
                   "book_nav_cny": round(total_nav, 2),
                   "k_gap": round(gap_k, 6),
                   "notional_gap_cny": round(gap_k * total_nav, 2) if total_nav else None}

    out = {
        "artifact": "etf_book_positions",
        "asof": asof,
        # r1514: `asof` is the episode/ticket bar, but the ledger is re-valued every session
        # between execution bars (r1469), so the account statement's own date is the newest
        # written row. Two dates, two facts: the page compared its price day against `asof`
        # and printed "两个日子对不上" while the block right below it was valued on the page's
        # own day -- a warning the face itself had already answered.
        "ledger_bar": (account_base or {}).get("bar"),
        "ticket_bar": asof,
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
        # r1562: the row above is the book this sheet's target lands on; this block says
        # whether the sheet's own trade list carries the account there, or whether the row
        # is a declaration with nothing behind it (see book_transition).
        "transition": transition,
        # r1563: the row the next face may subtract from (see account_row_for).
        "account_row": account_row,
        "next_order_base": None if not account_base else {
            "bar": account_base.get("bar"),
            "kind": str(account_base.get("kind") or "execution"),
            # r1564: `kind` is the row type; `arrival` says how the book got there. A declared
            # target must not be sold to the next sheet as an execution.
            "arrival": arrival,
            "arrival_actions": (len((transition or {}).get("actions") or [])
                                if arrival == "declared" else None),
            "source": account_base_source,
            "risk_book_cny": account_base.get("risk_book_cny"),
            "cash_cny": account_base.get("cash_cny"),
            "holdings": len(account_base.get("holdings") or []),
            "superseded_execution_bar": (base or {}).get("bar"),
        },
        "base_divergence": berr,
        "base_divergence_total_cny": berr_total,
        "base_source": base_source,
        "entry_sheet_lots": entry_lots,
        "accrual": accrual,
        "accrual_rows": accrual.get("rows_detail") or [],
        "settlement": settlement,
        "replay": replay_row,
        "engine_book": {"tail": eng, "divergence": eng_gap},
        "restatements": restatement_report(ledger,
                                           (account_base or {}).get("bar") or asof,
                                           _read_json_page()),
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
    # r1528: r1525 measured the entry discount as a share count and left it as prose. A count
    # with no owner on the statement is the shape a number takes before it is counted twice,
    # so the subset is attached to the row it lives inside -- and the row's lots, amount and
    # NAV are untouched (inside_holdings adds nothing; it only says where the shares already are).
    out["discount_inside_holdings"] = units_face.inside_holdings(_read_json(UNITS_FACE), out)
    return out


def load_inputs(stamp=None):
    stack = _read_json(STACK_FACE)
    latest = stack_face.latest_ticket_path()
    # r1512: pin the sheet to the one this episode declares. `latest.json` moves every time a
    # new sheet is priced, but the swap face only refreshes when a swap exists -- so on a quiet
    # bar the newest sheet and the episode belong to two decisions, and pairing them printed
    # "printed rows oversell the book -6,396" out of nothing but the calendar (2026-11-10: the
    # 11-10 target book read against 11-09's three printed actions). One episode, one sheet;
    # what the pinning cannot align is said out loud instead of reconciled silently.
    tpath, pinned, same = pin_episode_ticket(stack, latest)
    ticket = _read_json(tpath)
    ledger = load_ledger()
    face = assess(ticket, stack, ledger, stamp)
    face["ticket_alignment"] = {
        "episode_ticket": os.path.basename(tpath) if tpath else None,
        "episode_bar": (stack or {}).get("asof"),
        "latest_ticket": os.path.basename(latest) if latest else None,
        "pinned_to_episode": pinned,
        "same_ticket": same,
        "reading": ("本面按净额单面自己声明的那张票对账——两件事同一格，红绿才说得上"
                    if same else
                    "净额单面讲的是 %s 那次换票，盘上最新票面是 %s：两件事，本面只对"
                    "自己的那一件，不把另一张票的账借来判红" % (
                        os.path.basename(tpath) if tpath else "（无）",
                        os.path.basename(latest) if latest else "（无）")),
    }
    if stack is None:
        face["notes"] = ["没有已发布的净额单面（%s）：打印动作与声明账都对不出来" % rel(STACK_FACE)]
    elif ticket is None:
        face.setdefault("notes", []).append("没有在册的票面：动作的起点账读不出来")
    return face, ledger


def render_md(face):
    L = ["# ETF 复合书 · 打印的单，和账上的书", "",
         "会话 `%s`｜票 `%s`｜上游 `%s`" % (face.get("asof"), face.get("ticket"),
                                          (face.get("sources") or {}).get("swap_stack")), ""]
    _al = face.get("ticket_alignment") or {}
    if _al and not _al.get("same_ticket"):
        L += ["- 对的是哪张票：%s" % (_al.get("reading") or "?"), ""]
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

    _tr = face.get("transition") or {}
    if _tr:
        _st = str(_tr.get("status") or "?")
        if _st == "EXPLAINED":
            _say = "**这一行是交易走出来的**：打印的动作正好把上一行搬到声明的账。"
        elif _st == "UNEXPLAINED_TARGET_WITHOUT_TRADES":
            _say = ("**这一行不是交易走出来的**：账从 `%s` 到 `%s` 换了持仓，动作行 %d 笔，"
                    "搬动 **¥%s**。它是一张被直接写下的目标，不能当成交读。"
                    % (_tr.get("from_bar") or "?", _tr.get("bar") or "?",
                       int(_tr.get("actions") or 0),
                       format(_tr.get("cny_moved") or 0.0, ",.0f")))
        elif _st == "UNEXPLAINED_LOTS":
            _say = ("**动作行走不到声明的账**：%d 处腿/手数对不上，%s。"
                    % (len(_tr.get("vanished") or []) + len(_tr.get("appeared") or [])
                       + len(_tr.get("lots_changed") or []),
                       "搬动 **¥%s**" % format(_tr.get("cny_moved") or 0.0, ",.0f")
                       if _tr.get("cny_moved") is not None else "没有当日价，不编金额"))
        else:
            _say = "**这是账上的第一行**，没有上一行可比。"
        L += ["## 这一行账是从哪一行走到哪一行", "", _say, ""]
        if _tr.get("vanished") or _tr.get("appeared") or _tr.get("lots_changed"):
            L += ["| 变化 | 代码 | 上一行 + 打印动作 = 应有 | 这一行声明 |",
                  "|---|---|---|---|"]
            for s in _tr.get("vanished") or []:
                L.append("| 消失 | %s | 有 | **没有** |" % s)
            for s in _tr.get("appeared") or []:
                L.append("| 出现 | %s | 没有 | **有** |" % s)
            for r in _tr.get("lots_changed") or []:
                L.append("| 手数变 | %s | %s 手 | **%s 手** |"
                         % (r.get("symbol"), r.get("expected_lots"), r.get("target_lots")))
            L += [""]

    base = face.get("next_order_base")
    if base:
        _kind = base.get("kind") or "execution"
        _arrival = base.get("arrival")
        if _arrival == "declared":
            L += ["## 下一张单从哪本账起算", "",
                  "- 已写下的账：bar `%s`｜风险腿 ¥%s｜现金 ¥%s｜持仓 %d 只｜这一行是**声明行**"
                  % (base.get("bar"), format(base.get("risk_book_cny") or 0.0, ",.0f"),
                     format(base.get("cash_cny") or 0.0, ",.0f"), base.get("holdings") or 0),
                  "- 它是这张单写下的**目标**，动作行 %s 笔——**起点是声明，不是成交**："
                  "账上换过的持仓没有任何一笔交易把它搬过去，下一张单拿它起算时，"
                  "手里真正有多少只取决于券商成交，不取决于这一行。"
                  % (base.get("arrival_actions") if base.get("arrival_actions") is not None
                     else 0)]
        else:
            L += ["## 下一张单从哪本账起算", "",
                  "- 已写下的执行后账：bar `%s`｜风险腿 ¥%s｜现金 ¥%s｜持仓 %d 只｜这一行是**%s**"
                  % (base.get("bar"), format(base.get("risk_book_cny") or 0.0, ",.0f"),
                     format(base.get("cash_cny") or 0.0, ",.0f"), base.get("holdings") or 0,
                     "执行行" if _kind == "execution"
                     else "执行后按每日市值/回购利 accrual 出来的估值行")]
        _sup = base.get("superseded_execution_bar")
        if _kind != "execution" and _sup and _sup != base.get("bar"):
            L += ["- 上一笔执行停在 `%s`：那一行已经不是账户现在的样子，本面按 accrual 后的 `%s` 起算"
                  "（只把持仓和现金往前推，换手仍是 `%s` 那次）" % (_sup, base.get("bar"), _sup)]
        L.append("")
    elif face.get("verdict") != "CANNOT_VERIFY":
        L += ["## 下一张单从哪本账起算", "",
              "- **没有写下的执行后账**：下一张单只能退回上一张票面起算——那正是两本账分叉的入口。", ""]

    if (face.get("base_source") or "") == "swap_stack.holdings_after":
        _ent = face.get("entry_sheet_lots") or {}
        _post = {str(h.get("symbol")): int(h.get("lots") or 0)
                 for h in (face.get("ledger_row") or {}).get("holdings") or []}
        _mv = [s for s in sorted(set(_ent) | set(_post)) if _ent.get(s, 0) != _post.get(s, 0)]
        L += ["- 换票节（r1467）改过入场表：%s —— 所以上面说的「从票面起算」指的是**票面换票之后的账**，"
              "不是入场表；拿入场表相减会凭空多出一次反向换票（r1521 修的就是这一处）。"
              % "、".join(_mv), ""]

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

    acc = face.get("accrual") or {}
    if acc.get("status") in ("ACCRUED", "NO_NEW_BAR"):
        L += ["## 这本书每天的账", ""]
        cash0 = float((face.get("ledger_row") or {}).get("cash_cny") or 0.0)
        rate = acc.get("rate_latest")
        if acc.get("status") == "NO_NEW_BAR":
            L += ["- **没有一天的账可记**：执行 bar `%s` 与面板最新 bar 是同一天（%s）——不是算不出来，"
                  "是那天之后还没有收盘价。" % (acc.get("from_bar"), acc.get("from_bar"))]
        else:
            L += ["- 从 bar `%s` 起已写下 **%d 行**（新写 %d、重跑保持 %d），面板最新 bar `%s`。"
                  % (acc.get("from_bar"), acc.get("rows"), acc.get("written"),
                     acc.get("kept"), (acc.get("last") or {}).get("bar")),
                  "", "| bar | 风险腿 | 现金 | 账 | 当日 | 累计 |", "|---|---|---|---|---|---|"]
            for r in (face.get("accrual_rows") or []):
                L.append("| %s | ¥%s | ¥%s | ¥%s | %s | %s |"
                         % (r["bar"], format(r["risk_book_cny"], ",.0f"),
                            format(r["cash_cny"], ",.0f"), format(r["nav_cny"], ",.0f"),
                            "%+.3f%%" % (r["ret"] * 100.0) if r.get("ret") is not None else "?",
                            "%+.3f%%" % (r["cum_ret"] * 100.0)
                            if r.get("cum_ret") is not None else "?"))
        if rate is not None and cash0:
            L += ["",
                  "- 现金腿按 1 日回购计息（周五→周一算三天）：最近报价 **%.3f%%**（%s），cash ¥%s "
                  "每个交易日挣 **¥%.2f**，跨周末一格 **¥%.2f**——不记这一行，现金就只是躺在账上的数字。"
                  % (float(rate), acc.get("rate_latest_bar") or "?", format(cash0, ",.0f"),
                     cash0 * float(rate) / 100.0 / 365.0,
                     cash0 * float(rate) / 100.0 * 3.0 / 365.0)]
        if acc.get("rf_missing_bars"):
            L += ["- 有 **%d** 个 bar 没有前一日回购报价：按零计息并如实计数，不用猜的利率填。"
                  % acc["rf_missing_bars"]]
        if acc.get("panel_missing_symbols"):
            L += ["- 没有日线面板的腿：%s（不推价、不编价）。"
                  % "、".join(acc["panel_missing_symbols"])]
        L.append("")

    st = face.get("settlement") or {}
    if st:
        L += ["## 这一根 bar 能不能记估值（价格面板）", ""]
        if st.get("priced"):
            L += ["- bar `%s` 全腿都有收盘价：执行与估值都记在这一根上。" % st.get("bar")]
        else:
            L += ["- **bar `%s` 在价格面板里还没有全腿收盘价**——面板最后一根「全腿都有收盘」的 bar 是 `%s`，"
                  "这一根缺 %s。账上这一根只记**执行**（手数与成交价），不记**估值**；"
                  "等收盘价到齐再补记。"
                  % (st.get("bar"), st.get("last_fully_priced_bar") or "（没有）",
                     "、".join(st.get("missing_closes_on_bar") or []) or "（未知）"),
                  "- 补记时若数变了，会作为**改述**印在下面那一节，不会把读者手里的旧数悄悄换掉。"]
        past = st.get("ledger_bars_past_boundary") or []
        if past:
            L += ["- 账本里还有 **%d** 根 bar 写在「全腿收盘」那天之后（%s）：这些 bar 的估值在收盘价到齐前"
                  "**不作数**，也不会被当成当日的账。"
                  % (len(past), "、".join("%s(%s)" % (p.get("bar"), p.get("kind")) for p in past[:6]))]
        L.append("")

    rp = face.get("replay")
    if rp:
        L += ["## 引擎体检：同一批票往前 %d 个 bar" % rp.get("bars"), "",
              "- 从 bar `%s` 到执行 bar：持仓按面板收盘逐日重估、现金按 1 日回购计息"
              "（缺回购报价 %d 个 bar，有票停牌/缺价 %d 个 bar）。"
              % (rp.get("start_bar"), rp.get("rf_missing_bars") or 0, rp.get("stale_bars") or 0),
              "- 腿市值 ￥%s → ￥%s（**%+.2f%%**），现金利息 **￥%s**。"
              % (format(rp.get("legs_first_bar") or 0.0, ",.0f"),
                 format(rp.get("legs_last_bar") or 0.0, ",.0f"),
                 (rp.get("legs_ret") or 0.0) * 100.0,
                 format(rp.get("cash_interest_cny") or 0.0, ",.2f")),
              ("- 恒等腿：最后一行算出的腿市值与账本行自己记的腿金额差 **￥%.2f**（%s）——"
               "同一批手数、同一批收盘价，引擎必须把账本写下的钱算回来。"
               % (rp.get("identity_delta_cny") or 0.0,
                  "通过" if rp.get("identity_holds") else "**不通过**"))
              if rp.get("identity_status") != "UNPRICED_BAR" else
              ("- **这一段不是恒等体检**：执行 bar `%s` 自己缺 %s 的收盘价，回放只能标到 `%s`，"
               "那 ￥%.2f 的差是成交价与那一根旧收盘价之间的距离，**不是引擎算错**。等这一根的全腿"
               "收盘价到齐再验。"
               % (base.get("bar") if base else "?", "、".join(rp.get("base_bar_missing_closes") or []),
                  rp.get("base_bar_last_priced_day") or "（更早）",
                  rp.get("identity_delta_cny") or 0.0)),
              "- **这不是这本书的盈亏**：账本从执行 bar 才开始，这一段是同一批持仓的历史回放，"
              "只证明引擎在真面板上走得通，不给这本书记任何收益。", ""]

    eb = face.get("engine_book") or {}
    if eb.get("divergence"):
        d = eb["divergence"]
        L += ["## 票面背后还有一本账（引擎账 vs 执行账）", "",
              "- 造这张单的脚本自己维护一本归一化账（`%s`，最新 bar `%s`）：k=%.4f。"
              % ((eb.get("tail") or {}).get("source"), (eb.get("tail") or {}).get("bar"),
                 float(d["engine_k"])),
              "- 执行账（这张面写下的那本）：k=%.4f，NAV ¥%s。"
              % (float(d["book_k"]), format(d["book_nav_cny"], ",.0f")),
              "- 差 **%.2fpp = ¥%s 名义暴露**。两本账各自都没错：引擎账是**裁剪前**的策略暴露，"
              "执行账是额度允许的暴露。但这意味着**下一张单从哪本账起算，会差这么多钱**——"
              "所以「从账本起算」必须是执行账，不是引擎账。"
              % (float(d["k_gap"]) * 100.0, format(d["notional_gap_cny"], ",.0f")), ""]

    if face.get("notes"):
        L += ["## 读这张面时要知道的", ""]
        for n in face["notes"]:
            L.append("- %s" % n)
        L.append("")

    rst = face.get("restatements") or {}
    if rst:
        L += ["## 这一根 bar 有没有被改写过", ""]
        if rst.get("count"):
            L += ["- **已记下 %d 次改述**：同一根 bar `%s` 上一次写的数被换成了另一组，下面是两组数。"
                  % (rst["count"], rst.get("bar"))]
            for r in rst["records"]:
                b, a = r.get("before") or {}, r.get("after") or {}
                dl = r.get("delta") or {}
                L += ["- `%s` → `%s`：k %s → %s（%+.6f）、风险腿 ¥%s → ¥%s（%s）、现金 ¥%s → ¥%s（%s）。"
                      % (r.get("previous_written_ts") or "?", r.get("written_ts") or "?",
                         b.get("k"), a.get("k"), float(dl.get("k") or 0.0),
                         format(float(b.get("risk_book_cny") or 0.0), ",.0f"),
                         format(float(a.get("risk_book_cny") or 0.0), ",.0f"),
                         ("%+.0f" % float(dl.get("risk_book_cny") or 0.0)),
                         format(float(b.get("cash_cny") or 0.0), ",.0f"),
                         format(float(a.get("cash_cny") or 0.0), ",.0f"),
                         ("%+.0f" % float(dl.get("cash_cny") or 0.0)))]
                if r.get("lots_changed"):
                    L += ["- 手数变了：%s。" % "、".join(
                        "%s %s→%s" % (c["symbol"], c.get("before"), c.get("after"))
                        for c in r["lots_changed"])]
        else:
            L += ["- **这本账没有记到这根 bar 的改述**——但记录是从本轮才开始写的，"
                  "**之前改写过的 bar 这里看不到**：没有记录不等于没被改过。"]
        pg = rst.get("page_block")
        if pg and pg.get("same_bar") and pg.get("lots"):
            if rst.get("page_vs_ledger_agree") is False:
                _dlots = rst.get("page_vs_ledger_lots") or []
                if _dlots:
                    L += ["- **页面上同一根 bar 印的是另一组手数**：%s。两处都是公开发布的读数，"
                          "这里只并排印出来，不替任何一边改数（页面写者是另一台机）。"
                          % "、".join("%s 页面 %s / 账本 %s" % (d["symbol"], d.get("page_lots"),
                                                            d.get("ledger_lots"))
                                     for d in _dlots)]
                _pvc = rst.get("page_vs_ledger_cash") or {}
                if _pvc.get("page_minus_ledger"):
                    L += ["- 现金腿也对不上：页面 ¥%s / 账本 ¥%s（差 **%+.0f**）。"
                          % (format(float(_pvc.get("page") or 0.0), ",.0f"),
                             format(float(_pvc.get("ledger") or 0.0), ",.0f"),
                             float(_pvc["page_minus_ledger"]))]
            elif rst.get("page_vs_ledger_agree") is True:
                L += ["- 页面同一根 bar 的手数与账本一致。"]
        elif pg and pg.get("same_bar") is False:
            L += ["- 页面停在 bar `%s`，与这根 bar 不同天：不拿两天的账互相校验。" % pg.get("bar")]
        else:
            L += ["- 页面上没有这根 bar 的持仓区块：无法比对，这不是「一致」。"]
        L.append("")

    L += ["## 不能从这张面读出来的", ""]
    for c in face.get("caveats") or []:
        L.append("- %s" % c)
    L += ["", "- 出处：`scripts/etf_book_positions.py`；执行后账在 `%s`（按决策 bar 一行）。"
          "同一 bar 重跑若数值不变=保持；真的变了会记一条改述并在上面印出两组数。"
          % (face.get("sources") or {}).get("ledger"), ""]
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
    # r1469: the accrual must reproduce exactly, and every mark must carry its own identity
    pub_acc = published.get("accrual") or {}
    fr_acc = fresh.get("accrual") or {}
    if (pub_acc.get("status") or None) != (fr_acc.get("status") or None):
        bad.append("accrual_status")
    pr, fr = (pub_acc.get("rows_detail") or []), (fr_acc.get("rows_detail") or [])
    if len(pr) != len(fr):
        bad.append("accrual_rows")
    else:
        for a, b in zip(pr, fr):
            if a.get("bar") != b.get("bar") or abs((a.get("nav_cny") or 0.0)
                                                   - (b.get("nav_cny") or 0.0)) > 0.01:
                bad.append("accrual_nav")
                break
    for r in ledger.get("rows") or []:
        if str(r.get("kind") or "") == "valuation":
            if abs((r.get("nav_cny") or 0.0)
                   - ((r.get("risk_book_cny") or 0.0) + (r.get("cash_cny") or 0.0))) > 0.01:
                bad.append("valuation_nav_identity")
                break
    # r1518: one bar cannot be both the executed book and a mark of the book before it.
    # Valuations BETWEEN execution bars are the normal accrual output; a valuation sharing a
    # bar with an execution is the collision that let the last writer decide what the account
    # held (r1517 wrote 690/925/487/674 over a trade of 693/891/473/677).
    _exec_bars = {str(r.get("bar")) for r in ledger.get("rows") or []
                  if str(r.get("kind") or "execution") == "execution"}
    if any(str(r.get("bar")) in _exec_bars for r in ledger.get("rows") or []
           if str(r.get("kind") or "") == "valuation"):
        bad.append("valuation_row_on_execution_bar")

    # r1563: a bar's provenance is part of the face. A row that declared a book without
    # printing the trades that build it must say so, and that read must reach the page a
    # reader actually opens -- not stay in the JSON. A hand-flipped flag is caught here.
    pub_tr = published.get("transition") or {}
    fr_tr = fresh.get("transition") or {}
    for _k in ("status", "bar", "from_bar", "actions"):
        if (pub_tr.get(_k) or None) != (fr_tr.get(_k) or None):
            bad.append("transition_%s" % _k)
            break
    if ((pub_tr.get("vanished") or []) != (fr_tr.get("vanished") or [])
            or (pub_tr.get("appeared") or []) != (fr_tr.get("appeared") or [])):
        bad.append("transition_legs")
    if len(pub_tr.get("lots_changed") or []) != len(fr_tr.get("lots_changed") or []):
        bad.append("transition_lots")
    if os.path.exists(OUT_MD):
        _txt = open(OUT_MD, encoding="utf-8").read()
        if "这一行账是从哪一行走到哪一行" not in _txt:
            bad.append("page_missing_transition")

    # r1564: the base's provenance is part of the face too. A row declared without trades must
    # not be handed to the next sheet as an execution, and the page must say so in words a
    # reader sees -- a hand-flipped flag is caught here, not by reading the JSON.
    _pb, _fb = published.get("next_order_base") or {}, fresh.get("next_order_base") or {}
    if (_pb.get("arrival") or None) != (_fb.get("arrival") or None):
        bad.append("base_arrival")
    elif _pb.get("arrival") == "declared":
        if os.path.exists(OUT_MD):
            _txt2 = open(OUT_MD, encoding="utf-8").read()
            if "起点是声明，不是成交" not in _txt2:
                bad.append("page_missing_declaration")

    # r1469: the replay must still reproduce the ledger's own legs, and must reproduce exactly
    # r1483: an identity that was never measured is not a failed identity -- the failure is
    # publishing a verdict for a bar the panel cannot price at all.
    pub_rp = published.get("replay") or {}
    fr_rp = fresh.get("replay") or {}
    if pub_rp.get("identity_holds") is False:
        bad.append("replay_identity")
    if (pub_rp.get("identity_status") or None) != (fr_rp.get("identity_status") or None):
        bad.append("replay_identity_status")
    if ((pub_rp.get("bars"), pub_rp.get("legs_last_bar"))
            != (fr_rp.get("bars"), fr_rp.get("legs_last_bar"))):
        bad.append("replay_drift")
    # r1483: the settlement boundary is re-derived from the products, not taken from the face
    pub_st, fr_st = published.get("settlement") or {}, fresh.get("settlement") or {}
    for key in ("bar", "priced", "last_fully_priced_bar", "missing_closes_on_bar",
                "ledger_bars_past_boundary"):
        if (pub_st.get(key) or None) != (fr_st.get(key) or None):
            bad.append("settlement_" + key)

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

    # 6b. r1474: replacing a settled bar is a restatement, and it is recorded once
    chk("the change was recorded as a restatement", len(led.get("restatements") or []) == 1)
    rec = (led["restatements"] or [{}])[0]
    chk("the record carries both sets of numbers",
        (rec.get("before") or {}).get("lots", {}).get("A") == 50
        and (rec.get("after") or {}).get("lots", {}).get("A") == 40)
    chk("it names what moved in lots",
        [c["symbol"] for c in rec.get("lots_changed") or []] == ["A"])
    f = assess(t2, st2, led, stamp="t4")
    chk("re-running the change does not file a second one",
        len(led.get("restatements") or []) == 1 and f["ledger_action"] == "kept")
    f = assess(t2, st, led, stamp="t5")
    chk("changing it back is its own restatement", len(led.get("restatements") or []) == 2)
    chk("the face carries the restatement block", "restatements" in f
        and f["restatements"].get("count") == 2)

    # 6c. r1474: an empty trail is not evidence that nothing was rewritten
    rep = restatement_report({"rows": [], "restatements": []}, "2026-11-06", None)
    chk("no record is reported as no record", rep["count"] == 0 and rep["records"] == [])
    chk("it refuses to read the empty trail as 'never restated'",
        rep["trail_covers_bar"] is None)
    md = render_md({"asof": "2026-11-06", "verdict": "CANNOT_VERIFY",
                    "restatements": rep, "caveats": []})
    chk("the printed sheet says the trail does not reach back",
        "没有记录不等于没被改过" in md)

    # 6d. r1474: a number printed on another face must be compared, not ignored
    page = ("## 账上现在拿的是什么（本仓库自己算的账）\n\n"
            "**账上自己的账（2026-11-06 收盘）：风险腿 ￥390,144、现金 ￥609,856、持有 4 只。**\n\n"
            "| 代码 | 手数 | 参考价 | 金额 |\n|---|---|---|---|\n"
            "| 159263 | 683 | 1.143 | ￥78,067 |\n"
            "| 159513 | 915 | 1.705 | ￥156,008 |\n")
    ledp = {"rows": [{"bar": "2026-11-06", "k": 0.389744, "risk_book_cny": 389743.8,
                      "cash_cny": 610256.2,
                      "holdings": [{"symbol": "159263", "lots": 682},
                                   {"symbol": "159513", "lots": 914}]}],
            "restatements": []}
    rep2 = restatement_report(ledp, "2026-11-06", page)
    chk("the same bar on the page is read", (rep2.get("page_block") or {}).get("same_bar") is True)
    chk("the two faces disagreeing is reported as disagreement",
        rep2.get("page_vs_ledger_agree") is False
        and len(rep2.get("page_vs_ledger_lots") or []) == 2)
    md2 = render_md({"asof": "2026-11-06", "verdict": "CANNOT_VERIFY",
                     "restatements": rep2, "caveats": []})
    chk("both numbers reach the printed sheet",
        "683" in md2 and "682" in md2 and "另一组手数" in md2)
    rep3 = restatement_report(ledp, "2026-11-06", page.replace("2026-11-06", "2026-11-05"))
    chk("two different days are not compared to each other",
        (rep3.get("page_block") or {}).get("same_bar") is False
        and rep3.get("page_vs_ledger_agree") is None)
    rep4 = restatement_report(ledp, "2026-11-06", "no account section here")
    chk("a page with no block is 'cannot compare', not 'agrees'",
        rep4.get("page_block") is None and rep4.get("page_vs_ledger_agree") is None)

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

    # 9b. r1512: the row the accrual just wrote is the account the next sheet starts from
    _led = {"rows": [
        {"bar": "2026-11-09", "kind": "execution", "risk_book_cny": 392587.3,
         "cash_cny": 607412.7, "holdings": [{"symbol": "A", "lots": 10}]},
        {"bar": "2026-11-10", "kind": "valuation", "risk_book_cny": 400023.3,
         "cash_cny": 607412.7, "holdings": [{"symbol": "A", "lots": 10}]}],
        "restatements": []}
    _exec = _led["rows"][0]
    _acc = {"status": "ACCRUED", "last": _led["rows"][1]}
    _b, _src = account_base_after_accrual(_led, _exec, _acc)
    chk("the accrued row is the base, not the execution row it supersedes",
        _b["bar"] == "2026-11-10" and _b["risk_book_cny"] == 400023.3)
    chk("and the base says which kind of row it is", _src == "accrued_valuation")
    _b2, _src2 = account_base_after_accrual(_led, _exec, {"status": "NO_NEW_BAR", "last": None})
    chk("no accrual leaves the execution row as the base",
        _b2["bar"] == "2026-11-09" and _src2 == "execution_row")
    chk("an empty base stays empty rather than reading as an empty book",
        account_base_after_accrual(_led, None, _acc) == (None, None))

    # 9c. r1512: one episode, one sheet -- a newer sheet on disk is another decision
    import tempfile as _tf
    _d = _tf.mkdtemp()
    _old = os.path.join(_d, "TICKET-2026-11-09.json")
    _new = os.path.join(_d, "TICKET-2026-11-10.json")
    for _p in (_old, _new):
        open(_p, "w", encoding="utf-8").write("{}")
    _p, _pin, _same = pin_episode_ticket({"ticket": "TICKET-2026-11-09.json", "asof": "2026-11-09"},
                                         _new)
    chk("the episode's own sheet wins over the newest one", _p == _old and _pin is True)
    chk("and the two are not called the same ticket", _same is False)
    _p2, _pin2, _same2 = pin_episode_ticket({"ticket": "TICKET-2026-11-10.json",
                                             "asof": "2026-11-10"}, _new)
    chk("a same-episode sheet is reported as the same", _p2 == _new and _same2 is True)
    _p3, _pin3, _ = pin_episode_ticket({"ticket": "TICKET-2099-01-01.json"}, _new)
    chk("a declared sheet that is not on disk falls back to the newest, unpinned",
        _p3 == _new and _pin3 is False)

    # 10. r1469 accrual: cash earns calendar days, a missing quote accrues nothing
    chk("a three-day repurchase step is three days of the quote",
        abs(rf_step(1.185, 3) - 1.185 / 100.0 * 3 / 365.0) < 1e-12)
    chk("a missing quote is None, not a zero rate wearing a number", rf_step(None, 1) is None)

    # 11. marks: a day with no print carries the last close and is named
    holds = [{"symbol": "A", "lots": 10, "price": 2.0}]
    steps = price_steps(holds, {"A": {"2026-11-06": 2.0, "2026-11-09": 2.2}}, "2026-11-06")
    chk("only days after the start bar are stepped", [s["bar"] for s in steps] == ["2026-11-09"])
    closes2 = {"A": {"2026-11-06": 2.0, "2026-11-09": 2.2, "2026-11-10": 2.3},
               "B": {"2026-11-06": 1.0, "2026-11-10": 1.1}}
    holds2 = [{"symbol": "A", "lots": 10, "price": 2.0}, {"symbol": "B", "lots": 5, "price": 1.0}]
    steps2 = price_steps(holds2, closes2, "2026-11-06")
    chk("a suspended leg carries its last close", steps2[0]["marks"]["B"] == 1.0)
    chk("and is named as stale", steps2[0]["stale"] == ["B"])

    # 12. accrual writes one row per bar, with nav = legs + cash
    row = {"bar": "2026-11-06", "holdings": [{"symbol": "A", "lots": 10, "price": 2.0}],
           "cash_cny": 1000.0, "risk_book_cny": 2000.0, "source_face": "x"}
    rows, _miss = accrue_rows(row, [{"bar": "2026-11-09", "marks": {"A": 2.2}, "stale": [],
                                     "gap_days": 3}], {"2026-11-09": 1.185})
    chk("one bar gives one row", len(rows) == 1)
    chk("nav is legs plus cash",
        abs(rows[0]["nav_cny"] - (2200.0 + 1000.0 * (1 + rf_step(1.185, 3)))) < 0.01)
    chk("the cash leg visibly earned", rows[0]["cash_cny"] > 1000.0)
    chk("a missing quote is counted",
        accrue_rows(row, [{"bar": "2026-11-09", "marks": {"A": 2.2}, "stale": [],
                           "gap_days": 1}], {})[1] == 1)

    # 13. re-running the same bar keeps the row; a valuation is not an execution
    led2 = {"schema": "x", "rows": [dict(row)]}
    a1 = accrue(led2, stamp="t1", closes_by_symbol=closes2, rates={"2026-11-09": 1.185})
    a2 = accrue(led2, stamp="t2", closes_by_symbol=closes2, rates={"2026-11-09": 1.185})
    chk("accrual writes on the first run", a1["written"] == a1["rows"] and a1["status"] == "ACCRUED")
    chk("the same bars are kept on a re-run", a2["kept"] == a2["rows"] and a2["written"] == 0)
    chk("valuations are not mistaken for executions",
        latest_execution_row(led2)["bar"] == "2026-11-06")

    # 14. the replay engine must reproduce the amount the ledger row already carries
    rp = replay({"bar": "2026-11-10", "holdings": [{"symbol": "A", "lots": 10, "price": 2.0}],
                 "cash_cny": 1000.0, "risk_book_cny": 2000.0},
                {"A": {"2026-11-06": 1.9, "2026-11-09": 2.0, "2026-11-10": 2.0}},
                {"2026-11-09": 1.185}, window=4)
    chk("the replay reconstructs the row's own legs", rp and rp["identity_holds"])
    chk("and moves cash by interest only", rp and rp["cash_interest_cny"] >= 0.0)

    # 15. r1483 (T29): a bar the panel cannot price is not a valuation bar
    pb, blockers = priced_boundary(closes2, holds2)
    chk("the boundary is the last day every held leg printed", pb == "2026-11-10")
    chk("the legs missing past it are named, not zeroed", blockers == {"2026-11-09": ["B"]})
    chk("a one-leg panel has no boundary to claim",
        priced_boundary({"A": {"2026-11-09": 2.0}}, holds2)[0] is None)
    rp2 = replay({"bar": "2026-11-09",
                  "holdings": [{"symbol": "A", "lots": 10, "price": 2.0},
                               {"symbol": "B", "lots": 5, "price": 1.0}],
                  "cash_cny": 1000.0, "risk_book_cny": 25000.0}, closes2,
                 {"2026-11-09": 1.185}, window=4)
    chk("an unprinted execution bar yields no identity verdict",
        rp2 and rp2["identity_holds"] is None and rp2["identity_status"] == "UNPRICED_BAR")
    chk("it names the leg without a close on that bar", rp2["base_bar_missing_closes"] == ["B"])
    chk("and names the last day it could mark", rp2["base_bar_last_priced_day"] == "2026-11-06")
    rp3 = replay({"bar": "2026-11-10",
                  "holdings": [{"symbol": "A", "lots": 10, "price": 2.0},
                               {"symbol": "B", "lots": 5, "price": 1.0}],
                  "cash_cny": 1000.0, "risk_book_cny": 23000.0}, closes2,
                 {"2026-11-09": 1.185}, window=4)
    chk("a fully priced bar does carry a verdict",
        rp3 and rp3["identity_status"] == "PRICED_BAR" and rp3["identity_holds"] is False)
    ledu = {"schema": "x", "rows": [{"bar": "2026-11-06", "holdings": [
        {"symbol": "A", "lots": 50, "price": 2.0}, {"symbol": "B", "lots": 200, "price": 1.0}],
        "cash_cny": 900000.0, "risk_book_cny": 300000.0}]}
    stu = dict(st, asof="2026-11-09")
    fu = assess(t2, stu, ledu)
    chk("a book with no panel closes says its bar is unpriceable",
        (fu.get("settlement") or {}).get("priced") is False
        and fu["settlement"]["last_fully_priced_bar"] is None)
    chk("and writes no valuation row for it", fu["accrual"]["status"] == "NO_PRICED_BAR")
    mdu = render_md(fu)
    chk("the printed sheet names the bar it could not mark",
        "价格面板里还没有全腿收盘价" in mdu)

    # 16. r1518: one bar, two facts -- the executed book must be the one that stays
    _val = {"bar": "2026-11-10", "kind": "valuation", "from_bar": "2026-11-09",
            "holdings": [{"symbol": "A", "lots": 10, "price": 2.3, "amount_cny": 23000.0}],
            "risk_book_cny": 23000.0, "cash_cny": 1000.0, "nav_cny": 24000.0,
            "ret": 0.05, "cum_ret": 0.05, "source_face": "x"}
    _l16 = {"schema": "x", "rows": [{"bar": "2026-11-09", "kind": "execution",
                                     "holdings": [{"symbol": "A", "lots": 10, "price": 2.0}],
                                     "cash_cny": 1000.0, "risk_book_cny": 20000.0},
                                    dict(_val)]}
    _exec16 = {"bar": "2026-11-10", "kind": "execution",
               "holdings": [{"symbol": "A", "lots": 8, "price": 2.3}],
               "cash_cny": 5600.0, "risk_book_cny": 18400.0, "source_face": "x"}
    _act16 = upsert_row(_l16, _exec16, "t1")
    _row16 = [r for r in _l16["rows"] if r["bar"] == "2026-11-10"][0]
    chk("an executed bar replaces the mark-only row for the same day", _act16 == "updated")
    chk("no field of the replaced fact survives",
        _row16.get("kind") == "execution" and "nav_cny" not in _row16
        and "from_bar" not in _row16 and "ret" not in _row16)
    chk("the replacement is a recorded restatement, not a silent swap",
        len(_l16.get("restatements") or []) == 1)
    _a16 = accrue(_l16, stamp="t2",
                  closes_by_symbol={"A": {"2026-11-09": 2.0, "2026-11-10": 2.3,
                                          "2026-11-11": 2.4}},
                  rates={"2026-11-10": 1.185, "2026-11-11": 1.185}, upto="2026-11-11")
    _row16 = [r for r in _l16["rows"] if r["bar"] == "2026-11-10"][0]
    chk("accrual starts after the executed bar instead of overwriting it",
        _row16.get("kind") == "execution" and _row16["holdings"][0]["lots"] == 8)
    chk("the bar after it is valued from the executed book",
        [r["bar"] for r in _l16["rows"]].count("2026-11-11") == 1)
    chk("no bar is skipped when there is nothing to skip",
        (_a16.get("skipped_execution_bars") or []) == [])
    _both = {"rows": [{"bar": "2026-11-10", "kind": "valuation",
                       "holdings": [{"symbol": "A", "lots": 1}]},
                      {"bar": "2026-11-10", "kind": "execution",
                       "holdings": [{"symbol": "A", "lots": 2}]}]}
    chk("a bar carrying both kinds resolves to the executed book",
        start_inventory(_both, "2026-11-10")["holdings"][0]["lots"] == 2)

    # 17. r1563: the row may not be read as an account when its own trades cannot reach it
    _l17 = {"schema": "x", "rows": [
        {"bar": "2026-11-06", "kind": "execution",
         "holdings": [{"symbol": "A", "lots": 10, "price": 2.0}],
         "cash_cny": 1000.0, "risk_book_cny": 20000.0,
         "actions": [{"side": "BUY", "symbol": "A", "lots": 10}]},
        {"bar": "2026-11-09", "kind": "execution",
         "holdings": [{"symbol": "A", "lots": 12, "price": 2.0}],
         "cash_cny": 600.0, "risk_book_cny": 24000.0,
         "actions": [{"side": "BUY", "symbol": "A", "lots": 2}]},
        {"bar": "2026-11-11", "kind": "execution",
         "holdings": [{"symbol": "B", "lots": 30, "price": 1.0}],
         "cash_cny": 27000.0, "risk_book_cny": 30000.0, "actions": []}]}
    chk("a row no trade list can reach is not the account",
        account_row_for(_l17, "2026-11-11")["bar"] == "2026-11-09")
    chk("and a row the trades do reach is the account",
        account_row_for(_l17, "2026-11-09")["bar"] == "2026-11-09")
    _l17b = {"schema": "x", "rows": [_l17["rows"][0],
                                     {"bar": "2026-11-11", "kind": "execution",
                                      "holdings": [{"symbol": "A", "lots": 15, "price": 2.0}],
                                      "cash_cny": 900.0, "risk_book_cny": 30000.0,
                                      "actions": [{"side": "BUY", "symbol": "A", "lots": 5}]}]}
    chk("a reachable row on this bar is subtracted from itself",
        account_row_for(_l17b, "2026-11-11")["bar"] == "2026-11-11")
    _l17c = {"schema": "x", "rows": [_l17["rows"][0],
                                     {"bar": "2026-11-10", "kind": "execution",
                                      "holdings": [{"symbol": "A", "lots": 14, "price": 2.0}],
                                      "cash_cny": 900.0, "risk_book_cny": 28000.0,
                                      "actions": [{"side": "SELL", "symbol": "Z", "lots": 3}]},
                                     {"bar": "2026-11-11", "kind": "execution",
                                      "holdings": [{"symbol": "B", "lots": 30, "price": 1.0}],
                                      "cash_cny": 27000.0, "risk_book_cny": 30000.0,
                                      "actions": []}]}
    chk("a bar that printed trades stays the account even when the list does not close",
        account_row_for(_l17c, "2026-11-11")["bar"] == "2026-11-10")
    _s17 = {"asof": "2026-11-11", "ticket": "T", "k_after": 0.4,
            "risk_book_after_cny": 30000.0, "cash_cny": 27000.0,
            "holdings_after": [{"symbol": "B", "lots": 30, "price": 1.0}], "actions": []}
    _f17 = assess({"ticket": {"order": [{"symbol": "B", "price": 1.0, "lots": 30,
                                         "weight": 0.5}], "nav": 1000000.0}},
                  _s17, _l17)
    chk("the face publishes the book before the declaration",
        (_f17.get("account_row") or {}).get("bar") == "2026-11-09"
        and (_f17.get("account_row") or {}).get("source") == "book_before_declaration")
    chk("and the declaration is still named on the same face",
        str((_f17.get("transition") or {}).get("status") or "").startswith("UNEXPLAINED"))

    # r1563: the bar-to-bar move is a read in its own right and it must reach the page
    _lt = {"schema": "x", "rows": [
        {"bar": "2026-11-10", "kind": "execution",
         "holdings": [{"symbol": "A", "lots": 10, "price": 2.0}],
         "cash_cny": 1000.0, "risk_book_cny": 2000.0, "actions": []},
        {"bar": "2026-11-11", "kind": "execution",
         "holdings": [{"symbol": "B", "lots": 20, "price": 1.0}],
         "cash_cny": 2000.0, "risk_book_cny": 2000.0, "actions": []}]}
    _t1 = book_transition(_lt, "2026-11-11", [], [{"symbol": "A", "lots": 10, "price": 2.0}])
    chk("a row that kept the book needs no trades to explain it", _t1["status"] == "EXPLAINED")
    _t2 = book_transition(_lt, "2026-11-11", [], [{"symbol": "B", "lots": 20, "price": 1.0}])
    chk("a row that swapped the book without trades is named",
        _t2["status"] == "UNEXPLAINED_TARGET_WITHOUT_TRADES"
        and _t2["vanished"] == ["A"] and _t2["appeared"] == ["B"])
    chk("the money it moved is priced off the two rows it spans",
        abs((_t2["cny_moved"] or 0.0) - 4000.0) < 0.01)
    _frag = render_md({"asof": "2026-11-11", "ticket": "T", "verdict": "CANNOT_VERIFY",
                       "transition": _t2})
    chk("the page names the bar-to-bar move instead of leaving it in the json",
        "这一行不是交易走出来的" in _frag and "消失" in _frag and "出现" in _frag)

    # r1564: the row the next sheet starts from carries how it got there. One page cannot
    # call the same row "not walked by trades" and "an execution row".
    _l18 = {"schema": "x", "rows": [
        {"bar": "2026-11-06", "kind": "execution",
         "holdings": [{"symbol": "A", "lots": 100, "price": 2.0, "amount_cny": 20000.0}],
         "cash_cny": 1000.0, "risk_book_cny": 20000.0,
         "actions": [{"side": "BUY", "symbol": "A", "lots": 100}]},
        {"bar": "2026-11-07", "kind": "execution",
         "holdings": [{"symbol": "B", "lots": 50, "price": 1.0, "amount_cny": 5000.0}],
         "cash_cny": 3000.0, "risk_book_cny": 5000.0, "actions": []}]}
    _s18 = {"asof": "2026-11-07", "ticket": "T", "k_after": 0.625,
            "risk_book_after_cny": 5000.0, "cash_cny": 3000.0,
            "holdings_after": [{"symbol": "B", "lots": 50, "price": 1.0,
                                "amount_cny": 5000.0}], "actions": []}
    _tk18 = {"ticket": {"order": [{"symbol": "B", "price": 1.0, "lots": 50,
                                   "weight": 0.5}], "nav": 8000.0}}
    _f18 = assess(_tk18, _s18, _l18)
    _b18 = _f18.get("next_order_base") or {}
    chk("a base row that declared the book without trades is named a declaration",
        _b18.get("bar") == "2026-11-07" and _b18.get("arrival") == "declared")
    chk("the page says the next sheet starts from a declaration, not a fill",
        "起点是声明，不是成交" in render_md(_f18))
    _l19 = {"schema": "x", "rows": [_l18["rows"][0], {
        "bar": "2026-11-07", "kind": "execution",
        "holdings": [{"symbol": "B", "lots": 50, "price": 1.0, "amount_cny": 5000.0}],
        "cash_cny": 3000.0, "risk_book_cny": 5000.0,
        "actions": [{"side": "SELL", "symbol": "A", "lots": 100},
                    {"side": "BUY", "symbol": "B", "lots": 50}]}]}
    _s19 = dict(_s18)
    _s19["actions"] = [{"side": "SELL", "symbol": "A", "lots": 100},
                       {"side": "BUY", "symbol": "B", "lots": 50}]
    _f19 = assess(_tk18, _s19, _l19)
    chk("the same bar WITH its trades printed is an execution, not a declaration",
        (_f19.get("next_order_base") or {}).get("arrival") != "declared")

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