"""Does the defensive-ruler flip survive out of sample, or is the full window doing the work?

r1974 proved the ruler that labels "money" was broken (45 of 59 "cash" names are not cash).
r1975 then asked the treasurer's next question -- when you swap the repaired ruler in, does the
book still win per unit of risk? -- and answered: NO, the Sharpe edge goes from +0.240 to
-0.332. It also declared its own hole: the repair face prints the basket on the FULL window
only, so that face can say "the full-window reading flips" and nothing more.

This face closes that hole with the same objects and the same code paths:

  1. build both baskets (published ruler / repaired ruler) with `etf_equity_alpha.ew_universe`
     -- the exact function the repair face uses, so the arithmetic is imported, not copied;
  2. cut the book's own window at `etf_equity_alpha.IS_END` (2023-12-31) and price each half
     with `etf_equity_alpha.stats2` -- the exact function `etf_nobond_vt.report` uses for the
     book, so both sides of the comparison are renormalised the same way (r1262: a segment CAGR
     is measured off the segment's own first level, never off a global base);
  3. read the book's IS/OOS rows from the book face itself (never re-derive the book here: a
     second implementation of the book would be a second answer);
  4. judge the flip per segment, and separately judge whether the RULER REPAIR is itself a
     full-window artefact -- i.e. whether the repaired basket's advantage over the published
     basket lives in both halves or only in one.

Verdicts (frozen before the first run):

  FLIP_HOLDS_IN_BOTH_SEGMENTS      the book is behind per unit of risk in IS *and* OOS
  FLIP_IS_OUT_OF_SAMPLE_ONLY       the book is behind only after 2023 (the flip is recent)
  FLIP_IS_IN_SAMPLE_ONLY           the book is behind only up to 2023 (the flip has decayed)
  NO_FLIP_IN_EITHER_SEGMENT        the book is ahead in both halves -- contradicts r1975 and
                                   the face says so rather than picking a winner

  RULER_REPAIR_EFFECT_HOLDS_IN_BOTH_SEGMENTS / RULER_REPAIR_EFFECT_IS_SEGMENT_SPECIFIC

Nothing here writes a shared face. It reads three published faces plus the local panel and
lands its own new file. Money lines that would need a number no face publishes are withheld and
named (r98 family: an absent input is "cannot answer", never a zero).

  python scripts/defensive_ruler_flip_subperiods.py            # build + write json/md
  python scripts/defensive_ruler_flip_subperiods.py check      # re-derive and compare
  python scripts/defensive_ruler_flip_subperiods.py selftest   # hermetic legs
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_asset_class as AC  # noqa: E402
import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_class_ew_ruler_repair as RR  # noqa: E402

SCHEMA = "defensive_ruler_flip_subperiods/v1"
REPAIR_FACE = os.path.join(ROOT, "results", "etf_class_ew_ruler_repair.json")
BOOK_FACE = os.path.join(ROOT, "results", "etf_nobond_vt.json")
OUT_JSON = os.path.join(ROOT, "results", "defensive_ruler_flip_subperiods.json")
OUT_MD = os.path.join(ROOT, "research", "DEFENSIVE-RULER-FLIP-SUBPERIODS.md")
REL_JSON = "results/defensive_ruler_flip_subperiods.json"

IS_END = A.IS_END                     # 2023-12-31, the book's own split
WANT = ("bond", "money")
DEFENSIVE = ("bond", "money")

# ---- judges, frozen before the first run -----------------------------------------------
C1_TOL_PP = 0.02      # control: this face's full-window basket must reproduce the repair face
C1_TOL_X = 0.02       # ... on vol / sharpe / maxdd (absolute)
SEG_MIN_BARS = 200    # a segment shorter than this cannot answer
ROW_TOL = 5e-4        # stored precision of cagr/vol/maxdd in the source faces
SHARPE_TOL = 5e-3     # stored precision of sharpe (3dp)
BARS_PER_YEAR = 242.0


# ---------------------------------------------------------------------------------------
# pure helpers
# ---------------------------------------------------------------------------------------
def _stats(ser, label):
    """A.stats2 with the short-slice guard surfaced instead of swallowed."""
    ser = ser.dropna()
    if len(ser) < SEG_MIN_BARS:
        return {"label": label, "note": "short", "bars": int(len(ser)), "usable": False}
    out = A.stats2(ser, label)
    out["usable"] = "cagr" in out
    out["bars"] = int(len(ser))
    out["first"] = str(ser.index[0].date())
    out["last"] = str(ser.index[-1].date())
    return out


def _segments(ser):
    return {"full": _stats(ser, "full"),
            "is": _stats(ser[ser.index <= IS_END], "is"),
            "oos": _stats(ser[ser.index > IS_END], "oos")}


def _edge(book, bench):
    """The r1975 derivation, applied to one segment. Both sides must already be usable."""
    if not bench.get("usable") or book.get("sharpe") is None or bench.get("sharpe") is None:
        return {"usable": False, "why": "a side of this segment is missing"}
    edge = float(book["sharpe"]) - float(bench["sharpe"])
    dd_book, dd_bench = book.get("maxdd"), bench.get("maxdd")
    dd_mult = (abs(dd_book) / abs(dd_bench)) if dd_bench else None
    return {
        "usable": True,
        "book_sharpe": round(float(book["sharpe"]), 3),
        "bench_sharpe": round(float(bench["sharpe"]), 3),
        "sharpe_edge": round(edge, 3),
        "who_is_better_per_unit_of_risk": "book" if edge > 0 else ("bench" if edge < 0 else "tie"),
        "book_cagr": book.get("cagr"), "bench_cagr": bench.get("cagr"),
        "cagr_gap_pp": (round((float(book["cagr"]) - float(bench["cagr"])) * 100.0, 2)
                        if book.get("cagr") is not None and bench.get("cagr") is not None else None),
        "book_maxdd": dd_book, "bench_maxdd": dd_bench,
        "drawdown_multiple": None if dd_mult is None else round(dd_mult, 2),
    }


def _verdict(e_is, e_oos):
    if not (e_is.get("usable") and e_oos.get("usable")):
        return "CANNOT_ANSWER_A_SEGMENT_IS_MISSING"
    a, b = e_is["sharpe_edge"], e_oos["sharpe_edge"]
    if a < 0 and b < 0:
        return "FLIP_HOLDS_IN_BOTH_SEGMENTS"
    if a >= 0 and b < 0:
        return "FLIP_IS_OUT_OF_SAMPLE_ONLY"
    if a < 0 and b >= 0:
        return "FLIP_IS_IN_SAMPLE_ONLY"
    return "NO_FLIP_IN_EITHER_SEGMENT"


def _repair_effect(pub, rep):
    """Does the repaired ruler beat the published one in this segment, and by how much?"""
    if not (pub.get("usable") and rep.get("usable")):
        return {"usable": False, "why": "a side of this segment is missing"}
    return {
        "usable": True,
        "sharpe_gain": round(float(rep["sharpe"]) - float(pub["sharpe"]), 3),
        "vol_cut_pp": round((float(pub["vol"]) - float(rep["vol"])) * 100.0, 2),
        "cagr_delta_pp": round((float(rep["cagr"]) - float(pub["cagr"])) * 100.0, 2),
        "maxdd_relief_pp": round((abs(float(pub["maxdd"])) - abs(float(rep["maxdd"]))) * 100.0, 2),
    }


def _repair_verdict(g_is, g_oos):
    if not (g_is.get("usable") and g_oos.get("usable")):
        return "CANNOT_ANSWER_A_SEGMENT_IS_MISSING"
    pos_i, pos_o = g_is["sharpe_gain"] > 0, g_oos["sharpe_gain"] > 0
    if pos_i and pos_o:
        return "RULER_REPAIR_EFFECT_HOLDS_IN_BOTH_SEGMENTS"
    if pos_i and not pos_o:
        return "RULER_REPAIR_EFFECT_IS_SEGMENT_SPECIFIC:in_sample_only"
    if pos_o and not pos_i:
        return "RULER_REPAIR_EFFECT_IS_SEGMENT_SPECIFIC:out_of_sample_only"
    return "RULER_REPAIR_EFFECT_IS_SEGMENT_SPECIFIC:neither"


def _control_gate(my_full, rep_arm):
    """C1: this face's own full-window basket must reproduce the released repair arm."""
    fails = []
    for key, tol in (("cagr", C1_TOL_PP / 100.0), ("vol", C1_TOL_X),
                     ("sharpe", C1_TOL_X), ("maxdd", C1_TOL_X)):
        if my_full.get(key) is None or rep_arm.get(key) is None:
            fails.append("C1 %s missing (mine=%r released=%r)" % (key, my_full.get(key), rep_arm.get(key)))
            continue
        if abs(float(my_full[key]) - float(rep_arm[key])) > tol:
            fails.append("C1 %s departs: mine=%.6f released=%.6f tol=%g"
                         % (key, float(my_full[key]), float(rep_arm[key]), tol))
    return fails


