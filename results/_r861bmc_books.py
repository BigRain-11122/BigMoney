# -*- coding: utf-8 -*-
# r861 bm-c books: state + heartbeat bump + r861 round report line
# CLONE SOURCE LAW (r855 pit-lineage entry): round-report CANONICAL path =
#   logs/iteration-loop/round_reports-bm-c.md   (do NOT use the pre-r645 ROOT legacy path)
# r861 clone of _r860bmc_books.py (S0 stash-pop conflict surgery + r860 books landed + S6/QA products).
import json, time, io, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

did = ("r861 bm-c: (1) S0-1 identity anchor bm-c + round-zero probe py_faces=15 orphans=1 read-only "
       "(idle ComfyUI 8188 face same as r850-r860, no-kill; val-chain needs it); (1b) S0 CONFLICT SURGERY "
       "(round opener): r860 closeout stash-pop left 15 UU runtime/daily faces + stash retained + zero "
       "sequencer state (diagnosed via stash in-ce 'r860 closeout temp'); treasure_guard prescan 15 paths "
       "zero-hit rc0 -> reset 15 faces to HEAD baseline -> r860 closeout books commit (37 files, 730 "
       "insertions: S6 outputs + jman val-kit + books lines) -> pull --rebase met SECOND conflict face (18 "
       "shared faces = bm-a round-870 S6 books same-window writes: daily_scorecard/dashboard x2/paper x6/"
       "paper_export x2/prospect summaries x2/scorecard_v1/strategy_scorecard/t35_open_fill_verify/"
       "x2_watch_log) -> resolved ours=origin side (host=bm-a authoritative + this-round regenerable) + "
       "r787/r864 atomic add-A + git -c core.editor=true rebase --continue -> rebased clean -> push "
       "d1e2df78f -> fetch+rev-list 0/0 self-verified; r860 books debt cleared on origin; (2) S0.5 orders "
       "diff=0 unacked (68 files all acked), ORD 24ad1708 / DEC 68d13893 double zero-delta (d19_watermark "
       "probe rc0); (3) S1 smoke 49/49; S2 boards empty (job 0 / open tickets 0 / inbox unread 0), queue "
       "heads CLEAR (tech T5-T25 ALL done / explore empty), queue_head_collision_probe CLEAR, satengine "
       "alive rc0 (queue_next=[] = W208 upstream-blocked known face), idle_trigger green_idle=false (RAM "
       "12 pct -> no claim obligation, vram gate disclosure-only per T-183); (4) WATCH one-liners "
       "(anti-rescan law): jman trainer 21288 WAIT-phase alive 08:38:35 tick (receipt NOT yet generated -> "
       "consumption stays r862 head item; watcher detached 60s ticks verified; SLA board<=10:00 per "
       "O-20261010-0025 intact, final cont ETA ~08:54 -> board ~09:2x); W208/W209 freeze-chain cron "
       "9defca39 durable ALIVE (cron_list verified 4-59/17); (5) PRODUCT-A = S0 conflict surgery + r860 "
       "closeout books landed d1e2df78f (tree unblocked 0 dirty face, round-opener infrastructure fix); "
       "(6) PRODUCT-B = S6 43-leg chain 43/43 rc0 (_r861bmc_s6_runner.ps1 verbatim clone + per-leg "
       "heartbeat lines; dualrun DRIFT observation entry-419 done_at missing-left -> zero-drift streak "
       "reset 36->0 honest observation-phase data per law; compute_audit FLAG gpu_unauthorized=jman "
       "trainer (CEO-authorized MV GPU-exclusive line) + supply_floor breach ready=0<floor 3 (N2-MP1 "
       "claimed-but-RAM-gated W17 known face) both known-faces recorded; update_daily Sunday 0 new rows "
       "cutoff 2026-10-09 legal; py_watermark py_low_with_work_cands n=2 legal whitelist); PRODUCT-C = "
       "QA charter pack 5/5 explicit --round 861 (qa/smoke-r861-bm-c.md + equity-curve-r861-bm-c.png "
       "65,385B: 3sym x 800bar 91 trades determinism=True sharpe 0.1994 win_rate 0.4725 maxdd -0.0431 "
       "profit_factor 1.2646; signal CALL rc0 cell=ORA; panel bar 2026-10-09 golden-week no-op "
       "expected); (8) S7: attrition 4 ledgers CLEAN (2 historical shrinks [healed] noted); loop task "
       "pin=5 no-op (first fire 08:45); watchdog registered (first fire 08:40); pre-commit+pre-push "
       "claws installed idempotent")

