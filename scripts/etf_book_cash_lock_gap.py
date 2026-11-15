"""The gate says "pay the sleeve". Can the treasurer hand the cash over on decision day?

r1738/r1739 pulled the same book across the Y4 line by pricing the idle sleeve at a repo
carry, and r1739 wrote the limit of its own answer down:

    "the carrier comparison is inside the book's own cash share; it does not answer
     whether the treasurer can actually keep a 7/14/28-day ladder funded while
     rebalancing every 20 sessions"

That is the whole question.  A repo contract is not a bank deposit: once bought, the cash
is gone to its maturity bar (`etf_book_cash_ladder`: "a contract is never exited early").
The vol-target book de-levers into cash and re-levers in jumps -- r1738 measured that 43%
of its decision periods sit at equity weight 0 and that the idle share swings with the
sizing rule -- so "the sleeve earns 1.88%/yr" is only true if the sleeve can also be
handed back on the day the sizing rule asks for it, and the two events are 20 sessions
apart, not 0.

This face runs the same 5-name, 8% vol-target, 20-session book as the gate, on the same
panel and the same frozen line, and prices three ways a treasurer could hold the sleeve:

  locked      rungs always roll at maturity (the published ladder3 behaviour).  Deployment
              is limited to cash that has actually matured, so a re-lever can only be
              funded by whatever happened to come free -- the rest stays in cash and the
              book stays under-invested until it does.
  callable    at every maturity the rung is re-placed in the LONGEST ladder tenor that
              still matures before the next scheduled decision bar.  Nothing is ever locked
              past a decision, so no deployment is ever blocked; the price of that
              guarantee is the carry given up, and this face measures it.
  break       deploy in full anyway and forfeit the accrued interest on whatever has to be
              broken.  Exchange repo cannot be broken, so this is the cost of an emergency
              funding line, not a real option -- it is here as the lower bound of the
              price.

Controls (bit-exact, because they are the published faces recomposed, not re-estimated):
this face rebuilds the two published cells -- cash at 0 and cash on GC001 -- and must
reproduce results/etf_book_gate_knobs.json to 1e-4.  The ledger's own cash CAGR on the
unconstrained `locked` policy is printed beside the published 1.88% as a sanity band; it is
a different contract simulation, not a second copy of the published one.

Reuse, never re-implement:
  panel + score                    etf_composite_pf.build_panel / build_score
  flip repair + classification     etf_equity_alpha.repair_flips / classify
  the book engine (and its hooks)  etf_robust_pf.open_to_open_equity
  sizing scale + composition       etf_book_idle_cash.scale_schedule / compose
  the repo panel, tenors and fees  etf_book_cash_ladder.load_panel / TENORS / FEE_BP
  calendar gate + blocks + line    candidate_year_gate / etf_book_year_gate

Usage:
    python scripts/etf_book_cash_lock_gap.py run
    python scripts/etf_book_cash_lock_gap.py selftest
"""
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import etf_book_cash_ladder as CL  # noqa: E402
import etf_book_idle_cash as IC  # noqa: E402
import etf_book_year_gate as YG  # noqa: E402
import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_cash_lock_gap.json")
MD = os.path.join(ROOT, "research", "ETF_BOOK_CASH_LOCK_GAP.md")
KNOBS = os.path.join(ROOT, "results", "etf_book_gate_knobs.json")

REBAL, NHOLD, COST, VOL_TARGET = 20, 5, 0.0010, 0.08
LADDER = tuple(CL.LADDERS["ladder3"])            # GC007 / GC014 / GC028
TENOR_DAYS = {nm: CL.tenor_of(nm) for nm in LADDER}
LADDER_DAYS = tuple(sorted(TENOR_DAYS.values()))
OVERNIGHT = "GC001"
# A shortfall smaller than this fraction of NAV is commission dust on the contracts
# themselves (0.5/1.0/2.0bp per rung, once per entry), not cash the calendar locked. Both
# counts are published; only the material one is called a blocked decision.
MATERIAL_SHORT = 1e-3
# A sleeve thinner than this fraction of NAV is dust: the sizing rule has essentially no
# cash out. Its days are not counted in the sleeve's own yield -- counting them would
# dilute a 1.8%/yr yield to zero simply because the book happened to be 99.9% invested.
SLEEVE_EPS = 1e-3

# Frozen before any number was seen.
CRITERIA = {
    "C0_published_cells": "the cash-at-0 cell and the GC001 cell must reproduce "
                          "results/etf_book_gate_knobs.json (top2_share to 1e-4 and the "
                          "same verdict) -- otherwise this face is pricing a different book",
    "C0b_ledger_cash_band_pp": 0.50,
    "C0b_why": "the ledger re-places at each maturity instead of rolling independent "
               "rungs, so its cash CAGR is a different contract simulation; the band only "
               "checks it is pricing the same panel, it is not a precision claim",
}
VERDICTS = ("CONTROL_FAILED", "CALLABLE_LADDER_HOLDS", "GATE_NEEDS_CASH_YOU_CANNOT_RAISE",
            "NEITHER_HOLDS")


