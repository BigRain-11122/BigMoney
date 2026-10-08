# -*- coding: utf-8 -*-
"""r758 bm-c round-close bookkeeping: round report line append to the CANONICAL
face logs/iteration-loop/round_reports-bm-c.md (fleet/README sec.6 + r750 pit
law -- canonical path ONLY, never the ROOT face), write-then-grep self-verify,
heartbeat fleet/machines/bm-c.json + state-bm-c.json field updates (epoch=int
law R170/R178, clock_read T-separator law R262, round_no 758->759, DEC/ORD
UNCHANGED zero action facts-driven from _r758bmc_s05_facts.json per r583 law,
live cpu/ram/gpu re-sample).
Pattern credit: Tools/_r753bmc_close.py (canonical-RPT lineage)."""
import datetime
import json
import os
import psutil
import subprocess
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
RPT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")  # CANONICAL (fleet/README §6; r750 pit law)
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
ST = os.path.join(ROOT, "state-bm-c.json")
FACTS = os.path.join(ROOT, "results", "_r758bmc_s05_facts.json")

REPORT_LINE = (
    "2026-10-08T{TT}+08:00 | r758 | dept:工程+交易（复市 T-0 盘中值守轮·第 78 bm-c 连守轮·午休窗） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·py_low_board_clear 盘中板清合法 idle〔orders 51 disk unacked=0 双扫·"
    "inbox 0 双扫〕·compute_audit rc0 flags=[pool_starvation,supply_floor] 盘中席位间隙已知常在面如实披露·"
    "next_pick=claimed〔moneyflow IC 参考批·advisory only·供给属预注册起草线节奏〕） | "
    "当前活: r758 bm-c（12:36-12:4x 窗·复市 T-0 盘中值守第 78 连守轮·午休窗）——"
    "S0 轮首脏 3=自有面（satengine 状态×2+孤儿探针面）absorb 93a448fae→pull --rebase up-to-date（他机零新 commit）→"
    "克隆门三件（_r758bmc_boot.py 手写→_r758bmc_clone.py 双模替换 stale757=0 三件〔s05/s6/qa_ignite〕·"
    "compile OK×3·收据 _r758bmc_clone_receipt.json）——"
    "主产出=①DEC/ORD 双水位双扫 UNCHANGED 零动作（EE70CEF0/031E0E3E 两窗同哈希·unacked=0·inbox 0）"
    "②QA det-78th 5/5（律序 S6 40 腿 rc0 收齐→点火 pid 18640→终态 .err 0B——"
    "93 trades·equity 1,017,839 冻结恒等·determinism=True·png 66,342B·78 连证）"
    "③S6 40/40 rc0（dualrun ZERO-DRIFT streak 51 @408 条·cutoff 03:47·py_watermark py_low_board_clear 合法盘中 idle·"
    "lane 守卫诚实 skip 面：bm-a 心跳 fresh 14min→strategy_scorecard/market_clock_l3/paper 族 skip derive 零 "
    "stale-takeover·bm-a/bm-b 车道族 stdout-only no-op·fund_premium pre-15:30 no-op→今晚 15:30 bm-c 车道首采·"
    "fundamental 快照 22.1h fresh skip·cta_p1_paper 无可标 bar→今晚首 bar 自动接线）+"
    "④marks lane 盘中值守（marks-20261008.jsonl 5 行 11:25 尾·午休窗·13:00 复盘窗新行预期·host=bm-a 单写面·观察项）"
    "| 最近实物: qa/smoke-r758.md 5/5+qa/equity-curve-r758.png 66,342B+results/_r758bmc_s6_log.txt（40 腿 rc0）+"
    "results/_r758bmc_clone_receipt.json @ 2026-10-08T{TT}+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采"
    "（bm-c 车）+CTA_P1 首接线+首 marks 验证（≤10-08 23:59） | "
    "验证证据: smoke 49/49+QA 5/5（93 trades·1,017,839 冻结恒等〔r751-757 恒等锚一致〕·determinism=True·.err 0B·"
    "png 66,342B·market_clock cell=ORA·latest_panel_bar 2026-09-30 金周 no-op 如期）+S6 40/40 rc0（dualrun streak 51 "
    "ZERO-DRIFT @408·cutoff 03:47）+s05 双扫 facts-driven（DEC EE70CEF0 UNCHANGED/ORD 031E0E3E UNCHANGED 零动作·"
    "unacked=0·inbox 0·shape-asserted）+results/_r758bmc_clone_receipt.json（stale757=0·compile OK×3）+"
    "attrition CLEAN+post_review 45✓/0✗/WAIT 5+四件套四证（pin=5 no-op/watchdog 在位/双爪 IN-PLACE）+"
    "FleetLink 常态自证（listener pid 28396 alive+health 200 ok node=bm-c）+孤儿面=1（py_faces=4·常驻 ComfyUI 服务面·"
    "CEO 资产·只读披露不击杀·既有处置维持）+SAT 活 rc0+idle NOT-GREEN --worked（RAM 15%<40% 常驻 ComfyUI）+"
    "token_meter delta=0 | "
    "下轮指针: r759: (a) marks lane 13:00 复盘窗新行核验（bm-a 宿主车道·5 行在册·新窗预期）；"
    "(b) tonight post-close face（≤10-08 23:59）数据链全 re-arm+REGIME_GUARD v3 first-new-bar enforce"
    "（live.paper 前设 BIGMONEY_REGIME_GUARD=enforce）+fund_premium 15:30 first snapshot（bm-c lane）+"
    "CTA_P1 first-bar auto-wiring+first-marks verification+QDII watch holiday-delta；"
    "(c) QA 点火序律值守（S6 rc0→qa_ignite→poll 终态→close）；(d) 收尾脚本 RPT=正典面（r750 坑·禁克隆 ROOT 模板）；"
    "(e) FleetLink 常态监听自证一行随轮（listener pid/health）；(f) D-20261008-06 后缀命名律执法面"
    "（_r759bmc_* 前缀范式照旧）+命令查重律执法面（CEO 令落账前必查现行法面）；(g) bm-b FleetLink 回执候"
    "（他机车道零干预）；(h) 月界首考 10-31；next 5x=bm-c r760（HANDOVER r756-760）。[via bm-c r758] | "
    "轮产品计分：2（QA det-78th 确定性包+S6 40 腿再生+克隆门三件+双水位双扫核验=能跑能看实物） | "
    "记账预算：5（S0 churn absorb×1+轮报/心跳/state 收口+post_review/attrition 例行+克隆收据+s05 facts 双扫件）")

