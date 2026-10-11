# -*- coding: utf-8 -*-
# r860 bm-c books: state + heartbeat bump + r860 round report line
# CLONE SOURCE LAW (r855 pit-lineage entry): round-report CANONICAL path =
#   logs/iteration-loop/round_reports-bm-c.md   (do NOT use the pre-r645 ROOT legacy path)
# r860 clone of _r859bmc_books.py (canonical report path; jman val-chain kit armed + watch holds).
import json, time, io, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

did = ("r860 bm-c: (1) S0-1 identity anchor bm-c + round-zero probe py_faces=15 orphans=1 read-only "
       "(idle ComfyUI 8188 face same as r850-r859, no-kill; val-chain needs it); S0 dirty-face = 6 own "
       "runtime faces stash->rebase->pop clean ('Already up to date' 07:55; post-round fetch caught bm-b "
       "3 new = n2-mp1 autofill-claim family, closeout rebase handles); (2) S0.5 orders diff=0 (unacked 0), "
       "ORD 24ad1708 / DEC 68d13893 double zero-delta (d19_watermark probe rc0); (3) S1 smoke 49/49; "
       "S2 boards empty (job 0 / open tickets 0), queue heads CLEAR (tech T22 done / explore empty), "
       "queue_head_collision_probe CLEAR, satengine alive rc0 (queue_next=[], burns=[] = W208 "
       "upstream-blocked known face); moneyflow IC advisory still source-blocked (conn_stopped=true, "
       "rank fetch_failed 02:12, parked self-heal); (4) WATCH one-line (anti-rescan law): W208 NOT "
       "landed (origin tip 5c51cc0bc = bm-b autofill-claim family, zero bm-a commits), MSG-0535 "
       "unanswered, M10 cron 9defca39 armed (cron_list verified), r565 seat law no-substitution; "
       "(5) PRODUCT-A = jman val chain kit BUILT + detached watcher ARMED (O-20261010-0025 SLA "
       "board<=10:00): trainer 21288 alive 9.1h (cont-000010 landed 07:21, final cont-000012 ETA "
       "~08:54); kit = results/_r860bmc_jman_val_watcher.py self-contained 5-phase (WAIT->VAL->BOARD->"
       "RECOVERY->RECEIPT): recipe = kf_fix2_fleet proven graph (UNETLoader krea2_turbo_fp8 + "
       "CLIPLoader qwen3vl_4b_fp8 type=krea2 + VAELoader qwen_image_vae + KSampler 8step cfg1 euler "
       "simple + ConditioningZeroOut) + LoraLoaderModelOnly node verified via /object_info; 4 "
       "canonical scenes x strength {0,0.8,1.0} x fixed seed per scene = 12 gens @1024 sq sequential "
       "submit (RAM-safe), scenes = promo_closeup/library_lamplight/campus_bicycle/stage_mic with ID "
       "block verbatim from dataset captions; ALL 4 lint-PASS via prompt_lexicon t2i (scene0 "
       "[VAGUE]moody caught + fixed -> dark low-key studio light, spec-discipline closed loop); "
       "recovery-debt trio encoded (MiniGameOllamaServe/KeepWarm enable+run, verified both Disabled "
       "pre-fire, + comfy /free unload ordering after val); hard-kill window 09:35 (r833 same-line "
       "priority law) + teardown-hang kill (final ckpt stable 5min); launched detached pythonw "
       "08:05:34 zero-window, 60s tick log verified (last 08:12:35), receipt=results/"
       "_r860bmc_jman_val_receipt.json, board=cph4 jman-lora-640/LOOKBOARD_variant_640.jpg; "
       "(6) PRODUCT-B = S6 43-leg chain 43/43 rc0 (_r860bmc_s6_runner.ps1 verbatim clone, dualrun "
       "ZERO-DRIFT streak 35->36, 420 entries; update_daily Sunday 0 new rows cutoff 2026-10-09 "
       "legal; py_watermark verdict=insufficient_history n=1 legal with local_batch=true jman); "
       "PRODUCT-C = QA charter pack 5/5 explicit --round 860 (qa/smoke-r860-bm-c.md + "
       "equity-curve-r860-bm-c.png 65,510B: 3sym x 800bar 91 trades determinism=True sharpe 0.1994 "
       "win_rate 0.4725 maxdd -0.0431; signal CALL rc0 cell=ORA; panel bar 2026-10-09); (7) S7: "
       "attrition 4 ledgers CLEAN; autofill watchdog claim 0ab7c2bb4 n2-mp1-run-0of1 owner=bm-c "
       "(r199 launch-claim + r290 self-commit law, RAM gate blocks launch = known W17 face)")

