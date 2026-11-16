#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""forward paper accrual for the index-futures carry sleeve the desk sheet publishes

WHY THIS FILE EXISTS
--------------------
r1685 opened the basis line (C1/C2 cleared on IC and IM) and r1697-r1712 turned it
into a ticket: `results/idx_fut_desk_sheet.json` names the held contract, the lots,
the margin, the distance to a margin call and the roll.  DIRECTION-20261114 sec.5
says the one-month review reads two numbers -- the out-of-sample Sharpe and "the
real NAV this book has accumulated from today".  The first number exists.  The
second had nowhere to live: every carry face on disk is a replay of history, so a
month from now the honest answer would still be a backtest.

So this file books the ticket forward: from an anchor bar, mark the published
position to the contract closes, one line per trading day, and never rewrite a
line that already exists.

WHAT IT BOOKS
-------------
  * the position the desk sheet publishes, not one this file invents: product,
    held contract, lots (the recommended-lots block, which is the one that survives
    its own drawdown), multiplier, capital;
  * long futures P&L in CNY = lots * multiplier * (close_t - close_{t-1}) on the
    contract that was actually held, so the discount converging into the index is
    in the number rather than added as a separate carry estimate;
  * rolls are read from the same deepest-open-interest book `idx_fut_real_nav`
    uses (imported, not re-implemented): on a roll day the P&L is booked on the old
    contract up to that close and the new contract takes over from it, so the seam
    is at the same close and carries no splice.

HONEST BY CONSTRUCTION
----------------------
  * the ledger is FORWARD ONLY.  Lines before the anchor are not back-filled: a
    replay is published beside it as a labelled REPLAY block, never merged into
    the NAV series, because a number that starts as a backtest and grows a day at
    a time is still a backtest with a later cutoff;
  * a day already in the ledger is never rewritten (idempotent: re-running on the
    same bar is a no-op, printed as such);
  * slippage is not assumed to be zero silently -- rolls and the initial fill are
    printed as `n_rolls`/`entry_fill_assumed_at_close` so a reader can charge them;
  * losers are printed: a day the sleeve is under water shows a negative line, and
    the running drawdown is on the last row, not only in a backtest summary.

USAGE
    python scripts/idx_fut_carry_paper.py run          # accrue the missing bars
    python scripts/idx_fut_carry_paper.py show         # print the current ledger
    python scripts/idx_fut_carry_paper.py selftest     # offline checks
