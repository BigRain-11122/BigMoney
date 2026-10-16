# -*- coding: utf-8 -*-
"""r1027 bm-a closeout: round report line + state update + heartbeat."""
import io
import json
import time
import datetime
import subprocess

NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())

# ---------- 1. round report line ----------
report = (
    f"{TS} | r1027 bm-a (dept:工程-数据源修复T23) | WM-VERDICT: 绿 (red=false lane healthy; satengine ALIVE rc0 queue0) | "
    "当前: r1027 = moneyflow panel 3 天停摆双根因定谳+gate 饿死修复 (T23) -- EM clist 路径级封锁 (per-IP path-specific) "
    "+ gate() rank 车道 30min 节流早退把健康 daykline 车道饿死 3 天 (10-14 19:46 起 panel 零推进) | "
    "did: S0-1 orphan=1 (死窗 probe 面 mcp-bridge 只读零杀); S0 脏树=4 preflight 运行面 (heartbeat 05:26 closeout 写+probe 05:28:0x) "
    "bm-a 自有面定向吸收 146f7217d -> rebase 1 UU (watermark_red bm-c 05:25 vs bm-a 05:30 同族 probe 快照 live-wins take-mine) "
    "-> 9d3706ba4 clean; S0.5 orders_ack 差集零未回执 + D-19 双 delta DEC 881b6dcb / ORD fcc715ea 双 hold 零新派工; "
    "S1 smoke 49/49; S2 板无 open 票 + P2/P3 队头 T22/E14 均 done = 三空 -> T23 同轮登记同轮执行 (queue_seed_gate hits=[] open); "
    "S3 T23: 双差分探针八腿 (clist 全变体 FAIL incl delay-host/jsonp/http/fid-f3; fflow 000001 05:35 OK 14,583B -> 05:50 全 FAIL; "
    "push2 同主机 stock/get OK = clist 路径级封锁 + fflow 波动性 per-IP 封锁窗并存 r40/r46 族) -> gate 修复 "
    "(_rank_source_blocked 助手 + 节流分支 skip_rank_spawn 整块跳过重构; 首版 fall-through 漏 break 实弹自纠=fall-through 打印后 "
    "控制流仍流入 rank spawn 路径·rank 子代 fetch 失败无害自灭) + selftest 21/21 (S20 新增八断言) + 两发实弹 "
    "(05:46 错 spawn rank 自灭 -> 15s 后复跑 gate = fall-through -> spawned detached refresh = panel 首次挣脱 3 天饿死; "
    "refresh 子代撞波动封锁窗 3 连断诚实停 checkpoint 完好 -> 30min gate 自愈重试武装 top-level spawn 时钟; done=2152 todo≈3069); "
    "S6 43/43 rc0 bad=0 (driver _r1027bma_s6chain.ps1 分离进程+日志重定向); S7 tasks 双在册 pin=8 no-op + claws CR-归一 match "
    "+ inbox own-echo receipt MSG-0128 归档 processed | "
    "latest artifact: scripts/update_moneyflow.py (T23 修复+selftest) + results/_r1027bma_mf_source_diag.py+.json (八腿探针铁证) "
    "+ state/queue/tech.md T23 行 done + knowledge/METHODOLOGY_ASSETS.md E71 卡 + CODELY.md 判例行 | "
    "next milestone: moneyflow refresh 自愈窗观察 (封锁窗 lift -> todo≈3069 码 ~2.1h 填 10-14..10-16; 后续评估 done 码 2152 "
    "尾停 10-13 的 gap-fill repull) + W258 finalize -> W259 席位竞争窗, 时窗 <=2026-10-18 | "
    "verify: smoke 49/49 + S6 43/43 rc0 bad=0 + selftest 21/21 + 两发 gate 实弹输出留痕 + 探针 json 落盘 + "
    "schtasks 双在册 (Loop 05:58 / Watchdog 05:50) + D-19 双 hold 读回恒等 + push 后未达 origin=0"
)
with io.open("round_reports-bm-a.md", "r", encoding="utf-8") as f:
    txt = f.read()
