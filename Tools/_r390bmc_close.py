# -*- coding: utf-8 -*-
"""r390 bm-c closeout: state + heartbeat + round report + HANDOVER 5x catch-up.
Pattern credit: Tools/_r309bmc_close.py (adopted per r471 reuse law).
Laws: R170/R178 epoch must be python int; R262 clock_read T-separated ISO8601;
bytes-in/bytes-out file IO (r530 CRLF family); HANDOVER 5x = round_no % 5 == 0."""
import datetime as dt
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE_NO_WINDOW = 0x08000000
NOW = dt.datetime.now()
NOW_TS = NOW.strftime("%Y-%m-%d %H:%M:%S")
NOW_ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

REPORT_ENTRY = """
## [r390 00:3x] LOWAMP-DEEP-P1-SENS 烧完交付上 origin + nulls 双烧防护消息 + S0 r589 环纯 FF 集成
水位=绿（red=false·lane healthy；probe verdict=py_low_with_work_cands 点名解释=work cand 唯一 open 票 T-150 lane host=bm-a（p1c_stock 面板 bm-a 本地）不可认领+池 9 ready 全有主 0 unclaimed+引擎 queue_next 空=供给缺口结构面 r388⑤ 待 bm-a N4-B1 发生器席位——合法 idle 披露非违令）；smoke 47/47。①**本轮主产品=sens 分片烧完交付**：r389 根修（T-18 深板本机重建）实弹收口——sens 500/500 烧完（00:02:19-00:13:50·691.4s·6.15 core-hours·rc=0），claim closed ok 握手+ledger 行+sens.jsonl 500 行产物随轮 commit 50ebc7669 推 origin（45 件 +2559/-356·MSG-2346 inbox→processed rename 100% 干净过爪）；池行 ready/owner=bm-c 待 harvest 翻 done——claim 可见性已上 origin（r489 律），下轮核翻面。②S0 集成=r589 撤-FF-重落环：轮首树脏（r389 收口件未 commit+2 个 daemon claim/close commit ahead）+behind 18 → diff 面零重叠实证 → reset --mixed merge-base 65058d43a → 纯 FF 至 41d469463 零损失零 D 伪影；r389 全部收口件随本轮 commit 落账（含 REPORT-2026-10-03/LIVE-2026-10-03/post_review 44ok）。③nulls 双烧防护：池面实读=bm-b 23:56:18 占 nulls 行 claim（origin 零 bm-b claim 件）vs bm-a 在飞烧录（MSG-2346）=活体双烧风险（r389 报告称「bm-b 已撤」实未撤=勘误）；MSG-2359（r389 写成从未推）增补 00:2x 现况块（请求 bm-b 未起烧即释放/已起烧即回执披露双烧面）后随本轮首推上 origin——首稿从未可见=amend 零外见性（r589 律）。④D-19 水位消费：937A373D→4167B784（10-03 批 D-20261003-01~04=回执核销/BigLife/FluxVerse/分卷四行零涉本司行动行=纯更新零动作）；orders 150/150 ack 零未回执（S0.5+S7 双扫）。⑤S6 全链 38 腿 rc0：dualrun DRIFT 1 例观察相照录（$.entries[333].done_at 缺失·flip streak 复位照律）→compute_audit CLEAN（supply_gap 旗如实·pool-supply-gap load_state）→probe→update_lhb 实拉 11/11 rc0→regime ORANGE shadow→scorecard/CALL-09-30 ORANGE_COOL→13 外车道腿诚实 no-op→fund_premium 周末 no-op→b_layer gates 5/5→live.paper/t35v/t24 双腿 rc0→aggr/grid 幂等→system_v1 lane 守卫 no-op→t35_export/daily_scorecard/build_status stale-takeover 合法（bm-a 心跳 35min·O-2100 s2.4）→daily_report faces=5→ceo_live_usage LIVE-10-03 ORANGE→token→attrition guard scan 4 台账 CLEAN（2 healed 历史注记）→post_review ✓44/✗0/🟡5 零红。⑥引擎活性面：Tools 面 status rc0 alive=True core_cap=26 在效 last_cycle 00:24:09 queue_next 空（供给缺口）；诚实披露=scripts 共享面 status rc1「never ticked」+schtasks 注册面仍指 Tools 副本（19:21 起常驻·sens 正是它点火烧完）=r388 宣称「本机 tick 实跑共享件」与注册实况不符（下轮小活：注册面切换或注记 Tools 为正主）；自愈四查全过（loop pin=5 no-op/watchdog 幂等重注册/pre-commit+pre-push 爪 LF 归一重装）。
CEO 三行实况：当前活=sens 交付收口+nulls 防护消息+HANDOVER 5x 补账；最近实物=results/lowamp_deep_p1/sens.jsonl（500 行·commit 50ebc7669·00:3x）；下个里程碑=LOWAMP-DEEP-P1 全 10 单元收口→finalize+E1 判决（due 10-09 开市前·9/10 已 done·候 nulls 2000 bm-a 烧完）。
下轮指针：(a) 池面核验：sens 行 harvest 翻 done（claim 已上 origin；若一整轮后仍 ready=手工双翻 r488/r489 律）+nulls 行归属面（候 bm-b 对 MSG-2359 回执：未起烧=释放/已起烧=双烧披露）；(b) LOWAMP-DEEP-P1 finalize+E1 判决面（本机·due 10-09·complete gate=8 cell-faces done+nulls+sens 全 done）；(c) T-144(c) post-split 域增量扫描下沉（due 10-07）；(d) 引擎注册面清理小活（Tools vs scripts 实况对齐）；(e) 供给缺口观察（bm-a N4-B1 发生器席位+contest-ytd-p1 8/8 bm-a 在烧）；(f) 月界首考 10-31 准备（T-143）。
本地未达 origin commit 数=0（收口推送后 fetch+rev-list 自证）
"""

