"""ETF book card-track -- does the paper book own the exact book the card tells a reader to own?

The production book now exists as four separate faces: the card (what to hold), the ticket
(what to buy today), the forward ledger (what the paper book says it holds) and the CEO page
(what a reader is shown). r1290 caught the card and the ticket describing different days;
r1291 caught a lookup keyed on width only. Both were found by a human asking a question the
tree could not answer. This face answers the question that was still unasked: the ledger's
`book_in_force` block and the card's `sheet.legs` are two independent records of the SAME
frozen decision, and until now nothing compared them.

What it reports, all of it re-derived (never a literal):

  AGREEMENT  same decision bar / same names (set and order) / max |weight| difference /
             scale and cash differences, read from card and ledger respectively.
  DRIFT      the weights the frozen decision has drifted to by the last recorded bar, priced
             off the fill bar's OPEN through the panel closes, plus the one-way turnover (and
             its cost in bp) a re-target to the frozen weights would take TODAY. That number
             is the part of the next decision's bill that buys nothing -- it is paid to undo
             price drift, not to act on a new view.
  IDENTITY   the ledger's recorded nav path re-derived from those same fixed shares. If the
             paper book ever books a trade it did not publish, or loses a name, this leg
             moves. Tolerance covers exactly one thing: the repo carry the ledger credits to
             the cash leg and this reconstruction does not (reported separately, not hidden).

Honest limits, printed with the numbers: a 3-bar ledger cannot tell you whether the book
makes money (that is `etf_book_forward.significance`), and agreement today does not prove
agreement tomorrow -- the value is that the comparison now runs every round instead of when
someone thinks to look.

  python scripts/etf_book_card_track.py run
  python scripts/etf_book_card_track.py --selftest
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_book_forward as F
import etf_book_production as P
import etf_robust_pf as R
from config import PATHS

SCHEMA = "etf-book-card-track/v1"
CARD = os.path.join(PATHS.results_dir, "etf_book_production", "latest.json")
OUT = os.path.join(PATHS.results_dir, "etf_book_card_track.json")

W_TOL = 2e-3          # weights are published to 4 decimals on the card
SCALE_TOL = 2e-3
NAV_TOL = 1e-9        # the constant-weight re-derivation is exact; anything bigger is a trade


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def agree(card, led, w_tol=W_TOL, scale_tol=SCALE_TOL):
    """Compare the card's frozen decision against the ledger's `book_in_force`."""
    sheet = (card or {}).get("sheet") or {}
    bif = (led or {}).get("book_in_force") or {}
    legs = sheet.get("legs") or []
    card_names = [str(l.get("symbol")) for l in legs]
    led_names = [str(n) for n in (bif.get("names") or [])]
    card_w = {str(l.get("symbol")): float(l.get("weight") or 0.0) for l in legs}
    n = len(led_names)
    led_w = {k: (float(bif.get("scale") or 0.0) / n) for k in led_names} if n else {}
    common = sorted(set(card_w) & set(led_w))
    max_w = max((abs(card_w[k] - led_w[k]) for k in common), default=None)
    cash_card = sheet.get("cash_weight")
    cash_led = (1.0 - float(bif.get("scale") or 0.0)) if bif.get("scale") is not None else None
    scale_card = sheet.get("risk_scale")
    return {
        "card_decided_bar": sheet.get("book_decided_at"),
        "ledger_decided_bar": bif.get("bar"),
        "same_decision_bar": sheet.get("book_decided_at") == bif.get("bar"),
        "card_names": len(card_names),
        "ledger_names": y_n(led_names),
        "same_name_set": set(card_names) == set(led_names),
        "same_name_order": card_names == led_names,
        "missing_on_card": sorted(set(led_names) - set(card_names)),
        "missing_on_ledger": sorted(set(card_names) - set(led_names)),
        "max_weight_diff": None if max_w is None else round(max_w, 8),
        "weight_agrees": None if max_w is None else bool(max_w <= w_tol),
        "scale_card": scale_card,
        "scale_ledger": None if bif.get("scale") is None else round(float(bif["scale"]), 8),
        "scale_diff": (None if scale_card is None or bif.get("scale") is None
                       else round(abs(float(scale_card) - float(bif["scale"])), 8)),
        "cash_card": cash_card,
        "cash_ledger": None if cash_led is None else round(cash_led, 8),
        "cash_diff": (None if cash_card is None or cash_led is None
                      else round(abs(float(cash_card) - cash_led), 8)),
        "agrees": bool(
            sheet.get("book_decided_at") == bif.get("bar")
            and set(card_names) == set(led_names)
            and max_w is not None and max_w <= w_tol
            and scale_card is not None and bif.get("scale") is not None
            and abs(float(scale_card) - float(bif["scale"])) <= scale_tol
        ),
    }


def y_n(names):
    return {"n": len(names), "symbols": names}


def drift(led, close, openp, cost_per_side=None):
    """Weights the frozen decision has drifted to, and what undoing that drift costs."""
    bif = (led or {}).get("book_in_force") or {}
    bars = (led or {}).get("bars") or []
    names = [str(n) for n in (bif.get("names") or [])]
    scale = bif.get("scale")
    if not names or scale is None or len(bars) < 1:
        return {"available": False, "reason": "ledger has no book in force or no bars"}
    dates = [str(d.date()) if hasattr(d, "date") else str(d) for d in close.index]
    decision = bif.get("bar")
    if decision not in dates:
        return {"available": False, "reason": "decision bar %s not on the panel" % decision}
    missing = [n for n in names if n not in close.columns or n not in openp.columns]
    if missing:
        return {"available": False, "reason": "names missing from panel", "missing": missing}
    di = dates.index(decision)
    if di + 1 >= len(dates):
        return {"available": False, "reason": "no bar after the decision to fill on"}
    fill_bar = dates[di + 1]
    seed_bar = (led.get("seed") or {}).get("bar")
    last_bar = bars[-1].get("bar")
    if seed_bar not in dates or last_bar not in dates:
        return {"available": False, "reason": "seed/last bar not on the panel"}
    if dates.index(seed_bar) < dates.index(fill_bar):
        return {"available": False, "reason": "seed bar is before the fill bar"}

    n = len(names)
    w0 = float(scale) / n
    cash0 = 1.0 - float(scale)
    p_fill = openp.loc[fill_bar, names].astype(float)
    if not np.all(np.isfinite(p_fill.values)) or np.any(p_fill.values <= 0):
        return {"available": False, "reason": "non-finite fill price"}
    # Fixed shares bought at the fill: value per unit of starting NAV.
    v_seed = {k: w0 * float(close.loc[seed_bar, k]) / float(p_fill[k]) for k in names}
    tot_seed = sum(v_seed.values()) + cash0
    w_seed = {k: v_seed[k] / tot_seed for k in names}
    cash_seed = cash0 / tot_seed

    v_last = {k: v_seed[k] * float(close.loc[last_bar, k]) / float(close.loc[seed_bar, k])
              for k in names}
    tot_last = sum(v_last.values()) + cash_seed
    w_last = {k: v_last[k] / tot_last for k in names}

    # One-way turnover to re-target the frozen weights today (cash leg included, since the
    # cash weight drifts with the book just like a name does -- comparing it against its own
    # seed value would report zero drift on a book that has drifted 20% in value).
    cash_last = cash_seed / tot_last
    turn = 0.5 * sum(abs(w_last[k] - w0) for k in names) + 0.5 * abs(cash_last - cash0)
    cp = F.CONFIG["cost_per_side"] if cost_per_side is None else cost_per_side

    # Two reconstructions, because they answer different questions.
    #
    # (a) CONSTANT WEIGHT: what the ledger actually books. `_leg` charges sum(w*r) with the
    #     frozen w on every bar and adds carry on the target cash fraction, i.e. it assumes
    #     the weights are restored to target for free at every close. Re-deriving that path
    #     must equal the recorded nav to rounding -- that is the real identity, and it is
    #     what catches a trade the paper book never published.
    # (b) BUY AND HOLD: what a reader who follows the card literally owns. Its weights drift
    #     and it pays nothing until the next decision. The gap between (a) and (b) is the
    #     price of the convention, reported instead of asserted away.
    # NB the recorded per-bar `carry` is already the PORTFOLIO contribution (cash weight x
    # ladder rate), so it is added as-is; multiplying by the cash weight again under-charges
    # it by 30% and the identity leg then reads a phantom trade (caught in-window).
    cum_carry = sum((b.get("carry") or 0.0) for b in bars)
    nav_hat, dev, nav_bh = {}, [], {}
    cur_cw, cur_bh = 1.0, 1.0
    prev = None
    for b in bars:
        bar = b.get("bar")
        if bar not in dates:
            continue
        bh = sum(w_seed[k] * float(close.loc[bar, k]) / float(close.loc[seed_bar, k])
                 for k in names) + cash_seed
        nav_bh[bar] = bh
        if prev is None:
            cur_cw = 1.0
        else:
            ret = sum(w0 * (float(close.loc[bar, k]) / float(close.loc[prev, k]) - 1.0)
                      for k in names)
            cur_cw *= (1.0 + ret + (b.get("carry") or 0.0))
        nav_hat[bar] = cur_cw
        prev = bar
        if b.get("nav") is not None:
            dev.append(abs(cur_cw - float(b["nav"])))
    worst = max(dev) if dev else None
    bh_dev = None
    if bars and bars[-1].get("nav") is not None and nav_bh.get(bars[-1].get("bar")) is not None:
        bh_dev = abs(nav_bh[bars[-1]["bar"]] - float(bars[-1]["nav"]))

    # Where the decision grid stands now, off the ENGINE's dates (>= R.START). Counting bars
    # on the wider raw panel index shifts the modulo-20 grid and misreports the countdown.
    eng = openp.index[openp.index >= pd.Timestamp(R.START)]
    gp = P.grid_position(list(eng), pd.Timestamp(last_bar), F.CONFIG["rebal"])
    return {
        "available": True,
        "decision_bar": decision,
        "fill_bar": fill_bar,
        "seed_bar": seed_bar,
        "last_bar": last_bar,
        "names": n,
        "target_weight_each": round(w0, 8),
        "cash_target": round(cash0, 8),
        "weights_at_seed": {k: round(v, 6) for k, v in w_seed.items()},
        "weights_at_last": {k: round(v, 6) for k, v in w_last.items()},
        "top_drift_pp": round(max(((w_last[k] - w0) * 100 for k in names), key=abs), 4),
        "top_drift_name": max(names, key=lambda k: abs(w_last[k] - w0)),
        "max_abs_weight_drift_pp": round(max(abs(w_last[k] - w0) for k in names) * 100, 4),
        "drift_turnover_one_way": round(turn, 6),
        "drift_cost_bp": round(turn * cp * 1e4, 2),
        "next_decision_bars": gp.get("bars_until_next_decision"),
        "nav_identity_max_dev": None if worst is None else round(worst, 10),
        "nav_identity_ok": None if worst is None else bool(worst <= NAV_TOL),
        "nav_buyhold_gap": None if bh_dev is None else round(bh_dev, 10),
        "nav_buyhold_gap_bp": None if bh_dev is None else round(bh_dev * 1e4, 3),
        "cum_carry_bars": round(cum_carry, 10),
        "bars_matched": len(dev),
        "convention": ("ledger books constant target weights every bar (costless implicit "
                       "rebalance) + carry on the target cash fraction; a card follower holds "
                       "drifting weights, so nav_buyhold_gap is the convention's own footprint"),
    }


def build(card=None, led=None, close=None, openp=None):
    card = load_json(CARD) if card is None else card
    led = json.load(open(F.LEDGER, encoding="utf-8")) if led is None else led
    if close is None or openp is None:
        close, openp, _amt, _feats, _score, _cls, _flip = F.build_inputs()
        close = close.ffill()
    out = {
        "schema": SCHEMA,
        "ts": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(close.index[-1].date()) if len(close.index) else None,
        "card_path": os.path.relpath(CARD, os.path.dirname(os.path.dirname(CARD))),
        "ledger_path": os.path.relpath(F.LEDGER, os.path.dirname(os.path.dirname(F.LEDGER))),
        "agreement": agree(card, led),
        "drift": drift(led, close, openp),
        "caveats": [
            ("Agreement is a snapshot of two records of one frozen decision; it does not "
             "make either record correct, and it will not catch a both-faces-wrong defect."),
            ("The drift cost is the price of restoring frozen weights today; the engine only "
             "pays it on a grid decision bar, so it is an upper bound on what drift costs."),
            ("A 3-bar ledger cannot resolve a return edge -- see the significance block in "
             "results/etf_book_forward/LEDGER.json. This face measures book-keeping, not skill."),
        ],
    }
    return out


def main():
    if "--selftest" in sys.argv:
        return selftest()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd not in ("run",):
        print("usage: etf_book_card_track.py [run|--selftest]")
        return 2
    out = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    a, d = out["agreement"], out["drift"]
    print("CARD-TRACK %s card=%s ledger=%s agreement=%s | weights maxdiff=%s scale=%.4f/%.4f cash=%.4f/%.4f"
          % (out["evidence_cutoff"], a["card_names"], a["ledger_names"]["n"],
             "AGREE" if a["agrees"] else "MISMATCH",
             a["max_weight_diff"], a["scale_card"] or float("nan"),
             a["scale_ledger"] or float("nan"), a["cash_card"] or float("nan"),
             a["cash_ledger"] or float("nan")), flush=True)
    if d.get("available"):
        print("DRIFT since %s: max |dw| %.3fpp (%s %+.3fpp) -> re-target costs %.2fbp of nav "
              "(turn %.4f one way); %d bars to the next decision; nav identity maxdev %.2e "
              "(ok=%s, %d bars)"
              % (d["decision_bar"], d["max_abs_weight_drift_pp"], d["top_drift_name"],
                 d["top_drift_pp"], d["drift_cost_bp"], d["drift_turnover_one_way"],
                 d["next_decision_bars"], d["nav_identity_max_dev"], d["nav_identity_ok"],
                 d["bars_matched"]), flush=True)
    else:
        print("DRIFT unavailable: %s" % d.get("reason"), flush=True)
    print("wrote %s" % os.path.relpath(OUT), flush=True)
    return 0 if a["agrees"] and d.get("available") and d.get("nav_identity_ok") is not False else 1


def selftest():
    """Every leg is either a fixture that must fire or the live artefacts re-read."""
    n_ok = 0
    total = 0
    fails = []

    def chk(name, cond, detail=""):
        nonlocal n_ok, total
        total += 1
        if cond:
            n_ok += 1
        else:
            fails.append("%s %s" % (name, detail))

    def fixture(names=("A", "B"), scale=0.8, bar="2026-01-02", w=None, led_scale=None,
                led_bar=None, led_names=None):
        legs = [{"symbol": k, "weight": (w if w is not None else scale / len(names))}
                for k in names]
        card = {"sheet": {"book_decided_at": bar, "risk_scale": scale,
                          "cash_weight": 1 - scale, "legs": legs}}
        led = {"book_in_force": {"bar": led_bar or bar,
                                 "scale": scale if led_scale is None else led_scale,
                                 "names": list(led_names if led_names is not None else names)},
               "bars": [], "seed": {"bar": bar}}
        return card, led

    c, l = fixture()
    a = agree(c, l)
    chk("L1 identical records agree", a["agrees"] and a["max_weight_diff"] == 0.0, str(a))
    chk("L1b name set and order both flagged", a["same_name_set"] and a["same_name_order"])

    c, l = fixture(led_names=("B", "A"))
    a = agree(c, l)
    chk("L2 reordered names still agree on the set", a["same_name_set"] and not a["same_name_order"])
    chk("L2b order change alone keeps agrees true", a["agrees"] is True)

    c, l = fixture(led_names=("A", "C"))
    a = agree(c, l)
    chk("L3 a dropped name fails the agreement", a["agrees"] is False
        and a["missing_on_card"] == ["C"] and a["missing_on_ledger"] == ["B"], str(a))

    c, l = fixture(led_scale=0.6)
    a = agree(c, l)
    chk("L4 a scale disagreement fails", a["agrees"] is False and a["scale_diff"] == 0.2, str(a))
    chk("L4b cash is read off the ledger's scale", abs(a["cash_ledger"] - 0.4) < 1e-9)

    c, l = fixture(bar="2026-01-02", led_bar="2026-01-09")
    a = agree(c, l)
    chk("L5 a different decision bar fails", a["agrees"] is False
        and a["same_decision_bar"] is False)

    # Drift fixtures: a hand-made panel where the answer is known by construction.
    dates = pd.date_range("2026-01-01", periods=6, freq="D")
    px = pd.DataFrame({"A": [10.0, 10.0, 10.0, 10.0, 10.0, 20.0],
                       "B": [10.0] * 6}, index=dates)
    op = px.copy()
    flat = pd.DataFrame({"A": [10.0] * 6, "B": [10.0] * 6}, index=dates)
    navs = [1.0, 1.0, 1.0, 1.0, 1.4]
    led = {"book_in_force": {"bar": "2026-01-01", "scale": 0.8, "names": ["A", "B"]},
           "seed": {"bar": "2026-01-02"},
           "bars": [{"bar": str(dates[i].date()), "nav": navs[i - 1], "cash": 0.2, "carry": 0.0}
                    for i in range(1, 6)]}
    d = drift(led, px, op, cost_per_side=0.001)
    chk("L6 drift runs on a fixture", d.get("available") is True, str(d.get("reason")))
    chk("L6b flat prices -> zero drift turnover",
        drift(led, flat, flat, cost_per_side=0.001)["drift_turnover_one_way"] < 1e-12,
        str(drift(led, flat, flat)["drift_turnover_one_way"]))
    # A doubles on the last bar: 0.8 + 0.4 + 0.2 = 1.4 -> A weight 4/7, cash 1/7.
    chk("L6c drift is priced off the fill bar open",
        d["available"] and abs(d["weights_at_last"]["A"] - 4.0 / 7.0) < 1e-6,
        str(d.get("weights_at_last", {}).get("A")))
    chk("L6d drift turnover matches the hand number",
        d["available"] and abs(d["drift_turnover_one_way"] - 6.0 / 35.0) < 1e-6,
        str(d.get("drift_turnover_one_way")))
    chk("L6e drift cost is turnover x cost in bp",
        d["available"] and abs(d["drift_cost_bp"] - round(d["drift_turnover_one_way"] * 10, 2)) < 0.02)

    # The identity leg must MOVE when the recorded path is tampered with (r1261 class).
    led2 = json.loads(json.dumps(led))
    led2["bars"][-1]["nav"] = 1.5
    d2 = drift(led2, px, op, cost_per_side=0.001)
    chk("L7 identity leg catches a tampered nav", d2["available"] and d2["nav_identity_ok"] is False,
        str(d2.get("nav_identity_max_dev")))
    chk("L7b identity leg is clean on the untampered fixture",
        d["available"] and d["nav_identity_ok"] is True, str(d.get("nav_identity_max_dev")))

    led3 = {"book_in_force": {"bar": "2025-12-31", "scale": 0.8, "names": ["A", "B"]},
            "seed": {"bar": "2026-01-02"}, "bars": [{"bar": "2026-01-05", "nav": 1.0}]}
    chk("L8 a decision bar off the panel is refused",
        drift(led3, px, op)["available"] is False)

    # Live artefacts: the face must be readable today, not only under fixtures.
    card = load_json(CARD)
    led_live = load_json(F.LEDGER)
    chk("L9 the live card and ledger are on disk", card is not None and led_live is not None)
    if card and led_live:
        a_live = agree(card, led_live)
        chk("L9b live agreement is computed (not skipped)", isinstance(a_live["agrees"], bool)
            and a_live["card_names"] > 0, str(a_live)[:200])
        chk("L9c live gate: card and ledger describe the same decision",
            a_live["agrees"] is True, json.dumps(a_live, ensure_ascii=False)[:400])

    print("SELFTEST %d/%d legs" % (n_ok, total))
    for f in fails:
        print("  FAIL " + f)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())