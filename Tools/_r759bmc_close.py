# -*- coding: utf-8 -*-
"""r759 bm-c round-close bookkeeping: round report line append to the CANONICAL
face logs/iteration-loop/round_reports-bm-c.md (fleet/README sec.6 + r750 pit
law -- canonical path ONLY, never the ROOT face), write-then-grep self-verify,
heartbeat fleet/machines/bm-c.json + state-bm-c.json field updates (epoch=int
law R170/R178, clock_read T-separator law R262, round_no 759->760, DEC
UNCHANGED held / ORD single-hop 031E0E3E->2BD0F0C7 consumed zero-action
not-involving-our-repo per r583 facts-driven law, live cpu/ram/gpu re-sample).
Pattern credit: Tools/_r758bmc_close.py (canonical-RPT lineage)."""
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
FACTS = os.path.join(ROOT, "results", "_r759bmc_s05_facts.json")

REPORT_LINE = (
    "2026-10-08T{TT}+08:00 | r759 | dept:工程+交易（复市 T-0 盘中值守轮·第 79 bm-c 连守轮·午休窗） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·py_low_board_clear 盘中板清合法 idle〔orders 51 disk unacked=0 双扫·"
    "inbox 0 双扫〕·compute_audit rc0 flags=[pool_starvation,supply_floor] 盘中席位间隙已知常在面如实披露·"
    "next_pick=claimed〔moneyflow IC 参考批·advisory only·面板 source-blocked 30min 自愈节奏〕） | "
    "当前活: r759 bm-c（12:46-12:5x 窗·复市 T-0 盘中值守第 79 连守轮·午休窗）——"
    "S0 轮首脏 3=自有面（satengine 状态×2+dispatcher 状态）absorb ce45d5558→pull --rebase 遭守护面 live-regen 竞态拒→"
    "fetch+rev-list 等价自证 0 incoming/1 ahead 零 rebase 需要（净树根治律 r642·无 autostash）→"
    "克隆门三件（_r759bmc_boot.py 手写→_r759bmc_clone.py 双模替换 stale758=0 三件〔s05/s6/qa_ignite〕·"
    "compile OK×3·收据 _r759bmc_clone_receipt.json）——"
    "主产出=①DEC/ORD 双水位双扫（DEC EE70CEF0 UNCHANGED 两窗同哈希零动作；ORD 单跳 031E0E3E→2BD0F0C7="
    "bm-a 12:44 e1390c9 CEO 1008 增量包投料令执行件〔AD-049 Megacity/AD-050 大逃杀英雄/AA-049 GUI 套件·"
    "MiniGame/FluxVerse 域·不涉本仓→水位键更新零动作·facts-driven〕·unacked=0·inbox 0）"
    "②QA det-79th 5/5（律序 S6 40 腿 rc0 收齐→点火 pid 27960→终态 .err 0B——"
    "93 trades·equity 1,017,839 冻结恒等〔r751-758 锚链续持〕·determinism=True·png 66,311B·79 连证）"
    "③S6 40/40 rc0（dualrun ZERO-DRIFT streak 51 @408 条·cutoff 03:47·py_watermark py_low_board_clear 合法盘中 idle·"
    "lane 守卫诚实 skip 面：bm-a 心跳 8min fresh→strategy_scorecard/market_clock_l3/paper 族 skip derive 零 "
    "stale-takeover·bm-a/bm-b 车道族 stdout-only no-op·fund_premium pre-15:30 no-op→今晚 15:30 bm-c 车道首采·"
    "fundamental 快照 22.3h fresh skip·cta_p1_paper 无可标 bar→今晚首 bar 自动接线）+"
    "④marks lane 盘中值守（marks-20261008.jsonl 5 行 11:25 尾·午休窗·13:00 复盘窗新行预期·host=bm-a 单写面·观察项）"
    "| 最近实物: qa/smoke-r759.md 5/5+qa/equity-curve-r759.png 66,311B+results/_r759bmc_s6_log.txt（40 腿 rc0）+"
    "results/_r759bmc_clone_receipt.json @ 2026-10-08T{TT}+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采"
    "（bm-c 车）+CTA_P1 首接线+首 marks 验证（≤10-08 23:59） | "
    "验证证据: smoke 49/49+QA 5/5（93 trades·1,017,839 冻结恒等〔r751-758 恒等锚一致〕·determinism=True·.err 0B·"
    "png 66,311B·market_clock cell=ORA·latest_panel_bar 2026-09-30 金周 no-op 如期）+S6 40/40 rc0（dualrun streak 51 "
    "ZERO-DRIFT @408·cutoff 03:47）+s05 双扫 facts-driven（DEC EE70CEF0 UNCHANGED/ORD 031E0E3E→2BD0F0C7 单跳消费·"
    "unacked=0·inbox 0·shape-asserted）+results/_r759bmc_clone_receipt.json（stale758=0·compile OK×3）+"
    "attrition CLEAN+post_review 45✓/0✗/WAIT 5+四件套四证（pin=5 no-op 首发留 12:55/watchdog 在位下次 12:53/双爪 MATCH）+"
    "FleetLink 常态自证（listener pid 28396 alive+health 200 ok node=bm-c）+孤儿面=1（py_faces=4·常驻 ComfyUI 服务面·"
    "CEO 资产·只读披露不击杀·既有处置维持）+SAT 活 rc0+idle NOT-GREEN --worked（RAM 12.9%<40% 常驻 ComfyUI）+"
    "token_meter delta=0 | "
    "下轮指针: r760: (a) 5x 轮=HANDOVER r756-760 核对更新（research/HANDOVER.md 产物清单与完成状态·每 5 轮义务）；"
    "(b) marks lane 13:00 复盘窗新行核验（bm-a 宿主车道·5 行在册·新窗预期）；"
    "(c) tonight post-close face（≤10-08 23:59）数据链全 re-arm+REGIME_GUARD v3 first-new-bar enforce"
    "（live.paper 前设 BIGMONEY_REGIME_GUARD=enforce）+fund_premium 15:30 first snapshot（bm-c lane）+"
    "CTA_P1 first-bar auto-wiring+first-marks verification+QDII watch holiday-delta；"
    "(d) QA 点火序律值守（S6 rc0→qa_ignite→poll 终态→close）；(e) 收尾脚本 RPT=正典面（r750 坑·禁克隆 ROOT 模板）；"
    "(f) FleetLink 常态监听自证一行随轮（listener pid/health）；(g) D-20261008-06 后缀命名律执法面"
    "（_r760bmc_* 前缀范式照旧）+命令查重律执法面；(h) bm-b FleetLink 回执候（他机车道零干预）；"
    "(i) 月界首考 10-31。[via bm-c r759] | "
    "轮产品计分：2（QA det-79th 确定性包+S6 40 腿再生+克隆门三件+双水位双扫核验=能跑能看实物） | "
    "记账预算：5（S0 churn absorb×1+轮报/心跳/state 收口+post_review/attrition 例行+克隆收据+s05 facts 双扫件）")

