# -*- coding: utf-8 -*-
"""r741 bm-c round-close bookkeeping: round report line append (EOL-matched),
heartbeat fleet/machines/bm-c.json + state-bm-c.json field updates
(epoch=int law R170/R178, clock_read T-separator law R262, round_no 741->742,
DEC/ORD both UNCHANGED zero consumption, live cpu/ram/gpu re-sample).
Pattern credit: Tools/_r740bmc_close.py (canonical clone chain)."""
import datetime
import json
import os
import psutil
import subprocess
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
RPT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
ST = os.path.join(ROOT, "state-bm-c.json")

REPORT_LINE = (
    "2026-10-08T07:3x+08:00 | r741 | dept:工程（复市 T-0 盘前值守轮·第 61 bm-c 连守轮·血统 re-walk 克隆轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane healthy·next_pick=claimed moneyflow IC 车道〔orders 51 disk unacked=0 双扫·inbox 0 双扫〕·"
    "py_watermark py_low_board_clear=板清+盘前无 bar 合法 idle·compute_audit 诚实旗 supply_gap+supply_floor=供给线在飞态"
    "〔pool ready 1<floor 3·W182 12/12 分片已烧完 bm-a r867 落账·引擎续供面 bm-a 属主非本机动作面〕） | "
    "当前活: r741 bm-c（07:2x-07:3x 窗·09:15 前零盲动）——主产出=①QA det-61th 5/5（显式 --round 741 FIRST TRY 零误标·"
    "93 trades·equity 1,017,839 冻结恒等·determinism=True·png 66,214B）+②S6 40/40 rc0 首过"
    "（dualrun ZERO-DRIFT streak 51 @408 条·REPORT/LIVE-2026-10-08 再生〔state=ORANGE cap=50% heat=COOL〕·"
    "fund_premium pre-15:30 no-op→今日 15:30 bm-c 车道首采·cta_p1_paper 无可标 bar→今晚首 bar 自动接线·"
    "live_paper REGIME_GUARD shadow 盘前）+③血统 re-walk 克隆门（无预派生集→_r741bmc_clone.py 双模替换 stale740=0 三件"
    "〔s05/s6/qa_ignite〕+compile 门全过·收据 _r741bmc_clone_receipt.json）+自愈四件套全绿（loop pin=5 符 no-op 首火 07:35"
    "+watchdog 在位+双爪 IN-PLACE）+attrition CLEAN（4 账本 3 healed 历史缩行照录）+post_review 零红（48Y/0N/5W）"
    "+孤儿面=1（常驻 ComfyUI 服务面·CEO 私产·只读披露不击杀·既有处置维持） | "
    "最近实物: qa/smoke-r741.md 5/5（93 trades·equity 1,017,839 冻结恒等·determinism=True）+qa/equity-curve-r741.png 66,214B"
    "+results/_r741bmc_s6_log.txt（40 腿 rc0）+results/_r741bmc_clone_receipt.json @ 2026-10-08T07:3x+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链全门 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采（bm-c 车）"
    "+CTA_P1 首 bar 自动接线+首 marks 验证（≤10-08 23:59）；09:15 起值守 intraday 面；下一 5x=bm-c r745 | "
    "验证证据: qa/smoke-r741.md 5/5（determinism=True·93 trades·1,017,839 frozen identity·market_clock cell=ORA·"
    "latest_panel_bar 2026-09-30 金周 no-op 如期）+qa/equity-curve-r741.png 66,214B+results/_r741bmc_s6_log.txt"
    "（40 legs rc0·dualrun streak 51 ZERO-DRIFT）+results/_r741bmc_s05_facts.json 双扫（DEC EE659451/ORD 267B1EA0 双 UNCHANGED"
    "·unacked=0·inbox 0·shape-asserted）+results/_attrition_guard_scan.json CLEAN+quartet 四证（pin=5 no-op+watchdog 在位+双爪"
    "CR 归一恒等）+克隆门收据 _r741bmc_clone_receipt.json（stale740=0·compile OK×3） | "
    "下轮指针: r742: (a) 09:15+ intraday marks lane live 值守（复市首交易日）·盘前零盲动；"
    "(b) tonight post-close face（≤10-08 23:59）: data-chain full re-arm+REGIME_GUARD v3 first-new-bar enforce"
    "（首新 bar 前设 BIGMONEY_REGIME_GUARD=enforce）+fund_premium 15:30 first snapshot（bm-c lane）+CTA_P1 first-bar auto-wiring"
    "+first-marks verification（marks 1 行+state trial-live+compounding identity）+QDII watch holiday-delta；"
    "(c) O-2215-1 remaining: SUPPORT row 候 bm-b router spec（≤10-16）+矩阵 run refire 待 bm-a REGIME-5 标签（≤10-14）"
    "+numeric weights review window+10-21 criteria revisit per order sec.4；(d) 域切片消费票随研究部节奏"
    "（a-stock-data 三验→T-173·free-stockdb→T-104·HiThink key→数据缺口台账）；(e) cloudF row ≤10-14 standing；"
    "(f) O-2245 OSS enrollments gate standing；(g) 月界首考 10-31；next 5x=bm-c r745。[via bm-c r741] | "
    "轮产品计分：2（QA 61th 确定性包+S6 40 腿再生+克隆门三件=能跑能看实物） | "
    "记账预算：5（state+心跳+轮报+attrition/post_review 例行扫描件+克隆收据）")

