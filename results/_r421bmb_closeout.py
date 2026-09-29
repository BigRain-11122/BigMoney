# -*- coding: utf-8 -*-
"""r421 bm-b closeout writer: state.json + heartbeat + round report line."""
import json
import time

now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
now_s = time.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())
assert isinstance(epoch, int)

# ---------------- state.json (bm-b lane file, round 421)
state = {
    "machine_id": "bm-b",
    "round_no": 421,
    "note": (
        "r421: S0 merge-back pit-93 single-merge LANDED 03c5fd5e0 (21 UU "
        "resolved: 19 take-:3 deep-ts all-fresher bm-c side + "
        "compute_audit history union 201+201->203 zero-loss + "
        "regime_state identity; _r421_resolve.py; escape branch "
        "machine/bm-b-r420 superseded). MSG-1030 honored: pit-95 "
        "finalize-idempotent guard wired into w7 cmd_screen_finalize/"
        "cmd_judge_finalize PRE-first-landing (live-fire refusal rc=2 "
        "verified post-landing; selftest 40->42 L19a/b state-adaptive "
        "guard legs; reply MSG-1110 sent, original archived). "
        "W7-SCREEN harvest: burn 3904/3904 (pid19452 by ~10:53; 11:00 "
        "tick relaunch pid10532 full-checkpoint no-op honest) -> "
        "screen-finalize LANDED 10:59:31: survivors 284/3704=7.67%, "
        "null p95 0.5180 (W1-W6 band in-band), streak segmented "
        "9.34%/7.95%/6.00%, ledger 333432+3904=337336 linear -> "
        "pool dual-face done-flip (坑律一百零一批 entry+shard, "
        "three-way verified) + W7-JUDGE entry direct-ready (serial "
        "clear, judge-prep PASS, RAM 12.10/12.33/12.52) same commit "
        "3fc2533e2 pushed. S6 37 legs rc=0 x36 + minute_feed rc=3 "
        "source-rewrite honest repeat (510300 @09:41 3rd occurrence, "
        "observation window rolls). next: W7-JUDGE burn ignition "
        "(autofill 11:10 tick) -> judge-finalize next round + intake "
        "slice after; W1-W5 pit-95 wiring mechanical follow-up open "
        "face"
    ),
    "last_round_at": now_iso,
    "last_round_ts": now_iso,
    "ts": now_s,
}
with open("state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)
print("state.json written round", state["round_no"])

# ---------------- heartbeat fleet/machines/bm-b.json
hb_path = "fleet/machines/bm-b.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = time.strftime("%Y-%m-%d %H:%M")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["current_task"] = (
    "W7-JUDGE pool entry ready (autofill ignition 11:10 tick) + "
    "round 421 closeout"
)
hb["cpu_cores"] = 16
hb["free_ram_gb"] = 10.0
hb["gpu_free_vram_gb"] = 2.66
hb["total_ram_gb"] = 23.92
hb["cpu_util_pct"] = 25.0
hb["round_no"] = 420
hb["loop_round"] = 421
hb["verdict"] = (
    "W7-SCREEN chain advanced full stage: harvest+guard+JUDGE-entry "
    "landed pushed 3fc2533e2; merge-back clean; chain healthy"
)
hb["round"] = 421
hb["gpu_free_vram_mb"] = 2729
with open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
# self-verify (R170/R178 law: value AND type must both be int)
chk = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written epoch(int)=", chk["heartbeat_epoch_utc"],
      "clock=", chk["clock_read"])

