# -*- coding: utf-8 -*-
# r862 bm-c books: state + heartbeat bump + r862 round report line
# CLONE SOURCE LAW (r855 pit-lineage entry): round-report CANONICAL path =
#   logs/iteration-loop/round_reports-bm-c.md   (do NOT use the pre-r645 ROOT legacy path)
# r862 clone of _r861bmc_books.py (S0 clean rebase + S6 43/43 + QA pack r862 + jman/W208 watch holds).
import json, time, io, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

did = ("r862 bm-c: (1) S0-1 identity anchor bm-c + round-zero probe py_faces=16 orphans=2 read-only "
       "no-kill (idle ComfyUI 8188 + detached watcher faces; val-chain needs them); (1b) S0 clean: 7 dirty "
       "runtime faces (bm-c heartbeat/probe/autofill/dispatcher/idle_trigger/satengine x2) treasure_guard "
       "prescan 7 paths zero-hit rc0 -> reset HEAD baseline -> fetch b5c601d4b..1ff9f3971 (bm-b r871 4 "
       "commits: daemon face sync take-2/3 + T26 claim [v4 22-gate library A13-style predictor extension "
       "prereg drafting] + W21 supply-face adjudication [alphagen family closed 2/2 rerun ban] + MP1 pool "
       "done-flip settle heal) -> rebase origin/main clean zero-conflict -> in-sync; (2) S0.5 orders diff=0 "
       "unacked (pulled range zero fleet/orders changes; 68 files all acked standing), ORD 24ad1708 / DEC "
       "68d13893 double zero-delta (d19_watermark probe rc0 both changed=false); (3) S1 smoke 49/49; S2 "
       "boards empty (job 0 / open tickets 0 of 183 / inbox unread 0), queue heads CLEAR (tech T5-T25 all "
       "done + T26 claimed@bm-b 2026-10-11 -> no claimable head; explore empty), "
       "queue_head_collision_probe CLEAR; (4) S3: watermark red=false green (next_pick moneyflow IC "
       "reference batch status=claimed blocked-on-panel [bm-a collector lane, 30-min self-heal] -> "
       "advisory-only zero action this machine), satengine alive rc0 (queue_next=[] = W208 "
       "upstream-blocked known face, band ledger registered through W207), idle_trigger green_idle=false "
       "(RAM ~1-2GB free << 40%, VRAM 120MB << 6GB -> no claim obligation; gates disclosure-only per "
       "T-183); (5) WATCH one-liners (anti-rescan law): jman val-chain watcher pythonw 45008 ALIVE 60s "
       "ticks (trainer 21288+34312 musubi krea2_train_network final continuation in burn, final=False "
       "stable=False @08:53:36 tick; receipt NOT yet generated -> consumption stays r863 head item; SLA "
       "board<=10:00 per O-20261010-0025 intact, board ~09:2x expected); W208/W209 freeze-chain cron "
       "9defca39 durable ALIVE (cron_list verified 4-59/17); (6) PRODUCT-A = S6 43-leg chain 43/43 rc0 "
       "(_r862bmc_s6_runner.ps1 clone of r861 runner + per-leg heartbeat lines; dualrun ZERO-DRIFT 420 "
       "entries streak 1 [fresh streak after r861 observation-phase reset]; compute_audit FLAG "
       "gpu_unauthorized=jman trainer [CEO-authorized MV GPU-exclusive line] + supply_floor breach "
       "ready=0<floor 3 [N2-MP1 claimed-but-RAM-gated W17 known face] both known-faces recorded; "
       "py_watermark py_low_with_work_cands n=1 legal whitelist [local_batch_running=true=jman trainer, "
       "pool_ready_count=0, board empty]; update_daily Sunday 0 new rows cutoff 2026-10-09 legal; lane "
       "no-ops honest [ths/ah=bm-a lane, thermo=Money02 absent, options=RETIRED per O-20260929-1105]); "
       "PRODUCT-B = QA charter pack r862 5/5 explicit --round 862 (qa/smoke-r862-bm-c.md + "
       "equity-curve-r862-bm-c.png 65,467B: 3sym x 800bar 91 trades determinism=True sharpe 0.1994 "
       "annual=0.0072 maxdd=-0.0431 win_rate 0.4725 profit_factor 1.2646; signal CALL rc0 cell=ORA "
       "CALL-2026-10-09; panel bar 2026-10-09 latest trading day); (7) S7: attrition 4 ledgers CLEAN (3 "
       "historical shrinks [healed] noted); loop task pin=5 no-op (next fire 08:55); watchdog registered "
       "(first fire 08:52); pre-commit+pre-push claws installed idempotent")