TASK = (
    "当前活: r741 bm-c（07:2x-07:3x 窗·复市 T-0 盘前值守第 61 连守轮·09:15 前零盲动）——主产出=QA det-61th 5/5"
    "（--round 741 FIRST TRY·93 trades·1,017,839 冻结恒等）+S6 40/40 rc0 首过（dualrun streak 51·ORANGE cap=50%·"
    "fund_premium/CTA_P1 今晚首采）+血统克隆门三件（stale740=0）+自愈四件套全绿+attrition CLEAN+post_review 零红（48Y/0N/5W）"
    "| 最近实物: qa/smoke-r741.md 5/5+qa/equity-curve-r741.png 66,214B+results/_r741bmc_s6_log.txt"
    "+results/_r741bmc_clone_receipt.json @ 2026-10-08T07:3x+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 enforce+fund_premium 首采（bm-c 车）"
    "+CTA_P1 首接线+首 marks 验证（≤10-08 23:59）；下一 5x=bm-c r745")

ACTIVITY = (
    "r741 bm-c: pre-open watch round 61st consecutive (07:2x-07:3x window; reopen T-0). "
    "(1) S0: fetch -> behind 3 (bm-a r867/r868: W182 engine burn 12/12 shards COMPLETE, engine queue 0) -> ff merge clean "
    "zero UU; round-start dirty 6 = own daemon live faces + r740 commit-script untracked leftover (targeted absorb). "
    "(2) S0.5 sweeps (round-start + close double-scan): DEC EE659451 UNCHANGED + ORD 267B1EA0 UNCHANGED (both watermarks "
    "stable, zero consumption); fleet orders 51 disk unacked=0 both sweeps; inbox 0 both sweeps. "
    "(3) S1 smoke 49/49. (4) S3: round-zero orphan probe py_faces=5 orphans=1 (resident ComfyUI service face, CEO asset, "
    "read-only disclosure no-kill, standing disposition); satengine rc0 alive (N1 waves 1-182 registered); watermark green "
    "(red=false, next_pick=claimed moneyflow IC); job_list 0; board 177 disk zero open; idle trigger not green-idle (RAM "
    "18.2% free resident ComfyUI), idle_rounds=0, worked declared via QA+S6 products. (5) MAIN PRODUCTS: (a) lineage "
    "re-walk clone gate (no pre-derived set: _r741bmc_clone.py double-mode replacement, stale740=0 across s05/s6/qa_ignite "
    "trio, compile gate PASS, receipt _r741bmc_clone_receipt.json). (b) QA det-61th determinism pack 5/5 FIRST TRY (explicit "
    "--round 741): 93 trades, equity 1,017,839 frozen identity, determinism=True, png 66,214B, market_clock cell=ORA, "
    "latest_panel_bar 2026-09-30 golden-week no-op expected (reopen T-0, first new bar tonight). (c) S6 40/40 rc0 first "
    "pass via Tools/_r741bmc_s6.py canonical clone (dualrun ZERO-DRIFT streak 51 @408 entries; compute_audit honest flags "
    "supply_gap+supply_floor [pool ready=1 < floor 3, supply-line standing state, W182 burn landed by bm-a r867]; "
    "py_watermark py_low_board_clear legal idle [bars absent pre-open, board clear]; fund_premium pre-15:30 no-op -> "
    "today 15:30 bm-c-lane first snapshot; cta_p1_paper no markable bar -> tonight first-bar auto-wiring; REPORT/LIVE-"
    "2026-10-08 regen state=ORANGE cap=50% heat=COOL). (6) post_review zero red latest-per-id (YES=48 NO=0 WAIT=5); "
    "attrition CLEAN (4 ledger files, 3 healed historical shrink notes); self-heal quartet green (loop pin=5 no-op "
    "first-fire 07:35 + watchdog present + both claws IN-PLACE CR-normalized match). (7) No new pit this round -> zero "
    "CODELY append.")

