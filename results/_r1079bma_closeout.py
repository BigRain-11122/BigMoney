import json, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
PREV_EPOCH = 1792380285  # r1078 closeout epoch (last_heartbeat mirror)

DID = ("r1079: (1) S0 up-to-date clean window (zero-rebase; 2 own live probe faces at head only, absorbed at closeout); "
       "(2) D-19 DOUBLE-DELTA consumed same-round: head delta a14c3693->84fb3ea9 = three rows 11:16 MV female-lead LoRA line (@bm-c) / "
       "11:21 full-fleet training mobilization (@bm-c+@bm-b + bm-a night-window MV training slot) / 11:27 lab-report triple (executed by lab window) "
       "-- all BigStream/lab seats, ZERO BigMoney-loop obligation per r1057/r1064 dual-company precedent; night-window llama-server kill note = L2 fallback law in place; "
       "closeout double-scan caught FRESH delta 84fb3ea9->d181d4a8 = 11:53 cadence v2 (全面提速令, cadence.md sec.8): Bigmoney-IterationLoop 10->5min already executed by lab window, "
       "verified live PT5M XML face read-back; (3) register_loop_task.ps1 healer default aligned to cadence v2 (hardcoded PT10M rebuild face -> PT5M; rebuild drift risk closed, "
       "fleet-shared so bm-b/bm-c pulls inherit the law-conformant healer); (4) round-start orphan 0/33; idle green_idle=true idle_rounds=1 consumed same-round via --worked "
       "(D-19 double consumption + healer fix + S6 chain = actual product work per O-20261007-2315); (5) S2 zero claimable (job_list empty, task board 187/0 open, backlog pool 0, "
       "satengine ALIVE rc0 queue0 idle = W278 bm-c wave supply face); (6) S1 smoke 49/49; S6 46-leg face (43 Leg + live_paper) all rc0 bad=0 "
       "(_r1079bma_s6chain.ps1 = r1078 face verbatim clone; Monday intraday no-op faces honest; MF legs FREEZE-RETAIN r1073 disposition held, post-15:30 retest adjudication armed); "
       "dualrun streak 51 held zero-drift; A5 Friday face held (V1/V3/V4 PASS, V2 1/5, V5 1/3, deadline 10-31 on-track); "
       "(7) S7 quartet green (loop present PT5M pin=8 no-op + watchdog present S4U-flip carried C-20261016-04 + claws identical both)")

VERIFY = ("_r1079bma_s6chain_rc.log 44 rc-lines bad=0 + live_paper rc0 + smoke 49/49 + orders_ack_scan CLEAN 105/114/0 x2 (head + closeout, dual-face zero divergence) "
          "+ D-19 ADVANCED ord 84fb3ea9 then d181d4a8 (read-back full-string equality both, mirrors synced 7+3) + dualrun streak 51 "
          "+ PACK-2026-10-19 overall PENDING (V1/V3/V4 PASS, V2 streak 1, V5 streak 1) + quartet schtasks x2 + claws IDENTICAL x2 "
          "+ cadence v2 PT5M live XML verify + healer PT5M fix (grep read-back)")

VERDICT = ("GREEN: r1079 waiting-state maintenance round (Monday intraday, pre-15:30 bars window) -- D-19 double-delta consumed zero-obligation "
           "(3 training-line rows @bm-c/@bm-b/MV seats + 11:53 cadence v2 with loop 5-min face verified live), healer default aligned to cadence v2 (rebuild drift closed), "
           "S6 all rc0 (intraday no-ops honest), dualrun streak 51, A5 on-track 10-31, smoke 49/49, ack CLEAN 105/114/0, quartet green, "
           "zero claimable work (waiting-state faces declared one-line each)")

TASK = "r1079: D-19 double-delta consumption + cadence v2 healer alignment + S6 46-leg chain"
CUR = "r1079: D-19 double consumption + S6 46-leg chain (all rc0) + cadence v2 5-min face verified + healer aligned"
NEXT = ("r1080: (1) Monday 15:30 bars window: papers chain + MF lane retest adjudication (first post-close window after r1073 FREEZE-RETAIN; day-8..12 blockade chain evidence on file); "
        "(2) A5 streak advance on new-bar (V2 toward 5, V5 toward 3); (3) W278 prereg/splice/finalize watch (bm-c lane, W279 owner naming rides sec.7/8); "
        "(4) cadence v2 follow-through: @bm-b/@bm-c cadence-v2 receipts watch (22:0x window); loop 5-min cadence live from next fires (IgnoreNew overlap-guarded)")
NEXTM = ("A5 first-line acceptance 10-31 (V2 1/5 + V5 1/3 accruing on new-bar days); Monday post-15:30 MF retest adjudication; committee three-in-one report <=10-25")
ART = ("results/_r1079bma_s6chain.ps1 + results/_r1079bma_s6chain_rc.log (44 rc-lines bad=0) + Tools/register_loop_task.ps1 cadence-v2 healer fix (PT10M->PT5M) + PACK-2026-10-19 A5 re-read")
ACKNOTE = ("r1079: zero NEW fleet O-files in repo (scan CLEAN 105/114/0 x2 dual-face parity); D-19 group ord delta consumed TWICE "
           "(a14c3693->84fb3ea9->d181d4a8: 11:16/11:21/11:27 training-line rows + 11:53 cadence v2 -- zero BigMoney-loop obligation, "
           "loop 5-min face verified live + healer default aligned); dec 8706acd8 hold; inbox empty")
ORDSEEN = ("r1079: D-19 ord double-delta consumed (84fb3ea9 + d181d4a8): 11:16/11:21/11:27 training-line rows + 11:53 cadence v2; "
           "zero obligation, loop 5-min face verified + healer aligned")

