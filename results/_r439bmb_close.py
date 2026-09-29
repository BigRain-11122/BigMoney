# -*- coding: utf-8 -*-
# r439 bm-b round closeout: round report line + state.json + heartbeat.
import json
import time
import io
import re

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_LOCAL = time.strftime("%Y-%m-%d %H:%M:%S")

REPORT_LINE = (
    NOW + " | r439 | dept:策略+研究 joint (W10 漏斗推进·T-122) | "
    "WM-VERDICT: 绿 red=false @19:47 probe (py_low_with_work_cands 合法=local_batch_running=true W10 烧批在飞·audit supply_floor 旗如实=池饿面 W10 波即供给正在烧) | "
    "当前活: TRIAL-LABOR-W10-JUDGE 池条目 ready 283 格判决批待点火 | "
    "最近实物: results/trial_labor_w10/w10_screen.json @19:54 finalize (null p95 0.5164 带内·存活 283/2014=14.05%·RESEARCH FACT: MOM 门 1.88x 富集 oversold 19.97% vs none 10.64%=正轴发现·W9 AMP 反富集反面) | "
    "下个里程碑: W10-JUDGE 判决面烧批+judge-finalize (~40min 烧·下轮/autofill 承接 finalize→48h CEO 呈报钟起算·窗≤48h) | "
    "did: S0 fetch 零远端增量@轮首(后 bm-c r235 同窗入)→S0.5 令差集 122/122 零未回执+decisions.md 全树不存在零动作如实→S1 smoke 26/26→S3 W10 全漏斗单轮推进: GENERATE 收成遗产先落地 (n=2014 raw5000→dedup2014 低于 [2600,4600] 带下沿=预注册可证伪面如实·fp塌缩2410+corr塌缩3619·mom面 oversold736/none1278·sha16 e21c7eb83087035c·elapsed 646.4s 零引擎) →池双面翻 done+SCREEN 条目同 commit (2214 格) →手动 tick 点火 pid6200 19:47:02 → ckpt 2,214/2,214 完成 19:54 → screen-finalize 落地 (null p95 0.5164 IN [0.50,0.52]·存活 283=14.05%·MOM 分段富集 1.88x=正轴发现 vs W9 AMP 反富集·八门交互面落盘·账本 346,270 live-head 对账 OK) → judge-prep PASS (manifest 48·census L/D 冻结·G-MOM 153/1339/1492 warmup139) → JUDGE 条目同 commit 提交 (283 格·RAM r354 三采样过·host_gates MSG-1305·lane_owner=bm-b) → S6 33 腿 rc=0 (dualrun ZERO-DRIFT streak 25/3·09-29 bar 源未出=klc2 ~21:00 夜发 bm-c r235 定谳结构面第3轮如实 no-op→live.paper/t35/t24 触发门合法跳过·REPORT/LIVE-0929 再生·token delta=0) → S7 push 撞 bm-c r235 → rebase 重放 17 件 UU=13 分类+4 UNKNOWN(LIVE-*) → 正典解 (快照族全取新=bmb 侧 S6 晚跑·compute_audit history union 201+201→202 零丢失·LIVE-*/REPORT/js 孪生同侧·deep-ts probe r100/R350 加固) → push 通 12f365714..ccd807115 → 分类器 LIVE-* 家族补丁 (UNKNOWN 缺口结构性根治·selftest 26/26 ALL GREEN) | "
    "verify: screen ckpt 2,214/2,214 行实读+finalize stdout 读数逐项+账本 346,270 与 bm-c r235 定谳 (W9 344,031→A158-FV+9→A10+16=344,056) 交叉对账吻合+audit union 202=|A∪B| 零丢失校验+dualrun streak 25/3+smoke 26/26+push 12f365714..ccd807115 PASS+classifier selftest 26/26 | "
    "next: 收尾即手动 tick 点火 W10-JUDGE 烧批 → judge-finalize=下轮工作面 (48h CEO 呈报钟起算) → intake→W11 参考带喂给 [via bm-b]"
)

with io.open(r"logs/iteration-loop/round_reports.md", "a", encoding="utf-8",
             newline="") as f:
    f.write(REPORT_LINE + "\n")
print("round report appended r439")

# --- state.json ---
st = json.load(io.open("state.json", encoding="utf-8"))
st["round_no"] = 439
st["note"] = ("r439: W10 funnel full advance single round -- GENERATE harvest "
              "n=2014 landed+committed -> pool dual-face done -> SCREEN entry "
              "submitted same commit -> manual tick pid6200 19:47:02 -> "
              "2,214/2,214 ckpt complete 19:54 -> screen-finalize LANDED "
              "(null p95 0.5164 IN band, survivors 283/2,014=14.05%, MOM "
              "1.88x ENRICHMENT positive-axis finding, ledger 346,270 "
              "reconcile OK) -> judge-prep PASS -> TRIAL-LABOR-W10-JUDGE "
              "entry submitted same commit (283 cells, RAM+host_gates "
              "MSG-1305, lane_owner=bm-b); S6 33 legs rc=0; push collided "
              "bm-c r235 -> rebase canon-resolved 17 UU (snapshot take-new "
              "bmb-side later-run + audit union 202 zero-loss + LIVE-* "
              "UNKNOWN manual adjudication formalized into classifier "
              "selftest 26/26); JUDGE ignition = closing manual tick")
st["last_round_at"] = NOW
st["last_round_ts"] = "r439"
st["ts"] = NOW
st["updated"] = NOW
with io.open("state.json", "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state.json -> r439")

# --- heartbeat fleet/machines/bm-b.json ---
import psutil
vm = psutil.virtual_memory()
idle_ram_gb = round(vm.available / 1024**3, 1)
cores = psutil.cpu_count(logical=True)
gpu_free_vram_mb = None
try:
    out = __import__("subprocess").run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=10)
    if out.returncode == 0 and out.stdout.strip():
        gpu_free_vram_mb = int(float(out.stdout.strip().splitlines()[0]))
except Exception:
    gpu_free_vram_mb = None

hb = json.load(io.open(r"fleet/machines/bm-b.json", encoding="utf-8"))
hb["last_seen"] = NOW_LOCAL
hb["current_task"] = ("W10-JUDGE pool entry ready 283 cells (T-122); "
                      "ignition = closing manual tick; judge-finalize next "
                      "round")
hb["cpu_cores"] = cores
hb["idle_ram_gb"] = idle_ram_gb
hb["gpu_free_vram_mb"] = gpu_free_vram_mb
hb["verdict"] = "healthy"
epoch = int(time.time())
assert isinstance(epoch, int)
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = NOW
with io.open(r"fleet/machines/bm-b.json", "w", encoding="utf-8",
             newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk = json.load(io.open(r"fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("heartbeat written epoch=%d idle_ram=%.1fGB gpu_free=%sMB"
      % (epoch, idle_ram_gb, gpu_free_vram_mb))
