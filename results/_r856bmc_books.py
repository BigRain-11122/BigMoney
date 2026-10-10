# -*- coding: utf-8 -*-
# r856 bm-c books: state + heartbeat bump + r856 round report line
# CLONE SOURCE LAW (r855 pit-lineage entry): round-report CANONICAL path =
#   logs/iteration-loop/round_reports-bm-c.md   (do NOT use the pre-r645 ROOT legacy path)
import json, time, io, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

did = ("r856 bm-c: (1) S0-1 identity anchor bm-c + round-zero probe py_faces=14 orphans=1 read-only "
       "(idle ComfyUI 8188 face same as r850-r855, no-kill); S0 own 7 runtime faces absorb-commit "
       "7d037757e + rebase up-to-date at 06:26 (W208 not landed); MID-ROUND bm-b r865 double-commit "
       "landed (bba56e39a N2-W20 slice-1 + 161bd57c2 HANDOVER) -> absorb-2 dd35875a4 -> rebase 14-UU "
       "same-window S6 family resolved by _r856bmc_rebase_resolver.py (10 ts-audited theirs-newer "
       "06:34-06:39 > ours 06:33-06:35 + 3 md twins follow json + compute_audit history ts-key UNION "
       "201/201->201 latest-base=ours) -> rebase --continue clean -> HEAD b2d50e1a4; W208 STILL not "
       "landed (bm-b commits are N2 family, bm-a still dark ~9h); (2) S0.5 standing composer: ORD "
       "24ad1708 / DEC 68d13893 both zero-delta, unacked=0; inbox 1 consumed = MSG-20261011-0628 "
       "bm-b N2-W20 draft declaration (lane bm-b, collision probe CLEAR, zero bm-c action, moved "
       "processed); (3) S1 smoke 49/49; S2 boards empty (job 0 / open tickets 0, 49 all claimed); "
       "satengine alive rc0 (queue_next=[], burns=[] = W208 upstream-blocked known face); (4) WATCH: "
       "M10 cron 9defca39 armed (cron_list verified); jman 21288 alive CPU 42.7h ETA ~08:37-09:00 "
       "unchanged; (5) PRODUCT-A = S6 43-leg chain 43/43 rc0 (DONE 06:36:42, dualrun ZERO-DRIFT "
       "streak 31->32; update_daily Sunday 0 new rows cutoff 2026-10-09 legal; compute_audit 3 flags "
       "known-adjudicated: gpu_unauthorized=jman CEO-MV / pool_starvation+supply_floor=W208-blocked "
       "seat chain); PRODUCT-B = QA charter pack 5/5 (qa/smoke-r856-bm-c.md + equity-curve-r856-bm-c.png "
       "65,434B: 3sym x 800bar 91 trades determinism=True sharpe 0.1994 win_rate 0.4725 maxdd -0.0431 "
       "equity final 1,023,027; signal CALL rc0 cell=ORA; panel bar 2026-10-09); (6) S7: attrition 4 "
       "ledgers CLEAN (3 healed historical disclosed); quartet green (loop pin=5 no-op first-fire "
       "06:45, watchdog first-fire 06:41, pre-commit/pre-push claws installed LF-normalized); idle "
       "--worked (idle_rounds=0); py_watermark verdict=py_low_with_work_cands legal carry (local_batch=1 "
       "jman + boards/pool/bandit all empty machine-read)")

next_ptr = ("r857: (1) W208 landing watch -> M10 auto-execute chain (freeze -> selftest default-wave -> "
            "pathspec push -> 2-cycle n1_w209 ignition -> MSG receipt + flip M10 + delete cron 9defca39); "
            "stall escalation live: MSG-20261011-0535 answer watch (bm-a freeze-prep push OR yield MSG -> "
            "adoption per r578 six-step on yield receipt; GM re-dispatch order = execute same-round); "
            "(2) jman completion window ~08:37-09:00 (val_grid + LOOKBOARD_variant_640 + recovery-debt trio "
            "per O-20261010-0025, <=48h SLA); (3) W211 freeze-prep when W210 approaches (read "
            "pit-engine-finalize.md FIRST); (4) S0.5 standing composer; (5) books clone source = "
            "_r856bmc_books.py (canonical report path)")