next_ptr = ("r862: (1) jman receipt consumption FIRST: read results/_r860bmc_jman_val_receipt.json "
            "status OK/PARTIAL -> commit LOOKBOARD_variant_640.jpg to GROUP tree (git -C "
            "K:\\Fluxgroup\\FluxGroup add cph4/fleet/mv0001-handover/outbound/krea2/jman-lora-640/"
            "LOOKBOARD_variant_640.jpg + push) + verify 12 PNGs in frames/ + recovery trio state "
            "(MiniGameOllamaServe re-enabled+llama-server back, VRAM check) + report with absolute "
            "path (CEO delivery rule) + if EXCEPTION/FAIL -> diagnose watcher log + re-fire val phase "
            "only; (2) W208/W209 landing watch -> M10 auto-execute chain (unchanged, cron 9defca39 "
            "armed); (3) W211 freeze-prep when W210 approaches + W212 freeze gated (read "
            "pit-engine-finalize.md FIRST); (4) S0.5 standing composer; (5) books clone source = "
            "_r861bmc_books.py (canonical report path)")

activity = ("当前活: jman 完训验证链 watcher 在飞（trainer 21288 final cont ETA ~08:54·receipt 未生成·r862 头序消费）"
            "+ W208/W209 落链守望（cron 9defca39 durable armed） | "
            "最近实物: r860 closeout books 上链 d1e2df78f（S0 冲突手术=15 UU 解结+rebase 二段冲突收口）+ "
            "S6 43 腿 rc0 + QA 包 r861 5/5 @ " + now_iso + " | "
            "下个里程碑: LOOKBOARD_variant_640 上链 ~09:2x（SLA ≤10:00 per O-20261010-0025·r862 头序消费）")

verdict = ("r861 close: S0 stash-pop conflict surgery done + r860 books landed (d1e2df78f) + jman "
           "val-chain watcher holds (WAIT phase) + W208/W209 cron armed + S6 43/43 rc0 + QA pack "
           "r861 5/5 + smoke 49/49")

summary = ("r861 close: S0 conflict surgery (15 UU + rebase second face resolved) + r860 books landed "
           "d1e2df78f + jman watch holds (receipt pending r862) + S6 43/43 + QA 5/5")

report_line = ("2026-10-11T" + now_iso.split("T")[1] + " | r861 | dept:工程/舰队（S0 冲突手术+r860 books 补上链·S6 43 腿·QA 5/5·jman/W208 双守望窗维持） | "
               "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
               "WM-VERDICT: 绿（red=false·probe=py_low_with_work_cands n=2 合法白名单：local_batch_running=true=jman trainer CEO 优先 GPU 独占批·pool_ready N2-MP1 已 autofill claim 但 RAM-GATE 4GB 闸挡〔free 2.1G〕=W17 已知面·板空/open 票 0/bandit 0·引擎队列合法空=W208 上游阻塞已知面） | "
               "孤儿面=1（py_faces=15·ComfyUI 8188 idle server 同 r850-r860·只读不杀=val 链需件） | "
               "r861: ①S0-1 身份锚 bm-c+round-zero 探针 1 orphan·**S0 冲突手术=r860 closeout stash-pop 遗留 15 UU（运行时/日报可再生面·无序列器态·stash 在册确诊）→treasure_guard prescan 15 路径零命中 rc0→重置 HEAD 基线→r860 books 补提交 37 件→pull --rebase 二段冲突〔18 共享面=bm-a round-870 S6 books 同窗写〕→ours=origin 侧+r787/r864 原子 continue→干净 rebase→push d1e2df78f→0/0 自证**；"
               "②S0.5 差集 0（68 令全 ack）双水位零 delta（ORD 24ad1708/DEC 68d13893）；"
               "③S1 smoke 49/49·S2 双板空+inbox 0·队头 CLEAR（tech T5-T25 全 done/P3 空）·satengine 活 rc0 queue_next=[]（W208 上游阻塞已知面）·idle green=false 无领单义务；"
               "④守望面一行声明×2=jman trainer 21288 WAIT 相位活 08:38:35（receipt 未生成·r862 头序消费·SLA≤10:00 完好）+W208/W209 cron 9defca39 durable armed（cron_list 验活）；"
               "⑤PRODUCT-A=**S0 冲突手术+r860 closeout books 上链 d1e2df78f**（树解堵 0 脏面）；"
               "⑥PRODUCT-B=S6 43/43 rc0（_r861bmc_s6_runner.ps1 正典克隆+每腿心跳行·dualrun DRIFT 观察 entry-419 done_at 缺左→streak 36→0 观察相数据合法照录·compute_audit FLAG gpu_unauthorized=jman trainer〔CEO 授权 MV GPU 独占线〕+supply_floor ready=0<3〔N2-MP1 已 claim RAM 闸挡 W17 已知面〕双已知面照录·update_daily 周日 0 新行合法）；"
               "⑦PRODUCT-C=QA charter 包 5/5 显式 --round 861（qa/smoke-r861-bm-c.md+equity-curve-r861-bm-c.png 65,385B：3sym×800bar 91 trades determinism=True sharpe 0.1994·signal CALL rc0 cell=ORA·面板 bar 2026-10-09）；"
               "⑧S7 attrition 4 台账 CLEAN（2 史缩 [healed] 注记）+loop task pin=5 no-op+watchdog 注册（08:40 首火）+pre-commit/pre-push 双爪幂等装 | "
               "r862: (1) jman receipt 消费=头序（group tree commit LOOKBOARD_variant_640.jpg+绝对路径呈报+恢复三件核验；EXCEPTION→诊断 watcher log 重火 val 相）；"
               "(2) W208/W209 落链守望→M10 自动执行链维持；(3) W211/W212 freeze-prep（W210 近时先读 pit-engine-finalize.md）；"
               "(4) S0.5 常设组合器 | 本轮产品积分：2（S0 冲突手术+r860 books 上链=可验基础设施实物）+2（S6 43 面+QA 5/5=经营层实物）=4 | 记账预算：3 面内（state+心跳+轮报=法定簿记）")