NEXT_PTR = (
    "r742: (a) watch continuation 09:15+ intraday marks lane live (reopen first trading day), pre-open zero blind action; "
    "(b) tonight post-close face (<=10-08 23:59): data-chain full re-arm + REGIME_GUARD v3 first-new-bar enforce (set "
    "BIGMONEY_REGIME_GUARD=enforce before live.paper) + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar "
    "auto-wiring + first-marks verification (marks row + state trial-live + compounding identity) + QDII watch "
    "holiday-delta; (c) O-2215-1 remaining: SUPPORT row awaits bm-b router spec <=10-16; matrix run re-fires when bm-a "
    "REGIME-5 labels land <=10-14; numeric weights review window + 10-21 criteria revisit per order sec.4; (d) "
    "domain-slice consumption tickets follow research-dept cadence (a-stock-data triple-verify + akshare endpoint diff -> "
    "T-173; free-stockdb -> T-104 backfill verify; HiThink key -> data-gap ledger); (e) cloudF row collection window "
    "<=10-14 standing; (f) O-2245 OSS enrollments gate standing; (g) month-boundary first exam 10-31; next 5x = bm-c r745. "
    "[via bm-c r741]")

SUMMARY = ("r741: lineage re-walk clone gate (stale740=0 trio) + QA det-61th 5/5 FIRST TRY + S6 40/40 rc0 first pass "
           "(dualrun streak 51); DEC/ORD both UNCHANGED; unacked=0; smoke 49/49; attrition CLEAN; post_review 48Y/0N/5W.")

VERIFY = ("qa/smoke-r741.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True) + qa/equity-curve-r741.png "
          "66,214B + results/_r741bmc_s6_log.txt 40/40 rc0 (dualrun streak 51) + results/_r741bmc_s05_facts.json double "
          "sweep (DEC EE659451 UNCHANGED / ORD 267B1EA0 UNCHANGED / unacked=0 / inbox 0 / shape-asserted) + "
          "results/_r741bmc_clone_receipt.json (stale740=0, compile OK x3) + attrition CLEAN + post_review "
          "YES=48 NO=0 WAIT=5 + quartet green (pin=5/watchdog/claws)")


def _live_metrics():
    vm = psutil.virtual_memory()
    ram_gb = round(vm.available / (1024 ** 3), 1)
    cpu = psutil.cpu_percent(interval=None)
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                             capture_output=True, timeout=20)
        gpu_free = int(out.stdout.decode("utf-8", "replace").strip().splitlines()[0])
    except Exception:
        gpu_free = None
    return cpu, ram_gb, gpu_free


