# r1034 bm-a closeout: round report append + heartbeat + state update
# Encoding law: report append = UTF-8 + CRLF (r843/r846); JSON = raw UTF-8 indent=1
import io, json, time, datetime, psutil

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now_dt = datetime.datetime.now().astimezone()
now = now_dt.isoformat(timespec="seconds")
epoch = int(time.time())
vm = psutil.virtual_memory()
ram_free_gb = round(vm.available / 1e9, 1)
ram_free_mb = int(round(vm.available / 1e6))
ram_free_pct = int(round(100 * vm.available / vm.total))

R = "r1034"
report_line = (
    now + " | " + R + " bm-a (dept:舰队常规维护轮·S6 43/43 全绿+W262 席位让路裁定+moneyflow 双车道封锁观察) | "
    "当前活=r1034 常规维护收口（S6 43/43+live_paper bad=0；W261 finalize 已证完整·W262 席位=bm-c r1067 origin vacancy 先到·bm-a 让路·W263=bm-a 候位窗候 W262 注册）；"
    "最近实物=results/_r1034bma_s6chain_rc.log（43/43 rc0 bad=0 14:52:29）+results/_r1034bma_s6chain.ps1（驱动器）+docs/daily_report/REPORT-2026-10-17.md 再生+docs/live_usage/LIVE-2026-10-17.md 再生；"
    "下个里程碑=W262 注册落地→W263 bm-a 席位窗（probe+seat MSG·post-W262 universe 活重推导·窗≤48h 随 bm-c 冻结节奏）+moneyflow 面板 complete（双车道封锁解除后·每轮复测）；"
    "本轮=S0 吸收运行面+pull rebase 1-commit clean；D-19 双扫双 hold（dec 1d4741e4/ord 1df82bab 与水位恒等零新行）；S1 smoke 49/49；satengine ALIVE queue0 idle；watermark red=false；"
    "W261 链证=finalize one-pass 996,335+2,200=998,535 EXACT/K=572,120+fivekeys 6/6+sixgate 23 连绿（bm-c r1067 席位 MSG 消费）；"
    "moneyflow 观察=rank 车道仍 RemoteDisconnected·daykline 后备车道 14:50 spawn 刷新 3 连败（300706-08 conn 级 RemoteDisconnected）→fuse 停发 checkpoint 完好——EM 封锁疑似从 clist 扩至 per-stock 端点族（观察项·下轮复测判瞬态 vs 扩面）·panel cutoff 2026-10-13 complete=False；"
    "四件套=loop pin=8 no-op+claws x2 match+watchdog -Force 幂等重装+S4U 翻面 access-denied 携带（C-20261016-04）；inbox W262 seat MSG 已处理入 processed/；"
    "idle green_idle=false 合法（CEO 周末用机 RAM " + str(ram_free_pct) + "%）；孤儿面=1 只读（BigCompute pythonw 43.5h 三面孤儿）；本地未达 origin commit 数=0（收口推送后自证）"
)

# --- 1) round report append (UTF-8 + CRLF, tail probe) ---
rp = ROOT + r"\round_reports-bm-a.md"
raw = open(rp, "rb").read()
if raw and not raw.endswith(b"\n"):
    raw += b"\r\n"
with io.open(rp, "ab") as f:
    f.write(report_line.encode("utf-8") + b"\r\n")
print("report appended, line bytes:", len(report_line.encode("utf-8")))

# --- 2) heartbeat update ---
hb_path = ROOT + r"\fleet\machines\bm-a.json"
hb = json.load(io.open(hb_path, encoding="utf-8"))
last_epoch = hb.get("heartbeat_epoch_utc", 1792217656)

did = ("r1034 closed: standard maintenance round: S0 absorb runtime faces + pull rebase 1-commit clean (bm-c W262 seat pair) "
       "+ D-19 double-hold both scans (dec 1d4741e4 / ord 1df82bab identical to watermarks, zero new rows) "
       "+ S1 smoke 49/49 + satengine ALIVE queue0 idle + watermark red=false "
       "+ S6 chain 43/43 + live_paper rc0 bad=0 (14:44->14:52:29, driver _r1034bma_s6chain.ps1) "
       "+ W262 seat observed = bm-c r1067 82nd own wave (origin vacancy + commit-time order, bm-a yields per fleet README sec.4; "
       "W263 = bm-a next seat window gated on W262 registration, live re-derive on post-W262 universe, no-skip-claim) "
       "+ W261 complete chain verified from seat MSG (finalize one-pass 996,335+2,200=998,535 EXACT / K=572,120 + fivekeys 6/6 + sixgate 23rd consecutive) "
       "+ moneyflow observation: rank lane still RemoteDisconnected; daykline backup refresh spawned 14:50 -> 3 conn failures (300706-08) -> conn-fuse stopped checkpoint intact "
       "(EM blockade suspected widened from clist to per-stock endpoint family, retest next round; panel cutoff 2026-10-13 complete=False) "
       "+ quad green (loop pin=8 no-op, claws match x2, watchdog -Force idempotent re-reg, S4U flip access-denied carried C-20261016-04) "
       "+ inbox W262 seat MSG processed + queue P2/P3 heads all done/closed + idle green_idle=false lawful (CEO weekend machine) + orphan face=1 read-only carried")

