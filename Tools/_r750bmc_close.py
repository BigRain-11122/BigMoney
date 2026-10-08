# -*- coding: utf-8 -*-
"""r750 bm-c round-close bookkeeping: round report line append to the CANONICAL
face logs/iteration-loop/round_reports-bm-c.md (fleet/README sec.6 + r645
epoch-freeze note; r750 pit -- the r749 close clone had wrongly adopted bm-a's
r844/r865 ROOT-path law; healed this window), write-then-grep self-verify on
the canonical face, heartbeat fleet/machines/bm-c.json + state-bm-c.json field
updates (epoch=int law R170/R178, clock_read T-separator law R262, round_no
750->751, DEC/ORD both UNCHANGED zero consumption, live cpu/ram/gpu re-sample).
Pattern credit: Tools/_r749bmc_close.py (with r750 canonical-RPT fix applied)."""
import datetime
import json
import os
import psutil
import subprocess
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
RPT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")  # CANONICAL (fleet/README §6 + r645 freeze; r750 pit heal)
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
ST = os.path.join(ROOT, "state-bm-c.json")

REPORT_LINE = (
    "2026-10-08T{TT}+08:00 | r750 | dept:工程+交易（复市 T-0 开盘初窗值守轮·第 70 bm-c 连守轮·5x HANDOVER 核对轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·py_low_board_clear 开盘初窗板清+无新 bar 合法 idle〔orders 51 disk unacked=0 双扫·inbox 0 双扫〕·"
    "compute_audit rc0 idle-starvation 诚实面〔pool ready 0<floor 3·席位间隙已知面·W16-JUDGE 已收口·供给属预注册起草线节奏〕） | "
    "当前活: r750 bm-c（09:4x-09:5x 窗·第 70 连守轮）——S0 轮首脏 6=自有 daemon 面 absorb f9cf2f5ef→pull --rebase 落 bm-a r873"
    "（rebase 1/1 净·marks-20261008.jsonl 随波落地）——主产出=①QA det-70th 5/5（**新律序首跑**：S6 40 腿 rc0 收齐→qa_ignite 分离 "
    "pid 31484→终态轮询 .err 0B——93 trades·equity 1,017,839 冻结恒等·determinism=True·png 66,211B·70 连证·零 FACE_ERROR 竞态）+"
    "②marks-20261008.jsonl 落地实证（r749 指针(a) 闭：bm-a r873 1499a55e7 携带入仓·4,537B·ts 09:35:01·6 员 live 标记·"
    "state_cutoff 2026-09-30·r747 escalation 免）+③轮账本跨面治愈（r749 行落 ROOT 冻结面=bm-a r844 律跨机误用·r750 r865-heal 镜像 "
    "verbatim 复迁正典面 logs/iteration-loop/+heal 注记行·ROOT 面不动 git 史保全·收据 _r750bmc_ledger_heal_receipt.json·"
    "坑直写 pit-protocol-lane.md·本 close RPT 已归正典路径+grep 正典自验）+④克隆门三件（_r750bmc_clone.py 双模替换 stale749=0·"
    "compile OK×3·收据 _r750bmc_clone_receipt.json）+⑤5x HANDOVER 核对行（r746-750 窗）+CEO 面同日幂等再生 | "
    "最近实物: qa/smoke-r750.md 5/5+qa/equity-curve-r750.png 66,211B+results/_r750bmc_s6_log.txt（40 腿 rc0）+"
    "results/_r750bmc_ledger_heal_receipt.json+research/pit-protocol-lane.md r750 条 @ 2026-10-08T{TT}+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采（bm-c 车）+"
    "CTA_P1 首接线+首 marks 验证（≤10-08 23:59） | "
    "验证证据: smoke 49/49+QA 5/5（determinism=True·.err 0B·面恒等）+S6 40/40 rc0（dualrun ZERO-DRIFT streak 51 @408·cutoff 03:47）+"
    "s05 双扫（DEC EE659451/ORD 267B1EA0 双 UNCHANGED·unacked=0·inbox 0·shape-asserted）+attrition CLEAN（healed 缩行照录）+"
    "post_review 45✓/0✗/WAIT 5+四件套四证（pin=5 no-op/watchdog 重注/双爪 LF 归一）+孤儿面=1（常驻 ComfyUI 服务面 pid 28732·"
    "CEO 私产·只读披露不击杀·既有处置维持）+SAT 活 rc0+idle NOT-GREEN（ram 15.1%<40% 常驻 ComfyUI·idle_rounds=0·--worked） | "
    "下轮指针: r751: (a) marks lane 盘中增量续守（bm-a 宿主·首笔已落）；(b) tonight post-close face（≤10-08 23:59）数据链全 re-arm+"
    "REGIME_GUARD v3 first-new-bar enforce（live.paper 前设 BIGMONEY_REGIME_GUARD=enforce）+fund_premium 15:30 first snapshot"
    "（bm-c lane）+CTA_P1 first-bar auto-wiring+first-marks verification（marks row+state trial-live+compounding identity）+"
    "QDII watch holiday-delta；(c) QA 点火序律值守（S6 rc0→qa_ignite→poll 终态→close）；(d) 收尾脚本 RPT=正典面（r750 坑·禁克隆 r749 "
    "ROOT 模板）；(e) O-2215-1 remaining standing（SUPPORT row 待 bm-b router spec ≤10-16·matrix 待 bm-a REGIME-5 标签 ≤10-14·"
    "numeric weights review+10-21 revisit）；(f) cloudF row ≤10-14 standing；(g) 月界首考 10-31。[via bm-c r750] | "
    "轮产品计分：2（QA det-70th 确定性包+marks 落地验证+跨面治愈+HANDOVER 行=能跑能看实物） | "
    "记账预算：5（S0 absorb+轮报/心跳/state 收口+post_review/attrition 例行+克隆收据+s05 facts 双扫件）")

