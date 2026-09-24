"""QUEUE_BANDIT v1: batch-queue bandit scheduler (UCB1 over gate_attrition ledger).

Decision-support artifact, ZERO engine runs / ZERO network / ledger_trials_added=0.
Prereg (frozen before implementation): research/QUEUE_BANDIT.md
Lane: bm-a research dept, claim MSG-20260924-0910 (F-04).

Usage:
    python scripts\\bandit_queue.py run        # read ledger -> rank arms -> results/bandit_queue.json
    python scripts\\bandit_queue.py selftest  # offline synthetic fixtures (8 checks, prereg s5)
"""

import json
import math
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import science_gates  # noqa: E402  (cutoff_meta for C2-legal top-level key)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "results", "gate_attrition.json")
OUT = os.path.join(ROOT, "results", "bandit_queue.json")

# --- frozen constants (prereg s1/s2/s3/s4 -- DO NOT tune after runs) ---

ARM_ORDER = [  # frozen table order (tiebreak + untried order)
    "portfolio-construction",
    "synthesis-crosslib",
    "patterns-confirmation",
    "event-attention-factors",
    "trend-timeseries",
    "stock-pool-tilt",
    "futures-cta",
    "pairs-cointegration",
    "low-freq-asset",
    "regime-defense",
]

BATCH_TO_ARM = {  # frozen mapping; unknown batch -> unmapped bucket (never crash)
    "EW6-portfolio-validation": "portfolio-construction",
    "IV6-portfolio-riskbudget": "portfolio-construction",
    "p4-pairs": "pairs-cointegration",
    "P4_EXT_TILT": "stock-pool-tilt",
    "CTA_P1": "futures-cta",
    "CTA_P2_NOAU": "futures-cta",
}

TIER1_KEYS = ("validated", "g1_passers", "survivors_g1_prime_v2")  # any >=1/True -> 1.0
TIER2_KEYS = ("g1_candidates", "sleeve_candidates")                # any >=1 -> 0.5
UCB_C = math.sqrt(2.0)  # Auer 2002 standard constant

STATUS_ENUM = {"open", "gated-P1", "claimed", "closed", "blocked-source", "pending-GM-CEO"}

CANDIDATES = {  # frozen registry (prereg s4, statuses advisory-only, never bypass gates)
    "portfolio-construction": [
        {"name": "corr-watch W3 monthly cadence", "status": "open"},
        {"name": "FL forward window (needs >=60 paper bars, ~2026-12)", "status": "open"},
        {"name": "cash leg delivered (T-09 bm-c r45: cash_parking additive flag + repo "
                 "rates, acceptance 26 runs all-pass, zero-registration claim)", "status": "closed"},
    ],
    "synthesis-crosslib": [
        {"name": "XSTOCK_SYNTH (stock-pool cross-lib small-K)", "status": "claimed", "by": "bm-b"},
    ],
    "patterns-confirmation": [
        {"name": "A-layer exhausted (R42); oscillator/divergence laws closed", "status": "closed"},
    ],
    "event-attention-factors": [
        {"name": "Alpha158 true-gap 7 families (Aroon x3 / WVMA / volume-RSI x3, R59)", "status": "open"},
        {"name": "moneyflow IC reference batch (collector delivered R63; panel parked "
                 "source-blocked with 30-min self-heal; IC batch when panel completes)", "status": "open"},
        {"name": "P-B sector heat (EM clist leg blocked >13h)", "status": "blocked-source"},
    ],
    "trend-timeseries": [
        {"name": "NSP1/G2_NSP1/CTA triple-closed; revival needs new prereg (+P1 for expansion)", "status": "closed"},
    ],
    "stock-pool-tilt": [
        {"name": "P4_BATCH2 0/19 + P4_EXT_TILT 0/5 friction-wall law", "status": "closed"},
    ],
    "futures-cta": [
        {"name": "CTA_P1/NOAU closed; de-leveraged variant / per-contract roll = new prereg", "status": "closed"},
    ],
    "pairs-cointegration": [
        {"name": "P4_PAIRS closed; dual-leg / intraday = P1", "status": "closed"},
    ],
    "low-freq-asset": [
        {"name": "LFC closed", "status": "closed"},
    ],
    "regime-defense": [
        {"name": "REGIME_GUARD v3 replay PASS (12.01% in-gate, r94); O-1325 enforce approved; "
                 "wiring=T-21 (co-landing 2026-10-01)", "status": "claimed", "by": "bm-b"},
    ],
}