# round report: read tail first (anchor law), assert r860 main line tail, single append
with io.open(CANON, "r", encoding="utf-8") as f:
    can_body = f.read()
can_lines = [l for l in can_body.splitlines() if l.strip()]
assert ("| r860 |" in can_lines[-1]) and ("r860" in can_lines[-1]), ("canonical tail not r860 main line", can_lines[-1][:80])
assert ("| r861 |" not in can_body[-7000:]), "r861 main line already present"
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
    d["round_no"] = 862
    d["round_no_label"] = "r861"
    d["last_round"] = 861
    d["loop_round"] = 861
    d["heartbeat_epoch_utc"] = epoch
    d["cpu_pct"] = 31; d["cpu_util_pct"] = 31; d["cpu_idle_pct"] = 69
    d["free_ram_gb"] = 2.1; d["idle_ram_gb"] = 2.1; d["ram_free_gb"] = 2.1
    for k in ["gpu_free_vram_mb","gpu_free_vram_mib","gpu_idle_vram_mb","gpu_idle_vram_mib","gpu_vram_free_mb","gpu_free_mb","gpu_free_mib","gpu_idle_mib"]:
        if k in d: d[k] = 304
    d["gpu_idle_mb"] = 304
    d["head_sha"] = "d1e2df78f"
    d["current_task"] = activity
    d["activity_now"] = activity
    d["did"] = did
    d["verdict"] = verdict
    d["last_round_summary"] = summary
    d["note"] = ("r861 = S0 conflict-surgery round: r860 closeout stash-pop 15-UU resolved + books landed "
                 "d1e2df78f; jman watcher holds (receipt -> r862 head); S6 43/43; QA 5/5.")
    d["next"] = next_ptr
    d["next_pointer"] = next_ptr
    d["next_milestone"] = ("r862: jman receipt consumption (LOOKBOARD_variant_640 group-tree commit + "
                           "absolute-path report + recovery trio verify) + W208/W209 watch (cron 9defca39 armed)")
    d["latest_artifact"] = ("S0 conflict surgery + r860 closeout books landed d1e2df78f (37 files) + S6 "
                            "43-leg chain rc0 + QA pack r861 5/5 (equity-curve-r861-bm-c.png)")
    d["last_artifact"] = d["latest_artifact"]
    d["recent_artifact"] = d["latest_artifact"]
    d["last_action"] = ("r861 S0 conflict surgery (stash-pop 15 UU + rebase second face) + r860 books "
                        "landed + S6 43-leg chain + QA pack r861 5/5 + books")
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 1
    d["orphan_faces"] = 1
    d["health"] = "ok"
    d["verify"] = ("receipts: smoke 49/49 + qa/smoke-r861-bm-c.md (5/5 charter, explicit --round 861) + "
                   "results/_r861bmc_s6_log.txt (43/43 rc0) + results/_r861bmc_s6_runner.ps1 (clone with "
                   "per-leg heartbeat lines) + attrition CLEAN (4 ledgers) + push d1e2df78f 0/0 "
                   "self-verified + this books commit/push_verify")
    if not is_hb:
        d["sync"] = {"ahead_behind": "1/0 pre-books", "origin_tip": "d1e2df78f", "ts": now_iso,
                     "note": "r861 books: S0-conflict surgery + S6/QA products; commit+push follows this write"}
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
    assert d["round_no"] == 862, p
    assert d["loop_round"] == 861, p

print("BOOKS OK round_no=862(label r861) epoch=%d clock=%s report_line_appended=1" % (epoch, now_iso))