def main():
    cpu, ram_gb, gpu_free = _live_metrics()
    # 1) round report append (EOL-matched, byte-exact)
    raw = open(RPT, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    if not raw.endswith(eol):
        with open(RPT, "wb") as fh:      # r843 tail-terminator heal before append
            fh.write(raw + eol)
    line = REPORT_LINE.replace("07:3x", NOW[11:16]).encode("utf-8")
    with open(RPT, "ab") as fh:
        fh.write(line + eol)
    # 2) heartbeat
    hb = json.load(open(HB, encoding="utf-8"))
    for k in ("last_seen", "clock_read", "ts", "updated", "updated_at", "last_seen_at",
              "last_run_at", "last_ts", "current_task_at", "last_round_at"):
        hb[k] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["round_no"] = 742
    hb["last_round"] = 741
    hb["round_no_label"] = "round 741 (bm-c)"
    hb["current_task"] = TASK
    hb["latest_artifact"] = ("qa/smoke-r741.md 5/5 + qa/equity-curve-r741.png 66,214B + results/_r741bmc_s6_log.txt "
                             "(40 legs rc0) + results/_r741bmc_clone_receipt.json (stale740=0 trio) + "
                             "results/_r741bmc_s05_facts.json @ " + NOW)
    hb["next_milestone"] = ("tonight post-close: data-chain re-arm + REGIME_GUARD v3 first-new-bar enforce + "
                            "fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks "
                            "verify (<= 10-08 23:59); next 5x = bm-c r745")
    for k in ("did", "verdict", "note", "last_round_summary", "last_action"):
        hb[k] = SUMMARY
    hb["activity_now"] = ACTIVITY
    hb["next"] = NEXT_PTR
    hb["next_pointer"] = NEXT_PTR
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["verify"] = VERIFY
    hb["cpu_pct"] = cpu
    hb["cpu_util_pct"] = cpu
    hb["cpu_idle_pct"] = round(100.0 - cpu, 1)
    for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb"):
        hb[k] = ram_gb
    if gpu_free is not None:
        for k in ("gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
                  "gpu_vram_free_mb", "gpu_free_mb", "gpu_free_mib", "gpu_idle_mib", "gpu_idle_mb"):
            if k in hb:
                hb[k] = gpu_free
    json.dump(hb, open(HB, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    # 3) state
    st = json.load(open(ST, encoding="utf-8"))
    for k in ("clock_read", "last_seen", "ts", "updated", "updated_at", "last_run_at",
              "last_seen_at", "current_task_at", "last_round_at", "last_round_ts",
              "last_decisions_read_at"):
        st[k] = NOW
    st["heartbeat_epoch_utc"] = EPOCH
    st["round_no"] = 742
    st["last_round"] = 741
    st["round_no_label"] = "round 741 (bm-c)"
    st["current_task"] = TASK
    st["latest_artifact"] = hb["latest_artifact"]
    st["next_milestone"] = hb["next_milestone"]
    for k in ("did", "verdict", "note", "last_round_summary", "last_action"):
        st[k] = SUMMARY
    st["activity_now"] = ACTIVITY
    st["next"] = NEXT_PTR
    st["next_pointer"] = NEXT_PTR
    st["idle_rounds"] = 0
    st["agenda_starved"] = False
    st["verify"] = VERIFY
    st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r741 sweeps "
                                     "= UNCHANGED 267B1EA0 zero delta zero consumption; hex-case comparison normalized "
                                     "per r711 pit law; facts-driven from results/_r741bmc_s05_facts.json, 40hex "
                                     "shape-asserted, never hand-typed (r583 S4 law)")
    st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r741 "
                                       "sweeps = UNCHANGED EE659451 zero delta zero action; facts-driven from "
                                       "results/_r741bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)")
    st["cpu_pct"] = cpu
    st["cpu_idle_pct"] = round(100.0 - cpu, 1)
    for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb"):
        if k in st:
            st[k] = ram_gb
    if gpu_free is not None:
        for k in ("gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_free_mib", "gpu_free_mb"):
            if k in st:
                st[k] = gpu_free
    json.dump(st, open(ST, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    # 4) self-verify (R170/R178/R262)
    hb2 = json.load(open(HB, encoding="utf-8"))
    st2 = json.load(open(ST, encoding="utf-8"))
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int (R170/R178)"
    assert isinstance(st2["heartbeat_epoch_utc"], int), "state epoch not int"
    assert hb2["clock_read"][10] == "T", "clock_read T-sep (R262)"
    print("bookkeeping ok: hb epoch", hb2["heartbeat_epoch_utc"],
          "state last_round", st2["last_round"], "-> next round_no", st2["round_no"],
          "clock", hb2["clock_read"], "cpu", cpu, "ram_gb", ram_gb, "gpu_free", gpu_free)


if __name__ == "__main__":
    main()
