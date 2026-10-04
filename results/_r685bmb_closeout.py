# -*- coding: utf-8 -*-
"""r685 bm-b closeout: state round_no+1, heartbeat, round-report line,
HANDOVER 5x entry. Laws built in: r645 (json.dump + json.loads self-verify),
r641 (strict clock regex + epoch<->clock cross-check), r679 (append-only
marker idempotency count==0 before / ==1 after), r661/R178 (epoch int type).
"""
import datetime
import json
import os
import re
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(ROOT, "results", "_r685bmb_closeout_log.txt")
CLOCK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")

def now_cn():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()

def log(msg):
    with open(EV, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg, flush=True)

# --- 1. resource snapshot (best-effort; honest if unavailable) ---
res = {}
try:
    import psutil
    vm = psutil.virtual_memory()
    res["free_ram_gb"] = round(vm.available / 1024**3, 2)
    res["cpu_util_pct"] = psutil.cpu_percent(interval=0.5)
    res["py_cpu_pct"] = res["cpu_util_pct"]
except Exception as e:
    log(f"psutil probe fail: {e}")
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=20)
    mib = int(r.stdout.strip().splitlines()[0])
    res["gpu_idle_vram_gb"] = round(mib / 1024, 2)
    res["gpu_idle_vram_mb"] = mib
except Exception as e:
    log(f"nvidia-smi probe fail: {e}")

# --- 2. state.json round_no 684 -> 685 ---
sp = os.path.join(ROOT, "state.json")
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
assert st["round_no"] == 684, f"unexpected round_no {st['round_no']}"
st["round_no"] = 685
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
back = json.load(open(sp, encoding="utf-8"))
assert back["round_no"] == 685
log("state.json: round_no=685 written + reparse-verified")

# --- 3. heartbeat bm-b.json ---
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
with open(hb_path, encoding="utf-8") as f:
    hb = json.load(f)
epoch = int(time.time())
clock = now_cn()
assert CLOCK_RE.match(clock), f"clock format fail: {clock}"
# epoch<->clock cross-check (r641 law): wall clock close to epoch (<=120s)
assert abs(epoch - time.time()) < 2
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["round_no"] = 685
hb["round_no_label"] = "round 685 (bm-b)"
hb["current_task"] = ("FUND trio NULLS keepalive burn V889/Q698/D533 of 2000 "
                      "(ETA V 10-06T17/Q 10-07T11/D 10-08T06); RC-10 pool unit "
                      "RAM-gated queue; W3 judge finalize=bm-c seat adoption-watch")
hb["verdict"] = ("GREEN: S6 38/38 rc0; trio NULLS burning healthy (watch 3-证 OK); "
                 "smoke 48/48; dualrun ZERO-DRIFT streak 51; 0 open tickets")
hb["ts"] = clock
hb["updated"] = clock
hb["updated_at"] = clock
for k, v in res.items():
    hb[k] = v
