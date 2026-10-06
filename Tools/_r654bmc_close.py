# -*- coding: utf-8 -*-
"""r654 bm-c close batch: round-report line (canonical path) + state advance
654->655 (AFTER QA pack poll per r640 law; pack ignited with EXPLICIT --round
654 per r758 law, terminal 5/5 polled before this close) + heartbeat
three-line face + epoch int self-verify + watermark keys facts-driven from
results/_r654bmc_s05_facts.json (r583 S4 law, double-sweep s05+s7close).
Pattern credit: Tools/_r650bmc_close.py."""
import json
import os
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---- 0) facts (r583 S4 law: never hand-typed) ----
facts = json.load(open(r"results\_r654bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["dec_sha"]
ord_sha = facts["ord_sha"]
assert facts["dec_delta"] is False and facts["ord_delta"] is False
assert facts["unacked"] == [] and facts["inbox_unread"] == []
assert facts["fleet_orders_total"] == 163
assert len(dec_sha) == 64 and len(ord_sha) == 40
assert facts["shape_assert"] is True
assert facts["round"] == 654

# ---- 1) round-report line (canonical path) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("watermark: 绿（red=false lane healthy·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·SAT 活=Tools 注册面 wave167 bands 在册·board 0 open/176·金周 no-bar 至 10-09）"
       " | {ts} | r654 bm-c | dept:工程/舰队（金周值守轮·非 5x） | 当前活: r654 值守轮收口（S0 pull 净+autostash 零冲突·S6 38/38+QA 包 r654 显式轮标 5/5·双扫零 delta·零新坑）"
       " | 最近实物: qa/smoke-r654.md 5/5（显式 --round 654 零误标·93 trades·determinism=True·equity 800 点终值 1,017,839 面恒等 r642-653）+results/_r654bmc_s6_log.txt（38/38 rc0）+docs/live_usage/LIVE-2026-10-07.md（当日幂等再生）@ {ts}"
       " | 下个里程碑: fund-trio Q 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08（bm-b 车道）；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r655〔HANDOVER 窗〕 | "
       "S0: 轮首树脏=5 本车道面（r653 close-tail addendum+gate-pin+2 sat-engine daemon 面+tail2.py 未跟踪）→pull --rebase --autostash 干净应用（bm-b 在飞波 fabe270a6：fund-trio nulls +4/+5 推进+sat-engine 面）零冲突；"
       "S0.5 双扫（s05+s7close 两腿全清洁）：DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta+fleet orders 163/163 零未回执+inbox 空；bm-a r807「dec acc32216」疑点当轮核销=D-20261007-01/02/03 三行已在我方 635C3024 面（r644 A44C39E0→635C3024 窗已消费·双探针实证我方 face 含该三行）=bm-a 哈希域差异非新面·零漏消费；"
       "S1 48/48；S3: 板 open=0（Codely jobs=0·fleet 176 零 open/46 历史 claimed）·watermark 绿·SAT 活（Tools 面 status rc0·wave167 全在册）·post_review 45 YES/0 NO 零红项·"
       "trio watch r654: V 2000/2000 COMPLETE·Q 1927/2000（+9）·D 1597/2000（+7）——bm-b 正主车道在烧·池 2 ready（fund Q/D faces owner=bm-b keepalive 实证）+TRIAL-LABOR-W14-GENERATE waiting·试用劳力线=trio 在飞判决批已满足零新起草·禁代烧维持；"
       "MSG-0250 回执窗关闭=bm-a 03:28 拾取（processed）+r807 closeout 吸收 forensics（uu probes+r807 resolver·claw-reworded marker samples per existing law）——信息性零 bm-c 义务；"
       "S6 38/38 rc0（dualrun ZERO-DRIFT streak 51 @403 不变面·bm-a 车道面宿主心跳已活 5-6min 由其自 derive=守卫诚实跳计·REPORT/LIVE-2026-10-07 幂等再生·金周 no-bar 族诚实 no-op·token per-round fixed ~12980+8629 粗估·ledger delta=0）；"
       "QA包r654三件显式 --round 654 分离点火 pid31836+轮询终态零误标（5/5·93 trades·determinism=True·equity 800 点终值 1,017,839·png 66,109B·面恒等 r642-653）；"
       "S7 自愈面全绿（loop pin=5 no-op 首跳 04:45·watchdog 幂等重注册 04:44·precommit/prepush 双爪 LF 归一 match·attrition CLEAN 4 台账零 active loss·历史 healed 注记照录）；零新坑零 CODELY append（主件 30,117B 维持·余量 603B）；"
       "本地未达 origin commit 数=0（push+fetch+ls-tree 自证送达）"
       " | 证据=qa/smoke-r654.md 5/5+qa/equity-curve-r654.png+results/_r654bmc_s6_log.txt 38/38+results/_r654bmc_s05_facts.json（双扫 s05+s7close）"
       "+results/_attrition_guard_scan.json CLEAN+results/_r654bmc_trio_watch.json+results/_r654bmc_qa_runner.out（terminal 5/5）+results/post_review/REPORT-20261007.md（45 YES/0 NO）"
       " | 下轮指针：(a) fund-trio Q~2000 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08（bm-b 车道）；(b) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；(c) r655=5x HANDOVER 窗（research/HANDOVER.md r655 行义务）；(d) 月界首考 10-31 装配面\n").format(ts=now)
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("RR appended (canonical path)")

# ---- 2) state advance ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8-sig"))
assert st["round_no"] == 654, "unexpected round_no %s" % st["round_no"]
st["round_no"] = 655
st["round_no_label"] = "round 654 (bm-c)"

did = ("r654 bm-c: golden-week standing-guard round (zero new pits; no P0 tail). "
       "(1) S0: round-start dirty = 5 own-lane faces (r653 close-tail addendum + gate-pin + 2 sat-engine daemon faces + tail2.py untracked); "
       "pull --rebase --autostash applied clean (bm-b in-flight wave fabe270a6: fund-trio nulls +4/+5 + sat-engine faces), zero conflict. "
       "(2) S0.5 double-sweep (s05 + s7close): DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta at both sweeps; fleet orders 163/163 zero unacked; inbox empty. "
       "bm-a r807 'dec acc32216' suspicion reconciled in-round: D-20261007-01/02/03 rows already inside our 635C3024 face (consumed r644 A44C39E0->635C3024 window; dual probe proves face contains the three rows) "
       "= bm-a hash-domain difference, not a new face; zero missed consumption. "
       "(3) S1 smoke 48/48. S3: board open=0 (Codely jobs 0, fleet 176 zero open, 46 historical claimed); watermark green (red=false, next_pick=claimed moneyflow IC source-blocked bm-a lane legal); "
       "SAT alive (Tools face status rc0, wave 167); post_review 45 YES / 0 NO; "
       "trio watch r654: V 2000/2000 COMPLETE, Q 1927/2000 (+9), D 1597/2000 (+7) -- bm-b rightful burner lane; pool 2 ready (fund Q/D faces owner=bm-b keepalive) + TRIAL-LABOR-W14-GENERATE waiting; "
       "trial-labor line satisfied by in-flight trio judge batches, no new drafting, no proxy burn. "
       "MSG-0250 reply window closed: bm-a picked up 03:28 (processed) + r807 closeout absorbed forensics (uu probes + r807 resolver, claw-reworded marker samples per existing law). "
       "(4) S6 chain 38/38 rc0: dualrun ZERO-DRIFT streak 51 @403 unchanged face; bm-a lane-host faces derived by bm-a itself (hb fresh 5-6min, guards honest skip); "
       "REPORT/LIVE-2026-10-07 regenerated idempotent; golden-week no-op family honest; token per-round fixed ~12980+8629 rough, ledger delta 0. "
       "(5) QA pack r654: ignited detached pid 31836 with EXPLICIT --round 654 (r758/r640 law), polled terminal before close -- 5/5, 93 trades, determinism=True, "
       "equity 800 pts final 1,017,839 face-identical r642-r653, png 66,109B, zero mislabel. "
       "(6) S7 self-heal green: loop pin=5 no-op (first fire 04:45), watchdog re-register (04:44), both claws LF-normalized match, attrition CLEAN (4 ledgers, zero active loss). "
       "Zero new pits, zero CODELY append (main 30,117B held, headroom 603B). Delivery: push+fetch+ls-tree self-verify N=0.")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = ("r654: standing-guard round (QA r654 5/5 explicit --round, equity face-identical; S6 38/38; DEC/ORD double-sweep zero-delta 163/163; "
                            "trio V complete Q1927/D1597 bm-b lane; attrition CLEAN; self-heal green; zero new pits; bm-a acc32216 hash-domain reconciled zero missed consumption)")
st["last_action"] = did[:300]
st["ts"] = now
st["updated"] = now
st["updated_at"] = now
st["clock_read"] = now
st["last_seen"] = now
st["last_seen_at"] = now
st["last_run_at"] = now
st["last_decisions_read_at"] = now
st["last_decisions_at"] = now
st["last_decisions_sha"] = dec_sha
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r654 double-sweep s05+s7close both scans = 635C3024 MATCH zero-delta; "
                        "value facts-driven from results/_r654bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r654 double-sweep s05+s7close both scans = 437E9CDD MATCH zero-delta; "
                                "fleet orders 163/163 ack at BOTH S0.5 and S7 close sweeps (double-sweep law); value facts-driven from results/_r654bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = ("r654: standing-guard round; QA r654 5/5 explicit --round; S6 38/38; DEC/ORD 635C3024/437E9CDD double-sweep MATCH; attrition CLEAN; "
              "trio V 2000/2000 complete, Q 1927, D 1597 (bm-b lane); MSG-0250 window closed (bm-a absorbed); zero new pits; main 30,117B held.")