def verdict_of(readings):
    """Pure: every gate recomputed from the readings, nothing typed twice."""
    if not readings.get("control_reproduces_published_cells"):
        return "CONTROL_FAILED"
    arms = readings.get("arms") or {}
    if (arms.get("callable") or {}).get("Y4_top2_share"):
        return "CALLABLE_LADDER_HOLDS"
    if ((arms.get("locked") or {}).get("Y4_top2_share")
            or (arms.get("break") or {}).get("Y4_top2_share")):
        return "GATE_NEEDS_CASH_YOU_CANNOT_RAISE"
    return "NEITHER_HOLDS"


def carry_given_up_pp(led_cash_pct, callable_cash_pct):
    """Both inputs are already percentages, so their difference is already in points.

    The first draft multiplied this by 100 and the page printed "183.11 pp/yr" for a
    1.83 pp/yr cost -- a unit that reads as a hundredfold disaster. A percentage
    difference is the point difference; there is nothing left to convert.
    """
    return round(float(led_cash_pct) - float(callable_cash_pct), 2)


# ---------------------------------------------------------------------------------------
# the cash ledger: lots with a maturity date, never exited early unless told to
# ---------------------------------------------------------------------------------------
def _rate(series, when):
    v = series.get(when, np.nan)
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return v if np.isfinite(v) else None


def next_decision_after(decisions, when):
    """First scheduled decision bar strictly after `when` (None if there is none)."""
    for d in decisions:
        if d > when:
            return d
    return None


def place(liquid, when, quotes, tenors, fees=None):
    """Split `liquid` equally over `tenors`; parts without a quote stay liquid.

    Returns (lots, unplaced, fee_paid). The commission is charged per contract at entry
    out of the placed face value, exactly as `etf_book_cash_ladder.roll_rung` charges it.
    """
    if not tenors or liquid <= 0:
        return [], max(liquid, 0.0), 0.0
    part = liquid / float(len(tenors))
    lots, unplaced, fee_paid = [], 0.0, 0.0
    for k in tenors:
        r = _rate(quotes.get(k), when)
        if r is None:
            unplaced += part
            continue
        nm = next(n for n, t in TENOR_DAYS.items() if t == k)
        fee = part * CL.fee_bp(nm, fees) / 1e4
        fee_paid += fee
        lots.append({"entry": when, "mature": when + pd.Timedelta(days=k), "tenor": k,
                     "rate_pct": r, "principal": part - fee, "name": nm,
                     "fee": fee})
    return lots, unplaced, fee_paid


_DBG = bool(os.environ.get("LOCKGAP_DEBUG"))
_DBG_STATS = {"sum_acc": 0.0, "bars_with_lots": 0, "bars_with_liquid": 0, "sum_days": 0}


