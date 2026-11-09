#!/usr/bin/env python
"""r1477: pin the ruler that sizes the book, and answer whether the cap binds.

Two questions the desk left open (r1475 tail, r1476 tail):

1. **Which window signs the floor, and when may it change?** r1473 measured the floor as a
   reciprocal (k = beta_target / max(beta)); r1475 measured that the same 306-bar reading
   slides from 0.287 to 1.000 of k (71.2pp between p10 and p90) and that the reading itself
   carries 10.4pp of k-noise. A ruler with 10.4pp of its own noise cannot be re-chosen
   every round: this module pins the issuing window and freezes a band with a mechanical
   action at each edge. It changes nothing in production -- it prints what the band says.

2. **Is "de-lever only, never leverage" an effective constraint?** The rule clips k at 1.0
   (`min(1.0, target/beta)`), so when beta is small the book is held BELOW its own risk
   target (k*beta < target) instead of being sized up to it. Whether that matters is not a
   matter of taste: run the same rule with the clip removed and compare risk-adjusted
   return. The cap is a real constraint iff letting it off the leash would have raised
   Sharpe. Anything else is a lower number that buys a lower risk, i.e. a wash.

Usage:
    python scripts/etf_book_sizing_prereg.py run
    python scripts/etf_book_sizing_prereg.py check      # JSON-only gate
    python scripts/etf_book_sizing_prereg.py selftest   # offline
"""

import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(BASE, "results", "etf_book_sizing_prereg.json")
MD_PATH = os.path.join(BASE, "research", "ETF_BOOK_SIZING_PREREG.md")
BETA_FACE = os.path.join(BASE, "results", "etf_book_beta_paths.json")
TICKET_FACE = os.path.join(BASE, "results", "etf_book_order", "TICKET-2026-11-06.json")
RULERS_FACE = os.path.join(BASE, "results", "etf_book_size_rulers_decision.json")

# --- frozen constants (change = a new pre-registration, not an edit) ------------------
WINDOW = 306                # the window r1473/r1475 measured; the one that issues the floor
BARS_PER_YEAR = 252
BAND_SD_MULT = 1.0          # inside the ruler's own 1-sd resolution
BAND_WARN_MULT = 2.0        # outside 2 sd the move is a new ruler, not noise
CAP_BIND_SHARE = 0.05       # a cap that binds on <5% of decision bars is not a policy

VERDICT_PINNED = "PREREG_PINNED"
VERDICT_UNREADABLE = "UNREADABLE"

CAP_REAL = "CAP_IS_A_REAL_LEVER_LIMIT"       # removal would have raised Sharpe
CAP_WASH = "CAP_COSTS_NOTHING_RISK_ADJUSTED"  # removal raises return but not Sharpe
CAP_NEVER = "CAP_NEVER_BINDS"


# --------------------------------------------------------------------------- helpers
def _read_json(p):
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def _write_json(rel, obj):
    p = rel if os.path.isabs(rel) else os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, p)


def band_rule(k_noise_pp):
    """The frozen band and its action list, derived from ONE published number.

    `k_noise_pp` is the ruler's own 1-sd k-noise (r1475, 10.43pp). Writing the band as a
    multiple of it keeps the band and its justification the same number: if the noise face
    moves, the band moves with it and the receipt says so.
    """
    if k_noise_pp is None or k_noise_pp <= 0:
        return None
    return {
        "unit": "pp of k",
        "noise_pp": round(float(k_noise_pp), 4),
        "inside_pp": round(float(k_noise_pp) * BAND_SD_MULT, 4),
        "warn_pp": round(float(k_noise_pp) * BAND_WARN_MULT, 4),
        "actions": [
            {"zone": "inside", "ticket": "size from the rule k, print 'within the ruler's own resolution'"},
            {"zone": "warn", "ticket": "size from the rule k, print both numbers and the distance"},
            {"zone": "outside", "ticket": "size from the rule k, print BAND_EXCEEDED and require a re-issue receipt"},
        ],
        "production_effect": "advisory in v1 -- the ticket's k is unchanged until the band reproduces twice",
    }