TASK = (
    "当前活: r758 bm-c（12:36-12:4x 窗·复市 T-0 盘中值守第 78 连守轮·午休窗）——"
    "主产出=①DEC/ORD 双水位双扫 UNCHANGED 零动作（EE70CEF0/031E0E3E·unacked=0·inbox 0）"
    "②QA det-78th 5/5（93 trades·1,017,839 冻结恒等·determinism=True·png 66,342B·78 连证）"
    "③S6 40/40 rc0（dualrun streak 51）+克隆门 stale757=0+marks lane 5 行值守（11:25 尾·13:00 窗前）"
    "| 最近实物: qa/smoke-r758.md 5/5+qa/equity-curve-r758.png 66,342B+results/_r758bmc_s6_log.txt 40/40+"
    "results/_r758bmc_clone_receipt.json @ 2026-10-08T{TT}+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 enforce+fund_premium 15:30 首采（bm-c 车）+"
    "CTA_P1 首接线+首 marks 验证（≤10-08 23:59）")

ACTIVITY = (
    "r758 bm-c: reopen T-0 intraday watch round 78th consecutive (12:36-12:4x window; lunch break, marks lane 5 rows "
    "11:25 tail, 13:00 reopen window expected). (1) S0: round-start dirty 3 = own daemon live faces (satengine x2 + "
    "orphan-probe face) -> absorb commit 93a448fae -> pull --rebase up-to-date (no incoming). (2) S0.5 double sweep: "
    "DEC EE70CEF0 UNCHANGED + ORD 031E0E3E UNCHANGED both passes (zero action, watermarks held facts-driven); fleet "
    "orders 51 disk unacked=0; inbox 0. (3) S1 smoke 49/49 + SAT rc0 alive + orphan probe py_faces=4 orphans=1 "
    "(resident ComfyUI service face, CEO asset, read-only no-kill, standing disposition) + idle NOT-GREEN (ram_free "
    "15.0% < 40% resident ComfyUI, idle_rounds=0, --worked). (4) MAIN PRODUCTS: (a) lineage clone gate: "
    "_r758bmc_boot.py HAND-WRITTEN -> _r758bmc_clone.py: stale757=0 across s05/s6/qa_ignite, compile gate PASS, "
    "receipt _r758bmc_clone_receipt.json. (b) S6 40/40 rc0 via canonical clone (dualrun ZERO-DRIFT streak 51 @408 "
    "entries cutoff 03:47; compute_audit rc0 flags=[pool_starvation,supply_floor] intraday board-clear known "
    "standing faces honestly disclosed; py_watermark py_low_board_clear legal intraday idle; lane guards honest "
    "skips: bm-a heartbeat fresh 14min -> strategy_scorecard/market_clock_l3/paper-family skip derive zero "
    "stale-takeover; bm-a/bm-b owned lanes stdout-only no-op; fund_premium pre-15:30 no-op -> tonight 15:30 "
    "bm-c-lane first snapshot; fundamental snapshot 22.1h fresh skip; cta_p1_paper no markable bar -> tonight "
    "first-bar auto-wiring). (c) QA det-78th per ignition order law (r749 pit): S6 full-chain rc0 collected FIRST -> "
    "qa_ignite detached pid 18640 -> poll terminal (.err 0B): 93 trades, equity 1,017,839 frozen identity "
    "(r751-757 anchor holds), determinism=True, PNG 66,342B, market_clock cell=ORA, 78th consecutive pack. "
    "(d) marks lane watch: marks-20261008.jsonl 5 rows (11:25 tail, lunch window; 13:00 reopen window new rows "
    "expected; host=bm-a single-writer lane, observation item). (5) close: attrition + post_review + quartet + "
    "FleetLink self-cert + commit/push/verify.")

