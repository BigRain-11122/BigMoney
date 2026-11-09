"""The supply floor has been red because the money was made early -- and vol target is the
one dial the desk owns that moves WHEN the money arrives without touching the selection rule.

r1428 put an ETA on every book: the adopted book needs 3 more years under the Y-gate and 10
under `years_for_half`. r1432 wired the elected ruler into the operator boards, so the desk
now prints "no lawful supply" in a sentence an allocator can read. Neither round asked the
obvious question: is there a setting of the book that clears the calendar TODAY?

The capital rule is untouched. What is swept here is the only knob below the ranking:
`vol_target` (the scaling of the selected basket), which changes the annual profile rather
than which ETFs get bought. Every arm is priced by `etf_robust_pf.open_to_open_equity` and
judged by two implementations that already exist (`candidate_year_gate.admission_block` for
Y1..Y4, `etf_book_year_caliber.calibers`/`passes` for the two trusted rulers) -- no line and
no verdict is retyped in this file.

Frozen before any number was read (echoed into the receipt, re-derived by --check):

  arms       vol_target in {none (unscaled), 0.08, 0.06, 0.04, 0.03, 0.02}
  phases     candidate_year_gate_phases.PHASE_STARTS (imported, never retyped)
  rebal/hold/cost  20 / 5 / 10bp (the published adopted book's own grid)
  verdict    ADMIT_AT_EVERY_PHASE only if, in EVERY phase, the gate reads ADMIT on all
             four Y checks AND every trusted caliber passes. A caliber with no reading in
             a phase makes the arm INDETERMINATE -- never a pass (r98: unknown is not empty).
  money face cagr / sharpe / maxdd per arm are published beside the verdict, because a book
             that clears the calendar by earning nothing is not supply.

    python scripts/etf_book_vol_target_gate.py run
    python scripts/etf_book_vol_target_gate.py check
    python scripts/etf_book_vol_target_gate.py selftest
"""
from __future__ import annotations

import io
import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import candidate_year_gate as G  # noqa: E402
import candidate_year_gate_phases as P  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_book_year_caliber as K  # noqa: E402
import etf_book_year_gate as Y  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_vol_target_gate.json")
MD = os.path.join(ROOT, "research", "ETF_BOOK_VOL_TARGET_GATE.md")

REBAL, N_HOLD, COST = 20, 5, 0.0010
ARMS = (("unscaled", None), ("vt08", 0.08), ("vt06", 0.06),
        ("vt04", 0.04), ("vt03", 0.03), ("vt02", 0.02))
TRUSTED = ("effective_years", "years_for_half")

RULE = {
    "arms": [a[0] for a in ARMS],
    "vol_targets": {a[0]: a[1] for a in ARMS},
    "phase_set": list(P.PHASE_STARTS),
    "phase_set_source": "candidate_year_gate_phases.PHASE_STARTS (imported)",
    "grid": {"rebal": REBAL, "n_hold": N_HOLD, "cost_per_side": COST},
    "gate_source": "candidate_year_gate.admission_block (imported, Y1..Y4 untouched)",
    "ruler_source": "etf_book_year_caliber.calibers/passes (imported, lines untouched)",
    "trusted_rulers": list(TRUSTED),
    "pass_rule": ("ADMIT_AT_EVERY_PHASE iff every phase reads gate ADMIT (all four Y checks) "
                  "and both trusted rulers pass; a missing reading is INDETERMINATE, never pass"),
    "does_not_change_production": ("this file prices alternative scalings of the same "
                                   "selection; it wires nothing and adopts nothing"),
    "frozen_before_read": True,
}


