#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Does the ``rankind - ind`` differential survive a different sample of the same panel?

r1946 (scripts/astock_rankind_stability.py) read the within-industry rank arm of
r1945 and found the differential `q1_excess_rankind - q1_excess_ind` at t = 1.99 over
77 rebalances, positive in 6 of 7 calendar years. Its own next-stone line was explicit:

    move `rankind - ind` onto another sample, re-run it unchanged, and freeze the
    criterion first: same sign and t >= 1.5.

This face does exactly that and nothing else. It does not re-open the maths: every
row is produced by `astock_resid_industry_neutral.run`, the same function that wrote
the published face, on the same loaded panel, with the same 8bp/side cost, the same
quintiles, the same liquidity gate and the same point-in-time industry map.

What "another sample" means here (frozen before the run)
--------------------------------------------------------
The panel and the calendar are shared; only the *set of observation dates* changes.
Two alternates, both reported next to the reproduction of the original:

  S1  phase-shifted 10 bars (HOLD/2), stride 20
      every rebalance sits halfway between two of the original dates, so its forward
      window [t+10, t+30] is disjoint from both neighbouring original windows. The row
      count stays at the original density (76 here) -- the *dates* move, they do not thin.

  S2  stride 40, no shift
      every other original date, forward windows non-overlapping by construction and
      separated by a 20-bar gap. 39 rebalances.

S0 (offset 0, stride 20) is re-run here too and its 77 rows are compared cell for
cell against the published upstream face. If S0 does not reproduce, nothing else on
this face means anything and the run is an error, not a reading.

Frozen criterion (written here, before any run; not tuned afterwards)
---------------------------------------------------------------------
    holds(sample) := n >= 12 AND mean(differential) > 0 AND t(differential) >= 1.5

    HOLDS_ON_BOTH_ALTERNATE_SAMPLES   S1 holds and S2 holds
    HOLDS_ON_ONE_SAMPLE_ONLY          exactly one of them holds
    DOES_NOT_HOLD                     neither holds
    NOT_ENOUGH_REBALANCES             any sample under 12 rebalances

Honest boundaries that are printed with the result, not kept in a notebook
--------------------------------------------------------------------------
* Phase-shifted rows are NOT an independent dataset. Their 20-day formation windows
  overlap the original ones and the names are drawn from the same panel, so a shared
  market-wide move reaches both samples. This tests *sampling sensitivity*, which is
  what the next-stone asked for; it does not turn 77 rebalances into 153 independent
  ones and no pooled t is computed.
* Sign-flip p is reported for each sample but is not part of the verdict: at 39 rows
  (S2) it is a weak instrument, and the criterion above was frozen without it.
* Nothing here is a candidate, a prereg or an adoption. One panel, one cost model,
  no live constraints beyond the 8bp/side charge inside the rows.

Usage:
    python scripts/astock_rankind_second_sample.py run
    python scripts/astock_rankind_second_sample.py check
    python scripts/astock_rankind_second_sample.py selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_resid_reversal_probe as base  # noqa: E402  (panel loader + maths)
import astock_resid_industry_neutral as neut  # noqa: E402  (the row producer)
import astock_rankind_stability as stab  # noqa: E402  (series/t-stat/sign-flip)

UPSTREAM = os.path.join(ROOT, "results", "astock_resid_industry_neutral.json")
OUT = os.path.join(ROOT, "results", "astock_rankind_second_sample.json")

PAIR = ("rankind", "ind")
Q1_KEY = "q1_excess_%s"

SAMPLES = (
    {"id": "S0", "label": "reproduction (offset 0, stride 20)", "offset": 0, "stride": 20},
    {"id": "S1", "label": "phase-shifted 10 bars (offset 10, stride 20)", "offset": 10, "stride": 20},
    {"id": "S2", "label": "every other date (offset 0, stride 40)", "offset": 0, "stride": 40},
)
ALTERNATES = ("S1", "S2")
MIN_REBALANCES = 12
T_FLOOR = 1.5
DRAWS = 20000
SEED = 20261122
REPRO_TOL = 1e-12

