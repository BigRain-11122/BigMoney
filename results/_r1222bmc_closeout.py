# -*- coding: utf-8 -*-
# 2026-10-25 02:3x bm-c r1222 closeout: round report line + state bump + heartbeat
# + one HQ-FEEDBACK row (mechanism gap found this window).
import io
import json
import os
import subprocess
from datetime import datetime, timezone, timedelta

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ).replace(microsecond=0)
ts = now.isoformat()
epoch = int(now.timestamp())
sha = subprocess.run(["git", "-C", REPO, "rev-parse", "--short=10", "HEAD"],
                     capture_output=True, text=True).stdout.strip()

audit = json.load(io.open(os.path.join(REPO, "results", "compute_audit.bm-c.json"),
                          encoding="utf-8"))["latest"]
cpu_pct = audit.get("cpu_total_pct")
gpu = audit.get("gpu") or {}
gpu_free = round(12 * 1024 - float(gpu.get("mem_used_mb") or 0))

DID = ("r1222: W320 cycle CLOSED (adjudication PASS via byte-exact reverse-application of the two r1221 "
       "post-receipt heals / six-gate 83rd consecutive ALL PASS / finalize ledger 1,126,141+2,200=1,128,341 "
       "exact, merged K 699,720+2,200=701,920 exact / fivekeys 6/6 with ZERO prose deviations / sec.7-8 "
       "backfilled 29,943B) + W321 seat ADMIT published (A 721_501..723_500 / B 723_501..723_700)")
CUR = "W320 closed; next window = W321 prereg canon-clone freeze -> five-face splice -> engine self-ignite"

# ---- state
sp = os.path.join(REPO, "state-bm-c.json")
st = json.load(io.open(sp, encoding="utf-8"))
st.update({
    "round_no": 1223,
    "did": DID,
    "did_round": 1222,
    "current": "W320 cycle closed (finalize + fivekeys + backfill); W321 seat admitted",
    "current_task": CUR,
    "current_task_at": ts,
    "activity_now": "green: no local batch in flight (W320 burn complete), board clear",
    "clock_read": ts,
    "ts": ts,
    "agenda_starved": False,
    "idle_rounds": 0,
})
st.setdefault("sync", {})["ts"] = ts
io.open(sp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1) + "\n")

# ---- heartbeat
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(hp, encoding="utf-8"))
hb.update({
    "last_seen": ts,
    "ts": ts,
    "clock_read": ts,
    "heartbeat_epoch_utc": int(epoch),
    "current": "r1222: W320 cycle closed; W321 seat admitted",
    "current_task": CUR,
    "current_task_at": ts,
    "cpu_cores": 32,
    "free_ram_gb": hb.get("free_ram_gb"),
    "gpu_free_mb": int(gpu_free),
    "verdict": "GREEN",
    "idle_rounds": 0,
    "agenda_starved": False,
    "head_sha": sha,
    "round_no": 1222,
    "did": DID,
})
assert isinstance(hb["heartbeat_epoch_utc"], int)
assert "T" in hb["clock_read"]
io.open(hp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1) + "\n")

