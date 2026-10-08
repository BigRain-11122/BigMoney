# -*- coding: utf-8 -*-
"""r749 bm-c round-close bookkeeping: round report line append (ROOT canonical
path per r844 law, write-then-grep self-verify per r865 pit), heartbeat
fleet/machines/bm-c.json + state-bm-c.json field updates (epoch=int law
R170/R178, clock_read T-separator law R262, round_no 749->750, DEC/ORD both
UNCHANGED zero consumption, live cpu/ram/gpu re-sample).
Pattern credit: Tools/_r748bmc_close.py (with r865 ROOT-path fix applied)."""
import datetime
import json
import os
import psutil
import subprocess
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
RPT = os.path.join(ROOT, "round_reports-bm-c.md")   # ROOT canonical (r844 law)
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
ST = os.path.join(ROOT, "state-bm-c.json")

REPORT_LINE = (
    "2026-10-08T09:3x+08:00 | r749 | dept:工程+交易（复市 T-0 开盘初窗值守轮·第 69 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·verdict=py_low_board_clear=板清+开盘前无新 bar 合法 idle〔orders 51 disk "
    "unacked=0 双扫·inbox 0 双扫〕·compute_audit FLAG:supply_floor 如实披露=池 ready 1<floor 3·N1 引擎自有波队列在烧"
    "非断供·供给面属预注册起草线节奏） | "
    "当前活: r749 bm-c（09:2x-09:3x 窗·复市首交易日开盘初窗值守第 69 连守轮）——S0 轮首脏 7=自有 daemon 面"
    "（orphan-probe/autofill/dispatcher/idle 对/saturation×2）absorb commit→pull --rebase 落 bm-a r872/873——"
    "主产出=①QA det-69th 5/5（分离 pid 35668·.err 0B·93 trades·equity 1,017,839 冻结恒等·determinism=True·"
    "PNG 66,102B·69 连证）+②S6 40/40 rc0（dualrun ZERO-DRIFT streak 51 @408 条·cutoff 03:47 池面未变·"
    "fund_premium pre-15:30 no-op→今晚 15:30 bm-c 车道首采·CTA_P1 无可标 bar→今晚首 bar 自动接线）+"
    "③血统克隆门三件（_r749bmc_clone.py 序敏感双替换 stale748=0·compile 门全过·收据 _r749bmc_clone_receipt.json·"
    "引导件 _r749bmc_boot.py 留档）+④marks-20261008.jsonl 落盘验证=origin 未达（09:35 终查 fetch+ls-tree 无该件·"
    "bm-a 宿主 lane 未提交/未到火窗·R108 正典 bm-c 无该任务=预期态·r750 续守）+⑤坑直写固化（QA 分离跑手×S6 链"
    "同窗双调 market_clock 竞态→QA 捕获面瞬态 FACE_ERROR_HOT 假 cell「FAC」=tail[:100] 截断面·正典面 ORANGE_COOL "
    "git clean 由 S6 腿后写保全→research/pit-protocol-lane.md 直写 1,259B sha16 153710d0bc127f58·r666 范式·"
    "主件 CODELY.md 30,684B 帽内未动）+CEO 面再生（LIVE-2026-10-08.md HEAD 单行 stub→99 行全页·REPORT-2026-10-08 "
    "全页·同日幂等 last-writer 收敛）+自愈四件套全绿（loop pin=5 no-op 首火 09:35+watchdog 重注+双爪 LF 归一重装）+"
    "attrition CLEAN（4 账本 healed 历史缩行照录）+post_review 零红（45✓/0✗·WAIT 5）+孤儿面=1（常驻 ComfyUI 服务面 "
    "pid 28732·CEO 私产·只读披露不击杀·既有处置维持）+idle --worked（RAM 17%<40% 常驻 ComfyUI·idle_rounds=0·"
    "本轮实工=克隆门+QA+S6+坑固化） | "
    "最近实物: qa/smoke-r749.md 5/5+qa/equity-curve-r749.png 66,102B+results/_r749bmc_s6_log.txt（40 腿 rc0）+"
    "results/_r749bmc_clone_receipt.json+research/pit-protocol-lane.md r749 条（sha16 153710d0） "
    "@ 2026-10-08T09:3x+08:00 | "
    "下个里程碑: r750（09:4x+）marks-20261008.jsonl 落盘复查+5x HANDOVER 核对；今晚盘后（10-08 15:30+）数据链"
    "re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采（bm-c 车）+CTA_P1 首接线+首 marks 验证"
    "（≤10-08 23:59）；下一 5x=bm-c r750 | "
    "验证证据: smoke 49/49+qa/smoke-r749.md 5/5（determinism=True·93 trades·1,017,839 frozen identity·.err 0B）+"
    "qa/equity-curve-r749.png 66,102B+results/_r749bmc_s6_log.txt（40 legs rc0·dualrun streak 51 ZERO-DRIFT）+"
    "results/_r749bmc_s05_facts.json 双扫（DEC EE659451/ORD 267B1EA0 双 UNCHANGED·unacked=0·inbox 0·shape-asserted）+"
    "results/_attrition_guard_scan.json CLEAN+克隆门收据 _r749bmc_clone_receipt.json（stale748=0·compile OK×3）+"
    "post_review run（45✓/0✗）+四件套四证+pit 直写对账行（bytes=1259 sha16=153710d0 verbatim-in-file）+"
    "CALL 正典面 git clean（ORANGE_COOL·竞态瞬态未污染盘上） | "
    "下轮指针: r750: (a) marks-20261008.jsonl 落盘复查（bm-a lane·若 09:4x+ 仍缺=按 r747 指针在 bm-a 心跳面质询而非"
    "代烧）；(b) 5x 轮=HANDOVER 产物清单核对更新（r746-750 窗）；(c) tonight post-close face（≤10-08 23:59）: "
    "data-chain full re-arm+REGIME_GUARD v3 first-new-bar enforce（live.paper 前设 BIGMONEY_REGIME_GUARD=enforce）+"
    "fund_premium 15:30 first snapshot（bm-c lane）+CTA_P1 first-bar auto-wiring+first-marks verification+QDII watch "
    "holiday-delta；(d) QA 点火序新律（r749 pit·pit-protocol-lane.md）：S6 全链 rc0 收齐→qa_ignite→qa_poll 终态→close "
    "进位（避免 QA item4×S6 腿 5/7 同窗双调 market_clock）；(e) O-2215-1 remaining standing（bm-b router spec ≤10-16·"
    "bm-a REGIME-5 标签 ≤10-14·numeric weights review+10-21 revisit）；(f) cloudF row ≤10-14 standing；"
    "(g) 月界首考 10-31。[via bm-c r749] | "
    "轮产品计分：2（QA det-69th 确定性包+S6 40 腿全链再生+克隆门三件+坑直写固化+CEO 一页纸 stub→全页=能跑能看实物） | "
    "记账预算：5（S0 state absorb+轮报/心跳/state 收口+attrition/post_review 例行扫描+克隆收据+facts 双扫件）")