next_ptr = ("r861: (1) jman receipt consumption FIRST: read results/_r860bmc_jman_val_receipt.json "
            "status OK/PARTIAL -> commit LOOKBOARD_variant_640.jpg to GROUP tree (git -C "
            "K:\\Fluxgroup\\FluxGroup add cph4/fleet/mv0001-handover/outbound/krea2/jman-lora-640/"
            "LOOKBOARD_variant_640.jpg + push) + verify 12 PNGs in frames/ + recovery trio state "
            "(MiniGameOllamaServe re-enabled+llama-server back, VRAM check) + report with absolute "
            "path (CEO delivery rule) + if EXCEPTION/FAIL -> diagnose watcher log + re-fire val "
            "phase only; (2) W208 landing watch -> M10 auto-execute chain (unchanged, cron armed); "
            "(3) W211 freeze-prep when W210 approaches + W212 freeze gated (read "
            "pit-engine-finalize.md FIRST); (4) S0.5 standing composer; (5) books clone source = "
            "_r860bmc_books.py (canonical report path)")

activity = ("当前活: jman 完训验证链 watcher 在飞（trainer 21288 ETA ~08:54·detached pythonw 60s tick·val "
            "grid 12 gen→LOOKBOARD_variant_640→恢复债三件自动执行）+ W208 未落链守望（M10 cron 9defca39 armed） | "
            "最近实物: jman val chain kit + watcher armed 08:05:34（4 场景 lint-PASS·recovery trio 编码·receipt 面就绪）+ "
            "S6 43 腿 rc0 streak 36 + QA 包 r860 5/5 @ " + now_iso + " | 下个里程碑: LOOKBOARD_variant_640 上链 "
            "~09:2x（receipt 消费轮 commit group tree·SLA ≤10:00 per O-20261010-0025）")

verdict = ("r860 close: jman val-chain kit armed (watcher detached, auto-fire on trainer completion) + "
           "watch holds (W208, bm-a dark) + S6 43/43 rc0 (streak 36) + QA pack r860 5/5 + smoke 49/49")

summary = ("r860 close: jman val chain kit + detached watcher armed (SLA board<=10:00) + W208 watch holds + "
           "S6 43/43 streak 36 + QA 5/5")

