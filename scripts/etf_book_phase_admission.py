"""The adopted book's admission gate, read on every decision phase instead of one.

The CEO page has been printing two verdicts at once for a week (r1684's three-veto
readings say ADMIT; r1419's five-phase face says UNADJUDICABLE_PHASE) and telling the
reader in the same breath that the second one is still reading the OLD year rulers, so
the two sentences are not adjudicating the same ruler. A page that explains why its two
verdicts disagree, forever, is a page that never finishes the sentence.

This face finishes it: it reprices the adopted book on the same five weekly starts that
span one 20-bar rebalance block (imported from candidate_year_gate_phases, never
retyped) and puts the THREE veto-bearing readings -- S1 out-of-sample Sharpe, A1 CAGR
after cost, K1 one day's order against 1% of the weakest slot's ADV -- through
candidate_year_gate.decision_block on each of them. The thresholds are imported from
candidate_year_gate; nothing here can drift away from the gate the desk actually runs.

What the phases can and cannot move is printed, not assumed:

  * S1 and A1 are properties of the priced series, so they move with the decision grid.
  * K1 is a property of TODAY's tape (20-bar median turnover of the five slots the
    book would buy today), so it is identical at every phase by construction. It is
    still evaluated at every phase -- an admission that cannot fit the order is not an
    admission -- but a reader must not read a phase swing in it.

The aggregate is four words, derived from the per-phase verdicts (never hand-written):

  ADMIT_AT_EVERY_PHASE       every phase ADMITs -- the gate is not a coin toss on this
                             book, so the page's two-verdict paragraph can be retired
  REFUSED_AT_SOME_PHASE      at least one phase DENYs -- and which ruler refused, at
                             which start, is printed beside it
  INSUFFICIENT_AT_SOME_PHASE at least one phase could not be measured; "I could not
                             check it" outranks a pass and is never folded into one
  CANNOT_VERIFY              no phase published a verdict at all

Usage:
    python scripts/etf_book_phase_admission.py run
    python scripts/etf_book_phase_admission.py check
    python scripts/etf_book_phase_admission.py selftest
"""

from __future__ import annotations

import argparse
import io
import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import candidate_year_gate_phases as P  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_book_year_gate as Y  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_phase_admission.json")
GATE = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")
BOOK = "nobond_vt08_adopted"
# the phase-0 start is 2020-01-01 while the panel starts 2020-01-02; the two are the
# same grid cell for the purpose of the control leg below.
CONTROL_TOL_SHARPE = 0.02
CONTROL_TOL_CAGR_PP = 0.20


def _verdict_rank(v: str) -> int:
    """How much action a phase verdict asks for. Higher = stronger claim."""
    return {"ADMIT": 0, "DENY": 1, "INSUFFICIENT": 2}.get(str(v), 3)