TASK = (
    "当前活: r749 bm-c（09:2x-09:3x 窗·复市首交易日开盘初窗值守第 69 连守轮）——"
    "主产出=QA det-69th 5/5（pid 35668·93 trades·1,017,839 冻结恒等）+S6 40/40 rc0（dualrun streak 51·"
    "fund_premium/CTA_P1 今晚首采/首接线）+血统克隆门三件（stale748=0）+marks-20261008.jsonl 落盘验证"
    "=origin 未达（bm-a 宿主 lane·r750 续守）+坑直写（QA×S6 market_clock 竞态 FACE_ERROR_HOT 假 cell→"
    "pit-protocol-lane.md 1,259B）+CEO 面 stub→全页再生+S0 absorb+自愈四件套全绿+attrition CLEAN+"
    "post_review 零红（45✓/0✗）"
    "| 最近实物: qa/smoke-r749.md 5/5+qa/equity-curve-r749.png 66,102B+results/_r749bmc_s6_log.txt"
    "+results/_r749bmc_clone_receipt.json+research/pit-protocol-lane.md r749 条 @ 2026-10-08T09:3x+08:00 | "
    "下个里程碑: r750（09:4x+）marks 落盘复查+5x HANDOVER；今晚盘后（10-08 15:30+）数据链 re-arm+"
    "REGIME_GUARD v3 enforce+fund_premium 首采（bm-c 车）+CTA_P1 首接线+首 marks 验证（≤10-08 23:59）")