def ledger_pass(index, targets, decisions, quotes, policy, allow_break=False, fees=None):
    """Walk the book's own bars with a cash ledger; return what the treasurer could do.

    `targets` maps decision date -> the scale the sizing rule asked for.  The ledger never
    sees a future quote: the overnight fallback is priced at the previous bar's close, and
    every placement uses that bar's own quote.

    Two yields are reported and they are not the same number: `cash_cagr_pct` is the
    sleeve's OWN annualised yield (interest over money actually sitting in the sleeve, the
    quantity comparable with `etf_book_cash_ladder`'s 1.88%), while
    `portfolio_contrib_pct` is what that sleeve added to the book's return given that most
    of the book is invested.
    """
    index = pd.DatetimeIndex(index)
    decisions = sorted(pd.Timestamp(d) for d in decisions)
    dec_set = set(decisions)
    g1 = quotes[1] if 1 in quotes else quotes.get(OVERNIGHT)
    contrib = pd.Series(0.0, index=index)
    yret = np.zeros(len(index), dtype=float)      # sleeve's own per-bar return
    ydays = 0
    allowed, blocked = {}, []
    # The book starts with no position: all of NAV is cash on the first bar. Without this
    # the first deployment has nothing to deploy from and every arm would open blocked.
    lots, liquid, invested = [], 1.0, 0.0
    # The engine decides on its first panel bar but the book's own return series starts on
    # the bar after it, so that first allocation is the opening position here.
    pre = [d for d in decisions if d < index[0]]
    if pre:
        invested = float(targets[pre[-1]])
        liquid = 1.0 - invested
    penalty_total, fee_total, missing = 0.0, 0.0, 0
    prev = None
    for i, b in enumerate(index):
        days = int((b - prev).days) if prev is not None else 0
        sleeve0 = max(1.0 - invested, 0.0)
        # (1) accrual on locked lots and on any sweep account, pro-rata over calendar days
        acc = 0.0
        for lot in lots:
            acc += lot["principal"] * lot["rate_pct"] / 100.0 * days / 365.0
        if liquid > 0 and days > 0 and i > 0:
            r0 = _rate(g1, index[i - 1])
            if r0 is not None:
                acc += liquid * r0 / 100.0 * days / 365.0
        contrib.iloc[i] += acc
        if _DBG:
            _DBG_STATS["sum_acc"] += acc
            _DBG_STATS["bars_with_lots"] += 1 if lots else 0
            _DBG_STATS["bars_with_liquid"] += 1 if liquid > 0 else 0
            _DBG_STATS["sum_days"] += days
        if sleeve0 > SLEEVE_EPS and days > 0:
            yret[i] += acc / sleeve0
            ydays += days
            if _DBG:
                _DBG_STATS["guard_pass"] = _DBG_STATS.get("guard_pass", 0) + 1
                _DBG_STATS["sum_yret"] = _DBG_STATS.get("sum_yret", 0.0) + acc / sleeve0
        elif _DBG:
            _DBG_STATS["guard_fail"] = _DBG_STATS.get("guard_fail", 0) + 1
        prev = b
        # (2) settle whatever matured on or before this bar
        keep = []
        for lot in lots:
            if lot["mature"] <= b:
                liquid += lot["principal"]
            else:
                keep.append(lot)
        lots = keep
        # (3) the decision bar: raise cash if the sizing rule asks for more exposure
        if b in dec_set:
            target = float(targets[b])
            need = target - invested
            if need > 1e-12:
                use = min(need, max(liquid, 0.0))
                liquid -= use
                invested += use
                short = need - use
                if short > 1e-12:
                    locked_at_ask = sum(l["principal"] for l in lots)
                    paid, covered = 0.0, 0.0
                    if allow_break:
                        # cheapest break first: least accrued interest lost
                        order = sorted(range(len(lots)),
                                       key=lambda j: lots[j]["principal"]
                                       * lots[j]["rate_pct"] / 100.0
                                       * max(int((b - lots[j]["entry"]).days), 0))
                        for j in order:
                            if short <= 1e-12:
                                break
                            lot = lots[j]
                            if lot["principal"] <= 0:
                                continue
                            take = min(short, lot["principal"])
                            paid += take * lot["rate_pct"] / 100.0 * max(
                                int((b - lot["entry"]).days), 0) / 365.0
                            lot["principal"] -= take
                            covered += take
                            short -= take
                        penalty_total += paid
                        contrib.iloc[i] -= paid
                        if sleeve0 > SLEEVE_EPS:
                            yret[i] -= paid / sleeve0
                        invested += covered
                    # A shortfall while rungs are still out is the calendar's fault; a
                    # shortfall with nothing locked is commission quietly eating the sleeve.
                    blocked.append({"date": str(b.date()), "needed": round(need, 6),
                                    "raised": round(use + covered, 6),
                                    "short": round(short, 6),
                                    "locked_at_ask": round(locked_at_ask, 6),
                                    "kind": ("lock" if locked_at_ask > MATERIAL_SHORT
                                             else "leak"),
                                    "forfeit": round(paid, 8)})
            elif need < -1e-12:
                invested += need
                liquid += -need
            allowed[b] = round(invested, 10)
        # (4) put the sweeps back to work under this policy
        if liquid > 0:
            if policy == "locked":
                tenors = list(LADDER_DAYS)
            elif policy == "callable":
                nxt = next_decision_after(decisions, b)
                gap = int((nxt - b).days) if nxt is not None else 10 ** 6
                tenors = [k for k in LADDER_DAYS if k <= gap]
            else:
                tenors = [1] if 1 in quotes else []
            new, unplaced, fee = place(liquid, b, quotes, tenors, fees)
            lots.extend(new)
            liquid = unplaced
            if fee:
                fee_total += fee
                contrib.iloc[i] -= fee
                if sleeve0 > SLEEVE_EPS:
                    yret[i] -= fee / sleeve0
            if unplaced > 0 and policy != "callable":
                missing += 1
    material = [x for x in blocked if x["short"] > MATERIAL_SHORT]
    lock_blocks = [x for x in material if x["kind"] == "lock"]
    leak_blocks = [x for x in material if x["kind"] != "lock"]
    blocked_need = sum(x["needed"] for x in lock_blocks)
    blocked_short = sum(x["short"] for x in lock_blocks)
    nav = float(np.prod(1.0 + contrib.to_numpy()))
    span = max(int((index[-1] - index[0]).days), 1)
    yield_cv = float(np.prod(1.0 + yret))
    if os.environ.get("LOCKGAP_DEBUG"):
        nz = np.nonzero(yret)[0]
        print("DEBUG policy=%s ydays=%d yield_cv=%.6f nbars=%d min=%.3e max=%.3e "
              "sum=%.6f lots=%d lotprincipal=%.4f liquid=%.6f invested=%.4f "
              "first5=%s" % (policy, ydays, yield_cv, len(nz),
                             float(yret.min()), float(yret.max()), float(yret.sum()),
                             len(lots), float(sum(l["principal"] for l in lots)),
                             float(liquid), float(invested),
                             [round(float(x), 6) for x in yret[nz][:5]]))
    return {
        "allowed": allowed,
        "contrib": contrib,
        "blocked": blocked,
        "blocked_events": int(len(lock_blocks)),
        "leak_events": int(len(leak_blocks)),
        "blocked_events_any": int(len(blocked)),
        "blocked_short_total": round(blocked_short, 6),
        "blocked_share_of_asks": round(blocked_short / blocked_need, 6) if blocked_need else 0.0,
        "worst_short": round(max([x["short"] for x in lock_blocks] or [0.0]), 6),
        "blocked_material": sorted(material, key=lambda x: -x["short"])[:12],
        "penalty_total": round(penalty_total, 8),
        "fee_total": round(fee_total, 8),
        "missing_quote_events": int(missing),
        "cash_cagr_pct": round((yield_cv ** (365.0 / max(ydays, 1)) - 1.0) * 100.0, 4),
        "sleeve_days": int(ydays),
        "portfolio_contrib_pct": round((nav ** (365.0 / span) - 1.0) * 100.0, 4),
        "invested_final": round(invested, 6),
    }


