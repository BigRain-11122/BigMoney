# -*- coding: utf-8 -*-
# r658 bm-c close driver -- round report line + state + heartbeat, single
# source of truth for timestamps (same-clock law). Facts-driven from this
# round's receipts; QA 5/5 + S6 38/38 + post_review 45/0 verified in-window.
import json, time, datetime, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone()
ISO = NOW.isoformat(timespec="seconds")            # T-format with UTC offset
EPOCH = int(time.time())                          # JSON int (R170/R178 law)
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
ST = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")

WATERMARK = ("watermark: 绿（red=false lane healthy；SAT 活=Tools 面 engine_alive True·tick 本轮新鲜·"
             "verdict idle=黄金周合法态；board 0 open/176·Codely 0；no-bar 窗 10-09）")
CURRENT = ("当前活: r658 P0 冲突标记污染事件处置轮（post_review 3 NO 捕获 bm-b r796 rebase 窗 17 件共享面未解 "
           "marker 入 origin→全仓 census 45 命中=17 真污染→外科愈合=16 件 parent-blob 精确恢复+token_usage 行级 "
           "union 零损失证明→commit e6b9acfc2 推送送达核验 origin marker=0→post_review 45 YES/0 NO 翻绿→"
           "S6 38/38+QA r658 5/5）")
ARTIFACT = ("最近实物: commit e6b9acfc2（17 件共享面 marker 清零·含 CEO 面 dashboard_status 24 hunks/"
            "strategy_scorecard 2 hunks）+results/_r658bmc_marker_incident_census.json（45 命中逐件归因·污染提交 "
            "6d8e04b9a [via bm-b r796]·parent 全洁净）+results/_r658bmc_surgical_heal_receipt.json（union==parent "
            "blob·crash_fuse 3602<=3638·17/17 验证门）+qa/smoke-r658.md（5/5·93 trades·determinism=True·equity 终值 "
            "1,017,839 面恒等）+results/_r658bmc_s6_log.txt（38/38 rc0）+fleet/inbox/MSG-2026-10-07-0625 通报 @ " + ISO)
MILESTONE = ("下个里程碑: bm-b ~08:00 trio Q finalize 计划窗观察（Q 1960/2000·r794 声明·r668 first-to-2000 律·"
             "过窗空+hb 陈旧=升级 fleet-note/GM）+bm-a S6 重derive 回执确认（STALE_MIN 接管面已由本轮合法重derive）；"
             "10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r660（HANDOVER 窗）")
NARRATIVE = (
    "S0: 轮首脏=3 自有 daemon 面；pull --rebase --autostash fast-forward 590ba0fe0..1b40d8811"
    "（bm-b r795/796 rebase 窗+r798+bm-a r810 波·零冲突）→S3 post_review 3 NO（T-81 族 json_field 解析错）="
    "本轮 P0：全仓配对 marker census（45 命中=17 真污染+28 良性 auto-saves/probe 件）归因唯一污染提交 "
    "6d8e04b9a [via bm-b r796]·parent 全洁净→treasure_guard restore 分类门（16 件 restorable rc0+token_usage "
    "ledger 类硬拒=行级 union 唯一合法路）→外科愈合 16 件 parent-blob 二进制精确恢复+token_usage union"
    "（逐字段零损失证明：crash_fuse 3602<=3638·machines.default 活树 2,122,710B 超两侧快照→union==parent blob "
    "断言过）→17/17 marker 清零+JSON 全过验证门→fetch 核对零重叠→二次 pull --rebase --autostash 撞 EOL pop 冲突坑"
    "（文件集零重叠仍 pop 失败·17 件恢复面被静默回滚·载荷困 autostash）→r642 家族正法 reset --hard+stash drop+"
    "确定性重放（全载荷可再生核对：恢复面=git blob 确定性/daemon 面=live-wins/post_review 行=复跑补录）→"
    "commit e6b9acfc2（-F commitmsg 文件范式·[via bm-c r658] 机属后缀）推送 6d84d7c7f..e6b9acfc2+fetch+rev-parse+"
    "grep 送达核验（origin/main==e6b9acfc2·探测面 marker 计数 0）→MSG-2026-10-07-0625-bmc 通报（bm-a 重derive "
    "确认面+bm-b 根因两问：pre-commit 钳逃逸+r795 resolver 未接 r796 窗+全机 EOL pop 警示）→post_review 复跑 "
    "45 YES/0 NO/5 WAIT=P0 闭环。S6 38/38 rc0（strategy_scorecard/daily_scorecard/build_status 三腿=bm-a hb 陈旧 "
    "42-44min 触发 O-2100 s2.4 STALE_MIN 合法接管全量重derive·越过恢复态直达新鲜态；market_clock ORANGE_COOL；"
    "token_meter 重derive；golden-week no-op 族诚实）。S7: 双扫 s05+s7close DEC 635C3024/ORD 437E9CDD 双 MATCH 零 "
    "delta·164 ack 零未回执；attrition CLEAN（3 healed 注记照录零主动损失）；四自愈件绿（loop pin=5 no-op+"
    "watchdog+双爪装齐）；trio watch r658=Q 1960/V 2000/D 1626（bm-b 车道推进·计划窗未到·零代烧）；"
    "S4 CODELY 新坑 1 条（外科恢复面×autostash EOL pop 冲突坑·r642 家族新变体）先入主件后同窗续压批："
    "r808+r658 双坑 verbatim 迁 pit-git-resolver.md（r808 1,179B+r658 1,201B·零丢失断言过·receipt "
    "results/_r658bmc_codely_increment.json）主件 30,528→29,347B≤30,720B·域件 30,412B≤线；本地未达 origin "
    "commit 数=0（close 推送前实测）。零弹窗全程 silent-git wrapper。")