TASK = (
    "当前活: r759 bm-c（12:46-12:5x 窗·复市 T-0 盘中值守第 79 连守轮·午休窗）——"
    "主产出=①DEC/ORD 双水位双扫（DEC UNCHANGED·ORD 单跳 2BD0F0C7 消费零动作·不涉本仓·unacked=0·inbox 0）"
    "②QA det-79th 5/5（93 trades·1,017,839 冻结恒等·determinism=True·png 66,311B·79 连证）"
    "③S6 40/40 rc0（dualrun streak 51）+克隆门 stale758=0+marks lane 5 行值守（11:25 尾·13:00 窗前）"
    "| 最近实物: qa/smoke-r759.md 5/5+qa/equity-curve-r759.png 66,311B+results/_r759bmc_s6_log.txt 40/40+"
    "results/_r759bmc_clone_receipt.json @ 2026-10-08T{TT}+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 enforce+fund_premium 15:30 首采（bm-c 车）+"
    "CTA_P1 首接线+首 marks 验证（≤10-08 23:59）；next 5x=bm-c r760（HANDOVER r756-760）")

ACTIVITY = (
    "r759 bm-c: reopen T-0 intraday watch round 79th consecutive (12:46-12:5x window; lunch break, marks lane 5 rows "
    "11:25 tail, 13:00 reopen window expected). (1) S0: round-start dirty 3 = own daemon live faces (satengine x2 + "
    "dispatcher state) -> absorb commit ce45d5558; pull --rebase refused by daemon live-face regen race (unstaged "
    "changes between add and pull) -> race-free fetch + rev-list equivalence proven 0 incoming / 1 ahead = zero "
    "rebase needed (clean-tree law r642, no autostash). (2) S0.5 double sweep: DEC EE70CEF0 UNCHANGED both passes "
    "(zero action, watermark held); ORD single-hop 031E0E3E -> 2BD0F0C7 = bm-a 12:44 e1390c9 CEO 1008 asset-feed "
    "execution receipt (AD-049 Megacity / AD-050 battle-royale heroes / AA-049 GUI kit -- MiniGame/FluxVerse "
    "domain, NOT involving this repo -> watermark update zero action, facts-driven); fleet orders 51 disk "
    "unacked=0; inbox 0. (3) S1 smoke 49/49 + SAT rc0 alive + orphan probe py_faces=4 orphans=1 (resident ComfyUI "
    "service face, CEO asset, read-only no-kill, standing disposition) + idle NOT-GREEN (ram_free 12.9% < 40% "
    "resident ComfyUI, idle_rounds=0, --worked). (4) MAIN PRODUCTS: (a) lineage clone gate: _r759bmc_boot.py "
    "HAND-WRITTEN -> _r759bmc_clone.py: stale758=0 across s05/s6/qa_ignite, compile gate PASS, receipt "
    "_r759bmc_clone_receipt.json. (b) S6 40/40 rc0 via canonical clone (dualrun ZERO-DRIFT streak 51 @408 entries "
    "cutoff 03:47; compute_audit rc0 flags=[pool_starvation,supply_floor] intraday board-clear known standing "
    "faces honestly disclosed; py_watermark py_low_board_clear legal intraday idle; lane guards honest skips: "
    "bm-a heartbeat 8min fresh -> strategy_scorecard/market_clock_l3/paper-family skip derive zero "
    "stale-takeover; bm-a/bm-b owned lanes stdout-only no-op; fund_premium pre-15:30 no-op -> tonight 15:30 "
    "bm-c-lane first snapshot; fundamental snapshot 22.3h fresh skip; cta_p1_paper no markable bar -> tonight "
    "first-bar auto-wiring). (c) QA det-79th per ignition order law (r749 pit): S6 full-chain rc0 collected FIRST -> "
    "qa_ignite detached pid 27960 -> poll terminal (.err 0B): 93 trades, equity 1,017,839 frozen identity "
    "(r751-758 anchor chain holds), determinism=True, PNG 66,311B, market_clock cell=ORA, 79th consecutive pack. "
    "(d) marks lane watch: marks-20261008.jsonl 5 rows (11:25 tail, lunch window; 13:00 reopen window new rows "
    "expected; host=bm-a single-writer lane, observation item). (5) close: post_review 45Y/0N/5W + attrition "
    "CLEAN + quartet (pin=5 no-op first-fire 12:55 / watchdog next-run 12:53 / claws MATCH) + FleetLink "
    "self-cert (listener pid 28396 alive, health 200 ok node=bm-c) + commit/push/verify.")

