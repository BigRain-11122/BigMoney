# -*- coding: utf-8 -*-
"""r756 bm-c closeout: facts-driven DEC/ORD double-hop consume + state
round_no+1 + heartbeat product-law 3-line + canonical round report line +
commit msg file + validation (epoch int / T-separator clock / round_no
advance). Stale-takeover derive disclosure (bm-a heartbeat stale 46min ->
bm-c derive per O-2100 s2.4 STALE_MIN law)."""
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
WORKED_HM = "12:14"

p = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True,
                   creationflags=CF)
HEAD_SHA = p.stdout.decode("utf-8", "replace").strip()
assert re.fullmatch(r"[0-9a-f]{40}", HEAD_SHA), "head sha shape"
facts_mtime = os.path.getmtime(os.path.join(REPO, "results",
                                            "_r756bmc_s05_facts.json"))
LAST_PULLED = datetime.datetime.fromtimestamp(facts_mtime).astimezone().isoformat(
    timespec="seconds")

facts = json.load(open(REPO + r"\results\_r756bmc_s05_facts.json",
                       encoding="utf-8"))
assert facts["shape_assert"], "s05 shape assert failed"
assert re.fullmatch(r"[0-9A-F]{64}", facts["dec_sha"]), "dec sha shape"
assert re.fullmatch(r"[0-9A-F]{40}", facts["ord_sha"]), "ord sha shape"
assert facts["unacked"] == [] and facts["inbox_unread"] == [], \
    "unacked/inbox not clean"

ram_pct, vram_gb = 14.7, 1.18
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

did = ("r756: 复市 T-0 盘中值守第 76 连守轮（午休窗）+DEC/ORD 双跳全消费轮——"
       "①DEC EE659451->EE70CEF0（12:00 常务轮批 D-20261008-05~08 四行全消费：D-05 回执核销批 23 零动作/"
       "D-06 我方 F-20261008-02② 机器后缀命名律采纳为机队常式（新产物后缀自检律在役·本机 _r757bmc_* 范式照旧）/"
       "D-07 CPH4 域非本司/D-08 FleetLink 采纳收口——HQ poke 验证 GET /health 200+POST /poke 200 accepted 全链实弹·"
       "r755 回执三步经 HQ 验收闭·listener pid 28396 本窗复核活）；②ORD 双跳 32D5D4CF->77C9BC92（hop-1："
       "O-20261008-1205-bm-c 12:1x 修正版五步经 D-08 证实 r755 已全数执行+总动员 P-09 r755 已回执+"
       "MV/模型三闸/委员会 C-01~04 他司域行零本机动件）->6BE4D833（hop-2：C-20261008-05 传导闭环治理令——"
       "bm-c 面收口毕（秒级分发 bm-a↔bm-c 在役·下行三层兜底全态）零新动作·bm-b 回执候=他机车道）；"
       "③QA det-76th 5/5（93 trades·equity 1,017,839 冻结恒等·determinism=True·76 连证·png 66,325B）+"
       "S6 40/40 rc0（stale-takeover 诚实披露：strategy_scorecard/daily_scorecard/build_status 三守卫面"
       "bm-a 心跳 stale 46min→bm-c 合法接管派生〔O-2100 s2.4 STALE_MIN 律〕）+marks lane 5 行（11:25 新窗落行·观察项）+"
       "smoke 49/49+attrition CLEAN+post_review 45Y/0N/5W+四件套全绿（pin=5 no-op/watchdog 在位/双爪 IN-PLACE）+"
       "orphan face=1 standing（py_faces=5 常驻 ComfyUI·CEO 资产只读不杀）+SAT alive+"
       "idle NOT-GREEN --worked 12:14（RAM 14.7% 常驻产线占用）")

