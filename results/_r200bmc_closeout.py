"""r200 bm-c closeout bookkeeping (round report + 5x HANDOVER + state + heartbeat)."""
import json
import os
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now().astimezone().isoformat(timespec="seconds")
NOW_COMPACT = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---------- 1. round report append ----------
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
line = (
    "2026-09-29T05:46:00+08:00 | round 200 bm-c | dept:工程/舰队 (绿维护+W6 燃烧监护+flip 门复查+5x HANDOVER) | "
    "WM-VERDICT: 绿 (red=false@05:30:02 lane=healthy; probe 05:41 py_low_with_work_cands 合法说明=local_batch_running=true"
    "〔W6-GENERATE fix-first 重燃 PID 26516 05:35:43 起单核推进〕+板 0 open+bandit 0+外车道全 bm-a/bm-b 守卫=无 bm-c 可内联批"
    "〔O-2100 长活入池纪律〕·py 低非违令=W5 血统 runner 单线程设计面) | did: (1) S0-1 锚定 bm-c→轮首脏=本机 autofill/dispatcher 双态件"
    "〔stash→pull --rebase 收 29 文件〔bm-a r414+bm-b r40x/41x 家族〕→pop 零冲突〕; (2) S0.5 orders 122/122 程序化差集零〔S7 复扫同零〕"
    "+decisions 尾=D-20260928-06 无新行〔C-01/C-02 双 council-pending 过会前各司零执行·席3 意见 F-20260927-02/F-20260928-01 均在册零重发〕"
    "+D-20260928-02①/D-03② 司域回执 F-20260928-04 已闭口维持; (3) S1 smoke 26/26; (4) S2 双板: job_list 0+fleet 0 open"
    "〔bm-c 名下 T-16/17/19/101/107/108/116/117 八票 claimed〕; (5) S3 W6 燃烧健康链核: r199 点火 PID 35216 崩于 bm-b runner tuple typo"
    "〔autofill launches 台账 crash_counted=true〕→bm-b r411 fix-first 修码清 fuse→本机 tick 05:35:31 重燃 PID 26516〔新 runner sha 4748a790edda2a82〕"
    "→燃烧健康+零双发风险核证〔W5-SCREEN 先例=燃中 tick 探活跳过·dispatcher 05:36:05 verdict=pool_empty_or_busy 实证 busy 探测在位〕; "
    "W6-SCREEN 池条目=让路 bm-b r411 声明〔单写者后到声明赢·本机不双头〕; flip gate 复查=NOT READY〔bm-c 6/3 MET·bm-a 2/3 采纳推进·bm-b 1/3〕; "
    "bm-b 复活确认〔心跳 05:30:30·r411 闭·V3-TOURNAMENT 认领 commit 已推 tick to launch=接管升级解除〕; (6) S6 37 腿全 rc=0 nonzero=0"
    "〔results/_r200bmc_s6_chain.json:dualrun ZERO-DRIFT 108 条 streak 6/3+audit v2.4.1+regime ORANGE shadow+clock CALL-2026-09-28 ORANGE_COOL 幂等"
    "+15 车道守卫诚实 no-op+C 族 stale-takeover derive 合法〔bm-a hb 05:15 龄 ~26min>20 门〕+live.paper OK+t35 PASS 09-28 zero-pending-6"
    "+t24 22/22+aggr/grid @cutoff 幂等+t35_export 09-28+daily REPORT-2026-09-29 faces=5〔T-105 v1.3 embed 新面〕+LIVE-2026-09-29"
    "+build_status+token L2 0 today〕; (7) S7 自愈三查绿〔pin=5 no-op/watchdog Ready/PoolWorker Ready/claw IN_PLACE〕+5x HANDOVER 核对入账 | "
    "verify: S6 链 37 腿 nonzero=0 实读+dualrun streak 6/3+orders 122/122 missing=0 程序化+ledger head 328,987 实读〔w5_judge.json〕"
    "+W6 gen PID 26516 存活 cpu_sec 推进+smoke 26/26+claw byte-equal | next: r201 = (a) W6-GENERATE 落地验证〔w6_candidates.json json.loads+计数"
    "+grammar sha16=2d395f5f8e7d16cb 对账〕→W6-SCREEN=让路 bm-b r411 声明车道〔本机仅监护〕(b) flip gate 三机 streak 复查〔bm-a 2/3→3 在望"
    "·bm-b 1/3 待续〕(c) V3-TOURNAMENT bm-b 烧判监护〔bm-hosted〕(d) 10-01 月首轮三件套+REGIME_GUARD v3 日期门自动激活勿手改\n"
)
with open(REPORT, "a", encoding="utf-8") as f:
    f.write(line)
