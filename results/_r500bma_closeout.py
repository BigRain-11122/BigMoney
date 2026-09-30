# -*- coding: utf-8 -*-
"""r500 bm-a closeout: round report entries + HANDOVER 5x overdue window + state + heartbeat."""
import json
import time
import datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
NOW_SEC = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")[:22]  # keep +08:00 shape
EPOCH = int(time.time())

R499 = ("2026-10-01T03:30+08:00 | r499 补记（猝死窗·本行由 r500 按 r471 收养律补记·工作已由该会话自 commit "
        "883a51d81+9ed1ae49f 推送在案）| dept:研究/工程 | G2_OVERLAP_CENSUS_P2 普查烧批 rc0（237 行=M4 213+M5 24："
        "4 DUP-FORMULA-VERIFIED 引在库判词免重烧+38 DRIFT+126 NEW-FACE→registry H-P2 行供给池 7→133+69 UNVERIFIABLE "
        "prose 诚实不入池；5/8 冻结预测双向证伪·legacy 矿=真新富矿非 WQ/GTJA 拷贝；norm_v2 括号预筛+extractor 保真 "
        "4 轮工程修·selftest 31/31·prereg §7/§8 回填·零回测零网络 trials +0）| 后续：03:42-03:44 S6 全链产物+1 件 "
        "bmb 诊断收件箱消息（已被 bm-b r491 自愈面超越·存档性质）由 r500 收养上链 [via bm-a]")

R500 = ("2026-10-01T04:4x+08:00 | r500（猝死续作收口窗·双前驱：r499 会话 03:30 已 commit+push 后 03:42 续跑 S6 于 "
        "03:44 崩于 S7 前〔state/报告滞留 r498〕+03:58 会话静默死亡 exit=0 零 commit 零痕迹）| dept:工程 | "
        "WM=red（runnable-work-idle-low-cpu·py 尾 0/0.3/0.5%）合法 idle 白名单证成非违令：ready2="
        "EXCLUSION-MARGINAL/CROSS-START-FACEB 皆 lane_owner=bm-b 反重复让道 + W14-GENERATE waiting="
        "W13-judge-inflight 串行波门（prereg FROZEN bm-b r471+runner LANDED r472·门开自动点火）+ T-131 GM 署名门 + "
        "板 0 可领 | 实物1=r471 逐件验后收养：r499 S6 链产物 58 件全 parse-verified（receipt results/_r500bma_dirty_check.py）"
        "→ commit 914d84a9e+push | 实物2=15-UU rebase 撞车批正典解完推送：分类器 13 分类+5 UNKNOWN 逐件手工定性"
        "（LIVE/REPORT 孪生=twin coupling r327/r329 同侧字节直拷·_attrition_guard_scan=per-run snapshot）→ 6 ALL_FACES "
        "merge_lane_views resolve（compute_audit 203 行 union 零丢失等）+9 snapshot/js-wrapper/twin 深扫 ts 探针 "
        "take-new（全件 :3: 03:42-03:44 面>对岸 03:40 面·dashboard js R209 包装字节保留断言过）→ rebase Successfully+"
        "push 3a5ae3b53..914d84a9e + reconcile（compute_audit/gate_attrition drift=观察相已知族 r464/r498 定谳面留痕）+ "
        "resolver 留痕 results/_r500bma_resolve.py | 收口三面：state 498→500（两轮缺口补接·r226 判例）+r499 补记入轮报告+"
        "HANDOVER R461-500 5x 欠账窗披露单行（r460 baseline 355,375→live-read 368,797=LOWAMP-P1 finalize 头） | "
        "orders 139/139 零差集·D-19 sha ED4E0EAB MATCH 零动作（temp partial clone r481 配方·orders_sha D978090E 同窗存照）"
        "·inbox 2 件均非本机收件（0231=bmb→bmc r498 已阅·034x=bma→bmb 本机产出存档） | S6=采纳执行声明（r499 会话 "
        "03:42-03:44 全链 28 腿产物已收养上链·国庆休市无新 bar·本轮零重跑防冗余 churn·token L2 今日 0·三机效率行已面世"
        "REPORT-2026-10-01：bm-a 9.11/29 批·bm-b 11.15/4 批·bm-c N/A 诚实） | verify：smoke 47/47+58 件 parse 全过+"
        "attrition CLEAN（healed-4 历史）+工作树仅 daemon tick 余脏+自愈三件套（pin=8 no-op·4:28 下一班次实证·"
        "watchdog Ready 4:40·claw 在位核对）| 当前活=W13 JUDGE bm-b lane 看守+W14 池门自动点火观察；"
        "最近实物=914d84a9e（58 件收养+15-UU 正典解推送 04:3x）+三机核分布行（10-01 晨报验收面）；"
        "下里程碑=W13 judged 收口→W14 GENERATE 自动开烧（窗 ≤48h by 10-02）+10-02 晨报 bm-c 采样行汇入 | "
        "next: r501 W14 点火看守+EXCLUSION/CROSS-START bm-b 收敛观察+T-131 GM 门守候 [via bm-a]")

