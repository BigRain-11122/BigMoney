#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cash_shelf_flip_census -- how far does r2046's flip repair reach?

WHY THIS FACE EXISTS
--------------------
r2046 (`cash_shelf_year_by_year`) found one *sub-threshold* quote flip on one shelf:
511360 closed 1.047% lower on 2023-09-08 and was back within 4.4bp of the pre-drop price
two sessions later.  Neither published repair catches it -- r2041's rule is a 35% single
bar (`etf_equity_alpha.repair_flips`), and the money-ETF reader zeroes drops deeper than
50bp as share consolidations while *keeping* the rebound.  Zeroing the drop and the
rebound together moved that shelf's window CAGR by ~0.165pp/py, which r2046 printed and
priced into the wait.

r2046 published that as a by-product of one shelf.  The five-shelf table everything since
r2042 rests on is drawn from a family of 111 money / bond / convertible ETFs.  The question
that decides whether r2046's repair is a *reading* or a *one-off* is therefore not "how many
shelves have this shape" -- it is "on which shelves is a -50bp print actually abnormal".

That second half matters because the frozen flip geometry is an absolute one: a single bar
down 50bp followed by a return within 5bp of the pre-drop price.  For a money ETF whose
daily standard deviation is 4bp, that is a 12-sigma print -- a quote flip.  For a convertible
ETF whose daily standard deviation is 65bp, the same shape is an ordinary Tuesday.  Applying
the geometry alone would "repair" 23 normal moves on 511380 and move its annualised return
by more than a percentage point in the *wrong* direction.  So this face keeps the geometry
exactly as r2046 froze it, and adds the one thing that was missing: each print is measured
against its own instrument's daily standard deviation.

THE QUESTION (frozen before the first run)
------------------------------------------
Across every money / bond / convertible ETF in the panel: which of them carry a print that
is both (a) the r2046 flip shape and (b) large against that instrument's own daily
movement; what does neutralising *those* do to each instrument's annualised return; and
does the repair r2046 published stay inside the one shelf that earned it?

RULER (nothing re-decided here, one thing added)
------------------------------------------------
* window, panel, cost caliber     -- r2041 / r2046 (`cb_parking_shelf_at_size`,
                                     `etf_composite_pf.build_panel`)
* 35% repair                        -- `etf_equity_alpha.repair_flips`, applied to the whole
                                     panel first, so this face only sees what it leaves
* flip shape and both-bars-at-zero  -- r2046's own constants and `neutralise`, imported
* class assignment                  -- `etf_equity_alpha.classify`
* bars per year                     -- the instrument's own bar count
* **sigma of a pair** (added here)  -- |drop_bp| / (that instrument's daily return standard
                                     deviation in bp, same window, same bar count)
* **SIGMA_MIN = 4** (added here)    -- a print counts as a quote anomaly only when it is at
                                     least four of the instrument's own daily standard
                                     deviations.  This is not a significance test; it is the
                                     readability floor that separates "this print is not a
                                     market move for this instrument" from "this instrument
                                     moved".  Chosen before the first run, printed with every
                                     pair so a reader can move it.

This face charges **no** entry cost: it describes the quote series, not a trade.

VERDICTS (mechanical)
---------------------
* NO_PAIR_ANYWHERE                    -- nothing carries even the geometry; nothing to repair.
* THE_ANOMALY_IS_CONFINED_TO_ONE_SHELF -- exactly one instrument carries an anomaly (>= SIGMA_MIN).
* ANOMALIES_ARE_NAMED_NOT_SYSTEMATIC  -- more than one, but under a quarter of the priced
                                        universe: every one is listed.
* ANOMALIES_ARE_SYSTEMATIC            -- a quarter or more of the priced universe carries one.
Tags, printed beside the verdict rather than folded into it:
* THE_GEOMETRY_OVERREACHES  -- the shape fires on at least twice as many instruments as the
                               sigma ruler does: the absolute geometry alone would repair
                               normal moves, so the repair must not be applied by shape only.
* R2046_REPAIR_IS_CONFIRMED_BY_ITS_OWN_SIGMA -- every pair r2046 neutralised is anomalous on
                               this ruler too, so that repair was a repair.
* R2046_REPAIRS_A_NORMAL_MOVE -- one of r2046's neutralised pairs is not anomalous: that
                               shelf's published number is short by the repair.
* THE_FLIP_OUTWEIGHS_THE_MARGIN -- on a shelf r2046 prices, the anomaly, converted into
                               trading days of that shelf's own extra, exceeds the margin
                               r2046 left against the budget.
* MONEY_CLASS_MATCHES_A_FACTOR_FUND -- some row is class=money, is not a money-market fund
                               by its own name, and has a wide sigma: the classifier's 现金
                               keyword matched a free-cash-flow equity ETF.  Labelled, kept
                               out of the verdicts.
* MONEY_SERIES_CARRIES_UNCAUGHT_JUMPS -- some row is a money-market fund by name yet jumps
                               at a wide daily sigma: its series carries reprints neither
                               repair rule catches.  Labelled, kept out of the verdicts.

Usage:
    python scripts/cash_shelf_flip_census.py run
    python scripts/cash_shelf_flip_census.py --check
    python scripts/cash_shelf_flip_census.py --selftest
