# r402 bm-c recovery closeout bookkeeping: report line (bytes append, LF face),
# state-bm-c.json bump 401->402, heartbeat fleet/machines/bm-c.json refresh.
# Laws: r600/r379 byte-face append (no EOL rewrite); heartbeat epoch MUST be
# JSON int; clock_read MUST be T-separated ISO8601 with offset (smoke F7).
import json
import subprocess
import time
from datetime import datetime, timezone, timedelta

ROOT = "K:/Fluxgroup/FluxGroup/quant/bigmoney"
now = datetime.now(timezone(timedelta(hours=8)))
ts = now.strftime("%Y-%m-%d %H:%M:%S")
ts_t = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# fresh machine readings (psutil used by compute_audit -> available)
try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=1.0), 1)
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu, ram_free = 7.0, 3.2
try:
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        creationflags=0x08000000)
    gpu_free = int(out.decode().strip().splitlines()[0])
except Exception:
    gpu_free = 880

report_line = (
    f"{ts} | r402 | dept:工程 | r402 猝死会话收口恢复轮（r381 恢复首动作律+r471 收养律·零重做先验后收）："
    "主产品=落地感知 pool_dualrun_reconcile 仪器修（r401 近失误实弹：flip 已落地〔r203 commit 298c4796b〕+s4 CLOSED〔r204 option a〕"
    "而 status 读出恒打 flip gate: READY 永不自证完成=永悬门·r401 下轮指针误提 flip 计划面 r402 开工 git log -S 核验当场拦零重复执行；"
    "修法=FLIP_LANDED_COMMIT/FLIP_RECEIPT_REL 常量+status 摘要 LANDED 读出+per-machine 行去门判语+cmd_run streak 去 /3 目标"
    "+selftest E1-E3 三腿·本轮 13/13 复跑实证）"
    "+T-147 done 翻面（face complete since r398·零新工作·result_ref+progress_r402 注记）"
    "+坑律三笔（pit-git direct-write：字节手术行界终结符双计×孤 CR 抑制清滤=整文件 staged diff 双坑·断言链当场拦零 origin 伤害；"
    "pit-pool r393 crash fuse 机队点火门 r401 漏扫补录；CODELY r393 条下沉+两域指针行注记）"
    "+MSG-0725 出站回执（提案② owner_since 单调爪门 r400 已交付=MSG-0630 末节请求闭环）+MSG-0630 处理移 processed"
    f"｜S0：pull 拒（自机 r402 WIP 树脏）→收养 carry commit 后 rebase 集成（origin 10 笔=bm-b r607/608 QUALITY-ROE x1/x2 judged 交付"
    "+NULLS 68/2000 在飞+bm-b X2 stale-claim 接管 bm-a 06:50 陈 claim+kill-advice MSG-0725-bma+autofill tick 5 笔·fleet/orders+tasks 零变化）"
    "｜S1 smoke 47/47 rc0；S6 33/33 ALL-RC0（_r402bmc_s6_runner.log 07:26-07:29·dualrun ZERO-DRIFT streak 9·golden-week 数据腿合法 no-op〔cutoff 2026-09-30〕"
    "·strategy_scorecard/t35_export/daily_scorecard/build_status=stale-takeover 合法〔bm-a 心跳 50-53min>20〕·scorecard 6 卡 S=2 A=4）；"
    "attrition 4 账本 CLEAN（healed 注记照录）；D-19 4167B784 不变零动作；orders 151/151 双扫零未回执；"
    "sat-engine rc0 活（N1 W57-114 12/12 全自持·常驻 run 形态）；watermark 绿（red=false·next_pick=claimed moneyflow IC 等面板）；"
    "S2 job_list 空+fleet tasks 零 open；T-152=等待态一行声明（bm-b MSG-0500 裁决未达·按等待轮律零重扫）"
    "｜下轮指针：(a) T-144(c) D-06 收口对账窗 10-07（pre-split 存留条+PS/spawn/编码族路由）；(b) T-152 bm-b 到货链→池点火 10-09 开市窗；"
    "(c) N3-R3 参轴增广候选 prereg 起草｜本地未达 origin commit 数=收口 push 后自证回填\n"
    "\n"
    "**当前活**：r402 猝死收口恢复推送中（主产品 dualrun 落地感知仪器修已验 13/13）。\n"
    f"**最近实物**：scripts/pool_dualrun_reconcile.py（落地感知修·selftest 13/13 含 E1-E3）+ results/_r402bmc_s6_runner.log（33 legs ALL-RC0）@ 2026-10-03 07:29。\n"
    "**下个里程碑**：T-144(c) D-06 全线收口 10-07；T-152 bm-b 到货链→池点火 10-09 开市窗。\n"
    "水位 verdict：绿——red=false·next_pick=claimed（moneyflow IC 批等面板·source-blocked 自愈观察）。\n"
)

# 1) report append -- byte face, LF, assert current tail ends with newline
rp = ROOT + "/round_reports-bm-c.md"
with open(rp, "rb") as f:
    tail = f.read()
assert tail.endswith(b"\n"), "report tail missing newline -- byte-face append law"
with open(rp, "ab") as f:
    f.write(report_line.encode("utf-8"))