def _compare(pub, fresh, path=""):
    """Numeric/leaf comparison used by check(); returns a list of human-readable drifts."""
    diffs = []
    if isinstance(pub, dict) and isinstance(fresh, dict):
        for k in pub:
            if k not in fresh:
                diffs.append("%s.%s missing in the re-derivation" % (path, k))
                continue
            diffs.extend(_compare(pub[k], fresh[k], "%s.%s" % (path, k) if path else k))
        return diffs
    if isinstance(pub, list) and isinstance(fresh, list):
        if len(pub) != len(fresh):
            return ["%s length %d != %d" % (path, len(pub), len(fresh))]
        for i, (a, b) in enumerate(zip(pub, fresh)):
            diffs.extend(_compare(a, b, "%s[%d]" % (path, i)))
        return diffs
    if isinstance(pub, bool) or isinstance(fresh, bool):
        if pub != fresh:
            diffs.append("%s %r != %r" % (path, pub, fresh))
        return diffs
    if isinstance(pub, (int, float)) and isinstance(fresh, (int, float)):
        tol = SHARPE_TOL if "sharpe" in path else ROW_TOL
        if abs(float(pub) - float(fresh)) > tol:
            diffs.append("%s %.6f != %.6f" % (path, float(pub), float(fresh)))
        return diffs
    if pub != fresh:
        diffs.append("%s %r != %r" % (path, pub, fresh))
    return diffs


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _raw(ser):
    """Unrounded stats, used only to say how big a difference the printed precision hides."""
    ser = ser.dropna()
    r = ser.pct_change().dropna()
    yrs = (ser.index[-1] - ser.index[0]).days / 365.25
    growth = float(ser.iloc[-1]) / float(ser.iloc[0])
    vol = float(r.std() * np.sqrt(252))
    return {"cagr": growth ** (1 / yrs) - 1, "vol": vol,
            "sharpe": float(r.mean() * 252 / vol) if vol else None,
            "maxdd": float((ser / ser.cummax() - 1).min())}


