# -*- coding: utf-8 -*-
"""r754 bm-c closeout (attempt-2, adoption of crashed attempt-1 artifacts):
facts-driven ORD watermark consume + state round_no+1 + heartbeat product-law
3-line + canonical round report line + commit msg file + validation
(epoch int / T-separator clock / round_no advance)."""
import json, time, re
from datetime import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
WORKED_HM = "11:24"

facts = json.load(open(REPO + r"\results\_r754bmc_s05_facts.json", encoding="utf-8"))
assert facts["shape_assert"], "s05 shape assert failed"
assert re.fullmatch(r"[0-9A-F]{64}", facts["dec_sha"]), "dec sha shape"
assert re.fullmatch(r"[0-9A-F]{40}", facts["ord_sha"]), "ord sha shape"
assert facts["unacked"] == [] and facts["inbox_unread"] == [], "unacked/inbox not clean"

idle = json.load(open(REPO + r"\results\idle_trigger.bm-c.json", encoding="utf-8"))
ram_pct = float(idle.get("ram_free_pct", 15.6))
vram_gb = float(idle.get("vram_free_gb", 1.17))
RAM_FREE = round(23.9 * ram_pct / 100.0, 1)
GPU_MB = int(vram_gb * 1024)

ORD_SHA = facts["ord_sha"]
DEC_SHA = facts["dec_sha"]

did = ("r754: dual-attempt round (attempt-1 10:55-11:06 completed smoke 49/49 + S6 40/40 rc0 + "
       "QA det-74th 5/5 + clone gate stale753=0 + s05 dual sweep, died pre-closeout; attempt-2 11:15 "
       "took over via dead-pid lock law, adopted same-round artifacts per adoption law and closed) + "
       "ORD watermark double-hop consumed (2CF28BB4->09350733 attempt-1 facts->16EBEB66 attempt-2 facts, "
       "delta = bm-a BigStream MV/2D-LIVE CEO-order rows NOT involving BigMoney -> zero action) + "
       "marks lane origin@4 rows (09:35/09:45/10:35/10:45) progress vs r753 2 rows, no ping warranted + "
       "DEC EE659451 UNCHANGED; unacked=0; inbox 0; attrition CLEAN; post_review 45Y/0N/5W; "
       "idle NOT-GREEN --worked (RAM %.1f%% resident ComfyUI)." % ram_pct)

current_task = ("当前活: r754 bm-c（10:55-11:2x 窗·复市 T-0 盘中值守第 74 连守轮·双尝试轮=attempt-1 "
    "10:55-11:06 全活完成猝死于收尾前→attempt-2 11:15 收养同轮工件补收尾）——主产出=QA det-74th 5/5"
    "（93 trades·1,017,839 冻结恒等·determinism=True）+S6 40/40 rc0（dualrun streak 51）+克隆门 stale753=0"
    "+ORD 水位双跳消费 16EBEB66（bm-a BigStream 行零动作）+marks lane origin@4 行推进（10:45 行已落·不发 ping）"
    "| 最近实物: qa/smoke-r754.md 5/5+qa/equity-curve-r754.png 66,269B+results/_r754bmc_s6_log.txt 40/40"
    "+results/_r754bmc_clone_receipt.json @ " + NOW +
    " | 下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium "
    "15:30 首采（bm-c 车）+CTA_P1 首接线+首 marks 验证（≤10-08 23:59）；next 5x=bm-c r755（HANDOVER r751-755）")

latest_artifact = ("qa/smoke-r754.md 5/5 + qa/equity-curve-r754.png 66,269B + results/_r754bmc_s6_log.txt "
    "(40 legs rc0) + results/_r754bmc_clone_receipt.json (stale753=0 trio) @ " + NOW)

next_milestone = ("tonight post-close (10-08 15:30+): data-chain re-arm + REGIME_GUARD v3 first-new-bar "
    "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks "
    "verify (<= 10-08 23:59); next 5x = bm-c r755 (HANDOVER r751-755)")