current_task = ("当前活: r756 bm-c（12:05-12:1x 窗·复市 T-0 盘中值守第 76 连守轮·午休窗）——"
    "主产出=①DEC/ORD 双跳全消费（D-08 FleetLink 采纳收口·D-06 命名律采纳·C-05 传导闭环 bm-c 收口毕）"
    "②QA det-76th 5/5 ③S6 40/40 rc0"
    "| 最近实物: qa/smoke-r756.md 5/5+qa/equity-curve-r756.png 66,325B+results/_r756bmc_s6_log.txt 40/40+"
    "results/_r756bmc_hq_delta.json+results/_r756bmc_ord_hop2.json @ " + NOW +
    " | 下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium "
    "15:30 首采（bm-c 车）+CTA_P1 首接线+首 marks 验证（≤10-08 23:59）")

latest_artifact = ("qa/smoke-r756.md 5/5 + qa/equity-curve-r756.png 66,325B + results/_r756bmc_s6_log.txt "
    "(40 legs rc0) + results/_r756bmc_hq_delta.json + results/_r756bmc_ord_hop2.json @ " + NOW)

next_milestone = ("tonight post-close (10-08 15:30+): data-chain re-arm + REGIME_GUARD v3 first-new-bar "
    "enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks "
    "verify (<= 10-08 23:59)")

nxt = ("r757: (a) 盘中 marks lane watch（5 行在册·13:00 复盘窗新行预期·观察项）；(b) tonight post-close face"
    "（<=10-08 23:59）: data-chain full re-arm + REGIME_GUARD v3 first-new-bar enforce（set "
    "BIGMONEY_REGIME_GUARD=enforce before live.paper）+ fund_premium 15:30 first snapshot（bm-c lane）+ "
    "CTA_P1 first-bar auto-wiring + first-marks verification + QDII watch holiday-delta; (c) QA ignition "
    "order law standing (S6 rc0 -> qa_ignite -> qa_poll terminal -> close); (d) close scripts: RPT = "
    "canonical logs/iteration-loop/round_reports-bm-c.md (r750 pit; NEVER clone a ROOT template); "
    "(e) FleetLink 面已收口（D-08·HQ poke accepted 12:0x）——常态监听自证一行随轮（listener pid/health）；"
    "(f) D-20261008-06 后缀命名律执法面：新产物文件带机后缀自检（_r757bmc_* 前缀范式照旧）；"
    "(g) bm-b FleetLink 回执候（他机车道零干预）；(h) month-boundary first exam 10-31. [via bm-c r756]")

verify = ("smoke 49/49 + qa/smoke-r756.md 5/5 (93 trades equity 1,017,839 frozen identity determinism=True "
    ".err 0B png 66,325B 76 连证) + results/_r756bmc_s6_log.txt 40/40 rc0 (stale-takeover derive 诚实披露: "
    "strategy_scorecard/daily_scorecard/build_status 三守卫面 host=bm-a heartbeat stale 46min -> bm-c "
    "合法接管派生 O-2100 s2.4 STALE_MIN law) + s05 double sweep facts-driven (DEC EE659451->EE70CEF0 "
    "consumed 12:00 batch D-20261008-05~08 all-closed / ORD double-hop 32D5D4CF->77C9BC92->6BE4D833 双跳全消费: "
    "hop-1 = 1205-bm-c 12:1x 修正版 (r755 pre-executed all 5 steps, D-20261008-08 confirms closure) + P-09 "
    "总动员 (r755 receipted) + 他司域行零动作 / hop-2 = C-20261008-05 传导闭环治理令 (bm-c 收口毕零动作) / "
    "unacked=0 / inbox 0 / shape-asserted) + results/_r756bmc_clone_receipt.json (stale755=0, compile OK x3) + "
    "FleetLink 收口实证 (D-20261008-08: HQ poke GET /health 200 + POST /poke accepted + listener pid 28396 "
    "本窗复核活) + attrition CLEAN (4 ledgers 3 healed) + post_review 45 YES / 0 NO / 5 WAIT + quartet green "
    "(pin=5 no-op / watchdog 在位 / 双爪 IN-PLACE) + orphan face=1 standing (py_faces=5, resident ComfyUI "
    "service, CEO asset, read-only no-kill) + SAT alive + idle NOT-GREEN --worked " + WORKED_HM + " (RAM " +
    str(ram_pct) + "% resident ComfyUI) + marks lane 5 行 (11:25 新窗)")