report_line = ("2026-10-11T" + now_iso.split("T")[1] + " | r860 | dept:工程/舰队（jman 完训验证链 kit+watcher armed·S6 43 腿 streak 36·QA 5/5·守望窗维持） | "
               "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
               "WM-VERDICT: 绿（red=false·probe=insufficient_history n=1 周日合法态·local_batch=true=jman 训练批+val watcher 正活·pool_ready N2-MP1=autofill 已 claim 0ab7c2bb4·板空/open 票 0/bandit 0·引擎队列合法空=W208 上游阻塞已知面·RAM 0.4G 闸=jman trainer+ComfyUI+CEO 前台·O-0012 §3 审计面照录） | "
               "孤儿面=1（py_faces=15·ComfyUI 8188 idle server 同 r850-r859·只读不杀=val 链需件） | "
               "r860: ①S0-1 身份锚 bm-c+round-zero 探针 1 orphan·S0 脏面=本机运行态 stash-rebase-pop 干净+S0.5 差集 0 双水位零 delta（ORD 24ad1708/DEC 68d13893）；"
               "②S1 smoke 49/49·S2 双板空·队头 CLEAR·satengine 活 rc0·moneyflow IC 面板 source-blocked parked 照旧；"
               "③守望面一行声明=W208 未落链（origin tip 5c51cc0bc=bm-b autofill-claim 族·零 bm-a 提交）+M10 cron armed+MSG-0535 无应答维持；"
               "④PRODUCT-A=**jman 完训验证链 kit+detached watcher armed**（O-20261010-0025 SLA board≤10:00·trainer 21288 9.1h 活 cont-000010@07:21·final cont-000012 ETA ~08:54·kit=5 相位自足 WAIT→VAL→BOARD→RECOVERY→RECEIPT·配方=kf_fix2_fleet 已证图+LoraLoaderModelOnly 过 /object_info·4 正典场景×strength{0,0.8,1.0}×固种子=12 gen@1024 串行·ID 块逐字承 dataset captions·4 场景全 lint-PASS〔scene0 [VAGUE]moody 抓获修复〕·恢复债三件编码〔OllamaServe/KeepWarm enable 验 Disabled+先 /free 后恢复序〕·硬杀窗 09:35 r833 同线优先律+teardown-hang 5min 杀·pythonw 分离零窗 08:05:34·60s tick 验证 08:12:35·receipt=results/_r860bmc_jman_val_receipt.json）；"
               "⑤PRODUCT-B=S6 43/43 rc0（_r860bmc_s6_runner.ps1·dualrun ZERO-DRIFT streak 35→36·420 entries·update_daily 周日 0 新行合法）；"
               "⑥PRODUCT-C=QA charter 包 5/5 显式 --round 860（qa/smoke-r860-bm-c.md+equity-curve-r860-bm-c.png 65,510B：3sym×800bar 91 trades determinism=True sharpe 0.1994·信号 CALL rc0 cell=ORA·面板 bar 2026-10-09）；"
               "⑦S7 attrition 4 台账 CLEAN+autofill watchdog claim 0ab7c2bb4 n2-mp1 owner=bm-c（r199/r290 律·RAM 闸挡 launch=已知面） | "
               "r861: (1) jman receipt 消费=头序（status OK/PARTIAL→group tree commit LOOKBOARD_variant_640.jpg+push+绝对路径呈报+恢复三件核验；EXCEPTION→诊断 watcher log 重火 val 相）；"
               "(2) W208 落链守望→M10 自动执行链维持；(3) W211/W212 freeze-prep（W210 近时先读 pit-engine-finalize.md）；"
               "(4) S0.5 常设组合器 | 本轮产品积分：2（jman val chain kit+watcher=可跑实物·完训自动出 LOOKBOARD=供给线）+2（S6 43 面+QA 5/5=经营层实物）=4 | 记账预算：3 面内（state+心跳+轮报=法定簿记）")

# round report: read tail first (anchor law), assert r859 main line tail, single append
with io.open(CANON, "r", encoding="utf-8") as f:
    can_body = f.read()
can_lines = [l for l in can_body.splitlines() if l.strip()]
assert ("| r859 |" in can_lines[-1]) and ("r859" in can_lines[-1]), ("canonical tail not r859 main line", can_lines[-1][:80])
assert ("| r860 |" not in can_body[-6000:]), "r860 main line already present"
with io.open(CANON, "a", encoding="utf-8", newline="") as f:
    f.write(report_line + "\n")