# ---------------------------------------------------------------- pure readings
def ruler_median(cells: list[dict], name: str) -> dict:
    """Median / unanimity of one trusted ruler across phases, with its published line."""
    spec = K.CALIBERS[name]
    vals = [c["calibers"].get(name) for c in cells]
    read = [v for v in vals if v is not None]
    out = {"ruler": name, "line": spec["line"], "pass_when": spec["pass_when"],
           "unit": spec["unit"], "phases": len(vals), "phases_read": len(read)}
    if not read:
        out.update(state="INDETERMINATE", reason="no phase published this ruler")
        return out
    med = float(statistics.median(read))
    sides = {K.passes(name, v) for v in read}
    out.update(median=round(med, 6), spread=round(float(max(read) - min(read)), 6),
               side=("pass" if sides == {True} else "fail" if sides == {False} else "mixed"))
    if len(read) != len(vals):
        out.update(state="INDETERMINATE",
                   reason="only %d of %d phases carried a reading" % (len(read), len(vals)))
    elif out["side"] == "mixed":
        out.update(state="INDETERMINATE", reason="phases land on both sides of the line")
    else:
        out.update(state="PASS" if out["side"] == "pass" else "FAIL")
    return out


def arm_reading(name: str, cells: list[dict]) -> dict:
    """Verdict for one arm over its phase cells. Pure: same input -> same output."""
    gates = [c.get("gate_verdict") for c in cells]
    rulers = {t: ruler_median(cells, t) for t in TRUSTED}
    missing = [t for t, r in rulers.items() if r["state"] == "INDETERMINATE"]
    if not cells or any(g is None for g in gates):
        word, why = "INDETERMINATE", "a phase published no gate verdict"
    elif missing:
        word, why = "INDETERMINATE", "ruler(s) with no reading: %s" % ", ".join(missing)
    elif all(g == "ADMIT" for g in gates) and all(r["state"] == "PASS" for r in rulers.values()):
        word, why = "ADMIT_AT_EVERY_PHASE", "all phases ADMIT and both trusted rulers pass"
    else:
        fails = sorted({g for g in gates if g != "ADMIT"})
        bad = [t for t, r in rulers.items() if r["state"] == "FAIL"]
        why = "gate %s%s" % (",".join(fails) or "ok",
                             ("; ruler FAIL " + ",".join(bad)) if bad else "")
        word = "REFUSED"
    return {"arm": name, "word": word, "reason": why,
            "gate_verdicts": gates,
            "rulers": rulers,
            "phases": len(cells)}


def shape_invariance(arms: list[dict], ruler: str = "years_for_half") -> dict:
    """Does scaling the book move the ruler at all?

    A vol target multiplies the whole year table by one number per phase, so any ruler that
    reads only the SHAPE of the table must come out identical. That is a claim about the
    receipts and it is checked here rather than asserted in prose: every arm is compared to
    the first arm phase by phase, and the largest per-phase difference is published. A
    non-zero difference is not an error -- it is the finding that the ruler is NOT
    scale-invariant, which would make de-risking a real admission lever.
    """
    if len(arms) < 2:
        return {"ruler": ruler, "arms_compared": len(arms), "pairs": 0,
                "max_abs_delta": None, "invariant": None,
                "reason": "fewer than two arms were priced"}
    ref = arms[0]
    worst, pairs, missing = 0, 0, 0
    for a in arms[1:]:
        for c0, c1 in zip(ref["cells"], a["cells"]):
            v0, v1 = c0["calibers"].get(ruler), c1["calibers"].get(ruler)
            if v0 is None or v1 is None:
                missing += 1
                continue
            pairs += 1
            worst = max(worst, abs(float(v1) - float(v0)))
    medians = {a["arm"]: (a["rulers"].get(ruler) or {}).get("median") for a in arms}
    read = [v for v in medians.values() if v is not None]
    mrng = None if not read else round(float(max(read) - min(read)), 6)
    admitted = [a["arm"] for a in arms if a["word"] == "ADMIT_AT_EVERY_PHASE"]
    if not pairs:
        reason = "no pair of phases published this ruler -- nothing was compared"
    elif admitted:
        reason = ("scaling reaches an arm that clears the calendar (%s) -- de-risking IS an "
                  "admission lever" % ",".join(admitted))
    elif worst == 0.0:
        reason = ("scaling cannot move this ruler (max |d| 0): only which years earn, and how "
                  "many years exist, are left")
    else:
        reason = ("scaling does move this ruler (max |d| %s) but the arm median moves %s and no "
                  "arm admits: de-risking is not an admission lever here"
                  % (round(worst, 6), mrng))
    return {"ruler": ruler, "reference_arm": ref["arm"], "arms_compared": len(arms),
            "pairs": pairs, "unreadable_pairs": missing,
            "max_abs_delta": round(worst, 6), "invariant": (pairs > 0 and worst == 0.0),
            "median_by_arm": medians, "median_range": mrng,
            "arms_admitted": admitted, "reason": reason}


