# -*- coding: utf-8 -*-
"""r660 bm-c close batch: round-report line (canonical path) + state advance
660->661 (AFTER QA pack poll per r640 law; pack ignited with EXPLICIT --round
660 per r758 law, terminal 5/5 polled before this close) + heartbeat
three-line face + epoch int self-verify + watermark keys facts-driven from
results/_r660bmc_s05_facts.json (r583 S4 law, double-sweep s05+s7close).
Size declarations DERIVED at close time via git cat-file (r653 close-size law:
never copy a prior receipt's declared size).
Inbox face (differs from r655 empty-inbox assert): own MSG-2026-10-07-0625
stays in fleet/inbox awaiting bm-a (re-derive confirm) + bm-b (root-cause
answers) action faces -- both peer heartbeats predate the 06:25 notice, so
moving it now would risk peer miss; r659 precedent "awaiting peers" held.
Pattern credit: Tools/_r655bmc_close.py."""
import json
import os
import subprocess
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---- 0) facts (r583 S4 law: never hand-typed) ----
facts = json.load(open(r"results\_r660bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["dec_sha"]
ord_sha = facts["ord_sha"]
assert facts["dec_delta"] is False and facts["ord_delta"] is False
assert facts["unacked"] == []
assert facts["inbox_unread"] == ["MSG-2026-10-07-0625-bmc-marker-contamination-heal.md"]
assert facts["fleet_orders_total"] == 163
assert len(dec_sha) == 64 and len(ord_sha) == 40
assert facts["shape_assert"] is True
assert facts["round"] == 660

# ---- 0b) size gate-pin derived at close (r646 gate-pin law + r653 derive law) ----
codely_blob = int(subprocess.check_output(
    ["git", "cat-file", "-s", "HEAD:CODELY.md"]).decode().strip())
assert codely_blob <= 30720, "CODELY.md over 30KB gate: %d" % codely_blob

# ---- 1) round-report line (canonical path) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("watermark: 绿（red=false lane healthy·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·SAT 活=Tools 注册面 wave168 bands 在册·board 0 open/176·金周 no-bar 至 10-09）"
       " | {ts} | r660 bm-c | dept:工程/舰队（5x HANDOVER 窗） | 当前活: r660 5x HANDOVER 窗（HANDOVER r656-660 五轮核对行落盘 research/HANDOVER.md+QA 包 r660 显式轮标 5/5+S6 38/38+双扫零 delta·零新坑）"
       " | 最近实物: research/HANDOVER.md r660 行（r656-660 窗·统一链 775,012 实读·marker 污染治愈战役窗 r658 e6b9acfc2+r659 恢复+r656 机属判别律）+qa/smoke-r660.md 5/5（93 trades·determinism=True·equity 800 点终值 1,017,839 面恒等 r642-659）+results/_r660bmc_s6_log.txt（38/38 rc0）@ {ts}"
       " | 下个里程碑: bm-b trio-Q finalize 计划窗观察（Q 1968/2000·bm-b hb 06:15 声明 eta ~07:47·r794 计划·r668 first-to-2000 律·过窗空+hb 陈旧=升级 fleet-note/GM）+MSG-0625 bm-a/bm-b 动作面回执窗；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+CA 金周结构旗 re-eval；月界首考 10-31；下个 5x=r665 | "
       "S0: 轮首树脏=4 本车道 daemon 面（autofill+dispatcher+2 sat-engine live-wins）→pull --rebase --autostash already-up-to-date 零冲突；"
       "S0.5 双扫（s05+s7close 两腿全清洁）：DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta+fleet orders 163/163 零未回执+inbox=own MSG-0625 awaiting peers（bm-c 面已毕=治愈 e6b9acfc2 送达+r659 吸收面已历·bm-a/bm-b 心跳 05:56/06:15 均早于 06:25 通报=未读面如实·留件待其动作面回执）；"
       "S1 48/48；S3: 板 open=0（Codely jobs=0·fleet 176 零 open/46 历史 claimed）·watermark 绿（next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法）·SAT 活（Tools 面 status rc0·wave168 bands 全在册）·post_review 45✓/0✗/5🟡 零红项·"
       "trio watch r660: V 2000/2000 COMPLETE·Q 1968/2000·D 1634/2000 bm-b 正主车道推进（hb 06:15 eta Q ~07:47/D ~12:22·r794 声明计划窗未到=零失约·G4 r638 fallback armed）·池 2 ready（fund Q/D faces owner=bm-b）+TRIAL-LABOR-W14-GENERATE waiting 治理停放维持·试用劳力线=trio 在飞判决批已满足零新起草·禁代烧维持；"
       "S6 38/38 rc0（dualrun ZERO-DRIFT streak 51 @403 不变面·bm-a hb 陈 55min→4 面 stale-takeover derive 合法〔t35_open_fill/t35_export/daily_scorecard/build_status·O-2100 s2.4〕·CA supply_gap+supply_floor breach=已知金周结构旗 re-eval 10-09+·py_watermark insufficient_history〔n=2·12.9min 窗〕+板清+金周=合法 idle 白话面·REPORT/LIVE-2026-10-07 当日幂等再生·金周 no-bar 族诚实 no-op·token per-round fixed ~12980+8669 粗估·ledger delta=0）；"
       "QA包r660三件显式 --round 660 分离点火 pid5676+轮询终态零误标（5/5·93 trades·determinism=True·equity 800 点终值 1,017,839·png 66,248B·面恒等 r642-659）；"
       "HANDOVER r660 行=本核对轮主产出（r656-660 五增量窗：r656 commit 机属判别律+r658 marker 污染 P0 治愈 e6b9acfc2+MSG-0625 全机通报+r659 死尾吸收恢复+统一链 772,812→775,012 前移〔W168 finalize bm-a r809〕）；"
       "S7 自愈面全绿（loop pin=5 no-op 首跳 06:55·watchdog 幂等重注册·precommit/prepush 双爪 LF 归一重装·attrition CLEAN 4 台账零 active loss·历史 healed 注记照录）；零新坑零 CODELY append（主件 {cb}B 实测 derive·余量 {hr}B）；"
       "本地未达 origin commit 数=0（push+fetch+ls-tree 自证送达）"
       " | 证据=qa/smoke-r660.md 5/5+qa/equity-curve-r660.png+results/_r660bmc_s6_log.txt 38/38+results/_r660bmc_s05_facts.json（双扫 s05+s7close）"
       "+results/_attrition_guard_scan.json CLEAN+results/_r660bmc_trio_watch.json+results/_r660bmc_qa_runner.out（terminal 5/5）+results/post_review/REPORT-20261007.md（45✓/0✗/5🟡）+research/HANDOVER.md r660 行"
       " | 下轮指针：(a) bm-b trio-Q finalize 计划窗 ~07:47 观察（过窗空+hb 陈旧→fleet-note/GM 升级）；(b) MSG-0625 bm-a/bm-b 动作面回执收取（bm-a re-derive 确认+bm-b 双根因答案）；(c) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+compute_audit 金周结构旗 re-eval；(d) 月界首考 10-31 装配面；(e) 下个 5x=r665\n").format(
           ts=now, cb=codely_blob, hr=30720 - codely_blob)
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("RR appended (canonical path)")

# ---- 2) state advance ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8-sig"))
assert st["round_no"] == 660, "unexpected round_no %s" % st["round_no"]
st["round_no"] = 661
st["round_no_label"] = "round 660 (bm-c)"

did = ("r660 bm-c: 5x HANDOVER window round (zero new pits; no P0 tail). "
       "(1) S0: round-start dirty = 4 own-lane daemon faces (autofill/dispatcher/2 sat-engine live-wins); pull --rebase --autostash already-up-to-date, zero conflict. "
       "(2) S0.5 double-sweep (s05 + s7close): DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta at both sweeps; fleet orders 163/163 zero unacked; "
       "inbox = own MSG-0625 awaiting peers (bm-c face complete: heal e6b9acfc2 delivery-verified + caution path already exercised in r659 absorb; "
       "bm-a hb 05:56 / bm-b hb 06:15 both predate the 06:25 notice = unread face honest, left in inbox for their action-face receipts). "
       "(3) S1 smoke 48/48. S3: board open=0 (Codely jobs 0, fleet 176 zero open, 46 historical claimed); watermark green (red=false lane healthy, next_pick=claimed moneyflow IC source-blocked bm-a lane legal); "
       "SAT alive (Tools face status rc0, wave 168 bands); post_review 45 YES / 0 NO / 5 WAIT zero P0; "
       "trio watch r660: V 2000/2000 COMPLETE, Q 1968/2000, D 1634/2000 advancing on bm-b lane (hb 06:15 eta Q ~07:47 / D ~12:22, r794 declared plan window not due, zero proxy burn double-burn red line); "
       "pool 2 ready (fund Q/D faces owner=bm-b) + TRIAL-LABOR-W14-GENERATE waiting (governance park held); trial-labor line satisfied by in-flight trio judge batches, no new drafting. "
       "(4) S6 chain 38/38 rc0: dualrun ZERO-DRIFT streak 51 @403 unchanged face; bm-a hb stale 55min -> 4 shared host faces stale-takeover derive by bm-c lawful (O-2100 s2.4); "
       "CA supply_gap + supply_floor breach = known golden-week structural flags re-eval 10-09+; py_watermark insufficient_history (n=2, 12.9min window) + board clear + golden week = legal idle face; "
       "REPORT/LIVE-2026-10-07 regenerated idempotent; golden-week no-op family honest; token per-round fixed ~12980+8669 rough, ledger delta 0. "
       "(5) QA pack r660: ignited detached pid 5676 with EXPLICIT --round 660 (r758/r640 law), polled terminal before close -- 5/5, 93 trades, determinism=True, "
       "equity 800 pts final 1,017,839 face-identical r642-659, png 66,248B, zero mislabel. "
       "(6) 5x HANDOVER duty: research/HANDOVER.md r660 line landed (window r656-660: r656 commit-attribution via-suffix law; r658 marker-contamination P0 heal e6b9acfc2 + MSG-0625 fleet notice; "
       "r659 stranded close-tail absorb + EDITOR-unset continue cure; unified chain 772,812 -> 775,012 live-read @ n1_w168, W169 prereg building bm-a r811 lane). "
       "(7) S7 self-heal green: loop pin=5 no-op (first fire 06:55), watchdog idempotent re-register, both claws LF-normalized install, attrition CLEAN (4 ledgers, zero active loss). "
       "Zero new pits, zero CODELY append (main %dB derived at close via git cat-file, headroom %dB). Delivery: push+fetch+ls-tree self-verify N=0." % (codely_blob, 30720 - codely_blob))
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = ("r660: 5x HANDOVER round (HANDOVER r656-660 line landed; QA r660 5/5 explicit --round, equity face-identical; S6 38/38; "
                            "DEC/ORD double-sweep zero-delta 163/163; trio V complete Q1968/D1634 bm-b lane; attrition CLEAN; self-heal green; zero new pits)")
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
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r660 double-sweep s05+s7close both scans = 635C3024 MATCH zero-delta; "
                        "value facts-driven from results/_r660bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r660 double-sweep s05+s7close both scans = 437E9CDD MATCH zero-delta; "
                                "fleet orders 163/163 ack at BOTH S0.5 and S7 close sweeps (double-sweep law); value facts-driven from results/_r660bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = ("r660: 5x HANDOVER window round; HANDOVER r656-660 line landed; QA r660 5/5 explicit --round; S6 38/38; DEC/ORD 635C3024/437E9CDD double-sweep MATCH; attrition CLEAN; "
              "trio V 2000/2000 complete, Q 1968, D 1634 bm-b lane; inbox own MSG-0625 awaiting peers; zero new pits; main %dB derived at close." % codely_blob)