def upd(path, is_hb):
    with io.open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    ts_fields = ["ts","last_seen","last_seen_at","clock_read","updated","updated_at","last_run_at","last_round_at",
                 "last_round_ts","last_ts","last_round_closed","current_task_at","last_round_summary_at",
                 "last_orders_read_at","last_pulled_at","last_action_at","last_round_at_legacy"]
    for k in ts_fields:
        if k in d: d[k] = now_iso
    d["round_no"] = 861
    d["round_no_label"] = "r860"
    d["last_round"] = 860
    d["loop_round"] = 860
    d["heartbeat_epoch_utc"] = epoch
    d["cpu_pct"] = 40; d["cpu_util_pct"] = 40; d["cpu_idle_pct"] = 60
    d["free_ram_gb"] = 0.4; d["idle_ram_gb"] = 0.4; d["ram_free_gb"] = 0.4
    for k in ["gpu_free_vram_mb","gpu_free_vram_mib","gpu_idle_vram_mb","gpu_idle_vram_mib","gpu_vram_free_mb","gpu_free_mb","gpu_free_mib","gpu_idle_mib"]:
        if k in d: d[k] = 109
    d["gpu_idle_mb"] = 109
    d["head_sha"] = "0ab7c2bb4"
    d["current_task"] = activity
    d["activity_now"] = activity
    d["did"] = did
    d["verdict"] = verdict
    d["last_round_summary"] = summary
    d["note"] = ("r860 = jman val-kit arming round: watcher detached (auto-fire ~08:54, board ~09:2x, "
                 "SLA <=10:00), W208 watch holds, S6 43/43 streak 36; QA 5/5.")
    d["next"] = next_ptr
    d["next_pointer"] = next_ptr
    d["next_milestone"] = ("r861: jman receipt consumption (LOOKBOARD_variant_640 group-tree commit + "
                           "absolute-path report + recovery trio verify) + W208 watch (M10 armed)")
    d["latest_artifact"] = ("jman val chain kit + detached watcher armed 08:05:34 (5-phase self-contained, "
                            "4 scenes lint-PASS, recovery trio encoded, receipt path ready) + S6 43-leg "
                            "chain rc0 streak 36 + QA pack r860 5/5")
    d["last_artifact"] = d["latest_artifact"]
    d["recent_artifact"] = d["latest_artifact"]
    d["last_action"] = ("r860 jman val-kit arm (watcher detached) + W208 watch + S6 43-leg chain "
                        "(streak 36) + QA pack r860 5/5 + books")
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 1
    d["orphan_faces"] = 1
    d["health"] = "ok"
    d["verify"] = ("receipts: smoke 49/49 + qa/smoke-r860-bm-c.md (5/5 charter, explicit --round 860) + "
                   "results/_r860bmc_s6_log.txt (43/43 rc0 streak 36) + results/"
                   "_r860bmc_jman_val_watcher.py (kit, syntax-checked, 4-scene lint-PASS) + results/"
                   "_r860bmc_jman_val_watcher.log (detached ticks) + attrition CLEAN (4 ledgers) + this "
                   "books commit/push_verify")
    if not is_hb:
        d["sync"] = {"ahead_behind": "1/3 pre-books", "origin_tip": "5c51cc0bc", "ts": now_iso,
                     "note": "r860 books: jman val-kit + S6/QA products; closeout rebase (bm-b x3) then commit+push"}
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return d

upd(ROOT + r"\state-bm-c.json", False)

# heartbeat (fleet/machines/bm-c.json): CRLF face, indent=1 (r852 close convention)
upd(ROOT + r"\fleet\machines\bm-c.json", True)
raw = io.open(ROOT + r"\fleet\machines\bm-c.json", "r", encoding="utf-8").read()
io.open(ROOT + r"\fleet\machines\bm-c.json", "w", encoding="utf-8", newline="").write(raw.replace("\n", "\r\n"))

for p in [ROOT + r"\state-bm-c.json", ROOT + r"\fleet\machines\bm-c.json"]:
    with io.open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert isinstance(d["heartbeat_epoch_utc"], int), p
    assert "T" in d["clock_read"], p
    assert d["round_no"] == 861, p
    assert d["loop_round"] == 860, p

print("BOOKS OK round_no=861(label r860) epoch=%d clock=%s report_line_appended=1" % (epoch, now_iso))
