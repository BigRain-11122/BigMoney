"""r718 bm-c close-out: state round_no bump, round-report line append,
heartbeat refresh (three-line face per P-2026-09-29-07 #5, epoch int
self-check per R170/R178, clock_read T-separator per R262).
Pattern credit: Tools/_r717bmc_close.py (canonical)."""
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")  # T-separated, +08:00 offset


def fresh_metrics():
    m = {"cpu_pct": None, "ram_free_gb": None, "gpu_free_mb": None}
    try:
        import psutil
        m["cpu_pct"] = round(psutil.cpu_percent(interval=1.0), 1)
        vm = psutil.virtual_memory()
        m["ram_free_gb"] = round(vm.available / (1024 ** 3), 1)
    except Exception:
        pass
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=20)
        m["gpu_free_mb"] = int(r.stdout.strip().splitlines()[0])
    except Exception:
        pass
    return m


def main():
    m = fresh_metrics()

    # --- 1) state-bm-c.json round_no bump 718 -> 719
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 719
    json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # --- 2) round report line
    line_ts = TS
    rpt = (
        f"{line_ts} | r718 | dept:工程（复市 T-0 盘前值守轮·第 38 bm-c 连守轮·S6 40 腿合流轮） | "
        "WM-VERDICT: 绿（red=false lane healthy·py_low_board_clear=板空+盘前无 bar 合法 idle 白名单"
        "〔板 0 open/176 ack/池 406 全 done〕·compute_audit 旗标 supply_floor 照录=池 ready 0<floor 3"
        "·处置在册=引擎常供线 W181+ 投影+今晚盘后 bar 面天然候选供给+W16 波起草泊位 bm-a T-172"
        "〔never-dry 常设律·禁手工代烧〕） | "
        "当前活: r718 S6 驱动器 zt_pool 腿合流轮（r717 指针项 (g) 交付）——主产出="
        "①Tools/_r718bmc_s6.py 40 腿驱动器（r717 39 腿版+zt_pool 腿按令链序插入"
        " update_lhb→update_zt_pool→update_heat·bm-c 面 R31 实证「no-op: zt_pool lane owned by bm-a, "
        "not this machine (bm-c)」诚实 stdout-only no-op·40/40 rc0·dualrun ZERO-DRIFT streak 38）"
        "②QA 38th 确定性包 qa/smoke-r718.md 5/5+qa/equity-curve-r718.png 66,281B"
        "（determinism=True·93 trades·equity 1,017,839 冻结恒等·market_clock rc0 cell=ORA"
        "·latest_panel_bar 2026-09-30 金周合法）③scripts/qa_smoke_run.py 证据行修复"
        "（「S6 38-leg chain」硬编码陈旧串→leg-count-neutral「S6 chain」零漂移面·编译过+r718 pack 同窗再生验证"
        "=证据文本与实况恒等）④S0 双 commit own-churn absorb（e2e761e9b 1 面+9300a0c36 5 面"
        "=首 add typo pathspec 原子败诚实分跳补齐） | "
        "smoke 49/49 · S6 40/40 rc0（zt_pool 腿本机 no-op 等价·cta_p1_paper bar-门控诚实 no-op"
        "〔panel cutoff 2026-09-30<paper_start 2026-10-08→今晚首 bar 轮自动接线〕"
        "·fund_premium pre-15:30 no-op→今日 15:30 bm-c 车道首采） · "
        "QA 5/5（determinism=True 38th·runner .err 0B） · "
        "orders 双扫 unacked=0（51 disk/176 ack·S0.5 首扫零差+S7 收尾二扫同验） · "
        "DEC/ORD 双水位 UNCHANGED（EE659451/17accc40·算法对按 r716 钉〔DEC=SHA-256/ORD=SHA-1〕） · "
        "SAT 活 rc0（burns 0·队列空） · 板 0 open·job_list 0·backlog 2 可领=非本司域（游戏线）不领 · "
        "idle NOT-GREEN（RAM ~15-19%<40% 常驻 ComfyUI·idle_rounds=0·--worked 申报） · "
        "post_review 零红承接（REPORT-20261008 45✓/0✗/5🟡） · 孤儿面=1（本机常驻 ComfyUI 服务面"
        "·只读披露不击杀·既有处置维持） · attrition CLEAN（4 healed 注记照录） · "
        "自愈=loop pin=5 no-op+watchdog 重注册+双爪 IN-PLACE match（CR 归一比对 True/True） · "
        "token 面=L1 零 token 腿（token_meter rc0·L2 今日 0 腿） · "
        "方法论捕获=无新方法（纯复用范式：驱动器克隆+leg 插槽）·宝藏捕获=N/A（无五类收口批）"
        "·登记册零命中断言=N/A（无清扫/归档/恢复类动作） · "
        "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
        "下轮 r719：(a) 值守续（今日 09:15 复市首交易日·intraday marks 车道起活·盘前零盲动） "
        "(b) 今晚盘后面=数据链全门 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采（bm-c 车）"
        "+QDII watch 重跑长假差分+CTA_P1 首 bar 自动接线+首 marks 验证（≤今夜） "
        "(c) O-2215 ① 矩阵规格件+切换律 v1（≤10-16 12:00·待 bm-a REGIME-5 ≤10-14+bm-b 五态路由 spec 面） "
        "(d) O-2245 续作=首批 OSS- 落池件先过 Tools/oss_import_gate.py rc0 再 settle（bm-a ≤10-16） "
        "(e) cloudF 行收取窗 ≤10-14 常设 (f) 月界首考 10-31 | "
        "轮产品计分：2（40 腿驱动器+QA 38th 包+qa 证据行修复=能跑能看实物；值守窗零新产品线如实） | "
        "记账预算：3（state+心跳+轮报） [via bm-c r718]"
    )
    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    with open(rp, "a", encoding="utf-8", newline="") as f:
        f.write(rpt + "\n")

    # --- 3) heartbeat
    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    hb = json.load(open(hp, encoding="utf-8"))
    epoch = int(time.time())
    cpu = m["cpu_pct"] if m["cpu_pct"] is not None else hb.get("cpu_pct", 0.0)
    ram = m["ram_free_gb"] if m["ram_free_gb"] is not None else hb.get("free_ram_gb", 0.0)
    gpu = m["gpu_free_mb"] if m["gpu_free_mb"] is not None else hb.get("gpu_free_vram_mb", 0)
    current_task = (
        "当前活: r718 bm-c S6 40 腿合流轮（zt_pool 腿 r717 指针项 (g) 交付·40/40 rc0·复市 T-0 盘前值守"
        "第 38 连守轮·盘前零盲动） | "
        f"最近实物: Tools/_r718bmc_s6.py（40 腿驱动器）+ results/_r718bmc_s6_log.txt（40 legs rc0"
        f"·dualrun streak 38）+ qa/smoke-r718.md 5/5（det 38th） @ {TS} | "
        "下个里程碑: 今晚盘后（10-08 15:30+）数据链全门 re-arm+REGIME_GUARD v3 新 bar enforce"
        "+fund_premium 首采（bm-c 车）+QDII watch 长假差分重跑+CTA_P1 首 bar 自动接线+首 marks 验证"
        "（≤10-08 23:59）；09:15 起值守 intraday 面"
    )
    latest_artifact = (
        "Tools/_r718bmc_s6.py (40-leg S6 driver, zt_pool merged per mandate chain order) + "
        "results/_r718bmc_s6_log.txt (40 legs rc0, dualrun streak 38) + qa/smoke-r718.md 5/5 "
        "(determinism 38th, 93 trades, equity 1,017,839 frozen identity, png 66,281B) "
        "@ " + TS
    )
    verdict = (
        "r718 bm-c: S6 40-leg merge round + pre-open watch (38th consecutive, 10-08 reopen T-0, "
        "02:3x pre-open window, zero blind action). Product = Tools/_r718bmc_s6.py 40-leg driver "
        "(r717 pointer item (g): update_zt_pool leg inserted per mandate chain order update_lhb -> "
        "zt_pool -> update_heat; bm-c face = R31 honest stdout-only no-op verified in log; 40/40 "
        "rc0; dualrun ZERO-DRIFT streak 38) + QA 38th determinism pack (5/5, 93 trades, equity "
        "1,017,839 frozen identity, png 66,281B, runner .err 0B) + scripts/qa_smoke_run.py evidence-"
        "line fix (stale hardcoded 'S6 38-leg chain' -> leg-count-neutral 'S6 chain', compile-checked, "
        "r718 pack regenerated same-window to verify evidence text == reality). S0: behind=0 clean "
        "window, 6-face own-churn absorb via 2 commits (e2e761e9b + 9300a0c36; first add typo "
        "pathspec atomic-fail honestly split-restaged). Both watermarks UNCHANGED (EE659451/"
        "17accc40, algorithm pair per r716 pin); orders unacked=0 both sweeps; SAT alive rc0; "
        "board 0 open; not green-idle (RAM resident ComfyUI), idle_rounds=0 worked-declared; "
        "post_review zero red (45/0/5); orphan face=1 (resident ComfyUI, no-kill standing "
        "disposition); attrition CLEAN (4 healed noted); self-heal = loop pin=5 no-op + watchdog "
        "re-registered + both claws IN-PLACE (CR-normalized True/True); token L1 zero-token legs."
    )
    did = (
        "r718 bm-c: S6 zt_pool-leg merge + QA 38th pack (10-08 reopen T-0, 38th consecutive "
        "watch round, 02:3x pre-open window). (1) S0: fetch behind=0 clean; 6 own-churn daemon "
        "faces absorbed in 2 commits (e2e761e9b 1-face + 9300a0c36 5-face; first git add typo "
        "pathspec failed atomically -> remainder restaged honestly, zero loss); push delivered. "
        "(2) S0.5 sweeps 1+2: orders 51 disk/176 ack unacked=0 both; DEC EE659451 / ORD 17accc40 "
        "both UNCHANGED (SHA-256/SHA-1 pair per r716 pin, hex-case normalized per r711; facts "
        "results/_r718bmc_s05_facts.json, shape-asserted). (3) S1 smoke 49/49. (4) S3: satengine "
        "rc0 alive (burns 0, queue empty); watermark green (py_low_board_clear legal idle "
        "whitelist); board 0 open; backlog claimables = non-BigMoney domains, not claimed; idle "
        "NOT-GREEN (RAM 15.3% resident), idle_rounds=0, --worked declared. (5) MAIN PRODUCT: "
        "Tools/_r718bmc_s6.py = r717 39-leg canonical + update_zt_pool leg inserted at mandate "
        "chain position (between update_lhb and update_heat); run 40/40 rc0; zt_pool leg honest "
        "no-op verified ('no-op: zt_pool lane owned by bm-a, not this machine (bm-c)'); dualrun "
        "ZERO-DRIFT streak 38; cta_p1_paper bar-gated no-op (auto-fires tonight first-bar); "
        "fund_premium pre-15:30 no-op -> today 15:30 bm-c-lane first snapshot; compute_audit "
        "flags supply_floor recorded with standing disposition. (6) QA 38th pack: first via "
        "detached runner (Tools/_r718bmc_qa_ignite.py --round 718) 5/5; then scripts/qa_smoke_run."
        "py evidence-line fix (stale 'S6 38-leg chain' hardcoded string -> leg-count-neutral 'S6 "
        "chain'; py_compile OK) and same-window pack regeneration to keep evidence text == "
        "reality (5/5 again, determinism=True, equity 1,017,839 identity, png 66,281B). "
        "(7) post_review zero red (45Y/0N/5WAIT); orphan face=1 no-kill documented; attrition "
        "CLEAN (4 healed noted); self-heal = loop pin=5 no-op + watchdog re-registered + both "
        "claws IN-PLACE match; token L1 zero-token legs. (8) Product score 2 (runnable 40-leg "
        "driver + QA pack + shared-script honesty fix)."
    )
    nxt = (
        "r719: (a) watch continuation: today 09:15 reopen first trading day, intraday marks lane "
        "live, pre-open zero blind action until 09:15; (b) tonight post-close face (<=10-08 "
        "23:59): data-chain full re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium "
        "15:30 first snapshot (bm-c lane) + QDII watch rerun holiday-delta + CTA_P1 first-bar "
        "auto-wiring + first-marks verification (S6 cta_p1_paper leg; verify = marks 1 row + "
        "state trial-live + compounding identity); (c) O-2215 deliverable (1) matrix spec + "
        "switching law v1 (<=10-16 12:00; consumes bm-a REGIME-5 discriminator <=10-14 + bm-b "
        "five-state router spec); (d) O-2245 follow-ups: first OSS- enrollments (bm-a "
        "strategy-class adaptations <=10-16) must pass Tools/oss_import_gate.py rc0 before "
        "settle; (e) cloudF row weekly rerun supply (window <=10-14, standing); (f) "
        "month-boundary first exam 10-31. [via bm-c r718]"
    )
    hb.update({
        "idle_rounds": 0, "agenda_starved": False,
        "heartbeat_epoch_utc": epoch,
        "last_seen": TS, "clock_read": TS, "ts": TS,
        "cpu_pct": cpu, "cpu_util_pct": cpu, "cpu_idle_pct": round(100 - cpu, 1) if cpu is not None else None,
        "free_ram_gb": ram, "idle_ram_gb": ram, "ram_free_gb": ram,
        "gpu_free_vram_mb": gpu, "gpu_idle_vram_mb": gpu, "gpu_vram_free_mb": gpu,
        "gpu_free_mb": gpu, "gpu_idle_mb": gpu, "gpu_free_mib": gpu,
        "gpu_idle_vram_mib": gpu, "gpu_idle_mib": gpu,
        "round_no": 719, "round_no_label": "round 718 (bm-c)",
        "last_round": 718, "last_round_at": TS,
        "current_task": current_task, "current_task_at": TS,
        "latest_artifact": latest_artifact,
        "next_milestone": (
            "今晚盘后: data-chain re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium "
            "15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verify "
            "(<= 10-08 23:59); 09:15 起值守 intraday 面"
        ),
        "health": "ok",
        "activity_now": verdict, "did": did, "verdict": verdict,
        "note": ("r718: S6 40-leg zt_pool merge + QA det-38th 5/5 + qa evidence-line fix; "
                 "S6 40 rc0 streak 38; both watermarks unchanged; orders unacked=0; smoke 49/49."),
        "last_round_summary": ("r718: S6 40-leg merge (zt_pool) + QA det-38th 5/5 + qa evidence fix; "
                              "watermarks unchanged; unacked=0; smoke 49/49; post_review zero red."),
        "last_action": ("r718: S6 40-leg merge (zt_pool) + QA det-38th 5/5 + qa evidence fix; "
                        "watermarks unchanged; unacked=0; smoke 49/49; post_review zero red."),
        "next": nxt,
        "last_seen_at": TS, "updated_at": TS, "updated": TS,
        "last_run_at": TS, "last_ts": TS,
    })
    json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    chk = json.load(open(hp, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in chk["clock_read"], "clock_read must be T-separated"
    print("close-out done:", TS, "| cpu", cpu, "| ram_free", ram, "| gpu_free", gpu,
          "| epoch int OK | state round_no -> 719 | report line appended | heartbeat written")


if __name__ == "__main__":
    main()