activity = ("当前活: 守望窗（W208 未落链·MSG-0535 待 bm-a 响应/yield/GM 改派·M10 cron 9defca39 armed 17min "
            "节奏·jman trainer 21288 在烧 ETA ~08:37-09:00）| 最近实物: S6 43 腿 rc0 streak 32 + QA 证据包 "
            "r856 5/5（qa/smoke-r856-bm-c.md + equity-curve-r856-bm-c.png）+ 14-UU rebase 收口 "
            "（bm-b r865 同窗竞速 ts-audited 解决）@ " + now_iso + " | 下个里程碑: W209 freeze（W208 落链/"
            "yield/改派即执行）+ jman 完训验证三件 ~08:37-09:00（≤48h SLA）")

verdict = ("r856 close: watch round (W208 hold, bm-b r865 mid-round race resolved 14-UU ts-audited) + S6 43/43 "
           "rc0 (streak 32) + QA pack 5/5 + smoke 49/49 + jman 42.7h ETA ~08:37")

summary = ("r856 close: watch holds + S6 43/43 streak 32 + QA 5/5 + mid-round rebase race 14-UU resolved "
           "(bm-b r865) + jman ETA ~08:37")

report_line = ("2026-10-11T" + now_iso.split("T")[1] + " | r856 | dept:工程/舰队（守望窗维护轮·S6 43 腿 streak 32·QA 5/5·轮中 bm-b r865 竞速 14-UU 收口） | "
               "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
               "WM-VERDICT: 绿（red=false·lane=healthy·probe=py_low_with_work_cands 判读=合法承载非违令：唯一 work cand=local_batch=1 jman 训练批在飞〔trainer 21288 活 42.7h〕+板空/pool 0/open 票 0/bandit 0 机读·引擎队列合法空=W208 上游阻塞已知面·next_pick=claimed moneyflow IC bm-a 车道合法） | "
               "孤儿面=1（py_faces=14·ComfyUI 8188 idle server 同 r850-r855·只读不杀） | "
               "r856: ①S0-1 身份锚 bm-c+round-zero 探针 1 orphan·S0 本机 7 runtime faces absorb commit 7d037757e+rebase up-to-date（06:26 时点 W208 未落链）→"
               "**轮中竞速实录**：bm-b r865 双 commit 落 origin（N2-W20 slice-1+HANDOVER 5x）→absorb-2 dd35875a4→rebase 14-UU 同窗 S6 再导出面族="
               "_r856bmc_rebase_resolver.py（10 面 ts-audited theirs-newer〔06:34-06:39>我方 06:33-06:35〕+3 面 md twin-follows json+compute_audit history ts-key UNION 201/201→201 latest-base=ours）→"
               "rebase --continue 干净→HEAD b2d50e1a4；W208 仍未落链（bm-b 两 commit=N2 族·bm-a 续暗 ~9h）·M10 守望不变；"
               "②S0.5 常设组合器=ORD 24ad1708/DEC 68d13893 双哈希恒等零新行+unacked 0+inbox 1 件消费（MSG-20261011-0628 bm-b N2-W20 draft 声明·车道 bm-b·撞头探针 CLEAR·bm-c 零动作·移 processed）；"
               "③S1 smoke 49/49·S2 双板空（job 0/open 票 0·49 全 claimed）·satengine 活 rc0（queue_next=[]/burns=[]）；"
               "④守望面一行声明=W208 未落链+MSG-0535 无应答+M10 cron 9defca39 armed（cron_list 验证）+jman 21288 活 CPU 42.7h ETA ~08:37-09:00 不变；"
               "⑤PRODUCT-A=S6 43/43 rc0（_r856bmc_s6_chain.ps1 r855 verbatim clone·DONE 06:36:42·dualrun ZERO-DRIFT streak 31→32·update_daily 周日 0 新行 cutoff 2026-10-09 合法·compute_audit 三旗=已知定谳面照录〔gpu_unauthorized=jman CEO-MV·pool_starvation/supply_floor=W208 链堵〕）；"
               "⑥PRODUCT-B=QA charter 包 5/5（qa/smoke-r856-bm-c.md+equity-curve-r856-bm-c.png 65,434B：3sym×800bar 91 trades determinism=True sharpe 0.1994 win_rate 0.4725 maxdd -0.0431 equity final 1,023,027·信号 CALL rc0 cell=ORA·面板 bar 2026-10-09）；"
               "⑦S7 attrition 4 台账 CLEAN（3 healed 史披露）+四件套绿（loop pin=5 no-op 首火 06:45/watchdog 重装首火 06:41/双爪 LF 归一 installed）+idle --worked（idle_rounds=0） | "
               "r857: (1) W208 落链守望→M10 自动执行链（freeze→selftest→pathspec push→2-cycle n1_w209 点火→MSG 回执+翻 M10+删 cron 9defca39）·MSG-0535 应答观察（yield→r578 六步收养·GM 改派随令即执行）；"
               "(2) jman 完训窗 ~08:37-09:00 三件（val_grid+LOOKBOARD_variant_640+恢复债三件 per O-20261010-0025·≤48h SLA）；(3) W211 freeze-prep（W210 近时先读 pit-engine-finalize.md）；"
               "(4) S0.5 常设组合器 | 本轮产品积分：2（S6 43 面再生+QA 证据包 5/5=经营层实物） | 记账预算：3 面内（state+心跳+轮报=法定簿记）")