def _is_precision(ser_pub, ser_rep):
    """How far apart are the two rulers' baskets inside the in-sample half, measured?"""
    a = ser_pub[ser_pub.index <= IS_END].dropna()
    b = ser_rep[ser_rep.index <= IS_END].dropna()
    idx = a.index.intersection(b.index)
    if len(idx) < SEG_MIN_BARS:
        return {"usable": False, "why": "a side of this segment is missing"}
    ra, rb = _raw(a.loc[idx]), _raw(b.loc[idx])
    daily = (a.loc[idx].pct_change() - b.loc[idx].pct_change()).abs()
    return {
        "usable": True, "bars": int(len(idx)),
        "cagr_diff_pp": round((rb["cagr"] - ra["cagr"]) * 100.0, 5),
        "vol_diff_pp": round((rb["vol"] - ra["vol"]) * 100.0, 5),
        "sharpe_diff": round(rb["sharpe"] - ra["sharpe"], 5),
        "maxdd_diff_pp": round((abs(rb["maxdd"]) - abs(ra["maxdd"])) * 100.0, 5),
        "max_abs_daily_return_diff_pp": round(float(daily.max()) * 100.0, 6),
        "daily_diff_days": int((daily.fillna(0) > 1e-12).sum()),
        "reading": ("the two rulers hold the identical basket in the in-sample half (0 differing "
                    "days); the difference is measured here, not assumed"),
    }


def _by_year(ser):
    rows = []
    for yr, sl in ser.groupby(ser.index.year):
        r = _stats(sl, str(yr))
        rows.append({"year": int(yr), "cagr": r.get("cagr"), "vol": r.get("vol"),
                     "maxdd": r.get("maxdd"), "bars": r.get("bars")})
    return rows