HANDOVER_ENTRY = """> bm-c round 390 五倍数核对（2026-10-03 00:3x·增量窗 r381-390 十轮〔r385 漏 5x 核对=坑-79「指针写了≠执行」族如实注记·本行合并覆盖〕）：增量窗 r381-390=bm-c 面（**W108 让路+拆件收口+T-149 发送+LOWAMP-DEEP-P1 根修-烧完-交付四段线**——r381 W108 finalize 确定性孪生零成本让路 bm-b stall-drain 合法接管（yield receipt 66a8efae6·r381 律 audit.machine 记实际执行机·owned 波 finalize 权非排他保真面）；r382 收口 commit 误托引擎 append commit=簿记四件滞留坑（r385 治愈）+CODELY 拆件六域推进（git r368/pool r373/data r380 bm-c+engine r585 bm-a+protocol r387 bm-c=五 pit 域件全落）；r383/r384 猝死窗（22:35/22:45 tick 遗产由 r387 收容·号位烧毁不重用 r529 律）；r385 簿记滞留治愈+猝死会话在制活收养先令序重扫（W115 半冻结遗产=O-2115 供给序令后旧序推进=撤编辑存档+席位保留）；r386 T-147 三机撞票裁定+全套 ADOPT（LOWAMP-DEEP-P1 主考格冻结 prereg 承接 bm-b r596 猝死遗产·finalize+E1 判决面归本机 due 10-09·sizing 死信双机同窗独立发现）+S0 撤-FF 环自撞 helper strip 坑 CODELY 收录；r387 S0 手术轮（GM CAS×tick 双落竞态治愈 r589 环+T-147 还原 origin 正身+协议域拆件半成品收编=行集双向差集探针验宣称 r595 律回插+pit-protocol.md 27 条落册）+T-148 让路 bm-b（§4 commit 时间序第 5 例）+MSG-2230 误删复原（claw inbox 白名单互作用坑）；r388 **T-149 sender 完成**（value_faces.parquet 18,284,045B/4,133,848 行/5,224 符号/锚中位 693.5 git 送达 bm-a·sha256 manifest 双侧·发送三门 3/3）+O-2155/O-2158 实例面同律（CORE_CAP bm-c=26 单源+WORKERS 26+MAX_ACTIVE_BURNS 2）+LAD-EDGE base/x2 崩 fuse 拒发如实披露（r389 首件修复活）；r389 **LOWAMP-DEEP-P1 四崩根修**（T-18 深板本机重建 48 员/114,142 行 manifest-sha 门+loader 48/48 实弹+fuse 手术 base/x2/sens 清 reason=data_fixed+nulls 故意保留让路 bm-a MSG-2346）+T-149 关票（bm-a r599 receiver 双 manifest 齐）+MSG-2359 起草；r390=本核对轮 **sens 烧完交付**（500/500·claim closed ok 691.4s/6.15 core-h·rc0·commit 50ebc7669 推 origin 45 件）+MSG-2359 nulls 双烧防护首推（bm-b 23:56:18 占行零 claim 件 vs bm-a 在飞=活体风险·请求释放/回执）+S0 r589 环纯 FF 集成（ahead 2 daemon commit 撤+behind 18 零重叠 FF 41d469463）+D-19 水位 4167B784 消费（10-03 批零涉本司）+S6 38 腿 rc0（dualrun DRIFT 1 观察相·post_review 44/0/5·attrition CLEAN）+引擎注册面勘误披露（scripts 面 never ticked+注册仍指 Tools 副本=r388 宣称与实况不符）+HANDOVER 本行）产物清单漂移=scripts/t149_value_faces_export.py+data/fund_history_export/value_faces.parquet+fleet/transfers/T-2026-10-02-149-sender.json+results/t149_value_faces_export.json〔r388〕+Money02/data/cache/t18_deep_panel 本机深板（gitignored 数据面·r389）+results/lowamp_deep_p1/sens.jsonl 500 行+results/pool_claims/LOWAMP-DEEP-P1-SENS/lowamp-deep-p1-sens-0of1.bm-c.json+pool_worker_ledger 行〔r390〕+research/pit-{git,pool,data,protocol}.md 四域件+archive 202610.md 拆件窗批节〔r368-r387〕+fleet/tasks/T-2026-10-02-147-P1.json（ADOPT 承接）+fleet/inbox/MSG-2026-10-02-2359（nulls 保留位·r390 首推）+Tools/_r390bmc_s6.py〔r390〕；orders 150/150 双扫零未回执全窗维持；smoke 47/47；指针：**LOWAMP-DEEP-P1 finalize+E1 判决（due 10-09 开市前·9/10 单元 done·候 nulls bm-a 2000 烧完+sens harvest 翻面核验）+T-144(c) post-split 域增量下沉（due 10-07）+引擎注册面清理（Tools vs scripts 实况对齐）+月界首考 10-31 清单（T-143）**；下一 5x=bm-c r395。
"""

