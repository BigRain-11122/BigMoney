"""r200 bm-c pre-push bookkeeping amendment: W6-GENERATE landed mid-round
(05:46:27) after the bookkeeping was written -- update report/state/HANDOVER/
heartbeat to reflect the landing, then amend the (unpushed) commit."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------- 1. round report: replace the r200 line ----------
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
with open(REPORT, encoding="utf-8") as f:
    lines = f.read().split("\n")
idx = None
for i, l in enumerate(lines):
    if "| round 200 bm-c |" in l:
        idx = i
        break
assert idx is not None, "r200 report line not found"
NEW = (
    "2026-09-29T05:52:00+08:00 | round 200 bm-c | dept:工程/舰队 (绿维护+W6 着陆验证+flip 门复查+5x HANDOVER) | "
    "WM-VERDICT: 绿 (red=false@05:30:02 lane=healthy; probe 05:41 py_low_with_work_cands 合法说明=local_batch_running=true"
    "〔W6-GENERATE fix-first 重燃 PID 26516 05:35:43 起单核推进·05:46:27 完整着陆〕+板 0 open+bandit 0+外车道全 bm-a/bm-b 守卫"
    "=无 bm-c 可内联批〔O-2100 长活入池纪律〕·py 低非违令=W5 血统 runner 单线程设计面) | did: (1) S0-1 锚定 bm-c"
    "→轮首脏=本机 autofill/dispatcher 双态件〔stash→pull --rebase 收 29 文件〔bm-a r414+bm-b r40x/41x 家族〕→pop 零冲突〕; "
    "(2) S0.5 orders 122/122 程序化差集零〔S7 复扫同零〕+decisions 尾=D-20260928-06 无新行〔C-01/C-02 双 council-pending "
    "过会前各司零执行·席3 意见 F-20260927-02/F-20260928-01 均在册零重发〕+D-20260928-02①/D-03② 司域回执 F-20260928-04 "
    "已闭口维持; (3) S1 smoke 26/26; (4) S2 双板: job_list 0+fleet 0 open〔bm-c 名下 T-16/17/19/101/107/108/116/117 八票 claimed〕; "
    "(5) S3 W6 燃烧健康链核+**着陆验证闭环**: r199 点火 PID 35216 崩于 bm-b runner tuple typo〔autofill launches 台账 "
    "crash_counted=true〕→bm-b r411 fix-first 修码清 fuse→本机 tick 05:35:31 重燃 PID 26516〔新 runner sha 4748a790edda2a82〕"
    "→零双发风险核证〔W5-SCREEN 先例=燃中 tick 探活跳过·dispatcher 05:36:05 verdict=pool_empty_or_busy 实证 busy 探测在位〕"
    "→**05:46:27 w6_candidates.json 完整落盘=着陆验证 PASS**: json.loads 全验+raw 5000→distinct 3952〔fp 塌缩+17 对 corr≥0.999 "
    "collapse〕+grammar sha16=2d395f5f8e7d16cb 与冻结件恒等+六源排除 0 hits〔W1-W5 screen survivors+judged products+mass 全 declare〕"
    "+RAM gate 11.28GB+evidence_cutoff 2026-09-22+产物随本轮 commit 入库; W6-SCREEN 池条目=让路 bm-b r411 声明〔单写者后到声明赢·本机不双头〕; "
    "flip gate 复查=NOT READY〔bm-c 6/3 MET·bm-a 2/3 采纳推进·bm-b 1/3〕; bm-b 复活确认〔心跳 05:30:30·r411 闭·V3-TOURNAMENT "
    "认领 commit 已推 tick to launch=接管升级解除〕; (6) S6 37 腿全 rc=0 nonzero=0〔results/_r200bmc_s6_chain.json:dualrun "
    "ZERO-DRIFT 108 条 streak 6/3+audit v2.4.1+regime ORANGE shadow+clock CALL-2026-09-28 ORANGE_COOL 幂等+15 车道守卫诚实 no-op"
    "+C 族 stale-takeover derive 合法〔bm-a hb 05:15 龄 ~26min>20 门〕+live.paper OK+t35 PASS 09-28 zero-pending-6+t24 22/22"
    "+aggr/grid @cutoff 幂等+t35_export 09-28+daily REPORT-2026-09-29 faces=5〔T-105 v1.3 embed 新面〕+LIVE-2026-09-29"
    "+build_status+token L2 0 today〕; (7) S7 自愈三查绿〔pin=5 no-op/watchdog Ready/PoolWorker Ready/claw IN_PLACE〕"
    "+5x HANDOVER 核对入账 | verify: **W6 着陆三验=sha16 恒等+json.loads 全验+5000→3952 计数实读**+S6 链 37 腿 nonzero=0 实读"
    "+dualrun streak 6/3+orders 122/122 missing=0 程序化+ledger head 328,987 实读〔w5_judge.json〕+smoke 26/26+claw byte-equal "
    "| next: r201 = (a) W6-GENERATE 池条目 done-flip 收割〔tick 05:55 起自动 harvest·W1-W5 先例〕+W6-SCREEN=让路 bm-b r411 "
    "声明车道〔本机仅监护〕(b) flip gate 三机 streak 复查〔bm-a 2/3→3 在望·bm-b 1/3 待续〕(c) V3-TOURNAMENT bm-b 烧判监护"
    "〔bm-hosted〕(d) 10-01 月首轮三件套+REGIME_GUARD v3 日期门自动激活勿手改"
)
lines[idx] = NEW
with open(REPORT, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(lines))
print("report line replaced")

# ---------- 2. HANDOVER: amend the r200 entry with landing ----------
HO = os.path.join(ROOT, "research", "HANDOVER.md")
with open(HO, encoding="utf-8") as f:
    txt = f.read()
old = "+W6-SCREEN 让路 bm-b r411 声明+flip 门复查 NOT READY"
new = ("+**W6-GENERATE 05:46:27 着陆收割**〔5000 raw→3952 distinct·sha16 2d395f5f8e7d16cb 与冻结件恒等·六源排除 0 hits·"
       "RAM 11.28GB·产物 w6_candidates.json 入库〕+W6-SCREEN 让路 bm-b r411 声明+flip 门复查 NOT READY")
assert old in txt
txt = txt.replace(old, new, 1)
with open(HO, "w", encoding="utf-8", newline="") as f:
    f.write(txt)
print("HANDOVER amended")

# ---------- 3. state file: refresh did/verify/next ----------
STATE = os.path.join(ROOT, "state-bm-c.json")
with open(STATE, encoding="utf-8") as f:
    st = json.load(f)
st["note"] = ("r200 green maintenance + W6-GENERATE landing verified mid-round (05:46:27: 5000->3952 distinct, "
              "sha16 2d395f5f8e7d16cb identical to frozen grammar, zero double-ignite) + flip gate NOT READY re-check "
              "+ 5x HANDOVER")
st["did"] = ("S0-1 bm-c -> stash-pull(29 files: bma r414 + bmb r40x/41x)-pop -> S0.5 orders 122/122 zero-diff + decisions "
             "no-new-line (C-01/C-02 council-pending, seat-3 opinions in-file) -> S1 smoke 26/26 -> S2 boards 0 open "
             "(8 bm-c claimed) -> S3: W6 burn health verified + LANDING VERIFY PASS (crash->bmb fix->relaunch PID 26516 "
             "->05:46:27 w6_candidates.json complete: json.loads + raw 5000->distinct 3952 + grammar sha16 identical + "
             "6-source exclusion 0 hits + RAM 11.28GB); W6-SCREEN entry yielded to bmb r411 declaration; flip gate "
             "re-check NOT READY (bmc 6/3 MET, bma 2/3, bmb 1/3); bm-b revived 05:30:30 V3 claim pushed -> S6 37 legs "
             "nonzero=0 (dualrun streak 6/3) -> S7 self-heal trio green + 5x HANDOVER r196-200 window entry")
st["verify"] = ("W6 landing triple-verify (sha16 identical + json.loads + 5000->3952 count) + S6 chain 37 legs nonzero=0 "
                "(_r200bmc_s6_chain.json) + orders 122/122 missing=0 programmatic + ledger head 328,987 (w5_judge.json) "
                "+ claw IN_PLACE + pin=5 no-op + smoke 26/26")
st["next"] = ("r201 = (a) W6-GENERATE pool done-flip harvest (tick auto 05:55+ per W1-W5 precedent); W6-SCREEN = bmb r411 "
              "declared lane (bm-c watch only) (b) flip gate three-machine streak re-check (bma 2/3 near, bmb 1/3) "
              "(c) V3-TOURNAMENT bmb burn watch (bm-hosted) (d) 10-01 month-first triple fire (science_audit + "
              "monthly_briefing + self_review) + REGIME_GUARD v3 date gate auto-activates (no hand-edit)")
st["current_task"] = ("r200 closed: W6-GENERATE landing verified (3952 candidates) + green maintenance; next = "
                      "W6 done-flip harvest + W6-SCREEN (bmb lane) + flip gate + 10-01 triple fire")
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state amended")

# ---------- 4. heartbeat verdict ----------
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(HB, encoding="utf-8") as f:
    hb = json.load(f)
hb["current_task"] = st["current_task"]
hb["verdict"] = ("healthy: smoke 26/26; r200 closed -- W6-GENERATE landed 05:46:27 (5000->3952 distinct, sha16 identical, "
                 "zero double-ignite, product committed); W6-SCREEN yielded to bmb r411; flip gate NOT READY (bmc 6/3 MET, "
                 "bma 2/3, bmb 1/3); V3-TOURNAMENT bmb-hosted claim pushed; board 0 open / 8 bm-c claimed; orders 122/122; "
                 "5x HANDOVER r196-200 entry landed")
with open(HB, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-verify
with open(HB, encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2["heartbeat_epoch_utc"], int)
assert "T" in hb2["clock_read"] and " " not in hb2["clock_read"]
json.load(open(STATE, encoding="utf-8"))
print("amend complete, heartbeat verified epoch=", hb2["heartbeat_epoch_utc"])