NEXT_PTR = (
    "r760: (a) 5x round = HANDOVER r756-760 duty (verify + update research/HANDOVER.md product list & completion "
    "status, every-5-rounds law); (b) marks lane 13:00 reopen-window row check (bm-a host lane, 5 rows in ledger; "
    "new rows expected at reopen); (c) tonight post-close face (<=10-08 23:59): data-chain full re-arm + "
    "REGIME_GUARD v3 first-new-bar enforce (set BIGMONEY_REGIME_GUARD=enforce before live.paper) + fund_premium "
    "15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verification + QDII watch "
    "holiday-delta; (d) QA ignition order law standing (S6 rc0 -> qa_ignite -> qa_poll terminal -> close); "
    "(e) close scripts: RPT path = canonical logs/iteration-loop/round_reports-bm-c.md (r750 pit; NEVER clone a "
    "ROOT template); (f) FleetLink standing self-cert line per round (listener pid/health); (g) D-20261008-06 "
    "suffix-naming law (_r760bmc_* prefix pattern) + command-dedup law enforcement face; (h) bm-b FleetLink "
    "receipt awaited (other-machine lane, zero intervention); (i) month-boundary first exam 10-31. [via bm-c r759]")

SUMMARY = ("r759: S0 absorb 3 own faces (ce45d5558, rebase-race -> fetch+rev-list 0-incoming equivalence) + QA "
           "det-79th 5/5 (pid 27960, S6-first order, 93 trades, 1,017,839 frozen identity, determinism=True, png "
           "66,311B) + S6 40/40 rc0 (dualrun streak 51, CA flags disclosed: pool_starvation/supply_floor seat-gap "
           "known faces) + clone gate trio stale758=0 (boot hand-written) + DEC UNCHANGED / ORD single-hop consumed "
           "031E0E3E->2BD0F0C7 (bm-a CEO asset-feed receipt, not-involving-our-repo zero action); unacked=0; smoke "
           "49/49; marks lane 5 rows lunch watch; attrition CLEAN; post_review 45Y/0N/5W.")

