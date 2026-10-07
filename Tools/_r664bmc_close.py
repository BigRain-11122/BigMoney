# -*- coding: utf-8 -*-
"""r664 bm-c close batch: round-report line (canonical path) + state advance
664->665 (QA pack r664 polled terminal 5/5, ignited with EXPLICIT --round 664,
first-line label verified zero-mislabel) + heartbeat three-line face + epoch
int self-verify + watermark keys facts-driven from results/_r664bmc_s05_facts.json
(r583 S4 law, double-sweep s05+s7close). Size declaration DERIVED at close time
via git cat-file -s :CODELY.md (STAGED blob, r653 close-size law: never copy a
prior receipt's declared size; staged-face = the exact to-be-committed blob).
Inbox assert adapted: untracked inbox = exactly self-authored outbound
escalation MSG-2026-10-07-0801-bmc-ALL.md (RESOLVED note appended r664; stays
as full event archive for GM/peers, not a to-me item).
Child git call carries CREATE_NO_WINDOW (U060 flash guard).
Pattern credit: Tools/_r663bmc_close.py (row via .format only -- r661 % pit)."""
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
facts = json.load(open(r"results\_r664bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["dec_sha"]
ord_sha = facts["ord_sha"]
assert facts["dec_delta"] is False and facts["ord_delta"] is False
assert facts["unacked"] == []
assert facts["inbox_unread"] == ["MSG-2026-10-07-0801-bmc-ALL.md"], \
    "inbox unexpected: {}".format(facts["inbox_unread"])
assert facts["fleet_orders_total"] == 163
assert len(dec_sha) == 64 and len(ord_sha) == 40
assert facts["shape_assert"] is True
assert facts["round"] == 664

# ---- 0b) size gate-pin derived at close (r646 gate-pin + r653 derive law) ----
codely_blob = int(subprocess.check_output(
    ["git", "cat-file", "-s", ":CODELY.md"],
    creationflags=CNW).decode().strip())
assert codely_blob <= 30720, "CODELY.md over 30KB gate: {}".format(codely_blob)

# ---- 1) round-report line (canonical path; .format only, zero % operator) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("watermark: 绿（red=false lane healthy·py_series_tail 0/0/0.1 金周无 bar 合法 idle·SAT 活=W170 已入队 0/12 待 daemon 烧=供料恢复·board 0 open·bm-b 复活 r800 轮中·post_review 零 ✗）"
       " | {ts} | r664 bm-c | dept:工程/舰队（值守轮·bm-b 复活撤警面主产出） | 当前活: r664 值守轮（S0 absorb+pull 干净零 UU·S1 48/48·S6 38/38·QA r664 5/5 零误标·bm-b 复活三面实证→MSG-0801 RESOLVED 撤警注记+老化线解除+trio_watch 证据落盘）"
       " | 最近实物: fleet/inbox/MSG-2026-10-07-0801-bmc-ALL.md RESOLVED 段（bm-b 复活撤警：origin 三 commit 5aee5cf94/074058f5e/43cce34a3·Q 1985→1988·D 1648→1654 推进实证·checkpoint 零损失兑现）+results/_r664bmc_trio_watch.json（复活全证据+撤警判定）+qa/smoke-r664.md 5/5（93 trades·determinism=True·equity 1,017,839 面恒等·显式 --round 664 首行零误标）+qa/equity-curve-r664.png（66,201B）+results/_r664bmc_s6_log.txt（38/38 rc0）@ {ts}"
       " | 下个里程碑: trio finalize 窗观察恢复（10-05..10-09·Q 1988/2000 差 12·D 1654/2000 慢车道·Q first-to-2000 同窗 pool dual-flip 按 r668 归 bm-b 执行面 bm-c 观察记录）；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+CA 金周结构旗 re-eval；月界首考 10-31；下个 5x=r665（HANDOVER 窗） | "
       "S0: 轮首树脏=3 本车道 daemon 面→churn-absorb commit ac6d9a8cf→rebase e2a5e0e0b（r642 净树律）→pull --rebase origin 3 新 bm-b commit 收编干净零 UU（bm-b 复活首见面）；"
       "S0.5 双扫（s05+s7close 两腿）：DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta 双腿+163/163 零未回执+开窗 inbox 0 未读+收窗 inbox=自产外发 MSG-0801（RESOLVED 注记后留档）双扫同判；"
       "S1 48/48；S3: 板 open=0·watermark 绿·SAT 活（W170 已入队=_bm-a r813 freeze 供料落地·dedup 0/12 待烧·wave<=169 全 12/12）·post_review 零 ✗ 零 P0；"
       "**bm-b 复活撤警（本轮主事件·r663 next-pointer(a) 预注册动作兑现）**: origin 三 commit=08:09:54 r800 tail（自述 Q burn in-flight nulls.jsonl）+08:09:54/08:12:15 autofill keepalive owner=bm-b→复活实证三面齐（origin push 恢复+Q/D 推进+daemon tick）；origin 真值 Q 1988/D 1654（stall 冻结点 07:17:46 的 1985/1648 后 +3/+6 零双烧）；心跳面 06:40:15 陈旧=r800 轮中态（S0 起 08:09:54）非暗面；→MSG-2026-10-07-0801 追加 RESOLVED 段撤警（不删件·老化升级线 ~10:30 解除）+trio finalize 窗观察恢复；"
       "S4: 零新坑（3 克隆件 s05/s6/qa_ignite 裸数字律+残号门全零·QA ignite 首行轮标 r664 正确）·主件零 append 维持 {cb}B 余量 {hr}B；"
       "S6 38/38 rc0（dualrun ZERO-DRIFT streak 51 @403·4 共享宿主面 lane_io stale-takeover derive by bm-c=bm-a hb 57min 陈旧入长 W170 freeze 轮·O-2100 s2.4 设计态·REPORT/LIVE-2026-10-07 幂等再生·token per-round ~12980+8487 粗估）；"
       "QA包r664: 显式 --round 664·pid 4288·stdout 首行核验零误标→轮询终态 5/5（93 trades·determinism=True·equity 终值 1,017,839 与 r663 面恒等·png 66,201B）；"
       "S7 自愈面全绿（loop pin=5 no-op 首跳 08:25·watchdog 幂等重注册首跳 08:25·precommit/prepush 双爪 LF 归一重装·attrition CLEAN 4 台账零 active loss）；"
       "本地未达 origin commit 数=0（push+fetch+rev-list 自证送达）"
       " | 证据=fleet/inbox/MSG-2026-10-07-0801-bmc-ALL.md（RESOLVED 撤警段）+results/_r664bmc_trio_watch.json（复活证据）+qa/smoke-r664.md 5/5+qa/equity-curve-r664.png+results/_r664bmc_s6_log.txt 38/38+results/_r664bmc_s05_facts.json（双扫 s05+s7close）+results/_attrition_guard_scan.json CLEAN+results/_r664bmc_qa_runner.out（terminal 5/5 显式 --round 664）"
       " | 下轮指针：(a) r665=5x HANDOVER 窗（HANDOVER 产物清单核对更新）；(b) trio finalize 窗观察（Q 差 12·D 慢车道·双 2000 即 finalize；bm-b 再暗=老化线重启+按 r663 取证范式再升级）；(c) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+compute_audit 金周结构旗 re-eval；(d) 月界首考 10-31 装配面\n").format(
           ts=now, cb=codely_blob, hr=30720 - codely_blob)
_rr_tail = open(RR, "rb").read()[-30000:]
if b" | r664 bm-c | " in _rr_tail:
    print("RR row already present -- skip duplicate append")
else:
    with open(RR, "ab") as fh:
        fh.write(row.encode("utf-8") + b"\r\n")
    print("RR appended (canonical path)")

# ---- 2) state advance ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8-sig"))
assert st["round_no"] == 664, "unexpected round_no {}".format(st["round_no"])
st["round_no"] = 665
st["round_no_label"] = "round 664 (bm-c)"

did = ("r664 bm-c: standing maintenance round with bm-b-revival alert withdrawal as main product (no P0 tail, zero new pits). "
       "(1) S0: round-start dirty = 3 own-lane daemon faces; churn-absorb commit ac6d9a8cf (rebased to e2a5e0e0b) then pull --rebase picked up 3 fresh bm-b commits clean zero UU. "
       "(2) S0.5 double-sweep (s05+s7close): DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta both sweeps; fleet orders 163/163 zero unacked; inbox = self-authored outbound MSG-0801 only. "
       "(3) S1 smoke 48/48. S3: board open=0; watermark green; SAT alive (W170 ENQUEUED per bm-a r813 freeze: dedup 0/12 pending daemon burn, waves <=169 all 12/12); post_review zero-NO zero P0. "
       "BM-B REVIVAL (round main event, r663 next-pointer (a) prescribed action discharged): origin-visible 3 commits 08:09:54-08:12:15 (r800 tail self-describing Q burn in-flight + 2x autofill keepalive owner=bm-b), "
       "origin-truth Q 1988/2000 (+3 post-stall) D 1654/2000 (+6), zero duplicate-draw sign; bm-b heartbeat file 06:40:15 stale = r800 mid-round state (S0 started 08:09:54), NOT dark; "
       "-> alert WITHDRAWN: RESOLVED section appended to MSG-2026-10-07-0801 (no delete, aging line ~10:30 LIFTED), evidence results/_r664bmc_trio_watch.json, trio finalize window watch resumed (10-05..10-09). "
       "(4) S4: zero new pits (3 clones s05/s6/qa_ignite via bare-number law + residual gate all clean; QA ignite first-line label r664 correct); main file zero append, staged blob {}B headroom {}B. ".format(codely_blob, 30720 - codely_blob) +
       "(5) S6 chain 38/38 rc0: dualrun ZERO-DRIFT streak 51 @403; 4 shared host faces legitimately stale-takeover derived by bm-c (bm-a hb 57min stale inside long W170-freeze round, O-2100 s2.4 designed behavior); REPORT-2026-10-07 + LIVE-2026-10-07 regenerated idempotent; token per-round ~12980+8487 rough. "
       "(6) QA pack r664 5/5 zero-mislabel (explicit --round 664, pid 4288, first-line verified; 93 trades, determinism=True, equity final 1,017,839 face-identical, png 66,201B). "
       "(7) S7 self-heal green: loop pin=5 no-op (first fire 08:25), watchdog idempotent re-register (first fire 08:25), both claws LF-normalized install, attrition CLEAN (4 ledgers zero active loss). "
       "Delivery: push+fetch+rev-list self-verify N=0.")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = ("r664: standing maintenance round + bm-b-revival alert withdrawal as main product (origin 3 commits 08:09:54-08:12:15, Q 1985->1988 / D 1648->1654 advancing, "
                            "hb-stale = r800 mid-round not dark; RESOLVED note on MSG-2026-10-07-0801, aging line lifted, trio finalize watch resumed; "
                            "QA r664 5/5 zero-mislabel; S6 38/38; DEC/ORD double-sweep zero-delta 163/163; W170 enqueued for engine; zero new pits; attrition CLEAN)")
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
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r664 double-sweep s05+s7close both scans = 635C3024 MATCH zero-delta; "
                        "value facts-driven from results/_r664bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r664 double-sweep s05+s7close both scans = 437E9CDD MATCH zero-delta; "
                                "fleet orders 163/163 ack at BOTH S0.5 and S7 close sweeps (double-sweep law); value facts-driven from results/_r664bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = ("r664: standing round; QA r664 5/5 zero-mislabel (explicit --round 664, first-line verified); S6 38/38; DEC/ORD double-sweep MATCH; "
              "bm-b REVIVED (origin 3 commits 08:09:54-08:12:15, Q 1988/D 1654 advancing, hb-stale = r800 mid-round state) -> alert WITHDRAWN "
              "(RESOLVED note on MSG-2026-10-07-0801, no delete, aging line lifted; evidence _r664bmc_trio_watch.json); W170 enqueued for engine (0/12 pending); attrition CLEAN; main staged blob {}B at close.".format(codely_blob))
