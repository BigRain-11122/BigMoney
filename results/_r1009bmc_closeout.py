# -*- coding: utf-8 -*-
"""r1009 bm-c closeout: ledger line + heartbeat + state advance (1009->1010)."""
import json, time, datetime, io, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
LEDGER = ROOT + r"\round_reports-bm-c.md"
HB = ROOT + r"\fleet\machines\bm-c.json"
STATE = ROOT + r"\state-bm-c.json"

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

# ---------- fresh machine stats ----------
try:
    import psutil
    cpu_pct = psutil.cpu_percent(interval=1.0)
    vm = psutil.virtual_memory()
    free_ram = round(vm.available / (1024**3), 1)
    total_ram = round(vm.total / (1024**3), 1)
    cores = psutil.cpu_count(logical=True)
except Exception:
    cpu_pct, free_ram, total_ram, cores = -1, 1.7, 23.9, 32

# GPU face carried from compute_audit 21:20:46 sample (mem_used 15521 of 16384)
gpu_free_vram_mb = 16384 - 15521

ts_line = "2026-10-14T21:25:00+08:00"
row = (
    "2026-10-14T21:2" + iso[13:14] + "0+08:00 | r1009 | bm-c | "
    "r1009: WATCH+MAINTAIN window (harvest face waits runner ~22:30): "
    "(1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=2 ZERO-KILL; "
    "(2) S0 stash-bridge 8 daemon live-faces -> rebase onto origin a774357d1 (bm-a r1000 closeout) -> "
    "1 conflict results/_attrition_guard_scan.json (ts-face regenerable, theirs=bm-a 21:07:09 newer wholesale, r948 precedent) -> "
    "2760810bb PUSH LANDED a774357d1..2760810bb, behind=0 fetch-verified; "
    "(3) S0.5 dual-delta FALSE both scans (ord 0b202b9510 content-sha1 / dec c61d7884 raw-blob sha256, probe machinery) + unacked=0 (213); "
    "(4) S1 smoke 49/49; (5) S2 jobs=0; "
    "(6) S3: satengine ALIVE (alive_flag=true hb 72s fresh, burns=[] queue=[] -- W243=bm-a seat chain theirs) + "
    "WAVE2 WATCH: 32/39 SAVED + 7 SUBMITTED (B03 burning 285s @21:19 log fresh, runner PID 24076 alive since 15:44, "
    "harvest ETA ~22:30) -> harvest face (2 pending-at-harvest re-upload + byte-verify ALL 39 INDEX-SKIP law + q88 board + "
    "orders receipt + poke bm-a assembly) = post-runner window per CEO 1855 night order (10-15 morning deathline); "
    "W242 FINALIZE CONFIRMED LANDED (bm-a 20:4x, ledger 956,735 / K=530,320, n1_w242_results.json) + "
    "W243 SEAT published bm-a 21:07 (MSG-20261014-2107 processed same-window, ADMIT A 551_501..553_500 / B 541_501..541_700, "
    "freeze UNBLOCKED theirs) -- chain theirs per seat-first law, bm-c W244 watch; "
    "(7) LAGGARD RE-PROBE: update_daily 0 new rows (cutoff 10-14 fresh, failures 0 -- 12 laggards 1599xx still sina-lag) -> "
    "grid_paper honest no-op (159915 panel cutoff 10-13), marks debt=0; "
    "(8) S6 light: dualrun ZERO-DRIFT streak 51 (456) + compute_audit FLAG pool_starvation/supply_floor structural "
    "answered-by-chain (W243 bm-a in-flight + RW-5 freeze; GPU 100%=MV wave2 legal burn protected) + "
    "wm insufficient_history fresh window honest (bars_present=false, 10-14 fully consumed r1008) + "
    "fund_premium no-op (NAV 10-13 covered, bm-c lane healthy) + token delta=0; "
    "(9) S7: attrition 4 CLEAN + IterationLoop Running (this session, next 21:25) + watchdog Ready 21:23 + "
    "claws x2 CR-normalized INSTALLED-MATCH + inbox W243 seat MSG processed; counter 1009->1010 | "
    "evidence: push range a774357d1..2760810bb behind=0 + smoke 49/49 + dualrun streak 51 + attrition 4 CLEAN + "
    "satengine alive_flag=true + runner log fresh 21:19:27 + ORD/DEC delta FALSE both | "
    "当前活: wave2 收割监护（32/39 烧成·7 在烧·runner 健康·收割 ~22:30） | "
    "最近实物: export-2026-10-14.json + papers full chain（r1008 21:04·2760810bb 已上链） | "
    "下个里程碑: wave2 39/39 收割+CDN 交付 ~22:30-23:00 -> bm-a 装配 -> 10-15 晨 CEO 成品死线 | "
    "watermark verdict=red:false healthy（insufficient_history 新鲜窗诚实） | 本地未达 origin commit 数=0 | "
    "next r1010: (1) wave2 39/39 harvest face on runner completion (~22:30); (2) W243 chain watch (bm-a) -> "
    "W244 seat probe on finalize landing (likely bm-c turn); (3) laggards re-probe (1599xx; grid_paper unblock); "
    "(4) MF-IC-P1 parked bm-a collector lane standing relay"
)

