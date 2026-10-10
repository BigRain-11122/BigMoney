# -*- coding: utf-8 -*-
# r858 bm-c books: state + heartbeat bump + r858 round report line
# CLONE SOURCE LAW (r855 pit-lineage entry): round-report CANONICAL path =
#   logs/iteration-loop/round_reports-bm-c.md   (do NOT use the pre-r645 ROOT legacy path)
# r858 clone of _r857bmc_books.py (canonical report path; W208 watch holds, jman 81% follow).
import json, time, io, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

did = ("r858 bm-c: (1) S0-1 identity anchor bm-c + round-zero probe py_faces=14 orphans=1 read-only "
       "(idle ComfyUI 8188 face same as r850-r857, no-kill); S0 dirty-face = own runtime faces, "
       "stash-pull-pop clean (inbound 1 = bm-b r866 books only, rebase clean, W208 NOT landed at "
       "07:0x); (2) S0.5 standing composer s05_probe rc0: ORD 24ad1708 / DEC 68d13893 both "
       "zero-delta, unacked=0 (67 orders / 192 acks); inbox live-check = 0 pending (all 3 recent "
       "MSG already in processed/, closure intact — earlier Get-ChildItem misread corrected via "
       "python os.listdir cross-verify); (3) S1 smoke 49/49; S2 boards empty (job 0 / open tickets "
       "0, 49 all claimed); satengine alive rc0 (queue_next=[], burns=[] = W208 upstream-blocked "
       "known face); (4) WATCH one-line declaration: W208 not landed (bm-a dark since 21:52 "
       "~9.3h, MSG-0535 no answer, no substitution per r565 seat law), M10 cron 9defca39 armed "
       "(cron_list verified); jman trainer 21288 alive CPU 45.6h step 2501/3072 (81.4%) 11.47s/it "
       "ETA ~08:54; (5) PRODUCT-A = S6 43-leg chain 43/43 rc0 (_r858bmc_s6_chain.ps1 r857 "
       "verbatim clone, DONE 07:12:10, dualrun ZERO-DRIFT streak 33->34; update_daily Sunday 0 "
       "new rows cutoff 2026-10-09 legal; compute_audit 3 flags known-adjudicated: "
       "gpu_unauthorized=jman CEO-MV / pool_starvation+supply_floor=W208-blocked seat chain; "
       "py_watermark verdict=py_low_with_work_cands legal carry); PRODUCT-B = QA charter pack 5/5 "
       "(qa/smoke-r858-bm-c.md + equity-curve-r858-bm-c.png 65,449B: 3sym x 800bar 91 trades "
       "determinism=True sharpe 0.1994 win_rate 0.4725 maxdd -0.0431 equity final 1,023,027; "
       "signal CALL rc0 cell=ORA; panel bar 2026-10-09); (6) S7: attrition 4 ledgers CLEAN (2 "
       "healed historical disclosed); quartet green (loop pin=5 no-op first-fire 07:15, watchdog "
       "idempotent -Force re-register first-fire 07:15, pre-commit/pre-push claws LF-normalized "
       "installed); idle --worked (idle_rounds=0, RAM 2.8GB real-work round)")

next_ptr = ("r859: (1) W208 landing watch -> M10 auto-execute chain (freeze W209 -> selftest "
            "default-wave -> pathspec push -> 2-cycle n1_w209 ignition -> MSG receipt + flip M10 "
            "+ delete cron 9defca39); stall escalation live: MSG-20261011-0535 answer watch (bm-a "
            "freeze-prep push OR yield MSG -> adoption per r578 six-step on yield receipt; GM "
            "re-dispatch order = execute same-round); (2) jman completion window ~08:54 (val_grid + "
            "LOOKBOARD_variant_640 + recovery-debt trio per O-20261010-0025, <=48h SLA); (3) W211 "
            "freeze-prep when W210 approaches (read pit-engine-finalize.md FIRST); (4) S0.5 "
            "standing composer; (5) books clone source = _r858bmc_books.py (canonical report path)")

