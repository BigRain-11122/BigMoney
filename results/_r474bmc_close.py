"""r474 bm-c close writer: state + heartbeat programmatic update (r645 law:
json.dump + json.loads self-verify, epoch int, clock T-sep), CODELY.md one
pitfall-line append (byte-safe EOL detection per r641/r657 family), round
report main line append. ASCII console prints only (r446 probe law)."""
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
CODELY = os.path.join(ROOT, "CODELY.md")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")

now = datetime.datetime.now()
clock = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
clock_state = now.strftime("%Y-%m-%dT%H:%M:%S")
ts_space = now.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())

CURRENT_TASK = (
    "当前活: golden-week watch + pool owner_since regression adjudicated "
    "(bm-a r678 stale-base replay over fresher origin; owner=bm-b rows intact; "
    "bm-b next-tick self-heal expected; MSG-1332 issued) | 最近实物: "
    "results/_r474bmc_s6_log.txt (S6 38/38 rc0) + results/_r474bmc_poolreg.txt "
    "(regression dual-round origin evidence) + fleet/inbox/MSG-2026-10-04-1332-bmc-all.md "
    f"@ {clock} | 下个里程碑: r475 5x HANDOVER + fund-trio finalize window 10-05 "
    "10:30 opens (bm-b owner; ETA V 10-06 15:00 / Q long-pole 10-07 11:00); "
    "D-06 closure 10-07 (bm-c lead)"
)

LAST_ROUND = (
    "r474 bm-c: golden-week watch + pool owner_since regression adjudicated "
    "(bm-a r678 stale-base replay 13:04:19->12:56:12, owner rows intact, r648-family, "
    "MSG-1332 issued, self-heal expected) + THEME-JUDGE-P2 flip origin-verified DONE "
    "(r668 law) + S6 38/38 rc0 (3 CEO-face stale-takeover derives, bm-a hb stale 51min) "
    "+ compute_audit FLAG:supply_gap root-linked to trio standing ready-with-owner face; "
    "smoke 48/48; zero incident"
)

