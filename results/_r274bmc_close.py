# r274 bm-c S7 close: state round bump + heartbeat update (in-process, no window)
import json, time, datetime

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# 1) state-bm-c.json: round_no 274 -> 275
sp = "state-bm-c.json"
s = json.load(open(sp, encoding="utf-8"))
assert s["round_no"] == 274 and s["last_round_at"] == 273, f"unexpected state: {s['round_no']}/{s['last_round_at']}"
s["last_round_at"] = 274
s["round_no"] = 275
s["last_round_ts"] = "2026-09-30T14:04:08+08:00" if False else s.get("last_round_ts")
s["updated"] = now_iso
s["cpu_pct"] = 33.0
s["idle_ram_gb"] = 8.4
s["gpu_free_vram_mib"] = 9505
s["verify"] = ("S1 smoke 33/33; S6 33 legs rc0 except lhb rc3 source-revision OVERLAP MISMATCH (old42/new67 netbuy sign-flip, "
               "local zero-write, bm-a lane obs #11, reported unmasked); dualrun ZERO-DRIFT 139 streak 51/3; audit flags "
               "pool_starvation/supply_floor=RW-5 freeze honest; watermark py_low_board_clear; daily 0-new cutoff 09-29 "
               "pre-15:30 legal no-op; stale-takeover derives (scorecard/dailysc/paper-family/t35export/buildstat) all "
               "guard-internal legal per O-2100 s2.4 C_HOST_STALE_MIN=20min (bm-a hb 26-27min); attrition CLEAN 4 ledgers; "
               "orders 127/127 double-scan zero unacked; pin :X5 no-op + watchdog Ready + claw MATCH; RW-5 compliance "
               "zero new prereg/slot/supply/burn")
s["did"] = ("r274: RW-5 freeze-window wait-state maintenance round (board 0 open + pool 0 + supply lines frozen "
            "D-20260930-05, no re-scan of frozen waiting objects): (a) S6 chain full run, CEO faces regenerated incl. "
            "stale-takeover derives during bm-a round gap; (b) lhb rc3 obs #11 reported; (c) STALE_MIN law constant "
            "verified 20min (r273 '>30min' wording corrected, MSG-1042 canon face); (d) 15:30 post-close round will "
            "catch 09-30 bar (holiday-eve last session)")
s["current_task"] = ["r274 closed: freeze-window maintenance; r275 = 10-01 month-first trio (science_audit+monthly_briefing+self_review) + REGIME_GUARD v3 date-gate auto-activation + RW unfreeze watch (RW-4 slice-2 in flight bm-a)"]
s["next"] = ("(a) 10-01 month-first trio + REGIME_GUARD v3 auto-activation hands-off. (b) RW-1~4 unfreeze watch "
             "(RW-1/2/3 landed origin, RW-4 slice-2 bm-a in flight, T-127 verify 10-03) -> reeval burn = sole remaining "
             "canon TODO. (c) 15:30 post-close round = 09-30 bar landing (bm-b etf_daily lane + own fund_prem snapshot "
             "window). (d) 48h CEO clocks 10-02: SLOT-7/8/9/10 + W12 judge 05:22 + W13 CEO-REPORT 12:28 (watch only). "
             "(e) lhb rc3 adjudication = bm-a lane (obs #11 in book). (f) product score honest = 1 (face-refresh "
             "maintenance only, no new product in freeze window).")
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 2) heartbeat fleet/machines/bm-c.json
hp = "fleet/machines/bm-c.json"
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = now_iso.replace("T", " ")[:19]
h["heartbeat_epoch_utc"] = epoch  # int type (R170/R178 law)
h["clock_read"] = now_iso
h["cpu_cores"] = 32
h["idle_ram_gb"] = 8.4
h["gpu_free_vram_mib"] = 9505
h["verdict"] = ("r274 RW-5 freeze-window maintenance round all-green: smoke 33/33; S6 33 legs rc0 except lhb rc3 "
                "(source-revision, bm-a lane obs #11, unmasked); stale-takeover derives of CEO faces legal "
                "(C_HOST_STALE_MIN=20min, bm-a hb 26-27min); RW-5 compliance zero new prereg/slot/supply/burn; "
                "next: 10-01 month-first trio + 15:30 post-close 09-30 bar")
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 3) self-verify: reload and assert types/values
sv = json.load(open(hp, encoding="utf-8"))
assert isinstance(sv["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in sv["clock_read"] and " " not in sv["clock_read"], "clock_read must be T-separated"
st = json.load(open(sp, encoding="utf-8"))
assert st["round_no"] == 275 and st["last_round_at"] == 274
print(f"state 274->275 OK; heartbeat epoch int={sv['heartbeat_epoch_utc']} clock={sv['clock_read']}")