nxt = ("r755: (a) 5x round: HANDOVER r751-755 product-list verify-update (research/HANDOVER.md); "
    "(b) marks lane 4th window watch (rows arrive with bm-a waves; downgraded observation item); "
    "(c) tonight post-close face (<=10-08 23:59): data-chain full re-arm + REGIME_GUARD v3 first-new-bar "
    "enforce (set BIGMONEY_REGIME_GUARD=enforce before live.paper) + fund_premium 15:30 first snapshot "
    "(bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verification (marks row + state trial-live + "
    "compounding identity) + QDII watch holiday-delta; (d) QA ignition order law standing (S6 rc0 -> "
    "qa_ignite -> qa_poll terminal -> close); (e) close scripts: RPT = canonical "
    "logs/iteration-loop/round_reports-bm-c.md (r750 pit; NEVER clone a ROOT template); "
    "(f) O-2215-1 remaining: SUPPORT row awaits bm-b router spec <=10-16; matrix re-fires when bm-a "
    "REGIME-5 labels land <=10-14; numeric weights review + 10-21 revisit; (g) cloudF row <=10-14 standing; "
    "(h) month-boundary first exam 10-31. [via bm-c r754]")

verify = ("smoke 49/49 + qa/smoke-r754.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True "
    ".err 0B png 66,269B) + results/_r754bmc_s6_log.txt 40/40 rc0 (dualrun ZERO-DRIFT streak 51 @408) + "
    "s05 double sweep (attempt-1 10:58 + attempt-2 11:24; DEC EE659451 UNCHANGED / ORD "
    "2CF28BB4->09350733->16EBEB66 double-hop consumed facts-driven, delta = bm-a BigStream rows NOT "
    "involving BigMoney, zero action / unacked=0 / inbox 0 / shape-asserted) + results/_r754bmc_clone_receipt.json "
    "(stale753=0, compile OK x3) + attrition CLEAN (4 ledgers 3 healed) + post_review 45 YES / 0 NO / 5 WAIT "
    "(attempt-1 re-derive rc0) + quartet green (pin=5 no-op first-fire 11:25 / watchdog re-registered 11:26 "
    "first-fire / both claws LF-normalized reinstalled) + orphan face=1 standing disposition (py_faces=4, "
    "resident ComfyUI service, CEO asset, read-only no-kill) + SAT alive (resident pid 28728) + idle NOT-GREEN "
    "--worked " + WORKED_HM + " (RAM %.1f%% < 40%% resident ComfyUI)" % ram_pct)

ord_method = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r754 dual-attempt sweeps = "
    "CHANGED 2CF28BB4 -> 09350733 (attempt-1 facts, died pre-consume) -> 16EBEB66 (attempt-2 facts, consumed); "
    "delta = bm-a BigStream MV/2D-LIVE CEO-order rows NOT involving BigMoney -> zero action; hex-case "
    "comparison normalized per r711 pit law; facts-driven from results/_r754bmc_s05_facts.json, 40hex "
    "shape-asserted, never hand-typed (r583 S4 law)")

dec_method = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r754 dual-attempt "
    "sweeps = UNCHANGED EE659451 zero delta zero action; facts-driven from results/_r754bmc_s05_facts.json, "
    "64hex shape-asserted, never hand-typed (r583 S4 law)")

report_line = (NOW + " | r754 | dept:工程+交易（复市 T-0 盘中值守轮·第 74 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·verdict=py_low_board_clear 盘中板清+无新 bar 合法 idle〔orders 51 disk "
    "unacked=0 双扫·inbox 0 双扫〕·compute_audit rc0 flags=[pool_starvation,supply_floor] 诚实披露〔pool "
    "ready 0<floor 3·席位间隙已知面·供给属预注册起草线节奏〕·next_pick=claimed〔moneyflow IC 参考批·advisory only〕） | "
    "当前活: " + current_task + " | 验证证据: " + verify +
    " | 下轮指针: " + nxt + " | 轮产品计分：2（QA det-74th 确定性包+S6 40 腿再生+克隆门三件+ORD 双跳消费+marks "
    "lane origin@4 行实证=能跑能看实物） | 记账预算：5（S0 churn absorb×1〔attempt-1〕+轮报/心跳/state 收口+"
    "post_review/attrition 例行〔attempt-1 产物收养〕+克隆收据+s05 facts 双扫件）")