ACTIVITY = (
    "r749 bm-c: early-session watch round 69th consecutive (09:2x-09:3x window; reopen T-0 day, call auction done "
    "09:25, marks lane watch). (1) S0: round-start dirty 7 = own daemon live faces -> absorb commit -> pull --rebase "
    "onto bm-a r872/873 (rebase 1/1 clean). (2) S0.5 sweeps (round-start + close double-scan): DEC EE659451 "
    "UNCHANGED + ORD 267B1EA0 UNCHANGED (zero consumption); fleet orders 51 disk unacked=0 both sweeps; inbox 0 "
    "both sweeps. (3) S1 smoke 49/49 + QA det-69th determinism pack 5/5 (detached pid 35668, .err 0B): 93 trades, "
    "equity 1,017,839 frozen identity, determinism=True, PNG 66,102B. QA capture face showed transient "
    "FACE_ERROR_HOT cell ('FAC' = tail[:100] truncation) = race artifact of qa_ignite item4 leg x S6 chain legs "
    "5/7 both invoking market_clock_call.py in-window (QA read of regime_state.json hit S6 mid-rewrite window); "
    "canonical face preserved ORANGE_COOL by S6 leg later write (CALL+call_latest git-clean, disk-authoritative); "
    "rc0 throughout (honest fail-closed, not a crash); pit direct-written to research/pit-protocol-lane.md "
    "(1,259B, sha16 153710d0, r666 direct-write precedent, main CODELY.md 30,684B under cap untouched). (4) S3: "
    "orphan probe py_faces=4 orphans=1 (resident ComfyUI service face pid 28732, CEO asset, read-only disclosure "
    "no-kill, standing disposition); satengine rc0 alive (N1_BANDS registry through W183); watermark red=false "
    "verdict=py_low_board_clear (open_tickets=0, bandit=0, bars absent pre-open, legal idle); compute_audit "
    "FLAG:supply_floor disclosed (pool ready 1 < floor 3; N1 engine burns own wave queue, supply face belongs "
    "to prereg drafting cadence); idle NOT-GREEN (RAM ~17% free, resident ComfyUI), idle_rounds=0, --worked "
    "recorded (real work: clone gate + QA + S6 + pit). (5) MAIN PRODUCTS: (a) lineage clone gate "
    "(_r749bmc_clone.py: order-sensitive double-replacement, stale748=0 across s05/s6/qa_ignite, compile gate "
    "PASS, receipt _r749bmc_clone_receipt.json; bootstrap _r749bmc_boot.py archived - first-order prefix+bare "
    "collision caught and fixed in-window). (b) marks-20261008.jsonl landing verification (r748 pointer (a) "
    "main task): origin-absent at 09:31 AND 09:35 final re-check (fetch + ls-tree origin/main, no blob; bm-a "
    "host lane not yet committed / fire window; R108 canon bm-c has no such task = expected disposition; "
    "recheck -> r750, escalate to bm-a heartbeat inquiry if still absent, never proxy-burn). (c) S6 40/40 rc0 "
    "via Tools/_r749bmc_s6.py canonical clone (dualrun ZERO-DRIFT streak 51 @408 entries, cutoff 03:47 pool "
    "faces unchanged pre-open; py_watermark py_low_board_clear legal-idle; fund_premium pre-15:30 no-op -> "
    "tonight 15:30 bm-c-lane first snapshot; cta_p1_paper no markable bar -> tonight first-bar auto-wiring; "
    "lane guards honest stdout-only skips for bm-a/bm-b lanes). (d) CEO face regen: LIVE-2026-10-08.md HEAD "
    "1-line stub -> 99-line full page + REPORT-2026-10-08 full page (same-day idempotent regen, last-writer "
    "convergence; intraday tier honest 'no bar yet today' pre-minute-feed). (6) post_review run zero red "
    "(45 YES / 0 NO / 5 WAIT, report results/post_review/REPORT-20261008.md); attrition CLEAN (4 ledger "
    "files, healed historical shrink notes). (7) quartet green (loop pin=5 no-op first-fire 09:35 + watchdog "
    "re-registered + both claws reinstalled LF-normalized). (8) one new pit-domain lesson this round "
    "(QA x S6 market_clock race) -> direct-written per r666 precedent, zero main-file append.")

