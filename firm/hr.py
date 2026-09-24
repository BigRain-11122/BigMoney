"""HR system: evaluate traders, promote/fire automatically.

Usage:
    python -m firm.hr
"""
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
TRADERS_DIR = ROOT / "firm" / "traders"
G25_DIR = ROOT / "results" / "g25"

# promotion thresholds
# INTERN->TRAINEE requires paper tracking: backtest evidence alone must never
# promote (PLAN.md 0.6 no-live-before-paper; prevents wall-of-fame fake promotes)
# win_rate_min: advisory-only, NOT enforced (3 monthly points = noise-dominated;
# see firm/review/promotion.md v2). dd caps enforced via abs() -- dd is stored
# negative-signed (O-20260924-1727 F-1 fix: plain <= made the cap vacuous).
THRESHOLDS = {
    "INTERN_TO_TRAINEE": {"os_sharpe_min": 0.8, "trades_min": 30, "max_dd_max": 0.25,
                          "paper_months_min": 1},
    "TRAINEE_TO_TRADER": {"months_min": 3, "win_rate_min": 0.55, "max_dd_max": 0.15},
    "TRADER_TO_SENIOR": {"months_min": 6, "sharpe_min": 1.0},
    "SENIOR_TO_PRINCIPAL": {"months_min": 12, "sharpe_min": 1.5, "max_dd_max": 0.15},
}

FIRE_REASONS = {
    "paper_dd": "模拟盘回撤>20%",
    "live_monthly_loss": "实盘单月亏>8%",
    "ic_decay": "IC衰减>50%",
    "risk_violation": "违反风控",
}

ALLOCATION = {
    "PROSPECT": 0,   # T-24 (O-20260924-1542): observation tier below INTERN,
                     # allocation PERMANENTLY 0 (hard-asserted in run_review);
                     # excluded from scorecard ranking + EW6/IV6 composition
                     # by construction (live.paper.PAPER_LEVELS untouched).
    "INTERN": 0, "TRAINEE": 0, "TRADER": 5,
    "SENIOR": 15, "PRINCIPAL": 30, "FIRED": 0,
}

# PROSPECT -> INTERN is EVIDENCE-gated, never metrics-auto-promoted (ticket
# T-202609-24-24 spec verbatim: full G2 neighborhood + cost x2/x3 + per-year
# AND T-22 virtual-timepoint mass batch beat-passive 0.70 pass -- promotion
# standards NOT relaxed). _evaluate_level therefore always HOLDs PROSPECT;
# the promotion itself is executed by the registration pipeline once both
# evidence packs pass, recorded via status_history.
PROSPECT_PROMOTION_GATE = {
    "g2_full": "G2 neighborhood + cost x2/x3 + per-year (frozen, no relaxation)",
    "t22_beat_passive": "T-22 virtual-timepoint mass batch beat_rate_6m >= 0.70 "
                        "(O-20260924-1532, P-5/P-5B frozen caliber)",
}


def load_trader(tid: str) -> dict:
    p = TRADERS_DIR / f"{tid}.json"
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_trader(t: dict) -> None:
    p = TRADERS_DIR / f"{t['id']}.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(t, f, indent=2, ensure_ascii=False)