if not txt.endswith("\n"):
    txt += "\n"
with io.open("round_reports-bm-a.md", "w", encoding="utf-8", newline="") as f:
    f.write(txt + report + "\n")
print("report appended")

# ---------- 2. state update ----------
with io.open("state-bm-a.json", "r", encoding="utf-8") as f:
    st = json.load(f)

did = ("r1027 closed: moneyflow panel 3 天停摆双根因定谳+T23 gate 饿死修复 -- "
       "(1) 双差分探针八腿定谳: EM clist 路径级封锁 (全变体 FAIL/delay-host/jsonp/http/fid 换全灭) + fflow 波动性 per-IP 封锁窗 "
       "(05:35 OK->05:50 FAIL) 并存; (2) gate() 修复: rank 车道节流早退饿死 daykline 车道 3 天 -> _rank_source_blocked+skip_rank_spawn "
       "整块跳过重构 (首版 fall-through 漏 break 实弹自纠); (3) selftest 21/21 + 两发实弹: refresh spawn 成功=panel 首次挣脱饿死, "
       "撞波动窗 3 连断诚实停 30min 自愈武装 (done=2152 todo≈3069); (4) S6 43/43 rc0; (5) D-19 双 hold 零新派工; "
       "(6) T23 同轮登记同轮 done (tech 队列); E71 方法论卡+CODELY 判例行落账")

