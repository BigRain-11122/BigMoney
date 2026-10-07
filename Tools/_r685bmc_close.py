# -*- coding: utf-8 -*-
"""r685 bm-c close batch: HANDOVER 5x line insert + state + heartbeat + round
report line (python single source for JSON int-type law R170/R178/R262).
Round r685 = 5x HANDOVER window + S0 integration-battle round (r684 leftover
behind9/ahead3 queue redeemed). One new pit direct-written to
pit-git-resolver-rebase.md (main-file margin 15B red-line).
Pattern credit: Tools/_r684bmc_close.py."""
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

HO_LINE = (
    "> bm-c round 685 五倍数核对（2026-10-07 15:5x·增量窗 r681-685 五轮）：增量窗 r681-685=bm-c 面（**金周尾日值守主线+复市 T-1 连守+r684 遗留集成队列兑现战役轮（r685）+统一链 W174 finalize 落账 788,212**——r681 值守轮〔W174 finalize 后首收口：absorb 33977a1b7+rebase 落 bm-a r826/r827 W174 burn+finalize 波归 0·双扫零 delta·orders 166/166〕；r682 值守轮〔absorb 39db117fe+rebase 落 3 含 bm-a r828 水位键修复面〕；r683 值守轮〔第三连守：absorb bbf333c1a+零 rebase〕；r684 值守轮〔第四连守：absorb d307dbe3d+QA r684 5/5 零误标（93 trades·png 66,204B）+update_lhb 节流窗过 11/11 页 refetch rc0+bm-a 心跳陈 27-29min→7 共享单写面 stale-takeover derive（O-2100 §2.4）+postscript push-race 分支 machine/bm-c-r684 交付+pit-git-resolver.md 直写 1 条〕；r685=本核对轮〔**S0 集成战役**：r684 遗留 behind9/ahead3 队列兑现——5-pick rebase 撞 compute_audit.json diff3 冲突→三段 blob（ls-files -u sha 通道）两分法合并（latest newer-wins 15:08:08+history union 207→209 零重零乱序）→r808 手工 commit 完成 pick→r787 假冲突拒进→stage 解锁却生**重复 pick 载体 ea6662523**（如实披露·零独占内容）→pick4 absorb-x5 面冲突 ours-live-wins（r440 律）→quit+r624 branch -f 治愈→absorb-A 70f2631dc 有据 drop（陈旧 daemon 快照超集证明）→rebase 6/6 干净+push 送达 N=0·HEAD==origin；+5x HANDOVER 义务（本行）+S4 新坑 1 条直写 pit-git-resolver-rebase.md（r808×r787 同窗连用禁律·1,719B·收据 _r685bmc_pit_directwrite.json）+smoke 48/48+S0.5 双扫 DEC/ORD 双零 delta+orders 166/166+S6 38/38 rc0（dualrun streak 5·CA 旗 [supply_gap,supply_floor]=W174 席位间隙已知面待 W175 freezer 回填自清·水位 py_low_board_clear 合法 idle）+QA r685 5/5 零误标（png 66,191B）+tripwire（1184 行 CLEAN）+attrition CLEAN+四自愈件幂等〕〕）。产物清单漂移=qa/smoke-r68{1..5}.md+qa/equity-curve-r68{1..5}.png〔五轮常设证据包族〕+results/_r68{1..5}bmc_* 工件族〔s05 facts+s6 log+close 收据族+S0 集成日志 r685〕+Tools/_r68{1..5}bmc_{s05,s6,qa_ignite,close}.py 驱动族+Tools/_r685bmc_{pit_directwrite,ca_merge2}.py〔r685 冲突合并器+坑律直写器〕+research/pit-git-resolver-rebase.md〔r685 +1 条·13,288B〕+results/_r685bmc_pit_directwrite.json+docs/daily_report/REPORT-2026-10-07.md+docs/live_usage/LIVE-2026-10-07.md〔S6 链再生〕；统一链 **788,212 实读**（live head=results/perpetual_faces/n1_w174_results.json science_gates.ledger 实读·W174 finalize bm-a 已落账 786,012+2,200）；板 open=0·job_list 0·satengine rc0 活·池 ready=1/unclaimed=0（N1 关面 O-2115 §2 维持）·试用劳力线不触发（fund-trio D 族 bm-b 在飞 finalize 窗至 10-09+金周无 bar+W3 判决席位 bm-a）；指针：**10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar enforce+fund_premium 15:30 首采（bm-c 车道·readiness 已验 r671/r673/r675/r682/r684）+O-2115 验收包复跑（治理日）**；W175 freezer（bm-a·B-band 399_804..400_003 re-derive-MANDATORY）补池后 CA supply 旗预期自清；trio finalize 窗至 10-09（bm-b）；月界首考 10-31（T-143 交付 10-29）；下一 5x=bm-c r690。\n"
)

