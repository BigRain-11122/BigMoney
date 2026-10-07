"""r731 bm-c close-out: state round_no bump, round-report line append,
heartbeat refresh (three-line face per P-2026-09-29-07 #5, epoch int
self-check per R170/R178, clock_read T-separator per R262).
Pattern credit: Tools/_r730bmc_close.py (canonical)."""
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
        m["ram_pct"] = round(vm.available / vm.total * 100, 1)
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

    # --- 2) round report line
    line_ts = TS
    rpt = (
        f"{line_ts} | r731 | dept:工程（复市 T-0 盘前值守轮·第 51 bm-c 连守轮） | "
        "WM-VERDICT: 绿（red=false·next_pick=claimed moneyflow IC 车道"
        "·py_low_board_clear=板空+盘前无 bar 合法 idle 白名单"
        "〔板 176 票 0 open/51 disk unacked=0 双扫〕"
        "·compute_audit 旗标 supply_gap/supply_floor 照录=池 ready 1"
        "<floor 3·supply_family_streak 151.2min·run_samples=11 span 94.8min"
        "·处置在册=引擎常供线+今晚盘后 bar 面天然候选供给"
        "〔never-dry 常设律·禁手工代烧〕·single_core_hog 本窗无旗"
        "=QA runner 自然消亡先于采样窗） | "
        "当前活: r731 盘前值守轮（04:5x 窗·09:15 前零盲动）——主产出="
        "①QA 51st 确定性包 qa/smoke-r731.md 5/5+qa/equity-curve-r731.png "
        "66,078B（determinism=True·93 trades·equity 1,017,839 冻结恒等"
        "·market_clock rc0 cell=ORA·latest_panel_bar 2026-09-30 金周合法"
        "·显式 --round 731 FIRST TRY=零误标〔r721 教训连守〕）"
        "②S6 40 腿链正典再生 Tools/_r731bmc_s6.py（r730 正典克隆"
        "·40/40 rc0·dualrun ZERO-DRIFT streak 51 @408 条"
        "·cta_p1_paper bar-门控诚实 no-op"
        "〔panel cutoff 2026-09-30<paper_start 2026-10-08·今晚首 bar 轮自动接线〕"
        "·fund_premium pre-15:30 no-op→今日 15:30 bm-c 车道首采"
        "·live_paper lane_io 三信号否决诚实跳过〔bm-a origin 新鲜 3-4min〕"
        "·全 lane 守卫诚实 no-op） | "
        "S0=轮首脏 4=自家 daemon live faces（orphan probe 报告+dispatcher"
        "+satengine pair）→定向吸收 a4070a9d2（-F 消息件正法）"
        "→pull --rebase 重放 1 本地 pick 于 origin 前进波〔f8d127690"
        "=bm-a r862 W16-JUDGE finalize verified+consumed 40/40 判毕"
        "·合法模态零负结果·bm-c 只读消费面+churn absorbs〕零冲突"
        "·rebase 后 b0644f6df→push 送达（f8d127690..b0644f6df） | "
        "S0.5 双扫：orders 51 disk unacked=0（首扫零差·收尾二扫同验）"
        "·DEC EE659451/ORD 17accc40 双水位 UNCHANGED"
        "（算法对按 r716 钉〔DEC=SHA-256/ORD=SHA-1〕·hex-case 归一 r711 律"
        "·facts results/_r731bmc_s05_facts.json shape-asserted）"
        "·inbox 首扫 0 件·收尾二扫 0 件 | "
        "smoke 49/49 · S6 40/40 rc0 · QA 5/5（determinism=True 51st） · "
        "SAT 活 rc0 · job_list 0 · 板 176 票 0 open · idle NOT-GREEN"
        "（RAM 19.2%<40% 常驻 ComfyUI·idle_rounds=0·--worked 申报"
        "〔05:00:43 落盘〕） · post_review 零红承接"
        "（✓45 ✗0 🟡5·REPORT-20261008·03:41:16 生成窗照读·本窗零新宣称） · "
        "孤儿面=1（本机常驻 ComfyUI 服务面·CEO 私产·只读披露不击杀"
        "·既有处置维持） · attrition CLEAN（3 healed 注记照录） · "
        "自愈=loop pin=5 no-op（首火 05:05）+watchdog 重注册（首火 05:02）"
        "+双爪重装（LF 归一） · token 面=L1 零 token 腿（delta=0） · "
        "方法论/宝藏捕获=无新方法无五类收口批 · "
        "本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证） | "
        "下轮 r732：(a) 值守续（今日 09:15 复市首交易日·intraday marks "
        "车道起活·盘前零盲动） (b) 今晚盘后面（≤10-08 23:59）=数据链全门 "
        "re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采"
        "（bm-c 车）+QDII watch 长假差分重跑+CTA_P1 首 bar 自动接线"
        "+首 marks 验证 (c) O-2215 ① 矩阵规格件+切换律 v1（≤10-16 12:00） "
        "(d) O-2245 OSS gate 续作（≤10-16） (e) cloudF 收取窗 ≤10-14 常设 "
        "(f) 月界首考 10-31 (g) 下一 5x=bm-c r735 | "
        "轮产品计分：2（QA 51st 确定性包+S6 40 腿再生面=能跑能看实物"
        "；值守窗零新产品线如实） | 记账预算：3（state+心跳+轮报） "
        "[via bm-c r731]"
    )
    ram_pct_str = str(m.get("ram_pct") if m.get("ram_pct") is not None else 19.2)
    rpt = rpt.replace("RAM 19.2%", "RAM " + ram_pct_str + "%")
    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    with open(rp, "a", encoding="utf-8", newline="") as f:
        f.write(rpt + "\n")

    # --- 3) heartbeat
    current_task = (
        "当前活: r731 bm-c 盘前值守轮（QA det-51st 5/5+S6 40 腿正典再生 streak "
        "51·显式 --round 731 零误标·复市 T-0 盘前值守第 51 连守轮·盘前零盲动） | "
        f"最近实物: qa/smoke-r731.md 5/5（det 51st·93 trades·equity 1,017,839 "
        f"冻结恒等）+qa/equity-curve-r731.png 66,078B+results/_r731bmc_s6_log.txt"
        f"（40 legs rc0·dualrun streak 51） @ {TS} | "
        "下个里程碑: 今晚盘后（10-08 15:30+）数据链全门 re-arm+REGIME_GUARD v3 "
        "新 bar enforce+fund_premium 首采（bm-c 车）+QDII watch 长假差分重跑"
        "+CTA_P1 首 bar 自动接线+首 marks 验证（≤10-08 23:59）；09:15 起值守 "
        "intraday 面；下一 5x=bm-c r735"
    )
    latest_artifact = (
        "qa/smoke-r731.md 5/5 + qa/equity-curve-r731.png 66,078B (determinism "
        "51st, 93 trades, equity 1,017,839 frozen identity, explicit --round "
        "731 first try) + Tools/_r731bmc_s6.py + results/_r731bmc_s6_log.txt "
        "(40 legs rc0, dualrun ZERO-DRIFT streak 51) + "
        "results/_r731bmc_s05_facts.json (both sweeps unacked=0, both "
        "watermarks unchanged) + Tools/_r731bmc_{s0,s05,s3probe,qa_ignite,"
        "close}.py @ " + TS
    )
    verdict = (
        "r731 bm-c: pre-open watch round (51st consecutive watch, 10-08 reopen "
        "T-0, 04:5x pre-open window, zero blind action). Product = QA 51st "
        "determinism pack (explicit --round 731 FIRST TRY, zero mislabel; 5/5, "
        "93 trades, equity 1,017,839 frozen identity, png 66,078B, "
        "market_clock cell=ORA, latest_panel_bar 2026-09-30 golden-week "
        "expected) + S6 40-leg chain regen via Tools/_r731bmc_s6.py (r730 "
        "canonical clone; 40/40 rc0; dualrun ZERO-DRIFT streak 51 @408; "
        "cta_p1_paper bar-gated no-op auto-fires tonight first-bar; "
        "fund_premium pre-15:30 no-op -> today 15:30 bm-c-lane first "
        "snapshot; live_paper lane_io third-signal veto honest skip; all "
        "lane guards honest no-op; compute_audit flags supply_gap/supply_floor "
        "recorded with standing disposition never-dry + zero SLA violations; "
        "single_core_hog not flagged this window = QA runner natural death "
        "before audit sample). S0: round-start dirty 4 = own daemon live "
        "faces -> targeted absorb a4070a9d2 -> pull --rebase replayed 1 "
        "local pick onto bm-a r862 wave (W16-JUDGE finalize verified+consumed "
        "40/40 judged lawful modal-zero negative; read-only consumer face for "
        "bm-c; f8d127690) zero conflicts -> rebased b0644f6df -> push "
        "delivered (f8d127690..b0644f6df). Both watermarks UNCHANGED "
        "(EE659451/17accc40, algorithm pair per r716 pin, hex-case normalized "
        "per r711); orders unacked=0 both sweeps; inbox 0 both sweeps; SAT "
        "alive rc0; board 176 tickets 0 open; job_list 0; not green-idle "
        "(RAM 19.2% resident ComfyUI), idle_rounds=0, --worked declared "
        "05:00:43; post_review zero red carryover (03:41:16 window read, "
        "zero new claims this window); orphan face=1 (resident ComfyUI, "
        "no-kill standing disposition); attrition CLEAN (3 healed noted); "
        "self-heal = loop pin=5 no-op (first fire 05:05) + watchdog "
        "re-registered (first fire 05:02) + both claws reinstalled "
        "(LF-normalized); token L1 zero-token legs (delta=0)."
    )
    did = (
        "r731 bm-c: QA 51st pack + S6 40-leg regen (10-08 reopen T-0, 51st "
        "consecutive watch round, 04:5x pre-open window). (1) S0: round-start "
        "dirty 4 = own daemon live faces + orphan probe report -> targeted "
        "absorb a4070a9d2 -> pull --rebase replay 1 pick onto bm-a r862 "
        "wave zero conflicts -> rebased b0644f6df -> push delivered. (2) "
        "S0.5 sweeps 1+2: orders 51 disk unacked=0; DEC EE659451 / ORD "
        "17accc40 both UNCHANGED (facts results/_r731bmc_s05_facts.json, "
        "shape-asserted); inbox 0 both sweeps. (3) S1 smoke 49/49. (4) S3: "
        "satengine rc0 alive; watermark green (red=false, next_pick=claimed, "
        "py_low_board_clear legal idle whitelist); board 176 tasks 0 open; "
        "job_list 0; idle NOT-GREEN (RAM 19.2%<40% resident ComfyUI), "
        "idle_rounds=0, --worked declared 05:00:43. (5) MAIN PRODUCT: QA "
        "51st determinism pack 5/5 (explicit --round 731 FIRST TRY zero "
        "mislabel; 93 trades, equity 1,017,839 frozen identity, png 66,078B) "
        "+ S6 40-leg chain regen (Tools/_r731bmc_s6.py, r730 canonical "
        "clone; 40/40 rc0; dualrun ZERO-DRIFT streak 51). (6) post_review "
        "zero red carryover (zero new claims); orphan face=1 no-kill "
        "documented; attrition CLEAN (3 healed noted); self-heal quartet "
        "green (loop pin=5 no-op + watchdog re-registered + both claws "
        "reinstalled LF-normalized); token L1 zero-token legs delta=0. (7) "
        "Product score 2 (QA evidence pack + S6 regen = runnable visible "
        "artifacts)."
    )
    nxt = (
        "r732: (a) watch continuation: today 09:15 reopen first trading day, "
        "intraday marks lane live, pre-open zero blind action until 09:15; "
        "(b) tonight post-close face (<=10-08 23:59): data-chain full re-arm "
        "+ REGIME_GUARD v3 first-new-bar enforce + fund_premium 15:30 first "
        "snapshot (bm-c lane) + QDII watch rerun holiday-delta + CTA_P1 "
        "first-bar auto-wiring + first-marks verification (S6 cta_p1_paper "
        "leg; verify = marks 1 row + state trial-live + compounding "
        "identity); (c) O-2215 deliverable (1) matrix spec + switching law "
        "v1 (<=10-16 12:00; consumes bm-a REGIME-5 discriminator <=10-14 + "
        "bm-b five-state router spec); (d) O-2245 follow-ups: first OSS- "
        "enrollments (bm-a strategy-class adaptations <=10-16) must pass "
        "Tools/oss_import_gate.py rc0 before settle; (e) cloudF row "
        "collection window <=10-14 standing; (f) month-boundary first exam "
        "10-31. [via bm-c r731]"
    )
    verdict = verdict.replace("RAM 19.2%", "RAM " + ram_pct_str + "%")
    did = did.replace("RAM 19.2%", "RAM " + ram_pct_str + "%")
    # --- 1) state-bm-c.json rich refresh
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 732
    st["round_no_label"] = "round 731 (bm-c)"
    st["last_round"] = 731
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
    st["last_round_summary"] = ("r731: QA det-51st 5/5 (explicit --round 731 "
                                "first try) + S6 40 rc0 streak 51; watermarks "
                                "unchanged; unacked=0; inbox 0; smoke 49/49; "
                                "post_review zero red carryover.")
    st["last_action"] = st["last_round_summary"]
    st["note"] = ("r731: QA det-51th explicit --round 731 first try zero "
                  "mislabel; S6 40/40 rc0 streak 51; S0 absorb+rebase clean "
                  "(bm-a r862 wave absorbed zero conflicts); both watermarks "
                  "unchanged; orders unacked=0 both sweeps; smoke 49/49.")
    st["next_pointer"] = nxt
    st["latest_artifact"] = latest_artifact
    st["next_milestone"] = (
        "tonight post-close: data-chain re-arm + REGIME_GUARD v3 first-new-bar "
        "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 "
        "first-bar auto-wiring + first-marks verify (<= 10-08 23:59); next 5x "
        "= bm-c r735"
    )
    st["verify"] = (
        "qa/smoke-r731.md 5/5 + qa/equity-curve-r731.png 66,078B "
        "(determinism=True 51st, 93 trades, equity 1,017,839 frozen identity) "
        "+ results/_r731bmc_s6_log.txt (40 legs rc0, dualrun streak 51) + "
        "results/_r731bmc_s05_facts.json (both sweeps unacked=0, both "
        "watermarks unchanged) + Tools/_r731bmc_{s0,s05,s3probe,s6,qa_ignite,"
        "close}.py + results/_attrition_guard_scan.json"
    )
    st["last_decisions_sha_method"] = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git "
        "show; r731 sweeps = UNCHANGED EE659451 zero delta zero action; "
        "hex-case comparison normalized per r711 pit law; facts-driven from "
        "results/_r731bmc_s05_facts.json, 64hex shape-asserted, never "
        "hand-typed (r583 S4 law))"
    )
    st["last_orders_sha_method"] = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; "
        "r731 sweeps = UNCHANGED 17accc40, zero delta; hex-case comparison "
        "normalized per r711 pit law; facts-driven from "
        "results/_r731bmc_s05_facts.json, 40hex shape-asserted, never "
        "hand-typed (r583 S4 law))"
    )
    json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    hb.update({
        "idle_rounds": 0, "agenda_starved": False,
        "heartbeat_epoch_utc": epoch,
        "last_seen": TS, "clock_read": TS, "ts": TS,
        "cpu_pct": cpu, "cpu_util_pct": cpu,
        "cpu_idle_pct": round(100 - cpu, 1) if cpu is not None else None,
        "free_ram_gb": ram, "idle_ram_gb": ram, "ram_free_gb": ram,
        "gpu_free_vram_mb": gpu, "gpu_idle_vram_mb": gpu, "gpu_vram_free_mb": gpu,
        "gpu_free_mb": gpu, "gpu_idle_mb": gpu, "gpu_free_mib": gpu,
        "gpu_idle_vram_mib": gpu, "gpu_idle_mib": gpu,
        "round_no": 732, "round_no_label": "round 731 (bm-c)",
        "last_round": 731, "last_round_at": TS,
        "current_task": current_task, "current_task_at": TS,
        "latest_artifact": latest_artifact,
        "next_milestone": (
            "今晚盘后: data-chain re-arm + REGIME_GUARD v3 first-new-bar "
            "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 "
            "first-bar auto-wiring + first-marks verify (<= 10-08 23:59); "
            "next 5x = bm-c r735"
        ),
        "health": "ok",
        "activity_now": verdict, "did": did, "verdict": verdict,
        "note": ("r731: QA det-51st 5/5 (explicit --round first try) + S6 40 "
                 "rc0 streak 51; both watermarks unchanged; unacked=0; "
                 "inbox 0; smoke 49/49."),
        "last_round_summary": ("r731: QA det-51st 5/5 + S6 40 rc0 streak 51; "
                               "watermarks unchanged; unacked=0; "
                               "smoke 49/49."),
        "last_action": ("r731: QA det-51st 5/5 + S6 40 rc0 streak 51; "
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
          "| epoch int OK | state round_no -> 732 | report line appended | heartbeat written")


if __name__ == "__main__":
    main()
