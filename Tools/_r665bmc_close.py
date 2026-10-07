# -*- coding: utf-8 -*-
"""r665 bm-c close batch: 5x HANDOVER insert + round-report row + state advance
665->666 (QA pack r665 polled terminal 5/5, ignited with EXPLICIT --round 665,
first-line label verified zero-mislabel) + heartbeat three-line face + epoch int
self-verify + watermark keys facts-driven from results/_r665bmc_s05_facts.json
(r583 S4 law, double-sweep s05+s7close). Size declaration DERIVED at close time
via git cat-file -s :CODELY.md (STAGED blob, r653 close-size law; this round
CODELY.md +1 pit entry staged before close so staged face = to-be-committed).
Child git call carries CREATE_NO_WINDOW (U060 flash guard).
Pattern credit: Tools/_r664bmc_close.py (row via .format only -- r661 % pit)."""
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
facts = json.load(open(r"results\_r665bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["dec_sha"]
ord_sha = facts["ord_sha"]
assert facts["dec_delta"] is False and facts["ord_delta"] is False
assert facts["unacked"] == []
assert facts["inbox_unread"] == []
assert facts["fleet_orders_total"] == 163
assert len(dec_sha) == 64 and len(ord_sha) == 40
assert facts["shape_assert"] is True
assert facts["round"] == 665

# ---- 0b) size gate-pin derived at close (r646 gate-pin + r653 derive law) ----
codely_blob = int(subprocess.check_output(
    ["git", "cat-file", "-s", ":CODELY.md"],
    creationflags=CNW).decode().strip())
assert codely_blob <= 30720, "CODELY.md over 30KB gate: {}".format(codely_blob)

# ---- 0c) 5x HANDOVER insert (newest-first, before r660 line; EOL self-detect) ----
HO = r"research\HANDOVER.md"
ho_line = ("> bm-c round 665 五倍数核对（2026-10-07 09:0x·增量窗 r661-665 五轮）：增量窗 r661-665=bm-c 面（**金周值守主线+trio bm-b 停摆→复活→再停摆双升级链+r664 close-tail 死窗恢复与游离 HEAD rebase 治愈（r665）+统一链 W170 finalize 前移**——"
    "r661 值守轮〔QA r661 5/5 面恒等+S6 38/38+双扫零 delta+自愈全绿+零新坑〕；"
    "r662 值守轮〔QA r662 5/5+S6 38/38+**S4 新坑=轮号脚本克隆裸数字逃逸 replace 坑**（-replace r661→r662 只命中 r 前缀形态·qa_ignite 裸数字参数逃逸错标 r661 包·~40s 自捕·正法=裸数字 replace+克隆后残号门强制步+点火首行核验）+over-gate minisplit 当窗即办〕；"
    "r663 值守轮〔**trio 停摆升级面主产出**：bm-b 全暗 81min→Q/D 冻结探测+origin/本地/fuse 三面取证+MSG-2026-10-07-0801-bmc-ALL 升级+trio_watch 证据落盘+老化线 ~10:30〕；"
    "r664 值守轮〔**bm-b 复活撤警**：origin 三 commit 08:09:54-08:12:15（r800 tail Q burn in-flight+2x autofill keepalive）+Q 1985→1988/D 1648→1654 推进+hb 陈旧=r800 轮中态判非暗→MSG-0801 RESOLVED 撤警注记（不删件·老化线解除）+W170 入队知悉+QA r664 5/5；**会话死于 close 后 commit 前=close-tail 43 面搁浅**〕；"
    "r665=本核对轮〔**5x HANDOVER 义务（本行）+S0 死窗恢复**：43 自产面吸收 commit（r658 恢复律·attrition CLEAN 预检·-F 文件律）→**游离 HEAD rebase 中途态治愈**（r664 会话死于 pull --rebase 六 UU 已 staging 未 continue·本机吸收 commit 恰充重放 pick2=round 664 close 内容·r664 resolver 回执 6 面律复核·余 2 picks 899ecd4ed/2f9d5e474=纯 daemon tick 可弃 live-wins）→r420/r624 律 rebase --quit+branch -f main+symbolic-ref 同批→daemon churn-absorb→pull --rebase 3/3 零 UU→**恢复链即时推送送达**（r659 先例·origin f5254941c·fetch+rev-list 0/0 双证）"
    "+S0.5 双扫零 delta 163/163+S1 48/48+S6 38/38 rc0〔dualrun streak 51 @403·bm-a hb 4min 新鲜 lane_io 全 skip·REPORT/LIVE-2026-10-07 再生〕"
    "+**bm-b 再停摆→老化线重启**（Q 1988/D 1654 冻结 @08:16:09 36min+hb 06:40:15 陈 132min+origin 08:12:15 后零新 commit=r800 25min wrapper 击杀假说·阈值 09:15·过线=r663 证据范式再升级·takeover 恒闭=bm-c host_gates FAIL p1c_stock r393 族）"
    "+QA r665 5/5 显式 --round 665 零误标〔93 trades·determinism=True·equity 终值面恒等·png 66,185B〕+S4 新坑 1 条（silent-git 单块多行捕获×foreach 对象迭代坑）〕）。"
    "产物清单漂移=qa/smoke-r66{1..5}.md+qa/equity-curve-r66{1..5}.png〔五轮常设证据包族〕+results/_r66{1..5}bmc_* 工件族〔s6_log+s05_facts+qa_runner+trio_watch r663/664/665 三连+codely minisplit receipt r662+rebase_resolve 双件 r664+ledger_probe r665〕+Tools/_r66{1..5}bmc_{s05,s6,qa_ignite,close}.py 驱动器族+fleet/inbox/processed/MSG-2026-10-07-0801-bmc-ALL.md〔r663 升级+r664 RESOLVED 注记〕+CODELY.md r662/r665 坑律两行；零新产品行（值守窗零批 finalize 零判决零新链入=如实注记）；"
    "统一链 **779,412 实读前移**（live head=results/perpetual_faces/n1_w170_results.json science_gates.ledger.total 实测·W170 finalize bm-a r813〔777,212+2,200·K=371,920·skill_line 1.1841→1.184 delta -0.0001〕·W171 席位公示 bm-a r814〔A 391_004..393_003+B 393_004..393_203·161st wave·bm-c 只读观察面〕）；"
    "板 open=0·job_list 空·satengine 活〔rc0 Tools 注册面·W170 12/12〕·水位绿〔金周无 bar 合法 idle〕·试用劳力线不触发（板空+金周+研究席位 bm-a 车道+fund-trio bm-b 在烧）·DEC/ORD 双扫零 delta（635C3024/437E9CDD）163/163·attrition CLEAN·post_review 零 ✗；"
    "指针：**r666 aging-line verdict（bm-b 09:02 tick 后观察·过 09:15 线仍暗=r663 范式再升级 MSG+GM fleet-note·复活=撤警+trio finalize 窗恢复〔10-05..10-09·Q 差 12·D 差 346·r638 fallback armed〕）+10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+CA 金周结构旗 re-eval+月界首考 10-31 装配面；下一 5x=bm-c r670**")
data = open(HO, "rb").read()
anchor = "> bm-c round 660 ".encode("utf-8")
idx = data.find(anchor)
assert idx > 0, "HANDOVER anchor (r660 line) not found"
assert b"> bm-c round 665 " not in data[:4000], "HANDOVER r665 line already present"
eol = b"\r\n" if data[:idx].find(b"\r\n") >= 0 else b"\n"
data = data[:idx] + ho_line.encode("utf-8") + eol + data[idx:]
open(HO, "wb").write(data)
print("HANDOVER r665 line inserted (eol={})".format(eol))

# ---- 1) round-report line (canonical path; .format only, zero % operator) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("watermark: 绿（red=false lane healthy·py_series_tail 0/0/0.1 金周无 bar 合法 idle·SAT 活=Tools 注册面 rc0 W170 12/12+W171 席位 bm-a r814·board 0 open·bm-b 再停摆=老化线重启 09:15 阈值·post_review ✓45/✗0 零 P0）"
       " | {ts} | r665 bm-c | dept:工程/舰队（值守轮+S0 死窗恢复+5x HANDOVER） | 当前活: r665 值守轮（S0 r664 close-tail 43 面死窗恢复+游离 HEAD rebase 治愈+恢复链即时送达·S1 48/48·S6 38/38·QA r665 5/5 零误标·bm-b 再停摆探测→老化线重启+trio_watch 证据·5x HANDOVER 增量窗 r661-665）"
       " | 最近实物: commit f5254941c（r664 close-tail 43 面重落地+quit+branch-f 治愈+daemon absorb 恢复链·origin fetch+rev-list 0/0 送达双证）+results/_r665bmc_trio_watch.json（bm-b 再停摆证据+老化线 09:15）+qa/smoke-r665.md 5/5（93 trades·determinism=True·equity 终值面恒等·png 66,185B）+research/HANDOVER.md r665 5x 增量行+results/_r665bmc_s6_log.txt（38/38 rc0）@ {ts}"
       " | 下个里程碑: r666 aging-line verdict（bm-b 09:02 tick 后观察：仍暗过 09:15 线=r663 证据范式再升级 MSG+GM；复活=撤警+trio finalize 窗恢复）；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+CA 结构旗 re-eval；月界首考 10-31；下个 5x=r670 | "
       "S0: 轮首树脏=43 面 r664 close-tail 自产搁浅（上轮会话死于 close 后 commit 前）→attrition 门 CLEAN 预检→定向吸收 commit（r658 恢复律·-F 文件律·43 面全自产 allowlist 断言过）→**发现游离 HEAD=interactive rebase 遗留态**（r664 会话死于 pull --rebase 六 UU 冲突已 staging 未 continue·本机吸收 commit 恰充重放 pick2=round 664 close 内容·resolver 回执 6 面律逐面复核）→r420/r624 律 rebase --quit+branch -f main+symbolic-ref 同批治愈→余 2 picks 899ecd4ed/2f9d5e474=纯 daemon 活面 tick 可弃（工作树 live tick newer-wins·零信息损失）→daemon churn-absorb→pull --rebase 3/3 干净零 UU→**恢复链即时推送送达**（r659 先例·防再杀窗·origin 1aab5daf7→f5254941c·fetch+rev-list 0/0 双证）；"
       "S0.5 双扫: DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta·163/163 零未回执·inbox 0 未读（MSG-0801 在 processed=r664 S7 归档）；"
       "S1 48/48；S3: 板 open=0·watermark 绿·SAT 活 rc0（W170 12/12·W171 席位 bm-a r814 已知悉）·post_review 零 ✗ 零 P0；**bm-b 再停摆探测**（Q 1988/D 1654 冻结 @08:16:09 36min+hb 06:40:15 陈 132min+origin 08:12:15 后零新 commit→r800 25min wrapper 击杀假说·checkpoint 零损失律在位）→老化线重启（阈值 09:15·过线=r663 证据范式再升级·takeover 恒闭=bm-c host_gates FAIL p1c_stock r393 族·r668 watch-only）；"
       "S4: 新坑 1 条入件（silent-git 捕获单块多行字符串×foreach 按对象迭代不按行坑·DIRTY-COUNT 1/43 实弹·正法=消费面显式 -split·r511-③ 族姊妹面）·主件 append 后 staged blob {cb}B 余量 {hr}B；"
       "S6 38/38 rc0（dualrun ZERO-DRIFT streak 51 @403·bm-a hb 4min 新鲜=lane_io 守卫全诚实 skip·REPORT/LIVE-2026-10-07 幂等再生·token per-round ~12980+8487 粗估）；"
       "QA包r665: 显式 --round 665·pid 3200·qa/smoke-r665.md 首行轮标核验零误标→终态 5/5（93 trades·determinism=True·sharpe 0.1586·maxdd -4.33%·win 46.24%·equity 终值面恒等 r642-664·png 66,185B）；"
       "S7 自愈面全绿（loop pin=5 no-op·watchdog 幂等重注册·precommit/prepush 双爪 LF 归一重装·attrition CLEAN 4 台账零 active loss）；"
       "**诚实勘注：r664 轮报行预写「本地未达 origin commit 数=0」但其 close-tail 实际未 commit 未送达（会话死于 close 后 commit 前）=r532 close 尾行预写坑族再例——本行如实披露·43 面已由本轮 S0 重落地补达**；"
       "本地未达 origin commit 数=0（push+fetch+rev-list 自证送达）"
       " | 证据=commit f5254941c（origin 送达）+results/_r665bmc_trio_watch.json（再停摆证据+老化线）+qa/smoke-r665.md 5/5+qa/equity-curve-r665.png（66,185B）+results/_r665bmc_s6_log.txt 38/38 rc0+results/_r665bmc_s05_facts.json（双扫 DEC 635C3024+ORD 437E9CDD）+research/HANDOVER.md r665 5x 行+results/_attrition_guard_scan.json CLEAN+results/_r665bmc_qa_runner.out（terminal 5/5 显式 --round 665）"
       " | 下轮指针：(a) r666=aging-line verdict 轮（bm-b 09:02 tick 后探测：过 09:15 仍暗→r663 证据范式再升级新 MSG-bmc-ALL+GM fleet-note；复活→撤警+trio finalize 窗观察恢复）；(b) trio finalize 窗 10-05..10-09（Q 差 12·D 差 346·r638 fallback armed）；(c) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+CA 金周结构旗 re-eval；(d) 月界首考 10-31 装配面\n").format(
           ts=now, cb=codely_blob, hr=30720 - codely_blob)
_rr_tail = open(RR, "rb").read()[-30000:]
if b" | r665 bm-c | " in _rr_tail:
    print("RR row already present -- skip duplicate append")
else:
    with open(RR, "ab") as fh:
        fh.write(row.encode("utf-8") + b"\r\n")
    print("RR appended (canonical path)")

# ---- 2) state advance ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8-sig"))
assert st["round_no"] == 665, "unexpected round_no {}".format(st["round_no"])
st["round_no"] = 666
st["round_no_label"] = "round 665 (bm-c)"

did = ("r665 bm-c: S0 dead-window recovery round + 5x HANDOVER window (main products: r664 close-tail re-landing + detached-HEAD mid-rebase cure + bm-b re-stall aging-line restart + HANDOVER r661-665 increment entry). "
       "(1) S0: round-start dirty = 43 self-authored r664 close-tail faces (prior session killed post-close pre-commit, r658 pattern); attrition gate CLEAN pre-check; targeted absorb commit; discovered DETACHED HEAD = interactive rebase leftover (r664 session died after staging pick-2 6-UU resolutions, before continue); my absorb commit landed as the rebased pick-2 (round 664 close content, per r664 resolver receipt 6-face review); remaining picks 899ecd4ed/2f9d5e474 = pure regenerable daemon ticks dropped live-wins; r420/r624 cure: rebase --quit + branch -f main + symbolic-ref same batch; daemon churn-absorb; pull --rebase 3/3 clean zero UU; recovery chain pushed immediately (r659 kill-window precedent): origin f5254941c, fetch+rev-list 0/0. "
       "(2) S0.5 double-sweep: DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta; fleet orders 163/163 zero unacked; inbox 0 unread. "
       "(3) S1 smoke 48/48. S3: board open=0; watermark green; SAT alive rc0 (W170 12/12, W171 seat bm-a r814); post_review zero-NO zero P0. "
       "BM-B RE-STALL (r665 next-pointer (b) action): Q 1988/D 1654 frozen at 08:16:09 (36min), hb 06:40:15 stale 132min, zero new bm-b origin commits since 08:12:15; r800 wrapper-kill hypothesis (same failure mode as r664 close-tail); aging line RESTARTED (threshold 09:15, next bm-b tick 09:02); evidence results/_r665bmc_trio_watch.json; escalation armed per r663 pattern; takeover stays CLOSED (host_gates FAIL p1c_stock absent, r393 family, r668 watch-only). "
       "(4) S4: 1 new pit appended to CODELY.md (silent-git single-blob multi-line capture x foreach object-iteration pit; explicit -split law; r511-3 family sister face); staged blob {}B headroom {}B. ".format(codely_blob, 30720 - codely_blob) +
       "(5) S6 chain 38/38 rc0: dualrun ZERO-DRIFT streak 51 @403; bm-a hb 4min fresh so lane_io guards honest-skip; REPORT-2026-10-07 + LIVE-2026-10-07 regenerated idempotent; token per-round ~12980+8487 rough. "
       "(6) QA pack r665 5/5 zero-mislabel (explicit --round 665, pid 3200, first-line verified; 93 trades, determinism=True, equity final face-identical, png 66,185B). "
       "(7) 5x HANDOVER: r661-665 increment entry inserted at top of research/HANDOVER.md. "
       "(8) S7 self-heal green. HONESTY NOTE: r664 RR row pre-wrote delivery N=0 but its close-tail was never committed (session killed pre-commit) -- disclosed here per r532 pre-write-tail family; 43 faces re-landed by this round S0. "
       "Delivery: push+fetch+rev-list self-verify N=0.")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = ("r665: S0 dead-window recovery (43-face r664 close-tail absorb + detached-HEAD mid-rebase quit+branch-f cure + recovery chain delivered) + bm-b re-stall aging-line restart (Q/D frozen 36min, hb 132min stale, threshold 09:15) + 5x HANDOVER r661-665; QA r665 5/5 zero-mislabel; S6 38/38; DEC/ORD zero-delta 163/163; 1 new pit (silent-git foreach); attrition CLEAN")
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
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r665 s05 sweep = 635C3024 MATCH zero-delta; "
                        "value facts-driven from results/_r665bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r665 s05 sweep = 437E9CDD MATCH zero-delta; "
                                "fleet orders 163/163 zero unacked; value facts-driven from results/_r665bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = ("r665: S0 recovery + 5x HANDOVER round; QA r665 5/5 zero-mislabel (explicit --round 665, first-line verified); S6 38/38; DEC/ORD zero-delta; "
              "bm-b RE-STALLED (Q 1988/D 1654 frozen 08:16:09, hb 132min stale) -> aging line RESTARTED (threshold 09:15, evidence _r665bmc_trio_watch.json); "
              "detached-HEAD mid-rebase cured via r420/r624 (quit + branch -f + symbolic-ref); r664 close-tail 43 faces re-landed and delivered; "
              "1 new pit (silent-git single-blob foreach); attrition CLEAN; main staged blob {}B at close.".format(codely_blob))
