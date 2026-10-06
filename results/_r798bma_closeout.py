# -*- coding: utf-8 -*-
# _r798bma_closeout.py -- S5/S7 closeout: state round_no 797->798, heartbeat fields
# (epoch int + clock_read T-sep + ts), round-report line, CODELY.md Project execution
# record line. Multi-writer files: fresh-read-modify-write (r774 law).
import json, io, time, datetime, platform

def iso_now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

ts = iso_now()
epoch = int(time.time())

# ---------- state-bm-a.json ----------
SP = r"state-bm-a.json"
st = json.load(io.open(SP, encoding="utf-8"))
st["round_no"] = 798
st["current_task"] = ("r798 closed: O-20261006-2110/2250 dual-order deployment+enforcement window "
                     "(machine-state.ps1 pause/resume switch deployed+live-tested, 13 task runners "
                     "converted to hidden chain, dual notification gates 0/0, receipts filed); "
                     "next: W166 freeze arc per r797 plan or moneyflow IC prereg per bandit pick")
st["did"] = ("r798: S0 churn-absorb delivery of dead-r797 legacy (4 picks replayed onto origin "
             "31503b8e2 via r758 hand-land + r543 remaining-picks cherry-pick + r624 branch -f "
             "remount; 3 UU ALL_FACES merge_lane_views resolve union; push af4e1f555 clean) + "
             "O-20261006-2110 CEO machine-yield-law deployment (kit 2 files from origin blob, "
             "3 LOCALIZE blocks filled, pause live-run v1->v1.1 'ollama app' tray-respawner patch, "
             "status MODE=pause, resume command fixed NOT run per order) + O-20261006-2250 silence "
             "law (gates 0/0 read-back, 13 tasks to wscript hidden chain, zero-window memory) + "
             "receipts in both order files + ack x2 + D-19 ord watermark 9a273eca consumed")
st["last_action"] = "r798 closed: dual CEO-order deployment window complete, receipts filed"
st["heartbeat_epoch_utc"] = epoch
io.open(SP, "w", encoding="utf-8", newline="").write(json.dumps(st, ensure_ascii=False, indent=1))
print("state round_no:", st["round_no"], "| epoch:", epoch, "| isinstance int:", isinstance(st["heartbeat_epoch_utc"], int))

