# -*- coding: utf-8 -*-
"""r663 bm-c close batch: round-report line (canonical path) + state advance
663->664 (QA pack r663 polled terminal 5/5, ignited with EXPLICIT --round 663,
first-line label verified zero-mislabel) + heartbeat three-line face + epoch
int self-verify + watermark keys facts-driven from results/_r663bmc_s05_facts.json
(r583 S4 law, double-sweep s05+s7close). Size declaration DERIVED at close time
via git cat-file -s :CODELY.md (STAGED blob, r653 close-size law: never copy a
prior receipt's declared size; staged-face = the exact to-be-committed blob).
Inbox assert adapted: untracked inbox = exactly self-authored outbound
escalation MSG-2026-10-07-0801-bmc-ALL.md (stays for GM/peers, not a to-me item).
Child git call carries CREATE_NO_WINDOW (U060 flash guard).
Pattern credit: Tools/_r662bmc_close.py (row via .format only -- r661 % pit)."""
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
facts = json.load(open(r"results\_r663bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["dec_sha"]
ord_sha = facts["ord_sha"]
assert facts["dec_delta"] is False and facts["ord_delta"] is False
assert facts["unacked"] == []
assert facts["inbox_unread"] == ["MSG-2026-10-07-0801-bmc-ALL.md"], \
    "inbox unexpected: {}".format(facts["inbox_unread"])
assert facts["fleet_orders_total"] == 163
assert len(dec_sha) == 64 and len(ord_sha) == 40
assert facts["shape_assert"] is True
assert facts["round"] == 663

# ---- 0b) size gate-pin derived at close (r646 gate-pin + r653 derive law) ----
codely_blob = int(subprocess.check_output(
    ["git", "cat-file", "-s", ":CODELY.md"],
    creationflags=CNW).decode().strip())
assert codely_blob <= 30720, "CODELY.md over 30KB gate: {}".format(codely_blob)

# ---- 1) round-report line (canonical path; .format only, zero % operator) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("watermark: 绿（red=false lane healthy·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·SAT 活=Tools 注册面 wave169 12/12 全完·队列空待 bm-a W170 freeze 供料·board 0 open·金周 no-bar·bm-b 全暗 81min→trio Q/D 冻结→已按 r662 预注册路径升级 MSG-2026-10-07-0801）"
       " | {ts} | r663 bm-c | dept:工程/舰队（值守轮·trio 停摆升级面主产出） | 当前活: r663 值守轮（S0 absorb ee50221fd+pull up-to-date·S1 48/48·S6 38/38·QA r663 5/5 零误标·S7 自愈全绿·trio 停摆探测+origin/本地/fuse 三面取证+MSG-0801 升级+trio_watch 证据落盘）"
       " | 最近实物: fleet/inbox/MSG-2026-10-07-0801-bmc-ALL.md（bm-b 全暗取证升级件·接管门 OPEN 但 bm-c host_gates FAIL+bm-a 被 keep-block 拒 1494/1022 次·默认案=等 bm-b checkpoint 零损失）+results/_r663bmc_trio_watch.json（停摆全证据）+qa/smoke-r663.md 5/5（93 trades·determinism=True·equity 1,017,839 面恒等·显式 --round 663 首行零误标）+qa/equity-curve-r663.png（66,226B）+results/_r663bmc_s6_log.txt（38/38 rc0）@ {ts}"
       " | 下个里程碑: bm-b dark-watch aging（~10:30 前零 origin 可见推送→对 MSG-0801 追加 aging 行；bm-b 复活=daemon 自续零损失即撤警）+Q 差 15 draws/D 差 352·trio finalize 窗 10-05..10-09；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+CA 金周结构旗 re-eval；月界首考 10-31；下个 5x=r665（HANDOVER 窗） | "
       "S0: 轮首树脏=3 本车道 daemon 面→churn-absorb commit ee50221fd（r642 净树律·-F 文件）→pull --rebase up-to-date 干净零 UU；"
       "S0.5 双扫（s05+s7close 两腿）：DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta+163/163 零未回执+开窗 inbox 0 未读（W170 seat MSG bma 广播件非本机收件已读不动=seat 载荷面归 bm-a 收取）+收窗 inbox=自产外发 MSG-0801 留位 GM/peers；"
       "S1 48/48；S3: 板 open=0·watermark 绿·SAT 活（wave169 12/12 完·queue_next 空=引擎车道干涸待 bm-a W170 freeze 供料·r812 next P0）·post_review 45✓/0✗/5🟡 零红·"
       "**trio 停摆探测（本轮主事件）**: Q 1985/2000+D 1648/2000 双双冻结于 07:17:46（探针时 44min 零写）+bm-b hb 06:40:15 起 81min 陈旧（r799 close 后 ~8 tick 未更）+origin 自 ~07:17:46 后零 bm-b 可见推送=循环+daemon 同秒冻结机器级事件特征；接管门 OPEN（min(hb 81,claim 57)>20 per r297/r603）但 bm-c host_gates FAIL（p1c_stock 缓存不在本机·r393 fuse 家族明文 re-entry 仅 TRANSFER fleet decision）+bm-a daemon 爬梯被 fuse keep-block 拒（QUALITY nulls OFF-CALIBER containment 1494 拒·DIVLOWVOL nulls 1022 拒·last_refusal 07:28:04=keep-block 正确防毒面）→唯一即时可行案=等 bm-b（checkpoint 断点续跑零损失·Q 仅差 15 draws 分钟级）→按 r662 next-pointer 预注册路径落 MSG-2026-10-07-0801-bmc-ALL.md 升级 GM+全队；"
       "S4: 零新坑（3 克隆件 s05/s6/qa_ignite 裸数字律+残号门全零·QA ignite 首行轮标 r663 正确）·主件零 append 维持 {cb}B 余量 {hr}B；"
       "S6 38/38 rc0（dualrun ZERO-DRIFT streak 51 @403·4 共享宿主面 lane_io stale-takeover derive by bm-c=bm-a hb 38min 陈旧入长 W170 freeze 轮·O-2100 s2.4 设计态·REPORT/LIVE-2026-10-07 幂等再生·token per-round ~12980+8487 粗估）；"
       "QA包r663: 显式 --round 663·pid 20048·stdout 首行 40s 内核验零误标→轮询终态 5/5（93 trades·determinism=True·equity 终值 1,017,839 与 r662 面恒等·png 66,226B）；"
       "S7 自愈面全绿（loop pin=5 no-op 首跳 08:15·watchdog 幂等重注册·precommit/prepush 双爪 LF 归一重装·attrition CLEAN 4 台账零 active loss）；"
       "本地未达 origin commit 数=0（push+fetch+rev-list 自证送达）"
       " | 证据=fleet/inbox/MSG-2026-10-07-0801-bmc-ALL.md（升级件）+results/_r663bmc_trio_watch.json（停摆取证）+qa/smoke-r663.md 5/5+qa/equity-curve-r663.png+results/_r663bmc_s6_log.txt 38/38+results/_r663bmc_s05_facts.json（双扫 s05+s7close）+results/_attrition_guard_scan.json CLEAN+results/_r663bmc_qa_runner.out（terminal 5/5 显式 --round 663）+results/post_review/REPORT-20261007.md（45✓/0✗/5🟡）"
       " | 下轮指针：(a) bm-b dark-watch aging（~10:30 界·零 origin 推送→MSG-0801 追加 aging 行再升级；复活→撤警+Q/D 自续观察）；(b) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+compute_audit 金周结构旗 re-eval；(c) 月界首考 10-31 装配面；(d) 下个 5x=r665（HANDOVER 窗）\n").format(
           ts=now, cb=codely_blob, hr=30720 - codely_blob)
_rr_tail = open(RR, "rb").read()[-30000:]
if b" | r663 bm-c | " in _rr_tail:
    print("RR row already present -- skip duplicate append")
else:
    with open(RR, "ab") as fh:
        fh.write(row.encode("utf-8") + b"\r\n")
    print("RR appended (canonical path)")

# ---- 2) state advance ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8-sig"))
assert st["round_no"] == 663, "unexpected round_no {}".format(st["round_no"])
st["round_no"] = 664
st["round_no_label"] = "round 663 (bm-c)"

did = ("r663 bm-c: standing maintenance round with trio-stall escalation as main product (no P0 tail, zero new pits). "
       "(1) S0: round-start dirty = 3 own-lane daemon faces; churn-absorb commit ee50221fd then pull --rebase up-to-date, clean zero UU. "
       "(2) S0.5 double-sweep (s05+s7close): DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta both sweeps; fleet orders 163/163 zero unacked; open-window inbox 0 unread (W170 seat bma broadcast read, seat payload face left for bm-a collection); close-window inbox = self-authored outbound MSG-0801 only. "
       "(3) S1 smoke 48/48. S3: board open=0; watermark green; SAT alive (wave169 12/12, queue dry awaiting bm-a W170 freeze); post_review 45 YES / 0 NO / 5 WAIT zero P0. "
       "TRIO STALL (round main event): Q 1985/2000 + D 1648/2000 both frozen at 07:17:46 (44min zero writes at probe), bm-b hb stale 81min (r799 close 06:40:15, ~8 missed ticks), origin dark for bm-b since ~07:17:46 = loop+daemon same-second freeze machine-level event signature. "
       "Takeover gate OPEN per r297/r603 (min(hb 81, claim 57) > STALE_MIN 20) BUT bm-c host_gates FAIL (p1c_stock cache absent, r393 fuse family: re-entry only after TRANSFER fleet decision) AND bm-a daemon ladder refused by correct keep-blocks (QUALITY nulls OFF-CALIBER containment 1494 refusals, DIVLOWVOL nulls 1022, last 07:28:04). "
       "Only immediately executable path = wait for bm-b recovery (checkpoint resume zero loss; Q just 15 draws short; trio finalize window 10-05..10-09). Escalated per r662 next-pointer prescribed action: fleet/inbox/MSG-2026-10-07-0801-bmc-ALL.md (GM + ALL) + full evidence results/_r663bmc_trio_watch.json. "
       "(4) S4: zero new pits (3 clones s05/s6/qa_ignite via bare-number law + residual gate all clean; QA ignite first-line label r663 correct); main file zero append, staged blob {}B headroom {}B. ".format(codely_blob, 30720 - codely_blob) +
       "(5) S6 chain 38/38 rc0: dualrun ZERO-DRIFT streak 51 @403; 4 shared host faces legitimately stale-takeover derived by bm-c (bm-a hb 38min stale inside long W170-freeze round, O-2100 s2.4 designed behavior); REPORT-2026-10-07 + LIVE-2026-10-07 regenerated idempotent; token per-round ~12980+8487 rough. "
       "(6) QA pack r663 5/5 zero-mislabel (explicit --round 663, pid 20048, first-line verified; 93 trades, determinism=True, equity final 1,017,839 face-identical, png 66,226B). "
       "(7) S7 self-heal green: loop pin=5 no-op (first fire 08:15), watchdog idempotent re-register, both claws LF-normalized install, attrition CLEAN (4 ledgers zero active loss). "
       "Delivery: push+fetch+rev-list self-verify N=0.")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = ("r663: standing maintenance round + trio-stall escalation as main product (bm-b dark 81min: Q frozen 1985/2000 D 1648/2000 since 07:17:46; "
                            "takeover gate OPEN but bm-c host_gates FAIL + bm-a keep-block refused -> wait-bm-b zero-risk default escalated via MSG-2026-10-07-0801-bmc-ALL; "
                            "QA r663 5/5 zero-mislabel; S6 38/38; DEC/ORD double-sweep zero-delta 163/163; zero new pits; attrition CLEAN)")
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
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r663 double-sweep s05+s7close both scans = 635C3024 MATCH zero-delta; "
                        "value facts-driven from results/_r663bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r663 double-sweep s05+s7close both scans = 437E9CDD MATCH zero-delta; "
                                "fleet orders 163/163 ack at BOTH S0.5 and S7 close sweeps (double-sweep law); value facts-driven from results/_r663bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = ("r663: standing round; QA r663 5/5 zero-mislabel (explicit --round 663, first-line verified); S6 38/38; DEC/ORD double-sweep MATCH; "
              "trio stall escalated (bm-b dark: Q 1985/D 1648 frozen 07:17:46, hb 81min stale; takeover blocked for bm-c=host_gates, for bm-a=keep-blocks; "
              "wait-bm-b zero-risk default; MSG-2026-10-07-0801-bmc-ALL + results/_r663bmc_trio_watch.json); attrition CLEAN; main staged blob {}B at close.".format(codely_blob))