RR_LINE = (
    TS + " | r685 bm-c | dept:工程/舰队（金周尾日值守轮·复市前夜 T-0·5x HANDOVER 窗·S0 集成战役轮） "
    "| 水位绿（red=false·lane healthy·probe py_low_board_clear=合法 idle·金周无 bar） "
    "| 当前活: r685 S0 集成战役=r684 遗留 behind9/ahead3 队列兑现——5-pick rebase 撞 compute_audit.json diff3 冲突→三段 blob（ls-files -u sha 通道）两分法合并"
    "（latest newer-wins 15:08:08+history union 207→209 零重零乱序）→r808 手工 commit 完成 pick 734224bf9→r787 假冲突拒进→stage 解锁却生重复 pick 载体 ea6662523"
    "（如实披露·零独占内容=2 daemon 面 7+/7-）→pick4 absorb-x5 冲突 ours-live-wins（r440 律）→quit+r624 branch -f 治愈→absorb-A 70f2631dc 有据 drop"
    "（陈旧 daemon 快照超集证明）→rebase 6/6 干净+push 送达 rc0·HEAD==origin·N=0·"
    "S0.5 双扫=DEC 4C32527B/ORD A8B02C8A 双零 delta（轮首腿）+orders 166/166 零未回执+inbox 0 未读·S1 48/48·"
    "S3 SAT 活 rc0（burns_active=[]·queue_next=[]=O-2115 §2 N1 收口维持）+板 0 open（job_list 0+fleet tasks 0 open）+池 ready=1/unclaimed=0"
    "+post_review 维持 45Y/0N/5W 稳定·试用劳动力线不触发（fund-trio D 族 bm-b 在飞 finalize 窗至 10-09+金周无 bar+W3 判决席位 bm-a）·"
    "S6 38/38 rc0（dualrun ZERO-DRIFT streak 4→5·CA 旗 [supply_gap,supply_floor] 在场=W174 席位间隙已知面待 W175 freezer（bm-a）补池自清·"
    "bm-a 心跳陈 31min→多面 stale-takeover derive 按 O-2100 §2.4（scorecard/paper_export/daily_scorecard/build_status）·"
    "REPORT/LIVE-2026-10-07 幂等再生 ORANGE·fund_premium pre-15:30 no-op（bm-c 车道 10-08 15:30 首采就绪）·token_meter 落盘）·"
    "QA r685 5/5 零误标（explicit --round 685 分离 pid 6932 终态轮询过（r640 律）·93 trades·determinism=True·png 66,191B·"
    "equity final=1,017,839 跨轮恒等·latest_panel_bar=2026-09-30 金周 no-op 如期）·"
    "S4 新坑 1 条直写域件（主件余量 15B 红线→pit-git-resolver-rebase.md +1,719B·收据 _r685bmc_pit_directwrite.json）·"
    "S7 四自愈件幂等（loop pin=5 no-op·watchdog·双爪）+tripwire CLEAN（1184 行）+attrition CLEAN "
    "| 验证证据: qa/smoke-r685.md（5/5·首行轮标 r685）+qa/equity-curve-r685.png（66,191B）"
    "+results/_r685bmc_s6_log.txt（38/38 rc0）+results/_r685bmc_s05_facts.json（双扫）"
    "+results/_r685bmc_pit_directwrite.json+results/_r685bmc_s0_log.txt（S0 集成全程证据）+results/_attrition_guard_scan.json CLEAN "
    "| 下轮指针: 10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar enforce+fund_premium 15:30 首采（bm-c 车道·readiness 已验 r671/r673/r675/r682/r684）"
    "+O-2115 验收包复跑（治理日·scripts/o2115_acceptance_pack.py run）；W175 freezer（bm-a·B-band re-derive-MANDATORY）补池后 CA supply 旗预期自清；"
    "trio finalize 窗至 10-09（bm-b）；月界首考 10-31（T-143 交付 10-29）；下一 5x=bm-c r690 "
    "| 本地未达 origin commit 数=0（HEAD==origin 实测·closeout commit 后 push+fetch 终值收口）"
)


