# -*- coding: utf-8 -*-
"""r655 bm-c close batch: round-report line (canonical path) + state advance
655->656 (AFTER QA pack poll per r640 law; pack ignited with EXPLICIT --round
655 per r758 law, terminal 5/5 polled before this close) + heartbeat
three-line face + epoch int self-verify + watermark keys facts-driven from
results/_r655bmc_s05_facts.json (r583 S4 law, double-sweep s05+s7close).
Size declarations DERIVED at close time via git cat-file (r653 close-size law:
never copy a prior receipt's declared size).
Pattern credit: Tools/_r654bmc_close.py."""
import json
import os
import subprocess
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---- 0) facts (r583 S4 law: never hand-typed) ----
facts = json.load(open(r"results\_r655bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["dec_sha"]
ord_sha = facts["ord_sha"]
assert facts["dec_delta"] is False and facts["ord_delta"] is False
assert facts["unacked"] == [] and facts["inbox_unread"] == []
assert facts["fleet_orders_total"] == 163
assert len(dec_sha) == 64 and len(ord_sha) == 40
assert facts["shape_assert"] is True
assert facts["round"] == 655

# ---- 0b) size gate-pin derived at close (r646 gate-pin law + r653 derive law) ----
codely_blob = int(subprocess.check_output(
    ["git", "cat-file", "-s", "HEAD:CODELY.md"]).decode().strip())
assert codely_blob <= 30720, "CODELY.md over 30KB gate: %d" % codely_blob

# ---- 1) round-report line (canonical path) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("watermark: 绿（red=false lane healthy·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·SAT 活=Tools 注册面 wave167 bands 在册·board 0 open/176·金周 no-bar 至 10-09）"
       " | {ts} | r655 bm-c | dept:工程/舰队（5x HANDOVER 窗） | 当前活: r655 5x HANDOVER 窗（r651-655 五增量窗核对行落盘 research/HANDOVER.md+QA 包 r655 显式轮标 5/5+S6 38/38+双扫零 delta·零新坑）"
       " | 最近实物: research/HANDOVER.md r655 行（r651-655 增量窗五轮核对·统一链 772,812 实读）+qa/smoke-r655.md 5/5（93 trades·determinism=True·equity 800 点终值 1,017,839 面恒等 r642-654）+results/_r655bmc_s6_log.txt（38/38 rc0）@ {ts}"
       " | 下个里程碑: fund-trio Q 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08（bm-b 车道）；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+CA 金周结构旗 re-eval；月界首考 10-31；下个 5x=r660 | "
       "S0: 轮首树脏=4 本车道 daemon 面（autofill+dispatcher+2 sat-engine live-wins）→pull --rebase --autostash already-up-to-date 零冲突；"
       "S0.5 双扫（s05+s7close 两腿全清洁）：DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta+fleet orders 163/163 零未回执+inbox 空；"
       "S1 48/48；S3: 板 open=0（Codely jobs=0·fleet 176 零 open/46 历史 claimed）·watermark 绿（next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法）·SAT 活（Tools 面 status rc0·wave167 bands 全在册）·post_review 45 YES/0 NO 零红项·"
       "trio watch r655: V 2000/2000 COMPLETE·Q 1927/2000·D 1597/2000 轮间零增长=采样面——owner=bm-b keepalive 04:34:10 新鲜·bm-b 正主车道在烧·池 2 ready（fund Q/D faces）+TRIAL-LABOR-W14-GENERATE waiting 治理停放维持·试用劳力线=trio 在飞判决批已满足零新起草·禁代烧维持；"
       "S6 38/38 rc0（dualrun ZERO-DRIFT streak 51 @403 不变面·bm-a hb 陈 25min→4 面 stale-takeover derive 合法〔t35_open_fill/t35_export/daily_scorecard/build_status·O-2100 s2.4〕·REPORT/LIVE-2026-10-07 当日幂等再生·金周 no-bar 族诚实 no-op·token per-round fixed ~12980+8455 粗估·ledger delta=0）；"
       "QA包r655三件显式 --round 655 分离点火 pid34136+轮询终态零误标（5/5·93 trades·determinism=True·equity 800 点终值 1,017,839·png 66,254B·面恒等 r642-654）；"
       "HANDOVER r655 行=本核对轮主产出（r651-655 五增量窗：r651 D-06 mini-split+r653 close-size 收据-实测律+r654 bm-a r807 acc32216 和解+D-06 in-window gate fix 两连收口）；"
       "S7 自愈面全绿（loop pin=5 no-op 首跳 05:15·watchdog 幂等重注册 05:08·precommit/prepush 双爪 LF 归一 match·attrition CLEAN 4 台账零 active loss·历史 healed 注记照录）；零新坑零 CODELY append（主件 {cb}B 实测 derive·余量 {hr}B）；"
       "本地未达 origin commit 数=0（push+fetch+ls-tree 自证送达）"
       " | 证据=qa/smoke-r655.md 5/5+qa/equity-curve-r655.png+results/_r655bmc_s6_log.txt 38/38+results/_r655bmc_s05_facts.json（双扫 s05+s7close）"
       "+results/_attrition_guard_scan.json CLEAN+results/_r655bmc_trio_watch.json+results/_r655bmc_qa_runner.out（terminal 5/5）+results/post_review/REPORT-20261007.md（45 YES/0 NO）+research/HANDOVER.md r655 行"
       " | 下轮指针：(a) fund-trio Q~2000 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08（bm-b 车道）；(b) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+compute_audit 金周结构旗 re-eval；(c) 下个 5x=r660；(d) 月界首考 10-31 装配面\n").format(
           ts=now, cb=codely_blob, hr=30720 - codely_blob)
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("RR appended (canonical path)")

# ---- 2) state advance ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8-sig"))
assert st["round_no"] == 655, "unexpected round_no %s" % st["round_no"]
st["round_no"] = 656
st["round_no_label"] = "round 655 (bm-c)"

did = ("r655 bm-c: 5x HANDOVER window round (zero new pits; no P0 tail). "
       "(1) S0: round-start dirty = 4 own-lane daemon faces (autofill/dispatcher/2 sat-engine live-wins); pull --rebase --autostash already-up-to-date, zero conflict. "
       "(2) S0.5 double-sweep (s05 + s7close): DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta at both sweeps; fleet orders 163/163 zero unacked; inbox empty. "
       "(3) S1 smoke 48/48. S3: board open=0 (Codely jobs 0, fleet 176 zero open, 46 historical claimed); watermark green (next_pick=claimed moneyflow IC source-blocked bm-a lane legal); "
       "SAT alive (Tools face status rc0, wave 167 bands); post_review 45 YES / 0 NO; "
       "trio watch r655: V 2000/2000 COMPLETE, Q 1927/2000, D 1597/2000 zero inter-round growth = sampling face; owner=bm-b keepalive 04:34:10 fresh, bm-b rightful burner lane; "
       "pool 2 ready (fund Q/D faces owner=bm-b) + TRIAL-LABOR-W14-GENERATE waiting (governance park held); trial-labor line satisfied by in-flight trio judge batches, no new drafting, no proxy burn. "
       "(4) S6 chain 38/38 rc0: dualrun ZERO-DRIFT streak 51 @403 unchanged face; bm-a hb stale 25min -> 4 shared faces stale-takeover derive by bm-c (O-2100 s2.4); "
       "REPORT/LIVE-2026-10-07 regenerated idempotent; golden-week no-op family honest; token per-round fixed ~12980+8455 rough, ledger delta 0. "
       "(5) QA pack r655: ignited detached pid 34136 with EXPLICIT --round 655 (r758/r640 law), polled terminal before close -- 5/5, 93 trades, determinism=True, "
       "equity 800 pts final 1,017,839 face-identical r642-r654, png 66,254B, zero mislabel. "
       "(6) 5x HANDOVER duty: research/HANDOVER.md r655 line landed (window r651-655: r651 D-06 mini-split 30,570->26,496B; r653 close-size derive law; "
       "r654 bm-a acc32216 hash-domain reconciliation + in-window gate fix 31,297->29,509B; unified chain 772,812 live-read @ n1_w167). "
       "(7) S7 self-heal green: loop pin=5 no-op (first fire 05:15), watchdog re-register (05:08), both claws LF-normalized match, attrition CLEAN (4 ledgers, zero active loss). "
       "Zero new pits, zero CODELY append (main %dB derived at close via git cat-file, headroom %dB). Delivery: push+fetch+ls-tree self-verify N=0." % (codely_blob, 30720 - codely_blob))
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = ("r655: 5x HANDOVER round (HANDOVER r655 line landed window r651-655; QA r655 5/5 explicit --round, equity face-identical; S6 38/38; "
                            "DEC/ORD double-sweep zero-delta 163/163; trio V complete Q1927/D1597 bm-b lane zero-growth sampling face; attrition CLEAN; self-heal green; zero new pits)")
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
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r655 double-sweep s05+s7close both scans = 635C3024 MATCH zero-delta; "
                        "value facts-driven from results/_r655bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r655 double-sweep s05+s7close both scans = 437E9CDD MATCH zero-delta; "
                                "fleet orders 163/163 ack at BOTH S0.5 and S7 close sweeps (double-sweep law); value facts-driven from results/_r655bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = ("r655: 5x HANDOVER window round; HANDOVER r651-655 line landed; QA r655 5/5 explicit --round; S6 38/38; DEC/ORD 635C3024/437E9CDD double-sweep MATCH; attrition CLEAN; "
              "trio V 2000/2000 complete, Q 1927, D 1597 zero-growth sampling face (bm-b lane, keepalive 04:34:10 fresh); zero new pits; main %dB derived at close." % codely_blob)