# ---------------------------------------------------------------------------------------
def _read_json(path):
    if not os.path.exists(path):
        return None
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:                                                   # noqa: BLE001
        return None


def _published_cells(knobs):
    g = ((knobs or {}).get("readings") or {}).get("grid") or {}
    arm = g.get("n5_gate_arm") or {}
    return {c: {"top2_share": (arm.get(c) or {}).get("top2_share"),
                "verdict": (arm.get(c) or {}).get("verdict")} for c in ("cash_zero",
                                                                        "gc001_roll")}


def _compose_with(book, add):
    """Same step algebra as etf_book_idle_cash.compose, kept local so the contribution
    series a ledger produces (already a NAV fraction) can be dropped in unchanged."""
    r_book = book.pct_change().fillna(0.0)
    step = add.reindex(book.index).fillna(0.0)
    return pd.Series(np.cumprod(1.0 + r_book.to_numpy() + step.to_numpy()),
                     index=book.index) * float(book.iloc[0])


def _arm_block(name, ser, capacity, note):
    blk = YG._block(name, YG.yearly_returns(ser), capacity, ser, note)
    if capacity is not None:
        blk["capacity_cny_1day_5pct"] = round(capacity, 0)
        blk["checks"]["C1_capacity"] = bool(capacity >= G.CAPACITY_FLOOR_CNY)
        blk["verdict"] = G.verdict({"checks": blk["checks"]})
    st = A.stats2(ser, name)
    blk["stats"] = {k: (None if st.get(k) is None else round(float(st[k]), 6))
                    for k in ("cagr", "sharpe", "maxdd", "vol")}
    return blk