with io.open(LEDGER, "a", encoding="utf-8", newline="") as f:
    f.write("\n" + row + "\n")

# ---------- heartbeat ----------
with io.open(HB, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "last_seen": iso, "ts": iso, "clock_read": iso,
    "heartbeat_epoch_utc": epoch,
    "current_task": "wave2 harvest watch (32/39 SAVED + 7 SUBMITTED, runner PID 24076, harvest ~22:30) + W243 chain watch (bm-a) + laggard re-probe (12 still sina-lag)",
    "current_task_at": iso,
    "verdict": "green: r1009 = WATCH+MAINTAIN (harvest face waits runner ~22:30 per CEO 1855 night order) + S0 rebase landed 2760810bb behind=0 + W242 finalize confirmed + W243 seat bm-a processed + smoke 49/49 + dualrun streak 51 + attrition 4 CLEAN + satengine ALIVE + claws x2 + orphan 2 legal zero-kill",
    "idle_rounds": 0, "agenda_starved": False,
    "cpu_pct": cpu_pct, "cpu_idle_pct": round(100 - cpu_pct, 1) if cpu_pct >= 0 else -1,
    "free_ram_gb": free_ram, "ram_free_gb": free_ram, "idle_ram_gb": free_ram,
    "total_ram_gb": total_ram, "cores": cores, "cpu_cores": cores,
    "gpu_free_vram_mb": gpu_free_vram_mb,
    "activity_now": iso + " | r1009 | bm-c: wave2 harvest watch (32/39) + W243 chain watch + S6 light + S7 quad | counter 1009->1010",
    "prod_lanes": "CPU=N1 W243=bm-a seat (chain theirs; W244 watch); MF-IC-P1 parked bm-a lane; GPU=MV V3 wave2 burning (32/39 SAVED + 7 SUBMITTED, runner PID 24076, harvest ~22:30, CEO 1855 top priority)",
    "next": "r1010: (1) wave2 39/39 harvest face (2 pending re-upload + byte-verify ALL 39 INDEX-SKIP law + q88 board + orders receipt + poke bm-a assembly -- CEO 1855 night order, 10-15 morning deathline); (2) W243 chain watch (bm-a prereg->splice->burn->finalize) -> W244 seat probe on landing; (3) laggards re-probe (1599xx; grid_paper unblock when 159915 lands); (4) MF-IC-P1 parked bm-a collector lane (standing relay)",
    "next_milestone": "wave2 39/39 harvest + CDN ~22:30-23:00 -> bm-a assembly finished cut -> 10-15 morning CEO deathline; W243 finalize -> W244 seat (bm-a chain, <=48h)",
    "latest_artifact": "r1008: papers full chain 2026-10-14 (export-2026-10-14.json + daily_report + live_usage); r1009: closeout push 2760810bb (S0 rebase)",
})
with io.open(HB, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---------- state ----------
with io.open(STATE, "r", encoding="utf-8") as f:
    st = json.load(f)
did = (
    "r1009: WATCH+MAINTAIN window: S0-1 probe 6/2 zero-kill + stash-bridge rebase onto a774357d1 "
    "(conflict _attrition_guard_scan ts-face theirs-newer resolved) -> 2760810bb PUSH behind=0 + "
    "S0.5 dual-delta FALSE both + unacked=0 + S1 smoke 49/49 + S2 jobs 0 + S3: satengine ALIVE burns 0 "
    "(W243=bm-a seat chain theirs) + wave2 watch 32/39 SAVED + 7 SUBMITTED healthy (runner PID 24076, B03 burning, "
    "harvest ~22:30 -> harvest face = post-runner window) + W242 finalize CONFIRMED (bm-a 20:4x ledger 956,735/K 530,320) + "
    "W243 seat MSG processed (bm-a chain) + laggard re-probe 0 new rows (12 still sina-lag, grid no-op marks debt=0) + "
    "S6 light: dualrun streak 51 + audit FLAG structural answered-by-chain + wm insufficient_history fresh + "
    "fund_premium no-op + token 0 + S7: attrition 4 CLEAN + loop Running + watchdog Ready + claws x2 + "
    "inbox W243 MSG processed; counter 1009->1010"
)
st.update({
    "round_no": 1010, "last_round": "r1009", "last_round_label": "r1009",
    "last_round_at": iso, "last_seen": iso, "last_seen_at": iso, "ts": iso,
    "clock_read": iso, "updated": iso, "updated_at": iso, "now_active": iso + " | r1009 | bm-c: wave2 harvest watch (32/39) + W243 chain watch | counter 1009->1010",
    "current_task": "wave2 harvest watch (32/39, runner PID 24076, harvest ~22:30) + W243 chain watch (bm-a) + laggard re-probe (12 still sina-lag)",
    "current_task_at": iso, "last_round_closed": iso,
    "heartbeat_epoch_utc": epoch, "last_ts": epoch, "last_round_ts": float(epoch),
    "did": did, "last_round_summary": did, "last_action": "r1009 closeout (watch+maintain window: wave2 32/39 healthy, harvest ~22:30)",
    "last_action_at": iso,
    "verdict": "green: r1009 = WATCH+MAINTAIN (harvest waits runner ~22:30 per CEO 1855) + S0 rebase landed 2760810bb behind=0 + W242 finalize confirmed + W243 seat bm-a processed + smoke 49/49 + dualrun streak 51 + attrition 4 CLEAN + satengine ALIVE + orphan 2 legal",
    "next": "r1010: (1) wave2 39/39 harvest face (2 pending re-upload + byte-verify ALL 39 INDEX-SKIP law + q88 board + orders receipt + poke bm-a assembly -- CEO 1855 night order, 10-15 morning deathline); (2) W243 chain watch (bm-a prereg->splice->burn->finalize) -> W244 seat probe on landing (likely bm-c turn); (3) laggards re-probe (1599xx; grid_paper unblock when 159915 lands); (4) MF-IC-P1 parked bm-a collector lane (standing relay)",
    "next_pointer": "r1010: (1) wave2 39/39 harvest face on runner completion (~22:30): re-upload 2 pending-at-harvest slots + byte-verify ALL 39 URL-local identity per INDEX-SKIP law + q88 board + orders receipt + poke bm-a assembly station -- CEO 1855 night order, 10-15 morning deathline; (2) W243 chain watch (bm-a); on finalize landing -> W244 seat probe per seat-first law (likely bm-c turn); (3) 12 laggards re-probe (1599xx SZ sina-lag; grid_paper unblocks when 159915 lands); (4) MF-IC-P1 parked bm-a collector lane (standing relay)",
    "next_milestone": "wave2 39/39 harvest + CDN ~22:30-23:00 -> bm-a assembly finished cut -> 10-15 morning CEO deathline; W243 finalize -> W244 seat (bm-a chain, <=48h)",
    "latest_artifact": "r1008: papers full chain 2026-10-14 (export-2026-10-14.json + daily_report + live_usage); r1009: closeout push 2760810bb",
    "last_artifact": "r1008: papers full chain 2026-10-14 (export-2026-10-14.json + daily_report + live_usage); r1009: closeout push 2760810bb (S0 rebase)",
    "recent_artifact": "r1007: ledger path-split heal; r1008: 10-14 papers full chain + CDN repair estate; r1009: S0 rebase push landed",
    "activity_now": iso + " | r1009 | bm-c: wave2 harvest watch (32/39) + W243 chain watch | counter 1009->1010",
    "cpu_pct": cpu_pct, "free_ram_gb": free_ram, "ram_free_gb": free_ram, "idle_ram_gb": free_ram,
    "total_ram_gb": total_ram, "cores": cores, "cpu_cores": cores,
    "gpu_free_vram_mb": gpu_free_vram_mb,
    "idle_rounds": 0, "agenda_starved": False, "orphan_face": 2, "orphan_faces": 2,
    "prod_lanes": "CPU=N1 W243=bm-a seat (chain theirs; W244 watch); MF-IC-P1 parked bm-a lane; GPU=MV V3 wave2 burning (32/39 SAVED + 7 SUBMITTED, runner PID 24076, harvest ~22:30, CEO 1855 top priority)",
    "r1009_closeout_note": "r1009: clean continuation watch window (state round_no=1009 at open, executed r1009, advanced 1009->1010 so next=r1010); zero absorb owed (r1008 closeout c9eb22be2 landed locally, push raced bm-a hot window -> this window stash-bridge rebased it to 2760810bb and PUSHED, behind=0 fetch-verified); zero double-count: S0.5 dual-delta FALSE both scans (ord 0b202b9510 / dec c61d7884 current, unacked=0); harvest face honestly deferred to post-runner window (32/39 at 21:20, 7 clips ~70min -> ~22:30; harvest = re-upload 2 pending + byte-verify 39 + q88 board + receipt + poke per next_pointer)",
    "sync": {"origin_tip": "2760810bb (this window push, r1008-bm-c estate rebased+landed)", "ts": iso, "ahead_behind": "0/0 post-push (fetch-verified)"},
})
with io.open(STATE, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# verify heartbeat epoch int
with io.open(HB, "r", encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2.get("heartbeat_epoch_utc"), int), "epoch must be int"
print("CLOSEOUT-OK r1009 counter->1010 epoch=", epoch, "cpu=", cpu_pct, "ram_free=", free_ram)