def verdict_of(arms: list[dict]) -> str:
    if not arms:
        return "NO_ARMS"
    if any(a["word"] == "ADMIT_AT_EVERY_PHASE" for a in arms):
        return "LAWFUL_SUPPLY_FOUND"
    if all(a["word"] == "INDETERMINATE" for a in arms):
        return "INDETERMINATE"
    return "STILL_REFUSED"


# ---------------------------------------------------------------- run
def run() -> int:
    t0 = time.time()
    close, openp, amt, sc, n_flip = S.nobond_universe()
    cap = S.published_capacity()
    print("panel", len(close.columns), "cols", len(close), "bars flips", n_flip,
          "capacity", cap, "t=%.1fs" % (time.time() - t0), flush=True)

    arms_out = []
    for name, vt in ARMS:
        cells = []
        for start in P.PHASE_STARTS:
            ser, turn = R.open_to_open_equity(close, openp, amt, sc, REBAL, N_HOLD, COST,
                                             vol_target=vt, start=start)
            yrs = Y.yearly_returns(ser)
            rows = G._year_rows(yrs)
            blk = G.admission_block(yrs, cap, None, A.stats2(ser, "p").get("cagr"))
            st = A.stats2(ser, "p")
            cells.append({
                "start": start,
                "years": len(rows),
                "gate_verdict": blk["verdict"],
                "checks": blk["checks"],
                "calibers": K.calibers(rows),
                "cagr_pct": None if st.get("cagr") is None else round(st["cagr"] * 100, 4),
                "sharpe": None if st.get("sharpe") is None else round(float(st["sharpe"]), 4),
                "maxdd_pct": None if st.get("maxdd") is None else round(float(st["maxdd"]) * 100, 4),
                "turnover": round(turn, 2),
                "year_net_pct": {r["year"]: round(r["net_pct"], 4) for r in rows},
            })
        reading = arm_reading(name, cells)
        money = {k: (statistics.median([c[k] for c in cells if c.get(k) is not None])
                     if any(c.get(k) is not None for c in cells) else None)
                 for k in ("cagr_pct", "sharpe", "maxdd_pct", "turnover")}
        reading.update(vol_target=vt,
                       money={k: (None if v is None else round(float(v), 4))
                              for k, v in money.items()},
                       cells=cells)
        arms_out.append(reading)
        print("%-9s %-22s median cagr %s sharpe %s maxdd %s | %s" % (
            name, reading["word"],
            reading["money"]["cagr_pct"], reading["money"]["sharpe"],
            reading["money"]["maxdd_pct"], reading["reason"]), flush=True)

    face = {"tool": "etf_book_vol_target_gate", "asof": time.strftime("%Y-%m-%d"),
            "question": ("is there a vol target under which this book clears the calendar "
                         "today, rather than after the N years r1428 estimated?"),
            "rule": RULE, "capacity_cny_1day_5pct": cap,
            "arms": arms_out, "verdict": verdict_of(arms_out),
            "shape_invariance": {t: shape_invariance(arms_out, t) for t in TRUSTED},
            "verdict_reading": {
                "LAWFUL_SUPPLY_FOUND": "an arm clears the calendar at every phase -- supply exists",
                "STILL_REFUSED": "no arm clears it; the wait in r1428 is not a scaling artifact",
                "INDETERMINATE": "no arm could be read (deal with the read before the wait)",
                "NO_ARMS": "nothing was priced",
            }[verdict_of(arms_out)],
            "elapsed_sec": round(time.time() - t0, 1)}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    write_md(face)
    print("saved", OUT, flush=True)
    return 0