TASK = (
    "当前活: r750 bm-c（09:4x-09:5x 窗·复市 T-0 开盘初窗值守第 70 连守轮）——"
    "主产出=QA det-70th 5/5（新律序 S6 收齐→点火·pid 31484·93 trades·1,017,839 冻结恒等）+"
    "marks-20261008.jsonl 落地实证（bm-a r873 携带·指针(a) 闭）+轮账本跨面治愈（r749 行 verbatim 复迁正典面）+"
    "克隆门 stale749=0+5x HANDOVER（r746-750）+坑直写（收尾脚本跨机律误用→pit-protocol-lane.md）"
    "| 最近实物: qa/smoke-r750.md 5/5+qa/equity-curve-r750.png 66,211B+results/_r750bmc_s6_log.txt 40/40+"
    "results/_r750bmc_ledger_heal_receipt.json @ 2026-10-08T{TT}+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 enforce+fund_premium 15:30 首采（bm-c 车）+"
    "CTA_P1 首接线+首 marks 验证（≤10-08 23:59）")

ACTIVITY = (
    "r750 bm-c: reopen T-0 early-session watch round 70th consecutive (09:4x window; marks lane landed, intraday watch). "
    "(1) S0: round-start dirty 6 = own daemon live faces -> absorb commit f9cf2f5ef -> pull --rebase onto bm-a r873 "
    "a9f5897a7/1499a55e7 (rebase 1/1 clean; marks-20261008.jsonl arrived IN this wave = r748/749 origin-absent watch "
    "resolved: bm-a r873 carries the file, 4537B, ts 09:35:01, 6 traders live-marked, state_cutoff 2026-09-30; r747 "
    "escalation pointer waived). (2) S0.5 double sweep (_r750bmc_s05_facts.json): DEC EE659451 UNCHANGED + ORD 267B1EA0 "
    "UNCHANGED (zero consumption); fleet orders 51 disk unacked=0; inbox 0. (3) S1 smoke 49/49 + round-zero orphan "
    "probe py_faces=4 orphans=1 (resident ComfyUI service face pid 28732, CEO asset, read-only no-kill, standing "
    "disposition) + satengine rc0 alive (N1_BANDS registry through W183) + idle NOT-GREEN (ram_free 15.1% < 40% resident "
    "ComfyUI, idle_rounds=0, --worked). (4) MAIN PRODUCTS: (a) lineage clone gate (_r750bmc_clone.py: order-sensitive "
    "double-replacement, stale749=0 across s05/s6/qa_ignite, compile gate PASS, receipt _r750bmc_clone_receipt.json). "
    "(b) S6 40/40 rc0 via _r750bmc_s6.py canonical clone (dualrun ZERO-DRIFT streak 51 @408 entries, cutoff 03:47 pool "
    "faces unchanged pre-close; compute_audit rc0 load_state=idle-starvation pool_ready=0<floor 3 honest structural "
    "flag = seat-gap known face, W16-JUDGE closed by bm-a r873, supply face belongs to prereg drafting cadence; "
    "fund_premium pre-15:30 no-op -> tonight 15:30 bm-c-lane first snapshot; cta_p1_paper no markable bar -> tonight "
    "first-bar auto-wiring; lane guards honest stdout-only skips). (c) QA det-70th per NEW ignition order law (r749 "
    "pit): S6 full-chain rc0 collected FIRST -> qa_ignite detached pid 31484 -> poll terminal (.err 0B): 93 trades, "
    "equity 1,017,839 frozen identity, determinism=True, PNG 66,211B, market_clock cell=ORA, 70th consecutive pack -- "
    "race-free, zero FACE_ERROR transient this window. (d) LEDGER CROSS-FACE HEAL: r749 close script had mechanically "
    "applied bm-a's r844/r865 ROOT-path law -> r749 report row landed on bm-c's FROZEN ROOT face (r645 epoch-freeze "
    "note violated, ledger split r643-748@canonical vs r749@ROOT); r750 heal per r865-heal mirror: r749 row verbatim "
    "re-migrated to canonical logs/iteration-loop/round_reports-bm-c.md + dated heal-note row, ROOT face untouched "
    "(git history preserved), receipt _r750bmc_ledger_heal_receipt.json; pit direct-written to "
    "research/pit-protocol-lane.md (r666 precedent); this close RPT restored to canonical path + grep-canonical "
    "self-verify. (e) 5x HANDOVER refresh r746-750 window line. (5) post_review run zero red (45 YES / 0 NO / 5 WAIT); "
    "attrition CLEAN (4 ledger files, healed shrink note as recorded); quartet green (loop pin=5 no-op + watchdog "
    "re-registered + both claws reinstalled LF-normalized).")

