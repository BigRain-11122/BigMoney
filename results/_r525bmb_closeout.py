import json, time, datetime
import psutil

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EP = int(time.time())
psutil.cpu_percent(interval=0.5)
ram_free = round(psutil.virtual_memory().available / (1024**3), 1)

# ---- state.json (bm-b own file, indent=1 like existing) ----
s = json.load(open("state.json", encoding="utf-8"))
s["round_no"] = 525
s["note"] = ("r525 COMPLETED: W31 engine wave one-pass same-round closed loop (TWENTIETH engine wave, bm-b ninth-owned; "
 "crashed r525-session half-work adopted per r322/r471 three-face verify [law diff canonical + band gate ADMIT re-run on "
 "current tree + 12/12 shard audit.machine=bm-b]; chain gate honored W30-first [d75a3e967 22:48] -> prev 430,548 "
 "W30-on-origin derive + 2,200 = 432,748 chain-linear, K=66,120 == prereg sec.0 projection verbatim; S5 4/4 PASS "
 "anchor-roll W29->W30 disclosed [mu-drift 0.0078<0.02 / sigma -2.19%<10% / A p95 0.3074 vs 0.308 delta -0.0006<0.05 / "
 "K-lift -0.0012<=0.02 @n_eff_held 430,548, canon_flip NOT performed]; merged mu -0.0915 sigma 0.2445 se_mu 0.000951 "
 "narrowed; engine tick pre-commit burn 22:39-22:51 per r535 precedent; first-run no-rerun per r538; sec.7/8 same-window "
 "backfill + default-wave selftest PASS; pool_core_samples rebase conflict r294 conflict-region union 12+12=24 zero-loss; "
 "r501 rebase false-refusal commit -C net path; push FF bce5182fd delivery 13/13 ls-tree verified) + S6 holiday no-ops "
 "all rc0 (dualrun ZERO-DRIFT streak 15/3; audit pool_starvation/supply_floor = between-wave transient answered by W32=bm-c "
 "slot rotation, engine waves not in pool per SATURATION_ENGINE_LAW sec.1; WM insufficient_history legal first-sample; "
 "token delta=0) + S7 all-green (loop pin=2 no-op, watchdog S4U registered, attrition CLEAN, inbox empty, orders diff "
 "zero, D-19 SHA MATCH-unchanged) = next bm-b round: W32=bm-c slot watch (not mine), next bm-b owned wave=W34 per "
 "rotation, post-holiday first-bar S6 processing when market resumes")
