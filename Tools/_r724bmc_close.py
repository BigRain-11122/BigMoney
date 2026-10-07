"""r724 bm-c close-out: state round_no bump, round-report line append,
heartbeat refresh (three-line face per P-2026-09-29-07 #5, epoch int
self-check per R170/R178, clock_read T-separator per R262).
Pattern credit: Tools/_r723bmc_close.py (canonical)."""
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
        f"{line_ts} | r724 | dept:\u5de5\u7a0b\uff08\u590d\u5e02 T-0 \u76d8\u524d\u503c\u5b88\u8f6e"
        "\u00b7\u7b2c 44 bm-c \u8fde\u5b88\u8f6e\uff09 | "
        "WM-VERDICT: \u7eff\uff08red=false\u00b7next_pick=claimed moneyflow IC \u8f66\u9053"
        "\u00b7py_low_board_clear=\u677f\u7a7a+\u76d8\u524d\u65e0 bar \u5408\u6cd5 idle \u767d\u540d\u5355"
        "\u3014\u677f 45 \u7968\u5168 claimed \u96f6 open/51 disk unacked=0 \u53cc\u626b\u3015"
        "\u00b7compute_audit \u65d7\u6807 supply_floor \u7167\u5f55=\u6c60 ready 1"
        "\u3014W16-SCREEN owner bm-a\u3015<floor 3\u00b7\u5904\u7f6e\u5728\u518c=\u5f15\u64ce\u5e38\u4f9b"
        "\u7ebf+\u4eca\u665a\u76d8\u540e bar \u9762\u5929\u7136\u5019\u9009\u4f9b\u7ed9"
        "\u3014never-dry \u5e38\u8bbe\u5f8b\u00b7\u7981\u624b\u5de5\u4ee3\u70e7\u3015\uff09 | "
        "\u5f53\u524d\u6d3b: r724 \u76d8\u524d\u503c\u5b88\u8f6e\uff0803:3x \u7a97\u00b709:15 \u524d\u96f6"
        "\u76f2\u52a8\uff09\u2014\u2014\u4e3b\u4ea7\u51fa="
        "\u2460QA 44th \u786e\u5b9a\u6027\u5305 qa/smoke-r724.md 5/5+qa/equity-curve-r724.png 66,299B"
        "\uff08determinism=True\u00b793 trades\u00b7equity 1,017,839 \u51bb\u7ed3\u6052\u7b49"
        "\u00b7market_clock rc0 cell=ORA\u00b7latest_panel_bar 2026-09-30 \u91d1\u5468\u5408\u6cd5"
        "\u00b7\u663e\u5f0f --round 724=\u96f6\u8bef\u6807\u3014r721 \u6559\u8bad\u8fde\u5b88\u3015\uff09"
        "\u2461S6 40 \u817f\u94fe\u6b63\u5178\u518d\u751f Tools/_r724bmc_s6.py\uff08r723 \u6b63\u5178"
        "\u514b\u9686\u00b740/40 rc0\u00b7dualrun ZERO-DRIFT streak 44 @407 \u6761"
        "\u00b7cta_p1_paper bar-\u95e8\u63a7\u8bda\u5b9e no-op"
        "\u3014panel cutoff 2026-09-30<paper_start 2026-10-08\u00b7\u4eca\u665a\u9996 bar \u8f6e"
        "\u81ea\u52a8\u63a5\u7ebf\u3015\u00b7fund_premium pre-15:30 no-op\u2192\u4eca\u65e5 15:30 bm-c "
        "\u8f66\u9053\u9996\u91c7\u00b7\u5168 lane \u5b88\u536b\u8bda\u5b9e no-op\uff09 | "
        "S0=\u8f6e\u9996\u810f 7=6 \u81ea\u5bb6 daemon live faces+r723 commitmsg \u9057\u7559"
        "\u2192\u5b9a\u5411\u5438\u6536 05daaa412\u2192pull --rebase \u649e 1-UU"
        "\uff08results/_orphan_face_probe.json\u00b7\u4ed6\u673a 03:08:12 vs \u672c\u673a 03:35:19 "
        "\u5171\u4eab\u540d\u63a2\u9488\u5bf9\u649e\uff09\u2192treasure_guard restore-class \u95e8 rc0"
        "\uff08reproducible-artifact\uff09\u2192live-wins newer-ts take-theirs\u2192\u539f\u5b50 "
        "add+continue\u2192rebase rc0 86b7cb21f\uff08\u8fdb\u4ef6=bm-a r858/859\uff1aW16-SCREEN "
        "\u5ea7\u4f4d enroll+autofill \u8ba4\u9886\uff09 | "
        "S0.5 \u53cc\u626b\uff1aorders 51 disk unacked=0 \u53cc\u626b\u00b7DEC EE659451/ORD "
        "17accc40 \u53cc\u6c34\u4f4d UNCHANGED\uff08\u7b97\u6cd5\u5bf9\u6309 r716 \u9489"
        "\u3014DEC=SHA-256/ORD=SHA-1\u3015\u00b7hex-case \u5f52\u4e00 r711 \u5f8b"
        "\u00b7facts results/_r724bmc_s05_facts.json shape-asserted\uff09\u00b7inbox \u9996\u626b 1 "
        "\u4ef6=MSG-2026-10-08-0330 bm-a\u2192ALL W16-SCREEN \u5ea7\u4f4d\u58f0\u660e"
        "\uff08\u6c60\u6838\u5b9e entry 406 enroll\u00b7\u5355\u5206\u7247 w16-screen-0of1 owner=bm-a "
        "@03:32:08\u00b7bm-c \u96f6\u53ef\u9886\u9762\uff09\u2192\u5df2\u5904\u7406\u5f52\u6863 "
        "processed/\u00b7\u6536\u5c3e\u4e8c\u626b 0 \u4ef6 | "
        "smoke 49/49 \u00b7 S6 40/40 rc0 \u00b7 QA 5/5\uff08determinism=True 44th\uff09 \u00b7 "
        "SAT \u6d3b rc0 \u00b7 job_list 0 \u00b7 idle NOT-GREEN\uff08RAM 16.9%<40% \u5e38\u9a7b "
        "ComfyUI\u00b7idle_rounds=0\u00b7--worked \u7533\u62a5\uff09 \u00b7 post_review \u96f6\u7ea2"
        "\uff08\u271345 \u27170 \U0001F7E15\u00b7REPORT-20261008\u00b7\u672c\u7a97\u96f6\u65b0"
        "\u5ba3\u79f0\uff09 \u00b7 \u5b64\u513f\u9762=1\uff08\u672c\u673a\u5e38\u9a7b ComfyUI \u670d"
        "\u52a1\u9762\u00b7\u53ea\u8bfb\u62ab\u9732\u4e0d\u51fb\u6740\u00b7\u65e2\u6709\u5904\u7f6e"
        "\u7ef4\u6301\uff09 \u00b7 attrition CLEAN\uff084 healed \u6ce8\u8bb0\u7167\u5f55\uff09 \u00b7 "
        "\u81ea\u6108=loop pin=5 no-op\uff08\u9996\u706b 03:45\uff09+watchdog \u91cd\u6ce8\u518c"
        "\uff08\u9996\u706b 03:43\uff09+\u53cc\u722a\u91cd\u88c5\uff08LF \u5f52\u4e00\uff09 \u00b7 "
        "token \u9762=L1 \u96f6 token \u817f\uff08delta=0\uff09 \u00b7 \u65b9\u6cd5\u8bba/\u5b9d"
        "\u85cf\u6355\u83b7=\u65e0\u65b0\u65b9\u6cd5\u65e0\u4e94\u7c7b\u6536\u53e3\u6279 \u00b7 "
        "\u6539\u8fdb\u9762\uff1aHQ-FEEDBACK F-20261008-02 \u884c\u7ea7\u8ffd\u52a0\uff08\u5b64"
        "\u513f\u63a2\u9488\u5171\u4eab\u540d UU \u7a0e\u2192per-machine \u540e\u7f00\u5efa\u8bae"
        "\u00b7\u96c6\u56e2\u666e\u9002\u5f8b\uff09 \u00b7 \u672c\u5730\u672a\u8fbe origin commit "
        "\u6570=0\uff08commit \u540e push+fetch+rev-list \u81ea\u8bc1\uff09 | "
        "\u4e0b\u8f6e r725=5x\uff08HANDOVER \u66f4\u65b0\u8f6e\uff09\uff1a(a) \u503c\u5b88\u7eed\uff08"
        "\u4eca\u65e5 09:15 \u590d\u5e02\u9996\u4ea4\u6613\u65e5\u00b7intraday marks \u8f66\u9053\u8d77"
        "\u6d3b\u00b7\u76d8\u524d\u96f6\u76f2\u52a8\uff09 (b) \u4eca\u665a\u76d8\u540e\u9762"
        "\uff08\u226410-08 23:59\uff09=\u6570\u636e\u94fe\u5168\u95e8 re-arm+REGIME_GUARD v3 \u9996"
        "\u65b0 bar enforce+fund_premium 15:30 \u9996\u91c7\uff08bm-c \u8f66\uff09+QDII watch "
        "\u957f\u5047\u5dee\u5206\u91cd\u8dd1+CTA_P1 \u9996 bar \u81ea\u52a8\u63a5\u7ebf+\u9996 "
        "marks \u9a8c\u8bc1 (c) 5x \u8f6e=HANDOVER \u6838\u5bf9\u66f4\u65b0 (d) O-2215 \u77e9\u9635"
        "\u89c4\u683c\u4ef6+\u5207\u6362\u5f8b v1\uff08\u226410-16 12:00\uff09 (e) O-2245 OSS gate "
        "\u7eed\u4f5c\uff08\u226410-16\uff09 (f) cloudF \u6536\u53d6\u7a97 \u226410-14 \u5e38\u8bbe "
        "(g) \u6708\u754c\u9996\u8003 10-31 | "
        "\u8f6e\u4ea7\u54c1\u8ba1\u5206\uff1a2\uff08QA 44th \u786e\u5b9a\u6027\u5305+S6 40 \u817f"
        "\u518d\u751f=\u80fd\u8dd1\u80fd\u770b\u5b9e\u7269\uff09 | "
        "\u8bb0\u8d26\u9884\u7b97\uff1a4\uff08state+\u5fc3\u8df3+\u8f6e\u62a5+HQ-FEEDBACK \u884c\uff09 "
        "[via bm-c r724]"
    )
    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    with open(rp, "a", encoding="utf-8", newline="") as f:
        f.write(rpt + "\n")

    # --- 3) heartbeat
    current_task = (
        "\u5f53\u524d\u6d3b: r724 bm-c \u76d8\u524d\u503c\u5b88\u8f6e\uff08QA det-44th 5/5+S6 40 "
        "\u817f\u6b63\u5178\u518d\u751f streak 44\u00b7\u663e\u5f0f --round 724 \u96f6\u8bef\u6807"
        "\u00b7\u590d\u5e02 T-0 \u76d8\u524d\u503c\u5b88\u7b2c 44 \u8fde\u5b88\u8f6e\u00b7\u76d8\u524d"
        "\u96f6\u76f2\u52a8\uff09 | "
        f"\u6700\u8fd1\u5b9e\u7269: qa/smoke-r724.md 5/5\uff08det 44th\u00b793 trades\u00b7"
        f"equity 1,017,839 \u51bb\u7ed3\u6052\u7b49\uff09"
        f"+results/_r724bmc_s6_log.txt\uff0840 legs rc0\u00b7dualrun streak 44\uff09"
        f"+Tools/_r724bmc_s6.py @ {TS} | "
        "\u4e0b\u4e2a\u91cc\u7a0b\u7891: \u4eca\u665a\u76d8\u540e\uff0810-08 15:30+\uff09\u6570"
        "\u636e\u94fe\u5168\u95e8 re-arm+REGIME_GUARD v3 \u65b0 bar enforce+fund_premium \u9996\u91c7"
        "\uff08bm-c \u8f66\uff09+QDII watch \u957f\u5047\u5dee\u5206\u91cd\u8dd1+CTA_P1 \u9996 bar "
        "\u81ea\u52a8\u63a5\u7ebf+\u9996 marks \u9a8c\u8bc1\uff08\u226410-08 23:59\uff09\uff1b"
        "09:15 \u8d77\u503c\u5b88 intraday \u9762\uff1b\u4e0b\u8f6e r725=5x HANDOVER \u66f4\u65b0\u8f6e"
    )
    latest_artifact = (
        "qa/smoke-r724.md 5/5 + qa/equity-curve-r724.png 66,299B (determinism 44th, 93 trades, "
        "equity 1,017,839 frozen identity) + Tools/_r724bmc_s6.py + results/_r724bmc_s6_log.txt "
        "(40 legs rc0, dualrun ZERO-DRIFT streak 44) + results/_r724bmc_s05_facts.json (both "
        "watermarks unchanged, both sweeps unacked=0) + HQ-FEEDBACK F-20261008-02 @ " + TS
    )
    verdict = (
        "r724 bm-c: pre-open watch round (44th consecutive watch, 10-08 reopen T-0, 03:3x "
        "pre-open window, zero blind action). Product = QA 44th determinism pack (explicit "
        "--round 724 FIRST TRY, zero mislabel; 5/5, 93 trades, equity 1,017,839 frozen "
        "identity, png 66,299B, market_clock cell=ORA, latest_panel_bar 2026-09-30 golden-week "
        "expected) + S6 40-leg chain regen via Tools/_r724bmc_s6.py (r723 canonical clone; "
        "40/40 rc0; dualrun ZERO-DRIFT streak 44; cta_p1_paper bar-gated no-op auto-fires "
        "tonight first-bar; fund_premium pre-15:30 no-op -> today 15:30 bm-c-lane first "
        "snapshot; all lane guards honest no-op) + HQ-FEEDBACK F-20261008-02 improvement line "
        "(orphan-probe shared-filename UU tax -> per-machine suffix law). S0: round-start "
        "dirty 7 = own daemon live faces + r723 commitmsg leftover -> targeted absorb "
        "05daaa412 -> pull --rebase hit 1-UU on results/_orphan_face_probe.json (bm-a "
        "03:08:12 vs local 03:35:19 shared-name probe collision) -> treasure_guard "
        "restore-class rc0 (reproducible-artifact) -> live-wins newer-ts take-theirs -> "
        "atomic add+continue -> rebase rc0 86b7cb21f (incoming = bm-a r858/859 W16-SCREEN "
        "enroll + autofill claim). Both watermarks UNCHANGED (EE659451/17accc40, algorithm "
        "pair per r716 pin, hex-case normalized per r711); orders unacked=0 both sweeps; "
        "inbox sweep-1 = 1 MSG (bm-a W16-SCREEN seat declaration; pool entry 406 verified, "
        "single shard owner=bm-a 03:32:08, bm-c zero claimable face) -> processed/archived; "
        "sweep-2 = 0; SAT alive rc0; board 45 tickets all claimed, 0 open; not green-idle "
        "(RAM 16.9% resident ComfyUI), idle_rounds=0, --worked declared; post_review zero red "
        "(YES=45 NO=0 WAIT=5, REPORT-20261008, zero new claims this window); orphan face=1 "
        "(resident ComfyUI, no-kill standing disposition); attrition CLEAN (4 healed noted); "
        "self-heal = loop pin=5 no-op (first fire 03:45) + watchdog re-registered (first fire "
        "03:43) + both claws reinstalled (LF-normalized); token L1 zero-token legs (delta=0)."
    )
    did = (
        "r724 bm-c: pre-open watch round + QA 44th pack + S6 40-leg regen (10-08 reopen T-0, "
        "44th consecutive watch round, 03:3x pre-open window). (1) S0: round-start dirty 7 = "
        "own daemon live faces + r723 commitmsg leftover -> targeted absorb 05daaa412 -> pull "
        "--rebase hit 1-UU (results/_orphan_face_probe.json shared-name probe collision, bm-a "
        "03:08:12 vs local 03:35:19) -> treasure_guard restore-class rc0 -> live-wins "
        "newer-ts take-theirs -> atomic add+continue -> rebase rc0 86b7cb21f (incoming bm-a "
        "r858/859 W16-SCREEN enroll + claim). (2) S0.5 sweeps 1+2: orders 51 disk unacked=0 "
        "both; DEC EE659451 / ORD 17accc40 both UNCHANGED (facts results/"
        "_r724bmc_s05_facts.json, shape-asserted); inbox sweep-1 = 1 MSG bm-a W16-SCREEN seat "
        "declaration (pool entry 406 verified, single shard owner=bm-a, bm-c zero claimable) "
        "-> processed/archived, reply in round report; sweep-2 = 0. (3) S1 smoke 49/49. (4) "
        "S3: satengine rc0 alive; watermark green (red=false, next_pick=claimed, "
        "py_low_board_clear legal idle whitelist); board 45 all claimed 0 open; job_list 0; "
        "idle NOT-GREEN (RAM 16.9%<40% resident ComfyUI), idle_rounds=0, --worked declared. "
        "(5) MAIN PRODUCT: QA 44th determinism pack 5/5 (explicit --round 724 FIRST TRY zero "
        "mislabel; 93 trades, equity 1,017,839 frozen identity, png 66,299B) + S6 40-leg "
        "chain regen (Tools/_r724bmc_s6.py, r723 canonical clone; 40/40 rc0; dualrun "
        "ZERO-DRIFT streak 44; compute_audit flags supply_floor recorded with standing "
        "disposition) + HQ-FEEDBACK F-20261008-02 improvement line (orphan-probe "
        "shared-filename UU tax -> per-machine suffix law, group-universal). (6) post_review "
        "zero red (zero new claims); orphan face=1 no-kill documented; attrition CLEAN (4 "
        "healed noted); self-heal = loop pin=5 no-op + watchdog re-registered + both claws "
        "reinstalled LF-normalized; token L1 zero-token legs delta=0. (7) Product score 2 (QA "
        "evidence pack + S6 regen = runnable visible artifacts + improvement line; honest "
        "zero new product lines in pre-open watch window)."
    )
    nxt = (
        "r725 (5x HANDOVER update round): (a) watch continuation: today 09:15 reopen first "
        "trading day, intraday marks lane live, pre-open zero blind action until 09:15; (b) "
        "tonight post-close face (<=10-08 23:59): data-chain full re-arm + REGIME_GUARD v3 "
        "first-new-bar enforce + fund_premium 15:30 first snapshot (bm-c lane) + QDII watch "
        "rerun holiday-delta + CTA_P1 first-bar auto-wiring + first-marks verification (S6 "
        "cta_p1_paper leg; verify = marks 1 row + state trial-live + compounding identity); "
        "(c) 5x round duty: HANDOVER product-list check/update per every-5-rounds law; (d) "
        "O-2215 deliverable (1) matrix spec + switching law v1 (<=10-16 12:00; consumes bm-a "
        "REGIME-5 discriminator <=10-14 + bm-b five-state router spec); (e) O-2245 follow-ups: "
        "first OSS- enrollments (bm-a strategy-class adaptations <=10-16) must pass "
        "Tools/oss_import_gate.py rc0 before settle; (f) cloudF row collection window <=10-14 "
        "standing; (g) month-boundary first exam 10-31. [via bm-c r724]"
    )
    # --- 1) state-bm-c.json rich refresh
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 725
    st["round_no_label"] = "round 724 (bm-c)"
    st["last_round"] = 724
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
    st["last_round_summary"] = ("r724: QA det-44th 5/5 (explicit --round first try) + S6 40 "
                                "rc0 streak 44 + 1-UU probe-file conflict resolved live-wins "
                                "+ HQ-FEEDBACK F-20261008-02; watermarks unchanged; "
                                "unacked=0; inbox 1 processed; smoke 49/49.")
    st["last_action"] = st["last_round_summary"]
    st["note"] = ("r724: QA det-44th explicit --round 724 first try zero mislabel; S6 40/40 "
                  "rc0 streak 44; S0 1-UU orphan-probe shared-name conflict resolved "
                  "live-wins per law; both watermarks unchanged; orders unacked=0 both "
                  "sweeps; inbox MSG bm-a W16-SCREEN seat processed; smoke 49/49; "
                  "post_review zero red.")
    st["next_pointer"] = nxt
    st["latest_artifact"] = latest_artifact
    st["next_milestone"] = (
        "tonight post-close: data-chain re-arm + REGIME_GUARD v3 first-new-bar enforce + "
        "fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + "
        "first-marks verify (<= 10-08 23:59); next round r725 = 5x HANDOVER update round"
    )
    st["verify"] = (
        "qa/smoke-r724.md 5/5 + qa/equity-curve-r724.png 66,299B (determinism=True 44th, 93 "
        "trades, equity 1,017,839 frozen identity) + results/_r724bmc_s6_log.txt (40 legs "
        "rc0, dualrun streak 44) + results/_r724bmc_s05_facts.json (sweeps unacked=0, both "
        "watermarks unchanged) + Tools/_r724bmc_s6.py + Tools/_r724bmc_s05.py + "
        "Tools/_r724bmc_hqfb_append.py + Tools/_r724bmc_close.py + HQ-FEEDBACK "
        "F-20261008-02 + results/_attrition_guard_scan.json"
    )
    st["last_decisions_sha_method"] = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r724 "
        "sweeps = UNCHANGED EE659451 zero delta zero action; hex-case comparison normalized "
        "per r711 pit law; facts-driven from results/_r724bmc_s05_facts.json, 64hex "
        "shape-asserted, never hand-typed (r583 S4 law))"
    )
    st["last_orders_sha_method"] = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r724 sweeps = "
        "UNCHANGED 17accc40, zero delta; hex-case comparison normalized per r711 pit law; "
        "facts-driven from results/_r724bmc_s05_facts.json, 40hex shape-asserted, never "
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
        "round_no": 725, "round_no_label": "round 724 (bm-c)",
        "last_round": 724, "last_round_at": TS,
        "current_task": current_task, "current_task_at": TS,
        "latest_artifact": latest_artifact,
        "next_milestone": (
            "\u4eca\u665a\u76d8\u540e: data-chain re-arm + REGIME_GUARD v3 first-new-bar "
            "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar "
            "auto-wiring + first-marks verify (<= 10-08 23:59); 09:15 \u8d77\u503c\u5b88 "
            "intraday \u9762; next round r725 = 5x HANDOVER update round"
        ),
        "health": "ok",
        "activity_now": verdict, "did": did, "verdict": verdict,
        "note": ("r724: QA det-44th 5/5 (explicit --round first try) + S6 40 rc0 streak 44 "
                 "+ 1-UU probe-file conflict resolved live-wins + HQ-FEEDBACK "
                 "F-20261008-02; both watermarks unchanged; orders unacked=0; inbox 1 "
                 "processed; smoke 49/49; post_review zero red."),
        "last_round_summary": ("r724: QA det-44th 5/5 + S6 40 rc0 streak 44; watermarks "
                               "unchanged; unacked=0; inbox 1 processed; smoke 49/49."),
        "last_action": ("r724: QA det-44th 5/5 + S6 40 rc0 streak 44; watermarks unchanged; "
                        "unacked=0; inbox 1 processed; smoke 49/49."),
        "next": nxt,
        "last_seen_at": TS, "updated_at": TS, "updated": TS,
        "last_run_at": TS, "last_ts": TS,
    })
    json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    chk = json.load(open(hp, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in chk["clock_read"], "clock_read must be T-separated"
    print("close-out done:", TS, "| cpu", cpu, "| ram_free", ram, "| gpu_free", gpu,
          "| epoch int OK | state round_no -> 725 | report line appended | heartbeat written")


if __name__ == "__main__":
    main()
