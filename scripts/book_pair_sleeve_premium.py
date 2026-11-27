#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Which ruler says the cb sleeve is expensive -- the whole market's median, or the 20 bonds we own?

r2183 measured the 30/70 cushion against the CB market's median conversion premium and
r2184 turned that label into a live decision (cash in the sleeve while the label reads
rich, back in when it leaves rich).  Both read *one* ruler.  But the sleeve is the
dual-low book: it buys the 20 bonds with the smallest `close + conv_premium`, so by
construction it sits at the cheap end of the premium distribution.  A month in which
the market's median premium sits in its own top tertile can be an ordinary month for
the bonds we actually hold -- and then the page would be telling the desk to leave a
sleeve that is not expensive at all.

So this face holds the same book up against a second ruler and asks what changes:

  (1) the sleeve's own premium -- the median conversion premium of the bonds the rule
      held on each date, rebuilt from the same eligibility and the same pick formula
      the parent uses (imported, not re-derived), on the parent's own rebalance grid;
  (2) the two rulers' labels, month by month, with the same expanding-window tertile
      machinery and the same "read at the previous month end" lag -- only the ruler
      differs, so any disagreement is the ruler's doing;
  (3) the rule priced twice: cash in the sleeve when the market ruler says rich, and
      cash when the sleeve ruler says rich, each against its own matched-exposure
      control and its own block bootstrap.

Nothing here selects weights or arms; the cb arm, the etf arm, the 30% share and the
monthly grid all come from the parents.  What is new is only the second ruler.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FACE = "results/book_pair_sleeve_premium.json"
MD = "results/book_pair_sleeve_premium.md"
RESEARCH = "research/BOOK_PAIR_SLEEVE_PREMIUM.md"

N_HOLD = 20
REBAL = 20
PHASE = 0
MIN_PRICE = 80.0
MAX_PRICE = 200.0
ITM_PRICE = 130.0
ITM_PREMIUM = 1.0
MIN_COVER = 0.80          # a month whose held bonds mostly lack a premium is not measured
MIN_LABELLED = 24         # months on the sleeve ruler before its rule may be priced
AGREE_GAP = 0.90          # two rulers this close are the same ruler for practical use
MIN_DOWN_SIDE = 8
REGIME_NAMES = {0: "cheap", 1: "mid", 2: "rich"}


def _rp(rel):
    return os.path.join(ROOT, rel)


def _iso(ts):
    import datetime as _dt
    return _dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def _now_iso():
    import datetime as _dt
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _stamp(path):
    if not os.path.exists(path):
        return {"path": path, "missing": True}
    st = os.stat(path)
    return {"path": path, "size": int(st.st_size), "mtime": _iso(st.st_mtime)}


# ---------------------------------------------------------------- the sleeve
def sleeve_premium(panel, n_hold=N_HOLD, rebal=REBAL, phase=PHASE):
    """Median conversion premium of the bonds the dual-low rule held on each date.

    The pick is the parent's own: `cb_dual_low._eligible` with the published filters,
    scored `close + conv_premium.fillna(50)`, n_hold smallest.  The grid is the parent's
    too (signal at dates[i-1], trade at dates[i], every `rebal` bars from `phase`).
    Only the P&L is left out -- nothing here needs equity, just membership.
    """
    import numpy as np
    import cb_dual_low as C

    dates = list(panel["date"].drop_duplicates().sort_values())
    by_date = {d: g for d, g in panel.groupby("date")}
    last_seen = panel.groupby("code")["date"].max().to_dict()
    prem_of = {d: dict(zip(g["code"], g["conv_premium"])) for d, g in by_date.items()}

    holds = set()
    levels, cover = [], []
    rebalances = 0
    short_pool_skips = 0
    for i, d in enumerate(dates):
        # a bond whose series ended is not held any more (the parent liquidates it)
        if holds:
            holds = {c for c in holds if last_seen.get(c, d) >= d}
        if i > 0 and ((i - 1 - phase) % rebal == 0):
            sig = by_date.get(dates[i - 1])
            if sig is not None and not sig.empty:
                pool = C._eligible(sig, MIN_PRICE, MAX_PRICE, None, ITM_PRICE, ITM_PREMIUM)
                if len(pool) < n_hold:
                    short_pool_skips += 1
                else:
                    pool = pool.assign(score=pool["close"] + pool["conv_premium"].fillna(50.0))
                    holds = set(pool.nsmallest(n_hold, "score")["code"])
                    rebalances += 1
        if not holds:
            levels.append(np.nan)
            cover.append(0.0)
            continue
        today = prem_of.get(d, {})
        vals = [today.get(c) for c in holds]
        good = [v for v in vals if v is not None and v == v]
        levels.append(float(np.median(good)) if good else np.nan)
        cover.append(len(good) / float(len(holds)))

    import pandas as pd
    s = pd.Series(levels, index=pd.DatetimeIndex(dates), dtype=float)
    cv = pd.Series(cover, index=s.index, dtype=float)
    meta = {
        "arm": "n_hold=%d rebal=%d phase=%d cost=parent" % (n_hold, rebal, phase),
        "filters": "close %g..%g, drop deep-ITM (close>=%g and premium<=%g%%), no premium cap"
                   % (MIN_PRICE, MAX_PRICE, ITM_PRICE, ITM_PREMIUM),
        "rebalances": rebalances,
        "short_pool_skips": short_pool_skips,
        "days_with_a_level": int(s.notna().sum()),
        "first": str(s.index[0].date()) if len(s) else None,
        "last": str(s.index[-1].date()) if len(s) else None,
        "coverage_min": (round(float(cv.min()), 4) if len(cv) else None),
        "coverage_median": (round(float(cv.median()), 4) if len(cv) else None),
    }
    return s, cv, meta


def gate_unmeasured(levels, cover, month_ends, min_cover=MIN_COVER):
    """Month ends whose held bonds lack a premium are blanked, not guessed.

    A bond with no premium on that day is not "premium zero" -- it is a reading the
    panel does not have.  If too many of the held bonds are blank the month is dropped.
    """
    import numpy as np
    out = levels.copy()
    dropped = []
    for me in month_ends:
        idx = out.index[out.index <= me]
        if not len(idx):
            dropped.append({"month_end": str(me.date()), "why": "no level yet"})
            continue
        d = idx[-1]
        if cover.loc[d] < min_cover:
            out.loc[d] = np.nan
            dropped.append({"month_end": str(me.date()),
                            "why": "coverage %.2f below %.2f" % (cover.loc[d], min_cover)})
    return out, dropped


