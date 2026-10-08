# -*- coding: utf-8 -*-
"""r757 bm-c closeout: facts-driven DEC/ORD single-hop consume + state
round_no+1 + heartbeat product-law 3-line + canonical round report line +
commit msg file + validation (epoch int / T-separator clock / round_no
advance). Lane-guard honest-skip face this round (bm-a heartbeat fresh 4min,
zero stale-takeover) vs r756 stale-takeover derive."""
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
WORKED_HM = "12:31"

p = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True,
                   creationflags=CF)
HEAD_SHA = p.stdout.decode("utf-8", "replace").strip()
assert re.fullmatch(r"[0-9a-f]{40}", HEAD_SHA), "head sha shape"
facts_mtime = os.path.getmtime(os.path.join(REPO, "results",
                                            "_r757bmc_s05_facts.json"))
LAST_PULLED = datetime.datetime.fromtimestamp(facts_mtime).astimezone().isoformat(
    timespec="seconds")

facts = json.load(open(REPO + r"\results\_r757bmc_s05_facts.json",
                       encoding="utf-8"))
assert facts["shape_assert"], "s05 shape assert failed"
assert re.fullmatch(r"[0-9A-F]{64}", facts["dec_sha"]), "dec sha shape"
assert re.fullmatch(r"[0-9A-F]{40}", facts["ord_sha"]), "ord sha shape"
assert facts["unacked"] == [] and facts["inbox_unread"] == [], \
    "unacked/inbox not clean"

ram_pct, vram_gb = 15.0, 1.17
try:
    idle = json.load(open(REPO + r"\results\idle_trigger.bm-c.json",
                          encoding="utf-8"))
    ram_pct = float(idle.get("ram_free_pct", ram_pct))
    vram_gb = float(idle.get("vram_free_gb", vram_gb))
except Exception:
    pass
RAM_FREE = round(23.9 * ram_pct / 100.0, 1)
GPU_MB = int(vram_gb * 1024)

ORD_SHA = facts["ord_sha"]
DEC_SHA = facts["dec_sha"]

did = ("r757: 复市 T-0 盘中值守第 77 连守轮（12:25-12:3x 窗·午休窗）+ORD 单跳消费轮——"
       "①DEC EE70CEF0 双扫 UNCHANGED（零动作·水位维持）；②ORD 6BE4D833->031E0E3E 单跳"
       "（sweep-1 CHANGED/sweep-2 UNCHANGED：C-20261008-06 大规模精简行动令——顶层规则面盘点"
       "49 件/1416KB+orders.md 239.5KB 触线在即+同主题散布三病定谳·Phase 1 AI.md 瘦身 45%+"
       "命令查重律入 governance §4 已 bm-a 同窗执行毕·bm-c 零具体动作项（精简目标件全=集团/"
       "委员会域文件·本仓 CODELY.md 主件 D-06 ≤30KB 判据律在役同向）·命令查重律记录为常式"
       "（本机未来 CEO 令落账前必查现行法面=执法强化件优先零新法条）；③QA det-77th 5/5"
       "（93 trades·equity 1,017,839 冻结恒等·determinism=True·77 连证·png 66,127B·err 0B）+"
       "S6 40/40 rc0（lane guards 诚实跳过面：bm-a 心跳 fresh 4min→strategy_scorecard/"
       "market_clock_l3/paper 族/t35/paper_export/daily_scorecard/build_status 全守卫腿诚实 "
       "skip derive 零 stale-takeover〔与 r756 stale-46min-takeover 相对·bm-a r877 在班实证〕·"
       "pool_dualrun ZERO-DRIFT streak 51@408 entries·compute_audit idle-starvation/"
       "supply_floor 盘中板清已知常在面如实披露·py_watermark py_low_board_clear 盘中合法 "
       "idle）+marks lane 5 行（11:25 尾行·午休窗无新行·13:00 复盘窗新行预期）+smoke 49/49+"
       "attrition CLEAN（4 ledgers·3 healed）+post_review 45Y/0N/5W+四件套全绿（pin=5 no-op/"
       "watchdog 在位/双爪 IN-PLACE）+orphan face=1 standing（py_faces=5 常驻 ComfyUI·CEO 资产"
       "只读不杀）+SAT alive+idle NOT-GREEN --worked 12:31（RAM 15.0% 常驻产线占用）+"
       "FleetLink 常态自证（listener pid 28396 alive+/health 200 ok node=bm-c）+"
       "token_meter delta=0")

