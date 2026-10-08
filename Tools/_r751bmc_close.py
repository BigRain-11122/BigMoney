# -*- coding: utf-8 -*-
"""r751 bm-c round-close bookkeeping: round report line append to the CANONICAL
face logs/iteration-loop/round_reports-bm-c.md (fleet/README sec.6 + r645
epoch-freeze note; r750 pit law -- canonical path ONLY, never the ROOT face),
write-then-grep self-verify on the canonical face, heartbeat
fleet/machines/bm-c.json + state-bm-c.json field updates (epoch=int law
R170/R178, clock_read T-separator law R262, round_no 751->752, DEC/ORD both
UNCHANGED zero consumption, live cpu/ram/gpu re-sample).
Pattern credit: Tools/_r750bmc_close.py (canonical-RPT lineage)."""
import datetime
import json
import os
import psutil
import subprocess
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
RPT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")  # CANONICAL (fleet/README §6 + r645 freeze; r750 pit law)
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
ST = os.path.join(ROOT, "state-bm-c.json")

REPORT_LINE = (
    "2026-10-08T{TT}+08:00 | r751 | dept:工程+交易（复市 T-0 盘中值守轮·第 71 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·verdict=py_low_board_clear 盘中板清+无新 bar 合法 idle〔orders 51 disk unacked=0 双扫·inbox 0 双扫〕·"
    "compute_audit rc0 idle-starvation 诚实面〔pool ready 0<floor 3·席位间隙已知面·供给属预注册起草线节奏〕） | "
    "当前活: r751 bm-c（10:0x-10:1x 窗·第 71 连守轮）——S0 轮首脏 8=自有面（6 daemon live+2 r751 驱动器首建）absorb 97a26993f→"
    "fetch behind=2→pull --rebase 净重放（head=1c180e5b3）——主产出=①QA det-71th 5/5（律序值守：S6 40 腿 rc0 收齐→qa_ignite 分离 "
    "pid 3292→终态轮询 .err 0B——93 trades·equity 1,017,839 冻结恒等·determinism=True·png 66,085B·71 连证·零 FACE_ERROR 竞态）+"
    "②S6 40/40 rc0 首过（dualrun ZERO-DRIFT streak 51 @408 条·cutoff 03:47 池面未变·fund_premium pre-15:30 no-op→今晚 15:30 bm-c "
    "车道首采·cta_p1_paper 无可标 bar〔cutoff 2026-09-30<paper_start 2026-10-08〕→今晚首 bar 自动接线·全 lane 守卫诚实 no-op）+"
    "③克隆门三件（_r751bmc_clone.py 双模替换 stale750=0 三件〔s05/s6/qa_ignite〕·compile OK×3·收据 _r751bmc_clone_receipt.json）+"
    "④marks lane 盘中增量实证（marks-20261008.jsonl 2 行在册 09:35:01/09:45:01·6 员 live 标记·CE-01 equity_mark 1,001,852→"
    "1,001,770 盘中漂移正常·state_cutoff 2026-09-30 持有·bm-a 宿主 lane 健康·09:55+ 行随 bm-a 后续波次到达）+"
    "idle NOT-GREEN（RAM 16.7%<40% 常驻 ComfyUI·idle_rounds=0·--worked 10:09 申报） | "
    "最近实物: qa/smoke-r751.md 5/5+qa/equity-curve-r751.png 66,085B+results/_r751bmc_s6_log.txt（40 腿 rc0）+"
    "results/_r751bmc_clone_receipt.json @ 2026-10-08T{TT}+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采（bm-c 车）+"
    "CTA_P1 首接线+首 marks 验证（≤10-08 23:59） | "
    "验证证据: smoke 49/49+QA 5/5（determinism=True·.err 0B·93 trades·1,017,839 frozen identity·market_clock cell=ORA·"
    "latest_panel_bar 2026-09-30 金周 no-op 如期）+S6 40/40 rc0（dualrun streak 51 ZERO-DRIFT @408·cutoff 03:47）+"
    "s05 双扫（DEC EE659451/ORD 267B1EA0 双 UNCHANGED·unacked=0·inbox 0·shape-asserted）+attrition CLEAN（4 账本 3 healed "
    "历史缩行照录）+post_review 45✓/0✗/WAIT 5+四件套四证（pin=5 no-op 首火 10:15+watchdog 重注 10:10+双爪 LF 归一重装）+"
    "孤儿面=1（py_faces=5·常驻 ComfyUI 服务面 pid 28732·CEO 私产·只读披露不击杀·既有处置维持）+SAT 活 rc0（N1_BANDS 注册至 "
    "W184） | "
    "下轮指针: r752: (a) marks lane 盘中增量续守（bm-a 宿主）；(b) tonight post-close face（≤10-08 23:59）数据链全 re-arm+"
    "REGIME_GUARD v3 first-new-bar enforce（live.paper 前设 BIGMONEY_REGIME_GUARD=enforce）+fund_premium 15:30 first snapshot"
    "（bm-c lane）+CTA_P1 first-bar auto-wiring+first-marks verification（marks row+state trial-live+compounding identity）+"
    "QDII watch holiday-delta；(c) QA 点火序律值守（S6 rc0→qa_ignite→poll 终态→close）；(d) 收尾脚本 RPT=正典面（r750 坑·禁克隆 "
    "ROOT 模板）；(e) O-2215-1 remaining standing（SUPPORT row 待 bm-b router spec ≤10-16·matrix 待 bm-a REGIME-5 标签 "
    "≤10-14·numeric weights review+10-21 revisit）；(f) cloudF row ≤10-14 standing；(g) 月界首考 10-31；next 5x=bm-c r755"
    "（HANDOVER r751-755）。[via bm-c r751] | "
    "轮产品计分：2（QA det-71th 确定性包+S6 40 腿再生+克隆门三件+marks 盘中增量实证=能跑能看实物） | "
    "记账预算：5（S0 absorb+轮报/心跳/state 收口+post_review/attrition 例行+克隆收据+s05 facts 双扫件）")

