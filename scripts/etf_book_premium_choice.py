"""A one-off cost and a per-window cost cannot be compared without the holding period.

r1773 turned "stretched" into a rule: a leg paying more than 3.0 pp over its own basket must
find a same-class, same-market twin at least 1.0 pp cheaper, and the expected-return give-up
may not exceed 2.0 **pp per year**. On the 2026-11-16 ticket that rule refused the swap
(159655 -> 159529 saves 1,506 CNY one-off but gives up 2.12 pp/yr against the 2.00 cap).

That verdict is arithmetically right and horizon-blind. The saving is paid once, at the
order; the give-up is earned back per **decision window**, and this book replaces its seats
most windows. Annualising a per-window cost silently assumes the position is held for a
year. Read over the window the book actually keeps a seat, the same two numbers say the
opposite thing:

    saving   1,506 CNY, once
    give-up  86,286 x score_gap x slope_per_window = 145 CNY per 20-bar window
    => the swap pays for itself if the premium gap closes by more than p* = 9.6% before exit

So this face prints BOTH roads over BOTH rulers and lets the disagreement stand in the open:

  * ROAD A -- buy as printed, pay the premium.
  * ROAD B -- buy the same-market twin, pay less, rank lower.
  * ROAD C -- drop the leg and let the money sit in the ticket's own cash leg.

Every road is priced in the currency it costs in (CNY once, CNY per window), never added,
and the holding window is MEASURED from the book's own decision path (mean run length of a
seat), not asserted. What the face cannot know is whether the premium converges at exit --
that is why every road prints its break-even convergence probability instead of a net value:
a probability is a belief the operator can argue with, a net value would be a belief this
face invented.

  python scripts/etf_book_premium_choice.py paths       # today's three roads (default)
  python scripts/etf_book_premium_choice.py --check     # re-derive the published arithmetic
  python scripts/etf_book_premium_choice.py --selftest

Outputs:
  results/etf_book_premium_choice.json
  research/ETF_BOOK_PREMIUM_CHOICE.md

Exploratory: not a verdict on the book, not investment advice, no ledger booking.
"""
import glob
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts import etf_composite_pf as F            # noqa: E402
from scripts import etf_book_premium_swap as P       # noqa: E402

RESULTS = os.path.join(ROOT, "results")
OUT_JSON = os.path.join(RESULTS, "etf_book_premium_choice.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_PREMIUM_CHOICE.md")
ORDER_DIR = os.path.join(RESULTS, "etf_book_order")
SWAP_SCRIPT = os.path.join(ROOT, "scripts", "etf_book_premium_swap.py")

# --- rebuild gate (r1835): the CEO page now quotes this face every round, so the chain has to
# carry a producer -- and a build costs ~50s for inputs that move about once a trading day (one
# ticket, one snapshot csv).  The key is INPUTS ONLY: ticket bytes, snapshot bytes, a
# name/size/mtime census of the daily panel, and the bytes of this script and the swap module it
# imports.  No wall clock: a key that moves with the clock is a gate that never fires (r1832).
# Skipping leaves both files untouched, so the only thing a reader can lose is the wait.


