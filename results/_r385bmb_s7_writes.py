# -*- coding: utf-8 -*-
"""r385 bm-b S7 writes: state.json round_no 384->385 (CRLF, no trailing
newline preserved per r381 byte-style law) + round report line append +
heartbeat update (epoch int, clock_read T-separated)."""
import io
import json
import subprocess
import time

# --- state.json (CRLF, no trailing newline) ---
b = open("state.json", "rb").read()
assert b.count(b"\r\n") >= 3 and not b.endswith(b"\n")
s = json.loads(b.decode("utf-8"))
assert s["round_no"] == 384
s["round_no"] = 385
s["note"] = (
    "r385: maintenance+witness round (S6 33 legs rc=0 incl bm-a-stale "
    "194min takeover derives; census W2B alive-burning 5199/5620 @13:16 "
    "flush-cadence 200, ETA ~14:00+; S4 worker-tree lesson append -> "
    "CODELY 10,822B over hard line -> batch-50 reorg -> 9,315B; judge "
    "family 8 tickets still RAM-gated 1.2GB<4GB; W4-SCREEN burn in-flight "
    "bm-c)"
)
out = json.dumps(s, ensure_ascii=False, indent=1)
open("state.json", "wb").write(out.replace("\n", "\r\n").encode("utf-8"))
chk = open("state.json", "rb").read()
assert json.loads(chk.decode("utf-8"))["round_no"] == 385
assert chk.count(b"\r\n") == b.count(b"\r\n") and not chk.endswith(b"\n")
print("state.json -> round 385, byte style preserved")

# --- round report line (round_reports.md, LF) ---
rr = io.open("logs/iteration-loop/round_reports.md", encoding="utf-8").read()
assert rr.endswith("\n") and "\r\n" not in rr
now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
line = (
    f"{now} | round 385 bm-b | dept:工程/舰队 (维护+见证轮·worker 树探针正典化) | "
    "WM-VERDICT: 绿(red=false@13:10:21 lane healthy; probe 13:16 py_low_with_"
    "work_cands=合法结构占用: census W2B 活烧 5199/5620 @13:16 刷 200 条/拍 no-kill "
    "+ judge 族 8 票(W1/W2/W3+MASS x4+V2-P1)按 r354 RAM 门合法序列等待 [1.22]GB<4GB "
    "+ W4-SCREEN ready 由 bm-c autofill 烧 + 板 0 open + bandit 0 open) | did: "
    "(1) S0-1 bm-b 锚定+S0 pull --rebase up-to-date; (2) S0.5 轮首扫 99/99 零未回执"
    "+decisions.md 本机缺位零动作+inbox 空; (3) S1 smoke 25/25; (4) S2 板 0 open 全 "
    "claimed; (5) S3 常设线=W5 续挂(r162 判官漏斗 headroom 未变)+census W2B 终段见"
    "证: 12:56 flush i=4999 后 20min 无刷+父 pid 28820 单探针 cpu-idle-suspect → 树"
    "探定谳 3/4 spawn worker ~100% CPU 活烧+1 worker 分片排空=尾相常态 no-kill 零干"
    "预(r382 陈旧崩迹同族新面=父进程协调态); 13:16 flush i=5199/5620=刷节奏 200 条/"
    "拍 ETA ~14:00+ done-flip 归后续轮; (6) S6 33 腿全 rc=0(78.2s): audit "
    "pool-ready=2 / probe py_low_with_work_cands / update_daily 0 新行 cutoff "
    "09-24 盘中合法 / regime ORANGE d1 shadow(breadth 0.77 触发披露) / "
    "scorecard 6/28/7 卡=bm-a stale 194min 合法 stale-takeover derive(lane_io "
    "O-2100 s2.4 内建守卫) / MCC CALL-0924 ORANGE_COOL sleeves4 act0 / 采集器车"
    "道守卫诚实 no-op(bm-a x8+bm-c x1) / astock_daily 面板新鲜 no-op+rev_osc 幂等 "
    "no-op(本机双车道) / live_paper 锚定 OK(REGIME_GUARD enforce 请求→日期门 "
    "2026-10-01 诚实 shadow 降级)+t35v PASS 零例+t24a 22/22 drift0+t24b 0/22 / "
    "aggr+alloc+grid+sysv1 幂等守卫 no-op / t35_export 0924 / daily_scorecard+"
    "build_status=stale-takeover derive / daily_report REPORT-0928 faces=4 / "
    "token delta=0; post_review latest 12:02 今日无 NO=零 P0; (7) S4 坑律 append("
    "multiprocessing 父 idle≠停滞·worker 树探针定谳律)→CODELY 10,822B 超线→五十"
    "批当窗整编: r381+r162 两条 verbatim 迁 archive 202609.md 五十批节+指针行落位"
    "→9,315B 达标(行级零丢失校验+LF/尾行字节风格双探针保真); (8) S7: schtasks 双查"
    "在位(Loop 运行中 :02 针位+Watchdog 就绪)+register_loop pin=2 no-op+pre-commit "
    "claw CR 归一 in-sync+轮尾双扫 99/99 零差+state 385+心跳写后自证 | verify: "
    "smoke 25/25+S6 33 腿逐项 rc=0+census 树探 cpu_delta 实测+checkpoint flush 实证"
    "+五十批 verbatim 迁移断言过+orders 双扫差集空 | next: (a) census W2B finalize"
    "(~14:00+)→done-flip 单件→RAM≥4GB 三采样窗→W1/W2/W3-JUDGE+MASS x4 flips(bm-b="
    "flip executor)→autofill 续烧→finalize x5→W2/W3 intake; (b) W4-SCREEN bm-c 烧毕"
    "→screen-finalize→W4-JUDGE entry; (c) V2-P1 un-defer post-census+RAM; (d) "
    "15:30 后新 bar 窗本机双车道实弹+live.paper/t35/t24 三件套随新 bar; (e) bm-a "
    "若 15:35+ 仍静默按 MSG-1042 预案评估采集器接管; (f) CEO 48h 报告窗 09-29 22:45"
    "(bmb); marks/账本/SEED 全 +0\n"
)
io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8",
        newline="\n").write(line)
