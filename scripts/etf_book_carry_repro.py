#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Will the forward ledger freeze?  Re-derive every published bar and say where.

r1403 (bm-c).  Context: the book's cash leg is priced off the repo ladder
(`etf_book_forward.build_carry`), and the repo panel's last priced bar is
2026-10-27 while the book itself has published bars through 2026-11-06.  The
inbox message MSG-20261107-1637 asserts the next `etf_book_forward.py run`
"极可能把整本账冻住 (exit 3)".  That is a claim about arithmetic, so it can be
measured instead of feared — but only by re-deriving the marks WITHOUT writing
anything.

Two rules this probe obeys:

* It never writes the ledger.  `etf_book_forward.run` mutates and re-flags; this
  reads LEDGER.json, recomputes marks from the current panels, and diffs.
* It splits the answer exactly the way the live gate does — through
  `etf_book_forward.partition_settled`, one implementation (E289).  A settled
  bar that no longer reproduces BLOCKS the next run; a provisional bar is
  disclosed and may still be restated when its inputs arrive.  So "will it
  freeze" is a question about settled bars only, and the provisional ones are a
  question about whether they can ever settle.

Reported per bar: published nav, fresh nav, the delta, and the part of the delta
that is arithmetic in carry (cash weight x the difference between the published
per-bar rate and the rate the panel gives today).  That decomposition is a
diagnosis, not a proof: it says "the drift is the size of the missing rate", and
the exact number stays the recomputed nav.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import etf_book_forward as F

OUT_DIR = F.OUT_DIR
OUT = os.path.join(OUT_DIR, "carry_repro")
TOL = F.DRIFT_TOL


def _bar_map(bars):
    return {str(b.get("bar")): b for b in (bars or [])}


def reproduce(published, fresh, panel_last, carry_last, tol=TOL):
    """Diff published vs re-derived marks; decide the gate with the live splitter.

    `published` / `fresh` are lists of bar dicts carrying at least bar/nav; the
    published side may also carry cash and carry (the fresh side always does).
    """
    pub, fre = _bar_map(published), _bar_map(fresh)
    bars = sorted(set(pub) & set(fre))
    settled, provisional = F.partition_settled(bars, panel_last, carry_last)
    rows, blocking, unexplained = [], [], []
    for d in bars:
        p, f = pub[d], fre[d]
        delta = float(f["nav"]) - float(p["nav"])
        cash = p.get("cash", 0.0)
        c_pub, c_new = p.get("carry"), f.get("carry")
        cart = None
        if c_pub is not None and c_new is not None and cash is not None:
            cart = float(cash) * (float(c_new) - float(c_pub))
        rows.append({
            "bar": d,
            "settled": d in settled,
            "published_nav": float(p["nav"]),
            "fresh_nav": float(f["nav"]),
            "delta": delta,
            "abs_delta": abs(delta),
            "cash": cash,
            "carry_published": c_pub,
            "carry_fresh": c_new,
            "carry_arithmetic": cart,
            "drift_is_carry_sized": (cart is not None and abs(delta) <= abs(cart) * 2.0 + 1e-12),
        })
        if d in settled and abs(delta) > tol:
            blocking.append(d)
        if d in settled and not rows[-1]["drift_is_carry_sized"]:
            unexplained.append(d)
    return {
        "tol": tol,
        "panel_last_date": panel_last,
        "carry_last_bar": carry_last,
        "bars_compared": len(bars),
        "bars_missing_from_one_side": sorted(set(pub) ^ set(fre)),
        "settled_bars": sorted(settled),
        "provisional_bars": sorted(provisional),
        "blocking_bars": blocking,
        "settled_drift_not_explained_by_carry": unexplained,
        "max_abs_delta_settled": max([r["abs_delta"] for r in rows if r["settled"]], default=0.0),
        "max_abs_delta_provisional": max([r["abs_delta"] for r in rows if not r["settled"]], default=0.0),
        "gate_would_block": bool(blocking),
        "rows": rows,
    }


def forecast(pub, fresh, panel_last, tol=TOL):
    """What happens when the cash leg catches up: every bar it reaches becomes settled.

    The published marks were priced while the repo ladder was already behind, so the
    question is not today's verdict but the one on the day the lane refills.  Stepping
    carry_last through the provisional bars answers it without touching anything.
    """
    bars = sorted(set(_bar_map(pub)) & set(_bar_map(fresh)))
    out = []
    for cand in bars:
        doc = reproduce(pub, fresh, panel_last, cand, tol)
        if cand not in doc["provisional_bars"] and doc["bars_compared"] == 0:
            continue
        out.append({
            "carry_last_claimed": cand,
            "settled_bars": doc["settled_bars"],
            "blocking_bars": doc["blocking_bars"],
            "max_abs_delta_settled": doc["max_abs_delta_settled"],
        })
    return out