"""

import json
import math
import os
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import idx_fut_real_nav as RN  # the roll book, imported -- never re-implemented
import idx_fut_basis as BASE  # index panel reader + product->index map

LEDGER_DIR = os.path.join(ROOT, "results", "idx_fut_carry_paper")
LEDGER_PATH = os.path.join(LEDGER_DIR, "LEDGER.json")
LATEST_PATH = os.path.join(LEDGER_DIR, "latest.json")
DESK_PATH = os.path.join(ROOT, "results", "idx_fut_desk_sheet.json")

CAPITAL_CNY = 1_000_000.0   # the desk sheet's stated capital rung
REPLAY_YEARS = 1.0          # the labelled comparison window, not part of the NAV series


# ----------------------------------------------------------------- io helpers
def _load(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


# ------------------------------------------------------------- ticket reading
def read_ticket(desk):
    """The position the desk sheet publishes, per product.

    `margin_call_at_recommended_lots.lots` is the recommended size -- the one the
    page says survives its own drawdown.  `lots_for_capital` is what fits the
    margin rung, which is a different (larger, unfunded-tail) position; using it
    here would book a size the ticket itself flags as exposed to a call.
    """
    out = {}
    for prod in desk.get("candidates") or []:
        row = (desk.get("rows") or {}).get(prod)
        if not isinstance(row, dict) or row.get("status") != "ok":
            continue
        mc = row.get("margin_call_at_recommended_lots") or {}
        lots = mc.get("lots")
        if not lots:
            lots = row.get("lots_for_capital")
        if not lots:
            continue
        out[prod] = {
            "product": prod,
            "contract": row.get("held_contract"),
            "lots": int(lots),
            "multiplier": int(row.get("multiplier") or 0),
            "close": row.get("close"),
            "bar": row.get("cutoff"),
            "verdict": row.get("verdict"),
            "margin_per_lot_cny": row.get("margin_per_lot_cny"),
            "distance_to_call_pct": mc.get("fall_to_call_pct"),
        }
    return out


# ---------------------------------------------------------------- day series
def position_series(prod):
    """[(date, contract, close, old_contract_close_on_roll)] of the contract a deepest-OI
    book holds after each close.

    The calendar is the union of every cached contract's dates, which is exactly the
    calendar `active_path` walks; days where the held contract has no quote are kept
    with a None close so the accrue loop can skip them loudly instead of silently
    shortening the series (r1699 family).  On a roll day the outgoing contract's own
    close is carried in the fourth slot: the seam has to be priced on the leg that was
    actually held, and a forced roll (the old contract stopped quoting) hands back None
    so the caller books zero rather than a phantom gap between two contracts.
    """
    panel = RN.contract_panel(prod)
    if not panel:
        return [], []
    dates = sorted({d for series in panel.values() for d in series})
    held, rolls = RN.active_path(dates, panel)
    rows = []
    prev_sym = None
    for d in dates:
        sym = held.get(d)
        if not sym:
            continue
        px = (panel.get(sym) or {}).get(d)
        old_px = None
        if prev_sym and sym != prev_sym:
            old = (panel.get(prev_sym) or {}).get(d)
            old_px = old[0] if old else None
        rows.append((d, sym, px[0] if px else None, old_px))
        prev_sym = sym
    return rows, rolls


# ------------------------------------------------------------------- accrual
def accrue(acct, rows, force_anchor=None, idx_close=None):
    """Append the bars that are missing from this account's ledger.

    Returns (appended, note).  Never rewrites an existing line: the ledger's last
    date is the cut, and only rows after it are considered.  When the account is
    new, the anchor is the last already-complete bar (force_anchor overrides, for
    selftest), so the series starts at "today" rather than at the oldest contract.

    `idx_close` ({date: close}) turns on the index leg: the same lots held in the
    index outright.  It is published beside the futures line so `excess` (the
    discount converging) is separable from the index's own move -- the ticket's
    headline carry is an excess number, and a book that only prints absolute NAV
    makes a -12% year look like a broken carry when it is a working carry in a
    falling index.
    """
    lines = acct.setdefault("rows", [])
    if not lines:
        anchor_idx = len(rows) - 1
        if force_anchor is not None:
            for k, (d, _sym, _px, _opx) in enumerate(rows):
                if d >= force_anchor:
                    anchor_idx = k
                    break
        if not rows:
            return 0, "no rows"
        d0, sym0, px0 = rows[anchor_idx][:3]
        if px0 is None:
            return 0, "anchor bar has no close"
        lines.append({
            "date": d0, "contract": sym0, "close": px0,
            "pnl_cny": 0.0, "nav_cny": acct["capital_cny"], "event": "anchor",
        })
        acct["n_rolls"] = 0
        acct["notional_basis_cny"] = float(acct["lots"]) * float(acct["multiplier"]) * float(px0)
        ipx = (idx_close or {}).get(d0)
        acct["index_anchor"] = ipx
        if ipx:
            lines[-1]["index_close"] = ipx
            lines[-1]["index_pnl_cum_cny"] = 0.0
            lines[-1]["excess_pnl_cum_cny"] = 0.0
        return 1, "anchored at %s" % d0

    last = lines[-1]
    last_date = last["date"]
    idx = None
    for k, (d, _s, _p, _o) in enumerate(rows):
        if d == last_date:
            idx = k
            break
    if idx is None:
        return 0, "last ledger date %s is not on the contract calendar" % last_date

    appended = 0
    nav = float(last["nav_cny"])
    held_sym = last["contract"]
    prev_close = _previous_close(rows, idx, held_sym)
    prev_date = rows[idx][0]
    lots = acct["lots"]
    mult = acct["multiplier"]
    # the index leg is attached per line below (see _attach_index): what the same
    # lots would have made holding the index outright, so the reader can see how
    # much of the line is index and how much is the discount
    for d, sym, px, old_px in rows[idx + 1:]:
        if px is None:
            prev_date = d
            continue
        if sym != held_sym:
            # roll at this close: the outgoing leg is marked to its own close if it
            # quoted; a forced roll (it stopped quoting) books zero, never a gap
            # between two different contracts
            if old_px is not None and prev_close is not None:
                pnl = lots * mult * (old_px - prev_close)
            else:
                pnl = 0.0
            nav += pnl
            lines.append({
                "date": d, "contract": sym, "close": px,
                "pnl_cny": round(pnl, 2), "nav_cny": round(nav, 2),
                "event": "roll %s->%s" % (held_sym, sym),
                "seam_priced": old_px is not None,
                "prev_date": prev_date,
            })
            acct["n_rolls"] = int(acct.get("n_rolls", 0)) + 1
            held_sym = sym
            prev_close = px
        else:
            if prev_close is None:
                prev_date = d
                continue
            pnl = lots * mult * (px - prev_close)
            nav += pnl
            lines.append({
                "date": d, "contract": sym, "close": px,
                "pnl_cny": round(pnl, 2), "nav_cny": round(nav, 2),
                "event": None, "prev_date": prev_date,
            })
            prev_close = px
        _attach_index(lines[-1], acct, idx_close)
        prev_date = d
        appended += 1

    acct["nav_cny"] = round(nav, 2)
    acct["last_date"] = lines[-1]["date"]
    peak = max(l["nav_cny"] for l in lines)
    acct["peak_nav_cny"] = peak
    acct["drawdown_pct"] = round((nav / peak - 1.0) * 100.0, 4) if peak else 0.0
    return appended, "appended %d bar(s)" % appended


def _attach_index(line, acct, idx_close):
    """Attach the index leg to a ledger line: index P&L on the anchor notional, and the
    residual (futures P&L minus index P&L) that is the discount converging."""
    if not idx_close:
        return
    ipx = idx_close.get(line["date"])
    anchor = acct.get("index_anchor")
    notional0 = acct.get("notional_basis_cny")
    if ipx is None or not anchor or notional0 is None:
        return
    ipnl = notional0 * (ipx / anchor - 1.0)
    line["index_close"] = ipx
    line["index_pnl_cum_cny"] = round(ipnl, 2)
    line["excess_pnl_cum_cny"] = round((line["nav_cny"] - acct["capital_cny"]) - ipnl, 2)


def _previous_close(rows, idx, sym):
    """Close of `sym` on or before rows[idx] -- the mark the next day is measured from."""
    for k in range(idx, -1, -1):
        d, s, px = rows[k][:3]
        if s == sym and px is not None:
            return px
    return None


# -------------------------------------------------------------------- replay
def replay_block(prod, rows, lots, mult, idx_close=None, years=REPLAY_YEARS):
    """A LABELLED comparison: what the same position would have done over the last
    `years` of the contract calendar.  Never merged into the NAV series.

    Rolls follow the same seam rule as the forward ledger: the outgoing leg is marked
    to its own close when it quoted, a forced roll books zero.  The index leg is
    priced on the anchor notional so the block answers both questions a reader has:
    what the future made, and what of it was the discount rather than the index.
    """
    if not rows:
        return None
    cutoff = rows[-1][0]
    want = str(int(cutoff[:4]) - 1) + cutoff[4:]
    cand = [k for k, (d, _s, _p, _o) in enumerate(rows) if d >= want]
    start = cand[0] if cand else 0
    nav = CAPITAL_CNY
    peak = nav
    mdd = 0.0
    held_sym = rows[start][1]
    prev_close = rows[start][2]
    notional0 = float(lots) * float(mult) * float(rows[start][2] or 0.0)
    idx_anchor = (idx_close or {}).get(rows[start][0])
    idx_end = None
    n = 0
    for d, sym, px, old_px in rows[start + 1:]:
        if px is None:
            continue
        if sym != held_sym:
            if old_px is not None and prev_close is not None:
                nav += lots * mult * (old_px - prev_close)
            held_sym = sym
            prev_close = px
        else:
            if prev_close is None:
                prev_close = px
                continue
            nav += lots * mult * (px - prev_close)
            prev_close = px
        peak = max(peak, nav)
        if peak:
            mdd = min(mdd, nav / peak - 1.0)
        if idx_close and d in idx_close:
            idx_end = idx_close[d]
        n += 1
    index_pnl = None
    excess = None
    if idx_anchor and idx_end:
        index_pnl = notional0 * (idx_end / idx_anchor - 1.0)
        excess = (nav - CAPITAL_CNY) - index_pnl
    return {
        "label": "REPLAY_NOT_FORWARD",
        "window": [rows[start][0], cutoff],
        "days": n,
        "nav_start_cny": CAPITAL_CNY,
        "nav_end_cny": round(nav, 2),
        "total_pnl_cny": round(nav - CAPITAL_CNY, 2),
        "total_pct": round((nav / CAPITAL_CNY - 1.0) * 100.0, 3),
        "index_pnl_cny": None if index_pnl is None else round(index_pnl, 2),
        "excess_pnl_cny": None if excess is None else round(excess, 2),
        "excess_pct_of_capital": None if excess is None
        else round(excess / CAPITAL_CNY * 100.0, 3),
        "max_drawdown_pct": round(mdd * 100.0, 3),
        "note": "history with this position held daily -- a backtest, kept out of the "
                "forward series on purpose (see WHY THIS FILE EXISTS)",
    }


# -------------------------------------------------------------------- sizing
TARGET_VOL_PCT = 8.0
SIZING_PATH = os.path.join(LEDGER_DIR, "SIZING.json")


def per_lot_daily(rows, idx_close=None, years=REPLAY_YEARS):
    """Per-lot daily moves over the replay window, in index points, for the two arms.

    `fut_points` is what one lot made on the contract that was actually held: rolls are
    priced on the outgoing leg and a forced roll books zero -- the ledger's seam rule, not a
    second one.  `excess_points` is the same day minus what the same notional would have
    made in the index outright, so it is the residual the hedge would leave standing.
    """
    if not rows:
        return None
    cutoff = rows[-1][0]
    want = str(int(cutoff[:4]) - int(years)) + cutoff[4:]
    start = next((k for k, r in enumerate(rows) if r[0] >= want), 0)
    held = rows[start][1]
    prev = rows[start][2]
    prev_idx = (idx_close or {}).get(rows[start][0])
    fut_points, excess_points = [], []
    forced = 0
    for d, sym, px, old_px in rows[start + 1:]:
        if px is None:
            continue
        if sym != held:
            if old_px is None:
                forced += 1
                fut = 0.0
                notional = prev if prev is not None else px
            else:
                fut = (old_px - prev) if prev is not None else 0.0
                notional = old_px
            held, prev = sym, px
        else:
            fut = (px - prev) if prev is not None else 0.0
            notional = prev if prev is not None else px
            prev = px
        fut_points.append(fut)
        cur_idx = (idx_close or {}).get(d)
        if prev_idx and cur_idx and notional is not None:
            excess_points.append(fut - notional * (cur_idx / prev_idx - 1.0))
            prev_idx = cur_idx
        elif cur_idx:
            prev_idx = cur_idx
    return {"window": [rows[start][0], cutoff], "days": len(fut_points),
            "forced_rolls": forced, "fut_points": fut_points,
            "excess_points": excess_points}


def _ann_vol_cny(points, mult):
    """Annualised P&L vol of one lot, in CNY.  A short series is absent, not small."""
    if not points or len(points) < 20:
        return None
    return statistics.stdev(points) * float(mult) * math.sqrt(252.0)


def vol_target_arm(sigma_cny, capital, target_pct):
    """Lots that put this arm's annualised P&L vol at `target_pct` of capital.

    `lots_at_or_below_budget` floors on purpose: a fractional lot is not tradeable, and
    rounding up prints a position whose measured vol is above the budget it claims.
    """
    if not sigma_cny or sigma_cny <= 0 or not capital:
        return None
    float_lots = (target_pct / 100.0) * capital / sigma_cny
    return {
        "ann_vol_per_lot_cny": round(sigma_cny, 2),
        "vol_pct_of_capital_per_lot": round(sigma_cny / capital * 100.0, 4),
        "lots_float": round(float_lots, 4),
        "lots_at_or_below_budget": int(float_lots),
        "capital_for_one_lot_at_target": round(sigma_cny / (target_pct / 100.0), 2),
    }


def index_return_corr(a_code, b_code, years=REPLAY_YEARS):
    """Daily-return correlation of two index panels -- the basis leak a cross-index hedge
    leaves behind.  Absent panels print as None rather than as a flattering 1.0."""
    try:
        a = BASE.load_index(a_code)
        b = BASE.load_index(b_code)
    except Exception:
        return None
    days = sorted(set(a) & set(b))
    if len(days) < 61:
        return None
    cutoff = days[-1]
    want = str(int(cutoff[:4]) - int(years)) + cutoff[4:]
    days = [d for d in days if d >= want]
    if len(days) < 61:
        return None
    ra, rb = [], []
    for p, q in zip(days, days[1:]):
        if a.get(p) and b.get(p) and a.get(q) and b.get(q):
            ra.append(a[q] / a[p] - 1.0)
            rb.append(b[q] / b[p] - 1.0)
    if len(ra) < 60:
        return None
    ma = sum(ra) / len(ra)
    mb = sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra)
    vb = sum((y - mb) ** 2 for y in rb)
    if va <= 0 or vb <= 0:
        return None
    return round(cov / math.sqrt(va * vb), 4)


def hedge_block(prod, desk_rows):
    """What it costs to neutralise the index leg, read from the ticket's own bank of carry.

    Shorting an index future is not free: the short leg's own discount passes to the other
    side, so the hedge is priced at the short leg's carry.  A contract that sits at par is
    therefore the cheap hedge, and one that carries as much as the long leg gives the whole
    sleeve away.  Both numbers come from `gap_after_roll_cost_pp` on the ticket, which
    already nets that product's measured roll cost -- this face adds no estimator.
    """
    me = (desk_rows or {}).get(prod) or {}
    if not isinstance(me, dict):
        return {"status": "UNPRICED", "reason": "%s is not on the ticket" % prod}
    g = me.get("gap_after_roll_cost_pp") or {}
    long_carry = g.get("measured_median")
    basis = "measured_median"
    if long_carry is None:
        long_carry = g.get("file_floor")
        basis = "file_floor"
    if long_carry is None:
        return {"status": "UNPRICED",
                "reason": "the ticket prints no carry for %s, so no hedge can be priced" % prod}
    cands = []
    for other, r in sorted((desk_rows or {}).items()):
        if other == prod or not isinstance(r, dict) or r.get("status") != "ok":
            continue
        og = r.get("gap_after_roll_cost_pp") or {}
        cost = og.get("measured_median")
        cbasis = "measured_median"
        if cost is None:
            cost = og.get("file_floor")
            cbasis = "file_floor"
        if cost is None:
            continue
        cands.append({"hedge_product": other,
                      "cost_pp_per_year": round(float(cost), 3),
                      "cost_basis": cbasis})
    if not cands:
        return {"status": "UNPRICED",
                "reason": "no other product prints a carry, so no short leg can be priced"}
    best = min(cands, key=lambda c: (c["cost_pp_per_year"], c["hedge_product"]))
    net = float(long_carry) - best["cost_pp_per_year"]
    return {
        "status": "ok",
        "long_carry_pp": round(float(long_carry), 3),
        "long_carry_basis": basis,
        "candidates": cands,
        "cheapest": best,
        "net_carry_after_hedge_pp": round(net, 3),
        "verdict": ("HEDGE_KEEPS_THE_CARRY" if net >= 0.5 * float(long_carry)
                    else "HEDGE_GIVES_IT_AWAY"),
    }


def sizing_block(prod, rows, mult, capital, idx_close, desk_rows,
                 target_pct=TARGET_VOL_PCT):
    """The ticket's lots re-read under the 8% vol target, both arms, plus the hedge price.

    The ticket sizes on drawdown survival ("how many lots survive the drawdown it has
    already seen"), which is a different ruler from the book's 8% vol target.  Two arms are
    printed because they are two different trades: unhedged the line is mostly the index,
    hedged it is the discount -- and only the second one can be sized to a vol budget
    without pretending the index beta is free.
    """
    series = per_lot_daily(rows, idx_close)
    if not series or not series["days"]:
        return {"status": "NO_ROWS"}
    out = {
        "status": "ok",
        "window": series["window"],
        "days": series["days"],
        "forced_rolls": series["forced_rolls"],
        "target_pct": target_pct,
        "capital_cny": capital,
        "unhedged": vol_target_arm(_ann_vol_cny(series["fut_points"], mult), capital, target_pct),
        "hedged": vol_target_arm(_ann_vol_cny(series["excess_points"], mult), capital, target_pct),
        "hedge": hedge_block(prod, desk_rows),
    }
    hp = (out["hedge"] or {}).get("cheapest") or {}
    if hp.get("hedge_product"):
        out["hedge"]["index_corr_with_long"] = index_return_corr(
            BASE.PAIRS[prod][0], BASE.PAIRS[hp["hedge_product"]][0])
    return out


# ----------------------------------------------------------------------- run
def run(now=None, write=True):
    desk = _load(DESK_PATH)
    if not desk:
        print("desk sheet missing: %s" % DESK_PATH)
        return 2
    ticket = read_ticket(desk)
    if not ticket:
        print("desk sheet publishes no sleeve candidate -- nothing to book")
        return 2

    ledger = _load(LEDGER_PATH) or {}
    ledger.setdefault("kind", "idx_fut_carry_paper")
    accounts = ledger.setdefault("accounts", {})
    notes = []
    total_appended = 0
    sizing = {}
    desk_rows = desk.get("rows") or {}

    for prod, t in sorted(ticket.items()):
        rows, rolls = position_series(prod)
        if not rows:
            notes.append("%s: no contract panel" % prod)
            continue
        idx_close = None
        try:
            idx_close = BASE.load_index(BASE.PAIRS[prod][0])
        except Exception as exc:  # an absent index panel prints as a one-line note
            notes.append("%s: index panel unavailable (%s) -- excess leg off" % (prod, exc))
        acct = accounts.get(prod)
        if acct is None:
            acct = {
                "product": prod,
                "capital_cny": CAPITAL_CNY,
                "lots": t["lots"],
                "multiplier": t["multiplier"],
                "source_verdict": t["verdict"],
                "entry_fill_assumed_at_close": True,
                "rows": [],
            }
            accounts[prod] = acct
        # the ticket may have resized (a new verdict, a tighter call distance): record
        # what the ledger was booked at, and note a change instead of rewriting history
        if acct["lots"] != t["lots"] or acct["multiplier"] != t["multiplier"]:
            notes.append("%s: ticket changed lots %s->%s, multiplier %s->%s (ledger keeps "
                         "its booked size; resize is a separate decision)"
                         % (prod, acct["lots"], t["lots"], acct["multiplier"], t["multiplier"]))
        n, note = accrue(acct, rows, idx_close=idx_close)
        total_appended += n
        notes.append("%s: %s (%s)" % (prod, note, t["contract"]))
        acct["replay"] = replay_block(prod, rows, acct["lots"], acct["multiplier"],
                                      idx_close=idx_close)
        sizing[prod] = sizing_block(prod, rows, acct["multiplier"], acct["capital_cny"],
                                    idx_close, desk_rows)
        s_hedged = (sizing[prod].get("hedged") or {})
        if s_hedged.get("lots_float") is not None and acct["lots"]:
            notes.append("%s: ticket %d lot(s) vs %.2f at the %g%% vol target (hedged arm)"
                         % (prod, acct["lots"], s_hedged["lots_float"], TARGET_VOL_PCT))

    ledger["evidence_cutoff"] = str(
        (desk.get("evidence_cutoff") or datetime.now().strftime("%Y-%m-%d")))
    # the judgement's cutoff and the bars' cutoff are not the same date: the ticket is
    # judged on the continuous panel while the contract cache can lag it by a few sessions.
    # Printing both keeps a 11-16 ticket from reading as an 11-16 fill.
    ledger["contract_cutoff"] = max(
        [(a.get("rows") or [{}])[-1].get("date") or "" for a in accounts.values()] or [""]) or None
    ledger["generated"] = (now or datetime.now()).strftime("%Y-%m-%dT%H:%M:%S")
    ledger["source_face"] = "results/idx_fut_desk_sheet.json"
    ledger["ticket"] = ticket
    ledger["sizing"] = sizing
    ledger["note"] = ("forward lines only; a replay block is published beside each "
                      "account and never merged into its NAV series")

    if write:
        _dump(LEDGER_PATH, ledger)
        latest = _latest(ledger)
        _dump(LATEST_PATH, latest)
        _dump(SIZING_PATH, {"kind": "idx_fut_carry_paper_sizing",
                            "evidence_cutoff": ledger.get("evidence_cutoff"),
                            "generated": ledger.get("generated"),
                            "target_pct": TARGET_VOL_PCT,
                            "source_face": "results/idx_fut_desk_sheet.json",
                            "accounts": sizing,
                            "note": "the ticket sizes on drawdown survival; this face "
                                    "re-reads the same position under the book's 8% vol "
                                    "target, unhedged and hedged, and prices the hedge"})
        write_doc(latest, sizing)
    print("idx_fut_carry_paper: %d bar(s) appended" % total_appended)
    for n in notes:
        print("  " + n)
    return 0


DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_PAPER.md")


def write_doc(latest, sizing=None):
    """One page, no prose beyond what the numbers need: a desk reads this, not a report."""
    acc = latest.get("accounts") or {}
    if not acc:
        return
    sizing = sizing if sizing is not None else (latest.get("sizing") or {})
    out = []
    out.append("# the carry sleeve, booked forward")
    out.append("")
    out.append("evidence cutoff: **%s** | contract bars to **%s** | generated %s | "
               "source judgement: `results/idx_fut_desk_sheet.json`"
               % (latest.get("evidence_cutoff"), latest.get("contract_cutoff") or "--",
                  latest.get("generated")))
    out.append("")
    out.append("The two dates are printed because they are two dates: the ticket is judged "
               "on the continuous panel and the contract cache can lag it by a few sessions, "
               "so a ticket stamped with the judgement date is not a fill at that date.")
    out.append("")
    out.append("Forward lines only.  The forward series starts at the anchor below and "
               "grows one bar a day; the replay block is labelled and never merged into it.")
    out.append("")
    out.append("## forward (what this position has actually made since the anchor)")
    out.append("")
    out.append("| product | contract | lots | notional | since | bars | NAV (CNY) | "
               "P&L | index leg | discount leg | max DD | rolls |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for prod, a in sorted(acc.items()):
        notional = a["lots"] * a["multiplier"]
        out.append("| %s | %s | %d | %.0f x spot | %s | %d | %s | %+.4f%% | %s | %s | %.3f%% | %d |"
                   % (prod, a["contract"], a["lots"], notional, a["since"], a["bars"],
                      "{:,.2f}".format(a["nav_cny"]), a["pnl_pct"],
                      _fmt_cny(a.get("index_pnl_cum_cny")),
                      _fmt_cny(a.get("excess_pnl_cum_cny")),
                      a.get("drawdown_pct") or 0.0, a["n_rolls"]))
    out.append("")
    out.append("## replay (the same position over the last %g year -- a backtest, kept apart)"
               % REPLAY_YEARS)
    out.append("")
    out.append("| product | window | days | total | of which index | of which discount | max DD |")
    out.append("|---|---|---|---|---|---|---|")
    for prod, a in sorted(acc.items()):
        rb = a.get("replay") or {}
        if not rb:
            continue
        out.append("| %s | %s..%s | %d | %+.2f%% of capital | %s | %s | %.2f%% |"
                   % (prod, rb["window"][0], rb["window"][1], rb["days"], rb["total_pct"],
                      _fmt_pct_of_capital(rb.get("index_pnl_cny"), a["capital_cny"]),
                      _fmt_pct_of_capital(rb.get("excess_pnl_cny"), a["capital_cny"]),
                      rb["max_drawdown_pct"]))
    out.append("")
    out.append("**Read the two legs together.**  The ticket's headline carry is an *excess* "
               "number: it is what the future earns over the index, not what the account "
               "earns.  At this size the index leg dominates the absolute line, so a year "
               "that looks like a broken carry can be a working carry inside a falling "
               "index -- and the reverse.  Sizing is therefore a decision about the index "
               "exposure, not about the discount.")
    out.append("")
    out.append("## the same position at the %g%% vol target (two arms, because they are two trades)"
               % TARGET_VOL_PCT)
    out.append("")
    wins = sorted({tuple(s.get("window") or []) for s in sizing.values()
                   if (s or {}).get("window")})
    if wins:
        out.append("Vol is measured on the same replay window as the block above (%s..%s, "
                   "%d bar(s)), not on the full contract history, so it answers 'what would "
                   "this size have put on the table this year' rather than 'how volatile is "
                   "the discount forever'." % (wins[0][0], wins[0][1],
                                               (list(sizing.values())[0].get("days") or 0)))
        out.append("")
    out.append("| product | arm | vol of 1 lot | lots for %g%% | lots at or below | "
               "capital for 1 lot | this ticket's lots | vol of those lots |"
               % TARGET_VOL_PCT)
    out.append("|---|---|---|---|---|---|---|---|")
    for prod, a in sorted(acc.items()):
        sz = sizing.get(prod) or {}
        tick = a["lots"]
        for arm, label in (("unhedged", "index + carry"), ("hedged", "carry only")):
            row = sz.get(arm) or {}
            if not row:
                continue
            vol_of_ticket = "%.2f%%" % (tick * row["vol_pct_of_capital_per_lot"])
            out.append("| %s | %s | %s CNY/yr (%.2f%% of capital) | %.2f | %d | %s | %d | %s |"
                       % (prod, label, "{:,.0f}".format(row["ann_vol_per_lot_cny"]),
                          row["vol_pct_of_capital_per_lot"], row["lots_float"],
                          row["lots_at_or_below_budget"],
                          "{:,.0f}".format(row["capital_for_one_lot_at_target"]),
                          tick, vol_of_ticket))
    out.append("")
    out.append("## what the hedge costs (the short leg's carry, not an estimate)")
    out.append("")
    out.append("| product | long carry | cheapest hedge | hedge cost | net carry | verdict | "
               "index corr |")
    out.append("|---|---|---|---|---|---|---|")
    any_hedge = False
    for prod, a in sorted(acc.items()):
        hb = ((sizing.get(prod) or {}).get("hedge") or {})
        if hb.get("status") != "ok":
            continue
        any_hedge = True
        best = hb.get("cheapest") or {}
        corr = hb.get("index_corr_with_long")
        out.append("| %s | %.3f pp/yr | short %s | %.3f pp/yr | %+.3f pp/yr | %s | %s |"
                   % (prod, hb["long_carry_pp"], best.get("hedge_product"),
                      best.get("cost_pp_per_year"), hb["net_carry_after_hedge_pp"],
                      hb["verdict"], "--" if corr is None else "%.3f" % corr))
    if not any_hedge:
        out.append("| -- | -- | -- | -- | -- | UNPRICED | -- |")
    out.append("")
    out.append("**Read the two arms together.**  The ticket sizes on drawdown survival -- "
               "how many lots survive the drawdown this sleeve has already seen.  That is a "
               "different ruler from the book's %g%% vol target: unhedged, one lot is mostly "
               "index beta, so the target buys a fraction of a lot; hedged to the discount it "
               "buys a whole lot or more.  The hedge is priced at the short leg's own carry, "
               "which is why the cheap hedge is the contract sitting nearest par -- shorting "
               "a leg that carries as much as the long one hands the sleeve away, and that "
               "shows up as a negative net carry rather than as a caveat." % TARGET_VOL_PCT)
    out.append("")
    out.append("Basis risk is printed as the daily-return correlation of the two indices: a "
               "cross-index hedge leaves that residual behind, and it is not netted out of "
               "the net-carry column.")
    out.append("")
    out.append("Entry is filled at the anchor close and rolls are booked at the same close "
               "(no slippage assumed, printed as `entry_fill_assumed_at_close` and "
               "`n_rolls` so a reader can charge them).")
    out.append("")
    with open(DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


def _fmt_cny(v):
    if v is None:
        return "--"
    return "{:+,.0f}".format(v)


def _fmt_pct_of_capital(v, capital):
    if v is None or not capital:
        return "--"
    return "%+.2f%%" % (v / capital * 100.0)


def _latest(ledger):
    out = {
        "kind": "idx_fut_carry_paper_latest",
        "evidence_cutoff": ledger.get("evidence_cutoff"),
        "contract_cutoff": ledger.get("contract_cutoff"),
        "generated": ledger.get("generated"),
        "sizing": ledger.get("sizing") or {},
        "accounts": {},
    }
    for prod, acct in sorted((ledger.get("accounts") or {}).items()):
        rows = acct.get("rows") or []
        if not rows:
            continue
        last = rows[-1]
        out["accounts"][prod] = {
            "contract": last["contract"],
            "lots": acct["lots"],
            "multiplier": acct["multiplier"],
            "capital_cny": acct["capital_cny"],
            "nav_cny": last["nav_cny"],
            "pnl_cny": round(last["nav_cny"] - acct["capital_cny"], 2),
            "pnl_pct": round((last["nav_cny"] / acct["capital_cny"] - 1.0) * 100.0, 4),
            "index_pnl_cum_cny": last.get("index_pnl_cum_cny"),
            "excess_pnl_cum_cny": last.get("excess_pnl_cum_cny"),
            "since": rows[0]["date"],
            "bars": len(rows),
            "drawdown_pct": acct.get("drawdown_pct"),
            "n_rolls": acct.get("n_rolls", 0),
            "replay": acct.get("replay"),
        }
    return out


# ------------------------------------------------------------------ selftest
def selftest():
    ok = 0
    bad = []

    def check(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            bad.append(name)

    # 1. ticket reading uses the recommended-lots block, not the margin rung
    desk = {"candidates": ["IC"], "rows": {"IC": {
        "status": "ok", "held_contract": "IC2612", "close": 6375.0, "cutoff": "2026-11-13",
        "multiplier": 200, "lots_for_capital": 6, "verdict": "SLEEVE_CANDIDATE",
        "margin_call_at_recommended_lots": {"lots": 4, "fall_to_call_pct": 12.62}}}}
    t = read_ticket(desk)
    check("L1 recommended lots win", t["IC"]["lots"] == 4)
    check("L2 contract carried", t["IC"]["contract"] == "IC2612")

    # 2. accrue anchors at the last bar and books zero on the anchor day
    acct = {"capital_cny": 1e6, "lots": 4, "multiplier": 200, "rows": []}
    rows = [("2026-11-10", "IC2612", 6300.0, None), ("2026-11-11", "IC2612", 6320.0, None),
            ("2026-11-12", "IC2612", 6350.0, None)]
    n, _ = accrue(acct, rows)
    check("L3 one anchor line", n == 1 and len(acct["rows"]) == 1)
    check("L4 anchor nav is capital", acct["rows"][0]["nav_cny"] == 1e6)

    # 3. idempotent: same rows again adds nothing
    n2, note2 = accrue(acct, rows)
    check("L5 idempotent on same bar", n2 == 0 and len(acct["rows"]) == 1)

    # 4. next bar books lots*mult*price change
    rows2 = rows + [("2026-11-13", "IC2612", 6375.0, None)]
    n3, _ = accrue(acct, rows2)
    check("L6 one bar appended", n3 == 1)
    check("L7 pnl = 4*200*25", abs(acct["rows"][-1]["pnl_cny"] - 20000.0) < 1e-6)
    check("L8 nav = 1.02m", abs(acct["rows"][-1]["nav_cny"] - 1020000.0) < 1e-6)

    # 5. a quoted roll prices the outgoing leg to the seam, then hands over
    rows3 = rows2 + [("2026-11-14", "IC2701", 6500.0, 6400.0)]
    acct2 = {"capital_cny": 1e6, "lots": 4, "multiplier": 200, "rows": []}
    accrue(acct2, rows2)            # anchor 11-12, then 11-13
    n4, _ = accrue(acct2, rows3)
    last = acct2["rows"][-1]
    check("L9 roll line appended", n4 == 1 and last["event"] and "roll" in last["event"])
    check("L10 roll counts", acct2["n_rolls"] == 1)
    # seam on the old contract: 4*200*(6400-6375) = +20,000 -- not the 6500-6375 gap
    check("L11 seam priced on the held leg", abs(last["pnl_cny"] - 20000.0) < 1e-6)

    # 5b. a forced roll (outgoing leg not quoted) books zero, never a phantom gap
    acct2b = {"capital_cny": 1e6, "lots": 4, "multiplier": 200, "rows": []}
    accrue(acct2b, rows2)
    accrue(acct2b, rows2 + [("2026-11-14", "IC2701", 6500.0, None)])
    check("L11b forced seam books zero", abs(acct2b["rows"][-1]["pnl_cny"]) < 1e-6)

    # 6. a losing bar shows a negative line (never clamped)
    acct3 = {"capital_cny": 1e6, "lots": 4, "multiplier": 200, "rows": []}
    accrue(acct3, rows2)
    accrue(acct3, rows2 + [("2026-11-14", "IC2612", 6300.0, None)])
    check("L12 losses printed", acct3["rows"][-1]["pnl_cny"] < 0)

    # 7. drawdown is on the account, not only in a summary
    check("L13 drawdown negative after a loss", acct3.get("drawdown_pct", 0) < 0)

    # 8. replay is labelled and kept out of the NAV series
    rb = replay_block("IC", rows2, 4, 200)
    check("L14 replay labelled", rb and rb["label"] == "REPLAY_NOT_FORWARD")
    check("L15 replay not in rows", all("REPLAY" not in json.dumps(l) for l in acct2["rows"]))

    # 9. latest view reports the last line, not a recomputed one
    led = {"evidence_cutoff": "2026-11-13", "generated": "x",
           "accounts": {"IC": acct2}}
    lv = _latest(led)
    check("L16 latest reads last line",
          abs(lv["accounts"]["IC"]["nav_cny"] - acct2["rows"][-1]["nav_cny"]) < 1e-6)

    # 10. an empty desk sheet is refused, not silently booked
    check("L17 empty ticket refused", read_ticket({"candidates": [], "rows": {}}) == {})

    # 11. the per-lot series is close-to-close on the held leg, no anchor dependence
    ser = per_lot_daily(rows2, None)
    check("L18 futures points are close-to-close", abs(ser["fut_points"][0] - 20.0) < 1e-9)
    check("L18b futures points end on the last bar", abs(ser["fut_points"][-1] - 25.0) < 1e-9)

    # 12. the hedged arm is priced on the same notional, not on the futures move
    idx = {"2026-11-12": 100.0, "2026-11-13": 110.0}
    ser2 = per_lot_daily(rows2, idx)
    check("L19 excess leg nets the index out",
          abs(ser2["excess_points"][-1] - (25.0 - 6350.0 * 0.1)) < 1e-6)

    # 13. vol scales with the moves, so the lot count scales inversely
    va = _ann_vol_cny([1.0, -1.0] * 30, 200)
    vb = _ann_vol_cny([2.0, -2.0] * 30, 200)
    check("L20 doubling the moves doubles the vol", abs(vb - 2.0 * va) < 1e-6)
    check("L20b doubling the vol halves the lots",
          abs(vol_target_arm(va, 1e6, 8.0)["lots_float"]
              - 2.0 * vol_target_arm(vb, 1e6, 8.0)["lots_float"]) < 1e-9)

    # 14. the floored lot count never claims more vol than the budget
    arm = vol_target_arm(60000.0, 1e6, 8.0)
    check("L21 floor stays under the budget",
          arm["lots_at_or_below_budget"] <= arm["lots_float"]
          and arm["lots_at_or_below_budget"] * 60000.0 / 1e6 * 100.0 <= 8.0 + 1e-9)
    check("L22 capital for one lot is sigma over the target",
          abs(arm["capital_for_one_lot_at_target"] - 60000.0 / 0.08) < 1e-6)

    # 15. the hedge is the cheapest short leg, not the one carrying the most
    desk3 = {"IC": {"status": "ok", "gap_after_roll_cost_pp": {"measured_median": 6.856}},
             "IF": {"status": "ok", "gap_after_roll_cost_pp": {"measured_median": 0.65}},
             "IM": {"status": "ok", "gap_after_roll_cost_pp": {"measured_median": 8.068}}}
    hb = hedge_block("IC", desk3)
    check("L23 cheapest hedge wins", hb["cheapest"]["hedge_product"] == "IF")
    check("L23b net carry subtracts the hedge cost",
          abs(hb["net_carry_after_hedge_pp"] - (6.856 - 0.65)) < 1e-3)
    check("L24 a hedge keeps the carry", hb["verdict"] == "HEDGE_KEEPS_THE_CARRY")

    # 16. a short leg that carries as much as the long one gives the sleeve away
    desk4 = {"IC": desk3["IC"], "IM": desk3["IM"]}
    hb4 = hedge_block("IC", desk4)
    check("L25 expensive hedge is refused", hb4["verdict"] == "HEDGE_GIVES_IT_AWAY")
    check("L26 no carry face is UNPRICED, not zero",
          hedge_block("IC", {"IC": {"status": "ok"}})["status"] == "UNPRICED")
    check("L27 no rows is NO_ROWS, not a size",
          sizing_block("IC", [], 200, 1e6, None, desk3)["status"] == "NO_ROWS")

    total = ok + len(bad)
    if bad:
        print("idx_fut_carry_paper selftest %d/%d FAILED: %s" % (ok, total, ", ".join(bad)))
        return 1
    print("idx_fut_carry_paper selftest %d/%d" % (ok, total))
    return 0


# ------------------------------------------------------------ show (read-only)
def show():
    led = _load(LATEST_PATH) or _latest(_load(LEDGER_PATH) or {})
    if not led or not led.get("accounts"):
        print("no ledger yet -- run first")
        return 0
    print("idx_fut_carry_paper @ %s (cutoff %s)"
          % (led.get("generated"), led.get("evidence_cutoff")))
    for prod, a in sorted(led["accounts"].items()):
        print("  %s %s %d lot(s) x%d | nav %.2f (%+.4f%%) since %s, %d bar(s), dd %.3f%%, rolls %d"
              % (prod, a["contract"], a["lots"], a["multiplier"], a["nav_cny"],
                 a["pnl_pct"], a["since"], a["bars"], a["drawdown_pct"] or 0.0,
                 a["n_rolls"]))
        rb = a.get("replay") or {}
        if rb:
            print("     REPLAY %s..%s: %+.3f%% over %d day(s), mdd %.3f%% (not forward)"
                  % (rb["window"][0], rb["window"][1], rb["total_pct"], rb["days"],
                     rb["max_drawdown_pct"]))
            if rb.get("excess_pct_of_capital") is not None:
                print("       of which index %+.2f%% and discount %+.2f%% of capital"
                      % (rb["index_pnl_cny"] / a["capital_cny"] * 100.0,
                         rb["excess_pct_of_capital"]))
        sz = (led.get("sizing") or {}).get(prod) or {}
        for arm, label in (("unhedged", "index+carry"), ("hedged", "carry only")):
            row = sz.get(arm) or {}
            if not row:
                continue
            print("     %-11s vol %6.2f%% of capital per lot -> %.2f lot(s) for %g%% "
                  "(this ticket's %d lot(s) run %.2f%%)"
                  % (label, row["vol_pct_of_capital_per_lot"], row["lots_float"],
                     row.get("target_pct", TARGET_VOL_PCT), a["lots"],
                     a["lots"] * row["vol_pct_of_capital_per_lot"]))
        hb = sz.get("hedge") or {}
        if hb.get("status") == "ok":
            print("     hedge: short %s costs %.3f pp/yr -> net carry %+.3f pp/yr %s"
                  % (hb["cheapest"]["hedge_product"], hb["cheapest"]["cost_pp_per_year"],
                     hb["net_carry_after_hedge_pp"], hb["verdict"]))
        elif hb:
            print("     hedge: %s (%s)" % (hb.get("status"), hb.get("reason")))
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return run()
    if cmd == "show":
        return show()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
