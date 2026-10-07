"""r725 bm-c close-out: state round_no bump, round-report line append,
heartbeat refresh (three-line face per P-2026-09-29-07 #5, epoch int
self-check per R170/R178, clock_read T-separator per R262).
Pattern credit: Tools/_r724bmc_close.py (canonical)."""
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

    # --- 2) round report line
    line_ts = TS
    rpt = (
        f"{line_ts} | r725 | dept:\u5de5\u7a0b\uff08\u590d\u5e02 T-0 \u76d8\u524d\u503c\u5b88\u8f6e"
        "\u00b7\u7b2c 45 bm-c \u8fde\u5b88\u8f6e\u00b75x HANDOVER \u6838\u5bf9\u66f4\u65b0\u8f6e\uff09 | "
        "WM-VERDICT: \u7eff\uff08red=false\u00b7next_pick=claimed moneyflow IC \u8f66\u9053"
        "\u00b7py_low_board_clear=\u677f\u7a7a+\u76d8\u524d\u65e0 bar \u5408\u6cd5 idle \u767d\u540d\u5355"
        "\u3014\u677f 176 \u7968 0 open/51 disk unacked=0 \u53cc\u626b\u3015"
        "\u00b7compute_audit \u65d7\u6807 supply_gap/supply_floor \u7167\u5f55=\u6c60 ready 1"
        "\u3014W16-SCREEN owner bm-a\u3015<floor 3\u00b7\u5904\u7f6e\u5728\u518c=\u5f15\u64ce\u5e38\u4f9b"
        "\u7ebf+\u4eca\u665a\u76d8\u540e bar \u9762\u5929\u7136\u5019\u9009\u4f9b\u7ed9"
        "\u3014never-dry \u5e38\u8bbe\u5f8b\u00b7\u7981\u624b\u5de5\u4ee3\u70e7\u3015\uff09 | "
        "\u5f53\u524d\u6d3b: r725 5x HANDOVER \u6838\u5bf9\u66f4\u65b0\u8f6e\uff0803:4x \u7a97\u00b709:15 "
        "\u524d\u96f6\u76d2\u52a8\uff09\u2014\u2014\u4e3b\u4ea7\u51fa="
        "\u2460research/HANDOVER.md r725 \u884c\uff08\u589e\u91cf\u7a97 r721-725 \u4e94\u8f6e\u4ea7\u54c1"
        "\u6e05\u5355\u5237\u65b0\uff1aQA 41-45 \u8fde\u8bc1+S6 streak 42-45 \u8fde\u8425+r721 QA "
        "\u6807\u53f7\u81ea\u7ea0 quarantine \u5224\u4f8b+r724 1-UU \u5b64\u513f\u63a2\u9488\u5171\u4eab"
        "\u540d\u51b2\u7a81 live-wins \u5224\u4f8b+HQ-FEEDBACK F-20261008-02 \u6539\u8fdb\u884c"
        "\u00b7Tools/_r725bmc_handover.py \u5199\u5165\u81ea\u8bc1\uff09"
        "\u2461QA 45th \u786e\u5b9a\u6027\u5305 qa/smoke-r725.md 5/5+qa/equity-curve-r725.png "
        "66,274B\uff08determinism=True\u00b793 trades\u00b7equity 1,017,839 \u51bb\u7ed3\u6052\u7b49"
        "\u00b7market_clock rc0 cell=ORA\u00b7latest_panel_bar 2026-09-30 \u91d1\u5468\u5408\u6cd5"
        "\u00b7\u663e\u5f0f --round 725 FIRST TRY=\u96f6\u8bef\u6807\u3014r721 \u6559\u8bad\u8fde\u5b88"
        "\u3015\uff09\u2462S6 40 \u817f\u94fe\u6b63\u5178\u518d\u751f Tools/_r725bmc_s6.py"
        "\uff08r724 \u6b63\u5178\u514b\u9686\u00b740/40 rc0\u00b7dualrun ZERO-DRIFT streak 45 @407 "
        "\u6761\u00b7cta_p1_paper bar-\u95e8\u63a7\u8bda\u5b9e no-op"
        "\u3014panel cutoff 2026-09-30<paper_start 2026-10-08\u00b7\u4eca\u665a\u9996 bar \u8f6e"
        "\u81ea\u52a8\u63a5\u7ebf\u3015\u00b7fund_premium pre-15:30 no-op\u2192\u4eca\u65e5 15:30 bm-c "
        "\u8f66\u9053\u9996\u91c7\u00b7\u5168 lane \u5b88\u536b\u8bda\u5b9e no-op\uff09 | "
        "S0=\u8f6e\u9996\u810f 5=4 \u81ea\u5bb6 daemon live faces+orphan probe \u62a5\u544a"
        "\u2192\u5b9a\u5411\u5438\u6536 93530f5ad+\u8f6e\u4e2d dispatcher churn 3695d8aae"
        "\u2192pull --rebase up-to-date\uff08\u96f6 UU\u00b7\u96f6\u65b0\u5165\u4ef6\uff09\u2192push "
        "\u9001\u8fbe fc139dd1e..3695d8aae | "
        "S0.5 \u53cc\u626b\uff1aorders 51 disk unacked=0\uff08\u9996\u626b\u96f6\u5dee\u00b7\u6536"
        "\u5c3e\u4e8c\u626b\u540c\u9a8c\uff09\u00b7DEC EE659451/ORD 17accc40 \u53cc\u6c34\u4f4d "
        "UNCHANGED\uff08\u7b97\u6cd5\u5bf9\u6309 r716 \u9489\u3014DEC=SHA-256/ORD=SHA-1\u3015"
        "\u00b7hex-case \u5f52\u4e00 r711 \u5f8b\u00b7facts results/_r725bmc_s05_facts.json "
        "shape-asserted\uff09\u00b7inbox \u9996\u626b 0 \u4ef6\u00b7\u6536\u5c3e\u4e8c\u626b 0 \u4ef6 | "
        "smoke 49/49 \u00b7 S6 40/40 rc0 \u00b7 QA 5/5\uff08determinism=True 45th\uff09 \u00b7 "
        "SAT \u6d3b rc0 \u00b7 job_list 0 \u00b7 \u677f 176 \u7968 0 open \u00b7 idle NOT-GREEN"
        "\uff08RAM 13.3%<40% \u5e38\u9a7b ComfyUI\u00b7idle_rounds=0\u00b7--worked \u7533\u62a5"
        "\u301403:50:17 \u843d\u76d8\u3015\uff09 \u00b7 post_review \u96f6\u7ea2\u627f\u63a5"
        "\uff08\u271345 \u27170 \U0001F7E15\u00b7REPORT-20261008\u00b7r724 \u7a97\u9762\u7167\u8bfb"
        "\u00b7\u672c\u7a97\u96f6\u65b0\u5ba3\u79f0\uff09 \u00b7 \u5b64\u513f\u9762=1\uff08\u672c\u673a"
        "\u5e38\u9a7b ComfyUI \u670d\u52a1\u9762\u00b7CEO \u79c1\u4ea7\u00b7\u53ea\u8bfb\u62ab\u9732"
        "\u4e0d\u51fb\u6740\u00b7\u65e2\u6709\u5904\u7f6e\u7ef4\u6301\uff09 \u00b7 attrition CLEAN"
        "\uff084 healed \u6ce8\u8bb0\u7167\u5f55\uff09 \u00b7 \u81ea\u6108=loop pin=5 no-op\uff08\u9996"
        "\u706b 03:55\uff09+watchdog \u91cd\u6ce8\u518c\uff08\u9996\u706b 03:52\uff09+\u53cc\u722a"
        "\u91cd\u88c5\uff08LF \u5f52\u4e00\uff09 \u00b7 token \u9762=L1 \u96f6 token \u817f"
        "\uff08delta=0\uff09 \u00b7 \u65b9\u6cd5\u8bba/\u5b9d\u85cf\u6355\u83b7=\u65e0\u65b0\u65b9"
        "\u6cd5\u65e0\u4e94\u7c7b\u6536\u53e3\u6279 \u00b7 \u672c\u5730\u672a\u8fbe origin commit "
        "\u6570=0\uff08commit \u540e push+fetch+rev-list \u81ea\u8bc1\uff09 | "
        "\u4e0b\u8f6e r726\uff1a(a) \u503c\u5b88\u7eed\uff08\u4eca\u65e5 09:15 \u590d\u5e02\u9996"
        "\u4ea4\u6613\u65e5\u00b7intraday marks \u8f66\u9053\u8d77\u6d3b\u00b7\u76d8\u524d\u96f6\u76d2"
        "\u52a8\uff09 (b) \u4eca\u665a\u76d8\u540e\u9762\uff08\u226410-08 23:59\uff09=\u6570\u636e"
        "\u94fe\u5168\u95e8 re-arm+REGIME_GUARD v3 \u9996\u65b0 bar enforce+fund_premium 15:30 "
        "\u9996\u91c7\uff08bm-c \u8f66\uff09+QDII watch \u957f\u5047\u5dee\u5206\u91cd\u8dd1"
        "+CTA_P1 \u9996 bar \u81ea\u52a8\u63a5\u7ebf+\u9996 marks \u9a8c\u8bc1 (c) O-2215 \u2460 "
        "\u77e9\u9635\u89c4\u683c\u4ef6+\u5207\u6362\u5f8b v1\uff08\u226410-16 12:00\uff09 (d) "
        "O-2245 OSS gate \u7eed\u4f5c\uff08\u226410-16\uff09 (e) cloudF \u6536\u53d6\u7a97 "
        "\u226410-14 \u5e38\u8bbe (f) \u6708\u754c\u9996\u8003 10-31 (g) \u4e0b\u4e00 5x=bm-c "
        "r730 | "
        "\u8f6e\u4ea7\u54c1\u8ba1\u5206\uff1a2\uff08HANDOVER r725 \u4ea7\u54c1\u6e05\u5355\u5237"
        "\u65b0+QA 45th \u786e\u5b9a\u6027\u5305+S6 40 \u817f\u518d\u751f=\u80fd\u8dd1\u80fd\u770b"
        "\u5b9e\u7269\uff1b\u503c\u5b88\u7a97\u96f6\u65b0\u4ea7\u54c1\u7ebf\u5982\u5b9e\uff09 | "
        "\u8bb0\u8d26\u9884\u7b97\uff1a4\uff08state+\u5fc3\u8df3+\u8f6e\u62a5+HANDOVER \u6cd5\u5b9a\uff09 "
        "[via bm-c r725]"
    )
    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    with open(rp, "a", encoding="utf-8", newline="") as f:
        f.write(rpt + "\n")

    # --- 3) heartbeat
    current_task = (
        "\u5f53\u524d\u6d3b: r725 bm-c 5x HANDOVER \u6838\u5bf9\u66f4\u65b0\u8f6e\uff08HANDOVER "
        "r725 \u884c r721-725 \u7a97+QA det-45th 5/5+S6 40 \u817f\u6b63\u5178\u518d\u751f streak "
        "45\u00b7\u663e\u5f0f --round 725 \u96f6\u8bef\u6807\u00b7\u590d\u5e02 T-0 \u76d8\u524d\u503c"
        "\u5b88\u7b2c 45 \u8fde\u5b88\u8f6e\u00b7\u76d8\u524d\u96f6\u76d2\u52a8\uff09 | "
        f"\u6700\u8fd1\u5b9e\u7269: research/HANDOVER.md r725 \u884c+qa/smoke-r725.md 5/5"
        f"\uff08det 45th\u00b793 trades\u00b7equity 1,017,839 \u51bb\u7ed3\u6052\u7b49\uff09"
        f"+results/_r725bmc_s6_log.txt\uff0840 legs rc0\u00b7dualrun streak 45\uff09 @ {TS} | "
        "\u4e0b\u4e2a\u91cc\u7a0b\u7891: \u4eca\u665a\u76d8\u540e\uff0810-08 15:30+\uff09\u6570"
        "\u636e\u94fe\u5168\u95e8 re-arm+REGIME_GUARD v3 \u65b0 bar enforce+fund_premium \u9996"
        "\u91c7\uff08bm-c \u8f66\uff09+QDII watch \u957f\u5047\u5dee\u5206\u91cd\u8dd1+CTA_P1 "
        "\u9996 bar \u81ea\u52a8\u63a5\u7ebf+\u9996 marks \u9a8c\u8bc1\uff08\u226410-08 23:59"
        "\uff09\uff1b09:15 \u8d77\u503c\u5b88 intraday \u9762\uff1b\u4e0b\u4e00 5x=bm-c r730"
    )
    latest_artifact = (
        "research/HANDOVER.md r725 row (window r721-725 product-list refresh) + qa/smoke-r725.md "
        "5/5 + qa/equity-curve-r725.png 66,274B (determinism 45th, 93 trades, equity 1,017,839 "
        "frozen identity, explicit --round 725 first try) + Tools/_r725bmc_s6.py + "
        "results/_r725bmc_s6_log.txt (40 legs rc0, dualrun ZERO-DRIFT streak 45) + "
        "results/_r725bmc_s05_facts.json (both watermarks unchanged, both sweeps unacked=0) + "
        "Tools/_r725bmc_handover.py @ " + TS
    )
    verdict = (
        "r725 bm-c: 5x HANDOVER update round + pre-open watch (45th consecutive watch, 10-08 "
        "reopen T-0, 03:4x pre-open window, zero blind action). Product = HANDOVER r725 row "
        "(window r721-725 product-list refresh: QA 41-45 chain + S6 streak 42-45 + r721 QA "
        "mislabel quarantine precedent + r724 1-UU orphan-probe shared-name conflict "
        "live-wins precedent + HQ-FEEDBACK F-20261008-02 improvement line) + QA 45th "
        "determinism pack (explicit --round 725 FIRST TRY, zero mislabel; 5/5, 93 trades, "
        "equity 1,017,839 frozen identity, png 66,274B, market_clock cell=ORA, latest_panel_bar "
        "2026-09-30 golden-week expected) + S6 40-leg chain regen via Tools/_r725bmc_s6.py "
        "(r724 canonical clone; 40/40 rc0; dualrun ZERO-DRIFT streak 45; cta_p1_paper "
        "bar-gated no-op auto-fires tonight first-bar; fund_premium pre-15:30 no-op -> today "
        "15:30 bm-c-lane first snapshot; all lane guards honest no-op). S0: round-start dirty "
        "5 = own daemon live faces + orphan probe report -> targeted absorb 93530f5ad + "
        "mid-window dispatcher churn 3695d8aae -> pull --rebase up-to-date (zero UU, zero "
        "incoming) -> push delivered. Both watermarks UNCHANGED (EE659451/17accc40, algorithm "
        "pair per r716 pin, hex-case normalized per r711); orders unacked=0 both sweeps; "
        "inbox 0 both sweeps; SAT alive rc0; board 176 tickets 0 open; job_list 0; not "
        "green-idle (RAM 13.3% resident ComfyUI), idle_rounds=0, --worked declared 03:50:17; "
        "post_review zero red carryover (r724 window read, zero new claims this window); "
        "orphan face=1 (resident ComfyUI, no-kill standing disposition); attrition CLEAN "
        "(4 healed noted); self-heal = loop pin=5 no-op (first fire 03:55) + watchdog "
        "re-registered (first fire 03:52) + both claws reinstalled (LF-normalized); token "
        "L1 zero-token legs (delta=0)."
    )
    did = (
        "r725 bm-c: 5x HANDOVER update round + QA 45th pack + S6 40-leg regen (10-08 reopen "
        "T-0, 45th consecutive watch round, 03:4x pre-open window). (1) S0: round-start dirty "
        "5 = own daemon live faces + orphan probe report -> targeted absorb 93530f5ad + "
        "mid-window dispatcher churn absorb 3695d8aae -> pull --rebase up-to-date zero UU -> "
        "push delivered. (2) S0.5 sweeps 1+2: orders 51 disk unacked=0; DEC EE659451 / ORD "
        "17accc40 both UNCHANGED (facts results/_r725bmc_s05_facts.json, shape-asserted); "
        "inbox 0 both sweeps. (3) S1 smoke 49/49. (4) S3: satengine rc0 alive; watermark "
        "green (red=false, next_pick=claimed, py_low_board_clear legal idle whitelist); "
        "board 176 tasks 0 open; job_list 0; idle NOT-GREEN (RAM 13.3%<40% resident "
        "ComfyUI), idle_rounds=0, --worked declared. (5) MAIN PRODUCT: HANDOVER r725 row "
        "(Tools/_r725bmc_handover.py prepend, write-then-read-back assert; window r721-725 "
        "product-list refresh) + QA 45th determinism pack 5/5 (explicit --round 725 FIRST "
        "TRY zero mislabel; 93 trades, equity 1,017,839 frozen identity, png 66,274B) + S6 "
        "40-leg chain regen (Tools/_r725bmc_s6.py, r724 canonical clone; 40/40 rc0; dualrun "
        "ZERO-DRIFT streak 45; compute_audit flags supply_gap/supply_floor recorded with "
        "standing disposition). (6) post_review zero red carryover (zero new claims); orphan "
        "face=1 no-kill documented; attrition CLEAN (4 healed noted); self-heal = loop "
        "pin=5 no-op + watchdog re-registered + both claws reinstalled LF-normalized; token "
        "L1 zero-token legs delta=0. (7) Product score 2 (HANDOVER product-list refresh + QA "
        "evidence pack + S6 regen = runnable visible artifacts; honest zero new product "
        "lines in pre-open watch window)."
    )
    nxt = (
        "r726: (a) watch continuation: today 09:15 reopen first trading day, intraday marks "
        "lane live, pre-open zero blind action until 09:15; (b) tonight post-close face "
        "(<=10-08 23:59): data-chain full re-arm + REGIME_GUARD v3 first-new-bar enforce + "
        "fund_premium 15:30 first snapshot (bm-c lane) + QDII watch rerun holiday-delta + "
        "CTA_P1 first-bar auto-wiring + first-marks verification (S6 cta_p1_paper leg; "
        "verify = marks 1 row + state trial-live + compounding identity); (c) O-2215 "
        "deliverable (1) matrix spec + switching law v1 (<=10-16 12:00; consumes bm-a "
        "REGIME-5 discriminator <=10-14 + bm-b five-state router spec); (d) O-2245 "
        "follow-ups: first OSS- enrollments (bm-a strategy-class adaptations <=10-16) must "
        "pass Tools/oss_import_gate.py rc0 before settle; (e) cloudF row collection window "
        "<=10-14 standing; (f) month-boundary first exam 10-31; (g) next 5x = bm-c r730 "
        "HANDOVER. [via bm-c r725]"
    )
    # --- 1) state-bm-c.json rich refresh
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 726
    st["round_no_label"] = "round 725 (bm-c)"
    st["last_round"] = 725
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
    st["last_round_summary"] = ("r725: 5x HANDOVER row (r721-725) + QA det-45th 5/5 (explicit "
                                "--round first try) + S6 40 rc0 streak 45; watermarks "
                                "unchanged; unacked=0; inbox 0; smoke 49/49; post_review "
                                "zero red carryover.")
    st["last_action"] = st["last_round_summary"]
    st["note"] = ("r725: 5x HANDOVER update round; QA det-45th explicit --round 725 first "
                  "try zero mislabel; S6 40/40 rc0 streak 45; S0 clean window (absorb + "
                  "rebase up-to-date zero UU); both watermarks unchanged; orders unacked=0 "
                  "both sweeps; smoke 49/49.")
    st["next_pointer"] = nxt
    st["latest_artifact"] = latest_artifact
    st["next_milestone"] = (
        "tonight post-close: data-chain re-arm + REGIME_GUARD v3 first-new-bar enforce + "
        "fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + "
        "first-marks verify (<= 10-08 23:59); next 5x = bm-c r730 HANDOVER"
    )
    st["verify"] = (
        "research/HANDOVER.md r725 row + qa/smoke-r725.md 5/5 + qa/equity-curve-r725.png "
        "66,274B (determinism=True 45th, 93 trades, equity 1,017,839 frozen identity) + "
        "results/_r725bmc_s6_log.txt (40 legs rc0, dualrun streak 45) + "
        "results/_r725bmc_s05_facts.json (sweeps unacked=0, both watermarks unchanged) + "
        "Tools/_r725bmc_s6.py + Tools/_r725bmc_s05.py + Tools/_r725bmc_handover.py + "
        "Tools/_r725bmc_close.py + results/_attrition_guard_scan.json"
    )
    st["last_decisions_sha_method"] = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r725 "
        "sweeps = UNCHANGED EE659451 zero delta zero action; hex-case comparison normalized "
        "per r711 pit law; facts-driven from results/_r725bmc_s05_facts.json, 64hex "
        "shape-asserted, never hand-typed (r583 S4 law))"
    )
    st["last_orders_sha_method"] = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r725 sweeps = "
        "UNCHANGED 17accc40, zero delta; hex-case comparison normalized per r711 pit law; "
        "facts-driven from results/_r725bmc_s05_facts.json, 40hex shape-asserted, never "
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
        "round_no": 726, "round_no_label": "round 725 (bm-c)",
        "last_round": 725, "last_round_at": TS,
        "current_task": current_task, "current_task_at": TS,
        "latest_artifact": latest_artifact,
        "next_milestone": (
            "\u4eca\u665a\u76d8\u540e: data-chain re-arm + REGIME_GUARD v3 first-new-bar "
            "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar "
            "auto-wiring + first-marks verify (<= 10-08 23:59); next 5x = bm-c r730 "
            "HANDOVER"
        ),
        "health": "ok",
        "activity_now": verdict, "did": did, "verdict": verdict,
        "note": ("r725: 5x HANDOVER row (r721-725) + QA det-45th 5/5 (explicit --round "
                 "first try) + S6 40 rc0 streak 45; both watermarks unchanged; unacked=0; "
                 "inbox 0; smoke 49/49."),
        "last_round_summary": ("r725: 5x HANDOVER row + QA det-45th 5/5 + S6 40 rc0 streak "
                              "45; watermarks unchanged; unacked=0; smoke 49/49."),
        "last_action": ("r725: 5x HANDOVER row + QA det-45th 5/5 + S6 40 rc0 streak 45; "
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
          "| epoch int OK | state round_no -> 726 | report line appended | heartbeat written")


if __name__ == "__main__":
    main()
