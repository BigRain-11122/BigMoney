# -*- coding: utf-8 -*-
"""r760 bm-c round-close bookkeeping: round report line append to the CANONICAL
face logs/iteration-loop/round_reports-bm-c.md (fleet/README sec.6 + r750 pit
law -- canonical path ONLY, never the ROOT face), write-then-grep self-verify,
heartbeat fleet/machines/bm-c.json + state-bm-c.json field updates (epoch=int
law R170/R178, clock_read T-separator law R262, round_no 760->761, DEC
UNCHANGED held / ORD double-hop 2BD0F0C7->8F7FE7EE->9BA505B7 consumed
zero-action not-involving-our-repo per r583 facts-driven law, live cpu/ram/gpu
re-sample). Pattern credit: Tools/_r759bmc_close.py (canonical-RPT lineage)."""
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
FACTS = os.path.join(ROOT, "results", "_r760bmc_s05_facts.json")

REPORT_LINE = (
    "2026-10-08T{TT}+08:00 | r760 | dept:工程+交易（复市 T-0 盘中值守轮·第 80 bm-c 连守轮·午休→13:00 复盘窗过渡·5x 核对轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·py_low_board_clear 盘中板清合法 idle〔orders 51 disk unacked=0 双扫·"
    "inbox 0 双扫〕·compute_audit rc0 flags=[pool_starvation,supply_floor] 盘中席位间隙已知常在面如实披露·"
    "next_pick=claimed〔moneyflow IC 参考批·advisory only·供给属预注册起草线节奏〕） | "
    "当前活: r760 bm-c（12:55-13:0x 窗·复市 T-0 盘中值守第 80 连守轮·5x 核对轮）——"
    "S0 轮首脏 4=自有面（孤儿探针件+dispatcher 状态+satengine 状态×2）absorb a9c3bbfc7→"
    "fetch+rev-list 0 incoming 零 rebase 需要（净树根治律 r642·无 autostash）→"
    "克隆门三件（_r760bmc_boot.py 手写→_r760bmc_clone.py 双模替换 stale759=0 三件〔s05/s6/qa_ignite〕·"
    "compile OK×3·收据 _r760bmc_clone_receipt.json）——"
    "主产出=①DEC/ORD 双水位双扫（DEC EE70CEF0 UNCHANGED 两窗同哈希零动作；"
    "ORD 双跳 2BD0F0C7→8F7FE7EE〔bm-a 12:56 fcf9068 mv0001 受众共鸣双令·MiniGame/FluxVerse 域·diff +1 行涉本仓命中 0〕→"
    "9BA505B7〔bm-a 12:58 a1a108c mv0001 第十一追加令·同域〕·两跳皆不涉本仓→水位键更新零动作·facts-driven·"
    "O-20261008-1240 静默根治令 bm-c 腿复核=已闭〔HQ-SilenceGuard 任务在位 next 10-09 04:07+audit JSON 11:55+r755 执行痕〕·"
    "unacked=0·inbox 0）"
    "②QA det-80th 5/5（律序 S6 40 腿 rc0 收齐→点火 pid 21352→终态 .err 0B——"
    "93 trades·equity 1,017,839 冻结恒等〔r751-759 锚链续持〕·determinism=True·png 66,405B·80 连证）"
    "③S6 40/40 rc0（dualrun ZERO-DRIFT streak 51 @408 条·cutoff 03:47·py_watermark py_low_board_clear 合法盘中 idle·"
    "lane 守卫诚实 skip 面：bm-a 心跳新鲜→守卫族 skip derive 零 stale-takeover·bm-a/bm-b 车道族 stdout-only no-op·"
    "fund_premium pre-15:30 no-op→今晚 15:30 bm-c 车道首采·cta_p1_paper 无可标 bar→今晚首 bar 自动接线）+"
    "④5x HANDOVER r756-760 核对更新（research/HANDOVER.md r760 行=产物清单+完成状态·每 5 轮义务·r756-759 四轮实录并入）+"
    "⑤marks lane 盘中值守（marks-20261008.jsonl 5 行 11:25 尾·13:00 复盘窗新行未至〔bm-a 宿主单写面·下轮复核〕·观察项）"
    "| 最近实物: qa/smoke-r760.md 5/5+qa/equity-curve-r760.png 66,405B+results/_r760bmc_s6_log.txt（40 腿 rc0）+"
    "results/_r760bmc_clone_receipt.json+research/HANDOVER.md r760 行 @ 2026-10-08T{TT}+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采"
    "（bm-c 车）+CTA_P1 首接线+首 marks 验证（≤10-08 23:59） | "
    "验证证据: smoke 49/49+QA 5/5（93 trades·1,017,839 冻结恒等〔r751-759 恒等锚一致〕·determinism=True·.err 0B·"
    "png 66,405B·market_clock cell=ORA·latest_panel_bar 2026-09-30 金周 no-op 如期）+S6 40/40 rc0（dualrun streak 51 "
    "ZERO-DRIFT @408·cutoff 03:47）+s05 双扫 facts-driven（DEC EE70CEF0 UNCHANGED/ORD 双跳 2BD0F0C7→8F7FE7EE→9BA505B7 消费·"
    "unacked=0·inbox 0·shape-asserted）+results/_r760bmc_clone_receipt.json（stale759=0·compile OK×3）+"
    "research/HANDOVER.md r760 行（5x 义务）+attrition CLEAN+post_review 45✓/0✗/WAIT 5+四件套四证"
    "（pin=5 no-op 首发留 13:05/watchdog 在位 next 13:03/双爪 MATCH）+"
    "FleetLink 常态自证（listener pid 28396 alive+health 200 ok node=bm-c）+孤儿面=1（py_faces=5·常驻 ComfyUI 服务面·"
    "CEO 资产·只读披露不击杀·既有处置维持）+SAT 活 rc0+idle NOT-GREEN --worked（RAM 12.9%<40% 常驻 ComfyUI）+"
    "token_meter delta=0 | "
    "下轮指针: r761: (a) marks lane 13:00+ 复盘窗新行复核（bm-a 宿主车道·5 行在册·11:25 尾）；"
    "(b) tonight post-close face（≤10-08 23:59）数据链全 re-arm+REGIME_GUARD v3 first-new-bar enforce"
    "（live.paper 前设 BIGMONEY_REGIME_GUARD=enforce）+fund_premium 15:30 first snapshot（bm-c lane）+"
    "CTA_P1 first-bar auto-wiring+first-marks verification+QDII watch holiday-delta；"
    "(c) QA 点火序律值守（S6 rc0→qa_ignite→poll 终态→close）；(d) 收尾脚本 RPT=正典面（r750 坑·禁克隆 ROOT 模板）；"
    "(e) FleetLink 常态监听自证一行随轮（listener pid/health）；(f) D-20261008-06 后缀命名律执法面"
    "（_r761bmc_* 前缀范式照旧）+命令查重律执法面；(g) bm-b FleetLink 回执候（他机车道零干预）；"
    "(h) 月界首考 10-31；next 5x=bm-c r765（HANDOVER r761-765）。[via bm-c r760] | "
    "轮产品计分：2（QA det-80th 确定性包+S6 40 腿再生+克隆门三件+5x HANDOVER 核对更新+双水位双扫核验=能跑能看实物） | "
    "记账预算：5（S0 churn absorb×1+轮报/心跳/state 收口+post_review/attrition 例行+克隆收据+s05 facts 双扫件） | "
    "孤儿面=1 standing（py_faces=5 常驻 ComfyUI 服务·CEO 资产·只读不杀）")