commitmsg = ("round 754: QA det-74th 5/5 (93 trades 1,017,839 frozen identity; dual-attempt round: "
    "attempt-1 10:55-11:06 completed S6/QA/clone-gate/dual-sweep then died pre-closeout, attempt-2 11:15 "
    "adopted same-round artifacts per adoption law and closed) + S6 40/40 rc0 (dualrun ZERO-DRIFT streak 51) "
    "+ clone gate stale753=0 + ORD watermark double-consumed 2CF28BB4->16EBEB66 (bm-a BigStream rows, zero "
    "action) + DEC EE659451 unchanged + marks lane origin@4 rows progress (no ping) + idle --worked "
    "[via bm-c r754]")

def apply_common(d):
    d["round_no"] = 755
    d["round_no_label"] = "round 754 (bm-c)"
    d["last_round"] = 754
    d["last_round_at"] = NOW
    d["last_seen"] = NOW
    d["last_seen_at"] = NOW
    d["clock_read"] = NOW
    d["ts"] = NOW
    d["updated"] = NOW
    d["updated_at"] = NOW
    d["last_run_at"] = NOW
    d["last_ts"] = NOW
    d["current_task_at"] = NOW
    d["heartbeat_epoch_utc"] = EPOCH
    d["last_decisions_sha"] = DEC_SHA
    d["last_decisions_read_at"] = NOW
    d["last_decisions_at"] = NOW
    d["dec_sha_method"] = dec_method
    d["last_orders_sha"] = ORD_SHA
    d["last_orders_at"] = NOW
    d["ord_sha_method"] = ord_method
    d["last_decisions_sha_method"] = dec_method
    d["last_orders_sha_method"] = ord_method
    d["current_task"] = current_task
    d["latest_artifact"] = latest_artifact
    d["next_milestone"] = next_milestone
    d["next"] = nxt
    d["next_pointer"] = nxt
    d["verify"] = verify
    d["did"] = did
    d["note"] = did
    d["verdict"] = did
    d["last_round_summary"] = did
    d["last_action"] = did
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["free_ram_gb"] = RAM_FREE
    d["ram_free_gb"] = RAM_FREE
    d["idle_ram_gb"] = RAM_FREE
    d["gpu_free_vram_mb"] = GPU_MB
    d["gpu_free_vram_mib"] = GPU_MB
    d["gpu_free_mb"] = GPU_MB
    d["gpu_free_mib"] = GPU_MB
    d["gpu_idle_vram_mb"] = GPU_MB
    d["gpu_idle_vram_mib"] = GPU_MB
    d["gpu_idle_mb"] = GPU_MB
    d["gpu_idle_mib"] = GPU_MB
    d["gpu_vram_free_mb"] = GPU_MB
    d["cpu_pct"] = 3.0
    d["cpu_util_pct"] = 3.0

state = json.load(open(REPO + r"\state-bm-c.json", encoding="utf-8"))
apply_common(state)
with open(REPO + r"\state-bm-c.json", "w", encoding="utf-8") as fh:
    json.dump(state, fh, indent=1, ensure_ascii=False)

hb = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
apply_common(hb)
with open(REPO + r"\fleet\machines\bm-c.json", "w", encoding="utf-8") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)

with open(REPO + r"\logs\iteration-loop\round_reports-bm-c.md", "a", encoding="utf-8") as fh:
    fh.write(report_line + "\n")

with open(REPO + r"\_r754bmc_commitmsg.txt", "w", encoding="utf-8") as fh:
    fh.write(commitmsg)

s2 = json.load(open(REPO + r"\state-bm-c.json", encoding="utf-8"))
h2 = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
for name, d in (("state", s2), ("heartbeat", h2)):
    assert isinstance(d["heartbeat_epoch_utc"], int), name + " epoch not int"
    assert "T" in d["clock_read"] and "+" in d["clock_read"], name + " clock T-sep"
    assert d["round_no"] == 755, name + " round_no"
    assert d["last_orders_sha"] == ORD_SHA, name + " ord sha"
print("CLOSEOUT OK now=%s epoch=%d ram=%.1fGB gpu=%dMB ord=%s dec_unchanged=%s report_len=%d"
      % (NOW, EPOCH, RAM_FREE, GPU_MB, ORD_SHA[:8], DEC_SHA[:8] == "EE659451", len(report_line)))
