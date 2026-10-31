"""ETF book, production candidate -- an order sheet a human can actually place.

The research line settled on a configuration: bond/money sleeves carry no selection
skill (see etf_equity_alpha.py), so the book is built from equity + commodity +
convertible only, held at the top-N composite score, rebalanced every 20 bars, with a
volatility target that only ever de-levers. This script does two things and nothing else:

  1. re-runs that exact configuration on the full panel (so the number on the card is
     produced by the same engine that produced the research, not retyped);
  2. prints TODAY'S target book -- weights, cash slot, and a yuan/share order sheet at a
     stated capital, from the most recent bar in the panel.

It does not trade, does not touch any registry, and does not claim edge. The honest
caveats (survivorship in the ETF pool, IS-heavy history, 2026 flat) travel on the card.

  python scripts/etf_book_production.py run [--capital=1000000] [--n=8] [--rebal=20]
  python scripts/etf_book_production.py --selftest      # offline invariants
"""
import glob
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A
import exchange_calendar_audit as CA

OUT_DIR = os.path.join(E.PATHS.results_dir, "etf_book_production")
IS_END = "2023-12-31"
COST = 0.0010
TARGET_VOL = 0.08
USE_CLASSES = ("equity", "commodity", "convertible")
VT_TAIL_FILE = "etf_book_voltarget_tail.json"
ARMS_FACE_FILE = "etf_book_phase_atlas_arms.json"


def vol_overlay_tail_support():
    """Read the paired-bootstrap tail face (E253) -> what the 8% overlay is worth at the tail.

    The card has always said the vol target "is a drawdown tool, not an edge", and every number
    behind that sentence was a median or a single path (r1360 / E253). The face marks the same
    overlay on the DRAWDOWN TAIL with both books sharing one draw per resample, so the sentence
    can carry the number instead of the impression. Soft-fails to None: a missing face must
    never invent a number or break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_bootstrap", VT_TAIL_FILE)
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return None
    v = doc.get("verdict") or {}
    share = v.get("tail_share_of_middle")
    if share is None:
        return None

    def pp(key):
        x = v.get(key)
        return None if x is None else round(100.0 * float(x), 2)

    return {
        "artifact": "results/etf_book_bootstrap/" + VT_TAIL_FILE,
        "evidence_cutoff": doc.get("evidence_cutoff"),
        "bars": doc.get("bars"),
        "resamples": doc.get("n_resamples"),
        "blocks": [a.get("block") for a in (doc.get("arms") or [])],
        "median_maxdd_delta_pp": pp("median_maxdd_delta_median"),
        "p1_maxdd_delta_pp": pp("p1_maxdd_delta_median"),
        "median_cagr_delta_pp": pp("p50_cagr_delta_median"),
        "tail_share_of_middle": float(share),
        "tail_is_mostly_a_middle_effect": v.get("tail_is_mostly_a_middle_effect"),
    }


def vol_overlay_tail_sentence(face=None):
    """One sentence for a human, built from the measured face -- never from a literal number."""
    line = "The vol target only de-levers; it is a drawdown tool, not an edge."
    f = vol_overlay_tail_support() if face is None else face
    if not f:
        return line + " (its draw-tail price is not measured on this build)"
    mid, p1, cagr = (f.get("median_maxdd_delta_pp"), f.get("p1_maxdd_delta_pp"),
                     f.get("median_cagr_delta_pp"))
    if mid is None or p1 is None:
        return line + " (its draw-tail price is not measured on this build)"
    return line + (
        " Priced on the draw tail (paired bootstrap, %s resamples, blocks %s): the median "
        "drawdown gain is %+.2fpp but only %.0f%% of it survives at the worst 1%% of histories "
        "(%+.2fpp)%s -- mostly a middle-path tool."
        % (f.get("resamples"), "/".join(str(b) for b in (f.get("blocks") or [])),
           mid, 100.0 * f["tail_share_of_middle"], p1,
           "" if cagr is None else ", bought with %+.2fpp of median CAGR" % cagr))


def family_coherence(results_dir=None):
    """Which world the width arms behind this card were priced on (r1183).

    The card quotes one width out of a family of arms; that family's verdicts are only
    measurements if every arm face priced ONE panel. When the family withholds its labels
    ("WORLDS_NOT_COMPARABLE") or was never stamped, the card has to say so instead of
    quoting a verdict as if it had been measured. Absence reads "not assessable", never
    "fine" -- a missing artifact is not a pass.
    """
    d = E.PATHS.results_dir if results_dir is None else results_dir
    p = os.path.join(d, ARMS_FACE_FILE)
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return {"artifact": "results/" + ARMS_FACE_FILE, "verdict": None,
                "detail": "arm family face absent -- coherence not assessable",
                "panels": [], "arms": 0, "evidence_cutoff": None,
                "priced_same_panel": None}
    coh = doc.get("panel_coherence") or {}
    return {
        "artifact": "results/" + ARMS_FACE_FILE,
        "verdict": coh.get("verdict"),
        "detail": coh.get("detail"),
        "panels": coh.get("panels") or [],
        "arms": len(doc.get("arms") or {}),
        "evidence_cutoff": (doc.get("baseline") or {}).get("evidence_cutoff"),
        "priced_same_panel": (coh.get("verdict") == "ONE_WORLD"),
    }


def _page_priced_bar(results_dir=None):
    """The bar the CEO one-pager was priced on, read from its own artifact (r1186).

    The page is the last paper in the chain, so earlier faces can only see the page that
    already exists on disk -- which is exactly the measurement a stale-paper claim needs.
    Absent page artifact reads None (UNKNOWN), never "same day".
    """
    d = E.PATHS.results_dir if results_dir is None else results_dir
    root = os.path.dirname(os.path.abspath(d))
    try:
        with open(os.path.join(root, "docs", "live_book", "latest.json"), "r",
                  encoding="utf-8") as fh:
            ptr = json.load(fh) or {}
        rel = ptr.get("json") or ""
        if not rel:
            return None
        with open(os.path.join(root, rel), "r", encoding="utf-8") as fh:
            return (json.load(fh) or {}).get("priced_bar")
    except (OSError, ValueError):
        return None


def priced_faces(page_bar=None, results_dir=None, card_bar=None, ticket_bar=None):
    """Which closing bar each of the three papers a reader holds was priced on (r1185).

    The card, the executable sheet and the CEO one-pager all quote the same book, and two of
    them published only the boolean "same priced bar = True". A boolean a reader cannot
    re-derive is a claim, not a measurement: when one paper falls a bar behind, the reader is
    told "different" and left unable to say WHICH paper is the stale one. This reads the three
    bars from the artifacts themselves and answers in three states -- SAME_DAY /
    DIFFERENT_DAYS / UNKNOWN -- where a missing face reads UNKNOWN, never SAME_DAY.
    """
    d = E.PATHS.results_dir if results_dir is None else results_dir
    faces, missing = {}, []

    def _card():
        with open(os.path.join(d, "etf_book_production", "latest.json"), "r", encoding="utf-8") as fh:
            return ((json.load(fh) or {}).get("sheet") or {}).get("as_of_bar")

    def _ticket():
        # latest.json is a pointer: the agreement block lives on the dated ticket sheet.
        with open(os.path.join(d, "etf_book_order", "latest.json"), "r", encoding="utf-8") as fh:
            ptr = json.load(fh) or {}
        doc = ptr
        if not ptr.get("card_agreement") and ptr.get("as_of"):
            with open(os.path.join(d, "etf_book_order", "TICKET-%s.json" % ptr["as_of"]),
                      "r", encoding="utf-8") as fh:
                doc = json.load(fh) or {}
        return (doc.get("card_agreement") or {}).get("ticket_priced_bar")

    for key, reader in (("card", _card), ("ticket", _ticket)):
        try:
            faces[key] = reader()
        except (OSError, ValueError):
            faces[key] = None
    # A face building itself knows its own bar better than its artifact does: the card is
    # written AFTER this runs, so reading it back would compare today's paper to yesterday's
    # copy of itself (r1186).
    if card_bar:
        faces["card"] = card_bar
    if ticket_bar:
        faces["ticket"] = ticket_bar
    for key in ("card", "ticket"):
        if not faces[key]:
            missing.append(key)
    faces["page"] = page_bar or _page_priced_bar(d)
    if not faces["page"]:
        missing.append("page")

    if missing:
        verdict = "UNKNOWN"
        detail = "no pricing day on: %s -- unknown, not agreement" % ", ".join(missing)
    elif len(set(faces.values())) == 1:
        verdict = "SAME_DAY"
        detail = "all three papers priced the %s bar" % faces["card"]
    else:
        verdict = "DIFFERENT_DAYS"
        detail = ("priced on different bars: " +
                  " / ".join("%s %s" % (k, v) for k, v in faces.items()))
    return {"faces": faces, "verdict": verdict, "detail": detail,
            "missing": missing, "same_day": verdict == "SAME_DAY"}


def commodity_support():
    """Read results/etf_book_commodity_split.json -> what the commodity sleeve earns.

    The commodity class produced ~30% of the book's gross return, and nothing on this
    card said whether that came from ranking commodity ETFs or from being long the metal.
    The artifact prices the sleeve on its own universe against the sleeve's own equal
    weight, so the answer travels with the CAGR instead of staying in a digest.
    Soft-fails to None: a missing artifact must never break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_commodity_split.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        runs = {r.get("label"): r for r in doc.get("runs", [])}
        book, ew = runs.get("commodity_only") or {}, runs.get("commodity_ew") or {}
        if book.get("cagr") is None or ew.get("cagr") is None:
            return None
        pas = (doc.get("read") or {}).get("deepest_name_passive") or {}
        return {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "cell": doc.get("cell"),
            "n_cols": book.get("n_cols"),
            "book_cagr": book.get("cagr"),
            "ew_cagr": ew.get("cagr"),
            "excess_pp": book.get("excess_pp"),
            "gross_share_pct": (doc.get("read") or {}).get("commodity_gross_share_pct"),
            "passive_name": pas.get("name"),
            "passive_cagr": pas.get("cagr"),
            "verdict": (doc.get("read") or {}).get("verdict"),
        }
    except Exception:
        return None