ENGINEERING_CANDIDATES = [  # do not occupy arms (prereg s4); statuses track reality (advisory)
    {"name": "J13 v2 mill line (qualification 0.90 via v2a R65; prereg J13_V2_MINILOOP R66; "
             "IC1+IC2 novel 0/24, n_distinct 13/11; continue s9 cadence, stop when 2-run "
             "novel=0 AND n_distinct<8)", "status": "open"},
    {"name": "Optuna bayesian tuning skeleton (O-1120 D2 unfreeze: validated>=8 AND "
             "new-registrations<=1 in last window)", "status": "gated-P1"},
    {"name": "negative-event library first consumption = T-11 (signed O-1045; sequenced "
             "after XSTOCK harvest)", "status": "open"},
    {"name": "daily dual-leg T-08 (tencent validation leg; claimed r68, interactive-session "
             "WIP in tree)", "status": "claimed", "by": "bm-a + interactive session"},
]


def _gint(gates, key):
    v = gates.get(key)
    if v is None:
        return 0
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def reward_of(entry):
    """Mechanical reward rubric (prereg s2). Returns (reward, reason)."""
    gates = entry.get("gates") or {}
    for key in TIER1_KEYS:
        v = gates.get(key)
        if v is True or _gint(gates, key) >= 1:
            return 1.0, "tier1:%s" % key
    for key in TIER2_KEYS:
        if _gint(gates, key) >= 1:
            return 0.5, "tier2:%s" % key
    eliminated = entry.get("eliminated")
    if eliminated is not None and _gint({"e": eliminated}, "e") >= 1:
        return 0.0, "eliminated"
    return 0.0, "no_positive" + ("" if gates else ":missing_gates")


def build(ledger_path=LEDGER):
    with open(ledger_path, "r", encoding="utf-8-sig") as f:
        ledger = json.load(f)
    entries = ledger.get("entries", [])

    pulls = {arm: [] for arm in ARM_ORDER}
    unmapped = []
    for e in entries:
        name = e.get("batch", "")
        arm = BATCH_TO_ARM.get(name)
        if arm is None:
            unmapped.append(name)
            continue
        r, reason = reward_of(e)
        pulls[arm].append({
            "batch": name, "ts": e.get("ts"), "reward": r, "reason": reason,
            "cells_ledger_delta": e.get("cells_ledger_delta"),
            "kind": e.get("kind"),
        })

    n_total = sum(len(v) for v in pulls.values())
    arms_out = {}
    for arm in ARM_ORDER:
        pl = pulls[arm]
        n = len(pl)
        q = (sum(p["reward"] for p in pl) / n) if n else None
        if n and n_total:
            score = q + UCB_C * math.sqrt(math.log(n_total) / n)
        else:
            score = None
        arms_out[arm] = {
            "n_pulls": n,
            "mean_reward": q,
            "ucb1_score": score,
            "status": "untried" if n == 0 else "exploit",
            "last_batch": pl[-1]["batch"] if pl else None,
            "last_ts": pl[-1]["ts"] if pl else None,
            "pulls": pl,
            "candidates": CANDIDATES.get(arm, []),
        }

    untried = [a for a in ARM_ORDER if arms_out[a]["n_pulls"] == 0]
    tried = [a for a in ARM_ORDER if arms_out[a]["n_pulls"] > 0]
    exploit_ranking = sorted(
        tried, key=lambda a: (-arms_out[a]["ucb1_score"], ARM_ORDER.index(a)))
    ucb1_policy_order = untried + exploit_ranking  # faithful UCB1: untried first

    return {
        "schema": "bandit-queue v1",
        "generated": None,  # filled by run
        "source_ledger": "results/gate_attrition.json",
        "algorithm": {"name": "UCB1", "c": UCB_C, "n_total_pulls": n_total},
        "arms": arms_out,
        "exploit_ranking": exploit_ranking,
        "ucb1_policy_order": ucb1_policy_order,
        "unmapped_batches": unmapped,
        "engineering_candidates": ENGINEERING_CANDIDATES,
        "advisory_note": ("advisory only: scheduler never initiates batches; every batch "
                          "needs prereg+claim; P1-gated and GM/CEO-review items stay gated"),
        "audit": {"ledger_trials_added": 0, "kind": "decision-support"},
    }