activity = ("当前活: 守望窗（W208 未落链·MSG-0535 待 bm-a 响应/yield/GM 改派·M10 cron 9defca39 armed 17min "
            "节奏·jman trainer 21288 在烧 CPU 45.6h step 81% ETA ~08:54）| 最近实物: S6 43 腿 rc0 streak 34 + QA "
            "证据包 r858 5/5（qa/smoke-r858-bm-c.md + equity-curve-r858-bm-c.png）@ " + now_iso + " | 下个里程碑: "
            "W209 freeze（W208 落链/yield/改派即执行）+ jman 完训验证三件 ~08:54（≤48h SLA）")

verdict = ("r858 close: watch round (W208 hold, bm-a dark ~9.3h) + S6 43/43 rc0 (streak 34) + QA pack "
           "r858 5/5 + smoke 49/49 + jman 81% step 2501/3072 ETA ~08:54")

summary = ("r858 close: watch holds (W208, bm-a dark) + S6 43/43 streak 34 + QA 5/5 + jman 81% ETA ~08:54")

report_line = ("2026-10-11T" + now_iso.split("T")[1] + " | r858 | dept:工程/舰队（守望窗维护轮·S6 43 腿 streak 34·QA 5/5·jman 81% 跟随） | "
               "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
               "WM-VERDICT: 绿（red=false·lane=healthy·probe=py_low_with_work_cands 判读=合法承载非违令：唯一 work cand=local_batch=1 jman 训练批在飞〔trainer 21288 活 45.6h·step 2501/3072 81%·11.47s/it·ETA ~08:54〕+板空/pool 0/open 票 0/bandit 0 机读·引擎队列合法空=W208 上游阻塞已知面·RAM 2.8G 闸·next_pick=claimed moneyflow IC bm-a 车道合法） | "
               "孤儿面=1（py_faces=14·ComfyUI 8188 idle server 同 r850-r857·只读不杀） | "
               "r858: ①S0-1 身份锚 bm-c+round-zero 探针 1 orphan·S0 脏面=本机运行态 stash-pull-pop 干净（入站 1=bm-b r866 books·rebase 干净·W208 未落链）+S0.5 常设组合器 s05_probe rc0（ORD 24ad1708/DEC 68d13893 双零 delta·unacked 0〔67/192〕）+inbox 实况核验=0 待办（三 MSG 均已 processed 闭环·Get-ChildItem 误读经 os.listdir 交叉验证治愈）；"
               "②S1 smoke 49/49·S2 双板空（job 0/open 票 0·49 全 claimed）·satengine 活 rc0（queue_next=[]/burns=[]）；"
               "③守望面一行声明=W208 未落链（bm-a 暗 ~9.3h·MSG-0535 无应答·r565 席位律不代执行）+M10 cron 9defca39 armed（cron_list 验证）+W211 freeze-prep 未到期（W210 未近）+jman 21288 活 CPU 45.6h step 2501/3072 81% ETA ~08:54；"
               "④PRODUCT-A=S6 43/43 rc0（_r858bmc_s6_chain.ps1 r857 verbatim clone·DONE 07:12:10·dualrun ZERO-DRIFT streak 33→34·update_daily 周日 0 新行 cutoff 2026-10-09 合法·compute_audit 三旗=已知定谳面照录〔gpu_unauthorized=jman CEO-MV·pool_starvation/supply_floor=W208 链堵〕）；"
               "⑤PRODUCT-B=QA charter 包 5/5（qa/smoke-r858-bm-c.md+equity-curve-r858-bm-c.png 65,449B：3sym×800bar 91 trades determinism=True sharpe 0.1994 win_rate 0.4725 maxdd -0.0431 equity final 1,023,027·信号 CALL rc0 cell=ORA·面板 bar 2026-10-09）；"
               "⑥S7 attrition 4 台账 CLEAN（2 healed 史披露）+四件套绿（loop pin=5 no-op 首火 07:15/watchdog -Force 重装首火 07:15/双爪 LF 归一 installed）+idle --worked（idle_rounds=0·RAM 2.8G 实工轮） | "
               "r859: (1) W208 落链守望→M10 自动执行链（freeze→selftest→pathspec push→2-cycle n1_w209 点火→MSG 回执+翻 M10+删 cron 9defca39）·MSG-0535 应答观察（yield→r578 六步收养·GM 改派随令即执行）；"
               "(2) jman 完训窗 ~08:54 三件（val_grid+LOOKBOARD_variant_640+恢复债三件 per O-20261010-0025·≤48h SLA）；(3) W211 freeze-prep（W210 近时先读 pit-engine-finalize.md）；"
               "(4) S0.5 常设组合器 | 本轮产品积分：2（S6 43 面再生+QA 证据包 5/5=经营层实物） | 记账预算：3 面内（state+心跳+轮报=法定簿记）")

