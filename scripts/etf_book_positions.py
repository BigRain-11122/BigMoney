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
    return sorted(eligible, key=lambda r: str(r.get("bar")))[-1]


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
        "identity_holds": abs(identity_delta) <= 0.01,
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

    # r1469: between execution bars the book earns and loses money nobody records. Advance the
    # written book one row per bar (marks + 1-day repo on the cash leg), so the next order can
    # start from the account as it stands rather than from the last execution.
    accrual = {"status": "NO_BOOK"}
    replay_row = None
    if base:
        closes, rates, panel_missing = load_panel_and_rates(base.get("holdings") or [])
        accrual = accrue(ledger, stamp=stamp, closes_by_symbol=closes, rates=rates)
        accrual["panel_missing_symbols"] = panel_missing
        accrual["repo_quotes"] = len(rates)
        accrual["rate_latest_bar"] = max(rates) if rates else None
        accrual["rate_latest"] = rates[max(rates)] if rates else None
        replay_row = replay(base, closes, rates) if base and closes else None

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
        "accrual": accrual,
        "accrual_rows": accrual.get("rows_detail") or [],
        "replay": replay_row,
        "engine_book": {"tail": eng, "divergence": eng_gap},
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
              "- 恒等腿：最后一行算出的腿市值与账本行自己记的腿金额差 **￥%.2f**（%s）——"
              "同一批手数、同一批收盘价，引擎必须把账本写下的钱算回来。"
              % (rp.get("identity_delta_cny") or 0.0,
                 "通过" if rp.get("identity_holds") else "**不通过**"),
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

    # r1469: the replay must still reproduce the ledger's own legs, and must reproduce exactly
    pub_rp = published.get("replay") or {}
    fr_rp = fresh.get("replay") or {}
    if pub_rp and not pub_rp.get("identity_holds"):
        bad.append("replay_identity")
    if ((pub_rp.get("bars"), pub_rp.get("legs_last_bar"))
            != (fr_rp.get("bars"), fr_rp.get("legs_last_bar"))):
        bad.append("replay_drift")

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