def write_md(face: dict) -> None:
    L = ["# ETF book -- does a vol target clear the calendar today?", "",
         "As-of %s. Verdict: **%s** -- %s" % (face["asof"], face["verdict"],
                                              face["verdict_reading"]), "",
         "| arm | vol target | verdict | median CAGR | median Sharpe | median maxDD | turnover |",
         "|---|---|---|---|---|---|---|"]
    for a in face["arms"]:
        m = a["money"]
        L.append("| %s | %s | %s | %s%% | %s | %s%% | %s |" % (
            a["arm"], a["vol_target"], a["word"], m["cagr_pct"], m["sharpe"],
            m["maxdd_pct"], m["turnover"]))
    L += ["", "## Does scaling move the ruler?", ""]
    for ruler, blk in (face.get("shape_invariance") or {}).items():
        L.append("* **%s** -- max |d| across %d phase pairs = %s, arm median range %s. %s" % (
            ruler, blk.get("pairs"), blk.get("max_abs_delta"), blk.get("median_range"),
            blk.get("reason")))
    L += ["", "## Why each arm was refused", ""]
    for a in face["arms"]:
        rs = "; ".join("%s median %s vs line %s (%s)" % (t, r.get("median"), r["line"], r["state"])
                       for t, r in a["rulers"].items())
        L.append("* **%s** -- %s" % (a["arm"], a["reason"]))
        L.append("  - rulers: %s" % rs)
        L.append("  - gate verdicts per phase: %s" % ", ".join(a["gate_verdicts"]))
    L += ["", "Money face is published beside every verdict on purpose: a scaling that "
              "clears the calendar by earning nothing is not supply, and one that earns by "
              "concentrating the year is exactly what the elected ruler refuses."]
    with io.open(MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- check
def check() -> int:
    """Re-derive every verdict from the published rows. No pricing, no hand-typed words."""
    if not os.path.exists(OUT):
        print("REFUSED: no receipt at %s" % OUT)
        return 3
    with io.open(OUT, encoding="utf-8") as f:
        face = json.load(f)
    bad = 0
    for a in face["arms"]:
        got = arm_reading(a["arm"], a["cells"])
        if got["word"] != a["word"]:
            print("MISMATCH %s: published %s re-derived %s" % (a["arm"], a["word"], got["word"]))
            bad += 1
    want = verdict_of([arm_reading(a["arm"], a["cells"]) for a in face["arms"]])
    if want != face["verdict"]:
        print("MISMATCH verdict: published %s re-derived %s" % (face["verdict"], want))
        bad += 1
    for ruler, pub in (face.get("shape_invariance") or {}).items():
        got = shape_invariance(face["arms"], ruler)
        if got["max_abs_delta"] != pub.get("max_abs_delta"):
            print("MISMATCH shape invariance %s: published %s re-derived %s" % (
                ruler, pub.get("max_abs_delta"), got["max_abs_delta"]))
            bad += 1
    print("check", "OK" if not bad else "FAILED (%d)" % bad)
    return 0 if not bad else 1


# ---------------------------------------------------------------- selftest
def _cell(gate="ADMIT", ey=4.0, yh=4):
    return {"gate_verdict": gate, "years": 7,
            "calibers": {"effective_years": ey, "years_for_half": yh,
                         "net_top2_share": 0.6, "gross_top2_share": 0.6,
                         "net_sum_pct": 40.0, "gross_sum_pct": 40.0}}


def _chk(ok, msg, errs):
    print(("[PASS]" if ok else "[FAIL]") + " " + msg)
    if not ok:
        errs.append(msg)


def _arm_shape(name, yh, word="REFUSED"):
    return {"arm": name, "word": word,
            "rulers": {"years_for_half": {"median": statistics.median(
                [v for v in yh if v is not None]) if any(v is not None for v in yh) else None}},
            "cells": [{"calibers": {"years_for_half": v}} for v in yh]}


def selftest() -> int:
    errs = []
    good = [_cell(), _cell(ey=3.6, yh=5)]
    _chk(arm_reading("a", good)["word"] == "ADMIT_AT_EVERY_PHASE",
         "L1 all phases pass both trusted rulers -> ADMIT_AT_EVERY_PHASE", errs)
    _chk(arm_reading("a", [_cell(), _cell(gate="CONDITIONAL")])["word"] == "REFUSED",
         "L2 one CONDITIONAL phase refuses the arm (no averaging across phases)", errs)
    _chk(arm_reading("a", [_cell(yh=2), _cell(yh=2)])["word"] == "REFUSED",
         "L3 the elected ruler failing every phase refuses the arm", errs)
    none_cell = _cell()
    none_cell["calibers"] = {"effective_years": None, "years_for_half": None}
    _chk(arm_reading("a", [none_cell])["word"] == "INDETERMINATE",
         "L4 a ruler with no reading is INDETERMINATE, never a pass (r98)", errs)
    mixed = [_cell(yh=4), _cell(yh=2)]
    _chk(arm_reading("a", mixed)["rulers"]["years_for_half"]["state"] == "INDETERMINATE",
         "L5 phases on both sides of the line are mixed -> INDETERMINATE", errs)
    # the leg the first draft got wrong: one passing and one failing phase is MIXED, so the
    # arm reads INDETERMINATE at the arm level too -- it is not a refusal
    _chk(arm_reading("a", mixed)["word"] == "INDETERMINATE",
         "L5b a mixed ruler makes the arm INDETERMINATE, not REFUSED", errs)
    _chk(arm_reading("a", good)["rulers"]["years_for_half"]["line"]
         == K.CALIBERS["years_for_half"]["line"],
         "L6 the printed line is imported from the ruler module, not retyped", errs)
    _chk(verdict_of([arm_reading("a", good)]) == "LAWFUL_SUPPLY_FOUND",
         "L7 face verdict is found when any arm admits", errs)
    _chk(verdict_of([arm_reading("a", [_cell(yh=2)])]) == "STILL_REFUSED",
         "L8 face verdict is refused when no arm admits", errs)
    _chk(verdict_of([arm_reading("a", [none_cell])]) == "INDETERMINATE",
         "L9 an unreadable face is INDETERMINATE, not refused and not found", errs)
    _chk(verdict_of([]) == "NO_ARMS", "L10 empty input is its own word", errs)
    # L11: the frozen rule must name every arm that was priced
    _chk(len(RULE["arms"]) == len(ARMS) == len(RULE["vol_targets"]),
         "L11 rule declares exactly the arms that are priced", errs)
    same = [_arm_shape("a", [2, 1]), _arm_shape("b", [2, 1])]
    _chk(shape_invariance(same)["invariant"] is True and
         shape_invariance(same)["max_abs_delta"] == 0.0,
         "L12 two arms with the same shape read as scale-invariant", errs)
    diff = [_arm_shape("a", [2, 1]), _arm_shape("b", [3, 1])]
    got = shape_invariance(diff)
    _chk(got["invariant"] is False and got["max_abs_delta"] == 1.0
         and got["median_range"] == 0.5,
         "L13 a ruler that moves under scaling is reported, not smoothed away", errs)
    _chk("not an admission lever" in got["reason"] and
         "IS an admission lever" not in got["reason"],
         "L13b a moved-but-never-passing ruler is not called a lever", errs)
    lever = [_arm_shape("a", [2, 1]), _arm_shape("b", [4, 5], word="ADMIT_AT_EVERY_PHASE")]
    _chk("IS an admission lever" in shape_invariance(lever)["reason"],
         "L13c a scaling that reaches an admitting arm IS called a lever", errs)
    _chk(shape_invariance(same[:1])["invariant"] is None,
         "L14 one arm cannot support an invariance claim (None, not True)", errs)
    holes = [_arm_shape("a", [2, 1]), _arm_shape("b", [None, 1])]
    _chk(shape_invariance(holes)["unreadable_pairs"] == 1,
         "L15 unreadable pairs are counted, not silently skipped", errs)
    print("selftest", "PASS" if not errs else "FAILED (%d)" % len(errs))
    return 0 if not errs else 1


def main(argv: list[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("usage: etf_book_vol_target_gate.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))