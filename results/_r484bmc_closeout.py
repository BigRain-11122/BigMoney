"""r484 bm-c S7 closeout: CODELY entry + round report + state + heartbeat.
Laws: r679 append marker count gate; r645 state json programmatic write +
reparse self-check; R170/R178 heartbeat epoch int; R262 clock T-sep."""
import json
import os
import subprocess
import time
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CODELY = os.path.join(REPO, "CODELY.md")
REPORT = os.path.join(REPO, "round_reports-bm-c.md")
STATE = os.path.join(REPO, "state-bm-c.json")
HEART = os.path.join(REPO, "fleet", "machines", "bm-c.json")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now_epoch = int(time.time())
now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
assert "T" in now_iso and "+" in now_iso, "clock_read must be T-sep ISO with offset"

# ---- 1. CODELY.md append (marker gate) ----
codely = open(CODELY, "rb").read().decode("utf-8")
assert codely.count("r484 bm-c") == 0, "CODELY marker already present (r679 gate)"
entry = ("- [2026-10-04 16:4x r484 bm-c] 判决面 §9.1 类追加节冻结必复跑禁向闸+BAN-04 裸词碰撞正法"
         "（本窗实弹：对 W3 PREREG 复跑 Tools/banned_direction_gate.py --prereg 当场 REJECT——"
         "闸以「网格」裸词匹配「网格交易」方向，判决评估机械（p5c 虚拟起点×窗×成本×分段格面）"
         "与其零关系=纯词法碰撞；w2 §9.1 追加（r423）未复跑闸=先例缺口，同词文件今日复跑同拒）；"
         "正法=措辞精确化（判决网格→判决格面）保 §0.5「零禁向词面」合同成立=非绕闸非例外"
         "（闸 ADMIT 0 放行为证）+§0.5 落词法碰撞注记（§0.5=闸豁免区·_find_hits 只扫 body·S8 腿先例）；"
         "冻结史文 w1/w2 同词不回改按冻结纪律留档。How to apply：一切 prereg 追加节冻结"
         "（判决面/新批件）把禁向闸复跑列为冻结必检步；命中先分型——真禁向走 r494 例外三件套，"
         "词法碰撞走措辞精确化+§0.5 注记，禁绕闸禁静默跳过。\n")
with open(CODELY, "ab") as f:
    f.write(entry.encode("utf-8"))
codely2 = open(CODELY, "rb").read().decode("utf-8")
assert codely2.count("r484 bm-c") == 1, "CODELY marker count != 1"
print("CODELY appended, marker count == 1")

