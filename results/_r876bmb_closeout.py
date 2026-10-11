#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r876 bm-b closeout: round report line + state.json + heartbeat (single
writer per file, S5/S7 law). ASCII-only code (PS5.1 GBK law r829)."""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW_ISO = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
NOW_EPOCH = int(time.time())

R876_LINE = (
    "2026-10-11T" + time.strftime("%H:%M:%S") + "+08:00 | r876 bm-b | "
    "dept:研究+策略 joint（E15 leg-2 supply-floor chain leg 收口：**E15_EMOTION_REEVAL_P1 "
    "prereg FROZEN + runner + pool entry ready = supply floor 0->1**〔research/E15_EMOTION_REEVAL_P1.md @265d65754 "
    "跑前 commit 冻结先于任何 run·R99；banned_direction_gate ADMIT rc0 实跑；重估 derive 批=档存重估新程序非翻案 REEVAL18 谱系——4 钉死员 "
    "W2-23057/W3-23027/W3-27009/W3-46133 在 FDR4D 改革判线〔批内 BH FDR m=4 q=REFORM_Q_LEVEL+四维合成 g2_reform_fdr4d+D6 撞线 "
    "tl2._d6_admit_core·r271 禁手抄判线律全 import〕下重估；**零候选曲线重模拟**=判决分片件已携 legL_daily_returns n=1631〔r876 探针首证·4 员 "
    "shard 行实测〕→四维材料=冻结件 verbatim 携带+日收益纯派生〔ann/ceiling vs 五员 EW/regime_min/batch_dsr n_trials=4〕+注册六员 D6 对照 "
    "6 次轻重放〔reeval18 _registered_window_rets 同律〕；零 RNG 零种子零账本零 attrition；出场轴=①策略自有出场冻结携带〕；runner "
    "scripts/e15_emotion_reeval.py〔selftest 10/10 hermetic：ann/regime/BH m=4/缺维拒收/D6 clone 拒收/provenance 覆盖/成员钉死/cutoff_meta "
    "8 面〕；池 entry E15-EMOTION-REEVAL-P1-RUN ready〔lane_owner=null 任何合法机可烧·est 60-120s 单 worker BelowNormal·G 门七 "
    "件 fail-closed：roster/frozenfiles/shard/legidx/panel/REPRO/REFORM〕+F-04 MSG-20261011-1108-bmb-e15-freeze 防撞建声明同窗。"
    "Chain: S0 rider-commit daemon faces 后 pull clean（HEAD 8df621d3a→265d65754）；orders 67 in-dir 全 acked 零差集〔心跳 ack 192 "
    "含历史件〕；D-19 双水位零 delta〔dec caca0c6e/ord f90233c7 raw-blob sha 恒等·_r686bmb_d19_check.py〕；smoke 49/49；孤儿面=0〔py_faces=16 "
    "alive〕；satengine 活〔heartbeat 33s·idle·queue 0〕；水位红牌 red=false；S6 37 面全绿：pool_dualrun ZERO-DRIFT streak 31〔422 entries "
    "含新 E15 entry〕·compute_audit flags idle_with_work+supply_floor〔ready=1<3·E15 腿已入供给面·family streak 3666min=下两腿目录顺位待起草〕"
    "·py_watermark py_low_with_work_cands〔pool_ready=[E15-EMOTION-REEVAL-P1-RUN] 合法=池批待 autofill 点火〕·**alloc_paper rc=2 如实上报**"
    "〔data/daily/510880.csv 缺=T-184 删除事故受害件·bm-a transfer 票在案·deadline 10-12 15:30 守候面非新故障〕·thermo/dualarm/scorecard/"
    "clock_call〔ORANGE_COOL cap50%〕/daily_report/ceo_live_usage/daily_scorecard/build_status/token_meter 全 rc0·周日无新 bar→live.paper/"
    "t35/t24 paper 族 lawful skip·bm-b lanes no-op fresh；T-184 分支 ls-remote 未上 origin=receiver watch 续〔同 deadline〕。"
    "验证证据：commit 265d65754〔8 files 869 insertions〕+results/runnable_pool.json parse OK 422 entries E15 entry ready+"
    "selftest 10/10 rc0+banned_direction_gate ADMIT rc0+attrition guard scan CLEAN。下轮指针：r877=E15 烧录面池认领观察〔autofill 点火→burn→§7/"
    "§8 回填+digest+捕获律收口〕+supply-floor 后续腿〔目录第一梯队顺位起草 toward floor>=3 by 10-13〕+T-184 receiver watch。"
    "孤儿面=0；本地未达 origin commit 数=收口 push 后自证。"
)

DID = ("r876 E15 leg-2 (supply-floor chain leg-3, catalog #18): prereg E15_EMOTION_REEVAL_P1.md "
      "FROZEN @265d65754 (banned_direction_gate ADMIT rc0; reeval derive face: 4 pinned near-miss members "
      "re-adjudicated under FDR4D reform line; zero candidate-curve re-simulation -- frozen judge shards "
      "carry legL_daily_returns n=1631 first-proof; carried+derived four-dim materials, batch-internal BH "
      "FDR m=4 + g2_reform_fdr4d composite + D6 tl2._d6_admit_core; exit-axis 1-frozen-own; zero RNG/ledger/"
      "attrition) + runner scripts/e15_emotion_reeval.py (selftest 10/10 hermetic) + pool entry "
      "E15-EMOTION-REEVAL-P1-RUN ready (supply floor 0->1) + F-04 MSG-20261011-1108. Chain: S0 pull clean; "
      "orders 67/67 acked; D-19 dual watermark zero-delta; smoke 49/49; orphan face 0 (py_faces=16 alive); "
      "S6 37 faces rc0 (pool_dualrun ZERO-DRIFT streak 31, compute_audit flags idle_with_work/supply_floor "
      "ready=1<3 chain supplying, py_watermark py_low_with_work_cands lawful [pool batch ready], "
      "alloc_paper rc=2 honest [510880.csv missing = T-184 transfer dep, deadline 10-12 15:30], no new bar "
      "Sunday -> paper family lawful skip, bm-b lanes no-op fresh, thermo/dualarm/scorecard/clock_call/"
      "daily_report/ceo_live_usage rc0); T-184 branch not yet on origin (receiver watch).")

NEXT = ("r877: E15 burn-face pool claim watch (autofill ignition -> burn -> prereg sec.7/8 backfill + "
        "digest + capture-law closeout step) -> supply-floor next legs (catalog first-tier remaining "
        "items toward floor >=3 by <=2026-10-13; queue_head_collision_probe + queue_seed_gate before "
        "claim) -> T-184 transfer receiver leg watch (after bm-a pushes origin/transfer/t184-510880: "
        "git checkout origin/transfer/t184-510880 -- data/daily/510880.csv + git restore --staged R90 "
        "pit law + manifest Verify; deadline 2026-10-12 15:30) -> moneyflow IC panel watch "
        "(source-blocked self-heal face) -> W210/M9 chain watch (bm-a face)")

ARTIFACT = ("r876: research/E15_EMOTION_REEVAL_P1.md FROZEN + scripts/e15_emotion_reeval.py (selftest "
            "10/10) + pool entry E15-EMOTION-REEVAL-P1-RUN ready + MSG-20261011-1108-bmb-e15-freeze")

VERDICT = ("GREEN: r876 E15 leg-2 landed (prereg FROZEN + runner selftest 10/10 + pool entry ready = "
           "supply floor 0->1; smoke 49/49; orders/D-19 zero-delta; S6 37 rc0 with alloc_paper rc=2 "
           "honest T-184 dep; T-184 branch not on origin = receiver watch; compute_audit supply_floor "
           "flag = chain supplying toward floor 3)")

# ------------------------------------------------------------- round report
rr_path = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with open(rr_path, "a", encoding="utf-8") as f:
    f.write(R876_LINE + "\n")
print("round report line appended")

# ------------------------------------------------------------------ state.json
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round"] = 876
st["round_no"] = 877
st["round_no_label"] = "r876"
st["task"] = NEXT
st["next"] = NEXT
st["did"] = DID
st["last_action"] = DID
st["last_action_at"] = NOW_ISO
st["last_round_at"] = NOW_ISO
st["last_round_ts"] = NOW_ISO
st["last_seen"] = NOW_ISO
st["ts"] = NOW_ISO
st["updated"] = NOW_ISO
st["updated_at"] = NOW_ISO
st["clock_read"] = NOW_ISO
st["now_active"] = "r876 closeout: E15 prereg FROZEN + runner + pool entry ready (supply floor 0->1); burn via pool next"
st["latest_artifact"] = ARTIFACT
st["verdict"] = VERDICT
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["orphan_face_note"] = "r876 round probe: py_faces=16 alive, orphans=0"
st["last_decisions_read_at"] = NOW_ISO
st["last_orders_read_at"] = NOW_ISO
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1, sort_keys=True)
print("state.json updated (round 876 / round_no 877)")

# ------------------------------------------------------------- heartbeat bm-b
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["round"] = 876
hb["round_no"] = 877
hb["current_task"] = NEXT
hb["task"] = NEXT
hb["next"] = NEXT
hb["did"] = DID
hb["last_action"] = DID
hb["last_action_at"] = NOW_ISO
hb["last_round_at"] = NOW_ISO
hb["last_seen"] = NOW_ISO
hb["ts"] = NOW_ISO
hb["updated"] = NOW_ISO
hb["updated_at"] = NOW_ISO
hb["clock_read"] = NOW_ISO
hb["heartbeat_epoch_utc"] = NOW_EPOCH
hb["now_active"] = st["now_active"]
hb["latest_artifact"] = ARTIFACT
hb["verdict"] = VERDICT
hb["next_milestone"] = ("E15 burn + sec.7/8 backfill by <=2026-10-12; supply floor >=3 ready by "
                        "<=2026-10-13 (E15 = leg 1 of 3); T-184 510880 restore before 2026-10-12 "
                        "15:30 next bar (bm-a push pending)")
hb["orphan_face"] = 0
hb["orphan_faces"] = 0
hb["orphan_face_note"] = st["orphan_face_note"]
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
import psutil  # noqa: E402
vm = psutil.virtual_memory()
hb["free_ram_gb"] = round(vm.available / 1024 ** 3, 1)
hb["ram_free_gb"] = round(vm.available / 1024 ** 3, 1)
hb["ram_free_pct"] = round(vm.available / vm.total * 100, 1)
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1, sort_keys=True)

# self-proof: epoch must be JSON int (R170/R178 law)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be ISO8601 T-separated"
print("heartbeat updated + self-proof PASS (epoch int, clock T-separated)")
print("orders_ack unchanged:", len(chk.get("orders_ack", [])))