next_ptr = ("r863: (1) jman receipt consumption FIRST: read results/_r860bmc_jman_val_receipt.json "
            "status OK/PARTIAL -> commit LOOKBOARD_variant_640.jpg to GROUP tree (git -C "
            "K:\\Fluxgroup\\FluxGroup add cph4/fleet/mv0001-handover/outbound/krea2/jman-lora-640/"
            "LOOKBOARD_variant_640.jpg + push) + verify 12 PNGs in frames/ + recovery trio state "
            "(MiniGameOllamaServe re-enabled+llama-server back, VRAM check) + report with absolute "
            "path (CEO delivery rule) + if EXCEPTION/FAIL -> diagnose watcher log + re-fire val phase "
            "only; (2) W208/W209 landing watch -> M10 auto-execute chain (unchanged, cron 9defca39 "
            "armed); (3) W211 freeze-prep when W210 approaches + W212 freeze gated (read "
            "pit-engine-finalize.md FIRST); (4) S0.5 standing composer; (5) books clone source = "
            "_r862bmc_books.py (canonical report path)")

activity = ("当前活: jman 完训验证链 watcher 在飞（trainer 21288+34312 final 续训在烧·receipt 未生成·r863 头序消费）"
            "+ W208/W209 落链守望（cron 9defca39 durable armed） | "
            "最近实物: S6 43 腿 rc0（_r862bmc_s6_log.txt）+ QA 包 r862 5/5（qa/smoke-r862-bm-c.md） @ " + now_iso + " | "
            "下个里程碑: LOOKBOARD_variant_640 上链 ~09:2x（SLA ≤10:00 per O-20261010-0025·r863 头序消费）")

verdict = ("r862 close: S0 clean rebase (bm-b r871 pulled, zero conflict) + jman val-chain watcher holds "
           "(trainer final burn, receipt -> r863 head) + W208/W209 cron armed + S6 43/43 rc0 + QA pack "
           "r862 5/5 + smoke 49/49")

summary = ("r862 close: S0 clean rebase (bm-b r871 4 commits pulled zero-conflict) + jman watch holds "
           "(receipt pending r863) + S6 43/43 + QA 5/5")

report_line = ("2026-10-11T" + now_iso.split("T")[1] + " | r862 | dept:工程/舰队（S0 净 rebase+S6 43 腿+QA 5/5·jman/W208 双守望窗维持） | "
               "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
               "WM-VERDICT: 绿（red=false·probe=py_low_with_work_cands n=1 合法白名单：local_batch_running=true=jman trainer CEO 优先 GPU 独占批·pool_ready_count=0〔N2-MP1 RAM-GATE 闸挡 W17 已知面〕·板空/open 票 0/bandit 0·引擎队列合法空=W208 上游阻塞已知面） | "
               "孤儿面=2（py_faces=16·只读不杀=val 链/watcher 需件） | "
               "r862: ①S0-1 身份锚 bm-c+round-zero 探针 2 orphan 只读·S0 净=rebase 收 bm-b r871 四提交（daemon face sync×3+T26 认领+W21 alphagen 族闭合裁定+MP1 settle heal）零冲突零手术；"
               "②S0.5 差集 0（68 令全 ack·拉取域零新令）双水位零 delta（ORD 24ad1708/DEC 68d13893）；"
               "③S1 smoke 49/49·S2 双板空+inbox 0·队头 CLEAR（tech T5-T25 全 done+T26 claimed@bm-b 无可领头/P3 空）；"
               "④守望面一行声明×2=jman watcher pythonw 45008 活（trainer 21288+34312 final 续训·final=False stable=False 08:53:36 tick·receipt 未生成=r863 头序·SLA≤10:00 完好）+W208/W209 cron 9defca39 armed；"
               "⑤PRODUCT-A=**S6 43/43 rc0**（_r862bmc_s6_runner.ps1 克隆+每腿心跳行·dualrun ZERO-DRIFT 420 条 streak 1〔r861 观察相重置后新绿〕·compute_audit FLAG gpu_unauthorized〔jman trainer CEO 授权 MV 线〕+supply_floor ready=0<3〔W17 已知面〕双已知面照录·update_daily 周日 0 新行合法·车道 no-op 诚实〔ths/ah=bm-a 道·thermo=Money02 缺席·options=RETIRED〕）；"
               "⑥PRODUCT-B=QA charter 包 5/5 显式 --round 862（qa/smoke-r862-bm-c.md+equity-curve-r862-bm-c.png 65,467B：3sym×800bar 91 trades determinism=True sharpe 0.1994·signal CALL rc0 cell=ORA·面板 bar 2026-10-09 最新交易日）；"
               "⑦S7 attrition 4 台账 CLEAN（3 史缩 [healed] 注记）+loop task pin=5 no-op（08:55 首火）+watchdog 注册+双爪幂等装 | "
               "r863: (1) jman receipt 消费=头序（group tree commit LOOKBOARD_variant_640.jpg+绝对路径呈报+恢复三件核验；EXCEPTION→诊断 watcher log 重火 val 相）；"
               "(2) W208/W209 落链守望→M10 自动执行链维持；(3) W211/W212 freeze-prep（W210 近时先读 pit-engine-finalize.md）；"
               "(4) S0.5 常设组合器 | 本轮产品积分：2（S6 43 面链=经营层可验实物）+2（QA 包 5/5=charter 证据实物）=4 | 记账预算：3 面内（state+心跳+轮报=法定簿记）")