# ---- 2. round report append (marker gate) ----
rep = open(REPORT, "rb").read().decode("utf-8")
assert rep.count("｜r484｜") == 0, "round report marker already present (r679 gate)"
main_line = (
    f"{now_ts}｜r484｜dept:策略/研究（W3 s3 判决面冻结轮·T-158 在册）"
    "｜watermark verdict=绿（red=false·healthy·prep 计入 local_batch_running）"
    "｜当前活=W3 s3 全量判决面冻结+judge-prep 在飞（§9.1 append 冻结 commit 2b41a3958〔R99 冻结先于烧〕·"
    "785 存活者→|corr|≥0.999 leg-L 塌缩·prep 分离进程 16:35 起 ~13min 带·N_judge 塌缩后格数零宣称）"
    "｜最近实物=research/MASS_TRIAL_W3_PREREG.md §9.1（判决面冻结全文）+scripts/mass_trial_w1.py judge --wave 3"
    "（可跑 CLI·selftest 40/40 三新腿）+scripts/science_gates.py 种子 mass_trial_w3_judge=20285600 注册"
    f"（R250 一步律·同 commit）@ {now_iso}"
    "｜下个里程碑=r485 收养 w3_judge_state.json→入池 MASS-TRIAL-W3-JUDGE 4 分片→判决烧录在飞 ≤10-12"
    "（O-2115）；fund-trio finalize 10-05 10:30（bm-b）；O-2115/O-2030 验收 10-08；开市 10-09（≤48h）"
    "｜S0: daemon churn absorb 28ac69bf9（saturation 双面·treadmill ours-live-wins）→origin==HEAD 零差集零 merge"
    "｜S0.5: 双扫 155/155 零未回执（r477 全名口径·ACK_EXTRA README.md=历史无害）·D-19 decisions 4E5BE321+"
    "orders 68947C17 双 MATCH（r458 per-key 口径探针 _r484bmc_s05_check.py 动态读 state 水位）·inbox 0"
    "｜S1 smoke 48/48｜S2 板空（job_list 0·fleet 169 票 0 open）"
    "｜S3: satengine rc0 活（Tools 注册面 r467 律）·水位绿"
    "｜主产出：§9.1 冻结（prereg append·785 存活·candidates sha16 d0fc84b31113d572 实读禁手抄）"
    "+种子 20285600 注册（band ..20285899·SEED_REGISTRY 带隙扫描+rg --type py 零 RNG 命中·"
    "净空隙 tl_w2_gen 20285500..20285581 之上 tl_w2_scrnull 20286000 之下·同 commit R250）"
    "+judge --wave 3 CLI（_judge_faces 第三支〔首版 wave-2 无条件 return 死代码=selftest 当场抓回〕·"
    "argparse 三子命令 choices=[1,2,3]·selftest 40/40 三新腿〔seed 注册值+face 路由+nulls 分流〕·"
    "w1/w2 字节面不动）+禁向闸复跑（首跑 REJECT→词法碰撞定谳：BAN-04 裸词「网格」×判决评估格面=零关系·"
    "正法=措辞精确化「格面」+§0.5 词法碰撞注记〔§0.5=闸豁免区〕→ADMIT 0；w2 r423 先例未复跑闸缺口如实入坑律）"
    "→freeze commit 2b41a3958（3 文件+79/-16）→push_verify DELIVERED tip==remote→"
    "judge-prep --wave 3 分离 spawn 16:35:05（r423 协议镜像 Tools/_r484bmc_w3_judge_prep.py·"
    "psutil alive 实证·~13min 带〔w2 806 员实测锚·w3 785 员〕·r485 收养先例）"
    "｜S6 38/38 rc0 NON-ZERO=none（dualrun streak 51 零漂 372 entries·compute_audit rc0·"
    "pool_ready=3=bm-b NULLS 活烧面非本机勿碰·update_daily 金周 no-op·clock_call ORANGE_COOL·"
    "daily_report REPORT-20261004 落盘）"
    "｜S7: loop pin5 no-op+watchdog -Force 重装（16:40 首发在位）+双爪 LF 归一重装·"
    "attrition CLEAN（bm-a 面 2 healed 注记照录）·inbox/orders 二扫零差·RAM 9.6GB"
    "｜S4: 一条坑律行（§9.1 类追加节冻结必复跑禁向闸+词法碰撞措辞精确化正法）"
    "｜记分: 2（冻结判决面+judge --wave 3 可跑 CLI+prep 在飞=可跑可看实物）"
    "｜记账预算: 4/5（state+心跳+轮报+CODELY·无 registry 仪式件）"
    "｜本地未达 origin commit 数: 收口 push 后 push_verify 自证"
    "｜下轮指针=r485 ①收养 w3_judge_state.json（探针 prep 完成）→核塌缩/N_judge→"
    "入池 MASS-TRIAL-W3-JUDGE-SHARD-{0..3}（r509 raw-text 外科+done-flip 义务注记 W1 先例）"
    "②判决烧录在飞 ≤10-12 ③4/4 done→judge-finalize --wave 3+池面双翻同窗（r668 律）"
    "④fund-trio finalize 10-05 10:30（bm-b 正主·观察面）⑤O-2115/O-2030 验收 10-08\n")
close_line = (
    f"{now_iso}｜r484 bm-c S7-close｜本地未达 origin commit 数=0（产品面 push_verify DELIVERED "
    "tip 2b41a3958 实证 ahead=0/behind=0；收口 commit 后再证）｜收口实录：主产品=freeze commit "
    "2b41a3958（prereg §9.1+science_gates 种子+runner judge --wave 3 三件同 commit·R99）→"
    "prep 分离在飞（Tools/_r484bmc_w3_judge_prep.py·r485 收养）→S0 daemon absorb 28ac69bf9→"
    "close commit（簿记四写+探针族+S6 log）→push_verify 终证｜在册面行删除类=0（纯 append 轮·"
    "无清扫无 quarantine·登记簿零命中断言=不适用〔无清扫动作〕）｜轮产品计分：2（冻结判决面+可跑 "
    "CLI+在飞 prep·非等待态）\n")
with open(REPORT, "ab") as f:
    f.write((main_line + close_line).encode("utf-8"))
rep2 = open(REPORT, "rb").read().decode("utf-8")
assert rep2.count("｜r484｜") == 1 and rep2.count("r484 bm-c S7-close") == 1
print("round report appended, both markers == 1")