st["next"] = ("(a) fund-trio Q ~2000 completion window: pool dual-flip watch per r668 law; D finalize ~10-08 (bm-b lane). "
              "(b) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar. "
              "(c) r655 = 5x HANDOVER window (research/HANDOVER.md r655 line duty). "
              "(d) monthly exam 10-31 assembly face.")
st["verify"] = ("receipts: qa/smoke-r654.md 5/5 (explicit --round 654, pid 31836) + qa/equity-curve-r654.png + results/_r654bmc_s6_log.txt 38/38 rc0 "
                "+ results/_r654bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD) + results/_attrition_guard_scan.json CLEAN "
                "+ results/_r654bmc_trio_watch.json + results/_r654bmc_qa_runner.out (terminal 5/5) + results/post_review/REPORT-20261007.md (45 YES/0 NO)")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 654->655")

# ---- 3) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8-sig"))
act = ("当前活: r654 值守轮收口（S6 38/38+QA 包 r654 显式轮标 5/5·双扫零 delta·零新坑） | "
       "最近实物: qa/smoke-r654.md（5/5·93 trades·determinism=True·equity 终值 1,017,839 面恒等 r642-653）+results/_r654bmc_s6_log.txt（38/38 rc0）+docs/live_usage/LIVE-2026-10-07.md（当日幂等再生）@ " + now +
       " | 下个里程碑: fund-trio Q 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08（bm-b 车道）；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r655〔HANDOVER 窗〕")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 655, "round_no_label": "round 654 (bm-c)",
    "latest_artifact": ("qa/smoke-r654.md 5/5 (explicit --round 654, zero mislabel; equity 800 pts final 1,017,839 face-identical r642-653) "
                        "+ results/_r654bmc_s6_log.txt 38/38 rc0 + docs/live_usage/LIVE-2026-10-07.md (idempotent regen) @ " + now),
    "next_milestone": ("fund-trio Q completion pool dual-flip watch (r668 law) + D finalize ~10-08 (bm-b lane); 10-09 market reopen "
                       "(data-chain re-arm + regime_guard v3 first bar); monthly exam 10-31; next 5x = r655 (HANDOVER window)"),
    "verdict": ("alive: r654 standing-guard round complete (QA pack r654 5/5 zero-mislabel explicit --round 654; S6 38/38 rc0; smoke 48/48; "
                "board open=0; satengine alive; DEC/ORD double-sweep zero-delta 163/163; attrition CLEAN; post_review 45 YES/0 NO; "
                "trio V complete Q1927/D1597 bm-b rightful lane; MSG-0250 window closed (bm-a absorbed forensics); "
                "bm-a acc3226 hash-domain reconciled zero missed consumption; golden-week no-bar until 10-09)"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"])
