"""Does the width ladder need the 8% vol target to tell its story?

`etf_book_width_curve` priced the same frozen book at five pool widths *with* the 8% vol
target and reported the excess climbing 1.01 / -0.92 / 1.40 / 3.51 / 7.82pp. It could only
say one thing about the overlay: at the full pool the bare arm earns 15.18% against 11.16%
sized. One width is not a ladder -- a reader cannot tell whether breadth still pays when
nothing is de-risked, or whether the whole climb was the sizing rule quietly de-levering
wide pools harder than narrow ones.

This face prices the same ladder with `vol_target=None` (no sizing: the picks are held at
full weight) and puts the two ladders side by side. The sized ladder is *read* from the
published face, never recomputed, so the two cannot disagree about the book.

Criteria frozen here, before the first run, and re-derived by `check`:

  B1 SIGN_AGREES      at every width the bare excess is on the same side of zero as the
                      sized excess, outside a 0.5pp flat band (a 0.1pp number's sign is
                      noise, not evidence)
  B2 SHAPE_SURVIVES   the bare ladder never drops by more than 0.5pp per step going up
  B3 EDGE_EVERYWHERE  every width's bare excess is at least 1.0pp/yr
  B4 BREADTH_PAYS     the bare excess climbs at least 2.0pp from the narrowest width to
                      the full pool (a flat ladder means the picks work everywhere and
                      breadth buys nothing -- that is an answer, not a failure)

  SIZING_ARTIFACT       B1 fails -- the two arms tell opposite stories at some width
  BREADTH_SURVIVES_BARE B1 and B2 and B3 and B4 -- breadth pays with or without the overlay
  PICKS_ANY_WIDTH_BARE  B1 and B3 but not B2/B4 -- the picks work everywhere, breadth buys none
  MIXED_BARE            B1 holds but some width is under the edge floor
  NOT_READABLE          either ladder is missing arms

What the overlay costs is printed per width (`sizing_cost`): the CAGR it gives up and the
drawdown it buys back, at that width. A dash there means one arm could not be priced.

Usage:
  python scripts/etf_book_width_curve_bare.py run
  python scripts/etf_book_width_curve_bare.py check
  python scripts/etf_book_width_curve_bare.py --selftest
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A
import etf_book_width_curve as C

OUT = "etf_book_width_curve_bare.json"
SIZED_FACE = "etf_book_width_curve.json"

# frozen before the first run
WIDTHS = (15, 25, 40, 60, None)
REBAL = C.REBAL
N_HOLD = C.N_HOLD
COST = C.COST
MODERN_START = C.MODERN_START
FLAT_BAND_PP = 0.5
MONO_SLACK_PP = C.MONO_SLACK_PP
EDGE_MIN_PP = C.RULE_WORKS_MIN_PP
CLIMB_MIN_PP = C.WIDTH_EDGE_FULL_PP  # narrowest -> full pool must gain this much to say breadth pays
CONTROL_TOL_PP = 1.0                  # full-pool bare must land this close to the published arm


def _side(x):
    if x is None:
        return None
    if x > FLAT_BAND_PP:
        return 1
    if x < -FLAT_BAND_PP:
        return -1
    return 0


def sign_agreement(bare, sized):
    """bare/sized: {label: excess_pp|None}. Returns (ok, disagreements)."""
    bad = []
    for k in bare:
        if k not in sized:
            bad.append("%s: sized ladder has no such width" % k)
            continue
        s1, s2 = _side(bare[k]), _side(sized[k])
        if s1 is None or s2 is None:
            bad.append("%s: an arm could not be priced" % k)
        elif s1 * s2 < 0:
            bad.append("%s: bare %+.2fpp vs sized %+.2fpp" % (k, bare[k], sized[k]))
    return (not bad), bad


def bare_verdict(rows):
    """rows: {label: {excess_pp, sized_excess_pp}} in ladder order. Frozen rule."""
    if not rows or rows.get("all", {}).get("excess_pp") is None:
        return "NOT_READABLE"
    bare = {k: r.get("excess_pp") for k, r in rows.items()}
    sized = {k: r.get("sized_excess_pp") for k, r in rows.items()}
    ok, _bad = sign_agreement(bare, sized)
    if not ok:
        return "SIZING_ARTIFACT"
    keys = [k for k in rows]
    steps = [rows[k]["excess_pp"] - rows[keys[i]]["excess_pp"]
             for i, k in enumerate(keys) if i]
    monotone = all(s >= -MONO_SLACK_PP for s in steps)
    every = all(v >= EDGE_MIN_PP for v in bare.values())
    climb = bare[keys[-1]] - bare[keys[0]]
    if every and monotone and climb >= CLIMB_MIN_PP:
        return "BREADTH_SURVIVES_BARE"
    if every:
        return "PICKS_ANY_WIDTH_BARE"
    return "MIXED_BARE"


def load_sized(path=None):
    """Read the published sized ladder verbatim. Never recompute it."""
    p = path or os.path.join("results", SIZED_FACE)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        face = json.load(f)
    ladder = {}
    for k, r in (face.get("ladder") or {}).items():
        ladder[k] = {"cagr": (r.get("book") or {}).get("cagr"),
                     "sharpe": (r.get("book") or {}).get("sharpe"),
                     "maxdd": (r.get("book") or {}).get("maxdd"),
                     "equal_weight_cagr": (r.get("pool_equal_weight") or {}).get("cagr"),
                     "excess_pp": r.get("excess_pp"),
                     "excess_t": r.get("excess_t"),
                     "pool_median_names": r.get("pool_median_names")}
    return {"evidence_cutoff": face.get("evidence_cutoff"),
            "verdict": face.get("verdict"), "ladder": ladder}


def published_bare():
    """The published full-pool bare arm, read from etf_nobond_vt (control, not an input)."""
    p = "results/etf_nobond_vt.json"
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            face = json.load(f)
    except Exception:
        return None
    for run in face.get("runs") or []:
        if run.get("label") == "nobond_base" and run.get("cagr") is not None:
            return {"label": run["label"], "cagr": run["cagr"],
                    "sharpe": run.get("sharpe"), "maxdd": run.get("maxdd"),
                    "cutoff": face.get("evidence_cutoff")}
    return None


def price_bare_ladder(close, openp, amt, sc, widths, lo):
    """One row per width with the sizing overlay switched off."""
    amt_rank = amt.rank(axis=1, ascending=False)
    out = {}
    for w in widths:
        mask = None if w is None else (amt_rank <= w)
        sc_w = sc if mask is None else sc.where(mask)
        offered = C._slice(sc_w.notna().sum(axis=1), lo)
        s, turn = R.open_to_open_equity(close, openp, amt, sc_w, REBAL, N_HOLD, COST,
                                        vol_target=None, start=lo)
        s = C._slice(s, lo)
        ew = C._slice(C._ew(close, list(close.columns), mask), lo)
        st, ewst = C._stats(s), C._stats(ew)
        row = {"pool_cap": w if w is not None else "full",
               "pool_median_names": round(float(offered.median()), 1) if len(offered) else 0.0,
               "turnover_x": round(float(turn), 2),
               "bare_book": st, "pool_equal_weight": ewst}
        if st.get("cagr") is not None and ewst.get("cagr") is not None:
            row["excess_pp"] = round((st["cagr"] - ewst["cagr"]) * 100.0, 3)
            t, n = C.paired_t(s.pct_change(), ew.pct_change())
            row["excess_t"] = t
            row["paired_days"] = n
        else:
            row["excess_pp"] = None
            row["excess_t"] = None
            row["paired_days"] = 0
        out[C.label_of(w)] = row
        print("  bare cap=%5s pool_med=%5.1f cagr=%s sr=%s dd=%s | ew=%s | excess=%spp t=%s"
              % (row["pool_cap"], row["pool_median_names"],
                 _pct(st.get("cagr")), _num(st.get("sharpe")), _pct(st.get("maxdd")),
                 _pct(ewst.get("cagr")), _num(row["excess_pp"]), _num(row["excess_t"])),
              flush=True)
    return out


def sizing_diagnostic(close, openp, amt, sc, widths, lo, sized_ladder):
    """Why the two ladders part company: how much of the book the overlay holds in cash.

    This arm re-runs the *sized* rule only to read `diag`. It is a diagnostic, not the
    sized ladder: the published CAGRs stay the evidence, and each recomputed CAGRs is
    printed next to its published twin so a reader can see this diag sits on the same book.
    """
    amt_rank = amt.rank(axis=1, ascending=False)
    out = {}
    for w in widths:
        mask = None if w is None else (amt_rank <= w)
        sc_w = sc if mask is None else sc.where(mask)
        diag = []
        s, _turn = R.open_to_open_equity(close, openp, amt, sc_w, REBAL, N_HOLD, COST,
                                         vol_target=C.TARGET_VOL, start=lo, diag=diag)
        s = C._slice(s, lo)
        scales = [d["scale"] for d in diag if d.get("scale") is not None]
        st = C._stats(s)
        k = C.label_of(w)
        pub = (sized_ladder.get(k) or {}).get("cagr")
        row = {"mean_scale": round(float(np.mean(scales)), 4) if scales else None,
               "share_not_full": (round(float(np.mean([1.0 if x < 0.999 else 0.0
                                                       for x in scales])), 4)
                                  if scales else None),
               "decisions": len(scales),
               "reproduced_cagr": st.get("cagr"),
               "published_cagr": pub}
        if st.get("cagr") is not None and pub is not None:
            row["delta_pp"] = round((st["cagr"] - pub) * 100.0, 3)
        out[k] = row
        print("  diag cap=%5s mean_scale=%s not_full=%s cagr_reproduced=%s vs published=%s d=%s"
              % (row_pool(k), _num(row["mean_scale"]), _num(row["share_not_full"]),
                 _pct(row["reproduced_cagr"]), _pct(row["published_cagr"]),
                 _num(row.get("delta_pp"))), flush=True)
    return out


def row_pool(k):
    return "full" if k == "all" else k


def run():
    sized = load_sized()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)

    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    print("bond-free universe %d, flips %d, cutoff %s"
          % (len(cols), n_flip, str(close.index[-1].date())), flush=True)

    sc = E.build_score(close[cols], amt[cols], feats)
    bare_rows = price_bare_ladder(close[cols], openp[cols], amt[cols], sc, WIDTHS, MODERN_START)

    ladder = {}
    sized_ladder = (sized or {}).get("ladder") or {}
    for w in WIDTHS:
        k = C.label_of(w)
        row = dict(bare_rows[k])
        srow = sized_ladder.get(k) or {}
        row["sized_excess_pp"] = srow.get("excess_pp")
        row["sized_cagr"] = srow.get("cagr")
        row["sized_maxdd"] = srow.get("maxdd")
        b, s = row.get("bare_book") or {}, srow
        if b.get("cagr") is not None and s.get("cagr") is not None:
            row["sizing_cost"] = {
                "cagr_given_up_pp": round((b["cagr"] - s["cagr"]) * 100.0, 3),
                "maxdd_bought_pp": (round((s["maxdd"] - b["maxdd"]) * 100.0, 3)
                                    if b.get("maxdd") is not None and s.get("maxdd") is not None
                                    else None),
            }
        else:
            row["sizing_cost"] = None
        ladder[k] = row

    verdict = bare_verdict(ladder)
    bare_x = {k: v.get("excess_pp") for k, v in ladder.items()}
    sized_x = {k: v.get("sized_excess_pp") for k, v in ladder.items()}
    ok, disagreements = sign_agreement(bare_x, sized_x)
    t_readable = [r for r in ladder.values() if r.get("excess_t") is not None]

    out = {
        "evidence_cutoff": str(close.index[-1].date()),
        "universe": len(cols),
        "flips_repaired": int(n_flip),
        "rule": {"rebal_days": REBAL, "n_hold": N_HOLD, "cost_per_side": COST,
                 "vol_target": None,
                 "note": "same frozen book as etf_book_width_curve, sizing overlay switched off"},
        "window": {"modern_start": MODERN_START, "modern_end": str(close.index[-1].date())},
        "criteria": {"flat_band_pp": FLAT_BAND_PP, "mono_slack_pp": MONO_SLACK_PP,
                     "edge_min_pp": EDGE_MIN_PP, "climb_min_pp": CLIMB_MIN_PP,
                     "control_tol_pp": CONTROL_TOL_PP},
        "ladder": ladder,
        "verdict": verdict,
        "sign_agrees": ok,
        "sign_disagreements": disagreements,
        "shape_is_noise": bool(t_readable) and all(abs(r["excess_t"]) < C.T_READABLE
                                                  for r in t_readable),
        "sized_face": {"path": "results/" + SIZED_FACE,
                       "evidence_cutoff": (sized or {}).get("evidence_cutoff"),
                       "verdict": (sized or {}).get("verdict"),
                       "note": "read verbatim, never recomputed -- the two arms share one book"},
    }

    print("sizing diagnostic (runs the overlay only to read its cash weight):", flush=True)
    out["sizing_diagnostic"] = sizing_diagnostic(close[cols], openp[cols], amt[cols], sc,
                                                 (15, 25, None), MODERN_START, sized_ladder)

    ctl = published_bare()
    got = ladder["all"]["bare_book"].get("cagr")
    if ctl and got is not None:
        out["control_full_pool_bare"] = {
            "published_label": ctl["label"], "published_cagr": ctl["cagr"],
            "published_cutoff": ctl.get("cutoff"), "reproduced_cagr": got,
            "delta_pp": round((got - ctl["cagr"]) * 100.0, 3),
        }

    print("VERDICT %s (sign_agrees=%s, shape_is_noise=%s)"
          % (verdict, ok, out["shape_is_noise"]), flush=True)
    if not ok:
        for d in disagreements:
            print("  SIGN DISAGREES " + d, flush=True)
    with open(os.path.join("results", OUT), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote results/%s" % OUT, flush=True)
    return 0


def _pct(x):
    return "n/a" if x is None else "%.2f%%" % (x * 100.0)


def _num(x):
    return "n/a" if x is None else "%.2f" % x


def check():
    path = os.path.join("results", OUT)
    if not os.path.exists(path):
        print("STALE face missing: %s" % path)
        return 3
    with open(path, encoding="utf-8") as f:
        face = json.load(f)
    problems = []

    sized = load_sized()
    if sized is None:
        print("STALE sized face missing: results/%s" % SIZED_FACE)
        return 3
    if sized.get("evidence_cutoff") != face.get("evidence_cutoff"):
        print("STALE sized ladder is on %s, this face is on %s"
              % (sized.get("evidence_cutoff"), face.get("evidence_cutoff")))
        return 3

    ladder = face.get("ladder") or {}
    if not ladder:
        print("CHECK FAILED ladder empty")
        return 3

    # every printed excess must re-derive from its own two CAGRs
    for k, r in ladder.items():
        b, e = r.get("bare_book") or {}, r.get("pool_equal_weight") or {}
        if b.get("cagr") is not None and e.get("cagr") is not None:
            if r.get("excess_pp") != round((b["cagr"] - e["cagr"]) * 100.0, 3):
                problems.append("%s excess_pp does not re-derive from its own CAGRs" % k)
        else:
            problems.append("%s bare arm unreadable (no cagr)" % k)
        # the sized columns must be the published ones, not this script's own numbers
        srow = (sized["ladder"].get(k) or {})
        if r.get("sized_excess_pp") != srow.get("excess_pp"):
            problems.append("%s sized_excess_pp %r != published %r"
                            % (k, r.get("sized_excess_pp"), srow.get("excess_pp")))

    want = bare_verdict(ladder)
    if want != face.get("verdict"):
        problems.append("verdict %r != re-derived %r" % (face.get("verdict"), want))
    ok, bad = sign_agreement({k: v.get("excess_pp") for k, v in ladder.items()},
                             {k: v.get("sized_excess_pp") for k, v in ladder.items()})
    if bool(face.get("sign_agrees")) != ok:
        problems.append("sign_agrees %r != re-derived %r (%s)"
                        % (face.get("sign_agrees"), ok, "; ".join(bad) or "no detail"))
    if list(face.get("sign_disagreements") or []) != bad:
        problems.append("sign_disagreements do not re-derive")

    ctl = face.get("control_full_pool_bare")
    if ctl and ctl.get("published_cagr") is not None and ctl.get("reproduced_cagr") is not None:
        d = abs(ctl["reproduced_cagr"] - ctl["published_cagr"]) * 100.0
        if d > CONTROL_TOL_PP:
            problems.append("full-pool bare control drifted %.2fpp from the published arm" % d)
    else:
        problems.append("no full-pool bare control: the face cannot prove it priced this book")

    diag = face.get("sizing_diagnostic") or {}
    if not diag:
        problems.append("no sizing diagnostic: the verdict names the overlay but shows no cash weight")
    for k, r in diag.items():
        if r.get("mean_scale") is None:
            problems.append("diagnostic %s has no mean scale" % k)
        if r.get("delta_pp") is None:
            problems.append("diagnostic %s cannot show its own reproduced CAGR" % k)
        elif abs(r["delta_pp"]) > CONTROL_TOL_PP:
            problems.append("diagnostic %s reproduced %.2fpp off the published sized arm"
                            % (k, r["delta_pp"]))

    if problems:
        for p in problems:
            print("PROBLEM", p)
        return 3
    print("CHECK OK verdict=%s ladder=%d sign_agrees=%s shape_is_noise=%s"
          % (face.get("verdict"), len(ladder), face.get("sign_agrees"),
             face.get("shape_is_noise")))
    return 0


def selftest():
    legs = []

    def L(text, ok):
        legs.append((text, bool(ok)))

    def rows(bare, sized):
        return {k: {"excess_pp": bare[k], "sized_excess_pp": sized[k]} for k in bare}

    same_up = rows({"15": 1.5, "all": 9.0}, {"15": 1.0, "all": 7.8})
    L("both ladders positive and climbing -> BREADTH_SURVIVES_BARE",
      bare_verdict(same_up) == "BREADTH_SURVIVES_BARE")

    flip = rows({"15": 1.5, "all": -3.0}, {"15": 1.0, "all": 7.8})
    L("the two arms disagree at the full pool -> SIZING_ARTIFACT",
      bare_verdict(flip) == "SIZING_ARTIFACT")

    flat = rows({"15": 5.0, "25": 5.3, "all": 5.1}, {"15": 1.0, "25": 1.2, "all": 7.8})
    L("bare edge at every width but no climb -> PICKS_ANY_WIDTH_BARE",
      bare_verdict(flat) == "PICKS_ANY_WIDTH_BARE")

    thin = rows({"15": 0.4, "all": 5.0}, {"15": 1.0, "all": 7.8})
    L("a width under the edge floor -> MIXED_BARE", bare_verdict(thin) == "MIXED_BARE")

    shallow = rows({"15": 5.0, "all": 6.0}, {"15": 1.0, "all": 7.8})
    L("climbing only 1.0pp from 15 names to the full pool -> PICKS_ANY_WIDTH_BARE",
      bare_verdict(shallow) == "PICKS_ANY_WIDTH_BARE")

    deep = rows({"15": 1.2, "all": 7.0}, {"15": 1.0, "all": 7.8})
    L("a 5.8pp climb with every width above the floor -> BREADTH_SURVIVES_BARE",
      bare_verdict(deep) == "BREADTH_SURVIVES_BARE")

    band = rows({"15": 0.3, "all": 5.0}, {"15": -0.2, "all": 7.8})
    L("0.3pp vs -0.2pp is inside the flat band, not a disagreement",
      sign_agreement({"15": 0.3, "all": 5.0}, {"15": -0.2, "all": 7.8})[0]
      and bare_verdict(band) != "SIZING_ARTIFACT")

    L("no full pool -> NOT_READABLE", bare_verdict(rows({"15": 1.0}, {"15": 1.0})) == "NOT_READABLE")
    L("an unpriceable arm -> NOT_READABLE",
      bare_verdict(rows({"15": 1.0, "all": None}, {"15": 1.0, "all": 7.8})) != "BREADTH_SURVIVES_BARE")

    missing = sign_agreement({"15": 2.0}, {})
    L("a width the sized face does not have is a disagreement", not missing[0])

    # the sized columns must come from the published face, not from local recomputation
    sized = load_sized()
    L("sized ladder loads from the published face",
      sized is not None and "all" in sized["ladder"])
    L("sized ladder keeps the published excess verbatim",
      sized is None or sized["ladder"]["all"]["excess_pp"] ==
      json.load(open(os.path.join("results", SIZED_FACE), encoding="utf-8"))
      ["ladder"]["all"]["excess_pp"])

    # the ladder step is a band, not a pass
    edge = rows({"15": 1.0, "25": 1.2, "40": 0.7, "all": 0.9}, {"15": 0.0, "25": 1.0,
                                                                 "40": 1.4, "all": 0.9})
    L("exactly 0.5pp down stays inside the slack",
      bare_verdict(edge) != "SIZING_ARTIFACT")

    for text, ok in legs:
        print(("PASS " if ok else "FAIL ") + text)
    print("selftest %d/%d" % (sum(1 for _t, ok in legs if ok), len(legs)))
    return 0 if all(ok for _t, ok in legs) else 1


if __name__ == "__main__":
    arg = (sys.argv[1] if len(sys.argv) > 1 else "run").strip().lower()
    if arg in ("--selftest", "selftest"):
        sys.exit(selftest())
    if arg == "check":
        sys.exit(check())
    sys.exit(run())