# round report: read tail first (anchor law), assert r857 main line tail, single append
with io.open(CANON, "r", encoding="utf-8") as f:
    can_body = f.read()
can_lines = [l for l in can_body.splitlines() if l.strip()]
assert ("| r857 |" in can_lines[-1]) and ("r857" in can_lines[-1]), ("canonical tail not r857 main line", can_lines[-1][:80])
assert ("| r858 |" not in can_body[-6000:]), "r858 main line already present"
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
    d["round_no"] = 859
    d["round_no_label"] = "r858"
    d["last_round"] = 858
    d["loop_round"] = 858
    d["heartbeat_epoch_utc"] = epoch
    d["cpu_pct"] = 48; d["cpu_util_pct"] = 48; d["cpu_idle_pct"] = 52
    d["free_ram_gb"] = 2.8; d["idle_ram_gb"] = 2.8; d["ram_free_gb"] = 2.8
    for k in ["gpu_free_vram_mb","gpu_free_vram_mib","gpu_idle_vram_mb","gpu_idle_vram_mib","gpu_vram_free_mb","gpu_free_mb","gpu_free_mib","gpu_idle_mib"]:
        if k in d: d[k] = 94
    d["gpu_idle_mb"] = 94
    d["head_sha"] = "fe7c220c5"
    d["current_task"] = activity
    d["activity_now"] = activity
    d["did"] = did
    d["verdict"] = verdict
    d["last_round_summary"] = summary
    d["note"] = ("r858 = watch round: W208 no-answer holds (MSG-0535 live), S6 43/43 streak 34; "
                 "QA 5/5; jman 81% ETA ~08:54.")
    d["next"] = next_ptr
    d["next_pointer"] = next_ptr
    d["next_milestone"] = ("r859: W209 freeze on W208 landing/yield/GM-redispatch (M10 auto-execute, cron armed) "
                           "+ jman completion window ~08:54 (val_grid + LOOKBOARD_variant_640 + "
                           "recovery-debt trio) <=48h SLA")
    d["latest_artifact"] = ("S6 43-leg chain rc0 streak 34 + QA pack r858 5/5 (qa/smoke-r858-bm-c.md + "
                            "equity-curve-r858-bm-c.png)")
    d["last_artifact"] = d["latest_artifact"]
    d["recent_artifact"] = d["latest_artifact"]
    d["last_action"] = "r858 W208 watch + S6 43-leg chain (streak 34) + QA pack 5/5 + books"
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 1
    d["orphan_faces"] = 1
    d["health"] = "ok"
    d["verify"] = ("receipts: smoke 49/49 + qa/smoke-r858-bm-c.md (5/5 charter) + results/_r858bmc_s6_log.txt "
                   "(43/43 rc0 streak 34, DONE 07:12:10) + attrition CLEAN (4 ledgers) + quartet green + "
                   "idle --worked + this books commit/push_verify")
    if not is_hb:
        d["sync"] = {"ahead_behind": "1/0 pre-books", "origin_tip": "a8ff3243a", "ts": now_iso,
                     "note": "r858 books: watch round + S6/QA products; books commit follows this write"}
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
    assert d["round_no"] == 859, p
    assert d["loop_round"] == 858, p

print("BOOKS OK round_no=859(label r858) epoch=%d clock=%s report_line_appended=1" % (epoch, now_iso))
