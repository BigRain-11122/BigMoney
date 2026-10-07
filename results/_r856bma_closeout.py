"""r856 bm-a closeout: state + round report + heartbeat writer.
Multi-writer files -> python single-file fresh read-modify-write (2026-10-06 law)."""
import json
import time
import datetime as dt

NOW = dt.datetime.now()
ISO = NOW.isoformat(timespec="seconds")          # local +08:00
EPOCH = int(time.time())
R = "r856"

# ---------------- state-bm-a.json ----------------
p = "state-bm-a.json"
s = json.load(open(p, encoding="utf-8"))
s.update({
    "round": 856, "round_no": 856, "loop_round": R, "last_round": R,
    "current_task": f"{R} closed: zt_pool 4-face collector gate landed + EM depth probes; next=S5-01 adaptation replay prereg (pilot face pinned)",
    "did": (f"{R}: S0 E42 writer-pause rebase (single UU orphan-probe face, ts-newer "
            f"take-local; git-pull --rebase 'Cannot rebase onto multiple branches' "
            f"oddity x2 -> direct fetch+rebase cure, report-noted) + zt_pool gate "
            f"LANDED scripts/update_zt_pool.py (4 EM faces zt/zbgc/dtgc/strong; "
            f"calendar-transitive 15:30 gate = bar-unlanded-no-pull pure form; "
            f"forward-accrual FIRST_DATE 2026-10-08; per-day checkpoint ledger "
            f"collected_days.json; overlap row-level NaN-aware; conn-fuse 3; "
            f"30min throttle r18; r806 timeout jacket; lane bm-a R31; R58 shell "
            f"defense) + selftest 18/18 + live no-op rc0 + lane mirror ok + "
            f"smoke 49/49 (+1 updater row) + S6 39 legs rc0 (dualrun streak 51 "
            f"zero-drift; watermark py_low_board_clear; compute_audit "
            f"pool_starvation+supply_floor flags -> standing-line response = "
            f"next-round prereg draft per state pointer) + live shape probe "
            f"4/4 (zt52/zbgc12/dtgc9/strong199 @09-30) + EM depth bisect x4: "
            f"pool history ~2-3 weeks only (09-07=0/09-14=55/09-21=103/09-30=52 "
            f"-> forward-accrual design validated, deep-history replay "
            f"impossible; prereg pilot face pinned) + spec research/shortline/"
            f"ZT_POOL.md + S6 chain registration (iteration_prompt slot after "
            f"update_lhb + smoke row + lane_io face) + attrition CLEAN + orders "
            f"52/52 + DEC/ORD hash identical zero-action + orphan face=1 "
            f"(BigDomain cross-company, read-only)"),
    "last_action": f"{R} zt_pool collector gate landed (O-20261001-2103 R2 data face, S5-01 GO follow-through)",
    "now_active": f"{R} closed (zt_pool gate + depth probes); r857 = S5-01 adaptation replay prereg (pilot face) + 10-08 15:30 reopen re-arm",
    "next": (f"r857: S5-01 adaptation replay prereg draft (bigmoney-prereg-draft "
             f"skill; pilot face pinned by r856 depth probes: EM zt-pool "
             f"as-collected history ~2-3 weeks only (evidence "
             f"results/_r856bma_zt_depth_*.json) -> replay = mechanics-"
             f"verification pilot vs archived reference "
             f"scripts/_r855_vibe_emotion_metrics_ref.py on shallow window + "
             f"forward panel accrual; predictive-value face deferred per T-67 "
             f"§2 freeze (OPTIONS_WAVE2 pilot/definitive precedent); exit-axis "
             f"3-choice explicit + D6 corr gate + big-sample 3-iron + random "
             f"baseline) -> then cycle_position 3-axis into REGIME-5 supply "
             f"(needs ~10td forward history, usable ~10-22) + 10-08 15:30 "
             f"market-reopen data chain re-arm (all gates + REGIME_GUARD v3 "
             f"enforce; zt_pool first real collection lands tonight after "
             f"update_daily drops the 10-08 bar) + W181 seat watch"),
    "verify": ("smoke 49/49; zt_pool selftest 18/18 + live rc0; probe 4/4 "
               "endpoints live; depth bisect 4 rounds; S6 39 legs rc0; "
               "dualrun streak 51; attrition CLEAN; orders 52/52; "
               "DEC/ORD identical; not-at-origin=0 post-push (to verify)"),
    "last_seen": ISO, "last_round_at": ISO, "last_round_ts": ISO,
    "last_run": ISO, "updated": ISO, "ts": ISO, "clock_read": ISO,
    "heartbeat_epoch_utc": EPOCH,
    "last_heartbeat_epoch_utc": s.get("heartbeat_epoch_utc", EPOCH),
    "latest_artifact": ("scripts/update_zt_pool.py + research/shortline/"
                        f"ZT_POOL.md + results/_r856bma_zt_pool_probe.json "
                        f"@{ISO}"),
    "last_artifact": ("scripts/update_zt_pool.py + research/shortline/"
                      f"ZT_POOL.md + results/_r856bma_zt_pool_probe.json "
                      f"@{ISO}"),
})
json.dump(s, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------------- round_reports-bm-a.md (UTF-8 append + CRLF tail probe, r843 law) ----
rp = "round_reports-bm-a.md"
with open(rp, "ab") as f:
    f.write((
        f"\n{ISO} | {R} | bm-a | dept:数据/工程 | S0 E42 writer-pause rebase "
        f"(single UU ts-newer take-local; git-pull --rebase 'multiple branches' "
        f"oddity x2 -> direct fetch+rebase cure, recurs=pit) | zt_pool 4-face "
        f"collector gate LANDED (scripts/update_zt_pool.py: zt/zbgc/dtgc/strong, "
        f"calendar-transitive 15:30 gate, forward-accrual FIRST_DATE 2026-10-08, "
        f"per-day ledger checkpoint, overlap row-level, conn-fuse 3, lane bm-a; "
        f"spec research/shortline/ZT_POOL.md; S6 chain slot after update_lhb + "
        f"smoke 49/49 +1 row + lane_io face registered) | live shape probe 4/4 "
        f"(09-30: zt52/zbgc12/dtgc9/strong199, evidence _r856bma_zt_pool_probe."
        f"json) | EM depth bisect x4: pool history ~2-3 weeks (09-07=0/09-14=55/"
        f"09-21=103/09-30=52) -> deep replay impossible, forward-accrual "
        f"validated, prereg pilot face pinned | S6 39 legs rc0 (dualrun streak "
        f"51; watermark py_low_board_clear; compute_audit pool_starvation+"
        f"supply_floor -> standing-line response next round) | verify: selftest "
        f"18/18 + smoke 49/49 + live no-op rc0 + attrition CLEAN + orders 52/52 "
        f"+ DEC/ORD identical + orphan face=1 (BigDomain cross-company read-only)"
        f" | next: r857 S5-01 adaptation replay prereg (pilot face, "
        f"bigmoney-prereg-draft skill) + 10-08 15:30 reopen re-arm + W181 seat "
        f"watch | 本地未达 origin commit 数=0 (post-push verify)\n"
    ).encode("utf-8"))

# ---------------- heartbeat fleet/machines/bm-a.json ----------------
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8-sig"))
h.update({
    "machine_id": "bm-a",
    "round_no": 856, "round": 856, "loop_round": R,
    "last_seen": ISO, "last_run": ISO, "ts": ISO, "clock_read": ISO,
    "heartbeat_epoch_utc": EPOCH,
    "last_heartbeat_epoch_utc": h.get("heartbeat_epoch_utc", EPOCH),
    "idle_rounds": 0, "agenda_starved": False,
    "current": "zt_pool collector gate landed (O-20261001-2103 R2 data face)",
    "current_task": ("r856 closed: zt_pool 4-face gate + EM depth probes; "
                     "next=r857 S5-01 replay prereg + 15:30 reopen re-arm"),
    "last_action": f"{R} zt_pool gate landed + smoke 49/49 + S6 39 legs rc0",
    "last_artifact": (f"scripts/update_zt_pool.py + research/shortline/"
                      f"ZT_POOL.md + results/_r856bma_zt_pool_probe.json @{ISO}"),
    "latest_artifact": h.get("last_artifact"),
    "next_milestone": ("S5-01 adaptation replay prereg frozen (r857, ≤48h) -> "
                       "cycle_position REGIME-5 supply ~10-22 (needs ~10td "
                       "forward zt history); tonight 15:30: first real zt_pool "
                       "collection on 10-08 reopen bar"),
    "now_active": f"{R} closed; r857 prereg draft next",
    "task": "zt_pool gate landed; prereg next",
    "health": "ok",
})
try:
    import psutil
    vm = psutil.virtual_memory()
    h["ram_free_gb"] = round(vm.available / 1024**3, 1)
    h["ram_free_pct"] = round(vm.available / vm.total * 100, 1)
    h["cpu_load_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
except Exception:
    pass
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# self-verify epoch int type (R170/R178 law)
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
s2 = json.load(open(p, encoding="utf-8"))
assert isinstance(s2["heartbeat_epoch_utc"], int), "state epoch must be int"
print("closeout writes done; epoch int verified", EPOCH)