def label_months_window(prem, month_ends, lookback=750, min_hist=250):
    """Same lag and same tertiles, but the edges come from a trailing window.

    An expanding window is the honest ruler for "is this expensive by its own history",
    but it also means a structurally falling series can never read rich again (the
    sleeve's premium has drifted down for years).  This variant asks the local question:
    "expensive against the last three years", so the two arms can be read apart.
    """
    import numpy as np

    labels = [None] * len(month_ends)
    idx = prem.index
    vals = prem.values.astype(float)
    for k in range(1, len(month_ends)):
        cut = int(idx.searchsorted(month_ends[k - 1], side="right"))
        if cut < 1:
            continue
        lo = max(0, cut - lookback)
        hist = vals[lo:cut]
        hist = hist[~np.isnan(hist)]
        if len(hist) < min_hist:
            continue
        p = vals[cut - 1]
        if p != p:
            continue
        e1 = float(np.quantile(hist, 1.0 / 3.0))
        e2 = float(np.quantile(hist, 2.0 / 3.0))
        labels[k] = 2 if p >= e2 else (0 if p <= e1 else 1)
    return labels


def spot_reading(ser, month_ends, lookback=None):
    """Today's level against the same edges the label would use, without the lag."""
    import numpy as np

    if not len(ser.index):
        return {"missing": True}
    vals = ser.values.astype(float)
    vals = vals[~np.isnan(vals)]
    if not len(vals):
        return {"missing": True}
    p = float(vals[-1])
    cut = len(vals)
    lo = max(0, cut - lookback) if lookback else 0
    hist = vals[lo:cut]
    if len(hist) < 60:
        return {"missing": True}
    e1 = float(np.quantile(hist, 1.0 / 3.0))
    e2 = float(np.quantile(hist, 2.0 / 3.0))
    return {
        "reading_pct": round(p, 3),
        "cheap_below_pct": round(e1, 3),
        "rich_above_pct": round(e2, 3),
        "is_rich_now": bool(p >= e2),
        "is_cheap_now": bool(p <= e1),
        "asof": str(ser.index[ser.notna().values].max().date() if len(ser) else ""),
        "window": ("trailing %d readings" % lookback if lookback else "all readings"),
    }


def compare_labels(mkt, slv):
    """How often the two rulers put a month in a different bucket."""
    same = both = 0
    mkt_rich_only, slv_rich_only = [], []
    detail = []
    for k in range(len(mkt)):
        a, b = mkt[k], slv[k]
        if a is None or b is None:
            continue
        both += 1
        if a == b:
            same += 1
        else:
            detail.append({"kind": "label_differs", "market": REGIME_NAMES[a],
                           "sleeve": REGIME_NAMES[b]})
        if a == 2 and b != 2:
            mkt_rich_only.append(k)
        if b == 2 and a != 2:
            slv_rich_only.append(k)
    return {
        "months_both_labelled": both,
        "months_same": same,
        "agreement": (round(same / float(both), 4) if both else None),
        "gap_pp": (round(100.0 * (1.0 - same / float(both)), 2) if both else None),
        "market_rich_sleeve_not": len(mkt_rich_only),
        "sleeve_rich_market_not": len(slv_rich_only),
        "pairs_differing": len(detail),
    }


def verdict_of(agree, edges, n_labelled):
    """What the rulers jointly permit us to say.

    `edges` is {ruler: band} with the market ruler first.  The verdict is deliberately
    decided by whether each ruler's rule can pay for itself, not by how similar the
    labels look: two rulers that label different months but price the same rule are a
    reassuring pair, and that is a different sentence from a sign flip.
    """
    if n_labelled < MIN_LABELLED:
        return "SLEEVE_RULER_NOT_MEASURABLE_YET"
    a = (agree or {}).get("agreement")
    if a is None:
        return "SLEEVE_RULER_NOT_MEASURABLE_YET"
    los = {}
    for name, band in (edges or {}).items():
        lo = (band or {}).get("lo_pp")
        if lo is None:
            return "RULE_EDGE_NOT_PRICED_ON_ONE_OF_THE_RULERS"
        los[name] = lo > 0
    mkt = los.pop("market", None)
    if mkt is None:
        return "RULE_EDGE_NOT_PRICED_ON_ONE_OF_THE_RULERS"
    if any(v != mkt for v in los.values()):
        return "THE_ANSWER_DEPENDS_ON_WHICH_RULER"
    if a >= AGREE_GAP:
        return "TWO_RULERS_ONE_ANSWER"
    return "THE_RULERS_LABEL_DIFFERENT_MONTHS_BUT_PRICE_THE_RULE_ALIKE"


def current_state(slv_prem, mkt_prem, slv_labels, mkt_labels, month_ends,
                  recent_labels=None):
    """Where each ruler puts today, and whether they send the sleeve the same way."""
    import numpy as np

    def _blk(ser, labels):
        if not len(ser.index):
            return {"missing": True}
        last = ser.index[-1]
        p = float(ser.values[-1])
        vals = ser.values.astype(float)
        vals = vals[~np.isnan(vals)]
        pct = float((vals <= p).mean()) if len(vals) else None
        lab = None
        for k in range(len(labels) - 1, -1, -1):
            if labels[k] is not None:
                lab = labels[k]
                break
        return {
            "asof": str(last.date()),
            "median_premium_pct": round(p, 3),
            "percentile_in_own_history": round(pct, 4) if pct is not None else None,
            "label_in_force": REGIME_NAMES.get(lab),
            "read_at_month_end": (str(month_ends[-2].date())
                                  if lab is not None and len(month_ends) >= 2 else None),
            "applies_to_month_ending": str(month_ends[-1].date()) if len(month_ends) else None,
            "side": (None if lab is None else ("cash" if lab == 2 else "in_book")),
        }

    slv = _blk(slv_prem, slv_labels)
    mkt = _blk(mkt_prem, mkt_labels)
    # the label is a month-end reading applied with a lag; the spot reading is today's
    # level against the same edges.  They can disagree, and when they do the page is
    # quoting a decision taken before the sleeve last re-picked its bonds.
    slv["spot"] = spot_reading(slv_prem, month_ends)
    mkt["spot"] = spot_reading(mkt_prem, month_ends)
    if recent_labels is not None:
        rec = _blk(slv_prem, recent_labels)
        rec["spot"] = spot_reading(slv_prem, month_ends, lookback=750)
        rec["label_basis"] = "trailing 750 readings"
    else:
        rec = None
    agree = (slv.get("side") is not None and slv.get("side") == mkt.get("side"))
    spot_agree = (bool((slv.get("spot") or {}).get("is_rich_now"))
                  == bool((mkt.get("spot") or {}).get("is_rich_now")))
    return {
        "sleeve_ruler": slv,
        "market_ruler": mkt,
        "sleeve_ruler_recent": rec,
        "they_agree_today": bool(agree),
        "their_spot_readings_agree": bool(spot_agree),
        "if_they_disagree": (None if agree else
                             "the page's cash call comes from the market ruler; on the "
                             "sleeve's own premium the sleeve would stay in the book"),
        "if_spot_disagrees": (None if spot_agree else
                              "the label in force was read at the previous month end; the "
                              "bonds the sleeve holds today read differently, so the call "
                              "is a month-old reading of a sleeve that has since re-picked"),
    }


