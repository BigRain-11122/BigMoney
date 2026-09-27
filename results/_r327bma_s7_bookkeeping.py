# -*- coding: utf-8 -*-
"""r327 bm-a S7 bookkeeping: round report line + state file + heartbeat."""
import io
import json
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ---------- 1. round report line (CRLF ledger) ----------
REPORT = r"logs\iteration-loop\round_reports-bm-a.md"
line = (
    "2026-09-27T14:1x+08:00 | R327 bm-a (dept:工程+舰队+治理) | "
    "WM first-line verdict: green (red=false lane healthy; py_low_with_work_cands legal-occupied: sina_mf A1 repull lock-alive in-flight 14:06:58 terminal window ~15:0x; pool 77 done + 1 ready = W2-A lane bm-b (R31 guardrail not burnable by bm-a); board 0 open tickets 30 all-claimed; bandit next_pick=claimed moneyflow-IC source-blocked on panel; audit v2.3 flags=[]) | "
    "did: (A) S0 INHERITED-REBASE RESCUE = r326 session died mid push-rejection resolution (30-UU batch, 28 staged by its resolver, 2 dash-format daily-report UU left + 2 phantom 0-byte artifacts from its hand-copied path typo) -- batch-1 completed (_r327bma_resolve.py: dash twins same-day-regen ts-diffpick S3 13:44:35>13:35:35 whole-bytes + phantom REPORT-20260927.{json,md} absent-from-both-trees git rm -f zero-loss + 17 staged JSON strict-parse verify) -> rebase continue -> push REJECTED (origin moved: bm-c r83 pair + bm-b r327 pair landed mid-resolve) -> batch-2 11-UU canon-resolved (_r327bma_resolve2.py: CODELY in-place-archival adjudication = origin archived face 8452B + my 871B r326 suffix direct-concat 9324B both-pitlaws-present; autofill composite-key union 44+50->44 dedup-first per NEW L28 recipe (r83), last_tick 13:40:02 tie->HEAD; compute_audit (ts,machine) union 201+204->205 collisions 200 content-identical r322; regime asof-union; 7 snapshot/daily faces take-newer all-S2; dashboard js/json pair-law verified 13:42:39 both) -> PUSH LANDED dd34727b..ef92ff78 (r326 commit preserved message-faithful) "
    "(B) S0.5 orders 96/96 zero-unacked DOUBLE-SCAN (round-start + close) + decisions P-32: D-20260927-09 司域回执 = both mandated fixes VERIFIED on-tree law-anchored (classify_conflicts.py L31/L46 ts probe deep-scan nested r311/D-09 + SKILL.md L34 memory-union 后缀直拼 R208/r212/D-09) receipt this line; D-20260927-10 HQ-lane executed zero-action-ours; C-20260927-01 seat-3 opinion already issued r326 F-20260927-02 window to 09-29 "
    "(C) S1 smoke 25/25 PASS zero-fix "
    "(D) S3 closed loop = skill dual-copy sync (r321 law): LIVE drift caught during batch-2 consumption -- activated runtime SKILL.md was 318B behind committed canon (missing bm-c r83 L28 composite-key dedup recipe); synced Tools->.codely-cli both bigmoney-conflict-resolve files + data-gate-wiring + prereg-draft pairs all-identical + classify selftest green + runtime now carries 同复合键 recipe "
    "(E) S4 memory: pitlaw appended (resolver 冲突件清单必须程序化 derive diff-filter=U 禁手抄 -- r326 phantom-path 实弹) -> 10338B > 10KB hard line -> 15th-batch hot-cold archival SAME WINDOW per law (_r327bma_codely_15th.py: 四批~十四批外迁索引 2281B moved verbatim to research/memory-archive/202609.md 十五批节, CODELY 8258B byte-math asserted) "
    "(F) S6 chain 32/32 rc=0 (_r326bma_s6_chain.ps1 reused header-only; Sunday no-new-bar cutoff 09-24: audit py 0.9% flags=[] / wm healthy / regime ORANGE shadow breadth 0.77 / clock idempotent / lhb+heat weekend no-ops / fut+opt cutoff-covered / mf spawned detached rank pass / smf lock-alive no-op repull-in-flight / astock+sigexp+alloc+fundprem lane-guards honest no-op / ths same-day / ah spawned detached panel-incomplete / fundamental 16.4h fresh / b-layer ok / live.paper OK / t35v PASS / t24 22-22 / promo 0-22 / aggr+grid+sysv1 idempotent no-op sysv1 ARMED Monday / t35 export idempotent / daily_report regen faces=4 / build_status 6 traders / token L2 1 leg) | "
    "VERIFIED: smoke 25/25; resolver zero-loss assertions + byte math all-pass; push landed dd34727b..ef92ff78; skill fc-assert pairs identical; CODELY 8258B<10240B strict-utf8; archive anchors verbatim; S6 32x rc=0 stdout; heartbeat epoch int self-assert + clock ISO T-separated | "
    "NEXT: (1) sina_mf repull terminal window ~15:0x mechanical three-piece then bm-b sina-construct open-gate MSG; (2) bm-b W2-A probe->burn watch (lane bm-b); (3) Monday 09-28 09:15 T-91 s3 auto-fire; (4) 10-01 month trio standing; (5) R330 5x HANDOVER check [via bm-a]\r\n"
)
b = io.open(REPORT, "rb").read()
assert b.endswith(b"\r\n"), "ledger tail glue check"
io.open(REPORT, "ab").write(line.encode("utf-8"))
chk = io.open(REPORT, "rb").read()
chk.decode("utf-8")
assert chk == b + line.encode("utf-8")
print("round report: %dB -> %dB (R327 line appended CRLF)" % (len(b), len(chk)))