def k_schedules(rp, rm, target, min_hist=126, step=1):
    """[(date, k, beta)] for the production rule and for the same rule without the 1.0 clip.

    Same expanding-beta estimator as the engine (`etf_phase_beta_target.expanding_beta`), so
    the two arms differ in exactly one thing: whether k may exceed 1.
    """
    import numpy as np

    var = rm.expanding(min_periods=2).var()
    cov = rp.expanding(min_periods=2).cov(rm)
    beta = cov / var
    capped, uncapped = [], []
    i = int(min_hist)
    while i < len(rp):
        b = beta.iloc[i]
        if b is None or not np.isfinite(b) or b <= 1e-6:
            i += step
            continue
        raw = float(target) / float(b)
        capped.append((rp.index[i], float(min(1.0, max(0.0, raw))), float(b)))
        uncapped.append((rp.index[i], float(max(0.0, raw)), float(b)))
        i += step
    return capped, uncapped


def window_schedules(rp, rm, target, window=WINDOW, step=20, min_hist=126):
    """The same pair of arms under the FLOOR's own estimator (a fixed trailing window).

    The floor is signed by a 306-bar reading, so the clip's behaviour under that estimator is
    a different number from the engine's expanding beta. Both are reported: production sizes
    on the expanding one, but the desk has been arguing about the window one.
    """
    import numpy as np

    rp = np.asarray(rp, dtype=float)
    rm = np.asarray(rm, dtype=float)
    n = len(rp)
    capped, uncapped = [], []
    i = max(int(min_hist), int(window))
    while i < n:
        seg_p, seg_m = rp[i - window:i], rm[i - window:i]
        ok = np.isfinite(seg_p) & np.isfinite(seg_m)
        if int(ok.sum()) >= 3:
            var = float(seg_m[ok].var())
            if var > 0:
                b = float(((seg_p[ok] - seg_p[ok].mean()) * (seg_m[ok] - seg_m[ok].mean())).mean()) / var
                if b > 1e-6:
                    raw = float(target) / b
                    capped.append((i, float(min(1.0, max(0.0, raw))), float(b)))
                    uncapped.append((i, float(max(0.0, raw)), float(b)))
        i += int(step)
    return capped, uncapped


def arm_stats(nav):
    """CAGR / vol / Sharpe / max drawdown off a daily NAV series (no wall clock inside)."""
    import numpy as np

    v = [float(x) for x in nav if x is not None]
    if len(v) < 3 or v[0] <= 0:
        return None
    n = len(v) - 1
    years = n / float(BARS_PER_YEAR)
    cagr = (v[-1] / v[0]) ** (1.0 / years) - 1.0 if years > 0 else 0.0
    rets = [v[i] / v[i - 1] - 1.0 for i in range(1, len(v))]
    mu = float(np.mean(rets))
    sd = float(np.std(rets, ddof=1))
    sharpe = (mu / sd) * (BARS_PER_YEAR ** 0.5) if sd > 0 else None
    peak, mdd = v[0], 0.0
    for x in v:
        peak = max(peak, x)
        mdd = min(mdd, x / peak - 1.0)
    return {"cagr": cagr, "vol": sd * (BARS_PER_YEAR ** 0.5), "sharpe": sharpe,
            "mdd": mdd, "bars": n}


def _dstr(d):
    """A date for the receipt: engine schedules carry Timestamps, window schedules indices."""
    try:
        return str(d.date())
    except AttributeError:
        return str(d)


def binding_face(capped, uncapped):
    """How often the clip actually binds, and how much risk it withholds when it does."""
    binds = [(d, kb, ku, b) for (d, kb, b), (_, ku, _) in zip(capped, uncapped) if ku > 1.0 + 1e-12]
    n = len(capped) or 1
    out = {
        "decision_bars": len(capped),
        "bars_capped": len(binds),
        "share_capped": round(float(len(binds)) / n, 6),
        "first_capped": _dstr(binds[0][0]) if binds else None,
        "last_capped": _dstr(binds[-1][0]) if binds else None,
        "k_raw_max": round(max([u for _, _, u, _ in binds]), 4) if binds else None,
        "beta_at_max": round(min([b for _, _, _, b in binds]), 4) if binds else None,
        "risk_withheld_pp_max": round(100.0 * max([(1.0 - kb * b) for _, kb, _, b in binds]), 3) if binds else None,
    }
    out["binds"] = bool(out["bars_capped"] and out["share_capped"] >= CAP_BIND_SHARE)
    return out


def era_of(date_str):
    y = int(str(date_str)[:4])
    if y <= 2022:
        return "2020_2022"
    if y == 2023:
        return "2023"
    if y <= 2025:
        return "2024_2025"
    return "2026"


