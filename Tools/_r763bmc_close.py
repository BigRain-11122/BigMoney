# -*- coding: utf-8 -*-
"""r763 bm-c round-close bookkeeping: round report line append to the CANONICAL
face logs/iteration-loop/round_reports-bm-c.md (fleet/README sec.6 + r750 pit
law -- canonical path ONLY, never the ROOT face), write-then-grep self-verify,
heartbeat fleet/machines/bm-c.json + state-bm-c.json field updates (epoch=int
law R170/R178, clock_read T-separator law R262, round_no 763->764, DEC
UNCHANGED held / ORD single-hop A327B7B1->F46EAD7C consumed zero-action
not-involving-our-repo per r583 facts-driven law, live cpu/ram/gpu re-sample).
Pattern credit: Tools/_r762bmc_close.py (canonical-RPT lineage)."""
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
FACTS = os.path.join(ROOT, "results", "_r763bmc_s05_facts.json")

REPORT_LINE = (
    "2026-10-08T{TT}+08:00 | r763 | dept:工程+交易（复市 T-0 盘中值守轮·第 83 bm-c 连守轮·午后段） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·py_low_board_clear 盘中板清合法 idle〔orders 51 disk unacked=0 双扫·"
    "inbox 0 双扫〕·compute_audit rc0 flags=[pool_starvation,supply_floor] 盘中席位间隙已知常在面如实披露"
    "〔pool ready 0<floor 3·supply_family_streak 270.7min〕·idle_trigger --worked〔idle_rounds=0 已清〕） | "
    "当前活: r763 bm-c（13:5x-14:0x 窗·复市 T-0 盘中值守第 83 连守轮）——"
    "S0 轮首脏 8=自有面（6 daemon live+r762 commitmsg 尾对）absorb 77f00f525→pull --rebase behind=2 干净重放 1/1"
    "（入站=bm-a r880 W186 pre-seat 探针 ADMIT 阶梯 46 例+churn absorb——引擎域座位波·不涉本仓）→"
    "克隆门三件（_r763bmc_boot.py 手写→双模替换 stale762=0 三件〔s05/s6/qa_ignite〕·compile OK×3·"
    "收据 _r763bmc_clone_receipt.json）——"
    "主产出=①DEC/ORD 双水位双扫（DEC EE70CEF0 UNCHANGED 两窗同哈希零动作；"
    "ORD 单跳 A327B7B1→F46EAD7C〔bm-a 28ca3c5 mv0001 v2 样片交付回执·承 D-BS-20261008-10——BigStream MV 域·"
    "不涉本仓→水位键更新零动作·facts-driven·unacked=0·inbox 0〕）"
    "②QA det-83rd 5/5（律序 S6 40 腿 rc0 收齐→点火 pid 20576→终态 .err 0B——"
    "93 trades·equity 1,017,839 冻结恒等〔r751-762 锚链续持〕·determinism=True·png 66,383B·83 连证·"
    "撞名披露：bm-b e5f476d48（其 r764 收养死轮 r763 工件）先在册 qa/smoke-r763.md+png——r761 F-20261008-03 "
    "命名空间撞名族第 2 活例·两包冻结恒等同数字〔93 trades/sharpe 0.159/maxdd -0.0433/win_rate 0.4624/"
    "determinism=True〕零科学证据损失·bm-b 版 git 史保全·HQ 修法提案在册零新动作）"
    "③S6 40/40 rc0 首过（dualrun ZERO-DRIFT streak 51 @408 条·cutoff 03:47〔池面未变幂等采样如实〕·"
    "py_watermark py_low_board_clear 合法盘中 idle·lane 守卫诚实 skip 面：bm-a/bm-b 车道族 stdout-only no-op·"
    "fund_premium pre-15:30 no-op→今晚 15:30 bm-c 车道首采·cta_p1_paper 无可标 bar〔cutoff 2026-09-30<"
    "paper_start 2026-10-08〕→今晚首 bar 自动接线）+"
    "④marks lane 值守判定（r762 指针(a) 闭：13:39+13:45 tick 已落·7 行推进·bm-a 宿主车道健康·"
    "14:0x 红标升级阈值不再触发=解除实证）+"
    "⑤FleetLink 常态自证（listener pid 28396 alive+health 200 ok node=bm-c port 8790）"
    "| 最近实物: qa/smoke-r763.md 5/5+qa/equity-curve-r763.png 66,383B+results/_r763bmc_s6_log.txt（40 腿 rc0）+"
    "results/_r763bmc_clone_receipt.json @ 2026-10-08T{TT}+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采"
    "（bm-c 车）+CTA_P1 首接线+首 marks 验证（≤10-08 23:59） | "
    "验证证据: smoke 49/49+QA 5/5（93 trades·1,017,839 冻结恒等〔r751-762 恒等锚一致〕·determinism=True·.err 0B·"
    "png 66,383B·market_clock cell=ORA·latest_panel_bar 2026-09-30 金周 no-op 如期）+S6 40/40 rc0（dualrun streak 51 "
    "ZERO-DRIFT @408·cutoff 03:47）+s05 双扫 facts-driven（DEC EE70CEF0 UNCHANGED/ORD 单跳 A327B7B1→F46EAD7C 消费·"
    "unacked=0·inbox 0·shape-asserted）+results/_r763bmc_clone_receipt.json（stale762=0·compile OK×3）+"
    "attrition CLEAN（4 ledgers·3 healed 史缩照录）+post_review 45✓/0✗/WAIT 5（零新增✗）+四件套四证"
    "（pin=5 no-op first-fire 14:05/watchdog first-fire 14:04/双爪 installed LF 归一）+"
    "FleetLink 常态自证（listener pid 28396 health 200）+孤儿面=1（py_faces=4·常驻 ComfyUI 服务面 pid 28732·"
    "CEO 资产·只读披露不击杀·既有处置维持）+SAT 活 rc0+idle_trigger --worked（idle_rounds=0·RAM 10.3%<40% 常驻 "
    "ComfyUI）+token_meter delta=0（L2 本地腿 0 today） | "
    "下轮指针: r764: (a) marks lane 盘中增量续守（bm-a 宿主·13:45 尾·观察项）；"
    "(b) tonight post-close face（≤10-08 23:59）数据链全 re-arm+REGIME_GUARD v3 first-new-bar enforce"
    "（live.paper 前设 BIGMONEY_REGIME_GUARD=enforce）+fund_premium 15:30 first snapshot（bm-c lane）+"
    "CTA_P1 first-bar auto-wiring+first-marks verification+QDII watch holiday-delta；"
    "(c) QA 点火序律值守（S6 rc0→qa_ignite→poll 终态→close）；(d) 收尾脚本 RPT=正典面（r750 坑·禁克隆 ROOT 模板）；"
    "(e) FleetLink 常态监听自证一行随轮（listener pid/health）；(f) D-20261008-06 后缀命名律执法面"
    "（_r764bmc_* 前缀范式照旧）+命令查重律执法面；(g) bm-b FleetLink 回执候（他机车道零干预）；"
    "(h) 月界首考 10-31；next 5x=bm-c r765（HANDOVER r761-765）。[via bm-c r763] | "
    "轮产品计分：2（QA det-83rd 确定性包+S6 40 腿再生+克隆门三件+双水位双扫核验+marks 判定闭=能跑能看实物） | "
    "记账预算：5（S0 churn absorb×1+轮报/心跳/state 收口+post_review/attrition 例行+克隆收据+s05 facts 双扫件） | "
    "孤儿面=1 standing（py_faces=4 常驻 ComfyUI 服务·CEO 资产·只读不杀）")