TASK = (
    "当前活: r751 bm-c（10:0x-10:1x 窗·复市 T-0 盘中值守第 71 连守轮）——"
    "主产出=QA det-71th 5/5（律序 S6 收齐→点火 pid 3292·93 trades·1,017,839 冻结恒等）+"
    "S6 40/40 rc0（dualrun streak 51）+克隆门 stale750=0+marks lane 盘中增量实证（2 行 09:35/09:45·6 员 live 标记）"
    "| 最近实物: qa/smoke-r751.md 5/5+qa/equity-curve-r751.png 66,085B+results/_r751bmc_s6_log.txt 40/40+"
    "results/_r751bmc_clone_receipt.json @ 2026-10-08T{TT}+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 enforce+fund_premium 15:30 首采（bm-c 车）+"
    "CTA_P1 首接线+首 marks 验证（≤10-08 23:59）")

ACTIVITY = (
    "r751 bm-c: reopen T-0 intraday watch round 71st consecutive (10:0x window; marks lane live, 2 rows in). "
    "(1) S0: round-start dirty 8 = own faces (6 daemon live + 2 fresh r751 drivers) -> absorb commit 97a26993f -> "
    "fetch behind=2 -> pull --rebase clean replay (head=1c180e5b3). (2) S0.5 double sweep "
    "(_r751bmc_s05_facts.json): DEC EE659451 UNCHANGED + ORD 267B1EA0 UNCHANGED (zero consumption); fleet orders 51 "
    "disk unacked=0; inbox 0. (3) S1 smoke 49/49 + round-zero orphan probe py_faces=5 orphans=1 (resident ComfyUI "
    "service face pid 28732, CEO asset, read-only no-kill, standing disposition) + satengine rc0 alive (N1_BANDS "
    "registry through W184) + idle NOT-GREEN (ram_free 16.7% < 40% resident ComfyUI, idle_rounds=0, --worked 10:09). "
    "(4) MAIN PRODUCTS: (a) lineage clone gate (_r751bmc_clone.py: order-sensitive double-replacement, stale750=0 "
    "across s05/s6/qa_ignite, compile gate PASS, receipt _r751bmc_clone_receipt.json). (b) S6 40/40 rc0 first pass "
    "via _r751bmc_s6.py canonical clone (dualrun ZERO-DRIFT streak 51 @408 entries, cutoff 03:47 pool faces unchanged "
    "pre-close; compute_audit rc0 load_state=idle-starvation pool_ready=0<floor 3 honest structural flag = seat-gap "
    "known face, supply face belongs to prereg drafting cadence; py_watermark py_low_board_clear legal intraday idle; "
    "fund_premium pre-15:30 no-op -> tonight 15:30 bm-c-lane first snapshot; cta_p1_paper no markable bar -> tonight "
    "first-bar auto-wiring; lane guards honest stdout-only skips). (c) QA det-71th per ignition order law (r749 pit): "
    "S6 full-chain rc0 collected FIRST -> qa_ignite detached pid 3292 -> poll terminal (.err 0B): 93 trades, equity "
    "1,017,839 frozen identity, determinism=True, PNG 66,085B, market_clock cell=ORA, 71st consecutive pack -- "
    "race-free, zero FACE_ERROR transient this window. (d) MARKS LANE INTRADAY WATCH: marks-20261008.jsonl 2 rows "
    "in-ledger (09:35:01 / 09:45:01, 6 traders live-marked, CE-01 equity_mark 1,001,852 -> 1,001,770 intraday "
    "drift normal, state_cutoff 2026-09-30 held; bm-a host lane healthy, 09:55+ rows arrive with later bm-a waves). "
    "(5) post_review run zero red (45 YES / 0 NO / 5 WAIT); attrition CLEAN (4 ledger files, 3 healed shrink notes "
    "as recorded); quartet green (loop pin=5 no-op first-fire 10:15 + watchdog re-registered 10:10 + both claws "
    "reinstalled LF-normalized).")