st["next"] = ("(a) r666 = aging-line verdict round: probe bm-b after 09:02 tick; crossed 09:15 still dark -> re-escalate per r663 evidence pattern (new MSG-bmc-ALL + GM fleet-note); "
              "revived -> withdraw + resume trio finalize window watch (10-05..10-09, Q 12 short / D 346 short, r638 fallback armed). "
              "(b) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar + compute_audit golden-week structural flags re-eval. "
              "(c) W171 burn watch (bm-a seat, A 391_004..393_003 + B 393_004..393_203, 161st wave). "
              "(d) monthly exam 10-31 assembly face.")
st["verify"] = ("receipts: commit f5254941c on origin (r664 close-tail re-landing + cure chain, fetch+rev-list 0/0) "
                "+ results/_r665bmc_trio_watch.json (bm-b re-stall evidence + aging line) "
                "+ qa/smoke-r665.md 5/5 (explicit --round 665, pid 3200) + qa/equity-curve-r665.png (66,185B) "
                "+ results/_r665bmc_s6_log.txt 38/38 rc0 + results/_r665bmc_s05_facts.json (DEC 635C3024 + ORD 437E9CDD) "
                "+ research/HANDOVER.md r665 5x increment entry + results/_attrition_guard_scan.json CLEAN "
                "+ results/_r665bmc_qa_runner.out (terminal 5/5)")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 665->666")