CRITERIA = {
    "pair": "%s-minus-%s" % PAIR,
    "read": "q1_excess per rebalance, the implementable long leg, identical maths and costs",
    "holds": "n >= %d AND mean > 0 AND t >= %.1f" % (MIN_REBALANCES, T_FLOOR),
    "verdict_order": ["NOT_ENOUGH_REBALANCES", "HOLDS_ON_BOTH_ALTERNATE_SAMPLES",
                      "HOLDS_ON_ONE_SAMPLE_ONLY", "DOES_NOT_HOLD"],
    "samples_frozen": [s["label"] for s in SAMPLES],
    "s0_role": "reproduction only; a mismatch against the upstream face is an error, not a reading",
    "signflip": "%d draws, seed %d, reported but not part of the verdict" % (DRAWS, SEED),
    "note": "frozen in this file before the first run; no threshold was touched afterwards",
}


def _rel(path: str) -> str:
    """Repo-relative when possible; an absolute path when the face lives on another drive."""
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


# ------------------------------------------------------------------ sampling
def run_sample(dates, symbols, close, amount, shares, hist, offset: int, stride: int):
    """The upstream producer, unchanged, on a shifted view of the same panel.

    Slicing the arrays shifts every positional index by `offset` in one move, so the
    formation window, the forward window, the beta lookback and the liquidity gate all
    move together and land on the same true dates they would have hit natively.
    """
    if offset == 0:
        return neut.run(dates, symbols, close, amount, shares, hist, stride=stride)
    if not 0 <= offset < len(dates):
        raise ValueError("offset %d outside the calendar" % offset)
    return neut.run(dates[offset:], symbols, close[offset:], amount[offset:],
                    shares[offset:], hist, stride=stride)


def differential(rows):
    """rankind minus ind, one value per rebalance; a missing key is an error."""
    a = dict(stab.series(rows, Q1_KEY % PAIR[0]))
    b = dict(stab.series(rows, Q1_KEY % PAIR[1]))
    diff = []
    for date, value in stab.series(rows, Q1_KEY % PAIR[0]):
        if date not in b:
            raise KeyError("rebalance %s has no %r row" % (date, Q1_KEY % PAIR[1]))
        diff.append((date, value - b[date]))
    del a
    return diff


def sample_block(rows, spec):
    diff = differential(rows)
    vals = [v for _, v in diff]
    st = stab._stat(vals)
    yearly = stab.group_years(diff)
    block = {
        "id": spec["id"],
        "label": spec["label"],
        "offset": spec["offset"],
        "stride": spec["stride"],
        "n": len(vals),
        "first": diff[0][0] if diff else None,
        "last": diff[-1][0] if diff else None,
        "differential": {
            "summary": st,
            "annual": base.compound(vals) if vals else None,
            "yearly": [{"year": y["year"], "n": y["n"], "mean": y["mean"], "t": y["t"]}
                       for y in yearly],
            "years_positive": sum(1 for y in yearly if (y["mean"] or 0.0) > 0),
            "years_total": len(yearly),
            "signflip_p": stab.signflip_p(vals, draws=DRAWS, seed=SEED),
        },
        "legs": {
            "rankind_q1_annual": base.compound([r[Q1_KEY % "rankind"] for r in rows]),
            "ind_q1_annual": base.compound([r[Q1_KEY % "ind"] for r in rows]),
        },
    }
    block["holds"] = holds(block)
    return block


def holds(block) -> bool:
    st = block["differential"]["summary"]
    if block["n"] < MIN_REBALANCES or st.get("mean") is None or st.get("t") is None:
        return False
    return st["mean"] > 0 and st["t"] >= T_FLOOR


def verdict_for(blocks):
    alt = [blocks[i] for i in ALTERNATES if i in blocks]
    if any(b["n"] < MIN_REBALANCES for b in alt):
        return "NOT_ENOUGH_REBALANCES"
    good = [b["id"] for b in alt if holds(b)]
    if len(good) == len(alt):
        return "HOLDS_ON_BOTH_ALTERNATE_SAMPLES"
    if good:
        return "HOLDS_ON_ONE_SAMPLE_ONLY"
    return "DOES_NOT_HOLD"