def _atomic_write_json(path, obj):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def run():
    out = build()
    ts = None
    try:
        import datetime
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        ts = None
    out["generated"] = ts
    # C2-legal top-level metadata key (string value; cutoff_meta returns a dict)
    out.update(science_gates.cutoff_meta("2026-09-23"))
    _atomic_write_json(OUT, out)
    print("bandit_queue: wrote %s" % OUT)
    print("  n_total_pulls=%d  unmapped=%d" % (out["algorithm"]["n_total_pulls"], len(out["unmapped_batches"])))
    print("  exploit_ranking: %s" % ", ".join(
        "%s(Q=%.2f,n=%d)" % (a, out["arms"][a]["mean_reward"], out["arms"][a]["n_pulls"])
        for a in out["exploit_ranking"]))
    print("  untried (explore-first): %s" % ", ".join(out["ucb1_policy_order"][:len([a for a in ARM_ORDER if out["arms"][a]["n_pulls"] == 0])]))
    return 0


def _mk_ledger(entries):
    return {"schema": "gate-attrition-ledger v1", "entries": entries}


def selftest():
    import tempfile as tf
    ok = 0

    # 1. reward rubric branches
    r1, why1 = reward_of({"gates": {"validated": True}, "eliminated": None})
    r2, why2 = reward_of({"gates": {"g1_candidates": 3}, "eliminated": None})
    r3, why3 = reward_of({"gates": {"v2_pass": False}, "eliminated": 1})
    r4, why4 = reward_of({"batch": "x"})  # missing gates -> disclosed
    assert (r1, r2, r3, r4) == (1.0, 0.5, 0.0, 0.0), (r1, r2, r3, r4)
    assert why4.startswith("no_positive:missing_gates"), why4
    ok += 1; print("[PASS] 1 reward rubric branches 1.0/0.5/0.0/missing-field")

    # 2. UCB1 math single-point recomputation (hand value)
    # N=3: two pulls arm A (rewards 1.0,1.0), one pull arm B (reward 0.0)
    # A: 1.0 + sqrt(2)*sqrt(ln3/2) ; B: 0.0 + sqrt(2)*sqrt(ln3/1)
    exp_a = 1.0 + math.sqrt(2.0) * math.sqrt(math.log(3.0) / 2.0)
    exp_b = 0.0 + math.sqrt(2.0) * math.sqrt(math.log(3.0) / 1.0)
    tmpd = tf.mkdtemp()
    led = _mk_ledger([
        {"batch": "EW6-portfolio-validation", "gates": {"validated": True}, "eliminated": None},
        {"batch": "IV6-portfolio-riskbudget", "gates": {"validated": True}, "eliminated": None},
        {"batch": "p4-pairs", "gates": {"v2_pass": False}, "eliminated": 1},
    ])
    lp = os.path.join(tmpd, "ledger.json")
    with open(lp, "w", encoding="utf-8") as f:
        json.dump(led, f)
    out = build(lp)
    got_a = out["arms"]["portfolio-construction"]["ucb1_score"]
    got_b = out["arms"]["pairs-cointegration"]["ucb1_score"]
    assert abs(got_a - exp_a) < 1e-12 and abs(got_b - exp_b) < 1e-12, (got_a, exp_a, got_b, exp_b)
    ok += 1; print("[PASS] 2 UCB1 math bit-exact vs hand values")

    # 3. untried arms exploration-first ordering
    policy = out["ucb1_policy_order"]
    untried_count = len([a for a in ARM_ORDER if out["arms"][a]["n_pulls"] == 0])
    assert policy[:untried_count] == [a for a in ARM_ORDER if out["arms"][a]["n_pulls"] == 0]
    assert "portfolio-construction" in policy[untried_count:]  # tried comes after
    ok += 1; print("[PASS] 3 untried explore-first before tried arms")

    # 4. real batch name mapping 6/6
    real = _mk_ledger([
        {"batch": "EW6-portfolio-validation", "gates": {"validated": True}},
        {"batch": "IV6-portfolio-riskbudget", "gates": {"validated": True}},
        {"batch": "p4-pairs", "gates": {"v2_pass": False}, "eliminated": 1},
        {"batch": "P4_EXT_TILT", "gates": {"survivors_g1_prime_v2": 0}, "eliminated": 47},
        {"batch": "CTA_P1", "gates": {"g1_passers": 0}, "eliminated": 16},
        {"batch": "CTA_P2_NOAU", "gates": {"g1_passers": 0}, "eliminated": 16},
    ])
    lp2 = os.path.join(tmpd, "real.json")
    with open(lp2, "w", encoding="utf-8") as f:
        json.dump(real, f)
    out2 = build(lp2)
    assert not out2["unmapped_batches"]
    assert out2["algorithm"]["n_total_pulls"] == 6
    assert out2["arms"]["futures-cta"]["n_pulls"] == 2
    ok += 1; print("[PASS] 4 real batch mapping 6/6 zero unmapped")

    # 5. unknown batch name -> unmapped, no crash
    weird = _mk_ledger([{"batch": "TOTALLY-NEW-BATCH", "gates": {"validated": True}}])
    lp3 = os.path.join(tmpd, "weird.json")
    with open(lp3, "w", encoding="utf-8") as f:
        json.dump(weird, f)
    out3 = build(lp3)
    assert out3["unmapped_batches"] == ["TOTALLY-NEW-BATCH"]
    assert out3["algorithm"]["n_total_pulls"] == 0
    ok += 1; print("[PASS] 5 unknown batch -> unmapped bucket, no crash")

    # 6. tiebreak = frozen table order (two zero-reward n=1 arms)
    tie = _mk_ledger([
        {"batch": "p4-pairs", "gates": {}, "eliminated": 1},
        {"batch": "P4_EXT_TILT", "gates": {}, "eliminated": 47},
    ])
    lp4 = os.path.join(tmpd, "tie.json")
    with open(lp4, "w", encoding="utf-8") as f:
        json.dump(tie, f)
    out4 = build(lp4)
    er = out4["exploit_ranking"]
    assert er[0] == "stock-pool-tilt" and er[1] == "pairs-cointegration", er
    # stock-pool-tilt (idx 5) precedes pairs-cointegration (idx 7) in ARM_ORDER
    ok += 1; print("[PASS] 6 score tie broken by frozen table order")

    # 7. evidence_cutoff top-level key exists and is a string (C2 contract)
    out5 = build(lp2)
    out5.update(science_gates.cutoff_meta("2026-09-23"))
    assert isinstance(out5.get("evidence_cutoff"), str) and out5["evidence_cutoff"] == "2026-09-23"
    ok += 1; print("[PASS] 7 evidence_cutoff top-level string key present")

    # 8. candidate status enum legality
    for arm, cands in CANDIDATES.items():
        assert arm in ARM_ORDER, arm
        for c in cands:
            assert c["status"] in STATUS_ENUM, c
    for c in ENGINEERING_CANDIDATES:
        assert c["status"] in STATUS_ENUM, c
    ok += 1; print("[PASS] 8 candidate statuses all in frozen enum")

    print("selftest: %d/8 PASS" % ok)
    return 0


def main(argv):
    if len(argv) < 2 or argv[1] == "run":
        return run()
    if argv[1] == "selftest":
        return selftest()
    print("usage: bandit_queue.py [run|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