st.update({
    "round_no": 1027, "round": 1027, "loop_round": 1027, "last_round": 1027,
    "current": did, "did": did, "last_action": "r1027: T23 moneyflow gate 饿死修复 (双差分定谳+修复+selftest 21/21+refresh spawn 实弹)",
    "current_task": "r1027 T23 moneyflow source-block diagnosis + gate starvation fix (panel self-heal armed)",
    "task": "r1027 T23 moneyflow source-block diagnosis + gate starvation fix (panel self-heal armed)",
    "last_action_at": TS, "last_round_at": TS, "last_round_ts": TS, "last_round_closed": TS,
    "last_run": TS, "last_seen": TS, "ts": TS, "updated": TS, "updated_at": TS,
    "last_artifact": ("scripts/update_moneyflow.py (T23) + results/_r1027bma_mf_source_diag.py+json (八腿探针) + "
                      "state/queue/tech.md T23 done 行 + knowledge/METHODOLOGY_ASSETS.md E71 卡 + CODELY.md 判例行 + "
                      "_r1027bma_s6chain.ps1 (43 腿驱动器)"),
    "latest_artifact": ("scripts/update_moneyflow.py (T23) + results/_r1027bma_mf_source_diag.py+json (八腿探针) + "
                        "state/queue/tech.md T23 done 行 + knowledge/METHODOLOGY_ASSETS.md E71 卡 + CODELY.md 判例行 + "
                        "_r1027bma_s6chain.ps1 (43 腿驱动器)"),
    "recent_artifact": ("scripts/update_moneyflow.py (T23) + results/_r1027bma_mf_source_diag.py+json (八腿探针) + "
                        "state/queue/tech.md T23 done 行 + knowledge/METHODOLOGY_ASSETS.md E71 卡 + CODELY.md 判例行 + "
                        "_r1027bma_s6chain.ps1 (43 腿驱动器)"),
    "next": ("r1028+: (a) moneyflow refresh 自愈窗观察: 30min gate 重试在役, 封锁窗 lift -> todo≈3069 码 ~2.1h 填 10-14..10-16 "
             "(每 30min 一发 3 请求成本); (b) panel complete 后评估 gap-fill repull (done 码 2152 尾停 10-13 vs todo 码尾 10-16 "
             "=截面尾参差·daykline 补拉一次 3.6h 夜窗可齐); (c) rank clist 路径封锁观察 (EM 侧可能解除; 解除后 rank 车道自恢复); "
             "(d) MF-IC-P1 仍合法等待 (完备门 N>=150 资格日远未到·panel complete 只是第一件); (e) W258 finalize -> W259 席位竞争窗 "
             "(bm-c 自续链 ~10min·抢席窗窄·被占顺延 W259+); (f) moneyflow panel complete 即 next_pick 更新面 (IC 批仍候 N 门)"),
    "next_milestone": ("moneyflow panel 前向恢复 (封锁窗 lift 后 ~2.1h 内 complete) + W259 席位竞争, 时窗 <=2026-10-18"),
    "now_active": ("bm-a full-work r1027 毕 (T23 修复+panel 自愈武装); engine-lane = W258 bm-c 在飞 (prereg derive r1061), "
                   "W259 席位候窗; 35B:8090 常设; 周六夜窗满载合法"),
    "heartbeat_epoch_utc": EPOCH, "last_heartbeat_epoch_utc": EPOCH,
    "heartbeat_epoch_utc_type_int": True,
    "clock_read": TS,
    "idle_rounds": 0, "agenda_starved": False,
    "last_orders_at": TS, "last_decisions_at": TS,
    "last_decisions_seen": "r1027: DEC 881b6dcb hold (双 delta MATCH 零新行)",
    "last_orders_seen": "r1027: ORD fcc715ea hold (双 delta MATCH 零新行)",
    "orders_ack_note": "r1027: +0 (orders_ack 差集空; D-19 双 delta MATCH)",
    "orphan_face": 1, "orphan_faces": 1, "orphan_killed": 0,
    "notes_seq_repair_r1027": ("r1027 sequence-honest: 本窗=S0 吸收 preflight 运行面后正常推进; canonical face = "
                               "round_reports-bm-a.md + git log"),
    "verdict": ("green-product (watermark=绿 red=false; smoke 49/49; satengine ALIVE rc0 队列 0; T23 修复+selftest 21/21+两发实弹; "
                "panel 自愈武装候封锁窗; D-19 双 hold; 双爪双任务全绿; 孤儿面=1 死窗 probe 只读; P2 队列 T23 同轮登记同轮 done)"),
    "verify": ("smoke 49/49 + S6 43/43 rc0 bad=0 (chain log _r1027bma_s6chain_rc.log) + satengine status rc0 queue0 + "
               "selftest 21/21 (S20 八断言含) + gate 两发实弹输出 (fall-through + spawned detached refresh) + "
               "探针 results/_r1027bma_mf_source_diag.json 八腿 + schtasks 双在册 (Loop/Watchdog) + pin=8 no-op + "
               "claws CR 归一 match + D-19 双 hold 读回 + push 后 behind-0 自证"),
})

with io.open("state-bm-a.json", "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state updated, epoch int:", isinstance(st["heartbeat_epoch_utc"], int))

# ---------- 3. heartbeat ----------
with io.open("fleet/machines/bm-a.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
try:
    import psutil
    ram = psutil.virtual_memory()
    free_gb = round(ram.available / 1024**3, 1)
except Exception:
    free_gb = hb.get("free_ram_gb", 26.0)
hb.update({
    "last_seen": TS, "ts": TS, "clock_read": TS,
    "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True,
    "current_task": "r1027 T23 moneyflow gate-starvation fix landed (panel self-heal armed, block-window watch)",
    "verdict": "green-product r1027 (T23 done + S6 43/43 + smoke 49/49)",
    "idle_rounds": 0, "agenda_starved": False,
    "free_ram_gb": free_gb, "idle_ram_gb": free_gb, "ram_free_gb": free_gb,
})
with io.open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with io.open("fleet/machines/bm-a.json", "r", encoding="utf-8") as f:
    back = json.load(f)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
print("heartbeat updated, epoch int verified:", back["heartbeat_epoch_utc"])