st["next"] = ("(a) bm-b trio-Q finalize plan-window watch ~07:47 (r794 declared, r668 first-to-2000 law; window empty + hb stale -> fleet-note/GM escalation). "
              "(b) MSG-0625 bm-a/bm-b action-face receipts (bm-a re-derive confirm + bm-b root-cause answers). "
              "(c) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar + compute_audit golden-week structural flags re-eval. "
              "(d) monthly exam 10-31 assembly face. "
              "(e) next 5x = r665.")
st["verify"] = ("receipts: qa/smoke-r660.md 5/5 (explicit --round 660, pid 5676) + qa/equity-curve-r660.png + results/_r660bmc_s6_log.txt 38/38 rc0 "
                "+ results/_r660bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD) + results/_attrition_guard_scan.json CLEAN "
                "+ results/_r660bmc_trio_watch.json + results/_r660bmc_qa_runner.out (terminal 5/5) + results/post_review/REPORT-20261007.md (45 YES/0 NO/5 WAIT) "
                "+ research/HANDOVER.md r660 line")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 660->661")

# ---- 3) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8-sig"))
act = ("当前活: r660 5x HANDOVER 窗收口（research/HANDOVER.md r656-660 五增量窗核对行落盘+QA 包 r660 显式轮标 5/5+S6 38/38+双扫零 delta·零新坑） | "
       "最近实物: research/HANDOVER.md r660 行（r656-660 窗·统一链 775,012 实读·marker 污染治愈战役窗 r658 e6b9acfc2+r659 恢复+r656 机属判别律）+qa/smoke-r660.md（5/5·93 trades·determinism=True·equity 终值 1,017,839 面恒等 r642-659）+results/_r660bmc_s6_log.txt（38/38 rc0）@ " + now +
       " | 下个里程碑: bm-b trio-Q finalize 计划窗观察（Q 1968/2000·bm-b hb 06:15 声明 eta ~07:47·r794 计划·r668 first-to-2000 律·过窗空+hb 陈旧=升级 fleet-note/GM）+MSG-0625 bm-a/bm-b 动作面回执窗；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+CA 金周结构旗 re-eval；月界首考 10-31；下个 5x=r665")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 661, "round_no_label": "round 660 (bm-c)",
    "latest_artifact": ("research/HANDOVER.md r660 line (window r656-660 five-round increment check; unified chain 775,012 live-read @ n1_w168) "
                        "+ qa/smoke-r660.md 5/5 (explicit --round 660, zero mislabel; equity 800 pts final 1,017,839 face-identical r642-659) "
                        "+ results/_r660bmc_s6_log.txt 38/38 rc0 @ " + now),
    "next_milestone": ("bm-b trio-Q finalize plan-window watch ~07:47 (r794 declared, r668 first-to-2000 law) + D finalize ~12:22/10-08 (bm-b lane); MSG-0625 bm-a/bm-b action-face receipts; "
                       "10-09 market reopen (data-chain re-arm + regime_guard v3 first bar + compute_audit flags re-eval); monthly exam 10-31; next 5x = r665"),
    "verdict": ("alive: r660 5x HANDOVER round complete (HANDOVER r656-660 line landed; QA pack r660 5/5 zero-mislabel explicit --round 660; S6 38/38 rc0; smoke 48/48; "
                "board open=0; satengine alive wave168; DEC/ORD double-sweep zero-delta 163/163; attrition CLEAN; post_review 45 YES/0 NO; "
                "trio V complete Q1968/D1634 bm-b rightful lane; zero new pits; golden-week no-bar until 10-09; "
                "inbox = own MSG-0625 awaiting bm-a/bm-b action faces (their hbs predate notice)"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"])
