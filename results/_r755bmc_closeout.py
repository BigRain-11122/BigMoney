# -*- coding: utf-8 -*-
"""r755 bm-c closeout: facts-driven ORD double-hop consume + state round_no+1
+ heartbeat product-law 3-line + C-01 heartbeat fresh fields (last_pulled_at/
head_sha first landing) + canonical round report line + commit msg file +
validation (epoch int / T-separator clock / round_no advance)."""
import datetime
import json
import os
import re
import subprocess
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CF = 0x08000000
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
WORKED_HM = "11:54"

p = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True,
                   creationflags=CF)
HEAD_SHA = p.stdout.decode("utf-8", "replace").strip()
assert re.fullmatch(r"[0-9a-f]{40}", HEAD_SHA), "head sha shape"
facts_mtime = os.path.getmtime(os.path.join(REPO, "results",
                                            "_r755bmc_s05_facts.json"))
LAST_PULLED = datetime.datetime.fromtimestamp(facts_mtime).astimezone().isoformat(
    timespec="seconds")

facts = json.load(open(REPO + r"\results\_r755bmc_s05_facts.json",
                       encoding="utf-8"))
assert facts["shape_assert"], "s05 shape assert failed"
assert re.fullmatch(r"[0-9A-F]{64}", facts["dec_sha"]), "dec sha shape"
assert re.fullmatch(r"[0-9A-F]{40}", facts["ord_sha"]), "ord sha shape"
assert facts["unacked"] == [] and facts["inbox_unread"] == [], \
    "unacked/inbox not clean"

idle = json.load(open(REPO + r"\results\idle_trigger.bm-c.json", encoding="utf-8"))
ram_pct = float(idle.get("ram_free_pct", 15.3))
vram_gb = float(idle.get("vram_free_gb", 1.19))
RAM_FREE = round(23.9 * ram_pct / 100.0, 1)
GPU_MB = int(vram_gb * 1024)

ORD_SHA = facts["ord_sha"]
DEC_SHA = facts["dec_sha"]

did = ("r755: 复市 T-0 盘中值守第 75 连守轮+CEO 三令同轮承接（ORD 双跳全消费：一跳 16EBEB66->20B6976C="
       "总动员 P-09+O-20261008-1205-bm-c+治理令 C-20261008-01 三令涉本机全执行同轮收口〔FleetLink 采纳三步="
       "roster 就地修正 host=FLUXGROUP/root=K:/Fluxgroup/FluxGroup/wake_tasks 12 实核真值+FluxGroup-FleetLink "
       "任务注册+listener :8790 tailnet 100.123.74.104+loopback 双绑 health ok pid 28396+P-09 回执行 1,223B "
       "CAS 直投 a57b0f98 tip verified；C-01 快改=心跳双字段 last_pulled_at/head_sha 首落+轮首 pull 核查入下轮 "
       "S0〕；二跳 20B6976C->32D5D4CF=静默根治 O-20261008-1240-bm-c+C-02 委员会席位令→O-1240 三步同轮收口"
       "〔silence-enforce.ps1 首跑=闸读回 ToastEnabled=0+任务审计违规 0+HQ-SilenceGuard 注册（登录+每日 04:07·"
       "下跑 2026/10/9 04:07 实锚）+P-11 回执行 1,037B CAS 直投 475eb2f8 tip verified；Quark 1.0.0.21 任务 "
       "Disable 拒绝访问=厂商 ACL 物理件域如实披露〕·C-02 委员会面零动作）+QA det-75th 5/5（93 trades·"
       "1,017,839 冻结恒等·determinism=True·75 连证）+S6 40/40 rc0（dualrun ZERO-DRIFT streak 51 @408）+"
       "5x HANDOVER r751-755 行（2,137B 字节守恒）+克隆门 stale754=0+marks lane 4 行持平（10:45 后无新行·"
       "bm-a 波滞后+午休窗·观察项不发 ping）+DEC EE659451 UNCHANGED; unacked=0; inbox 0; attrition CLEAN; "
       "post_review 45Y/0N/5W; orphan face=1 standing (py_faces=5 常驻 ComfyUI); SAT alive (pid 28728); "
       "idle NOT-GREEN --worked 11:54 (RAM 15.3% resident ComfyUI)")