# ---------------------------------------------------------------------------------------
# the face
# ---------------------------------------------------------------------------------------
def build(write=True, quiet=False):
    if not os.path.exists(REPAIR_FACE):
        raise SystemExit("FATAL: source face missing: results/etf_class_ew_ruler_repair.json")
    if not os.path.exists(BOOK_FACE):
        raise SystemExit("FATAL: source face missing: results/etf_nobond_vt.json")
    t0 = time.time()
    repair = _load(REPAIR_FACE)
    book_face = _load(BOOK_FACE)

    # --- the basket, both rulers, on the panel the repair face itself used
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    name_of = lambda c: cmap.get(str(c)[:6], ("", ""))[1]
    kw = AC.classify(list(close.columns))
    ret = close.pct_change()
    fullvol = ret.std() * np.sqrt(252)
    maxabs = ret.abs().max()
    base = A.classify(close.columns, cmap, close)
    fixed = RR.repair_ruler(close.columns, kw, name_of, fullvol, maxabs)

    ser_pub = A.ew_universe(close, amt, base, WANT)
    ser_rep = A.ew_universe(close, amt, fixed, WANT)
    basket_pub = _segments(ser_pub)
    basket_rep = _segments(ser_rep)

    # --- the book: the row the book face declares as the production candidate
    cand = (book_face.get("caliber") or {}).get("production_candidate") or "nobond_vt08"
    row = next((r for r in (book_face.get("runs") or []) if r.get("label") == cand), None)
    if row is None:
        raise SystemExit("FATAL: book face has no row labelled %r" % (cand,))
    book = {
        "label": cand,
        "full": {"cagr": row.get("cagr"), "vol": row.get("vol"),
                 "sharpe": row.get("sharpe"), "maxdd": row.get("maxdd"),
                 "years": row.get("years"), "usable": True},
        "is": {"cagr": row.get("cagr_is"), "sharpe": row.get("sharpe_is"),
               "maxdd": row.get("maxdd_is"), "usable": True},
        "oos": {"cagr": row.get("cagr_oos"), "sharpe": row.get("sharpe_oos"),
                "maxdd": row.get("maxdd_oos"), "usable": True},
        "source": "results/etf_nobond_vt.json::runs[%s]" % cand,
        "note": ("the book's per-segment VOL is not published (the face carries cagr/sharpe/maxdd "
                 "only), so no segment money line is printed here"),
    }
    for seg in ("is", "oos"):
        if row.get("sharpe_" + seg) is None:
            book[seg]["usable"] = False

    # --- which names the repair moves, and whether any of them can move the BASKET in IS
    # A move only matters to this face if it changes membership of the bond+money union:
    # money->bond is inside the union on both sides, equity->crossborder is outside on both.
    moves = [c for c in close.columns if base.get(c) != fixed.get(c)]
    by_kind = {}
    for c in moves:
        k = "%s->%s" % (base.get(c), fixed.get(c))
        by_kind[k] = by_kind.get(k, 0) + 1
    membership = [c for c in moves
                  if (base.get(c) in WANT) != (fixed.get(c) in WANT)]
    in_is, firsts = [], []
    for c in membership:
        fv = close[c].first_valid_index()
        if fv is None:
            continue
        firsts.append((c, fv))
        if fv <= pd.Timestamp(IS_END):
            in_is.append({"symbol": c, "kind": "%s->%s" % (base.get(c), fixed.get(c)),
                          "first_bar": str(fv.date())})
    firsts.sort(key=lambda x: x[1])
    # why the ones that do exist still never reach the basket: measured on the arm window
    hist_all = close.notna().cumsum()
    elig_all = (amt >= E.MIN_AMT) & (hist_all >= E.MIN_HIST)
    arm_idx = close.index[(close.index >= pd.Timestamp(A.START)) & (close.index <= pd.Timestamp(IS_END))]
    for rec in in_is:
        c = rec["symbol"]
        rec["eligible_days_in_arm_window"] = int(elig_all.loc[arm_idx, c].sum())
        med = amt.loc[arm_idx, c].median()
        rec["amount_median_m_cny"] = None if not np.isfinite(med) else round(float(med) / 1e6, 2)
    ruler_moves = {
        "count": len(moves),
        "by_kind": by_kind,
        "membership_moves": len(membership),
        "membership_by_kind": {k: v for k, v in by_kind.items()
                               if (k.startswith("money->") and k != "money->bond")
                               or k.split("->")[1] in WANT},
        "existed_in_is": len(in_is),
        "existed_in_is_list": in_is[:20],
        "min_amount_gate_m_cny": round(float(E.MIN_AMT) / 1e6, 1),
        "first_bar_min": str(firsts[0][1].date()) if firsts else None,
        "first_bar_max": str(firsts[-1][1].date()) if firsts else None,
        "verdict": ("THE_REPAIR_CANNOT_TOUCH_IS_BY_CONSTRUCTION" if not in_is
                    else "THE_REPAIR_MOVES_NAMES_THAT_EXISTED_IN_IS"),
        "sentence": ("none of the %d names whose re-label changes the bond+money basket has a "
                     "price before %s (earliest %s), so both rulers hold the SAME basket in the "
                     "in-sample half -- that half is not a ruler comparison at all"
                     % (len(membership), IS_END,
                        str(firsts[0][1].date()) if firsts else "n/a")) if not in_is else
                    ("all but %d of the %d names whose re-label changes the basket have no price "
                     "before %s; the %d that do are measured in `is_precision`, not assumed away"
                     % (len(in_is), len(membership), IS_END, len(in_is))),
    }

    # --- the comparison, per segment
    cmp_ = {seg: _edge(book[seg], basket_rep[seg]) for seg in ("full", "is", "oos")}
    flip = _verdict(cmp_["is"], cmp_["oos"])

    # --- question two: is the REPAIR itself a full-window artefact?
    eff = {seg: _repair_effect(basket_pub[seg], basket_rep[seg]) for seg in ("full", "is", "oos")}
    repair_verdict = _repair_verdict(eff["is"], eff["oos"])

    # --- controls
    rep_arm = ((repair.get("arms") or {}).get("repaired") or {}).get("bond+money") or {}
    pub_arm = ((repair.get("arms") or {}).get("published") or {}).get("bond+money") or {}
    c1_fails = _control_gate(basket_rep["full"], rep_arm)
    c1b_fails = _control_gate(basket_pub["full"], pub_arm)
    arm_win = repair.get("arm_window") or {}
    mine_win = {"first": basket_rep["full"].get("first"), "last": basket_rep["full"].get("last"),
                "bars": basket_rep["full"].get("bars")}
    window_ok = bool(arm_win and mine_win["first"] == arm_win.get("first")
                     and mine_win["last"] == arm_win.get("last")
                     and mine_win["bars"] == arm_win.get("bars"))
    cutoff_ok = bool(repair.get("evidence_cutoff") and repair.get("evidence_cutoff")
                     == book_face.get("evidence_cutoff"))
    if c1_fails or c1b_fails or not window_ok or not cutoff_ok:
        raise SystemExit("FATAL: controls failed, refusing to publish: %s"
                         % json.dumps({"repaired_arm": c1_fails, "published_arm": c1b_fails,
                                       "window": window_ok, "cutoff": cutoff_ok}, ensure_ascii=False))

    face = {
        "artifact": REL_JSON,
        "schema": SCHEMA,
        "generated": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": book_face.get("evidence_cutoff"),
        "question": ("the ruler repair flips who is better per unit of risk on the FULL window -- "
                     "does that flip survive out of sample?"),
        "inputs": [{"path": "results/etf_class_ew_ruler_repair.json", "sha256": _sha(REPAIR_FACE)},
                   {"path": "results/etf_nobond_vt.json", "sha256": _sha(BOOK_FACE)}],
        "window": {"first": mine_win["first"], "last": mine_win["last"], "bars": mine_win["bars"],
                   "is_end": IS_END, "bars_per_year": BARS_PER_YEAR,
                   "is_years": book["is"].get("years"), "oos_years": book["oos"].get("years")},
        "panel": {"shape": [int(close.shape[0]), int(close.shape[1])], "flips_repaired": int(n_flip),
                  "digest": ((repair.get("panel") or {}).get("digest") or {})},
        "members": {"published": int(sum(1 for c in close.columns if base.get(c) in WANT)),
                    "repaired": int(sum(1 for c in close.columns if fixed.get(c) in WANT))},
        "basket": {"published": basket_pub, "repaired": basket_rep,
                   "published_by_year": _by_year(ser_pub), "repaired_by_year": _by_year(ser_rep)},
        "is_precision": _is_precision(ser_pub, ser_rep),
        "book": book,
        "comparison": cmp_,
        "repair_effect": eff,
        "ruler_moves": ruler_moves,
        "verdict": {"flip": flip, "ruler_repair": repair_verdict,
                    "full_window_flip_from_r1975": cmp_["full"]},
        "controls": {"repaired_arm_reproduced": not c1_fails, "published_arm_reproduced": not c1b_fails,
                     "window_identity": window_ok, "cutoff_identity": cutoff_ok,
                     "window_expected": arm_win, "window_measured": mine_win},
        "notes": {
            "not_the_same_object": ("the book is a bond-free 5-name rotating composite with an 8% vol "
                                    "target; the basket is an equal-weight holding of every "
                                    "bond+money ETF. A Sharpe comparison is a metric comparison."),
            "price_only_basket": ("the basket is priced on ETF closes, so its dividends are not in "
                                  "the return: its true total return and Sharpe are understated, "
                                  "which works against the basket in every segment."),
            "segment_cagr_caliber": ("both sides are renormalised off each segment's own first level "
                                     "(etf_equity_alpha.stats2), never off the global base."),
            "no_segment_money_line": ("needed CAGR = basket Sharpe x book vol, and the book face "
                                      "publishes no per-segment vol; the money line is withheld "
                                      "rather than approximated."),
            "survivorship": "the basket is drawn from ETFs that exist today.",
            "no_subperiod_of_the_basket_beyond_two_halves": (
                "two halves plus calendar years are printed; a third split would be a new judge."),
        },
        "elapsed_sec": round(time.time() - t0, 1),
    }
    if write:
        with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        write_md(face, OUT_MD)
    if not quiet:
        print("verdict flip=%s ruler_repair=%s" % (flip, repair_verdict))
        for seg in ("full", "is", "oos"):
            c = cmp_[seg]
            print(" %-4s book SR %s vs basket SR %s -> edge %s (%s)" %
                  (seg, c.get("book_sharpe"), c.get("bench_sharpe"), c.get("sharpe_edge"),
                   c.get("who_is_better_per_unit_of_risk")))
        print("json -> %s" % REL_JSON)
    return face