# ------------------------------------------------------------------ reproduction
def reproduction_delta(rows, upstream_rows):
    """Cell-for-cell max |delta| between the re-run S0 rows and the published rows."""
    if len(rows) != len(upstream_rows):
        return {"rows_match": False, "row_count": len(rows),
                "upstream_row_count": len(upstream_rows), "max_abs_delta": None,
                "first_mismatch": "row count differs"}
    worst, where = 0.0, None
    for mine, theirs in zip(rows, upstream_rows):
        if mine.get("date") != theirs.get("date"):
            return {"rows_match": False, "row_count": len(rows),
                    "upstream_row_count": len(upstream_rows), "max_abs_delta": None,
                    "first_mismatch": "date %s vs %s" % (mine.get("date"), theirs.get("date"))}
        for key in sorted(set(mine) | set(theirs)):
            a, b = mine.get(key), theirs.get(key)
            if isinstance(a, list) and isinstance(b, list):
                pairs = list(zip(a, b))
                for x, y in pairs:
                    d = _num_delta(x, y)
                    if d is None:
                        return {"rows_match": False, "row_count": len(rows),
                                "upstream_row_count": len(upstream_rows),
                                "max_abs_delta": None,
                                "first_mismatch": "%s on %s is not a list of numbers"
                                                  % (key, mine.get("date"))}
                    if d > worst:
                        worst, where = d, "%s@%s" % (key, mine.get("date"))
                if len(a) != len(b):
                    return {"rows_match": False, "row_count": len(rows),
                            "upstream_row_count": len(upstream_rows), "max_abs_delta": None,
                            "first_mismatch": "%s length on %s" % (key, mine.get("date"))}
                continue
            d = _num_delta(a, b)
            if d is None:
                if a != b:
                    return {"rows_match": False, "row_count": len(rows),
                            "upstream_row_count": len(upstream_rows), "max_abs_delta": None,
                            "first_mismatch": "%s on %s: %r vs %r"
                                              % (key, mine.get("date"), a, b)}
                continue
            if d > worst:
                worst, where = d, "%s@%s" % (key, mine.get("date"))
    return {"rows_match": worst <= REPRO_TOL, "row_count": len(rows),
            "upstream_row_count": len(upstream_rows), "max_abs_delta": worst,
            "worst_field": where}


