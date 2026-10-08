# -*- coding: utf-8 -*-
"""r748 bm-c round-close bookkeeping: round report line append (EOL-matched),
heartbeat fleet/machines/bm-c.json + state-bm-c.json field updates
(epoch=int law R170/R178, clock_read T-separator law R262, round_no 748->749,
DEC/ORD both UNCHANGED zero consumption, live cpu/ram/gpu re-sample).
Pattern credit: Tools/_r747bmc_close.py (canonical clone chain)."""
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
    "2026-10-08T09:1x+08:00 | r748 | dept:工程+交易（复市 T-0 盘前→开盘初窗值守轮·第 68 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane healthy·verdict=py_low_board_clear=板清+开盘前无新 bar 合法 idle〔orders 51 disk "
    "unacked=0 双扫·inbox 0 双扫〕） | "
    "当前活: r748 bm-c（09:0x-09:1x 窗·复市首交易日 09:15 集合竞价前零盲动）——S0 absorb 7adf03101（7 自有面=round-zero "
    "orphan-probe+autofill+dispatcher+idle 对+saturation×2）→pull --rebase 落 bm-a r872 f4071a955（rebase 1/1 净）——"
    "主产出=①QA det-68th 5/5（分离 pid 35256·.err 0B·93 trades·equity 1,017,839 冻结恒等·determinism=True·png 66,109B·"
    "68 连证）+②S6 40/40 rc0 首过（dualrun ZERO-DRIFT streak 52 @408 条·cutoff 03:47 池面未变·fund_premium pre-15:30 "
    "no-op→今日 15:30 bm-c 车道首采·cta_p1_paper 无可标 bar→今晚首 bar 自动接线）+③血统克隆门（_r748bmc_clone.py 双模替换 "
    "stale747=0 三件+compile 门全过·收据 _r748bmc_clone_receipt.json）+④marks lane live watch（r747 指针(a) 主任务：marks "
    "道=bm-a 宿主 R108 正典·bm-c 本机无该任务=预期态；假日证据链复核=10-01..10-07 日 marks+settle 双面全落〔sina 假日返昨 "
    "收→marks 冻结 09-30 收盘恒等·state_cutoff 2026-09-30 全程正确持有〕·bm-a 心跳 08:51 fresh r871→872 在飞；今日 "
    "marks-20261008.jsonl 首火 09:25/09:30 窗未至=盘前零盲动·落盘验证→r749）+自愈四件套全绿（loop pin=5 no-op 首火 09:15"
    "+watchdog 重注 09:12+双爪 LF 归一重装）+attrition CLEAN（4 账本 healed 历史缩行照录）+post_review 零红（45✓/0✗ 重 "
    "derive）+孤儿面=1（常驻 ComfyUI 服务面 pid 28732·CEO 私产·只读披露不击杀·既有处置维持）+idle NOT-GREEN（RAM 17.0%<40%"
    "常驻 ComfyUI·idle_rounds=0·本轮实工=克隆门+QA+S6） | "
    "最近实物: qa/smoke-r748.md 5/5（93 trades·equity 1,017,839 冻结恒等·determinism=True）+qa/equity-curve-r748.png "
    "66,109B+results/_r748bmc_s6_log.txt（40 腿 rc0）+results/_r748bmc_clone_receipt.json @ 2026-10-08T09:1x+08:00 | "
    "下个里程碑: r749（09:25+ 窗）marks-20261008.jsonl 首落盘验证（真 session 价 vs 假日恒等 marks 对照）；今晚盘后"
    "（10-08 15:30+）数据链全门 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采（bm-c 车）+CTA_P1 首接线"
    "+首 marks 验证（≤10-08 23:59）；下一 5x=bm-c r750 | "
    "验证证据: smoke 49/49+qa/smoke-r748.md 5/5（determinism=True·93 trades·1,017,839 frozen identity·market_clock cell=ORA"
    "·latest_panel_bar 2026-09-30 金周 no-op 如期）+qa/equity-curve-r748.png 66,109B+results/_r748bmc_s6_log.txt（40 legs rc0"
    "·dualrun streak 52 ZERO-DRIFT）+results/_r748bmc_s05_facts.json 双扫（DEC EE659451/ORD 267B1EA0 双 UNCHANGED·unacked=0"
    "·inbox 0·shape-asserted）+results/_attrition_guard_scan.json CLEAN+quartet 四证（pin=5 no-op+watchdog 重注+双爪 LF 归一）"
    "+克隆门收据 _r748bmc_clone_receipt.json（stale747=0·compile OK×3）+post_review 重 derive（45✓/0✗·零红） | "
    "下轮指针: r749: (a) 09:25/09:35+ marks-20261008.jsonl 落盘验证（首 intraday marks 真 session_open/mark 值对照假日恒等面"
    "·marks lane live watch 续守）；(b) tonight post-close face（≤10-08 23:59）: data-chain full re-arm+REGIME_GUARD v3 "
    "first-new-bar enforce（首新 bar 前设 BIGMONEY_REGIME_GUARD=enforce）+fund_premium 15:30 first snapshot（bm-c lane）"
    "+CTA_P1 first-bar auto-wiring+first-marks verification（marks 1 行+state trial-live+compounding identity）+QDII watch "
    "holiday-delta；(c) O-2215-1 remaining: SUPPORT row 候 bm-b router spec（≤10-16）+矩阵 run refire 待 bm-a REGIME-5 "
    "标签（≤10-14）+numeric weights review window+10-21 criteria revisit per order sec.4；(d) 域切片消费票随研究部节奏"
    "（a-stock-data 三验→T-173·free-stockdb→T-104·HiThink key→数据缺口台账）；(e) cloudF row ≤10-14 standing；"
    "(f) O-2245 OSS enrollments gate standing；(g) 月界首考 10-31；next 5x=bm-c r750（HANDOVER r746-750）。[via bm-c r748] | "
    "轮产品计分：2（QA 68th 确定性包+S6 40 腿再生+克隆门三件+marks 假日证据链复核=能跑能看实物） | "
    "记账预算：5（state+心跳+轮报+attrition/post_review 例行扫描件+克隆收据）")