# ---------------------------------------------------------------- verify
def _verify(face, stamps=None):
    problems = []
    if face.get("face") != FACE:
        problems.append("face pointer %r" % face.get("face"))
    if not face.get("evidence_cutoff"):
        problems.append("no evidence_cutoff")

    win = face.get("window") or {}
    if not win.get("months"):
        problems.append("window has no months")

    cmp_ = face.get("rulers") or {}
    both = cmp_.get("months_both_labelled")
    same = cmp_.get("months_same")
    if isinstance(both, int) and isinstance(same, int):
        if same > both:
            problems.append("months_same %s > months_both_labelled %s" % (same, both))
        want = round(same / float(both), 4) if both else None
        if want is not None and cmp_.get("agreement") != want:
            problems.append("agreement %r != same/both %r" % (cmp_.get("agreement"), want))
    else:
        problems.append("the rulers block does not count its own months")

    for side in ("market", "sleeve"):
        blk = (face.get("rules") or {}).get(side) or {}
        r = blk.get("rule") or {}
        a = blk.get("always_on") or {}
        if r and a and r.get("months") != a.get("months"):
            problems.append("%s: rule and always-on scored on different month counts "
                            "(%s vs %s)" % (side, r.get("months"), a.get("months")))

    verd = face.get("verdict")
    if not verd:
        problems.append("no verdict")
    else:
        want = verdict_of(cmp_,
                          {k: (v or {}).get("edge_band")
                           for k, v in (face.get("rules") or {}).items()},
                          win.get("sleeve_labelled_months") or 0)
        if want != verd:
            problems.append("verdict %r does not follow its rows (%r)" % (verd, want))

    cur = face.get("current") or {}
    for name in ("sleeve_ruler", "market_ruler", "sleeve_ruler_recent"):
        blk = cur.get(name) or {}
        if not blk:
            continue
        want_side = (None if blk.get("label_in_force") is None
                     else ("cash" if blk.get("label_in_force") == "rich" else "in_book"))
        if blk.get("side") != want_side:
            problems.append("%s: side %r does not follow label %r"
                            % (name, blk.get("side"), blk.get("label_in_force")))
        _read, _app = blk.get("read_at_month_end"), blk.get("applies_to_month_ending")
        if _read and _app and _read == _app:
            # the label for a month is read at the *previous* month end; the same day on
            # both sides means the label was issued on data it is then applied to
            problems.append("%s: label read at %s and applied to the same month end"
                            % (name, _read))
        sp = blk.get("spot") or {}
        if sp and "is_rich_now" in sp:
            if not isinstance(sp.get("rich_above_pct"), (int, float)):
                problems.append("%s: spot reading without its threshold" % name)

    drift = []
    if stamps:
        for key, want_stamp in stamps.items():
            got = ((face.get("inputs") or {}).get(key) or {})
            if key in ("cb", "sleeve_arm"):
                got = got.get("panel") or ({} if key == "cb" else got)
            if key == "w_source":
                got = got.get("stamp") or {}
            if want_stamp.get("missing"):
                drift.append("%s missing on disk" % key)
            elif got.get("size") != want_stamp.get("size") or \
                    got.get("mtime") != want_stamp.get("mtime"):
                drift.append("%s moved (face %s/%s, disk %s/%s)"
                             % (key, got.get("size"), got.get("mtime"),
                                want_stamp.get("size"), want_stamp.get("mtime")))
    if drift:
        return {"ok": False, "verdict": face.get("verdict"), "problems": problems,
                "drift": drift, "kind": "CHECK STALE FACE_DRIFT"}
    if problems:
        return {"ok": False, "verdict": face.get("verdict"), "problems": problems,
                "kind": "CHECK FAILED"}
    return {"ok": True, "verdict": face.get("verdict"), "problems": [],
            "kind": "CHECK OK"}


def check():
    p = _rp(FACE)
    if not os.path.exists(p):
        print(json.dumps({"ok": False, "kind": "CHECK STALE face missing",
                          "path": p}, ensure_ascii=False))
        return 2
    with open(p, encoding="utf-8") as fh:
        face = json.load(fh)
    stamps = {
        "cb": _stamp(_rp("data/cb_panel.csv.gz")),
        "w_source": _stamp(_rp("results/book_pair_blend.json")),
    }
    res = _verify(face, stamps)
    print(json.dumps(res, ensure_ascii=False))
    if res["ok"]:
        return 0
    return 3 if res.get("kind", "").startswith("CHECK FAILED") else 2