def _sha_file(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def inputs_sig(ticket_path=None, snap_path=None):
    """The bytes a rebuild would read; the ticket and the snapshot are named, not guessed."""
    if ticket_path is None:
        _t, ticket_path = P.latest_ticket()
    if snap_path is None:
        t, _tp = P.latest_ticket()
        asof = t.get("as_of") or t.get("evidence_cutoff")
        _prem, _names, snap_path = P.load_premium_snapshot(asof)
    from config import PATHS
    daily_dir = PATHS.daily_dir
    names = hashlib.sha256()
    n = size = 0
    newest = 0
    if daily_dir and os.path.isdir(daily_dir):
        for fn in sorted(os.listdir(daily_dir)):
            if not fn.endswith(".csv"):
                continue
            try:
                st = os.stat(os.path.join(daily_dir, fn))
            except OSError:
                continue
            n += 1
            size += st.st_size
            newest = max(newest, st.st_mtime_ns)
            names.update(fn.encode("utf-8"))
    return {
        "panel_files": n,
        "panel_bytes": size,
        "panel_newest_mtime_ns": newest,
        "panel_names_sha": names.hexdigest()[:16],
        "ticket": (os.path.basename(ticket_path) if ticket_path else None),
        "ticket_sha": _sha_file(ticket_path),
        "snapshot": (os.path.basename(snap_path) if snap_path else None),
        "snapshot_sha": _sha_file(snap_path),
        "script_sha": _sha_file(os.path.abspath(__file__)),
        "swap_script_sha": _sha_file(SWAP_SCRIPT),
        # r2219: the denominator-date evidence is an input, not a comment -- if it moves,
        # a face priced without it is stale (r1311 class)
        "nav_evidence_sha": _sha_file(NAV_EVIDENCE),
    }


def input_key(sig):
    return hashlib.sha256(json.dumps(sig, sort_keys=True).encode("utf-8")).hexdigest()


def gate_decision(prev, key):
    """Rebuild unless the face on disk already answered exactly these inputs.

    Conservative on purpose: a missing face, a face written before this key existed, or any
    input byte moving all rebuild.  A failed read is never "same inputs".
    """
    if not isinstance(prev, dict) or not prev:
        return False, "NO_PREVIOUS_FACE"
    stored = (prev.get("inputs") or {}).get("key")
    if not stored:
        return False, "PREVIOUS_FACE_HAS_NO_INPUT_KEY"
    if stored != key:
        return False, "INPUTS_CHANGED"
    return True, "SAME_INPUTS"


# --- which day is the premium's denominator from? (r2219) -------------------------------
# A premium is price / NAV - 1. r2213 proved the DENOMINATOR's own date is not the batch
# stamp: on the 2026-11-27 session 1,371 board rows and 1,157 dated sina rows sat on that
# day's path, 8 and 115 on the previous close. This face multiplies that premium by CNY and
# turns it into "swap this leg" advice, so it has to ask the same question -- otherwise the
# swap on 159655 (premium 10.36%, 8,999 CNY) is priced off a NAV published 2026-11-28, a
# number that did not exist when the 2026-11-27 decision was taken.
NAV_EVIDENCE = os.path.join(RESULTS, "etf_nav", "source_dating.json")


def load_nav_evidence(asof):
    """Per-code proof of which day a premium's denominator is from (r2213's face, reused).

    The evidence face must name the session this ticket was priced on, else it is another
    session's proof and proves nothing here (r2215's `evidence-face-other-session`).
    """
    if not NAV_EVIDENCE or not os.path.exists(NAV_EVIDENCE):
        return {"status": "face missing", "by_symbol": {}}
    try:
        with open(NAV_EVIDENCE, "r", encoding="utf-8") as f:
            face = json.load(f)
    except (OSError, ValueError) as exc:
        return {"status": "unreadable: %s" % exc, "by_symbol": {}}
    session = face.get("board_session")
    want = str(asof)[:10] if asof else None
    if want and session != want:
        return {"status": "other session", "session": session, "by_symbol": {}}
    by = {}
    for r in face.get("rows") or []:
        code = str(r.get("code") or "")
        if not code:
            continue
        b, s = r.get("board_position"), r.get("sina_position")
        if b == "SAME_SESSION" and s == "SAME_SESSION":
            word = "same-session"
        elif "PREV_SESSION" in (b, s):
            word = "prev-session"
        else:
            word = "unproven"
        beyond = None
        d = r.get("sina_nav_date")
        if d and session and d > session:
            try:
                beyond = int((pd.Timestamp(d) - pd.Timestamp(session)).days)
            except (TypeError, ValueError):
                beyond = None
        by[code] = {"status": word, "board_position": b, "sina_position": s,
                    "sina_nav_date": d, "board_nav": r.get("board_nav"),
                    "sina_nav": r.get("sina_nav"), "days_beyond_session": beyond}
    return {"status": "ok", "session": session, "by_symbol": by}


def face_verdict(legs):
    """The face word follows from the legs, and a swap needs a PROVEN denominator.

    Pure, so check() can re-derive it and a selftest can drive it with fixtures.
    """
    words = [r.get("verdict") for r in legs]
    unproven = [r for r in legs if r.get("verdict") == "STRETCHED_ON_UNPROVEN_NAV"]
    if "SWAP_AT_BOOK_HORIZON" in words:
        return ("RULERS_DISAGREE_SWAP_AT_HORIZON"
                if any(r.get("rulers_disagree") for r in legs) else "RULERS_AGREE_SWAP")
    if unproven:
        # every stretched leg on this sheet rests on a denominator this face cannot place on
        # its own session: the arithmetic still prints, the advice does not
        return "NO_PROVEN_SWAP_LEG"
    if "HOLD_AT_BOOK_HORIZON" in words:
        return "RULERS_AGREE_HOLD"
    if "NOT_PRICED" in words:
        return "NOT_PRICED"
    if words and all(w == "NOT_STRETCHED" for w in words):
        return "NO_STRETCHED_LEG"
    return "UNPRICED"


# --- frozen before the first run, echoed into the payload -------------------------------
REBAL = 20                  # the book's own decision grid (bars between decisions)
HORIZON = P.HORIZON         # 20 bars: one window is one decision period
N_HOLD = 5                  # the ticket's aggressive end (5 names)
START = "2020-01-01"        # the book's own start, so the tenure is measured on its history
P_CONVERGE_FLOOR = 0.50     # a swap must pay for itself if the gap closes at least half the time
BARS_PER_YEAR = 252.0
WINDOW_YEARS = HORIZON / BARS_PER_YEAR


# ------------------------------------------------------------------ the book's own window
def seat_tenure(close, openp, amt, score, rebal=REBAL, n_hold=N_HOLD, start=START,
                min_amt=None, min_hist=None):
    """Mean number of decision windows a seat is kept, read off the book's own selections.

    The selection rule is the engine's default (`score[day].nlargest(n)`); sizing, cost and
    T+1 are irrelevant here because a seat's lifetime is decided by selection alone. The
    fresh-share read is the same one r1768 published (first decision counted as all-fresh,
    because nothing is held before it), so the two faces can be cross-checked.
    """
    min_amt = F.MIN_AMT if min_amt is None else min_amt
    min_hist = F.MIN_HIST if min_hist is None else min_hist
    hist = close.notna().cumsum()
    elig = (amt >= min_amt) & (hist >= min_hist)
    sc = score.where(elig)
    dates = [d for d in openp.index if d >= pd.Timestamp(start)]
    prev, run, spans = set(), {}, []
    decisions = seats = fresh = 0
    for i in range(0, max(0, len(dates) - 1), rebal):
        d = dates[i]
        row = sc.loc[d].dropna()
        if len(row) < n_hold:
            continue
        cur = set(row.nlargest(n_hold).index)
        decisions += 1
        seats += len(cur)
        fresh += len(cur - prev)
        for nm in cur:
            run[nm] = run.get(nm, 0) + 1
        for nm in prev - cur:
            spans.append(run.pop(nm))
        prev = cur
    spans.extend(run.values())          # seats still held at the last decision, counted as seen
    arr = np.asarray(spans, dtype=float) if spans else np.zeros(0)
    mean_dec = float(arr.mean()) if arr.size else None
    return {
        "decisions": decisions,
        "seat_periods": seats,
        "fresh_seats": fresh,
        "fresh_share": (round(fresh / float(seats), 4) if seats else None),
        "seats_closed": int(arr.size),
        "mean_tenure_decisions": None if mean_dec is None else round(mean_dec, 4),
        "median_tenure_decisions": (float(np.median(arr)) if arr.size else None),
        "max_tenure_decisions": (int(arr.max()) if arr.size else None),
        "share_held_one_window": (round(float((arr <= 1).mean()), 4) if arr.size else None),
        "tenure_years": (round(mean_dec * WINDOW_YEARS, 4) if mean_dec is not None else None),
        "window_years": round(WINDOW_YEARS, 6),
    }


# ------------------------------------------------------------------ one road, two rulers
def price_road(label, amount_cny, saving_cny, giveup_cny_per_window, giveup_pp_per_year,
               tenure_windows, floor=P_CONVERGE_FLOOR):
    """One substitutable road priced in both currencies and both rulers.

    `saving_cny` is a one-off CNY amount realised only if the premium gap closes at exit;
    `giveup_cny_per_window` is what the lower-ranked substitute gives up over ONE window.
    The two are never subtracted: the road prints its own break-even convergence
    probability (p*) and the operator supplies the belief.
    """
    out = {
        "road": label,
        "amount_cny": round(float(amount_cny), 2),
        "saving_cny_once": round(float(saving_cny), 2),
        "giveup_cny_per_window": round(float(giveup_cny_per_window), 2) if giveup_cny_per_window is not None else None,
        "giveup_pp_per_year": None if giveup_pp_per_year is None else round(float(giveup_pp_per_year), 4),
        "windows_of_giveup_affordable": None,
        "breakeven_convergence_p": None,
        "breakeven_tenure_windows": None,
        "breakeven_tenure_years": None,
        "pays_over_book_tenure": None,
    }
    if saving_cny is None or not np.isfinite(saving_cny):
        out["note"] = "no saving to price (the road costs nothing at the order)"
        return out
    if giveup_cny_per_window is None or not np.isfinite(giveup_cny_per_window):
        out["note"] = "give-up not priceable: no score gap or no measured slope"
        return out
    if giveup_cny_per_window <= 0:
        out["breakeven_convergence_p"] = 0.0
        out["breakeven_tenure_windows"] = None
        out["pays_over_book_tenure"] = True
        out["note"] = "the substitute ranks at or above the leg -- nothing is given up"
        return out
    if saving_cny <= 0:
        out["breakeven_convergence_p"] = None
        out["breakeven_tenure_windows"] = 0.0
        out["pays_over_book_tenure"] = False
        out["note"] = "nothing is saved at the order, so no window of give-up is affordable"
        return out
    p_star = float(giveup_cny_per_window) / float(saving_cny)
    hold = float(saving_cny) / float(giveup_cny_per_window)
    out["breakeven_convergence_p"] = round(p_star, 6)
    out["breakeven_tenure_windows"] = round(hold, 3)
    out["breakeven_tenure_years"] = round(hold * WINDOW_YEARS, 4)
    out["pays_over_book_tenure"] = bool(p_star < floor) if tenure_windows is not None else None
    out["floor_convergence_p"] = floor
    out["note"] = ("the swap pays for itself if the premium gap closes by more than %.1f%% "
                   "before exit; it takes %.1f windows of give-up to eat the whole saving"
                   % (100.0 * p_star, hold))
    return out


def decide_leg(leg, amount_cny, prem_pct, candidate, slope_per_window, tenure, cash_annual_pct,
               leg_score=None, nav=None):
    """One stretched leg -> three roads plus the two rulers' words. Pure (used by check too).

    `nav` is this leg's denominator-date evidence (r2219): a dict with `status` one of
    same-session / prev-session / unproven, or None when nothing proves it. Only a
    same-session denominator may produce a SWAP word -- the arithmetic prints either way.
    """
    out = {
        "symbol": P._sym(leg["symbol"]),
        "class": leg.get("class"),
        "amount_cny": round(float(amount_cny), 2),
        "premium_pct": None if prem_pct is None else round(float(prem_pct), 6),
        "premium_cny": None if prem_pct is None else round(float(amount_cny) * float(prem_pct) / 100.0, 2),
        "stretched": None if prem_pct is None else bool(float(prem_pct) > P.PREMIUM_SWAP_PP),
        "leg_score": None if leg_score is None else round(float(leg_score), 6),
        "nav_evidence": nav,
        "premium_is_session_native": (None if nav is None else nav.get("status") == "same-session"),
        "roads": [],
        "verdict": None,
        "annual_ruler": None,
        "rulers_disagree": False,
    }
    if prem_pct is None:
        out["verdict"] = "UNPRICED"
        out["note"] = "no premium row for this leg in the session snapshot"
        return out
    if not out["stretched"]:
        out["verdict"] = "NOT_STRETCHED"
        out["note"] = "inside the %.1f pp threshold" % P.PREMIUM_SWAP_PP
        return out

    leg_road = price_road("A_buy_as_printed", amount_cny, 0.0, 0.0, 0.0, tenure)
    leg_road["pays_over_book_tenure"] = None
    leg_road["breakeven_convergence_p"] = None
    leg_road["note"] = ("baseline: pay %.0f CNY of premium once, substitute nothing, so there "
                        "is neither a saving nor a give-up to compare" % (out["premium_cny"] or 0.0))
    out["roads"].append(leg_road)

    cand = candidate or {}
    if cand.get("symbol"):
        gap = cand.get("score_gap")
        saving = cand.get("premium_saving_cny")
        giveup_win = None if gap is None or slope_per_window is None else float(amount_cny) * abs(float(gap)) * float(slope_per_window)
        if out["leg_score"] is None and gap is not None:
            out["leg_score"] = round(float(cand.get("score")) + float(gap), 6)
        out["roads"].append(price_road("B_same_market_twin", amount_cny, saving, giveup_win,
                                       cand.get("giveup_pp_per_year"), tenure))
        out["roads"][-1]["twin"] = {"symbol": cand.get("symbol"), "market": cand.get("market"),
                                    "premium_pct": cand.get("premium_pct"),
                                    "score": cand.get("score"), "score_gap": gap}
    else:
        out["roads"].append({"road": "B_same_market_twin", "saving_cny_once": None,
                             "note": "no same-market, same-class twin on today's sheet"})

    # ROAD C: drop the leg, park the notional in the ticket's own cash leg
    giveup_c = None
    if cash_annual_pct is not None and out["leg_score"] is not None:
        leg_win = float(out["leg_score"]) * float(slope_per_window) * float(amount_cny)
        cash_win = float(cash_annual_pct) / 100.0 * WINDOW_YEARS * float(amount_cny)
        giveup_c = leg_win - cash_win
    out["roads"].append(price_road("C_drop_to_cash", amount_cny, out["premium_cny"], giveup_c,
                                   None, tenure))

    any_swap = [r for r in out["roads"] if r.get("pays_over_book_tenure") is True]
    any_hold = [r for r in out["roads"] if r.get("pays_over_book_tenure") is False]
    giveup_annual = None
    for r in out["roads"]:
        if r["road"] == "B_same_market_twin" and r.get("giveup_pp_per_year") is not None:
            giveup_annual = r["giveup_pp_per_year"]
    out["annual_ruler"] = None if giveup_annual is None else (
        "HOLD" if giveup_annual > P.MAX_GIVEUP_PP_YR else "SWAP")
    proven = nav is not None and nav.get("status") == "same-session"
    if any_swap and not proven:
        # the roads still price, but they price a denominator this face cannot put on its own
        # session -- a number published the next calendar day cannot decide today's swap
        out["verdict"] = "STRETCHED_ON_UNPROVEN_NAV"
        out["rulers_disagree"] = bool(out["annual_ruler"] == "HOLD")
        why = ("nothing proves this leg's denominator is the %s NAV" % ((nav or {}).get("session")
                                                                       or "session's"))
        d = (nav or {}).get("sina_nav_date")
        if d and (nav or {}).get("days_beyond_session"):
            why = ("its NAV is dated %s, %d day(s) after the session this ticket was priced on"
                   % (d, nav["days_beyond_session"]))
        elif (nav or {}).get("status") == "prev-session":
            why = "its NAV sits on the previous close, not on this session's path"
        out["note"] = ("%s -- so the %.0f CNY premium and the %.0f%% convergence below are "
                       "arithmetic on an unproven denominator, and this face does not swap on "
                       "them" % (why, out["premium_cny"] or 0.0,
                                 100.0 * min(r["breakeven_convergence_p"] for r in any_swap)))
    elif any_swap:
        out["verdict"] = "SWAP_AT_BOOK_HORIZON"
        out["rulers_disagree"] = bool(out["annual_ruler"] == "HOLD")
        out["note"] = ("over the book's own %.2f-window hold, the substitution pays for itself "
                       "at a %.1f%% convergence probability; the annual ruler read the same "
                       "numbers as %.2f pp/yr against a %.2f cap"
                       % (tenure or float("nan"),
                          100.0 * min(r["breakeven_convergence_p"] for r in any_swap),
                          giveup_annual or 0.0, P.MAX_GIVEUP_PP_YR))
    elif any_hold:
        out["verdict"] = "HOLD_AT_BOOK_HORIZON"
        out["note"] = "no road pays for itself over the book's own holding window"
    else:
        out["verdict"] = "NOT_PRICED"
        out["note"] = "no road could be priced end to end"
    return out


# ------------------------------------------------------------------ sheet
def paths(sig=None, key=None):
    ticket, tpath = P.latest_ticket()
    order = (ticket.get("ticket") or {}).get("order") or []
    if not order:
        raise SystemExit("ticket carries no order rows: %s" % tpath)
    asof = ticket.get("as_of") or ticket.get("evidence_cutoff")
    prem, names, snap_path = P.load_premium_snapshot(asof)
    P.PREM_BY_SYMBOL, P.NAME_BY_SYMBOL = prem, names

    close, openp, amt, feats = F.build_panel()
    score = F.build_score(close, amt, feats)
    last = score.index[-1]
    classes = P.classify(list(close.columns))
    ranked = score.loc[last].dropna()
    sl = P.score_slope(close, score)
    slope_win = sl.get("slope_median_per_horizon")
    tenure = seat_tenure(close, openp, amt, score)

    cash_annual = None
    carry = (ticket.get("carry_split") or {})
    if carry.get("rate_today_pct") is not None:
        cash_annual = float(carry["rate_today_pct"])

    # the twin search is r1773's frozen rule, imported rather than re-implemented
    nav_face = load_nav_evidence(asof)
    by_symbol = nav_face.get("by_symbol") or {}
    legs_out = []
    leg_syms = set(P._sym(r["symbol"]) for r in order)
    for r in order:
        sym = P._sym(r["symbol"])
        row = P.decide_leg(r, prem.get(sym), leg_syms, ranked, classes,
                           slope_win if slope_win is not None else 0.0)
        legs_out.append(decide_leg(r, float(r.get("amount") or 0.0), prem.get(sym),
                                   row.get("candidate"), slope_win, tenure.get("mean_tenure_decisions"),
                                   cash_annual, leg_score=ranked.get(sym),
                                   nav=by_symbol.get(sym)))

    verdict = face_verdict(legs_out)

    payload = {
        "face": "etf_book_premium_choice",
        "ticket": os.path.relpath(tpath, ROOT).replace("\\", "/"),
        "as_of": asof,
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "decision_bar": str(pd.Timestamp(last).date()),
        "snapshot": os.path.relpath(snap_path, ROOT).replace("\\", "/"),
        "snapshot_symbols": len(prem),
        "nav_evidence": {"status": nav_face.get("status"), "session": nav_face.get("session"),
                         "face": os.path.relpath(NAV_EVIDENCE, ROOT).replace("\\", "/")},
        "criteria": {
            "premium_swap_pp": P.PREMIUM_SWAP_PP,
            "min_saving_pp": P.MIN_SAVING_PP,
            "max_giveup_pp_per_year_annual_ruler": P.MAX_GIVEUP_PP_YR,
            "horizon_bars": HORIZON,
            "rebalance_bars": REBAL,
            "n_hold": N_HOLD,
            "start": START,
            "convergence_floor_for_swap": P_CONVERGE_FLOOR,
            "bars_per_year": BARS_PER_YEAR,
        },
        "law": {
            "horizon": ("a one-off CNY saving and a per-window give-up are compared only over "
                        "the window the book actually holds; the annual ruler is printed too, "
                        "never silently applied"),
            "currencies": "one-off CNY vs CNY-per-window vs pp/yr: printed side by side, never summed",
            "belief": ("whether the premium converges at exit is not measurable from a single "
                       "session snapshot, so every road prints its break-even probability"),
            "twin_rule": "inherited from etf_book_premium_swap: same class AND same market",
        },
        "seat_tenure": tenure,
        "score_slope": {"status": sl.get("status"), "bars": sl.get("bars"),
                        "slope_median_per_horizon": slope_win,
                        "slope_annualised": sl.get("slope_annualised"),
                        "corr_median": sl.get("corr_median")},
        "cash_annual_pct": cash_annual,
        "legs": legs_out,
        "verdict": verdict,
    }
    sw = [r for r in legs_out for x in r["roads"] if x.get("pays_over_book_tenure")]
    payload["totals"] = {
        "legs": len(legs_out),
        "stretched_legs": sum(1 for r in legs_out if r.get("stretched")),
        "roads_priced": sum(len([x for x in r["roads"] if x.get("breakeven_convergence_p") is not None])
                            for r in legs_out),
        "best_saving_cny": round(max([x.get("saving_cny_once") or 0.0 for r in legs_out for x in r["roads"]] or [0.0]), 2),
        "best_giveup_cny_per_window": round(min([x["giveup_cny_per_window"] for r in legs_out
                                                 for x in r["roads"]
                                                 if x.get("pays_over_book_tenure") is True
                                                 and x["road"] != "A_buy_as_printed"] or [0.0]), 2),
        "rulers_disagreeing_legs": sum(1 for r in legs_out if r.get("rulers_disagree")),
    }
    if key is None:
        sig = inputs_sig(tpath, snap_path)
        key = input_key(sig)
    payload["inputs"] = {"key": key, "sig": sig}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    write_md(payload, os.path.relpath(tpath, ROOT).replace("\\", "/"))
    print(json.dumps({"verdict": verdict, "totals": payload["totals"],
                      "tenure": tenure.get("mean_tenure_decisions"), "as_of": asof},
                     ensure_ascii=False))
    return payload


def write_md(p, tpath):
    L = []
    A = L.append
    A("# ETF 复合书 —— 溢价腿的三条路，按这本自己的持有窗定价（%s）" % p["as_of"])
    A("")
    A("问题接着 r1773：那一面把「stretched」写成规则（溢价 >%.1f pp 的腿要找同类同市场的替代腿，"
      "省幅 ≥%.1f pp 才算替代，放弃的预期收益 >%.2f pp/年 就不换），今日判词 `HOLD_STRETCHED`。"
      % (P.PREMIUM_SWAP_PP, P.MIN_SAVING_PP, P.MAX_GIVEUP_PP_YR))
    A("")
    A("**本面要问的是那把尺子本身**：省下的溢价是**下单时的一次性 CNY**，放弃的是**每个决策窗**的预期收益。"
      "把后者年化再和前者比，等于默认这个仓位持有一整年。这本书不持有整年——下面是从它自己的选股路径量出来的持有窗。")
    A("")
    hot = [r for r in p["legs"] if r.get("stretched")]
    for r0 in hot:
        b = next((x for x in r0["roads"] if x["road"] == "B_same_market_twin"
                  and x.get("breakeven_convergence_p") is not None), None)
        if not b:
            continue
        A("## 一句话")
        A("")
        A("%s 换同市场的孪生 %s：一次省 **%.0f 元**，每窗放弃 **%.0f 元** → 回本 %.1f 窗（%.2f 年）；"
          "这本书平均只坐 %.2f 窗，所以只要溢价差在离场前收敛超过 **%.1f%%**，换就是划算的。"
          "同一组数按年化读是 %.2f pp/年（上限 %.2f pp/年），所以年化尺子说不换。"
          "两条结论都为真——它们回答的是两个问题：「这一窗换不换」与「值不值得长期持有这只更贵的腿」。"
          % (r0["symbol"], (b.get("twin") or {}).get("symbol") or "—",
             b["saving_cny_once"], b["giveup_cny_per_window"],
             b["breakeven_tenure_windows"], b["breakeven_tenure_years"],
             (p.get("seat_tenure") or {}).get("mean_tenure_decisions") or 0.0,
             100.0 * b["breakeven_convergence_p"], b.get("giveup_pp_per_year") or 0.0,
             P.MAX_GIVEUP_PP_YR))
        A("")
    t = p["seat_tenure"]
    A("## 这本书自己持有多久（量出来的，不是假设的）")
    A("")
    A("| 项 | 值 | 读法 |")
    A("|---|---|---|")
    A("| 决策次数 | %s | 全史 %s 起，每 %d 根 bar 一次 |" % (t["decisions"], p["criteria"]["start"], p["criteria"]["rebalance_bars"]))
    A("| 平均持有窗 | **%s 个**（%s 年） | 一个座位的平均寿命 |" % (t["mean_tenure_decisions"], t["tenure_years"]))
    A("| 中位持有窗 | %s 个 | |" % t["median_tenure_decisions"])
    A("| 只持一窗的座位占比 | %s | 买进来下一次就被换掉 |" % t["share_held_one_window"])
    A("| 新座占比 | %s | 新买的座位 / 全部座位决策（按座位计，与 r1768 按收益贡献计的 94.8%% 不是同一个量） |" % t["fresh_share"])
    A("")
    A("读法：这本书**平均持有 %s 个决策窗**（中位 %s 个，%.0f%% 的座位只坐一窗），"
      "所以「每年放弃多少」这个数字在它身上要除以约 %.0f 才落到它真正付一次的代价。"
      % (t["mean_tenure_decisions"], t["median_tenure_decisions"],
         100.0 * (t["share_held_one_window"] or 0.0), 1.0 / max(t["window_years"], 1e-9)))
    A("")
    A("## 两条尺子（都印出来，谁也不许偷偷替换谁）")
    A("")
    A("| 尺子 | 成本口径 | 今日它会说什么 |")
    A("|---|---|---|")
    A("| 年化尺子（r1773 采用的） | 放弃 ÷ 年 | 高于 %.2f pp/年 就不换 |" % P.MAX_GIVEUP_PP_YR)
    A("| 持有窗尺子（本面） | 放弃 ÷ 这本书自己的一窗 | 省下的钱 ÷ 每窗放弃 = 回本窗数 |")
    A("")
    A("两者不矛盾，只是回答不同的问题：年化尺子在问「值不值得长期持有这只更贵的腿」，持有窗尺子在问"
      "「这一窗换不换」。这本书的实际持有窗是前者假设的 1/12，所以两者的答案会分开——今天确实分开了（见下表）。")
    A("")
    A("**本轮判决：%s**" % p["verdict"])
    A("")
    nev = p.get("nav_evidence") or {}
    unproven = [r for r in p["legs"] if r.get("verdict") == "STRETCHED_ON_UNPROVEN_NAV"]
    if unproven:
        A("**为什么这个词不是 SWAP**：溢价 = 价格 ÷ 净值 − 1，而下面这几条腿的**分母日期**不是这一场：")
        A("")
        for r in unproven:
            nv = r.get("nav_evidence") or {}
            A("* **%s**：净值日期 %s（%s 发布的），本场是 %s；证据面 %s" % (
                r["symbol"], nv.get("sina_nav_date") or "—",
                ("晚 %d 天" % nv["days_beyond_session"]) if nv.get("days_beyond_session") else "同场/未知",
                p.get("as_of"), nev.get("face") or "—"))
        A("")
        A("算术照印，建议不成立：一张票在 %s 做决定时看不到 %s 才发布的数。" %
          (p.get("as_of"), unproven[0].get("nav_evidence", {}).get("sina_nav_date") or "下一交易日"))
        A("")
    A("## 逐腿三条路")
    A("")
    for r in p["legs"]:
        if r["premium_pct"] is not None and not r["stretched"]:
            A("* **%s**（%s，金额 %.0f）：溢价 %+.3f%%（%+.0f 元），在 %.1f pp 门槛内 —— 不参与本面的选择。"
              % (r["symbol"], r["class"], r["amount_cny"], r["premium_pct"], r["premium_cny"] or 0.0,
                 P.PREMIUM_SWAP_PP))
            continue
        A("### %s（%s，金额 %.0f，溢价 %s%%）" % (
            r["symbol"], r["class"], r["amount_cny"],
            "—" if r["premium_pct"] is None else "%.3f" % r["premium_pct"]))
        A("")
        if r["premium_pct"] is not None:
            A("溢价金额 **%s 元**；stretched=%s；年化尺子读作 %s；本窗尺子读作 **%s**%s"
              % (r["premium_cny"], r["stretched"], r["annual_ruler"] or "—", r["verdict"],
                 "（两把尺子给出相反答案）" if r.get("rulers_disagree") else ""))
            A("")
        A("| 路 | 一次性省 | 每窗放弃 | 回本窗数（年） | 回本所需收敛概率 p* | 本窗尺子 |")
        A("|---|---|---|---|---|---|")
        for x in r["roads"]:
            A("| %s | %s | %s | %s (%s) | %s | %s |" % (
                x["road"],
                "—" if x.get("saving_cny_once") is None else "%.0f" % x["saving_cny_once"],
                "—" if x.get("giveup_cny_per_window") is None else "%.0f" % x["giveup_cny_per_window"],
                "—" if x.get("breakeven_tenure_windows") is None else "%.1f" % x["breakeven_tenure_windows"],
                "—" if x.get("breakeven_tenure_years") is None else "%.2f 年" % x["breakeven_tenure_years"],
                "—" if x.get("breakeven_convergence_p") is None else "%.1f%%" % (100.0 * x["breakeven_convergence_p"]),
                "划算" if x.get("pays_over_book_tenure") is True else ("不划算" if x.get("pays_over_book_tenure") is False else "—")))
        A("")
        if r.get("note"):
            A("> %s" % r["note"])
            A("")
    A("## 这张面拒绝做的事")
    A("")
    A("* **不把两种货币相加**：省下的是下单时 CNY，放弃的是每窗 CNY。印 p* 而不是印「净值」，"
      "因为净值需要一个收敛概率，而这个概率本面测不出来——它取决于这只基金未来几个交易日溢价会不会回落，"
      "盘上只有一天的快照。")
    A("* **不用全宇宙溢价历史外推**：`data/etf_premium/nav_history` 只覆盖 9 只标的，r1773 已就此立界，本面沿用。")
    A("* **不改票**：本面只定价，重定价归 `etf_book_order`。")
    A("")
    A("## 为什么这是上一面的修正而不是推翻")
    A("")
    A("r1773 的三个数（省 1,506 元、放弃 2.12 pp/年、上限 2.00 pp/年）在本面里逐字不变，"
      "本面新增的只有一件事：**那个「每」被漏掉了**。同一份数据，除以一窗得到 %s 元，除以一年得到 1,829 元——"
      "读者拿哪个数下决定，取决于他打算持有多久；而这本题面自己的答案（%s 窗）恰好是最短的那个。"
      % ("%.0f" % (p["totals"]["best_giveup_cny_per_window"] or 0.0), t["mean_tenure_decisions"]))
    A("")
    A("数据面：告票 `%s`，溢价快照 `%s`（%d 只），决策 bar `%s`，证据截止 `%s`；"
      "现金腿年化取票面 `carry_split.rate_today_pct` = %s%%。"
      % (tpath, p["snapshot"], p["snapshot_symbols"], p["decision_bar"], p["evidence_cutoff"], p["cash_annual_pct"]))
    A("")
    A("探索性：不是对这本书的判决，不是投资建议，不记账。")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# ------------------------------------------------------------------ check
def check():
    """Re-derive the published arithmetic from the inputs; name what is NOT re-derived.

    Re-derived: premiums, premium CNY, savings, per-window give-up, break-even windows,
    p*, the window ruler's word, the annual ruler's word, the face word.
    NOT re-derived: the ranking scores and the measured seat tenure -- both need a ~60 s
    panel build. That boundary is printed rather than hidden (r1773 convicted the other
    habit twice in this book).
    """
    if not os.path.exists(OUT_JSON):
        print(json.dumps({"ok": False, "problem": "no published face on disk"}))
        return 2
    with open(OUT_JSON, "r", encoding="utf-8") as f:
        pub = json.load(f)
    problems = []
    crit = pub.get("criteria") or {}
    for k, want in (("premium_swap_pp", P.PREMIUM_SWAP_PP), ("max_giveup_pp_per_year_annual_ruler", P.MAX_GIVEUP_PP_YR),
                    ("horizon_bars", HORIZON), ("rebalance_bars", REBAL),
                    ("convergence_floor_for_swap", P_CONVERGE_FLOOR)):
        if crit.get(k) != want:
            problems.append("criteria %s = %r but the code froze %r" % (k, crit.get(k), want))
    ticket, _ = P.latest_ticket()
    asof = ticket.get("as_of") or ticket.get("evidence_cutoff")
    # r2159: the ticket moving is drift, not a wrong number -- say STALE or the chain never
    # buys the rebuild and this face freezes on the previous session (r1934 class).
    moved = []
    if pub.get("as_of") != asof:
        moved.append("the ticket moved to %s (this face was priced on %s)"
                     % (asof, pub.get("as_of")))
    prem, _names, snap = P.load_premium_snapshot(asof)
    if not prem:
        problems.append("snapshot missing for %s (%s)" % (asof, snap))
    nav_face = load_nav_evidence(asof)
    if nav_face.get("status") != "ok":
        # r1850: a missing/foreign evidence face must say STALE so the chain buys a rebuild,
        # and it must never read as "clean" (r1311: silence read as passing)
        problems.append("STALE nav evidence is %s (%s)"
                        % (nav_face.get("status"), os.path.basename(NAV_EVIDENCE)))
    order = {P._sym(r["symbol"]): r for r in (ticket.get("ticket") or {}).get("order") or []}
    slope = (pub.get("score_slope") or {}).get("slope_median_per_horizon")
    tenure = (pub.get("seat_tenure") or {}).get("mean_tenure_decisions")
    for row in pub.get("legs") or []:
        sym = row["symbol"]
        src = order.get(sym)
        if src is None:
            problems.append("%s is not on the ticket any more" % sym)
            continue
        want = prem.get(sym)
        if (want is None) != (row["premium_pct"] is None):
            problems.append("%s premium availability drifted" % sym)
        elif want is not None:
            if abs(want - row["premium_pct"]) > 1e-6:
                problems.append("%s premium %.6f on the face but %.6f in the snapshot" % (sym, row["premium_pct"], want))
            want_cny = float(src.get("amount") or 0.0) * want / 100.0
            if abs(want_cny - (row["premium_cny"] or 0.0)) > 0.05:
                problems.append("%s premium CNY %.2f vs re-derived %.2f" % (sym, row["premium_cny"] or 0.0, want_cny))
            if bool(row.get("stretched")) != bool(want > P.PREMIUM_SWAP_PP):
                problems.append("%s stretched flag disagrees with the threshold" % sym)
        amount = float(src.get("amount") or 0.0)
        for road in row.get("roads") or []:
            sav, give = road.get("saving_cny_once"), road.get("giveup_cny_per_window")
            if sav is None or give is None:
                continue
            if sav > 0 and give > 0:
                p_star, hold = give / sav, sav / give
                if abs((road.get("breakeven_convergence_p") or -1) - p_star) > 1e-4:
                    # both sides are printed at 2 dp CNY, so p* carries ~1e-5 of printing noise
                    problems.append("%s/%s p* %.6f vs re-derived %.6f" % (sym, road["road"], road.get("breakeven_convergence_p") or -1, p_star))
                # r2159: both sides are printed at 2 dp CNY and the give-up is itself a
                # product of printed inputs, so hold = sav/give carries
                # hold*(0.01/sav + 0.01/give) of printing noise -- not a fixed 1e-3.  The
                # old constant turned that noise into a red leg (159655/B: 30.672 vs
                # 30.6707, a 1.3e-3 gap on a 199 CNY divisor).
                hold_tol = max(1e-3, hold * (0.01 / max(sav, 1e-9)
                                             + 0.01 / max(give, 1e-9)))
                if abs((road.get("breakeven_tenure_windows") or -1) - hold) > hold_tol:
                    problems.append("%s/%s break-even windows drifted (%.3f vs %.3f, tol %.4f)"
                                    % (sym, road["road"],
                                       road.get("breakeven_tenure_windows") or -1, hold,
                                       hold_tol))
                want_pays = bool(p_star < P_CONVERGE_FLOOR)
                if bool(road.get("pays_over_book_tenure")) != want_pays:
                    problems.append("%s/%s window ruler word disagrees with p* vs the floor" % (sym, road["road"]))
            if road["road"] == "B_same_market_twin" and slope is not None:
                gap = (road.get("twin") or {}).get("score_gap")
                if gap is not None and give is not None:
                    want_give = amount * abs(float(gap)) * float(slope)
                    if abs(want_give - give) > max(0.5, 1e-3 * abs(want_give)):
                        problems.append("%s twin give-up %.2f vs amount x gap x slope %.2f" % (sym, give, want_give))
            if road["road"] == "A_buy_as_printed" and sav not in (0.0, None):
                problems.append("%s road A claims a saving it should not have" % sym)
        if row.get("stretched") is False and row.get("verdict") != "NOT_STRETCHED":
            problems.append("%s is inside the threshold but the word is %s" % (sym, row.get("verdict")))
        if row.get("stretched") and row.get("verdict") == "NOT_STRETCHED":
            problems.append("%s is stretched but the word is NOT_STRETCHED" % sym)
        if row.get("annual_ruler") is not None:
            b = [x for x in row["roads"] if x["road"] == "B_same_market_twin" and x.get("giveup_pp_per_year") is not None]
            if b:
                want_word = "HOLD" if b[0]["giveup_pp_per_year"] > P.MAX_GIVEUP_PP_YR else "SWAP"
                if row["annual_ruler"] != want_word:
                    problems.append("%s annual ruler %r vs re-derived %r" % (sym, row["annual_ruler"], want_word))
        # r2219: the denominator-date evidence is re-derived from the face on disk, and a
        # SWAP word on an unproven denominator is a defect rather than a stale number
        want_nav = (nav_face.get("by_symbol") or {}).get(sym)
        if (want_nav or {}).get("status") != (row.get("nav_evidence") or {}).get("status"):
            problems.append("%s nav evidence %r vs %r in %s"
                            % (sym, (row.get("nav_evidence") or {}).get("status"),
                               (want_nav or {}).get("status"), os.path.basename(NAV_EVIDENCE)))
        if row.get("premium_is_session_native") != ((want_nav or {}).get("status") == "same-session"):
            problems.append("%s premium_is_session_native %r disagrees with the evidence face"
                            % (sym, row.get("premium_is_session_native")))
        if row.get("verdict") == "SWAP_AT_BOOK_HORIZON" and (want_nav or {}).get("status") != "same-session":
            problems.append("%s recommends a swap on a denominator the evidence face does not place "
                            "on this session" % sym)
    want = face_verdict(pub.get("legs") or [])
    if pub.get("verdict") != want:
        problems.append("face verdict %r does not follow from the legs (re-derived %r)"
                        % (pub.get("verdict"), want))
    if moved and problems:
        problems = ["STALE " + m for m in moved] + [
            "these followed the ticket: " + p for p in problems]
    out = {"ok": not problems, "problems": problems, "verdict": pub.get("verdict"),
           "moved_inputs": moved,
           "tenure_windows": tenure,
           "re_derived_from_inputs": ["premium_pct", "premium_cny", "stretched", "saving CNY",
                                      "per-window give-up", "break-even windows/years", "p*",
                                      "window-ruler word", "annual-ruler word",
                                      "denominator-date evidence (status per leg)", "face word"],
           "not_re_derived": ["ranking scores (panel build ~60s)", "measured seat tenure (same build)"]}
    print(json.dumps(out, ensure_ascii=False))
    return 0 if not problems else 2


# ------------------------------------------------------------------ selftest
def selftest():
    ok = 0
    total = 0

    def leg(cond, label):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s" % label)

    # L1 p* = give-up / saving; break-even windows = saving / give-up
    r = price_road("B", 86286.0, 1506.35, 145.4, 2.12, 1.05)
    leg(abs(r["breakeven_convergence_p"] - 145.4 / 1506.35) < 1e-6, "L1 p* = give-up/saving")
    leg(abs(r["breakeven_tenure_windows"] - 1506.35 / 145.4) < 1e-3, "L1b break-even windows")
    leg(r["pays_over_book_tenure"] is True, "L1c 9.7% convergence beats the 50% floor")

    # L2 the same road with a give-up 20x bigger is refused
    r = price_road("B", 86286.0, 1506.35, 3000.0, 2.12, 1.05)
    leg(r["pays_over_book_tenure"] is False, "L2 a give-up above the saving is refused")
    leg(abs(r["breakeven_convergence_p"] - 3000.0 / 1506.35) < 1e-6, "L2b p* above 1 prints as above 1")

    # L3 a substitute that ranks at or above the leg gives nothing up
    r = price_road("B", 86286.0, 1506.35, 0.0, 0.0, 1.05)
    leg(r["breakeven_convergence_p"] == 0.0 and r["pays_over_book_tenure"] is True,
        "L3 free swap is free")

    # L4 no saving -> nothing affordable, never a divide-by-zero
    r = price_road("B", 86286.0, 0.0, 145.4, 2.12, 1.05)
    leg(r["pays_over_book_tenure"] is False and r["breakeven_tenure_windows"] == 0.0,
        "L4 zero saving is refused, not inf")

    # L5 a road with no give-up price (missing score) stays unpriced rather than assumed
    r = price_road("B", 86286.0, 1506.35, None, None, 1.05)
    leg(r["pays_over_book_tenure"] is None and r.get("note"), "L5 unpriced give-up stays unpriced")

    # L6 the annual ruler is a DIFFERENT ruler: 2.12 pp/yr against a 2.00 cap means HOLD
    #    while the window ruler on the same numbers means SWAP -- the disagreement is the face
    ann = 2.12 > P.MAX_GIVEUP_PP_YR
    win = price_road("B", 86286.0, 1506.35, 145.4, 2.12, 1.05)["pays_over_book_tenure"]
    leg(ann and win is True, "L6 annual says HOLD, window says SWAP on the same numbers")

    # L7 tenure counts a kept seat once, not once per decision: four names rotate out after
    # one window, three names stay two windows, two names stay one -> mean = 1.3
    idx = pd.bdate_range("2024-01-01", periods=REBAL * 2 + 2)
    names = ["AAA", "BBB", "CCC", "DDD", "EEE", "ZZZ", "YYY", "XXX", "WWW", "VVV"]
    px = pd.DataFrame(100.0, index=idx, columns=names)
    sc = pd.DataFrame(0.0, index=idx, columns=names)
    d0, d1, d2 = idx[0], idx[REBAL], idx[REBAL * 2]
    sc.loc[d0, ["AAA", "BBB", "CCC", "DDD", "EEE"]] = 1.0
    sc.loc[d1:, ["AAA", "BBB", "CCC", "DDD", "EEE"]] = -1.0
    sc.loc[d1:, ["ZZZ", "YYY", "XXX", "WWW", "VVV"]] = 1.0
    sc.loc[d2:, ["WWW", "VVV"]] = 0.5
    amt = pd.DataFrame(1e9, index=idx, columns=names)
    ten = seat_tenure(px, px, amt, sc, rebal=REBAL, n_hold=5, start=str(idx[0].date()),
                      min_amt=0.0, min_hist=1)
    leg(ten["seats_closed"] == 10 and abs(ten["mean_tenure_decisions"] - 1.5) < 1e-9,
        "L7 tenure spans a kept seat (mean 1.5 over 10 spans), not per-decision counting")
    leg(ten["decisions"] == 3, "L7b three decision bars read")

    # L8 the fresh-share read is internally consistent with the seat count it is derived from
    #    (it is NOT the same metric as r1768's "fresh names share of the select leg" -- that
    #    one weights by return contribution, this one counts seats)
    t = pub_tenure()
    if t is None:
        leg(True, "L8 no published face yet -- the consistency leg has nothing to read")
    else:
        leg(t["seat_periods"] > 0
            and abs(t["fresh_seats"] / float(t["seat_periods"]) - t["fresh_share"]) < 1e-4
            and 0.0 < t["fresh_share"] <= 1.0,
            "L8 fresh share = fresh seats / seat periods, and inside (0, 1]")
        leg(t["mean_tenure_decisions"] is None or t["mean_tenure_decisions"] >= 1.0,
            "L8b a seat lasts at least one window by construction")

    # L9 one-off vs per-window are never summed: road A has no saving and no give-up either
    a = price_road("A", 86286.0, 0.0, 0.0, 0.0, 1.05)
    leg(a["saving_cny_once"] == 0.0 and a["giveup_cny_per_window"] == 0.0,
        "L9 road A carries neither a saving nor a give-up")

    # L10 CNY units: one window of give-up is amount x gap x slope, in CNY
    gap, slope, amount = 0.1569, 0.010739587458382917, 86286.0
    want = amount * gap * slope
    r = price_road("B", amount, 1506.35, want, 2.12, 1.05)
    leg(abs(r["giveup_cny_per_window"] - want) < 0.01, "L10 give-up CNY = amount x gap x slope")

    # L11 the window is one decision: 20 bars of 252 is 0.0794 years
    leg(abs(WINDOW_YEARS - 20.0 / 252.0) < 1e-12, "L11 window years = horizon bars / bars per year")

    # L12 a stretched leg with no twin still prices road C (drop to cash) and says so
    fixture = {"symbol": "159655", "class": "crossborder", "amount": 86286.0}
    out = decide_leg(fixture, 86286.0, 6.746, None, 0.010739587458382917, 1.05, 1.265)
    roads = {x["road"]: x for x in out["roads"]}
    leg(roads.get("B_same_market_twin", {}).get("saving_cny_once") is None,
        "L12 no twin -> road B is not invented")
    leg(roads.get("C_drop_to_cash", {}).get("saving_cny_once") is not None,
        "L12b road C still carries the premium it saves")
    leg(out["verdict"] in ("SWAP_AT_BOOK_HORIZON", "HOLD_AT_BOOK_HORIZON", "NOT_PRICED"),
        "L12c the leg still gets a word")

    # L13 the rebuild gate skips ONLY a face that answered exactly these inputs
    k = input_key({"a": 1})
    leg(gate_decision({"inputs": {"key": k}}, k) == (True, "SAME_INPUTS"),
        "L13 same inputs -> SAME_INPUTS (the build is skipped)")
    leg(gate_decision({"inputs": {"key": k}}, input_key({"a": 2})) == (False, "INPUTS_CHANGED"),
        "L13b one input byte moving -> INPUTS_CHANGED (the build runs)")
    leg(gate_decision({}, k) == (False, "NO_PREVIOUS_FACE"),
        "L13c no face on disk is not 'same inputs'")
    leg(gate_decision({"verdict": "X"}, k) == (False, "PREVIOUS_FACE_HAS_NO_INPUT_KEY"),
        "L13d a face written before the key existed is rebuilt, not trusted")

    # L14 the key moves with every input it claims to read, and with none that it does not
    base = {"ticket_sha": "aa", "snapshot_sha": "bb", "script_sha": "cc",
            "swap_script_sha": "dd", "panel_files": 3}
    k0 = input_key(base)
    leg(all(input_key(dict(base, **{f: "zz"})) != k0
            for f in ("ticket_sha", "snapshot_sha", "script_sha", "swap_script_sha", "panel_files")),
        "L14 every named input is part of the key (an edit cannot ride a face it did not rebuild)")
    leg(input_key(base) == k0, "L14b the key is a function of the inputs, not of the clock")

    # L15 r2219: a swap needs a denominator this face can place on its own session.
    #   Same numbers, three evidence states -- only the proven one may say SWAP.
    fx = {"symbol": "159655", "class": "crossborder", "amount": 86286.0}
    twin = {"symbol": "159502", "market": "sh", "score": 0.49, "score_gap": 0.07,
            "premium_pct": 2.4, "premium_saving_cny": 7000.0, "giveup_pp_per_year": 1.0}
    args = (86286.0, 10.36, twin, 0.010739587458382917, 1.05, 1.265)
    same = {"status": "same-session", "sina_nav_date": "2026-11-27", "days_beyond_session": None}
    prev = {"status": "prev-session", "sina_nav_date": "2026-11-26", "days_beyond_session": None}
    ahead = {"status": "prev-session", "sina_nav_date": "2026-11-28", "days_beyond_session": 1}
    out_ok = decide_leg(fx, *args, nav=same)
    leg(out_ok["verdict"] == "SWAP_AT_BOOK_HORIZON" and out_ok["premium_is_session_native"] is True,
        "L15 a proven same-session denominator still swaps (arbitrary time by itself is not enough)")
    out_prev = decide_leg(fx, *args, nav=prev)
    leg(out_prev["verdict"] == "STRETCHED_ON_UNPROVEN_NAV"
        and out_prev["premium_cny"] is not None and out_prev["roads"],
        "L15b a leg on the previous close keeps its arithmetic but loses the swap word")
    out_ahead = decide_leg(fx, *args, nav=ahead)
    leg(out_ahead["verdict"] == "STRETCHED_ON_UNPROVEN_NAV"
        and "2026-11-28" in (out_ahead.get("note") or ""),
        "L15c a NAV dated after the session is named in the note, not silently trusted")
    out_none = decide_leg(fx, *args, nav=None)
    leg(out_none["verdict"] == "STRETCHED_ON_UNPROVEN_NAV",
        "L15d no evidence is not evidence of being native (silence never reads as clean)")
    leg(face_verdict([out_ok]) == "RULERS_AGREE_SWAP"
        and face_verdict([out_prev]) == "NO_PROVEN_SWAP_LEG"
        and face_verdict([out_prev, out_ok]) == "RULERS_AGREE_SWAP",
        "L15e the face word follows the legs, and one proven leg is enough to print a swap")

    # L15f-L15g the evidence reader refuses another session's proof and reads three buckets
    import tempfile
    keep = NAV_EVIDENCE
    globals()["NAV_EVIDENCE"] = os.path.join(tempfile.gettempdir(), "premium_choice_nav_fixture.json")
    try:
        with open(NAV_EVIDENCE, "w", encoding="utf-8") as f:
            json.dump({"board_session": "2026-11-27", "rows": [
                {"code": "AAA", "board_position": "SAME_SESSION", "sina_position": "SAME_SESSION",
                 "sina_nav_date": "2026-11-27"},
                {"code": "BBB", "board_position": "NO_DATA", "sina_position": "PREV_SESSION",
                 "sina_nav_date": "2026-11-28"},
                {"code": "CCC", "board_position": "UNDECIDABLE", "sina_position": "UNDECIDABLE",
                 "sina_nav_date": "2026-11-26"},
            ]}, f)
        e = load_nav_evidence("2026-11-27")
        by = e["by_symbol"]
        leg(e["status"] == "ok" and by["AAA"]["status"] == "same-session"
            and by["BBB"]["status"] == "prev-session" and by["BBB"]["days_beyond_session"] == 1
            and by["CCC"]["status"] == "unproven",
            "L15f evidence reads three buckets and counts the days a NAV runs past the session")
        leg(load_nav_evidence("2026-11-26")["status"] == "other session",
            "L15g another session's proof proves nothing here")
    finally:
        globals()["NAV_EVIDENCE"] = keep
        try:
            os.remove(os.path.join(tempfile.gettempdir(), "premium_choice_nav_fixture.json"))
        except OSError:
            pass

    print("premium-choice selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def pub_tenure():
    """Tenure as published (used by a selftest leg so the suite does not need a panel build)."""
    if not os.path.exists(OUT_JSON):
        return None
    with open(OUT_JSON, "r", encoding="utf-8") as f:
        return (json.load(f) or {}).get("seat_tenure")


def if_stale():
    """Chain entry: rebuild only when the inputs behind the published face have moved."""
    sig = inputs_sig()
    key = input_key(sig)
    prev = None
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, "r", encoding="utf-8") as f:
                prev = json.load(f)
        except (OSError, ValueError):
            prev = None
    skip, why = gate_decision(prev, key)
    if skip:
        print("premium_choice: SAME_INPUTS key=%s -- face left untouched (%s)"
              % (key[:16], (prev or {}).get("verdict")))
        return 0
    print("premium_choice: %s key=%s -- rebuilding" % (why, key[:16]))
    paths(sig=sig, key=key)
    return 0


def main(argv):
    cmd = [a for a in argv[1:] if not a.startswith("-")]
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    if "--if-stale" in argv:
        return if_stale()
    if cmd and cmd[0] not in ("paths", "sheet"):
        print("usage: etf_book_premium_choice.py [paths|--if-stale|--check|--selftest]")
        return 2
    paths()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