NEXT_PTR = (
    "r750: (a) marks-20261008.jsonl landing re-check (bm-a lane; if still absent at 09:4x+ escalate via bm-a "
    "heartbeat inquiry face per r747 pointer, never proxy-burn); (b) 5x round = HANDOVER artifact checklist "
    "refresh (r746-750 window); (c) tonight post-close face (<=10-08 23:59): data-chain full re-arm + "
    "REGIME_GUARD v3 first-new-bar enforce (set BIGMONEY_REGIME_GUARD=enforce before live.paper) + "
    "fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verification "
    "(marks row + state trial-live + compounding identity) + QDII watch holiday-delta; (d) QA ignition order "
    "new law (r749 pit, research/pit-protocol-lane.md): S6 full-chain rc0 -> qa_ignite -> qa_poll terminal -> "
    "close advance (avoid QA item4 x S6 legs 5/7 same-window double market_clock invocation); (e) O-2215-1 "
    "remaining: SUPPORT row awaits bm-b router spec <=10-16; matrix run re-fires when bm-a REGIME-5 labels "
    "land <=10-14; numeric weights review window + 10-21 criteria revisit per order sec.4; (f) cloudF row "
    "collection window <=10-14 standing; (g) month-boundary first exam 10-31. [via bm-c r749]")

SUMMARY = ("r749: S0 absorb daemon faces rebase onto bm-a r872/873 + clone gate (stale748=0 trio) + QA det-69th "
           "5/5 (pid 35668) + S6 40/40 rc0 (dualrun streak 51) + marks-20261008 origin-absent verified (r750 "
           "recheck) + QA x S6 market_clock race pit direct-written (1,259B); DEC/ORD both UNCHANGED; unacked=0; "
           "smoke 49/49; attrition CLEAN; post_review 45Y/0N/5W.")

VERIFY = ("smoke 49/49 + qa/smoke-r749.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True .err "
          "0B) + qa/equity-curve-r749.png 66,102B + results/_r749bmc_s6_log.txt 40/40 rc0 (dualrun streak 51 "
          "ZERO-DRIFT) + results/_r749bmc_s05_facts.json double sweep (DEC EE659451 UNCHANGED / ORD 267B1EA0 "
          "UNCHANGED / unacked=0 / inbox 0 / shape-asserted) + results/_r749bmc_clone_receipt.json (stale748=0, "
          "compile OK x3) + attrition CLEAN + post_review 45 YES / 0 NO (run) + quartet green "
          "(pin=5/watchdog/claws) + pit direct-write reconcile line (bytes=1259 sha16=153710d0 verbatim-in-file) "
          "+ CALL canonical face git-clean ORANGE_COOL")


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
    # 1) round report append (ROOT canonical, EOL-matched, byte-exact)
    raw = open(RPT, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    if not raw.endswith(eol):
        with open(RPT, "wb") as fh:      # tail-terminator heal before append (r843 family)
            fh.write(raw + eol)
    line = REPORT_LINE.replace("09:3x", NOW[11:16]).encode("utf-8")
    with open(RPT, "ab") as fh:
        fh.write(line + eol)
    # write-then-grep self-verify (r865 pit law)
    back = open(RPT, "rb").read()
    assert b"| r749 |" in back.split(eol)[-2] + back.split(eol)[-3], "r749 row not in ROOT tail (r865 law)"
    # 2) heartbeat
    hb = json.load(open(HB, encoding="utf-8"))
    for k in ("last_seen", "clock_read", "ts", "updated", "updated_at", "last_seen_at",
              "last_run_at", "last_ts", "current_task_at", "last_round_at"):
        hb[k] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["round_no"] = 750
    hb["last_round"] = 749
    hb["round_no_label"] = "round 749 (bm-c)"
    hb["current_task"] = TASK.replace("09:3x", NOW[11:16])
    hb["latest_artifact"] = ("qa/smoke-r749.md 5/5 + qa/equity-curve-r749.png 66,102B + results/_r749bmc_s6_log.txt "
                             "(40 legs rc0) + results/_r749bmc_clone_receipt.json (stale748=0 trio) + "
                             "research/pit-protocol-lane.md r749 entry @ " + NOW)
    hb["next_milestone"] = ("r750 (09:4x+): marks-20261008.jsonl landing re-check + 5x HANDOVER refresh; tonight "
                            "post-close: data-chain re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium "
                            "15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verify "
                            "(<= 10-08 23:59)")
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
    st["round_no"] = 750
    st["last_round"] = 749
    st["round_no_label"] = "round 749 (bm-c)"
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
    st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r749 sweeps "
                                    "= UNCHANGED 267B1EA0 zero delta zero consumption; hex-case comparison normalized "
                                    "per r711 pit law; facts-driven from results/_r749bmc_s05_facts.json, 40hex "
                                    "shape-asserted, never hand-typed (r583 S4 law)")
    st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r749 "
                                       "sweeps = UNCHANGED EE659451 zero delta zero action; facts-driven from "
                                       "results/_r749bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)")
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
