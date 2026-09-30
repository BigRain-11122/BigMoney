"""D-20260930-41 deliverable #4 -- account cost-turnover-tax integration.

ORDER = docs/audits/ORDER-retail-quant-research-track-20260930.md sec.2 item 4
("本账户成本-换手-税收一体化核算"). L1 deterministic, zero network, zero
engine, zero new trials: every number derives from the FROZEN in-repo cost
calibers (knowledge/cost_spec.py Face A + knowledge/rules.py CN-C1 routed
FeeSchedule) and the local five-member daily panel (ADV20).

Usage (module mode, cwd = repo root):
    python -m scripts.account_cost_tax run        # write results/account_cost_tax.json
    python -m scripts.account_cost_tax selftest   # hermetic golden assertions
Direct run also works (repo-root sys.path fix mirrors cost_spec).
"""
import json
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# GBK console reconfigure entry law (r236 family): this script prints CNY
# signs and the PS 5.1 console defaults to GBK.
if hasattr(sys.stdout, "encoding") and sys.stdout.encoding \
        and sys.stdout.encoding.lower().replace("-", "") not in ("utf8", "utf8mb4"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from knowledge import cost_spec, rules  # noqa: E402

FIVE_MEMBERS = ["510300", "510050", "510500", "512100", "588000"]
STOCK_REF_CODE = "600519"          # sh main board (routed stock caliber)
PANEL_DIR = os.path.join(_REPO_ROOT, "data", "daily")
OUT_PATH = os.path.join(_REPO_ROOT, "results", "account_cost_tax.json")

# turnover budgets (round-trips per year) for the drag table
TURNOVER_RTS_PER_YEAR = [1, 2, 4, 12, 26, 52]
# ticket sizes (yuan) for the min-commission escalation table
TICKETS = [5000, 10000, 20000, 50000, 135000, 1000000]
BP = 1e4


def _panel_rows(code):
    path = os.path.join(PANEL_DIR, f"sh{code}.csv")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        for line in f:
            parts = line.strip().split(",")
            rows.append(dict(zip(header, parts)))
    return rows


def _adv20_yuan(rows):
    amounts = [float(r["amount"]) for r in rows[-20:] if r.get("amount")]
    if len(amounts) < 20:
        return None
    return sum(amounts) / len(amounts)


def _panel_span(rows):
    return rows[0]["date"], rows[-1]["date"], len(rows)


def _side_cost_bp(fee, ticket_yuan=None):
    """Flat-v1-basis per-side cost in bp, honoring the CN-C3 min commission
    (¥5 floor) when a ticket size is given."""
    commission_bp = fee.commission_rate * BP
    if ticket_yuan is not None and ticket_yuan > 0:
        commission_bp = max(commission_bp, fee.commission_min / ticket_yuan * BP)
    fixed_bp = (fee.handling_fee + fee.supervision_fee
                + fee.transfer_fee + fee.slippage_a) * BP
    return commission_bp + fixed_bp


def _sell_side_cost_bp(fee, ticket_yuan=None):
    return _side_cost_bp(fee, ticket_yuan) + fee.stamp_tax * BP


def compute():
    etf_fee = rules.FeeSchedule()                      # default ETF caliber (frozen)
    stock_fee = rules.fee_schedule_for(STOCK_REF_CODE)  # CN-C1 routed stock caliber

    members = {}
    evidence_cutoff = None
    for code in FIVE_MEMBERS:
        rows = _panel_rows(code)
        first, last, n = _panel_span(rows)
        adv20 = _adv20_yuan(rows)
        slip_bp = rules.cost_v2_slippage(adv20) * BP
        v2_side_bp = cost_spec.x1_side_rate(etf_fee) * BP - etf_fee.slippage_a * BP + slip_bp
        v2_sell_bp = v2_side_bp + etf_fee.stamp_tax * BP
        members[code] = {
            "panel_first": first, "panel_last": last, "panel_rows": n,
            "adv20_yuan": adv20, "v2_slippage_bp": slip_bp,
            "v2_side_buy_bp": round(v2_side_bp, 4),
            "v2_side_sell_bp": round(v2_sell_bp, 4),
            "v2_round_trip_bp": round(v2_side_bp + v2_sell_bp, 4),
            "t_plus": "T+0" if rules.is_t0(code) else "T+1",
        }
        if evidence_cutoff is None or last > evidence_cutoff:
            evidence_cutoff = last

    # Face A flat basis (frozen): ETF symmetric, stock routed asymmetric
    etf_x1_buy_bp = cost_spec.x1_side_rate(etf_fee) * BP
    etf_x1_sell_bp = cost_spec.x1_sell_side_rate(etf_fee) * BP
    stock_buy_bp = _side_cost_bp(stock_fee)
    stock_sell_bp = _sell_side_cost_bp(stock_fee)

    # CN-C3 min-commission escalation (flat v1 basis, ETF + stock columns)
    min_comm = []
    for t in TICKETS:
        min_comm.append({
            "ticket_yuan": t,
            "etf_side_buy_bp": round(_side_cost_bp(etf_fee, t), 4),
            "etf_round_trip_bp": round(
                _side_cost_bp(etf_fee, t) + _sell_side_cost_bp(etf_fee, t), 4),
            "stock_side_buy_bp": round(_side_cost_bp(stock_fee, t), 4),
            "stock_round_trip_bp": round(
                _side_cost_bp(stock_fee, t) + _sell_side_cost_bp(stock_fee, t), 4),
        })

    # turnover-budget drag: annual friction the strategy must clear vs the
    # same-exposure buy-and-hold passive leg (net-alpha ceiling = drag)
    v2_avg_rt_bp = sum(m["v2_round_trip_bp"] for m in members.values()) / len(members)
    drag = []
    for rts in TURNOVER_RTS_PER_YEAR:
        drag.append({
            "round_trips_per_year": rts,
            "annual_drag_bp_face_a_flat": round((etf_x1_buy_bp + etf_x1_sell_bp) * rts, 2),
            "annual_drag_bp_v2_member_avg": round(v2_avg_rt_bp * rts, 2),
            "stock_annual_drag_bp": round((stock_buy_bp + stock_sell_bp) * rts, 2),
        })

    return {
        "schema": "account_cost_tax_v1",
        "order_ref": "D-20260930-41 deliverable #4",
        "caliber_sources": {
            "face_a": "knowledge/cost_spec.py X1_RATE (frozen, ETF default)",
            "routing": "knowledge/rules.py fee_schedule_for (CN-C1, r479)",
            "v2_basis": "knowledge/rules.py cost_v2_slippage ADV20 tiers (frozen)",
            "grid_legacy": "cost_spec.GRID_LEGACY_COST_BP_X1 = 13.0bp (frozen historical)",
        },
        "evidence_cutoff": evidence_cutoff,
        "etf_face_a_flat": {
            "side_buy_bp": round(etf_x1_buy_bp, 4),
            "side_sell_bp": round(etf_x1_sell_bp, 4),
            "round_trip_bp": round(etf_x1_buy_bp + etf_x1_sell_bp, 4),
            "x2_stress_round_trip_bp": round((etf_x1_buy_bp + etf_x1_sell_bp) * 2, 4),
        },
        "stock_cn_c1_routed": {
            "ref_code": STOCK_REF_CODE,
            "side_buy_bp": round(stock_buy_bp, 4),
            "side_sell_bp": round(stock_sell_bp, 4),
            "round_trip_bp": round(stock_buy_bp + stock_sell_bp, 4),
            "note": "stamp 5bp sell-only + transfer 0.1bp both sides; "
                    "stock conclusions inadmissible until engine fee_by_symbol wiring lands (r479 boundary)",
        },
        "five_members_v2_adv20": members,
        "v2_member_avg_round_trip_bp": round(v2_avg_rt_bp, 4),
        "min_commission_escalation": min_comm,
        "min_commission_critical_ticket_yuan": round(
            stock_fee.commission_min / etf_fee.commission_rate, 2),
        "turnover_drag": drag,
        "t0_etf_codes": sorted(rules.T0_ETF_CODES),
        "tax_face": {
            "capital_gains_individual": "A-share trading capital gains for individual investors: income-tax exempt (institutional-fact citation, ORDER sec.1.1 discipline; not self-run)",
            "stock_dividend_tax": "differentiated by holding period: >1y exempt / 1m-1y 10% / <1m 20% (institutional-fact citation)",
            "etf": "no stamp tax (CN-C1); distributions rare for the five-member universe",
            "caveat": "tax policy is a cited institutional fact, not backtested; policy change risk disclosed",
        },
        "search_accounting": {
            "new_trials": 0,
            "dsr": "N/A (L1 derivation, no backtest cells)",
            "pbo": "N/A (L1 derivation, no backtest cells)",
            "full_start_distribution": "N/A (no strategy conclusion claimed; robustness belongs to deliverable #1)",
        },
    }


def cmd_run():
    data = compute()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    rt = data["etf_face_a_flat"]["round_trip_bp"]
    print(f"account_cost_tax: written {os.path.relpath(OUT_PATH, _REPO_ROOT)}")
    print(f"  ETF Face A RT = {rt} bp | stock RT = "
          f"{data['stock_cn_c1_routed']['round_trip_bp']} bp "
          f"(buy {data['stock_cn_c1_routed']['side_buy_bp']} / "
          f"sell {data['stock_cn_c1_routed']['side_sell_bp']})")
    print(f"  v2 ADV20 member-avg RT = {data['v2_member_avg_round_trip_bp']} bp "
          f"| min-comm critical ticket = "
          f"¥{data['min_commission_critical_ticket_yuan']}")
    print(f"  evidence_cutoff = {data['evidence_cutoff']} | new_trials = 0")
    return 0


def cmd_selftest():
    fails = []

    def check(name, cond):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    check("cost_spec.verify() frozen face intact", cost_spec.verify())
    d = compute()
    # frozen golden numbers (r479 + cost_spec records)
    check("ETF Face A per-side 13.041bp",
          abs(d["etf_face_a_flat"]["side_buy_bp"] - 13.041) < 1e-6)
    check("ETF Face A round-trip 26.082bp",
          abs(d["etf_face_a_flat"]["round_trip_bp"] - 26.082) < 1e-6)
    check("stock buy side 13.141bp (CN-C1/2/3)",
          abs(d["stock_cn_c1_routed"]["side_buy_bp"] - 13.141) < 1e-6)
    check("stock sell side 18.141bp (stamp sell-only)",
          abs(d["stock_cn_c1_routed"]["side_sell_bp"] - 18.141) < 1e-6)
    check("stock round-trip 31.282bp",
          abs(d["stock_cn_c1_routed"]["round_trip_bp"] - 31.282) < 1e-6)
    check("ETF sell == buy (stamp 0, bit-for-bit asymmetry face)",
          d["etf_face_a_flat"]["side_sell_bp"] == d["etf_face_a_flat"]["side_buy_bp"])
    # CN-C3 min commission: ¥5 floor bites below ¥20k, exact at ¥20k
    crit = d["min_commission_critical_ticket_yuan"]
    check("min-commission critical ticket = ¥20,000", abs(crit - 20000.0) < 1e-6)
    row5k = next(r for r in d["min_commission_escalation"] if r["ticket_yuan"] == 5000)
    check("¥5,000 ticket ETF side 20.541bp (comm floor 10bp)",
          abs(row5k["etf_side_buy_bp"] - 20.541) < 1e-6)
    row20k = next(r for r in d["min_commission_escalation"] if r["ticket_yuan"] == 20000)
    check("¥20,000 ticket at critical (13.041bp unchanged)",
          abs(row20k["etf_side_buy_bp"] - 13.041) < 1e-6)
    # v2 tier routing sanity: big-ADV member sits at the 2bp tier
    big = d["five_members_v2_adv20"]["510300"]
    check("510300 ADV20 >= ¥5e8 -> 2bp tier",
          big["adv20_yuan"] >= rules.ADV20_TIER_2BP_YUAN
          and abs(big["v2_slippage_bp"] - 2.0) < 1e-9)
    # five members all T+1 (frozen universe, honest face)
    check("five members all T+1",
          all(m["t_plus"] == "T+1" for m in d["five_members_v2_adv20"].values()))
    # search accounting: zero new trials
    check("new_trials = 0 (L1 only)", d["search_accounting"]["new_trials"] == 0)
    # determinism: double compute byte-identical
    d2 = compute()
    check("double-run byte-identical",
          json.dumps(d, sort_keys=True) == json.dumps(d2, sort_keys=True))
    # evidence_cutoff from the real panel tail
    check("evidence_cutoff present", bool(d["evidence_cutoff"]))

    print(f"selftest: {'ALL PASS' if not fails else 'FAIL ' + str(fails)}")
    return 0 if not fails else 1


def main(argv):
    if len(argv) < 2 or argv[1] not in ("run", "selftest"):
        print(__doc__)
        return 2
    return cmd_run() if argv[1] == "run" else cmd_selftest()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