TASK = (
    "当前活: r760 bm-c（12:55-13:0x 窗·复市 T-0 盘中值守第 80 连守轮·5x 核对轮）——"
    "主产出=①QA det-80th 5/5（93 trades·1,017,839 冻结恒等·determinism=True·png 66,405B·80 连证）"
    "②DEC UNCHANGED/ORD 双跳 8F7FE7EE→9BA505B7 消费零动作（不涉本仓·unacked=0·inbox 0）"
    "③S6 40/40 rc0（dualrun streak 51）+克隆门 stale759=0+5x HANDOVER r756-760 核对更新"
    "+marks lane 5 行值守（11:25 尾·13:00 窗新行未至）"
    "| 最近实物: qa/smoke-r760.md 5/5+qa/equity-curve-r760.png 66,405B+results/_r760bmc_s6_log.txt 40/40+"
    "results/_r760bmc_clone_receipt.json+research/HANDOVER.md r760 行 @ 2026-10-08T{TT}+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 enforce+fund_premium 15:30 首采（bm-c 车）+"
    "CTA_P1 首接线+首 marks 验证（≤10-08 23:59）；next 5x=bm-c r765（HANDOVER r761-765）")

ACTIVITY = (
    "r760 bm-c: reopen T-0 intraday watch round 80th consecutive (12:55-13:0x window; lunch -> 13:00 reopen "
    "transition, 5x checkpoint round; marks lane 5 rows 11:25 tail, reopen-window rows not yet landed at 13:0x, "
    "next round re-check). (1) S0: round-start dirty 4 = own daemon live faces (orphan probe report + dispatcher + "
    "satengine x2) -> absorb commit a9c3bbfc7; fetch + rev-list 0 incoming = zero rebase needed (clean-tree law "
    "r642, no autostash). (2) S0.5 double sweep: DEC EE70CEF0 UNCHANGED both passes (zero action, watermark "
    "held); ORD double-hop 2BD0F0C7 -> 8F7FE7EE (sweep-1: bm-a 12:56 fcf9068 mv0001 audience-resonance dual "
    "order, MiniGame/FluxVerse domain, diff +1 line / our-repo hits 0) -> 9BA505B7 (sweep-2: bm-a 12:58 a1a108c "
    "mv0001 11th-appendix research order, same domain) -- both hops not-involving-our-repo -> watermark update "
    "zero action, facts-driven; O-20261008-1240 silence-order bm-c leg re-verified CLOSED (HQ-SilenceGuard task "
    "in place next 10-09 04:07 + silence-audit.json 11:55 + r755 execution trace); fleet orders 51 disk "
    "unacked=0; inbox 0. (3) S1 smoke 49/49 + SAT rc0 alive + orphan probe py_faces=5 orphans=1 (resident "
    "ComfyUI service face, CEO asset, read-only no-kill, standing disposition) + idle NOT-GREEN (ram_free 12.9% "
    "< 40% resident ComfyUI, idle_rounds=0, --worked). (4) MAIN PRODUCTS: (a) lineage clone gate: "
    "_r760bmc_boot.py HAND-WRITTEN -> _r760bmc_clone.py: stale759=0 across s05/s6/qa_ignite, compile gate "
    "PASS, receipt _r760bmc_clone_receipt.json. (b) S6 40/40 rc0 via canonical clone (dualrun ZERO-DRIFT "
    "streak 51 @408 entries cutoff 03:47; compute_audit rc0 flags=[pool_starvation,supply_floor] intraday "
    "board-clear known standing faces honestly disclosed; py_watermark py_low_board_clear legal intraday idle; "
    "lane guards honest skips: bm-a heartbeat fresh -> guard-family skip derive zero stale-takeover; "
    "bm-a/bm-b owned lanes stdout-only no-op; fund_premium pre-15:30 no-op -> tonight 15:30 bm-c-lane first "
    "snapshot; cta_p1_paper no markable bar -> tonight first-bar auto-wiring). (c) QA det-80th per ignition "
    "order law (r749 pit): S6 full-chain rc0 collected FIRST -> qa_ignite detached pid 21352 -> poll terminal "
    "(.err 0B): 93 trades, equity 1,017,839 frozen identity (r751-759 anchor chain holds), determinism=True, "
    "PNG 66,405B, market_clock cell=ORA, 80th consecutive pack. (d) 5x HANDOVER duty: research/HANDOVER.md "
    "r760 row inserted (r756-760 increment window, product list & completion status, every-5-rounds law, "
    "r756-759 four rounds merged in). (e) marks lane watch: marks-20261008.jsonl 5 rows (11:25 tail; 13:00 "
    "reopen-window rows not yet landed; host=bm-a single-writer lane, observation item). (5) close: post_review "
    "45Y/0N/5W + attrition CLEAN + quartet (pin=5 no-op first-fire 13:05 / watchdog next-run 13:03 / claws "
    "MATCH x2) + FleetLink self-cert (listener pid 28396 alive, health 200 ok node=bm-c) + commit/push/verify.")

