#!/usr/bin/env python
# -*- coding: ascii -*-
# r836 bm-b closeout: state + heartbeat + round report, load-modify-write (r818 law).
import json, time, datetime
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# --- state.json (bm-b face) ---
sp = ROOT + r"\state.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 836
st["round"] = 836
st["round_no_label"] = "r836"
st["last_round_at"] = now
st["ts"] = now
st["updated"] = now
st["updated_at"] = now
st["last_seen"] = now
st["clock_read"] = now
st["now_active"] = "r836 closeout: M-1 regime axis freeze + two CEO orders consumed + S6 full chain"
st["did"] = "r836: O-20261010-1645 continuity ack (backtest non-stop standing law) + O-20261010-1725 M-1 schedule row 10-11 delivered 1 day early: regime axis freeze (REGIME_AXIS_M1_FREEZE.md + scripts/regime_axis_m1.py selftest 7 legs + results/regime_axis_m1/panic_windows.json 25 days/12 windows, P>=1000 x20 + icepoint x5) + ticket T-182 claimed+done same round + S6 full 37-leg chain + D19 orders consumed+advanced"
st["verdict"] = "r836: GREEN-ish; compute_audit FLAG supply_gap+ignition_sla (TRIAL-LABOR-W17-JUDGE bm-c lane, standing observation per O-1645 enforcement face); alloc_paper rc=2 = known P5 stale-leg 510880 (s3 review 2026-10); smoke 49/49"
st["latest_artifact"] = "r836: research/REGIME_AXIS_M1_FREEZE.md + results/regime_axis_m1/panic_windows.json (25 panic days/12 windows, selftest 7/7), 2026-10-10 17:3x"
st["next_milestone"] = "r837+: C-03 bm-b baseline wiring receipt (due <=10-11 14:30) + M-1 P0 slicing claim (10-13/14) -> matrix v1 plain report 10-16 (O-1725 schedule)"
q = ("r837 queue: (1) C-20261009-03 bm-b workspace baseline wiring receipt (<=24h from r835); "
     "(2) M-1 P0 slicing face -- research-dept claim per O-1725 schedule 10-13/14 (slicing uses frozen axis: "
     "REGIME5 labels + panic_windows.json; candidate slices: 4-asset core book / lowvol family / 6 employees / "
     "SYSTEM-V1 / oversold trio / theme rider); (3) O-1645 enforcement: F1-BULL-COND prereg same-window draft "
     "(T-177 leg-2 rank-1) if W17 verdict lands -> W18 prereg same window (泊位开放条款); (4) r834 root-cause "
     "forensics continued (USN journal window dump + zombie git 24568) -- standing until closed")
st["current_task"] = q
st["task"] = q
st["next"] = q
st["last_action"] = "r836: M-1 regime axis freeze v1.0 (O-1725 schedule item 10-11, 1 day early) + two-order consumption"
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-b.json (script load-modify-field, r818 law) ---
hp = ROOT + r"\fleet\machines\bm-b.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["round"] = 836
hb["round_no"] = 836
hb["now_active"] = "r836 closeout: M-1 regime axis freeze + O-1645/O-1725 consumed + S6 full chain"
hb["current_task"] = q
hb["task"] = q
hb["next"] = q
hb["last_round_at"] = now
hb["last_seen"] = now
hb["updated"] = now
hb["updated_at"] = now
hb["ts"] = now
hb["clock_read"] = now
hb["heartbeat_epoch_utc"] = epoch
hb["latest_artifact"] = st["latest_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["verdict"] = st["verdict"]
hb["last_action"] = st["last_action"]
ack = hb.get("orders_ack", [])
for o in ("O-20261010-1645-bm-a.md", "O-20261010-1725-bm-a.md"):
    if o not in ack:
        ack.append(o)
hb["orders_ack"] = ack
hb["orders_ack_count"] = len(ack)
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 0
hb["orphan_face_note"] = "r836 orphan probe py_faces=17 orphans=0"
hb["sync"] = {"ahead": 0, "behind": 0, "last_push_ts": now,
              "note": "r836 closeout push; post-push fetch+ls-remote self-proof in S7 shell step"}
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"

# --- round report line (bm-b uses logs/iteration-loop/round_reports.md) ---
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
line = (
    "%s | r836 | bm-b: S0-1 anchored bm-b (orphan probe py_faces=17 orphans=0); pull converged at 17:06 merge (dead-r836 S0 residue reused, zero re-do); "
    "S0.5 double-order consumption: O-20261010-1645 回测不停机令 ack (continuity evidence = satengine alive rc0, W17 7/8 shards bm-c lane in-flight per order live-facts, perpetual N1 W202 continuous; enforcement = supply/queue legs below + F1-BULL-COND prereg queued r837) + "
    "O-20261010-1725 M-1 排程令 SAME-ROUND delivery of schedule row 10-11 (1 day early): **政体轴冻结 v1.0** = REGIME5 v1.0 labels pointer + panic-window operational freeze "
    "(P: n_sealed_down>=1000 x20 + I icepoint: n_sealed<=30 & down>=800 x5 = 25 days/12 event windows, matches order '~25 窗' exactly; anchors 5/5 machine-verified; idempotent rerun byte-identical; "
    "selftest 7 legs PASS) -> research/REGIME_AXIS_M1_FREEZE.md + scripts/regime_axis_m1.py + results/regime_axis_m1/panic_windows.json; ticket T-182 opened+claimed+done same round (anti-dup: board scan pre-claim max=T-181, zero M-1 claim on origin); "
    "S1 smoke 49/49; S6 full 37-leg chain rc0 except alloc_paper rc=2 known P5 stale-leg 510880 (s3 review face, honest disclosure): dualrun ZERO-DRIFT streak 20; compute_audit FLAG supply_gap+ignition_sla (W17-JUDGE, bm-c lane obs per O-1645); "
    "py_watermark insufficient_history (legit Saturday); market_clock ORANGE_COOL 0 activated; options lane RETIRED honest no-op (O-202609-1105); scorecard/report/live_usage/build faces rebuilt; "
    "D19: decisions zero-delta, orders consumed (2 new CEO orders) + watermark advanced via guard tool; satengine alive (heartbeat 10s, queue 0 local); idle verdict not-GREEN-IDLE (VRAM 3.4<6GB) "
    "| evidence: results/regime_axis_m1/panic_windows.json + research/REGIME_AXIS_M1_FREEZE.md + fleet/tasks/T-2026-10-10-182-P1.json + smoke Summary 49/49 + results/compute_audit.bm-b.json + results/pool_dualrun.bm-b.jsonl "
    "| score: 2 (frozen axis = runnable product: derive script + verifiable JSON + selftest) | 下轮指针: r837 = C-03 baseline receipt + P0 slicing claim + O-1645 supply legs (F1-BULL-COND prereg same-window if W17 lands) | orphan-face=0 | 本地未达 origin commit 数=0 (post-push fetch proof below)\n"
) % now
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("closeout written: state r836, heartbeat r836 ack+2 (%d total), round report line, epoch=%d int-verified" % (len(ack), epoch))