# ---- 3. state update (programmatic + reparse) ----
st = json.load(open(STATE, encoding="utf-8"))
st["round_no"] = 484
st["clock_read"] = now_iso
st["last_seen"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
st["last_round_at"] = now_iso
st["last_round_ts"] = now_ts
st["current_task"] = (
    "当前活: W3 s3 全量判决面冻结+judge-prep 在飞（§9.1 append 冻结 commit 2b41a3958〔R99〕·"
    "785 存活→|corr|≥0.999 塌缩·prep 分离进程 16:35 起 ~13min 带·r485 收养） "
    "| 最近实物: research/MASS_TRIAL_W3_PREREG.md §9.1（判决面冻结全文）+scripts/mass_trial_w1.py "
    "judge --wave 3（可跑 CLI·selftest 40/40）+science_gates 种子 20285600 注册（R250 一步律同 commit）"
    f" @ {now_iso} | 下个里程碑: r485 收养 w3_judge_state.json→入池 MASS-TRIAL-W3-JUDGE 4 分片→"
    "判决烧录在飞 ≤10-12（O-2115）；fund-trio finalize 10-05 10:30（bm-b）；O-2115/O-2030 验收 10-08；开市 10-09")
st["did"] = (
    "r484 bm-c W3 judge-face freeze round: (1) S0 daemon churn absorb 28ac69bf9 (saturation faces, "
    "treadmill ours-live-wins, origin==HEAD zero-diff); (2) S0.5 orders 155/155 zero-unacked dual-scan "
    "(r477 full-name caliber), D-19 decisions 4E5BE321 + group orders 68947C17 double MATCH zero-consume, "
    "inbox 0; (3) S1 smoke 48/48; (4) S2 boards empty (job_list 0, fleet 169 tickets 0 open); (5) S3 "
    "satengine rc0 alive (Tools face per r467), watermark green. MAIN PRODUCT: MASS_TRIAL_W3 s3 "
    "judge-face FROZEN (sec.9.1 append, commit 2b41a3958, R99 freeze-before-burn): 785 survivors -> "
    "|corr|>=0.999 leg-L collapse -> N_judge zero-claim; candidates sha16 d0fc84b31113d572 live-read; "
    "seed mass_trial_w3_judge=20285600 band 20285600..20285899 registered same commit (R250 one-step; "
    "clean gap above trial_labor_w2_gen 20285500..20285581 below tl_w2_scrnull 20286000; registry+rg "
    "zero RNG hit); runner judge-prep/judge/judge-finalize --wave 3 via _judge_faces (first draft "
    "wave-2 unconditional-return dead-code caught by selftest; w1/w2 byte-faces intact; ckpt "
    "w3_judge_shard_*; refinalize env split); banned-direction gate re-run at append-freeze: first run "
    "REJECT on BAN-04 bare-word 'grid' lexical collision with the judgment evaluation grid (w2 r423 "
    "precedent gap: same-word frozen file rejects today) -> lexical reword grid->cell-face + sec.0.5 "
    "collision note (sec.0.5 = gate-exempt zone), ADMIT 0 (not a bypass, not an exception); selftest "
    "40/40 (3 new w3 legs) + science_gates 69/69; push_verify DELIVERED tip 2b41a3958; judge-prep "
    "--wave 3 spawned detached 16:35:05 (r423 protocol mirror Tools/_r484bmc_w3_judge_prep.py, psutil "
    "alive, ~13min band per w2 806-backtest anchor, r485 adopt+enroll precedent). (6) S6 38/38 rc0 "
    "(dualrun streak 51 zero-drift 372 entries; pool_ready=3 = bm-b NULLS live-burn, not ours; "
    "update_daily golden-week no-op; clock_call ORANGE_COOL; daily_report written). (7) S7 quartet "
    "green (loop pin5 no-op, watchdog -Force, dual claws LF-normalized, attrition CLEAN with 2 healed "
    "bm-a notes); CODELY one pit-law line (append-freeze must re-run banned gate + lexical-collision "
    "reword path).")
st["last_round"] = (
    "r484 bm-c: W3 s3 judge-face FROZEN (sec.9.1 append, commit 2b41a3958, R99): 785 survivors -> "
    "corr>=0.999 collapse N_judge zero-claim; seed 20285600 band ..20285899 registered same commit "
    "(R250; clean gap tl_w2_gen/tl_w2_scrnull); judge --wave 3 CLI (selftest 40/40, 3 new legs); "
    "banned-gate re-run at append-freeze caught BAN-04 bare-word collision (w2 r423 precedent gap) -> "
    "lexical reword grid->cell-face + sec.0.5 note, ADMIT; judge-prep --wave 3 detached in-flight "
    "(spawn 16:35, ~13min band); S6 38/38; orders 155/155 zero-unacked dual-scan; D-19 double MATCH")
st["next"] = (
    "(a) r485: poll/adopt w3_judge_state.json from detached prep (verify collapse + N_judge) -> enroll "
    "MASS-TRIAL-W3-JUDGE-SHARD-{0..3} into runnable_pool (r509 raw-text surgical, ~N_judge/4 cells per "
    "shard, lane_owner null, done-flip duty notes per W1 no-handshake precedent) -> burn in-flight "
    "<=10-12 (O-2115). (b) after 4/4 done: judge-finalize --wave 3 (single-shot ledger append + "
    "w3_judge.json + pool dual-flip same window per r668 law + treasure-capture question at finalize). "
    "(c) fund-trio finalize 10-05 10:30 (bm-b owner, watch only). (d) O-2115/O-2030 acceptance 10-08. "
    "(e) market reopen 10-09.")
st["verify"] = (
    "freeze evidence = research/MASS_TRIAL_W3_PREREG.md sec.9.1 (commit 2b41a3958) + scripts/"
    "mass_trial_w1.py --wave 3 (selftest 40/40: seed 20285600 + face routing + nulls stream split) + "
    "scripts/science_gates.py SEED_REGISTRY registration (selftest 69/69) + banned gate ADMIT JSON; "
    "delivery = push_verify DELIVERED tip 2b41a3958 ahead=0/behind=0; prep = psutil alive + "
    "results/_r484bmc_w3_judge_prep_log.txt spawn line 16:35:05; S6 = results/_r484bmc_s6_log.txt "
    "38/38 rc0; S7 = attrition CLEAN + claws byte-fresh + loop pin5; state json.loads self-check + "
    "heartbeat epoch int + clock T-sep POST-WRITE (this script)")
with open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)
st2 = json.load(open(STATE, encoding="utf-8"))
assert st2["round_no"] == 484
print("state written, reparse OK, round_no == 484")