"""

from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import cb_parking_shelf_at_size as SS  # noqa: E402  (window, panel, cost caliber)
import etf_book_cash_vehicle as CV  # noqa: E402  (money ETF share resets)
import etf_composite_pf as E  # noqa: E402  (ETF panel)
import etf_equity_alpha as A  # noqa: E402  (35% repair, class map)
import cash_shelf_year_by_year as YY  # noqa: E402  (flip shape, neutralise)

FACE = "results/cash_shelf_flip_census.json"
DOC = "research/CASH_SHELF_FLIP_CENSUS.md"
YEAR_FACE = YY.FACE               # r2046 -- the five priced shelves and their margins
UNIVERSE_CLASSES = ("money", "bond", "convertible")
MIN_BARS = 250                    # below this the annualisation is noise; the row is unpriced
SIGMA_MIN = 4.0                   # see docstring: readability floor, not a significance test
SYSTEMATIC_SHARE = 0.25           # verdict line, chosen before the first run
GEOMETRY_OVERREACH = 2.0          # shape fires on >= 2x as many instruments as sigma does
MONEY_SIGMA_WIDE_BP = 25.0        # a money ETF's daily sigma should be 1-2bp
PRICE_DEC = 6

MARK_BEGIN = "<!-- FLIP-CENSUS:BEGIN -->"
MARK_END = "<!-- FLIP-CENSUS:END -->"


# --------------------------------------------------------------------- io helpers

def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(path):
    with io.open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return json.load(f)


def _content_sha(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# --------------------------------------------------------------------- measurement

def cagr_from_rets(rets):
    """Annualise a per-bar return series on its own bar count (r2045/r2046 ruler)."""
    rets = rets.dropna()
    if len(rets) < 2:
        return None
    level = float(np.cumprod(1.0 + rets.to_numpy())[-1])
    if level <= 0:
        return None
    bpy = YY.bars_per_year(rets)
    if not bpy:
        return None
    return (level ** (bpy / len(rets)) - 1.0) * 100.0


def window_rets(px, klass, start, end, code=None):
    """Per-bar returns of one instrument inside the window, plus its money-reset days.

    Money ETFs get their share consolidations taken out first (r2041 caliber); every other
    class is a plain close-to-close series.  No entry cost is charged -- see the docstring.
    The reset list is returned for disclosure only: a reset that comes straight back is
    exactly the shape this face is looking for, so it is *not* excluded here.
    """
    px = px.dropna()
    px = px[(px.index >= pd.Timestamp(start)) & (px.index <= pd.Timestamp(end))]
    resets = []
    if klass == "money":
        try:
            base = CV.load_etf(code)
            base = base[(base.index >= pd.Timestamp(start)) & (base.index <= pd.Timestamp(end))]
            if base.dropna().shape[0] >= 40:
                rets, resets = CV.consolidation_returns(base)
                px = base
            else:
                rets = px.pct_change()
        except Exception:
            rets = px.pct_change()
    else:
        rets = px.pct_change()
    return px, rets, resets


def sigma_bp(rets):
    """The instrument's own daily return standard deviation in bp (window, own bars)."""
    r = rets.dropna()
    if len(r) < 2:
        return None
    s = float(r.std())
    return None if not np.isfinite(s) or s <= 0 else s * 1e4


def class_confidence(row, name):
    """Whether the row's class can be trusted for this reading.

    `etf_equity_alpha.classify` decides money-ness from the fund's *name* first, and its
    keyword list contains 现金 -- which also matches every free-cash-flow equity ETF
    (现金流ETF).  Those arrive here as class=money with a 60bp daily sigma.  Rather than
    re-decide the classification (that belongs to the shared classifier, not to this face),
    the row is labelled and kept out of the verdicts:

      suspect_class  -- class=money, sigma over the wide line, and the fund's name does not
                        call itself a money-market fund: the name rule matched another word.
      suspect_series -- class=money, name says 货币, yet its own daily sigma is over the wide
                        line: the series carries jumps the two repair rules do not catch,
                        so a reading taken off it is not about the fund.
    """
    if row.get("class") != "money":
        return "ok"
    sig = row.get("sigma_bp") or 0.0
    if sig <= MONEY_SIGMA_WIDE_BP:
        return "ok"
    # 现金流 is what the classifier's 现金 keyword actually matched: those are equity
    # factor funds, not cash.  Anything else that calls itself a money fund and still
    # jumps this wide is a series problem, not a naming problem.
    if "现金流" in (name or ""):
        return "suspect_class"
    return "suspect_series"