DID = (
    "r474 bm-c golden-week watch round (zero-incident, one pool-face regression "
    "adjudicated): (1) S0: no rebase leftovers; round-start dirty = 4 own lane faces; "
    "origin behind=1 (bm-a r678 theme-judge-p2 finalize wave) zero face intersection "
    "(r437 pre-check) -> absorb commit 86847bdfd (4 lane faces) + merge origin/main "
    "CLEAN zero-UU -> push_verify DELIVERED tip 44c642c46. (2) S0.5: orders 153/153 "
    "zero un-acked (S0.5 + S7 double-scan, same-caliber); inbox 0 inbound (1 outbound "
    "own MSG-1332); D-19 decisions 4E5BE321 + group-orders 68947C17 double MATCH "
    "-> zero consumption. (3) S1 smoke 48/48. (4) S2: boards empty (job_list 0; "
    "fleet open=0; 46 claimed = other machines' lanes). (5) S3: satengine rc0 alive "
    "via Tools copy (hb 49.4s, burns_active=[], queue_next=[] = N1 closed face per "
    "O-2115 sec-2); WM red=false healthy; next_pick=claimed moneyflow IC (advisory "
    "face); THEME-JUDGE-P2 finalize + entry+shard pool flip VERIFIED DONE on origin "
    "(r668 law compliance; judged_negative honest closure incl 0.75 deep-break E24-ii; "
    "attrition row 8004/641985) -> r473 watch face CLOSED; FUND trio V758/Q588/D436 "
    "zero-growth 12min window = between-push sampling per ETA face (24.49 rows/h, "
    "bm-b absorb cadence ~2h); POOL REGRESSION ADJUDICATED: trio owner_since "
    "13:04:19 -> 12:56:12 single-step backward = bm-a r678 pool needle surgery "
    "replayed stale local lane base over fresher origin (last pool-touching commit "
    "6f9a32757, parent 6e0170690 already contained 13:04:19; merge stat 7 lines = "
    "3 trio regressions + P2 flip; r648-family; pusher-side claw structural blind "
    "spot: origin freshening within fetch->push window invisible to own-base claw "
    "comparison); owner=bm-b rows intact -> r288 keepalive gate unaffected -> bm-b "
    "next tick self-heal expected; zero third-party surgery per r626d-2; "
    "MSG-2026-10-04-1332 issued: bm-a (per-face max-merge law scope extension = ALL "
    "pool-carrying pushes incl finalize/flip/needle/absorb, per MSG-0612/0640) + "
    "bm-b (FYI + heartbeat 36min-stale note at read time). (6) S6 38/38 rc0 "
    "NON-ZERO=none: dualrun ZERO-DRIFT streak 51 (368 entries); update_daily 0 new "
    "rows cutoff 2026-09-30 (golden week); market_regime ORANGE shadow "
    "days_in_state=2; compute_audit FLAG:supply_gap (ready=3/floor=3 breach=false, "
    "zero ignition SLA breach; root = trio standing status=ready-with-owner face "
    "while actively burning per ETA face -- audit cannot see owner-rows-as-burning; "
    "documented in MSG-1332); bm-a heartbeat stale 51min -> stale-takeover derive by "
    "bm-c for 3 CEO faces (paper_export / daily_scorecard / dashboard_status per "
    "O-2100 s2.4 STALE_MIN law); REPORT/LIVE-2026-10-04 idempotent regen "
    "state=ORANGE. (7) S7: loop pin5 phase-ok (next fire 13:35); watchdog "
    "registered (next fire 13:34); pre-commit + pre-push claws LF-normalized MATCH "
    "x2 zero reinstall; attrition CLEAN (4 ledgers, 2 bm-a healed historical notes "
    "recorded); orders S7 rescan 153/153 zero-diff; D-19 recheck double MATCH. "
    "(8) S4: one CODELY pitfall line (pool-carrying push per-face newer-wins scope "
    "extension + pusher-side claw blind spot; pointer MSG-1332); CODELY 69.8KB "
    ">50KB watermark recorded honestly (structural residual per r504 note; "
    "re-anchor/merge = GROUP/GM adjudication face; no unilateral archival)."
)

VERIFY = (
    "S6 38/38 rc0 NON-ZERO=none (results/_r474bmc_s6_log.txt, S6-chain-end marker + "
    "FAILS=[]); smoke 48/48; orders 153/153 zero-diff double-scan (same-caliber "
    "set-diff); D-19 decisions 4E5BE321 + group-orders 68947C17 double MATCH "
    "raw-blob caliber; attrition CLEAN (4 ledgers); claws LF-normalized MATCH x2; "
    "loop pin5 phase-ok; watchdog registered; satengine alive rc0 (Tools face hb "
    "49.4s); pool regression dual-round origin evidence (r473 healthy 13:04:19 vs "
    "r474 12:56:12; last pool-touching commit = bm-a 6f9a32757); THEME-JUDGE-P2 "
    "entry+shard flip origin-verified DONE; heartbeat epoch int + clock T-sep "
    "self-checked"
)

NEXT = (
    "(a) r475: 5x HANDOVER duty (research/HANDOVER.md refresh). (b) r475+r476 pool "
    "self-heal re-check: origin trio owner_since fresh (<15min age) = self-heal "
    "evidence; if stale 2+ rounds AND bm-b heartbeat dead -> stale-takeover "
    "escalation per MSG-1332 closure criteria. (c) fund-trio finalize window "
    "10-05 10:30 opens (bm-b owner; ETA V 10-06 15:00 / Q long-pole 10-07 11:00). "
    "(d) D-20261004-02(1)(2)(3) receipt window 10-06 00:00. (e) D-06 full closure "
    "window 10-07 (bm-c lead). (f) O-2115/O-2030 acceptance 10-08; market reopen "
    "10-09."
)