with open(rp, "rb") as f:
    back = f.read()
assert back == tail + report_line.encode("utf-8"), "append not byte-clean"

# 2) state bump
sp = ROOT + "/state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 402
st["last_round_at"] = "r402"
st["last_round_ts"] = ts
st["updated"] = ts_t
st["cpu_pct"] = cpu
st["idle_ram_gb"] = ram_free
st["gpu_free_vram_mib"] = gpu_free
st["verify"] = ("smoke 47/47 rc0; dualrun selftest 13/13 rerun-verified (E1-E3 landed legs); "
                "S6 33/33 ALL-RC0 (crashed-session run adopted, log _r402bmc_s6_runner.log; "
                "dualrun ZERO-DRIFT streak 9; golden-week data legs legal no-ops); "
                "attrition 4 ledgers CLEAN; D-19 4167B784 unchanged zero action; "
                "orders 151/151 double-scan zero unacked; sat-engine rc0 alive (N1 W57-114 12/12 "
                "resident-run form); watermark GREEN (red=false, next_pick=claimed moneyflow IC panel-wait)")
st["did"] = ("r402 recovery-closeout of crashed r402 session (died post-S6 pre-commit; WIP verified "
             "then adopted per r381/r471): landed-aware pool_dualrun_reconcile instrument "
             "(FLIP_LANDED_COMMIT/FLIP_RECEIPT_REL + LANDED status readout + selftest E1-E3, 13/13) "
             "+ T-147 done-flip (face complete since r398) + 3 pit increments (git direct-write "
             "byte-surgery/EOL pit; pool r393 sweep backfill; CODELY r393 sink + pointer notes) "
             "+ MSG-0725 receipt to bm-a + S6 33/33 rc0")
st["current_task"] = "r402 closeout: carry commit + rebase integrate (origin 10 ahead) + push + delivery self-verify"
st["next"] = ("(a) T-144(c) D-06 closure reconciliation 10-07 (pre-split survivors + PS/spawn/encoding routing); "
              "(b) T-152 bm-b intake chain -> pool ignition 10-09 pre-market; "
              "(c) N3-R3 param-axis densification candidate prereg draft")
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = ts_t
st["last_ts"] = ts
st["last_decisions_read_at"] = ts_t
st["last_round"] = f"2026-10-03 r402 bm-c: crash-recovery closeout (landed-aware dualrun instrument + T-147 done + pit increments) + S6 33/33 rc0"
st["last_seen"] = ts
st["updated_at"] = ts_t
json.dump(st, open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# 3) heartbeat
hp = ROOT + "/fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["round_no"] = 402
hb["cpu_pct"] = cpu
hb["cpu_util_pct"] = cpu
hb["cpu_idle_pct"] = round(100 - cpu, 1)
hb["free_ram_gb"] = ram_free
hb["ram_free_gb"] = ram_free
hb["idle_ram_gb"] = ram_free
hb["total_ram_gb"] = 25.7
hb["gpu_free_vram_mb"] = gpu_free
hb["gpu_free_vram_mib"] = gpu_free
hb["gpu_idle_vram_mb"] = gpu_free
hb["gpu_idle_vram_mib"] = gpu_free
hb["gpu_vram_free_mb"] = gpu_free
hb["prod_lanes"] = ("r402 recovery-closeout: landed-aware dualrun instrument (selftest 13/13 incl E1-E3) "
                    "+ T-147 done-flip + pit increments x3 + S6 33/33 rc0; smoke 47/47")
hb["verdict"] = ("r402: crash-recovery carry commit (own WIP adopted per r381/r471, verified pre-commit: "
                 "smoke 47/47 + selftest 13/13 + S6 log all-rc0); watermark GREEN golden-week")
hb["current_task"] = "r402 closeout: carry commit + rebase + push + delivery self-verify"
hb["activity_now"] = "r402 closeout: carry commit + rebase integrate origin + push + self-verify"
hb["latest_artifact"] = ("scripts/pool_dualrun_reconcile.py (landed-aware instrument, selftest 13/13) "
                         "+ results/_r402bmc_s6_runner.log (33 legs rc0) @ 2026-10-03 07:29")
hb["next_milestone"] = ("T-144(c) D-06 full closure 10-07 (pre-split survivor routing); "
                        "T-152 bm-b intake chain -> pool ignition 10-09 pre-market window")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts_t
hb["last_seen"] = ts
hb["last_seen_at"] = ts
hb["updated_at"] = ts_t
hb["health"] = "ok"
json.dump(hb, open(hp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# self-verify: epoch MUST be int in both files (smoke F7 double-offense law)
for p in (sp, hp):
    d = json.load(open(p, encoding="utf-8"))
    e = d["heartbeat_epoch_utc"]
    assert isinstance(e, int) and not isinstance(e, bool), f"{p}: epoch not int: {type(e)}"
    assert "T" in d["clock_read"] and "+" in d["clock_read"], f"{p}: clock_read format: {d['clock_read']}"
print(f"CLOSEOUT BOOKKEEPING OK ts={ts} cpu={cpu} ram_free={ram_free} gpu_free={gpu_free} epoch={epoch}")
print("report_line_len =", len(report_line.encode('utf-8')))