def list_traders() -> list[dict]:
    out = []
    for p in sorted(TRADERS_DIR.glob("*.json")):
        if p.name.startswith("_"):
            continue
        with open(p, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def g25_verdict(tid: str) -> str:
    """Per-trader G2.5 three-check verdict (DSR/CI/PBO) from results/g25/<ID>.json.

    BACKTEST_SCIENCE.md s8: G2.5 is a promotion precondition -- missing/fail/
    pending (insufficient) = no promotion, paper observation continues.
    Written by scripts/g25_retro.py (T-02 4/7); this file only READS verdicts.
    """
    p = G25_DIR / f"{tid}.json"
    if not p.exists():
        return "missing"
    try:
        with open(p, encoding="utf-8") as f:
            v = json.load(f).get("verdict")
    except (OSError, ValueError):
        return "invalid"
    return v if v in ("pass", "fail", "pending") else "invalid"


def evaluate(t: dict) -> str:
    """Return action: PROMOTE / FIRE / HOLD."""
    lvl = t["level"]
    if lvl == "FIRED":
        return "HOLD"

    action = _evaluate_level(t)
    # G2.5 promotion precondition (audit P0-1): only a full three-check pass
    # may promote; missing/fail/pending/invalid all hold. Never gates FIRE.
    if action == "PROMOTE" and g25_verdict(t["id"]) != "pass":
        return "HOLD"
    return action


def _evaluate_level(t: dict) -> str:
    """Level ladder (unchanged thresholds); promotion gating lives in evaluate()."""
    lvl = t["level"]

    # PROSPECT (T-24): observation-only tier, allocation 0 by construction,
    # zero capital risk; ladder auto-actions OFF (no auto-promote, no
    # auto-fire) -- promotion is evidence-gated per PROSPECT_PROMOTION_GATE.
    if lvl == "PROSPECT":
        return "HOLD"

    # INTERN -> TRAINEE
    if lvl == "INTERN":
        os_ = t["backtest"]["out_sample"]
        th = THRESHOLDS["INTERN_TO_TRAINEE"]
        if (t["paper"]["months_tracked"] >= th["paper_months_min"]
                and os_["sharpe"] >= th["os_sharpe_min"]
                and os_["trades"] >= th["trades_min"]
                and abs(os_["max_dd"]) <= th["max_dd_max"]):
            return "PROMOTE"
        # fail after 3 months
        return "HOLD"

    # TRAINEE -> TRADER
    if lvl == "TRAINEE":
        p = t["paper"]
        th = THRESHOLDS["TRAINEE_TO_TRADER"]
        if (p["months_tracked"] >= th["months_min"]
                and abs(p["current_dd"]) <= th["max_dd_max"]):
            return "PROMOTE"
        if p["current_dd"] <= -0.20:
            return "FIRE"
        return "HOLD"

    # TRADER -> SENIOR
    if lvl == "TRADER":
        l = t["live"]
        th = THRESHOLDS["TRADER_TO_SENIOR"]
        if l["months_tracked"] >= th["months_min"] and l["sharpe"] >= th["sharpe_min"]:
            return "PROMOTE"
        if l["monthly_returns"] and l["monthly_returns"][-1] < -0.08:
            return "FIRE"
        return "HOLD"

    # SENIOR -> PRINCIPAL (promotion.md v2 frozen criteria; branch installed
    # 2026-09-25, closing the O-20260924-1727 engineering todo). No SENIOR
    # auto-fire: FIRED at this tier is risk-department audit territory only.
    # .get() with fail-safe defaults -- live settlement fields may not exist
    # yet on legacy files; missing evidence must HOLD (same philosophy as the
    # G2.5 gate) and must never crash run_review for the other traders.
    if lvl == "SENIOR":
        l = t["live"]
        th = THRESHOLDS["SENIOR_TO_PRINCIPAL"]
        dd = l.get("current_dd")
        if (l.get("months_tracked", 0) >= th["months_min"]
                and l.get("sharpe", 0.0) >= th["sharpe_min"]
                and dd is not None and abs(dd) <= th["max_dd_max"]):
            return "PROMOTE"
        return "HOLD"

    return "HOLD"


def next_level(level: str) -> str:
    return {
        "INTERN": "TRAINEE",
        "TRAINEE": "TRADER",
        "TRADER": "SENIOR",
        "SENIOR": "PRINCIPAL",
    }.get(level, level)


def run_review():
    traders = list_traders()
    # T-24 hard assertion: PROSPECT is observation-only, allocation PERMANENTLY
    # 0 (spec verbatim). Violation = abort before any level/allocation write.
    assert ALLOCATION.get("PROSPECT") == 0, \
        "hr invariant: PROSPECT allocation must be permanently 0"
    for t in traders:
        if t["level"] == "PROSPECT":
            assert t["live"]["allocation_pct"] == 0, \
                f"hr invariant: PROSPECT {t['id']} carries nonzero allocation"
    print(f"=== Bigmoney HR Review · {date.today()} ===")
    print(f"total traders: {len(traders)}\n")
    summary = {}
    for t in traders:
        action = evaluate(t)
        if action == "PROMOTE":
            new_lvl = next_level(t["level"])
            t["status_history"].append({
                "date": str(date.today()), "from": t["level"],
                "to": new_lvl, "note": "auto-promote"
            })
            t["level"] = new_lvl
            t["live"]["allocation_pct"] = ALLOCATION[new_lvl]
            save_trader(t)
        elif action == "FIRE":
            t["status_history"].append({
                "date": str(date.today()), "from": t["level"],
                "to": "FIRED", "note": "auto-fire"
            })
            t["level"] = "FIRED"
            t["live"]["allocation_pct"] = 0
            save_trader(t)
        summary[t["id"]] = (t["level"], action)

    # print table
    print(f"{'ID':<12} {'level':<10} {'action':<8}")
    print("-" * 35)
    for tid, (lvl, act) in summary.items():
        print(f"{tid:<12} {lvl:<10} {act:<8}")

    # allocation summary
    total = sum(ALLOCATION[t["level"]] for t in traders if t["level"] != "FIRED")
    print(f"\nactive allocation: {total}% (cap 100%)")


if __name__ == "__main__":
    run_review()