HANDOVER = ("[2026-10-01 04:4x r500 bm-a] HANDOVER 5x window entry (window R461-R500, OVERDUE BACKLOG DISCLOSED: "
            "r465-r495 bm-a 5x rows never filed -- window carried dead-session chains r483/r491/r494/r496/r497/r498/r499 "
            "plus S0-conflict demotions; per r420-cont/r460 precedent no backfill fabrication, single overdue window "
            "covered compactly here; bm-b r470/r480/r483 + bm-c r280/r290 rows cross-read for their lanes). BASELINE = "
            "r460 bm-a entry ledger anchor 355,375 (innovation_quota RRG-ROTATION-P1 head). LEDGER LIVE-READ ANCHOR "
            "THIS ROUND = 368,797 (results/lowamp_p1/lowamp_p1_results.json trials_ledger.total, live-read r500; window "
            "delta +13,422; exact per-batch arithmetic attributed to owner 5x rows: W13-SCREEN +593 r467 bm-a / "
            "W13-JUDGE +99 bm-b r459 / SLOT-8 COV +2,112 + SLOT-9 CROWD +2,004 + SLOT-10 PREMIUM_SENT +2,004 bm-c / "
            "ETF_OPS_BP2 +15 bm-b / LOWAMP-P1 +2,008 r498 bm-a / T-126 REEVAL18 演习线 + G2 P1/P2 census = zero-burn "
            "registry faces / N1-W2 faceb family / remainder per owner rows [cross-read not re-derived]). THIS-WINDOW "
            "bm-a PRODUCTS (R461-R500): (1) trial-labor supply chain: W13 SUMN freeze whole-package r461 (prereg+SEED "
            "20323000/20323500/20324000 three-step law+catalog pre-arm) + layer kit r463 + runner/GENERATE/SCREEN "
            "r466-467 (SUMN >=1.3x prediction FALSIFIED 0.28x-0.41x anti-enrichment toxic; 593 cells null p95 0.5116 "
            "in-band 8th; survivors 99/393; fix-first 5 sites + axis-expansion structural-chain pit law r467; JUDGE = "
            "waiting bm-b lane) ; LOWAMP-P1 judged batch CLOSED judged-negative r498 (18/18 faces, DSR 0.0%, n_trials "
            "2008, sr_ann -1.4475 vs sr_star 0.0816, T-132 done, 判负关线 per O-1901) ; G2_OVERLAP_CENSUS P1/P2 "
            "r493/r499 (M4/M5 237 rows, 126 NEW-FACE supply pool 7->133, 5/8 frozen predictions falsified, legacy mine "
            "= genuinely-new-rich). (2) engineering laws: T-133 s1 autofill saturation recursion r494 + O-2355 T-134 "
            "s3 multicore enforcement r496 (law-1 launch gate + law-2 core-sampler red flag + harvest-flip + lowamp "
            "handshake; LOWAMP campaign 0->2/18 live unfreeze) + T-134 s4 efficiency face r497 (compute_audit v2.4.2 "
            "parallel_efficiency + daily-report three-machine row) + T-135 Bonsai 4070S GPU night-window reverify r497 "
            "(tg128 58.33+-0.20 vs 09-27 anchor +6.6% PASS + co-reside can) + RW-4/RW-6 engine-repair faces "
            "(panel-gate data-gate three-leg / recompute pointer, non-verdict-approved honest note). (3) conflict-"
            "resolve canon chains: r483/r493/r494/r498/r500 multi-window UU batches canon-resolved + AA-envelope "
            "adjudication law r498 + yield-ticket pit law r483 + r500 15-UU closeout (classifier + merge_lane_views + "
            "deep-probe take-new + twin same-side byte-copy). (4) r500 (this round): double-predecessor crash "
            "closeout (r499 post-push S6 death + 03:58 silent zero-trace death) + 58-file S6 harvest adopted + "
            "state/report two-round gap healed. Maintenance: S6 28-36 legs rc0 per rounds (national holiday no-new-bar "
            "legal skip); smoke 47/47; orders ack 139/139 zero-diff; month-first trio r496 done. NEXT 5x = round 505 "
            "bm-a. Pointers: W13 JUDGE (bm-b judge-prep+burn lane) -> W14-GENERATE pool auto-fire (enqueue gate "
            "standing_no_judge_inflight); PERPETUAL_FACES s1 amendment v1.1 GM ruling pending (bm-b MSG-20261001-0400, "
            "W3 held); T-131 GM-signature gate standing wait; 10-02 morning report bm-c sampling row merge; "
            "SLOT-7/8/9/10 48h CEO clocks due 10-02 (bm-c rows).")