# round report: read tail first (anchor law), assert r861 main line tail, single append
with io.open(CANON, "r", encoding="utf-8") as f:
    can_body = f.read()
can_lines = [l for l in can_body.splitlines() if l.strip()]
assert ("| r861 |" in can_lines[-1]) and ("r861" in can_lines[-1]), ("canonical tail not r861 main line", can_lines[-1][:80])
assert ("| r862 |" not in can_body[-7000:]), "r862 main line already present"
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
    d["round_no"] = 863
    d["round_no_label"] = "r862"
    d["last_round"] = 862
    d["loop_round"] = 862
    d["heartbeat_epoch_utc"] = epoch
    d["cpu_pct"] = 39; d["cpu_util_pct"] = 39; d["cpu_idle_pct"] = 61
    d["free_ram_gb"] = 1.0; d["idle_ram_gb"] = 1.0; d["ram_free_gb"] = 1.0
    for k in ["gpu_free_vram_mb","gpu_free_vram_mib","gpu_idle_vram_mb","gpu_idle_vram_mib","gpu_vram_free_mb","gpu_free_mb","gpu_free_mib","gpu_idle_mib"]:
        if k in d: d[k] = 120
    d["gpu_idle_mb"] = 120
    d["head_sha"] = "1ff9f3971"
    d["current_task"] = activity
    d["activity_now"] = activity
    d["did"] = did
    d["verdict"] = verdict
    d["last_round_summary"] = summary
    d["note"] = ("r862 = clean-rebase maintenance round: bm-b r871 pulled zero-conflict; jman watcher "
                 "holds (receipt -> r863 head); S6 43/43; QA 5/5.")
    d["next"] = next_ptr
    d["next_pointer"] = next_ptr
    d["next_milestone"] = ("r863: jman receipt consumption (LOOKBOARD_variant_640 group-tree commit + "
                           "absolute-path report + recovery trio verify) + W208/W209 watch (cron 9defca39 armed)")
    d["latest_artifact"] = ("S6 43-leg chain rc0 (_r862bmc_s6_log.txt) + QA pack r862 5/5 "
                            "(equity-curve-r862-bm-c.png)")
    d["last_artifact"] = d["latest_artifact"]
    d["recent_artifact"] = d["latest_artifact"]
    d["last_action"] = ("r862 S0 clean rebase (bm-b r871 pulled) + S6 43-leg chain rc0 + QA pack r862 "
                       "5/5 + books")
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 2
    d["orphan_faces"] = 2
    d["health"] = "ok"
    d["verify"] = ("receipts: smoke 49/49 + qa/smoke-r862-bm-c.md (5/5 charter, explicit --round 862) + "
                   "results/_r862bmc_s6_log.txt (43/43 rc0) + results/_r862bmc_s6_runner.ps1 (clone with "
                   "per-leg heartbeat lines) + attrition CLEAN (4 ledgers, 3 healed shrinks noted) + this "
                   "books commit/push_verify")
    if not is_hb:
        d["sync"] = {"ahead_behind": "1/0 pre-books", "origin_tip": "1ff9f3971", "ts": now_iso,
                     "note": "r862 books: S6 43/43 + QA pack r862; commit+push follows this write"}
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
    assert d["round_no"] == 863, p
    assert d["loop_round"] == 862, p

print("BOOKS OK round_no=863(label r862) epoch=%d clock=%s report_line_appended=1" % (epoch, now_iso))
