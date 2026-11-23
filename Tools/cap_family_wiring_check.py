"""r1991 evidence harness: does the cap-family wiring leg actually say anything?

The leg added to smoke_test.py (`config: every cap face is on the chain with a
check, in DAG order`) reads today's published state, which happens to be green.
A predicate driven only by today's green state cannot show that it would have
said "no" yesterday (r1861 third-state lesson, r1934 behavioural legs), so this
harness drives the SAME function -- imported from smoke_test, not reimplemented
-- against mutated inputs and asserts it turns red on each of the five shapes
that were actually observed or feared in this family:

  1. a face published without a top-level evidence_cutoff
     (regime_cap_breach_timeline and regime_cap_binding_days shipped that way)
  2. a writer-only chain leg (no `check` first -> a stale face never refreshes
     itself: r1935 / r1850 class)
  3. a consumer leg placed before the face it reads (r1318 class)
  4. a face that is on disk but not on the chain at all (r1322 class)
  5. a face missing from disk entirely

Run: python results/_r1991bmc_cap_family_wiring_check.py
"""
import json
import os
import shutil
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import smoke_test  # noqa: E402  (single source of the predicate)

FACES = ("regime_cap_compliance_cost", "regime_cap_measure_sizes",
         "regime_cap_breach_pnl", "regime_cap_breach_timeline",
         "regime_cap_binding_days", "regime_cap_breach_cash_vs_repo",
         "regime_cap_enforced_counterfactual")

RESULTS = []


def leg(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         (" :: " + detail) if detail else ""))


def _real_legs():
    import importlib
    return [tuple(t) for t in importlib.import_module("Tools.s6_chain_bmc").LEGS]


def _stage(tmp, mutate=None):
    """Copy the seven faces into tmp; `mutate(name, payload)` may edit/return None."""
    for name in FACES:
        src = os.path.join(_ROOT, "results", name + ".json")
        if not os.path.exists(src):
            continue
        with open(src, encoding="utf-8") as fh:
            payload = json.load(fh)
        if mutate is not None:
            payload = mutate(name, payload)
            if payload is None:
                continue
        with open(os.path.join(tmp, name + ".json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)


def main():
    real = _real_legs()

    # 1. today's state: the leg must be green (and say which faces it counted)
    tmp = tempfile.mkdtemp(prefix="r1991green_")
    try:
        _stage(tmp)
        bad = smoke_test.cap_family_wiring_problems(legs=real, results_dir=tmp)
        leg("today's seven faces pass the wiring predicate", not bad,
            "; ".join(bad)[:160])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 2. a face without a top-level cutoff must be named, not skipped
    tmp = tempfile.mkdtemp(prefix="r1991nocut_")
    try:
        _stage(tmp, lambda n, p: (p.pop("evidence_cutoff", None),
                                  p)[1] if n == "regime_cap_binding_days" else p)
        bad = smoke_test.cap_family_wiring_problems(legs=real, results_dir=tmp)
        leg("a face published without evidence_cutoff turns the leg red",
            any("regime_cap_binding_days" in b and "evidence_cutoff" in b
                for b in bad), "; ".join(bad)[:160])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 3. writer-only leg: a (check, run) pair collapsed back to (run,)
    writer_only = []
    for t in real:
        if t[0] == "regime_cap_breach_pnl" and len(t) >= 3:
            writer_only.append((t[0], t[2], t[1]))
        else:
            writer_only.append(t)
    tmp = tempfile.mkdtemp(prefix="r1991writer_")
    try:
        _stage(tmp)
        bad = smoke_test.cap_family_wiring_problems(legs=writer_only,
                                                    results_dir=tmp)
        leg("a writer-only leg (no check first) turns the leg red",
            any("regime_cap_breach_pnl" in b and "check" in b for b in bad),
            "; ".join(bad)[:160])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 4. consumer before producer
    reordered = []
    order_swap = {"regime_cap_breach_timeline", "regime_cap_compliance_cost"}
    held = []
    for t in real:
        if t[0] in order_swap:
            held.append(t)
            continue
        reordered.extend(held)
        held = []
        reordered.append(t)
    reordered.extend(held)
    reordered = [t for t in reordered if t[0] not in order_swap]
    reordered.insert(0, [t for t in real if t[0] == "regime_cap_breach_timeline"][0])
    reordered.append([t for t in real if t[0] == "regime_cap_compliance_cost"][0])
    tmp = tempfile.mkdtemp(prefix="r1991order_")
    try:
        _stage(tmp)
        bad = smoke_test.cap_family_wiring_problems(legs=reordered,
                                                    results_dir=tmp)
        leg("a consumer placed before its producer turns the leg red",
            any("runs after its reader" in b for b in bad),
            "; ".join(bad)[:160])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 5. on disk but not on the chain
    truncated = [t for t in real if t[0] != "regime_cap_measure_sizes"]
    tmp = tempfile.mkdtemp(prefix="r1991offchain_")
    try:
        _stage(tmp)
        bad = smoke_test.cap_family_wiring_problems(legs=truncated,
                                                    results_dir=tmp)
        leg("a face missing from the chain turns the leg red",
            any("regime_cap_measure_sizes" in b and "not on the chain" in b
                for b in bad), "; ".join(bad)[:160])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 6. missing file
    tmp = tempfile.mkdtemp(prefix="r1991absent_")
    try:
        _stage(tmp, lambda n, p: None if n == "regime_cap_breach_cash_vs_repo" else p)
        bad = smoke_test.cap_family_wiring_problems(legs=real, results_dir=tmp)
        leg("a missing face turns the leg red",
            any("regime_cap_breach_cash_vs_repo" in b and "face missing" in b
                for b in bad), "; ".join(bad)[:160])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    ok = sum(1 for _, c, _ in RESULTS if c)
    print("\n%d/%d PASS" % (ok, len(RESULTS)))
    return 0 if ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
