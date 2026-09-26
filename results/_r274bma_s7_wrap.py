# -*- coding: utf-8 -*-
"""R274 bm-a S7: state + heartbeat + round-report write-back (single now() per R271 law)."""
import json, subprocess, time
from datetime import datetime

now = datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M")
iso = now.astimezone().isoformat()
epoch = int(time.time())

def ps(cmd):
    return subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                          capture_output=True, text=True).stdout.strip()

cpu_pct = ps("(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average")
free_ram = ps("[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)")
vram = ps("nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits")
try:
    cpu_pct = float(cpu_pct)
except Exception:
    cpu_pct = 0.0
try:
    free_ram = float(free_ram)
except Exception:
    free_ram = 0.0
try:
    vram_gb = round(float(vram.splitlines()[0]) / 1024.0, 1)
except Exception:
    vram_gb = 0.0

# ---- state-bm-a.json (indent=1 face, no trailing newline) ----
sp = "state-bm-a.json"
sraw = open(sp, "rb").read()
st = json.loads(sraw.decode("utf-8"))
st["round_no"] = 274
st["did"] = ("R274 unattended maintenance+T-84 doc-lane round: s1 re-probe D:/ still absent (physical hold continues, sole legal deferral); "
             "s3 DELIVERED research/V60_LESSONS_INTAKE.md (funnel-vs-stack 6-layer isomorphism table -> G1'v2/D2/DSR+PBO/regime/D5/D6 + frozen-line vs "
             "20->30pct relaxation philosophy divergence; Top3 triplet-collapse dedup-gate lesson + recipe for selection/tournament preregs, template wiring "
             "reserved GM sign+7-day veto; trend-as-king four-source convergence = priority weight zero admission credit); s4 DELIVERED research/V60_ASSET_MERGE.md "
             "(8-row merge list to CEO, two CEO physical items: D:/Money re-mount-or-TRANSFER-planA-or-lane-handover + System B assets via git-branch/croc; "
             "supply face = LHB/moneyflow/THS collectors ready); CODELY.md pitfall entry appended (dedup-gate lesson); orders 85/85 canonical diff empty "
             "(double-scan round open+close); decisions tail D-20260926-11 unchanged zero new BigMoney rows (D-10 IntradayMarks E2 closed by HQ per adjudication, "
             "zero BigMoney action); smoke 25/25; S6 28 legs rc=0 weekend no-op family (moneyflow rank spawn + AH refresh in 30-min throttle windows from r273)")
st["verdict"] = ("R274: watermark GREEN (red=false, py_low_board_clear weekend legal-idle: open 0/bandit 0/pool 0; pool_starvation flag same face = "
                 "legal-idle whitelist, T-84 held on physical D: dependency not computable-lane), smoke 25/25, S6 28x rc=0, "
                 "T-84 s3/s4 legislation-committed (acceptance = next post_review), s1/s2 blocked on physical dependency")
st["next"] = ("09-28 next trading-bar chain (Monday paper/prospect/t35 legs fire), T-84: D: volume return -> auto-resume s1->s2; CEO physical items pending "
              "(D:/Money + System B transfer), migration executor supervised (window to 09-29 12:00), 10-01 month-first round chain (science_audit+briefing+"
              "self_review+REGIME_GUARD v3 date gate), MF_IC_P1 on panel recovery (rank spawn + AH refresh in throttle windows)")
for k in ("ts", "last_round_ts", "updated_at", "last_run", "last_round_at", "updated"):
    st[k] = ts
st["last_round"] = 274
st["current_task"] = ("T-84 v6.0 convergence: s3+s4 delivered R274 (V60_LESSONS_INTAKE + V60_ASSET_MERGE); s1/s2 held on D:/Money physical dependency; "
                      "MF_IC_P1 on panel recovery")
open(sp, "wb").write(json.dumps(st, ensure_ascii=False, indent=1).encode("utf-8"))

# ---- heartbeat fleet/machines/bm-a.json ----
hp = "fleet/machines/bm-a.json"
hraw = open(hp, "rb").read()
h = json.loads(hraw.decode("utf-8"))
h["last_seen"] = ts
h["current_task"] = st["current_task"]
h["cpu_pct"] = cpu_pct
h["free_ram_gb"] = free_ram
h["gpu_free_vram_gb"] = vram_gb
h["verdict"] = st["verdict"]
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
h["round_no"] = 274
h["idle_ram_gb"] = round(free_ram, 1)
open(hp, "wb").write(json.dumps(h, ensure_ascii=False, indent=1).encode("utf-8"))

