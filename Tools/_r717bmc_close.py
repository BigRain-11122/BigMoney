"""r717 bm-c close-out: state round_no bump, round-report line append,
heartbeat refresh (three-line face per P-2026-09-29-07 #5, epoch int
self-check per R170/R178, clock_read T-separator per R262).
Pattern credit: Tools/_r716bmc_close.py (canonical)."""
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

    # --- 1) state-bm-c.json round_no bump 717 -> 718
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 718
    json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # --- 2) round report line
    line_ts = TS
    rpt = (
        f"{line_ts} | r717 | dept:工程（复市 T-0 盘前值守轮·第 37 bm-c 连守轮·值守+QA 复验轮） | "
        "WM-VERDICT: 绿（red=false lane healthy·py_low_board_clear=板空+盘前无 bar 合法 idle 白名单"
        "〔板 0 open/176 ack/池 406 全 done〕·compute_audit 旗标 pool_starvation+supply_floor 照录"
        "=池 ready 0<floor 3·处置在册=引擎常供线 W181+ 投影+今晚盘后 bar 面天然候选供给"
        "+W16 波起草泊位 bm-a T-172〔never-dry 常设律·禁手工代烧〕） | "
        "当前活: r717 值守+QA 复验轮（盘前零盲动）——主产出=①QA 37th 确定性包"
        "qa/smoke-r717.md 5/5+qa/equity-curve-r717.png 66,110B（determinism=True·93 trades"
        "·equity 1,017,839 冻结恒等·market_clock rc0 cell=ORA·latest_panel_bar 2026-09-30 金周合法）"
        "②S6 39 腿驱动器 Tools/_r717bmc_s6.py（39/39 rc0·dualrun ZERO-DRIFT streak 37"
        "·cta_p1_paper bar-门控诚实 no-op〔panel cutoff 2026-09-30<paper_start 2026-10-08"
        "→今晚首 bar 轮自动接线〕·fund_premium pre-15:30 no-op→今日 15:30 bm-c 车道首采）"
        "③S0 干净窗=7-face own-churn absorb（88c46ca30 post-rebase）+净树 rebase zero conflict"
        "（吸收 bm-a r856 双commit=zt_pool 4-face gate+S6 链槽+S5-01 GO 面） | "
        "smoke 49/49（他机 r856 增腿 zt_pool selftest 48→49·0 FAIL） · "
        "S6 39/39 rc0（r716 版驱动器·bm-a r856 新增 zt_pool 腿=bm-a 车道 R31〔本机 no-op 等价〕"
        "·r718 驱动器合流 40 腿） · QA 5/5（determinism=True 37th） · "
        "orders 双扫 unacked=0（51 disk/176 ack·S0.5 首扫零差+S7 收尾二扫同验） · "
        "DEC/ORD 双水位 UNCHANGED（EE659451/17accc40·算法对按 r716 钉〔DEC=SHA-256/ORD=SHA-1〕） · "
        "SAT 活 rc0（burns 0·队列空） · 板 0 open·job_list 0·backlog 2 可领=非本司域（游戏线）不领 · "
        "idle NOT-GREEN（RAM 16.9%<40% 常驻 ComfyUI·idle_rounds=0·--worked 申报） · "
        "post_review 零红承接（今日 149 行 0 红） · 孤儿面=1（本机常驻 ComfyUI 服务面·只读披露不击杀"
        "·既有处置维持） · attrition CLEAN（4 healed 注记照录） · "
        "自愈=loop pin=5 no-op+watchdog 重注册+双爪重装（LF-normalized） · "
        "token 面=L1 零 token 腿（token_meter rc0） · 方法论捕获=无新方法（纯值守复用）·"
        "宝藏捕获=N/A（无五类收口批）·登记册零命中断言=N/A（无清扫/归档/恢复类动作） · "
        "本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证） | "
        "下轮 r718：(a) 值守续（今日 09:15 复市首交易日·intraday marks 车道起活·盘前零盲动） "
        "(b) 今晚盘后面=数据链全门 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采（bm-c 车）"
        "+QDII watch 重跑长假差分+CTA_P1 首 bar 自动接线+首 marks 验证（≤今夜） "
        "(c) O-2215 ① 矩阵规格件+切换律 v1（≤10-16 12:00·待 bm-a REGIME-5 ≤10-14+bm-b 五态路由 spec 面） "
        "(d) O-2245 续作=首批 OSS- 落池件先过 Tools/oss_import_gate.py rc0 再 settle（bm-a ≤10-16） "
        "(e) cloudF 行收取窗 ≤10-14 常设 (f) 月界首考 10-31 (g) S6 驱动器合流 zt_pool 腿（40 腿·bm-c 面=stdout-only no-op） | "
        "轮产品计分：2（QA 确定性包=能跑能看实物+S6 再生面；零新产品线〔盘前值守如实〕） | "
        "记账预算：3（state+心跳+轮报） [via bm-c r717]"
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
        "当前活: r717 bm-c 值守+QA 复验轮（复市 T-0 盘前·37th 连守·盘前零盲动） | "
        f"最近实物: qa/smoke-r717.md 5/5 + qa/equity-curve-r717.png 66,110B（determinism=True 37th·"
        "93 trades·equity 1,017,839 冻结恒等）+ results/_r717bmc_s6_log.txt（39 legs rc0·dualrun streak 37）"
        f" @ {TS} | "
        "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce"
        "+fund_premium 15:30 首采（bm-c 车）+CTA_P1 首 bar 接线+首 marks 验证（≤10-08 23:59）；"
        "09:15 起值守 intraday 面"
    )
    latest_artifact = (
        "qa/smoke-r717.md 5/5 + qa/equity-curve-r717.png 66,110B (determinism=True 37th, 93 trades, "
        "equity 1,017,839 frozen identity) + results/_r717bmc_s6_log.txt (39 legs rc0, dualrun streak 37) "
        "@ " + TS
    )
    verdict = (
        "r717 bm-c: pre-open holding round + QA 37th determinism pack clean (5/5, equity 1,017,839 "
        "frozen identity, png 66,110B, market_clock rc0). S6 39/39 rc0 (r716-canon driver; bm-a r856 "
        "new zt_pool leg = bm-a lane, bm-c no-op equivalent, r718 driver merges 40); dualrun "
        "ZERO-DRIFT streak 37; cta_p1_paper honest bar-gated no-op (auto-fires tonight first-bar); "
        "fund_premium pre-15:30 no-op -> today 15:30 bm-c-lane first snapshot. S0: 7-face own-churn "
        "absorb (88c46ca30) + clean rebase absorbing bm-a r856 twin commits; both watermarks "
        "UNCHANGED (EE659451/17accc40, algorithm pair per r716 pin); orders unacked=0 both sweeps; "
        "SAT alive rc0; board 0 open; not green-idle (RAM resident ComfyUI), idle_rounds=0 "
        "worked-declared; post_review zero red (149 rows today); orphan face=1 (resident ComfyUI, "
        "no-kill standing disposition); attrition CLEAN (4 healed noted); self-heal = loop pin=5 "
        "no-op + watchdog re-registered + both claws reinstalled (LF-normalized); token L1 "
        "zero-token legs."
    )
    did = (
        "r717 bm-c: pre-open holding round + QA re-verification (10-08 reopen T-0, 37th consecutive "
        "bm-c watch round, 02:2x pre-open window, zero blind action). (1) S0: 7-face own-churn absorb "
        "(88c46ca30 post-rebase: orphan probe + dispatcher/idle/satengine runtime faces + r717 probes) "
        "-> clean rebase zero conflict absorbing bm-a r856 twin commits (rebase resolver helpers + "
        "zt_pool 4-face collector gate + smoke 49th leg) -> behind=0 pre-round. (2) S0.5 sweeps 1+2: "
        "orders 51 disk/176 ack unacked=0 both sweeps; DEC EE659451 / ORD 17accc40 both UNCHANGED "
        "(algorithm pair SHA-256/SHA-1 per r716 pin, hex-case normalized per r711 law; facts "
        "results/_r717bmc_s05_facts.json, shape-asserted). (3) S1 smoke 49/49 (48->49 = bm-a r856 "
        "zt_pool selftest leg, 0 FAIL). (4) S3: satengine rc0 alive (burns 0, queue empty); watermark "
        "green (py_low_board_clear legal idle whitelist); board 0 open (job_list 0 + fleet nondone "
        "all others' claimed faces); backlog claimables = non-BigMoney domains + NOT green-idle -> "
        "no claim; idle_rounds=0 worked-declared. (5) S6 39/39 rc0 (Tools/_r717bmc_s6.py, r716-canon "
        "copy; dualrun ZERO-DRIFT streak 37; cta_p1_paper honest bar-gated no-op panel cutoff "
        "2026-09-30 < paper_start 2026-10-08 -> auto-fires tonight first-bar round; fund_premium "
        "pre-15:30 no-op -> today 15:30 bm-c-lane first snapshot; py_watermark verdict="
        "py_low_board_clear; compute_audit flags pool_starvation+supply_floor recorded with "
        "standing disposition per r715/r716). (6) QA 37th determinism pack via detached runner "
        "(Tools/_r717bmc_qa_ignite.py -> scripts/qa_smoke_run.py --round 717): 5/5 -- full backtest "
        "93 trades determinism=True, equity final 1,017,839 frozen identity, sharpe 0.1586, png "
        "66,110B, market_clock_call rc0 (cell=ORA, idempotent same-day), latest_panel_bar 2026-09-30 "
        "golden-week legal until 10-08; runner .err zero bytes. (7) post_review zero red (149 rows "
        "today, 0 cross); orphan face=1 (resident ComfyUI server face, read-only no-kill, standing "
        "disposition); attrition CLEAN (4 healed noted); self-heal = loop pin=5 no-op + watchdog "
        "re-registered + both claws reinstalled (LF-normalized); token L1 zero-token legs "
        "(token_meter rc0). (8) Product score 2 (QA determinism pack = runnable/viewable artifact + "
        "S6 regen faces; zero new product line, pre-open holding honest)."
    )
    nxt = (
        "r718: (a) watch continuation: today 09:15 reopen first trading day, intraday marks lane "
        "live, pre-open zero blind action until 09:15; (b) tonight post-close face (<=10-08 23:59): "
        "data-chain full re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium 15:30 first "
        "snapshot (bm-c lane) + QDII watch rerun holiday-delta + CTA_P1 first-bar auto-wiring + "
        "first-marks verification (S6 cta_p1_paper leg; verify = marks 1 row + state trial-live + "
        "compounding identity); (c) S6 driver merge zt_pool leg (40 legs, bm-c face = stdout-only "
        "no-op per R31); (d) O-2215 deliverable (1) matrix spec + switching law v1 (<=10-16 12:00; "
        "consumes bm-a REGIME-5 discriminator <=10-14 + bm-b five-state router spec); (e) O-2245 "
        "follow-ups: first OSS- enrollments (bm-a strategy-class adaptations <=10-16) must pass "
        "Tools/oss_import_gate.py rc0 before settle; (f) cloudF row weekly rerun supply (window "
        "<=10-14, standing); (g) month-boundary first exam 10-31. [via bm-c r717]"
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
        "round_no": 718, "round_no_label": "round 717 (bm-c)",
        "last_round": 717, "last_round_at": TS,
        "current_task": current_task, "current_task_at": TS,
        "latest_artifact": latest_artifact,
        "next_milestone": (
            "今晚盘后: data-chain re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium 15:30 "
            "first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verify "
            "(<= 10-08 23:59); 09:15 起值守 intraday 面"
        ),
        "health": "ok",
        "activity_now": verdict, "did": did, "verdict": verdict,
        "note": ("r717: holding round + QA 37th determinism pack (5/5, equity 1,017,839 identity); "
                 "S6 39 rc0 streak 37; both watermarks unchanged; orders unacked=0; smoke 49/49."),
        "last_round_summary": ("r717: holding round + QA det-37th 5/5 + S6 39 rc0 streak 37; "
                              "watermarks unchanged; unacked=0; smoke 49/49; post_review zero red."),
        "last_action": ("r717: holding round + QA det-37th 5/5 + S6 39 rc0 streak 37; "
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
          "| epoch int OK | state round_no -> 718 | report line appended | heartbeat written")


if __name__ == "__main__":
    main()