st["next"] = ("(a) bm-b dark-watch aging: if zero origin-visible bm-b push by ~10:30, append aging line to MSG-2026-10-07-0801 and re-escalate; if bm-b revives, "
              "daemon checkpoint auto-resume = zero loss, withdraw alert (note on MSG, no delete) and resume trio finalize window watch (10-05..10-09). "
              "(b) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar + compute_audit golden-week structural flags re-eval (bar-day calendar self-detect is final arbiter). "
              "(c) monthly exam 10-31 assembly face. "
              "(d) next 5x = r665 (HANDOVER window).")
st["verify"] = ("receipts: fleet/inbox/MSG-2026-10-07-0801-bmc-ALL.md (escalation) + results/_r663bmc_trio_watch.json (stall evidence) "
                "+ qa/smoke-r663.md 5/5 (explicit --round 663, pid 20048) + qa/equity-curve-r663.png (66,226B) + results/_r663bmc_s6_log.txt 38/38 rc0 "
                "+ results/_r663bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD) "
                "+ results/_attrition_guard_scan.json CLEAN + results/_r663bmc_qa_runner.out (terminal 5/5) + results/post_review/REPORT-20261007.md (45 YES/0 NO/5 WAIT)")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 663->664")

# ---- 3) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8-sig"))
act = ("当前活: r663 值守轮收口（S0 absorb+pull 干净·S1 48/48·S6 38/38·QA r663 5/5 零误标·S7 自愈全绿·trio 停摆三面取证+MSG-0801 GM/ALL 升级=本轮主产出） | "
       "最近实物: fleet/inbox/MSG-2026-10-07-0801-bmc-ALL.md（bm-b 全暗 81min 取证升级：Q 1985/2000·D 1648/2000 冻结 07:17:46·接管门 OPEN 但 bm-c host_gates FAIL+bm-a 被 keep-block 拒·默认案=等 bm-b checkpoint 零损失）+results/_r663bmc_trio_watch.json+qa/smoke-r663.md（5/5·93 trades·determinism=True）+qa/equity-curve-r663.png @ " + now +
       " | 下个里程碑: bm-b dark-watch aging（~10:30 界·复活=自续撤警）；Q 差 15/D 差 352·trio finalize 窗 10-05..10-09；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r665")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 664, "round_no_label": "round 663 (bm-c)",
    "latest_artifact": ("fleet/inbox/MSG-2026-10-07-0801-bmc-ALL.md (bm-b dark stall escalation: Q/D nulls frozen, takeover gate OPEN but blocked for all claimers, wait-bm-b zero-risk default) "
                        "+ results/_r663bmc_trio_watch.json (full evidence) + qa/smoke-r663.md 5/5 (explicit --round 663, zero-mislabel, equity 1,017,839 face-identical) "
                        "+ qa/equity-curve-r663.png (66,226B) + results/_r663bmc_s6_log.txt 38/38 rc0 @ " + now),
    "next_milestone": ("bm-b dark-watch aging (~10:30 boundary; revive = daemon checkpoint auto-resume + withdraw alert; dark = aging line on MSG-0801 + re-escalate); "
                       "Q 15 draws / D 352 short, trio finalize window 10-05..10-09; 10-09 market reopen (data-chain re-arm + regime_guard v3 first bar + compute_audit flags re-eval); "
                       "monthly exam 10-31; next 5x = r665"),
    "verdict": ("alive: r663 standing round complete (QA r663 5/5 zero-mislabel explicit --round 663; S6 38/38 rc0; smoke 48/48; board open=0; satengine alive wave169 12/12 queue dry awaiting bm-a W170 freeze; "
                "DEC/ORD double-sweep zero-delta 163/163; attrition CLEAN; post_review 45 YES/0 NO; zero new pits; "
                "TRIO STALL ESCALATED: bm-b dark (hb 81min stale, origin dark since 07:17:46), Q 1985/2000 + D 1648/2000 frozen, takeover gate OPEN but bm-c host_gates FAIL + bm-a keep-block refused -> "
                "wait-bm-b zero-risk default, MSG-2026-10-07-0801-bmc-ALL + full evidence in-repo; golden-week no-bar face held"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"])