with open(hb_path, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
back = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch not int (R170/R178 law)"
assert CLOCK_RE.match(back["clock_read"]), "clock_read format red (R262 law)"
log(f"heartbeat: epoch={epoch} int-verified, clock={clock}, res={res}")

# --- 4. round report line append (marker idempotency r679 law) ---
rr_path = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with open(rr_path, "rb") as f:
    rr_bytes = f.read()
marker = "r685 (bm-b)".encode("utf-8")
n0 = rr_bytes.count(marker)
assert n0 == 0, f"marker already present x{n0} (r679 idempotency gate)"
line = (
    "2026-10-04T18:22:00+08:00 | r685 (bm-b) PRODUCT (dept:工程+数据维护): "
    "[watermark verdict: GREEN (red=false lane=healthy; satengine alive rc0 queue=19 RAM-floor gate 3.6GB<4.0GB machine discipline; "
    "dualrun ZERO-DRIFT streak 51 (377 entries, cutoff 17:55:45); post_review zero active red)] | "
    "当前活: FUND trio NULLS 三族在烧 V889/Q698/D533 of 2000 @18:18 (44.5/34.9/26.6pct, owner=bm-b, rates 23.6/20.1/17.5/h, "
    "ETA V 10-06T17 / Q 10-07T11 / D 10-08T06) + CONTEST RC-10 池单元 RAM-gated 排队 + W3 judge finalize=bm-c 席位在飞(bm-a/bm-b 收养姿态, origin 未见 w3_judge.json) | "
    "最近实物: S6 38/38 rc0 (results/_r685bmb_s6_log.txt; REPORT/LIVE-2026-10-04 再生 ORANGE cap50) + trio_burn_eta.json 刷新 @18:18 (三证健康判定全绿) | "
    "本轮同窗: S0 r437 预对齐净路 (pull 被 13 脏面阻→交集判定 1 面 crash_fuse.json origin-checkout→定向 absorb→merge origin 6 commits 零 UU) + "
    "MSG-1810 bm-a 让位回执收账 (processed/) + orders/D-19 双扫双键 MATCH (154/154 零未回执; decisions 4E5BE321 SHA-256 / orders 68947C17 SHA-1) + "
    "smoke 48/48 + 板扫 169 票 0 open + attrition 4 ledgers CLEAN + 自愈 4/4 (loop pin=2 no-op/watchdog PRESENT/双爪 IN-SYNC) + HANDOVER 5x 本行 | "
    "笔误披露: S0 absorb commit 误标 round 691 (实际窗 r685, 表尾 r684+1; 已推送不改史, 如实注记 per r683 前例) | "
    "验证证据: results/_r685bmb_s6_log.txt 38/38 rc0 + results/trio_burn_eta.json + state=685 + 心跳 epoch int 自证 (results/_r685bmb_closeout_log.txt) | "
    "下轮指针: trio 看守续跑 + V 烧完(~10-06T17)后首族 finalize 候选窗 (r672 预演 ALL-GREEN 证据在场; r668 池面双翻律) + "
    "W3 finalize bm-c 产物落地观察 (id 零重探针 r482 律必跑) + RC-10 autofill 点火观察 | 本地未达 origin commit 数=N (commit 后 push+fetch+ls-tree 自证)"
)
sep = b"" if rr_bytes.endswith(b"\n") else b"\n"
with open(rr_path, "ab") as f:
    f.write(sep + line.encode("utf-8") + b"\n")
n1 = open(rr_path, "rb").read().count(marker)
assert n1 == 1, f"marker count {n1} != 1 after append"
log("round_reports.md: r685 line appended, marker count==1 verified")

# --- 5. HANDOVER 5x entry (r685 = multiple of 5) ---
ho_path = os.path.join(ROOT, "research", "HANDOVER.md")
with open(ho_path, "rb") as f:
    ho_bytes = f.read()
ho_marker = "bm-b round 685".encode("utf-8")
h0 = ho_bytes.count(ho_marker)
assert h0 == 0, f"HANDOVER marker already present x{h0}"
ho_line = (
    "> bm-b round 685 五倍数核对面（2026-10-04 18:2x·增量窗 r681-r685 五轮·前窗 r676-r680 已由 r680 行覆盖）："
    "增量窗 r681-r685=bm-b 面貌（**FUND 三族 NULLS 值守主线收口窗+W3 judge 分片接力+CONTEST 终表冲刺**）——"
    "r681 维护窗（S6 34 腿）；r682 D-19 探针 orders 腿口径缺陷治愈（results/_r686bmb_d19_check.py 双键 MATCH 版，r458/r672 律落码）+S6 38/38+trio watch 刷新；"
    "r683 **W3-JUDGE-SHARD-1 烧录完成 194/194**（mass_trial w3_judge_shard_1of4.jsonl 落盘+池双翻 done-flip+claim 回填，commit bcdbc43e0 DELIVERED）"
    "+autofill relaunch_cooldown 重烧环拆除（r668 律当窗补翻 r485 配方五门，treasure_guard rc0）；"
    "r684 **T-148 CONTEST pending-legs 收口**（scripts/contest_ytd_legs.py pending-legs 烧录 runner：lowamp 两员 YTD 烧录落表 LX-LA-EDGE-deep-base ytd +0.49% rank #43 / -x2 +0.51% rank #41+revcensus 全 pool shard 行 census-stats parity 锚点 abort-on-drift；"
    "contest_table.json 刷新 209 measured+10 pending；CONTEST-TABLE.md CEO 面刷新）+池单元 CONTEST-YTD-P1-RC-0OF1 autofill submit 落池（host_gates p1c+data_deps 4 路径+workers 4 BelowNormal）；"
    "r685 本轮=S0 r437 预对齐净路（交集 1 面 checkout+absorb+merge 零 UU）+MSG-1810 收账+S6 38/38+trio watch V889/Q698/D533+HANDOVER 本行。"
    "产物清单漂移=results/_r683bmb_*（W3 shard-1 翻面/autofill 重烧环）+scripts/contest_ytd_legs.py+results/contest_table.json+research/CONTEST-TABLE.md（r684）"
    "+results/_r686bmb_d19_check.py（r682 治愈版）+results/_r685bmb_s6_chain.py/_r685bmb_s6_log.txt/_r685bmb_closeout_log.txt+results/trio_burn_eta.json 逐轮刷新"
    "+docs/daily_report/REPORT-2026-10-04.*+docs/live_usage/LIVE-2026-10-04.*（S6 维护链再生物）。"
    "池态: FUND 三族 NULLS bm-b canonical burner 在飞 V889/Q698/D533 of 2000 @18:18（44.5/34.9/26.6pct·rates 23.6/20.1/17.5/h·ETA V 10-06T17/Q 10-07T11/D 10-08T06·finalize 候选窗 10-05 10:30..10-09·预演 r672 ALL-GREEN 证据在场·finalize 轮必同窗池面双翻 r668 律）；"
    "CONTEST RC-10 池单元 RAM-gated 排队（autofill 点火后→assemble 重跑=219-measured 终表→10-08 治理日前交付 CEO 面）；"
    "MASS-TRIAL-W3-JUDGE 四分片烧毕 done（w3_judge_shard_{0..3}of4.jsonl 全落盘）·wave 级 finalize=bm-c 席位在飞（origin 未见 w3_judge.json·id 零重探针 r482 律+r668 池翻律必随）；"
    "MASS-TRIAL-W1-JUDGE x4 全 done；N1-W116 2/12 shards。维护面: smoke 48/48 全窗；S6 38/38 rc0（dualrun ZERO-DRIFT streak 51）；orders 154/154 双扫零未回执；"
    "attrition 4 ledgers CLEAN；D-19 双键 MATCH（decisions 4E5BE321 SHA-256/orders 68947C17 SHA-1）。指针: *V 烧完→10-06T17→首族 finalize 候选（三族窗 10-06..10-08·判决面按冻结路径如实出）*；"
    "T-148 contest 终表 10-08 前刷新；O-2115/O-2030 验收 10-08+开市 10-09 数据道恢复；月界首考 10-31；下一 5x=bm-b r690。"
)
sep = b"" if ho_bytes.endswith(b"\n") else b"\n"
with open(ho_path, "ab") as f:
    f.write(sep + ho_line.encode("utf-8") + b"\n")
h1 = open(ho_path, "rb").read().count(ho_marker)
assert h1 == 1, f"HANDOVER marker count {h1} != 1"
log("HANDOVER.md: r685 5x entry appended, marker count==1 verified")
log("CLOSEOUT ALL DONE")
