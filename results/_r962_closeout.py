# r962 closeout: round report line + state + heartbeat (fresh-read-modify-write)
import json, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

REPORT = (
    f"{NOW} | r962 | bm-a | dept:工程/研究（T-182 slice-2 theme 行接线 + S0 风暴收口 + S6 38 腿全绿）"
    "| WM-VERDICT: RED (lane=pool-batch-runnable-idle-low-cpu；W17 SHARD-5/6/7+JUDGE 池内 ready、autofill 2min 序列点火在烧 pid 45988 实证、手工代烧引擎法禁、GM waiver O-1612)"
    "| 孤儿面=0 (round-zero 只读探针 33 py faces)"
    "| S0: writer-pause 窗（4 repo-writer 任务 disable→rebase 毕即 enable）+churn 吸收 2 commit+pull --rebase 撞 r961 重放=14 UU——4 ALL_FACES 走 merge_lane_views resolve（compute_audit history union 203 行+regime_state/update_status/token_usage）+8 手工按 skill 正典（3 snapshot 深扫 ts 探针 staged blob 取 :3: 新〔scorecard_v1 21:20:17/strategy_scorecard 21:20:25/_attrition_guard_scan 21:22:09〕；3 孪生对 json 探针定侧+md 同侧字节拷〔REPORT 同秒 tie→r140 取 :2: HEAD 法·首跑误取 :3: 当轮 byte-diff 自抓自纠；LIVE-2026-10-10/LIVE-latest :3: 新〕；d19_watermark 手工裁决 [:2: 新 receipt·双侧 watermark sha 恒等 a20664ec/5437bc4e=零信息损失]）→ resolver=results/_r962_resolve.py 留痕；reconcile 同窗=regime_state/update_status/token_usage ZERO-DRIFT、compute_audit drift→S6 dualrun 治愈 streak 2"
    "| S0.5: fleet/orders 65 O-件 vs 199 ack 零未回执（README=文档假阳性排除）；D-19 集团水位：ORD delta 5437bc4e→3af479f1=1 行（21:3x mv0001 全曲 KF 批派 bm-c·BigStream 线零 BigMoney 面·其 W17 让渡注=本机已在飞面）→消费+ADVANCED ord=3af479f1、dec 不变 a20664ec"
    "| S1: smoke 49/49"
    "| S3: T-182 slice-2=**theme-wave-rider 行入 P0 矩阵**（THEME-JUDGE-P1 TJ-FULL-x1 pooled 日流·nav 锚 pooled_net 逐位 5e-6·selftest 13/13 绿）→ 矩阵重生成 6/10 行接线：theme 主场 BULL 1.32% (n=166) 压线≥1.30% 达标；客场 GRIND -10.88%/BEAR -4.48%/SUPPORT -10.45% harmed=调度 off 候选（四市调度律正脸：牛市武器只在牛市工作）；dip-rebound 诚实改判（rev_p2=trade 级件·日流重建=下切片）；W17 望=pid 45988 序列在烧零手工点火"
    "| S6: 38 腿链全 rc0（dualrun ZERO-DRIFT streak2；周末 no-op 诚实；paper 腿幂等 cutoff 2026-10-09；daily_report/ceo_live/build_status 刷新）"
    "| S7: 四件套绿（loop pin8 no-op/watchdog 注册 21:52/双爪装）+attrition CLEAN+idle_trigger --worked→idle_rounds 0"
    "| 执法强化件（查重律零新法条）: ①r140 同秒 tie→HEAD 法在自写 resolver 首跑违例〔t3>=t2 误取 :3:〕——当轮 REPORT 孪生 byte-diff 自抓自纠·修复版=results/_r962_resolve.py 入库为证；②13:50 长任务禁管道律复发〔S6 链 Select-Object 管道 5min 零输出被杀〕——改 *> 文件重定向重跑全绿·results/_r962_s6_chain.py+log 入库为证"
    "| 序列诚实注: r959/r960 会话死于重放中、r961 完成提交但报告行未落（estate 由 r961 commit 99e4456dc 吸收上 origin）——本行=r962、序列以本行为准续编"
    "| 本轮产品积分:2（P0 矩阵 theme 行=可跑实物+矩阵 json/md 更新）·记账预算:5 内（state/心跳/轮报告/水位件）"
    "| 本地未达 origin commit 数=0（收口 push+fetch+rev-list 自证）"
    " | [r962 bm-a]"
)

p = "round_reports-bm-a.md"
with open(p, encoding="utf-8") as f:
    src = f.read()
if not src.endswith("\n"):
    src += "\n"
src += REPORT + "\n"
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("round report appended, total lines:", src.count("\n"))