st["next"] = ("(a) fund-trio Q ~2000 completion window: pool dual-flip watch per r668 law; D finalize ~10-08 (bm-b lane). "
              "(b) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar + compute_audit golden-week structural flags re-eval. "
              "(c) monthly exam 10-31 assembly face. "
              "(d) next 5x = r660.")
st["verify"] = ("receipts: qa/smoke-r655.md 5/5 (explicit --round 655, pid 34136) + qa/equity-curve-r655.png + results/_r655bmc_s6_log.txt 38/38 rc0 "
                "+ results/_r655bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD) + results/_attrition_guard_scan.json CLEAN "
                "+ results/_r655bmc_trio_watch.json + results/_r655bmc_qa_runner.out (terminal 5/5) + results/post_review/REPORT-20261007.md (45 YES/0 NO) "
                "+ research/HANDOVER.md r655 line")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 655->656")

# ---- 3) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8-sig"))
act = ("当前活: r655 5x HANDOVER 窗收口（research/HANDOVER.md r651-655 五增量窗核对行落盘+QA 包 r655 显式轮标 5/5+S6 38/38+双扫零 delta·零新坑） | "
       "最近实物: research/HANDOVER.md r655 行（r651-655 窗·统一链 772,812 实读）+qa/smoke-r655.md（5/5·93 trades·determinism=True·equity 终值 1,017,839 面恒等 r642-654）+results/_r655bmc_s6_log.txt（38/38 rc0）@ " + now +
       " | 下个里程碑: fund-trio Q 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08（bm-b 车道）；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+CA 金周结构旗 re-eval；月界首考 10-31；下个 5x=r660")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 656, "round_no_label": "round 655 (bm-c)",
    "latest_artifact": ("research/HANDOVER.md r655 line (window r651-655 five-round increment check; unified chain 772,812 live-read @ n1_w167) "
                        "+ qa/smoke-r655.md 5/5 (explicit --round 655, zero mislabel; equity 800 pts final 1,017,839 face-identical r642-654) "
                        "+ results/_r655bmc_s6_log.txt 38/38 rc0 @ " + now),
    "next_milestone": ("fund-trio Q completion pool dual-flip watch (r668 law) + D finalize ~10-08 (bm-b lane); 10-09 market reopen "
                       "(data-chain re-arm + regime_guard v3 first bar + compute_audit flags re-eval); monthly exam 10-31; next 5x = r660"),
    "verdict": ("alive: r655 5x HANDOVER round complete (HANDOVER r651-655 line landed; QA pack r655 5/5 zero-mislabel explicit --round 655; S6 38/38 rc0; smoke 48/48; "
                "board open=0; satengine alive; DEC/ORD double-sweep zero-delta 163/163; attrition CLEAN; post_review 45 YES/0 NO; "
                "trio V complete Q1927/D1597 zero-growth sampling face bm-b rightful lane; zero new pits; golden-week no-bar until 10-09)"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"])