st["next"] = ("(a) r665 = 5x HANDOVER window: verify + update research/HANDOVER.md product inventory and completion states. "
              "(b) trio finalize window watch (10-05..10-09): Q 1988/2000 (12 short) + D 1654/2000 slow lane; Q first-to-2000 same-window pool dual-flip per r668 = bm-b execution face, bm-c watch+record; "
              "if bm-b goes dark AGAIN: aging line restart + re-escalate per r663 evidence pattern. "
              "(c) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar + compute_audit golden-week structural flags re-eval (bar-day calendar self-detect is final arbiter). "
              "(d) monthly exam 10-31 assembly face.")
st["verify"] = ("receipts: fleet/inbox/MSG-2026-10-07-0801-bmc-ALL.md (RESOLVED withdrawal section) + results/_r664bmc_trio_watch.json (revival evidence) "
                "+ qa/smoke-r664.md 5/5 (explicit --round 664, pid 4288) + qa/equity-curve-r664.png (66,201B) + results/_r664bmc_s6_log.txt 38/38 rc0 "
                "+ results/_r664bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD) "
                "+ results/_attrition_guard_scan.json CLEAN + results/_r664bmc_qa_runner.out (terminal 5/5) + results/post_review/REPORT-20261007.md (zero NO)")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 664->665")