TASK = (
    "当前活: r763 bm-c（13:5x-14:0x 窗·复市 T-0 盘中值守第 83 连守轮）——"
    "主产出=①QA det-83rd 5/5（93 trades·1,017,839 冻结恒等·determinism=True·png 66,383B·83 连证·"
    "bm-b e5f476d48 先在册撞名披露=r761 F-20261008-03 族第 2 活例·两包恒等零损失）"
    "②DEC UNCHANGED/ORD 单跳 A327B7B1→F46EAD7C 消费零动作（BigStream MV 域·不涉本仓·unacked=0·inbox 0）"
    "③S6 40/40 rc0（dualrun streak 51）+克隆门 stale762=0"
    "+marks lane 判定闭（13:39/13:45 tick 落·7 行·红标阈值解除实证）"
    "+FleetLink 自证 pid 28396 health 200 port 8790"
    "| 最近实物: qa/smoke-r763.md 5/5+qa/equity-curve-r763.png 66,383B+results/_r763bmc_s6_log.txt 40/40+"
    "results/_r763bmc_clone_receipt.json @ 2026-10-08T{TT}+08:00 | "
    "下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 enforce+fund_premium 15:30 首采（bm-c 车）+"
    "CTA_P1 首接线+首 marks 验证（≤10-08 23:59）；next 5x=bm-c r765（HANDOVER r761-765）")