REPORT_LINE = (NOW + " | r1079 | 维护轮（水位 green red=false·satengine ALIVE rc0 queue0 idle·S0 up-to-date 全净零 rebase）："
    "主交付=D-19 双增量同轮消费（轮首 a14c3693->84fb3ea9=11:16 女主 LoRA 线 @bm-c/11:21 满载训练动员令 @bm-c+@bm-b+bm-a 夜窗 MV 训练位/11:27 实验室三连 executed 实验室窗——"
    "全 BigStream/lab 席位面·r1057/r1064 双公司判例零 BigMoney-loop 义务·夜窗 llama-server 杀面=L2 fallback 法在位）+收尾双扫捕新增量 84fb3ea9->d181d4a8=11:53 全面提速令 v2"
    "（cadence §8·Bigmoney-IterationLoop 10->5min 实验室窗已执行·本窗 XML PT5M live 读回实证）+register_loop_task.ps1 治愈器默认对齐 cadence v2（硬编 PT10M 重建面->PT5M·"
    "重建漂移风险闭口·fleet 共享脚本 bm-b/bm-c 拉取即承法面治愈器）；轮首孤儿 0/33；idle green_idle=true idle_rounds=1 -> --worked 清零（D-19 双消费+治愈器修+S6 链=实际产出）；"
    "S2 零可领如实（job_list 空·任务板 187/0 open·backlog 池空·satengine queue0 idle=W278 bm-c 波道供给面）；S1 smoke 49/49；"
    "S6 46 腿面（43 Leg+live_paper）全 rc0 bad=0（_r1079bma_s6chain.ps1=r1078 面 verbatim 克隆·周一盘中 no-op 恒真·MF 腿 FREEZE-RETAIN r1073 处置维持·15:30 后窗重测裁决 armed）；"
    "dualrun 连绿 51 持有零漂移；A5 周五面持有（V1/V3/V4 PASS·V2 1/5·V5 1/3·deadline 10-31 轨上）；S7 四件套绿（loop 在位 PT5M pin=8 no-op·watchdog 在位 S4U flip=carried C-20261016-04·双爪 IDENTICAL）"
    " | 证据=_r1079bma_s6chain_rc.log 44 rc 行 bad=0+live_paper rc0·smoke 49/49·orders_ack CLEAN 105/114/0 x2 双面零分歧·D-19 ADVANCED 84fb3ea9+d181d4a8 读回恒等（镜像 7+3）·"
    "dualrun streak 51·PACK-2026-10-19 overall PENDING·quartet schtasks x2+双爪 IDENTICAL·cadence v2 PT5M XML verify+治愈器 PT5M 修正 grep 读回 "
    "| 本地未达 origin commit 数=0（push 后 fetch+ls-tree 验·state push_verified 面记录） "
    "| 下轮指针：今日 15:30 后窗=papers 链+MF lane 重测裁决（FREEZE-RETAIN 后首个收盘窗·day-8..12 封锁链证据在案）+A5 随新 bar 推进；"
    "W278 prereg/splice/finalize 观察（bm-c 车道）；cadence v2 随访=@bm-b/@bm-c 回执窗 22:0x·loop 5-min 节奏自下轮起 live（IgnoreNew 防重叠）")

def upd(path, is_heart):
    d = json.load(open(path, encoding="utf-8"))
    d["round_no"] = 1080
    d["round"] = 1079
    d["loop_round"] = 1079
    d["round_no_label"] = "r1079"
    d["last_round"] = "r1079"
    d["last_heartbeat_epoch_utc"] = PREV_EPOCH
    d["heartbeat_epoch_utc"] = EPOCH
    d["heartbeat_epoch_utc_type_int"] = True
    d["clock_read"] = NOW
    d["ts"] = NOW
    d["last_seen"] = NOW
    d["last_run"] = NOW
    d["last_round_at"] = NOW
    d["last_round_ts"] = NOW
    d["last_round_closed"] = NOW
    d["last_action_at"] = NOW
    d["updated"] = NOW
    d["updated_at"] = NOW
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 0
    d["orphan_faces"] = 0
    d["orphan_killed"] = 0
    d["did"] = DID
    d["current"] = CUR
    d["current_task"] = TASK
    d["task"] = TASK
    d["last_action"] = DID
    d["now_active"] = "bm-a loop r1079 closeout (D-19 double consumption + cadence v2 healer + S6 chain)"
    d["verdict"] = VERDICT
    d["verify"] = VERIFY
    d["next"] = NEXT
    d["next_milestone"] = NEXTM
    d["last_artifact"] = ART
    d["latest_artifact"] = ART
    d["recent_artifact"] = ART
    d["orders_ack_note"] = ACKNOTE
    d["last_orders_seen"] = ORDSEEN
    d["last_orders_at"] = NOW
    d["last_decisions_at"] = NOW
    if is_heart:
        d["last_round_label"] = "r1079"
        d["health"] = "alive"
    json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    # verify epoch int + clock T-format
    d2 = json.load(open(path, encoding="utf-8"))
    assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in d2["clock_read"] and " " not in d2["clock_read"], "clock_read must be T-separated"
    print("updated", path, "epoch", d2["heartbeat_epoch_utc"], "clock", d2["clock_read"])

upd(r"state-bm-a.json", False)
upd(r"fleet\machines\bm-a.json", True)

with open(r"round_reports-bm-a.md", "a", encoding="utf-8") as fh:
    fh.write(REPORT_LINE + "\n")
print("report line appended, len", len(REPORT_LINE))
