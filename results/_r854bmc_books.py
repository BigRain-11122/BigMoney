# -*- coding: utf-8 -*-
# r854 bm-c books: state + heartbeat bump + round report line (r853 bloodline verbatim-clone)
import json, time, io

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now_iso = "2026-10-11T05:58:00+08:00"
epoch = int(time.time())

did = ("r854 bm-c: (1) S0-1 identity anchor bm-c + round-zero probe py_faces=14 orphans=1 read-only "
       "(idle ComfyUI 8188 face same as r850-r853, no-kill); S0 own 7 runtime faces absorb-commit 53f54a827 "
       "+ rebase ff onto origin (0 ahead/4 behind, bm-b r863 N2-W19 slice-2 closeout absorbed clean); "
       "(2) S0.5 ORD delta f90233c7->24ad1708 = 1 new row (line 392 @bm-a MiniGame X2348 screenshot-sweep "
       "receipt, NOT this company -> watermark update zero-action per D-19 law); DEC 68d13893 MATCH zero-delta; "
       "local fleet orders 67/67 acked unacked=0; inbox empty; (3) S1 smoke 49/49; S2 boards empty "
       "(job 0 / open tickets 0, 49 all claimed); satengine alive rc0 (queue_next empty, burns 0 = W208 "
       "upstream-blocked known face); (4) WATCH FACE: W208 still NOT landed (origin zero new commits since "
       "bm-b r863), stall-notice MSG-20261011-0535 no answer yet (bm-a dark ~8h); MSG-0455 pool-EOL "
       "adjudication CLOSED via bm-b r863 (pf selftest 9/9 green on bm-b LF tree, request fulfilled = "
       "cross-machine EOL red root closure complete, both-face proof chain closed); (5) PRODUCT = S6 43-leg "
       "chain 43/43 rc0 (_r854bmc_s6_chain.ps1 r853 verbatim clone, DONE 05:53:02, dualrun ZERO-DRIFT streak "
       "29->30) + QA charter pack 5/5 (qa/smoke-r854-bm-c.md + equity-curve-r854-bm-c.png: 3sym x 800bar "
       "91 trades determinism=True sharpe 0.1994 win_rate 0.4725 maxdd -0.0431 equity final 1,023,027; "
       "signal CALL rc0 cell=ORA; panel bar 2026-10-09); compute_audit flags = 3 known-adjudicated faces "
       "(gpu_unauthorized=jman CEO-MV-order burn GPU 100%, pool_starvation/supply_floor=seat chain blocked "
       "upstream W208); py_watermark verdict insufficient_history (Sunday no-new-bar legal state per r843); "
       "(6) jman 21288 alive CPU 37.9h total, step 2079/3072 (68%) @ 11.52s/it, continuation checkpoint "
       "cont-000008 @05:43 (cadence ~1.6h holding), ETA ~08:37-09:00 (improved vs 09:45 estimate); W209 M10 "
       "cron 9defca39 armed (17min cadence, durable verified); W211 freeze-prep not due (W210 blocked behind "
       "W208/W209); (7) S7: attrition 4 ledgers CLEAN (2 healed historical shrinks disclosed); quartet green "
       "(loop pin=5 no-op first-fire 05:55, watchdog re-registered first-fire 05:54, pre-commit + pre-push "
       "claws installed CR-normalized); idle --worked (idle_rounds=0, NOT green-idle: VRAM 106MiB jman "
       "in-flight); ORD watermark 24ad1708a40e6cf8 written this books")

next_ptr = ("r855: (1) W208 landing watch -> M10 auto-execute chain (freeze -> selftest default-wave -> "
            "pathspec push -> 2-cycle n1_w209 ignition -> MSG receipt + flip M10 + delete cron 9defca39); "
            "stall escalation live: MSG-20261011-0535 answer watch (bm-a freeze-prep push OR yield MSG -> "
            "adoption per r578 six-step on yield receipt; GM re-dispatch order = execute same-round); "
            "(2) jman completion window ~08:37-09:00 (val_grid + LOOKBOARD_variant_640 + recovery-debt trio "
            "per O-20261010-0025, <=48h SLA); (3) W211 freeze-prep when W210 approaches (read "
            "pit-engine-finalize.md FIRST); (4) S0.5 standing composer; (5) 10-16 governance criteria on file")