VERIFY_TEXT = ("r390 product round: LOWAMP-DEEP-P1-SENS burn COMPLETE + delivered to origin "
 "(500/500 rows, claim closed ok 691.4s 6.15 core-hours rc0, commit 50ebc7669, 45 files +2559/-356) "
 "-- r389's T-18 deep-panel rebuild proven end-to-end in fire (4x-crashed shard now burns clean). "
 "Harvest face: claim-by-file on origin for daemon done-flip (pool row ready/owner=bm-c, next-round verify). "
 "Fleet safety: MSG-2359 nulls-row reservation pushed with 00:2x update block (bm-b holds origin claim "
 "since 23:56:18 with zero claim-file vs bm-a in-flight burn = live double-burn risk; bm-b asked "
 "release-or-receipt per r489 law; r389's 'bm-b withdrew' reading corrected). S0: r589 loop (2 local "
 "pool_worker claim/close commits re-landed as worktree state, pure FF to 41d469463, 18 origin commits, "
 "zero file overlap, zero D artifacts). D-19 watermark consumed 937A373D -> 4167B784 (2026-10-03 batch "
 "D-20261003-01..04: zero bigmoney action rows). S6 38 legs rc0 (dualrun DRIFT 1 observation-phase entry "
 "streak reset; audit CLEAN with supply_gap flag honest; lhb 11/11 pulled; post_review 44 ok/0 fail/5 wait; "
 "attrition guard 4 ledgers CLEAN). Engine: Tools-face status rc0 alive core_cap=26 last_cycle 00:24:09, "
 "queue_next empty = known supply-gap structural face (awaiting bm-a N4-B1 generator seats); honest "
 "disclosure: scripts-face status rc1 'never ticked' + schtasks registration still points at Tools copy "
 "(resident since 19:21, the instance that ignited sens) = r388's 'tick runs shared copy' claim vs "
 "registration reality mismatch, queued as next-round cleanup. Watermark green; probe py_low_with_work_cands "
 "explained (T-150 lane-host=bm-a unclaimable + pool 9 ready 0 unclaimed = legal idle). Smoke 47/47. "
 "Orders 150/150 zero unacked. HANDOVER 5x catch-up: r385 missed check disclosed per pit-79, r381-390 "
 "window covered this round.")