CODELY_LINE = (
    "- [2026-10-04 13:3x r474 bm-c] 池面携带 push per-face newer-wins 适用面扩展+pusher 侧 claw 结构盲区"
    "（r474 实弹定谳·零单方手术零 origin 伤害）：bm-a r678 finalize/pool_flip 针手术以本地 lane 镜像陈旧基座"
    "整面重放 runnable_pool.json→覆写 origin 更新的 FUND trio owner_since 13:04:19→12:56:12（commit "
    "parent 6e0170690 本含 13:04:19·merge stat 7 行=3 回退行+P2 翻面行）；pusher 侧 claw"
    "（pool_claim_regressions 对自家 fetch 基座比对）对 fetch→push 窗内 origin 新鲜化结构性不可见=盲区本体。"
    "律面=MSG-0612/0640 per-face max-merge（owner_since 类时间戳 newer-wins）/push 后 sync_face settle 正法"
    "不限于 S0 reland 环——一切携带池面整面重放的 push（finalize/flip/needle/absorb 均含）同律。"
    "How to apply：池面携带 push 前对 owner_since 类时间戳面 per-face max-merge vs 最新 fetch，或 push 后立即 "
    "merge_lane_views sync_face；收方面见单步回退先按 r648 双侧实取定谳分型（本地 behind 型 vs 陈旧重放型），"
    "owner 行完好=keepalive 自愈预期勿手补戳勿第三方手术（r626d-②）；定谳全文指针="
    "fleet/inbox/MSG-2026-10-04-1332-bmc-all.md。"
)

REPORT_LINE = (
    f"{clock}｜r474｜dept:工程（golden-week 值守轮·池面回退定谳·零事故）｜"
    "watermark verdict=绿（red=false healthy·satengine rc0 活〔Tools 注册面·heartbeat_age 49.4s·"
    "burns_active=[]·queue_next=[]=N1 关面 per O-2115 sec-2〕·py_watermark=py_low_board_clear 合法 idle）｜"
    "当前活=金周值守+池面 owner_since 回退定谳｜"
    "最近实物=results/_r474bmc_s6_log.txt（S6 38/38 rc0·chain-end+FAILS=[]）+results/_r474bmc_poolreg.txt"
    "（回退定谳双轮 origin 证据件）+fleet/inbox/MSG-2026-10-04-1332-bmc-all.md（协同通告）｜"
    "下个里程碑=r475 5x HANDOVER+fund-trio finalize 窗 10-05 10:30 开（bm-b 正主·ETA V 10-06 15:00/"
    "Q 长杆 10-07 11:00）+D-06 收口 10-07（bm-c 主导）+开市 10-09（≤48h）｜"
    "S0: 无 rebase 残留·轮首 4 脏面=本机车道面·origin behind=1（bm-a r678 finalize wave）零交集"
    "（r437 预对齐）→absorb 86847bdfd+merge 净零 UU→push_verify DELIVERED（tip 44c642c46）｜"
    "S0.5: 令差集=0（153/153 同口径·S7 二扫复确认）·inbox 0 入站（1 出站自 MSG-1332）·D-19 双 MATCH→零消费｜"
    "S1 smoke 48/48｜S2 板空（job 0·fleet open=0·46 claimed=他机车道）｜"
    "S3: satengine rc0 活·WM red=false healthy·next_pick=claimed moneyflow IC（advisory）·"
    "THEME-JUDGE-P2 finalize+池 entry+shard 双翻面 origin 实证 DONE（r668 律合规✓·judged_negative honest "
    "closure 8004/641985·r473 watch 面闭合）·FUND trio V758/Q588/D436（12min 零增长=轮间采样面 per ETA "
    "24.49 行/h·bm-b absorb 节奏 ~2h）·池面定谳：trio owner_since 13:04:19→12:56:12 单步回退=bm-a r678 "
    "池面针手术陈旧基座整面重放（parent 6e0170690 本含 13:04:19·merge stat 7 行=3 回退+P2 翻面）·r648 家族·"
    "pusher 侧 claw 对 fetch→push 窗内 origin 新鲜化结构性盲区·owner=bm-b 行完好→r288 门不受影响→bm-b 下 tick "
    "自愈预期·零第三方手术（r626d-②）→MSG-1332 通告 bm-a（per-face max-merge 正法适用面=一切池面携带 push）"
    "+bm-b（FYI+心跳 36min 陈提示）·W14 停泊维持 per O-0808｜"
    "S6 38/38 rc0（dualrun ZERO-DRIFT streak 51〔368 entries〕·update_daily 金周零新行 cutoff 2026-09-30·"
    "market_regime ORANGE shadow days=2·compute_audit FLAG:supply_gap〔ready=3/floor=3 breach=false·"
    "根因=trio status=ready-with-owner 站立面而实烧录中 per ETA face·审计不可见 owner 行=烧录·MSG-1332 已载〕·"
    "bm-a 心跳 stale 51min→lane_io stale-takeover derive 3 CEO 面〔paper_export/daily_scorecard/"
    "dashboard_status per O-2100 s2.4〕·REPORT/LIVE-2026-10-04 幂等再生 state=ORANGE·金周无新 bar 腿诚实 no-op）｜"
    "S7: loop pin5 phase-ok（next fire 13:35）·watchdog 在位（next fire 13:34）·双爪 LF 归一 MATCH x2 零重装·"
    "attrition CLEAN（4 ledgers·2 bm-a healed 注记照录）·orders S7 二扫 153/153 零差·D-19 复核双 MATCH｜"
    "S4: 1 坑律行（池面携带 push per-face newer-wins 适用面扩展+pusher 侧 claw 盲区·指针 MSG-1332）·"
    "CODELY 69.8KB>50KB 水位如实记录（结构残余 per r504 注记·重锚/合并=集团 GM 裁定面·零单方整编）｜"
    "记分: 1（S6 管线产出+回退定谳证据件+MSG 协同件+3 CEO 面 takeover derive+REPORT/LIVE 再生·"
    "等待态声明: finalize 窗 10-05 开·N1 关+trio bm-b 属主+板空=零新面孔可烧·非空转）｜"
    "记账预算: 5/5（state+心跳+轮报+S7 回执+CODELY 1 坑律行）｜"
    "本地未达 origin commit 数: 0（push_verify DELIVERIED）｜"
    "零清扫/归档/删除类动作轮：登记册零命中断言 N/A-无此类动作（O-2030 §二.3 自证面）"
)

