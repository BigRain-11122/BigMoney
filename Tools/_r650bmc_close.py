# -*- coding: utf-8 -*-
"""r650 bm-c close batch: round-report line (canonical path, r643+ continuity)
+ state advance 650->651 (AFTER QA pack poll per r640 law; pack ignited with
explicit --round 650 per r758 law -> zero mislabel verified 5/5) + heartbeat
three-line face + epoch int self-verify + watermark keys facts-driven from
results/_r650bmc_s05_facts.json (r583 S4 law, double-sweep s05+s7close).
Pattern credit: Tools/_r649bmc_close.py."""
import json
import os
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---- 0) facts (r583 S4 law: never hand-typed) ----
facts = json.load(open(r"results\_r650bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["decisions_sha256"]
ord_sha = facts["orders_sha1"]
assert facts["dec_match_prev"] is True and facts["ord_match_prev"] is True
assert facts["unacked_count"] == 0, "unacked orders at close sweep!"
assert len(dec_sha) == 64 and len(ord_sha) == 40
assert facts["sweep"] == "s7close", "close must consume the s7close sweep face"

# ---- 1) round-report line (canonical path, r643+ continuity) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("watermark: 绿（red=false lane healthy·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·SAT 活=Tools 注册面 wave167 bands 在册·W168 席位=bm-a 已公示 processed·board 0 open/176·金周 no-bar 至 10-09）"
       " | {ts} | r650 bm-c | dept:工程/舰队（金周值守轮·5x HANDOVER 窗） | 当前活: r650 五倍数核对轮（HANDOVER r650 行落盘+S6 38/38+QA 包 r650 显式轮标零误标+trio watch+自愈全绿）"
       " | 最近实物: research/HANDOVER.md r650 5x 行（增量窗 r646-650）+qa/smoke-r650.md 5/5（显式 --round 650 零误标·equity 800 点终值 1,017,839·93 trades·determinism=True·面恒等 r642-649）@ {ts}"
       " | 下个里程碑: fund-trio Q 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08（bm-b 车道）；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r655 | "
       "S0: 轮首树脏=3 本车道 daemon 面（autofill+satengine 双面）→定向 checkpoint commit 3abb4f70e（r642 净树零 autostash 根治律）→pull --rebase 再撞 daemon 活写（引擎 tick 每轮自写态面）→daemon live-lane 面定向 stash push→pull --rebase 干净（up to date+ahead 1）→stash pop 零冲突还原（daemon 面 live-wins·禁 discard=防双烧丢账）"
       "；S0.5 双扫（s05+s7close）DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta+fleet orders 164/164 零未回执（两腿全清洁）；S1 48/48；"
       "S3: 板 open=0（Codely jobs=0·fleet 176 件零 open/零 in_progress·46 皆历史 claimed）·watermark 绿（red=false·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法）·SAT 活（Tools 注册面 status rc0·wave167 bands 全在册 dedup 12/12）·"
       "fund-trio=bm-b 正主车道在烧（V 2000/2000 COMPLETE·Q 1883/2000·D 1559/2000·r650bmc_trio_watch 实读·crash-fuse 拒非 burner 守门正确·本机 watch-only 禁代烧）·"
       "W168 席位=bm-a 属主（A 384_404..386_403/B 386_404..386_603·E36 第 27 例·席位 MSG 收讫 processed·反重复零起草）·试用劳力线=trio 在飞判决批已满足·不触发新起草；"
       "S6 38/38 rc0（dualrun ZERO-DRIFT streak 51 @403 entries·REPORT/LIVE-2026-10-07 再生·四 bm-a 宿主面 stale-takeover derive 合法〔hb 陈 71min·O-2100 s2.4〕·t24_prospect enforce 请求→诚实降级 shadow〔date gate〕·金周 no-bar·compute_audit FLAG:supply_gap,supply_floor 已知结构旗〔pool ready=2·trio 占火力·复市 10-09+ 再评〕如实照录）；"
       "QA包r650三件显式 --round 650 分离点火 pid18192+轮询终态零误标（5/5·93 trades·determinism=True·equity 800 点终值 1,017,839·png 66,319B·面恒等 r642-649）；"
       "attrition CLEAN（4 台账零 active loss·历史 healed 注记照录）+inbox 处理 1 件（W168 席位 MSG→processed·bm-a 信息性零 bm-c 义务）+自愈面全绿（loop pin=5 no-op 03:35 首跳·watchdog 幂等重注册 03:28 首跳·precommit/prepush 双爪 LF 归一 match）；"
       "**5x HANDOVER 义务**：research/HANDOVER.md r650 5x 行落盘（增量窗 r646-650 五轮全景+产物清单漂移+统一链 772,812 实读前移〔live head=n1_w167_results.json science_gates.ledger.total 实测·facts 驱动 results/_r650bmc_handover_facts.json〕）；"
       "token 行=per-round fixed context ~ 12980+8482 tokens（粗估）·ledger delta=0"
       " | 证据=qa/smoke-r650.md 5/5+qa/equity-curve-r650.png+results/_r650bmc_s6_log.txt 38/38+results/_r650bmc_s05_facts.json（双扫）"
       "+results/_attrition_guard_scan.json+results/_r650bmc_handover_facts.json+results/_r650bmc_trio_watch.json+research/HANDOVER.md r650 行"
       " | 下轮指针：(a) fund-trio Q~2000 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08（bm-b 车道）；(b) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；"
       "(c) bm-a MSG-2026-10-07-0250 回执 watch（污染自审）；(d) 月界首考 10-31 装配面；下个 5x=r655\n").format(ts=now)
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("RR appended (canonical path)")

# ---- 2) state advance ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8"))
assert st["round_no"] == 650, "unexpected round_no %s" % st["round_no"]
st["round_no"] = 651
st["round_no_label"] = "round 650 (bm-c)"

did = ("r650 bm-c: golden-week 5x HANDOVER-window standing guard round (HANDOVER r650 line + QA pack r650 + S6 38/38 + trio watch + "
       "attrition CLEAN + self-heal green; zero new pits -- all standing faces). "
       "(1) S0: round-start dirty tree = 3 own-lane daemon faces -> targeted checkpoint commit 3abb4f70e (r642 clean-tree zero-autostash law); "
       "pull --rebase hit engine-tick live-write race -> daemon-lane targeted stash push -> clean pull (up to date, ahead 1) -> stash pop zero-conflict restore "
       "(daemon live-wins; discard forbidden = double-burn protection). "
       "(2) S0.5 double-sweep (s05 + s7close): DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta at both sweeps; fleet orders 164/164 zero unacked. "
       "(3) S1 smoke 48/48. S3: board open=0 (Codely jobs 0, fleet 176 zero open/in_progress, 46 all historical claimed); watermark green "
       "(red=false, next_pick=claimed moneyflow IC source-blocked bm-a lane legal); SAT alive (Tools registered face status rc0, wave 167 bands, W168 seat bm-a). "
       "Fund-trio = bm-b rightful-burner lane in flight (V 2000/2000 COMPLETE, Q 1883/2000, D 1559/2000 per _r650bmc_trio_watch.json; "
       "crash-fuse keeps refusing non-burner machines; no proxy burn by bm-c). W168 seat MSG received -> processed (bm-a owned, zero bm-c drafting, anti-dup). "
       "Trial-labor line satisfied by in-flight trio judge batches, no new drafting. "
       "(4) S6 chain 38/38 rc0: dualrun ZERO-DRIFT streak 51 @403; REPORT/LIVE-2026-10-07 regenerated; four bm-a-host faces stale-takeover derived legally "
       "(hb stale 71min); compute_audit FLAG:supply_gap,supply_floor = known golden-week structural face (pool ready=2, trio holds the fire; re-eval 10-09+); "
       "t24_prospect enforce requested -> honest shadow downgrade (date gate); golden-week no-bar until 10-09. "
       "(5) QA pack r650: ignited detached pid 18192 with EXPLICIT --round 650 (r758/r640 law), polled terminal before close -- 5/5, 93 trades, "
       "determinism=True, equity 800 points final 1,017,839 face-identical r642-r649, png 66,319B, zero mislabel. "
       "(6) Attrition guard CLEAN (4 ledgers, zero active loss). Inbox: W168 seat MSG processed (informational); sole remaining file = own r648 outbound "
       "MSG-0250 pending bm-a pickup. Self-heal green: loop pin=5 no-op (first fire 03:35), watchdog idempotent re-register (03:28), claws installed LF-normalized. "
       "(7) 5x HANDOVER duty discharged: research/HANDOVER.md r650 line inserted (increment window r646-650 full-face + product-list drift + "
       "unified ledger head 772,812 facts-driven read from n1_w167_results.json science_gates.ledger.total, probe results/_r650bmc_handover_facts.json).")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = ("r650: golden-week 5x HANDOVER window round (HANDOVER r650 line r646-650 + QA r650 5/5 zero-mislabel + S6 38/38 + "
                            "DEC/ORD double-sweep zero-delta 164/164 + attrition CLEAN + self-heal green; trio V complete Q1883/D1559 bm-b lane; "
                            "W168 seat bm-a processed; unified chain 772,812)")
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
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r650 double-sweep s05+s7close both scans = 635C3024 MATCH zero-delta; "
                        "value facts-driven from results/_r650bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r650 double-sweep s05+s7close both scans = 437E9CDD MATCH zero-delta; "
                                "fleet orders 164/164 ack at BOTH S0.5 and S7 close sweeps (double-sweep law); value facts-driven from results/_r650bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = ("r650: 5x HANDOVER window round; HANDOVER r650 line (r646-650) landed; QA r650 5/5 explicit --round; S6 38/38; "
              "DEC/ORD 635C3024/437E9CDD double-sweep MATCH; attrition CLEAN; unified chain 772,812 (W167 finalize); "
              "trio V 2000/2000 complete, Q 1883, D 1559 (bm-b lane); W168 seat bm-a processed; zero new pits.")
