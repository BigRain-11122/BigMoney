"""r366 bm-b closeout writes: round-report line + state bump + T-96
progress_r366 + heartbeat refresh. Binary-safe single-pass, LF blood
per file (round_reports.md is i/mixed -- append LF line, no rewrites)."""
import io
import json
import time

NOW = "2026-09-28T07:44:00+08:00"

REPORT = "logs/iteration-loop/round_reports.md"
line = (
    "2026-09-28T07:44:00+08:00 | round 366 bm-b | dept:策略/研究 (T-96 W2 intake slice) "
    "| WM-VERDICT: GREEN (red=false@07:20 lane healthy; py_low_with_work_cands=合法解释: "
    "census W2B 4-worker 结构面 ~25% py 上限 + 全部判决翻转 RAM r354 三采样>=4GB 门合法持有, "
    "板空 bandit 空, 零违令) | did: (1) S0-1 bm-b 锚定 + S0 pull --rebase 落地 HEAD 694d0a0a, "
    "轮首脏 p1d_gates.json=车道件不吞(定向 add 律); (2) S0.5 令差集 99/99 零未回执 + "
    "decisions.md 不存在零动作 + inbox MSG-0725=自发件留窗待他机; (3) smoke 25/25; "
    "(4) T-96 slice-5 INTAKE LANDED (r362 续作点 d): cmd_intake + _d6_admit_core + "
    "_trial_intake_rows (D6 绑定门 0.7/注册克隆拒收/簇内塌缩留 DSR 最高平手最低 id/"
    "TRIAL-<FAMILY>-<NN>=策略模块 per §4 PBO family 定义/零存活合法面/audit 段全量) + "
    "selftest 58->63/63 (5 新 hermetic 腿) + dispatch intake 接线; "
    "(5) **W1 血统 D6 死路面真 bug 被 [18] hermetic 腿抓出**: registered-corr>=0.7 拒收 "
    "判词从未被执行 (eliminated 只收簇内 loser, rejected 构造的 registered-corr 分支 "
    "只对簇内 loser 可达=死路面; 注册克隆可直入 admitted), W1 judge 仍在池 waiting="
    "零判读污染, 双波跑前同修 (trial_labor_w1.py cmd_intake + trial_labor_w2.py "
    "_d6_admit_core registered-outright-eliminate 前置); (6) SIGNAL_BUILDERS 镜像错 "
    "(tl1 属性误写)=真数据探针连环撞#1 修毕(函数内 import=W1 先例字面), registered-six "
    "重算面真数据探针 rc=0 (6/6 尾==cutoff 2026-09-22, 6.6s); (7) 双跑 stdout 字节恒等 "
    "rc=0 (stderr=scipy Sobol 平衡警告既有良性面); (8) census W2B ETA 勘误: MSG-0725 "
    "10:30 过乐观——块级 checkpoint BLOCK=200 每块一跳(~26min) 非停滞, 实测均速 7.6 行/min "
    "(1600 行/3.53h, i 至 1799=块乱序合法), 剩 4020 -> 诚实 ETA ~16:20, worker 4x~95% "
    "CPU 活跃, 自由 RAM 1.17GB; (9) CODELY r366 坑律入册(镜像先例须锚判词非字面+块级 "
    "cadence 误诊) 水位 10,052B 超线 -> 当窗整编三十五批(4 条 verbatim 入 archive "
    "202609.md, 7,017B 回线, 行级零丢失校验); (10) S6 26 腿全 rc=0(bm-a 守卫面合法 "
    "stale-takeover x3: t35_open_fill_verify/daily_scorecard/build_status, bm-a 心跳 "
    "27min 过期 O-2100 s2.4 律); (11) S7 双扫零新增令零沉没 | verified: selftest 63/63 "
    "+ W1 selftest 19/19 + CLI intake 门诚实 rc=2 + 探针 rc=0 + S6 26xrc=0 + schtasks "
    "双任务在位 pin=2 + pre-commit claw no-op | next: (a) census W2B finalize 守望 "
    "(ETA ~16:20) -> done-flip -> RAM 窗 -> W1-JUDGE/MASS x4/W2-JUDGE 翻转 (bm-b 轮="
    "flip executor); (b) W2 judge 落地 -> judge-finalize -> intake 实弹首跑 (唯一未探面="
    "checkpoint 行 join, [16] 腿已覆形); (c) C 族 §9.2 append-confirm (W2B finalize 后) "
    "| T-96 progress_r366 landed\n")

with io.open(REPORT, "ab") as f:
    f.write(line.encode("utf-8"))

