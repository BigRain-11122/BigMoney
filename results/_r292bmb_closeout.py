# -*- coding: utf-8 -*-
"""r292 bm-b closeout: state.json + round report line + heartbeat (three-file ledger update)."""
import datetime
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M:%S")
ts_iso = now.isoformat()

# --- machine stats sample (same faces as compute_audit/py_watermark) ---
cpu_pct, free_ram_gb, gpu_free_mb = 0.0, 0.0, 0
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.5), 1)
    free_ram_gb = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception as e:
    print("psutil sample fail:", e)
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                          "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10).stdout
    gpu_free_mb = int(float(out.strip().splitlines()[0]))
except Exception as e:
    print("gpu sample fail:", e)

epoch = int(now.timestamp())
assert isinstance(epoch, int)

# --- state.json ---
sp = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
st = json.load(open(sp, encoding="utf-8-sig"))
st["round_no"] = 292
st["did"] = ("r292: S6 30/30 legs rc=0 (audit CLEAN pool-supply-gap) + town.html org_chart v2 对齐小活闭环 "
             "(研究楼 mandate BigMoney·调研部席位注记+footer r292 注, node --check PASS) + "
             "CN-TREND burn 活性验证 (4 worker 满核) + orders 91/91 双扫零未回执")
st["verdict"] = "green maintenance+alignment round ok (harvest pending p1_results; T-87 refresh in-flight)"
st["next"] = ("CN-TREND p1_results 落地观察=harvest 十面门(_r287bmb_cntrend_harvest.py)+pool flip; "
              "CENSUS-FUS-S2-W1=bm-a 车道 watch; T-87 pass ETA ~06:40 复探; "
              "09-28 周一开市新 bar 全链接力; 迁移窗 v2.2 armed 至 09-29 12:00")
st["current_task"] = "r292 done: S6 30/30 + town org_chart alignment; CN-TREND nulls burn in-flight (harvest on landing); T-87 refresh in-flight"
st["last_round_ts"] = ts
st["last_result"] = "ok"
st["last_tick"] = ts[-5:]
st["updated_at"] = ts
st["last_seen"] = ts_iso
st["ts"] = ts
st["last_run"] = f"R292 {ts_iso}"
st["last_round_at"] = ts
st["updated"] = ts
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state.json -> round 292")

# --- heartbeat fleet/machines/bm-b.json (own file only) ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8-sig"))
hb["last_seen"] = ts_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts_iso
hb["current_task"] = "r292 done: S6 30/30 legs rc=0 + town.html org_chart v2 alignment"
hb["cpu_cores"] = 16
hb["free_ram_gb"] = free_ram_gb
hb["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 1)
hb["total_ram_gb"] = 23.9
hb["cpu_util_pct"] = cpu_pct
hb["round_no"] = 292
hb["verdict"] = "healthy"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO"
print("heartbeat -> epoch int ok, clock T ok, cpu", cpu_pct, "ram", free_ram_gb, "gpu_mb", gpu_free_mb)

# --- round report line (bm-b file) ---
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    f"{ts_iso} | r292 (bm-b) | dept:工程 | WM-VERDICT: 绿 (red=false healthy; probe verdict=insufficient_history 15min 窗样本不足非红"
    "·py 29.8-42.2%=CN-TREND nulls 4-worker 真烧+T-87 限速采集=合法高位非闲) | did: S0 pull --rebase already-up-to-date"
    "(轮首脏=autofill_state 心跳脏 stash/pop 干净零冲突让路自提交律) + S0.5 orders 91/91 差集空(收尾双扫见 push 后复探)+决策审核步="
    "..\\..\\docs\\decisions.md 本机不可达零动作(镜面=fleet/orders O-件已覆盖·R291 律) + S1 smoke 25/25 + S3 小活闭环=town.html "
    "楼名/详情对齐 firm\\org_chart.md v2 部门表(九部门逐行 diff=唯一漂移=研究部行 2026-09-27 新增 BigMoney·调研部席位→研究楼 mandate "
    "追加『BigMoney·调研部席位（集团建制 2026-09-27）』+footer r292 注·node --check 语法门 rc=0·footer 追加近失误 git diff 当场自捕"
    "复恢零外泄→S4 坑律入册) + S6 30/30 legs rc=0(compute_audit CLEAN flags=[] load=pool-supply-gap·中秋 09-25 休市 cutoff 09-24 "
    "全覆盖诚实 no-op·astock refresh 在飞 lock-alive no-op·bm-a/bm-c 六车道 stdout-only·fundamental 5.1h skip·daily_report "
    "faces=4 同日再生·clock ORANGE_COOL 幂等·lhb min-interval guard) + CN-TREND burn 活性实证(4 worker 各 100% 核 CPU 6200s+"
    "·p1_results 未落地=harvest 按 r244 landed-marker 律续延) + T-87 refresh 在飞(ETA~06:40) + S4 CODELY +1 坑律(footer 追加保全律"
    "·5865B<10KB 硬线) | evidence: results/_r292_s6_chain.ps1+log(30/30 rc=0) + results/_r292_town_inline.js(node --check rc=0) + "
    "smoke 25/25 + schtasks 三任务在册(IterationLoop 正在运行/Watchdog 就绪/Autofill 就绪) + heartbeat epoch int 自证 "
    "| next: r293=CN-TREND p1_results 落地→harvest 十面门+pool flip+harvest_note(r279③) + CENSUS-FUS-S2-W1 bm-a 车道 watch + "
    "T-87 ETA 06:40 后 pass-completion 复探 + 09-28 周一开市新 bar 全链接力 + 迁移窗 watch(v2.2 armed 至 09-29 12:00·勿双 arm)\n"
)
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("round_reports.md appended r292")
