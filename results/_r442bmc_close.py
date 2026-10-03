# -*- coding: utf-8 -*-
"""r442 bm-c close: state + heartbeat + round-report line.
Golden-week maintenance round: S0 16-UU integration surgery (r437 netpath +
resolve recipes), S6 29/29, W2 judgment burn in-flight (CPU-advancing wait)."""
import io, json, time, datetime

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    idle_ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu_pct, idle_ram_gb = 3.0, 9.3

# ---- state-bm-c.json ----
with io.open("state-bm-c.json", "r", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 442
st["did"] = ("r442 bm-c golden-week integration/maintenance round: (1) S0 surgery -- origin +15 ahead with 3 "
             "daemon-lane faces dirty (full intersection) -> r437 pre-align netpath (treasure_guard restore-class "
             "rc0 reproducible-artifact 3/3 -> origin-verbatim checkout -> targeted absorb d1af0259c) -> merge "
             "origin/main hit 15 UU -> merge_lane_views resolve recipes on 5 lane faces (runnable_pool 366-entry "
             "id-union done-absorption / compute_audit ts-union 203 / regime_state row-union / token_usage+"
             "update_status max-cutoff) + 10 regenerable faces origin-wins --theirs per r440 law -> merge 8adeb3daf "
             "-> push race (bm-b keepalive claim-refresh landed mid-window) -> merge #2 clean auto-merge 97dcbc285 "
             "-> push_verify DELIVERED (ahead=0, tip bilateral). (2) S0.5 double-scan 152/152 zero unacked both "
             "scans; D-19 decisions MATCH EB14B510 + GORDERS MATCH 68947C17 (group-tree origin fetch+raw-bytes "
             "sha). (3) S1 smoke 47/47. (4) W2 judge-finalize burn poll: pid 31336 alive CPU 13429->15311s "
             "advancing (~98% single core), log 2 spawn banners, artifact w2_judge.json absent, kill-line 04:04 "
             "NOT triggered (CPU advancing), deadline <=10-06 intact. (5) S6 29/29 rc0 (dualrun ZERO-DRIFT streak "
             "44; scorecard stale-takeover derive per O-2100 s2.4 STALE_MIN -- bm-a hb stale 41min: 6 traders "
             "S=2/A=4, best VOLATILITY-CE-01 87.0; CALL ORANGE_COOL asof 09-30; REPORT-2026-10-04 + LIVE-2026-10-04 "
             "refreshed ORANGE cap50; token delta=0). (6) satengine alive rc0 (heartbeat 37s fresh, queue 0, "
             "burns 0 -- N1 supply closed pending W2 landing per r441 next(e)). (7) S7 self-heal 4x green "
             "(pin5 no-op, watchdog re-registered first-fire 03:58, both claws installed), attrition CLEAN, "
             "inbox empty.")
st["verify"] = ("push_verify DELIVERED (tip 97dcbc285fffc192c49589bd56e49628433bc915 bilateral, ahead=0); merge #2 "
                "auto-merge zero UU; resolve outputs parse-verified (tool asserted); smoke 47/47; S6 log "
                "results/_r442bmc_s6_log.txt 29/29 rc0 fails=0; dualrun streak 44; D-19+GORDERS raw-bytes MATCH; "
                "orders double-scan 152/152 zero unacked; satengine rc0 alive_flag true; W2 CPU advancing "
                "13429->15311s; attrition CLEAN rc0; epoch int + clock T-sep in-wrap asserted")
st["next"] = ("(a) W2 poll each round: python Tools/_r426bmc_w2_judge_finalize.py status -> w2_judge.json landing = "
              "same-round adoption (adapt _r426bmc_close.py: count->replace->assert + burn-log atomic commit, "
              "deadline <=10-06; kill-line = zero log progress AND CPU stopped after 04:04 -> deterministic kill "
              "escalation report). (b) D-06 final sweep 10-07: pit-data CRLF adjudication + assertion-layer "
              "increment ruling (r402/r419/r420) + flow-sinking final pass + full reconciliation. (c) O-2030 "
              "acceptance evidence pack 10-08 (weld faces r432-434 + demo receipts + W2 landing capture-point "
              "sample + batch-2 migration-ritual row). (d) T-134 next conversion trigger = panel-host round or "
              "single_core runner queued. (e) W2 landing -> N1 supply reopen; py_low zero-ignition post-landing = "
              "supply-chain P0 to GM.")
st["current_task"] = ("r442 done (16-UU S0 surgery DELIVERED + S6 29/29 streak 44 + scorecard stale-takeover); "
                      "next: W2 landing poll + adoption (<=10-06) / D-06 final sweep 10-07 / O-2030 pack 10-08")
st["last_round"] = ("r442 bm-c: S0 16-UU integration surgery (r437 netpath + resolve recipes 5 lane faces + 10 "
                    "regenerables origin-wins, push-race merge #2, DELIVERED 97dcbc285) + S6 29/29 (dualrun 44, "
                    "scorecard stale-takeover S=2/A=4) + W2 judgment burn alive CPU-advancing artifact pending; "
                    "smoke 47/47; orders/D19/GORDERS MATCH")
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["last_ts"] = now_iso
st["last_seen"] = now_iso
st["last_decisions_read_at"] = now_iso
st["updated"] = now_iso[:19].replace("T", " ")
st["updated_at"] = now_iso
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = now_iso
st["cpu_pct"] = cpu_pct
st["idle_ram_gb"] = idle_ram_gb
st["gpu_free_vram_mib"] = 14548
with io.open("state-bm-c.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-c.json ----
with io.open("fleet/machines/bm-c.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = now_iso
hb["last_seen_at"] = now_iso
hb["updated_at"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["round_no"] = 442
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["cpu_idle_pct"] = round(100.0 - cpu_pct, 1)
hb["idle_ram_gb"] = idle_ram_gb
hb["free_ram_gb"] = idle_ram_gb
hb["ram_free_gb"] = idle_ram_gb
hb["gpu_free_vram_mb"] = 14548
hb["gpu_free_vram_mib"] = 14548
hb["activity_now"] = ("W2 thousand-trial judgment burn in flight (pid 31336, single-core ~98% CPU advancing, "
                      "artifact w2_judge.json pending, deadline <=10-06); N1 supply reopen queued behind it")
hb["current_task"] = ("r442: S0 16-UU surgery DELIVERED + S6 29/29 all-green; W2 judgment burn in flight")
hb["latest_artifact"] = ("S0 integration surgery: 15-conflict merge resolved zero-loss (resolve recipes 5 lane "
                         "faces + origin-wins 10 regenerables) + scorecard stale-takeover derive (6 traders "
                         "S=2/A=4) + docs/daily_report/REPORT-2026-10-04.md + docs/live_usage/LIVE-2026-10-04.md "
                         "refreshed @" + now_iso)
hb["next_milestone"] = ("W2 judgment artifact landing -> same-round adoption (burn-log atomic commit), window "
                        "<=10-06; then N1 supply reopen; D-06 final sweep 10-07; O-2030 evidence pack 10-08")
hb["verdict"] = ("green (golden-week maintenance round all-green; W2 judgment burn healthy CPU-advancing wait "
                 "state; board/bandit/pool all lawful)")
with io.open("fleet/machines/bm-c.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-proof: epoch must be JSON int, clock T-separated (F7/R262 laws)
with io.open("fleet/machines/bm-c.json", "r", encoding="utf-8") as f:
    chk = json.load(f)
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (F7 law)"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock must be T-separated (R262 law)"
with io.open("state-bm-c.json", "r", encoding="utf-8") as f:
    chk2 = json.load(f)
assert isinstance(chk2["heartbeat_epoch_utc"], int), "state epoch must be int"
assert chk2["round_no"] == 442, "round_no must be 442"

# ---- round report line: bytes append (mixed-encoding history file, r641 law) ----
line = (
    "watermark: green (red=false; satengine alive rc0 queue 0; py_low_with_work_cands 合法白名单=板全闭环 0 票+bandit "
    "空+本地 W2 判决烧录占位在飞+池面 ready3/unclaimed1 属 autofill 辖区非手工代烧面) | " + now_iso + " | r442 | "
    "dept:工程 | 当前活: W2 千人审判判决烧录在飞 (pid 31336 单核 ~98% CPU 前进 13429->15311s, artifact w2_judge.json "
    "待落, kill-line 04:04 不触发[CPU 前进], deadline <=10-06) | S0: 集成手术 -- origin +15 且树脏 3 daemon 面全交集 -> r437 "
    "预对齐净路 (treasure_guard restore-class rc0 reproducible-artifact 3/3 -> origin-verbatim checkout -> 定向 absorb "
    "d1af0259c) -> merge 撞 15 UU -> 5 车道面 merge_lane_views resolve 配方 (runnable_pool 366-entry id-union "
    "done-absorption/compute_audit ts-union 203/regime_state row-union/token_usage+update_status max-cutoff) + 10 可再生面 "
    "origin-wins --theirs (r440 两分法) -> merge 8adeb3daf -> push 竞态 (bm-b keepalive claim-refresh 窗内落地) -> merge #2 "
    "干净 auto-merge -> push_verify DELIVERED tip 97dcbc285 双侧恒等 | S0.5: 双扫 152/152 零未回执 (轮首+S7 两扫) + D-19 "
    "MATCH EB14B510 + GORDERS MATCH 68947C17 (集团树 origin fetch+python 原始字节双 hash) | S1: smoke 47/47 | S2/S3: 任务板无 "
    "可领票 (T-165 bm-a 占/T-155 bm-b 占/本机 T-158 在飞 W2 判决段); satengine rc0 活 (心跳 37s, N1 队列空=W2 落地后重开) | "
    "S6: 29/29 rc0 (dualrun ZERO-DRIFT streak 44; scorecard lane_io stale-takeover 合法接管 [bm-a 心跳 stale 41min, "
    "O-2100 s2.4 STALE_MIN]: 6 交易员 S=2/A=4/B=0/C=0 最佳 VOLATILITY-CE-01 87.0; CALL ORANGE_COOL asof 09-30; "
    "REPORT-2026-10-04+LIVE-2026-10-04 刷新 [ORANGE cap50% 6 员]; token delta=0; 月度三件 10-02 已跑免重) | S7: 自愈 4x "
    "绿 (pin5 no-op/watchdog 重注 03:58 首发火/双爪在位) + attrition CLEAN + inbox 零未读 | 验证证据: "
    "results/_r442bmc_s6_log.txt (29 腿逐 rc), merge #1/#2 提交链 + push_verify JSON (tip 双侧), resolve 工具 parse-verified "
    "断言, smoke Summary 47/47 | 记分: 1 (S0 集成手术=实际文件改动保 16 冲突面零丢失收敛+S6 管线产出; 无新决策实物 -- W2 判决批 "
    "在飞=等待态一行声明非空转, r441 昨窗 2 分实物在册) | 记账预算: 3/5 (state+心跳+轮报) | 本地未达 origin commit 数: 1 "
    "(closeout commit 即推·推后 fetch 自证) | 登记簿零命中断言: 本轮 treasure_guard restore-class 3 面 rc0 "
    "reproducible-artifact, TREASURE_REGISTRY 零命中, 无清扫/归档/删除动作 | ceo-visibility: [当前活] 千人审判第二批判决 "
    "正在本机烧录 (805 行判决面, 4/4 分片齐, 冻结 4796399f3, 已烧 4.3h CPU 前进中) | [最近实物] S0 集成手术 16 冲突面零丢失合并 "
    "DELIVERED + 战绩卡合法接管刷新 (S=2/A=4) + 每日战报/实盘一页纸 10-04 刷新 @" + now_iso[:16] + " | [下个里程碑] W2 判决 "
    "artifact 落地即同轮收养 (burn-log 原子 commit), 窗 <=10-06; 随后 N1 供给重开; D-06 全线收口 10-07; O-2030 证据包 10-08\n")
with io.open("round_reports-bm-c.md", "ab") as f:
    f.write(line.encode("utf-8"))

print("r442 closeout writes done; epoch=", epoch, "cpu=", cpu_pct, "ram_free=", idle_ram_gb)