assert rr.count("\n") + 1 == sum(
    1 for _ in io.open("logs/iteration-loop/round_reports.md", encoding="utf-8"))
print("round report appended")

# --- heartbeat (fleet/machines/bm-b.json) ---
hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
raw = open("fleet/machines/bm-b.json", "rb").read()
crlf = raw.count(b"\r\n")
ps = ("[Math]::Round((Get-CimInstance Win32_OperatingSystem)"
      ".FreePhysicalMemory/1MB,2)")
free_ram = float(subprocess.check_output(
    ["powershell", "-NoProfile", "-Command", ps], text=True).strip())
ps2 = "[Math]::Round((Get-Counter '\\Processor(_Total)\\% Processor Time' -SampleInterval 2).CounterSamples[0].CookedValue,1)"
cpu_pct = float(subprocess.check_output(
    ["powershell", "-NoProfile", "-Command", ps2], text=True).strip())
ps3 = ("$g=nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits;"
       "if($g){[double]($g|Select-Object -First 1)/1024}else{0}")
gpu_free = round(float(subprocess.check_output(
    ["powershell", "-NoProfile", "-Command", ps3], text=True).strip()), 2)
epoch = int(time.time())
clock = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb.update({
    "machine_id": "bm-b",
    "last_seen": clock,
    "heartbeat_epoch_utc": epoch,
    "clock_read": clock,
    "current_task": (
        "r385 done: maintenance+witness (S6 33 legs rc=0 incl bm-a-stale "
        "194min takeover derives; S4 worker-tree lesson -> CODELY batch-50 "
        "reorg 9,315B) -> next: census W2B finalize (~14:00+, 5199/5620 "
        "@13:16) -> done-flip -> RAM>=4GB window -> judge flips W1/W2/W3+"
        "MASS x4 (bm-b executor); W4-SCREEN burn on bm-c; 15:30 new-bar "
        "window local dual lanes; CEO 48h report 09-29 22:45"
    ),
    "cpu_cores": 16,
    "free_ram_gb": free_ram,
    "gpu_free_vram_gb": gpu_free,
    "total_ram_gb": 23.92,
    "cpu_util_pct": cpu_pct,
    "round_no": 385,
    "verdict": (
        "healthy: smoke 25/25, orders 99/99 dual-scan clean, S6 33 legs "
        "rc=0 (bm-a hb stale 194min -> lane_io stale-takeover derives "
        "lawful O-2100 s2.4, bm-a rewrites on revival); census W2B "
        "alive-burning verified by worker-tree probe (3/4 workers ~100% "
        "CPU; parent-idle = coordinator norm; 5199/5620 @13:16, flush "
        "cadence 200/beat, ETA ~14:00+) final-stretch no-kill; W4-SCREEN "
        "ready, burn in-flight on bm-c autofill; judge family W1/W2/W3+"
        "MASS x4+V2-P1 all RAM r354 gated lawful serialization "
        "[1.22]GB<4GB; W5 stays parked (judge funnel headroom unchanged); "
        "board 0 open; post_review 0 latest-NO; CODELY 9,315B after "
        "batch-50 reorg"
    ),
})
out = json.dumps(hb, ensure_ascii=False, indent=1)
open("fleet/machines/bm-b.json", "wb").write(
    out.replace("\n", "\r\n").encode("utf-8"))
j2 = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
ep = j2["heartbeat_epoch_utc"]
assert isinstance(ep, int) and not isinstance(ep, bool), "epoch must be int"
assert "T" in j2["clock_read"] and j2["clock_read"].endswith("+08:00")
assert j2["round_no"] == 385
print(f"heartbeat written: epoch={ep}(int) clock={clock} "
      f"ram={free_ram}GB cpu={cpu_pct}% gpu={gpu_free}GB "
      f"crlf_style={'preserved' if open('fleet/machines/bm-b.json','rb').read().count(chr(13).encode()+chr(10).encode())==crlf else 'CHANGED'}")
