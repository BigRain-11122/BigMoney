# r465 bm-b S5/S7 closing writer: state increment + round report line + heartbeat (epoch int self-verified)
import json, time, io, datetime

ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# 1) state.json round_no 464 -> 465
sp = "state.json"
st = json.load(io.open(sp, encoding="utf-8"))
assert st["round_no"] == 464, st["round_no"]
st["round_no"] = 465
io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1))

# 2) round report line (bm-b uses logs/iteration-loop/round_reports.md)
line = (
    "2026-09-30T14:0x+08:00 | r465 bm-b | WATERMARK: green (14:03 probe rc0 py_low_board_clear lawful: board 0 open + pool 139/139 done + bandit 0 open [moneyflow IC claimed-parked EM source, bm-a lane] + RW-5 freeze in effect = lawful idle freeze face) | "
    "CURRENT-ACTIVE: r465 5x HANDOVER inventory window round -- S0 stash-pull-pop FF zero-conflict (round-start-dirty=autofill_state.bm-b.json self-owned lane runtime) + S6 38-leg chain full-run via _r460bmb_s6_chain driver reuse + HANDOVER r465 5x row landed (increment window r461-465, ledger head 362,083 live-read verified, pool 139/139 done) | "
    "LAST-ARTIFACTS: research/HANDOVER.md r465 5x row @14:0x + results/paper/marks/marks-20260930.jsonl tick 18 positions @14:03 (5.74s) + docs/daily_report/REPORT-2026-09-30.md regenerated (faces=5) + docs/live_usage/LIVE-2026-09-30.md (ORANGE cap50 COOL) regenerated | "
    "NEXT-MILESTONE: >=15:35 round = post-close unlock legs (09-30 bars -> live.paper/t35/prospect accrue); RW-1~4 unfreeze <=48h (bm-a T-127, 2026-10-02) then W14 prereg window opens -- within 48h; 2026-10-01 first round fires month-first trio (science_audit/monthly_briefing/self_review) + REGIME_GUARD v3 date-gate auto-activates hands-off | "
    "EVIDENCE: smoke 31/31 + S6 38-leg all rc0 NON-GREEN=NONE (dualrun ZERO-DRIFT streak 51/3 @139 BEFORE compute_audit order held + regime ORANGE breadth 0.83>=65% + lhb rc0 30min-guard no-op + minute_feed throttle 19min<20min honest no-op + foreign-lane honest no-ops + fundamental 2.5h fresh-skip + C-family lane_io guard skips @ bm-a hb 12min fresh + attrition CLEAN 4 ledgers (2 healed) + loop pin=2 no-op first fire 14:12 + watchdog ready 14:10 + claw LF-normalized installed + orders 127/127 zero-diff both-scans + decisions.md tail 09-26 zero-new + inbox 1 unread MSG-1352 bma->bmc non-bm-b addressee left for recipient zero bm-b action + heartbeat epoch int self-verified) | "
    "NEXT-POINTER: r466 = in-session freeze watch; >=15:35 round = post-close unlock legs (09-30 bars); 2026-10-01 first round fires month-first trio (science_audit/monthly_briefing/self_review) + REGIME_GUARD v3 date-gate auto-activates hands-off; next 5x = bm-b r470 [via bm-b]\n"
)
with io.open(r"logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write(line)

# 3) heartbeat fleet/machines/bm-b.json
hp = "fleet/machines/bm-b.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = ts
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = ts
h["current_task"] = "r465 5x HANDOVER inventory round: S6 38-leg rc0, HANDOVER r465 row, freeze watch"
h["cpu_util_pct"] = 2.8
h["free_ram_gb"] = 8.3
h["idle_ram_gb"] = 8.3
h["ram_free_gb"] = 8.3
h["gpu_free_vram_gb"] = 6.7
h["gpu_free_vram_mb"] = 6876
h["gpu_idle_vram_gb"] = 6.7
h["round_no"] = 465
h["round"] = 465
h["loop_round"] = 465
h["last_round_at"] = ts
h["verdict"] = ("idle_watch: RW-5 freeze lawful-idle face (pool 139/139 done, board 0 open); "
                "5x HANDOVER r465 row landed; next unlock = 15:30 post-close bars")
h["n_orders_ack"] = len(h["orders_ack"])
io.open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(h, ensure_ascii=False, indent=1))

# self-verify: epoch int + clock_read T-separator + reload parses
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), type(chk["heartbeat_epoch_utc"])
assert "T" in chk["clock_read"], chk["clock_read"]
print("r465 closing writer OK: state=465, report line appended, heartbeat epoch int", chk["heartbeat_epoch_utc"], chk["clock_read"])