# ---------- 2. state file ----------
SP = "state-bm-a.json"
d = json.load(io.open(SP, "r", encoding="utf-8"))
d["round_no"] = 327
d["did"] = ("R327: inherited-rebase rescue completed (r326 died mid-resolution: batch-1 finish 2-UU dash twins S3-newer + 2 phantom 0-byte drops; "
            "batch-2 11-UU canon-resolved CODELY archival-adjudication + composite-key autofill 44 + take-newer S2) push LANDED ef92ff78; "
            "D-09 both-fix on-tree verified receipt; skill dual-copy sync r321 (runtime was 318B stale vs canon); pitlaw + 15th-batch CODELY archival 8258B")
d["verdict"] = ("green: audit flags=[]; py low legal-occupied (sina_mf repull in-flight lock-alive ETA ~15:0x); pool 77 done + 1 ready lane bm-b; "
                "board 0 open tickets; orders 96/96 double-scan zero-unacked")
d["next"] = ("R328+: (1) sina_mf repull terminal ~15:0x three-piece + bm-b open-gate MSG; (2) bm-b W2-A burn watch; "
             "(3) Mon 09-28 09:15 T-91 s3 auto-fire; (4) 10-01 month trio; (5) R330 5x HANDOVER")
d["ts"] = TS
d["last_round_ts"] = TS
d["updated_at"] = TS
d["last_seen"] = TS
d["current_task"] = "R327 done: inherited-rebase rescue landed ef92ff78 + skill dual-copy sync + 15th-batch CODELY archival; R328: repull terminal three-piece ~15:0x + bm-b W2-A burn watch"
d["task"] = d["current_task"]
s = json.dumps(d, ensure_ascii=False, indent=1)
json.loads(s)
io.open(SP, "w", encoding="utf-8", newline="\n").write(s + "\n")
json.load(io.open(SP, "r", encoding="utf-8"))
print("state-bm-a.json: round_no=%d ts=%s" % (d["round_no"], TS))

# ---------- 3. heartbeat ----------
HP = r"fleet\machines\bm-a.json"
h = json.load(io.open(HP, "r", encoding="utf-8"))
h["last_seen"] = NOW.strftime("%Y-%m-%d %H:%M:%S")
h["current_task"] = d["current_task"]
h["verdict"] = d["verdict"]
h["heartbeat_epoch_utc"] = int(time.time())
h["clock_read"] = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
cpu = subprocess.run(["powershell", "-NoProfile", "-Command",
                      "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
                     capture_output=True).stdout.decode().strip() or "0"
try:
    h["cpu_pct"] = float(cpu)
except Exception:
    h["cpu_pct"] = 0.0
s = json.dumps(h, ensure_ascii=False, indent=1)
json.loads(s)
io.open(HP, "w", encoding="utf-8", newline="\n").write(s + "\n")
back = json.load(io.open(HP, "r", encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in back["clock_read"], "clock_read must be T-separated ISO (R262 law)"
print("heartbeat: epoch=%d (int verified) clock=%s cpu=%s%%" % (
    back["heartbeat_epoch_utc"], back["clock_read"], back["cpu_pct"]))
print("S7 BOOKKEEPING OK")
