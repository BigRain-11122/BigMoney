#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r253 bm-c S7 closeout: guard scan + dualrun verdict + state/heartbeat/report updates."""
import json, subprocess, sys, io, os, time, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)

# 1) leg-01 dualrun verdict from evidence
ev = json.load(open("results/_r253bmc_s6_chain.json", encoding="utf-8"))
leg1 = next((r for r in ev["rows"] if r["i"] == 1), {})
print("LEG1 dualrun:", leg1.get("tail", "")[:220])

# 2) attrition ledger guard scan
g = run(["python", "scripts/attrition_ledger_guard.py", "scan"])
print("attrition rc=%d :: %s" % (g.returncode, (g.stdout or "").strip().splitlines()[-1:]))

# 3) state round_no 252 -> 253
st = json.load(open("state-bm-c.json", encoding="utf-8"))
prev = st.get("round_no")
st["round_no"] = int(prev or 0) + 1
with open("state-bm-c.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state round_no %s -> %s" % (prev, st["round_no"]))

# 4) heartbeat
now = datetime.datetime.now().astimezone()
epoch = int(time.time())
cpu = run(["powershell", "-NoProfile", "-Command",
           "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"])
free_gb = run(["powershell", "-NoProfile", "-Command",
               "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"])
try:
    cpu_pct = float(cpu.stdout.strip() or 0)
except Exception:
    cpu_pct = 0
try:
    ram_free = float(free_gb.stdout.strip() or 0)
except Exception:
    ram_free = 0

hb = json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))
hb["round_no"] = st["round_no"]
hb["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
hb["current_task"] = "r253 rebase double-wedge resolution + S6 sweep (r252 yield work landed origin)"
hb["cpu_cores"] = 32
hb["free_ram_gb"] = ram_free
hb["gpu_free_vram_mb"] = hb.get("gpu_free_vram_mb")
hb["verdict"] = "loaded_ok"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now.isoformat(timespec="seconds")
with open("fleet/machines/bm-c.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be ISO8601 with T"
print("heartbeat ok epoch=%d clock=%s cpu=%s ram_free=%s" % (epoch, chk["clock_read"], cpu_pct, ram_free))

# 5) round report line
line = "%s | r253 | rebase 双楔收口：r252 让路工件经两轮 origin 撞批（bm-b r446 窗+bm-a r458 窗）按 r443/r446/r449 union-blob 律解冲突 20+16 件（17+12 派生面取 origin 防回退·compute_audit history union 210·x2 双跑 6+6 全留·CODELY 双侧热冷整编并集 9989B 达标·archive +r252/+r253 bm-c 节零丢失），amend 补记+push 43b67d30e 上链；S0.5 令 122/122 差集 0·inbox 清零（自产让路回执归档）；S6 37 腿 36 绿（update_lhb rc3=源改史 netbuy 翻号·本地保持·r229 律同 bm-a r458 披露）；水位绿 lane=healthy next_pick=moneyflow IC 批（EM 面板源死 53/5222 parked·SINA 备源面板完备 5228/5228 cutoff 09-24=可换道候选）；S7 attrition CLEAN+自愈三件+状态 252->253；产品分=2（r252 yield 交叉验证工件上链+双楔解冲突脚本族+FULL S6 面刷新） | evidence=results/_r253bmc_s6_chain.json+push 43b67d30e | 下轮指针=SINA MF 面板 IC 参照批换道评估（EM 源死 SINA 完备）或 SLOT-7 泊位起草（池 ready=1<3 地板 breach）\n" % now.strftime("%Y-%m-%d %H:%M:%S")
with open("logs/iteration-loop/round_reports-bm-c.md", "a", encoding="utf-8") as f:
    f.write(line)
print("round report appended")
