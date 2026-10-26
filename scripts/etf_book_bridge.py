"""ETF book bridge -- the two published faces of "the production book", priced apart.

Two artefacts both call themselves the production book and print different numbers:

  * the **card** (``scripts/etf_book_production.py``): 12 names, 8% vol target applied
    inside the engine, 10bp/side, universe = equity + commodity + convertible,
    headline 9.47%/yr -- engine ``etf_robust_pf.open_to_open_equity``;
  * the **ticket** (``scripts/etf_book_order.py`` + the forward ledger): 5 names, a
    beta-0.20 overlay on the cash remainder at GC001, universe = the ticket KEEP list
    (equity + commodity + crossborder), headline 11.05%/yr -- engine
    ``etf_composite_pf.run_next_open``.

An operator cannot tell which one is "the book" from either page. This script does not
pick one: it starts at the card's printed number and moves ONE knob at a time until it
reaches the ticket's printed number, so the gap gets attributed instead of argued about.

Knobs, in bridge order:

  window    full history          -> 2024-01-01 onward (the width audit's inception)
  universe  ticket KEEP           -> card USE_CLASSES   (+convertible, -crossborder)
  engine    card open_to_open     -> ticket run_next_open
  rule      8% vol target         -> beta 0.20 overlay
  width     12 names              -> 5 names
  cash      idle cash earns 0     -> GC001..GC028 repo ladder
  cost      10bp/side             -> 8bp/side

Why the two engines are not interchangeable (this is the part that is easy to get wrong):
``open_to_open_equity`` takes its decision on the CLOSE of bar d and then accrues the new
book from the OPEN of bar d -- the first leg starts before the decision exists.
``run_next_open`` charges the weight change at the open of the NEXT bar. The selftest pins
both conventions on a one-symbol panel where each final level is hand-computable:

  run_next_open : C_N / O_1        (fill day earns open->close, then close-to-close)
  open_to_open  : O_N / O_1        (every leg is an open-to-open leg)

so on any book whose opens and closes differ the two engines give different answers by
construction, and neither can referee the other.

  python scripts/etf_book_bridge.py run [--cost-bp=10]
  python scripts/etf_book_bridge.py --selftest

Outputs:
  results/etf_book_bridge.json

Exploratory reconciliation: no verdict on admission, no ledger booking, no registry write.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import etf_asset_class as AC                      # noqa: E402  (ticket-side classifier)
import etf_composite_pf as F                      # noqa: E402  (ticket engine + score)
import etf_equity_alpha as AE                     # noqa: E402  (card-side classifier/repair)
import etf_phase_beta_target as BT                # noqa: E402  (beta overlay accounting)
import etf_phase_beta_window as BW                # noqa: E402  (repo cash leg)
import etf_robust_pf as R                         # noqa: E402  (card engine + stats)
import etf_variants_null_rolling as V             # noqa: E402  (ticket KEEP list)
from scripts import etf_book_production as PROD   # noqa: E402  (card universe + constants)
from scripts import etf_book_width_audit as WA    # noqa: E402  (the vol-target schedule)
from scripts import etf_book_order as EO          # noqa: E402  (ticket cadence/overlay)

REBAL = EO.REBAL
TARGET_VOL = PROD.TARGET_VOL
BETA_TARGET = 0.20
COST_BP = 10.0
WIDTHS = (5, 12)
SHORT_START = "2024-01-01"
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "results")


# ---------------------------------------------------------------- universes

def build_panels(raw=None):
    """Both universes off ONE raw panel, so the universe knob is the only difference.

    The ticket and the card classify independently (``etf_asset_class`` name/prefix rules
    vs ``etf_equity_alpha``'s name-then-vol fallback) and keep different class sets, so
    they genuinely hold different books -- that is a knob, not a detail to normalise away.
    """
    if raw is None:
        close, openp, amt, feats = F.build_panel()
    else:
        close, openp, amt, feats = raw
    out = {}

    cols_t = [c for c in close.columns if AC.classify(list(close.columns))[c] in V.KEEP]
    out["ticket"] = {"close": close[cols_t], "openp": openp[cols_t],
                     "amt": amt[cols_t], "feats": feats, "classes": "V.KEEP"}

    close_c, openp_c, n_flip = AE.repair_flips(close, openp)
    cmap = AE.load_class_map()
    cls_c = AE.classify(close_c.columns, cmap, close_c)
    cols_c = [c for c in close_c.columns if cls_c[c] in PROD.USE_CLASSES]
    out["card"] = {"close": close_c[cols_c], "openp": openp_c[cols_c],
                   "amt": amt[cols_c], "feats": feats, "classes": "USE_CLASSES",
                   "flips_repaired": int(n_flip)}
    for pan in out.values():
        pan["score"] = F.build_score(pan["close"], pan["amt"], pan["feats"])
        mkt = next((c for c in BT.MKT if c in pan["close"].columns), None)
        if mkt is None:
            raise SystemExit("FATAL: no market column on the panel")
        pan["mkt"] = pan["close"][mkt]
    # The two class lists nearly coincide; say exactly how nearly, otherwise a "universe"
    # knob that swaps three symbols could be read as two different markets.
    st, sc = set(cols_t), set(cols_c)
    diff = {"ticket_only": sorted(st - sc), "card_only": sorted(sc - st),
            "shared": len(st & sc)}
    return out, diff


# ---------------------------------------------------------------- engines

def card_engine(pan, n_hold, vol_target, cost=0.0010):
    """The card's own engine: open_to_open_equity, vol target applied inside the weights."""
    ser, turn = R.open_to_open_equity(pan["close"], pan["openp"], pan["amt"], pan["score"],
                                      REBAL, n_hold, cost, vol_target=vol_target,
                                      vol_window=60)
    return ser, float(turn)


_BOOK = {}


def book_leg(pan, n_hold, cost=F.COST):
    """Unlevered book at one width -- computed once, shared by every leverage rule.

    Both rules must ride the SAME book series, otherwise the rule step would be measured
    on two different baskets (the r1262 confound).
    """
    key = (id(pan), int(n_hold), round(float(cost), 8))
    if key not in _BOOK:
        _BOOK[key] = F.run_next_open(pan["close"], pan["openp"], pan["amt"], pan["feats"],
                                     REBAL, n_hold=n_hold, cost=cost,
                                     score=pan["score"])
    return _BOOK[key]


def ticket_engine(pan, n_hold, rule="none", cost_bp=COST_BP, repo=False,
                  book_cost=F.COST):
    """The ticket engine + its two leverage rules (none / vol8 / beta0.20).

    ``rule='none'`` returns the unlevered book series (no overlay leg at all), so the
    bridge can price the rule step as a real change rather than as k=1 arithmetic.
    ``book_cost`` is the per-side rate on the BOOK leg; the overlay charges its own
    ``cost_bp`` on the k leg. Setting both to zero isolates the fill convention from fees.
    """
    ser, turn, _gap = book_leg(pan, n_hold, cost=book_cost)
    if rule == "none":
        return ser, float(turn), None
    idx = ser.index.intersection(pan["mkt"].index)
    rp = BT.rets(ser.reindex(idx))
    rm = BT.rets(pan["mkt"].reindex(idx))
    if rule == "vol":
        sched = WA.vol_schedule(rp, rm, TARGET_VOL)
    elif rule == "beta":
        sched = EO.k_schedule(rp, rm, BETA_TARGET)
    else:
        raise SystemExit("FATAL: unknown rule %r" % rule)
    rf = None
    missing = 0
    if repo:
        rates = BW.load_repo_rates()
        cash_rf, missing = BW.repo_daily_cash(idx, rates)
        rf = cash_rf.reindex(idx).fillna(0.0)
    strat, _bench, kk = BT.apply_overlay(rp, rm, sched, 0.0, cost_bp, rf=rf)
    if strat is None:
        raise SystemExit("FATAL: overlay produced no live window (n=%d rule=%s)"
                         % (n_hold, rule))
    return strat, float(turn), {"k_mean": round(float(kk.mean()), 4),
                                "cash_share": round(float((1.0 - kk).mean()), 4),
                                "cash_leg_missing_bars": int(missing)}


# ---------------------------------------------------------------- stats

def stat(ser, start=None):
    """R.stats on an optional slice -- one metrics implementation for every cell."""
    if ser is None or not len(ser):
        return {}
    s = ser if start is None else ser[ser.index >= pd.Timestamp(start)]
    if len(s) < 40:
        return {}
    m = R.stats(s, "")
    return {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}


def cell(ser, turn, extra=None):
    out = {"turnover_per_decision": round(float(turn), 3),
           "full": stat(ser), "since2024": stat(ser, SHORT_START)}
    if extra:
        out.update(extra)
    return out


def cagr(c, win="full"):
    return ((c or {}).get(win) or {}).get("cagr")


def pp(a, b):
    if a is None or b is None:
        return None
    return round(100.0 * (b - a), 2)


# ---------------------------------------------------------------- run

def run(cost_bp=COST_BP):
    pans, uni_diff = build_panels()
    rows = {}
    print("universes: ticket=%d cols, card=%d cols"
          % (len(pans["ticket"]["close"].columns), len(pans["card"]["close"].columns)),
          flush=True)

    # card engine: width x rule (the card's own 2x2)
    for name, pan in pans.items():
        for n in WIDTHS:
            for lbl, vt in (("none", None), ("vol8", TARGET_VOL)):
                ser, turn = card_engine(pan, n, vt)
                rows["card@%s|n%d|%s" % (name, n, lbl)] = cell(ser, turn)

    # ticket engine: width x rule (none / vol8 / beta), plus the repo cash variant
    for name, pan in pans.items():
        for n in WIDTHS:
            for rule in ("none", "vol", "beta"):
                if rule == "none":
                    ser, turn, extra = ticket_engine(pan, n, "none")
                    rows["ticket@%s|n%d|none" % (name, n)] = cell(ser, turn, extra)
                else:
                    ser, turn, extra = ticket_engine(pan, n, rule, cost_bp=cost_bp)
                    rows["ticket@%s|n%d|%s" % (name, n, rule)] = cell(ser, turn, extra)
                    ser_c, turn_c, extra_c = ticket_engine(pan, n, rule, cost_bp=cost_bp,
                                                           repo=True)
                    rows["ticket@%s|n%d|%s+repo" % (name, n, rule)] = cell(ser_c, turn_c,
                                                                          extra_c)
                print("%-28s cagr %6.2f%% (2024+ %6.2f%%)"
                      % (list(rows)[-1], 100.0 * (cagr(rows[list(rows)[-1]]) or 0.0),
                         100.0 * (cagr(rows[list(rows)[-1]], "since2024") or 0.0)),
                      flush=True)

    # fee-free twins at the published width: without them the "engine" step is a black box
    # (fill convention? fee accounting? the leverage estimator?), and those three call for
    # completely different fixes.
    for name, pan in pans.items():
        ser, turn = card_engine(pan, 12, TARGET_VOL, cost=0.0)
        rows["card@%s|n12|vol8@0bp" % name] = cell(ser, turn)
    ser, turn, extra = ticket_engine(pans["ticket"], 12, "vol", cost_bp=0.0,
                                     book_cost=0.0)
    rows["ticket@ticket|n12|vol@0bp"] = cell(ser, turn, extra)
    print("fee-free twins: card@ticket %.2f%% / ticket@ticket %.2f%% (2024+)"
          % (100.0 * (cagr(rows["card@ticket|n12|vol8@0bp"], "since2024") or 0.0),
             100.0 * (cagr(rows["ticket@ticket|n12|vol@0bp"], "since2024") or 0.0)),
          flush=True)

    # ---- width effect, per engine / rule / window (this is r1278's open question)
    width = {}
    for key, base in (("card|none", "card@%s|n%d|none"), ("card|vol8", "card@%s|n%d|vol8"),
                      ("ticket|none", "ticket@%s|n%d|none"),
                      ("ticket|vol", "ticket@%s|n%d|vol"),
                      ("ticket|beta", "ticket@%s|n%d|beta"),
                      ("ticket|beta+repo", "ticket@%s|n%d|beta+repo")):
        for uni in ("ticket", "card"):
            for win in ("full", "since2024"):
                a = rows.get(base % (uni, 5)) or {}
                b = rows.get(base % (uni, 12)) or {}
                width.setdefault(key, {}).setdefault(uni, {})[win] = pp(cagr(a, win),
                                                                       cagr(b, win))

    # ---- engine delta, fixed universe / width / rule / window
    engine = {}
    for uni in ("ticket", "card"):
        for rule in ("none", "vol"):
            for n in WIDTHS:
                a = rows.get("card@%s|n%d|%s" % (uni, n, "vol8" if rule == "vol" else "none"))
                b = rows.get("ticket@%s|n%d|%s" % (uni, n, rule))
                for win in ("full", "since2024"):
                    engine.setdefault("n%d|%s|%s" % (n, rule, uni), {})[win] = pp(
                        cagr(a, win), cagr(b, win))

    # ---- universe delta, fixed engine / width / rule / window
    universe = {}
    for rule in ("none", "vol"):
        for n in WIDTHS:
            a = rows.get("ticket@ticket|n%d|%s" % (n, rule))
            b = rows.get("ticket@card|n%d|%s" % (n, rule))
            for win in ("full", "since2024"):
                universe.setdefault("n%d|%s" % (n, rule), {})[win] = pp(cagr(a, win),
                                                                       cagr(b, win))

    # ---- the bridge: card's printed face -> ticket's printed face
    steps = []

    def snap(key, win="full"):
        return {"key": key, "cagr": cagr(rows.get(key), win)}

    start = {"key": "card@card|n12|vol8", "cagr": cagr(rows.get("card@card|n12|vol8"))}
    chain = [
        ("window", "full history -> 2024-01-01", "card@card|n12|vol8", "full",
         "card@card|n12|vol8", "since2024"),
        ("universe", "card USE_CLASSES -> ticket KEEP", "card@card|n12|vol8", "since2024",
         "card@ticket|n12|vol8", "since2024"),
        ("card-fee", "10bp -> no fee (card engine)", "card@ticket|n12|vol8", "since2024",
         "card@ticket|n12|vol8@0bp", "since2024"),
        ("basis", "open_to_open -> run_next_open, no fee either side",
         "card@ticket|n12|vol8@0bp", "since2024", "ticket@ticket|n12|vol@0bp", "since2024"),
        ("ticket-fee", "no fee -> book 8bp + k-leg 10bp", "ticket@ticket|n12|vol@0bp",
         "since2024", "ticket@ticket|n12|vol", "since2024"),
        ("rule", "vol 8% -> beta 0.20", "ticket@ticket|n12|vol", "since2024",
         "ticket@ticket|n12|beta", "since2024"),
        ("width", "12 names -> 5 names", "ticket@ticket|n12|beta", "since2024",
         "ticket@ticket|n5|beta", "since2024"),
        ("cash", "nothing -> repo ladder", "ticket@ticket|n5|beta", "since2024",
         "ticket@ticket|n5|beta+repo", "since2024"),
    ]
    for knob, desc, before, win_b, after, win_a in chain:
        a = cagr(rows.get(before), win_b)
        b = cagr(rows.get(after), win_a)
        steps.append({"knob": knob, "move": desc, "before": before, "after": after,
                      "window": win_a, "cagr_before": a, "cagr_after": b,
                      "effect_pp": pp(a, b)})
    # cost is the last knob: re-run the final cell at the ticket's 8bp
    ser, turn, extra = ticket_engine(pans["ticket"], 5, "beta", cost_bp=8.0, repo=True)
    rows["ticket@ticket|n5|beta+repo@8bp"] = cell(ser, turn, extra)
    a = cagr(rows.get("ticket@ticket|n5|beta+repo"), "since2024")
    b = cagr(rows.get("ticket@ticket|n5|beta+repo@8bp"), "since2024")
    steps.append({"knob": "cost", "move": "10bp -> 8bp/side",
                  "before": "ticket@ticket|n5|beta+repo",
                  "after": "ticket@ticket|n5|beta+repo@8bp", "window": "since2024",
                  "cagr_before": a, "cagr_after": b, "effect_pp": pp(a, b)})
    end = {"key": "ticket@ticket|n5|beta+repo@8bp", "cagr": b}
    total = pp(start["cagr"], end["cagr"])
    summed = round(sum(s["effect_pp"] or 0.0 for s in steps), 2)
    print("bridge: %.2f%% -> %.2f%% (total %+.2fpp, steps sum %+.2fpp)"
          % (100.0 * (start["cagr"] or 0), 100.0 * (end["cagr"] or 0), total, summed),
          flush=True)
    for s in steps:
        print("  %-10s %-46s %+6.2fpp" % (s["knob"], s["move"], s["effect_pp"] or 0.0),
              flush=True)
    if abs(summed - total) > 0.05:
        raise SystemExit("FATAL: bridge is not additive (sum %.2f vs total %.2f)"
                         % (summed, total))

    # ---- the two engines' "8% vol target" is two different rules: measure the delivery
    label_div = {}
    for key, lbl in (("card@card|n12|vol8", "card_engine@card_panel"),
                     ("card@ticket|n12|vol8", "card_engine@ticket_panel"),
                     ("ticket@ticket|n12|vol", "ticket_engine@ticket_panel"),
                     ("ticket@card|n12|vol", "ticket_engine@card_panel")):
        r = rows.get(key) or {}
        vol = (r.get("full") or {}).get("vol")
        label_div[lbl] = {"delivered_vol_full": vol,
                          "ratio_to_label": round(float(vol) / TARGET_VOL, 3)
                          if vol else None,
                          "k_mean": r.get("k_mean")}
    print("vol label: card engine delivers %s of its 8%% label, ticket overlay %s"
          % (label_div["card_engine@card_panel"]["ratio_to_label"],
             label_div["ticket_engine@ticket_panel"]["ratio_to_label"]), flush=True)

    # published artefacts, for the two endpoints (report, never re-derived silently)
    published = {}
    try:
        card = json.load(open(os.path.join(OUT_DIR, "etf_book_production", "latest.json"),
                              encoding="utf-8"))
        published["card_n12_vt08_full"] = card["backtest"]["n12_vt08"]["full"]["cagr"]
        published["card_n5_vt08_full"] = card["backtest"]["n5_vt08"]["full"]["cagr"]
    except (OSError, KeyError, ValueError):
        published["card_n12_vt08_full"] = None
    try:
        wa = json.load(open(os.path.join(OUT_DIR, "etf_book_width_audit.json"),
                            encoding="utf-8"))
        for r in (wa.get("rows") or []):
            if r.get("n_hold") == 5 and r.get("rule") == "beta":
                published["ticket_beta_n5_since2024"] = ((r.get("book") or {}).get("cagr"))
    except (OSError, KeyError, ValueError):
        published["ticket_beta_n5_since2024"] = None

    out = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(max(pan["close"].index[-1].date()
                                   for pan in pans.values())),
        "script": "scripts/etf_book_bridge.py",
        "config": {"rebal": REBAL, "widths": list(WIDTHS), "target_vol": TARGET_VOL,
                   "beta_target": BETA_TARGET, "cost_bp_per_side": cost_bp,
                   "short_start": SHORT_START,
                   "universe_sizes": {k: len(v["close"].columns) for k, v in pans.items()},
                   "universe_diff": uni_diff},
        "arms": rows,
        "width_effect_pp": width,
        "engine_delta_pp": engine,
        "universe_delta_pp": universe,
        "vol_label_delivery": label_div,
        "bridge": {"start": start, "steps": steps, "end": end,
                   "total_pp": total, "steps_sum_pp": summed,
                   "path_dependent": True},
        "published": published,
        "caveats": [
            "Path-dependent attribution: the step ORDER is one path through a factorial; "
            "an interaction-heavy knob (rule x width) will move between positions.",
            "Both engines are charged a per-side rate on turnover, but they apply the vol "
            "scale differently (inside the weights vs on top of an unlevered book), so the "
            "engine step carries a little accounting with it -- disclosed, not netted.",
            "The card engine accrues the new book from the open of its decision bar, i.e. "
            "one bar of return exists before the decision does; run_next_open fills at "
            "open(d+1). Neither engine can referee the other's level.",
            "Survivorship (the ETF pool is today's list) applies to every cell equally and "
            "is NOT what the differences measure.",
        ],
    }
    lp = os.path.join(OUT_DIR, "etf_book_bridge.json")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(lp, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("wrote", lp, flush=True)
    return out


# ---------------------------------------------------------------- selftest

def _synth(n=200, gap=0.01):
    """One eligible symbol: flat universe so both engines hold it 100% of the time."""
    dates = pd.bdate_range("2020-01-01", periods=n)
    close = 100.0 * (1.004 ** np.arange(n))
    openp = close * (1.0 + gap * ((np.arange(n) % 2) * 2 - 1))
    c = pd.DataFrame({"510300": close}, index=dates)
    o = pd.DataFrame({"510300": openp}, index=dates)
    a = pd.DataFrame({"510300": np.full(n, 1e9)}, index=dates)
    return c, o, a


def selftest():
    ok = 0
    bad = []

    def chk(name, cond, msg=""):
        nonlocal ok
        if cond:
            ok += 1
            print("[PASS] %s %s" % (name, msg), flush=True)
        else:
            bad.append(name)
            print("[FAIL] %s %s" % (name, msg), flush=True)

    # L1 -- metrics sanity: doubling over exactly 2 years
    idx = pd.date_range("2020-01-01", periods=731, freq="D")
    double = pd.Series(np.linspace(1.0, 2.0, 731), index=idx)
    m = stat(double)
    chk("metrics:cagr", abs((m.get("cagr") or 0) - 0.4142) < 1e-3,
        "cagr=%.4f" % (m.get("cagr") or 0))
    chk("metrics:dd", abs(m.get("maxdd") or 0) < 1e-9, "maxdd=%.3e" % (m.get("maxdd") or 0))

    # L2 -- the two fill conventions, hand-computable on a one-symbol panel
    c, o, a = _synth()
    n = len(c)
    score = pd.DataFrame(1.0, index=c.index, columns=c.columns)
    t_ser, _t, _g = F.run_next_open(c, o, a, None, 1, n_hold=1, cost=0.0, score=score)
    k_ser, _k = R.open_to_open_equity(c, o, a, score, 1, 1, 0.0)
    warm = int(F.MIN_HIST)              # first bar whose history clears the gate
    C, O = c.iloc[:, 0], o.iloc[:, 0]
    # run_next_open decides every bar (a full score was supplied), so it fills at bar 1 and
    # books close(1)/open(1) then close-to-close: C_N / O_1. The card engine cannot pick
    # until the eligible history clears MIN_HIST, so its first leg is open(120)/open(119)
    # and it books open-to-open from there: O_N / O_{warm-1}.
    exp_ticket = float(C.iloc[n - 1] / O.iloc[1])
    exp_card = float(O.iloc[n - 1] / O.iloc[warm - 1])
    chk("engine:ticket_final", abs(float(t_ser.iloc[-1]) - exp_ticket) < 1e-9,
        "%.10f vs %.10f" % (float(t_ser.iloc[-1]), exp_ticket))
    chk("engine:card_final", abs(float(k_ser.iloc[-1]) - exp_card) < 1e-9,
        "%.10f vs %.10f" % (float(k_ser.iloc[-1]), exp_card))
    # activity: both must actually trade, otherwise the identities above are trivially free
    chk("engine:traded", len(t_ser) > 100 and len(k_ser) > 100,
        "bars %d/%d" % (len(t_ser), len(k_ser)))
    chk("engine:not_flat", float(t_ser.iloc[-1]) != 1.0 and float(k_ser.iloc[-1]) != 1.0,
        "levels %.4f/%.4f" % (float(t_ser.iloc[-1]), float(k_ser.iloc[-1])))

    def live_growth(ser):
        """Growth over the window both engines actually hold the book in."""
        sl = ser[ser.index >= c.index[warm]]
        return float(sl.iloc[-1]) / float(sl.iloc[0])

    # L3 -- same window, opens == closes: the two conventions must agree exactly, which is
    # what proves the delta on a real panel comes from the open/close face, not from the
    # warm-up offset.
    c2, o2, a2 = _synth(gap=0.0)
    t2, _x, _y = F.run_next_open(c2, o2, a2, None, 1, n_hold=1, cost=0.0, score=score)
    k2, _z = R.open_to_open_equity(c2, o2, a2, score, 1, 1, 0.0)
    g_t, g_k = live_growth(t2), live_growth(k2)
    chk("engine:no_gap_agrees", abs(g_t - g_k) < 1e-9,
        "growth %.10f vs %.10f" % (g_t, g_k))
    # ... and with a real gap they must disagree, otherwise "engine delta" would be a myth
    g_t1, g_k1 = live_growth(t_ser), live_growth(k_ser)
    chk("engine:conventions_differ", abs(g_t1 / g_k1 - 1.0) > 1e-3,
        "growth %.6f vs %.6f (rel %.5f)" % (g_t1, g_k1, abs(g_t1 / g_k1 - 1.0)))

    # L4 -- bridge arithmetic is additive by construction
    vals = [0.0947, 0.152, 0.1188, 0.1152, 0.1105, 0.1157, 0.1169]
    st = [{"effect_pp": pp(vals[i], vals[i + 1])} for i in range(len(vals) - 1)]
    chk("bridge:additive",
        abs(sum(s["effect_pp"] for s in st) - pp(vals[0], vals[-1])) < 0.02,
        "sum=%.2f total=%.2f" % (sum(s["effect_pp"] for s in st), pp(vals[0], vals[-1])))

    # L5 -- pp helper direction: positive means the AFTER arm is higher
    chk("helper:pp_sign", pp(0.10, 0.12) == 2.0 and pp(0.12, 0.10) == -2.0,
        "pp(0.10,0.12)=%s" % pp(0.10, 0.12))

    print("selftest %d/%d PASS" % (ok, ok + len(bad)), flush=True)
    return 0 if not bad else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--cost-bp", type=float, default=COST_BP)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.cmd == "run":
        run(cost_bp=args.cost_bp)
        return 0
    raise SystemExit("unknown subcommand: %s" % args.cmd)


if __name__ == "__main__":
    sys.exit(main())