TASK = (
    "当前活: r748 bm-c（09:0x-09:1x 窗·复市 T-0 盘前→开盘初窗值守第 68 连守轮·09:15 前零盲动）——"
    "主产出=QA det-68th 5/5（pid 35256·93 trades·1,017,839 冻结恒等）+S6 40/40 rc0 首过（dualrun streak 52·"
    "fund_premium/CTA_P1 今晚首采/首接线）+血统克隆门三件（stale747=0）+marks lane 假日证据链复核（bm-a 宿主 daemon "
    "10-01..10-07 日面全落·state_cutoff 2026-09-30 正确持有·今日首火 09:25 窗未至→r749 落盘验证）+S0 absorb 7adf03101 "
    "rebase 落 bm-a r872+自愈四件套全绿+attrition CLEAN+post_review 零红（45✓/0✗）"
    "| 最近实物: qa/smoke-r748.md 5/5+qa/equity-curve-r748.png 66,109B+results/_r748bmc_s6_log.txt"
    "+results/_r748bmc_clone_receipt.json @ 2026-10-08T09:1x+08:00 | "
    "下个里程碑: r749（09:25+）marks-20261008.jsonl 首落盘验证；今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 "
    "enforce+fund_premium 首采（bm-c 车）+CTA_P1 首接线+首 marks 验证（≤10-08 23:59）；下一 5x=bm-c r750")

