# -*- coding: utf-8 -*-
# r434 bm-b close: round report line + state.json bump + heartbeat refresh
import json, io, time, datetime

now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# --- 1) round report line (bm-b uses shared logs/iteration-loop/round_reports.md) ---
line = (
    ts + " | r434 | dept:策略+研究 joint (W9 SCREEN 烧录·finalize·JUDGE 入池) | "
    "WM-VERDICT: 绿 red=false @16:56 probe (py_low_board_clear 合法=板空带池待燃面·autofill 点火权在握) | "
    "当前活: W9 判官烧批在跑 (judge-0of1 pid13280 @17:11:56 点火·243 judged cells·est ~30-45min) | "
    "最近实物: results/trial_labor_w9/w9_screen.json (2,715 cells finalize @17:10:14·survivors 243·"
    "null p95 0.5172 带内·AMP 反富集研究事实) + w9_screen_cells.csv + judge_state.json + "
    "TRIAL-LABOR-W9-JUDGE 池条目 (host_gates 附) @17:11 | "
    "下个里程碑: w9_judge.json 判决面 (judge-finalize·窗 ~17:50-18:00 落地起 48h CEO 报告钟) | "
    "did: (1) S0.5 令差集 122/122 双扫零新令 + bm-c MSG-1705 W10 候选供给宣言让路回执归档 (本机车道=W9·零竞争·bm-c MOM gate 候选同窗落地 1ce325dc2) + decisions.md 路径不存在零动作面; "
    "(2) 双面律欠账清偿: W8-JUDGE/W9-GENERATE shard face 残留 closed (entry 均 done·纯簿记·ckpt 408/408+w9_candidates 实证后闭); "
    "(3) S6 37 腿全 rc=0: dualrun ZERO-DRIFT streak 20/3; compute_audit FLAG supply_gap/supply_floor 如实 (ready 1<3=W9 漏斗过渡态在飞答案·JUDGE 已入池后自愈); py_watermark py_low_board_clear; update_daily 0 新行=09-29 bar 源未出诚实 no-op (第 9 轮测); regime ORANGE d2; clock ORANGE_COOL 0 激活; 守卫面 (scorecard/paper 族/t35/export/dashboard) bm-a 心跳 8-9min 新鲜诚实跳过; aggr/alloc/grid 幂等 no-op; REPORT+LIVE 09-29 regen; token delta=0; "
    "(4) push 风暴 13-UU (bm-c r228 close 同窗) 正典解: 分类器 9 分类+4 UNKNOWN (live_usage x4=r433 手工定性先例同律) -> _r434bmb_resolve.py 机械探针 (本窗我侧 :3: 全面更新鲜 16:56-58 vs :2: 16:54·零平手·孪生同侧·compute_audit union 202->cap 201·regime union 2=2) -> rebase continue -> push PASS; "
    "(5) W9 主线: autofill r351 origin-moved 双 defer (16:50/17:00) -> 会话拉平后手动 tick 点火 SCREEN 17:02:42 pid4592 (r398 手动点火先例) -> ckpt 2,715/2,715 @17:10:07 -> screen-finalize 落地: distinct 2515+nulls 200·null p95_line 0.517199 IN 重校带 [0.50,0.52]·survivors 243/2515=9.66%; 研究事实=AMP 分段存活 narrow 7.17% < wide 10.69% < none 11.02% (振幅确认门在初筛面反富集·与 W8 TSTATE deep_pullback 1.80x 正富集反向·负轴发现如实携带); ledger 341,073+2,715=343,788 对账 OK (pit-112 embed 块在产物); judge-prep PASS (manifest 48·census L/D==frozen·vol 594/518·yang 819/812·vconf 784/828·streak 384/389/856·tstate 188/1453+332/1572·amp 801/811); TRIAL-LABOR-W9-JUDGE 入池 (host_gates dir_nonempty 48 parquet 实证非空·RAM r354 三采样 12.7/12.9/12.9·lane_owner=bm-b 双面·_r434bmb_w9_judge_submit.py 提交脚本一字段勘误后过) -> 手动 tick 点火 JUDGE 17:11:56 pid13280 fill_latency 0.8min; 双面翻转 entry+shard done 同 commit (pit-89 燃落地轮翻转律); T-121 progress_r434; "
    "(6) S7 三自愈绿 (loop pin=2·watchdog·claw 重装); smoke 26/26; 单执行体核验 17:02 实例让道零旁开 | "
    "verify: screen ckpt 2,715/2,715 行实测 + finalize 断言全过 (完备门 0 missing) + ledger 块在 w9_screen.json (343,788=341,073+2,715) + judge-prep PASS 7 门 meta 全对齐冻结锚 + JUDGE 提交 SUBMIT_RC=0 + 点火 verdict=launched target_met=true | "
    "next: autofill 续燃 judge (30-45min 窗) -> 下轮收割 judge-finalize (w9_judge.json 判决面·G1/G2/DSR/PBO/E[FP]·48h CEO 报告钟起) -> s4 intake 按预注册; W10 泊位候选 (bm-c MOM gate) 待晋升机采用"
)
with io.open(r"logs\iteration-loop\round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write(line + "\n")
print("report line appended")

# --- 2) state.json bump (bm-b face) ---
st = json.load(io.open(r"state.json", encoding="utf-8"))
st["machine_id"] = "bm-b"
st["round_no"] = 434
st["note"] = ("r434: W9 SCREEN burned+finalized+JUDGE submitted same round -- survivors 243/2515 "
              "(9.66%), null p95 0.5172 in-band, AMP ANTI-enrichment research fact (narrow 7.17% < "
              "wide 10.69% < none 11.02%), ledger 343,788; JUDGE ignited 17:11:56 pid13280; "
              "push-storm 13-UU canon-resolved (:3: fresher uniform); dual-face residues closed")
st["last_round_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
st["last_round_ts"] = now.strftime("%Y-%m-%d %H:%M:%S")
st["ts"] = now.strftime("%Y-%m-%d %H:%M:%S")
st["updated"] = "r434 W9 screen done + judge burn in-flight (S6 37 rc=0, smoke 26/26)"
with io.open(r"state.json", "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("state bumped -> 434")

# --- 3) heartbeat (int epoch, T-separator clock) ---
epoch = int(time.time())
hb = json.load(io.open(r"fleet\machines\bm-b.json", encoding="utf-8"))
hb["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
hb["current_task"] = ("W9 JUDGE burn in-flight (pid13280 @17:11:56, 243 judged cells, est ~30-45min); "
                      "SCREEN finalized: survivors 243, null p95 0.5172 in-band, AMP anti-enrichment fact")
hb["round_no"] = 434
hb["loop_round"] = 434
hb["round"] = 434
hb["verdict"] = ("green lane healthy; W9 funnel screen->judge advanced same round (burn 7.4min + "
                 "finalize + judge-prep + JUDGE entry submitted + ignited); ledger 343,788; "
                 "supply_gap/supply_floor audit flags = W9 transitional in-flight answer; "
                 "board clear, bandit empty; push-storm 13-UU canon-resolved zero-loss")
with io.open(r"fleet\machines\bm-b.json", "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk = json.load(io.open(r"fleet\machines\bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must use T separator"
print("heartbeat epoch int OK:", chk["heartbeat_epoch_utc"], chk["clock_read"])