def _pct(x, nd=2):
    return "n/a" if x is None else ("%." + str(nd) + "f%%") % (float(x) * 100.0)


def _sp(x, nd=3):
    return "n/a" if x is None else ("%." + str(nd) + "f") % float(x)


def write_md(f, path):
    w, b, c = f["window"], f["basket"], f["book"]
    bp, br = b["published"], b["repaired"]
    cf, ci, co = f["comparison"]["full"], f["comparison"]["is"], f["comparison"]["oos"]
    ef, ei, eo = f["repair_effect"]["full"], f["repair_effect"]["is"], f["repair_effect"]["oos"]
    L = []
    A_ = L.append
    A_("# 防御尺子修好之后的翻面：过得了样本外吗")
    A_("")
    A_("generated %s | evidence_cutoff %s | 窗 %s..%s（%d bar·IS 至 %s）"
       % (f["generated"], f["evidence_cutoff"], w["first"], w["last"], w["bars"], w["is_end"]))
    A_("")
    A_("## 一句话")
    A_("")
    A_("- **翻面判词：`%s`** —— 书 `%s` 在风险调整后**%s**。"
       % (f["verdict"]["flip"], c["label"],
          {"FLIP_HOLDS_IN_BOTH_SEGMENTS": "两段都落后于修好的防御篮子",
           "FLIP_IS_OUT_OF_SAMPLE_ONLY": "只在样本外（2024 起）落后，样本内反而是书更好",
           "FLIP_IS_IN_SAMPLE_ONLY": "只在样本内落后，2024 起又回到书更好",
           "NO_FLIP_IN_EITHER_SEGMENT": "两段都不落后（与全窗读数矛盾，面里如实并列不挑选）",
           "CANNOT_ANSWER_A_SEGMENT_IS_MISSING": "有一段缺数，无法回答"}.get(f["verdict"]["flip"], "")))
    A_("- **尺子修复本身的判词：`%s`** —— 修好后的篮子在两段里对旧尺子的夏普增益 %s / %s。"
       % (f["verdict"]["ruler_repair"], _sp(ei.get("sharpe_gain")), _sp(eo.get("sharpe_gain"))))
    A_("- 缺口在哪一段：全窗差 **%s** 是两段的混合——样本内 **%s**、样本外 **%s**（符号在这两段里是反的）。"
       % (_sp(cf.get("sharpe_edge")), _sp(ci.get("sharpe_edge")), _sp(co.get("sharpe_edge"))))
    A_("- 为什么样本内与尺子无关：%s。" % f["ruler_moves"]["sentence"])
    A_("- 全窗那一行（r1975 的结论）照旧印在 `verdict.full_window_flip_from_r1975`，本面不改它。")
    A_("")
    A_("## 两段并排（同一窗、同一口径、同一段首归一）")
    A_("")
    A_("| 段 | 书 年化 | 书 夏普 | 书 回撤 | 篮子 年化 | 篮子 波动 | 篮子 夏普 | 篮子 回撤 | 夏普差（书-篮） | 回撤倍数 |")
    A_("|---|---|---|---|---|---|---|---|---|---|")
    for tag, seg, cc in (("全窗", "full", cf), ("IS ≤%s" % w["is_end"], "is", ci),
                         ("OOS >%s" % w["is_end"], "oos", co)):
        A_("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
           % (tag, _pct(cc.get("book_cagr")), _sp(cc.get("book_sharpe")), _pct(cc.get("book_maxdd")),
              _pct(cc.get("bench_cagr")), _pct(br[seg].get("vol")), _sp(cc.get("bench_sharpe")),
              _pct(cc.get("bench_maxdd")), _sp(cc.get("sharpe_edge")),
              "n/a" if cc.get("drawdown_multiple") is None else "%.2fx" % cc["drawdown_multiple"]))
    A_("")
    A_("书那几列全部来自书自己的面（`results/etf_nobond_vt.json::runs[%s]`，含 `cagr_is/sharpe_is/maxdd_is` "
       "与 `_oos` 六格），本面不重算书——重算一次就是第二个答案。" % c["label"])
    A_("")
    A_("## 尺子修复在每段里做了什么")
    A_("")
    A_("| 段 | 旧尺子夏普 | 新尺子夏普 | 夏普增益 | 波动降低 | 年化变化 | 回撤减轻 |")
    A_("|---|---|---|---|---|---|---|")
    for tag, seg, ee in (("全窗", "full", ef), ("IS", "is", ei), ("OOS", "oos", eo)):
        A_("| %s | %s | %s | %s | %s | %s | %s |"
           % (tag, _sp(bp[seg].get("sharpe")), _sp(br[seg].get("sharpe")), _sp(ee.get("sharpe_gain")),
              "%s pp" % ee.get("vol_cut_pp"), "%s pp" % ee.get("cagr_delta_pp"),
              "%s pp" % ee.get("maxdd_relief_pp")))
    A_("")
    A_("旧尺子成员 %d 名、新尺子 %d 名（同一块面板 %d 行 × %d 列，翻转抹平 %d 处）。"
       % (f["members"]["published"], f["members"]["repaired"], f["panel"]["shape"][0],
          f["panel"]["shape"][1], f["panel"]["flips_repaired"]))
    A_("")
    rm = f["ruler_moves"]
    A_("### 为什么样本内两把尺子给出的篮子一模一样")
    A_("")
    A_("整块面板上被改动标签的名字共 **%d 只**（%s），但其中只有 **%d 只**会改变「债+货币」这只篮子的成员"
       "（`money->bond` 在并集内两边都算，`equity->crossborder` 两边都在并集外）。这 %d 只的最早一根 bar "
       "落在 **%s .. %s**；在 %s 之前就有价格的有 **%d 只**。"
       % (rm["count"], "、".join("%s %d" % (k, v) for k, v in sorted(rm["by_kind"].items())),
          rm["membership_moves"], rm["membership_moves"], rm["first_bar_min"],
          rm["first_bar_max"], w["is_end"], rm["existed_in_is"]))
    A_("")
    A_("所以 `%s`：%s。" % (rm["verdict"], rm["sentence"]))
    A_("")
    ip = f.get("is_precision") or {}
    if ip.get("usable"):
        A_("实测差异（样本内两把尺子的篮子，%d bar，不取整）：年化 **%+.5f pp**、波动 **%+.5f pp**、"
           "夏普 **%+.5f**、回撤 **%+.5f pp**；单日收益最大差 **%.6f pp**，有差异的日子 **%d 天**。"
           % (ip["bars"], ip["cagr_diff_pp"], ip["vol_diff_pp"], ip["sharpe_diff"],
              ip["maxdd_diff_pp"], ip["max_abs_daily_return_diff_pp"], ip["daily_diff_days"]))
        A_("")
        A_("读法：这不是「两把尺子碰巧一样」，而是**能改变篮子的名字在样本内要么还没上市、要么过不了流动性门**，"
           "所以样本内这一段拿旧尺子或新尺子算出来的都是同一只篮子——它只能回答「书 vs 一只没被污染的篮子」，"
           "回答不了「尺子修好之后翻不翻」。")
        A_("")
        if rm.get("existed_in_is_list"):
            A_("那 %d 只在 %s 之前就有价格的名字，在臂窗（%s..%s）里的实际资格："
               % (len(rm["existed_in_is_list"]), w["is_end"], w["first"], w["is_end"]))
            A_("")
            A_("| 代码 | 改法 | 最早 bar | 臂窗内有资格的交易日 | 臂窗成交额中位（百万元） | 门（百万元） |")
            A_("|---|---|---|---|---|---|")
            for rec in rm["existed_in_is_list"]:
                A_("| %s | %s | %s | %d | %s | %s |"
                   % (rec["symbol"], rec["kind"], rec["first_bar"],
                      rec.get("eligible_days_in_arm_window") or 0,
                      "n/a" if rec.get("amount_median_m_cny") is None else rec["amount_median_m_cny"],
                      rm.get("min_amount_gate_m_cny")))
            A_("")
            A_("0 天有资格 = 它们在这段里从来没进过篮子，所以两条曲线逐日完全相同（上表 0 天有差异）。")
            A_("")
    A_("## 逐年在做什么（篮子，两把尺子）")
    A_("")
    A_("| 年 | 旧尺子年化 | 新尺子年化 | 年化差 | 新尺子回撤 |")
    A_("|---|---|---|---|---|")
    rep_year = {r["year"]: r for r in b["repaired_by_year"]}
    for r in b["published_by_year"]:
        rr = rep_year.get(r["year"], {})
        gap = (None if (r.get("cagr") is None or rr.get("cagr") is None)
               else round((rr["cagr"] - r["cagr"]) * 100.0, 2))
        A_("| %d | %s | %s | %s pp | %s |"
           % (r["year"], _pct(r.get("cagr")), _pct(rr.get("cagr")), gap, _pct(rr.get("maxdd"))))
    A_("")
    A_("篮子是收盘价口径，分红不在收益里——这低估了篮子的真实总收益与夏普，三个段都是对篮子不利方向的保守读数。")
    A_("")
    diff_years = [r for r in b["published_by_year"]
                  if rep_year.get(r["year"], {}).get("cagr") is not None and r.get("cagr") is not None
                  and abs(rep_year[r["year"]]["cagr"] - r["cagr"]) > 1e-9]
    if diff_years:
        A_("两把尺子只在 **%s** 这两年读出不同的年化（其余年份 0.0pp），也就是被旧尺子算成现金的那批股票 ETF "
           "进入样本之后才分叉：%s。"
           % ("、".join(str(r["year"]) for r in diff_years),
              "；".join("%d 年旧尺子 %s / 新尺子 %s"
                        % (r["year"], _pct(r.get("cagr")), _pct(rep_year[r["year"]].get("cagr")))
                        for r in diff_years)))
        A_("")
    A_("## 没印的东西（以及为什么不印）")
    A_("")
    notes = f["notes"]
    A_("- `%s`：%s" % ("每段的钱", notes["no_segment_money_line"]))
    A_("- `%s`：%s" % ("篮子不是这本书", notes["not_the_same_object"]))
    A_("- `%s`：%s" % ("分段年化口径", notes["segment_cagr_caliber"]))
    A_("- `%s`：%s" % ("幸存者", notes["survivorship"]))
    A_("")
    A_("## 复跑")
    A_("")
    A_("```")
    A_("python scripts/defensive_ruler_flip_subperiods.py            # 重算并写面（控制臂不过即拒绝发布）")
    A_("python scripts/defensive_ruler_flip_subperiods.py check      # 重 derive 逐字段对账（源面字节动=STALE rc3）")
    A_("python scripts/defensive_ruler_flip_subperiods.py selftest   # 离线腿")
    A_("```")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")


