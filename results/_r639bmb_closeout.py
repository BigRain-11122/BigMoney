#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r639 bm-b closeout: state bump, heartbeat, round-report line, fleet MSG.

Adoption round: 23:32 lane session (r639 predecessor) hit the 25-min harness
timeout at 23:57:02 mid-round; this session (00:02 tick) adopted its verified
WIP (town.html KPI alignment PASS, pit-git append complete) and closed r639.
"""
import json
import os
import time
import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
NEW_SHA = "4167b7841a5b2b889fa8f8d27b81286faae39b340e786609998431ee6fd46d26"

# ---------- state.json ----------
sp = os.path.join(REPO, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 639
st["note"] = ("r639: ADOPTION round - 23:32 lane session (r639 predecessor) hit 25min harness timeout at 23:57 "
              "mid-round after completing its own S0 (isolated-worktree merge f95419e5c pushed 23:40 + 2-face take-new "
              "resolve + wtsync 73-file sync) and product slice (town.html org_chart v2 KPI row alignment, "
              "town_align_check 11/11 KPI-OK node rc0; pit-git +1 law entry w/ md5 reconciliation line); "
              "bookkeeping-family mtimes (state 23:18/round_reports 23:19/CODELY 23:03) all <= round end = dead-session "
              "adoption lawful (r631). This session (00:02 tick): S0 new push-race merge (local autofill 375368771 vs "
              "origin 6 commits bm-c r435+churns+bm-a r647/648) via isolated worktree r630 net-path: ZERO UU, pool face "
              "probe = runnable_pool 2-line bm-b claim-refresh only (newer-wins lawful), crash_fuse/dispatcher identical "
              "to origin; CAS push 7a941986f..758fd3eed OK; main tree reset --mixed + wtsync2 98-file targeted checkout "
              "(0 live-face skips, pathspec-from-file WITHOUT `--` per pit entry); post-merge dualrun ZERO-DRIFT "
              "streak 30 = settle proof. S0.5: orders 152/152 double-scan zero-unacked; D-19 ANOMALY: origin "
              "decisions.md now hashes 4167b784 = PRE-10-03-batch bytes (revert/rewrite of consumed batch "
              "D-20261003-01~04; r638 receipts stand) - zero new dispatch rows vs consumed set, watermark set to "
              "current consumed sha, anomaly flagged to fleet master via MSG. S1 smoke 47/47. S3: watermark green "
              "(next_pick=claimed advisory); satengine rc0 idle; trial-labor standing line = in-flight FUND trio NULLS "
              "burn (dualrun 366 entries pure-append); post_review first-batch backfill REPORT-20261004 "
              "(ok37/x7/yellow5): 7 x-rows = historical claims file-absent (T-73 s3 x3 / R252 bm-a ledger repair / "
              "T-83-S3 slice2 / T-86 s2 / T-87 REV-OSC) - deterministic derive stands, no ledger self-edit (O-2115), "
              "owner follow-up queued. S6 31 legs rc0 (Sunday golden-week honest no-ops; CEO faces regenerated: "
              "REPORT-2026-10-04, LIVE-2026-10-04 ORANGE cap50, CALL-2026-09-30 ORANGE_COOL; py_low_with_work_cands "
              "= legal in-flight trio burns + board closed + pool_ready_unclaimed 1). S7 4/4 (loop pin2, watchdog, "
              "claws x2) + attrition CLEAN + orders 152/152.")
st["last_round_at"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["last_seen"] = NOW
st["last_decisions_sha"] = NEW_SHA
st["last_decisions_at"] = NOW
st["round_no_label"] = "round 639 (bm-b)"
json.dump(st, open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# ---------- heartbeat ----------
hp = os.path.join(REPO, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["round_no"] = 639
hb["round_no_label"] = "round 639 (bm-b)"
hb["current_task"] = ("FUND trio NULLS burn watch (V434/Q309/D193 daemons live, dualrun streak30, finalize window "
                      "10-05..10-09 held on G-SEG GM ruling) + r639 adoption closeout landed (town.html org_chart v2 "
                      "KPI alignment + push-race merge 758fd3eed + REPORT/LIVE-2026-10-04 faces)")
hb["verdict"] = ("GREEN (smoke 47/47; S0 merge pushed 758fd3eed ls-remote-verified; S6 31 legs rc0; dualrun "
                 "ZERO-DRIFT streak 30; engine alive rc0 idle; orders 152/152 double-scan clean; attrition CLEAN; "
                 "D-19 decisions.md regression anomaly flagged to bm-a (sha reverted to pre-10-03 batch); "
                 "post_review 7 x-rows queued to owners; trio burns healthy)")
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["ts"] = NOW
hb["updated"] = NOW
hb["updated_at"] = NOW
try:
    import psutil
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / 1024 ** 3, 2)
    hb["idle_ram_gb"] = hb["free_ram_gb"]
    hb["ram_free_gb"] = hb["free_ram_gb"]
    hb["ram_avail_gb"] = hb["free_ram_gb"]
    hb["cpu_util_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
except Exception:
    pass
json.dump(hb, open(hp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"

# ---------- round report line ----------
rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")
entry = (
    "\n" + NOW + " | round 639 (bm-b)\n"
    "watermark verdict: 绿（red=false; next_pick=claimed advisory 照旧）\n"
    "当前活: r639 死会话收养收口（23:32 前体 25min 超时中断）——S0 push-race 合并推送 + town.html 产品件落地 + 本日 CEO 面再生成\n"
    "最近实物: town.html org_chart v2 KPI 行对齐（11/11 KPI-OK·node rc0·23:46）+ REPORT-2026-10-04.md + LIVE-2026-10-04.md（00:2x）+ 合并 758fd3eed\n"
    "下个里程碑: FUND 三族 NULLS 烧完 finalize 窗 10-05..10-09（G-SEG GM 裁定悬置）· post_review 7 ✗ 历史断件属主追办 · 窗 ≤48h\n"
    "做了什么: 收养前体已验 WIP（town 对齐+pit-git +1 律）；重做 S0（本地 autofill 375368771 vs origin 6 提交·隔离 worktree r630 净路·零 UU·池面 2 行 claim-refresh newer-wins·CAS 推送 758fd3eed·主树 reset --mixed+wtsync2 98 件定向 checkout）；S0.5 令 152/152 双扫零未回执+D-19 异常（decisions.md 回退至 4167b784=10-03 批前字节·已消费回执仍在账·水位随实况+MSG 呈 bm-a）；S1 47/47；S3 水位绿·引擎活 rc0·试用线=在飞三族烧；post_review 首批回填（✓37/✗7/🟡5，7 ✗=历史宣称断件·确定性 derive 立面·O-2115 禁自改台账·属主追办入队）；S6 31 腿 rc0（周日国庆诚实 no-op·py_low_with_work_cands=在飞烧合法态·pool_ready_unclaimed=1）；S7 4/4+attrition CLEAN\n"
    "验证证据: smoke 47/47；push 7a941986f..758fd3eed（ls-remote 复核）；dualrun ZERO-DRIFT streak 30（366 entries）；attrition scan CLEAN（4 ledgers）；wtsync2 报告 98/0；town_align_report PASS；S6 各腿 rc0 行\n"
    "下轮指针: r640 = G-SEG/VALUE finalize 前置追踪（r633 双阻塞已呈）+ post_review ✗ 属主追办确认 + town.html 小活收尾（楼名/详情 org_chart v2 全表对齐验收）\n"
    "本地未达 origin commit 数=0（push 后 ls-remote 自证）\n"
)
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(entry)

# ---------- fleet MSG: decisions.md regression anomaly ----------
msg_dir = os.path.join(REPO, "fleet", "inbox")
msg_path = os.path.join(msg_dir, "MSG-20261004-0030-bmb.md")
with open(msg_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(
        "# MSG-20261004-0030 bm-b -> bm-a（机队总控）\n\n"
        "主题：集团仓 docs/decisions.md 疑似回退异常（D-19 消费面实测）\n\n"
        "- 2026-10-04 00:20 探针（r631 sparse clone 法·origin tip）：decisions.md SHA-256 = "
        "4167b7841a5b2b889fa8f8d27b81286faae39b340e786609998431ee6fd46d26\n"
        "- 该值 = r637 及以前水位值（10-03 批 D-20261003-01~04 消费前字节）；r638（10-03 23:25）同法实测 "
        "a82b096c... 并消费 10-03 批（回执在 round_reports/orders 台账）\n"
        "- 即：origin tip 的 decisions.md 缺失 10-03 批行 = 回退/改写（force-push 或 main 重置？）\n"
        "- BigMoney 侧零动作损益：10-03 批涉本司行已消费且回执在账；本窗按实况更新水位并在此留痕\n"
        "- 请总控定谳：有意（CEO/GM 清理）还是意外（误推/劫持）；若意外请恢复——集团台账 append-only 律面\n"
        "- 另：results/post_review/REPORT-20261004.md 首批回填 7 ✗（历史宣称断件：T-73 s3×3/R252 bm-a "
        "ledger repair/T-83-S3 slice2/T-86 s2/T-87 REV-OSC）多数属主= bm-a/bm-c，请按 O-20260924-2115 于下轮 "
        "P0 复核（禁改台账，重 derive 或补闭）\n\n"
        "via bm-b round 639 closeout\n")

print("closeout ok: state=639 epoch=%d clock=%s msg=%s" % (EPOCH, NOW, os.path.basename(msg_path)))
