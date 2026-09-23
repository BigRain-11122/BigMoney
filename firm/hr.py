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

# promotion thresholds
# INTERN->TRAINEE requires paper tracking: backtest evidence alone must never
# promote (PLAN.md 0.6 no-live-before-paper; prevents wall-of-fame fake promotes)
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
    "INTERN": 0, "TRAINEE": 0, "TRADER": 5,
    "SENIOR": 15, "PRINCIPAL": 30, "FIRED": 0,
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


def evaluate(t: dict) -> str:
    """Return action: PROMOTE / FIRE / HOLD."""
    lvl = t["level"]
    if lvl == "FIRED":
        return "HOLD"

    # INTERN -> TRAINEE
    if lvl == "INTERN":
        os_ = t["backtest"]["out_sample"]
        th = THRESHOLDS["INTERN_TO_TRAINEE"]
        if (t["paper"]["months_tracked"] >= th["paper_months_min"]
                and os_["sharpe"] >= th["os_sharpe_min"]
                and os_["trades"] >= th["trades_min"]
                and os_["max_dd"] <= th["max_dd_max"]):
            return "PROMOTE"
        # fail after 3 months
        return "HOLD"

    # TRAINEE -> TRADER
    if lvl == "TRAINEE":
        p = t["paper"]
        th = THRESHOLDS["TRAINEE_TO_TRADER"]
        if (p["months_tracked"] >= th["months_min"]
                and p["current_dd"] <= th["max_dd_max"]):
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