activity = ("当前活: 守望窗（W208 未落链·停滞通报 MSG-0535 待 bm-a 响应/yield/GM 改派·M10 cron 9defca39 armed "
            "17min 节奏·jman trainer 21288 在烧 step 2079/3072 68% ETA ~08:37-09:00）| "
            "最近实物: S6 43 腿 rc0 streak 30 + QA 证据包 r854 5/5（qa/smoke-r854-bm-c.md + "
            "equity-curve-r854-bm-c.png）+ MSG-0455 跨机 EOL 裁定闭环回执 @ 2026-10-11T05:58 | "
            "下个里程碑: W209 freeze（W208 落链/yield/改派即执行）+ jman 完训验证三件 ~08:37-09:00（≤48h SLA）")

verdict = ("r854 close: W208 watch holds (no answer to MSG-0535 yet, no substitution per cross-machine law) "
           "+ MSG-0455 EOL adjudication closed via bm-b r863 + S6 43/43 rc0 (streak 30) + QA pack 5/5 + "
           "smoke 49/49 + jman 68% ETA ~08:37")

summary = ("r854 close: watch round (W208 no-answer holds, MSG-0455 closed via bm-b r863) + S6 43/43 "
           "streak 30 + QA 5/5 + jman ETA ~08:37")

report_line = ("2026-10-11T05:58:00+08:00 | r854 | dept:工程/舰队（守望窗+W208 应答观察轮·S6 43 腿 streak 30·QA 5/5·MSG-0455 闭环） | "
               "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
               "WM-VERDICT: 绿（red=false·probe=insufficient_history 周日无新 bar 合法态·satengine 活 queue 空=W208 上游阻塞已知面·RAM 2.1G 闸·jman CEO-MV 在烧 GPU 100%） | "
               "孤儿面=1（py_faces=14·ComfyUI 8188 idle server 同 r850-r853·read-only no-kill） | "
               "r854: ①S0 本机 7 runtime faces absorb commit 53f54a827+rebase ff（入站 4=bm-b r863 N2-W19 slice-2 closeout·0 冲突）；"
               "②S0.5 ORD delta f90233c7→24ad1708=1 新行（392 行 @bm-a MiniGame 走查回执·不涉本司→水位更新零动作）·DEC 68d13893 恒等·本地 67/67 ack 零未回执·收件箱空；"
               "③S1 smoke 49/49·S2 双板空（49 票全 claimed·open 0）·satengine 活 rc0（queue_next 空 burns 0=W208 已知面）；"
               "④守望面=W208 未落链（origin 零新 commit）·MSG-20261011-0535 无应答（bm-a 暗 ~8h 继续观察）·"
               "**MSG-0455 pool-EOL 跨机裁定闭环**（bm-b r863 复跑 pf selftest 9/9 green on LF tree=请求达成·EOL 红根跨机闭合·双面机证链收口）；"
               "⑤PRODUCT=S6 43/43 rc0（_r854bmc_s6_chain.ps1 r853 verbatim clone·DONE 05:53:02·dualrun streak 29→30）"
               "+QA 包 5/5（3sym×800bar 91 笔确定性回测 sharpe 0.1994+equity PNG+信号 CALL rc0+面板 bar 2026-10-09）"
               "·三审计旗=已知定谳面照录（gpu_unauthorized=jman CEO-MV·pool_starvation/supply_floor=W208 链堵）；"
               "⑥jman 21288 活 CPU 37.9h·step 2079/3072（68%）@11.52s/it·cont-000008 checkpoint 05:43（~1.6h 节奏在档）·"
               "**ETA ~08:37-09:00（较 09:45 估算改善）**·W209 M10 cron 9defca39 armed 验证·W211 freeze-prep 未到期；"
               "⑦S7 attrition 4 CLEAN（2 healed 披露）+四件套绿（loop pin=5 no-op 05:55·watchdog 幂等重装 05:54·双爪 installed CR 归一）+idle --worked | "
               "r855: (1) W208 落链守望→M10 自动执行链·MSG-0535 应答观察（freeze-prep OR yield→r578 收养 OR GM 改派随令即执行）；"
               "(2) jman 完训窗口 ~08:37-09:00 三件（val_grid+LOOKBOARD_variant_640+恢复债三件·≤48h SLA）；(3) W211 freeze-prep（W210 近时先读 pit-engine-finalize.md）；"
               "(4) S0.5 常设 composer | 本轮产品积分：2（S6 43 面再生+QA 证据包 5/5=经营层实物） | 记账预算：3 面内（state+心跳+轮报=法定簿记）")