st["next"] = ("(a) fund-trio Q ~2000 completion window: pool dual-flip watch per r668 law; D finalize ~10-08 (bm-b lane). "
              "(b) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar. "
              "(c) watch bm-a reply to MSG-2026-10-07-0250 (marker-pollution self-audit). "
              "(d) monthly exam 10-31 assembly face. (e) next 5x = r655.")
st["verify"] = ("receipts: qa/smoke-r650.md 5/5 (explicit --round 650) + qa/equity-curve-r650.png + results/_r650bmc_s6_log.txt 38/38 rc0 "
                "+ results/_r650bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD) + results/_attrition_guard_scan.json CLEAN "
                "+ results/_r650bmc_handover_facts.json + results/_r650bmc_trio_watch.json + research/HANDOVER.md r650 line")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 650->651")

# ---- 3) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8"))
act = ("当前活: r650 五倍数核对轮（HANDOVER r650 行落盘+S6 38/38+QA 包 r650 显式轮标零误标+trio watch+自愈全绿） | "
       "最近实物: research/HANDOVER.md r650 5x 行（增量窗 r646-650）+qa/smoke-r650.md 5/5（equity 800 点终值 1,017,839·93 trades·determinism=True·面恒等 r642-649）@ " + now +
       " | 下个里程碑: fund-trio Q 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08（bm-b 车道）；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r655")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 651, "round_no_label": "round 650 (bm-c)",
    "latest_artifact": ("research/HANDOVER.md r650 5x line (increment window r646-650) + qa/smoke-r650.md 5/5 (explicit --round 650, zero mislabel; "
                        "equity 800 pts final 1,017,839 face-identical r642-649) + results/_r650bmc_s6_log.txt 38/38 rc0 @ " + now),
    "next_milestone": ("fund-trio Q completion pool dual-flip watch (r668 law) + D finalize ~10-08 (bm-b lane); 10-09 market reopen "
                       "(data-chain re-arm + regime_guard v3 first bar); monthly exam 10-31; next 5x = r655"),
    "verdict": ("alive: r650 5x HANDOVER window round complete (HANDOVER r650 line landed; QA pack r650 5/5 zero-mislabel explicit --round 650; "
                "S6 38/38 rc0; smoke 48/48; board open=0; satengine alive; DEC/ORD double-sweep zero-delta 164/164; attrition CLEAN; "
                "trio V complete Q1883/D1559 bm-b rightful lane; W168 seat bm-a processed; unified chain 772,812; golden-week no-bar until 10-09)"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"], "| ack_count =", chk.get("orders_ack_count"))