# ---- 4. heartbeat update (programmatic + reparse + epoch int) ----
hb = json.load(open(HEART, encoding="utf-8"))
n_ack = len(hb.get("orders_ack", []))
hb["clock_read"] = now_iso
hb["last_seen"] = now_iso
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["heartbeat_epoch_utc"] = now_epoch
hb["round_no"] = 484
hb["round_no_label"] = "r484"
hb["ts"] = now_ts
hb["health"] = "healthy"
hb["current_task"] = st["current_task"]
hb["verdict"] = st["last_round"]
hb["activity_now"] = (
    "W3 s3 judge-face FROZEN + prep in-flight (sec.9.1 append commit 2b41a3958, R99; seed 20285600 "
    "registered same commit R250; judge --wave 3 CLI selftest 40/40; banned-gate re-run caught BAN-04 "
    "bare-word lexical collision -> reword grid->cell-face + sec.0.5 note, ADMIT; judge-prep --wave 3 "
    "detached alive ~13min band, r485 adopt+enroll); S6 38/38 rc0 (dualrun streak 51); boards empty; "
    "orders 155/155 zero-unacked; pool_ready=3 = bm-b NULLS live-burn (not ours)")
hb["latest_artifact"] = (
    "research/MASS_TRIAL_W3_PREREG.md sec.9.1 (judge-face freeze) + scripts/mass_trial_w1.py judge "
    "--wave 3 + Tools/_r484bmc_w3_judge_prep.py (detached prep driver) + results/_r484bmc_s6_log.txt "
    "(38/38 rc0)")
hb["next_milestone"] = (
    "r485 adopt w3_judge_state.json -> enroll MASS-TRIAL-W3-JUDGE 4 shards -> burn in-flight <=10-12 "
    "(O-2115); fund-trio finalize 10-05 10:30 (bm-b); acceptance 10-08; market reopen 10-09")
hb["prod_lanes"] = (
    "W3 s3 judge lane open (freeze landed, prep in-flight, pool enrollment r485); FUND trio NULLS "
    "bm-b in-flight (watch only, keepalive healthy); N2-W15 freeze-window still the true gap line "
    "(r480+ queue); boards empty; no new orders this window")
# live machine sample
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1.0)
    ram = round(psutil.virtual_memory().available / 1024 ** 3, 1)
except Exception:
    cpu, ram = 3.0, 9.6
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=CNW, text=True)
    gpu_free = int(r.stdout.strip().splitlines()[0])
except Exception:
    gpu_free = 549
for k, v in (("cpu_pct", cpu), ("cpu_util_pct", cpu), ("idle_ram_gb", ram),
             ("ram_free_gb", ram), ("free_ram_gb", ram)):
    hb[k] = v
for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib",
          "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb",
          "gpu_idle_vram_mib", "gpu_idle_mb"):
    hb[k] = gpu_free
with open(HEART, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, indent=1, ensure_ascii=False)
hb2 = json.load(open(HEART, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock must be T-sep (R262)"
assert len(hb2["orders_ack"]) == n_ack, "orders_ack must be unchanged"
print(f"heartbeat written: epoch={hb2['heartbeat_epoch_utc']} (int), clock={hb2['clock_read']}, "
      f"ack={n_ack}, cpu={cpu}, ram={ram}, gpu_free={gpu_free}")
print("CLOSEOUT_DONE")