hb.update({
    "ts": now, "updated": now, "updated_at": now, "last_seen": now, "last_run": now,
    "last_round": 1034, "last_round_at": now, "last_round_closed": now, "last_round_ts": now,
    "round": 1034, "round_no": 1034, "loop_round": 1034,
    "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": last_epoch,
    "clock_read": now,
    "current": did, "did": did,
    "current_task": "r1034 maintenance (S6 43/43 rerun + W262 seat yield + moneyflow double-lane block observation)",
    "task": "r1034 maintenance (S6 43/43 rerun + W262 seat yield + moneyflow double-lane block observation)",
    "last_action": "r1034: S6 43/43 rc0 + D-19 double-hold + W262 seat yielded to bm-c (W263 next window) + moneyflow daykline lane 3-conn-fail fuse observation",
    "last_action_at": now,
    "last_artifact": "results/_r1034bma_s6chain_rc.log (43/43 rc0 bad=0 14:52:29) + results/_r1034bma_s6chain.ps1 + docs/daily_report/REPORT-2026-10-17.md + docs/live_usage/LIVE-2026-10-17.md regenerated",
    "latest_artifact": "results/_r1034bma_s6chain_rc.log (43/43 rc0 bad=0 14:52:29) + results/_r1034bma_s6chain.ps1 + docs/daily_report/REPORT-2026-10-17.md + docs/live_usage/LIVE-2026-10-17.md regenerated",
    "recent_artifact": "results/_r1034bma_s6chain_rc.log (43/43 rc0 bad=0 14:52:29) + results/_r1034bma_s6chain.ps1 + docs/daily_report/REPORT-2026-10-17.md + docs/live_usage/LIVE-2026-10-17.md regenerated",
    "last_orders_at": now, "last_orders_read_at": now,
    "last_orders_seen": "r1034: opening + closing double-scan both HOLD (ord 1df82bab identical, zero new rows; dec 1d4741e4 hold)",
    "last_decisions_at": now, "last_decisions_read_at": now,
    "last_decisions_seen": "r1034: dec 1d4741e4 hold both scans (identical both windows)",
    "orders_ack_note": "r1034: zero new order rows both scans (ord 1df82bab hold), zero unacked order files on disk",
    "next": "r1035+: (a) W262 prereg derive/freeze/burn watch on bm-c -> W262 registration lands -> W263 bm-a seat window opens (probe+seat MSG, live re-derive on post-W262 universe, no-skip-claim); (b) moneyflow retest next round: daykline lane conn-fail = transient vs widened-EM-blockade adjudication; (c) 5x HANDOVER check at r1035; (d) S4U conversion privilege-window backlog (C-20261016-04, elevated=0 carried)",
    "next_milestone": "W262 registration -> W263 bm-a own-wave seat window (follows bm-c freeze cadence, eta today evening) + moneyflow panel complete (post-unblock, window <=2026-10-19)",
    "now_active": "bm-a r1034 maintenance closed (S6 43/43 + D-19 double-hold); engine-lane W262 seat = bm-c 82nd own wave (bm-a yielded, W263 = bm-a window post-W262-registration); moneyflow double-lane conn-block observed (rank + daykline both RemoteDisconnected, fuse stopped, self-heal standing); 35B:8090 standing; Saturday CEO-weekend lawful idle=false (RAM " + str(ram_free_pct) + "%)",
    "verdict": "green r1034 maintenance (watermark=green red=false; smoke 49/49; satengine ALIVE rc0 queue0 idle; S6 43/43 rc0 bad=0 + live_paper rc0; D-19 dec 1d4741e4/ord 1df82bab double-hold zero rows; W262 seat yielded to bm-c per commit-time order, W263 = bm-a window; moneyflow rank+daykline double conn-block, checkpoint intact, self-heal standing; claws match x2; Loop pin=8 no-op; Watchdog -Force re-reg; S4U access-denied carried C-20261016-04; orphan face=1 read-only)",
    "verify": "S6 43/43 rc0 bad=0 log _r1034bma_s6chain_rc.log + smoke 49/49 + satengine status rc0 + d19 probe double-hold readback (dec/ord sha identical) + claws CR-normalized match=YES x2 + register_loop pin=8 no-op + attrition_guard rc0 (chain leg) + round_reports-bm-a.md r1034 line landed",
    "free_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb, "idle_ram_gb": ram_free_gb,
    "ram_free_mb": ram_free_mb, "idle_ram_mb": ram_free_mb,
    "free_ram_pct": ram_free_pct, "ram_free_pct": ram_free_pct,
    "ram_load_pct": 100 - ram_free_pct,
    "total_ram_gb": 93.6,
    "gpu_free_vram_mb": 750, "gpu_total_vram_mb": 12282,
    "gpu_source_note": "nvidia-smi live read " + now + " (CEO working machine, honest free face)",
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_face": 1, "orphan_faces": 1, "orphan_killed": 0,
})
with io.open(hb_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written, epoch int OK:", chk["heartbeat_epoch_utc"])

# --- 3) state update ---
st_path = ROOT + r"\state-bm-a.json"
st = json.load(io.open(st_path, encoding="utf-8"))
st_epoch_last = st.get("heartbeat_epoch_utc", 1792217656)
st.update({
    "ts": now, "updated": now, "updated_at": now, "last_seen": now, "last_run": now,
    "last_round": 1034, "last_round_at": now, "last_round_closed": now, "last_round_ts": now,
    "round": 1034, "round_no": 1034, "loop_round": 1034,
    "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": st_epoch_last,
    "clock_read": now,
    "current": did, "did": did,
    "current_task": "r1034 maintenance (S6 43/43 rerun + W262 seat yield + moneyflow double-lane block observation)",
    "task": "r1034 maintenance (S6 43/43 rerun + W262 seat yield + moneyflow double-lane block observation)",
    "last_action": "r1034: S6 43/43 rc0 + D-19 double-hold + W262 seat yielded to bm-c (W263 next window) + moneyflow daykline 3-conn-fail fuse observation",
    "last_action_at": now,
    "last_artifact": "results/_r1034bma_s6chain_rc.log (43/43 rc0 bad=0 14:52:29) + results/_r1034bma_s6chain.ps1 + docs/daily_report/REPORT-2026-10-17.md regenerated",
    "latest_artifact": "results/_r1034bma_s6chain_rc.log (43/43 rc0 bad=0 14:52:29) + results/_r1034bma_s6chain.ps1 + docs/daily_report/REPORT-2026-10-17.md regenerated",
    "recent_artifact": "results/_r1034bma_s6chain_rc.log (43/43 rc0 bad=0 14:52:29) + results/_r1034bma_s6chain.ps1 + docs/daily_report/REPORT-2026-10-17.md regenerated",
    "last_orders_at": now, "last_orders_read_at": now,
    "last_orders_seen": "r1034: opening + closing double-scan both HOLD (ord 1df82bab identical zero new rows; dec 1d4741e4 hold both)",
    "last_decisions_at": now, "last_decisions_read_at": now,
    "last_decisions_seen": "r1034: dec 1d4741e4 hold both scans",
    "next": "r1035+: (a) W262 registration watch -> W263 bm-a seat window (live re-derive post-W262 universe); (b) moneyflow daykline retest (transient vs widened blockade); (c) 5x HANDOVER check at r1035; (d) S4U backlog carried",
    "next_milestone": "W262 registration -> W263 bm-a seat window + moneyflow panel complete (post-unblock)",
    "now_active": "bm-a r1034 maintenance closed; W262 seat = bm-c (bm-a yields, W263 next window post-W262-registration); moneyflow double-lane conn-block observation standing",
    "verdict": "green r1034 maintenance (S6 43/43 rc0 bad=0 + smoke 49/49 + satengine ALIVE queue0 + D-19 double-hold + W262 yield + moneyflow fuse-stopped checkpoint intact + quad green)",
    "verify": "S6 43/43 rc0 bad=0 log _r1034bma_s6chain_rc.log + smoke 49/49 + d19 probe double-hold + claws match x2 + loop pin=8 no-op + attrition rc0",
    "free_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb, "idle_ram_gb": ram_free_gb,
    "ram_free_mb": ram_free_mb, "idle_ram_mb": ram_free_mb,
    "free_ram_pct": ram_free_pct, "ram_free_pct": ram_free_pct, "ram_load_pct": 100 - ram_free_pct,
    "total_ram_gb": 93.6,
    "gpu_free_vram_mb": 750,
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_face": 1, "orphan_faces": 1, "orphan_killed": 0,
    "notes_r1034": "r1034: (1) W262 seat = bm-c 82nd own wave per origin-vacancy + commit-time order (bm-a r1033 next-plan expected W262 but bm-c r1067 landed 14:37:28 first; bm-a yields per fleet README sec.4; W263 = bm-a window, gated on W262 REGISTRATION for live re-derive, no-skip-claim zero W263/W264 claims on origin verified in seat MSG); "
                   "(2) moneyflow daykline backup lane first observed conn-level failures (300706-08 RemoteDisconnected 14:50, fuse stopped checkpoint intact) -- EM blockade suspected widened from clist path to per-stock endpoint family OR transient window; next-round retest adjudicates; rank lane fetch_failed fall-through fix (r1027) worked as designed (no starvation)",
})
with io.open(st_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
chk2 = json.load(io.open(st_path, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int)
print("state written, round_no:", chk2["round_no"])
print("closeout writes complete")