# --- state file ---
sp = "state-bm-a.json"
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
st.update({
    "round_no": 962, "round": 962, "loop_round": 962, "last_round": 962,
    "last_round_at": NOW, "last_round_closed": NOW, "ts": NOW, "updated": NOW,
    "updated_at": NOW, "last_run": NOW, "last_seen": NOW,
    "current": "r962 closeout done",
    "current_task": "r963: W17 burn watch (autofill seq SHARD-5/6/7+JUDGE) + T-182 pending rows (dip-rebound daily-stream recon / six-members / four-asset) + D-19/ORD watermark + S6 chain",
    "did": "r962: S0 14-UU rebase storm canon-resolved (4 merge_lane_views + 8 hand per skill, r140 tie-bug self-caught+fixed) + D-19 ORD delta consumed+advanced 3af479f1 + T-182 slice-2 theme-wave-rider row wired (P0 matrix 6/10, theme home BULL 1.32% pass, away harmed=dispatch-off candidates) + S6 38 legs rc0",
    "last_action": "T-182 slice-2 theme row + S0 storm closeout",
    "last_artifact": "results/regime_matrix_p0/P0-MATRIX-v1-2026-09-30.md (6/10 rows wired, 21:38)",
    "latest_artifact": "results/regime_matrix_p0/P0-MATRIX-v1-2026-09-30.md (6/10 rows wired, 21:38)",
    "recent_artifact": "results/regime_matrix_p0/P0-MATRIX-v1-2026-09-30.md (6/10 rows wired, 21:38)",
    "next": "r963: W17 burn watch + T-182 pending-row pinning (dip-rebound stream recon) + D-19/ORD watermark",
    "now_active": "r963: W17 burn watch + T-182 pending rows + D-19/ORD watermark + S6 chain",
    "task": "r963: W17 burn watch + T-182 pending rows + D-19/ORD watermark + S6 chain",
    "idle_rounds": 0, "agenda_starved": False,
    "next_milestone": "r963 T-182 pending-row pinning; W17 autofill seq completion + judge leg; 10-13/14 O-1725 P0 matrix delivery; 10-31 month-boundary first exam (T-143 assembly 10-29)",
    "orphan_face": 0, "orphan_faces": 0,
    "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True,
    "clock_read": NOW,
    "verdict": "red (W17 pool-batch-runnable-idle-low-cpu lane: SHARD-5/6/7+JUDGE ready, autofill sequential ignition live pid 45988, manual burn forbidden, GM waiver O-1612; all other faces green: smoke 49/49, rebase storm resolved zero-loss, theme row wired, S6 38 legs rc0)",
    "verify": "red (W17 pool-batch-runnable-idle-low-cpu lane: autofill owns ignition, live pid 45988; all other faces green)",
    "last_orders_seen": "r962 consume: group ORD delta 5437bc4e->3af479f1 = 1 row (21:3x mv0001 full-song KF dispatch to bm-c, BigStream lane, zero BigMoney face; W17-yield note = already-executing face); fleet orders 65 O-files vs 199 ack ZERO unacked",
    "last_orders_at": NOW, "last_orders_ts": NOW, "last_orders_read_at": NOW,
    "last_orders_sha": "3af479f1383537596cd0937a8d64e056879c27e8",
    "last_decisions_seen": "r962: DEC a20664ec content UNCHANGED (probe == watermark, zero re-consume)",
    "last_decisions_at": NOW, "last_decisions_read_at": NOW,
    "notes_seq_r962": "r959/r960 died mid-replay, r961 committed but report line absent (estate absorbed in commit 99e4456dc on origin); sequence resumes honestly at r962 per round_reports canonical face",
})
if "d19_watermark_guard" in st:
    st["d19_watermark_guard"]["round_ref"] = 962
    st["d19_watermark_guard"]["ts"] = NOW
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state updated round_no=962, epoch int:", EPOCH)

# --- heartbeat ---
hp = "fleet/machines/bm-a.json"
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "ts": NOW, "updated": NOW, "updated_at": NOW, "last_seen": NOW,
    "last_round": 962, "round": 962, "round_no": 962, "loop_round": 962,
    "last_round_at": NOW, "last_round_closed": NOW,
    "current": "r962 closeout done",
    "current_task": "r963: W17 burn watch + T-182 pending rows + D-19/ORD watermark + S6 chain",
    "did": "r962: S0 14-UU rebase storm canon-resolved (r140 tie-bug self-caught+fixed) + D-19 ORD advanced 3af479f1 + T-182 theme-wave-rider row wired (P0 matrix 6/10) + S6 38 legs rc0",
    "last_action": "T-182 slice-2 theme row + S0 storm closeout",
    "last_artifact": "results/regime_matrix_p0/P0-MATRIX-v1-2026-09-30.md (6/10 rows, 21:38)",
    "latest_artifact": "results/regime_matrix_p0/P0-MATRIX-v1-2026-09-30.md (6/10 rows, 21:38)",
    "recent_artifact": "results/regime_matrix_p0/P0-MATRIX-v1-2026-09-30.md (6/10 rows, 21:38)",
    "next": "r963: W17 burn watch + T-182 pending-row pinning + D-19/ORD watermark",
    "now_active": "r963: W17 burn watch + T-182 pending rows + D-19/ORD watermark + S6 chain",
    "task": "r963: W17 burn watch + T-182 pending rows + D-19/ORD watermark + S6 chain",
    "idle_rounds": 0, "agenda_starved": False, "orphan_face": 0, "orphan_faces": 0,
    "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True,
    "clock_read": NOW,
    "verdict": "red (W17 pool lane: autofill sequential ignition live pid 45988, 4 entries ready, manual burn forbidden; all other faces green: smoke 49/49, theme row wired, S6 38 legs rc0)",
    "last_orders_seen": "r962 consume: group ORD delta 5437bc4e->3af479f1 = 1 row (mv0001 KF dispatch to bm-c, zero BigMoney face); fleet orders 65 O-files vs 199 ack ZERO unacked",
    "last_orders_at": NOW, "last_orders_ts": NOW, "last_orders_read_at": NOW,
    "last_orders_sha": "3af479f1383537596cd0937a8d64e056879c27e8",
    "last_decisions_seen": "r962: DEC a20664ec content UNCHANGED (zero re-consume)",
    "last_decisions_at": NOW, "last_decisions_ts": NOW, "last_decisions_read_at": NOW,
    "last_decisions_sha": "a20664ec0852a5ada8cea3f3fb93ea35254d0023",
})
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
# self-verify epoch int type (R170/R178 law)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat updated, epoch int verified:", chk["heartbeat_epoch_utc"])