def measure_one(code, klass, px_all, start, end):
    """One row: geometry pairs, their sigma, and what neutralising each set does to the CAGR."""
    px_w, rets, resets = window_rets(px_all, klass, start, end, code=code)
    px_w = px_w.dropna()
    if px_w.shape[0] < MIN_BARS:
        return {
            "code": code, "class": klass, "bars": int(px_w.shape[0]), "priced": False,
            "why_unpriced": "fewer than %d bars in the window" % MIN_BARS,
            "sigma_bp": None, "geometry_pairs": 0, "anomalous_pairs": 0, "in_resets": 0,
            "max_sigma": None, "max_round_trip_bp": None,
            "cagr_raw_pct": None, "cagr_all_shape_pct": None, "cagr_anomalous_pct": None,
            "effect_all_shape_pp": None, "effect_anomalous_pp": None,
            "pairs": [],
        }
    sig = sigma_bp(rets)
    pairs = YY.find_flip_pairs(px_w)
    reset_days = {str(pd.Timestamp(d["date"] if isinstance(d, dict) else d).date())
                  for d in (resets or [])}
    for p in pairs:
        p["sigma"] = (None if not sig else round(abs(float(p["drop_bp"])) / sig, 2))
        p["in_money_resets"] = p["drop_date"] in reset_days
    anomalous = [p for p in pairs if p["sigma"] is not None and p["sigma"] >= SIGMA_MIN]
    raw_c = cagr_from_rets(rets)
    all_c = cagr_from_rets(YY.neutralise(rets, px_w, pairs))
    ano_c = cagr_from_rets(YY.neutralise(rets, px_w, anomalous))
    biggest = max([float(p["round_trip_bp"]) for p in pairs], default=None)
    return {
        "code": code, "class": klass, "bars": int(px_w.shape[0]), "priced": True,
        "why_unpriced": None,
        "sigma_bp": None if sig is None else round(sig, 3),
        "geometry_pairs": len(pairs), "anomalous_pairs": len(anomalous),
        "in_resets": int(sum(1 for p in pairs if p["in_money_resets"])),
        "max_sigma": (None if not pairs or sig is None
                      else round(max(abs(float(p["drop_bp"])) for p in pairs) / sig, 2)),
        "max_round_trip_bp": None if biggest is None else round(biggest, 2),
        "cagr_raw_pct": None if raw_c is None else round(raw_c, PRICE_DEC),
        "cagr_all_shape_pct": None if all_c is None else round(all_c, PRICE_DEC),
        "cagr_anomalous_pct": None if ano_c is None else round(ano_c, PRICE_DEC),
        "effect_all_shape_pp": (None if (raw_c is None or all_c is None)
                                else round(all_c - raw_c, PRICE_DEC)),
        "effect_anomalous_pp": (None if (raw_c is None or ano_c is None)
                                else round(ano_c - raw_c, PRICE_DEC)),
        "pairs": pairs,
    }


def margin_days(row_year):
    """Trading days of this shelf's own extra that one CNY of wait is worth (r2046 inversion)."""
    net = row_year.get("net_p95_cny")
    days = row_year.get("payback_days_p95_on_this_line")
    if not net or not days or days <= 0 or net <= 0:
        return None
    return net / days, float(days)


def verdict_for(n_anomalous, n_priced):
    if not n_anomalous:
        return "NO_PAIR_ANYWHERE"
    if n_priced and (n_anomalous / float(n_priced)) >= SYSTEMATIC_SHARE:
        return "ANOMALIES_ARE_SYSTEMATIC"
    if n_anomalous == 1:
        return "THE_ANOMALY_IS_CONFINED_TO_ONE_SHELF"
    return "ANOMALIES_ARE_NAMED_NOT_SYSTEMATIC"