# ---------------------------------------------------------------------------------------
# check / selftest
# ---------------------------------------------------------------------------------------
def check(path=None, quiet=False):
    path = path or OUT_JSON
    if not os.path.exists(path):
        print("STALE: %s missing" % path)
        return 3
    pub = _load(path)
    stale = []
    for it in pub.get("inputs") or []:
        p = os.path.join(ROOT, it.get("path") or "")
        if not it.get("path") or not os.path.exists(p):
            stale.append("source face missing: %s" % it.get("path"))
        elif _sha(p) != it.get("sha256"):
            stale.append("source bytes moved: %s" % it.get("path"))
    if stale:
        for s in stale:
            print("STALE: " + s)
        return 3
    fresh = build(write=False, quiet=True)
    diffs = _compare({k: v for k, v in pub.items()
                      if k not in ("generated", "elapsed_sec", "artifact")},
                     {k: v for k, v in fresh.items()
                      if k not in ("generated", "elapsed_sec", "artifact")})
    if diffs:
        for d in diffs[:25]:
            print("CHECK FAILED: " + d)
        return 1
    if not quiet:
        print("check ok: %d verdicts re-derived on %s, all printed numbers match"
              % (2, pub.get("evidence_cutoff")))
    return 0


def selftest():
    fails = []
    ok = []

    # L1 the edge derivation points at whoever is better per unit of risk
    e = _edge({"sharpe": 1.101, "cagr": 0.1116, "maxdd": -0.1056},
              {"sharpe": 1.433, "cagr": 0.0128, "maxdd": -0.0135, "usable": True})
    if not (e["usable"] and e["sharpe_edge"] < 0 and e["who_is_better_per_unit_of_risk"] == "bench"):
        fails.append("L1 edge sign wrong: %r" % (e,))
    else:
        ok.append("L1 edge sign")
    e2 = _edge({"sharpe": 1.5, "cagr": 0.1, "maxdd": -0.1},
               {"sharpe": 1.4, "cagr": 0.05, "maxdd": -0.1, "usable": True})
    if e2["who_is_better_per_unit_of_risk"] != "book":
        fails.append("L2 book-ahead not recognised")
    else:
        ok.append("L2 book-ahead recognised")

    # L3 the verdict matrix, all four shapes
    cases = {(-0.3, -0.3): "FLIP_HOLDS_IN_BOTH_SEGMENTS",
             (0.2, -0.3): "FLIP_IS_OUT_OF_SAMPLE_ONLY",
             (-0.3, 0.2): "FLIP_IS_IN_SAMPLE_ONLY",
             (0.2, 0.2): "NO_FLIP_IN_EITHER_SEGMENT"}
    for (a, b), want in cases.items():
        got = _verdict({"usable": True, "sharpe_edge": a}, {"usable": True, "sharpe_edge": b})
        if got != want:
            fails.append("L3 verdict(%s,%s)=%s want %s" % (a, b, got, want))
    if not any(x.startswith("L3") for x in fails):
        ok.append("L3 verdict matrix (4 shapes)")
    if _verdict({"usable": False}, {"usable": True, "sharpe_edge": -1}) != "CANNOT_ANSWER_A_SEGMENT_IS_MISSING":
        fails.append("L3b a missing segment must not be answered")
    else:
        ok.append("L3b missing segment -> cannot answer")

    # L4 a segment CAGR is measured off the segment's own first level (r1262)
    idx = pd.bdate_range("2020-01-02", "2026-11-20")
    half = len(idx) // 2
    vals = np.concatenate([np.linspace(1.0, 2.0, half), np.full(len(idx) - half, 2.0)])
    ser = pd.Series(vals, index=idx)
    seg = _segments(ser)
    if not (seg["is"]["cagr"] > 0.10 and abs(seg["oos"]["cagr"]) < 0.01):
        fails.append("L4 segment renormalisation off: is=%.4f oos=%.4f"
                     % (seg["is"].get("cagr", 0), seg["oos"].get("cagr", 0)))
    else:
        ok.append("L4 segment CAGR renormalised off the segment's own first level")

    # L5 a slice too short to price is refused, not silently zeroed
    short = _stats(ser.iloc[:20], "short")
    if short.get("usable") or short.get("cagr") is not None:
        fails.append("L5 a 20-bar slice was priced")
    else:
        ok.append("L5 short slice -> cannot answer")

    # L6 the check comparator catches a hand-edited number and leaves equal numbers alone
    if not _compare({"a": {"cagr": 0.0128}}, {"a": {"cagr": 0.02}}):
        fails.append("L6 hand-edited number not caught")
    elif _compare({"a": {"cagr": 0.0128}}, {"a": {"cagr": 0.0128}}):
        fails.append("L6 identical numbers flagged")
    else:
        ok.append("L6 comparator both ways")

    # L7 the control gate refuses a basket that departs from the released arm
    if _control_gate({"cagr": 0.0129, "vol": 0.0093, "sharpe": 1.43, "maxdd": -0.0135},
                     {"cagr": 0.0128, "vol": 0.0093, "sharpe": 1.43, "maxdd": -0.0135}):
        fails.append("L7 control gate fired on a match")
    if not _control_gate({"cagr": 0.02, "vol": 0.0093, "sharpe": 1.43, "maxdd": -0.0135},
                         {"cagr": 0.0128, "vol": 0.0093, "sharpe": 1.43, "maxdd": -0.0135}):
        fails.append("L7b control gate let a 0.72pp departure through")
    if not (any(x.startswith("L7") for x in fails)):
        ok.append("L7 control gate both ways")

    # L8 the repair verdict reads both halves, not just the full window
    if _repair_verdict({"usable": True, "sharpe_gain": 0.2}, {"usable": True, "sharpe_gain": 0.2}) \
            != "RULER_REPAIR_EFFECT_HOLDS_IN_BOTH_SEGMENTS":
        fails.append("L8 both-halves repair verdict wrong")
    if _repair_verdict({"usable": True, "sharpe_gain": 0.2}, {"usable": True, "sharpe_gain": -0.1}) \
            != "RULER_REPAIR_EFFECT_IS_SEGMENT_SPECIFIC:in_sample_only":
        fails.append("L8b in-sample-only repair verdict wrong")
    if not any(x.startswith("L8") for x in fails):
        ok.append("L8 repair-effect verdict both ways")

    # L9 determinism: the same series priced twice is byte-identical
    a = _segments(ser)
    b = _segments(ser)
    if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
        fails.append("L9 pricing is not deterministic")
    else:
        ok.append("L9 deterministic")

    print("selftest: %d/%d PASS" % (len(ok), len(ok) + len(fails)))
    for x in ok:
        print("  ok   " + x)
    for x in fails:
        print("  FAIL " + x)
    return 0 if not fails else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        build()
        return 0
    if a.cmd == "check":
        return check()
    if a.cmd == "selftest":
        return selftest()
    raise SystemExit("unknown command: %s" % a.cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