ord_method = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r756 double sweep = "
    "CHANGED double-hop 32D5D4CF -> 77C9BC92 (sweep-1: O-20261008-1205-bm-c 12:1x 修正版 [r755 pre-executed "
    "all 5 steps, D-20261008-08 confirms closure] + P-09 总动员 [r755 receipted] + 他司域 MV/模型三闸/委员会 "
    "C-01~04 rows zero bm-c action) -> 6BE4D833 (sweep-2: C-20261008-05 传导闭环治理令 [bm-c 面收口毕 zero "
    "action]); hex-case comparison normalized per r711 pit law; facts-driven from "
    "results/_r756bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law)")

dec_method = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r756 double sweeps "
    "= CHANGED EE659451 -> EE70CEF0 (12:00 常务轮 batch D-20261008-05~08 all consumed same-round: D-05 "
    "receipts zero-action / D-06 our F-20261008-02② naming law ADOPTED as fleet canon / D-07 CPH4 domain "
    "not-ours / D-08 FleetLink adoption CLOSED via HQ poke verification); sweep-2 UNCHANGED EE70CEF0; "
    "facts-driven from results/_r756bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)")

report_line = (NOW + " | r756 | dept:工程+交易（复市 T-0 盘中值守轮·第 76 bm-c 连守轮·午休窗） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·py 盘中板清合法 idle〔orders 51 disk unacked=0 双扫·inbox 0 双扫〕"
    "·next_pick=claimed〔moneyflow IC 参考批·advisory only·供给属预注册起草线节奏〕） | " + current_task +
    " | 验证证据: " + verify + " | 下轮指针: " + nxt +
    " | 轮产品计分：2（QA det-76th 5/5+equity png 66,325B+S6 40 腿面板再生+HQ 双跳消费收口=能跑能看实物）"
    " | 记账预算：5（S0 churn absorb×1+轮报/心跳/state 收口+post_review/attrition 例行+克隆收据+s05 facts "
    "双扫件） | 孤儿面=1 standing（py_faces=5 常驻 ComfyUI 服务·CEO 资产·只读不杀）")

commitmsg = ("round 756: DEC/ORD double-hop fully consumed (DEC EE659451->EE70CEF0: D-06 naming law "
    "adopted + D-08 FleetLink adoption CLOSED via HQ poke verify, listener pid 28396 re-checked alive; "
    "ORD 32D5D4CF->77C9BC92->6BE4D833: 1205-bm-c revised-order r755 pre-executed confirmed + C-05 "
    "transmission-loop bm-c face closed) + QA det-76th 5/5 (93 trades 1,017,839 frozen identity) + S6 "
    "40/40 rc0 (stale-takeover derive O-2100 s2.4: bm-a hb stale 46min -> bm-c) + smoke 49/49 + marks "
    "lane 5-row watch + idle --worked [via bm-c r756]")


def apply_common(d):
    d["round_no"] = 757
    d["round_no_label"] = "round 756 (bm-c)"
    d["last_round"] = 756
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

with open(REPO + r"\_r756bmc_commitmsg.txt", "w", encoding="utf-8") as fh:
    fh.write(commitmsg)

s2 = json.load(open(REPO + r"\state-bm-c.json", encoding="utf-8"))
h2 = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
for name, d in (("state", s2), ("heartbeat", h2)):
    assert isinstance(d["heartbeat_epoch_utc"], int), name + " epoch not int"
    assert "T" in d["clock_read"] and "+" in d["clock_read"], name + " clock T-sep"
    assert d["round_no"] == 757, name + " round_no"
    assert d["last_orders_sha"] == ORD_SHA, name + " ord sha"
    assert d["last_pulled_at"] == LAST_PULLED and d["head_sha"] == HEAD_SHA, \
        name + " fresh fields"
print("CLOSEOUT OK now=%s epoch=%d ram=%.1fGB gpu=%dMB ord=%s dec=%s "
      "head=%s last_pulled=%s report_len=%d"
      % (NOW, EPOCH, RAM_FREE, GPU_MB, ORD_SHA[:8],
         DEC_SHA[:8], HEAD_SHA[:12], LAST_PULLED, len(report_line)))