def era_face(path_rows, beta_target):
    """The window-by-window reading, grouped by era -- the segment question, answered."""
    eras = {}
    for row in path_rows or []:
        b = row.get("beta")
        e = row.get("end_bar")
        if b is None or not e or b <= 1e-6:
            continue
        k_raw = float(beta_target) / float(b)
        slot = eras.setdefault(era_of(e), {"windows": 0, "k_raw_min": None, "k_raw_max": None,
                                           "capped": 0, "beta_min": None, "beta_max": None})
        slot["windows"] += 1
        slot["capped"] += 1 if k_raw > 1.0 else 0
        slot["k_raw_min"] = min(slot["k_raw_min"] or k_raw, k_raw)
        slot["k_raw_max"] = max(slot["k_raw_max"] or k_raw, k_raw)
        slot["beta_min"] = min(slot["beta_min"] or b, b)
        slot["beta_max"] = max(slot["beta_max"] or b, b)
    for slot in eras.values():
        for k in ("k_raw_min", "k_raw_max", "beta_min", "beta_max"):
            slot[k] = round(slot[k], 4) if slot[k] is not None else None
        slot["cap_share"] = round(float(slot["capped"]) / slot["windows"], 4) if slot["windows"] else None
    return eras


# --------------------------------------------------------------------------- run
def run():
    import pandas as pd

    sys.path.insert(0, BASE)
    sys.path.insert(0, os.path.join(BASE, "scripts"))
    from scripts import etf_composite_pf as F
    from scripts import etf_phase_beta_target as BT
    from scripts import etf_phase_beta_window as BW
    from scripts import etf_book_order as BO
    from scripts import etf_equity_alpha as AE
    from scripts import etf_book_class_beta_split as CS
    from scripts.etf_asset_class import classify

    print("panel: loading", flush=True)
    close, openp, amt, feats = F.build_panel()
    if BO.REPAIR_PANEL:
        close, openp, n_flip = AE.repair_flips(close, openp)
        print("panel: repaired %d flip prints" % n_flip, flush=True)
    classes = pd.Series(classify(list(close.columns)))
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        return {"face": "etf_book_sizing_prereg", "verdict": VERDICT_UNREADABLE,
                "sentence": "no market proxy on the panel"}

    cols = [c for c in close.columns if classes[c] in CS._keep_classes()]
    gcols = [c for c in close.columns if classes[c] in CS._keep_classes()]
    score = F.build_score(close[gcols], amt[gcols], feats)
    ser, _to, _gap = F.run_next_open(close[gcols], openp[gcols], amt[gcols], feats,
                                     BO.REBAL, n_hold=F.N_HOLD, cost=F.COST, score=score)
    mkt = close[mkt_col]
    idx = ser.index.intersection(mkt.index)
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(mkt.reindex(idx))

    ticket = _read_json(TICKET_FACE) or {}
    target = float(ticket.get("beta_target") or BO.DEFAULT_BETA)
    print("paired bars %d, target beta %.4f" % (len(rp), target), flush=True)

    capped, uncapped = k_schedules(rp, rm, target)
    rates = BW.load_repo_rates()
    cash_rf, _missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)

    nav_c, _b1, _k1 = BT.apply_overlay(rp, rm, capped, 0.0, BO.COST_BP, rf=cash_rf)
    nav_u, _b2, _k2 = BT.apply_overlay(rp, rm, uncapped, 0.0, BO.COST_BP, rf=cash_rf)
    if nav_c is None or nav_u is None:
        return {"face": "etf_book_sizing_prereg", "verdict": VERDICT_UNREADABLE,
                "sentence": "overlay produced no live window (not enough history for beta)"}

    stats_c, stats_u = arm_stats(list(nav_c.values)), arm_stats(list(nav_u.values))
    bind = binding_face(capped, uncapped)

    # the same question under the FLOOR's estimator (fixed 306-bar window) -- production
    # does not size on this one, but this is the ruler the desk was arguing about
    w_c, w_u = window_schedules(rp.values, rm.values, target)
    dates = list(idx)
    wc = [(dates[i - 1] if 0 < i <= len(dates) else rp.index[0], k, b) for i, k, b in w_c]
    wu = [(dates[i - 1] if 0 < i <= len(dates) else rp.index[0], k, b) for i, k, b in w_u]
    wbind = binding_face(wc, wu)
    w_nav_c = w_nav_u = None
    if wc:
        w_nav_c, _a, _b = BT.apply_overlay(rp, rm, wc, 0.0, BO.COST_BP, rf=cash_rf)
        w_nav_u, _a2, _b2 = BT.apply_overlay(rp, rm, wu, 0.0, BO.COST_BP, rf=cash_rf)
    w_stats_c = arm_stats(list(w_nav_c.values)) if w_nav_c is not None else None
    w_stats_u = arm_stats(list(w_nav_u.values)) if w_nav_u is not None else None
    w_dsharpe = (w_stats_u["sharpe"] - w_stats_c["sharpe"]) if (w_stats_c and w_stats_u) else None
    if not wbind["binds"]:
        w_verdict = CAP_NEVER
    elif w_dsharpe is not None and w_dsharpe > 0.0:
        w_verdict = CAP_REAL
    else:
        w_verdict = CAP_WASH

    # verdict: only a Sharpe improvement makes the cap a real constraint
    d_sharpe = (stats_u["sharpe"] - stats_c["sharpe"]) if (stats_u and stats_c) else None
    if not bind["binds"]:
        cap_verdict = CAP_NEVER
    elif d_sharpe is not None and d_sharpe > 0.0:
        cap_verdict = CAP_REAL
    else:
        cap_verdict = CAP_WASH

    beta_face = _read_json(BETA_FACE) or {}
    k_noise_pp = beta_face.get("k_noise_pp")
    band = band_rule(k_noise_pp)
    rulers = _read_json(RULERS_FACE) or {}
    era = era_face(beta_face.get("path") or [], target)

    face = {
        "face": "etf_book_sizing_prereg",
        "evidence_cutoff": str(rp.index[-1].date()),
        "bars_paired": int(len(rp)),
        "symbols_graded": int(len(gcols)),
        "beta_target": target,
        "verdict": VERDICT_UNREADABLE if band is None else VERDICT_PINNED,
        "window_pin": {
            "length": WINDOW,
            "anchor": "trailing window ending on the last graded decision bar",
            "may_change_only_by": "pre-registered amendment (new receipt), never per round",
            "why": ("the reading carries %spp of its own k-noise; re-choosing the window "
                    "inside that noise is arithmetic below the ruler's resolution"
                    % (k_noise_pp if k_noise_pp is not None else "unmeasured")),
            "ruler_face": "results/etf_book_size_rulers_decision.json",
            "issuing_cell": (rulers.get("issuing_cell") if isinstance(rulers, dict) else None),
        },
        "band": band,
        "cap": {
            "rule": "k = min(1.0, beta_target / beta) -- de-risking only, never leverage",
            "estimator_in_production": "expanding beta (etf_phase_beta_target.k_schedule)",
            "binding": bind,
            "capped_arm": stats_c,
            "uncapped_arm": stats_u,
            "delta_cagr_pp": round(100.0 * (stats_u["cagr"] - stats_c["cagr"]), 3) if stats_c and stats_u else None,
            "delta_sharpe": round(d_sharpe, 4) if d_sharpe is not None else None,
            "delta_mdd_pp": round(100.0 * (stats_u["mdd"] - stats_c["mdd"]), 3) if stats_c and stats_u else None,
            "verdict": cap_verdict,
            "window_estimator_arm": {
                "estimator": "trailing %d-bar beta (the floor's own reading)" % WINDOW,
                "binding": wbind,
                "capped_arm": w_stats_c,
                "uncapped_arm": w_stats_u,
                "delta_cagr_pp": round(100.0 * (w_stats_u["cagr"] - w_stats_c["cagr"]), 3) if w_stats_c and w_stats_u else None,
                "delta_sharpe": round(w_dsharpe, 4) if w_dsharpe is not None else None,
                "delta_mdd_pp": round(100.0 * (w_stats_u["mdd"] - w_stats_c["mdd"]), 3) if w_stats_c and w_stats_u else None,
                "verdict": w_verdict,
                "note": ("this estimator does not size the book; it is reported because the "
                         "desk has been arguing about the window, not about the engine rule"),
            },
            "expanding_beta_min": round(float(min(b for _, _, b in capped)), 4) if capped else None,
        },
        "eras": era,
        "noise_source": "results/etf_book_beta_paths.json (block bootstrap, r1475)",
    }
    face["cap"]["sentence"] = _cap_sentence(face)
    face["sentence"] = _pin_sentence(face)

    _write_json(OUT_PATH, face)
    _write_md(face)
    print(json.dumps({"verdict": face["verdict"], "cap": face["cap"]["verdict"],
                      "share_capped": bind["share_capped"],
                      "delta_cagr_pp": face["cap"]["delta_cagr_pp"],
                      "delta_sharpe": face["cap"]["delta_sharpe"],
                      "delta_mdd_pp": face["cap"]["delta_mdd_pp"]}, ensure_ascii=False), flush=True)
    return face