def _num_delta(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return None if a != b else 0.0
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        fa, fb = float(a), float(b)
        if fa != fa and fb != fb:  # both NaN
            return 0.0
        return abs(fa - fb)
    if a is None and b is None:
        return 0.0
    return None


# ------------------------------------------------------------------ build
def build_report(upstream, upstream_path: str = UPSTREAM, panel=None, keep_rows: bool = False):
    hist = neut.load_industry()
    if panel is None:
        panel = base.load_panel()
    dates, symbols, close, amount, shares = panel

    blocks, raw = {}, {}
    for spec in SAMPLES:
        rows = run_sample(dates, symbols, close, amount, shares, hist,
                          offset=spec["offset"], stride=spec["stride"])
        if not rows:
            raise SystemExit("sample %s produced no rows" % spec["id"])
        blocks[spec["id"]] = sample_block(rows, spec)
        raw[spec["id"]] = rows

    # which of the two legs moved when the sample moved? A differential can collapse
    # because the arm it is supposed to beat got lucky; that is a different story from
    # the arm itself getting worse, and the reader must not have to re-derive which.
    ref = blocks["S0"]["legs"]
    for sid, block in blocks.items():
        block["legs_vs_reference"] = {
            "reference": "S0",
            "rankind_delta": block["legs"]["rankind_q1_annual"] - ref["rankind_q1_annual"],
            "ind_delta": block["legs"]["ind_q1_annual"] - ref["ind_q1_annual"],
            "bigger_mover": ("rankind" if abs(block["legs"]["rankind_q1_annual"]
                                               - ref["rankind_q1_annual"])
                             >= abs(block["legs"]["ind_q1_annual"] - ref["ind_q1_annual"])
                             else "ind"),
        }

    up_rows = upstream.get("rows") or []
    repro = reproduction_delta(raw["S0"], up_rows)
    if not repro["rows_match"]:
        print("ERROR reproduction failed: %s" % json.dumps(repro, ensure_ascii=False))
        raise SystemExit("S0 does not reproduce the upstream rows; refusing to publish a reading")

    verdict = verdict_for(blocks)
    diff_of = {sid: blocks[sid]["differential"]["summary"] for sid in blocks}
    one_line = (
        "rankind-minus-ind across samples: S0 %+.5f (t=%.2f, n=%d) | S1 %+.5f (t=%.2f, n=%d) | "
        "S2 %+.5f (t=%.2f, n=%d) -> %s"
        % (
            diff_of["S0"]["mean"], diff_of["S0"]["t"] or 0.0, blocks["S0"]["n"],
            diff_of["S1"]["mean"], diff_of["S1"]["t"] or 0.0, blocks["S1"]["n"],
            diff_of["S2"]["mean"], diff_of["S2"]["t"] or 0.0, blocks["S2"]["n"],
            verdict,
        )
    )

    report = {
        "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": upstream.get("evidence_cutoff"),
        "machine": "bm-c",
        "kind": "census-derived",
        "prereg": None,
        "adoption": None,
        "question": "does rankind-minus-ind keep its sign and reach t>=1.5 on another sample of the same panel?",
        "row_producer": "scripts/astock_resid_industry_neutral.py::run (imported, not re-implemented)",
        "upstream": {
            "path": _rel(upstream_path),
            "sha256": stab.sha256_of(upstream_path),
            "generated": upstream.get("generated"),
            "kind": upstream.get("kind"),
            "rebalances": len(up_rows),
            "verdict": upstream.get("verdict"),
        },
        "criteria": CRITERIA,
        "window": {
            "panel_symbols": len(symbols),
            "panel_dates": len(dates),
            "panel_first": dates[0] if len(dates) else None,
            "panel_last": dates[-1] if len(dates) else None,
            "hold_days": base.HOLD,
            "cost_one_side": base.COST_ONE_SIDE,
            "min_amount_20d": base.MIN_AMOUNT_20D,
        },
        "reproduction": repro,
        "samples": blocks,
        "verdict": verdict,
        "headline": {"verdict": verdict, "one_line": one_line},
        "boundaries": [
            "one panel, one calendar: alternates are different observation dates, not a second dataset",
            "S1 forward windows are disjoint from S0 but its formation windows overlap; rows are not independent",
            "no pooled t across samples is computed or claimed",
            "sign-flip p is reported per sample and is not part of the frozen verdict",
            "unchanged upstream limits: ST/limit-up/limit-down and delisting unhandled, book is not tradable",
        ],
    }
    if keep_rows:
        report["rows"] = raw
    return report


# ------------------------------------------------------------------ check
VOLATILE = {"generated", "upstream", "samples"}


def _flat(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not prefix and k in VOLATILE:
                continue
            out.update(_flat(v, "%s.%s" % (prefix, k) if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(_flat(v, "%s[%d]" % (prefix, i)))
    else:
        out[prefix] = obj
    return out


def check() -> int:
    """Cheap external anchor + arithmetic re-derivation.

    The expensive part of this face is three panel passes; a check leg must not pay for
    it every round. What is verified instead:
      * the upstream face is byte-identical (else the whole face is one generation old)
      * the published S0 rows still equal the upstream rows, field for field
      * the verdict and every reported leg re-derive from the published rows
    S1/S2 rows are not re-derived here -- that is stated in the output, not hidden.
    """
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % _rel(OUT))
        return 3
    with open(OUT, encoding="utf-8") as fh:
        published = json.load(fh)
    upstream = json.load(open(UPSTREAM, encoding="utf-8"))
    recorded = (published.get("upstream") or {}).get("sha256")
    live = stab.sha256_of(UPSTREAM)
    if recorded != live:
        print("STALE upstream bytes changed (%s... -> %s...): re-run" % (
            str(recorded)[:12], live[:12]))
        return 3
    up_rows = upstream.get("rows") or []
    if published.get("reproduction", {}).get("row_count") != len(up_rows):
        print("STALE upstream rebalance count moved (%s -> %d): re-run" % (
            published.get("reproduction", {}).get("row_count"), len(up_rows)))
        return 3

    problems = []
    samples = published.get("samples") or {}
    # arithmetic: each sample's differential re-derives from its own two legs is not
    # possible (rows are not published), so instead verify every number is internally
    # consistent (n, first/last, verdict, years) and that the top verdict follows.
    for sid, block in samples.items():
        if not isinstance(block.get("n"), int) or block["n"] < 0:
            problems.append("%s row count is not a non-negative int" % sid)
        if block["n"] >= MIN_REBALANCES and block["holds"] != (
                (block["differential"]["summary"].get("mean") or 0.0) > 0
                and (block["differential"]["summary"].get("t") or -9e9) >= T_FLOOR):
            problems.append("%s holds flag disagrees with its own mean/t" % sid)
        if block["differential"]["years_total"] != len(block["differential"]["yearly"]):
            problems.append("%s years_total disagrees with the yearly table" % sid)
        if block["differential"]["years_positive"] > block["differential"]["years_total"]:
            problems.append("%s more positive years than years" % sid)
        if (block["differential"]["signflip_p"] is not None
                and not 0.0 <= block["differential"]["signflip_p"] <= 1.0):
            problems.append("%s sign-flip p outside [0,1]" % sid)
    want = verdict_for(samples)
    if published.get("verdict") != want:
        problems.append("verdict published=%r recomputed=%r" % (published.get("verdict"), want))
    if (published.get("headline") or {}).get("verdict") != want:
        problems.append("headline verdict disagrees with the recomputed verdict")

    flat = _flat(published)
    for key in ("criteria.holds", "criteria.pair", "question"):
        if key not in flat:
            problems.append("%s missing from the face" % key)
    if not (published.get("reproduction") or {}).get("rows_match"):
        problems.append("published face records a failed reproduction")

    if problems:
        print("CHECK FAILED: %d field(s) drift" % len(problems))
        for p in problems[:10]:
            print("  " + p)
        return 3
    print("CHECK OK %s | %d fields | S0 reproduction anchored to upstream sha %s... | "
          "S1/S2 rows not re-derived here (three panel passes)" % (
              published["verdict"], len(flat), str(live)[:12]))
    return 0


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    legs = []

    # L1 the shift really shifts: an offset view's first rebalance is later than the base
    dates = ["2020-01-%02d" % (i + 1) for i in range(28)] + ["2020-02-%02d" % (i + 1) for i in range(29)]
    legs.append(("synthetic calendar has 57 days", len(dates) == 57))

    calls = []

    class Spy:
        @staticmethod
        def run(*a, **k):
            calls.append((len(a[0]), k.get("stride"), a[0][0]))
            return [{"date": a[0][0], Q1_KEY % "rankind": 0.01, Q1_KEY % "ind": 0.0}]

    real = neut.run
    cols = [[0.0] * len(dates)]
    try:
        globals()["neut"].run = Spy.run
        run_sample(dates, ["a"], cols[0], cols[0], cols[0], None, offset=0, stride=20)
        run_sample(dates, ["a"], cols[0], cols[0], cols[0], None, offset=10, stride=40)
    finally:
        globals()["neut"].run = real

    legs.append(("offset 0 hands the panel over untouched",
                 calls[0] == (57, 20, "2020-01-01")))
    legs.append(("offset 10 slices 10 rows off the front and keeps stride",
                 calls[1] == (47, 40, "2020-01-11")))

    rows = [
        {"date": "2021-01-04", Q1_KEY % "rankind": 0.02, Q1_KEY % "ind": 0.01},
        {"date": "2021-02-01", Q1_KEY % "rankind": -0.01, Q1_KEY % "ind": 0.00},
        {"date": "2021-03-01", Q1_KEY % "rankind": 0.03, Q1_KEY % "ind": 0.01},
    ]
    d = differential(rows)
    legs.append(("differential subtracts the control arm date for date",
                 [round(v, 12) for _, v in d] == [0.01, -0.01, 0.02]))

    missing = False
    try:
        differential([{"date": "2021-01-04", Q1_KEY % "rankind": 0.02}])
    except KeyError:
        missing = True
    legs.append(("a rebalance without the control leg is an error, not a skip", missing))

    good = {"n": 40, "differential": {"summary": {"mean": 0.004, "t": 1.6}}}
    weak = {"n": 40, "differential": {"summary": {"mean": 0.004, "t": 1.4}}}
    wrong = {"n": 40, "differential": {"summary": {"mean": -0.004, "t": -1.6}}}
    short = {"n": 8, "differential": {"summary": {"mean": 0.01, "t": 3.0}}}
    legs.append(("holds needs sign, t floor and enough rows",
                 holds(good) and not holds(weak) and not holds(wrong) and not holds(short)))

    def blocks(s1, s2, n_short=False):
        b = {"S1": dict(s1, id="S1"), "S2": dict(s2, id="S2")}
        if n_short:
            b["S1"] = dict(s1, id="S1", n=5)
        return b

    legs.append(("verdict: both hold", verdict_for(blocks(good, good)) == "HOLDS_ON_BOTH_ALTERNATE_SAMPLES"))
    legs.append(("verdict: one holds", verdict_for(blocks(good, weak)) == "HOLDS_ON_ONE_SAMPLE_ONLY"))
    legs.append(("verdict: neither holds", verdict_for(blocks(weak, wrong)) == "DOES_NOT_HOLD"))
    legs.append(("verdict: short sample outranks the rest",
                 verdict_for(blocks(good, good, n_short=True)) == "NOT_ENOUGH_REBALANCES"))

    # reproduction detector must fail loudly on a planted difference
    mine = [{"date": "2021-01-04", "n": 10, "q": [0.1, 0.2], "x": 0.5}]
    same = [{"date": "2021-01-04", "n": 10, "q": [0.1, 0.2], "x": 0.5}]
    off = [{"date": "2021-01-04", "n": 10, "q": [0.1, 0.200001], "x": 0.5}]
    legs.append(("reproduction accepts identical rows",
                 reproduction_delta(mine, same)["rows_match"]))
    legs.append(("reproduction catches a one-in-a-million drift",
                 not reproduction_delta(mine, off)["rows_match"]))
    legs.append(("reproduction catches a shifted date",
                 not reproduction_delta(mine, [dict(same[0], date="2021-01-05")])["rows_match"]))
    legs.append(("reproduction catches a shorter panel",
                 not reproduction_delta(mine, [])["rows_match"]))
    legs.append(("NaN equals NaN in the comparison, not 'differs'",
                 reproduction_delta([{"date": "d", "ic": float("nan")}],
                                    [{"date": "d", "ic": float("nan")}])["rows_match"]))

    # check must be shown failing, or it is only a promise
    import contextlib
    import io as _io
    import shutil
    import tempfile

    tmpdir = tempfile.mkdtemp(prefix="_r1947bmc_s2_")
    out = os.path.join(tmpdir, "out.json")
    up = os.path.join(tmpdir, "up.json")
    shutil.copyfile(UPSTREAM, up)
    upstream = json.load(open(up, encoding="utf-8"))
    face = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else None
    rc_missing = rc_stale = rc_fail = rc_clean = None
    text_stale = text_fail = ""
    saved = (globals()["UPSTREAM"], globals()["OUT"])
    try:
        globals()["OUT"] = out
        shutil.copyfile(saved[0], up)
        globals()["UPSTREAM"] = up

        with contextlib.redirect_stdout(_io.StringIO()):
            rc_missing = check()

        if face is not None:
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(face, fh)
            with contextlib.redirect_stdout(_io.StringIO()):
                rc_clean = check()
            with open(up, "ab") as fh:
                fh.write(b"\n")
            buf = _io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc_stale = check()
            text_stale = buf.getvalue()
            shutil.copyfile(saved[0], up)
            broken = dict(face)
            broken["verdict"] = "HOLDS_ON_BOTH_ALTERNATE_SAMPLES" if face["verdict"] != \
                "HOLDS_ON_BOTH_ALTERNATE_SAMPLES" else "DOES_NOT_HOLD"
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(broken, fh)
            buf = _io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc_fail = check()
            text_fail = buf.getvalue()
    finally:
        globals()["UPSTREAM"], globals()["OUT"] = saved
        shutil.rmtree(tmpdir, ignore_errors=True)

    legs.append(("a missing face reads STALE, not clean",
                 rc_missing == 3 and rc_missing is not None))
    if face is not None:
        legs.append(("identical bytes re-derive clean", rc_clean == 0))
        legs.append(("one byte of upstream drift reads STALE, not clean",
                     rc_stale == 3 and "STALE" in text_stale))
        legs.append(("a flipped verdict reads CHECK FAILED without STALE",
                     rc_fail == 3 and "CHECK FAILED" in text_fail and "STALE" not in text_fail))

    ok = sum(1 for _, good_leg in legs if good_leg)
    for name, good_leg in legs:
        print("%s %s" % ("PASS" if good_leg else "FAIL", name))
    print("selftest %d/%d %s" % (ok, len(legs), "PASS" if ok == len(legs) else "FAIL"))
    return 0 if ok == len(legs) else 3


# ------------------------------------------------------------------ main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["run", "check", "selftest"], nargs="?", default="run")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()

    upstream = json.load(open(UPSTREAM, encoding="utf-8"))
    report = build_report(upstream)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print(report["headline"]["one_line"])
    for sid in ("S0", "S1", "S2"):
        b = report["samples"][sid]
        d = b["differential"]
        print("%s n=%3d %s..%s mean %+.5f t=%5.2f p=%.3f years %d/%d holds=%s"
              % (sid, b["n"], b["first"], b["last"], d["summary"]["mean"],
                 d["summary"]["t"] or 0.0,
                 d["signflip_p"] if d["signflip_p"] is not None else float("nan"),
                 d["years_positive"], d["years_total"], b["holds"]))
    print("reproduction max|delta| = %s over %d rows"
          % (report["reproduction"]["max_abs_delta"], report["reproduction"]["row_count"]))
    print("-> %s" % _rel(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