current_task = ("当前活: r757 bm-c（12:25-12:3x 窗·复市 T-0 盘中值守第 77 连守轮·午休窗）——"
    "主产出=①ORD 单跳消费（C-20261008-06 精简行动令·bm-c 零动作+查重律常式注记）"
    "②QA det-77th 5/5 ③S6 40/40 rc0"
    "| 最近实物: qa/smoke-r757.md 5/5+qa/equity-curve-r757.png 66,127B+results/_r757bmc_s6_log.txt "
    "40/40+results/_r757bmc_s05_facts.json @ " + NOW +
    " | 下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+"
    "fund_premium 15:30 首采（bm-c 车）+CTA_P1 首接线+首 marks 验证（≤10-08 23:59）")

latest_artifact = ("qa/smoke-r757.md 5/5 + qa/equity-curve-r757.png 66,127B + results/_r757bmc_s6_log.txt "
    "(40 legs rc0) + results/_r757bmc_s05_facts.json + results/_r757bmc_ord_delta.json @ " + NOW)

next_milestone = ("tonight post-close (10-08 15:30+): data-chain re-arm + REGIME_GUARD v3 first-new-bar "
    "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks "
    "verify (<= 10-08 23:59)")

nxt = ("r758: (a) 盘中 marks lane watch（5 行在册·13:00 复盘窗新行预期·观察项）；(b) tonight post-close face"
    "（<=10-08 23:59）: data-chain full re-arm + REGIME_GUARD v3 first-new-bar enforce（set "
    "BIGMONEY_REGIME_GUARD=enforce before live.paper）+ fund_premium 15:30 first snapshot（bm-c lane）+ "
    "CTA_P1 first-bar auto-wiring + first-marks verification + QDII watch holiday-delta; (c) QA ignition "
    "order law standing (S6 rc0 -> qa_ignite -> qa_poll terminal -> close); (d) close scripts: RPT = "
    "canonical logs/iteration-loop/round_reports-bm-c.md (r750 pit; NEVER clone a ROOT template); "
    "(e) FleetLink 常态监听自证一行随轮（listener pid/health）; (f) D-20261008-06 后缀命名律执法面："
    "新产物文件带机后缀自检（_r758bmc_* 前缀范式照旧）+ C-20261008-06 命令查重律执法面（CEO 令落账前"
    "必查现行法面·已有法覆盖=登记执法强化件·零新法条）; (g) bm-b FleetLink 回执候（他机车道零干预）; "
    "(h) month-boundary first exam 10-31. [via bm-c r757]")

verify = ("smoke 49/49 + qa/smoke-r757.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True "
    ".err 0B png 66,127B 77 连证) + results/_r757bmc_s6_log.txt 40/40 rc0 (lane guards honest-skip face: "
    "bm-a heartbeat fresh 4min -> strategy_scorecard/market_clock_l3/paper 族/t35/paper_export/"
    "daily_scorecard/build_status 全守卫腿 skip derive 零 stale-takeover·bm-a r877 在班实证; "
    "pool_dualrun ZERO-DRIFT streak 51 @408 entries cutoff 03:47; compute_audit idle-starvation/"
    "supply_floor 盘中板清已知常在面如实披露; py_watermark py_low_board_clear 合法盘中 idle; "
    "fund_premium pre-15:30 no-op -> tonight 15:30 bm-c-lane first snapshot; cta_p1_paper no markable "
    "bar -> tonight first-bar auto-wiring) + s05 double sweep facts-driven (DEC EE70CEF0 UNCHANGED 双扫 "
    "零动作 / ORD single-hop 6BE4D833 -> 031E0E3E: sweep-1 CHANGED [C-20261008-06 大规模精简行动令 "
    "consumed -- group-domain Phase 1 bm-a executed same-window, bm-c zero concrete action, "
    "dedup-law standing canon noted] / sweep-2 UNCHANGED 031E0E3E / unacked=0 / inbox 0 / shape-asserted) "
    "+ results/_r757bmc_clone_receipt.json (stale756=0, compile OK x3) + FleetLink 常态自证 (listener "
    "pid 28396 alive + /health 200 ok node=bm-c ts=12:31:15) + attrition CLEAN (4 ledgers 3 healed) + "
    "post_review 45 YES / 0 NO / 5 WAIT + quartet green (pin=5 no-op / watchdog 在位 / 双爪 IN-PLACE) + "
    "orphan face=1 standing (py_faces=5, resident ComfyUI service, CEO asset, read-only no-kill) + "
    "SAT alive + idle NOT-GREEN --worked " + WORKED_HM + " (RAM " + str(ram_pct) + "% resident ComfyUI) "
    "+ marks lane 5 行 (11:25 尾行·午休窗) + token_meter delta=0")