# ---- 3) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8-sig"))
act = ("当前活: r665 值守轮收口（S0 r664 close-tail 43 面死窗恢复+游离 HEAD rebase 治愈+恢复链送达·S1 48/48·S6 38/38·QA r665 5/5 零误标·bm-b 再停摆→老化线重启 09:15·5x HANDOVER r661-665 增量行） | "
       "最近实物: commit f5254941c（r664 close-tail 43 面重落地+quit+branch-f 治愈+daemon absorb·origin fetch+rev-list 0/0 送达双证）+results/_r665bmc_trio_watch.json（bm-b 再停摆证据+老化线）+qa/smoke-r665.md（5/5·93 trades·determinism=True）+research/HANDOVER.md r665 5x 行 @ " + now +
       " | 下个里程碑: r666 aging-line verdict（bm-b 09:02 tick 后·过 09:15 线=r663 范式再升级）；trio finalize 窗 10-05..10-09（Q 差 12·D 差 346）；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 666, "round_no_label": "round 665 (bm-c)",
    "latest_artifact": ("commit f5254941c on origin (r664 close-tail 43-face re-landing + detached-HEAD rebase cure chain, fetch+rev-list 0/0) "
                        "+ results/_r665bmc_trio_watch.json (bm-b re-stall evidence + aging line restart) "
                        "+ qa/smoke-r665.md 5/5 (explicit --round 665, zero-mislabel, equity face-identical) "
                        "+ qa/equity-curve-r665.png (66,185B) + research/HANDOVER.md r665 5x increment entry @ " + now),
    "next_milestone": ("r666 = aging-line verdict (bm-b post-09:02-tick probe; crossed 09:15 -> r663-pattern re-escalation; revived -> withdraw + trio finalize window watch); "
                       "10-09 market reopen (data-chain re-arm + regime_guard v3 first bar + compute_audit flags re-eval); "
                       "monthly exam 10-31"),
    "verdict": ("alive: r665 recovery+standing round complete (S0 dead-window recovery: 43-face r664 close-tail absorb + detached-HEAD mid-rebase quit+branch-f cure + recovery chain delivered 0/0; "
                "QA r665 5/5 zero-mislabel explicit --round 665; S6 38/38 rc0; smoke 48/48; board open=0; satengine alive rc0 W170 12/12 + W171 seat bm-a; "
                "DEC/ORD double-sweep zero-delta 163/163; attrition CLEAN; post_review zero NO; 1 new pit appended (silent-git single-blob foreach); "
                "bm-b RE-STALLED (Q 1988/D 1654 frozen 08:16:09, hb 06:40:15 stale 132min, origin zero new commits) -> aging line RESTARTED threshold 09:15, "
                "evidence _r665bmc_trio_watch.json, escalation armed per r663 pattern, takeover CLOSED (host_gates FAIL p1c_stock); 5x HANDOVER r661-665 entry inserted; "
                "golden-week no-bar face held)"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"])