ACTIVITY = (
    "r748 bm-c: pre-open -> early-session watch round 68th consecutive (09:0x-09:1x window; reopen T-0, call auction "
    "09:15). (1) S0: round-start dirty 7 = own daemon live faces (round-zero orphan probe + autofill + dispatcher + "
    "idle pair + saturation x2) -> absorb commit 7adf03101 -> pull --rebase onto bm-a r872 f4071a955 (rebase 1/1 "
    "clean). (2) S0.5 sweeps (round-start + close double-scan): DEC EE659451 UNCHANGED + ORD 267B1EA0 UNCHANGED "
    "(zero consumption); fleet orders 51 disk unacked=0 both sweeps; inbox 0 both sweeps. (3) S1 smoke 49/49 + QA "
    "det-68th determinism pack 5/5 (detached pid 35256, .err 0B): 93 trades, equity 1,017,839 frozen identity, "
    "determinism=True, png 66,109B, market_clock cell=ORA, latest_panel_bar 2026-09-30 golden-week no-op expected. "
    "(4) S3: orphan probe py_faces=4 orphans=1 (resident ComfyUI service face pid 28732, CEO asset, read-only "
    "disclosure no-kill, standing disposition; per-machine suffix face _orphan_face_probe.bm-c.json 09:05 fresh); "
    "satengine rc0 alive (N1_BANDS registry readback normal through W183); watermark red=false lane healthy "
    "verdict=py_low_board_clear (open_tickets=0, bandit=0, bars absent pre-open, window n=2, legal idle; tasks board "
    "0 open / 46 claimed = other-machine in-flight lanes; job_list 0); idle trigger NOT-GREEN (RAM 17.0% free, "
    "resident ComfyUI), idle_rounds=0, real work this round (clone gate + QA + S6). (5) MAIN PRODUCTS: (a) lineage "
    "clone gate (_r748bmc_clone.py from r747 originals: double-replacement, stale747=0 across s05/s6/qa_ignite, "
    "compile gate PASS, receipt _r748bmc_clone_receipt.json). (b) marks lane live watch = r747 pointer (a): lane "
    "hosted on bm-a (R108 canon; bm-c has no such task = expected); holiday evidence chain verified (daily marks+"
    "settle faces 10-01..10-07 all landed, sina holiday quotes freeze marks at 09-30 closes, state_cutoff 2026-09-30 "
    "correctly held all week); bm-a heartbeat fresh 08:51 (r871->872 in flight); today marks-20261008.jsonl first "
    "fire 09:25/09:30 window not yet reached at round close 09:1x -> pre-open zero blind action, landing "
    "verification -> r749. (c) S6 40/40 rc0 first pass via Tools/_r748bmc_s6.py canonical clone (dualrun ZERO-DRIFT "
    "streak 52 @408 entries, cutoff 03:47 pool faces unchanged pre-open; py_watermark py_low_board_clear legal-idle; "
    "fund_premium pre-15:30 no-op -> today 15:30 bm-c-lane first snapshot; cta_p1_paper no markable bar -> tonight "
    "first-bar auto-wiring). (6) post_review deterministic re-derive zero red (45 YES / 0 NO, report results/"
    "post_review/REPORT-20261008.md); attrition CLEAN (4 ledger files, healed historical shrink notes). (7) quartet "
    "green (loop pin=5 no-op first-fire 09:15 + watchdog re-registered 09:12 + both claws reinstalled "
    "LF-normalized). (8) No new pit-domain lesson this round (all flows canonical-path, zero in-window self-caught "
    "misses) -> zero CODELY append.")

