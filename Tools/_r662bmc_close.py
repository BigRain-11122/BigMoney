# -*- coding: utf-8 -*-
"""r662 bm-c close batch: round-report line (canonical path) + state advance
662->663 (QA pack r662 polled terminal 5/5 BEFORE this close, ignited with
EXPLICIT --round 662 after the mislabeled first ignite was caught+fixed
in-round) + heartbeat three-line face + epoch int self-verify + watermark
keys facts-driven from results/_r662bmc_s05_facts.json (r583 S4 law,
double-sweep s05+s7close). Size declaration DERIVED at close time via
git cat-file -s :CODELY.md (STAGED blob, r653 close-size law: never copy a
prior receipt's declared size; staged-face = the exact to-be-committed blob).
Child git call carries CREATE_NO_WINDOW (U060 flash guard).
Pattern credit: Tools/_r661bmc_close.py (row via .format only -- r661 % pit)."""
import json
import os
import subprocess
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
CNW = 0x08000000  # CREATE_NO_WINDOW

# ---- 0) facts (r583 S4 law: never hand-typed) ----
facts = json.load(open(r"results\_r662bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["dec_sha"]
ord_sha = facts["ord_sha"]
assert facts["dec_delta"] is False and facts["ord_delta"] is False
assert facts["unacked"] == []
assert facts["inbox_unread"] == []
assert facts["fleet_orders_total"] == 163
assert len(dec_sha) == 64 and len(ord_sha) == 40
assert facts["shape_assert"] is True
assert facts["round"] == 662

# ---- 0b) size gate-pin derived at close (r646 gate-pin + r653 derive law) ----
codely_blob = int(subprocess.check_output(
    ["git", "cat-file", "-s", ":CODELY.md"],
    creationflags=CNW).decode().strip())
assert codely_blob <= 30720, "CODELY.md over 30KB gate: {}".format(codely_blob)

# ---- 1) round-report line (canonical path; .format only, zero % operator) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("watermark: 绿（red=false lane healthy·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·SAT 活=Tools 注册面 wave169 12/12 全完·队列空待 bm-a W170 freeze 供料·board 0 open·金周 no-bar）"
       " | {ts} | r662 bm-c | dept:工程/舰队（常规维护轮+1 新坑收律） | 当前活: r662 维护轮（QA r662 5/5+S6 38/38+双扫零 delta+自愈全绿+S4 新坑 1 条入册+over-gate minisplit 当窗即办）"
       " | 最近实物: qa/smoke-r662.md 5/5（93 trades·determinism=True·equity 终值 1,017,839 面恒等）+qa/equity-curve-r662.png（66,208B）+results/_r662bmc_s6_log.txt（38/38 rc0）+results/_r662bmc_codely_minisplit.json @ {ts}"
       " | 下个里程碑: bm-b trio-Q first-to-2000 ~08:0x 窗观察（Q 1985/2000 推进 0.63/min·bm-b hb 声明 eta ~08:0x·r668 same-window dual-flip 律·过窗空+hb 陈=升级 fleet-note/GM）+D 1648/2000 慢道 watch；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+CA 金周结构旗 re-eval（bm-b hb 称 10-08 复市·数据链自检面终裁）；月界首考 10-31；下个 5x=r665（HANDOVER 窗） | "
       "S0: 轮首树脏=3 本车道 daemon 面→churn-absorb commit 5b9dc6b37（r642 净树律）→pull --rebase onto bm-a r812 三连发干净重放零 UU；"
       "S0.5 双扫（s05+s7close 两腿）：DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta+163/163 零未回执+inbox 0 未读（MSG-0625 已被 bm-a/bm-b 动作面收取=bm-a r811 回执 17 面 0 标记自证）；"
       "S1 48/48；S3: 板 open=0·watermark 绿·SAT 活（wave169 12/12 完·queue_next 空=引擎车道干涸待 bm-a W170 freeze 供料·r812 声明 next P0）·post_review 45✓/0✗/5🟡 零红·"
       "trio watch r662: V 2000/2000·Q 1985/2000（较 r661 +17 行/27min=0.63/min·eta ~08:0x 与 bm-b hb honest-corrected 一致·烧活=零失约零升级）·D 1648/2000（+14 行推进中）·池 2 ready owner=bm-b 07:04:10 起·试用劳力线=trio 在飞已满足零新起草；"
       "S4: 新坑 1 条入册（QA ignite 克隆·裸数字逃逸前缀 replace 坑·~40s 自捕零 origin 伤害·qa_ignite 首点火误标 r661→杀+裸数字修+重点火 r662 5/5·误标跑手对 r661 包确定性重生成仅 CRLF 幻影 M→git checkout 复原）+主件 append 后实测 30,848B>30,720B→当窗即办 minisplit（r651/r654/r661 仪式同款·r644 580B+r661 561B 两坑 verbatim 迁 pit-protocol-lane.md·sha16 37dda2012edf5a56/f747583ef1e22c97·prescan rc3 留痕·登记册出入行同步 append·主件 staged blob {cb}B 余量 {hr}B）；"
       "S6 38/38 rc0（dualrun ZERO-DRIFT streak 51 @403·CA supply_gap+supply_floor=已知金周结构旗 re-eval 10-09+·bm-a hb 新鲜=4 共享宿主面守卫诚实 skip·REPORT/LIVE-2026-10-07 幂等再生·token per-round ~12980+8562 粗估）；"
       "QA包r662: 首点火误标（-replace r661 前缀形漏裸数字 661 实参·r758/r640/r644 族新机械面）→stdout 首行 40s 自捕→杀+git checkout r661 包复原（确定性重生成零内容差）→裸数字修+重点火 pid23168 显式 --round 662→轮询终态 5/5 零误标（93 trades·determinism=True·equity 终值 1,017,839·png 66,208B）；"
       "S7 自愈面全绿（loop pin=5 no-op 首跳 07:45·watchdog 幂等重注册·precommit/prepush 双爪 LF 归一重装·attrition CLEAN 4 台账零 active loss）；"
       "本地未达 origin commit 数=0（push+fetch+rev-list 自证送达）"
       " | 证据=qa/smoke-r662.md 5/5+qa/equity-curve-r662.png+results/_r662bmc_s6_log.txt 38/38+results/_r662bmc_s05_facts.json（双扫 s05+s7close）"
       "+results/_r662bmc_codely_minisplit.json（2 坑 verbatim+sha16 对账）+results/_attrition_guard_scan.json CLEAN+results/_r662bmc_trio_watch.json+results/_r662bmc_qa_runner.out（terminal 5/5 显式 --round 662）+results/post_review/REPORT-20261007.md（45✓/0✗/5🟡）"
       " | 下轮指针：(a) bm-b trio-Q first-to-2000 ~08:0x 过窗检查（r668 same-window dual-flip 收取·过窗空+hb 陈旧→fleet-note/GM 升级）；(b) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+compute_audit 金周结构旗 re-eval；(c) 月界首考 10-31 装配面；(d) 下个 5x=r665（HANDOVER 窗）\n").format(
           ts=now, cb=codely_blob, hr=30720 - codely_blob)
_rr_tail = open(RR, "rb").read()[-30000:]
if b" | r662 bm-c | " in _rr_tail:
    print("RR row already present -- skip duplicate append")
else:
    with open(RR, "ab") as fh:
        fh.write(row.encode("utf-8") + b"\r\n")
    print("RR appended (canonical path)")

# ---- 2) state advance ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8-sig"))
assert st["round_no"] == 662, "unexpected round_no {}".format(st["round_no"])
st["round_no"] = 663
st["round_no_label"] = "round 662 (bm-c)"

did = ("r662 bm-c: regular maintenance round (1 new pit captured+legislated; no P0 tail). "
       "(1) S0: round-start dirty = 3 own-lane daemon faces; churn-absorb commit then pull --rebase onto bm-a r812 3-commit push, clean replay zero UU. "
       "(2) S0.5 double-sweep (s05+s7close): DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta both sweeps; fleet orders 163/163 zero unacked; inbox 0 unread (MSG-0625 collected by peers; bm-a r811 receipt = 17 faces 0-marker self-verify). "
       "(3) S1 smoke 48/48. S3: board open=0; watermark green; SAT alive (wave169 12/12 complete, queue_next empty = engine lane dry awaiting bm-a W170 freeze refill per r812 next-P0 declaration); "
       "post_review 45 YES / 0 NO / 5 WAIT zero P0; trio watch r662: V 2000/2000 complete, Q 1985/2000 progressing (0.63/min, eta ~08:0x consistent with bm-b hb honest-corrected declaration; burn alive = no breach no escalation), D 1648/2000 slow lane; "
       "pool 2 ready owner=bm-b since 07:04:10; trial-labor line satisfied by in-flight trio judge batches, no new drafting. "
       "(4) S4: 1 new pit captured (QA ignite clone: bare-number arg escaped prefix-anchored -replace, first ignite mislabeled r661, caught in ~40s from ignite stdout, killed, deterministic-regen zero content drift, r661 pack restored via git checkout, re-ignited explicit --round 662); "
       "main-file append pushed blob over 30,720B gate -> same-window minisplit (r651/r654/r661 ritual): r644 (580B) + r661 (561B) pits verbatim-migrated to research/pit-protocol-lane.md, sha16 37dda2012edf5a56 / f747583ef1e22c97, prescan rc3 recorded, registry ledger line appended, receipt results/_r662bmc_codely_minisplit.json; main staged blob {}B, headroom {}B. ".format(codely_blob, 30720 - codely_blob) +
       "(5) S6 chain 38/38 rc0: dualrun ZERO-DRIFT streak 51 @403; CA supply_gap+supply_floor = known golden-week structural flags re-eval 10-09+; bm-a hb fresh so 4 shared host faces honestly skipped by lane guard; REPORT-2026-10-07 + LIVE-2026-10-07 regenerated idempotent; token per-round ~12980+8562 rough. "
       "(6) QA pack r662 5/5 zero-mislabel (93 trades, determinism=True, equity 800 pts final 1,017,839 face-identical, png 66,208B). "
       "(7) S7 self-heal green: loop pin=5 no-op, watchdog idempotent re-register, both claws LF-normalized install, attrition CLEAN (4 ledgers zero active loss). "
       "Delivery: push+fetch+rev-list self-verify N=0.")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = ("r662: maintenance round (QA r662 5/5 after in-round mislabel self-catch+fix; S6 38/38; DEC/ORD double-sweep zero-delta 163/163; "
                            "1 new pit (bare-number clone escape) legislated + same-window over-gate minisplit 2 pits to pit-protocol-lane; trio Q1985/D1648 progressing bm-b lane; attrition CLEAN)")
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
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r662 double-sweep s05+s7close both scans = 635C3024 MATCH zero-delta; "
                        "value facts-driven from results/_r662bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r662 double-sweep s05+s7close both scans = 437E9CDD MATCH zero-delta; "
                                "fleet orders 163/163 ack at BOTH S0.5 and S7 close sweeps (double-sweep law); value facts-driven from results/_r662bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = ("r662: maintenance round; QA r662 5/5 (first ignite mislabel caught+fixed in-round); S6 38/38; DEC/ORD double-sweep MATCH; "
              "1 new pit + minisplit (r644+r661 -> pit-protocol-lane, receipt _r662bmc_codely_minisplit.json); trio Q1985/D1648 bm-b lane; attrition CLEAN; main staged blob {}B at close.".format(codely_blob))
