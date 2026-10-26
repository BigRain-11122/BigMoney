"""How much of the published ETF book headline is the split-print repair worth?

The production card repairs every single-bar move past `FLIP_THR` (35%) and rescales both
price faces, so the number on the card (12 names, 20-bar grid, 10bp/side, 8% vol rule) is
produced on a REPAIRED panel. Nobody had priced that repair: the E81 line showed the same
class of print moving several research faces (calendar cost, size-neutral spread, the
robustness grid), and every one of those faces charged an unadjusted print at weight 1/n --
exactly the way this book charges it when a held name splits untraded.

So this audit publishes the raw twin beside the untouched card:

  arm A (repair=True)   -- the published book, asserted equal to the card's own row;
  arm B (repair=False)  -- the same config, same universe, same score builder, raw prints;
  attribution           -- every repaired print, whether the book actually held that name,
                           and the book-level bp it would have charged at 1/n.

The point is not to re-decide anything: the repair is a data fix, not a knob. It is to
replace "we repaired the panel" with "the repair is worth X pp of the published number".

  python scripts\\etf_book_split_audit.py run
  python scripts\\etf_book_split_audit.py selftest
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_book_production as P
import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A

OUT_DIR = os.path.join(E.PATHS.results_dir, "etf_book_split_audit")
CARD_JSON = os.path.join(E.PATHS.results_dir, "etf_book_production", "latest.json")
CFG = {"n_hold": 12, "rebal": 20, "cost": P.COST, "vol_target": P.TARGET_VOL}
METRICS = ("cagr", "sharpe", "maxdd", "vol")


def flip_events(close_raw, cols, thr=A.FLIP_THR, persist_bars=5, persist_tol=0.20):
    """Every single-bar move past `thr` inside the production universe, with two tests.

    Bars are compared to the previous priced close (a split often sits next to a
    suspension bar), and each print carries two independent readings:

    * implied share ratio -- an integer ratio is the tell of a split, but a 1:3.15 or
      1:3.71 conversion (both live in this panel) is a corporate action that no integer
      test will recognise, so the ratio is evidence, never the verdict;
    * LEVEL PERSISTENCE -- a corporate action leaves the new price level in place, while a
      misprint that gets restated reverts. Taking the next `persist_bars` priced closes and
      asking whether they stay within `persist_tol` of the print is the decisive test.
    """
    ev = []
    for c in cols:
        s = close_raw[c].dropna()
        if len(s) < 2:
            continue
        vals = s.to_numpy(dtype=float)
        r = s.pct_change()
        for j, (d, v) in enumerate(r.items()):
            if v is None or not np.isfinite(v) or abs(v) <= thr:
                continue
            ratio = 1.0 / (1.0 + v) if v > -1.0 else np.inf
            if ratio < 1.0 and np.isfinite(ratio):
                ratio = 1.0 / ratio
            near = int(round(ratio)) if np.isfinite(ratio) else None
            resid = abs(ratio / near - 1.0) if near and near >= 1 else None
            after = vals[j + 1:j + 1 + persist_bars]
            drift = None
            if len(after):
                drift = float(np.median(after / vals[j] - 1.0))
            ev.append({
                "name": c, "date": str(pd.Timestamp(d).date()),
                "ret_pct": round(100.0 * float(v), 2),
                "prev_close": round(float(s.shift(1).loc[d]), 4),
                "close": round(float(vals[j]), 4),
                "implied_ratio": None if near is None else round(float(ratio), 4),
                "nearest_int": near,
                "resid_pct": None if resid is None else round(100.0 * float(resid), 3),
                "integer_like": bool(near is not None and near >= 2 and resid is not None
                                     and resid <= 0.02),
                "post_drift_pct": None if drift is None else round(100.0 * drift, 2),
                "level_persists": (None if drift is None else bool(abs(drift) <= persist_tol)),
            })
    ev.sort(key=lambda e: (e["date"], e["name"]))
    return ev


def book_windows(diag):
    """(decision date, set of names, scale) per decision, in date order."""
    out = []
    for row in diag:
        out.append((pd.Timestamp(row["date"]), set(row["book"]), float(row.get("scale") or 1.0)))
    out.sort(key=lambda x: x[0])
    return out


def attribute(events, windows, n_hold, cut_dates):
    """Attach book membership to each event and total the bp the raw print would charge."""
    edges = [w[0] for w in windows]
    for e in events:
        d = pd.Timestamp(e["date"])
        held, dec = False, None
        for i in range(len(windows) - 1, -1, -1):
            if edges[i] <= d:
                dec = edges[i]
                held = e["name"] in windows[i][1]
                break
        e["book_decision"] = None if dec is None else str(dec.date())
        e["held_by_book"] = bool(held)
        # one name in an n-name book at full weight: the raw print charges |r|/n
        e["book_bp_if_unrepaired"] = round(10000.0 * abs(e["ret_pct"]) / 100.0 / n_hold, 2)
        e["book_bp_signed"] = round(-10000.0 * (e["ret_pct"] / 100.0) / n_hold, 2)
    inbook = [e for e in events if e["held_by_book"]]
    return {
        "events": len(events),
        "events_in_universe": len(events),
        "events_held_by_book": len(inbook),
        "integer_like_events": len([e for e in events if e["integer_like"]]),
        "level_persist_events": len([e for e in events if e["level_persists"]]),
        "level_persist_in_book": len([e for e in inbook if e["level_persists"]]),
        "reverting_events": len([e for e in events if e["level_persists"] is False]),
        "bp_if_unrepaired_abs": round(sum(e["book_bp_if_unrepaired"] for e in inbook), 2),
        "bp_if_unrepaired_signed": round(sum(e["book_bp_signed"] for e in inbook), 2),
    }


def _stats(bt_row):
    return {k: (None if bt_row.get(k) is None else round(float(bt_row[k]), 6))
            for k in METRICS}


def repair_legacy(close, openp, thr=A.FLIP_THR):
    """The repair as it stood before r1282: returns measured with `close.pct_change()`.

    pandas 3 no longer fills across a suspension bar, so a split print that follows one
    comes back NaN. The level rebuild still flattened those prints (NaN floors to a 0%
    day), but the count printed on the card missed them and a small REAL move on such a
    bar was dropped with them. Kept here as a priced counterfactual, not as a code path.
    """
    r = close.pct_change()
    bad = r.abs() > thr
    r_clean = r.where(~bad, 0.0).fillna(0.0)
    first = close.ffill().bfill().iloc[0]
    adj = (1.0 + r_clean).cumprod().multiply(first, axis=1)
    adj = adj.where(close.notna())
    factor = adj / close
    return adj, openp * factor, int(bad.to_numpy().sum())


def residual_prints(close, thr=A.FLIP_THR):
    """How many prints past `thr` survive in this panel, measured against priced closes."""
    r = close.ffill().pct_change()
    return int((r.abs() > thr).to_numpy().sum())


def run(n_hold=CFG["n_hold"], rebal=CFG["rebal"]):
    rep = P.prep_panel(repair=True)
    raw = P.prep_panel(repair=False)
    leg = P.prep_panel(repair_fn=repair_legacy)
    close, openp, amt, score, cls, n_flip = rep
    close_r, openp_r, amt_r, score_r, _c_r, n_raw = raw
    close_l, openp_l, amt_l, score_l, _c_l, n_legacy = leg
    assert n_raw == 0 and list(close.columns) == list(close_r.columns) == list(close_l.columns)
    assert list(close.columns) == list(close_l.columns) and list(amt.columns) == list(amt_l.columns)

    bt_a, ser_a = P.backtest(close, openp, amt, score, n_hold, rebal,
                             cost=CFG["cost"], vol_target=CFG["vol_target"])
    bt_b, ser_b = P.backtest(close_r, openp_r, amt_r, score_r, n_hold, rebal,
                             cost=CFG["cost"], vol_target=CFG["vol_target"])
    bt_c, ser_c = P.backtest(close_l, openp_l, amt_l, score_l, n_hold, rebal,
                             cost=CFG["cost"], vol_target=CFG["vol_target"])

    arms = {}
    for arm, bt in (("repaired", bt_a), ("raw", bt_b), ("legacy_repair", bt_c)):
        arms[arm] = {lbl: _stats(bt[lbl]) for lbl in ("full", "is", "oos")}
        arms[arm]["turnover_per_decision"] = bt["turnover_per_decision"]
    delta = {}
    for lbl in ("full", "is", "oos"):
        delta[lbl] = {k: (None if arms["repaired"][lbl][k] is None
                          else round(arms["repaired"][lbl][k] - arms["raw"][lbl][k], 6))
                      for k in METRICS}

    diag = []
    R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, CFG["cost"],
                          vol_target=CFG["vol_target"], diag=diag)
    windows = book_windows(diag)
    events = flip_events(close_r, list(close_r.columns))
    attr = attribute(events, windows, n_hold, None)

    cutoff = str(close.index[-1].date())
    out = {
        "evidence_cutoff": cutoff,
        "script": "scripts/etf_book_split_audit.py",
        "config": {"n_hold": n_hold, "rebal": rebal, "cost_bp_per_side": CFG["cost"] * 1e4,
                   "vol_target": CFG["vol_target"], "flip_thr": A.FLIP_THR,
                   "universe_size": len(close.columns), "flips_repaired": n_flip},
        "arms": arms,
        "delta_repaired_minus_raw": delta,
        "flip_attribution": {k: v for k, v in attr.items() if k != "events"},
        "events_held_by_book": [e for e in events if e["held_by_book"]],
        "event_count": len(events),
        "curves_identical": bool(ser_a.round(12).equals(ser_b.round(12))),
        "repair_completeness": {
            "prints_reported_now": n_flip,
            "prints_reported_legacy": n_legacy,
            "prints_measured_vs_priced_close": residual_prints(close_r),
            "prints_surviving_in_repaired_panel": residual_prints(close),
            "prints_surviving_in_legacy_panel": residual_prints(close_l),
            "legacy_equals_published": bool(ser_c.round(12).equals(ser_a.round(12))),
        },
    }
    out["verdict"] = verdict(out)

    # ---- the gate that stops this audit from pricing a different book than the card
    card_ok = None
    if os.path.exists(CARD_JSON):
        card = json.load(open(CARD_JSON, encoding="utf-8"))
        row = (card.get("backtest") or {}).get("n%d_vt08" % n_hold) or {}
        diffs = []
        for lbl in ("full", "is", "oos"):
            for k in METRICS:
                got, want = arms["repaired"][lbl][k], row.get(lbl, {}).get(k)
                if got is None or want is None:
                    continue
                if abs(float(got) - float(want)) > 5e-5:
                    diffs.append("%s.%s %.6f!=%.6f" % (lbl, k, got, want))
        card_ok = not diffs
        out["card_agreement"] = {"equal": card_ok, "diffs": diffs,
                                 "card_ts": card.get("ts"),
                                 "card_cutoff": card.get("evidence_cutoff")}
        if not card_ok:
            out["verdict"] += " [CARD MISMATCH: %s]" % "; ".join(diffs[:4])

    os.makedirs(OUT_DIR, exist_ok=True)
    for name in ("AUDIT-%s.json" % cutoff, "latest.json"):
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({"evidence_cutoff": cutoff, "verdict": out["verdict"],
                      "arms": arms, "delta": delta,
                      "attribution": out["flip_attribution"],
                      "repair_completeness": out["repair_completeness"],
                      "card_agreement": card_ok}, ensure_ascii=False, indent=1))
    return out, (card_ok is not False)


def verdict(out):
    d = out["delta_repaired_minus_raw"]["full"]
    a = out["flip_attribution"]
    n_ev = out["event_count"]
    if out.get("curves_identical"):
        return ("the repair is worth nothing here: the raw and repaired curves are "
                "identical to 12 decimals (%d prints flagged in the universe, %d ever held)"
                % (n_ev, a["events_held_by_book"]))
    return ("the repair is worth %+.2fpp of CAGR on the published headline (full window, "
            "%.2f%% vs %.2f%% raw); %d prints flagged in the universe, %d of them ever in "
            "the book (%d of those level-persistent, i.e. corporate actions), %.0fbp of "
            "raw charge in total"
            % (100.0 * d["cagr"], 100.0 * out["arms"]["repaired"]["full"]["cagr"],
               100.0 * out["arms"]["raw"]["full"]["cagr"], n_ev, a["events_held_by_book"],
               a["level_persist_in_book"], a["bp_if_unrepaired_abs"]))


def selftest():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(("PASS " if cond else "FAIL ") + name + (" " + detail if detail else ""),
              flush=True)

    # 1. inventory: an integer split print is found, its ratio is recovered, a small move
    #    is not flagged (the threshold is a corporate-action screen, not a vol filter).
    idx = pd.bdate_range("2021-01-04", periods=30)
    px = pd.Series(100.0, index=idx, dtype=float)
    px.iloc[10:] = 50.0                                   # 2:1 split
    px.iloc[20] = 55.0                                    # +10% real day
    df = pd.DataFrame({"sh510300": px})
    ev = flip_events(df, ["sh510300"])
    chk("split print detected once", len(ev) == 1, str(len(ev)))
    chk("split ratio recovered as integer", ev and ev[0]["nearest_int"] == 2
        and ev[0]["integer_like"] and abs(ev[0]["implied_ratio"] - 2.0) < 1e-9, str(ev[:1]))
    chk("ordinary 10% day not flagged", all(abs(e["ret_pct"] - (-50.0)) < 1e-6 for e in ev))
    chk("split print stays at its new level", ev and ev[0]["level_persists"] is True,
        "drift=%s" % (ev[0]["post_drift_pct"] if ev else None))

    # 1b. a misprint that gets restated reverts, and the ratio of a NON-integer conversion
    #     is not recognised by the integer test -- persistence is the test that survives both
    px2 = pd.Series(100.0, index=idx, dtype=float)
    px2.iloc[10] = 75.0                                   # -25% ... below thr, then
    px2.iloc[11:] = 100.0                                 # ...straight back: a restatement
    px2.iloc[15:] = 31.7                                  # 3.155:1 conversion, no revert
    df2 = pd.DataFrame({"sh510500": px2})
    ev_conv = flip_events(df2, ["sh510500"])
    conv = [e for e in ev_conv if e["date"] == str(idx[15].date())]
    chk("non-integer conversion flagged", len(conv) == 1, str(len(ev_conv)))
    chk("integer test misses a 3.15:1 conversion",
        conv and conv[0]["integer_like"] is False, str(conv[:1]))
    chk("persistence test still calls it a conversion",
        conv and conv[0]["level_persists"] is True, str(conv[:1]))
    px3 = pd.Series(100.0, index=idx, dtype=float)
    px3.iloc[12] = 50.0
    px3.iloc[13:] = 100.0                                 # straight back: a restatement
    ev_rev = flip_events(pd.DataFrame({"sh510050": px3}), ["sh510050"])
    rev = [e for e in ev_rev if e["date"] == str(idx[12].date())]
    chk("a restated print is not persistent",
        rev and rev[0]["level_persists"] is False, str(rev[:1]))
    chk("reverting prints counted separately",
        len([e for e in ev_rev if e["level_persists"] is False]) >= 1)

    # 2. membership: a print inside the holding window is charged, one before the book
    #    existed is not -- the attribution must not count prints the book never held.
    w = [(pd.Timestamp("2021-01-04"), {"sh510300", "sh510500"}, 0.9),
         (pd.Timestamp("2021-01-20"), {"sh510500"}, 1.0)]
    att = attribute(ev, w, 2, None)
    chk("in-book print attributed to the book", att["events_held_by_book"] == 1, str(att))
    chk("bp charge is |r|/n", abs(att["bp_if_unrepaired_abs"] - 2500.0) < 1e-6,
        str(att["bp_if_unrepaired_abs"]))
    ev2 = [dict(e, date="2021-01-21") for e in ev]     # now outside the held book
    att2 = attribute(ev2, w, 2, None)
    chk("print after the member left is not charged", att2["events_held_by_book"] == 0)

    # 3. END-TO-END on a synthetic panel with a mid-window split in a held name: the raw
    #    arm must take the hit and the repaired arm must not. An invariance leg alone
    #    would pass while nothing traded, so the activity legs come first.
    idx = pd.bdate_range("2021-01-04", periods=400)
    rng = np.random.default_rng(11)
    syn = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0, 0.004, (len(idx), 6)), axis=0)),
                       index=idx, columns=["51030%d" % i for i in range(6)])
    syn.iloc[200:, 2] *= 0.5                             # 2:1 split on one name
    s_open = syn.shift(1).bfill()
    s_amt = pd.DataFrame(1e8, index=idx, columns=syn.columns)
    s_score = syn.pct_change(20).fillna(0.0)
    rep_close, rep_open, n_rep = A.repair_flips(syn, s_open)
    chk("synthetic split repaired", n_rep == 1, "n=%d" % n_rep)
    chk("repair leaves no >35% bar", (rep_close.pct_change().abs().max().max() <= A.FLIP_THR))
    chk("raw keeps the split bar", (syn.pct_change().abs().max().max() > A.FLIP_THR))

    # 3b. REGRESSION for the r1282 fix: a split that follows a suspension bar must be
    #     counted and flattened. pandas 3's pct_change returns NaN there, so the pre-fix
    #     repair flattened it by accident (NaN -> 0% day) but reported 0 prints.
    gap = syn.copy()
    gap.iloc[150, 4] = np.nan                            # suspension bar
    gap.iloc[151:, 4] *= 0.5                             # split on the next priced bar
    g_rep, _g_open, g_n = A.repair_flips(gap, gap.shift(1).bfill())
    _l_rep, _l_open, g_n_legacy = repair_legacy(gap, gap.shift(1).bfill())
    chk("gap-adjacent split is counted", g_n >= 2, "n=%d (legacy %d)" % (g_n, g_n_legacy))
    chk("legacy count misses the gap-adjacent print", g_n > g_n_legacy,
        "now=%d legacy=%d" % (g_n, g_n_legacy))
    chk("repaired panel has no print past thr",
        residual_prints(g_rep) == 0, "residual=%d" % residual_prints(g_rep))
    chk("raw panel still has one", residual_prints(gap) >= 1, str(residual_prints(gap)))
    feats_r = {"mom_12_1": rep_close.pct_change(20)}
    feats_b = {"mom_12_1": syn.pct_change(20)}
    sa, _ = R.open_to_open_equity(rep_close, rep_open, s_amt,
                                  E.build_score(rep_close, s_amt, feats_r), 20, 3, 0.001)
    sb, _ = R.open_to_open_equity(syn, s_open, s_amt,
                                  E.build_score(syn, s_amt, feats_b), 20, 3, 0.001)
    chk("both arms traded", sa.notna().sum() > 50 and sb.notna().sum() > 50,
        "a=%d b=%d" % (sa.notna().sum(), sb.notna().sum()))
    chk("raw arm diverges from repaired arm", not sa.round(12).equals(sb.round(12)),
        "final a=%.6f b=%.6f" % (sa.iloc[-1], sb.iloc[-1]))

    # 4. the card's own panel builder keeps its published default
    import inspect
    sig = inspect.signature(P.prep_panel)
    chk("prep_panel defaults to the repaired panel",
        sig.parameters["repair"].default is True)

    print("SELFTEST " + ("OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if "selftest" in a or "--selftest" in a:
        sys.exit(selftest())
    o, agree = run()
    sys.exit(0 if agree else 1)