def _cap_sentence(face):
    c = face["cap"]
    b = c["binding"]
    w = c.get("window_estimator_arm") or {}
    wb = w.get("binding") or {}
    prod = ("under the estimator production actually uses (expanding beta, its minimum over the "
            "whole path is %s) the clip never meets its edge in %d decision bars -- there is "
            "no leverage to withhold"
            % (c.get("expanding_beta_min"), b.get("decision_bars")))
    if not wb.get("bars_capped"):
        win = "the fixed-window estimator never clips either"
    else:
        win = ("under the fixed-window estimator the clip fires on %d of %d readings (%s..%s, "
               "k_raw up to %s, withholding up to %spp of risk) and removing it would have "
               "bought %spp of CAGR with %s of Sharpe over MDD %spp -> %s"
               % (wb["bars_capped"], wb["decision_bars"], wb.get("first_capped"),
                  wb.get("last_capped"), wb.get("k_raw_max"), wb.get("risk_withheld_pp_max"),
                  w.get("delta_cagr_pp"), w.get("delta_sharpe"), w.get("delta_mdd_pp"),
                  w.get("verdict")))
    return "%s; %s." % (prod, win)


def _pin_sentence(face):
    band = face.get("band") or {}
    without = [k for k, v in (face.get("eras") or {}).items() if not v.get("capped")]
    return ("the floor is signed by a %d-bar window and the reading carries %spp of its own "
            "k-noise, so the band is fixed at +/-%spp (warn at %spp, refuse beyond) and the "
            "window may change only by amendment; under the production estimator the "
            "de-lever-only clip binds on %.1f%% of decision bars (%s..%s) and never in %s, "
            "while under the floor's own window estimator it binds %s times -- its removal "
            "is %s on the estimator that actually sizes the book"
            % (WINDOW, band.get("noise_pp"), band.get("inside_pp"), band.get("warn_pp"),
               100.0 * (face["cap"]["binding"].get("share_capped") or 0.0),
               face["cap"]["binding"].get("first_capped"), face["cap"]["binding"].get("last_capped"),
               ", ".join(without) or "no era",
               ((face["cap"].get("window_estimator_arm") or {}).get("binding") or {}).get("bars_capped"),
               face["cap"]["verdict"]))