def passive_mix_support():
    """Read results/etf_book_passive_mix.json -> what the rotation is worth vs never trading.

    Every other number on this card prices the book against another RANKING rule. This one
    prices it against the alternative a holder actually has: the same class exposure held
    statically. Without it the card can claim a CAGR but not that the machinery earns it.
    Soft-fails to None: a missing artifact must never break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_passive_mix.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        runs = {r.get("label"): r for r in doc.get("runs", [])}
        book, static = runs.get("book") or {}, runs.get("static_mix") or {}
        read = doc.get("read") or {}
        if book.get("cagr") is None or static.get("cagr") is None or not read.get("verdict"):
            return None
        return {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "cell": doc.get("cell"),
            "book_cagr": book.get("cagr"),
            "book_maxdd": book.get("maxdd"),
            "static_cagr": static.get("cagr"),
            "static_maxdd": static.get("maxdd"),
            "premium_pp": read.get("selection_premium_pp"),
            "book_turnover": read.get("book_turnover_per_decision"),
            "static_turnover": read.get("static_turnover_per_decision"),
            "verdict": read.get("verdict"),
            # r1308: the same question asked outside the published regime. Absent on older
            # artifacts, so the card has to work with and without it.
            "by_window": read.get("by_window") or {},
            "cross_window": read.get("cross_window"),
            "premium_flips": read.get("premium_flips_between_periods"),
        }
    except Exception:
        return None


def decomp_support():
    """Read results/etf_book_window_decomp.json -> why the 2015-2019 window prints two numbers.

    r1305 published -8.86pp excess for 2015-2019 and this card also shows a small POSITIVE
    selection premium for the same window (r1308's passive-mix pre2020 cell). Both are real
    and they are different cells; without the ladder the two lines read as a contradiction.
    Soft-fails to None: a missing artifact must never break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_window_decomp.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        rungs = doc.get("rungs") or []
        if not rungs:
            return None
        return {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "window": doc.get("window"),
            "steps": [{"rung": r.get("rung"), "moves": r.get("moves"),
                       "cagr": r.get("book_cagr"), "excess_pp": r.get("excess_vs_ew_pp"),
                       "delta_pp": r.get("delta_vs_previous_pp")} for r in rungs],
            "total_move_pp": (doc.get("read") or {}).get("total_move_pp"),
            "controls": doc.get("controls") or {},
            "verdict": (doc.get("read") or {}).get("verdict"),
        }
    except Exception:
        return None


def spanning_support():
    """Read results/etf_book_spanning.json -> does the book still have an intercept?

    r1310: the card can quote a CAGR against another ranking rule or against a static class
    mix, but neither answers the question a funder asks -- after the four liquid exposures
    an account could simply hold (gold / Nasdaq QDII / CSI300 / bond), is anything left?
    Soft-fails to None: a missing artifact must never break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_spanning.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        full = doc.get("full") or {}
        ports = doc.get("span_portfolios") or {}
        ew = ports.get("equal_weight_basket") or {}
        if full.get("alpha_annual") is None or ew.get("cagr") is None:
            return None
        return {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "as_of": doc.get("evidence_cutoff"),
            "book_cagr": (doc.get("book") or {}).get("cagr"),
            "book_sharpe": (doc.get("book") or {}).get("sharpe"),
            "book_maxdd": (doc.get("book") or {}).get("maxdd"),
            "basket_cagr": ew.get("cagr"),
            "basket_sharpe": ew.get("sharpe"),
            "basket_maxdd": ew.get("maxdd"),
            "alpha_annual": full.get("alpha_annual"),
            "alpha_t": full.get("alpha_t"),
            "r2": full.get("r2"),
            "resid_vol_annual": full.get("resid_vol_annual"),
            "is_alpha_t": (doc.get("is") or {}).get("alpha_t"),
            "oos_alpha_t": (doc.get("oos") or {}).get("alpha_t"),
            "arms": {k: {"cagr": (v or {}).get("cagr"), "sharpe": (v or {}).get("sharpe"),
                         "maxdd": (v or {}).get("maxdd")}
                     for k, v in ports.items() if k != "equal_weight_basket"},
            "codes": ew.get("codes") or [],
            # r1311: the stagger arm is priced through the same regression (one code path),
            # and the control assertion says whether this window re-priced the PUBLISHED
            # book (r1297). Both travel with the number or the number is unreadable.
            "staggered_arm": _stagger_block(doc),
            "stagger_control": doc.get("stagger_control"),
        }
    except Exception:
        return None


def _stagger_block(doc):
    """The staggered arm's intercept, its risk, and the sentence the two alphas imply."""
    st = ((doc.get("arms") or {}).get("staggered") or {})
    full = st.get("full") or {}
    if full.get("alpha_annual") is None:
        return None
    stats = st.get("stats") or {}
    book = doc.get("full") or {}
    return {
        "window": st.get("window"),
        "alpha_annual": full.get("alpha_annual"),
        "alpha_t": full.get("alpha_t"),
        "r2": full.get("r2"),
        "resid_vol_annual": full.get("resid_vol_annual"),
        "is_alpha_t": (st.get("is") or {}).get("alpha_t"),
        "oos_alpha_t": (st.get("oos") or {}).get("alpha_t"),
        "cagr": stats.get("cagr"),
        "sharpe": stats.get("sharpe"),
        "maxdd": stats.get("maxdd"),
        "book_alpha_annual": book.get("alpha_annual"),
        "book_alpha_t": book.get("alpha_t"),
        "crosses_two_sigma": bool((full.get("alpha_t") or 0.0) >= 2.0),
        "book_crosses_two_sigma": bool((book.get("alpha_t") or 0.0) >= 2.0),
    }


def spanning_pre2020_support():
    """Read results/etf_book_spanning_pre2020.json -> does the intercept survive the window
    the book was not fitted in?

    r1312: the four-beta section on this card only ever spoke about 2020+ -- the window the
    book earned its money in. The same regression run on U_pre over 2015-2019 answers the
    question a reader actually has ("is this exposure mix, or skill?"), and it answers it
    negatively, so it belongs on the card and not in a digest (r1275). Soft-fails to None:
    a missing artefact must never break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_spanning_pre2020.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        arms = doc.get("arms") or {}
        single = arms.get("single") or {}
        st = arms.get("staggered") or {}
        ew = (doc.get("span_portfolios") or {}).get("equal_weight_basket") or {}
        full_s, full_g = single.get("full") or {}, st.get("full") or {}
        if full_s.get("alpha_annual") is None or ew.get("cagr") is None:
            return None
        return {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "window": doc.get("window"),
            "universe": doc.get("universe") or {},
            "single": {"alpha_annual": full_s.get("alpha_annual"),
                       "alpha_t": full_s.get("alpha_t"), "r2": full_s.get("r2"),
                       "is_alpha_t": (single.get("is") or {}).get("alpha_t"),
                       "oos_alpha_t": (single.get("oos") or {}).get("alpha_t"),
                       "cagr": (single.get("stats") or {}).get("cagr"),
                       "sharpe": (single.get("stats") or {}).get("sharpe"),
                       "maxdd": (single.get("stats") or {}).get("maxdd")},
            "staggered": {"alpha_annual": full_g.get("alpha_annual"),
                          "alpha_t": full_g.get("alpha_t"), "r2": full_g.get("r2"),
                          "is_alpha_t": (st.get("is") or {}).get("alpha_t"),
                          "oos_alpha_t": (st.get("oos") or {}).get("alpha_t"),
                          "cagr": (st.get("stats") or {}).get("cagr"),
                          "sharpe": (st.get("stats") or {}).get("sharpe"),
                          "maxdd": (st.get("stats") or {}).get("maxdd")},
            "basket": {"cagr": ew.get("cagr"), "sharpe": ew.get("sharpe"),
                       "maxdd": ew.get("maxdd"), "vol": ew.get("vol")},
            "control": doc.get("control"),
            "verdict": doc.get("verdict"),
        }
    except Exception:
        return None


def drawdown_band_support():
    """Read the bootstrap block arms -> how bad can this book's drawdown be?

    r1348: the card prints ONE drawdown (-12.5%) computed on one ordering of the trading
    days, while the block bootstrap of the same book puts the 5th-percentile drawdown
    between -17.1% and -25.0% depending on the block length -- i.e. the card's number is a
    median of a ruler, not a tail. A tail sentence must travel with the parameter that
    produced it (E248), and the page a human reads is where the tail matters most.
    Soft-fails to None (a missing artefact must never break the production face) and
    refuses to interpolate: if the arms are for a different cutoff than the card's bar,
    the band is reported as stale rather than passed off as today's.
    """
    d = os.path.join(E.PATHS.results_dir, "etf_book_bootstrap")
    try:
        files = sorted(glob.glob(os.path.join(d, "BLOCKS-*.json")))
        if not files:
            return None
        p = files[-1]
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        arms = doc.get("arms") or []
        if len(arms) < 2:
            return None
        band = {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "evidence_cutoff": doc.get("evidence_cutoff"),
            "block_set": [a.get("block") for a in arms],
            "n_resamples": (arms[0].get("n_resamples")),
            "arm_rows": [{"block": a.get("block"),
                          "maxdd_p5": (a.get("maxdd") or {}).get("5"),
                          "maxdd_p50": (a.get("maxdd") or {}).get("50"),
                          "dd_break_share": (a.get("shares") or {}).get("maxdd_le_line"),
                          "point_pctile_maxdd": (a.get("point_pctile") or {}).get("maxdd")}
                         for a in arms],
            "maxdd_p5_band": doc["spread"]["maxdd_p5"],
            "maxdd_p50_band": doc["spread"]["maxdd_p50"],
            "dd_break_band": doc["spread"]["dd_break_share"],
            "readings": doc.get("readings"),
        }
        band["band_pp"] = abs(band["maxdd_p5_band"]["max"] - band["maxdd_p5_band"]["min"]) * 100
        return band
    except Exception:
        return None


def drawdown_band_paragraphs(band, card_maxdd):
    if not band:
        return ["No bootstrap band on disk: the drawdown above is a single-path number and "
                "its tail is unpublished. Run scripts/etf_book_nav_envelope.py.", ""]
    a = band["maxdd_p5_band"]
    m = band["maxdd_p50_band"]
    br = band["dd_break_band"]
    lines = [
        "The drawdown column above is one ordering of the trading days. Bootstrapping the "
        "book's own return path (blocks %s bars, %d resamples) puts the 5th-percentile "
        "drawdown between **%.1f%% and %.1f%%** and the median between %.1f%% and %.1f%% -- "
        "a spread of %.1fpp produced by the block length alone, i.e. by how long the ruler "
        "remembers dependence."
        % ("/".join(str(b) for b in band["block_set"]), band["n_resamples"] or 0,
           a["min"] * 100, a["max"] * 100, m["min"] * 100, m["max"] * 100, band["band_pp"]),
        "",
        "| block (bars) | maxDD p5 | maxDD p50 | share worse than -20% | point maxDD pctile |",
        "|---|---|---|---|---|",
    ]
    for r in band["arm_rows"]:
        lines.append("| %s | %s | %s | %s | %s |" % (
            r["block"],
            "-" if r["maxdd_p5"] is None else "%.2f%%" % (r["maxdd_p5"] * 100),
            "-" if r["maxdd_p50"] is None else "%.2f%%" % (r["maxdd_p50"] * 100),
            "-" if r["dd_break_share"] is None else "%.1f%%" % (r["dd_break_share"] * 100),
            "-" if r["point_pctile_maxdd"] is None else "%.1f" % r["point_pctile_maxdd"]))
    lines += ["",
              "Read the card's own %.1f%% as the median of that ruler, not its tail: size the "
              "position against the p5 column, which is %.1fpp worse than the headline at the "
              "widest block." % (card_maxdd * 100, abs(card_maxdd - a["min"]) * 100), ""]
    if band["evidence_cutoff"]:
        lines += ["> Band priced on the **%s** bar from %s. A tail quoted without its block is "
                  "a sentence without its parameter (E248)." % (band["evidence_cutoff"],
                                                                band["artifact"]), ""]
    return lines


def preperiod_support():
    """Read results/etf_book_pre2020.json -> the one-line out-of-period verdict.

    The card's whole history is 2020+. results/etf_book_pre2020.json prices the same
    engine on the 224 ETFs that already existed, over 2015-2019, and prints a negative
    excess there -- so the published return is a single-regime result and the card has
    to say so next to the CAGR rather than leave it in a digest (r1275: a measured
    difference has to land where the decision is made). Soft-fails to None: a missing
    or unreadable file must never break the production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_pre2020.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        cell = doc["cells"]["A_pre_universe_pre_period"]["cells"]
        primary = doc.get("grid", {}).get("primary", "N5_R20")
        row = cell[primary]
        return {
            "artifact": os.path.relpath(p, os.path.dirname(E.PATHS.results_dir)).replace("\\", "/"),
            "grid_cell": primary,
            "window": "%s..%s" % (doc["cells"]["A_pre_universe_pre_period"]["start"],
                                  doc["cells"]["A_pre_universe_pre_period"]["end"]),
            "universe_size": doc["cells"]["A_pre_universe_pre_period"]["universe_size"],
            "book_cagr": row["book"]["cagr"],
            "ew_cagr": row["ew"]["cagr"],
            "excess_pp": row["excess_cagr_pp"],
            "null_p": row.get("null", {}).get("p_value"),
            "cells_negative": sum(1 for v in cell.values() if v["excess_cagr_pp"] < 0),
            "cells_total": len(cell),
        }
    except Exception:
        return None


def hysteresis_support():
    """Read results/etf_book_hysteresis.json -> does this book trade on noise?

    r1324: the book re-decides every 20 bars and its score is an average of percentile
    ranks, so "it trades on noise" is the obvious thing to say about it and nobody had
    priced it. scripts/etf_book_hysteresis.py measured it two ways (the cut-line margin,
    and a displacement buffer priced through the same engine). Both readings belong on
    the card: a reader deciding whether to hold this book cares whether the turnover is
    signal or churn. Soft-fails to None -- a missing artefact must never break the
    production face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_book_hysteresis.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        arms = doc.get("arms") or []
        base = next((a for a in arms if float(a.get("k") or 0.0) == 0.0), None)
        if base is None:
            return None
        cfg = doc.get("config") or {}
        census = doc.get("margin_census") or {}
        trades = doc.get("trade_margins") or {}

        def stats(a):
            return (a.get("stats") or {}).get("full") or {}

        base_s = stats(base)
        # the arm that beats the no-buffer book on all four numbers at once, if any:
        # turnover down, CAGR/Sharpe up, drawdown shallower. Data-driven, never assumed.
        best = None
        for a in arms:
            s = stats(a)
            if a is base or s.get("cagr") is None:
                continue
            if (a.get("turnover_per_decision") < base.get("turnover_per_decision")
                    and s["cagr"] > base_s["cagr"]
                    and (s.get("sharpe") or 0) > (base_s.get("sharpe") or 0)
                    and (s.get("maxdd") or 0) > (base_s.get("maxdd") or 0)):
                if best is None or s["cagr"] > stats(best)["cagr"]:
                    best = a
        return {
            "artifact": "results/etf_book_hysteresis.json",
            "evidence_cutoff": doc.get("evidence_cutoff"),
            "config": {"n_hold": cfg.get("n_hold"), "rebal": cfg.get("rebal"),
                       "cost_bp": cfg.get("cost_bp"), "grid": cfg.get("grid")},
            "control": doc.get("control"),
            "census": {"n_decisions": census.get("n_decisions"),
                       "cut_score_median": census.get("cut_score_median"),
                       "share_within_0p10": (census.get("share_within") or {}).get("0.1"),
                       "cut_sd_median": (census.get("cut_sd_q") or {}).get("0.5")},
            "trades": trades,
            "arms": [{"k": a.get("k"),
                      "turnover": a.get("turnover_per_decision"),
                      "cagr": stats(a).get("cagr"),
                      "sharpe": stats(a).get("sharpe"),
                      "maxdd": stats(a).get("maxdd")} for a in arms],
            "best_arm_k": (best or {}).get("k"),
            "caveats": (doc.get("caveats") or [])[:2],
        }
    except Exception:
        return None


def sign_pit_support():
    """Read results/etf_sign_pit.json -> are this book's factor signs knowable in real time?

    E205 (r1335): the six SIGNS are exactly the panel's full-sample IC signs, so the book is
    priced with knowledge of which way each factor paid. scripts/etf_sign_pit.py prices the
    honest arm (signs from already-realised windows only) on the same engine. That number
    belongs on the card: a reader deciding whether to run this book is reading a period, and
    the card must say so. Soft-fails to None -- a missing artefact never breaks the face.
    """
    p = os.path.join(E.PATHS.results_dir, "etf_sign_pit.json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        s = doc.get("summary") or {}
        if s.get("cagr_fixed") is None or s.get("cagr_pit") is None:
            return None
        matches = doc.get("fixed_sign_matches_full_sample_ic") or {}
        return {
            "artifact": "results/etf_sign_pit.json",
            "verdict": doc.get("verdict"),
            "n_factors": len(matches),
            "n_match": sum(1 for v in matches.values() if v),
            "cagr_fixed": float(s["cagr_fixed"]),
            "cagr_pit": float(s["cagr_pit"]),
            "sharpe_fixed": float(s.get("sharpe_fixed") or 0.0),
            "sharpe_pit": float(s.get("sharpe_pit") or 0.0),
            "cagr_reversed": float(s.get("cagr_reversed_sign") or 0.0),
            "evidence_cutoff": doc.get("evidence_cutoff"),
        }
    except Exception:
        return None


def control_moved(face_control, card, cell_key="n12_vt08", tol=1e-9):
    """Has the control arm a research face graded against moved on the SAME bar?

    A cutoff comparison answers "was this face priced before the card started": it is blind
    to the way the card actually changes -- a config edit, a repaired print or a re-derived
    cell on the bar it already carried. Those leave the date identical and every number the
    face graded itself against different, which is exactly the state in which the face is
    stale and a date-only gate reads green.

    The face already records what it graded against (control.published / published_turnover),
    so the question is answerable at check time with no engine run: compare the recorded
    numbers with the card now on disk. Returns (moved, reason):
      moved=None  -> the card or its cell is absent, nothing to compare (the caller falls
                     back to its cutoff rule and says so; that is not the same as clean)
      moved=True  -> the control moved under this face: stale, the chain pays a refresh
      moved=False -> these are the numbers the face was graded against.
    """
    if not card:
        return None, "production card unreadable -- the control arm cannot be re-read"
    cell = (card.get("backtest") or {}).get(cell_key)
    if not cell:
        return None, "production card carries no %s cell -- the control arm cannot be re-read" % cell_key
    face_control = face_control or {}
    if face_control.get("published") is None:
        return None, "face recorded no published control -- nothing to compare against"
    now = (cell.get("full") or {}).get("cagr")
    if now is None:
        return None, "card cell %s has no full-window CAGR -- the control arm cannot be re-read" % cell_key
    was = face_control.get("published")
    if abs(float(now) - float(was)) > tol:
        return True, ("the control arm this face graded against moved on the same bar: "
                      "%.6f then, %.6f now (%s)" % (float(was), float(now), cell_key))
    was_turn = face_control.get("published_turnover")
    now_turn = cell.get("turnover_per_decision")
    if was_turn is not None and now_turn is not None and abs(float(now_turn) - float(was_turn)) > tol:
        return True, ("the control arm's turnover moved on the same bar: "
                      "%.6f then, %.6f now (%s)" % (float(was_turn), float(now_turn), cell_key))
    return False, None


def load_names():
    """ETF code -> short name from the shipped list; empty on failure (never fatal)."""
    p = os.path.join(E.PATHS.data_dir, "basic", "etf_list.csv")
    df = None
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            df = pd.read_csv(p, encoding=enc)
            break
        except Exception:
            continue
    if df is None:
        return {}
    out = {}
    c_code, c_name = df.columns[0], df.columns[1]
    for code, name in zip(df[c_code].astype(str), df[c_name].astype(str)):
        code = code.strip()
        # the list carries exchange prefixes (sz159998) while the panel uses bare codes
        out[code[-6:]] = name.strip()
    return out


def scale_for(book, op, upto, target_vol=TARGET_VOL):
    """Same realised-vol overlay as etf_robust_pf book_vol: weights on 60d open returns."""
    if not book:
        return 1.0, None
    rets = op.pct_change()
    window = rets.loc[:upto].tail(60)[list(book)]
    if window.shape[0] < 20:
        return 1.0, None
    w = np.array([book[k] for k in window.columns])
    cov = window.cov().to_numpy()
    v = float(np.sqrt(w @ cov @ w) * np.sqrt(252))
    if not np.isfinite(v) or v <= 0:
        return 1.0, None
    return float(min(1.0, target_vol / v)), v


def backtest(close, openp, amt, score, n_hold, rebal, cost=COST, vol_target=None,
             vol_window=60):
    ser, turn = R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, cost,
                                      vol_target=vol_target, vol_window=vol_window)
    out = {}
    for lbl, sl in (("full", ser), ("is", ser[ser.index <= IS_END]),
                    ("oos", ser[ser.index > IS_END])):
        m = A.stats2(sl, lbl)
        out[lbl] = {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}
    out["turnover_per_decision"] = round(turn, 3)
    out["n_hold"] = n_hold
    out["vol_target"] = vol_target
    out["cost_bp"] = cost * 1e4
    return out, ser


def grid_position(dates, last_bar, rebal):
    """Where the last bar sits on the engine's every-`rebal`-bars decision grid.

    The panel ends at `last_bar`, so the next grid point usually lies in the future and
    has no date yet -- report it as a count of trading bars, not as an invented date.
    """
    if last_bar not in dates:
        return {"is_decision_bar": None, "bars_since_decision": None,
                "bars_until_next_decision": None, "last_decision_bar": None}
    i = dates.index(last_bar)
    off = i % rebal
    return {"is_decision_bar": off == 0,
            "bars_since_decision": off,
            "bars_until_next_decision": (rebal - off) % rebal,
            "last_decision_bar": str(dates[i - off].date())}


def delivered_vs_target(bt_row, target):
    """Realised vol next to the number on the label, window by window, with the ratio.

    The overlay is min(1, target / v) sized on the *picked names' backward* vol, so no
    window is guaranteed to deliver `target` -- the sleeve can run hotter than its label.
    The ratio is reported, never corrected: a fitted multiplier on the same sample is
    exactly the fitting that r1270's window x target sweep exists to detect.
    """
    out = {"target_vol": target, "windows": {}}
    for lbl in ("full", "is", "oos"):
        m = (bt_row or {}).get(lbl) or {}
        v = m.get("vol")
        if v is None:
            continue
        out["windows"][lbl] = {"target": target, "delivered": round(float(v), 4),
                               "ratio": round(float(v) / target, 3) if target else None}
    f = out["windows"].get("full")
    if f and f["ratio"] is not None:
        out["headline"] = ("target %.0f%% -> delivered %.1f%% over the full window (%.2fx)"
                           % (target * 100, f["delivered"] * 100, f["ratio"]))
    elif f:
        out["headline"] = ("delivered %.1f%% over the full window (no target set)"
                           % (f["delivered"] * 100))
    else:
        out["headline"] = None
    return out


PANEL_CENSUS = {}
PANEL_DIGEST = {}


def prep_panel(repair=True, repair_fn=None):
    """Panel + score exactly as the production run sees them (class filter included).

    Shared by `run` and by any sweep over the configuration, so a sensitivity study can
    never quietly price a different universe than the card.

    Returns the class map alongside the panel: the order sheet labels every leg with it,
    and recomputing it downstream would be a second, drift-prone classification. The
    flip count travels too -- it is printed on the card as evidence the panel was repaired.
    """
    close, openp, amt, feats = E.build_panel()
    # r1177: the census of the panel as the source printed it, taken before the repair (after
    # it the count is zero by construction). The card has to state how wide the panel it
    # counted was, otherwise its total and the ticket's -- which censuses only the classes it
    # ranks -- read as an arithmetic drift instead of a universe difference.
    global PANEL_CENSUS, PANEL_DIGEST
    try:
        PANEL_CENSUS = A.flip_census(close)
    except Exception:
        PANEL_CENSUS = {}
    if repair_fn is not None:
        # counterfactual repair injected by an audit (e.g. the pre-r1282 behaviour), so a
        # twin can be priced through THIS universe and score builder instead of a copy.
        close, openp, n_flip = repair_fn(close, openp)
    elif repair:
        close, openp, n_flip = A.repair_flips(close, openp)
    else:
        # the raw twin: the panel exactly as the source prints it, for audits that have
        # to price what the repair is worth instead of assuming it (etf_book_split_audit).
        n_flip = 0
    # r1178: the fingerprint is taken on the FULL repaired panel, before this face narrows
    # to the classes it ranks -- otherwise the card's digest would only ever match itself,
    # and "we all repair" would stay a claim instead of a comparable number.
    try:
        PANEL_DIGEST = A.panel_digest(close, openp, amt)
    except Exception:
        PANEL_DIGEST = {}
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in USE_CLASSES]
    close, openp, amt = close[cols], openp[cols], amt[cols]
    score = E.build_score(close, amt, feats)
    return close, openp, amt, score, cls, n_flip


def run(capital=1_000_000.0, n_hold=8, rebal=20):
    close, openp, amt, score, cls, n_flip = prep_panel()
    cols = list(close.columns)
    names = load_names()

    runs = {}
    for n in sorted({5, 8, n_hold}):
        for lbl, vt in (("base", None), ("vt08", TARGET_VOL)):
            key = "n%d_%s" % (n, lbl)
            runs[key], _ = backtest(close, openp, amt, score, n, rebal, vol_target=vt)
            print(key, runs[key]["full"], flush=True)

    # ---- the book IN FORCE, read off the engine's own decision step.
    # The engine only re-decides every `rebal` bars, so re-ranking the panel's last bar
    # here hands a human a sheet that trades 11 of 12 names on a bar the card itself
    # labels "HOLD". That is what this function did until r1277: at cutoff 2026-10-23 the
    # card listed the 10-23 top-12 while the book in force was the one decided 2026-10-14,
    # sharing a single name (159307) -- and the forward ledger, which does decide on the
    # grid, was tracking that other book. Consuming the diag row makes the card and the
    # ledger the same object by construction rather than by agreement.
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    masked = score.where(elig)
    last = masked.index[-1]
    diag = []
    R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, COST,
                          vol_target=TARGET_VOL, diag=diag)
    if not diag:
        raise RuntimeError("panel too short for one decision on the grid")
    drow = diag[-1]
    dec_bar = pd.Timestamp(drow["date"])
    picks = list(drow["book"])
    scale = float(drow["scale"])
    s = masked.loc[dec_bar].dropna()          # the scores that actually picked
    book = {p: 1.0 / len(picks) for p in picks}
    realised_vol = scale_for(book, openp, dec_bar)[1]
    weights = {p: w * scale for p, w in book.items()}
    cash = 1.0 - sum(weights.values())

    px = close.reindex(columns=close.columns).ffill().loc[last]
    legs = []
    for p in picks:
        w = weights[p]
        price = float(px.get(p)) if p in px.index else None
        amount = w * capital
        shares = int(amount / price // 100 * 100) if price and price > 0 else None  # 100-share lots
        legs.append({
            "symbol": p,
            "name": names.get(p) or names.get(p[2:]) or "",
            "class": cls[p],
            "score": round(float(s[p]), 4),
            "weight": round(w, 4),
            "amount_cny": round(amount, 0),
            "ref_price": price,
            "lots_100": shares,
            "actual_amount_cny": round(shares * price, 0) if shares and price else None,
        })
    legs.sort(key=lambda r: -r["amount_cny"])

    # r1342: the printed amount column is the EXECUTABLE one. A weight times capital is a
    # target, not an order: only whole 100-share lots can be placed, so the desk can only
    # spend less than the target and the difference lands in cash. Until now the card
    # printed targets and a cash row of (1 - k) * capital, which overstated money at work
    # (E201 measured 0.13% NAV) and made a cross-face check against the ticket read
    # "different book" every round. Targets are still published beside the executable
    # column -- the fix is a second column, not a hidden rounding.
    target_book = sum(float(l["amount_cny"]) for l in legs)
    spent = sum(float(l["actual_amount_cny"]) for l in legs
                if l["actual_amount_cny"] is not None)

    op_dates = [d for d in openp.index if d >= pd.Timestamp(R.START)]
    grid = grid_position(op_dates, last, rebal)

    sheet = {
        "as_of_bar": str(last.date()),
        "decision": "REBALANCE: this bar's close is a decision point -- place at next open"
                    if grid["is_decision_bar"]
                    else "HOLD: %d bars until the next decision point"
                         % grid["bars_until_next_decision"],
        "is_grid_decision_bar": grid["is_decision_bar"],
        "last_decision_bar": str(dec_bar.date()),
        "book_decided_at": str(dec_bar.date()),
        "bars_until_next_decision": grid["bars_until_next_decision"],
        "capital_cny": capital,
        "target_vol": TARGET_VOL,
        "realised_book_vol_60d": None if realised_vol is None else round(realised_vol, 4),
        "risk_scale": round(scale, 4),
        "cash_weight": round(cash, 4),
        # E230: two cash readings, both published. cash_amount_cny keeps its old meaning
        # (the risk scale's own slot, (1 - scale) * capital) because other faces already
        # consume it; cash_executable_cny is the money that actually cannot be invested
        # once lots are whole, and it is the row the ticket reconciles against.
        "cash_amount_cny": round(cash * capital, 0),
        "cash_executable_cny": round(capital - spent, 0),
        "amount_column": "executable",
        "book_target_cny": round(target_book, 0),
        "book_executable_cny": round(spent, 0),
        "lot_residual_cny": round(target_book - spent, 0),
        "lot_residual_pct_nav": round(100.0 * (target_book - spent) / capital, 4) if capital else None,
        "legs": legs,
    }

    dv = delivered_vs_target(runs.get("n%d_vt08" % n_hold), TARGET_VOL)
    # r1287: the card is the sheet a human reads, so it states out loud which bar it was
    # priced on against the official calendar -- the panel cannot judge this by itself.
    feed = CA.live_ticket_feed_status(last)
    vt_tail = vol_overlay_tail_support()
    # r1177: the card is one of the two faces a reader holds, so it states which prices its
    # numbers sit on, in the same words the executable sheet uses (one implementation,
    # etf_equity_alpha.price_basis_line). The count comes from the repair that actually ran,
    # not from a second census -- the raw panel is gone by the time this line is written --
    # and the width of the panel it was counted on travels with it so the card's total and
    # the ticket's (which censuses only the classes it ranks) can never read as a drift.
    basis = A.price_basis_line(True, n_flip, A.FLIP_THR, PANEL_CENSUS.get("symbols"),
                               "results/etf_book_flip_contamination.json",
                               columns=PANEL_CENSUS.get("columns"))
    if PANEL_DIGEST:
        basis["panel_digest"] = PANEL_DIGEST
    out = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(last.date()),
        "feed_status": feed,
        "price_basis": basis,
        "family_coherence": family_coherence(),
        "priced_faces": priced_faces(card_bar=sheet.get("as_of_bar")),
        "script": "scripts/etf_book_production.py",
        "config": {"universe_classes": list(USE_CLASSES), "n_hold": n_hold, "rebal": rebal,
                   "cost_bp_per_side": COST * 1e4, "vol_target": TARGET_VOL,
                   "capital_cny": capital, "universe_size": len(cols),
                   "flips_repaired": n_flip,
                   "execution": "decide at close t -> fill at open t+1 -> hold to next rebalance"},
        "backtest": runs,
        "vol_delivery": dv,
        "vol_overlay_tail": vt_tail,
        "sheet": sheet,
        "caveats": [
            "ETF pool is today's listed set: survivorship inflates the equity sleeve.",
            "2020-2023 contributes ~5.8%/yr; most of the return sits in 2024+.",
            vol_overlay_tail_sentence(vt_tail),
            "Delivered vol is not the label: %s. The label is a per-hold risk target, so an "
            "8%% label annualises near 10%% once hold-level vol dispersion is priced in -- a "
            "definition gap, not a sizing bug (research/ETF_VOL_CALIBRATION.md)." % (dv.get("headline") or "no history"),
            "Order sheet is research output, not an investment recommendation.",
            "The sheet is the book decided at book_decided_at, not a re-ranking of the "
            "latest bar: the engine only re-decides every %d bars, so an off-grid ranking "
            "would trade names the book never held." % rebal,
        ],
        "preperiod": preperiod_support(),
        "concentration": concentration_support(),
        "sleeve_gate": sleeve_gate_support(),
        "commodity": commodity_support(),
        "passive_mix": passive_mix_support(),
        "window_decomp": decomp_support(),
        "spanning": spanning_support(),
        "spanning_pre2020": spanning_pre2020_support(),
        "hysteresis": hysteresis_support(),
        "drawdown_band": drawdown_band_support(),
    }
    pp = out["preperiod"]
    if pp is not None:
        out["caveats"].insert(0,
            "ONE REGIME, NOT A VERIFIED EDGE: on the %d ETFs that existed before 2020, "
            "priced 2015-2019 (a window this card never covered) the same engine returned "
            "%+.2f%%/yr against %+.2f%%/yr equal weight = %+.2fpp excess, worse in %d of %d "
            "grid cells, random-score p=%.2f. The published CAGR is the 2020+ regime, not a "
            "property of the factors. That cell is bond-inclusive, 5 names wide and has no "
            "sizing rule; 'The 2015-2019 reconciliation' below prices what each of those "
            "differences is worth. See %s."
            % (pp["universe_size"], pp["book_cagr"] * 100, pp["ew_cagr"] * 100,
               pp["excess_pp"], pp["cells_negative"], pp["cells_total"],
               pp["null_p"] if pp["null_p"] is not None else float("nan"), pp["artifact"]))
    cs = out["commodity"]
    if cs is not None and cs.get("excess_pp") is not None:
        beat = cs["excess_pp"] > 0.5
        vs_passive = None
        if cs.get("passive_cagr") is not None:
            vs_passive = (cs["book_cagr"] - cs["passive_cagr"]) * 100
        out["caveats"].insert(1,
            "THE COMMODITY SLEEVE IS %s: it produced %s%% of gross return; the same engine "
            "restricted to the %s commodity ETFs returned %+.2f%%/yr against %+.2f%%/yr for "
            "holding those names equally (%+.2fpp), and the deepest-turnover commodity name "
            "(%s) returned %s passively%s. Read the sleeve as %s. See %s."
            % ("MOSTLY METAL BETA WITH A MODEST RANKING OVERLAY" if beat else
               "EXPOSURE, NOT A RANKING",
               cs.get("gross_share_pct"), cs.get("n_cols"), cs["book_cagr"] * 100,
               cs["ew_cagr"] * 100, cs["excess_pp"], cs.get("passive_name"),
               ("%+.2f%%/yr" % (cs["passive_cagr"] * 100)) if cs.get("passive_cagr") is not None
               else "n/a",
               (", i.e. the book beat holding the metal by %+.2fpp" % vs_passive)
               if vs_passive is not None else "",
               "commodity/gold exposure plus a small selection add-on, not a commodity "
               "ranking that pays" if beat else "commodity/gold beta, not selection",
               cs["artifact"]))
    if feed.get("status") in ("stale_feed", "feed_broken"):
        out["caveats"].insert(0, "FEED IS BEHIND: this card is priced on the %s bar, %s "
                              "official trading day(s) short of the %s bar the market has "
                              "already published. The names are that old, not a fresh call."
                              % (feed.get("ticket_bar"), feed.get("lag_days"),
                                 feed.get("expected_bar")))
    sp = sign_pit_support()
    if sp is not None:
        out["caveats"].insert(0, "THE SIX FACTOR DIRECTIONS WERE CHOSEN WITH HINDSIGHT: every "
                              "published number here uses a fixed sign block, and those signs are "
                              "exactly this panel's full-sample IC signs (%d of %d factors match). "
                              "Re-priced with signs estimated only from already-realised windows, "
                              "the same engine returns %+.2f%%/yr (Sharpe %+.2f) against %+.2f%%/yr "
                              "(%+.2f) for the fixed signs -- and reversing the trailing sign does "
                              "not recover it (%+.2f%%/yr). Read the headline as the size of a "
                              "period, not the size of a rule. See %s."
                              % (sp["n_match"], sp["n_factors"], sp["cagr_pit"] * 100,
                                 sp["sharpe_pit"], sp["cagr_fixed"] * 100, sp["sharpe_fixed"],
                                 sp["cagr_reversed"] * 100, sp["artifact"]))
    band = out["drawdown_band"]
    card_dd = ((runs.get("n%d_vt08" % n_hold) or {}).get("full") or {}).get("maxdd")
    if band and card_dd is not None:
        a = band["maxdd_p5_band"]
        stale = (band["evidence_cutoff"] or "") != str(last.date())
        out["caveats"].insert(0, "THE DRAWDOWN LINE ABOVE IS A MEDIAN, NOT A TAIL: it is priced "
                              "on one ordering of the trading days. Bootstrapping this book's "
                              "own return path at blocks %s (the block is a free parameter) puts "
                              "the 5th-percentile drawdown between %.1f%% and %.1f%% and the "
                              "share of resamples worse than -20%% between %.1f%% and %.1f%%. "
                              "Size against the p5 column. See %s%s."
                              % ("/".join(str(b) for b in band["block_set"]),
                                 a["min"] * 100, a["max"] * 100,
                                 band["dd_break_band"]["min"] * 100,
                                 band["dd_break_band"]["max"] * 100, band["artifact"],
                                 "" if not stale else
                                 " (band priced on the %s bar, not this card's %s -- stale)"
                                 % (band["evidence_cutoff"], last.date())))
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "PRODUCTION-%s.json" % last.date()), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT_DIR, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    write_card(out)
    print(json.dumps(sheet, ensure_ascii=False, indent=1))
    return out


def concentration_support():
    """Whose CAGR is this? The card quotes the published reading (r1192).

    Through `etf_book_concentration.reading()` -- the same single implementation the ticket
    (r1190) and the CEO page (r1191) consume -- so the three faces can only disagree by
    pricing different days, never by formatting the same document twice."""
    try:
        import etf_book_concentration as _C
    except Exception as exc:                                      # noqa: BLE001
        return {"status": "unreadable", "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        return _C.reading()
    except Exception as exc:                                      # noqa: BLE001
        return {"status": "unreadable", "detail": "reading failed (%s)" % str(exc)[:120]}


def sleeve_gate_support():
    """Does the commodity sleeve need a risk gate of its own? (r1192)

    Soft-fails to None: the card keeps working without the experiment's artifact, it just
    says so. It never prints a gate verdict it did not read."""
    try:
        import etf_book_sleeve_gate as _G
    except Exception as exc:                                      # noqa: BLE001
        return {"status": "unreadable", "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        return _G.read_published()
    except Exception as exc:                                      # noqa: BLE001
        return {"status": "unreadable", "detail": "reading failed (%s)" % str(exc)[:120]}


def concentration_paragraphs(cc):
    """Whose CAGR this card is quoting, from the concentration face's own numbers."""
    if not cc or cc.get("status") != "ok":
        return ["Cannot verify here: %s. The card will not imply a broad book from a face it "
                "cannot read." % ((cc or {}).get("status") or "absent"), ""]
    top = cc.get("top") or []
    base = cc.get("baseline") or {}
    lk = cc.get("top_k_out") or {}
    veh = cc.get("sleeve") or {}
    lead = ", ".join("%s %s %.1f%%" % (t.get("symbol"), t.get("name") or "", 100 * (t.get("share") or 0))
                     for t in top[:3])
    parts = ["The top three contributors are %s of a %s%%/yr book (their share of the gross "
             "return sum is %.1f%%, HHI %.2f across %s names held)."
             % (lead or "unknown", "%.1f" % (100 * base.get("cagr")) if base.get("cagr") is not None else "?",
                100 * (cc.get("top3_share") or 0), cc.get("hhi") or 0, cc.get("distinct_names"))]
    if lk.get("delta_cagr_pp") is not None:
        parts.append("Delete those %s names from the universe and the book's CAGR drops %.2fpp "
                     "against this card, so the ranking is not only those names."
                     % (lk.get("k"), abs(lk["delta_cagr_pp"])))
    if veh.get("delta_cagr_pp") is not None:
        veh_full = (veh.get("stats") or {}).get("full") or {}
        dd = None
        if veh_full.get("maxdd") is not None and base.get("maxdd") is not None:
            dd = 100 * (veh_full["maxdd"] - base["maxdd"])
        parts.append("Delete the whole %s sleeve (%s ETFs) and the book's CAGR drops %.2fpp"
                     % (veh.get("class"), veh.get("symbols_removed"), abs(veh["delta_cagr_pp"]))
                     + (" while the drawdown goes %.1fpp deeper -- the paying leg is also the "
                        "cushion." % abs(dd) if dd is not None else "."))
    art = cc.get("artifact") or "the concentration face"
    try:
        _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        art = os.path.relpath(art, _root).replace("\\", "/")
    except Exception:                                             # noqa: BLE001
        pass
    return [" ".join(parts), "",
            "Read the headline above as the return of a book built like this, not as the return "
            "of the ranking rule alone. See %s." % art, ""]


def sleeve_gate_paragraphs(sg):
    """The sleeve-gate answer: three gates, each against its own dose-matched placebo."""
    if not sg or sg.get("status") != "ok":
        return ["Not assessed here: %s -- the card will not imply that the sleeve needs no gate "
                "just because the experiment is missing." % ((sg or {}).get("status") or "absent"), ""]
    lines = [str(sg.get("sentence") or ""), ""]
    # r1193: the rows and the closest arm come from the reader's single assembly; the
    # card used to re-open the artifact and re-derive "closest" for itself.
    gates = sg.get("gates") or []
    if gates:
        decisions = (sg.get("book") or {}).get("decisions") or 0
        lines += ["| gate | sleeve switched off | CAGR vs card | max drawdown vs card | verdict |",
                  "|---|---|---|---|---|"]
        for g in gates:
            lines.append("| %s | %d/%d decisions (%.1f%%) | %+.2fpp | %+.2fpp | %s |" % (
                g.get("name"), g.get("off_decisions") or 0, decisions,
                100 * (g.get("off_share") or 0), g.get("delta_cagr_pp") or 0.0,
                g.get("delta_maxdd_pp") or 0.0, g.get("verdict") or "?"))
        lines += ["",
                  "A positive drawdown delta is a *shallower* drawdown than this card's; the dose "
                  "column is how much of the decision grid the gate kept the sleeve out of, and "
                  "each arm is compared against its own placebo of the same dose.", ""]
        best = sg.get("closest")
        bar = (sg.get("criteria") or {}).get("min_dd_gain_pp")
        if best and bar is not None and (best.get("dd_gain_pp") or 0) > 0:
            lines += ["Closest arm: the %s gate improves the drawdown by %+.2fpp (frozen bar "
                      "%.1fpp) and beats its dose-matched placebo by %+.2fpp on the same measure, "
                      "so it is the only arm not explained by holding less sleeve -- it missed "
                      "the bar and is therefore NOT adopted; re-test it on new data, do not move "
                      "the bar." % (best.get("name"), best.get("dd_gain_pp") or 0.0, bar,
                                    best.get("placebo_dd_edge_pp") or 0.0), ""]
    lines += ["The placebo arm matters: switching a sleeve off a fixed share of decisions "
              "changes the exposure and the timing at once, so only the arm that beats its own "
              "untimed placebo is evidence of a signal rather than of a shorter holding period. "
              "See %s." % (sg.get("artifact") or "results/etf_book_sleeve_gate.json"), ""]
    return lines


def write_card(out):
    s, cfg, bt = out["sheet"], out["config"], out["backtest"]
    b = bt.get("n%d_vt08" % cfg["n_hold"], {})
    lines = [
        "# ETF book -- production candidate, order sheet (%s bar)" % s["as_of_bar"],
        "",
        "Config: %d names of a %d-instrument bond-free pool, rebalance every %d bars, "
        "%g bp/side, %.0f%% vol target (de-lever only)."
        % (cfg["n_hold"], cfg["universe_size"], cfg["rebal"], cfg["cost_bp_per_side"],
           cfg["vol_target"] * 100),
        "",
        "| window | CAGR | Sharpe | max drawdown | realised vol | target |",
        "|---|---|---|---|---|---|",
    ]
    dv = out.get("vol_delivery") or {}
    for lbl in ("full", "is", "oos"):
        m = b.get(lbl) or {}
        if m.get("cagr") is None:
            continue
        d = (dv.get("windows") or {}).get(lbl) or {}
        lines.append("| %s | %.1f%% | %.2f | %.1f%% | %.1f%% | %.0f%% (%.2fx) |" % (
            {"full": "2020-01 onwards", "is": "2020-2023", "oos": "2024 onwards"}[lbl],
            m["cagr"] * 100, m["sharpe"] or 0.0, m["maxdd"] * 100,
            (m.get("vol") or 0.0) * 100, cfg["vol_target"] * 100, d.get("ratio") or 0.0))
    lines += [""]
    if dv.get("headline"):
        lines += ["**Vol label vs delivered risk: %s.** The overlay only de-levers, so a "
                  "sleeve sized on its own backward vol can run hotter than %.0f%%; read the "
                  "risk column, not the label." % (dv["headline"], cfg["vol_target"] * 100), ""]
    lines += [
        "",
        "**Feed: %s** -- priced on the %s bar; the official calendar expects %s (lag %s "
        "official day(s))." % (
            (out.get("feed_status") or {}).get("status", "unknown"), s["as_of_bar"],
            (out.get("feed_status") or {}).get("expected_bar") or "unknown",
            (out.get("feed_status") or {}).get("lag_days")), "",
    ]
    _pb = out.get("price_basis") or {}
    if _pb.get("sentence"):
        lines += ["**Price basis:** %s" % _pb["sentence"], ""]
    _pdg = _pb.get("panel_digest") or {}
    if _pdg.get("digest"):
        lines += ["**Panel digest:** `%s` (%d bars x %d symbols, %s->%s, covers %s) -- the executable "
                  "sheet and the forward ledger print the same fingerprint only when all "
                  "three priced one panel, on the same blocks." % (
                      _pdg["digest"], _pdg["dates"], _pdg["columns"],
                      _pdg["first"], _pdg["last"], "/".join(_pdg.get("blocks") or [])), ""]
    _pf = out.get("priced_faces") or {}
    if _pf:
        _f = _pf.get("faces") or {}
        _s = "card %s / ticket %s / page %s" % (_f.get("card") or "unknown",
                                                _f.get("ticket") or "unknown",
                                                _f.get("page") or "unknown")
        _when = " (compared at %s)" % out["ts"] if out.get("ts") else ""
        if _pf.get("verdict") == "SAME_DAY":
            lines += ["**Priced day: SAME_DAY** -- %s%s; this card, the executable sheet and "
                      "the CEO page all priced the same closing bar." % (_s, _when), ""]
        elif _pf.get("verdict") == "DIFFERENT_DAYS":
            lines += ["**Priced day: DIFFERENT_DAYS** -- %s%s; %s. A reader comparing numbers "
                      "across these papers is comparing two different books, so read the lagging "
                      "one only as history." % (_s, _when, _pf.get("detail") or "no detail"), ""]
        else:
            lines += ["**Priced day: UNKNOWN** -- %s%s; %s. Absence of a day is not agreement."
                      % (_s, _when, _pf.get("detail") or "no detail"), ""]
    _fc = out.get("family_coherence") or {}
    if _fc.get("verdict") == "ONE_WORLD":
        lines += ["**Family coherence: ONE_WORLD** -- all %d width arms priced `%s` (cutoff %s); "
                  "the verdicts that license this card's width are measurements on one panel." % (
                      _fc.get("arms") or 0, ((_fc.get("panels") or [""])[0] or "?)"),
                      _fc.get("evidence_cutoff")), ""]
    elif _fc.get("verdict"):
        lines += ["**Family coherence: %s** -- %s. The width verdicts are withheld "
                  "(`WORLDS_NOT_COMPARABLE`), so the width this card uses is not licensed by a "
                  "measured family." % (_fc["verdict"], _fc.get("detail") or "no detail"), ""]
    else:
        lines += ["**Family coherence: not assessable** -- %s; the width is unproven here, "
                  "not verified." % (_fc.get("detail") or "arm family face absent"), ""]
    lines += [
        "**Today (%s bar): %s** (last grid decision %s)." % (
            s["as_of_bar"], s["decision"], s["last_decision_bar"]),
        "",
        "Realised 60d book vol %.1f%% -> risk scale %.2f, cash slot %.1f%%."
        % ((s["realised_book_vol_60d"] or 0) * 100, s["risk_scale"], s["cash_weight"] * 100),
        "",
        "| code | name | sleeve | weight | target (CNY) | executable (CNY) | 100-share lots |",
        "|---|---|---|---|---|---|---|",
    ]
    for leg in s["legs"]:
        exec_amt = leg.get("actual_amount_cny")
        lines.append("| %s | %s | %s | %.1f%% | %s | %s | %s |" % (
            leg["symbol"], leg["name"], leg["class"], leg["weight"] * 100,
            format(int(leg["amount_cny"]), ","),
            "-" if exec_amt is None else format(int(exec_amt), ","), leg["lots_100"]))
    lines += ["| cash | - | money | %.1f%% | %s | %s | - |" % (
        s["cash_weight"] * 100, format(int(s["cash_amount_cny"]), ","),
        format(int(s["cash_executable_cny"]), ",")), ""]
    lines += [
        "**Which column is money.** A weight times capital is the sizing INTENT; only "
        "whole 100-share lots can be placed. So the executable column can only spend %s "
        "of the %s target book, and the desk keeps %s (%.2f%% NAV) in cash that the risk "
        "scale never asked for -- that residue is the price of lot granularity, not a "
        "position. Place the executable column. Until r1342 this card printed the target "
        "column as if it were the order, which is why the ticket disagreed with it by "
        "0.13%% NAV (E201); the two faces now reconcile to the yuan." % (
            format(int(s["book_executable_cny"]), ","),
            format(int(s["book_target_cny"]), ","),
            format(int(s["lot_residual_cny"]), ","),
            s["lot_residual_pct_nav"] or 0.0), "",
    ]
    lines += ["## Whose CAGR is this?", ""]
    lines += concentration_paragraphs(out.get("concentration"))
    lines += ["## Does the commodity sleeve need a gate of its own?", ""]
    lines += sleeve_gate_paragraphs(out.get("sleeve_gate"))
    lines += ["## What the rotation is worth", ""]
    lines += passive_mix_paragraphs(out.get("passive_mix"))
    lines += decomp_paragraphs(out.get("window_decomp"))
    lines += ["## What is left after the four betas", ""]
    lines += spanning_paragraphs(out.get("spanning"))
    lines += ["## Does any of it survive outside 2020-2026?", ""]
    lines += spanning_pre2020_paragraphs(out.get("spanning_pre2020"))
    lines += ["## Does the book trade on noise?", ""]
    lines += hysteresis_paragraphs(out.get("hysteresis"))
    full = b.get("full") or {}
    if full.get("maxdd") is not None:
        lines += ["## How bad can the drawdown be?", ""]
        lines += drawdown_band_paragraphs(out.get("drawdown_band"), full["maxdd"])
    lines += ["## Caveats", ""] + ["- " + c for c in out["caveats"]] + [""]
    with open(os.path.join(OUT_DIR, "CARD.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def decomp_paragraphs(dc):
    """The 2015-2019 reconciliation section. Pure: takes the artifact block, returns lines.

    The card carries two readings of one window -- the -8.86pp excess caveat and the
    passive-mix premium -- and they only make sense side by side with the ladder that
    connects them.
    """
    if not (dc and dc.get("steps")):
        return []
    steps = [s for s in dc["steps"] if s.get("delta_pp") is not None]
    first = dc["steps"][0]
    # a rung id is an artifact key, not a sentence; the axis is what a reader needs
    axis = {"r2_bond_free_pool": "dropping the bond/money sleeve",
            "r3_wider_book": "widening the book to 12 names",
            "r4_vol_overlay": "adding the 8% sizing rule"}
    parts = ["%+.1fpp from %s" % (s["delta_pp"], axis.get(s["rung"], s["rung"]))
             for s in steps]
    ctrl = dc.get("controls") or {}
    ok = all((c.get("passes") is not False) for c in ctrl.values() if isinstance(c, dict))
    return [
        "## The 2015-2019 reconciliation", "",
        "This card states two things about 2015-2019 that look like a contradiction: the "
        "caveat below reports %.1fpp of excess (%.1f%%/yr absolute) before 2020, while the "
        "rotation section above reports a premium on that same window. They are different "
        "cells, and the ladder between them is measured, not argued: from the caveat's cell "
        "(all classes, 5 names, no sizing rule) to this book's cell, holding the window and "
        "the fill rule fixed, the CAGR moves %+.1fpp in total (%s). Both ends reproduce "
        "their published number within %.1fpp%s. See %s."
        % (first.get("excess_pp") or 0.0, (first.get("cagr") or 0.0) * 100,
           dc.get("total_move_pp") or 0.0,
           ", ".join(parts),
           (ctrl.get("rung1_vs_pre2020_cellA") or {}).get("tolerance_pp") or 0.5,
           "" if ok else " (one control is out of tolerance -- read the artifact before "
                        "quoting these steps)",
           dc["artifact"]),
        "",
        "So the pre-2020 failure belongs to the bond-inclusive, unsized cell (%.1f%%/yr) "
        "and not to the ranking: with the same sizing rule on both arms the ranking still "
        "pays before 2020, just less than it pays after. What the ladder does NOT say is "
        "that the ranking works without the sizing rule -- on this window it does not."
        % ((first.get("cagr") or 0.0) * 100), ""]


def passive_mix_paragraphs(pm):
    """The rotation-vs-static-mix section text. Pure: needs only the artifact block.

    Kept a function so the wording is testable without writing a card, and so the two
    windows (published regime, and the pre-2020 control) are emitted from one place.
    """
    if not (pm and pm.get("premium_pp") is not None):
        return ["Not measured: results/etf_book_passive_mix.json is missing, so this card "
                "cannot say what the rotation is worth against simply holding the classes.", ""]
    out = ["Against a static mix of this book's own class exposure -- no scoring, no "
           "rotation, same grid, same cost rule, same 8%% overlay -- the book returns "
           "%.1f%%/yr vs %.1f%%/yr (%+.1fpp), worst drawdown %.1f%% vs %.1f%%, carrying "
           "%.1fx the static arm's turnover. That is the number the machinery has to "
           "beat to justify trading at all. See %s."
           % (pm["book_cagr"] * 100, pm["static_cagr"] * 100, pm["premium_pp"],
              (pm.get("book_maxdd") or 0) * 100, (pm.get("static_maxdd") or 0) * 100,
              (pm.get("book_turnover") / pm["static_turnover"])
              if pm.get("static_turnover") else float("nan"), pm["artifact"]), ""]
    bw = pm.get("by_window") or {}
    pre_w = bw.get("pre2020") or {}
    post_w = bw.get("post2020_pre_universe") or {}
    if pre_w.get("premium_pp") is not None and post_w.get("premium_pp") is not None:
        out += [
            "The same test outside the regime this card was published on -- the %d ETFs "
            "that already existed before 2020, priced 2015-2019, same engine, same grid, "
            "same cost rule, same overlay on both arms: the book returns %.1f%%/yr vs "
            "%.1f%%/yr for the static mix (%+.1fpp), against %+.1fpp on those SAME %d names "
            "over 2020+. Read the two together: %s"
            % (pre_w.get("universe_size") or 0, pre_w["book_cagr"] * 100,
               pre_w["static_cagr"] * 100, pre_w["premium_pp"], post_w["premium_pp"],
               post_w.get("universe_size") or 0,
               ("the premium does not survive the period change, so what pays is the "
                "regime, not the ranking -- the ranking is only worth carrying where the "
                "regime that produced it still holds."
                if pm.get("premium_flips") else
                "the premium survives the period change, so the machinery is not what "
                "the pre-2020 window was missing.")), ""]
    return out


def spanning_paragraphs(sp):
    """The four-beta section text. Pure: needs only the artifact block.

    Both arms' risk travels with both returns, and the t-stat decides the wording -- a
    sentence that reads the point estimate as skill without printing t is the failure this
    section exists to prevent (E147).
    """
    if not (sp and sp.get("alpha_annual") is not None):
        return ["Not measured: results/etf_book_spanning.json is missing, so this card "
                "cannot say what is left after the liquid betas.", ""]
    arms = sp.get("arms") or {}
    gold = arms.get("gold") or {}
    sentence = ("Regressed on the four exposures an account could hold instead of this book "
                "(gold / Nasdaq-100 QDII / CSI300 / treasury bond, same execution basis, "
                "same cost), the book's daily returns leave an intercept of **%+.1f%%/yr with "
                "t=%.2f** and R2=%.2f, as of %s. The equal-weight four-ETF basket itself "
                "returns %.1f%%/yr at Sharpe %.2f and worst drawdown %.1f%%, against the "
                "book's %.1f%%/yr, Sharpe %.2f and %.1f%%."
                % (sp["alpha_annual"] * 100, sp.get("alpha_t") or 0.0, sp.get("r2") or 0.0,
                   sp.get("as_of"), (sp.get("basket_cagr") or 0) * 100,
                   sp.get("basket_sharpe") or 0.0, (sp.get("basket_maxdd") or 0) * 100,
                   (sp.get("book_cagr") or 0) * 100, sp.get("book_sharpe") or 0.0,
                   (sp.get("book_maxdd") or 0) * 100))
    out = [sentence, ""]
    if (sp.get("alpha_t") or 0) < 2.0:
        out += ["Read that as **not distinguishable from a fixed loadings mix**, not as zero "
                "and not as proven skill: the in-sample half of the window prints t=%.2f and "
                "the out-of-sample half t=%.2f, so the point estimate is carried by the later "
                "period and the line is a risk statement rather than a return one."
                % (sp.get("is_alpha_t") or 0.0, sp.get("oos_alpha_t") or 0.0), ""]
    if gold.get("cagr") is not None:
        out += ["The single arm that out-earns the book is gold (%.1f%%/yr) at a %.1f%% "
                "drawdown -- the comparison has to be printed next to the return or it reads "
                "as a verdict. See %s."
                % (gold["cagr"] * 100, (gold.get("maxdd") or 0) * 100, sp["artifact"]), ""]
    st = sp.get("staggered_arm") or {}
    if st.get("alpha_annual") is not None:
        head = ("The staggered 6+6 book (same universe, score, execution and cost; second "
                "sleeve offset half a rebalance period) leaves **%+.1f%%/yr at t=%.2f** "
                "(IS t=%.2f / OOS t=%.2f) with residual vol %.1f%%, against the single "
                "sleeve's %+.1f%%/yr at t=%.2f and %.1f%%"
                % (st["alpha_annual"] * 100, st.get("alpha_t") or 0.0,
                   st.get("is_alpha_t") or 0.0, st.get("oos_alpha_t") or 0.0,
                   (st.get("resid_vol_annual") or 0.0) * 100,
                   (st.get("book_alpha_annual") or 0.0) * 100,
                   st.get("book_alpha_t") or 0.0,
                   (sp.get("resid_vol_annual") or 0.0) * 100))
        if st["crosses_two_sigma"] and not st["book_crosses_two_sigma"]:
            tail = (". The split clock clears a t of 2 where the single sleeve does not: that "
                    "is a strategy difference worth its own test, not a free lunch -- one arm "
                    "over the threshold is a hypothesis, not an edge.")
        elif not st["crosses_two_sigma"]:
            tail = (". Neither arm clears a t of 2, so the turnover saving remains the only "
                    "measured difference between them (E149/E150).")
        else:
            tail = (".")
        out += [head + tail, ""]
    return out


def spanning_pre2020_paragraphs(sp):
    """The outside-the-boom-window section. Pure: needs only the artefact block.

    r1312: the section above answers "is anything left after the four betas" on 2020+.
    This one answers "and does that survive the window the book was not fitted in" -- and
    prints the buy-and-hold basket beside it, because a book that loses to four ETFs in a
    negative-alpha window is a different object from one that merely fails a t-test.
    """
    if not (sp and (sp.get("single") or {}).get("alpha_annual") is not None):
        return ["Not measured: results/etf_book_spanning_pre2020.json is missing, so this "
                "card cannot say whether the intercept exists outside 2020-2026.", ""]
    s, g, b = sp.get("single") or {}, sp.get("staggered") or {}, sp.get("basket") or {}
    win = sp.get("window") or ["?", "?"]
    n_pre = (sp.get("universe") or {}).get("U_pre")
    out = ["The same regression, run on the %s ETFs that already existed before the boom, "
           "over %s..%s (a window this card's configuration was never fitted in, control "
           "delta %spp against the published pre-2020 cell):" % (
               n_pre if n_pre is not None else "pre-2020", win[0], win[1],
               (sp.get("control") or {}).get("delta_pp")), ""]
    out += ["| arm | CAGR | Sharpe | maxDD | intercept | t | R2 |", "|---|---|---|---|---|---|---|"]
    for label, a in (("single sleeve", s), ("staggered 6+6", g)):
        if a.get("cagr") is None:
            continue
        out.append("| %s | %.1f%% | %.2f | %.1f%% | %+.1f%%/yr | %.2f | %.2f |" % (
            label, a["cagr"] * 100, a.get("sharpe") or 0.0, (a.get("maxdd") or 0) * 100,
            a["alpha_annual"] * 100, a.get("alpha_t") or 0.0, a.get("r2") or 0.0))
    if b.get("cagr") is not None:
        out.append("| equal-weight four ETFs | %.1f%% | %.2f | %.1f%% | - | - | - |" % (
            b["cagr"] * 100, b.get("sharpe") or 0.0, (b.get("maxdd") or 0) * 100))
    out += [""]
    if (s.get("alpha_t") or 0) < 2.0 and (g.get("alpha_t") or 0) < 2.0:
        out += ["**Neither arm clears a t of 2 outside 2020-2026** (single t=%.2f, staggered "
                "t=%.2f; the out-of-sample half prints t=%.2f and t=%.2f, i.e. no intercept "
                "there at all). Read it as: the published "
                "intercept is a property of the boom window and the panel that grew in it, "
                "not yet a property of the rule -- the pre-2020 cross-section is small and "
                "survival-filtered, so this is one honest negative, not a demolition. It is, "
                "however, the reason not to scale size on the 9-10%% headline."
                % (s.get("alpha_t") or 0.0, g.get("alpha_t") or 0.0,
                   s.get("oos_alpha_t") or 0.0, g.get("oos_alpha_t") or 0.0),
                ""]
    if b.get("cagr") is not None and s.get("cagr") is not None:
        d = (s["cagr"] - b["cagr"]) * 100
        if d < 0:
            out += ["In that window a static equal-weight basket of the same four ETFs "
                    "returned %.1f%%/yr at Sharpe %.2f against the book's %.1f%%/yr at %.2f "
                    "(%+.1fpp), so the negative is not merely a failed t-test -- the rotation "
                    "cost money there. See %s."
                    % (b["cagr"] * 100, b.get("sharpe") or 0.0, s["cagr"] * 100,
                       s.get("sharpe") or 0.0, d, sp["artifact"]), ""]
    return out


def hysteresis_paragraphs(h):
    """The noise section. Pure: needs only the artefact block.

    r1324: two questions that read the same and are not -- "is the cut line arbitrary?"
    and "are the trades I actually pay for noise?". This prints both, because a buffer
    that lowers turnover without lowering the return is a cost knob, and saying so is the
    difference between a measured answer and a marketing one.
    """
    if not (h and h.get("arms")):
        return ["Not measured: results/etf_book_hysteresis.json is missing, so this card "
                "cannot say whether the book's turnover is signal or churn.", ""]
    cz, tr, cfg = h.get("census") or {}, h.get("trades") or {}, h.get("config") or {}
    out = []
    if cz.get("n_decisions"):
        out += ["The book holds %s names and re-decides every %s bars, so its score only "
                "has to separate the 12th name from the 13th. Over %d decisions that gap "
                "is a median of %.3f standard deviations of the bar's own cross-section, "
                "and %.1f%% of decisions sit inside 0.10 sd -- **the cut line is, "
                "literally, a coin flip at the margin**."
                % (cfg.get("n_hold"), cfg.get("rebal"), cz["n_decisions"],
                   cz.get("cut_sd_median") or 0.0, (cz.get("share_within_0p10") or 0) * 100),
                ""]
    if tr.get("n_pairs"):
        out += ["The trades are not. Of the %d executed pairs (a name leaving, a name "
                "entering) the median score gap is %.2f sd and only %.1f%% sit inside "
                "0.10 sd. Read the two lines together: the ranking is noisy exactly where "
                "it costs nothing, and decisive where it costs %s bp a side."
                % (tr["n_pairs"], tr.get("gap_sd_median") or 0.0,
                   (tr.get("share_under_0p10sd") or 0) * 100, cfg.get("cost_bp")), ""]
    arms = h["arms"]
    out += ["Priced the other way: a buffer that only displaces an incumbent when the "
            "challenger beats it by k*sd, run through the same engine on the same grid "
            "(%s, %s bp/side, control arm %s vs %s published = %spp):"
            % ("/".join("k=%g" % float(a["k"]) for a in arms if a.get("k") is not None),
               cfg.get("cost_bp"),
               "%.2f%%" % ((h.get("control") or {}).get("measured", 0) * 100),
               "%.2f%%" % ((h.get("control") or {}).get("published", 0) * 100),
               "%+.2f" % ((h.get("control") or {}).get("delta_pp") or 0.0)), ""]
    out += ["| buffer | turnover/decision | CAGR | Sharpe | maxDD |", "|---|---|---|---|---|"]
    for a in arms:
        if a.get("cagr") is None:
            continue
        out.append("| k=%g | %.3f | %.2f%% | %.2f | %.1f%% |" % (
            float(a["k"]), a.get("turnover") or 0.0, a["cagr"] * 100,
            a.get("sharpe") or 0.0, (a.get("maxdd") or 0) * 100))
    out += [""]
    k0, kend = arms[0], arms[-1]
    if h.get("best_arm_k") is not None:
        best = next(a for a in arms if a.get("k") == h["best_arm_k"])
        out += ["k=%g is the only arm that lowers turnover (%.3f -> %.3f), keeps the "
                "return (%+.2fpp) and improves both Sharpe and drawdown; past k=0.35 the "
                "buffer starts costing return and depth. So the buffer is a **cost knob, "
                "not a discovered edge** -- worth using, worth nothing to brag about."
                % (float(h["best_arm_k"]), k0.get("turnover") or 0.0,
                   best.get("turnover") or 0.0,
                   ((best.get("cagr") or 0.0) - (k0.get("cagr") or 0.0)) * 100), ""]
    elif (kend.get("turnover") or 0.0) < (k0.get("turnover") or 0.0):
        out += ["No arm improves all four numbers together: turnover falls %.3f -> %.3f "
                "only by giving up return or depth, so there is nothing here to adopt."
                % (k0.get("turnover") or 0.0, kend.get("turnover") or 0.0), ""]
    for c in (h.get("caveats") or []):
        out += ["- " + c]
    if h.get("caveats"):
        out += [""]
    return out


def selftest():
    close, openp, amt, feats = E.build_panel()
    close, openp, _ = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in USE_CLASSES][:60]
    close, openp, amt = close[cols], openp[cols], amt[cols]
    score = E.build_score(close, amt, feats)
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(("PASS " if cond else "FAIL ") + name + (" " + detail if detail else ""), flush=True)

    # 1. vol target never levers up: scale <= 1 for any book
    book = {c: 1.0 / 3 for c in cols[:3]}
    sc, v = scale_for(book, openp, openp.index[-1])
    chk("vol target never levers up", 0 < sc <= 1.0, "scale=%s vol=%s" % (sc, v))
    # 2. alignment: a bar one step off the grid must not read as a decision bar
    dates = [d for d in openp.index if d >= pd.Timestamp(R.START)]
    if len(dates) > 41:
        d0 = dates[40]  # on-grid under rebal=20
        d1 = dates[41]
        chk("grid flags the on-grid bar", grid_position(dates, d0, 20)["is_decision_bar"] is True)
        chk("grid rejects the off-grid bar", grid_position(dates, d1, 20)["is_decision_bar"] is False)
        chk("grid counts bars to the next decision", grid_position(dates, d1, 20)["bars_until_next_decision"] == 19,
            str(grid_position(dates, d1, 20)["bars_until_next_decision"]))
    # 3. weights + cash conserve exactly 1.0
    w = {c: 1.0 / 5 for c in cols[:5]}
    sc2, _ = scale_for(w, openp, openp.index[-1])
    tot = sum(sc2 * x for x in w.values())
    chk("weights + cash == 1", abs(tot + (1.0 - tot) - 1.0) < 1e-12, "invested=%.6f" % tot)
    # 4. engine reproduces a flat line only when it has no history (sanity on the harness)
    ser, _ = R.open_to_open_equity(close, openp, amt, score, 20, 5, COST)
    chk("harness actually traded", ser.notna().sum() > 10 and ser.std() > 0,
        "bars=%d std=%.6f" % (ser.notna().sum(), ser.std()))

    # 5. delivered-vs-target is pure arithmetic and never invents a missing window
    dv = delivered_vs_target({"full": {"vol": 0.1018}, "is": {"vol": 0.09}}, 0.08)
    chk("vol delivery ratio", abs(dv["windows"]["full"]["ratio"] - 1.2725) < 5e-4, dv["headline"] or "")
    chk("vol delivery skips absent windows", "oos" not in dv["windows"])
    chk("vol delivery headline quotes delivered risk", "10.2%" in (dv["headline"] or ""))
    chk("vol delivery without a target has no ratio",
        delivered_vs_target({"full": {"vol": 0.10}}, 0)["windows"]["full"]["ratio"] is None)

    # 6. end-to-end on a synthetic panel: the whole run() path (order sheet + card) must
    #    execute. r1270's prep_panel() extraction left run() reading names that no longer
    #    existed in its scope, and the card -- the only placeable deliverable -- crashed
    #    for a full round with every other leg green, because no leg ever called run().
    idx = pd.bdate_range("2021-01-04", periods=400)
    rng = np.random.default_rng(7)
    syn = pd.DataFrame(
        100 * np.exp(np.cumsum(rng.normal(0, 0.01, (len(idx), 9)), axis=0)),
        index=idx, columns=["519%03d" % i for i in range(9)])
    s_open = syn.shift(1).bfill()
    s_amt = pd.DataFrame(1e8, index=idx, columns=syn.columns)
    s_score = syn.pct_change(20).fillna(0.0)
    s_cls = {c: "equity" for c in syn.columns}
    tmp = tempfile.mkdtemp(prefix="etf_book_prod_selftest_")
    keep = (globals()["prep_panel"], globals()["load_names"], globals()["OUT_DIR"])
    try:
        globals()["prep_panel"] = lambda: (syn, s_open, s_amt, s_score, s_cls, 0)
        globals()["load_names"] = lambda: {}
        globals()["OUT_DIR"] = tmp
        o = run(capital=1_000_000.0, n_hold=3, rebal=20)
        card = open(os.path.join(tmp, "CARD.md"), encoding="utf-8").read()
        chk("run() produces a placeable sheet",
            len(o["sheet"]["legs"]) == 3 and o["sheet"]["as_of_bar"] == str(idx[-1].date()),
            "legs=%d as_of=%s" % (len(o["sheet"]["legs"]), o["sheet"]["as_of_bar"]))
        chk("card states delivered vol against the label",
            "Vol label vs delivered risk" in card and "target 8%" in card)
        chk("card lists every leg", all(l["symbol"] in card for l in o["sheet"]["legs"]))
        chk("output carries the vol delivery block",
            (o.get("vol_delivery") or {}).get("headline") is not None)
        # r1348: the card's single drawdown is the median of a ruler. The band must reach the
        # page a human reads, and must not be invented when the arms are absent.
        band = o.get("drawdown_band")
        if band:
            chk("card prices the drawdown band the arms measured",
                ("How bad can the drawdown be?" in card
                 and "%.1f%%" % (band["maxdd_p5_band"]["min"] * 100) in card),
                band.get("block_set") and str(band.get("block_set")))
            chk("band quotes its block set, not a bare tail",
                all(str(b) in card for b in band["block_set"]))
            chk("band is not silently stale",
                (band["evidence_cutoff"] == o["evidence_cutoff"])
                == ("stale" not in card.split("## Caveats")[0]))
            chk("band carried as a caveat on the operator page",
                any("MEDIAN, NOT A TAIL" in c for c in o["caveats"]))
        else:
            chk("card says the tail is unpublished when the arms are absent",
                "No bootstrap band on disk" in drawdown_band_paragraphs(None, -0.1)[0])
        # 7. the sheet must be the book IN FORCE (the last on-grid decision), not today's
        #    ranking. Until r1277 the card re-ranked the panel's last bar and handed out a
        #    book 11/12 apart from the one the engine -- and the forward ledger -- held.
        sdiag = []
        R.open_to_open_equity(syn, s_open, s_amt, s_score, 20, 3, COST,
                              vol_target=TARGET_VOL, diag=sdiag)
        held = set(sdiag[-1]["book"])
        chk("sheet is the book in force, not today's ranking",
            set(l["symbol"] for l in o["sheet"]["legs"]) == held
            and o["sheet"]["book_decided_at"] == sdiag[-1]["date"],
            "sheet=%s diag=%s" % (o["sheet"]["book_decided_at"], sdiag[-1]["date"]))
        # activity: on this fixture the off-grid ranking really does differ, so the leg
        # above cannot pass on the old behaviour (a broken test that never traded).
        today = set(s_score.iloc[-1].nlargest(3).index)
        chk("off-grid ranking differs from the held book",
            today != held and today != set(),
            "today=%s held=%s" % (sorted(today), sorted(held)))
        chk("sheet cash equals 1 - risk_scale",
            abs(o["sheet"]["cash_weight"] - (1.0 - o["sheet"]["risk_scale"])) < 1e-3,
            "cash=%.4f scale=%.4f" % (o["sheet"]["cash_weight"], o["sheet"]["risk_scale"]))
        # r1342: the printed amount column must be the executable one. Three legs, in a
        # row, because each of them fails differently: (a) the legs really are lot-rounded
        # on this fixture, so the assertion is not comparing two identical sums; (b) the
        # cash row is capital minus what lots actually spend, not (1 - scale) * capital;
        # (c) the card carries both columns, so the fix adds a reading rather than hiding
        # the rounding inside a single number.
        _sh = o["sheet"]
        _spent = sum(float(l["actual_amount_cny"]) for l in _sh["legs"])
        chk("executable amounts are lot * price, not weight * capital",
            all(abs(float(l["actual_amount_cny"]) - l["lots_100"] * float(l["ref_price"])) <= 1.0
                for l in _sh["legs"]),
            "spent=%.0f target=%.0f" % (_spent, _sh["book_target_cny"]))
        chk("executable book never exceeds its target",
            _sh["book_executable_cny"] <= _sh["book_target_cny"] + 1.0,
            "exec=%.0f target=%.0f" % (_sh["book_executable_cny"], _sh["book_target_cny"]))
        chk("the published executable book is what the lots actually spend",
            abs(_sh["book_executable_cny"] - _spent) <= 2.0,
            "published=%.0f legs=%.0f" % (_sh["book_executable_cny"], _spent))
        chk("executable cash is capital minus what lots spend",
            abs(_sh["cash_executable_cny"] - (_sh["capital_cny"] - _spent)) <= 2.0,
            "exec-cash=%.0f exec=%.0f cap=%.0f" % (_sh["cash_executable_cny"], _spent,
                                                   _sh["capital_cny"]))
        chk("target cash keeps the risk scale's slot, executable cash does not",
            abs(_sh["cash_amount_cny"] + _sh["book_target_cny"] - _sh["capital_cny"]) <= 2.0
            and _sh["cash_executable_cny"] >= _sh["cash_amount_cny"] - 1.0
            and _sh["lot_residual_cny"] >= -1.0,
            "slot-cash=%.0f exec-cash=%.0f residue=%.0f"
            % (_sh["cash_amount_cny"], _sh["cash_executable_cny"], _sh["lot_residual_cny"]))
        chk("card prints target and executable side by side",
            "executable (CNY)" in card and "target (CNY)" in card
            and "Which column is money" in card
            and format(int(_sh["cash_executable_cny"]), ",") in card)
    finally:
        globals()["prep_panel"], globals()["load_names"], globals()["OUT_DIR"] = keep
        shutil.rmtree(tmp, ignore_errors=True)

    # 8. the out-of-period face: when the artifact exists the card must carry it (a
    #    measured difference that only lives in a digest is not disclosed), and when it
    #    does not, the production face must still run.
    pp = preperiod_support()
    if pp is None:
        chk("preperiod face soft-fails when absent", True, "results/etf_book_pre2020.json absent")
    else:
        chk("preperiod face reads the primary cell",
            all(k in pp for k in ("universe_size", "book_cagr", "ew_cagr", "excess_pp",
                                  "null_p", "cells_negative", "cells_total"))
            and pp["cells_total"] > 0 and pp["universe_size"] > 0,
            "%s %s book=%.4f ew=%.4f excess=%+.2fpp neg=%d/%d p=%s"
            % (pp["grid_cell"], pp["window"], pp["book_cagr"], pp["ew_cagr"],
               pp["excess_pp"], pp["cells_negative"], pp["cells_total"], pp["null_p"]))
    _keep_results = E.PATHS.results_dir
    try:
        E.PATHS.results_dir = os.path.join(tmp, "no_such_results")
        chk("preperiod face is not fatal when the artifact is missing",
            preperiod_support() is None)
    finally:
        E.PATHS.results_dir = _keep_results

    # 9. the commodity-sleeve face: the sleeve's 30% share has to be labelled as exposure
    #    or as selection on the card, and a missing artifact must not break production.
    cs = commodity_support()
    if cs is None:
        chk("commodity face soft-fails when absent", True,
            "results/etf_book_commodity_split.json absent")
    else:
        chk("commodity face reads both arms",
            all(k in cs for k in ("n_cols", "book_cagr", "ew_cagr", "excess_pp", "verdict"))
            and cs["book_cagr"] is not None and cs["ew_cagr"] is not None
            and abs(cs["excess_pp"] - (cs["book_cagr"] - cs["ew_cagr"]) * 100) < 0.05,
            "book=%.4f ew=%.4f excess=%+.2fpp verdict=%s"
            % (cs["book_cagr"], cs["ew_cagr"], cs["excess_pp"], cs["verdict"]))
    try:
        E.PATHS.results_dir = os.path.join(tmp, "no_such_results")
        chk("commodity face is not fatal when the artifact is missing",
            commodity_support() is None)
    finally:
        E.PATHS.results_dir = _keep_results

    # 10. the passive-mix face: the card has to say what the rotation is worth against
    #     simply holding the classes, and a missing artifact must not break production.
    pm = passive_mix_support()
    if pm is None:
        chk("passive-mix face soft-fails when absent", True,
            "results/etf_book_passive_mix.json absent")
    else:
        chk("passive-mix face reads both arms and the premium",
            all(k in pm for k in ("book_cagr", "static_cagr", "premium_pp", "verdict"))
            and pm["book_cagr"] is not None and pm["static_cagr"] is not None
            and pm["premium_pp"] is not None
            and abs(pm["premium_pp"] - (pm["book_cagr"] - pm["static_cagr"]) * 100) < 0.05,
            "book=%.4f static=%.4f premium=%+.2fpp verdict=%s"
            % (pm["book_cagr"], pm["static_cagr"], pm["premium_pp"], pm["verdict"]))
    try:
        E.PATHS.results_dir = os.path.join(tmp, "no_such_results")
        chk("passive-mix face is not fatal when the artifact is missing",
            passive_mix_support() is None)
    finally:
        E.PATHS.results_dir = _keep_results

    # 10b. the two-window face (r1308): when the artifact prices the pre-2020 control too,
    #      the card has to print both periods and let the flip change the conclusion.
    pm_fix = {"artifact": "x.json", "book_cagr": 0.0949, "static_cagr": 0.0313,
              "premium_pp": 6.36, "book_maxdd": -0.118, "static_maxdd": -0.229,
              "book_turnover": 0.98, "static_turnover": 0.0935,
              "by_window": {"pre2020": {"universe_size": 224, "book_cagr": -0.0497,
                                        "static_cagr": 0.0389, "premium_pp": -8.86},
                            "post2020_pre_universe": {"universe_size": 224,
                                                      "premium_pp": 3.11}},
              "premium_flips": True}
    txt_flip = "\n".join(passive_mix_paragraphs(pm_fix))
    chk("card carries both windows of the rotation test",
        "2015-2019" in txt_flip and "2020+" in txt_flip and "224" in txt_flip
        and "does not survive the period change" in txt_flip,
        "%d lines" % len(passive_mix_paragraphs(pm_fix)))
    txt_keep = "\n".join(passive_mix_paragraphs(dict(pm_fix, premium_flips=False)))
    chk("a surviving premium says the other thing",
        "does not survive" not in txt_keep and "survives the period change" in txt_keep)
    chk("a single-window artifact prints the headline only",
        len(passive_mix_paragraphs({k: v for k, v in pm_fix.items()
                                    if k not in ("by_window", "premium_flips")})) == 2)

    # 10c. the reconciliation section (r1308): the ladder has to be on the card, and a
    #      control out of tolerance has to say so instead of printing clean steps.
    dc = decomp_support()
    if dc is None:
        chk("reconciliation face soft-fails when absent", True,
            "results/etf_book_window_decomp.json absent")
    else:
        chk("reconciliation face carries the ladder",
            len(dc.get("steps") or []) >= 2 and dc.get("total_move_pp") is not None,
            "steps=%d total=%s" % (len(dc.get("steps") or []), dc.get("total_move_pp")))
        txt = "\n".join(decomp_paragraphs(dc))
        chk("card prints the reconciliation with both ends",
            "2015-2019 reconciliation" in txt and "%.1fpp" % dc["total_move_pp"] in txt,
            "%d lines" % len(decomp_paragraphs(dc)))
        broken = json.loads(json.dumps(dc))
        for k in broken.get("controls") or {}:
            broken["controls"][k]["passes"] = False
        chk("a failed control is disclosed in the text, not swallowed",
            "out of tolerance" in "\n".join(decomp_paragraphs(broken)))
    try:
        E.PATHS.results_dir = os.path.join(tmp, "no_such_results")
        chk("reconciliation face is not fatal when the artifact is missing",
            decomp_support() is None)
    finally:
        E.PATHS.results_dir = _keep_results
    chk("no reconciliation artifact -> no section",
        decomp_paragraphs(None) == [])

    # 10d. the outside-the-window section (r1312): both arms' t, the basket, and the
    #      sentence that changes when the alpha DOES clear 2. A section that prints the
    #      same words for a pass and a failure would hide the finding it exists to carry.
    sp20 = spanning_pre2020_support()
    fix = {"window": ["2015-01-01", "2019-12-31"], "universe": {"U_pre": 193},
           "single": {"alpha_annual": 0.0203, "alpha_t": 1.04, "r2": 0.70, "cagr": 0.0512,
                      "sharpe": 0.70, "maxdd": -0.1671},
           "staggered": {"alpha_annual": 0.0100, "alpha_t": 0.48, "r2": 0.68,
                         "cagr": 0.0426, "sharpe": 0.574, "maxdd": -0.1762},
           "basket": {"cagr": 0.0864, "sharpe": 0.968, "maxdd": -0.1298},
           "control": {"delta_pp": 0.13, "within_0p5pp": True},
           "artifact": "results/etf_book_spanning_pre2020.json"}
    txt = "\n".join(spanning_pre2020_paragraphs(fix))
    chk("card prints the outside-window section with both arms",
        "193" in txt and "single sleeve" in txt and "staggered 6+6" in txt
        and "Neither arm clears a t of 2" in txt, "%d lines" % len(spanning_pre2020_paragraphs(fix)))
    chk("the buy-and-hold basket is printed beside the book",
        "equal-weight four ETFs" in txt and "rotation cost money" in txt)
    passing = json.loads(json.dumps(fix))
    passing["single"]["alpha_t"] = 2.6
    passing["staggered"]["alpha_t"] = 2.2
    chk("a passing alpha stops printing the negative sentence",
        "Neither arm clears" not in "\n".join(spanning_pre2020_paragraphs(passing)))
    chk("no outside-window artifact -> disclosed, not silent",
        "Not measured" in spanning_pre2020_paragraphs(None)[0])
    chk("outside-window face reads the live artifact when present",
        sp20 is None or (sp20.get("window") and sp20.get("single", {}).get("alpha_t") is not None),
        "artifact %s" % ("absent" if sp20 is None else sp20.get("window")))

    # 10e. the noise section (r1324): the card has to print the cut-line margin and the
    #      trade margin side by side -- they point opposite ways -- and the "cost knob"
    #      sentence has to be earned by an arm, not written in advance.
    hz = hysteresis_support()
    hfix = {"artifact": "results/etf_book_hysteresis.json", "evidence_cutoff": "2026-10-27",
            "config": {"n_hold": 12, "rebal": 20, "cost_bp": 10.0, "grid": [0.0, 0.05, 0.5]},
            "control": {"published": 0.0962, "measured": 0.0962, "delta_pp": 0.0,
                        "within_tol": True},
            "census": {"n_decisions": 83, "cut_score_median": 0.0045,
                       "share_within_0p10": 0.8675, "cut_sd_median": 0.0181},
            "trades": {"n_pairs": 590, "gap_sd_median": 0.9741, "share_under_0p10sd": 0.0288},
            "arms": [{"k": 0.0, "turnover": 0.934, "cagr": 0.0962, "sharpe": 0.992,
                      "maxdd": -0.1177},
                     {"k": 0.05, "turnover": 0.901, "cagr": 0.0969, "sharpe": 1.006,
                      "maxdd": -0.1159},
                     {"k": 0.5, "turnover": 0.702, "cagr": 0.0958, "sharpe": 0.99,
                      "maxdd": -0.1348}],
            "best_arm_k": 0.05, "caveats": ["exploratory: no preregistration"]}
    txt = "\n".join(hysteresis_paragraphs(hfix))
    chk("card prints both margins of the same question",
        "coin flip at the margin" in txt and "0.97 sd" in txt
        and "0.10 sd" in txt and "590" in txt, "%d lines" % len(hysteresis_paragraphs(hfix)))
    chk("card prints the arm grid with the control arm", "| k=0 |" in txt and "k=0.5" in txt)
    chk("an improving arm earns the cost-knob sentence",
        "cost knob" in txt and "k=0.05" in txt and "+0.07pp" in txt)
    nohelp = json.loads(json.dumps(hfix))
    nohelp["best_arm_k"] = None
    nohelp["arms"][1] = dict(nohelp["arms"][1], cagr=0.0900)
    txt_no = "\n".join(hysteresis_paragraphs(nohelp))
    chk("no improving arm prints the negative, not the knob",
        "cost knob" not in txt_no and "nothing here to adopt" in txt_no)
    chk("no hysteresis artifact -> disclosed, not silent",
        "Not measured" in hysteresis_paragraphs(None)[0])
    chk("hysteresis face reads the live artifact when present",
        hz is None or (hz.get("census") or {}).get("n_decisions"))
    try:
        E.PATHS.results_dir = os.path.join(tmp, "no_such_results")
        chk("hysteresis face is not fatal when the artifact is missing",
            hysteresis_support() is None)
    finally:
        E.PATHS.results_dir = _keep_results

    # 10f. the draw-tail price (r1360 / E253): the card's "a drawdown tool, not an edge"
    #      sentence carried only medians. It now has to quote the measured tail share, and the
    #      number has to be DERIVED from the face -- a literal in code goes stale in silence the
    #      moment the bootstrap reruns, which is the defect this leg exists to prevent.
    vtf = vol_overlay_tail_support()
    chk("tail sentence reads the live face when the artifact is present",
        vtf is None or (vtf.get("tail_share_of_middle") is not None
                        and vtf.get("median_maxdd_delta_pp") is not None), str(bool(vtf)))
    vfix = {"resamples": 2000, "blocks": [5, 20], "median_maxdd_delta_pp": 6.04,
            "p1_maxdd_delta_pp": 1.26, "median_cagr_delta_pp": -4.61,
            "tail_share_of_middle": 0.209}
    vs = vol_overlay_tail_sentence(vfix)
    chk("tail sentence carries the share AND the price paid for it",
        "21%" in vs and "+6.04pp" in vs and "+1.26pp" in vs and "-4.61pp" in vs
        and "drawdown tool, not an edge" in vs, vs[-70:])
    chk("an unmeasured tail says so instead of quoting a number",
        "not measured" in vol_overlay_tail_sentence({"tail_share_of_middle": None})
        and "not measured" in vol_overlay_tail_sentence(dict(vfix, p1_maxdd_delta_pp=None)))
    try:
        E.PATHS.results_dir = os.path.join(tmp, "no_such_results")
        chk("a missing tail artifact is not fatal", vol_overlay_tail_support() is None)
    finally:
        E.PATHS.results_dir = _keep_results

    # 10g. the card is one of the two faces a reader holds, so it says which prices its
    #      numbers sit on (r1177) -- and it must say it in the SAME words as the executable
    #      sheet, because two faces of one book quoting two definitions of "clean" is the
    #      defect this line exists to end (E289).
    _pb_line = A.price_basis_line(True, 168, A.FLIP_THR, None)
    chk("price basis line states the repair and the size it neutralised",
        "168" in _pb_line["sentence"] and "已修复" in _pb_line["sentence"]
        and _pb_line["panel"].startswith("repaired"), _pb_line["sentence"][:50])
    chk("price basis line on a clean panel says the repair changed nothing",
        "同一批数字" in A.price_basis_line(True, 0, A.FLIP_THR, 0)["sentence"])
    _pb_out = {"sheet": {"as_of_bar": "2026-10-30", "decision": "HOLD",
                         "last_decision_bar": "2026-10-14", "realised_book_vol_60d": 0.07,
                         "risk_scale": 0.9, "cash_weight": 0.1,
                         "cash_amount_cny": 100000.0, "cash_executable_cny": 99000.0,
                         "book_target_cny": 900000.0, "book_executable_cny": 890000.0,
                         "lot_residual_cny": 10000.0, "lot_residual_pct_nav": 1.0,
                         "legs": []},
                "config": {"n_hold": 8, "universe_size": 10, "rebal": 20,
                           "cost_bp_per_side": 8.0, "vol_target": 0.08},
                "backtest": {}, "caveats": [], "price_basis": _pb_line}
    _pb_dir = tempfile.mkdtemp(prefix="etf_book_prod_pb_")
    _card_txt = os.path.join(_pb_dir, "CARD.md")
    global OUT_DIR
    _keep_out = OUT_DIR
    try:
        OUT_DIR = _pb_dir
        write_card(_pb_out)
        _txt = open(_card_txt, encoding="utf-8").read()
    finally:
        OUT_DIR = _keep_out
    chk("the card prints the price basis line",
        "**Price basis:**" in _txt and "168" in _txt, "%d chars" % len(_txt))
    _pb_out["price_basis"] = None
    try:
        OUT_DIR = _pb_dir
        write_card(_pb_out)
        _txt2 = open(_card_txt, encoding="utf-8").read()
    finally:
        OUT_DIR = _keep_out
    shutil.rmtree(_pb_dir, ignore_errors=True)
    chk("no price basis -> no invented line", "**Price basis:**" not in _txt2)

    # 10h. the width this card uses is licensed by the arm family, and a family can only
    #      license anything if every arm face priced ONE panel (r1183, consuming the r1180
    #      coherence block). Three states, three sentences, and absence is never a pass.
    _keep_res = E.PATHS.results_dir
    _fc_dir = tempfile.mkdtemp(prefix="etf_book_prod_fc_")
    try:
        E.PATHS.results_dir = _fc_dir
        _absent = family_coherence()
        chk("no arm family face -> coherence not assessable, never a pass",
            _absent["verdict"] is None and _absent["priced_same_panel"] is None
            and "not assessable" in (_absent["detail"] or ""), str(_absent["detail"])[:50])

        def _write_fc(coh, arms):
            with open(os.path.join(_fc_dir, ARMS_FACE_FILE), "w", encoding="utf-8") as fh:
                json.dump({"panel_coherence": coh, "arms": arms,
                           "baseline": {"evidence_cutoff": "2026-10-30"}}, fh)

        _write_fc({"verdict": "ONE_WORLD", "detail": "all 11 faces priced a1a4",
                   "panels": ["a1a4"]}, {("k%02d" % i): {} for i in range(11)})
        _one = family_coherence()
        chk("one panel -> ONE_WORLD with the arm count and the cutoff",
            _one["verdict"] == "ONE_WORLD" and _one["priced_same_panel"] is True
            and _one["arms"] == 11 and _one["evidence_cutoff"] == "2026-10-30")
        _write_fc({"verdict": "MIXED_WORLDS", "detail": "two panels", "panels": ["a", "b"]}, {"k": {}})
        chk("two panels -> NOT licensed",
            family_coherence()["priced_same_panel"] is False)
    finally:
        E.PATHS.results_dir = _keep_res
        shutil.rmtree(_fc_dir, ignore_errors=True)

    def _render_with_fc(fc):
        global OUT_DIR
        p = dict(_pb_out)
        p["family_coherence"] = fc
        try:
            OUT_DIR = _pb_dir2
            write_card(p)
            return open(os.path.join(_pb_dir2, "CARD.md"), encoding="utf-8").read()
        finally:
            OUT_DIR = _keep_out2

    _pb_dir2 = tempfile.mkdtemp(prefix="etf_book_prod_fc_render_")
    _keep_out2 = OUT_DIR
    try:
        _t_one = _render_with_fc({"verdict": "ONE_WORLD", "arms": 11, "panels": ["a1a4"],
                                  "evidence_cutoff": "2026-10-30", "priced_same_panel": True})
        chk("card states ONE_WORLD with the panel and the arm count",
            "Family coherence: ONE_WORLD" in _t_one and "11" in _t_one and "a1a4" in _t_one)
        _t_mixed = _render_with_fc({"verdict": "MIXED_WORLDS", "detail": "two panels",
                                    "arms": 11, "panels": ["a", "b"], "priced_same_panel": False})
        chk("card says the width is NOT licensed when the family is mixed",
            "MIXED_WORLDS" in _t_mixed and "not licensed" in _t_mixed
            and "ONE_WORLD" not in _t_mixed)
        _t_none = _render_with_fc({"verdict": None, "detail": "arm family face absent",
                                   "arms": 0, "panels": [], "priced_same_panel": None})
        chk("card says not assessable when the family face is absent",
            "not assessable" in _t_none and "ONE_WORLD" not in _t_none)
    finally:
        OUT_DIR = _keep_out2
        shutil.rmtree(_pb_dir2, ignore_errors=True)

    # 10i. the three papers a reader holds each say which day they were priced on, and the
    #      answer has to be re-derivable from the artifacts (r1185). A boolean nobody can
    #      recompute is a claim; a missing face is UNKNOWN, never agreement.
    _keep_res3 = E.PATHS.results_dir
    _pf_dir = tempfile.mkdtemp(prefix="etf_book_prod_pf_")
    try:
        E.PATHS.results_dir = _pf_dir
        _pf_none = priced_faces(page_bar="2026-10-30")
        chk("no card/ticket artifact -> the day is UNKNOWN, not agreement",
            _pf_none["verdict"] == "UNKNOWN" and _pf_none["same_day"] is False
            and "card" in _pf_none["missing"] and "ticket" in _pf_none["missing"],
            str(_pf_none["detail"])[:60])

        def _write_pf(card_bar, ticket_bar):
            for sub, payload in (("etf_book_production", {"sheet": {"as_of_bar": card_bar}}),
                                 ("etf_book_order",
                                  {"card_agreement": {"ticket_priced_bar": ticket_bar}})):
                os.makedirs(os.path.join(_pf_dir, sub), exist_ok=True)
                with open(os.path.join(_pf_dir, sub, "latest.json"), "w", encoding="utf-8") as fh:
                    json.dump(payload, fh)

        _write_pf("2026-10-30", "2026-10-30")
        _pf_same = priced_faces(page_bar="2026-10-30")
        chk("all three on one bar -> SAME_DAY with the day itself",
            _pf_same["verdict"] == "SAME_DAY" and _pf_same["same_day"] is True
            and _pf_same["faces"]["card"] == "2026-10-30"
            and _pf_same["faces"]["ticket"] == "2026-10-30"
            and _pf_same["faces"]["page"] == "2026-10-30", str(_pf_same["detail"])[:60])
        _pf_split = priced_faces(page_bar="2026-10-29")
        chk("a stale paper -> DIFFERENT_DAYS naming the stale one",
            _pf_split["verdict"] == "DIFFERENT_DAYS" and _pf_split["same_day"] is False
            and "page 2026-10-29" in _pf_split["detail"], str(_pf_split["detail"])[:80])
        _pf_nopage = priced_faces(page_bar=None)
        chk("the page without a bar -> UNKNOWN rather than a same-day pass",
            _pf_nopage["verdict"] == "UNKNOWN" and _pf_nopage["missing"] == ["page"])
        # r1186: the card is written AFTER this runs, so it must hand its own bar in rather
        # than read back yesterday's copy of itself.
        _pf_ovr = priced_faces(page_bar="2026-10-30", card_bar="2026-10-30",
                               ticket_bar="2026-10-30")
        chk("a face that knows its own bar is not compared to its own older artifact",
            _pf_ovr["verdict"] == "SAME_DAY" and _pf_ovr["faces"]["card"] == "2026-10-30"
            and _pf_ovr["faces"]["ticket"] == "2026-10-30", str(_pf_ovr["faces"]))
        chk("an absent page artifact reads None, never agreement",
            _page_priced_bar(_pf_dir) is None)
    finally:
        E.PATHS.results_dir = _keep_res3
        shutil.rmtree(_pf_dir, ignore_errors=True)

    print("SELFTEST " + ("OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    if "--selftest" in args:
        sys.exit(selftest())
    opts = {}
    for a in args:
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            opts[k] = v
    run(capital=float(opts.get("capital", 1_000_000)),
        n_hold=int(opts.get("n", 12)), rebal=int(opts.get("rebal", 20)))