# ---- round report
line = (
    "%s | r1222 | W320 CYCLE CLOSED IN ONE WINDOW (state round_no was 1222 at open, did_round=1221; the r1221 "
    "window had spliced + burned 12/12 and died before finalize). PRODUCT = results/perpetual_faces/n1_w320_results.json "
    "(mu -0.09283239 / sigma 0.24517796 / A p95 0.3096 / p99 0.4580 / se_mu@K701,920 0.000293; ledger "
    "1,126,141+2,200=1,128,341 exact; merged K 699,720+2,200=701,920 exact) + five-key assertion 6/6 ALL PASS "
    "(results/_r1222bmc_w320_fivekeys.json, ZERO prose deviations: mu-gap 0.01138<0.02, sigma-rel 3.47e-05<10%, "
    "A-p95 delta -0.0129<0.05, K-lift 0.0000, se_mu 0.000293<=0.000293) + six-gate 83rd consecutive ALL PASS "
    "(results/_r1222bmc_w320_sixgate.json) + prereg sec.7/sec.8 machine-backfilled (29,943B, 0 placeholders) + "
    "W321 seat ADMIT published (fleet/inbox/MSG-20261025-0205-bmc-w321-seat.md: A 721,501..723,500 = 74th "
    "consecutive A-hop, base==registered W320 B tail+1; B 723,501..723,700 = 75th above-own-A, base==own-A tail+1; "
    "universe 310 owner rows / ordinal 311; seed_admit FREE x2; relation_asserts 4/4; the W320 prereg's naive "
    "projection 721_301..723_300 was NOT transcribed -- the live trace jumps +1 hop because W320's own B band "
    "refuses that start). ADJUDICATION (new this window, verdict PASS): the W320 freeze receipt's n1 post face is a "
    "PRE-HEAL face -- r1221 wrote the receipt 01:27 then ran two bare-number heals 01:31 (cfg shard_subdir "
    "n1_w319->n1_w320 + prose wave label). Instead of smoothing or failing, the delta was PROVED: reverse-applying "
    "both disclosed heal edits reproduces the receipt post sha 12b6961285eecb68 byte-exactly "
    "(results/_n1_face_adjudication_w320.json, heal_deltas=2 disclosed, unexplained=0); pf reconciles on the direct "
    "eol-basis face; worktree LF == landed LF on both files. VERIFY: S6 chain 39/40 rc0 "
    "(results/_r1222bmc_s6_chain.json; sole rc=1 = t35_open_fill_verify 'marks file for 2026-10-23 missing' = the "
    "bm-b-owned intraday lane, disclosed r1219/r1220/r1221 and permanently unrecoverable -- intraday ticks are not "
    "backfillable); dualrun ZERO-DRIFT 616 entries streak 51; smoke 57/57 PASS; attrition guard 4 ledgers CLEAN "
    "(3 historical shrinks healed); round-zero orphan probe py_faces=5 orphans=0 resident_servers=2 killed=[]; "
    "saturation engine status rc0 (W320 12/12 adopted, no local queue item); D-19 triple watermark both faces "
    "unchanged (dec 0bf59c3c92a370cc / ord 8ff7de47df154ffa) => decision rows: D-20261024-03/-14/-15 and "
    "D-20261025-01..-04 read, none re-opens a bm-c exec obligation beyond what the loop already does; fleet/orders "
    "109 files / 234 acks / unacked=0; Bigmoney-IterationLoop + Bigmoney-LoopWatchdog present (no re-registration), "
    "both git claws present. IDLE FACE: compute_audit flags supply_owner_silent -- pool ready_total=3, "
    "ready_ignitable=0, all three (E81/E90/E93) owned by bm-b whose heartbeat is 2,985 min stale and whose lanes "
    "last wrote 10-24 03:39 / 10-23 23:53 / 10-24 02:16 (corroboration = silence is real, no live lane tick). I did "
    "NOT hand-claim a pool entry: the claim face is owner_since/claimed_since lane-view merged and a manual "
    "unattended edit at window tail risks the r1098 merge law for zero product this window. NEXT-WINDOW OWNER+DEADLINE "
    "(D-20261024-10 three-element form): r1223 window (bm-c, <=2026-10-25 12:00 per D-20261024-15 first-lane "
    "deadline) claims exactly one of E81/E90/E93 through the canonical claim path and ignites it, or records why "
    "not. PIT (two, both caught before canon): (1) a freeze receipt can legitimately predate a post-receipt heal -- "
    "treat receipt-vs-land mismatch as two distinct causes (EOL basis vs later heal) and prove the heal by reverse "
    "application, never by assertion; (2) the finalize run piped through Select-Object was killed by the tool's "
    "5-minute no-output window AFTER the script had already written its product -- always check the product file and "
    "the ledger identity before re-running, because a re-run is a double-burn. | CEO face: current=W320 cycle fully "
    "closed, W321 seat admitted; latest artifact=results/perpetual_faces/n1_w320_results.json + "
    "research/PERPETUAL_N1_W320_PREREG.md (2026-10-25T02:2x); next milestone=W321 prereg freeze + five-face splice "
    "+ 12/12 burn (<=48h) | watermark verdict: GREEN (red=false, next_pick claimed, board clear, no ignitable "
    "local batch) | orphans=0 | local-not-on-origin commits=0 at open; post-push self-proof 3455fa2aa4 pushed "
    "f80cf5a700..3455fa2aa4 | dept:research/engineering\n"
)
rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
raw = io.open(rp, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in raw else "\n"
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    if not raw.endswith(eol):
        f.write(eol)
    f.write(line.replace("\n", eol).rstrip(eol) + eol)

# ---- HQ-FEEDBACK row (mechanism gap: takeover legs missing on the 7 priority lanes)
fb = (
    "| F-20261025-01 | P2 | D-20261024-15 的「一轮一 lane 接管」在 7 条优先车道上机械上不可执行——接管腿只在 "
    "astock/etf/marks 三条车道存在，fund_statements/moneyflow/minute_feed/ah/ths/sina_mf/heat/zt_pool 八个 gate "
    "脚本里 grep 'takeover' 命中 0，且这八条仍按 host-only 守卫（仅 bm-a/所属机动作）把他机打成诚实 no-op | "
    "本窗实测：`Select-String -Path scripts/update_fund_statements.py,update_moneyflow.py,update_minute_feed.py,"
    "ah_panel_puller.py,update_ths_panel.py -Pattern takeover` 零命中；同批 compute_audit 显示池面 3 条 ready 全挂 "
    "bm-b（心跳静默 2,985min）而 ready_ignitable=0 | 建议：把 D-20261024-14 已焊的 takeover_decision 纯函数（"
    "update_etf_daily 导出）复用到这八条 gate 的 host-only 守卫处，加 --takeover + 属主心跳≥120min 双条件，"
    "接管事实写进各 lane 状态件 owner/by/ts（零新机制、零新文件，与 r1100/r1101 同范式）| open |\n"
)
fp = os.path.join(REPO, "HQ-FEEDBACK.md")
fraw = io.open(fp, encoding="utf-8", newline="").read()
feol = "\r\n" if "\r\n" in fraw else "\n"
with io.open(fp, "a", encoding="utf-8", newline="") as f:
    if not fraw.endswith(feol):
        f.write(feol)
    f.write(fb.replace("\n", feol))
print("closeout written", ts, "head", sha, "cpu", cpu_pct, "gpu_free", gpu_free)