ACTIVITY = (
    "golden-week watch; pool owner_since regression adjudicated (bm-a r678 "
    "stale-base replay 13:04:19->12:56:12, owner rows intact, bm-b self-heal "
    "expected, MSG-1332 issued); THEME-JUDGE-P2 flip origin-verified DONE; "
    "FUND trio V758/Q588/D436 (between-push sampling); 3 CEO-face stale-takeover "
    "derives (bm-a hb stale 51min); boards empty; N1 closed per O-2115 sec-2; "
    "zero-incident round"
)

VERDICT_HB = (
    "GREEN (smoke 48/48; orders 153/153 double-scan; D-19 double MATCH; satengine "
    "alive rc0 Tools face hb 49.4s; S6 38 legs rc0 fail=0 dualrun streak 51; "
    "compute_audit FLAG:supply_gap root-linked to trio standing ready-with-owner "
    "face (documented MSG-1332, burn active per ETA face); attrition CLEAN; claws "
    "MATCH x2; pool owner_since regression adjudicated r648-family (bm-a r678 "
    "stale-base replay, owner rows intact, self-heal expected); push_verify "
    "DELIVERED; zero cloud token)"
)

PROD_LANES = (
    "FUND trio NULLS bm-b in-flight (watch only, V38.1%/Q29.6%/D21.9% per ETA "
    "face); pool trio owner_since self-heal watch (r475/r476 closure criteria per "
    "MSG-1332); THEME-JUDGE-P2 closed DONE; N1 closed per O-2115 sec-2; boards "
    "empty; zero-incident watch round"
)

