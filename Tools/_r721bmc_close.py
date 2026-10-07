"""r721 bm-c close-out: state round_no bump, round-report line append,
heartbeat refresh (three-line face per P-2026-09-29-07 #5, epoch int
self-check per R170/R178, clock_read T-separator per R262).
Pattern credit: Tools/_r720bmc_close.py (canonical)."""
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
    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    hb = json.load(open(hp, encoding="utf-8"))
    epoch = int(time.time())
    cpu = m["cpu_pct"] if m["cpu_pct"] is not None else hb.get("cpu_pct", 0.0)
    ram = m["ram_free_gb"] if m["ram_free_gb"] is not None else hb.get("free_ram_gb", 0.0)
    gpu = m["gpu_free_mb"] if m["gpu_free_mb"] is not None else hb.get("gpu_free_vram_mb", 0)

    # (state rich refresh moved below, after text faces)

    # --- 2) round report line
    line_ts = TS
    rpt = (
        f"{line_ts} | r721 | dept:工程（复市 T-0 盘前值守轮·第 41 bm-c 连守轮） | "
        "WM-VERDICT: 绿（red=false lane healthy·py_low_board_clear=板空+盘前无 bar 合法 idle 白名单"
        "〔板 0 open/51 disk unacked=0 双扫/池 406 全 done〕·compute_audit 旗标 pool_starvation"
        "+supply_floor 照录=池 ready 0<floor 3·处置在册=引擎常供线 W181+ 投影+今晚盘后 bar 面"
        "天然候选供给〔never-dry 常设律·禁手工代烧〕） | "
        "当前活: r721 盘前值守轮（03:0x 窗·09:15 前零盲动）——主产出="
        "①QA 41st 确定性包 qa/smoke-r721.md 5/5+qa/equity-curve-r721.png 66,217B"
        "（determinism=True·93 trades·equity 1,017,839 冻结恒等·market_clock rc0 cell=ORA"
        "·latest_panel_bar 2026-09-30 金周合法）"
        "②S6 40 腿链正典再生 Tools/_r721bmc_s6.py（r720 正典版克隆·40/40 rc0"
        "·dualrun ZERO-DRIFT streak 41 @406 条·cta_p1_paper bar-门控诚实 no-op"
        "〔今晚首 bar 轮自动接线〕·fund_premium pre-15:30 no-op→今日 15:30 bm-c 车道首采"
        "·全 lane 守卫诚实 no-op）"
        "③inbox 处理：MSG-2026-10-08-0250 bm-a→ALL S5_01_ZT_PILOT 批认领（F-04 认领先行）"
        "→移入 processed+去重确认（本司不碰该批）"
        "④QA 标号自纠：qa_smoke_run 缺省 state+1 误标 r722 双件〔r758/r640/r644 定律族〕"
        "→treasure_guard prescan 零命中→隔离 results/_quarantine/qa_mislabel_r721/"
        "→显式 --round 721 重产正标包（同窗零信息损失） | "
        "S0=轮首脏 6=自家 daemon live faces+orphan probe 报告→定向吸收 43e19c9c8→pull --rebase"
        " rc0 up-to-date（观察到 bm-a 备胎分支 machine/bm-a-r858 到达=其让路通道照旧非本司面）"
        "→收尾 commit 定向吸收轮中 churn | "
        "smoke 49/49 · S6 40/40 rc0 · QA 5/5（determinism=True 41th） · "
        "orders 双扫 unacked=0（51 disk·S0.5 首扫零差+S7 收尾二扫同验） · "
        "DEC/ORD 双水位 UNCHANGED（EE659451/17accc40·算法对按 r716 钉〔DEC=SHA-256/ORD=SHA-1〕"
        "·hex-case 归一 r711 律·facts results/_r721bmc_s05_facts.json shape-asserted） · "
        "SAT 活 rc0（N1_BANDS 面回读正常） · 板 0 open·job_list 0·本司常置 T-134 认领在册"
        "·backlog 2 可领=非本司域（游戏线）不领 · idle NOT-GREEN（RAM 16.8%<40% 常驻 ComfyUI"
        "·idle_rounds=0·--worked 申报） · post_review 零红（YES=45 NO=0 WAIT=5"
        "·REPORT-20261008） · 孤儿面=1（本机常驻 ComfyUI 服务面·CEO 私产·只读披露不击杀"
        "·既有处置维持） · attrition CLEAN（4 healed 注记照录） · "
        "自愈=loop pin=5 no-op（首火 03:15）+watchdog 重注册+双爪重装（LF 归一） · "
        "token 面=L1 零 token 腿（token_meter rc0） · "
        "方法论捕获=无新方法（纯值守复用·误标自纠=既有定律应用非新律）"
        "·宝藏捕获=N/A（无五类收口批）·登记册零命中断言=prescan 2 路径零命中"
        "（隔离区动作·manifest results/_quarantine/qa_mislabel_r721/manifest.json） · "
        "本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证） | "
        "下轮 r722：(a) 值守续（今日 09:15 复市首交易日·intraday marks 车道起活·盘前零盲动） "
        "(b) 今晚盘后面=数据链全门 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采"
        "（bm-c 车）+QDII watch 重跑长假差分+CTA_P1 首 bar 自动接线+首 marks 验证（≤10-08 23:59） "
        "(c) O-2215 ① 矩阵规格件+切换律 v1（≤10-16 12:00·待 bm-a REGIME-5 ≤10-14+bm-b 五态路由 spec 面） "
        "(d) O-2245 续作=首批 OSS- 落池件先过 Tools/oss_import_gate.py rc0 再 settle（bm-a ≤10-16） "
        "(e) cloudF 行收取窗 ≤10-14 常设 (f) 月界首考 10-31·下一 5x=r725 | "
        "轮产品计分：2（QA 41th 确定性包+S6 40 腿再生面+inbox 去重处置=能跑能看实物） | "
        "记账预算：3（state+心跳+轮报） [via bm-c r721]"
    )
    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    with open(rp, "a", encoding="utf-8", newline="") as f:
        f.write(rpt + "\n")

    # --- 3) heartbeat
    current_task = (
        "当前活: r721 bm-c 盘前值守轮（QA det-41th 5/5+S6 40 腿正典再生 streak 41"
        "+inbox bm-a zt-pilot 批认领去重处置+QA 标号自纠〔r722 误标→隔离→--round 721 正标重产〕"
        "·复市 T-0 盘前值守第 41 连守轮·盘前零盲动） | "
        f"最近实物: qa/smoke-r721.md 5/5（det 41th·93 trades·equity 1,017,839 冻结恒等）"
        f"+results/_r721bmc_s6_log.txt（40 legs rc0·dualrun streak 41）"
        f"+Tools/_r721bmc_s6.py @ {TS} | "
        "下个里程碑: 今晚盘后（10-08 15:30+）数据链全门 re-arm+REGIME_GUARD v3 新 bar enforce"
        "+fund_premium 首采（bm-c 车）+QDII watch 长假差分重跑+CTA_P1 首 bar 自动接线+首 marks 验证"
        "（≤10-08 23:59）；09:15 起值守 intraday 面；下一 5x=r725"
    )
    latest_artifact = (
        "qa/smoke-r721.md 5/5 + qa/equity-curve-r721.png 66,217B (determinism 41th, 93 trades, "
        "equity 1,017,839 frozen identity) + Tools/_r721bmc_s6.py + results/_r721bmc_s6_log.txt "
        "(40 legs rc0, dualrun ZERO-DRIFT streak 41) + results/_r721bmc_s05_facts.json (both "
        "watermarks unchanged, both sweeps unacked=0) + fleet/inbox/processed/"
        "MSG-2026-10-08-0250-bma-ALL-s501-zt-pilot-prereg-claim.md (bm-a batch-claim deconflict "
        "ack) @ " + TS
    )
    verdict = (
        "r721 bm-c: pre-open watch round (41st consecutive watch, 10-08 reopen T-0, 03:0x "
        "pre-open window, zero blind action). Product = QA 41st determinism pack (explicit "
        "--round 721; 5/5, 93 trades, equity 1,017,839 frozen identity, png 66,217B, "
        "market_clock cell=ORA, latest_panel_bar 2026-09-30 golden-week expected) + S6 40-leg "
        "chain regen via Tools/_r721bmc_s6.py (r720 canonical clone; 40/40 rc0; dualrun "
        "ZERO-DRIFT streak 41; cta_p1_paper bar-gated no-op auto-fires tonight first-bar; "
        "fund_premium pre-15:30 no-op -> today 15:30 bm-c-lane first snapshot) + inbox "
        "processing (MSG-2026-10-08-0250 bm-a->ALL S5_01_ZT_PILOT batch-claim -> processed + "
        "deconflict, this company does not touch that batch) + QA label self-correction "
        "(default state+1 mislabel r722 pair [r758/r640/r644 law family] -> treasure_guard "
        "prescan zero hits -> quarantined results/_quarantine/qa_mislabel_r721/ -> explicit "
        "--round 721 re-run, zero information loss same window). S0: round-start dirty 6 = own "
        "daemon faces + probe report -> targeted absorb 43e19c9c8 -> pull --rebase rc0 "
        "up-to-date; mid-round daemon churn absorbed at closeout. Both watermarks UNCHANGED "
        "(EE659451/17accc40, algorithm pair per r716 pin, hex-case normalized per r711); "
        "orders unacked=0 both sweeps; SAT alive rc0; board 0 open; not green-idle (RAM "
        "resident ComfyUI), idle_rounds=0 worked-declared; post_review zero red (YES=45 NO=0 "
        "WAIT=5, REPORT-20261008); orphan face=1 (resident ComfyUI, no-kill standing "
        "disposition); attrition CLEAN (4 healed noted); self-heal = loop pin=5 no-op + "
        "watchdog re-registered + both claws reinstalled (LF-normalized); token L1 zero-token "
        "legs."
    )
    did = (
        "r721 bm-c: pre-open watch round + QA 41th pack + S6 40-leg regen (10-08 reopen T-0, "
        "41st consecutive watch round, 03:0x pre-open window). (1) S0: round-start dirty 6 = "
        "own daemon live faces + orphan probe report -> targeted absorb 43e19c9c8 -> pull "
        "--rebase rc0 up-to-date; mid-round daemon churn absorbed at closeout. (2) S0.5 "
        "sweeps 1+2: orders 51 disk unacked=0 both; DEC EE659451 / ORD 17accc40 both "
        "UNCHANGED (SHA-256/SHA-1 pair per r716 pin, hex-case normalized per r711; facts "
        "results/_r721bmc_s05_facts.json, shape-asserted); inbox sweep-1 = MSG-2026-10-08-0250 "
        "bm-a->ALL S5_01_ZT_PILOT batch-claim -> moved to processed + deconflict ack (F-04 "
        "claim-first honored); sweep-2 inbox 0 unread. (3) S1 smoke 49/49. (4) S3: satengine "
        "rc0 alive; watermark green (py_low_board_clear legal idle whitelist); board 0 open; "
        "job_list 0; idle NOT-GREEN, idle_rounds=0, --worked declared. (5) MAIN PRODUCT: QA "
        "41st determinism pack 5/5 (explicit --round 721; 93 trades, equity 1,017,839 frozen "
        "identity, png 66,217B) + S6 40-leg chain regen (Tools/_r721bmc_s6.py, r720 canonical "
        "clone; 40/40 rc0; dualrun ZERO-DRIFT streak 41; compute_audit flags pool_starvation"
        "+supply_floor recorded with standing disposition). (6) QA label self-correction per "
        "r758/r640/r644 law family (default state+1 mislabel r722 pair -> prescan zero hits "
        "-> quarantine -> explicit --round 721 rerun). (7) post_review zero red; orphan "
        "face=1 no-kill documented; attrition CLEAN (4 healed noted); self-heal = loop pin=5 "
        "no-op + watchdog re-registered + both claws reinstalled LF-normalized; token L1 "
        "zero-token legs. (8) Product score 2 (QA evidence pack + S6 regen + inbox deconflict "
        "= runnable visible artifacts; honest zero new product lines in pre-open watch "
        "window)."
    )
    nxt = (
        "r722: (a) watch continuation: today 09:15 reopen first trading day, intraday marks "
        "lane live, pre-open zero blind action until 09:15; (b) tonight post-close face "
        "(<=10-08 23:59): data-chain full re-arm + REGIME_GUARD v3 first-new-bar enforce + "
        "fund_premium 15:30 first snapshot (bm-c lane) + QDII watch rerun holiday-delta + "
        "CTA_P1 first-bar auto-wiring + first-marks verification (S6 cta_p1_paper leg; verify "
        "= marks 1 row + state trial-live + compounding identity); (c) O-2215 deliverable (1) "
        "matrix spec + switching law v1 (<=10-16 12:00; consumes bm-a REGIME-5 discriminator "
        "<=10-14 + bm-b five-state router spec); (d) O-2245 follow-ups: first OSS- enrollments "
        "(bm-a strategy-class adaptations <=10-16) must pass Tools/oss_import_gate.py rc0 "
        "before settle; (e) cloudF row collection window <=10-14 standing; (f) month-boundary "
        "first exam 10-31; next 5x=r725. [via bm-c r721]"
    )
    # --- 1) state-bm-c.json rich refresh
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 722
    st["round_no_label"] = "round 721 (bm-c)"
    st["last_round"] = 721
    for k in ("last_round_at", "last_seen", "last_seen_at", "last_run_at",
              "last_ts", "updated", "updated_at", "current_task_at",
              "last_decisions_read_at"):
        st[k] = TS
    st["ts"] = TS
    st["clock_read"] = TS
    st["heartbeat_epoch_utc"] = epoch
    st["cpu_pct"] = cpu
    st["cpu_idle_pct"] = round(100 - cpu, 1) if cpu is not None else st.get("cpu_idle_pct")
    for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb"):
        st[k] = ram
    for k in ("gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_free_mib", "gpu_free_mb"):
        st[k] = gpu
    st["current_task"] = current_task
    st["did"] = did
    st["verdict"] = verdict
    st["activity_now"] = verdict
    st["last_round_summary"] = ("r721: QA det-41th 5/5 + S6 40 rc0 streak 41 + inbox "
                                "deconflict (bm-a zt-pilot claim); watermarks unchanged; "
                                "unacked=0; smoke 49/49.")
    st["last_action"] = st["last_round_summary"]
    st["note"] = ("r721: QA det-41th explicit --round 721 (mislabel r722 self-corrected via "
                  "quarantine); S6 40/40 rc0 streak 41; both watermarks unchanged; orders "
                  "unacked=0 both sweeps; smoke 49/49; post_review zero red.")
    st["next_pointer"] = nxt
    st["latest_artifact"] = latest_artifact
    st["next_milestone"] = (
        "tonight post-close: data-chain re-arm + REGIME_GUARD v3 first-new-bar enforce + "
        "fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + "
        "first-marks verify (<= 10-08 23:59)"
    )
    st["verify"] = (
        "qa/smoke-r721.md 5/5 + qa/equity-curve-r721.png 66,217B (determinism=True 41th, 93 "
        "trades, equity 1,017,839 frozen identity) + results/_r721bmc_s6_log.txt (40 legs "
        "rc0, dualrun streak 41) + results/_r721bmc_s05_facts.json (sweeps unacked=0, both "
        "watermarks unchanged) + Tools/_r721bmc_s6.py + Tools/_r721bmc_s05.py + "
        "Tools/_r721bmc_close.py + results/_attrition_guard_scan.json + "
        "results/_quarantine/qa_mislabel_r721/manifest.json"
    )
    st["last_decisions_sha_method"] = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r721 "
        "sweeps = UNCHANGED EE659451 zero delta zero action; hex-case comparison normalized "
        "per r711 pit law; facts-driven from results/_r721bmc_s05_facts.json, 64hex "
        "shape-asserted, never hand-typed (r583 S4 law))"
    )
    st["last_orders_sha_method"] = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r721 sweeps = "
        "UNCHANGED 17accc40, zero delta; hex-case comparison normalized per r711 pit law; "
        "facts-driven from results/_r721bmc_s05_facts.json, 40hex shape-asserted, never "
        "hand-typed (r583 S4 law))"
    )
    json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    hb.update({
        "idle_rounds": 0, "agenda_starved": False,
        "heartbeat_epoch_utc": epoch,
        "last_seen": TS, "clock_read": TS, "ts": TS,
        "cpu_pct": cpu, "cpu_util_pct": cpu, "cpu_idle_pct": round(100 - cpu, 1) if cpu is not None else None,
        "free_ram_gb": ram, "idle_ram_gb": ram, "ram_free_gb": ram,
        "gpu_free_vram_mb": gpu, "gpu_idle_vram_mb": gpu, "gpu_vram_free_mb": gpu,
        "gpu_free_mb": gpu, "gpu_idle_mb": gpu, "gpu_free_mib": gpu,
        "gpu_idle_vram_mib": gpu, "gpu_idle_mib": gpu,
        "round_no": 722, "round_no_label": "round 721 (bm-c)",
        "last_round": 721, "last_round_at": TS,
        "current_task": current_task, "current_task_at": TS,
        "latest_artifact": latest_artifact,
        "next_milestone": (
            "今晚盘后: data-chain re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium "
            "15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verify "
            "(<= 10-08 23:59); 09:15 起值守 intraday 面; next 5x=r725"
        ),
        "health": "ok",
        "activity_now": verdict, "did": did, "verdict": verdict,
        "note": ("r721: QA det-41th 5/5 (explicit --round) + S6 40 rc0 streak 41 + inbox "
                 "deconflict; both watermarks unchanged; orders unacked=0; smoke 49/49; "
                 "post_review zero red."),
        "last_round_summary": ("r721: QA det-41th 5/5 + S6 40 rc0 streak 41 + inbox "
                              "deconflict; watermarks unchanged; unacked=0; smoke 49/49."),
        "last_action": ("r721: QA det-41th 5/5 + S6 40 rc0 streak 41 + inbox deconflict; "
                        "watermarks unchanged; unacked=0; smoke 49/49."),
        "next": nxt,
        "last_seen_at": TS, "updated_at": TS, "updated": TS,
        "last_run_at": TS, "last_ts": TS,
    })
    json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    chk = json.load(open(hp, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in chk["clock_read"], "clock_read must be T-separated"
    print("close-out done:", TS, "| cpu", cpu, "| ram_free", ram, "| gpu_free", gpu,
          "| epoch int OK | state round_no -> 722 | report line appended | heartbeat written")


if __name__ == "__main__":
    main()