ACTIVITY = (
    "r763 bm-c: reopen T-0 intraday watch round 83rd consecutive (13:5x-14:0x window, afternoon session). "
    "(1) S0: round-start dirty 8 = own faces (6 daemon live + r762 commitmsg tail pair) -> absorb 77f00f525 -> "
    "pull --rebase behind=2 clean replay 1/1 (incoming = bm-a r880 W186 pre-seat probe ADMIT staircase 46th + "
    "churn absorb, engine-domain seat wave, not-involving-our-repo). (2) S0.5 double sweep: DEC EE70CEF0 "
    "UNCHANGED both passes (zero action, watermark held); ORD single-hop A327B7B1 -> F46EAD7C via commit 28ca3c5 "
    "(mv0001 v2 sample-delivery receipt under D-BS-20261008-10 execution -- BigStream MV domain, "
    "not-involving-our-repo -> watermark update zero action, facts-driven); fleet orders 51 disk unacked=0; "
    "inbox 0. (3) S1 smoke 49/49 + SAT rc0 alive + orphan probe py_faces=4 orphans=1 (resident ComfyUI service "
    "face pid 28732, CEO asset, read-only no-kill, standing disposition) + idle NOT-GREEN (RAM 10.3% < 40% "
    "resident ComfyUI) --worked 14:02 (idle_rounds=0). (4) MAIN PRODUCTS: (a) lineage clone gate: "
    "_r763bmc_boot.py HAND-WRITTEN -> double-replacement stale762=0 across s05/s6/qa_ignite, compile gate "
    "PASS, receipt _r763bmc_clone_receipt.json. (b) S6 40/40 rc0 via canonical clone (dualrun ZERO-DRIFT "
    "streak 51 @408 entries cutoff 03:47 -- pool blob unchanged, idempotent sample honestly reported; "
    "compute_audit rc0 flags=[pool_starvation,supply_floor] intraday board-clear known standing faces honestly "
    "disclosed (supply_family_streak 270.7 min, pool ready=0 < floor 3); py_watermark py_low_board_clear legal "
    "intraday idle; lane guards honest skips: bm-a/bm-b owned lanes stdout-only no-op; fund_premium pre-15:30 "
    "no-op -> tonight 15:30 bm-c-lane first snapshot; cta_p1_paper no markable bar (cutoff 2026-09-30 < "
    "paper_start 2026-10-08) -> tonight first-bar auto-wiring). (c) QA det-83rd per ignition order law (r749 "
    "pit): S6 full-chain rc0 collected FIRST -> qa_ignite detached pid 20576 -> poll terminal (.err 0B): 93 "
    "trades, equity 1,017,839 frozen identity (r751-762 anchor chain holds), determinism=True, PNG 66,383B, "
    "market_clock cell=ORA, latest_panel_bar 2026-09-30 golden-week no-op expected, 83rd consecutive pack. "
    "Collision disclosure: bm-b commit e5f476d48 (its r764 dead-r763 churn-absorb) already carries "
    "qa/smoke-r763.md + equity-curve-r763.png in git history -- r761 F-20261008-03 qa-pack namespace "
    "collision family SECOND live case; both packs share identical frozen-identity numbers (93 trades / "
    "sharpe 0.159 / maxdd -0.0433 / win_rate 0.4624 / determinism=True) = zero scientific evidence loss; "
    "bm-b version git-preserved (git show e5f476d48:qa/smoke-r763.md); HQ namespace-fix proposal already on "
    "file, zero new action beyond honest disclosure. (d) marks lane verdict (r762 pointer (a) CLOSED): 13:39 "
    "and 13:45 ticks landed, 7 rows progressing, bm-a host single-writer lane healthy; 14:0x red-flag "
    "escalation threshold NOT triggered = disarmed per r762 addendum, now verified with fresh ticks. "
    "(e) FleetLink self-cert: listener pid 28396 alive, health 200 ok node=bm-c port 8790. (5) close: "
    "post_review 45Y/0N/5W (zero new NO) + attrition CLEAN (4 ledgers, 3 healed history-shrink notes) + "
    "quartet (pin=5 no-op first-fire 14:05 / watchdog first-fire 14:04 / claws installed LF-normalized) + "
    "commit/push/verify.")

NEXT_PTR = (
    "r764: (a) marks lane intraday watch continuation (bm-a host lane, 13:45 tail, observation item); "
    "(b) tonight post-close face (<=10-08 23:59): data-chain full re-arm + REGIME_GUARD v3 first-new-bar "
    "enforce (set BIGMONEY_REGIME_GUARD=enforce before live.paper) + fund_premium 15:30 first snapshot "
    "(bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verification (marks row + state trial-live + "
    "compounding identity) + QDII watch holiday-delta; (c) QA ignition order law standing (S6 rc0 -> "
    "qa_ignite -> qa_poll terminal -> close); (d) close scripts: RPT path = canonical "
    "logs/iteration-loop/round_reports-bm-c.md (r750 pit; NEVER clone a ROOT template); (e) FleetLink "
    "standing self-cert line per round (listener pid/health); (f) D-20261008-06 suffix-naming law "
    "(_r764bmc_* prefix pattern) + command-dedup law enforcement face; (g) bm-b FleetLink receipt awaited "
    "(other-machine lane, zero intervention); (h) month-boundary first exam 10-31; next 5x = bm-c r765 "
    "(HANDOVER r761-765). [via bm-c r763]")