# ---------------- round report line (bm-b lane file)
line = (
    f"{now_iso} | r421 | dept:策略+研究 joint (T-118 W7 chain + "
    f"pit-95 wiring) | WM-VERDICT: py_low_board_clear @11:03 "
    f"(open 0/bandit 0/local_batch false; pool ready1=W7-JUDGE "
    f"supply-point ignition 11:10 lawful face) | did: (1) S0-1 bm-b "
    f"anchor; S0 merge-back pit-93 single-merge: pit-99 "
    f"targeted-commit-first (checkpoint FULL 3904/3904 + autofill "
    f"snapshot b56cd928c) -> merge origin/main (bm-c r210/r211): 21 "
    f"UU resolved per bigmoney-conflict-resolve canon (classifier 9 "
    f"+ 12 UNKNOWN hand-classified same-day regen twins) = 19 "
    f"take-:3 whole bytes (deep-ts probe :3 fresher on every face "
    f"zero ties, twins/pointers same side, js-wrapper whole bytes "
    f"R209) + compute_audit history union 201+201->203 zero-loss "
    f"(199 common +2 bm-b +2 bm-c, latest take-:3 @10:48:27) + "
    f"regime_state identity assertion whole-doc :3 == union; "
    f"merge commit 03c5fd5e0 PUSHED (escape branch machine/"
    f"bm-b-r420 superseded); (2) S0.5 orders 122/122 zero-diff ack "
    f"+ group decisions.md path absent zero-action + inbox MSG-1030 "
    f"read->executed->receipt MSG-1110->archived; (3) S1 smoke "
    f"26/26; (4) S3 W7 chain full-stage advance: MSG-1030 wiring "
    f"honored PRE-first-landing (tl6.finalize_already_landed 4-line "
    f"guard x cmd_screen_finalize/cmd_judge_finalize; live-fire: "
    f"first-run fresh-pass landed, re-run FINALIZE-IDEMPOTENT-GUARD "
    f"rc=2 refusal zero double-append; selftest 40->42/42 L19a/b "
    f"state-adaptive legs) + screen-finalize LANDED 10:59:31 "
    f"(3904/3904 cells, null p95 0.5180 W1-W6 band in-band, "
    f"survivors 284/3704=7.67%, streak segmented down/none/up = "
    f"9.34%/7.95%/6.00% = behavioral-confirmation cost face honest, "
    f"trials_ledger 333432+3904=337336 cross-wave linear verified) "
    f"+ pool TRIAL-LABOR-W7-SCREEN dual-face done-flip (坑律一百零"
    f"一批 entry+shard closed_at 11:01:40, three-way verified: "
    f"product 3704+200/284/0.5180/337336 == entry literal == "
    f"prereg sec.0; burn 10:40:01 pid19452 complete by ~10:53 + "
    f"11:00:01 tick relaunch pid10532 full-checkpoint no-op honest "
    f"re-ready-window cost) + TRIAL-LABOR-W7-JUDGE entry "
    f"direct-ready same commit 3fc2533e2 PUSHED (entry-time deps "
    f"all MET: serial-position zero in-flight judge faces, "
    f"judge-prep PASS manifest 48/census frozen/survivors 284/"
    f"five-gate meta anchors, RAM r354 12.10/12.33/12.52 GB); (5) "
    f"S6 37 legs: dualrun ZERO-DRIFT 113 entries streak 5/3 -> "
    f"audit FLAG supply_gap+ignition_sla(TRIAL-LABOR-W7-JUDGE "
    f"ready post-tick)+supply_floor wave-mid honest (supply_family "
    f"streak 1101.8min) -> WM py_low_board_clear -> daily "
    f"no-op<15:30 cutoff 09-28 -> regime ORANGE d2 shadow (hs300<"
    f"MA200 #10 + breadth 0.83) -> scorecard stale-takeover 2S/4A "
    f"best VOLATILITY-CE-01 87.0 -> clock ORANGE_COOL sleeves4 "
    f"act0 -> lhb no-op fresh -> collectors 10x lane-guard no-ops "
    f"+ futures/astock/etf no-op fresh + rev_osc idempotent -> "
    f"minute_feed rc=3 510300 @09:41 source-rewrite honest repeat "
    f"3rd occurrence (observation window rolls, local untouched) "
    f"-> fundamental fresh skip + b_layer all_pass -> live.paper "
    f"6 anchors OK + t35 fill PASS zero-pending-6 + t24 paper "
    f"22/22 drift0 + promotion 0/22 lawful NOT-ELIGIBLE + "
    f"aggr/alloc/grid idempotent + system_v1 lane no-op -> "
    f"paper_export equity 5,988,732 + daily_scorecard + "
    f"daily_report REPORT-0929 faces5 + ceo_live LIVE-0929 ORANGE "
    f"cap50 COOL -> build_status stale-takeover (bm-a hb stale "
    f"46min lawful O-2100 s2.4) + token delta=0; (6) S7 trio green "
    f"(Loop running pin=2 verified schtasks R49 law + Watchdog "
    f"re-registered -Force idempotent + claw in-sync) + state 421 "
    f"+ heartbeat epoch int + inbox 0 unread | evidence: origin "
    f"push receipts 03c5fd5e0 + 3fc2533e2; _r421_resolve.py + "
    f"_r421bmb_w7_flip_entry.py receipts in-repo; selftest 42/42 "
    f"rc=0; py_compile rc=0; guard refusal stdout verbatim; pool "
    f"re-read verify 113 entries | next: (a) W7-JUDGE burn ignition "
    f"autofill 11:10 tick (est ~6min 284 cells W6 293=5.6min "
    f"precedent) -> judge-finalize + intake slices next rounds (48h "
    f"CEO clock starts at judge-finalize); (b) W1-W5 pit-95 "
    f"same-type wiring = open mechanical follow-up slice any "
    f"healthy machine; (c) minute_feed 09:41 window roll watch | "
    f"marks/ledger/SEED +0 beyond frozen prereg faces (ledger "
    f"337336 = prereg sec.0 declared batch append) [r421 bm-b]\n"
)
with open("logs/iteration-loop/round_reports.md", "a",
          encoding="utf-8") as f:
    f.write(line)
print("round report line appended", now_iso)