# self-verify epoch int + clock T-sep (smoke F7 face)
h2 = json.loads(open(hp, "rb").read().decode("utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in h2["clock_read"], "clock_read must be T-separated"
assert abs(int(time.time()) - h2["heartbeat_epoch_utc"]) < 120
print("heartbeat ok: epoch int", h2["heartbeat_epoch_utc"], "clock", h2["clock_read"])

# ---- round report append (CRLF, no trailing newline at EOF) ----
rp = "logs/iteration-loop/round_reports-bm-a.md"
rb = open(rp, "rb").read()
line = (
    f"{ts} | R274 | bm-a dept:研究·总经办（T-84 s3/s4 车道·doc-basis 不受 D: 挂起影响）| "
    f"水位 GREEN（py_low_board_clear 周末合法 idle：open 0/bandit 0/pool 0；compute_audit pool_starvation 旗同面=合法白名单——T-84 挂起为 D: 物理依赖非算力可解车道）| "
    f"①S0.5 双扫：orders 85/85 canonical diff empty、decisions 尾 D-20260926-11 零新行（D-10 拍板=IntradayMarks E2 HQ 闭口，本司零动作；D-11 计数修正=HQ 轮，非本司例）| "
    f"②T-84 s3 交付 research/V60_LESSONS_INTAKE.md：漏斗六层 vs 我方栈同构对照表（L1 基础→G1'v2 null 校准线/L2 OOS→D2 前向锁+锚定门〔Sharpe 5.89 与 dd −32.63% 内部矛盾面在我方 D2+锚定门下结构性不可达〕/L3 过拟合→DSR0.95+族 PBO0.25+D1 多重性账/L4 政体→政体分层但反哲学〔其 20→30% 放松 vs 我方判线冻结律〕/L5 成本→D5 v2/L6 相关→D6）；Top3 三胞胎塌缩=去重缺陷非同质化——D6 批前面拦不住批内筛选后坍缩，配方=排名前持仓 sha256 指纹+两两 |corr|≥0.999 塌缩一格+诚实 dedup 披露（禁转译收敛叙事），模板接线留 GM 署名+7 天否决窗；唯趋势存活=四源互证记研究优先级权重（T-57 nulls −1.18/A158 判负/社区 2017 衰减/其 v6.0 异源同向），其宣称零入册信用| "
    f"③T-84 s4 交付 research/V60_ASSET_MERGE.md：8 行归并清单呈 CEO（A 线受阻 D:/、B 漏斗教训已落地、供给面三采集器在位、v5 愿景入候选、纪律互证）+CEO 待办两物理件（D:/Money 三径：重挂/TRANSFER 方案A/车道移交；System B 资产 git 分支或 croc）| "
    f"④票面 progress_r274 写回（五面探测+separator 误配首写 14+/13- 自捕→默认 separators 修正 2+/1- 纯字段增量）+CODELY.md 坑律条目（dedup 门教训·33.8KB<50KB 免整编）| "
    f"⑤smoke 25/25；S6 28 腿全 rc=0 周末 no-op 族（update_daily 0 新行 cutoff 09-24、market_clock CALL-2026-09-24 cell=ORANGE_COOL activated=0、moneyflow rank spawn+AH refresh 在 r273 起算 30min 节流窗内、fund_premium bm-c 车道诚实 no-op、B 层掩码再生 all_pass）| "
    f"证据: 两 research 交付件+票面 2+/1- diff+commit 链+CODELY 追加+S6 各腿 rc=0 实录 | "
    f"下轮: D: 卷回归即自动续 s1→s2；CEO 两物理件待办；09-28 新 bar 链；10-01 月首轮三件套+REGIME_GUARD v3 日期门 [via bm-a]"
)
if rb.endswith(b"\r\n") or rb.endswith(b"\n"):
    open(rp, "ab").write(line.encode("utf-8") + b"\r\n")
else:
    open(rp, "ab").write(b"\r\n" + line.encode("utf-8"))
print("round report appended")
print("done", ts)