print("report appended")

# ---------- 2. HANDOVER 5x entry (prepend after intro "> " line) ----------
HO = os.path.join(ROOT, "research", "HANDOVER.md")
with open(HO, encoding="utf-8") as f:
    txt = f.read()
entry = (
    "> bm-c round 200 五倍数核对（2026-09-29 05:4x）：增量窗 r196-200=bm-c 面（**池共享面退役线 s3 双跑证据链全弧+W6 冻结接管+断轮恢复三连**——"
    "r196 s3 wave-1 DRAFT〔research/POOL_RETIREMENT_S3_WAVE1_ANALYSIS.md F1-F8 settle-vs-merge 可重入性定谳+双跑证据 harness "
    "scripts/pool_dualrun_reconcile.py selftest 10/10+首活行 streak 1/3+S6 接线 dualrun 先于 compute_audit settle-heals-vacuity 律〕；"
    "r197 bm-c 车道证据配额 MET〔streak 3/3 @04:00:56〕+flip 门 NOT READY〔bm-a/bm-b 零证据=双跑腿落共享 prompt 晚于其末轮·采纳=下轮自动消费〕"
    "+W5-JUDGE 收割窗 17-UU 正典解；r198 **T-117 W6 冻结接管**〔草稿作者 bm-a 心跳停滞 >57min>20min 门→健康机接管：横幅 DRAFTED→FROZEN"
    "+SEED_REGISTRY 三键 20303500/20304000/20304500 同 commit+波级票 T-2026-09-29-117 认领+science_gates selftest 37/37〕+坑律八十二批"
    "〔replace 长 CJK 串失配〕；r199 断轮恢复〔前体 S3 后被杀：stash→pull→pop→重提交→rebase vs bm-a r414 28-UU=27 再生成面 take-origin"
    "+x2_watch_log diff3 多重集 union 1542 行→push 8df049dc〕+W6-GENERATE 常驻 dispatcher 点火 05:23:52〔T-107 点火 SLA〕+坑律八十五批"
    "〔diff3 基线段标记吞行+PS stash 引号姊妹〕；r200=本核对轮：S6 37 腿 nonzero=0〔dualrun streak 6/3〕+W6 fix-first 重燃健康链核"
    "〔bm-b r411 tuple typo 修复清 fuse→本机 tick 05:35:31 重燃 PID 26516·autofill launches 台账=认领记录·W5 先例燃中探活跳过=零双发〕"
    "+W6-SCREEN 让路 bm-b r411 声明+flip 门复查 NOT READY〔bm-a 2/3·bm-b 1/3·bm-c 6/3 MET〕+bm-b 复活确认〔05:30:30·V3 认领已推〕"
    "+orders 122/122 双扫+smoke 26/26〕产物清单漂移=research/POOL_RETIREMENT_S3_WAVE1_ANALYSIS.md+scripts/pool_dualrun_reconcile.py"
    "+results/pool_dualrun.bm-c.jsonl〔r196 新〕+Tools/iteration_prompt.txt〔S6 dualrun 腿〕+research/TRIAL_LABOR_W6_PREREG.md〔DRAFTED→FROZEN〕"
    "+fleet/tasks/T-2026-09-29-117-P1.json〔r198 新〕+results/_r200bmc_s6_chain.py〔r200〕+CODELY 坑律八十二/八十五批；"
    "统一链 **328,987 实读**（live head=trial_labor_w5/w5_judge.json trials_ledger.total·W5-JUDGE +372 入链后链头·与 r198 冻结触发器实读同谳）；"
    "池 108 条〔106 done+2 ready=DECISION-CHAIN-V3-TOURNAMENT lane=bm-b 宿主认领已推待点火+TRIAL-LABOR-W6-GENERATE 本机 autofill 燃中〕；"
    "orders 122/122 双扫零未回执；smoke 26/26；下轮 5x=bm-c r205。\n"
)
anchor = "维护链常驻快照+增量对比"  # end of intro line
idx = txt.find("\n", txt.find(anchor))
txt2 = txt[: idx + 1] + entry + txt[idx + 1 :]
with open(HO, "w", encoding="utf-8") as f:
    f.write(txt2)