def run(tol=TOL):
    led = F.load_ledger()
    if not led:
        return {"status": "no_ledger", "reason": "results/etf_book_forward/LEDGER.json absent"}
    pub = led.get("bars") or []
    fwd, marks, dates, _cls, _n = F.compute_marks()
    seed_bar = (led.get("seed") or {}).get("bar")
    if not seed_bar:
        return {"status": "no_seed", "reason": "ledger seed bar absent; nothing is a track record"}
    fresh = F._indexed(marks, seed_bar)
    panel_last = str(dates[-1].date()) if dates else None
    carry_last = F.carry_last_bar() if getattr(fwd, "carry", None) is not None else None
    doc = reproduce(pub, fresh, panel_last, carry_last, tol)
    doc.update({
        "status": "ok",
        "carry_leg_absent": carry_last is None,
        "carry_leg_note": ("repo ladder unreadable in this window: the ledger's carry leg is "
                           "zero and every bar settles on the price panel alone"
                           if carry_last is None else
                           "bars after carry_last rode a forward-filled rate"),
        "generated": __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z"),
        "engine_block": F._engine_block(fwd),
        "published_last_bar": str(pub[-1]["bar"]) if pub else None,
        "fresh_last_bar": fresh[-1]["bar"] if fresh else None,
        "unattributed_bars": [r["bar"] for r in doc["rows"]
                              if r["carry_arithmetic"] is not None
                              and abs(r["delta"]) > abs(r["carry_arithmetic"]) * 2.0 + 1e-12],
        "if_carry_catches_up": forecast(pub, fresh, panel_last, tol),
        "honest": {
            "writes": "none (read-only; the ledger is not opened for writing)",
            "carry_arithmetic": ("per-bar cash x (fresh rate - published rate): a size match, "
                                 "not a proof of cause"),
            "settled_rule": ("same splitter as the live gate; only settled bars can block"),
        },
    })
    return doc


def _write(doc):
    os.makedirs(OUT, exist_ok=True)
    last = doc.get("published_last_bar") or "none"
    path = os.path.join(OUT, "CARRY-REPRO-%s.json" % last)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    return path


# ---------------------------------------------------------------- selftest
def _selftest():
    legs = []

    def leg(name, fn, want):
        try:
            got = fn()
        except Exception as exc:                                   # pragma: no cover
            got = "EXC:%s" % exc
        ok = got == want
        legs.append({"leg": name, "ok": ok, "got": got, "want": want})

    def bar(d, nav, cash=0.3, carry=0.0):
        return {"bar": d, "nav": nav, "cash": cash, "carry": carry}

    pub = [bar("2026-10-23", 1.0), bar("2026-10-26", 1.001),
           bar("2026-10-28", 1.002, carry=1.0e-05), bar("2026-11-06", 1.003, carry=1.1e-05)]
    fresh = [bar("2026-10-23", 1.0), bar("2026-10-26", 1.001),
             bar("2026-10-28", 1.00202, carry=3.7e-05), bar("2026-11-06", 1.00311, carry=3.7e-05)]

    # L1 settled bars that reproduce never block, even if provisional ones moved.
    leg("settled clean -> no block",
        lambda: reproduce(pub, fresh, "2026-11-06", "2026-10-27")["gate_would_block"], False)
    # L2 the same numbers DO block when the panel claims to price them (carry caught up).
    leg("same marks block once carry_says it priced them",
        lambda: reproduce(pub, fresh, "2026-11-06", "2026-11-06")["gate_would_block"], True)
    # L3 a delta smaller than tol on a settled bar is not drift.
    leg("settled delta below tol is silent",
        lambda: reproduce([bar("2026-10-26", 1.001)], [bar("2026-10-26", 1.001 + 5e-10)],
                          "2026-11-06", "2026-11-06")["gate_would_block"], False)
    # L4 the carry arithmetic is signed and sized by the cash weight.
    leg("carry arithmetic = cash x rate gap",
        lambda: round(reproduce(pub, fresh, "2026-11-06", "2026-10-27")["rows"][2]
                      ["carry_arithmetic"], 12), round(0.3 * (3.7e-05 - 1.0e-05), 12))
    # L5 a settled bar that moved for a non-carry reason is named, not excused. The full
    # bar list is passed because the shared splitter treats bars[-1] as the newest bar --
    # a one-bar list makes that bar provisional by construction.
    leg("unexplained settled drift is named",
        lambda: reproduce(pub, [bar("2026-10-23", 1.0), bar("2026-10-26", 1.5),
                                bar("2026-10-28", 1.002, carry=1.0e-05),
                                bar("2026-11-06", 1.003, carry=1.1e-05)],
                          "2026-11-06", "2026-11-06")["settled_drift_not_explained_by_carry"],
        ["2026-10-26"])
    # L6 a bar present on one side only is reported rather than silently ignored.
    leg("one-sided bar reported",
        lambda: reproduce(pub, fresh[:-1], "2026-11-06", "2026-10-27")["bars_missing_from_one_side"],
        ["2026-11-06"])
    # L7 no carry coverage is NOT read as extra provisionality: the shared splitter only
    # uses carry_last when it has one, so with the repo panel absent those bars settle
    # and the published carry-bearing marks no longer reproduce -- reported, not hidden.
    leg("carry_last None removes the carry-based provisionality",
        lambda: reproduce(pub, fresh, "2026-11-06", None)["gate_would_block"], True)
    # L8 empty ledger never reads as a pass.
    leg("no overlapping bars -> zero compared",
        lambda: reproduce([], fresh, "2026-11-06", "2026-10-27")["bars_compared"], 0)
    # L9 determinism: same inputs, same doc (minus nothing -- no wall clock here).
    leg("deterministic",
        lambda: reproduce(pub, fresh, "2026-11-06", "2026-10-27")
        == reproduce(pub, fresh, "2026-11-06", "2026-10-27"), True)

    ok = sum(1 for l in legs if l["ok"])
    for l in legs:
        print("[%s] %s" % ("PASS" if l["ok"] else "FAIL", l["leg"]))
        if not l["ok"]:
            print("   got=%r want=%r" % (l["got"], l["want"]))
    print("SELFTEST %d/%d legs" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    doc = run()
    if doc.get("status") != "ok":
        print(json.dumps(doc, ensure_ascii=False))
        return 2
    path = _write(doc)
    print(json.dumps({k: doc[k] for k in (
        "bars_compared", "settled_bars", "provisional_bars", "blocking_bars",
        "max_abs_delta_settled", "max_abs_delta_provisional", "gate_would_block")},
        ensure_ascii=False, indent=1))
    print("wrote %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))