def append_eol_aware(path, text):
    raw = open(path, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    if not raw.endswith(b"\n"):
        pre = eol
    else:
        pre = b""
    with open(path, "ab") as f:
        f.write(pre + text.encode("utf-8") + eol + eol)


append_eol_aware("round_reports-bm-a.md", R499)
append_eol_aware("round_reports-bm-a.md", R500)
append_eol_aware("research/HANDOVER.md", HANDOVER)

# state file
st = json.load(open("state-bm-a.json", encoding="utf-8"))
st["round_no"] = 500
st["did"] = ("r500 (double-predecessor crash closeout): adopted dead r499-session S6 chain outputs (58 files "
             "parse-verified r471 law, receipt _r500bma_dirty_check.py) + 15-UU rebase collision canon-resolved "
             "(classifier 13+5 UNKNOWN adjudicated; 6 ALL_FACES merge_lane_views resolve + 9 snapshot/twin/js-wrapper "
             "deep-probe take-new all replay-side 03:42-03:44 fresher; resolver _r500bma_resolve.py) + push "
             "3a5ae3b53..914d84a9e + reconcile 2 drift faces (compute_audit/gate_attrition = known observation "
             "family r464/r498) + state/report two-round gap healed (r499 backfill entry + r500 entry + HANDOVER "
             "R461-500 overdue 5x window single row, baseline 355,375 -> live-read 368,797 LOWAMP finalize head) + "
             "WM red legal-idle proof (ready2 both bm-b lanes + W14 gate + T-131 GM gate) + orders 139/139 + "
             "D-19 ED4E0EAB MATCH zero-action + S6 adopt-execution declaration (no re-churn on holiday)")
st["verify"] = ("smoke 47/47 + 58-file parse sweep + attrition CLEAN (healed-4 hist) + rebase Successfully + push "
                "914d84a9e + reconcile post-resolve + self-heal trio (pin=8 no-op next-fire 4:28 verified, watchdog "
                "Ready 4:40, claw present)")
st["next"] = ("r501: W13 JUDGE bm-b-lane watch + W14-GENERATE pool auto-fire watch (gate opens on W13 judge "
              "completion) + EXCLUSION/CROSS-START bm-b convergence + T-131 GM gate standing wait + 10-02 morning "
              "report three-machine bm-c row merge")
st["last_round_at"] = NOW
st["current_task"] = "r500 closed: crash-continuation adoption + 15-UU canon resolve + push; watch W13-judge/W14 auto-fire"
st["updated"] = NOW
st["last_round"] = ("2026-10-01 r500: double-predecessor crash closeout + 58-file S6 harvest adopted + 15-UU "
                    "rebase canon-resolved + push 914d84a9e + state/report gap healed")
st["last_decisions_at"] = NOW
st["last_round_ts"] = NOW
json.dump(st, open("state-bm-a.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# heartbeat
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["last_seen"] = NOW
hb["current_task"] = st["current_task"]
hb["verdict"] = ("r500 closed (crash-continuation): dead r499-session S6 outputs adopted+pushed (58 files), "
                 "15-UU rebase canon-resolved (resolver _r500bma_resolve.py), state/report 2-round gap healed; "
                 "WM red legal-idle (bm-b lanes + W14 gate); W13 judge + W14 auto-fire on watch")
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["task"] = hb["verdict"]
hb["round_no"] = 500
try:
    import psutil
    hb["cpu_pct"] = psutil.cpu_percent(interval=0.5)
    hb["cpu_util_pct"] = hb["cpu_pct"]
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / 1e9, 1)
    hb["idle_ram_gb"] = hb["free_ram_gb"]
except Exception:
    pass
json.dump(hb, open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# self-verify heartbeat law: epoch must be int
chk = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO (R262 law)"
print("closeout OK: state round_no=500, heartbeat epoch int OK, clock OK, appended r499-backfill + r500 + HANDOVER row")