def upd(path, is_hb):
    with io.open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    ts_fields = ["ts","last_seen","last_seen_at","clock_read","updated","updated_at","last_run_at","last_round_at",
                 "last_round_ts","last_ts","last_round_closed","current_task_at","last_round_summary_at",
                 "last_orders_read_at","last_pulled_at","last_action_at","last_round_at_legacy"]
    for k in ts_fields:
        if k in d: d[k] = now_iso
    d["round_no"] = 855
    d["round_no_label"] = "r854"
    d["last_round"] = 854
    d["loop_round"] = 854
    d["heartbeat_epoch_utc"] = epoch
    d["cpu_pct"] = 51; d["cpu_util_pct"] = 51; d["cpu_idle_pct"] = 49
    d["free_ram_gb"] = 2.1; d["idle_ram_gb"] = 2.1; d["ram_free_gb"] = 2.1
    for k in ["gpu_free_vram_mb","gpu_free_vram_mib","gpu_idle_vram_mb","gpu_idle_vram_mib","gpu_vram_free_mb","gpu_free_mb","gpu_free_mib","gpu_idle_mib"]:
        if k in d: d[k] = 106
    d["gpu_idle_mb"] = 16278
    d["current_task"] = activity
    d["activity_now"] = activity
    d["did"] = did
    d["verdict"] = verdict
    d["last_round_summary"] = summary
    d["note"] = ("r854 = watch round: W208 no-answer holds (MSG-0535 live), MSG-0455 EOL adjudication CLOSED "
                 "via bm-b r863 (selftest 9/9 green LF tree); S6 43/43 streak 30; QA 5/5; jman 68% "
                 "step 2079/3072 ETA ~08:37-09:00.")
    d["next"] = next_ptr
    d["next_pointer"] = next_ptr
    d["next_milestone"] = ("r855: W209 freeze on W208 landing/yield/GM-redispatch (M10 auto-execute, cron armed) "
                           "+ jman completion window ~08:37-09:00 (val_grid + LOOKBOARD_variant_640 + "
                           "recovery-debt trio) <=48h SLA")
    d["latest_artifact"] = ("S6 43-leg chain rc0 streak 30 + QA pack r854 5/5 (qa/smoke-r854-bm-c.md + "
                            "equity-curve-r854-bm-c.png) + MSG-0455 cross-machine EOL closure receipt")
    d["last_artifact"] = d["latest_artifact"]
    d["recent_artifact"] = d["latest_artifact"]
    d["last_action"] = "r854 W208 answer-watch + MSG-0455 closure receipt + S6 43-leg chain (streak 30) + QA pack + books"
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 1
    d["orphan_faces"] = 1
    d["health"] = "ok"
    # ORD watermark: consumed delta f90233c7 -> 24ad1708 (1 new row not-this-company, zero-action)
    d["last_orders_sha"] = "24ad1708a40e6cf8197742bc8812b015ff185f1b715bb5f097006c4501f9d5f2"
    d["last_orders_sha_note"] = ("r854 consumed: 1 new row (line 392 @bm-a MiniGame X2348 screenshot-sweep receipt, "
                                 "not BigMoney -> zero-action); prior f90233c7 held since r851")
    d["verify"] = ("receipts: smoke 49/49 + qa/smoke-r854-bm-c.md (5/5 charter) + results/_r854bmc_s6_log.txt "
                   "(43/43 rc0 streak 30, DONE 05:53:02) + attrition CLEAN (4 ledgers) + quartet green + "
                   "idle --worked + this books commit/push_verify")
    if not is_hb:
        d["sync"] = {"ahead_behind": "0/0 pre-books", "origin_tip": "36f2df813", "ts": now_iso,
                     "note": "r854 books: watch round + S6/QA products; books commit follows this write"}
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return d

upd(ROOT + r"\state-bm-c.json", False)

# heartbeat (fleet/machines/bm-c.json): CRLF face, indent=1, no trailing NL (r852 close convention)
hbd = upd(ROOT + r"\fleet\machines\bm-c.json", True)
raw = io.open(ROOT + r"\fleet\machines\bm-c.json", "r", encoding="utf-8").read()
io.open(ROOT + r"\fleet\machines\bm-c.json", "w", encoding="utf-8", newline="").write(raw.replace("\n", "\r\n"))

for p in [ROOT + r"\state-bm-c.json", ROOT + r"\fleet\machines\bm-c.json"]:
    with io.open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert isinstance(d["heartbeat_epoch_utc"], int), p
    assert "T" in d["clock_read"], p
    assert d["round_no"] == 855, p
    assert d["loop_round"] == 854, p

# round report line append (anchor law: read tail first, single append)
# anchor = exact line prefix (bare "r854" false-positives on r853's next-pointer text)
rp = ROOT + r"\round_reports-bm-c.md"
with io.open(rp, "r", encoding="utf-8") as f:
    body = f.read()
assert ("| r854 |" not in body[-4000:]), "r854 main line already present"
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(report_line + "\n")

print("BOOKS OK round_no=855(label r854) epoch=%d clock=%s report_line_appended=1" % (epoch, now_iso))