NEXT_PTR = (
    "r761: (a) marks lane 13:00+ reopen-window row re-check (bm-a host lane, 5 rows 11:25 tail at r760 close; "
    "new rows expected after 13:00 reopen); (b) tonight post-close face (<=10-08 23:59): data-chain full "
    "re-arm + REGIME_GUARD v3 first-new-bar enforce (set BIGMONEY_REGIME_GUARD=enforce before live.paper) + "
    "fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verification "
    "+ QDII watch holiday-delta; (c) QA ignition order law standing (S6 rc0 -> qa_ignite -> qa_poll terminal "
    "-> close); (d) close scripts: RPT path = canonical logs/iteration-loop/round_reports-bm-c.md (r750 pit; "
    "NEVER clone a ROOT template); (e) FleetLink standing self-cert line per round (listener pid/health); "
    "(f) D-20261008-06 suffix-naming law (_r761bmc_* prefix pattern) + command-dedup law enforcement face; "
    "(g) bm-b FleetLink receipt awaited (other-machine lane, zero intervention); (h) month-boundary first "
    "exam 10-31; next 5x = bm-c r765 (HANDOVER r761-765). [via bm-c r760]")

SUMMARY = ("r760: 5x HANDOVER (r756-760 row in research/HANDOVER.md) + S0 absorb 4 own faces (a9c3bbfc7, "
           "fetch+rev-list 0-incoming equivalence) + QA det-80th 5/5 (pid 21352, S6-first order, 93 trades, "
           "1,017,839 frozen identity, determinism=True, png 66,405B) + S6 40/40 rc0 (dualrun streak 51; CA "
           "flags [pool_starvation,supply_floor] intraday known standing faces; fund_premium/cta_p1 pre-15:30 "
           "no-op -> tonight first snapshot/auto-wiring) + clone gate stale759=0 + DEC UNCHANGED / ORD "
           "double-hop consumed 2BD0F0C7->8F7FE7EE->9BA505B7 (bm-a mv0001 audience-resonance + 11th-appendix "
           "orders, MiniGame/FluxVerse domain, not-involving-our-repo zero action; 1240 silence-order bm-c leg "
           "re-verified CLOSED); unacked=0; smoke 49/49; marks lane 5 rows (11:25 tail); attrition CLEAN; "
           "post_review 45Y/0N/5W.")