SUMMARY = ("r763: QA det-83rd 5/5 (pid 20576, S6-first order, 93 trades, 1,017,839 frozen identity, "
           "determinism=True, png 66,383B, 83rd consecutive; bm-b e5f476d48 prior-in-history collision "
           "disclosed = F-20261008-03 family 2nd live case, identical frozen numbers zero evidence loss) + "
           "S6 40/40 rc0 (dualrun streak 51; CA flags [pool_starvation,supply_floor] intraday known standing "
           "faces; fund_premium/cta_p1 pre-15:30 no-op -> tonight first snapshot/auto-wiring) + clone gate "
           "stale762=0 + DEC UNCHANGED / ORD single-hop consumed A327B7B1->F46EAD7C (bm-a 28ca3c5 mv0001 v2 "
           "sample receipt, BigStream MV domain, not-involving-our-repo zero action); unacked=0; smoke 49/49; "
           "marks lane 7 rows (13:39+13:45 ticks landed, escalation disarmed verified); attrition CLEAN; "
           "post_review 45Y/0N/5W.")

VERIFY = ("smoke 49/49 + qa/smoke-r763.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True "
          ".err 0B png 66,383B) + results/_r763bmc_s6_log.txt 40/40 rc0 (dualrun ZERO-DRIFT streak 51) + "
          "results/_r763bmc_s05_facts.json double sweep (DEC EE70CEF0 UNCHANGED / ORD single-hop "
          "A327B7B1->F46EAD7C consumed zero-action / unacked=0 / inbox 0 / shape-asserted) + "
          "results/_r763bmc_clone_receipt.json (stale762=0, compile OK x3) + attrition CLEAN (4 ledgers) + "
          "post_review 45 YES / 0 NO / 5 WAIT (zero new NO) + quartet green (pin=5 no-op first-fire 14:05 / "
          "watchdog first-fire 14:04 / claws installed LF-normalized x2) + orphan face=1 standing disposition "
          "(py_faces=4) + SAT alive rc0 + idle_trigger --worked (idle_rounds=0, RAM 10.3% resident ComfyUI) + "
          "FleetLink listener pid 28396 health 200 port 8790 + marks lane 7 rows (13:45 tail, escalation "
          "disarmed verified) + token_meter delta=0")


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
    assert back.count(b"| r763 |") == 1, "r763 row not exactly-once in canonical tail (r865+r750 law)"
    assert b"| r763 |" in back.split(eol)[-2] + back.split(eol)[-3], "r763 row not in canonical tail"
    # 2) heartbeat
    hb = json.load(open(HB, encoding="utf-8"))
    for k in ("last_seen", "clock_read", "ts", "updated", "updated_at", "last_seen_at",
              "last_run_at", "last_ts", "current_task_at", "last_round_at"):
        hb[k] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["round_no"] = 764
    hb["last_round"] = 763
    hb["round_no_label"] = "round 763 (bm-c)"
    hb["current_task"] = TASK.replace("{TT}", NOW[11:16])
    hb["latest_artifact"] = ("qa/smoke-r763.md 5/5 + qa/equity-curve-r763.png 66,383B + results/_r763bmc_s6_log.txt "
                             "(40 legs rc0) + results/_r763bmc_clone_receipt.json (stale762=0 trio) @ " + NOW)
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
    # 3) state (round_no 763->764; DEC held / ORD single-hop consumed facts-driven)
    st = json.load(open(ST, encoding="utf-8"))
    for k in ("clock_read", "last_seen", "ts", "updated", "updated_at", "last_run_at",
              "last_seen_at", "current_task_at", "last_round_at", "last_round_ts",
              "last_decisions_read_at"):
        st[k] = NOW
    st["heartbeat_epoch_utc"] = EPOCH
    st["round_no"] = 764
    st["last_round"] = 763
    st["round_no_label"] = "round 763 (bm-c)"
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
    st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r763 double "
                                    "sweeps = single-hop A327B7B1 -> F46EAD7C (bm-a commit 28ca3c5: mv0001 v2 "
                                    "sample-delivery receipt under D-BS-20261008-10 execution, BigStream MV domain, "
                                    "our-repo hits 0 -> bm-c zero concrete action, watermark updated facts-driven); "
                                    "hex-case comparison normalized per r711 pit law; facts-driven from "
                                    "results/_r763bmc_s05_facts.json, 40hex shape-asserted, never hand-typed "
                                    "(r583 S4 law)")
    st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r763 "
                                       "sweeps = UNCHANGED EE70CEF0 both passes (zero action, watermark held); "
                                       "facts-driven from results/_r763bmc_s05_facts.json, 64hex shape-asserted, "
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