def aggregate(rows: list[dict]) -> dict:
    """Pure: five per-phase verdicts -> the four-word state + the evidence.

    The order of the tests is the point. A phase that could not be measured is not a
    phase that passed (r98 / r1159), so INSUFFICIENT is tested before DENY: a face that
    silently reported "all phases admit" while one leg was unreadable would be the
    r1282/r1594 shape -- a green that proves only its own self-consistency.
    """
    out = {"phases": len(rows), "starts": [r.get("start") for r in rows],
           "verdicts": [r.get("verdict") for r in rows]}
    known = [r for r in rows if r.get("verdict") in ("ADMIT", "DENY", "INSUFFICIENT")]
    if not known:
        out.update(state="CANNOT_VERIFY", reason="no phase published a verdict")
        return out

    out["distinct_verdicts"] = sorted({r["verdict"] for r in known})
    out["admit_phases"] = sum(1 for r in known if r["verdict"] == "ADMIT")
    out["deny_phases"] = sum(1 for r in known if r["verdict"] == "DENY")
    out["insufficient_phases"] = sum(1 for r in known if r["verdict"] == "INSUFFICIENT")

    sharpe = [float(r["oos_sharpe"]) for r in known if r.get("oos_sharpe") is not None]
    cagr = [float(r["cagr_pct"]) for r in known if r.get("cagr_pct") is not None]
    if sharpe:
        out.update(oos_sharpe_min=round(min(sharpe), 4), oos_sharpe_max=round(max(sharpe), 4),
                   oos_sharpe_spread=round(max(sharpe) - min(sharpe), 4))
    if cagr:
        out.update(cagr_min_pct=round(min(cagr), 4), cagr_max_pct=round(max(cagr), 4),
                   cagr_spread_pp=round(max(cagr) - min(cagr), 4))
    # "weakest phase" means the one a reader would act on: a phase that refuses or
    # cannot be measured if any exist, otherwise the phase with the smallest margin on
    # the OOS Sharpe ruler (the one closest to flipping, not simply the earliest).
    non_admit = [r for r in known if r["verdict"] != "ADMIT"]
    if non_admit:
        weakest = max(non_admit, key=lambda r: _verdict_rank(r["verdict"]))
        out["weakest_because"] = "verdict=%s" % weakest["verdict"]
    else:
        cand = [r for r in known if r.get("oos_sharpe") is not None]
        weakest = min(cand, key=lambda r: float(r["oos_sharpe"])) if cand else known[0]
        out["weakest_because"] = "smallest oos_sharpe margin"
    out["weakest_phase"] = weakest.get("start")

    if out["insufficient_phases"]:
        unreadable = sorted({k for r in known for k, v in (r.get("checks") or {}).items()
                             if v is None})
        out.update(state="INSUFFICIENT_AT_SOME_PHASE",
                   reason="%d of %d phases could not be measured%s"
                          % (out["insufficient_phases"], len(known),
                             (" (%s)" % "/".join(unreadable)) if unreadable else ""))
        return out
    if out["deny_phases"]:
        failed = sorted({k for r in known for k in (r.get("failed_checks") or [])})
        wh = [r["start"] for r in known if r["verdict"] == "DENY"]
        out.update(state="REFUSED_AT_SOME_PHASE",
                   reason="%d of %d phases DENY (%s) on %s"
                          % (out["deny_phases"], len(known), ", ".join(wh),
                             "/".join(failed) or "unnamed ruler"))
        return out
    out.update(state="ADMIT_AT_EVERY_PHASE",
               reason="all %d phases ADMIT on the three veto readings" % len(known))
    return out


def spread_state(values: list[float], verdicts: list[str], line: float) -> dict:
    """The r1419 aggregate rule, applied to a ruler that is not top-2 share.

    The rule text lives in `candidate_year_gate_phases.RULE` and the selftest pins this
    function against `candidate_year_gate_phases.adjudicate` on the same numbers, so the
    two readings of "the phases disagree more than the signal" cannot drift apart:
    a phase spread wider than the median's distance to the line means the verdict was a
    coin toss over start dates, whatever ruler produced it.
    """
    vals = [float(v) for v in values if v is not None]
    out = {"phases": len(verdicts), "line": round(float(line), 4),
           "distinct_verdicts": sorted(set(verdicts))}
    if not vals:
        out.update(state="UNADJUDICABLE_PHASE", reason="no phase published a value",
                   median=None, spread=None, margin=None)
        return out
    med = float(statistics.median(vals))
    spread = float(max(vals) - min(vals))
    margin = abs(med - float(line))
    out.update(median=round(med, 4), spread=round(spread, 4), margin=round(margin, 4),
               spread_exceeds_margin=bool(spread > margin))
    if len(set(verdicts)) > 1:
        out.update(state="UNADJUDICABLE_PHASE",
                   reason="phases disagree on the verdict: %s"
                          % ", ".join(sorted(set(verdicts))))
        return out
    if spread > margin:
        out.update(state="UNADJUDICABLE_PHASE",
                   reason=("phase spread %.4f is wider than the %.4f distance from the "
                           "median to the %.2f line" % (spread, margin, float(line))))
        return out
    out.update(state=verdicts[0],
               reason=("all %d phases read %s and the spread %.4f is inside the %.4f "
                       "margin" % (len(verdicts), verdicts[0], spread, margin)))
    return out