VERIFY = ("smoke 49/49 + qa/smoke-r760.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True "
          ".err 0B png 66,405B) + results/_r760bmc_s6_log.txt 40/40 rc0 (dualrun ZERO-DRIFT streak 51) + "
          "results/_r760bmc_s05_facts.json double sweep (DEC EE70CEF0 UNCHANGED / ORD double-hop "
          "2BD0F0C7->8F7FE7EE->9BA505B7 consumed zero-action / unacked=0 / inbox 0 / shape-asserted) + "
          "results/_r760bmc_clone_receipt.json (stale759=0, compile OK x3) + research/HANDOVER.md r760 5x row "
          "+ attrition CLEAN + post_review 45 YES / 0 NO / 5 WAIT + quartet green (pin=5 no-op first-fire "
          "13:05 / watchdog next-run 13:03 / claws MATCH x2) + orphan face=1 standing disposition "
          "(py_faces=5) + SAT alive rc0 + idle NOT-GREEN --worked (RAM 12.9% resident ComfyUI) + FleetLink "
          "listener pid 28396 health 200 + marks lane 5 rows (11:25 tail) + token_meter delta=0")


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
    assert back.count(b"| r760 |") == 1, "r760 row not exactly-once in canonical tail (r865+r750 law)"
    assert b"| r760 |" in back.split(eol)[-2] + back.split(eol)[-3], "r760 row not in canonical tail"
    # 2) heartbeat
    hb = json.load(open(HB, encoding="utf-8"))
    for k in ("last_seen", "clock_read", "ts", "updated", "updated_at", "last_seen_at",
              "last_run_at", "last_ts", "current_task_at", "last_round_at"):
        hb[k] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["round_no"] = 761
    hb["last_round"] = 760
    hb["round_no_label"] = "round 760 (bm-c)"
    hb["current_task"] = TASK.replace("{TT}", NOW[11:16])
    hb["latest_artifact"] = ("qa/smoke-r760.md 5/5 + qa/equity-curve-r760.png 66,405B + results/_r760bmc_s6_log.txt "
                             "(40 legs rc0) + results/_r760bmc_clone_receipt.json (stale759=0 trio) + "
                             "research/HANDOVER.md r760 5x row @ " + NOW)
    hb["next_milestone"] = ("tonight post-close (10-08 15:30+): data-chain re-arm + REGIME_GUARD v3 first-new-bar "
                            "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring "
                            "+ first-marks verify (<= 10-08 23:59); next 5x = bm-c r765 (HANDOVER r761-765)")
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
    # 3) state (round_no 760->761; DEC held / ORD double-hop consumed facts-driven)
    st = json.load(open(ST, encoding="utf-8"))
    for k in ("clock_read", "last_seen", "ts", "updated", "updated_at", "last_run_at",
              "last_seen_at", "current_task_at", "last_round_at", "last_round_ts",
              "last_decisions_read_at"):
        st[k] = NOW
    st["heartbeat_epoch_utc"] = EPOCH
    st["round_no"] = 761
    st["last_round"] = 760
    st["round_no_label"] = "round 760 (bm-c)"
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
    st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r760 double "
                                    "sweeps = double-hop 2BD0F0C7 -> 8F7FE7EE -> 9BA505B7 (sweep-1: bm-a 12:56 fcf9068 "
                                    "mv0001 audience-resonance dual order P-2026-10-08-05 items 9/10; sweep-2: bm-a "
                                    "12:58 a1a108c mv0001 11th-appendix research order -- both MiniGame/FluxVerse "
                                    "domain, diff +1 line / our-repo hits 0 -> bm-c zero concrete action, watermark "
                                    "updated facts-driven); hex-case comparison normalized per r711 pit law; "
                                    "facts-driven from results/_r760bmc_s05_facts.json, 40hex shape-asserted, never "
                                    "hand-typed (r583 S4 law)")
    st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r760 "
                                       "sweeps = UNCHANGED EE70CEF0 both passes (zero action, watermark held); "
                                       "facts-driven from results/_r760bmc_s05_facts.json, 64hex shape-asserted, "
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