def read_json(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)


def main():
    # --- HANDOVER 5x line insert (after title line 1) ---
    hp = os.path.join(ROOT, "research", "HANDOVER.md")
    with open(hp, "r", encoding="utf-8", newline="") as fh:
        lines = fh.read().split("\n")
    assert lines[0].startswith("# Bigmoney"), "HANDOVER title anchor"
    already = any("round 685 " in l for l in lines[:4])
    assert not already, "r685 5x line already present"
    lines.insert(1, HO_LINE.rstrip("\n"))
    with open(hp, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(lines))
    print("HANDOVER 5x line inserted at line 2")

    # --- state ---
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = read_json(sp)
    assert st["round_no"] == 685, "round_no anchor mismatch: %s" % st["round_no"]
    st["round_no"] = 686
    st["round_no_label"] = "round 685 (bm-c)"
    st["last_round_at"] = TS
    st["last_round_ts"] = TS
    st["last_seen"] = TS
    st["last_seen_at"] = TS
    st["ts"] = TS
    st["updated"] = TS
    st["updated_at"] = TS
    st["last_run_at"] = TS
    st["clock_read"] = TS
    st["last_decisions_read_at"] = TS
    st["current_task"] = (
        "当前活: r685 S0 集成战役轮+5x HANDOVER 窗（复市前夜 T-0·第五 bm-c 连守轮）："
        "S0 集成 r684 遗留队列（5-pick rebase+compute_audit diff3 两分法合并+r808 手工 commit+重复载体 ea6662523 如实披露"
        "+r624 治愈+absorb-A 有据 drop+push 送达 N=0）·S0.5 双扫双零 delta·S1 48/48·S3 SAT 活+水位绿+板 0+池 ready1/unclaimed0·"
        "S6 38/38 rc0（dualrun streak 5·CA 旗=W174 席位间隙已知面·bm-a 心跳陈→多面 stale-takeover derive）·"
        "QA r685 5/5 零误标（93 trades·png 66,191B）·S4 新坑 1 条直写域件·tripwire+attrition CLEAN+四自愈件幂等 "
        "| 最近实物: qa/smoke-r685.md（5/5）+qa/equity-curve-r685.png（66,191B）+research/pit-git-resolver-rebase.md（+1,719B 新坑律）"
        "+results/_r685bmc_s6_log.txt（38/38）+results/_r685bmc_pit_directwrite.json "
        "| 下个里程碑: 10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar enforce+fund_premium 15:30 首采（bm-c 车道）"
        "+O-2115 验收包复跑（治理日）；W175 freezer（bm-a）；trio finalize 窗至 10-09（bm-b）；月界首考 10-31"
    )
    st["current_task_at"] = TS
    st["activity_now"] = st["current_task"]
    st["did"] = (
        "r685 bm-c: S0 integration-battle round + 5x HANDOVER window, reopen T-0 eve "
        "(fifth consecutive bm-c guard round). (1) S0: redeemed r684 postscript leftover "
        "queue (behind 9 / ahead 3) -- absorb x2 own faces; 5-pick pull --rebase hit "
        "diff3 conflict on results/compute_audit.json -> three-stage blob extraction "
        "(ls-files -u sha channel per r648 law) + two-law merge (latest newer-wins "
        "15:08:08, history append-union 207->209 zero-dup zero-disorder, validation "
        "suite PASS); rebase --continue refused despite clean index (ls-files -u "
        "empty) with misleading conflict message (r787 family) -> manual commit "
        "734224bf9 completed pick 2 (r808 law); staging daemon faces then unblocked "
        "continue but sequencer re-committed them as DUPLICATE pick carrier "
        "ea6662523 (same message, 2 daemon faces only, zero unique content -- "
        "honestly disclosed, no surgery); pick 3 postscript applied clean "
        "(3178e6278: resolver.md append + receipt); pick 4 absorb-x5 conflicted on 2 "
        "saturation faces -> ours-live-wins (r440 law) after rebase --quit; "
        "absorb-A 70f2631dc DROPPED with evidence (pure stale daemon snapshot, "
        "worktree faces strictly newer superset); r624 cure (branch -f main + "
        "checkout, symbolic-ref verified); final rebase 6/6 clean + push rc0, "
        "HEAD==origin, N=0. NEW PIT direct-written to pit-git-resolver-rebase.md "
        "(1,719B): r808 manual-commit-completed pick + r787 stage-unlock must NOT "
        "combine in same pick window (duplicate carrier hazard). (2) S0.5 "
        "double-sweep: DEC 4C32527B / ORD A8B02C8A zero-delta; fleet orders 166/166 "
        "zero unacked; inbox 0. (3) S1 smoke 48/48. S3: satengine alive rc0, "
        "watermark red=false probe py_low_board_clear legal idle; board 0 open; "
        "pool ready=1 unclaimed=0 (N1 closure per O-2115 sec-2 maintained); "
        "post_review 45Y/0N/5W stable; trial-labor line not triggered. (4) S6 "
        "chain 38/38 rc0: dualrun ZERO-DRIFT streak 5; CA flags "
        "[supply_gap,supply_floor] = W174 between-seat gap known face, natural "
        "clear expected after W175 freezer (bm-a) refill; bm-a heartbeat stale "
        "31min -> shared single-writer faces stale-takeover derived by bm-c per "
        "O-2100 sec-2.4; REPORT/LIVE-2026-10-07 idempotent ORANGE; fund_premium "
        "pre-15:30 no-op (bm-c lane ready for 10-08 15:30 first snapshot); "
        "token_meter row saved. (5) QA r685 5/5 zero-mislabel (explicit --round "
        "685 detached pid 6932, terminal polled per r640 law; 93 trades, "
        "determinism=True, png 66,191B, equity final=1,017,839 cross-round "
        "identical, latest_panel_bar=2026-09-30 golden-week no-op expected). (6) "
        "S7: 4 self-heal idempotent (loop pin=5 no-op, watchdog, claws); "
        "tripwire CLEAN (1184 lines); attrition CLEAN. (7) 5x HANDOVER line "
        "inserted (r681-685 window), chain head 788,212 live-read (W174 finalize "
        "landed)."
    )
    st["last_round"] = st["did"]
    st["last_round_summary"] = (
        "r685: S0 integration-battle + 5x HANDOVER round: r684 leftover queue "
        "redeemed (compute_audit diff3 two-law merge 209 hist; duplicate carrier "
        "ea6662523 disclosed; absorb-A evidence-dropped; r624 cure; push N=0); "
        "DEC/ORD zero-delta; orders 166/166; smoke 48/48; SAT alive; WM green "
        "legal idle; S6 38/38 rc0 (dualrun streak 5; CA flags known face); QA "
        "r685 5/5 zero-mislabel; 1 new pit direct-written (resolver-rebase "
        "domain, receipt); tripwire+attrition CLEAN; 4 self-heal idempotent; "
        "HANDOVER r681-685 line; reopen 10-08"
    )
    st["next"] = (
        "(a) 10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + REGIME_GUARD "
        "v3 first-bar enforce activation + fund_premium first snapshot 15:30 "
        "(bm-c lane, readiness verified r671/r673/r675/r682/r684) + O-2115 "
        "acceptance pack rerun (governance day, scripts/"
        "o2115_acceptance_pack.py run). (b) W175 next-freezer B-band "
        "399_804..400_003 re-derive-MANDATORY (bm-a lane; pool refill there = CA "
        "supply flags expected natural-clear AFTER; bm-a heartbeat stale face = "
        "watch its loop revival). (c) trio finalize window watch to 10-09 (bm-b "
        "canonical lane). (d) monthly exam 10-31 assembly face (T-143, "
        "deliverable 10-29). (e) next bm-c 5x HANDOVER = r690. (f) per-close: "
        "tripwire scan (E09 law) + dup-heal scan."
    )
    st["note"] = (
        "r685: S0 integration-battle + 5x HANDOVER; compute_audit diff3 merge; "
        "duplicate carrier disclosed; 1 new pit direct-write; QA r685 5/5; "
        "tripwire/attrition CLEAN"
    )
    st["verify"] = (
        "receipts: qa/smoke-r685.md (5/5, first-line round label r685 verified) + "
        "qa/equity-curve-r685.png (66,191B) + results/_r685bmc_s6_log.txt (38/38 "
        "rc0) + results/_r685bmc_s05_facts.json (double-sweep) + results/"
        "_r685bmc_pit_directwrite.json (pit direct-write receipt) + results/"
        "_r685bmc_s0_log.txt (S0 integration battle log) + results/"
        "_attrition_guard_scan.json CLEAN + research/HANDOVER.md r685 5x line"
    )
    assert isinstance(st.get("last_decisions_sha"), str) and len(st["last_decisions_sha"]) == 64
    assert isinstance(st.get("last_orders_sha"), str) and len(st["last_orders_sha"]) == 40
    write_json(sp, st)

    # --- heartbeat ---
    hbp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    hb = read_json(hbp)
    assert isinstance(hb.get("heartbeat_epoch_utc"), int)
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["clock_read"] = TS
    hb["ts"] = TS
    hb["last_seen"] = TS
    hb["last_seen_at"] = TS
    hb["updated_at"] = TS
    hb["updated"] = TS
    hb["round_no"] = 686
    hb["current_task"] = st["current_task"]
    hb["current_task_at"] = TS
    hb["activity_now"] = st["current_task"]
    hb["prod_lanes"] = (
        "r685 S0 集成战役轮+5x HANDOVER（r684 遗留队列兑现 N=0 送达+compute_audit diff3 两分法合并"
        "+QA r685 5/5 零误标+smoke 48/48+S6 38/38（dualrun streak 5·CA 旗=W174 席位间隙已知面）"
        "+S4 新坑 1 条直写域件+attrition/tripwire CLEAN·板空+水位绿+SAT 活·金周无 bar 至 10-08 复市）"
    )
    hb["health"] = (
        "alive (r685 S0 integration-battle + 5x HANDOVER round clean: loop pin=5, "
        "watchdog present, claws MATCH, attrition CLEAN, tripwire CLEAN; "
        "golden-week no-bar until 10-08 reopen; fund_premium lane ready for "
        "10-08 15:30 first snapshot; CA supply flags = between-seat gap honest "
        "face until W175 freezer refills; bm-a heartbeat stale 31min observed "
        "r685 -> shared faces stale-takeover derived by bm-c per O-2100 sec-2.4)"
    )
    hb["verdict"] = (
        "alive: r685 S0 integration-battle + 5x HANDOVER round (r684 leftover "
        "behind9/ahead3 queue redeemed, push delivered N=0); compute_audit.json "
        "diff3 two-law merge (latest newer-wins + history union 209); duplicate "
        "pick carrier ea6662523 honestly disclosed (zero unique content); "
        "absorb-A evidence-dropped; QA r685 5/5 zero-mislabel (93 trades "
        "determinism=True, png 66,191B, equity 1,017,839 cross-round identical); "
        "smoke 48/48; S6 38/38 rc0 (dualrun streak 5; CA flags known face); s05 "
        "double-sweep zero-delta both keys; board open=0; satengine alive rc0; 1 "
        "new pit direct-written (pit-git-resolver-rebase.md, receipt); "
        "tripwire+attrition CLEAN; 4 self-heal idempotent; HANDOVER r681-685 "
        "line; chain head 788,212 live-read; reopen 10-08"
    )
    hb["next_milestone"] = (
        "10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + REGIME_GUARD v3 "
        "first-bar enforce + fund_premium 15:30 first snapshot (bm-c lane) + "
        "O-2115 acceptance pack rerun (governance day); W175 freezer B-band "
        "re-derive (bm-a; pool refill = CA supply flags expected clear after); "
        "trio finalize to 10-09 (bm-b); monthly exam 10-31 (T-143 deliverable "
        "10-29); next bm-c 5x HANDOVER = r690"
    )
    hb["latest_artifact"] = (
        "qa/smoke-r685.md (5/5) + qa/equity-curve-r685.png (66,191B) + research/"
        "pit-git-resolver-rebase.md (+1,719B new pit law) + results/"
        "_r685bmc_pit_directwrite.json @ " + TS
    )
    hb["note"] = (
        "r685: S0 integration-battle + 5x HANDOVER; QA r685 5/5; 1 new pit "
        "direct-write; tripwire/attrition CLEAN"
    )
    assert isinstance(hb["heartbeat_epoch_utc"], int)
    write_json(hbp, hb)

    # --- round report ---
    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    with open(rp, "a", encoding="utf-8", newline="") as fh:
        fh.write(RR_LINE + "\n")
    print("close batch done: HANDOVER line, state 686, heartbeat epoch", EPOCH, "rr line appended")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