def run():
    t0 = time.time()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cls = A.classify(close.columns, A.load_class_map(), close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)

    rates = CL.load_panel()
    diag0 = []
    book0, turn0 = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, REBAL,
                                        NHOLD, COST, vol_target=VOL_TARGET, diag=diag0)
    index = book0.index
    targets = {pd.Timestamp(r["date"]): float(r["scale"]) for r in diag0}
    decisions = sorted(targets)
    idle0 = (1.0 - IC.scale_schedule(diag0, index)).clip(lower=0.0, upper=1.0)
    last = sc.index[-1]
    picks = list(sc.loc[last].dropna().nlargest(NHOLD).index)
    capacity = YG.capacity_cny(picks, amt)

    quotes_full = CL.load_panel(bars=index)
    quotes = {}
    for nm, days in TENOR_DAYS.items():
        quotes[days] = quotes_full[nm]
    quotes[1] = quotes_full[OVERNIGHT]

    # --- controls: recompose the two published cells with the published carriers --------
    step0 = pd.Series(0.0, index=index)
    step_g1 = IC.cash_step_returns(rates, index, name=OVERNIGHT, ladder=None, fees=None)[0]
    ctrl_zero = _arm_block("ctrl/cash_zero", IC.compose(book0, idle0, step0), capacity,
                           "the calendar gate's own arm: sleeve priced at 0")
    ctrl_g1 = _arm_block("ctrl/gc001", IC.compose(book0, idle0, step_g1), capacity,
                         "overnight roll, never locked")

    # --- the three treasurer policies --------------------------------------------------
    arms, ledgers = {}, {}
    for name, policy, brk in (("locked", "locked", False),
                              ("callable", "callable", False),
                              ("break", "locked", True)):
        led = ledger_pass(index, targets, decisions, quotes, policy, allow_break=brk,
                          fees=None)
        ledgers[name] = led
        allowed = led["allowed"]
        if all(abs(allowed[d] - targets[d]) <= MATERIAL_SHORT for d in decisions
               if d in allowed):
            book_arm, turn_arm = book0, turn0          # nothing was ever blocked
        else:
            diag = []

            def _replay(w, d, path, est, _m=allowed):
                # The opening decision is before the ledger's first bar; it is the opening
                # position there, so it carries the sizing rule's own scale unchanged.
                t = pd.Timestamp(d)
                return float(_m[t]) if t in _m else float(targets[t])

            book_arm, turn_arm = R.open_to_open_equity(
                close[cols], openp[cols], amt[cols], sc, REBAL, NHOLD, COST,
                diag=diag, scale_hook=_replay)
        ser = _compose_with(book_arm, led["contrib"])
        note = {"locked": "rungs roll; deployment limited to matured cash",
                "callable": "every rung re-placed inside the gap to the next decision",
                "break": "deploy in full, forfeit accrued interest on the broken lot"}[name]
        blk = _arm_block("arm/%s" % name, ser, capacity, note)
        blk["cash_cagr_pct"] = led["cash_cagr_pct"]
        blk["sleeve_days"] = led["sleeve_days"]
        blk["portfolio_contrib_pct"] = led["portfolio_contrib_pct"]
        blk["fee_total"] = led["fee_total"]
        blk["leak_events"] = led["leak_events"]
        blk["blocked_events"] = led["blocked_events"]
        blk["blocked_share_of_asks"] = led["blocked_share_of_asks"]
        blk["worst_short"] = led["worst_short"]
        blk["forfeit_pp"] = round(led["penalty_total"] * 100.0, 4)
        blk["turnover_per_side"] = round(float(turn_arm), 4)
        arms[name] = {"block": blk,
                      "cagr": (blk.get("stats") or {}).get("cagr"),
                      "sharpe": (blk.get("stats") or {}).get("sharpe"),
                      "maxdd_pct": (None if (blk.get("stats") or {}).get("maxdd") is None
                                    else round(float(blk["stats"]["maxdd"]) * 100.0, 4)),
                      "top2_share": (blk.get("year_metrics") or {}).get("top2_share"),
                      "Y4_top2_share": (blk.get("checks") or {}).get("Y4_top2_share"),
                      "verdict": blk.get("verdict"),
                      "cash_cagr_pct": blk["cash_cagr_pct"],
                      "sleeve_days": blk["sleeve_days"],
                      "portfolio_contrib_pct": blk["portfolio_contrib_pct"],
                      "fee_total": blk["fee_total"],
                      "leak_events": blk["leak_events"],
                      "blocked_events": blk["blocked_events"],
                      "blocked_share_of_asks": blk["blocked_share_of_asks"],
                      "worst_short": blk["worst_short"],
                      "forfeit_pp": blk["forfeit_pp"]}

    # --- controls that can fail --------------------------------------------------------
    pub = _published_cells(_read_json(KNOBS))
    ok_zero = (pub["cash_zero"]["top2_share"] is not None
               and ctrl_zero.get("year_metrics") is not None
               and abs(float(ctrl_zero["year_metrics"]["top2_share"])
                       - float(pub["cash_zero"]["top2_share"])) <= 1e-4
               and ctrl_zero.get("verdict") == pub["cash_zero"]["verdict"])
    ok_g1 = (pub["gc001_roll"]["top2_share"] is not None
             and ctrl_g1.get("year_metrics") is not None
             and abs(float(ctrl_g1["year_metrics"]["top2_share"])
                     - float(pub["gc001_roll"]["top2_share"])) <= 1e-4
             and ctrl_g1.get("verdict") == pub["gc001_roll"]["verdict"])
    control_ok = bool(ok_zero and ok_g1)
    band = CRITERIA["C0b_ledger_cash_band_pp"]
    led_cash_pub = 1.88      # results/etf_book_gate_knobs.json cash_carrier_cagr_pct.ladder3
    led_cash = ledgers["locked"]["cash_cagr_pct"]
    led_ok = bool(abs(float(led_cash) - led_cash_pub) <= band)

    readings = {
        "control_reproduces_published_cells": control_ok,
        "control_cells": {
            "cash_zero": {"ours": ctrl_zero.get("year_metrics", {}).get("top2_share"),
                          "published": pub["cash_zero"]["top2_share"],
                          "verdict_ours": ctrl_zero.get("verdict"),
                          "verdict_published": pub["cash_zero"]["verdict"]},
            "gc001_roll": {"ours": ctrl_g1.get("year_metrics", {}).get("top2_share"),
                           "published": pub["gc001_roll"]["top2_share"],
                           "verdict_ours": ctrl_g1.get("verdict"),
                           "verdict_published": pub["gc001_roll"]["verdict"]},
        },
        "ledger_cash_cagr_in_band": led_ok,
        "ledger_cash_cagr_pct": led_cash,
        "ledger_cash_cagr_published_pct": led_cash_pub,
        "ledger_cash_cagr_band_pp": band,
        "gate_line_top2_share_max": G.TOP2_SHARE_MAX,
        "arms": {k: {kk: v[kk] for kk in ("cagr", "sharpe", "maxdd_pct", "top2_share",
                                          "Y4_top2_share", "verdict", "cash_cagr_pct",
                                          "sleeve_days", "portfolio_contrib_pct",
                                          "fee_total", "leak_events",
                                          "blocked_events", "blocked_share_of_asks",
                                          "worst_short", "forfeit_pp")}
                 for k, v in arms.items()},
        "controls": {
            "cash_zero": {"top2_share": ctrl_zero.get("year_metrics", {}).get("top2_share"),
                          "verdict": ctrl_zero.get("verdict"),
                          "stats": ctrl_zero.get("stats")},
            "gc001_roll": {"top2_share": ctrl_g1.get("year_metrics", {}).get("top2_share"),
                           "verdict": ctrl_g1.get("verdict"),
                           "stats": ctrl_g1.get("stats")},
        },
        "carry_given_up_for_callable_pp": carry_given_up_pp(
            led_cash, arms["callable"]["cash_cagr_pct"]),
        "blocked_worst_case": ledgers["locked"]["blocked_material"][:8],
        "blocked_events_any": {k: v["blocked_events_any"] for k, v in ledgers.items()},
        "bars": int(len(index)),
        "flips_repaired": int(n_flip),
        "decisions": int(len(decisions)),
    }
    readings["verdict"] = verdict_of(readings)

    rep = {
        "face": "etf_book_cash_lock_gap",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": str(pd.Timestamp(index[-1]).date()),
        "window": {"start": str(pd.Timestamp(index[0]).date()),
                   "end": str(pd.Timestamp(index[-1]).date()), "bars": int(len(index))},
        "question": "The gate's Y4 pass comes from paying the idle sleeve at a repo carry. "
                    "Can that cash actually be raised on the decision bar it is needed?",
        "config": {"n_hold": NHOLD, "rebal": REBAL, "cost_per_side": COST,
                   "vol_target": VOL_TARGET, "ladder": list(LADDER),
                   "tenor_days": {k: int(v) for k, v in TENOR_DAYS.items()},
                   "overnight": OVERNIGHT, "policy": "locked | callable | break"},
        "criteria": CRITERIA,
        "readings": readings,
        "source_faces": {"knobs": os.path.relpath(KNOBS, ROOT)},
        "honest": [
            "an exchange repo contract cannot be broken early; the `break` arm is the cost "
            "of an emergency funding line standing in for that impossibility, and its "
            "number is a lower bound on the price of being wrong about the calendar",
            "the ledger keeps balances in units of NAV, matching the engine's own convention "
            "that weights do not drift between rebalances (the same convention the published "
            "idle-cash face uses); a drifting sleeve would move these numbers by less than "
            "the disclosed rounding",
            "`callable` uses the longest ladder tenor that matures before the NEXT SCHEDULED "
            "decision bar -- knowing your own rebalance date is not a forecast, but it does "
            "assume the treasurer keeps that calendar, and it assumes a rung can be placed "
            "at that bar's close",
            "the sleeve is re-placed on the book's own bar calendar, so a maturity that "
            "lands on a non-bar day waits for the next bar; the interest is booked to the "
            "bar the cash actually returns, not the nominal maturity date",
            "`2026` is a partial calendar year and is flagged partial by the gate's own "
            "60-bar rule, exactly as in the published cells",
            "the book is the gate's 5-name arm; the forward ledger runs 12 names with the "
            "same carrier, and r1739 already showed width does not change the carrier "
            "verdict, so this face does not re-run width",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    with io.open(MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(_md(rep))
    print(json.dumps({"verdict": readings["verdict"],
                      "arms": {k: {"top2": v["top2_share"], "cagr": v["cagr"],
                                   "blocked": v["blocked_events"]}
                               for k, v in readings["arms"].items()},
                      "control_ok": readings["control_reproduces_published_cells"],
                      "out": os.path.relpath(OUT, ROOT),
                      "elapsed_sec": rep["elapsed_sec"]}, ensure_ascii=False))
    return 0


def _md(rep):
    r = rep["readings"]
    L = []
    L.append("# ETF book — can the treasurer hand the cash over on decision day?")
    L.append("")
    L.append("Evidence cutoff **%s**. Generated by `scripts\\etf_book_cash_lock_gap.py`."
             % rep["evidence_cutoff"])
    L.append("")
    L.append("## Verdict")
    L.append("")
    L.append("**%s**" % r["verdict"])
    L.append("")
    L.append("The gate's Y4 pass is bought with a repo carry on the idle sleeve. A repo "
             "contract cannot be sold back before its maturity, so the question is not what "
             "the sleeve earns but whether it can be handed over on the bar the sizing rule "
             "asks for it.")
    L.append("")
    L.append("| arm | sleeve policy | best-two share | line | gate | CAGR | Sharpe | maxDD |")
    L.append("|---|---|---|---|---|---|---|---|")
    rows = (("callable", "re-placed inside the gap to the next decision"),
            ("locked", "rungs roll; deploy only matured cash"),
            ("break", "deploy in full, forfeit accrued interest"))
    for key, desc in rows:
        a = r["arms"][key]
        L.append("| %s | %s | %s | <= %.2f%% | %s | %s | %s | %s |" % (
            key, desc,
            "n/a" if a["top2_share"] is None else "%.2f%%" % (a["top2_share"] * 100.0),
            r["gate_line_top2_share_max"] * 100.0, a["verdict"],
            "n/a" if a["cagr"] is None else "%.2f%%" % (a["cagr"] * 100.0),
            "n/a" if a["sharpe"] is None else "%.3f" % a["sharpe"],
            "n/a" if a["maxdd_pct"] is None else "%.2f%%" % a["maxdd_pct"]))
    for key, desc in (("cash_zero", "sleeve priced at 0 (the gate's own arm)"),
                      ("gc001_roll", "overnight roll, never locked")):
        c = r["controls"][key]
        st = c.get("stats") or {}
        L.append("| *%s* | %s | %s | <= %.2f%% | %s | %s | %s | %s |" % (
            key, desc,
            "n/a" if c["top2_share"] is None else "%.2f%%" % (c["top2_share"] * 100.0),
            r["gate_line_top2_share_max"] * 100.0, c["verdict"],
            "n/a" if st.get("cagr") is None else "%.2f%%" % (float(st["cagr"]) * 100.0),
            "n/a" if st.get("sharpe") is None else "%.3f" % float(st["sharpe"]),
            "n/a" if st.get("maxdd") is None else "%.2f%%" % (float(st["maxdd"]) * 100.0)))
    L.append("")
    L.append("## What the calendar actually costs")
    L.append("")
    lk, ca = r["arms"]["locked"], r["arms"]["callable"]
    L.append("| reading | value |")
    L.append("|---|---|")
    L.append("| cash CAGR: locked ladder (ledger) | %.2f%%/yr |" % lk["cash_cagr_pct"])
    L.append("| cash CAGR: published ladder3 | %.2f%%/yr |"
             % r["ledger_cash_cagr_published_pct"])
    L.append("| cash CAGR: callable ladder | %.2f%%/yr |" % ca["cash_cagr_pct"])
    L.append("| carry given up to stay callable | %.2f pp/yr |"
             % r["carry_given_up_for_callable_pp"])
    L.append("| decisions where the roll could not fund the ask | %d of %d |"
             % (lk["blocked_events"], r["decisions"]))
    L.append("| share of asked cash that was locked | %.1f%% |"
             % (lk["blocked_share_of_asks"] * 100.0))
    L.append("| worst single shortfall (fraction of NAV) | %.3f |" % lk["worst_short"])
    L.append("| interest forfeited by breaking (total, pp of NAV) | %.3f |"
             % r["arms"]["break"]["forfeit_pp"])
    L.append("")
    L.append("## Controls")
    L.append("")
    L.append("| control | ours | published | verdict |")
    L.append("|---|---|---|---|")
    for key in ("cash_zero", "gc001_roll"):
        c = r["control_cells"][key]
        L.append("| %s best-two share | %s | %s | %s / %s |" % (
            key, c["ours"], c["published"], c["verdict_ours"], c["verdict_published"]))
    L.append("| ledger cash CAGR in band (%.2f pp) | %s | %.2f%% vs %.2f%% | %s |" % (
        r["ledger_cash_cagr_band_pp"], r["ledger_cash_cagr_pct"],
        r["ledger_cash_cagr_pct"], r["ledger_cash_cagr_published_pct"],
        "PASS" if r["ledger_cash_cagr_in_band"] else "FAIL"))
    L.append("")
    if r["blocked_worst_case"]:
        L.append("## The decisions that could not be funded")
        L.append("")
        L.append("| date | asked | raised | short |")
        L.append("|---|---|---|---|")
        for b in r["blocked_worst_case"]:
            L.append("| %s | %.3f | %.3f | %.3f |" % (b["date"], b["needed"], b["raised"],
                                                      b["short"]))
        L.append("")
    L.append("## Honest limits")
    L.append("")
    for h in rep["honest"]:
        L.append("- %s" % h)
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------------------
def selftest():
    bad = []

    def chk(ok, msg):
        print("[%s] %s" % ("PASS" if ok else "FAIL", msg))
        if not ok:
            bad.append(msg)

    idx = pd.DatetimeIndex(pd.to_datetime(
        ["2026-01-05", "2026-01-12", "2026-01-19", "2026-01-26", "2026-02-02",
         "2026-02-09", "2026-02-16", "2026-02-23", "2026-03-02"]))
    flat = pd.Series([2.0] * len(idx), index=idx)
    quotes = {1: flat, 7: flat, 14: flat, 28: flat}

    # L1 -- a 28-day contract is not money on the bar it is asked for
    dec = [idx[0], idx[3]]
    led = ledger_pass(idx, {idx[0]: 0.5, idx[3]: 1.0}, dec, quotes, "locked",
                      fees=None)
    chk(led["blocked_events"] == 1 and led["blocked_short_total"] > 0.0
        and led["blocked_material"][0]["kind"] == "lock",
        "a rolled 28-day rung cannot fund the next decision (locked arm is blocked)")

    # L2 -- the same calendar, placed to fit, is never blocked
    led_c = ledger_pass(idx, {idx[0]: 0.5, idx[3]: 1.0}, dec, quotes, "callable",
                        fees=None)
    chk(led_c["blocked_events"] == 0
        and abs(led_c["allowed"][idx[3]] - 1.0) <= MATERIAL_SHORT,
        "callable arm funds the whole ask (no material shortfall) -- commission dust only")

    # L3 -- breaking forfeits exactly the accrued interest of the broken lots
    led_b = ledger_pass(idx, {idx[0]: 0.5, idx[1]: 1.0, idx[3]: 1.0},
                        [idx[0], idx[1], idx[3]], quotes, "locked", allow_break=True,
                        fees=None)
    # At idx[1] the 7-day third has just matured, the 14/28-day thirds are 7 days out:
    # breaking them costs principal * 2% * 7/365 each, i.e. about 1.28e-4 of NAV in total.
    chk(1.20e-4 < led_b["penalty_total"] < 1.35e-4,
        "the break arm charges exactly the accrued interest it forfeits (%.2e)"
        % led_b["penalty_total"])
    one = ledger_pass(idx, {idx[0]: 1.0, idx[3]: 1.0}, [idx[0], idx[3]], quotes, "locked",
                      allow_break=True, fees=None)
    chk(one["blocked_events"] == 0, "break arm never reports an unfunded ask")

    # L4 -- accrual uses calendar days/365, not bar counts (a 7-day rung earns 7 days)
    led7 = ledger_pass(idx, {idx[0]: 0.0}, [idx[0]], quotes, "locked", fees=None)
    chk(abs(led7["cash_cagr_pct"] - 2.0) < 0.35,
        "flat 2%% quotes produce a cash CAGR near 2%%/yr over the window")

    # L5 -- commission is charged once per contract at entry
    led_fee = ledger_pass(idx, {idx[0]: 0.0}, [idx[0]], quotes, "locked", fees=None)
    chk(led_fee["fee_total"] > 0.0 and led_fee["cash_cagr_pct"] < 2.0,
        "commissions are charged at entry and lower the cash CAGR below the gross rate")

    # L6 -- a missing quote parks the money at the sweep rate instead of inventing a rate
    rich = pd.Series([3.0] * len(idx), index=idx)
    sweep = pd.Series([1.0] * len(idx), index=idx)
    holey = {1: sweep, 7: rich, 14: rich,
             28: pd.Series([np.nan] * len(idx), index=idx)}
    led_m = ledger_pass(idx, {idx[0]: 0.0}, [idx[0]], holey, "locked", fees=None)
    chk(led_m["missing_quote_events"] >= 1
        and 2.2 < led_m["cash_cagr_pct"] < 2.5,
        "a missing tenor quote parks its third at the 1% sweep, not at the 3% it never saw")

    # L7 -- the verdict ladder, in order
    def _v(ctrl, callable_, locked_, brk):
        return verdict_of({"control_reproduces_published_cells": ctrl,
                           "arms": {"callable": {"Y4_top2_share": callable_},
                                    "locked": {"Y4_top2_share": locked_},
                                    "break": {"Y4_top2_share": brk}}})
    chk(_v(False, True, True, True) == "CONTROL_FAILED",
        "control failure outranks every arm reading")
    chk(_v(True, True, False, False) == "CALLABLE_LADDER_HOLDS",
        "a callable ladder that passes is the answer that survives the calendar")
    chk(_v(True, False, True, True) == "GATE_NEEDS_CASH_YOU_CANNOT_RAISE",
        "a pass that only exists while the cash is locked is not executable")
    chk(_v(True, False, False, False) == "NEITHER_HOLDS",
        "neither arm passing is reported as neither")

    # L8 -- the constraint only ever lowers exposure, never raises it
    tgt = {idx[0]: 0.9, idx[3]: 1.0, idx[6]: 0.1}
    leds = ledger_pass(idx, tgt, [idx[0], idx[3], idx[6]], quotes, "locked", fees=None)
    chk(all(leds["allowed"][d] <= tgt[d] + 1e-9 for d in tgt),
        "a constrained arm never invests more than the sizing rule asked for")

    # L9 -- the carry cost is a difference of two percentages, so it stays in points
    # (multiplying again by 100 printed "183.11 pp/yr" for what is a 1.83 pp/yr cost)
    chk(abs(carry_given_up_pp(1.8276, -0.0035) - 1.83) < 1e-9,
        "the carry given up is a difference of two percentages (1.83 pp, not 183.11 pp)")
    chk(carry_given_up_pp(1.8276, -0.0035) > 0.0,
        "staying callable costs carry: the sign points at what is given up, not earned")

    print("selftest: %d/%d PASS" % (11 - len(bad), 11))
    return 0 if not bad else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return run()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