NEXT_PTR = (
    "r749: (a) 09:25/09:35+ marks-20261008.jsonl landing verification (first intraday marks with fresh session "
    "prices vs holiday-constant identity; marks lane live watch continues through session); (b) tonight post-close "
    "face (<=10-08 23:59): data-chain full re-arm + REGIME_GUARD v3 first-new-bar enforce (set "
    "BIGMONEY_REGIME_GUARD=enforce before live.paper) + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 "
    "first-bar auto-wiring + first-marks verification (marks row + state trial-live + compounding identity) + QDII "
    "watch holiday-delta; (c) O-2215-1 remaining: SUPPORT row awaits bm-b router spec <=10-16; matrix run re-fires "
    "when bm-a REGIME-5 labels land <=10-14; numeric weights review window + 10-21 criteria revisit per order sec.4; "
    "(d) domain-slice consumption tickets follow research-dept cadence (a-stock-data triple-verify -> T-173; "
    "free-stockdb -> T-104 backfill verify; HiThink key -> data-gap ledger); (e) cloudF row collection window "
    "<=10-14 standing; (f) O-2245 OSS enrollments gate standing; (g) month-boundary first exam 10-31; next 5x = "
    "bm-c r750 (HANDOVER r746-750). [via bm-c r748]")

SUMMARY = ("r748: S0 absorb 7adf03101 rebase onto bm-a r872 + lineage clone gate (stale747=0 trio) + QA det-68th 5/5 "
           "(pid 35256) + S6 40/40 rc0 first pass (dualrun streak 52) + marks holiday evidence chain verified (state_cutoff "
           "2026-09-30 held, first fire 09:25 pending -> r749); DEC/ORD both UNCHANGED; unacked=0; smoke 49/49; "
           "attrition CLEAN; post_review 45Y/0N.")

VERIFY = ("smoke 49/49 + qa/smoke-r748.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True) + "
          "qa/equity-curve-r748.png 66,109B + results/_r748bmc_s6_log.txt 40/40 rc0 (dualrun streak 52) + "
          "results/_r748bmc_s05_facts.json double sweep (DEC EE659451 UNCHANGED / ORD 267B1EA0 UNCHANGED / "
          "unacked=0 / inbox 0 / shape-asserted) + results/_r748bmc_clone_receipt.json (stale747=0, compile OK x3) + "
          "attrition CLEAN + post_review 45 YES / 0 NO (deterministic re-derive) + quartet green "
          "(pin=5/watchdog/claws)")


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
        with open(RPT, "wb") as fh:      # tail-terminator heal before append (r843 family)
            fh.write(raw + eol)
    line = REPORT_LINE.replace("09:1x", NOW[11:16]).encode("utf-8")
    with open(RPT, "ab") as fh:
        fh.write(line + eol)
    # 2) heartbeat
    hb = json.load(open(HB, encoding="utf-8"))
    for k in ("last_seen", "clock_read", "ts", "updated", "updated_at", "last_seen_at",
              "last_run_at", "last_ts", "current_task_at", "last_round_at"):
        hb[k] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["round_no"] = 749
    hb["last_round"] = 748
    hb["round_no_label"] = "round 748 (bm-c)"
    hb["current_task"] = TASK.replace("09:1x", NOW[11:16])
    hb["latest_artifact"] = ("qa/smoke-r748.md 5/5 + qa/equity-curve-r748.png 66,109B + results/_r748bmc_s6_log.txt "
                             "(40 legs rc0) + results/_r748bmc_clone_receipt.json (stale747=0 trio) + "
                             "results/_r748bmc_s05_facts.json @ " + NOW)
    hb["next_milestone"] = ("r749 (09:25+ window): marks-20261008.jsonl first landing verification; tonight "
                            "post-close: data-chain re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium "
                            "15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verify "
                            "(<= 10-08 23:59); next 5x = bm-c r750")
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
    st["round_no"] = 749
    st["last_round"] = 748
    st["round_no_label"] = "round 748 (bm-c)"
    st["current_task"] = hb["current_task"]
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
    st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r748 sweeps "
                                    "= UNCHANGED 267B1EA0 zero delta zero consumption; hex-case comparison normalized "
                                    "per r711 pit law; facts-driven from results/_r748bmc_s05_facts.json, 40hex "
                                    "shape-asserted, never hand-typed (r583 S4 law)")
    st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r748 "
                                       "sweeps = UNCHANGED EE659451 zero delta zero action; facts-driven from "
                                       "results/_r748bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)")
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