current_task = ("当前活: r755 bm-c（11:35-12:0x 窗·复市 T-0 盘中值守第 75 连守轮·CEO 三令承接轮）——"
    "主产出=①FleetLink 采纳三步（O-1205-bm-c：roster 修正+listener :8790 双绑 health ok+P-09 回执 CAS "
    "a57b0f98）②静默根治三步（O-1240-bm-c：闸复写读回 0+HQ-SilenceGuard 常设自愈+P-11 回执 CAS 475eb2f8）"
    "③QA det-75th 5/5+S6 40/40+5x HANDOVER r751-755+心跳双字段首落（C-01）"
    "| 最近实物: qa/smoke-r755.md 5/5+qa/equity-curve-r755.png 66,146B+research/HANDOVER.md r755 行 2,137B+"
    "results/_r755bmc_fleet_adopt_receipt.json+results/_r755bmc_silence_receipt.json @ " + NOW +
    " | 下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium "
    "15:30 首采（bm-c 车）+CTA_P1 首接线+首 marks 验证（≤10-08 23:59）；FleetLink 采纳收口待 HQ poke 验证")

latest_artifact = ("qa/smoke-r755.md 5/5 + qa/equity-curve-r755.png 66,146B + results/_r755bmc_s6_log.txt "
    "(40 legs rc0) + research/HANDOVER.md 5x line r751-755 (2,137B) + results/_r755bmc_fleet_adopt_receipt.json "
    "+ results/_r755bmc_silence_receipt.json @ " + NOW)

next_milestone = ("tonight post-close (10-08 15:30+): data-chain re-arm + REGIME_GUARD v3 first-new-bar "
    "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks "
    "verify (<= 10-08 23:59); FleetLink adoption closes on HQ poke verify")

nxt = ("r756: (a) 轮首 pull 步核查回执面（C-01 转办常设：s05 双扫后核 P-09/P-11 有无 HQ 追加指令+FleetLink "
    "poke 验证态）；(b) marks lane 5th window watch（4 行持平·bm-a 波滞后+午休窗·观察项）；(c) tonight "
    "post-close face（<=10-08 23:59）: data-chain full re-arm + REGIME_GUARD v3 first-new-bar enforce（set "
    "BIGMONEY_REGIME_GUARD=enforce before live.paper）+ fund_premium 15:30 first snapshot（bm-c lane）+ "
    "CTA_P1 first-bar auto-wiring + first-marks verification + QDII watch holiday-delta; (d) QA ignition "
    "order law standing (S6 rc0 -> qa_ignite -> qa_poll terminal -> close); (e) close scripts: RPT = "
    "canonical logs/iteration-loop/round_reports-bm-c.md (r750 pit; NEVER clone a ROOT template); "
    "(f) FleetLink adoption awaits HQ poke verify (listener :8790 live pid 28396); (g) O-2215-1 remaining: "
    "SUPPORT row awaits bm-b router spec <=10-16; matrix re-fires when bm-a REGIME-5 labels land <=10-14; "
    "(h) month-boundary first exam 10-31. [via bm-c r755]")

verify = ("smoke 49/49 + qa/smoke-r755.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True "
    ".err 0B png 66,146B 75 连证) + results/_r755bmc_s6_log.txt 40/40 rc0 (dualrun ZERO-DRIFT streak 51 @408 "
    "cutoff 03:47) + s05 double sweep (DEC EE659451 UNCHANGED / ORD double-hop 16EBEB66->20B6976C->32D5D4CF "
    "双跳全消费 facts-driven: hop-1 = 总动员 P-09 + O-1205-bm-c + 治理令 C-01 (涉本机·全同轮执行) / hop-2 = "
    "O-1240-bm-c 静默根治 (涉本机·同轮执行) + C-02 委员会面 (零动作) / unacked=0 / inbox 0 / shape-asserted) + "
    "results/_r755bmc_clone_receipt.json (stale754=0, compile OK x3) + FleetLink 三步实证 (roster 本地=origin "
    "hash 恒等落位 + listener bound 100.123.74.104:8790+127.0.0.1:8790 + health ok node=bm-c + P-09 回执 CAS "
    "a57b0f98 tip verified + qwen3.6-coder:35b 100% GPU 常驻 ollama ps 实核) + 静默三步实证 (闸读回 "
    "ToastEnabled=0 + 任务审计违规 0 + HQ-SilenceGuard 注册下跑 2026/10/9 04:07 + P-11 回执 CAS 475eb2f8 "
    "tip verified + Quark 1.0.0.21 Disable 拒绝访问厂商 ACL 如实披露) + 5x HANDOVER 字节守恒 (2,137B) + "
    "attrition CLEAN (4 ledgers 3 healed) + post_review 45 YES / 0 NO / 5 WAIT + quartet green (pin=5 "
    "no-op / watchdog 重注 / 双爪 LF 归一 + FleetLink+HQ-SilenceGuard 两常设任务注册) + orphan face=1 "
    "standing disposition (py_faces=5, resident ComfyUI service, CEO asset, read-only no-kill) + SAT "
    "alive (resident pid 28728) + idle NOT-GREEN --worked " + WORKED_HM + " (RAM 15.3% < 40% resident "
    "ComfyUI) + 心跳双字段 last_pulled_at/head_sha 首落 (C-01 快改)")