# round report: read tail first (anchor law), assert r855 addendum tail, single append
with io.open(CANON, "r", encoding="utf-8") as f:
    can_body = f.read()
can_lines = [l for l in can_body.splitlines() if l.strip()]
assert "r855 bm-c addendum" in can_lines[-1], ("canonical tail not r855 addendum", can_lines[-1][:80])
assert ("| r856 |" not in can_body[-6000:]), "r856 main line already present"
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
    d["round_no"] = 857
    d["round_no_label"] = "r856"
    d["last_round"] = 856
    d["loop_round"] = 856
    d["heartbeat_epoch_utc"] = epoch
    d["cpu_pct"] = 23; d["cpu_util_pct"] = 23; d["cpu_idle_pct"] = 77
    d["free_ram_gb"] = 1.2; d["idle_ram_gb"] = 1.2; d["ram_free_gb"] = 1.2
    for k in ["gpu_free_vram_mb","gpu_free_vram_mib","gpu_idle_vram_mb","gpu_idle_vram_mib","gpu_vram_free_mb","gpu_free_mb","gpu_free_mib","gpu_idle_mib"]:
        if k in d: d[k] = 103
    d["gpu_idle_mb"] = 16281
    d["head_sha"] = "b2d50e1a4"
    d["current_task"] = activity
    d["activity_now"] = activity
    d["did"] = did
    d["verdict"] = verdict
    d["last_round_summary"] = summary
    d["note"] = ("r856 = watch round: W208 no-answer holds (MSG-0535 live), mid-round bm-b r865 race resolved "
                 "14-UU ts-audited; S6 43/43 streak 32; QA 5/5; jman 42.7h ETA ~08:37-09:00.")
    d["next"] = next_ptr
    d["next_pointer"] = next_ptr
    d["next_milestone"] = ("r857: W209 freeze on W208 landing/yield/GM-redispatch (M10 auto-execute, cron armed) "
                           "+ jman completion window ~08:37-09:00 (val_grid + LOOKBOARD_variant_640 + "
                           "recovery-debt trio) <=48h SLA")
    d["latest_artifact"] = ("S6 43-leg chain rc0 streak 32 + QA pack r856 5/5 (qa/smoke-r856-bm-c.md + "
                            "equity-curve-r856-bm-c.png) + 14-UU mid-round rebase race resolved ts-audited")
    d["last_artifact"] = d["latest_artifact"]
    d["recent_artifact"] = d["latest_artifact"]
    d["last_action"] = "r856 W208 watch + S6 43-leg chain (streak 32) + QA pack 5/5 + mid-round rebase race closeout + books"
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 1
    d["orphan_faces"] = 1
    d["health"] = "ok"
    d["verify"] = ("receipts: smoke 49/49 + qa/smoke-r856-bm-c.md (5/5 charter) + results/_r856bmc_s6_log.txt "
                   "(43/43 rc0 streak 32, DONE 06:36:42) + attrition CLEAN (4 ledgers) + quartet green + "
                   "idle --worked + 14-UU resolver receipt (resolver stdout in session log) + this books "
                   "commit/push_verify")
    if not is_hb:
        d["sync"] = {"ahead_behind": "0/0 pre-books", "origin_tip": "161bd57c2", "ts": now_iso,
                     "note": "r856 books: watch round + S6/QA products + mid-round race closeout; books commit follows this write"}
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
    assert d["round_no"] == 857, p
    assert d["loop_round"] == 856, p

print("BOOKS OK round_no=857(label r856) epoch=%d clock=%s report_line_appended=1" % (epoch, now_iso))