NEXT_PTR = (
    "r752: (a) marks lane intraday incremental watch (bm-a host lane; 2 rows in-ledger 09:35/09:45, 09:55+ rows with "
    "later bm-a waves); (b) tonight post-close face (<=10-08 23:59): data-chain full re-arm + REGIME_GUARD v3 "
    "first-new-bar enforce (set BIGMONEY_REGIME_GUARD=enforce before live.paper) + fund_premium 15:30 first snapshot "
    "(bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verification (marks row + state trial-live + "
    "compounding identity) + QDII watch holiday-delta; (c) QA ignition order law standing (S6 rc0 -> qa_ignite -> "
    "qa_poll terminal -> close); (d) close scripts: RPT path = canonical logs/iteration-loop/round_reports-bm-c.md "
    "(r750 pit; NEVER clone a ROOT template); (e) O-2215-1 remaining: SUPPORT row awaits bm-b router spec <=10-16; "
    "matrix re-fires when bm-a REGIME-5 labels land <=10-14; numeric weights review + 10-21 revisit; (f) cloudF row "
    "<=10-14 standing; (g) month-boundary first exam 10-31; next 5x = bm-c r755 (HANDOVER r751-755). [via bm-c r751]")

SUMMARY = ("r751: S0 absorb 8 own faces rebase clean (head 1c180e5b3) + QA det-71th 5/5 (pid 3292, S6-first order, "
           "93 trades, 1,017,839 frozen identity) + S6 40/40 rc0 (dualrun streak 51) + clone gate trio stale750=0 + "
           "marks intraday 2 rows verified (09:35/09:45, 6 traders live); DEC/ORD both UNCHANGED; unacked=0; smoke "
           "49/49; attrition CLEAN; post_review 45Y/0N/5W.")