# state.json bump (LF blood, atomic single write)
s = json.load(io.open("state.json", encoding="utf-8"))
s["round_no"] = 366
s["note"] = ("r366 bm-b: T-96 slice-5 intake landed (D6 binding gate + W1-lineage "
             "dead-path bug caught by hermetic leg, dual-wave pre-run fix); census "
             "W2B honest ETA ~16:20 (block-cadence law, MSG-0725 correction)")
b = (json.dumps(s, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
io.open("state.json", "wb").write(b)

# T-96 ticket progress_r366
tp = "fleet/tasks/T-2026-09-28-96-P1.json"
t = json.load(io.open(tp, encoding="utf-8"))
assert t["id"] == "T-2026-09-28-96" and t.get("status") == "claimed"
t["progress_r366"] = (
    "r366 bm-b SLICE-5 INTAKE LANDED (post-census build window, r362 next-step d): "
    "scripts/trial_labor_w2.py cmd_intake + _d6_admit_core (pure, hermetic) + "
    "_trial_intake_rows -- prereg sec.4 s4 face: D6 binding gate ceiling 0.7 "
    "(registered-corr outright reject + survivor-cluster collapse keep highest DSR, "
    "tie lowest candidate_id), candidate daily returns from judge checkpoint rows "
    "(engine face, stop overlay included; w2_judge.json cells stripped by design), "
    "registered six = engine recompute at registered config cutoff-truncated-first "
    "(r363 law), TRIAL-<FAMILY>-<NN> per-module counter (family=strategy module per "
    "sec.4 PBO definition), lawful-zero face + audit segment; selftest 58->63/63 "
    "(5 new [18] legs) + subprocess double-run byte-identical + CLI intake gate "
    "honest rc=2 + registered-six real-data probe rc=0 (6/6 tail==cutoff 6.6s). "
    "**W1-lineage D6 dead-path bug caught by the hermetic leg**: W1 cmd_intake "
    "registered-corr>=0.7 reject was never enforced (eliminated collects cluster "
    "losers only; the rejected-list registered-corr branch is unreachable for "
    "non-cluster candidates = registered clone could sail into admitted) -- W1 "
    "judge still pool-waiting = zero judged cells consumed by the buggy path; "
    "dual-wave pre-run fix landed same round (trial_labor_w1.py cmd_intake "
    "mirrored). Pitlaw r366 in CODELY (mirror-assert-prereg-semantics-not-"
    "precedent-literal + census BLOCK=200 cadence misdiagnosis note). Census W2B "
    "honest ETA correction: ~16:20 (block-cadence 200/flush, avg 7.6 rows/min, "
    "MSG-0725 ~10:30 was optimistic). Next: judge-finalize -> intake live first "
    "fire (only unprobed face = checkpoint row join, shape-covered by [16]); "
    "CODELY r366 entry + batch-35 archival consumed.")
t["progress_r366_ts"] = "2026-09-28 07:44"
b = json.dumps(t, ensure_ascii=False, indent=1).encode("utf-8")
if not b.endswith(b"\n"):
    b += b"\n"
io.open(tp, "wb").write(b)

# heartbeat bm-b (LF blood; epoch MUST be JSON int; clock_read T-separated)
epoch = int(time.time())
clock = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
h = json.load(io.open("fleet/machines/bm-b.json", encoding="utf-8"))
h["last_seen"] = clock
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = clock
h["current_task"] = ("r366: T-96 slice-5 intake landed + W1 D6 dead-path bug "
                     "dual-wave pre-run fix (hermetic-leg catch); census W2B "
                     "honest ETA ~16:20 (block cadence, MSG-0725 correction); "
                     "next = census finalize watch -> RAM window -> W1-JUDGE/MASS "
                     "x4/W2-JUDGE flips (bm-b = flip executor) -> intake live fire")
h["round_no"] = 366
h["verdict"] = ("healthy: smoke 25/25, W2 selftest 63/63 + W1 19/19, S6 26 legs "
                "rc=0, intake CLI gate honest rc=2, census W2B 1600/5620 burning "
                "(4 workers ~95% CPU), free RAM 1.17GB (all flips RAM-gated lawful)")
h["orders_ack"] = h.get("orders_ack", [])
h["n_orders_ack"] = len(h["orders_ack"])
h["round"] = 366
h["loop_round"] = 366
b = json.dumps(h, ensure_ascii=False, indent=1).encode("utf-8")
if not b.endswith(b"\n"):
    b += b"\n"
io.open("fleet/machines/bm-b.json", "wb").write(b)

# self-verify (R170/R178 dual law: value AND type)
chk = json.load(io.open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock T-separated"
print("closeout writes OK; epoch", chk["heartbeat_epoch_utc"],
      "clock", chk["clock_read"], "round", chk["round_no"])
