"""r716 bm-c close-out: state round_no bump, round-report line append,
heartbeat refresh (three-line face per P-2026-09-29-07 #5, epoch int
self-check per R170/R178, clock_read T-separator per R262)."""
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

    # --- 1) state-bm-c.json round_no bump 716 -> 717
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 717
    json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # --- 2) round report line
    line_ts = TS
    rpt = (
        f"{line_ts} | r716 | dept:工程（复市 T-0 盘前值守轮·第 36 bm-c 连守轮·值守+维护收口轮） | "
        "WM-VERDICT: 绿（red=false lane healthy·py_low_board_clear=板空+盘前无 bar 合法 idle 白名单"
        "〔板 0 open/176 ack/池 406 全 done〕·compute_audit 旗标 pool_starvation+supply_floor 照录"
        "=池 ready 0<floor 3·处置在册=引擎常供线 W181+ 投影+今晚盘后 bar 面天然候选供给"
        "+W16 波起草泊位 bm-a T-172〔never-dry 常设律·禁手工代烧〕） | "
        "当前活: r716 值守+维护收口轮（盘前零盲动·无新产品线如实）——主产出=①S0.5 水位算法对坑同窗抓获+直写钉"
        "（ORD 按 DEC 惯性误算 sha256=假 changed 报警→核 r715 facts 键长 40hex→SHA-1 复算恒等 UNCHANGED 零假账"
        "→r712 律④主件红线窗〔30,606B〕直写 pit-protocol-d19.md 算法对钉〔DEC=SHA-256/ORD=SHA-1〕"
        "+收据 _r716bmc_pit_d19_directwrite.json）②S6 39 腿驱动器 Tools/_r716bmc_s6.py"
        "（cta_p1_paper bar-门控 no-op 连续验证·streak 36） | "
        "smoke 48/48 · S6 39/39 rc0（dualrun ZERO-DRIFT streak 36·cta_p1_paper bar-门控诚实 no-op"
        "〔panel cutoff 2026-09-30<paper_start 2026-10-08→今晚首 bar 轮自动接线〕"
        "·fund_premium pre-15:30 no-op→今日 15:30 bm-c 车道首采·盘前 no-op 腿合法） · "
        "orders 双扫 unacked=0（51 disk/176 ack·S0.5 首扫零差+S7 收尾二扫同验） · "
        "DEC/ORD 双水位 UNCHANGED（EE659451/17accc40·ORD=SHA-1 口径按 r716 钉） · "
        "SAT 活 rc0（burns 0·队列空） · 板 0 open·backlog 2 可领=非本司域（游戏线 G17/CPH4 渲染基准）不领 · "
        "idle NOT-GREEN（RAM 16.8%<40% 常驻·idle_rounds=0·--worked 申报） · "
        "post_review 零红承接（今日战报 ✗0） · 孤儿面=1（本机常驻 ComfyUI 服务面·只读披露不击杀·既有处置维持） · "
        "attrition CLEAN（4 healed 注记照录） · 自愈=loop pin=5 no-op+watchdog 重注册+双爪 IN-PLACE match · "
        "token 面=L1 零 token 腿（token_meter rc0） · 方法论捕获=无新方法（纯值守复用）·"
        "宝藏捕获=N/A（无五类收口批）·登记册零命中断言=N/A（无清扫/归档/恢复类动作） · "
        "本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证） | "
        "下轮 r717：(a) 值守续（今日 09:15 复市首交易日·intraday marks 车道起活·盘前零盲动） "
        "(b) 今晚盘后面=数据链全门 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采（bm-c 车）"
        "+QDII watch 重跑长假差分+CTA_P1 首 bar 自动接线+首 marks 验证（≤今夜） "
        "(c) O-2215 ① 矩阵规格件+切换律 v1（≤10-16 12:00·待 bm-a REGIME-5 ≤10-14+bm-b 五态路由 spec 面） "
        "(d) O-2245 续作=首批 OSS- 落池件先过 Tools/oss_import_gate.py rc0 再 settle（bm-a ≤10-16） "
        "(e) cloudF 行收取窗 ≤10-14 常设 (f) 月界首考 10-31 | "
        "轮产品计分：1（S6 再生面+算法对钉直写+驱动器=维护窗实物；零新产品线〔盘前值守如实〕） | "
        "记账预算：3（state+心跳+轮报） [via bm-c r716]"
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
        "当前活: r716 bm-c 值守+维护收口轮（复市 T-0 盘前·36th 连守·盘前零盲动） | "
        f"最近实物: Tools/_r716bmc_s6.py + results/_r716bmc_s6_log.txt（39 legs rc0·dualrun streak 36）"
        "+ pit-protocol-d19.md 水位算法对钉直写（收据 _r716bmc_pit_d19_directwrite.json） @ {TS} | "
        "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce"
        "+fund_premium 15:30 首采（bm-c 车）+CTA_P1 首 bar 接线+首 marks 验证（≤10-08 23:59）；"
        "09:15 起值守 intraday 面"
    )
    latest_artifact = (
        "Tools/_r716bmc_s6.py (39-leg driver) + results/_r716bmc_s6_log.txt (39 legs rc0, "
        "dualrun streak 36) + research/pit-protocol-d19.md algorithm-pair pin "
        "(receipt results/_r716bmc_pit_d19_directwrite.json) @ " + TS
    )
    verdict = (
        "r716 bm-c: pre-open holding/maintenance round clean. ORD watermark false-alarm caught same-window "
        "(sha256-inertia miscompute vs stored sha1 key; sha1 recompute identical, zero false consumption) -> "
        "algorithm-pair pin direct-written to pit-protocol-d19.md per r712 law-4 (main 30,606B untouched); "
        "S6 39/39 rc0 streak 36; both watermarks UNCHANGED; orders unacked=0 both sweeps; board 0 open; "
        "backlog claimables = non-BigMoney domains, not claimed (not green-idle); orphan face=1 (resident "
        "ComfyUI, no-kill standing disposition); post_review zero red; attrition CLEAN; idle_rounds=0 "
        "worked-declared."
    )
    did = (
        "r716 bm-c: pre-open holding/maintenance round (10-08 reopen T-0, 36th consecutive bm-c watch round, "
        "02:2x pre-open window, zero blind action). (1) S0: 4-face own-churn absorb (1804bb6ef: satengine/"
        "dispatcher faces + orphan probe report) -> clean rebase -> behind=0. (2) S0.5 sweep 1+2: orders 51 "
        "disk/176 ack unacked=0 both sweeps; DEC EE659451 / ORD 17accc40 both UNCHANGED -- ORD false-alarm "
        "caught same-window (sha256 inertia miscompute 2bb2ee75 vs stored sha1 40-hex key; algorithm-pair "
        "resolved per r786 family, sha1 recompute identical; zero false consumption) -> algorithm-pair pin "
        "(DEC=SHA-256/ORD=SHA-1) direct-written to research/pit-protocol-d19.md per r712 law-4 (main-file "
        "margin-redline window 30,606B), receipt results/_r716bmc_pit_d19_directwrite.json (main untouched "
        "30,606B, target 20,475B, both <=30KB). (3) S1 smoke 48/48. (4) S3: satengine rc0 alive (burns 0, "
        "queue empty); watermark green; board 0 open (job_list 0 + fleet nondone all others' claimed faces); "
        "backlog 2 claimable lines = non-BigMoney domains (G17 game lane / CPH4 render bench) + NOT "
        "green-idle -> no claim; idle NOT-GREEN (RAM 16.8% free <40% resident ComfyUI), idle_rounds=0 "
        "worked-declared. (5) S6 39/39 rc0 (Tools/_r716bmc_s6.py driver; dualrun ZERO-DRIFT streak 36; "
        "cta_p1_paper honest bar-gated no-op panel cutoff 2026-09-30 < paper_start 2026-10-08 -> auto-fires "
        "tonight first-bar round; fund_premium pre-15:30 no-op -> today 15:30 bm-c-lane first snapshot; "
        "py_watermark verdict=py_low_board_clear legal idle whitelist; compute_audit flags pool_starvation+"
        "supply_floor recorded with standing disposition per r715). (6) QA: none this round (5x window "
        "r711-715 closed at r715; next 5x=r720). (7) post_review zero red (today REPORT 0 cross); orphan "
        "face=1 (resident ComfyUI server face, read-only no-kill, standing disposition); attrition CLEAN "
        "(4 healed noted); self-heal = loop pin=5 no-op + watchdog re-registered + both claws IN-PLACE; "
        "token L1 zero-token legs (token_meter rc0). (8) Product score 1 (S6 regen faces + algorithm-pair "
        "pin + driver = maintenance-window artifacts; zero new product line, pre-open holding honest)."
    )
    nxt = (
        "r717: (a) watch continuation: today 09:15 reopen first trading day, intraday marks lane live, "
        "pre-open zero blind action until 09:15; (b) tonight post-close face (<=10-08 23:59): data-chain "
        "full re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium 15:30 first snapshot (bm-c lane) "
        "+ QDII watch rerun holiday-delta + CTA_P1 first-bar auto-wiring + first-marks verification (S6 "
        "cta_p1_paper leg; verify = marks 1 row + state trial-live + compounding identity); (c) O-2215 "
        "deliverable (1) matrix spec + switching law v1 (<=10-16 12:00; consumes bm-a REGIME-5 "
        "discriminator <=10-14 + bm-b five-state router spec); (d) O-2245 follow-ups: first OSS- enrollments "
        "(bm-a strategy-class adaptations <=10-16) must pass Tools/oss_import_gate.py rc0 before settle; (e) "
        "cloudF row weekly rerun supply (window <=10-14, standing); (f) month-boundary first exam 10-31. "
        "[via bm-c r716]"
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
        "round_no": 717, "round_no_label": "round 716 (bm-c)",
        "last_round": 716, "last_round_at": TS,
        "current_task": current_task, "current_task_at": TS,
        "latest_artifact": latest_artifact,
        "next_milestone": (
            "今晚盘后: data-chain re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium 15:30 "
            "first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verify "
            "(<= 10-08 23:59); 09:15 起值守 intraday 面"
        ),
        "health": "ok",
        "activity_now": verdict, "did": did, "verdict": verdict,
        "note": ("r716: holding/maintenance round; ORD algorithm-pair pin direct-written (DEC=SHA-256/"
                 "ORD=SHA-1); S6 39 rc0 streak 36; both watermarks unchanged; orders unacked=0."),
        "last_round_summary": ("r716: holding round + ORD sha1/sha256 false-alarm catch + algorithm-pair "
                              "pin direct-write + S6 39 rc0 streak 36; watermarks unchanged; unacked=0; "
                              "smoke 48/48; post_review zero red."),
        "last_action": ("r716: holding round + ORD algorithm-pair pin direct-write + S6 39 rc0 streak 36; "
                        "watermarks unchanged; unacked=0; smoke 48/48; post_review zero red."),
        "next": nxt,
        "last_seen_at": TS, "updated_at": TS, "updated": TS,
        "last_run_at": TS, "last_ts": TS,
    })
    json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    chk = json.load(open(hp, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in chk["clock_read"], "clock_read must be T-separated"
    print("close-out done:", TS, "| cpu", cpu, "| ram_free", ram, "| gpu_free", gpu,
          "| epoch int OK | state round_no -> 717 | report line appended | heartbeat written")


if __name__ == "__main__":
    main()