# ---- 3) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8-sig"))
act = ("当前活: r664 值守轮收口（S0 absorb+pull 干净·S1 48/48·S6 38/38·QA r664 5/5 零误标·S7 自愈全绿·bm-b 复活撤警=本轮主产出） | "
       "最近实物: fleet/inbox/MSG-2026-10-07-0801-bmc-ALL.md RESOLVED 段（bm-b 复活撤警：origin 三 commit·Q 1985→1988·D 1648→1654 推进·老化线解除·checkpoint 零损失兑现）+results/_r664bmc_trio_watch.json+qa/smoke-r664.md（5/5·93 trades·determinism=True）+qa/equity-curve-r664.png @ " + now +
       " | 下个里程碑: trio finalize 窗观察恢复（Q 差 12·D 慢车道·10-05..10-09）；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r665（HANDOVER 窗）")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 665, "round_no_label": "round 664 (bm-c)",
    "latest_artifact": ("fleet/inbox/MSG-2026-10-07-0801-bmc-ALL.md RESOLVED (bm-b revival alert withdrawal: 3 origin commits 08:09:54-08:12:15, Q 1988/D 1654 advancing, hb-stale = r800 mid-round) "
                        "+ results/_r664bmc_trio_watch.json (revival evidence) + qa/smoke-r664.md 5/5 (explicit --round 664, zero-mislabel, equity 1,017,839 face-identical) "
                        "+ qa/equity-curve-r664.png (66,201B) + results/_r664bmc_s6_log.txt 38/38 rc0 @ " + now),
    "next_milestone": ("r665 = 5x HANDOVER window; trio finalize window watch 10-05..10-09 (Q 12 draws short / D slow lane; bm-b execution face); "
                       "10-09 market reopen (data-chain re-arm + regime_guard v3 first bar + compute_audit flags re-eval); "
                       "monthly exam 10-31"),
    "verdict": ("alive: r664 standing round complete (QA r664 5/5 zero-mislabel explicit --round 664; S6 38/38 rc0; smoke 48/48; board open=0; satengine alive W170 ENQUEUED 0/12 pending daemon burn; "
                "DEC/ORD double-sweep zero-delta 163/163; attrition CLEAN; post_review zero NO; zero new pits; "
                "bm-b REVIVED -> alert WITHDRAWN (RESOLVED note on MSG-2026-10-07-0801, no delete; origin 3 commits 08:09:54-08:12:15, Q 1988/D 1654 advancing; "
                "hb-stale = r800 mid-round state not dark; trio finalize window watch resumed; golden-week no-bar face held)"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"])