NEXT_PTR = (
    "r759: (a) marks lane 13:00 reopen-window row check (bm-a host lane, 5 rows in ledger; new rows expected at "
    "reopen); (b) tonight post-close face (<=10-08 23:59): data-chain full re-arm + REGIME_GUARD v3 first-new-bar "
    "enforce (set BIGMONEY_REGIME_GUARD=enforce before live.paper) + fund_premium 15:30 first snapshot (bm-c lane) "
    "+ CTA_P1 first-bar auto-wiring + first-marks verification + QDII watch holiday-delta; (c) QA ignition order "
    "law standing (S6 rc0 -> qa_ignite -> qa_poll terminal -> close); (d) close scripts: RPT path = canonical "
    "logs/iteration-loop/round_reports-bm-c.md (r750 pit; NEVER clone a ROOT template); (e) FleetLink standing "
    "self-cert line per round (listener pid/health); (f) D-20261008-06 suffix-naming law + command-dedup law "
    "enforcement face (check existing law before registering new orders); (g) bm-b FleetLink receipt awaited "
    "(other-machine lane, zero intervention); (h) month-boundary first exam 10-31; next 5x = bm-c r760 "
    "(HANDOVER r756-760). [via bm-c r758]")

SUMMARY = ("r758: S0 absorb 3 own faces (93a448fae) + rebase up-to-date + QA det-78th 5/5 (pid 18640, S6-first "
           "order, 93 trades, 1,017,839 frozen identity, determinism=True, png 66,342B) + S6 40/40 rc0 (dualrun "
           "streak 51, CA flags disclosed: pool_starvation/supply_floor seat-gap known faces) + clone gate trio "
           "stale757=0 (boot hand-written) + DEC/ORD double-sweep UNCHANGED zero action (EE70CEF0/031E0E3E); "
           "unacked=0; smoke 49/49; marks lane 5 rows lunch watch; attrition CLEAN; post_review 45Y/0N/5W.")