VERIFY = ("smoke 49/49 + qa/smoke-r759.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True .err 0B "
          "png 66,311B) + results/_r759bmc_s6_log.txt 40/40 rc0 (dualrun ZERO-DRIFT streak 51) + "
          "results/_r759bmc_s05_facts.json double sweep (DEC EE70CEF0 UNCHANGED / ORD 031E0E3E->2BD0F0C7 single-hop "
          "consumed zero-action / unacked=0 / inbox 0 / shape-asserted) + results/_r759bmc_clone_receipt.json "
          "(stale758=0, compile OK x3) + attrition CLEAN + post_review 45 YES / 0 NO / 5 WAIT + quartet green "
          "(pin=5 no-op first-fire 12:55 / watchdog next-run 12:53 / claws MATCH) + orphan face=1 standing "
          "disposition (py_faces=4) + SAT alive rc0 + idle NOT-GREEN --worked (RAM 12.9% resident ComfyUI) + "
          "FleetLink listener pid 28396 health 200 + marks lane 5 rows (11:25 tail)")


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
    assert back.count(b"| r759 |") == 1, "r759 row not exactly-once in canonical tail (r865+r750 law)"
    assert b"| r759 |" in back.split(eol)[-2] + back.split(eol)[-3], "r759 row not in canonical tail"
    # 2) heartbeat
    hb = json.load(open(HB, encoding="utf-8"))
    for k in ("last_seen", "clock_read", "ts", "updated", "updated_at", "last_seen_at",
              "last_run_at", "last_ts", "current_task_at", "last_round_at"):
        hb[k] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["round_no"] = 760
    hb["last_round"] = 759
    hb["round_no_label"] = "round 759 (bm-c)"
    hb["current_task"] = TASK.replace("{TT}", NOW[11:16])
    hb["latest_artifact"] = ("qa/smoke-r759.md 5/5 + qa/equity-curve-r759.png 66,311B + results/_r759bmc_s6_log.txt "
                             "(40 legs rc0) + results/_r759bmc_clone_receipt.json (stale758=0 trio) @ " + NOW)
    hb["next_milestone"] = ("tonight post-close (10-08 15:30+): data-chain re-arm + REGIME_GUARD v3 first-new-bar "
                            "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring "
                            "+ first-marks verify (<= 10-08 23:59); next 5x = bm-c r760 (HANDOVER r756-760)")
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
    # 3) state (round_no 759->760; DEC held / ORD single-hop consumed facts-driven)
    st = json.load(open(ST, encoding="utf-8"))
    for k in ("clock_read", "last_seen", "ts", "updated", "updated_at", "last_run_at",
              "last_seen_at", "current_task_at", "last_round_at", "last_round_ts",
              "last_decisions_read_at"):
        st[k] = NOW
    st["heartbeat_epoch_utc"] = EPOCH
    st["round_no"] = 760
    st["last_round"] = 759
    st["round_no_label"] = "round 759 (bm-c)"
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
    st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r759 double "
                                    "sweeps = single-hop 031E0E3E -> 2BD0F0C7 (sweep-1 CHANGED: bm-a 12:44 e1390c9 "
                                    "CEO 1008 asset-feed execution receipt AD-049/050+AA-049 -- MiniGame/FluxVerse "
                                    "domain, not-involving-our-repo -> bm-c zero concrete action, watermark updated "
                                    "facts-driven); sweep-2 UNCHANGED 2BD0F0C7); hex-case comparison normalized per "
                                    "r711 pit law; facts-driven from results/_r759bmc_s05_facts.json, 40hex "
                                    "shape-asserted, never hand-typed (r583 S4 law)")
    st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r759 "
                                       "sweeps = UNCHANGED EE70CEF0 both passes (zero action, watermark held); "
                                       "facts-driven from results/_r759bmc_s05_facts.json, 64hex shape-asserted, "
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