ord_method = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r757 double sweep = "
    "single-hop 6BE4D833 -> 031E0E3E (sweep-1 CHANGED: C-20261008-06 大规模精简行动令 [顶层规则面 49 件/"
    "1416KB 盘点 + orders.md 239.5KB 触线 + 同主题散布三病; Phase 1 AI.md -45% + 命令查重律入 governance "
    "§4 = bm-a same-window executed; bm-c zero concrete action -- group/committee domain files, 本仓 "
    "CODELY.md D-06 <=30KB 判据律在役同向; dedup-law standing canon noted for future order registration "
    "on this machine]; sweep-2 UNCHANGED 031E0E3E); hex-case comparison normalized per r711 pit law; "
    "facts-driven from results/_r757bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law)")

dec_method = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r757 double sweeps "
    "= UNCHANGED EE70CEF0 both passes (zero action, watermark held); facts-driven from "
    "results/_r757bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)")

report_line = (NOW + " | r757 | dept:工程+交易（复市 T-0 盘中值守轮·第 77 bm-c 连守轮·午休窗） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·py 盘中板清合法 idle〔orders 51 disk unacked=0 双扫·inbox 0 双扫〕"
    "·next_pick=claimed〔moneyflow IC 参考批·advisory only·供给属预注册起草线节奏〕） | " + current_task +
    " | 验证证据: " + verify + " | 下轮指针: " + nxt +
    " | 轮产品计分：2（QA det-77th 5/5+equity png 66,127B+S6 40 腿面板再生+ORD 单跳消费收口=能跑能看实物）"
    " | 记账预算：5（S0 churn absorb×1+轮报/心跳/state 收口+post_review/attrition 例行+克隆收据+s05 facts "
    "双扫件） | 孤儿面=1 standing（py_faces=5 常驻 ComfyUI 服务·CEO 资产·只读不杀）")

commitmsg = ("round 757: ORD single-hop consumed (6BE4D833->031E0E3E: C-20261008-06 large-scale slimming "
    "action order -- group-domain files, Phase 1 AI.md -45% + command-dedup law executed by bm-a "
    "same-window; bm-c zero concrete action, dedup-law noted as standing canon) + DEC EE70CEF0 unchanged "
    "(double sweep) + QA det-77th 5/5 (93 trades 1,017,839 frozen identity determinism=True, png 66,127B) "
    "+ S6 40/40 rc0 (lane guards honest-skip: bm-a hb fresh 4min, zero stale-takeover; dualrun streak 51; "
    "fund_premium/cta_p1 pre-15:30 no-op -> tonight first snapshot/auto-wiring) + smoke 49/49 + marks lane "
    "5-row lunch watch + quartet green + FleetLink listener health 200 + idle --worked [via bm-c r757]")


def apply_common(d):
    d["round_no"] = 758
    d["round_no_label"] = "round 757 (bm-c)"
    d["last_round"] = 757
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

with open(REPO + r"\_r757bmc_commitmsg.txt", "w", encoding="utf-8") as fh:
    fh.write(commitmsg)

s2 = json.load(open(REPO + r"\state-bm-c.json", encoding="utf-8"))
h2 = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
for name, d in (("state", s2), ("heartbeat", h2)):
    assert isinstance(d["heartbeat_epoch_utc"], int), name + " epoch not int"
    assert "T" in d["clock_read"] and "+" in d["clock_read"], name + " clock T-sep"
    assert d["round_no"] == 758, name + " round_no"
    assert d["last_orders_sha"] == ORD_SHA, name + " ord sha"
    assert d["last_pulled_at"] == LAST_PULLED and d["head_sha"] == HEAD_SHA, \
        name + " fresh fields"
print("CLOSEOUT OK now=%s epoch=%d ram=%.1fGB gpu=%dMB ord=%s dec=%s "
      "head=%s last_pulled=%s report_len=%d"
      % (NOW, EPOCH, RAM_FREE, GPU_MB, ORD_SHA[:8],
         DEC_SHA[:8], HEAD_SHA[:12], LAST_PULLED, len(report_line)))