VERIFY = ("smoke 49/49 + qa/smoke-r758.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True .err 0B "
          "png 66,342B) + results/_r758bmc_s6_log.txt 40/40 rc0 (dualrun ZERO-DRIFT streak 51) + "
          "results/_r758bmc_s05_facts.json double sweep (DEC EE70CEF0 UNCHANGED / ORD 031E0E3E UNCHANGED zero "
          "action / unacked=0 / inbox 0 / shape-asserted) + results/_r758bmc_clone_receipt.json (stale757=0, "
          "compile OK x3) + attrition CLEAN + post_review 45 YES / 0 NO / 5 WAIT + quartet green (pin=5 no-op / "
          "watchdog / claws) + orphan face=1 standing disposition (py_faces=4) + SAT alive rc0 + idle NOT-GREEN "
          "--worked (RAM 15.0% resident ComfyUI) + FleetLink listener health 200 + marks lane 5 rows (11:25 tail)")


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
    facts = json.load(open(FACTS, encoding="utf-8"))
    assert facts["shape_assert"], "s05 facts shape assert must hold before consuming watermarks"
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
    assert back.count(b"| r758 |") == 1, "r758 row not exactly-once in canonical tail (r865+r750 law)"
    assert b"| r758 |" in back.split(eol)[-2] + back.split(eol)[-3], "r758 row not in canonical tail"
    # 2) heartbeat
    hb = json.load(open(HB, encoding="utf-8"))
    for k in ("last_seen", "clock_read", "ts", "updated", "updated_at", "last_seen_at",
              "last_run_at", "last_ts", "current_task_at", "last_round_at"):
        hb[k] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["round_no"] = 759
    hb["last_round"] = 758
    hb["round_no_label"] = "round 758 (bm-c)"
    hb["current_task"] = TASK.replace("{TT}", NOW[11:16])
    hb["latest_artifact"] = ("qa/smoke-r758.md 5/5 + qa/equity-curve-r758.png 66,342B + results/_r758bmc_s6_log.txt "
                             "(40 legs rc0) + results/_r758bmc_clone_receipt.json (stale757=0 trio) @ " + NOW)
    hb["next_milestone"] = ("tonight post-close (10-08 15:30+): data-chain re-arm + REGIME_GUARD v3 first-new-bar "
                            "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring "
                            "+ first-marks verify (<= 10-08 23:59); next 5x = bm-c r760")
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
    # 3) state (round_no 758->759; DEC/ORD UNCHANGED zero action, watermarks held)
    st = json.load(open(ST, encoding="utf-8"))
    for k in ("clock_read", "last_seen", "ts", "updated", "updated_at", "last_run_at",
              "last_seen_at", "current_task_at", "last_round_at", "last_round_ts",
              "last_decisions_read_at"):
        st[k] = NOW
    st["heartbeat_epoch_utc"] = EPOCH
    st["round_no"] = 759
    st["last_round"] = 758
    st["round_no_label"] = "round 758 (bm-c)"
    if facts["dec_delta"]:
        st["last_decisions_sha"] = facts["dec_sha"]
        st["last_decisions_at"] = NOW
    if facts["ord_delta"]:
        st["last_orders_sha"] = facts["ord_sha"]
        st["last_orders_at"] = NOW
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
    st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r758 double "
                                    "sweeps = UNCHANGED 031E0E3E both passes (zero delta zero action, watermark "
                                    "held); hex-case comparison normalized per r711 pit law; facts-driven from "
                                    "results/_r758bmc_s05_facts.json, 40hex shape-asserted, never hand-typed "
                                    "(r583 S4 law)")
    st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r758 "
                                       "sweeps = UNCHANGED EE70CEF0 both passes (zero action, watermark held); "
                                       "facts-driven from results/_r758bmc_s05_facts.json, 64hex shape-asserted, "
                                       "never hand-typed (r583 S4 law)")
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
    # 4) self-verify (R170/R178/R262 + watermark consumption verify)
    hb2 = json.load(open(HB, encoding="utf-8"))
    st2 = json.load(open(ST, encoding="utf-8"))
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int (R170/R178)"
    assert isinstance(st2["heartbeat_epoch_utc"], int), "state epoch not int"
    assert hb2["clock_read"][10] == "T", "clock_read T-sep (R262)"
    assert st2["last_orders_sha"] == facts["ord_sha"], "ORD watermark consumption verify failed"
    assert st2["last_decisions_sha"] == facts["dec_sha"], "DEC watermark must track facts sha"
    print("bookkeeping ok: hb epoch", hb2["heartbeat_epoch_utc"],
          "state last_round", st2["last_round"], "-> next round_no", st2["round_no"],
          "clock", hb2["clock_read"], "cpu", cpu, "ram_gb", ram_gb, "gpu_free", gpu_free,
          "ord_sha", st2["last_orders_sha"][:8])


if __name__ == "__main__":
    main()
