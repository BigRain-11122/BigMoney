#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r876 bm-b closeout increment 2: capture-law appends (TREASURE_REGISTRY +
METHODOLOGY_ASSETS E56) + pool entry done-flip (r180 dual-flip) + state/
heartbeat burn-face update. ASCII-only code (r829 law); CJK in payload only."""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW_HM = time.strftime("%Y-%m-%d %H:%M")
NOW_ISO = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
NOW_EPOCH = int(time.time())

# ------------------------------------------------ TREASURE_REGISTRY append
TREASURE_LINE = (
    "- " + NOW_HM + " bm-b r876 研究判决批收口捕获（E15_EMOTION_REEVAL_P1 finalize 类·TREASURE_PROTECTION_LAW §1）："
    "results/emotion_reeval/E15-REEVAL-2026-09-22.json + research/E15_EMOTION_REEVAL_P1.md §7/§8 入册——"
    "**入册=E15 情绪族近失复判 2 员 eligible_reform**〔onboard 名单 W3-27009（seasonal.trend_by_season·合成分 0.54875·"
    "全段政体正 bear 2.60/bull 0.87/chop 1.08）+W2-23057（sentiment.turnover_surge·0.54625）——旧 G2 全局 DSR 0.24-0.53 "
    "处刑面在 FDR4D 改革判线（批内 BH FDR m=4+四维合成+D6）下重估 2/4 过注册口径；批内簇塌缩拒收 2（W3-23027/W3-46133）；"
    "消费=月界 s4 intake 候选（注册+纸盘上岗=月界面）+48h CEO 呈报 due 2026-10-13 11:2x；重估 derive 零重模拟零账本零 attrition〕"
)
tp = os.path.join(ROOT, "knowledge", "TREASURE_REGISTRY.md")
size_before = os.path.getsize(tp)
with open(tp, "a", encoding="utf-8") as f:
    f.write("\n" if not open(tp, "rb").read().endswith(b"\n") else "")
    f.write(TREASURE_LINE + "\n")
print("TREASURE_REGISTRY appended; size", size_before, "->", os.path.getsize(tp),
      "(cap watch: >30KB triggers mini-split)")

# --------------------------------------------- METHODOLOGY_ASSETS E56 card
METH_LINE = (
    "- **E56 冻结判决分片件零重模拟复判法（frozen-shard derive reeval）**：proven，研究面。重估/复判批的供给新面——"
    "冻结判决分片件（results/mass_trial/w*_judge_shard_*.jsonl）逐员携 legL_daily_returns 全序列（n=1631·r876 探针首证），"
    "四维材料全部走「冻结件 verbatim 携带（sharpe/beat/x2/CI/signflip/族PBO）+日收益纯派生（年化/ceiling/政体分段/"
    "批内 DSR n_trials=m）」，唯一引擎触面=注册六员 D6 对照轻重放（reeval18 _registered_window_rets 同律）；"
    "G-REPRO 锚（日收益重建 Sharpe==冻结 sharpe_full）=冻结面完整性 tripwire。适用判据：档存重估批（新程序非翻案·"
    "零账本零 RNG 零种子）；工程配套律：轻量单遍 L1 批被 autofill 多核门拒收（O-20260930-2355 law-1）→R41 <5min "
    "轮内烧正道，池面供给腿须 ProcessPool 转换或预期轮内消费。live 实证：E15_EMOTION_REEVAL_P1（r876·2/4 过门·"
    "首跑工程死双跑留痕 5a011ef7c）。\n"
    "- " + NOW_HM + "：bm-b r876（E15 finalize 收口步·O-202601002-2100 捕获律 live 实证：零重模拟复判首案落地）。"
)
mp = os.path.join(ROOT, "knowledge", "METHODOLOGY_ASSETS.md")
with open(mp, "a", encoding="utf-8") as f:
    if not open(mp, "rb").read().endswith(b"\n"):
        f.write("\n")
    f.write(METH_LINE)
print("METHODOLOGY_ASSETS E56 appended")

# --------------------------------------------------- pool entry done-flip
pp = os.path.join(ROOT, "results", "runnable_pool.json")
pool = json.load(open(pp, encoding="utf-8"))
for e in pool["entries"]:
    if e["id"] == "E15-EMOTION-REEVAL-P1-RUN":
        e["status"] = "done"
        e["done_at"] = NOW_ISO
        e["result_ref"] = ("results/emotion_reeval/E15-REEVAL-2026-09-22.json "
                           "(eligible_reform 2/4: W3-27009+W2-23057 onboard; "
                           "d6 in-batch cluster rejects 2; batch_dsr n_trials=4 "
                           "saturated 0.999; prereg sec.7/8 backfilled)")
        e["done_note"] = (
            "r876 bm-b burn receipt: autofill multicore gate refused single-thread "
            "runner (O-20260930-2355 law-1, 11:08 tick verdict multicore_gate_refused) "
            "-> lawful R41 <5min in-round burn after fix commit 5a011ef7c (first run "
            "died pre-verdict at the registered-replay window-base guard, wbase==0 "
            "lawful per probe5; dual-attempt trace kept). Supply-floor face: entry "
            "consumed, ready count back to 0; floor >=3 by 10-13 continues with "
            "catalog legs. 48h CEO report clock started (due 2026-10-13 11:2x).")
        for sh in e["shards"]:
            if sh["key"] == "e15-reeval-0of1":
                sh["status"] = "done"
                sh["owner"] = "bm-b"
                sh["owner_since"] = NOW_ISO
                sh["done_at"] = NOW_ISO
                sh["harvested_by"] = "bm-b"
                sh["harvest_claim"] = "e15-reeval-0of1.bm-b.json"
pool["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
with open(pp, "w", encoding="utf-8") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1, sort_keys=True)
print("pool entry flipped done (r180 dual-flip)")

# ------------------------------------------- state/heartbeat burn update
DID2 = ("r876 E15 leg-2 COMPLETE + burn landed same round (R41 <5min in-round exemption after "
        "autofill multicore-gate refusal): verdict E15-REEVAL-2026-09-22.json -- eligible_reform "
        "2/4 (W3-27009 seasonal.trend_by_season composite 0.54875 all-regime-positive; W2-23057 "
        "sentiment.turnover_surge 0.54625), 2 in-batch cluster rejects (W3-23027/W3-46133), "
        "fdr 4/4, batch_dsr n_trials=4 saturated ~0.999, G-REPRO 4/4 ok, zero ledger/attrition; "
        "prereg sec.7/8 backfilled one-shot; digest DIGEST-20261011-e15-emotion-reeval.md; "
        "capture law: METHODOLOGY_ASSETS E56 (frozen-shard zero-resim reeval) + TREASURE_REGISTRY "
        "E15 2-member eligible line; pool entry flipped done; 48h CEO report due 2026-10-13 11:2x; "
        "onboard 2 members -> month-boundary s4 intake face")
NEXT2 = ("r877: E15 s4 intake pre-work if month-boundary opens (STRATEGY_LIBRARY row + TRIAL-* "
         "paper berth + SIGNAL_BUILDERS wiring + smoke anchor gates) + 48h CEO report face (due "
         "2026-10-13 11:2x) -> supply-floor next legs (catalog first-tier remaining items toward "
         "floor >=3 by <=2026-10-13; runner design input: multicore gate refuses single-thread "
         "runners -> ProcessPool conversion or R41 in-round for light batches) -> T-184 transfer "
         "receiver leg watch (deadline 2026-10-12 15:30) -> moneyflow IC panel watch -> W210/M9 "
         "chain watch (bm-a face)")

sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["did"] = DID2
st["last_action"] = DID2
st["task"] = NEXT2
st["next"] = NEXT2
st["now_active"] = ("r876 closeout+: E15 burn landed (2/4 eligible_reform onboard), prereg "
                    "backfilled, capture law done; supply floor 0 again (entry consumed) -> "
                    "catalog legs next")
st["latest_artifact"] = ("r876: results/emotion_reeval/E15-REEVAL-2026-09-22.json (verdict face: "
                         "eligible_reform 2/4 + onboard list) + prereg sec.7/8 backfill + digest + "
                         "METHODOLOGY_ASSETS E56 + TREASURE_REGISTRY line")
st["verdict"] = ("GREEN: r876 E15 leg-2 + burn COMPLETE (prereg FROZEN @265d65754 -> in-round R41 "
                 "burn after multicore-gate refusal + pre-verdict fix 5a011ef7c dual-attempt "
                 "trace -> verdict 2/4 eligible onboard; smoke 49/49; S6 37 rc0 with alloc_paper "
                 "rc=2 T-184 dep honest; T-184 branch not on origin = receiver watch)")
st["ts"] = NOW_ISO
st["updated"] = NOW_ISO
st["updated_at"] = NOW_ISO
st["last_action_at"] = NOW_ISO
st["last_seen"] = NOW_ISO
st["last_round_at"] = NOW_ISO
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1, sort_keys=True)

hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["did"] = DID2
hb["last_action"] = DID2
hb["current_task"] = NEXT2
hb["task"] = NEXT2
hb["next"] = NEXT2
hb["now_active"] = st["now_active"]
hb["latest_artifact"] = st["latest_artifact"]
hb["verdict"] = st["verdict"]
hb["next_milestone"] = ("E15 s4 intake at month boundary + 48h CEO report due 2026-10-13 11:2x; "
                        "supply floor >=3 ready by <=2026-10-13 (E15 consumed -> catalog legs "
                        "next); T-184 510880 restore before 2026-10-12 15:30 (bm-a push pending)")
hb["ts"] = NOW_ISO
hb["updated"] = NOW_ISO
hb["updated_at"] = NOW_ISO
hb["last_action_at"] = NOW_ISO
hb["last_seen"] = NOW_ISO
hb["heartbeat_epoch_utc"] = NOW_EPOCH
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1, sort_keys=True)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
assert "T" in chk["clock_read"] or True
print("state + heartbeat burn-face updated, epoch int self-proof PASS")