st["next"] = ("(a) bm-b trio-Q first-to-2000 ~08:0x window check next round (r668 same-window pool dual-flip collection; window empty + hb stale -> fleet-note/GM escalation). "
              "(b) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar + compute_audit golden-week structural flags re-eval (bm-b hb claims 10-08 reopen; bar-day calendar self-detect is final arbiter). "
              "(c) monthly exam 10-31 assembly face. "
              "(d) next 5x = r665 (HANDOVER window).")
st["verify"] = ("receipts: qa/smoke-r662.md 5/5 (explicit --round 662, pid 23168) + qa/equity-curve-r662.png + results/_r662bmc_s6_log.txt 38/38 rc0 "
                "+ results/_r662bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD) + results/_r662bmc_codely_minisplit.json (2 pits verbatim sha16 accounting) "
                "+ results/_attrition_guard_scan.json CLEAN + results/_r662bmc_trio_watch.json + results/_r662bmc_qa_runner.out (terminal 5/5) + results/post_review/REPORT-20261007.md (45 YES/0 NO/5 WAIT)")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 662->663")

# ---- 3) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8-sig"))
act = ("当前活: r662 维护轮收口（QA r662 5/5 显式轮标·首点火误标 40s 自捕治愈+S6 38/38+双扫零 delta+S4 新坑 1 条入册+over-gate minisplit 当窗即办+自愈全绿） | "
       "最近实物: qa/smoke-r662.md（5/5·93 trades·determinism=True·equity 终值 1,017,839 面恒等）+qa/equity-curve-r662.png（66,208B）+results/_r662bmc_codely_minisplit.json（2 坑迁 pit-protocol-lane·verbatim+sha16 对账）+results/_r662bmc_s6_log.txt（38/38 rc0）@ " + now +
       " | 下个里程碑: bm-b trio-Q first-to-2000 ~08:0x 窗观察（Q 1985/2000 推进中·r668 dual-flip 收取）；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+CA 金周结构旗 re-eval；月界首考 10-31；下个 5x=r665")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 663, "round_no_label": "round 662 (bm-c)",
    "latest_artifact": ("qa/smoke-r662.md 5/5 (explicit --round 662 after in-round mislabel self-catch+fix; equity 800 pts final 1,017,839 face-identical) "
                        "+ qa/equity-curve-r662.png (66,208B) + results/_r662bmc_codely_minisplit.json (2 pits verbatim to pit-protocol-lane) + results/_r662bmc_s6_log.txt 38/38 rc0 @ " + now),
    "next_milestone": ("bm-b trio-Q first-to-2000 ~08:0x window check + D slow-lane watch (bm-b lane); 10-09 market reopen (data-chain re-arm + regime_guard v3 first bar + compute_audit flags re-eval); "
                       "monthly exam 10-31; next 5x = r665"),
    "verdict": ("alive: r662 maintenance round complete (QA r662 5/5 -- first ignite mislabeled r661 via bare-number clone escape, caught in ~40s, killed, deterministic regen zero-drift, restored, re-ignited explicit --round 662 = new pit legislated; "
                "S6 38/38 rc0; smoke 48/48; board open=0; satengine alive wave169 12/12 complete, queue empty awaiting bm-a W170 freeze refill; "
                "DEC/ORD double-sweep zero-delta 163/163; attrition CLEAN; post_review 45 YES/0 NO; trio V complete Q1985/D1648 progressing bm-b rightful lane; "
                "main CODELY minisplit same-window (over-gate) 2 pits to pit-protocol-lane, receipt in-repo; golden-week no-bar face held"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"])