RR_LINE = " | ".join([WATERMARK, ISO, "r658 bm-c", "dept:工程/数据", CURRENT, ARTIFACT, MILESTONE, NARRATIVE])

with open(RR, "a", encoding="utf-8", newline="\n") as f:
    f.write(RR_LINE + "\n")

# --- state write-back (round_no 658->659 per S7 increment law) ---
st = json.load(open(ST, encoding="utf-8-sig"))
assert st["round_no"] == 658, "round_no drift: " + str(st["round_no"])
st.update({
    "round_no": 659, "round_no_label": "round 658 (bm-c)",
    "clock_read": ISO, "ts": ISO, "updated": ISO, "updated_at": ISO,
    "last_seen": ISO, "last_seen_at": ISO, "last_ts": ISO,
    "last_round_at": ISO, "last_round_ts": ISO, "last_round_summary": "r658: P0 marker-contamination heal round (17 shared faces, bm-b r796 window; byte-exact parent restore + token ledger union; origin clean at e6b9acfc2; post_review 45/0; S6 38/38 stale-takeover re-derive; QA 5/5; CODELY +1 pit migrated same-window)",
    "current_task": CURRENT, "current_task_at": ISO, "activity_now": CURRENT + " | " + ARTIFACT + " | " + MILESTONE,
    "cpu_pct": 0.3, "cpu_util_pct": 0.3, "cpu_idle_pct": 99.7,
    "free_ram_gb": 3.8, "ram_free_gb": 3.8, "idle_ram_gb": 3.8,
    "gpu_free_vram_mib": 1078, "gpu_free_vram_mb": 1078, "gpu_idle_vram_mib": 1078,
    "gpu_idle_vram_mb": 1078, "gpu_free_mb": 1078, "gpu_idle_mb": 1078,
    "gpu_vram_free_mb": 1078, "gpu_free_mib": 1078,
    "heartbeat_epoch_utc": EPOCH,
    "last_decisions_read_at": ISO, "last_decisions_at": ISO,
    "next": "(a) bm-b ~08:00 trio-Q finalize plan-window watch (r794 declared, r668 law; window empty + hb stale -> fleet-note/GM escalation). (b) bm-a S6 re-derive receipt confirm (stale-takeover faces this round; lane returns when bm-a hb fresh). (c) 10-09 market reopen data-chain re-arm + REGIME_GUARD v3 first bar + compute_audit structural flags re-eval. (d) monthly exam 10-31. (e) next 5x = r660 (HANDOVER window).",
    "note": "r658: P0 heal round (blob live-derived, receipt-backed); QA r658 5/5 explicit --round; S6 38/38; DEC/ORD double-sweep zero-delta 164 ack; attrition CLEAN; CODELY +1 pit (autostash EOL pop) migrated same-window to pit-git-resolver.md, main 29,347B.",
    "verify": "receipts: commit e6b9acfc2 (origin/main verified, marker grep 0) + results/_r658bmc_marker_incident_census.json + results/_r658bmc_surgical_heal_receipt.json + results/_r658bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD MATCH) + qa/smoke-r658.md 5/5 + qa/equity-curve-r658.png + results/_r658bmc_s6_log.txt 38/38 rc0 + results/_attrition_guard_scan.json CLEAN + results/_r658bmc_trio_watch.json + results/_r658bmc_codely_increment.json + results/_r658bmc_qa_runner.out (terminal 5/5) + fleet/inbox/MSG-2026-10-07-0625-bmc-marker-contamination-heal.md",
    "did": "r658 bm-c: P0 conflict-marker contamination heal round. (1) S0: pull --rebase --autostash fast-forward 590ba0fe0..1b40d8811 (bm-b r795/r796 rebase-window wave + r798 + bm-a r810; zero conflict). (2) S3 post_review 3 NO rows (T-81 family json_field parse errors) -> P0: full-repo paired-marker census 45 hits = 17 live contamination (dashboard_status 24 hunks, strategy_scorecard 2 hunks, REPORT/LIVE quartet, status/regime/lhb/futures/fund/token faces) + 28 benign (auto-saves + r505/506 probe artifacts); sole corrupting commit 6d8e04b9a [via bm-b r796], parent blobs all clean. Heal per treasure_guard verdict split: 16 reproducible faces byte-exact parent-blob restore (rc0 restorable) + token_usage.json append-only-ledger class healed via line-level union with zero-loss proof (union==parent blob; crash_fuse 3602<=3638; machines.default file-size snapshots superseded by live tree 2,122,710B). Validation gate 17/17 marker-free + JSON parse pass. Mid-window autostash EOL pop-conflict pit hit (disjoint file sets, pop still failed, restored faces silently rolled back): absorbed per r642 family -- reset --hard + stash drop + deterministic re-apply (all payloads verified regenerable). Commit e6b9acfc2 pushed 6d84d7c7f..e6b9acfc2, delivery-verified (fetch + rev-parse + marker grep 0). Fleet MSG-2026-10-07-0625 (bm-a re-derive confirm face + bm-b root-cause two questions + all-machine EOL caution). post_review re-run 45 YES/0 NO/5 WAIT = P0 closed. (3) S6 38/38 rc0 (strategy_scorecard/daily_scorecard/build_status legs = bm-a hb stale 42-44min -> O-2100 s2.4 STALE_MIN lawful stale-takeover full re-derive by bm-c, faces refreshed past restored states; market_clock ORANGE_COOL; golden-week no-op family honest). (4) S7: double-sweep DEC/ORD zero-delta 164 ack; attrition CLEAN; self-heal 4-piece green (loop pin=5 no-op + watchdog + pre-commit/pre-push claws); trio watch Q 1960/V 2000/D 1626 bm-b lane advancing, plan window not due, zero proxy burn; S4 CODELY +1 pit (autostash EOL pop-conflict, r642 family variant) appended then migrated same-window with r808 to pit-git-resolver.md (zero-loss receipts, main 29,347B <= line); 本地未达 origin commit 数=0.",
})
json.dump(st, open(ST, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# --- heartbeat (epoch int self-verified per smoke F7 law) ---
hb = json.load(open(HB, encoding="utf-8-sig"))
hb.update({
    "last_seen": ISO, "ts": ISO, "clock_read": ISO,
    "heartbeat_epoch_utc": EPOCH,
    "cpu_pct": 0.3, "cpu_idle_pct": 99.7,
    "free_ram_gb": 3.8, "idle_ram_gb": 3.8, "ram_free_gb": 3.8,
    "gpu_free_vram_mib": 1078, "gpu_free_vram_mb": 1078, "gpu_idle_vram_mib": 1078,
    "current_task": CURRENT + " | " + ARTIFACT + " | " + MILESTONE,
    "current_task_at": ISO,
    "verdict": "P0-heal round: origin contamination cleaned (17 faces, commit e6b9acfc2); boards 0 open; SAT alive idle (golden week); trio bm-b lane advancing",
})
json.dump(hb, open(HB, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
check = json.load(open(HB, encoding="utf-8-sig"))
assert isinstance(check["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in check["clock_read"], "clock_read must be T-separated ISO (R262 law)"
print("CLOSE WRITTEN", ISO, "epoch_int=", check["heartbeat_epoch_utc"])