# ---------------------------------------------------------------- build
def build(write=True, quiet=False):
    from_shell = not quiet

    def say(msg):
        if from_shell:
            sys.stdout.write(msg + "\n")

    import book_pair_cushion_regime as Cu

    say("[1/5] loading parents (one cb panel read) ...")
    inp = Cu.load_inputs()
    cb, etf, prem, w = inp["cb"], inp["etf"], inp["prem"], inp["w"]
    import cb_dual_low as C
    panel = C._load_panel()
    say("      cb bars=%d  etf bars=%d  w_cb=%.2f  market premium days=%d"
        % (len(cb), len(etf), w, len(prem)))

    say("[2/5] rebuilding the sleeve's own membership and its premium ...")
    slv_prem_raw, cover, slv_meta = sleeve_premium(panel)
    say("      rebalances=%d  short-pool skips=%d  days=%d  coverage median=%s"
        % (slv_meta["rebalances"], slv_meta["short_pool_skips"],
           slv_meta["days_with_a_level"], slv_meta["coverage_median"]))

    say("[3/5] the same month grid, two rulers, one lag rule ...")
    mi, mc, me, mb = Cu.monthly_frame(cb, etf, w)
    slv_prem, dropped = gate_unmeasured(slv_prem_raw, cover, list(mi))
    lab_mkt = Cu.label_months(prem, list(mi))
    lab_slv = Cu.label_months(slv_prem, list(mi))
    lab_rec = label_months_window(slv_prem, list(mi), lookback=750, min_hist=250)
    n_mkt = sum(1 for x in lab_mkt if x is not None)
    n_slv = sum(1 for x in lab_slv if x is not None)
    n_rec = sum(1 for x in lab_rec if x is not None)
    cmp_ = compare_labels(lab_mkt, lab_slv)
    cmp_rec = compare_labels(lab_mkt, lab_rec)
    say("      months=%d  market labelled=%d  sleeve labelled=%d  recent-window labelled=%d"
        % (len(mi), n_mkt, n_slv, n_rec))
    say("      agreement with the market ruler: sleeve-own %s, sleeve-recent %s"
        % (cmp_.get("agreement"), cmp_rec.get("agreement")))

    say("[4/5] the rule priced on each ruler ...")
    rules = {}
    for side, labs in (("market", lab_mkt), ("sleeve", lab_slv), ("sleeve_recent", lab_rec)):
        arm = Cu.rule_arm(me.values, mc.values, labs, w)
        band = Cu.mean_diff_band(arm.get("rule_rets") or [], arm.get("matched_rets") or [])
        rverd, redge = Cu.rule_verdict(arm, band)
        rules[side] = {
            "label_months": sum(1 for x in labs if x is not None),
            "months_in_cash_sleeve": arm.get("months_in_cash_sleeve"),
            "months_scored": arm.get("months_scored"),
            "switches": arm.get("switches"),
            "cost_paid_pp": arm.get("cost_paid_pp"),
            "avg_cb_exposure": arm.get("avg_cb_exposure"),
            "rule": arm.get("rule"),
            "always_on": arm.get("always_on"),
            "matched_exposure": arm.get("matched_exposure"),
            "edge_band": band,
            "rule_verdict": rverd,
        }
    verd = verdict_of(cmp_, {k: v["edge_band"] for k, v in rules.items()}, n_slv)

    say("[5/5] today on both rulers + face ...")
    cur = current_state(slv_prem, prem, lab_slv, lab_mkt, list(mi), recent_labels=lab_rec)
    # what the two rulers would each have sent to cash, month by month -- the reader's
    # page quotes these two numbers instead of re-deriving label logic
    diffs = []
    for k in range(len(mi)):
        a, b = lab_mkt[k], lab_slv[k]
        if a is None or b is None or a == b:
            continue
        diffs.append({"month_ending": str(mi[k].date()),
                      "market": REGIME_NAMES[a], "sleeve": REGIME_NAMES[b]})

    face = {
        "face": FACE,
        "generated_at": _now_iso(),
        # this face reads three series and is only as fresh as the oldest of them
        "evidence_cutoff": min(str(etf.index[-1].date()),
                               str(cb.index[-1].date()),
                               (slv_meta.get("last") or "9999-12-31")),
        "panels": {
            "etf": str(etf.index[-1].date()),
            "cb_arm": str(cb.index[-1].date()),
            "sleeve_premium": slv_meta.get("last"),
            "premium_day_used": cur["sleeve_ruler"].get("asof"),
        },
        "question": ("Does 'the cb sleeve is expensive' mean the same thing on the "
                     "market's median premium as on the premium of the 20 bonds the "
                     "sleeve actually holds?"),
        "caliber": {
            "weight": "read from results/book_pair_blend.json best.w_cb",
            "market_ruler": ("median conv_premium across the whole cb panel on each date "
                             "(the parent's own series)"),
            "sleeve_ruler": ("median conv_premium of the bonds the dual-low rule held on "
                             "that date; membership rebuilt from cb_dual_low._eligible "
                             "with the parent's pick formula and grid"),
            "coverage_gate": ("a month is dropped when fewer than %.0f%% of the held bonds "
                              "have a premium reading on that date" % (100.0 * MIN_COVER)),
            "labels": ("tertiles of each ruler's own history up to the previous month end, "
                       "expanding window, >=250 readings -- identical machinery both sides"),
            "rule_cost": "%.0fbp per side on the %.2f cb share" % (Cu.COST_BP, w),
            "bootstrap": "circular blocks of %d months, %d draws, seed %d"
                         % (Cu.BOOT_L, Cu.BOOT_N, Cu.SEED),
        },
        "window": {
            "first": str(mi[0].date()) if len(mi) else None,
            "last": str(mi[-1].date()) if len(mi) else None,
            "last_bar": str(etf.index[-1].date()),
            "months": int(len(mi)),
            "market_labelled_months": n_mkt,
            "sleeve_labelled_months": n_slv,
            "recent_window_labelled_months": n_rec,
            "months_dropped_for_coverage": len(dropped),
            "why": "the blend only exists where both parents have a level",
        },
        "inputs": {
            "w_cb": w,
            "w_source": inp["w_meta"],
            "cb": inp["cb_meta"],
            "etf": {k: inp["etf_meta"].get(k) for k in
                    ("face", "arm", "execution", "panel", "universe")},
            "sleeve_arm": {"meta": slv_meta,
                           "panel": _stamp(_rp("data/cb_panel.csv.gz"))},
            "generic_panel": _stamp(_rp("data/generic_cb_panel.csv.gz")),
        },
        "rulers": cmp_,
        "rulers_recent_window": cmp_rec,
        "label_differences": diffs,
        "rules": rules,
        "current": cur,
        "verdict": verd,
        "unverified": [
            "membership is rebuilt from the parent's pick formula, not read from the "
            "parent's holdings -- the parent does not publish them, so a formula change "
            "on its side would move this face without either side failing",
            "the sleeve's own premium jumps at rebalances (a pick turns over half the 20 "
            "bonds), so part of its month-end reading is 'which bonds we happen to hold', "
            "not only 'how expensive they are' -- the coverage gate cannot see that",
            "the sleeve ruler still has only one premium cycle in it (%d labelled months); "
            "a second cycle is what would tell us whether the two rulers converge in a "
            "genuinely cheap market" % n_slv,
            "an expanding-window tertile cannot call a structurally falling series rich: "
            "the sleeve reads rich in %d of %d months and the market in %d, so the two "
            "arms do not fire equally often -- the recent-window arm is published beside "
            "them for that reason, not as a tiebreak"
            % (rules["sleeve"]["months_in_cash_sleeve"], n_slv,
               rules["market"]["months_in_cash_sleeve"]),
            "premium on a held bond can be stale on its last quoted day; the coverage "
            "gate drops a month below %.0f%% coverage, it does not correct the rest"
            % (100.0 * MIN_COVER),
            "the rule is priced on monthly switches only; intra-month runs are not modelled",
            "the cb arm and the etf arm are the parents' published arms -- this face does "
            "not re-test them",
        ],
    }

    if write:
        with open(_rp(FACE), "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        with open(_rp(MD), "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
        with open(_rp(RESEARCH), "w", encoding="utf-8") as fh:
            fh.write(render_research(face))

    say("      verdict = %s" % verd)
    say("      agreement with market: sleeve-own %s (market-rich/sleeve-not %d, "
        "sleeve-rich/market-not %d) | sleeve-recent %s"
        % (cmp_.get("agreement"), cmp_.get("market_rich_sleeve_not"),
           cmp_.get("sleeve_rich_market_not"), cmp_rec.get("agreement")))
    for side in ("market", "sleeve", "sleeve_recent"):
        b = rules[side]
        say("      %-14s: cash %s/%s mo | edge %s pp [%s .. %s] | rule sharpe %s vs "
            "always-on %s -> %s"
            % (side, b["months_in_cash_sleeve"], b["label_months"],
               (b["edge_band"] or {}).get("point_pp"),
               (b["edge_band"] or {}).get("lo_pp"), (b["edge_band"] or {}).get("hi_pp"),
               (b["rule"] or {}).get("sharpe"), (b["always_on"] or {}).get("sharpe"),
               b["rule_verdict"]))
    for name in ("market_ruler", "sleeve_ruler", "sleeve_ruler_recent"):
        blk = cur.get(name) or {}
        sp = blk.get("spot") or {}
        say("      today %-19s label %s (read %s) | spot %s%% vs rich>=%s -> rich=%s"
            % (name, blk.get("label_in_force"), blk.get("read_at_month_end"),
               sp.get("reading_pct"), sp.get("rich_above_pct"), sp.get("is_rich_now")))
    say("      label sides agree=%s | spot readings agree=%s"
        % (cur.get("they_agree_today"), cur.get("their_spot_readings_agree")))
    return face


# ---------------------------------------------------------------- markdown
def _n(v, dash="n/a"):
    return dash if v is None else ("%+.2f" % v if isinstance(v, float) else str(v))


def _pc(v, dash="n/a"):
    return dash if v is None else "%.1f%%" % (100.0 * v)


def render_md(face):
    cur = face["current"]
    s = cur.get("sleeve_ruler") or {}
    m = cur.get("market_ruler") or {}
    r = face["rules"]
    t = face["rulers"]

    L = ["# Which ruler says the sleeve is expensive", ""]
    L.append("**%s**" % face["question"])
    L.append("")
    L.append("generated %s · cutoff %s · book %s cb share"
             % (face["generated_at"], face["evidence_cutoff"],
                _pc((face.get("inputs") or {}).get("w_cb"), "n/a")))
    L.append("")
    L.append("| verdict | |")
    L.append("|---|---|")
    L.append("| **%s** | rules labelled same in %s of %s months (%s differ) |"
             % (face["verdict"], t.get("months_same"), t.get("months_both_labelled"),
                t.get("pairs_differing")))
    L.append("")

    L.append("## Today, on each ruler")
    L.append("")
    L.append("| ruler | label in force | read at | sleeve | today's reading | its own rich line | expensive now? |")
    L.append("|---|---|---|---|---|---|---|")
    rows = (("market median", m, "市场口径"),
            ("our 20 bonds", s, "袖自己的 20 只"),
            ("our bonds, 3y window", cur.get("sleeve_ruler_recent") or {}, "同上·近三年窗"))
    for name, blk, cn in rows:
        sp = blk.get("spot") or {}
        if not blk:
            L.append("| %s | n/a | n/a | n/a | n/a | n/a | n/a |" % name)
            continue
        L.append("| %s | %s | %s | %s | %.2f%% | %.2f%% | %s |"
                 % (name, blk.get("label_in_force") or "n/a",
                    blk.get("read_at_month_end") or "n/a",
                    {"cash": "收进现金", "in_book": "留在书里"}.get(blk.get("side") or "", "n/a"),
                    sp.get("reading_pct") or 0.0, sp.get("rich_above_pct") or 0.0,
                    ("贵" if sp.get("is_rich_now") else "不贵") if sp else "n/a"))
    L.append("")
    if not cur.get("they_agree_today"):
        L.append("> 两把尺的滞后标签不同向：%s" % (cur.get("if_they_disagree") or ""))
        L.append("")
    if not cur.get("their_spot_readings_agree"):
        L.append("> 两把尺的**当日读数**不同向：%s" % (cur.get("if_spot_disagrees") or ""))
        L.append("")

    L.append("## The rule, priced on each ruler")
    L.append("")
    L.append("| ruler | cash months | rule CAGR | rule Sharpe | rule MDD | always-on Sharpe | edge/mo | band | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for side, label in (("market", "market median"), ("sleeve", "our 20 bonds"),
                        ("sleeve_recent", "our bonds, 3y window")):
        b = r.get(side) or {}
        rr, aa = b.get("rule") or {}, b.get("always_on") or {}
        e = b.get("edge_band") or {}
        L.append("| %s | %s/%s | %s | %s | %s | %s | %s pp | %s .. %s | %s |"
                 % (label, b.get("months_in_cash_sleeve"), b.get("label_months"),
                    _pc(rr.get("cagr")), _n(rr.get("sharpe")), _pc(rr.get("maxdd")),
                    _n(aa.get("sharpe")), _n(e.get("point_pp")),
                    _n(e.get("lo_pp")), _n(e.get("hi_pp")), b.get("rule_verdict")))
    L.append("")

    L.append("## Where the two rulers disagree")
    L.append("")
    L.append("- months both labelled: **%s**" % t.get("months_both_labelled"))
    L.append("- same bucket: **%s** (%s)" % (t.get("months_same"), _pc(t.get("agreement"))))
    L.append("- market says rich, our bonds do not: **%s**" % t.get("market_rich_sleeve_not"))
    L.append("- our bonds say rich, market does not: **%s**" % t.get("sleeve_rich_market_not"))
    dd = face.get("label_differences") or []
    if dd:
        L.append("")
        L.append("| month ending | market | our bonds |")
        L.append("|---|---|---|")
        for row in dd[:24]:
            L.append("| %s | %s | %s |" % (row["month_ending"], row["market"], row["sleeve"]))
        if len(dd) > 24:
            L.append("| … | %d more | |" % (len(dd) - 24))
    L.append("")

    L.append("## What is not verified")
    L.append("")
    for u in face.get("unverified") or []:
        L.append("- %s" % u)
    L.append("")
    return "\n".join(L)


def render_research(face):
    r = face["rules"]
    t = face["rulers"]
    cur = face["current"]
    L = ["# 袖级溢价：第二个尺子", ""]
    L.append("**问题**：%s" % face["question"])
    L.append("")
    L.append("## 为什么要有这把尺")
    L.append("")
    L.append("r2183 把 30/70 的缓冲按**全市场**转债溢价中位数的分档切开，r2184 又把那个标签"
             "变成一条会下单的决定（标签 rich 时袖收现金）。可是这只袖不是市场：双低规则买的是"
             "`收盘价 + 转股溢价` 最小的 20 只，天然压在溢价分布的下端。市场口径的「贵」，对"
             "自己手里的 20 只可能只是平常一个月——若如此，页面会叫我们把一只并不贵的袖换成现金。")
    L.append("")
    L.append("## 口径（parents imported, not rebuilt）")
    L.append("")
    L.append("- 袖成员：`cb_dual_low._eligible` 同一套过滤（价 %g~%g、剔深度实值）+ 同一打分式"
             "（`close + conv_premium.fillna(50)`，取最小 %d）+ 同一调仓网格（rebal=%d/phase=%d，"
             "信号在 t−1）" % (MIN_PRICE, MAX_PRICE, N_HOLD, REBAL, PHASE))
    L.append("- 袖读数：当日所持券 `conv_premium` 的中位数；覆盖率低于 %.0f%% 的月份直接丢掉，"
             "不补值（缺读数不是零溢价）" % (100.0 * MIN_COVER))
    L.append("- 两把尺的标签机械完全相同（各自历史的扩张窗三分位、只在上一月末读数、≥250 读数），"
             "差别只有尺本身；另加一把**近三年滚动窗**尺（750 读数），因为扩张窗对结构性下行的序列"
             "永远不会喊贵，两臂的「现金月数」不可直接相比")
    L.append("- 权重、cb/etf 两腿、成本、bootstrap 全部从父面 import（`book_pair_cushion_regime`）")
    L.append("")
    L.append("## 读数")
    L.append("")
    L.append("| 尺 | 现金月数 | 规则 CAGR | 规则夏普 | 规则 MDD | 一直持有夏普 | 每月边缘 | 区间 | 判词 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for side, label in (("market", "市场口径"), ("sleeve", "袖自己的 20 只"),
                        ("sleeve_recent", "袖·近三年窗")):
        b = r.get(side) or {}
        rr, aa = b.get("rule") or {}, b.get("always_on") or {}
        e = b.get("edge_band") or {}
        L.append("| %s | %s/%s | %s | %s | %s | %s | %s pp | %s .. %s | %s |"
                 % (label, b.get("months_in_cash_sleeve"), b.get("label_months"),
                    _pc(rr.get("cagr")), _n(rr.get("sharpe")), _pc(rr.get("maxdd")),
                    _n(aa.get("sharpe")), _n(e.get("point_pp")), _n(e.get("lo_pp")),
                    _n(e.get("hi_pp")), b.get("rule_verdict")))
    L.append("")
    L.append("标签一致率（对市场尺）：袖自己 **%s**（同桶 %s/%s 月；市场说贵而袖不贵 **%s** 个月，"
             "袖说贵而市场不贵 **%s** 个月）；袖·近三年窗 **%s**。"
             % (_pc(t.get("agreement")), t.get("months_same"), t.get("months_both_labelled"),
                t.get("market_rich_sleeve_not"), t.get("sleeve_rich_market_not"),
                _pc((face.get("rulers_recent_window") or {}).get("agreement"))))
    L.append("")
    _sp_m = (cur["market_ruler"].get("spot") or {})
    _sp_s = (cur["sleeve_ruler"].get("spot") or {})
    L.append("今天：市场口径滞后标签 %s，当日读数 %.2f%%（自己的贵线 %.2f%%）；袖口径滞后标签 %s，"
             "当日读数 %.2f%%（自己的贵线 %.2f%%）。标签同向=%s，**当日读数同向=%s**。"
             % (cur["market_ruler"].get("label_in_force"),
                _sp_m.get("reading_pct") or 0.0, _sp_m.get("rich_above_pct") or 0.0,
                cur["sleeve_ruler"].get("label_in_force"),
                _sp_s.get("reading_pct") or 0.0, _sp_s.get("rich_above_pct") or 0.0,
                cur.get("they_agree_today"), cur.get("their_spot_readings_agree")))
    L.append("")
    L.append("## 判词的边界")
    L.append("")
    for u in face.get("unverified") or []:
        L.append("- %s" % u)
    L.append("")
    L.append("复跑：`python scripts/book_pair_sleeve_premium.py`（写入三件）／`check` 只判不写。")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- selftest
def selftest():
    import numpy as np
    import pandas as pd

    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, "PASS", ""))
        except Exception as exc:  # noqa: BLE001
            legs.append((name, "FAIL", "%s: %s" % (type(exc).__name__, exc)))

    def _assert(cond, msg):
        if not cond:
            raise AssertionError(msg)

    def _panel(rows):
        return pd.DataFrame(rows, columns=["date", "code", "close", "conv_premium"])

    def t_sleeve_picks_the_cheapest():
        # 25 bonds: 20 cheap (premium 5..24) and 5 expensive (premium 90..94).
        # the rule scores close+premium, so the cheap ones must be the sleeve.
        days = pd.date_range("2020-01-01", periods=2, freq="B")
        rows = []
        for d in days:
            for k in range(20):
                rows.append((d, "C%02d" % k, 100.0, 5.0 + k))
            for k in range(5):
                rows.append((d, "E%02d" % k, 100.0, 90.0 + k))
        s, cv, meta = sleeve_premium(_panel(rows))
        _assert(meta["rebalances"] == 1, "two bars = one pick, got %d" % meta["rebalances"])
        # median of 5..24 is 14.5
        _assert(abs(float(s.iloc[-1]) - 14.5) < 1e-9,
                "sleeve median should be 14.5, got %s" % s.iloc[-1])
        _assert(float(cv.iloc[-1]) == 1.0, "full coverage expected")

    def t_sleeve_excludes_the_market_rich_tail():
        # the market median is dragged by expensive bonds the sleeve never buys
        days = pd.date_range("2020-01-01", periods=2, freq="B")
        rows = []
        for d in days:
            for k in range(20):
                rows.append((d, "C%02d" % k, 100.0, 5.0 + k))
            for k in range(60):
                rows.append((d, "X%02d" % k, 150.0, 300.0))
        s, _cv, _m = sleeve_premium(_panel(rows))
        mkt = _panel(rows).groupby("date")["conv_premium"].median().sort_index()
        _assert(float(s.iloc[-1]) < 25.0, "sleeve stays cheap: %s" % s.iloc[-1])
        _assert(float(mkt.iloc[-1]) > 100.0, "market median is rich: %s" % mkt.iloc[-1])

    def t_short_pool_is_not_a_pick():
        days = pd.date_range("2020-01-01", periods=2, freq="B")
        rows = [(d, "C%02d" % k, 100.0, 5.0) for d in days for k in range(10)]
        s, cv, meta = sleeve_premium(_panel(rows))
        _assert(meta["rebalances"] == 0, "a 10-bond pool cannot fill 20 slots")
        _assert(meta["short_pool_skips"] >= 1, "the skip must be counted")
        _assert(pd.isna(s).all(), "no sleeve -> no level")

    def t_coverage_gate_blanks_thin_months():
        idx = pd.date_range("2020-01-01", periods=60, freq="B")
        levels = pd.Series(20.0, index=idx)
        cover = pd.Series(1.0, index=idx)
        cover.iloc[-1] = 0.5
        me = [idx[-1].normalize()]
        out, dropped = gate_unmeasured(levels, cover, me, min_cover=0.8)
        _assert(pd.isna(out.loc[idx[-1]]), "a 50%-covered month must be dropped")
        _assert(dropped and "coverage" in dropped[0]["why"], "the drop must say why")
        out2, _ = gate_unmeasured(levels, cover, me, min_cover=0.4)
        _assert(not pd.isna(out2.loc[idx[-1]]), "a 50%-covered month passes a 40% gate")

    def t_compare_counts_both_directions():
        mkt = [2, 2, 0, 1, None]
        slv = [2, 1, 1, 1, 2]
        out = compare_labels(mkt, slv)
        _assert(out["months_both_labelled"] == 4, "the None month is not compared")
        _assert(out["months_same"] == 2, "months 0 and 3 agree")
        _assert(out["market_rich_sleeve_not"] == 1, "month 1 is market-rich only")
        _assert(out["sleeve_rich_market_not"] == 0, "the None month cannot be sleeve-rich")
        _assert(out["agreement"] == 0.5, "2 of 4 agree")

    def t_agreement_needs_both_labels():
        out = compare_labels([None, None], [2, 0])
        _assert(out["months_both_labelled"] == 0 and out["agreement"] is None,
                "no overlap -> no agreement number, not a zero")

    def t_verdict_requires_a_measurable_ruler():
        v = verdict_of({"agreement": 0.5}, {"market": {"lo_pp": 0.1}, "sleeve": {"lo_pp": 0.1}}, 10)
        _assert(v == "SLEEVE_RULER_NOT_MEASURABLE_YET", "thin ruler: %s" % v)

    def t_verdict_flags_a_ruler_dependent_answer():
        v = verdict_of({"agreement": 0.8}, {"market": {"lo_pp": 0.02},
                                           "sleeve": {"lo_pp": -0.05}}, 60)
        _assert(v == "THE_ANSWER_DEPENDS_ON_WHICH_RULER", "sign flip: %s" % v)
        v = verdict_of({"agreement": 0.95}, {"market": {"lo_pp": 0.02},
                                            "sleeve": {"lo_pp": 0.01}}, 60)
        _assert(v == "TWO_RULERS_ONE_ANSWER", "same sign + close: %s" % v)
        v = verdict_of({"agreement": 0.6}, {"market": {"lo_pp": 0.02},
                                           "sleeve": {"lo_pp": 0.01},
                                           "sleeve_recent": {"lo_pp": 0.03}}, 60)
        _assert(v.startswith("THE_RULERS_LABEL_DIFFERENT"), "same sign + far: %s" % v)
        v = verdict_of({"agreement": 0.9}, {"market": {"lo_pp": None},
                                           "sleeve": {"lo_pp": 0.01}}, 60)
        _assert(v == "RULE_EDGE_NOT_PRICED_ON_ONE_OF_THE_RULERS", "missing band: %s" % v)
        # a third ruler that flips is enough to make the answer ruler-dependent
        v = verdict_of({"agreement": 0.95}, {"market": {"lo_pp": 0.02},
                                            "sleeve": {"lo_pp": 0.01},
                                            "sleeve_recent": {"lo_pp": -0.01}}, 60)
        _assert(v == "THE_ANSWER_DEPENDS_ON_WHICH_RULER", "third-ruler flip: %s" % v)

    def t_current_follows_each_label():
        idx = pd.date_range("2020-01-01", periods=30, freq="B")
        slv = pd.Series(np.linspace(10, 40, 30), index=idx)
        mkt = pd.Series(np.linspace(10, 40, 30), index=idx)
        me = pd.date_range("2020-01-31", periods=3, freq="ME")
        cur = current_state(slv, mkt, [None, 2, 2], [None, 0, 0], list(me))
        _assert(cur["sleeve_ruler"]["label_in_force"] == "rich", "sleeve label")
        _assert(cur["sleeve_ruler"]["side"] == "cash", "rich -> cash")
        _assert(cur["market_ruler"]["side"] == "in_book", "cheap -> in book")
        _assert(cur["they_agree_today"] is False, "different sides disagree")
        _assert(cur["sleeve_ruler"]["read_at_month_end"] == str(me[-2].date()),
                "the label is read at the previous month end")

    def t_verify_reads_its_rows():
        face = {
            "face": FACE, "evidence_cutoff": "2026-01-01",
            "verdict": "TWO_RULERS_ONE_ANSWER",
            "window": {"months": 6, "sleeve_labelled_months": 60},
            "rulers": {"months_both_labelled": 4, "months_same": 4, "agreement": 1.0},
            "rules": {"market": {"rule": {"months": 4}, "always_on": {"months": 4},
                                 "edge_band": {"lo_pp": 0.1, "hi_pp": 0.3}},
                      "sleeve": {"rule": {"months": 4}, "always_on": {"months": 4},
                                 "edge_band": {"lo_pp": 0.1, "hi_pp": 0.3}}},
            "current": {"sleeve_ruler": {"label_in_force": "mid", "side": "in_book",
                                         "read_at_month_end": "2026-01-31",
                                         "applies_to_month_ending": "2026-02-28"},
                        "market_ruler": {"label_in_force": "rich", "side": "cash",
                                         "read_at_month_end": "2026-01-31",
                                         "applies_to_month_ending": "2026-02-28"}},
        }
        res = _verify(face)
        _assert(res["ok"], "a consistent face must verify: %s" % res.get("problems"))

    def t_verify_catches_a_memorised_verdict():
        face = {
            "face": FACE, "evidence_cutoff": "2026-01-01",
            "verdict": "TWO_RULERS_ONE_ANSWER",
            "window": {"months": 6, "sleeve_labelled_months": 60},
            "rulers": {"months_both_labelled": 4, "months_same": 4, "agreement": 1.0},
            "rules": {"market": {"rule": {"months": 4}, "always_on": {"months": 4},
                                 "edge_band": {"lo_pp": 0.1}},
                      "sleeve": {"rule": {"months": 4}, "always_on": {"months": 4},
                                 "edge_band": {"lo_pp": -0.1}}},
        }
        res = _verify(face)
        _assert(not res["ok"] and res["kind"].startswith("CHECK FAILED"),
                "a sign flip must not keep the 'one answer' verdict")

    def t_verify_catches_a_side_that_ignores_its_label():
        face = {
            "face": FACE, "evidence_cutoff": "2026-01-01",
            "verdict": "SLEEVE_RULER_NOT_MEASURABLE_YET",
            "window": {"months": 1, "sleeve_labelled_months": 0},
            "rulers": {"months_both_labelled": 0, "months_same": 0, "agreement": None},
            "rules": {},
            "current": {"sleeve_ruler": {"label_in_force": "mid", "side": "cash"}},
        }
        res = _verify(face)
        _assert(not res["ok"], "a mid label with a cash side is a decision nobody made")

    def t_verify_names_drift_as_stale():
        face = {
            "face": FACE, "evidence_cutoff": "2026-01-01",
            "verdict": "SLEEVE_RULER_NOT_MEASURABLE_YET",
            "window": {"months": 1, "sleeve_labelled_months": 0},
            "rulers": {"months_both_labelled": 0, "months_same": 0, "agreement": None},
            "rules": {}, "inputs": {"cb": {"panel": {"size": 1, "mtime": "a"}}},
        }
        res = _verify(face, {"cb": {"size": 2, "mtime": "b"}})
        _assert(not res["ok"] and "STALE" in res["kind"],
                "drift must say STALE so the chain pays to rebuild")

    def t_markdown_prints_both_rulers():
        face = {
            "generated_at": "2026-01-01T00:00:00+08:00", "evidence_cutoff": "2026-01-01",
            "question": "q", "verdict": "TWO_RULERS_ONE_ANSWER",
            "inputs": {"w_cb": 0.3},
            "rulers": {"months_both_labelled": 4, "months_same": 4, "agreement": 1.0,
                       "pairs_differing": 0, "market_rich_sleeve_not": 0,
                       "sleeve_rich_market_not": 0},
            "label_differences": [],
            "rules": {s: {"months_in_cash_sleeve": 0, "rule": {"cagr": 0.1, "sharpe": 1.0,
                                                              "maxdd": -0.1},
                          "always_on": {"sharpe": 0.9},
                          "edge_band": {"point_pp": 0.1, "lo_pp": 0.0, "hi_pp": 0.2},
                          "rule_verdict": "X"} for s in ("market", "sleeve")},
            "current": {"sleeve_ruler": {"median_premium_pct": 20.0, "side": "in_book",
                                         "label_in_force": "mid",
                                         "percentile_in_own_history": 0.5},
                        "market_ruler": {"median_premium_pct": 70.0, "side": "cash",
                                         "label_in_force": "rich",
                                         "percentile_in_own_history": 0.98},
                        "they_agree_today": False,
                        "if_they_disagree": "the page's cash call comes from the market ruler"},
            "unverified": ["x"],
        }
        md = render_md(face)
        _assert("TWO_RULERS_ONE_ANSWER" in md, "the verdict must be printed")
        _assert("our 20 bonds" in md and "market median" in md, "both rulers must be named")
        rd = render_research(face)
        _assert("袖" in rd, "the research page must speak about the sleeve")

    def t_window_labels_read_local_history():
        # a series that steps down and stays down: the expanding tertiles never call it
        # rich again, the trailing window does
        idx = pd.date_range("2012-01-01", periods=4000, freq="B")
        # a regime that halved and now oscillates: inside the trailing window the top of
        # the oscillation is "rich", against the whole history it is nowhere near
        tail = np.tile(np.linspace(8.0, 20.0, 50), 40)
        vals = np.concatenate([np.full(2000, 30.0), tail])
        s = pd.Series(vals, index=idx)
        me = list(pd.date_range("2022-01-31", periods=12, freq="ME"))
        import book_pair_cushion_regime as Cu
        exp = Cu.label_months(s, me)
        loc = label_months_window(s, me, lookback=750, min_hist=250)
        _assert(all(x in (0, 1) for x in exp if x is not None), "expanding never says rich")
        _assert(any(x == 2 for x in loc if x is not None),
                "the trailing window must be able to say rich inside a down-trend")

    def t_spot_reading_uses_the_same_edges():
        idx = pd.date_range("2020-01-01", periods=300, freq="B")
        vals = list(np.full(299, 10.0)) + [30.0]
        s = pd.Series(vals, index=idx)
        sp = spot_reading(s, [idx[-1]], lookback=None)
        _assert(sp["is_rich_now"] is True, "a reading above its own 67th pct is rich now")
        _assert(sp["rich_above_pct"] < 30.0, "the rich line must sit below the reading")
        flat = spot_reading(pd.Series(np.full(300, 10.0), index=idx), [idx[-1]])
        _assert(flat["is_rich_now"] is True, "a flat series sits on its own line")

    def t_json_roundtrip():
        face = {"a": 1, "b": [1, 2, {"c": None}]}
        _assert(json.loads(json.dumps(face)) == face, "json roundtrip")

    leg("the sleeve takes the cheapest 20", t_sleeve_picks_the_cheapest)
    leg("the sleeve is not the market tail", t_sleeve_excludes_the_market_rich_tail)
    leg("a short pool is a skip, not a pick", t_short_pool_is_not_a_pick)
    leg("a thin-coverage month is dropped", t_coverage_gate_blanks_thin_months)
    leg("the 3y window reads local history", t_window_labels_read_local_history)
    leg("the spot reading uses the label's edges", t_spot_reading_uses_the_same_edges)
    leg("disagreement is counted both ways", t_compare_counts_both_directions)
    leg("no overlap yields no agreement number", t_agreement_needs_both_labels)
    leg("a thin sleeve ruler is not measurable", t_verdict_requires_a_measurable_ruler)
    leg("a sign flip is a ruler-dependent answer", t_verdict_flags_a_ruler_dependent_answer)
    leg("today's side follows each ruler's label", t_current_follows_each_label)
    leg("consistent face verifies", t_verify_reads_its_rows)
    leg("a memorised verdict is caught", t_verify_catches_a_memorised_verdict)
    leg("a side that ignores its label is caught", t_verify_catches_a_side_that_ignores_its_label)
    leg("drift is named STALE", t_verify_names_drift_as_stale)
    leg("page prints both rulers", t_markdown_prints_both_rulers)
    leg("json roundtrip", t_json_roundtrip)

    bad = [x for x in legs if x[1] != "PASS"]
    for name, st, why in legs:
        print("%-48s %s %s" % (name, st, why))
    print("SELFTEST %d/%d PASS" % (len(legs) - len(bad), len(legs)))
    return 1 if bad else 0


# ---------------------------------------------------------------- cli
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    build(write=True, quiet=args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