# ---------- heartbeat fleet/machines/bm-a.json ----------
HP = r"fleet\machines\bm-a.json"
h = json.load(io.open(HP, encoding="utf-8"))
h["last_seen"] = ts
h["current_task"] = "r798 closed: O-2110/2250 dual-order deployment+receipts; machine GPU/LLM face paused per CEO yield law (quant fleet lines preserved)"
h["cpu_cores"] = 32
try:
    import psutil
    h["idle_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
except Exception:
    h["idle_ram_gb"] = None
h["gpu_idle_vram_mb"] = 11199  # 12282 total - ~1083 used at pause-verified face
h["verdict"] = "healthy: fleet lines green (smoke 48/48, S6 38/38, engine alive); GPU/LLM/cron face=PAUSED per O-20261006-2110 live-test (resume on CEO quanmian-kaigong)"
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = ts
h["ts"] = ts
io.open(HP, "w", encoding="utf-8", newline="").write(json.dumps(h, ensure_ascii=False, indent=1))
chk = json.load(io.open(HP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("heartbeat ok | epoch int:", isinstance(chk["heartbeat_epoch_utc"], int), "| ack:", len(chk.get("orders_ack", [])))

# ---------- round report line ----------
RP = r"logs\iteration-loop\round_reports-bm-a.md"
line = (
    "{ts} | r798 bm-a (dept:工程) | watermark verdict: 绿(red=false lane=healthy; probe py 低位=golden-week 合法 idle 白名单面: 板全闭环 0 open 票+引擎 idle verdict+0 active burns) | "
    "当前活: O-20261006-2110/2250 双 CEO 令部署执法窗收口(让路律 machine-state.ps1 开关+静默律 13 任务隐藏链+双路闸 0/0) | "
    "最近实物: C:\\Users\\sjs20\\Desktop\\FluxGroup\\.codely-cli\\machine-state.ps1(v1.1 pause 实测 OK vramUsedMB=1089)+fleet/orders/O-20261006-2110-bm-c.md 与 O-20261006-2250-bm-c.md bm-a 回执节全勾 @23:2x | "
    "下个里程碑: W166 冻结链(r797 计划 4 工具件续作·never-dry 线≤24h)+D-20261005-07/08 回执窗 10-07 12:00 | "
    "did: S0 churn-absorb 送达 dead-r797 遗产(4 pick 重放·3 UU ALL_FACES merge_lane_views union·r758 手落+r543 余 pick 补落+r624 重挂·push af4e1f555 31503b8e2..af4e1f555 干净)·"
    "S0.5 差集 2 令(O-2110 让路律: kit 双件 origin blob 直取部署集团根 .codely-cli+三 LOCALIZE 填实〔$tasks=BigCompute 6+MiniGameOllama 2·$pinModel=qwen3-8b-ud:q4_k_xl 部署时在驻 legacy qwen2.5:7b-instruct 如实披露·$keepAliveTask=null〕+pause 实跑 v1 揭托盘 app respawn 盲区→v1.1 补丁复跑 OK production-clean exit 0+status MODE=pause+resume 照令未跑+触发词律入用户级 CODELY.md·"
    "O-2250 静默律: 双路闸设值读回 0/0+57 任务审计 13 转换 wscript //B //nologo 隐藏链〔CarGZH×8/QuantOversightDigest/GimmeAll/MoneyAutoGuardian/FluxBoardAuto/ResidentQA·13/13 读回验证零败〕+第三方 8 项只列报+零窗律入记忆)·双令回执节填写+ack 170·"
    "决策审核步 dec a44c39e0 match 零动作+ord 6f3ac292→9a273eca 消费(增量行=本窗两令已执行)·S1 smoke 48/48·S6 38/38 rc0 151s(_r798bma_s6_chain)·S7 四件套绿(pin=8 no-op+watchdog 重注册+双爪重装 CR 归一)+attrition CLEAN x4·inbox W166 seat 信(自发已交付 d1dc12117)核验后移 processed·state 797→798+心跳 epoch int 自证 | "
    "verify: O-2110 pause v1.1 实测输出在令回执节(vramUsedMB=1089/进程面 ollama 族计数 0)·O-2250 闸读回 0/0+13/13 wscript 读回·smoke 48/48·S6 38/38·本地未达 origin commit 数=0(commit 后 push+fetch+rev-list 复核补录) | "
    "next: (1) r799=W166 冻结链续作(r797 计划件: face probe→prereg→freeze edits→verify 9 腿→commit→tick 自燃 12 shards)或 moneyflow IC prereg(bandit next_pick claimed 指针) (2) D-20261005-07/08 回执窗 10-07 12:00 (3) T-173 48h 题材报告 due 10-08 午 | [r798 bm-a]\n"
).format(ts=ts)
with io.open(RP, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("RR line appended")

# ---------- CODELY.md Project execution record ----------
CP = r"CODELY.md"
s = io.open(CP, encoding="utf-8").read()
entry = ("- [{ts_short} r798 bm-a] O-20261006-2110/2250 双令 bm-a 执行记录（CEO 用机让路律+机队静默工作律·同窗合并回执 10-07 18:00 大限）："
         "让路律=kit 双件部署 `C:\\Users\\sjs20\\Desktop\\FluxGroup\\.codely-cli\\machine-state.ps1`(v1.1)+pause 实测 OK（首跑揭 Ollama 托盘 app respawn 盲区→本机补 kill 面修复·VRAM 6748→1089MB·status MODE=pause·resume 固化未跑）；"
         "静默律=双路通知闸 0/0 读回+13 自建任务转 wscript 隐藏链（13/13 零败）+零窗律入用户级 CODELY.md；触发词「我要打游戏/我要工作=本机 pause·全面开工=resume+O 令广播」入记忆。"
         "正典=两令件 bm-a 回执节；坑=kit 模板托盘盲区建议回流上游。How to apply：听到触发词即进程内 `&` 执行开关勿再问。\n").format(ts_short=ts[:16])
anchor = "### Reference"
i = s.find(anchor)
if i < 0:
    s += "\n" + entry
else:
    j = s.rfind("\n", 0, i) + 1
    s = s[:j] + entry + s[j:]
io.open(CP, "w", encoding="utf-8", newline="").write(s)
print("CODELY.md Project entry appended | bytes:", len(s.encode("utf-8")))