def build():
    year_face = _load(YEAR_FACE)
    budget = float(year_face["adoption"]["budget_sessions"])
    ticket = float(year_face["headline"]["ticket_cash_cny"])

    close_all, open_all, _amt, _feats = E.build_panel()
    close_all, _open2, n_flip_35 = A.repair_flips(close_all, open_all)
    window_end = str(close_all.index[-1].date())

    cmap = A.load_class_map()
    cols = list(close_all.columns)
    cls = A.classify(cols, cmap, close_all)
    universe = [c for c in cols if str(cls.get(c)) in UNIVERSE_CLASSES]

    rows = [measure_one(c, str(cls.get(c)), close_all[c], SS.START, window_end)
            for c in sorted(universe)]
    for r in rows:
        info = cmap.get(str(r["code"])[:6])
        r["name"] = info[1] if info else ""
        r["class_confidence"] = class_confidence(r, r["name"])
    priced = [r for r in rows if r["priced"]]

    clean = [r for r in priced if r["class_confidence"] == "ok"]
    geom = [r for r in clean if r["geometry_pairs"] > 0]
    anom = [r for r in clean if r["anomalous_pairs"] > 0]
    share = (len(anom) / len(clean)) if clean else 0.0
    verdict = verdict_for(len(anom), len(clean))

    by_code = {r["code"]: r for r in rows}
    shelf_days, shelf_untouched = [], []
    for yr in year_face["rows"]:
        r = by_code.get(yr["code"])
        conv = margin_days(yr)
        if r is None:
            continue
        if r["class_confidence"] != "ok":
            shelf_untouched.append({"code": yr["code"],
                                    "note": "class labelled %s (%s, sigma %s bp) -- no "
                                            "reading taken off this row"
                                            % (r["class_confidence"], r["name"],
                                               _f(r["sigma_bp"], 1))})
            continue
        if r["anomalous_pairs"] == 0:
            if yr["quote_audit"]["flip_pairs"]:
                shelf_untouched.append({"code": yr["code"],
                                        "note": "r2046 neutralised %d pair(s) this sigma ruler "
                                                "does not call anomalous"
                                                % len(yr["quote_audit"]["flip_pairs"])})
            else:
                shelf_untouched.append({"code": yr["code"], "note": "no pair on either ruler"})
            continue
        if conv is None or r["effect_anomalous_pp"] is None:
            continue
        daily_cny, days = conv
        flip_cny = r["effect_anomalous_pp"] / 100.0 * ticket
        pub = yr.get("published_payback_days_p95")
        on_line = yr.get("payback_days_p95_on_this_line")
        bpy = yr.get("bars_per_year") or 0.0
        shelf_days.append({
            "code": yr["code"],
            "effect_anomalous_pp": r["effect_anomalous_pp"],
            "flip_cny_per_year": round(flip_cny, 2),
            "daily_extra_cny": round(daily_cny, 2),
            "share_of_yearly_extra_pct": (round(abs(flip_cny) / (daily_cny * bpy) * 100.0, 2)
                                          if (daily_cny and bpy) else None),
            "r2046_published_days": None if pub is None else round(float(pub), 2),
            "r2046_on_this_line_days": None if on_line is None else round(float(on_line), 2),
            "r2046_delta_days": (None if (pub is None or on_line is None)
                                 else round(float(on_line) - float(pub), 2)),
            "published_margin_days": round(budget - days, 2),
            "r2046_pairs": len(yr["quote_audit"]["flip_pairs"]),
        })
    over_margin = [s for s in shelf_days
                   if s["published_margin_days"] is not None
                   and s["r2046_delta_days"] is not None
                   and s["r2046_delta_days"] > s["published_margin_days"]]

    by_class = {}
    for r in clean:
        d = by_class.setdefault(r["class"], {"priced": 0, "geometry": 0, "anomalous": 0,
                                             "pairs": 0, "anomalous_pairs": 0})
        d["priced"] += 1
        d["pairs"] += r["geometry_pairs"]
        d["anomalous_pairs"] += r["anomalous_pairs"]
        if r["geometry_pairs"]:
            d["geometry"] += 1
        if r["anomalous_pairs"]:
            d["anomalous"] += 1

    money_wide = [{"code": r["code"], "name": r["name"], "sigma_bp": r["sigma_bp"]}
                  for r in priced
                  if r["class_confidence"] == "suspect_series"]
    suspects = [{"code": r["code"], "name": r["name"], "class": r["class"],
                 "sigma_bp": r["sigma_bp"], "why": r["class_confidence"]}
                for r in priced if r["class_confidence"] != "ok"]

    tags = []
    if geom and len(geom) >= GEOMETRY_OVERREACH * max(len(anom), 1):
        tags.append("THE_GEOMETRY_OVERREACHES")
    # r2046 neutralised pairs on exactly the shelves its own quote_audit lists; this ruler
    # either backs those repairs or calls one of them a normal move
    r2046_repaired = [yr for yr in year_face["rows"] if yr["quote_audit"]["flip_pairs"]]
    unconfirmed = [yr["code"] for yr in r2046_repaired
                   if (by_code.get(yr["code"]) or {}).get("anomalous_pairs", 0) == 0]
    if r2046_repaired and not unconfirmed:
        tags.append("R2046_REPAIR_IS_CONFIRMED_BY_ITS_OWN_SIGMA")
    if unconfirmed:
        tags.append("R2046_REPAIRS_A_NORMAL_MOVE")
    if over_margin:
        tags.append("THE_FLIP_OUTWEIGHS_THE_MARGIN")
    if [s for s in suspects if s["why"] == "suspect_class"]:
        tags.append("MONEY_CLASS_MATCHES_A_FACTOR_FUND")
    if money_wide:
        tags.append("MONEY_SERIES_CARRIES_UNCAUGHT_JUMPS")

    face = {
        "schema": "cash-shelf-flip-census/v2",
        "artifact": "cash_shelf_flip_census",
        "generated": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": window_end,
        "window": {"start": SS.START, "end": window_end},
        "question": ("across every money / bond / convertible ETF in the panel: which carry a "
                     "print that is both r2046's flip shape and large against that instrument's "
                     "own daily movement, what does neutralising those do to its annualised "
                     "return, and does r2046's repair stay inside the one shelf that earned it"),
        "flip_rule": dict(year_face["flip_rule"]),
        "sigma_rule": {
            "definition": "|drop_bp| / (that instrument's daily return std in bp, same window)",
            "min_sigma": SIGMA_MIN,
            "why": ("the frozen geometry is an absolute -50bp; on a money ETF with a 4bp daily "
                    "sigma that is 12 sigma, on a convertible ETF with a 65bp sigma it is a "
                    "normal move. Repairing by shape alone would move 511380's annualised "
                    "return by more than a percentage point in the wrong direction."),
            "this_is_not": "a significance test; it is the readability floor for 'not a market move'",
        },
        "universe": {
            "classes": list(UNIVERSE_CLASSES),
            "priced": len(priced), "unpriced": len(rows) - len(priced), "min_bars": MIN_BARS,
            "clean": len(clean), "suspects": suspects,
            "with_geometry": len(geom), "with_anomaly": len(anom),
            "geometry_pairs": int(sum(r["geometry_pairs"] for r in clean)),
            "anomalous_pairs": int(sum(r["anomalous_pairs"] for r in clean)),
            "all_class_geometry_pairs": int(sum(r["geometry_pairs"] for r in priced)),
            "share_with_anomaly": round(share, 6),
            "systematic_share": SYSTEMATIC_SHARE,
            "by_class": by_class,
            "money_sigma_over_%dbp" % int(MONEY_SIGMA_WIDE_BP): money_wide,
        },
        "ruler": {
            "cost_bp_charged": 0.0,
            "why": ("this face describes the quote series, not a trade; the entry cost is the "
                    "same bar in both branches and cancels in the difference"),
            "annualisation": "each instrument's own bar count (cash_shelf_year_by_year.bars_per_year)",
            "panel_repair_applied_first": "etf_equity_alpha.repair_flips (35% single bar)",
            "flips_repaired_35pct_rule": int(n_flip_35),
        },
        "upstream": {"year_face": YEAR_FACE,
                     "year_face_sha256": _sha(os.path.join(ROOT, YEAR_FACE))},
        "adoption": {
            "budget_sessions": budget, "ticket_cash_cny": ticket,
            "source": YEAR_FACE + " :: adoption / headline",
            "note": "no second budget or ticket is declared here; both are read and printed",
        },
        "verdict": verdict,
        "tags": tags,
        "shelf_days": shelf_days,
        "shelf_untouched": shelf_untouched,
        "headline": {
            "verdict": verdict, "tags": tags,
            "priced": len(priced), "clean": len(clean),
            "with_geometry": len(geom), "with_anomaly": len(anom),
            "anomalous": [{"code": r["code"], "class": r["class"], "name": r["name"],
                           "sigma": r["max_sigma"], "pairs": r["anomalous_pairs"],
                           "effect_pp": r["effect_anomalous_pp"]}
                          for r in sorted(anom, key=lambda x: -(x["max_sigma"] or 0))],
            "geometry_only": [r["code"] for r in sorted(geom, key=lambda x: -(x["max_sigma"] or 0))
                              if r["anomalous_pairs"] == 0],
            "shelves_over_margin": [s["code"] for s in over_margin],
            "shelves_untouched": [s["code"] for s in shelf_untouched],
        },
        "rows": rows,
    }
    face["content_sha256"] = _content_sha({k: v for k, v in face.items() if k != "content_sha256"})
    return face