NEXT_PTR = (
    "r751: (a) marks lane intraday incremental watch (bm-a host lane; first marks landed 09:35:01, state_cutoff "
    "2026-09-30; tonight post-close = first-marks verification marks row + state trial-live + compounding identity "
    "per r749 pointer (c)); (b) tonight post-close face (<=10-08 23:59): data-chain full re-arm + REGIME_GUARD v3 "
    "first-new-bar enforce (set BIGMONEY_REGIME_GUARD=enforce before live.paper) + fund_premium 15:30 first snapshot "
    "(bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verification + QDII watch holiday-delta; (c) QA "
    "ignition order law standing (S6 rc0 -> qa_ignite -> qa_poll terminal -> close); (d) close scripts: RPT path = "
    "canonical logs/iteration-loop/round_reports-bm-c.md (r750 pit; NEVER clone r749's ROOT template); (e) O-2215-1 "
    "remaining: SUPPORT row awaits bm-b router spec <=10-16; matrix re-fires when bm-a REGIME-5 labels land <=10-14; "
    "numeric weights review + 10-21 revisit; (f) cloudF row <=10-14 standing; (g) month-boundary first exam 10-31. "
    "[via bm-c r750]")

SUMMARY = ("r750: S0 absorb daemon faces rebase onto bm-a r873 + QA det-70th 5/5 (pid 31484, new ignition order "
           "S6->qa_ignite->poll) + marks-20261008 landed (bm-a r873, 09:35:01 first 6-trader live marks, pointer-(a) "
           "closed, escalation waived) + r749 ledger cross-face heal (stray ROOT row verbatim re-migrated to canonical "
           "logs/iteration-loop/) + cross-machine law pit direct-written; DEC/ORD both UNCHANGED; unacked=0; smoke "
           "49/49; attrition CLEAN; post_review 45Y/0N/5W.")

VERIFY = ("smoke 49/49 + qa/smoke-r750.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True .err 0B "
          "png 66,211B) + results/_r750bmc_s6_log.txt 40/40 rc0 (dualrun ZERO-DRIFT streak 51) + "
          "results/_r750bmc_s05_facts.json double sweep (DEC EE659451 UNCHANGED / ORD 267B1EA0 UNCHANGED / unacked=0 / "
          "inbox 0 / shape-asserted) + results/_r750bmc_clone_receipt.json (stale749=0, compile OK x3) + "
          "results/_r750bmc_ledger_heal_receipt.json (r749 row verbatim exactly-once in canonical, ROOT sha256 "
          "unchanged) + attrition CLEAN + post_review 45 YES / 0 NO (run) + quartet green (pin=5/watchdog/claws) + "
          "orphan face=1 standing disposition + pit direct-write reconcile line")


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
    assert back.count(b"| r750 |") == 1, "r750 row not exactly-once in canonical tail (r865+r750 law)"
    assert b"| r750 |" in back.split(eol)[-2] + back.split(eol)[-3], "r750 row not in canonical tail"
    # 2) heartbeat
    hb = json.load(open(HB, encoding="utf-8"))
    for k in ("last_seen", "clock_read", "ts", "updated", "updated_at", "last_seen_at",
              "last_run_at", "last_ts", "current_task_at", "last_round_at"):
        hb[k] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["round_no"] = 751
    hb["last_round"] = 750
    hb["round_no_label"] = "round 750 (bm-c)"
    hb["current_task"] = TASK.replace("{TT}", NOW[11:16])
    hb["latest_artifact"] = ("qa/smoke-r750.md 5/5 + qa/equity-curve-r750.png 66,211B + results/_r750bmc_s6_log.txt "
                             "(40 legs rc0) + results/_r750bmc_clone_receipt.json (stale749=0 trio) + "
                             "results/_r750bmc_ledger_heal_receipt.json (r749 row verbatim in canonical) + "
                             "research/pit-protocol-lane.md r750 entry @ " + NOW)
    hb["next_milestone"] = ("tonight post-close (10-08 15:30+): data-chain re-arm + REGIME_GUARD v3 first-new-bar "
                            "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + "
                            "first-marks verify (<= 10-08 23:59); next 5x = bm-c r755")
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
    st["round_no"] = 751
    st["last_round"] = 750
    st["round_no_label"] = "round 750 (bm-c)"
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
    st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r750 sweeps "
                                    "= UNCHANGED 267B1EA0 zero delta zero consumption; hex-case comparison normalized "
                                    "per r711 pit law; facts-driven from results/_r750bmc_s05_facts.json, 40hex "
                                    "shape-asserted, never hand-typed (r583 S4 law)")
    st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r750 "
                                       "sweeps = UNCHANGED EE659451 zero delta zero action; facts-driven from "
                                       "results/_r750bmc_s05_facts.json, 64hex shape-asserted, never hand-typed "
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
