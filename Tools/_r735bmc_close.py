"""r735 bm-c close-out: state round_no bump (735 done -> 736), round-report
line append, heartbeat refresh (three-line face per P-2026-09-29-07 #5,
epoch int self-check per R170/R178, clock_read T-separator per R262).
Pattern credit: Tools/_r734bmc_close.py (canonical)."""
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
    rpt = (
        f"{TS} | r735 | dept:工程（复市 T-0 盘前值守轮·第 55 bm-c 连守轮） | "
        "WM-VERDICT: 绿（red=false·next_pick=claimed moneyflow IC 车道"
        "〔板 176 票 0 open/51 disk unacked=0 双扫恒等〕） | "
        "当前活: r735 盘前值守轮（06:0x 窗·09:15 前零盲动）——主产出="
        "①CODELY mini-split（r734 交接 FIRST ACTION 完成）：主件 disk "
        "32,999→30,654B ≤30,720 帽 ✓（git blob LF 面 32,896B→~30,554B"
        "·autocrlf r420 族盘面如实注记）·4 条 verbatim 迁出="
        "r863 rebase-continue 零 UU 仍拒坑（742B）→pit-git-resolver-rebase.md"
        "〔resolver 主件 30,089B 满员·rebase 冲突窗子件归位·交接计划偏离"
        "已在收据 amendment 注记〕+r863 buildgen FRESH token 坑（506B）"
        "→pit-engine.md〔与 r734 行合并缺陷随迁治愈补 NL·r439 族〕"
        "+r734 pre-push 爪删集 push range 语义坑（1,139B）→pit-git-staged.md"
        "〔r806 同域〕+r711 水位 hash hex 大小写归一坑（774B）"
        "→pit-protocol-d19.md〔假 delta 族执法面·r672 姊妹〕"
        "·两趟手术如实注记（pass-1 指针行 931B 超帽 50B→pass-2 裁剪 815B "
        "合帽·迁移块零触碰）·receipt _r735bmc_codely_minisplit.json"
        "（sha16×4·byte 方程两趟断言·treasure prescan rc3 留痕 per r703 "
        "precedent·全域件 ≤30KB 四绿） "
        "②QA det-55th 确定性包 qa/smoke-r735.md 5/5+qa/equity-curve-r735.png "
        "66,145B（determinism=True·93 trades·equity 1,017,839 冻结恒等"
        "·sharpe=0.159 maxdd=-0.0433 win_rate=0.4624·market_clock rc0 "
        "cell=ORA·latest_panel_bar 2026-09-30 金周合法"
        "·显式 --round 735 FIRST TRY=零误标〔第 3 连守〕"
        "·runner pid 33380 分离态 .err 空·终态轮询后收口〔r640 律〕）"
        "③S6 40 腿链正典再生 Tools/_r735bmc_s6.py（r734 正典克隆"
        "·40/40 rc0·dualrun ZERO-DRIFT streak 51 维持"
        "·cta_p1_paper bar-门控诚实 no-op〔今晚首 bar 轮自动接线〕"
        "·fund_premium pre-15:30 no-op→今日 15:30 bm-c 车道首采"
        "·REPORT/LIVE-2026-10-08 再生·全 lane 守卫诚实 no-op） | "
        "S0=轮首脏 7=自家 daemon live faces→定向吸收 bc74915e8"
        "→pull --rebase 吸收 bm-a r864 链（3cb5a35ba 顶）→push 送达 "
        "6caeaaf85（fetch+rev-parse 双恒等自证·本地未达 origin=0） | "
        "S0.5 双扫：orders 51 disk unacked=0（首扫零差·收尾二扫恒等）"
        "·DEC EE659451/ORD 17accc40 双水位 UNCHANGED（算法对按 r716 钉"
        "·hex-case 归一 r711 律·facts results/_r735bmc_s05_facts.json "
        "shape-asserted）·inbox 双扫 0 件 | "
        "smoke 49/49 · S6 40/40 rc0 · QA 5/5（determinism=True 55th） · "
        "SAT 活 rc0 · job_list 0 · 板 176 票 0 open · idle NOT-GREEN"
        "（RAM 16.9% 常驻 ComfyUI 挤压·idle_rounds=0·--worked 申报） · "
        "post_review 零红（YES=45 NO=0 WAIT=5·本窗零新宣称） · "
        "孤儿面=1（本机常驻 ComfyUI 服务面·CEO 私产·只读披露不击杀"
        "·既有处置维持） · attrition CLEAN（4 ledger files·3 healed 注记"
        "照录） · 自愈=loop pin=5 no-op（首火 06:05）+watchdog 重注册"
        "（首火 06:03）+双爪重装（LF 归一） · token 面=L1 零 API token"
        "·方法论/宝藏捕获=无新方法无五类收口批（如实零 append） · "
        "本地未达 origin commit 数=0（6caeaaf85 双 rev-parse 恒等） | "
        "下轮 r736：(a) 值守续（今日 09:15 复市首交易日·intraday marks "
        "车道起活·盘前零盲动） (b) 今晚盘后面（≤10-08 23:59）=数据链全门 "
        "re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采"
        "（bm-c 车）+QDII watch 长假差分重跑+CTA_P1 首 bar 自动接线"
        "+首 marks 验证 (c) O-2215 ① 矩阵规格件+切换律 v1（≤10-16 12:00） "
        "(d) O-2245 OSS gate 续作（≤10-16） (e) cloudF 收取窗 ≤10-14 常设 "
        "(f) 月界首考 10-31 (g) 下一 5x=bm-c r740 | "
        "轮产品计分：2（QA 55th 确定性包+S6 40 腿再生+mini-split 收据面"
        "=能跑能看实物） | 记账预算：3（state+心跳+轮报） "
        "[via bm-c r735]"
    )
    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    with open(rp, "a", encoding="utf-8", newline="") as f:
        f.write(rpt + "\n")

    # --- 3) heartbeat three-line face + rich fields
    current_task = (
        "当前活: r735 bm-c 盘前值守轮（CODELY mini-split 收口=主件 30,654B "
        "≤30,720 帽·4 条 verbatim 迁出+两趟手术如实注记·QA det-55th 5/5"
        "+S6 40 腿正典再生 streak 51 维持·显式 --round 735 零误标·"
        "复市 T-0 盘前值守第 55 连守轮·盘前零盲动） | "
        f"最近实物: qa/smoke-r735.md 5/5（det 55th·93 trades·equity "
        f"1,017,839 冻结恒等）+qa/equity-curve-r735.png 66,145B"
        f"+results/_r735bmc_codely_minisplit.json（mini-split 收据）"
        f"+results/_r735bmc_s6_log.txt（40 legs rc0） @ {TS} | "
        "下个里程碑: 今晚盘后（10-08 15:30+）数据链全门 re-arm+REGIME_GUARD "
        "v3 新 bar enforce+fund_premium 首采（bm-c 车）+CTA_P1 首 bar 自动接线"
        "+首 marks 验证（≤10-08 23:59）；09:15 起值守 intraday 面；下一 5x=bm-c r740"
    )
    latest_artifact = (
        "qa/smoke-r735.md 5/5 + qa/equity-curve-r735.png 66,145B (determinism "
        "55th, 93 trades, equity 1,017,839 frozen identity, explicit --round "
        "735 first try) + results/_r735bmc_codely_minisplit.json (4 entries "
        "verbatim migrated, sha16x4, two-pass honest note, all files <=30KB) "
        "+ Tools/_r735bmc_{prescan,s05,codely_minisplit,codely_minisplit_fix,"
        "s6,qa_ignite}.py + results/_r735bmc_s6_log.txt (40 legs rc0, dualrun "
        "streak 51) + results/_r735bmc_s05_facts.json (both sweeps unacked=0, "
        "both watermarks unchanged) @ " + TS
    )
    verdict = (
        "r735 bm-c: pre-open watch round (55th consecutive watch, 10-08 reopen "
        "T-0, 06:0x pre-open window, zero blind action). Product = (1) CODELY "
        "mini-split per r734 handoff FIRST ACTION: main disk 32,999->30,654B "
        "<=30,720 cap, 4 entries verbatim migrated (r863 rebase-continue "
        "742B -> pit-git-resolver-rebase.md [resolver main 30,089B full, "
        "sub-file placement, amendment noted in receipt]; r863 buildgen "
        "FRESH 506B -> pit-engine.md [merged-line defect healed, r439 "
        "family]; r734 pre-push claw 1,139B -> pit-git-staged.md [r806 "
        "domain]; r711 hex-case 774B -> pit-protocol-d19.md [false-delta "
        "family enforcement face]); two-pass honest note (pass-1 pointer "
        "931B overshot cap by 50B -> pass-2 trim 815B, zero loss to "
        "migrated blocks); receipt sha16x4 + byte equations + prescan rc3 "
        "per r703 precedent; all touched files <=30KB. (2) QA 55th "
        "determinism pack 5/5 (explicit --round 735 FIRST TRY zero mislabel "
        "3rd consecutive; 93 trades, equity 1,017,839 frozen identity, png "
        "66,145B, market_clock cell=ORA, latest_panel_bar 2026-09-30 "
        "golden-week expected; runner pid 33380 detached, .err empty, "
        "terminal state polled before close per r640 law). (3) S6 40-leg "
        "chain regen via Tools/_r735bmc_s6.py (r734 canonical clone; 40/40 "
        "rc0; dualrun streak 51; cta_p1_paper bar-gated no-op auto-fires "
        "tonight first-bar; fund_premium pre-15:30 no-op -> today 15:30 "
        "bm-c-lane first snapshot; REPORT/LIVE-2026-10-08 regen). S0: "
        "round-start dirty 7 = own daemon live faces -> targeted absorb "
        "bc74915e8 -> pull --rebase absorbed bm-a r864 chain (tip 3cb5a35ba) "
        "-> products push delivered 6caeaaf85 (fetch+rev-parse dual identity, "
        "local-behind-origin=0). Both watermarks UNCHANGED (EE659451/"
        "17accc40, algorithm pair per r716 pin, hex-case normalized per "
        "r711); orders unacked=0 both sweeps identical; inbox 0 both "
        "sweeps; smoke 49/49; SAT alive rc0; board 176 tickets 0 open; "
        "job_list 0; not green-idle (RAM compressed by resident ComfyUI), "
        "idle_rounds=0, --worked declared; post_review zero red (YES=45 "
        "NO=0 WAIT=5); orphan face=1 (resident ComfyUI, no-kill standing "
        "disposition); attrition CLEAN (4 files, 3 healed noted); "
        "self-heal = loop pin=5 no-op (first fire 06:05) + watchdog "
        "re-registered (first fire 06:03) + both claws reinstalled "
        "(LF-normalized); token L1 zero API token."
    )
    did = (
        "r735 bm-c: CODELY mini-split + QA 55th + S6 40-leg regen (10-08 "
        "reopen T-0, 55th consecutive watch round, 06:0x pre-open window). "
        "(1) S0: round-start dirty 7 = own daemon live faces -> targeted "
        "absorb bc74915e8 -> pull --rebase absorbed bm-a r864 chain -> "
        "products push delivered 6caeaaf85. (2) S0.5 sweeps 1+2: orders 51 "
        "disk unacked=0 both sweeps identical; DEC EE659451 / ORD 17accc40 "
        "both UNCHANGED (facts results/_r735bmc_s05_facts.json, "
        "shape-asserted); inbox 0 both sweeps. (3) S1 smoke 49/49. (4) S3: "
        "satengine rc0 alive; watermark green (red=false, next_pick="
        "claimed); board 176 tasks 0 open; job_list 0; idle NOT-GREEN "
        "(resident ComfyUI), idle_rounds=0, --worked declared. (5) MAIN "
        "PRODUCT: CODELY mini-split (main 32,999->30,654B disk, 4 entries "
        "verbatim, receipt _r735bmc_codely_minisplit.json, two-pass "
        "pointer-trim honest note) + QA 55th determinism pack 5/5 "
        "(explicit --round 735 FIRST TRY; 93 trades, equity 1,017,839 "
        "frozen identity, png 66,145B) + S6 40-leg chain regen (40/40 rc0, "
        "dualrun streak 51). (6) post_review zero red (YES=45 NO=0); "
        "orphan face=1 no-kill documented; attrition CLEAN; self-heal "
        "quartet green (loop pin=5 no-op + watchdog re-registered + both "
        "claws reinstalled LF-normalized); token L1 zero API token. (7) "
        "Product score 2 (mini-split receipt + QA evidence pack + S6 "
        "regen = runnable visible artifacts)."
    )
    nxt = (
        "r736: (a) watch continuation: today 09:15 reopen first trading "
        "day, intraday marks lane live, pre-open zero blind action until "
        "09:15; (b) tonight post-close face (<=10-08 23:59): data-chain "
        "full re-arm + REGIME_GUARD v3 first-new-bar enforce + "
        "fund_premium 15:30 first snapshot (bm-c lane) + QDII watch "
        "rerun holiday-delta + CTA_P1 first-bar auto-wiring + first-marks "
        "verification (S6 cta_p1_paper leg; verify = marks 1 row + state "
        "trial-live + compounding identity); (c) O-2215 deliverable (1) "
        "matrix spec + switching law v1 (<=10-16 12:00; consumes bm-a "
        "REGIME-5 discriminator <=10-14 + bm-b five-state router spec); "
        "(d) O-2245 follow-ups: first OSS enrollments (bm-a "
        "strategy-class adaptations <=10-16) must pass "
        "Tools/oss_import_gate.py rc0 before settle; (e) cloudF row "
        "collection window <=10-14 standing; (f) month-boundary first "
        "exam 10-31. [via bm-c r735]"
    )
    # --- 1) state-bm-c.json rich refresh
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 736
    st["round_no_label"] = "round 735 (bm-c)"
    st["last_round"] = 735
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
    st["last_round_summary"] = (
        "r735: CODELY mini-split (main 32,999->30,654B <=cap, 4 entries "
        "verbatim, two-pass pointer trim honest note) + QA det-55th 5/5 "
        "(explicit --round 735 first try 3rd consecutive) + S6 40 rc0 "
        "streak 51; watermarks unchanged; unacked=0 both sweeps; inbox 0; "
        "smoke 49/49; post_review zero red."
    )
    st["last_action"] = st["last_round_summary"]
    st["note"] = (
        "r735: mini-split handoff FIRST ACTION done (resolver-rebase "
        "sub-file amendment per byte math, receipt notes); QA det-55th "
        "explicit first try; S6 40/40 rc0; absorb bc74915e8 + rebase "
        "(bm-a r864 chain) + push 6caeaaf85; both watermarks unchanged; "
        "unacked=0 both sweeps; smoke 49/49."
    )
    st["next_pointer"] = nxt
    st["latest_artifact"] = latest_artifact
    st["next_milestone"] = (
        "tonight post-close: data-chain re-arm + REGIME_GUARD v3 "
        "first-new-bar enforce + fund_premium 15:30 first snapshot (bm-c "
        "lane) + CTA_P1 first-bar auto-wiring + first-marks verify "
        "(<= 10-08 23:59); next 5x = bm-c r740"
    )
    st["verify"] = (
        "results/_r735bmc_codely_minisplit.json (sha16x4, byte equations, "
        "all touched <=30KB) + qa/smoke-r735.md 5/5 + "
        "qa/equity-curve-r735.png 66,145B (determinism=True 55th, 93 "
        "trades, equity 1,017,839 frozen identity) + "
        "results/_r735bmc_s6_log.txt (40 legs rc0, dualrun streak 51) + "
        "results/_r735bmc_s05_facts.json (both sweeps unacked=0, both "
        "watermarks unchanged) + results/_attrition_guard_scan.json"
    )
    st["last_decisions_sha_method"] = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main "
        "git show; r735 sweeps = UNCHANGED EE659451 zero delta zero "
        "action; hex-case comparison normalized per r711 pit law; "
        "facts-driven from results/_r735bmc_s05_facts.json, 64hex "
        "shape-asserted, never hand-typed (r583 S4 law))"
    )
    st["last_orders_sha_method"] = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 "
        "law; r735 sweeps = UNCHANGED 17accc40, zero delta; hex-case "
        "comparison normalized per r711 pit law; facts-driven from "
        "results/_r735bmc_s05_facts.json, 40hex shape-asserted, never "
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
        "round_no": 736, "round_no_label": "round 735 (bm-c)",
        "last_round": 735, "last_round_at": TS,
        "current_task": current_task, "current_task_at": TS,
        "latest_artifact": latest_artifact,
        "next_milestone": (
            "今晚盘后: data-chain re-arm + REGIME_GUARD v3 first-new-bar "
            "enforce + fund_premium 15:30 first snapshot (bm-c lane) + "
            "CTA_P1 first-bar auto-wiring + first-marks verify "
            "(<= 10-08 23:59); next 5x = bm-c r740"
        ),
        "health": "ok",
        "activity_now": verdict, "did": did, "verdict": verdict,
        "note": (
            "r735: CODELY mini-split (main <=cap, 4 verbatim, two-pass "
            "honest note) + QA det-55th 5/5 (explicit --round first try "
            "3rd consecutive) + S6 40 rc0 streak 51; both watermarks "
            "unchanged; unacked=0; inbox 0; smoke 49/49."
        ),
        "last_round_summary": (
            "r735: mini-split + QA det-55th 5/5 + S6 40 rc0 streak 51; "
            "watermarks unchanged; unacked=0; smoke 49/49."
        ),
        "last_action": (
            "r735: mini-split + QA det-55th 5/5 + S6 40 rc0 streak 51; "
            "watermarks unchanged; unacked=0; smoke 49/49."
        ),
        "next": nxt,
        "last_seen_at": TS, "updated_at": TS, "updated": TS,
        "last_run_at": TS, "last_ts": TS,
    })
    json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    chk = json.load(open(hp, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in chk["clock_read"], "clock_read must be T-separated"
    print("close-out done:", TS, "| cpu", cpu, "| ram_free", ram, "| gpu_free", gpu,
          "| epoch int OK | state round_no -> 736 | report line appended | heartbeat written")


if __name__ == "__main__":
    main()