# --------------------------------------------------------------------- rendering

def _f(v, nd=2):
    if v is None:
        return "-"
    if isinstance(v, int) and not isinstance(v, bool):
        return str(v)
    try:
        return ("%." + str(nd) + "f") % float(v)
    except (TypeError, ValueError):
        return str(v)


def render_block(face):
    u = face["universe"]
    out = ["**Verdict: `%s`**  " % face["verdict"]]
    if face["tags"]:
        out.append("**Tags: %s**  " % ", ".join("`%s`" % t for t in face["tags"]))
    out.append("")
    out.append("Window %s .. %s. Family %d instruments, **%d priced** (>= %d bars), of which "
               "**%d clean** and **%d labelled** (see the last table). "
               "The frozen flip shape fires on **%d clean instruments / %d pairs**; the sigma "
               "ruler (>= %.0f own daily sigmas) calls **%d instruments / %d pairs** anomalous. "
               "Panel repair applied first: %d prints above 35%%."
               % (face["window"]["start"], face["window"]["end"],
                  u["priced"] + u["unpriced"], u["priced"], u["min_bars"],
                  u["clean"], len(u["suspects"]),
                  u["with_geometry"], u["geometry_pairs"],
                  face["sigma_rule"]["min_sigma"], u["with_anomaly"], u["anomalous_pairs"],
                  face["ruler"]["flips_repaired_35pct_rule"]))
    out.append("")
    out.append("| class | priced | shape fires | anomalous | shape pairs | anomaly pairs |")
    out.append("|---|---|---|---|---|---|")
    for k in sorted(u["by_class"]):
        d = u["by_class"][k]
        out.append("| %s | %d | %d | %d | %d | %d |"
                   % (k, d["priced"], d["geometry"], d["anomalous"], d["pairs"],
                      d["anomalous_pairs"]))
    out.append("")
    out.append("### Anomalous prints (>= %.0f own sigmas)" % face["sigma_rule"]["min_sigma"])
    out.append("")
    if face["headline"]["anomalous"]:
        out.append("| code | name | class | anomalous pairs | biggest sigma | daily sigma (bp) | "
                   "effect on its own CAGR (pp/yr) |")
        out.append("|---|---|---|---|---|---|---|")
        sig = {r["code"]: r["sigma_bp"] for r in face["rows"]}
        for a in face["headline"]["anomalous"]:
            out.append("| %s | %s | %s | %d | %s | %s | %s |"
                       % (a["code"], a.get("name") or "-", a["class"], a["pairs"],
                          _f(a["sigma"], 2), _f(sig.get(a["code"]), 2), _f(a["effect_pp"], 6)))
    else:
        out.append("None: no instrument in the family carries a print this large.")
    if face["headline"]["geometry_only"]:
        out.append("")
        out.append("Shape-only (normal moves this ruler keeps out): %s"
                   % ", ".join("`%s`" % c for c in face["headline"]["geometry_only"][:12]))
    out.append("")
    out.append("### The five shelves r2046 prices")
    out.append("")
    if face["shelf_days"]:
        out.append("| code | effect (pp/yr) | effect (CNY/yr) | share of its yearly extra | "
                   "r2046 published (days) | on this line (days) | delta (days) | margin left (days) |")
        out.append("|---|---|---|---|---|---|---|---|")
        for s in face["shelf_days"]:
            out.append("| %s | %s | %s | %s%% | %s | %s | %s | %s |"
                       % (s["code"], _f(s["effect_anomalous_pp"], 6),
                          _f(s["flip_cny_per_year"], 2), _f(s["share_of_yearly_extra_pct"], 1),
                          _f(s["r2046_published_days"], 2), _f(s["r2046_on_this_line_days"], 2),
                          _f(s["r2046_delta_days"], 2), _f(s["published_margin_days"], 2)))
    else:
        out.append("None of the five shelves carries an anomalous print on this ruler.")
    if face["shelf_untouched"]:
        out.append("")
        for s in face["shelf_untouched"]:
            out.append("- `%s`: %s" % (s["code"], s["note"]))
    if u.get("suspects"):
        out.append("")
        out.append("### Labelled rows (kept out of every verdict)")
        out.append("")
        out.append("| code | name | labelled | daily sigma (bp) | why |")
        out.append("|---|---|---|---|---|")
        for s in u["suspects"]:
            why = ("the classifier's name rule matched 现金 in a free-cash-flow equity ETF"
                   if s["why"] == "suspect_class"
                   else "a money-market fund whose own series jumps this wide")
            out.append("| %s | %s | %s | %s | %s |"
                       % (s["code"], s["name"] or "-", s["why"], _f(s["sigma_bp"], 1), why))
    return "\n".join(out)


