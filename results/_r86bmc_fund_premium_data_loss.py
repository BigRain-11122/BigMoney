# -*- coding: utf-8 -*-
"""r86 bm-c: fund_premium machine-local data-face loss incident probe.

Diagnosis: bm-c tree rebuilt 2026-09-27 into unified root (old tree
K:\\金钱牛马 retired+deleted per U196/U238). gitignored machine-local
data/fund_premium/ (NAV history x48 + dividends + panel 76,025 rows,
retained asset per T-16 r53) did NOT survive: not in git, not migrated.
Status mirror (results/fund_premium_status.json) nav block still says
done 48/48 (stale checkpoint record) while live disk facts show 0 files
=> status-vs-disk divergence on the lane owner's own machine.

Recovery (this round): backfill-nav detached PID captured, per-symbol
checkpoint resume-safe (r52 precedent). Follow-ups: backfill-dividends,
panel rebuild (build_premium_panel.py pure-local), gate re-check.
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def dir_facts(path):
    if not os.path.isdir(path):
        return {"exists": False}
    files = []
    for base, _dirs, names in os.walk(path):
        files.extend(names)
    return {"exists": True, "file_count": len(files)}


def main():
    status_path = os.path.join(ROOT, "results", "fund_premium_status.json")
    with open(status_path, encoding="utf-8") as f:
        status = json.load(f)

    # gitignored machine-local faces vs present dirs
    faces = ["heat", "ext_slots", "moneyflow", "sina_mf", "astock_daily",
             "fund_premium", "ths_ggzjl", "ah_panel", "bond_w3a"]
    inventory = {k: dir_facts(os.path.join(ROOT, "data", k))["exists"]
                 for k in faces}
    data_dirs = sorted(os.listdir(os.path.join(ROOT, "data")))

    old_root = r"K:\金钱牛马"
    old_tree = os.path.join(old_root, "BigMoney", "data", "fund_premium")

    out = {
        "probe": "_r86bmc_fund_premium_data_loss",
        "round": "r86",
        "machine": "bm-c",
        "lane": "fund_premium (T-16, lane_owner=bm-c)",
        "incident": {
            "type": "machine-local data-face loss on root migration",
            "cause": "bm-c rebuilt 2026-09-27 into unified root; old tree "
                     "K:\\金钱牛马 deleted; gitignored data/fund_premium/ "
                     "not migrated, not in git",
            "lost_assets": [
                "nav history 48/48 full-history (e.g. 159901 4991 rows "
                "2006-03-24..2026-09-23, r52 evidence)",
                "dividends 48/48 (r53, incl. 17 zero-div findings)",
                "panel 76,025 rows x 48 members 2020-01-02..2026-09-23 "
                "(r53, retained asset for P-A2/P-B1)",
                "snapshots bulk face (recreated automatically by S6 "
                "snapshot leg on next weekday)",
            ],
            "status_mirror_divergence": {
                "nav_block_claims": "done 48/48 coverage 1.0 (stale "
                                   "checkpoint record, written in old tree)",
                "disk_facts_live": "nav_files=0 snapshots=0",
                "verdict": "mirror stale vs disk; gate subcommand reads "
                           "disk -> honest fail-closed, no silent "
                           "corruption risk",
            },
        },
        "evidence": {
            "old_root_gone": not os.path.isdir(old_root),
            "old_tree_gone": not os.path.isdir(old_tree),
            "data_dir_inventory": data_dirs,
            "machine_local_face_presence": inventory,
            "fund_premium_face": dir_facts(os.path.join(ROOT, "data",
                                                        "fund_premium")),
            "status_ts": status.get("ts"),
            "status_mode": status.get("mode"),
        },
        "recovery": {
            "action": "backfill-nav detached (r52 precedent), "
                      "checkpoint per-symbol resume-safe, 2.5s throttle, "
                      "5-conn fuse",
            "started": "2026-09-27T14:54:08+08:00",
            "pid": 12828,
            "log": "results/_r86bmc_backfill_nav.log",
            "eta_min": 25,
            "follow_ups": [
                "harvest backfill-nav (48/48 target, fuse check)",
                "backfill-dividends leg (48 symbols, sina face)",
                "panel rebuild via scripts/build_premium_panel.py "
                "(pure-local, zero network, selftest 26/26)",
                "gate re-check: NAV coverage >=95% restored",
                "status mirror nav block re-derived from disk after "
                "recovery",
            ],
        },
        "ledger_trials_added": 0,
        "evidence_cutoff": "2026-09-24",
    }
    out_path = os.path.join(ROOT, "results",
                            "_r86bmc_fund_premium_data_loss.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("wrote", out_path)
    print("old_root_gone:", out["evidence"]["old_root_gone"],
          "| faces present:", [k for k, v in inventory.items() if v])


if __name__ == "__main__":
    main()