s["last_round_at"] = NOW
s["last_round_ts"] = EP
s["ts"] = NOW; s["updated"] = NOW; s["updated_at"] = NOW
json.dump(s, open("state.json", "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-b.json ----
h = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
h["last_seen"] = NOW
h["heartbeat_epoch_utc"] = EP
h["clock_read"] = NOW
h["current_task"] = "W31 engine wave closed one-pass (chain 432,748, K=66,120, S5 4/4); engine idle honest; W32=bm-c rotation slot watch; next bm-b owned wave=W34"
h["round_no"] = 525
h["cpu_util_pct"] = psutil.cpu_percent(interval=None)
h["free_ram_gb"] = ram_free
h["idle_ram_gb"] = ram_free
h["verdict"] = ("healthy: W31 closed (freeze+burn adoption+finalize landed origin bce5182fd, 13/13 ls-tree verified); "
 "watermark green (dualrun streak 15/3; pool_starvation/supply_floor = between-wave transient answered by W32=bm-c slot); "
 "board closed; S6 all rc0 holiday no-ops; attrition CLEAN")
json.dump(h, open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert isinstance(h["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"

# ---- round report line (bm-b file) ----
REPORT = """## r525 (2026-10-01 23:0x +08:00) bm-b
- watermark verdict: 绿（dualrun ZERO-DRIFT streak 15/3；audit pool_starvation/supply_floor 旗=引擎波不入池面·W32=bm-c 槽位轮值间隙答·同 r524 定性；WM insufficient_history=合法首样窗·板全闭环 bandit 0）
- 当前活：W31 引擎波收口完成（本轮主产出·dept:研究·dept:工程）
- 最近实物：results/perpetual_faces/n1_w31_results.json（23:0x·链头 432,748·K=66,120·merged mu -0.0915）+ 12 分片 results/p2cal_ext/n1_w31/（tick 自燃 22:39-22:51）
- 下个里程碑：W32=bm-c 槽位冻结观察（轮值律·非本机座位）；bm-b 下枚自有波=W34；假日后首个交易日 S6 数据面处理（窗≤48h：W32 预期 bm-c 侧冻结）
- 做了什么：S0.5 orders 差集空+D-19 水位 MATCH-unchanged 零动作（dec 探针复用猝死会话遗产件）；S1 smoke 47/47；收编猝死 r525 会话 W31 遗产（三面验证=法行 diff 正典范式+带闸 ADMIT 当前树复跑〔N3-R1 腿+探针簇 r335 腿+W29 兑现腿〕+12/12 分片 audit.machine=bm-b）→冻结提交 60f59746e（r535 tick 预落盘先例披露）→rebase 撞 pool_core_samples=r294 冲突区 union 12+12=24 零丢失（resolver _r525bmb_pool_samples_union.py 留痕）+r501 假拒绝 commit -C 净路→finalize --wave 31 首跑一趟过→§7/§8 同窗机械回填（r307 两态律）→缺省波 selftest PASS（r522 律）→finalize 提交 89eb7c23e→ride bce5182fd→push FF 送达 13/13 ls-tree 自证
- 验证证据：prev=430,548（W30-on-origin derive·链性纪律 W30 先落两态兑现）+2,200=432,748 链线性；K=66,120==prereg §0 投影逐位；S5 4/4 PASS（锚滚动律 W29→W30 披露：mu-drift 0.0078<0.02/sigma −2.19%<±10%/A p95 0.3074 vs 0.308 Δ−0.0006<0.05/K-lift −0.0012≤0.02 @n_eff_held 430,548·canon_flip NOT performed·负向如实）；se_mu 0.000968→0.000951 收窄；voids_applied=[LOWAMP-P1]；banned 闸 PASS；S6 全 rc0；attrition CLEAN；本地未达 origin commit 数=0
- 下轮指针：W32=bm-c 槽位观察（非本机座位·勿抢）；W34=bm-b 下枚自有波（A 109_004..111_003 投影面 W33 落位后再机验）；月度 trio 已由 bm-a r542 跑毕（10-01 月首轮·不双跑）；HANDOVER 5x 窗口行本轮已补（r505-r525 九枚自有波窗）
"""
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(REPORT)

# ---- HANDOVER 5x window entry (round 525 = multiple of 5) ----
H = """- [2026-10-01 23:0x r525 bm-b] HANDOVER 5x window entry (window r505-r525, OVERDUE-BACKLOG NOTE: r510/r515/r520 bm-b 5x stamps missed -- window carried the crash-adoption era (r513/r522/r523 closeout heal + never-dry engine wave line); per r420-cont/r500/r335 precedent no backfill fabrication, single window covered compactly here; bm-a r510/r515 + bm-c r315/r335 rows cross-read for their lanes). LEDGER LIVE-READ ANCHOR THIS ROUND = 432,748 (results/perpetual_faces/n1_w31_results.json trials_ledger.total live-read r525 23:0x, evidence_cutoff 2026-09-22). THIS-WINDOW bm-b PRODUCTS (r505-r525): (1) never-dry engine wave line: NINE bm-b-owned N1 waves frozen+burned+finalized chain-linear this window -- W10 [r509] / W11 [r510] / W13 [r513] / W16 [r516] / W19 [r518, same-window double-freeze collision YIELD vs W17 then re-based finalize per r511 law] / W22 [r519] / W25 [r520] / W28 [r524 one-pass] / W31 [r525 this round, TWENTIETH engine wave, first zero-skip wave since W28], +2,200 each = +19,800 bm-b-lane arithmetic (cross-machine wave rows W12/W14/W17/W18/W20/W21/W23/W24/W26/W27/W29/W30 per bm-a/bm-c owner rows); cumulative merged face now mu -0.0915 sigma 0.2445 se_mu 0.000951 K=66,120 (skill_line_v2 K-lift negative single-wave fluctuation family honest, canon_flip never triggered); every wave carried band-gate ADMIT machine receipt + prereg sec.7/8 same-window backfill + default-wave selftest + ledger block persisted in product per r509. (2) closeout-sweep era participation: r513 W13 shard restore 719833f63 (audit.machine ownership verify) + r519 family disclosure; zero surgical full-tree payloads adopted as standing discipline. (3) r522 orphan-reconciliation leg for the engine tick crash-loss face (4 orphans reconstructed, shards_done_total 102->106, same defect family flagged for bm-c Tools engine port). (4) r525 (this round): crashed-session adoption of W31 half-work per r322/r471 (three-face verify) then one-pass closeout (chain gate W30-first honored, prev 430,548 + 2,200 = 432,748; S5 4/4 PASS anchor-roll W29->W30 disclosed; pool_core_samples r294 conflict-region union 12+12=24; r501 rebase false-refusal commit -C net path; push FF bce5182fd, delivery 13/13 ls-tree verified). Maintenance per rounds: smoke 47/47 chains; S6 28-37 legs rc0 holiday no-op chains; dualrun streak chain to 15/3 ZERO-DRIFT; orders dual-scan zero-diff every round (orders_ack tail O-20261001-2106); D-19 decisions SHA MATCH-unchanged chain (753f99e8); monthly trio done by bm-a r542 (10-01 month-first, no double-run); token deltas 0; attrition CLEAN chains; S4U task law held (loop pin=2, watchdog S4U). NEXT 5x = round 530 bm-b. Pointers: W32=bm-c slot (rotation law; projection A 107_004..109_003 / B 41_401..41_600 clean per r525 gate W32+ leg -- verify at W32 prereg by machine gate per r535 derive law); next bm-b owned wave=W34; post-holiday first-bar S6 processing when market resumes (10-08 expected); REGIME_GUARD v3 date-gate active hands-off; month-boundary first exam 10-31.
"""
with open("research/HANDOVER.md", "a", encoding="utf-8") as f:
    f.write(H)

print("STATE_OK round=525 ep=%d (%s) ram_free=%s cpu=%s" % (EP, NOW, ram_free, h["cpu_util_pct"]))
print("HEARTBEAT_OK epoch_int=%s clock=%s" % (isinstance(h["heartbeat_epoch_utc"], int), h["clock_read"]))
print("REPORT_OK HANDOVER_OK")