def render_doc(face):
    return "\n".join([
        "# 报价翻转普查：r2046 那笔修正到底该走多远",
        "",
        "- artifact: `%s`（`--check` 可复算，`--selftest` 可离线自检）" % face["artifact"],
        "- generated: %s ｜ evidence_cutoff: %s" % (face["generated"], face["evidence_cutoff"]),
        "- 窗口: %s .. %s ｜ 家族 %d 只（%s），可定价 %d 只"
        % (face["window"]["start"], face["window"]["end"],
           face["universe"]["priced"] + face["universe"]["unpriced"],
           "/".join(face["universe"]["classes"]), face["universe"]["priced"]),
        "",
        "## 问题",
        "",
        face["question"] + "。",
        "",
        "## 为什么需要第二把尺",
        "",
        "r2046 冻结的翻转形状是**绝对**的：单 bar 跌 50bp、3 bar 内回到原价 5bp 内。",
        "对一只日波动 4bp 的货币 ETF，这是 12 个自身 sigma；对一只日波动 65bp 的转债 ETF，",
        "这是普通的一天。只按形状修，会把 511380 的 23 次正常波动一起中和掉，",
        "把它的年化往**反方向**推动一个多百分点。",
        "",
        "所以本面把形状原样保留，只加一把尺：每一对都按**该标的自己的日收益标准差**记账，",
        "`sigma >= 4` 才算异常打印（这是可读性下限，不是显著性检验；每一对的 sigma 都印出来）。",
        "",
        "## 读数",
        "",
        MARK_BEGIN,
        render_block(face),
        MARK_END,
        "",
        "## 怎么读",
        "",
        "- `shape` = r2046 几何形状命中数；`anomalous` = 其中 >= 4 个自身 sigma 的。",
        "  两者差距就是「只按形状修」会误伤多少正常波动。",
        "- `effect on its own CAGR` = 只中性化异常对之后的年化 − 原样年化。",
        "  这是**该不该修**的读数：非异常对的修正不是修正，是篡改。",
        "- `effect in days` 把修正换算成该货架自己每天的超额，再和 r2046 留下的余量比。",
        "",
        "## 不宣称",
        "",
        "1. 不解释翻转成因（份额折算 / 做市报价 / 数据源 amend 都可能）；",
        "2. 只覆盖一种形状：单 bar 深跌 + 3 bar 内回到原价 5bp 内；",
        "3. sigma 是窗口内的常数，不做时变波动率；",
        "4. 家族外品种不在射程（权益类的 35% 翻转另有其规则）。",
        "",
    ])


# --------------------------------------------------------------------- commands