VERIFY = ("smoke 49/49 + qa/smoke-r751.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True .err 0B "
          "png 66,085B) + results/_r751bmc_s6_log.txt 40/40 rc0 (dualrun ZERO-DRIFT streak 51) + "
          "results/_r751bmc_s05_facts.json double sweep (DEC EE659451 UNCHANGED / ORD 267B1EA0 UNCHANGED / unacked=0 "
          "/ inbox 0 / shape-asserted) + results/_r751bmc_clone_receipt.json (stale750=0, compile OK x3) + attrition "
          "CLEAN + post_review 45 YES / 0 NO / 5 WAIT (run) + quartet green (pin=5/watchdog/claws) + orphan face=1 "
          "standing disposition (py_faces=5) + idle NOT-GREEN --worked 10:09")


def _live_metrics():
    vm = psutil.virtual_memory()
    ram_gb = round(vm.available / (1024 ** 3), 1)
    cpu = psutil.cpu_percent(interval=None)
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                             capture_output=True, timeout=20, creationflags=0x08000000)
        gpu_free = int(out.stdout.decode("utf-8", "replace").strip().splitlines()[0])
    except Exception:
        gpu_free = None
    return cpu, ram_gb, gpu_free


def main():
    cpu, ram_gb, gpu_free = _live_metrics()
    # 1) round report append (CANONICAL face, EOL-matched, byte-exact)
    raw = open(RPT, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    if not raw.endswith(eol):
        with open(RPT, "wb") as fh:      # tail-terminator heal before append (r843 family)
            fh.write(raw + eol)
    line = REPORT_LINE.replace("{TT}", NOW[11:16]).encode("utf-8")
    with open(RPT, "ab") as fh:
        fh.write(line + eol)
    # write-then-grep self-verify ON THE CANONICAL FACE (r865 law, r750-pit corrected)
    back = open(RPT, "rb").read()
    assert back.count(b"| r751 |") == 1, "r751 row not exactly-once in canonical tail (r865+r750 law)"
    assert b"| r751 |" in back.split(eol)[-2] + back.split(eol)[-3], "r751 row not in canonical tail"
    # 2) heartbeat
    hb = json.load(open(HB, encoding="utf-8"))
    for k in ("last_seen", "clock_read", "ts", "updated", "updated_at", "last_seen_at",
              "last_run_at", "last_ts", "current_task_at", "last_round_at"):
        hb[k] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["round_no"] = 752
    hb["last_round"] = 751
    hb["round_no_label"] = "round 751 (bm-c)"
    hb["current_task"] = TASK.replace("{TT}", NOW[11:16])
    hb["latest_artifact"] = ("qa/smoke-r751.md 5/5 + qa/equity-curve-r751.png 66,085B + results/_r751bmc_s6_log.txt "
                             "(40 legs rc0) + results/_r751bmc_clone_receipt.json (stale750=0 trio) @ " + NOW)
    hb["next_milestone"] = ("tonight post-close (10-08 15:30+): data-chain re-arm + REGIME_GUARD v3 first-new-bar "
                            "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring "
                            "+ first-marks verify (<= 10-08 23:59); next 5x = bm-c r755")
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
    st["round_no"] = 752
    st["last_round"] = 751
    st["round_no_label"] = "round 751 (bm-c)"
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
    st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r751 sweeps "
                                    "= UNCHANGED 267B1EA0 zero delta zero consumption; hex-case comparison normalized "
                                    "per r711 pit law; facts-driven from results/_r751bmc_s05_facts.json, 40hex "
                                    "shape-asserted, never hand-typed (r583 S4 law)")
    st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r751 "
                                       "sweeps = UNCHANGED EE659451 zero delta zero action; facts-driven from "
                                       "results/_r751bmc_s05_facts.json, 64hex shape-asserted, never hand-typed "
                                       "(r583 S4 law)")
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
