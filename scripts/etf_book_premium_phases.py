"""ETF book -- is the selection premium a level, or one decision sequence?

The card's central claim is results/etf_book_passive_mix.json: the shipped book beats
holding its own class exposure statically by +6.36pp/yr. That number rests on ONE decision
calendar. r1325 proved, on this same book, why that is not yet a decision: an arm that
improved turnover, CAGR, Sharpe and maxDD together on the production calendar reversed on
70% of four phase-shifted calendars, because the book's own CAGR spans 9.12%..10.93% across
phases of one 20-bar cycle.

This face applies the same ruler to the claim the whole card stands on. The premium is
re-priced on four decision grids started at four different bars inside one 20-bar cycle,
each with its own book decisions AND its own static class weights (the static shape is
re-derived inside every phase from that phase's own attribution run, so both arms move
together and the premium stays a paired comparison rather than two unrelated runs).

  LEVEL       the premium is positive in every phase and clear of the floor -> the card's
              headline is a level, and phase is not a knob that can flip it.
  SEQUENCE    the premium changes sign or collapses in some phases -> the headline is one
              decision sequence; the card has to print a range, not a point.

WHY THE CRITERIA SIT ABOVE THE CODE: the verdict rule is frozen as constants before the
first run and echoed into the payload; --check refuses a face whose echoed criteria differ
from the constants, so a later "small adjustment" cannot be mistaken for the rule. The
verdict is recomputed from the summary by the gate instead of being taken on trust.

The activity precondition (r1261) is asserted, not assumed: four phases that collapsed onto
one decision grid would make every arm reproduce and "premium is a level" trivially true.
Uniqueness is checked on the decision DATES, not decision counts -- four phases inside one
cycle can share a count and still never decide on the same day.

Reuse, not re-implementation: panel/engine/static arms/stats all come from
etf_book_production / etf_robust_pf / etf_equity_alpha and are driven through
etf_book_passive_mix.price_window, i.e. the exact function that produced the published
premium.

Usage:
    python scripts/etf_book_premium_phases.py run
    python scripts/etf_book_premium_phases.py --check      # gate: criteria echo + verdict
    python scripts/etf_book_premium_phases.py --selftest   # offline invariants
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import pandas as pd

import etf_book_passive_mix as M
from scripts import etf_book_production as P

OUT_JSON = ROOT / "results" / "etf_book_premium_phases.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_PREMIUM_PHASES.md"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run. The payload echoes these and --check refuses a face whose
# echo differs, so the rule cannot be re-tuned after the numbers are known.
N_PHASES = 4                 # phases spread across one rebalance cycle
PHASE_REBAL = 20             # the cycle the phases are drawn from (production REBAL)
PREMIUM_POSITIVE_SHARE_MIN = 1.00   # "level" = the premium never changes sign
PREMIUM_PARTIAL_SHARE_MIN = 0.75    # "mostly level" floor for a disclosed range
MEDIAN_PREMIUM_FLOOR_PP = 2.0       # a premium under 2pp/yr does not pay for 0.93 turnover
CONTROL_TOL_PP = 0.5                # r1297: the control arm must be the published arm

CRITERIA = {
    "n_phases": N_PHASES,
    "phase_rebal": PHASE_REBAL,
    "premium_positive_share_min": PREMIUM_POSITIVE_SHARE_MIN,
    "premium_partial_share_min": PREMIUM_PARTIAL_SHARE_MIN,
    "median_premium_floor_pp": MEDIAN_PREMIUM_FLOOR_PP,
    "control_tolerance_pp": CONTROL_TOL_PP,
    "cell": "N%d_R%d_10bp" % (M.N_HOLD, M.REBAL),
}


# ---------------------------------------------------------------- mechanics
def decision_signature(index, start, rebal=PHASE_REBAL):
    """The dates this phase's decision grid actually lands on.

    The engine decides every `rebal` bars counted from the first bar >= start, so the grid
    is derivable from the panel index without re-running the engine. Two phases sharing a
    decision COUNT prove nothing (r1261); the signature is the set of dates.
    """
    post = [d for d in index if d >= pd.Timestamp(start)]
    return [str(pd.Timestamp(d).date()) for d in post[::rebal]]


def summarize(cells, floor=MEDIAN_PREMIUM_FLOOR_PP):
    """Fold per-phase premium readings into the frozen summary, or say why not."""
    premiums = [c.get("premium_pp") for c in cells]
    numbered = [p for p in premiums if isinstance(p, (int, float))]
    out = {"n_phases": len(cells), "n_priced": len(numbered)}
    if not numbered:
        out["status"] = "undetermined"
        out["reason"] = "no phase priced a premium"
        return out
    pos = sum(1 for p in numbered if p > 0)
    out.update({
        "positive_phases": pos,
        "positive_share": round(pos / len(numbered), 4),
        "median_pp": round(statistics.median(numbered), 2),
        "min_pp": round(min(numbered), 2),
        "max_pp": round(max(numbered), 2),
        "spread_pp": round(max(numbered) - min(numbered), 2),
        "floor_pp": floor,
        "status": "priced" if len(numbered) == len(cells) else "partial",
    })
    return out


def verdict_for(summary):
    """Frozen decision rule. Recomputed by --check; never hand-written into the payload."""
    if not summary or summary.get("status") == "undetermined":
        return "undetermined: no phase priced a premium"
    share = summary.get("positive_share") or 0.0
    med = summary.get("median_pp")
    floor = summary.get("floor_pp", MEDIAN_PREMIUM_FLOOR_PP)
    if summary.get("status") == "partial":
        return ("partial: %d of %d phases priced, so this is not a verdict on the premium"
                % (summary.get("n_priced"), summary.get("n_phases")))
    if share >= PREMIUM_POSITIVE_SHARE_MIN and med is not None and med >= floor:
        return ("level: the premium is positive on %d/%d phases (median %+.2fpp/yr, floor "
                "%.2f) -- the card's headline is a level, not one decision sequence"
                % (summary["positive_phases"], summary["n_phases"], med, floor))
    if share >= PREMIUM_PARTIAL_SHARE_MIN and med is not None and med >= floor:
        return ("mostly level: positive on %d/%d phases (median %+.2fpp/yr) with a disclosed "
                "sign change -- print the range, do not print a point"
                % (summary["positive_phases"], summary["n_phases"], med))
    return ("sequence: the premium is positive on only %d/%d phases (median %s pp/yr) -- the "
            "headline is one decision sequence and must not be quoted as a level"
            % (summary["positive_phases"], summary["n_phases"],
               "n/a" if med is None else "%+.2f" % med))


def range_of(cells, key):
    vals = [c.get(key) for c in cells if isinstance(c.get(key), (int, float))]
    if not vals:
        return None
    return {"min": round(min(vals), 4), "max": round(max(vals), 4),
            "spread": round(max(vals) - min(vals), 4)}


def build():
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    cols = list(close.columns)
    phases = M_phase_starts(close.index)
    signatures = [decision_signature(close.index, p) for p in phases]
    if len(set(map(tuple, signatures))) != len(signatures):
        raise SystemExit("phases collapsed onto one decision grid -- the experiment would "
                         "reproduce the same sequence four times (r1261)")
    if any(not s for s in signatures):
        raise SystemExit("a phase produced no decisions -- the mechanism did not move")

    print("panel %s flips=%d phases=%s" % (close.shape, n_flip,
                                           [str(p.date()) for p in phases]), flush=True)
    cells = []
    for i, phase in enumerate(phases):
        print("[phase %d] start=%s" % (i, phase.date()), flush=True)
        box = M.price_window(close, openp, amt, score, cls, cols,
                             str(phase.date()), None, "phase%d" % i,
                             classes=list(P.USE_CLASSES), splits=False)
        read = box.get("read") or {}
        cells.append({
            "phase": i,
            "start": str(phase.date()),
            "decisions": len(signatures[i]),
            "first_decision": signatures[i][0] if signatures[i] else None,
            "last_decision": signatures[i][-1] if signatures[i] else None,
            "book_cagr": (box.get("book") or {}).get("cagr"),
            "static_cagr": (box.get("static_mix") or {}).get("cagr"),
            "book_sharpe": (box.get("book") or {}).get("sharpe"),
            "static_sharpe": (box.get("static_mix") or {}).get("sharpe"),
            "book_maxdd": (box.get("book") or {}).get("maxdd"),
            "static_maxdd": (box.get("static_mix") or {}).get("maxdd"),
            "premium_pp": read.get("selection_premium_pp"),
            "book_turnover_per_decision": read.get("book_turnover_per_decision"),
            "static_turnover_per_decision": read.get("static_turnover_per_decision"),
            "vol_delivered": read.get("vol_delivered"),
            "static_weights": box.get("static_weights"),
        })

    summary = summarize(cells)
    out = {
        "schema": "etf_book_premium_phases/v1",
        "question": ("the card's headline is +%.2fpp/yr of selection premium on one decision "
                     "calendar -- does that premium survive four phases of that calendar?"
                     % (cells[0].get("premium_pp") or 0.0)),
        "engine": ("etf_book_passive_mix.price_window -- the exact function that produced the "
                   "published premium; no re-implementation"),
        "criteria": dict(CRITERIA),
        "phases": cells,
        "summary": summary,
        "verdict": verdict_for(summary),
        "ranges": {
            "book_cagr": range_of(cells, "book_cagr"),
            "static_cagr": range_of(cells, "static_cagr"),
            "premium_pp": range_of(cells, "premium_pp"),
            "book_sharpe": range_of(cells, "book_sharpe"),
        },
        "control": control_block(cells, M.published_book_cagr()),
        "window": "%s..panel end (every phase)" % M.A.START,
        "caveats": [
            ("the static arm rides class equal-weight indices that rebalance daily at ZERO "
             "cost, so the premium is a LOWER bound on what the ranking adds -- unchanged "
             "from the face this one re-prices"),
            ("all four phases share one panel and one vintage of the data, so this measures "
             "calendar dependence, not data dependence"),
            ("the book's own phase spread is printed next to the premium: if the premium is "
             "smaller than that spread it cannot be told apart from calendar luck"),
            ("ETF pool is survival-filtered and both arms share the pool, so the bias "
             "cancels in the premium, not in the levels"),
        ],
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print("wrote", OUT_JSON, flush=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_md(out), encoding="utf-8")
    print("wrote", OUT_MD, flush=True)
    print("VERDICT", out["verdict"], flush=True)
    return 0


def M_phase_starts(index):
    """Phase starts, delegated to the r1325 implementation (single source)."""
    import etf_book_buffer_adoption as B
    return B.phase_starts(index, start=M.A.START, rebal=PHASE_REBAL, n=N_PHASES)


def control_block(cells, published):
    got = cells[0].get("book_cagr") if cells else None
    delta = (round((got - published) * 100, 2)
             if isinstance(got, (int, float)) and isinstance(published, (int, float)) else None)
    return {
        "arm": "book@phase0 (first decision %s)"
               % (cells[0].get("start") if cells else "-"),
        "published_cagr": published,
        "recomputed_cagr": got,
        "delta_pp": delta,
        "tolerance_pp": CONTROL_TOL_PP,
        "passes": (None if delta is None else abs(delta) <= CONTROL_TOL_PP),
        "note": ("not asserted: published artifact unavailable" if delta is None
                 else "phase 0 is the published window, so it must reproduce the published arm"),
    }


def render_md(payload):
    s = payload["summary"]
    lines = [
        "# ETF book -- selection premium across decision phases",
        "",
        "Question: %s" % payload["question"],
        "",
        "**Verdict**: %s" % payload["verdict"],
        "",
        "| phase | start | decisions | book CAGR | static CAGR | premium pp | book Sharpe |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in payload["phases"]:
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            c.get("phase", "-"), c.get("start", "-"), c.get("decisions", "-"),
            _pct(c.get("book_cagr")), _pct(c.get("static_cagr")),
            _pp(c.get("premium_pp")), _num(c.get("book_sharpe"))))
    r = payload.get("ranges") or {}
    lines += [
        "",
        "Premium: positive on %d/%d phases, median %s pp/yr, range %s..%s (%s pp spread)."
        % (s.get("positive_phases", 0), s.get("n_phases", 0), _pp(s.get("median_pp")),
           _pp(s.get("min_pp")), _pp(s.get("max_pp")), _pp(s.get("spread_pp"))),
        "",
        "Ruler: the book's own CAGR spans %s..%s across these phases (%s pp) -- compare the "
        "premium's spread against that before quoting any single number."
        % (_pct((r.get("book_cagr") or {}).get("min")),
           _pct((r.get("book_cagr") or {}).get("max")),
           _spread_pp((r.get("book_cagr") or {}).get("spread"))),
        "",
        "Control: %s" % (payload.get("control") or {}).get("note", "-"),
        "",
        "## Caveats",
    ]
    for c in payload.get("caveats") or []:
        lines.append("- %s" % c)
    return "\n".join(lines) + "\n"


def _pct(x):
    return "n/a" if not isinstance(x, (int, float)) else "%.2f%%" % (x * 100)


def _pp(x):
    return "n/a" if not isinstance(x, (int, float)) else "%+.2f" % x


def _num(x, nd=2):
    return "n/a" if not isinstance(x, (int, float)) else ("%." + str(nd) + "f") % x


def _spread_pp(x):
    """A CAGR spread is stored as a FRACTION (0.0181); print it as percentage points.

    r1292/r1316 family: passing the fraction to the pp formatter printed "+0.02 pp" for a
    spread that is really 1.81 pp -- an understatement by 100x in the very line that tells
    the reader how big the premium has to be to beat calendar luck.
    """
    return "n/a" if not isinstance(x, (int, float)) else "%.2f" % (x * 100)


# ---------------------------------------------------------------- gate
def check_payload(payload, criteria=None):
    """Refuse a face whose rule echo or recomputed verdict drifted from the frozen rule."""
    want = dict(criteria or CRITERIA)
    got = payload.get("criteria") or {}
    for k, v in want.items():
        if got.get(k) != v:
            raise SystemExit("criteria drift on %r: payload=%r frozen=%r -- the face was "
                             "built under a different rule" % (k, got.get(k), v))
    summary = payload.get("summary") or {}
    recomputed = verdict_for(summary)
    if recomputed != payload.get("verdict"):
        raise SystemExit("verdict does not recompute: payload=%r recomputed=%r"
                         % (payload.get("verdict"), recomputed))
    phases = payload.get("phases") or []
    if len(phases) != want["n_phases"]:
        raise SystemExit("payload prices %d phases, rule says %d"
                         % (len(phases), want["n_phases"]))
    if len({(c.get("start"), c.get("first_decision")) for c in phases}) != len(phases):
        raise SystemExit("two phases share a start/decision signature -- they would price "
                         "the same sequence twice (r1261)")
    ctl = payload.get("control") or {}
    if ctl.get("passes") is False:
        raise SystemExit("control arm does not reproduce the published arm: %r" % ctl)
    return {"phases": len(phases), "positive_phases": summary.get("positive_phases"),
            "median_pp": summary.get("median_pp")}


def check():
    if not OUT_JSON.exists():
        raise SystemExit("no face at %s -- run it first" % OUT_JSON)
    with open(OUT_JSON, encoding="utf-8") as fh:
        payload = json.load(fh)
    read = check_payload(payload)
    print("premium_phases --check OK %s -> %s" % (read, payload.get("verdict")))
    return 0


# ---------------------------------------------------------------- selftest
def _cells(premiums, book=0.09, static=0.03):
    return [{"phase": i, "start": "2020-01-%02d" % (1 + i), "premium_pp": p,
             "book_cagr": book + 0.001 * i, "static_cagr": static,
             "first_decision": "2020-01-%02d" % (1 + i)} for i, p in enumerate(premiums)]


def selftest():
    ok = 0

    def eq(name, got, want, tol=1e-9):
        nonlocal ok
        if isinstance(want, float):
            if got is None or abs(got - want) > tol:
                raise SystemExit("FAIL %s: got %r want %r" % (name, got, want))
        elif got != want:
            raise SystemExit("FAIL %s: got %r want %r" % (name, got, want))
        ok += 1

    # 1) a summary of all-positive premiums above the floor is a LEVEL
    s = summarize(_cells([6.4, 5.1, 4.0, 3.5]))
    eq("level share", s["positive_share"], 1.0)
    eq("level median", s["median_pp"], 4.55, 1e-9)
    eq("level status", s["status"], "priced")
    eq("level verdict prefix", verdict_for(s).split(":")[0], "level")
    eq("leg count = phases", s["n_phases"], 4)

    # 2) one sign change is NOT a level, and says so with the count
    s2 = summarize(_cells([6.4, -0.8, 4.0, 3.5]))
    eq("flip share", s2["positive_share"], 0.75)
    eq("flip verdict prefix", verdict_for(s2).split(":")[0], "mostly level")
    s3 = summarize(_cells([6.4, -0.8, -1.0, 3.5]))
    eq("majority-down share", s3["positive_share"], 0.5)
    eq("majority-down verdict prefix", verdict_for(s3).split(":")[0], "sequence")

    # 3) all positive but under the floor is still not a level (the rule has two doors)
    s4 = summarize(_cells([1.5, 1.4, 1.3, 1.2]))
    eq("thin share", s4["positive_share"], 1.0)
    eq("thin verdict prefix", verdict_for(s4).split(":")[0], "sequence")

    # 4) an unpriced phase cannot become a verdict
    s5 = summarize(_cells([6.4, None, 4.0, 3.5]))
    eq("partial status", s5["status"], "partial")
    eq("partial verdict prefix", verdict_for(s5).split(":")[0], "partial")
    s6 = summarize([])
    eq("empty status", s6["status"], "undetermined")
    eq("empty verdict prefix", verdict_for(s6).split(":")[0], "undetermined")

    # 5) control gate: the same arm inside tolerance passes, a drifted arm fails
    eq("control pass", control_block(_cells([6.4], book=0.095), 0.0949)["passes"], True)
    eq("control fail", control_block(_cells([6.4], book=0.12), 0.0949)["passes"], False)
    eq("control missing artifact", control_block(_cells([6.4]), None)["passes"], None)

    # 6) decision signature is dates every REBAL bars, and shifts with the start
    idx = pd.bdate_range("2020-01-01", periods=60)
    sig_a = decision_signature(idx, "2020-01-01")
    sig_b = decision_signature(idx, str(idx[5].date()))
    eq("signature stride", len(sig_a), 3)
    eq("signature first", sig_a[0], "2020-01-01")
    eq("signature moved", sig_a != sig_b, True)

    # 7) range_of reports the ruler, and ignores unpriced cells
    r = range_of(_cells([6.4, 5.1, 4.0, 3.5]) + [{"premium_pp": None}], "premium_pp")
    eq("range min", r["min"], 3.5)
    eq("range max", r["max"], 6.4)
    eq("range spread", r["spread"], 2.9, 1e-9)

    # 7b) the ruler line prints a CAGR spread in PERCENTAGE POINTS, not the raw fraction
    # (r1292/r1316 family: 0.0181 passed straight to the pp formatter printed "+0.02 pp")
    eq("a fraction spread renders as pp", _spread_pp(0.0181), "1.81")
    eq("a missing spread renders as n/a", _spread_pp(None), "n/a")
    _ruler = [l for l in render_md({
        "question": "q", "verdict": "v",
        "phases": _cells([6.4, 5.1, 4.0, 3.5]),
        "summary": summarize(_cells([6.4, 5.1, 4.0, 3.5])),
        "ranges": {"book_cagr": range_of(
            [{"book_cagr": 0.0912}, {"book_cagr": 0.1093}], "book_cagr")},
        "control": {"note": "n"}, "caveats": []}).splitlines() if l.startswith("Ruler:")]
    eq("the ruler line prints the pp spread", "1.81 pp" in (_ruler[0] if _ruler else ""), True)

    # 8) the gate recomputes the verdict and refuses a hand-edited one
    payload = {"criteria": dict(CRITERIA), "phases": _cells([6.4, 5.1, 4.0, 3.5]),
               "summary": summarize(_cells([6.4, 5.1, 4.0, 3.5])),
               "control": {"passes": True}}
    payload["verdict"] = verdict_for(payload["summary"])
    eq("gate accepts an honest face", check_payload(payload)["phases"], 4)
    bad = dict(payload, verdict="level: everything is fine")
    try:
        check_payload(bad)
    except SystemExit:
        ok += 1
    else:
        raise SystemExit("FAIL gate accepted a hand-written verdict")

    # 9) the gate refuses a criteria echo that differs from the frozen rule
    drift = dict(payload, criteria=dict(CRITERIA, median_premium_floor_pp=0.0))
    try:
        check_payload(drift)
    except SystemExit:
        ok += 1
    else:
        raise SystemExit("FAIL gate accepted a re-tuned floor")

    # 10) the gate refuses two phases with the same signature
    dup = dict(payload, phases=[dict(_cells([1.0, 2.0, 3.0, 4.0])[0]) for _ in range(4)])
    dup["summary"] = summarize(dup["phases"])
    dup["verdict"] = verdict_for(dup["summary"])
    try:
        check_payload(dup)
    except SystemExit:
        ok += 1
    else:
        raise SystemExit("FAIL gate accepted four identical phases")

    print("etf_book_premium_phases selftest: %d/%d PASS" % (ok, ok))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check"))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.check or args.cmd == "check":
        return check()
    return build()


if __name__ == "__main__":
    sys.exit(main())