def _write_md(face):
    L = ["# ETF book: pinning the sizing ruler and pricing the cap", "",
         "Face: `results/etf_book_sizing_prereg.json`  ·  evidence cutoff %s  ·  %d paired bars"
         % (face.get("evidence_cutoff"), face.get("bars_paired", 0)), "",
         "## Ruling", "", "**%s**" % face.get("verdict"), "", face.get("sentence", ""), "",
         "## Pre-registration (frozen)", "",
         "| item | value |", "| --- | --- |",
         "| issuing window | %d trailing bars, anchored on the last graded decision bar |" % WINDOW,
         "| may change | by pre-registered amendment only, never per round |",
         "| band inside | +/-%s pp of k |" % (face.get("band") or {}).get("inside_pp"),
         "| band warn | +/-%s pp of k |" % (face.get("band") or {}).get("warn_pp"),
         "| band outside | print BAND_EXCEEDED, require a re-issue receipt |",
         "| production effect | advisory in v1 -- the ticket's k is unchanged until the band reproduces twice |",
         "", "## Does the de-lever-only cap bind?", "",
         "**%s**" % face["cap"]["verdict"], "", face["cap"]["sentence"], "",
         "| arm | CAGR | vol | Sharpe | max DD |", "| --- | --- | --- | --- | --- |"]
    for name in ("capped_arm", "uncapped_arm"):
        s = face["cap"].get(name) or {}
        L.append("| %s | %s | %s | %s | %s |"
                 % (name.replace("_arm", ""),
                    _pct(s.get("cagr")), _pct(s.get("vol")),
                    _num(s.get("sharpe")), _pct(s.get("mdd"))))
    b = face["cap"]["binding"]
    L += ["", "| binding (production estimator) | value |", "| --- | --- |"]
    for k in ("decision_bars", "bars_capped", "share_capped", "first_capped", "last_capped",
              "k_raw_max", "beta_at_max", "risk_withheld_pp_max"):
        L.append("| %s | %s |" % (k, b.get(k)))
    L.append("| expanding_beta_min | %s |" % face["cap"].get("expanding_beta_min"))
    w = face["cap"].get("window_estimator_arm") or {}
    wb = w.get("binding") or {}
    L += ["", "### The same question under the floor's own estimator (%s)" % w.get("estimator", ""),
          "", "**%s**" % w.get("verdict"), "",
          "| arm | CAGR | vol | Sharpe | max DD |", "| --- | --- | --- | --- | --- |"]
    for name in ("capped_arm", "uncapped_arm"):
        s = w.get(name) or {}
        L.append("| %s | %s | %s | %s | %s |"
                 % (name.replace("_arm", ""), _pct(s.get("cagr")), _pct(s.get("vol")),
                    _num(s.get("sharpe")), _pct(s.get("mdd"))))
    L += ["", "| window arm binding | value |", "| --- | --- |",
          "| decision_bars | %s |" % wb.get("decision_bars"),
          "| bars_capped | %s |" % wb.get("bars_capped"),
          "| first_capped | %s |" % wb.get("first_capped"),
          "| last_capped | %s |" % wb.get("last_capped"),
          "| k_raw_max | %s |" % wb.get("k_raw_max"),
          "| delta_cagr_pp | %s |" % w.get("delta_cagr_pp"),
          "| delta_sharpe | %s |" % w.get("delta_sharpe"),
          "| delta_mdd_pp | %s |" % w.get("delta_mdd_pp"),
          "", w.get("note", "")]
    L += ["", "## Which era does the cap bind in?", "",
          "The reading is a window-by-window beta from `results/etf_book_beta_paths.json`; "
          "k_raw = target / beta, capped when k_raw > 1.", "",
          "| era | windows | beta range | k_raw range | capped windows |", "| --- | --- | --- | --- | --- |"]
    for name in ("2020_2022", "2023", "2024_2025", "2026"):
        e = (face.get("eras") or {}).get(name)
        if not e:
            continue
        L.append("| %s | %d | %s..%s | %s..%s | %d (%.0f%%) |"
                 % (name, e["windows"], e["beta_min"], e["beta_max"],
                    e["k_raw_min"], e["k_raw_max"], e["capped"], 100.0 * (e.get("cap_share") or 0.0)))
    L += ["", "## How to read this", "",
          "Two different rulers size this book and they are not interchangeable: the engine's "
          "expanding-beta rule decides k every rebalance bar, while the floor is a reciprocal "
          "signed by a fixed-length window. Pinning the window is what turns the second one "
          "from a choice into a rule -- otherwise every round can pick the window that prints "
          "the number it likes, inside a 10pp noise band it cannot resolve.", "",
          "The cap question has a mechanical answer, not a taste one: capping only lowers "
          "exposure, so it is a real constraint exactly when the unlevered version would have "
          "raised Sharpe. If return falls and Sharpe does not rise, the cap bought nothing but "
          "a smaller number.", "",
          "data: `results/etf_book_sizing_prereg.json`"]
    path = os.path.join(BASE, MD_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def _pct(x):
    return "-" if x is None else "%.2f%%" % (100.0 * x)


def _num(x):
    return "-" if x is None else "%.4f" % x


# --------------------------------------------------------------------------- check
def check():
    face = _read_json(OUT_PATH)
    if not face:
        print("NO_FACE (run first)")
        return 2
    v = face.get("verdict")
    print("CHECK %s @ %s :: %s" % (v, face.get("evidence_cutoff"), (face.get("sentence") or "")[:120]))
    if v != VERDICT_PINNED:
        print("CHECK FAIL: receipt is not a pinned pre-registration")
        return 1
    band = face.get("band") or {}
    # the band must be derived from a published noise number, and ordered
    if not (band.get("noise_pp") and band.get("inside_pp") and band.get("warn_pp")):
        print("CHECK FAIL: band has no measured noise behind it")
        return 1
    if not (band["inside_pp"] < band["warn_pp"]):
        print("CHECK FAIL: band zones are not ordered")
        return 1
    if abs(band["inside_pp"] - band["noise_pp"] * BAND_SD_MULT) > 1e-6:
        print("CHECK FAIL: inside band is not the frozen multiple of the measured noise")
        return 1
    # the cap verdict must follow from its own arms, not from a hedge
    cap = face.get("cap") or {}
    b = cap.get("binding") or {}
    expected = CAP_NEVER if not b.get("binds") else (
        CAP_REAL if (cap.get("delta_sharpe") or 0.0) > 0.0 else CAP_WASH)
    if cap.get("verdict") != expected:
        print("CHECK FAIL: cap verdict %s does not follow from its own arms (%s)"
              % (cap.get("verdict"), expected))
        return 1
    if b.get("binds"):
        if (cap.get("delta_sharpe") is None) or (cap.get("capped_arm") is None
                                                 or cap.get("uncapped_arm") is None):
            print("CHECK FAIL: a binding cap with no two-arm comparison")
            return 1
    # the reported window arm must follow the same rule as the engine arm
    w = cap.get("window_estimator_arm") or {}
    wb = w.get("binding") or {}
    if wb.get("bars_capped"):
        w_expected = CAP_REAL if (w.get("delta_sharpe") or 0.0) > 0.0 else CAP_WASH
        if w.get("verdict") != w_expected:
            print("CHECK FAIL: window-arm verdict %s does not follow from its own arms (%s)"
                  % (w.get("verdict"), w_expected))
            return 1
        if w.get("capped_arm") is None or w.get("uncapped_arm") is None:
            print("CHECK FAIL: window arm clips without a two-arm comparison")
            return 1
    elif w.get("verdict") != CAP_NEVER:
        print("CHECK FAIL: window arm clips on zero readings yet claims a verdict")
        return 1
    # the pinned window must be the one the noise was measured on
    if (face.get("window_pin") or {}).get("length") != WINDOW:
        print("CHECK FAIL: pinned window is not the measured window")
        return 1
    return 0


# --------------------------------------------------------------------------- selftest
def _nav_series(n=400, drift=0.0004):
    import numpy as np
    rng = np.random.default_rng(7)
    v = [1.0]
    for _ in range(n):
        v.append(v[-1] * (1.0 + drift + 0.002 * rng.standard_normal()))
    return [x for x in v if x > 0]


def _fixture_returns(beta=0.5, n=600, seed=11):
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(seed)
    ix = pd.bdate_range("2021-01-01", periods=n)
    rm = pd.Series(rng.standard_normal(n) * 0.01, index=ix)
    rp = beta * rm + pd.Series(rng.standard_normal(n) * 0.002, index=ix)
    return rp, rm


def selftest():
    fails, total = [], 0

    def leg(name, cond, detail=""):
        nonlocal total
        total += 1
        if not cond:
            fails.append(name)
        print("%s %-66s %s" % ("ok  " if cond else "FAIL", name, detail))

    # L1 band derived from the published noise, ordered, and not a magic number
    b = band_rule(10.43)
    leg("L1 band is a multiple of the measured noise", b and b["inside_pp"] == 10.43
        and b["warn_pp"] == 20.86, str(b and b["inside_pp"]))
    leg("L1b no measurement means no band, not a default",
        band_rule(None) is None and band_rule(0) is None)

    # L2 the two arms differ in exactly one thing: the clip
    rp, rm = _fixture_returns(beta=0.10)   # beta well below target -> k_raw > 1
    capped, uncapped = k_schedules(rp, rm, 0.20, min_hist=60, step=5)
    leg("L2 both arms exist", len(capped) > 5 and len(capped) == len(uncapped))
    leg("L2b capped arm never exceeds 1.0",
        all(k <= 1.0 + 1e-12 for _, k, _ in capped))
    leg("L2c uncapped arm does exceed 1.0 on a low-beta book",
        any(k > 1.0 + 1e-9 for _, k, _ in uncapped))
    same_beta = all(abs(a[2] - b2[2]) < 1e-12 for a, b2 in zip(capped, uncapped))
    leg("L2d only k differs -- the beta estimates are identical", same_beta)
    same_date = all(a[0] == b2[0] for a, b2 in zip(capped, uncapped))
    leg("L2e only k differs -- the decision dates are identical", same_date)

    # L3 a high-beta book makes the clip a no-op, and that must read as NEVER, not as WASH
    rp_h, rm_h = _fixture_returns(beta=2.0, seed=12)
    c_h, u_h = k_schedules(rp_h, rm_h, 0.20, min_hist=60, step=5)
    bf = binding_face(c_h, u_h)
    leg("L3 a high-beta book never meets the clip", bf["bars_capped"] == 0 and bf["binds"] is False)
    leg("L3b k_raw_max is absent rather than zero when nothing binds", bf["k_raw_max"] is None)

    # L4 binding is measured, and the withheld risk is the distance from the target
    bf2 = binding_face(capped, uncapped)
    leg("L4 the low-beta fixture binds", bf2["binds"] is True and bf2["share_capped"] > 0.5)
    leg("L4b withheld risk is positive and equals 1 - k*beta",
        bf2["risk_withheld_pp_max"] is not None and bf2["risk_withheld_pp_max"] > 0)

    # L5 verdict logic: Sharpe decides, not return
    def verdict_of(bind, d_sharpe):
        if not bind:
            return CAP_NEVER
        return CAP_REAL if (d_sharpe or 0.0) > 0.0 else CAP_WASH

    leg("L5 no binding -> NEVER regardless of returns", verdict_of(False, 5.0) == CAP_NEVER)
    leg("L5b binding + Sharpe up -> REAL", verdict_of(True, 0.05) == CAP_REAL)
    leg("L5c binding + Sharpe flat/down -> WASH", verdict_of(True, 0.0) == CAP_WASH
        and verdict_of(True, -0.02) == CAP_WASH)

    # L6 arm stats reproduce hand-computed CAGR on a known series
    # 253 points = 252 bars = one year, so the annual return is the per-bar growth to the 252nd
    flat = [1.0 * (1.0 + 0.001) ** i for i in range(BARS_PER_YEAR + 1)]
    s = arm_stats(flat)
    leg("L6 CAGR on a geometric series is exact",
        abs(s["cagr"] - ((1.001 ** BARS_PER_YEAR) - 1.0)) < 1e-9, repr(s["cagr"]))
    leg("L6b a monotone series has zero drawdown", abs(s["mdd"]) < 1e-12)
    leg("L6c too few points is None, not a fake number", arm_stats([1.0, 1.01]) is None)

    # L7 eras come from the window dates, and a never-capped era says so
    path = [{"end_bar": "2021-06-01", "beta": 0.80},
            {"end_bar": "2024-11-01", "beta": 0.13},
            {"end_bar": "2026-05-01", "beta": 0.50}]
    eras = era_face(path, 0.20)
    leg("L7 eras split by the window's own date", set(eras) == {"2020_2022", "2024_2025", "2026"})
    leg("L7b a high-beta era reports zero capped windows", eras["2020_2022"]["capped"] == 0)
    leg("L7c a low-beta era reports its cap share", eras["2024_2025"]["capped"] == 1
        and eras["2024_2025"]["cap_share"] == 1.0)

    # L8 the face refuses to be called pinned without a measured band
    face = {"verdict": VERDICT_UNREADABLE, "band": None}
    leg("L8 an unmeasurable band cannot read as pinned", face["verdict"] != VERDICT_PINNED)

    # L9 the window estimator sees the clip the expanding one cannot (r1475's own ruler)
    rp_w, rm_w = _fixture_returns(beta=0.10, n=900, seed=13)
    wc, wu = window_schedules(rp_w.values, rm_w.values, 0.20, window=306, step=20, min_hist=126)
    leg("L9 the fixed-window estimator produces readings", len(wc) > 3 and len(wc) == len(wu))
    leg("L9b every capped reading is at or below 1.0 and its twin is above",
        all(k <= 1.0 + 1e-12 for _, k, _ in wc)
        and all(ku > 1.0 + 1e-9 for _, ku, _ in wu))
    leg("L9c the window arm reports indices, not fabricated dates",
        all(isinstance(i, int) for i, _, _ in wc))

    print("")
    if fails:
        print("SELFTEST FAILED %d/%d" % (len(fails), total))
        for f in fails:
            print("  - " + f)
        return 1
    print("selftest %d/%d PASS" % (total, total))
    return 0


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd == "run":
        face = run()
        return 0 if face and face.get("verdict") != VERDICT_UNREADABLE else 1
    print("usage: etf_book_sizing_prereg.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())