def cmd_run():
    face = build()
    with io.open(os.path.join(ROOT, FACE), "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
        f.write("\n")
    doc_path = os.path.join(ROOT, DOC)
    body = render_doc(face)
    if os.path.exists(doc_path):
        old = io.open(doc_path, encoding="utf-8").read()
        if MARK_BEGIN in old and MARK_END in old:
            pre = old.split(MARK_BEGIN)[0]
            post = MARK_END + old.split(MARK_END, 1)[1]
            body = pre + MARK_BEGIN + "\n" + render_block(face) + "\n" + post
    with io.open(doc_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    u = face["universe"]
    print("RUN OK %s verdict=%s priced=%d shape=%d/%d anomaly=%d/%d tags=%s"
          % (FACE, face["verdict"], u["priced"], u["with_geometry"], u["geometry_pairs"],
             u["with_anomaly"], u["anomalous_pairs"], ",".join(face["tags"]) or "-"))
    return 0


CHECK_FIELDS = ("geometry_pairs", "anomalous_pairs", "in_resets", "sigma_bp", "max_sigma",
                "cagr_raw_pct", "cagr_all_shape_pct", "cagr_anomalous_pct",
                "effect_all_shape_pp", "effect_anomalous_pp")


def cmd_check():
    path = os.path.join(ROOT, FACE)
    if not os.path.exists(path):
        print("CHECK FAILED face missing -> STALE, run `run`")
        return 3
    face = _load(FACE)
    want_sha = face["upstream"]["year_face_sha256"]
    got_sha = _sha(os.path.join(ROOT, YEAR_FACE))
    if want_sha != got_sha:
        print("STALE: %s bytes changed (face %s.. != disk %s..) -> re-run"
              % (YEAR_FACE, want_sha[:12], got_sha[:12]))
        return 3
    fresh = build()
    if str(face.get("evidence_cutoff")) != str(fresh.get("evidence_cutoff")):
        print("STALE: panel tail moved %s -> %s, this census is a statement about a window"
              % (face.get("evidence_cutoff"), fresh.get("evidence_cutoff")))
        return 3
    bad = []
    for key in ("verdict", "tags"):
        if face.get(key) != fresh.get(key):
            bad.append("%s: face=%s recompute=%s" % (key, face.get(key), fresh.get(key)))
    for key in ("priced", "unpriced", "clean", "with_geometry", "with_anomaly",
                "geometry_pairs", "anomalous_pairs"):
        if face["universe"].get(key) != fresh["universe"].get(key):
            bad.append("universe.%s: face=%s recompute=%s"
                       % (key, face["universe"].get(key), fresh["universe"].get(key)))
    if [s["code"] for s in face["universe"]["suspects"]] != \
            [s["code"] for s in fresh["universe"]["suspects"]]:
        bad.append("universe.suspects set changed")
    if face["universe"]["by_class"] != fresh["universe"]["by_class"]:
        bad.append("universe.by_class drifted")
    fmap = {r["code"]: r for r in fresh["rows"]}
    for r in face["rows"]:
        fr = fmap.get(r["code"])
        if fr is None:
            bad.append("%s vanished upstream" % r["code"])
            continue
        for field in CHECK_FIELDS:
            a, b = r.get(field), fr.get(field)
            if a is None and b is None:
                continue
            if a is None or b is None or abs(float(a) - float(b)) > 1e-6:
                bad.append("%s %s: face=%s recompute=%s" % (r["code"], field, a, b))
        if len(r["pairs"]) != len(fr["pairs"]):
            bad.append("%s pair list changed" % r["code"])
        if r.get("class_confidence") != fr.get("class_confidence"):
            bad.append("%s class_confidence: face=%s recompute=%s"
                       % (r["code"], r.get("class_confidence"), fr.get("class_confidence")))
    for s in face["shelf_days"]:
        fs = next((x for x in fresh["shelf_days"] if x["code"] == s["code"]), None)
        if fs is None:
            bad.append("%s shelf_days row vanished" % s["code"])
            continue
        for field in ("effect_anomalous_pp", "flip_cny_per_year", "share_of_yearly_extra_pct",
                      "r2046_published_days", "r2046_on_this_line_days", "r2046_delta_days",
                      "published_margin_days"):
            a, b = s.get(field), fs.get(field)
            if a is None or b is None or abs(float(a) - float(b)) > 1e-6:
                bad.append("%s shelf_days.%s: face=%s recompute=%s"
                           % (s["code"], field, a, b))
    if bad:
        print("CHECK FAILED %d leg(s):" % len(bad))
        for b in bad[:20]:
            print("  - " + b)
        return 1
    print("CHECK OK %s: verdict/tags/universe/%d rows re-derived, %d anomaly lists identical"
          % (FACE, len(face["rows"]), face["universe"]["with_anomaly"]))
    return 0


# --------------------------------------------------------------------- selftest

def _synth(n=400, seed=11, sigma_bp=2.0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2021-01-04", periods=n)
    steps = rng.normal(0.00008, sigma_bp / 1e4, n)
    return pd.Series(100.0 * np.cumprod(1.0 + steps), index=idx)


def measure_on_series(px, klass="bond"):
    """measure_one without touching the money-ETF loader (synthetic series are not on disk)."""
    px_w = px.dropna()
    rets = px_w.pct_change()
    if px_w.shape[0] < MIN_BARS:
        return {"priced": False, "geometry_pairs": 0, "anomalous_pairs": 0,
                "effect_anomalous_pp": None, "why_unpriced": "too few bars"}
    sig = sigma_bp(rets)
    pairs = YY.find_flip_pairs(px_w)
    for p in pairs:
        p["sigma"] = None if not sig else round(abs(float(p["drop_bp"])) / sig, 2)
    anom = [p for p in pairs if p["sigma"] is not None and p["sigma"] >= SIGMA_MIN]
    raw_c = cagr_from_rets(rets)
    ano_c = cagr_from_rets(YY.neutralise(rets, px_w, anom))
    eff = None if (raw_c is None or ano_c is None) else round(ano_c - raw_c, PRICE_DEC)
    return {"priced": True, "sigma_bp": sig, "geometry_pairs": len(pairs),
            "anomalous_pairs": len(anom), "effect_anomalous_pp": eff}


def selftest():
    errs, legs = [], [0]

    def chk(ok, msg):
        legs[0] += 1
        if not ok:
            errs.append("L%d %s" % (legs[0], msg))

    # L1-L4 the shape as r2046 froze it (imported, not retyped)
    px = _synth(sigma_bp=2.0)
    px.iloc[100] = px.iloc[99] * 0.994
    pairs = YY.find_flip_pairs(px)
    chk(len(pairs) == 1 and pairs[0]["gap_bars"] == 1, "L1 shape not found on a clean synthetic flip")

    px2 = _synth()
    px2.iloc[100:] = px2.iloc[100:] * 0.994
    chk(len(YY.find_flip_pairs(px2)) == 0, "L2 a permanent drop was booked as a flip")

    px3 = _synth()
    px3.iloc[100] = px3.iloc[99] * 0.9985
    px3.iloc[101] = px3.iloc[100] * (1 / 0.9985)
    chk(len(YY.find_flip_pairs(px3)) == 0, "L3 a sub-threshold drop was booked as a flip")

    px4 = _synth()
    px4.iloc[100] = px4.iloc[99] * 0.994
    for k in (101, 102, 103):
        px4.iloc[k] = px4.iloc[k - 1] * 1.0005
    chk(len(YY.find_flip_pairs(px4)) == 0, "L4 a rebound outside the 3-bar window counted")

    # L5 neutralise zeroes both bars and nothing else
    rets = px.pct_change()
    neut = YY.neutralise(rets, px, pairs)
    d = pd.Timestamp(pairs[0]["drop_date"])
    b = pd.Timestamp(pairs[0]["back_date"])
    chk(neut.loc[d] == 0.0 and neut.loc[b] == 0.0, "L5 neutralise left a pair bar non-zero")

    # L6 the effect's sign on a quiet instrument: a real flip lowers the neutralised CAGR
    raw_c, neut_c = cagr_from_rets(rets), cagr_from_rets(neut)
    chk(raw_c is not None and neut_c is not None and neut_c < raw_c,
        "L6 neutralising did not lower the CAGR (%s vs %s)" % (raw_c, neut_c))

    # L7 the sigma ruler separates the same shape on a quiet and on a noisy instrument
    quiet = measure_on_series(px)
    chk(quiet["geometry_pairs"] == 1 and quiet["anomalous_pairs"] == 1,
        "L7 a -60bp print on a 2bp-sigma series was not called anomalous (%s)" % (quiet,))
    noisy = _synth(sigma_bp=65.0)
    noisy.iloc[100] = noisy.iloc[99] * 0.994
    noisy_row = measure_on_series(noisy)
    # the shape fires on ordinary noise here (that is the defect this ruler exists for),
    # so the leg asserts the count it must NOT call anomalous, not the shape count.
    chk(noisy_row["geometry_pairs"] >= 1 and noisy_row["anomalous_pairs"] == 0,
        "L7 a -60bp print on a 65bp-sigma series was called anomalous (%s)" % (noisy_row,))

    # L8 no pairs -> zero effect, so the census cannot claim a repair it did not make
    clean = measure_on_series(_synth())
    chk(clean["geometry_pairs"] == 0 and clean["effect_anomalous_pp"] == 0.0,
        "L8 a clean series was assigned a non-zero effect")

    # L9 sigma is the instrument's own, so widening its noise must lower a pair's sigma
    sig_quiet = sigma_bp(px.pct_change())
    sig_noisy = sigma_bp(_synth(sigma_bp=65.0).pct_change())
    chk(sig_quiet is not None and sig_noisy is not None and sig_noisy > 10 * sig_quiet,
        "L9 sigma did not track the series' own noise (%s vs %s)" % (sig_quiet, sig_noisy))

    # L10 margins: the conversion refuses a row without a positive net wait
    chk(margin_days({"net_p95_cny": 0.0, "payback_days_p95_on_this_line": 3.0}) is None,
        "L10 margin_days invented a daily extra from a zero net wait")
    conv = margin_days({"net_p95_cny": 100.0, "payback_days_p95_on_this_line": 5.0})
    chk(conv is not None and abs(conv[0] - 20.0) < 1e-9 and conv[1] == 5.0,
        "L10 daily extra = net / days not honoured (%s)" % (conv,))

    # L11 verdicts are mechanical, on the anomaly count
    chk(verdict_for(0, 100) == "NO_PAIR_ANYWHERE", "L11 empty anomaly count")
    chk(verdict_for(1, 100) == "THE_ANOMALY_IS_CONFINED_TO_ONE_SHELF", "L11 one-shelf threshold")
    chk(verdict_for(2, 100) == "ANOMALIES_ARE_NAMED_NOT_SYSTEMATIC", "L11 named threshold")
    chk(verdict_for(25, 100) == "ANOMALIES_ARE_SYSTEMATIC", "L11 systematic threshold")

    # L12 the same shape, two instruments: only the quiet one may be repaired
    q_eff = quiet["effect_anomalous_pp"]
    n_eff = noisy_row["effect_anomalous_pp"]
    chk(q_eff is not None and abs(q_eff) > 0 and n_eff == 0.0,
        "L12 the ruler repaired a normal move (%s / %s)" % (q_eff, n_eff))

    # L13 a money row is labelled, never silently re-classified
    chk(class_confidence({"class": "bond", "sigma_bp": 70.0}, "十年国债ETF") == "ok",
        "L13 a bond row with a wide sigma was labelled")
    chk(class_confidence({"class": "money", "sigma_bp": 2.0}, "货币ETF华宝") == "ok",
        "L13 a quiet money row was labelled")
    chk(class_confidence({"class": "money", "sigma_bp": 63.0}, "现金流ETF华夏") == "suspect_class",
        "L13 a free-cash-flow equity ETF was not labelled as a class suspect")
    chk(class_confidence({"class": "money", "sigma_bp": 51.0}, "货币ETF广发") == "suspect_series",
        "L13 a money fund with a 51bp sigma was not labelled as a series suspect")

    if errs:
        print("SELFTEST FAILED %d/%d" % (len(errs), legs[0]))
        for e in errs:
            print("  - " + e)
        return 1
    print("SELFTEST OK %d/%d" % (legs[0], legs[0]))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd in ("--check", "check"):
        return cmd_check()
    if cmd in ("--selftest", "selftest"):
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