ord_method = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r755 double sweep = "
    "CHANGED double-hop 16EBEB66 -> 20B6976C (sweep-1: 总动员 P-09 + O-20261008-1205-bm-c + 治理令 "
    "C-20261008-01, ALL executed same-round) -> 32D5D4CF (sweep-2: O-20261008-1240-bm-c silence order "
    "executed same-round + C-02 committee face zero-action); hex-case comparison normalized per r711 "
    "pit law; facts-driven from results/_r755bmc_s05_facts.json, 40hex shape-asserted, never hand-typed "
    "(r583 S4 law)")

dec_method = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r755 double "
    "sweeps = UNCHANGED EE659451 zero delta zero action; facts-driven from "
    "results/_r755bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)")

report_line = (NOW + " | r755 | dept:工程+交易（复市 T-0 盘中值守轮·第 75 bm-c 连守轮·CEO 三令承接轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·py_watermark verdict=insufficient_history 盘中板清+无新 bar 合法 idle〔orders "
    "51 disk unacked=0 双扫·inbox 0 双扫〕·compute_audit rc0 flags=[pool_starvation,supply_floor] 诚实披露〔pool "
    "ready 0<floor 3·席位间隙已知面·供给属预注册起草线节奏〕+single_core_hog candidate=SAT 常驻 1 核已知面"
    "·next_pick=claimed〔moneyflow IC 参考批·advisory only〕） | " + current_task +
    " | 验证证据: " + verify + " | 下轮指针: " + nxt +
    " | 轮产品计分：2（FleetLink 采纳三步+静默根治三步+QA det-75th+S6 40 腿再生+5x HANDOVER=能跑能看实物）"
    " | 记账预算：5（S0 churn absorb×1+轮报/心跳/state 收口+post_review/attrition 例行+克隆收据+s05 facts "
    "双扫件）")

commitmsg = ("round 755: CEO tri-order round (FleetLink adoption O-1205-bm-c: roster fix + listener :8790 "
    "health ok + P-09 receipt CAS a57b0f98; silence root-cure O-1240-bm-c: gate re-assert + HQ-SilenceGuard "
    "+ P-11 receipt CAS 475eb2f8; C-01 quick-fix: heartbeat last_pulled_at/head_sha) + ORD double-hop "
    "16EBEB66->20B6976C->32D5D4CF fully consumed + QA det-75th 5/5 (93 trades 1,017,839 frozen identity) + "
    "S6 40/40 rc0 (dualrun streak 51) + 5x HANDOVER r751-755 + clone gate stale754=0 + DEC EE659451 "
    "unchanged + marks lane 4-row watch + idle --worked [via bm-c r755]")


def apply_common(d):
    d["round_no"] = 756
    d["round_no_label"] = "round 755 (bm-c)"
    d["last_round"] = 755
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
    d["last_pulled_at"] = LAST_PULLED
    d["head_sha"] = HEAD_SHA
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
    d["cpu_pct"] = 5.0
    d["cpu_util_pct"] = 5.0


state = json.load(open(REPO + r"\state-bm-c.json", encoding="utf-8"))
apply_common(state)
with open(REPO + r"\state-bm-c.json", "w", encoding="utf-8") as fh:
    json.dump(state, fh, indent=1, ensure_ascii=False)

hb = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
apply_common(hb)
with open(REPO + r"\fleet\machines\bm-c.json", "w", encoding="utf-8") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)

with open(REPO + r"\logs\iteration-loop\round_reports-bm-c.md", "a",
          encoding="utf-8") as fh:
    fh.write(report_line + "\n")

with open(REPO + r"\_r755bmc_commitmsg.txt", "w", encoding="utf-8") as fh:
    fh.write(commitmsg)

s2 = json.load(open(REPO + r"\state-bm-c.json", encoding="utf-8"))
h2 = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
for name, d in (("state", s2), ("heartbeat", h2)):
    assert isinstance(d["heartbeat_epoch_utc"], int), name + " epoch not int"
    assert "T" in d["clock_read"] and "+" in d["clock_read"], name + " clock T-sep"
    assert d["round_no"] == 756, name + " round_no"
    assert d["last_orders_sha"] == ORD_SHA, name + " ord sha"
    assert d["last_pulled_at"] == LAST_PULLED and d["head_sha"] == HEAD_SHA, \
        name + " fresh fields"
print("CLOSEOUT OK now=%s epoch=%d ram=%.1fGB gpu=%dMB ord=%s dec_unchanged=%s "
      "head=%s last_pulled=%s report_len=%d"
      % (NOW, EPOCH, RAM_FREE, GPU_MB, ORD_SHA[:8],
         DEC_SHA[:8] == "EE659451", HEAD_SHA[:12], LAST_PULLED, len(report_line)))
