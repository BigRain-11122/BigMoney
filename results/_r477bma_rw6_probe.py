"""RW-6 leg-A probe (r477 bm-a, ticket T-127, decision D-20260930-05 item 6).

One-time recompute of the 6 registered members on the FULLY-FIXED engine
(RW-1 T+1-open exits + RW-2 cutoff hard-truncation + RW-3 single-source
cost spec + RW-4 panel gate), with the FINAL old-vs-new table:
per member, per segment (IS/OOS), four metrics (sharpe/annual/trades/dd).

Three-way consistency law (r253 single-count / r459 replay-drift guard):
  fresh recompute  ==  r472 refrozen trader-JSON fields  ==  r472 probe 'new'
Any drift = red, fail-closed. Old face = pre-fix frozen values preserved
verbatim in results/_r472bma_rw1_probe.json (honest overstatement baseline).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

METRICS = ("sharpe", "annual", "trades", "dd")


def seg_row(got_seg: dict) -> dict:
    return {"sharpe": got_seg["sharpe"], "annual": got_seg["annual_return"],
            "trades": got_seg["trades"], "dd": got_seg["max_drawdown"]}


def main() -> int:
    from live import paper as live_paper
    from firm.hr import list_traders, load_trader

    r472 = json.loads(
        (ROOT / "results" / "_r472bma_rw1_probe.json").read_text(encoding="utf-8"))
    r472_members = r472["leg2"]["members"]

    prices_full = live_paper.load_core()
    reg_ids = [t["id"] for t in list_traders()
               if t.get("level") in live_paper.PAPER_LEVELS]
    assert len(reg_ids) == 6, f"expected 6 registered, got {len(reg_ids)}: {reg_ids}"

    table, drift = {}, []
    for tid in reg_ids:
        t = load_trader(tid)
        a = live_paper.anchor_gate(t, prices_full)
        got = a.get("got")
        if got is None:
            table[tid] = {"ok": False, "error": a.get("error")}
            drift.append(f"{tid}: anchor_gate error {a.get('error')}")
            continue
        fresh = {seg: seg_row(got[seg]) for seg in ("in_sample", "out_sample")}
        frozen = {seg: dict(t["backtest"][seg]) for seg in ("in_sample", "out_sample")}
        old_r472 = r472_members[tid]["old"]
        new_r472 = r472_members[tid]["new"]
        # three-way byte-stability (numeric compare at frozen 4dp schema)
        checks = {}
        for seg in ("in_sample", "out_sample"):
            for k, fk in (("sharpe", "sharpe"), ("annual", "annual"),
                          ("trades", "trades"), ("dd", "max_dd")):
                v_fresh = fresh[seg][k]
                v_r472 = new_r472[seg][fk if fk in new_r472[seg] else k]
                v_frozen = frozen[seg][fk if fk in frozen[seg] else k]
                ok = (abs(float(v_fresh) - float(v_r472)) < 5e-5 and
                      abs(float(v_fresh) - float(v_frozen)) < 5e-5)
                checks[f"{seg}.{k}"] = bool(ok)
                if not ok:
                    drift.append(f"{tid}.{seg}.{k}: fresh={v_fresh} "
                                 f"r472={v_r472} frozen={v_frozen}")
        table[tid] = {
            "ok": all(checks.values()),
            "old": old_r472, "new": fresh, "checks": checks,
        }

    out = {
        "batch": "RW6-member-final-recompute",
        "evidence_cutoff": "2026-09-22",
        "engine_fixes": {
            "rw1_tplus1_open_exits": True,   # engine/backtester pending_exits
            "rw2_cutoff_hard_truncation": True,
            "rw3_single_source_cost": True,
            "rw4_panel_gate": True,
        },
        "n_members": len(reg_ids), "members": table,
        "drift": drift,
        "verdict": "BYTE-STABLE" if not drift else "DRIFT",
    }
    art = ROOT / "results" / "_r477bma_rw6_probe.json"
    art.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[RW-6 leg-A] verdict={out['verdict']} members={len(reg_ids)} "
          f"drift={len(drift)} -> {art.name}")
    if drift:
        for d in drift:
            print("  DRIFT:", d)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