def live_picks(sc, amt):
    """The five slots the book buys today, and the weakest one's 20-bar median amount.

    Same recipe as etf_book_year_gate (nlargest 5 of the last score row) because the
    capacity ruler is the gate's own: an equal-weight book must fill its worst name.
    """
    last = sc.index[-1]
    picks = list(sc.loc[last].dropna().nlargest(5).index)
    advs = {}
    for sym in picks:
        if sym in amt.columns:
            med = float(amt[sym].tail(20).median())
            if pd.notna(med) and med > 0:
                advs[sym] = med
    weakest = min(advs.values()) if advs else None
    return picks, advs, weakest


def run() -> int:
    t0 = time.time()
    close, openp, amt, sc, n_flip = S.nobond_universe()
    picks, advs, adv_weakest = live_picks(sc, amt)
    rows = []
    for start in P.PHASE_STARTS:
        ser, turn = P.arm(close, openp, amt, sc, 0.08, 0.0, start)
        osr = G.oos_sharpe(ser)
        cagr = A.stats2(ser, BOOK).get("cagr")
        cagr_pct = None if cagr is None else round(float(cagr) * 100.0, 4)
        blk = G.decision_block(osr, cagr_pct, adv_weakest, len(picks) or None)
        rows.append({
            "start": start,
            "verdict": blk["verdict"],
            "oos_sharpe": osr,
            "cagr_pct": cagr_pct,
            "checks": blk["checks"],
            "failed_checks": blk["failed_checks"],
            "bars": int(len(ser.dropna())),
            "first_bar": str(pd.Timestamp(ser.dropna().index[0]).date()),
            "last_bar": str(pd.Timestamp(ser.dropna().index[-1]).date()),
            "turnover_per_side": round(float(turn), 3),
        })
        print("  %s -> %-12s oos_sharpe %s cagr %s"
              % (start, blk["verdict"], osr, cagr_pct), flush=True)

    agg = aggregate(rows)
    print("%s -> %s (%s)" % (BOOK, agg["state"], agg.get("reason")), flush=True)

    # The same r1419 rule that decided the old face is now run on the NEW rulers. A
    # verdict that four of five phases share can still be a coin toss if the spread
    # across starts is wider than the distance to the line -- that is exactly what the
    # rule says, and it is the question the CEO page has been leaving open.
    phase_verdicts = [r["verdict"] for r in rows]

    def one_ruler(key):
        """Per-phase verdicts of ONE ruler, so 'these phases disagree' means that ruler
        disagreed with itself -- not that a different ruler refused."""
        out = []
        for r in rows:
            v = (r.get("checks") or {}).get(key)
            out.append("INSUFFICIENT" if v is None else ("ADMIT" if v else "DENY"))
        return out

    spread_s1 = spread_state([r.get("oos_sharpe") for r in rows], one_ruler("S1_oos_sharpe"),
                             G.GATE_OOS_SHARPE_MIN)
    spread_a1 = spread_state([r.get("cagr_pct") for r in rows], one_ruler("A1_cagr_after_cost"),
                             G.GATE_CAGR_MIN_PCT)
    spread_s1["ruler"] = "S1_oos_sharpe"
    spread_a1["ruler"] = "A1_cagr_after_cost"
    spread_reading = {
        "rule_source": "candidate_year_gate_phases.RULE['aggregate'] (imported text, "
                       "pinned against candidate_year_gate_phases.adjudicate in selftest)",
        "verdict_input": "each ruler's own per-phase verdict (one_ruler), so a spread "
                         "sentence names the ruler that disagreed with itself; the "
                         "whole-gate verdicts are printed beside it as whole_verdicts",
        "whole_verdicts": phase_verdicts,
        "S1": spread_s1,
        "A1": spread_a1,
    }

    old_phase = {}
    try:
        with io.open(P.OUT, encoding="utf-8") as f:
            op = json.load(f)
        for b in op.get("books") or []:
            if b.get("book") == BOOK:
                old_phase = {"face_asof": op.get("asof"),
                             "state": (b.get("adjudication") or {}).get("state"),
                             "median_top2_share": (b.get("adjudication") or {}).get("median_top2_share"),
                             "spread_pp": (b.get("adjudication") or {}).get("spread_pp"),
                             "rulers": "Y4 top-2 share (the r1684 gate demoted this ruler "
                                       "to a diagnostic; r1426 found it cannot adjudicate "
                                       "itself on phases)"}
    except Exception:                                            # noqa: BLE001
        old_phase = {"state": None, "why": "the old phase face is not readable"}

    gate_decision = None
    try:
        with io.open(GATE, encoding="utf-8") as f:
            gj = json.load(f)
        gate_decision = {"asof": gj.get("asof"),
                         "data_last": (gj.get("data") or {}).get("last"),
                         "verdict": (gj.get("decision") or {}).get("verdict"),
                         "reads": {k: v for k, v in
                                   ((gj.get("decision") or {}).get("reads") or {}).items()
                                   if k != "capacity_by_capital"}}
    except Exception:                                            # noqa: BLE001
        gate_decision = {"verdict": None, "why": "YEAR-GATE.json is not readable"}

    control = None
    if gate_decision and gate_decision.get("reads") and rows:
        p0 = rows[0]
        gs = gate_decision["reads"].get("oos_sharpe")
        gc = gate_decision["reads"].get("cagr_after_cost_pct")
        d_sharpe = None if (gs is None or p0["oos_sharpe"] is None) else round(
            float(p0["oos_sharpe"]) - float(gs), 4)
        d_cagr = None if (gc is None or p0["cagr_pct"] is None) else round(
            float(p0["cagr_pct"]) - float(gc), 4)
        control = {"phase": p0["start"], "gate_asof": gate_decision.get("asof"),
                   "delta_oos_sharpe": d_sharpe, "delta_cagr_pp": d_cagr,
                   "tolerance": {"oos_sharpe": CONTROL_TOL_SHARPE,
                                 "cagr_pp": CONTROL_TOL_CAGR_PP},
                   "reproduces": (d_sharpe is not None and d_cagr is not None
                                  and abs(d_sharpe) <= CONTROL_TOL_SHARPE
                                  and abs(d_cagr) <= CONTROL_TOL_CAGR_PP),
                   "why": ("phase 0 starts 2020-01-01 and the gate's own run starts on the "
                           "panel's first bar; the two must price the same series, so a "
                           "gap here is a defect in THIS face, not in the gate")}

    out = {
        "artifact": "etf_book_phase_admission",
        "face": "etf_book_phase_admission",
        "asof": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "question": ("the three veto readings that decide whether this book can take new "
                     "capital were only ever evaluated on one decision phase; does the "
                     "same gate answer the same way at every phase?"),
        "book": BOOK,
        "phases_from": "candidate_year_gate_phases.PHASE_STARTS (imported, not retyped)",
        "gate_lines_imported": {
            "oos_sharpe_min": G.GATE_OOS_SHARPE_MIN,
            "oos_start": G.GATE_OOS_START,
            "cagr_min_pct": G.GATE_CAGR_MIN_PCT,
            "impact_max_pct_of_adv": G.GATE_IMPACT_MAX * 100.0,
            "capacity_lens": [t for _c, t in G.GATE_CAPITALS_CNY],
        },
        "data": {"bars": int(len(close.index)),
                 "first": str(pd.Timestamp(close.index[0]).date()),
                 "last": str(pd.Timestamp(close.index[-1]).date()),
                 "flips_repaired": int(n_flip),
                 "bond_free_universe": int(len(close.columns)),
                 "live_picks": picks,
                 "live_picks_asof": str(pd.Timestamp(sc.index[-1]).date()),
                 "adv_median_by_slot": {k: round(v, 0) for k, v in advs.items()},
                 "adv_weakest_cny": None if adv_weakest is None else round(adv_weakest, 0)},
        "phase_rows": rows,
        "adjudication": agg,
        "spread_reading": spread_reading,
        "control_vs_gate": control,
        "gate_face": gate_decision,
        "old_phase_face": old_phase,
        "honest": [
            "K1 is a reading of today's tape, so it is identical at every phase by "
            "construction; only S1 and A1 can move with the decision grid",
            "the gate's own YEAR-GATE face prices the book once (phase 0); this face "
            "prices it five times and does not replace that face's printed numbers",
            "five weekly starts are one rebalance block, not a sample of all calendars; "
            "a sixth start would be a sixth coin toss, not new evidence",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print(json.dumps({"state": agg["state"], "reason": agg.get("reason"),
                      "control": None if control is None else control["reproduces"],
                      "elapsed_sec": out["elapsed_sec"]}, ensure_ascii=False))
    print("saved", OUT)
    return 0


def check() -> int:
    """Re-derive the aggregate from the published rows and name what does not hold."""
    if not os.path.exists(OUT):
        print("FACE MISSING: %s" % OUT)
        return 3
    with io.open(OUT, encoding="utf-8") as f:
        face = json.load(f)
    problems = []
    rows = face.get("phase_rows") or []
    if not rows:
        problems.append("FACE EMPTY: no phase rows")
    agg = aggregate(rows) if rows else {"state": "CANNOT_VERIFY", "reason": "no rows"}
    pub = face.get("adjudication") or {}
    if pub.get("state") != agg["state"]:
        problems.append("VERDICT DRIFT: published %s, re-derived %s"
                        % (pub.get("state"), agg["state"]))
    for key in ("admit_phases", "deny_phases", "insufficient_phases",
                "oos_sharpe_spread", "cagr_spread_pp"):
        if agg.get(key) != pub.get(key):
            problems.append("NUMBER DRIFT %s: published %r, re-derived %r"
                            % (key, pub.get(key), agg.get(key)))
    ctl = face.get("control_vs_gate") or {}
    if ctl and ctl.get("reproduces") is not True:
        problems.append("CONTROL FAILED: phase 0 does not reproduce the gate's own "
                        "reading (%s)" % ctl)
    cut = face.get("evidence_cutoff")
    if not cut:
        problems.append("NO CUTOFF: the face does not say which bar it priced")
    # r1850: a face whose own check re-derives from its own rows is always self-consistent,
    # so freshness has to be asked of an EXTERNAL anchor. The gate prices the same book on
    # the same panel, and the two are printed side by side -- a bar between them would turn
    # a book difference into a rebuild artefact.
    try:
        with io.open(GATE, encoding="utf-8") as f:
            gate_last = ((json.load(f) or {}).get("data") or {}).get("last")
        if cut and gate_last and str(cut) < str(gate_last):
            problems.append("STALE FACE_BEHIND_GATE: this face priced %s, the gate's panel is %s"
                            % (cut, gate_last))
    except Exception:                                            # noqa: BLE001
        problems.append("UNREADABLE GATE: cannot check freshness against %s" % GATE)
    if problems:
        print(json.dumps({"ok": False, "problems": problems}, ensure_ascii=False, indent=1))
        return 3
    print(json.dumps({"ok": True, "state": agg["state"], "phases": len(rows),
                      "evidence_cutoff": cut}, ensure_ascii=False))
    return 0


def selftest() -> int:
    """Fixtures only -- the aggregate must be reachable in all four words."""
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def r(start, verdict, sharpe=1.0, cagr=10.0, failed=None, checks=None):
        return {"start": start, "verdict": verdict, "oos_sharpe": sharpe, "cagr_pct": cagr,
                "failed_checks": failed or [],
                "checks": checks or {"S1_oos_sharpe": verdict != "DENY",
                                     "A1_cagr_after_cost": True,
                                     "K1_capacity_1pct_adv": True}}

    def L1_all_admit():
        a = aggregate([r("p%d" % i, "ADMIT") for i in range(5)])
        assert a["state"] == "ADMIT_AT_EVERY_PHASE", a

    def L2_one_deny_refuses():
        rows = [r("p%d" % i, "ADMIT") for i in range(4)] + [
            r("p4", "DENY", sharpe=0.4, cagr=4.0, failed=["S1_oos_sharpe"],
              checks={"S1_oos_sharpe": False, "A1_cagr_after_cost": False,
                      "K1_capacity_1pct_adv": True})]
        a = aggregate(rows)
        assert a["state"] == "REFUSED_AT_SOME_PHASE", a
        assert "S1_oos_sharpe" in a["reason"], "被拒的尺子必须点名: %r" % (a["reason"],)
        assert a["weakest_phase"] == "p4", a

    def L3_unreadable_outranks_deny():
        # r98/r1159: "I could not measure it" is not "it passed", and it is not folded
        # into DENY either -- the two ask for different actions.
        rows = [r("p0", "INSUFFICIENT", sharpe=None, cagr=None,
                  checks={"S1_oos_sharpe": None, "A1_cagr_after_cost": True,
                          "K1_capacity_1pct_adv": True}),
                r("p1", "DENY", failed=["A1_cagr_after_cost"],
                  checks={"S1_oos_sharpe": True, "A1_cagr_after_cost": False,
                          "K1_capacity_1pct_adv": True})]
        a = aggregate(rows)
        assert a["state"] == "INSUFFICIENT_AT_SOME_PHASE", a
        assert "S1_oos_sharpe" in a["reason"], a

    def L4_no_rows_is_cannot_verify():
        a = aggregate([])
        assert a["state"] == "CANNOT_VERIFY", a

    def L5_spread_is_max_minus_min():
        rows = [r("p0", "ADMIT", sharpe=1.70, cagr=11.30),
                r("p1", "ADMIT", sharpe=1.79, cagr=11.38),
                r("p2", "ADMIT", sharpe=1.62, cagr=11.12)]
        a = aggregate(rows)
        assert abs(a["oos_sharpe_spread"] - 0.17) < 1e-9, a
        assert abs(a["cagr_spread_pp"] - 0.26) < 1e-6, a

    def L6_state_names_follow_counts():
        # a verdict word may not be hand-written: every state must be reachable from a
        # count, and the counts printed must be the ones that produced it.
        rows = [r("p0", "ADMIT"), r("p1", "ADMIT"), r("p2", "DENY",
                failed=["K1_capacity_1pct_adv"],
                checks={"S1_oos_sharpe": True, "A1_cagr_after_cost": True,
                        "K1_capacity_1pct_adv": False})]
        a = aggregate(rows)
        assert (a["admit_phases"], a["deny_phases"], a["insufficient_phases"]) == (2, 1, 0), a
        assert a["state"] == "REFUSED_AT_SOME_PHASE"
        assert "K1_capacity_1pct_adv" in a["reason"]

    def L7_spread_rule_matches_the_r1419_engine():
        # The rule may not be re-invented here: the same numbers handed to the old
        # face's own adjudicator must produce the same state.
        vals = [0.693, 1.0436, 1.2339, 1.612, 1.7928]
        verds = ["DENY", "ADMIT", "ADMIT", "ADMIT", "ADMIT"]
        mine = spread_state(vals, verds, 0.70)
        theirs = P.adjudicate([{"start": "p%d" % i, "verdict": v, "top2_share": x}
                               for i, (v, x) in enumerate(zip(verds, vals))], line=0.70)
        assert mine["state"] == theirs["state"], (mine, theirs)
        assert abs(mine["spread"] - theirs["spread_pp"] / 100.0) < 1e-9, (mine, theirs)
        assert abs(mine["margin"] - theirs["margin_pp"] / 100.0) < 1e-9, (mine, theirs)
        # and it must actually be able to reach the other two states
        ok = spread_state([1.70, 1.72, 1.71], ["ADMIT"] * 3, 0.70)
        assert ok["state"] == "ADMIT", ok
        wide = spread_state([0.75, 1.90, 1.30], ["ADMIT"] * 3, 0.70)
        assert wide["state"] == "UNADJUDICABLE_PHASE", wide

    for name, fn in [
        ("L1 五相位全 ADMIT", L1_all_admit),
        ("L2 一相位 DENY=拒 且点名尺子与起点", L2_one_deny_refuses),
        ("L3 读不出优先于被拒（r98）", L3_unreadable_outranks_deny),
        ("L4 无相位=CANNOT_VERIFY", L4_no_rows_is_cannot_verify),
        ("L5 spread=最大减最小", L5_spread_is_max_minus_min),
        ("L6 判词由计数决定", L6_state_names_follow_counts),
        ("L7 spread 规则与 r1419 引擎逐数一致", L7_spread_rule_matches_the_r1419_engine),
    ]:
        leg(name, fn)

    passed = sum(1 for _n, ok, _m in legs if ok)
    for n, ok, msg in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", n, "" if ok else "  <- " + msg))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