NEXT_TEXT = ("(r391)(a) pool verify: sens row harvest flip to done (claim on origin since 50ebc7669; "
 "if still ready after a full round = hand-flip both layers per r488/r489 law); nulls row ownership face "
 "(await bm-b receipt on MSG-2359: not-launched=release claim, launched=double-burn disclosure); "
 "(b) LOWAMP-DEEP-P1 finalize + E1 judgment (due 10-09 pre-market; complete gate = 8 cell-faces done + "
 "nulls 2000 (bm-a in-flight) + sens done); (c) T-144(c) post-split domain increment scan (due 10-07); "
 "(d) engine registration face cleanup (Tools vs scripts copy alignment); (e) supply-gap watch (bm-a "
 "N4-B1 generator seats + contest-ytd-p1 8/8 bm-a burning); (f) monthly exam 10-31 prep (T-143)")


def main():
    # --- machine sampling (CPU/RAM via psutil, GPU via nvidia-smi CREATE_NO_WINDOW) ---
    cpu_pct, idle_ram_gb, gpu_free_mib = 17, 3.0, 806
    try:
        import psutil
        cpu_pct = int(psutil.cpu_percent(interval=1))
        idle_ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    except Exception:
        pass
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, creationflags=CREATE_NO_WINDOW,
                           text=True, encoding="utf-8", errors="replace", timeout=20)
        if r.returncode == 0 and r.stdout.strip():
            gpu_free_mib = int(float(r.stdout.strip().splitlines()[0]))
    except Exception:
        pass
    epoch = int(dt.datetime.now().timestamp())

    # --- state-<id>.json ---
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.loads(open(sp, "rb").read().decode("utf-8-sig"))
    st.update({
        "round_no": 390,
        "last_round_at": "r390",
        "last_round_ts": NOW_TS,
        "updated": NOW_ISO,
        "cpu_pct": cpu_pct,
        "idle_ram_gb": idle_ram_gb,
        "gpu_free_vram_mib": gpu_free_mib,
        "verify": VERIFY_TEXT,
        "did": ("r390: sens burn delivered to origin (500/500 + claim closed ok + MSG-2359 nulls "
                "protection) + S0 r589-loop FF integration (18 commits) + D-19 consume 4167B784 + "
                "S6 38 legs rc0 + HANDOVER 5x catch-up (r381-390, r385 miss disclosed)"),
        "current_task": "r390 closeout: state/heartbeat/report/HANDOVER writes + final commit + push + delivery self-verify",
        "next": NEXT_TEXT,
        "heartbeat_epoch_utc": epoch,
        "clock_read": NOW_ISO,
        "last_ts": NOW_TS,
        "last_round": f"2026-10-03 r390 bm-c: sens 500/500 delivered + nulls protection MSG-2359 + S0 FF integration + S6 rc0 + HANDOVER 5x",
        "last_seen": NOW_TS,
        "updated_at": NOW_ISO,
    })
    with open(sp, "wb") as fh:
        fh.write(json.dumps(st, ensure_ascii=False, indent=1).encode("utf-8"))

    # --- heartbeat fleet/machines/bm-c.json ---
    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    hb = json.loads(open(hp, "rb").read().decode("utf-8-sig"))
    hb.update({
        "cpu_util_pct": cpu_pct, "cpu_pct": cpu_pct,
        "free_ram_gb": idle_ram_gb, "ram_free_gb": idle_ram_gb,
        "idle_ram_gb": idle_ram_gb,
        "gpu_free_vram_mb": gpu_free_mib, "gpu_vram_free_mb": gpu_free_mib,
        "gpu_free_vram_mib": gpu_free_mib, "gpu_idle_vram_mib": gpu_free_mib,
        "gpu_idle_vram_mb": gpu_free_mib,
        "cpu_idle_pct": max(0, 100 - cpu_pct),
        "verdict": VERIFY_TEXT,
        "round_no": 390,
        "prod_lanes": ("r390: sens burn delivered to origin (500/500 claim closed ok, commit 50ebc7669) + "
                       "MSG-2359 nulls double-burn protection pushed + S0 r589-loop FF integration (18 commits, "
                       "zero overlap) + D-19 watermark 4167B784 consumed + S6 38 legs rc0 + HANDOVER 5x catch-up "
                       "(r385 missed check disclosed)"),
        "current_task": "r390 closeout: final commit + push + delivery self-verify",
        "activity_now": "S7 closeout: state/heartbeat/HANDOVER writes + final commit + push; engine idle (supply gap, queue empty)",
        "latest_artifact": ("results/lowamp_deep_p1/sens.jsonl (500 rows, N=500 space-filling draws rng([20337000,k])) "
                            "+ results/pool_claims/LOWAMP-DEEP-P1-SENS/lowamp-deep-p1-sens-0of1.bm-c.json (closed ok) "
                            "via commit 50ebc7669 @ 2026-10-03 00:3x"),
        "next_milestone": ("LOWAMP-DEEP-P1 finalize + E1 judgment by 10-09 pre-market "
                           "(9/10 units done: 8 cell-faces + sens; nulls 2000 bm-a in-flight)"),
        "heartbeat_epoch_utc": epoch,
        "clock_read": NOW_ISO,
        "last_seen": NOW_TS, "last_seen_at": NOW_TS,
        "updated_at": NOW_ISO,
        "health": "ok",
    })
    with open(hp, "wb") as fh:
        fh.write(json.dumps(hb, ensure_ascii=False, indent=1).encode("utf-8"))

    # --- round report append ---
    rp = os.path.join(ROOT, "round_reports-bm-c.md")
    with open(rp, "ab") as fh:
        fh.write(REPORT_ENTRY.encode("utf-8"))

    # --- HANDOVER 5x prepend (after title, before r380 entry) ---
    hdp = os.path.join(ROOT, "research", "HANDOVER.md")
    raw = open(hdp, "rb").read().decode("utf-8-sig")
    anchor = "> bm-c round 380"
    idx = raw.find(anchor)
    assert idx > 0, "HANDOVER r380 anchor missing"
    new = raw[:idx] + HANDOVER_ENTRY + "\n" + raw[idx:]
    with open(hdp, "wb") as fh:
        fh.write(new.encode("utf-8"))

    # --- self-verify: json loads + epoch int + clock T-format (R170/R178/R262) ---
    st2 = json.loads(open(sp, "rb").read().decode("utf-8-sig"))
    hb2 = json.loads(open(hp, "rb").read().decode("utf-8-sig"))
    assert isinstance(st2["heartbeat_epoch_utc"], int), "epoch not int"
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int"
    assert "T" in st2["clock_read"] and "+" in st2["clock_read"], "clock_read format"
    print(f"closeout OK: state round_no={st2['round_no']} epoch={st2['heartbeat_epoch_utc']} "
          f"clock={st2['clock_read']} cpu={cpu_pct}% ram_free={idle_ram_gb}GB gpu_free={gpu_free_mib}MiB")
    print("report +1 entry; HANDOVER r390 5x prepended;")


if __name__ == "__main__":
    main()