LATEST_ARTIFACT = (
    "results/_r474bmc_s6_log.txt (S6 38/38 rc0) + results/_r474bmc_poolreg.txt "
    "(pool regression dual-round origin evidence) + "
    "fleet/inbox/MSG-2026-10-04-1332-bmc-all.md "
    f"@ {clock}"
)

NEXT_MILESTONE = (
    "r475 5x HANDOVER; fund-trio finalize window 10-05 10:30 (bm-b owner; ETA "
    "face V 10-06 15:00 / Q long-pole 10-07 11:00); pool self-heal re-check "
    "r475/r476; D-20261004-02 receipt window 10-06 00:00; D-06 closure 10-07 "
    "(bm-c lead); O-2115/O-2030 acceptance 10-08; market reopen 10-09"
)


def append_line(path, line):
    with open(path, "rb") as fh:
        data = fh.read()
    eol = b"\r\n" if b"\r\n" in data[-200:] else b"\n"
    prefix = b"" if data.endswith(b"\n") or data.endswith(b"\r\n") else eol
    with open(path, "ab") as fh:
        fh.write(prefix + line.encode("utf-8") + eol)
    return len(line.encode("utf-8"))


def main():
    # 1) state update
    with open(STATE, encoding="utf-8-sig") as fh:
        st = json.load(fh)
    st["clock_read"] = clock_state
    st["current_task"] = CURRENT_TASK
    st["did"] = DID
    st["heartbeat_epoch_utc"] = epoch
    st["last_round"] = LAST_ROUND
    st["last_round_at"] = clock_state
    st["last_round_ts"] = ts_space
    st["last_seen"] = clock_state
    st["last_ts"] = ts_space
    st["next"] = NEXT
    st["round_no"] = 474
    st["updated"] = clock_state
    st["updated_at"] = clock_state
    st["verify"] = VERIFY
    with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
    back = json.load(open(STATE, encoding="utf-8-sig"))
    assert isinstance(back["heartbeat_epoch_utc"], int), "epoch not int"
    assert "T" in back["clock_read"], "clock no T-sep"
    assert back["round_no"] == 474

    # 2) heartbeat update
    with open(HB, encoding="utf-8-sig") as fh:
        hb = json.load(fh)
    hb["activity_now"] = ACTIVITY
    hb["clock_read"] = clock
    hb["current_task"] = CURRENT_TASK
    hb["heartbeat_epoch_utc"] = epoch
    hb["last_seen"] = clock
    hb["last_seen_at"] = clock
    hb["latest_artifact"] = LATEST_ARTIFACT
    hb["next_milestone"] = NEXT_MILESTONE
    hb["prod_lanes"] = PROD_LANES
    hb["round_no"] = 474
    hb["round_no_label"] = "round 474 (bm-c)"
    hb["ts"] = clock
    hb["updated"] = clock
    hb["updated_at"] = clock
    hb["verdict"] = VERDICT_HB
    with open(HB, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)
    back2 = json.load(open(HB, encoding="utf-8-sig"))
    assert isinstance(back2["heartbeat_epoch_utc"], int), "hb epoch not int"
    assert "T" in back2["clock_read"], "hb clock no T-sep"
    assert back2["round_no"] == 474

    # 3) CODELY one pitfall line
    n1 = append_line(CODELY, CODELY_LINE)
    with open(CODELY, "rb") as fh:
        cdata = fh.read()
    assert cdata.count(CODELY_LINE.encode("utf-8")) == 1, "codely line count != 1"

    # 4) round report main line
    n2 = append_line(REPORT, REPORT_LINE)

    print("STATE_OK round", back["round_no"], "epoch", back["heartbeat_epoch_utc"])
    print("HB_OK round", back2["round_no"], "clock", back2["clock_read"])
    print("CODELY_APPENDED", n1, "bytes; file now", len(cdata))
    print("REPORT_APPENDED", n2, "bytes")


if __name__ == "__main__":
    main()
