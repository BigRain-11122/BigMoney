# -*- coding: utf-8 -*-
# r434 bm-b: W9-SCREEN burn-landing round dual-face flip (pit-89 law: flip in the
# round where the burn lands; dual-face law: entry+shard same commit) + T-121
# progress_r434 note. Screen-finalize + judge-prep + JUDGE entry submitted same round.
import json, io

POOL = r"results/runnable_pool.json"
TICKET = r"fleet/tasks/T-2026-09-29-121-P1.json"

pool = json.load(io.open(POOL, encoding="utf-8"))
flip = None
for e in pool.get("entries", []):
    if e.get("id") == "TRIAL-LABOR-W9-SCREEN":
        assert e.get("status") == "ready", "unexpected screen entry status: %s" % e.get("status")
        e["status"] = "done"
        e["done_at"] = "2026-09-29T17:10:14+08:00"
        e["result_ref"] = (
            "results/trial_labor_w9/w9_screen.json (2,715/2,715 cells ckpt complete "
            "17:10:07 runner pid4592 manual-tick ignition 17:02:42 r398 lineage after "
            "r351 origin-moved double-defer 16:50/17:00; finalize landed 17:10:14: "
            "distinct 2515 + nulls 200, null p95_line 0.517199 IN prereg sec.5.2 "
            "recalibrated band [0.50,0.52], survivors 243/2515 = 9.66%; AMP segmented "
            "survival = amp_narrow 59/823 7.17% < amp_wide 79/739 10.69% < none "
            "105/953 11.02% = W9 research fact: amplitude-confirmation gate shows "
            "ANTI-enrichment at screen face (gate-restricted cells survive WORSE than "
            "no-gate cells, opposite of W8 TSTATE deep_pullback 1.80x enrichment); "
            "seven-gate interaction face computed; ledger 341,073+2,715=343,788 "
            "reconcile OK; judge-prep PASS same round (manifest 48, census L/D == "
            "frozen, gate meta 801wide/811narrow amp anchors); TRIAL-LABOR-W9-JUDGE "
            "pool entry submitted same round (host_gates MSG-1305 wiring, "
            "lane_owner=bm-b dual-face)")
        for s in e.get("shards", []):
            if s.get("key") == "screen-0of1":
                s["status"] = "done"
                s["owner"] = "bm-b"
                s["owner_since"] = "2026-09-29 17:02:42"
                s["done_at"] = "2026-09-29 17:10:07"
                s["result_ref"] = (
                    "results/trial_labor_w9/checkpoint/screen_shard_0of1.jsonl "
                    "(2,715/2,715 rows complete, cross-kill resume law)")
        flip = e["id"]
assert flip, "W9-SCREEN entry not found"
with io.open(POOL, "w", encoding="utf-8", newline="") as f:
    json.dump(pool, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("pool flip:", flip, "-> done (entry+shard dual-face)")

t = json.load(io.open(TICKET, encoding="utf-8"))
t["progress_r434_bmb"] = (
    "r434 bm-b: SCREEN slice burned+finalized same round -- manual-tick ignition "
    "17:02:42 pid4592 (r398 manual-ignition lineage; r351 origin-moved defer healed "
    "by session pull, 16:50/17:00 double-defer disclosed) -> ckpt 2,715/2,715 "
    "complete 17:10:07 -> screen-finalize LANDED 17:10:14: distinct 2515 + nulls "
    "200, null p95_line 0.517199 IN recalibrated band [0.50,0.52] (sec.5.2 "
    "continuation), survivors 243/2515 = 9.66%; RESEARCH FACT: AMP segmented "
    "survival amp_narrow 7.17% < amp_wide 10.69% < none 11.02% = amplitude-"
    "confirmation gate ANTI-enrichment at screen face (negative-axis finding, "
    "opposite of W8 TSTATE deep_pullback 1.80x); ledger 341,073+2,715=343,788 "
    "reconcile OK; judge-prep PASS (manifest 48 members, census L/D == frozen, "
    "vol 594calm/518wild, yang 819/812, vconf 784surge/828dry, streak "
    "384up/389down/856neither, tstate 188true/1453decidable + 332true/1572decidable, "
    "amp 801wide/811narrow decidable 1612); TRIAL-LABOR-W9-JUDGE pool entry "
    "submitted same round (results/_r434bmb_w9_judge_submit.py, host_gates "
    "dir_nonempty Money02 deep-panel ohlcv 48 parquet verified non-empty, RAM "
    "r354 three-sample 12.7/12.9/12.9 GB, lane_owner=bm-b); JUDGE burn = autofill "
    "face next tick; judge-finalize = separate round work per frozen law (48h CEO "
    "report clock starts at judge-finalize)")
t["progress_r434_ts"] = "2026-09-29T17:12:00+08:00"
with io.open(TICKET, "w", encoding="utf-8", newline="") as f:
    json.dump(t, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("ticket progress_r434 written")