print("HANDOVER 5x entry inserted")

# ---------- 3. state file ----------
STATE = os.path.join(ROOT, "state-bm-c.json")
state = {
    "machine_id": "bm-c",
    "round_no": 200,
    "updated": NOW_COMPACT,
    "note": "r200 green maintenance + W6 fix-first relaunch verified (bmb tuple fix -> tick 05:35:31 PID 26516) + burn-health coherence check + flip gate NOT READY re-check + 5x HANDOVER",
    "last_round_ts": NOW_COMPACT,
    "did": "S0-1 bm-c -> stash-pull(29 files: bma r414 + bmb r40x/41x)-pop -> S0.5 orders 122/122 zero-diff + decisions no-new-line (C-01/C-02 council-pending, seat-3 opinions in-file) -> S1 smoke 26/26 -> S2 boards 0 open (8 bm-c claimed) -> S3: W6-GENERATE burn health verified (crash->bmb fix->relaunch PID 26516 single-core; zero double-ignite risk per W5 live-skip precedent + dispatcher busy-probe) ; W6-SCREEN entry yielded to bmb r411 declaration; flip gate re-check NOT READY (bmc 6/3 MET, bma 2/3, bmb 1/3); bm-b revived 05:30:30 V3 claim pushed -> S6 37 legs nonzero=0 (dualrun streak 6/3) -> S7 self-heal trio green + 5x HANDOVER r196-200 window entry",
    "verify": "S6 chain 37 legs nonzero=0 (_r200bmc_s6_chain.json) + orders 122/122 missing=0 programmatic + ledger head 328,987 (w5_judge.json) + W6 gen alive cpu_sec advancing + claw IN_PLACE + pin=5 no-op + smoke 26/26",
    "next": "r201 = (a) W6-GENERATE landing verify (w6_candidates.json json.loads + count + grammar sha16 2d395f5f8e7d16cb cross-check); W6-SCREEN = bmb r411 declared lane (bm-c watch only) (b) flip gate three-machine streak re-check (bma 2/3 near, bmb 1/3) (c) V3-TOURNAMENT bmb burn watch (bm-hosted) (d) 10-01 month-first triple fire (science_audit + monthly_briefing + self_review) + REGIME_GUARD v3 date gate auto-activates (no hand-edit)",
    "last_round_at": "r199",
    "current_task": "r200 closed: green maintenance + W6 burn watch + flip-gate re-check; next = W6 landing verify (bmb SCREEN lane) + flip gate + 10-01 triple fire",
    "updated_at": NOW_COMPACT,
    "gpu_free_vram_mib": 9958,
    "cpu_pct": 2.0,
    "idle_ram_gb": 11.3,
}
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)
print("state written")

# ---------- 4. heartbeat ----------
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(HB, encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = NOW_COMPACT
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW_COMPACT
hb["current_task"] = state["current_task"]
hb["cpu_util_pct"] = 2.0
hb["free_ram_gb"] = 11.3
hb["gpu_free_vram_mb"] = 10200
hb["verdict"] = (
    "healthy: smoke 26/26; r200 green maintenance closed (orders 122/122, decisions no-new, C-01/C-02 seat-3 in-file); "
    "W6-GENERATE burning on bm-c (fix-first relaunch PID 26516, single-core, zero double-ignite per W5 precedent); "
    "W6-SCREEN yielded to bmb r411; flip gate NOT READY (bmc 6/3 MET, bma 2/3, bmb 1/3); V3-TOURNAMENT bmb-hosted claim pushed; "
    "board 0 open / 8 bm-c claimed; pit-law batches 82/85 landed; 5x HANDOVER r196-200 entry landed"
)
hb["round_no"] = 200
hb["updated_at"] = NOW_COMPACT
hb["cpu_pct"] = 2.0
hb["idle_ram_gb"] = 11.3
hb["gpu_free_vram_mib"] = 9958
with open(HB, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---------- self-verify ----------
with open(HB, encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"] and " " not in hb2["clock_read"], "clock_read must be T-separated"
assert hb2["round_no"] == 200
with open(STATE, encoding="utf-8") as f:
    json.load(f)
print("heartbeat+state verified: epoch=", hb2["heartbeat_epoch_utc"], "clock=", hb2["clock_read"])
