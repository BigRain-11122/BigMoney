#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Six smoke legs that had no command anyone could run, each given one.

r2091b mapped the suite's 647 literal legs: 322 are inline blocks (only the whole suite
can re-ask them) and six of those were red with no check entry at all.  This script
gives each of the six a check entry that reads the SAME published faces the suite reads.

Two things are deliberately different from the suite block:

* every leg is split into a pure ``judge_*`` that takes parsed documents and returns
  ``(ok, detail)``, so a negative control can prove it goes red on a doctored payload
  instead of trusting that "it ran";
* ``--selftest`` builds a synthetic GREEN payload per leg and then breaks exactly one
  field, asserting the judge flips to ``False`` -- a leg that cannot be made red is not
  a guard (r1282 / r1935 family).

``run`` prints one line per leg and writes ``results/smoke_inline_leg_checks.<id>.json``.
Exit 0 = all six re-asked and green, 1 = at least one leg red, 2 = mechanism failure.
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
for _p in (ROOT, SCRIPTS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

SCHEMA = "smoke-inline-leg-checks/v1"
DECLARED_ZH = "起点是声明，不是成交"          # positions page, long form
DECLARED_ZH_SHORT = "声明，不是成交"          # CEO page, the r1361 shorthand
TOLL_ZH = "再买一手要上调 k"


def _p(*parts):
    return os.path.join(ROOT, *parts)


def _read_json(path):
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def _read_text(path):
    try:
        with io.open(path, encoding="utf-8") as fh:
            return fh.read()
    except Exception:
        return ""


def machine_id():
    try:
        return (_read_json(_p("fleet", "machine.json")) or {}).get("machine_id") or "unknown"
    except Exception:
        return "unknown"


# ---------------------------------------------------------------- judges (pure) ---
def judge_declared_starting_book(pos, md, ceo_md):
    """The starting book is declared or traded -- and both pages say which."""
    if not pos:
        return False, "results/etf_book_positions.json missing or unreadable"
    base = (pos or {}).get("next_order_base") or {}
    trans = (pos or {}).get("transition") or {}
    want = None
    if trans and str(trans.get("bar") or "") == str(base.get("bar") or ""):
        if trans.get("status") == "UNEXPLAINED_TARGET_WITHOUT_TRADES":
            want = "declared"
        elif trans.get("status") == "EXPLAINED":
            want = "traded"
    bad = []
    if base and (base.get("arrival") or None) != want:
        bad.append("base arrival %r but the transition says %r"
                   % (base.get("arrival"), want))
    if want == "declared":
        if DECLARED_ZH not in (md or ""):
            bad.append("the positions page does not name the declared starting book")
        if ceo_md is not None and DECLARED_ZH_SHORT not in ceo_md:
            bad.append("the CEO page does not name it either")
    detail = "; ".join(bad[:3]) or "arrival %s on bar %s" % (
        base.get("arrival") or "unknown", base.get("bar"))
    return (not bad), detail


def judge_ceo_page_prose(rc, detail):
    """zh_page_prose_census answers; this leg only carries its verdict."""
    return (rc == 0), str(detail)


def judge_card_track(doc):
    """The paper book owns the book the card sells (asks the producer's own gate)."""
    if not doc:
        return False, "results/etf_book_card_track.json missing or unreadable"
    from scripts import etf_book_card_track as _ct
    ag = doc.get("agreement") or {}
    dr = doc.get("drift") or {}
    code, word = _ct.gate_exit(ag, dr, doc.get("card_ticket"))
    ok = doc.get("schema") == "etf-book-card-track/v1" and code == 0
    detail = ("agrees=%s decision_bar=%s wt_maxdiff=%s navdev=%s gate=%s(rc%d) drift=%s"
              % (ag.get("agrees"), ag.get("ledger_decided_bar"),
                 ag.get("max_weight_diff"), dr.get("nav_identity_max_dev"),
                 word, code, dr.get("reason") or "-"))
    return ok, detail


def judge_order_sheet_floor(kg, ptr, md):
    """The order sheet prints the floor's per-name cut, not only its total."""
    if not kg or not md:
        return False, "no published k-gap face or no published ORDER page"
    if str(kg.get("bar")) != str((ptr or {}).get("as_of")):
        return False, "k-gap face is %s, the sheet is %s" % (
            kg.get("bar"), (ptr or {}).get("as_of"))
    rows = all((str(r.get("symbol")) in md
                and format(float(r.get("short_cny") or 0.0), ",.2f") in md
                and ("%.4fpp" % float(r.get("next_lot_dk_pp") or 0.0)) in md)
               for r in kg.get("rows") or [])
    cheap = kg.get("cheapest_next_lot") or {}
    ok = bool(kg.get("rows")) and rows and TOLL_ZH in md and str(cheap.get("symbol")) in md
    return ok, ("%d row(s) printed, cheapest next lot %s"
                % (len(kg.get("rows") or []), cheap.get("symbol"))
                if ok else "sheet does not print the per-name rows the k-gap face publishes")


def judge_toll_ladder(doc, arms):
    """The toll-ladder verdict re-derives from the arm faces it names."""
    t = (doc or {}).get("toll_ladder") or {}
    if not t:
        return False, "results/etf_book_atlas_toll_ladder.json has no toll_ladder block"
    ok = (t.get("rungs") or 0) >= 2 and bool(t.get("spread_pp"))
    lv = []
    off = []
    for row in (t.get("argmax_cells") or []):
        src = (arms or {}).get(row.get("file"))
        if src is None:
            ok = False
            off.append("%s: arm face missing" % (row.get("file"),))
            continue
        meds = [c["median_cagr_pp"] for c in (src.get("per_cell") or [])]
        lv.append(round(max(meds) - min(meds), 3) if meds else None)
    rows_ = t.get("argmax_cells") or []
    for row, pub, got in zip(rows_, t.get("spread_pp") or [], lv):
        if got is None or pub is None or abs(float(pub) - float(got)) > 1e-6:
            off.append("%s: ladder spread %s pp, arms re-derive %s pp"
                       % (row.get("file"), pub, got))
    ok = ok and bool(lv) and all(
        a is not None and b is not None and abs(a - b) < 1e-6
        for a, b in zip(lv, t.get("spread_pp") or []))
    if off:
        ok = False
    if t.get("verdict") == "ORDERING_IS_A_TOLL_ARTEFACT":
        ok = (ok and t.get("break_even_toll_bp") is not None
              and t.get("spread_at_production_toll_pp") is not None
              and t.get("band_at_production_toll_pp") is not None
              and t["spread_at_production_toll_pp"]
              <= t["band_at_production_toll_pp"] + 1e-9
              and (t.get("spread_rank_corr_with_toll") or 0) <= -0.90)
    b = (doc or {}).get("buffer_ladder") or {}
    if b.get("verdict") == "SINGLE_RUNG_CROSSING_IS_ONE_DRAW":
        ok = ok and b.get("n_clearing_rungs") == 1
    elif b.get("verdict") == "CROSSINGS_WITHOUT_DOSE":
        ok = ok and (b.get("n_clearing_rungs") or 0) >= 2
    detail = ("verdict=%s break_even=%s rungs=%d spread@8bp=%s band=%s"
              % (t.get("verdict"), t.get("break_even_toll_bp"), t.get("rungs") or 0,
                 t.get("spread_at_production_toll_pp"),
                 t.get("band_at_production_toll_pp")))
    if off:
        detail = "; ".join(off[:4]) + " | " + detail
    return ok, detail


def judge_section_bars(doc, page_view, rederive_rc):
    """Every CEO-page section names the bar it was priced on."""
    if doc is None:
        return False, "results/live_book_section_bars.json missing"
    bad = []
    if rederive_rc != 0:
        bad.append("the published section bars do not re-derive")
    if (doc.get("n_on_headline") or 0) + (doc.get("n_off_headline") or 0) \
            + (doc.get("n_ahead_of_headline") or 0) != (doc.get("n_sections") or 0):
        bad.append("the on/off/ahead counts do not add up to the dated sections")
    for row in doc.get("off_headline") or []:
        if doc.get("headline_bar") and row.get("bar") >= doc["headline_bar"]:
            bad.append("section %r is called off-headline but is not older" % (row.get("key"),))
        if row.get("provenance") == "no_writer":
            bad.append("section %r is behind the page and no chain leg re-runs it"
                       % (row.get("key"),))
    for row in doc.get("ahead_of_headline") or []:
        if doc.get("headline_bar") and row.get("bar") <= doc["headline_bar"]:
            bad.append("section %r is called ahead but is not newer" % (row.get("key"),))
    if doc.get("verdict") == "PAGE_MIXES_BARS" and not (doc.get("off_headline") or []):
        bad.append("verdict says mixed with nothing behind the headline")
    cap = ((page_view or {}).get("doc") or {}).get("capital") or {}
    cap_bar = cap.get("evidence_cutoff")
    if cap_bar and (doc.get("by_key") or {}).get("capital") != str(cap_bar)[:10]:
        bad.append("the capital section's bar is not the one the page records")
    return (not bad), ("; ".join(bad)[:220] or
                       "%s: %d/%d dated sections on the headline, oldest %s (max lag %s sessions)"
                       % (doc.get("verdict"), doc.get("n_on_headline"),
                          doc.get("n_sections"), doc.get("oldest"),
                          doc.get("max_lag_sessions")))


# ------------------------------------------------------------- loaders (disk) ----
def leg_declared_starting_book():
    pos = _read_json(_p("results", "etf_book_positions.json"))
    md = _read_text(_p("results", "etf_book_positions.md"))
    pages = sorted(glob.glob(_p("docs", "live_book", "LIVE-BOOK-*.md")))
    ceo = _read_text(pages[-1]) if pages else None
    return judge_declared_starting_book(pos, md, ceo)


def leg_ceo_page_prose():
    try:
        import zh_page_prose_census as _zpc
        return judge_ceo_page_prose(*_zpc.check())
    except Exception as exc:                                  # noqa: BLE001
        return judge_ceo_page_prose(2, "census import/call failed: %r" % (exc,))


def leg_card_track():
    return judge_card_track(_read_json(_p("results", "etf_book_card_track.json")))


def leg_order_sheet_floor():
    kg = _read_json(_p("results", "etf_book_k_gap.json"))
    ptr = _read_json(_p("results", "etf_book_order", "latest.json"))
    md = ""
    if ptr and ptr.get("as_of"):
        md = _read_text(_p("results", "etf_book_order", "ORDER-%s.md" % ptr["as_of"]))
    return judge_order_sheet_floor(kg, ptr, md)


def leg_toll_ladder():
    doc = _read_json(_p("results", "etf_book_atlas_toll_ladder.json"))
    arms = {}
    for row in (((doc or {}).get("toll_ladder") or {}).get("argmax_cells") or []):
        name = row.get("file") or ""
        arms[name] = _read_json(_p("results", name))
    return judge_toll_ladder(doc, arms)


def leg_section_bars():
    doc = _read_json(_p("results", "live_book_section_bars.json"))
    try:
        import live_book_section_bars as _SB
        rc = _SB.check()
    except Exception as exc:                                  # noqa: BLE001
        return False, "section-bars check failed: %r" % (exc,)
    try:
        import importlib as _il
        _mod = _il.import_module("scripts.ceo_live_usage")
    except Exception:                                         # noqa: BLE001
        _mod = None
    view = None
    if _mod is not None and hasattr(_mod, "_page_view"):
        try:
            view = _mod._page_view()
        except Exception:                                     # noqa: BLE001
            view = None
    return judge_section_bars(doc, view, rc)


LEGS = [
    ("product: a declared starting book is named as a declaration on both faces",
     leg_declared_starting_book),
    ("product: the Chinese CEO pages carry no new English prose (r1582)",
     leg_ceo_page_prose),
    ("product: the paper book owns the book the card sells",
     leg_card_track),
    ("product: the order sheet prints the floor's per-name cut, not only its total",
     leg_order_sheet_floor),
    ("product: toll-ladder verdict is recomputable from the arm faces",
     leg_toll_ladder),
    ("product: the CEO page's sections each name the bar they were priced on",
     leg_section_bars),
]


# ------------------------------------------------------------------- selftest ----
def _green_declared():
    return ({"next_order_base": {"bar": "2026-11-24", "arrival": "declared"},
             "transition": {"bar": "2026-11-24",
                            "status": "UNEXPLAINED_TARGET_WITHOUT_TRADES"}},
            "起点是声明，不是成交。", "……起点是声明，不是成交……")


def _green_card():
    return {"schema": "etf-book-card-track/v1",
            "agreement": {"same_decision_bar": True, "agrees": True},
            "drift": {"available": True, "nav_identity_ok": True},
            "card_ticket": None}


def _green_kg():
    return ({"bar": "2026-11-24",
             "rows": [{"symbol": "510760", "short_cny": 5034.8, "next_lot_dk_pp": 0.0323}],
             "cheapest_next_lot": {"symbol": "513690"}},
            {"as_of": "2026-11-24"},
            "510760 5,034.80 0.0323pp 再买一手要上调 k 513690")


def _green_toll():
    return ({"toll_ladder": {"rungs": 2, "spread_pp": [1.24],
                             "argmax_cells": [{"file": "arm_a.json"}],
                             "verdict": "ORDERING_HOLDS"},
             "buffer_ladder": {"verdict": "CROSSINGS_WITHOUT_DOSE",
                               "n_clearing_rungs": 2}},
            {"arm_a.json": {"per_cell": [{"median_cagr_pp": 10.0},
                                         {"median_cagr_pp": 11.24}]}})


def _green_sections():
    return ({"verdict": "PAGE_ALIGNED", "n_sections": 2, "n_on_headline": 2,
             "n_off_headline": 0, "n_ahead_of_headline": 0, "headline_bar": "2026-11-24",
             "off_headline": [], "ahead_of_headline": [],
             "by_key": {"capital": "2026-11-24"}, "oldest": "2026-11-24",
             "max_lag_sessions": 0},
            {"doc": {"capital": {"evidence_cutoff": "2026-11-24T15:05:57+08:00"}}},
            0)


SELFTEST_CASES = [
    ("declared starting book", judge_declared_starting_book, _green_declared,
     lambda p: (p[0]["next_order_base"].update({"arrival": "traded"}) or p[0], p[1], p[2])),
    ("CEO page prose census", judge_ceo_page_prose, lambda: (0, "clean"),
     lambda p: (1, "new English prose on the Chinese page")),
    ("card track gate", judge_card_track, _green_card,
     lambda p: dict(p, schema="etf-book-card-track/v0")),
    ("order sheet per-name cut", judge_order_sheet_floor, _green_kg,
     lambda p: (p[0], p[1], p[2].replace("0.0323pp", ""))),
    ("toll ladder re-derivation", judge_toll_ladder, _green_toll,
     lambda p: (p[0], {"arm_a.json": {"per_cell": [{"median_cagr_pp": 10.0},
                                                    {"median_cagr_pp": 12.5}]}})),
    ("section bars", judge_section_bars, _green_sections,
     lambda p: (dict(p[0], n_on_headline=3), p[1], p[2])),
]


def selftest():
    fails = []

    def _leg(ok, why):
        print("  %s %s" % ("ok  " if ok else "FAIL", why), flush=True)
        if not ok:
            fails.append(why)

    for name, judge, green, breakit in SELFTEST_CASES:
        try:
            payload = green()
            g_ok, g_detail = judge(*payload) if isinstance(payload, tuple) else judge(payload)
            _leg(g_ok, "%s: green control passes (%s)" % (name, str(g_detail)[:70]))
        except Exception as exc:                              # noqa: BLE001
            _leg(False, "%s: green control raised %r" % (name, exc))
            continue
        try:
            bad = breakit(green())
            b_ok, _ = judge(*bad) if isinstance(bad, tuple) else judge(bad)
            _leg(b_ok is False, "%s: one broken field turns it red" % name)
        except Exception as exc:                              # noqa: BLE001
            _leg(False, "%s: negative control raised %r" % (name, exc))

    # absence is a verdict, not a crash: every judge must survive an empty document
    absent = [
        ("declared starting book", lambda: judge_declared_starting_book(None, "", None)),
        ("CEO page prose census", lambda: judge_ceo_page_prose(2, "census unavailable")),
        ("card track gate", lambda: judge_card_track(None)),
        ("order sheet per-name cut", lambda: judge_order_sheet_floor(None, None, "")),
        ("toll ladder re-derivation", lambda: judge_toll_ladder(None, {})),
        ("section bars", lambda: judge_section_bars(None, None, 0)),
    ]
    for name, call in absent:
        try:
            out = call()
            _leg(isinstance(out, tuple) and len(out) == 2 and out[0] is False,
                 "%s: absent input is a red verdict, not an exception" % name)
        except Exception as exc:                              # noqa: BLE001
            _leg(False, "%s: absent input raised %r" % (name, exc))

    total = len(SELFTEST_CASES) * 2 + len(absent)
    print("SMOKE-INLINE-LEG-CHECKS-SELFTEST %d/%d legs failed=%d"
          % (total - len(fails), total, len(fails)), flush=True)
    return 0 if not fails else 1


# ----------------------------------------------------------------------- run ----
def run():
    rows = []
    for name, fn in LEGS:
        try:
            ok, detail = fn()
        except Exception as exc:                              # noqa: BLE001
            ok, detail = False, "raised %r" % (exc,)
        rows.append({"leg": name, "ok": bool(ok), "detail": str(detail)[:400]})
        print("%s %s | %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)

    red = [r for r in rows if not r["ok"]]
    doc = {
        "schema": SCHEMA,
        "machine_id": machine_id(),
        "generated": __import__("datetime").datetime.now().astimezone().isoformat(),
        "source": "smoke_test.py inline legs (r2091b map, ready set)",
        "n_legs": len(rows),
        "n_pass": len(rows) - len(red),
        "n_fail": len(red),
        "legs": rows,
    }
    out = _p("results", "smoke_inline_leg_checks.%s.json" % doc["machine_id"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("SMOKE-INLINE-LEG-CHECKS %d legs, %d pass, %d fail -> %s"
          % (len(rows), doc["n_pass"], doc["n_fail"], out), flush=True)
    return 0 if not red else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--json" in argv or len(argv) == 1:
        return run()
    print("usage: smoke_inline_leg_checks.py [run|--selftest]", flush=True)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
