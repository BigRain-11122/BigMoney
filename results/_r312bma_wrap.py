# -*- coding: utf-8 -*-
"""R312 bm-a wrap: round report append + state bump + heartbeat + inbox archive."""
import json
import os
import shutil
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now().astimezone().isoformat(timespec="seconds")

REPORT = (
    NOW + " | R312 bm-a (dept:宸ョ▼+绛栫暐) | WM first-line verdict: red=false lane healthy; "
    "probe 10:38 py_low_board_clear (board 0 open 0 bandit 0; pool_ready 0 = DRAINED BY COMPLETION "
    "honest face; audit v2.3 CLEAN flags[] + pool_starvation_candidate first-sample logged "
    "run_samples=1 span null = completion-drain not neglect; MF_IC_P1 supply line legally waiting EM panel "
    "source-blocked 53/5222 30min-self-heal alive, sina panel complete 5228/5228 = T-72 separate lane) "
    "| did: (A) S0.5 both-scans: orders 96/96 zero unacked (round-start set-diff + wrap rescan); "
    "decisions.md review: D-20260927-04 BigMoney revival-red anchor law receipt standing (self-fix already "
    "executed R256 per decision text, reasonable=accept) + D-20260927-05 item3 commit-pre-conflict-marker "
    "check SELF-ADOPTED and first-executed this round PASS (clean); inbox 1 msg processed (MSG-1025 bm-c "
    "T-19 stage-2c claim-decl visibility-only -> processed/) "
    "(B) COMPUTE FACE POOL DRAINED 76/76 done 0 ready: r314 evidence-gate flip X2-DA 1806/1806 first, "
    "then in-round shard burns X2-deep DB/DC/DD/DE (26.9/26.8/26.4/18.3s @14workers, 1806/1812/1806/1806 cells) "
    "+ PROS 9 shards (legacy LA-LD 6908 cells + deep DA-DE 6622-6644 cells, ~75s each @25workers) + "
    "final flip 9/9 -> harvest faces (X2 finalize + PROS finalize) = bm-b ticket-owner science face "
    "handed over via pushed pool commit; T-89/T-90 9+9 shard grind COMPLETE per r314 canon "
    "(C) S7 push-collision resolved per canon: wave-1 push rejected (bm-b in-window same-shard flips, "
    "bm-c r74b joined fleet loop) -> pull --rebase 2 UU -> classifier autofill_state=mixed-dict+ledger "
    "(union 50+50 cap50 ts-asc CRLF-mirror, last_tick whole-dict ts-compare kept theirs 10:30:02) + "
    "runnable_pool=UNKNOWN manual per-entry done-absorb union 76/76 converged (bm-b had independently "
    "burned all 14 same shards in same window = duplicate compute converged by keep-last design, "
    "zero data loss) -> resolvers _r312bma_resolve.py + _r312bma_resolve_state.py -> GIT_EDITOR=true "
    "continue -> push LANDED b1e48136 "
    "(D) canon upgrades: classifier new rule runnable_pool=pool-entry-done-union (selftest 19/19 ALL GREEN) "
    "+ SKILL.md table row; CODELY.md new pitfall entry (in-round shard burn pre-fetch law r312) + "
    "heat/cold reorg batch-8 (10 entries migrated verbatim zero-loss to memory-archive/202609.md, "
    "CODELY.md 9,595B->2,929B under 10KB hard line) "
    "(E) S6 24 legs rc=0 + bar-conditional legal skip (Sunday cutoff 09-24 same posture: audit CLEAN / "
    "wm py_low_board_clear / daily 0-new / regime ORANGE shadow trigger breadth 0.77 / scorecard 6-28-7 / "
    "clock ORANGE_COOL sleeves4 activated0 idempotent / lhb+fut+opt cutoff-covered zero-network / heat weekend / "
    "mf rank-spawn in-flight / smf fresh / astock+sigexport bm-b-lane honest no-op / ths same-day / "
    "ah detached-refresh in-flight / fundprem bm-c-lane / fundamental 13.0h fresh / b-layer pass / "
    "daily_scorecard 6 traders / daily_report faces=4 token=1 / build_status 10factors 432combos / "
    "token L2 1 leg) "
    "| VERIFIED: smoke 25/25; schtasks alive per R49 law (IterationLoop Running + Watchdog Ready) "
    "| NEXT: Monday 09-28 open window = new-bar full chain + T-91 s3 auto-fire (SIG/BARS-09-28 -> sysv1 "
    "replay -> first cohort entries + marks -> three report faces); bm-b harvest verdicts standing "
    "(X2 finalize + PROS finalize = ticket-owner science face); pool-hunger candidate confirm window "
    "~11:08 honest reading = completion-drained + supply lines (MF_IC_P1 EM-blocked waiting, next "
    "prereg supply = bm-b verdict-driven v2 line per O-0809); 10-01 month trio standing"
)

with open(os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-a.md"), "a", encoding="utf-8") as f:
    f.write(REPORT + "\n")

# state bump
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 312
st["did"] = ("R312: pool drained 76/76 (X2-deep 4 + PROS 9 in-round burns ~15min wall + evidence-gate flips "
             "all done) -> harvest faces handed to bm-b ticket owner; push-collision union-resolved "
             "(pool done-absorb + autofill launches union) landed b1e48136")
st["verdict"] = ("py_low_board_clear legal-idle completion face (pool drained 0 ready, board 0 open, "
                 "MF_IC_P1 supply waiting EM unblock; audit CLEAN + starvation-candidate first-sample honest)")
st["next"] = ("R313: Monday 09-28 window = new-bar chain + T-91 s3 auto-fire; bm-b harvest verdicts "
              "(X2/PROS finalize) standing; 10-01 month trio standing")
st["ts"] = NOW
st["last_round_ts"] = NOW
st["updated_at"] = NOW
st["current_task"] = "R313 next: Monday window watch + supply line (MF_IC_P1 EM unblock / bm-b verdict-driven v2)"
st["last_run"] = NOW
st["last_round_at"] = NOW
st["last_seen"] = NOW
st["task"] = "R312: pool drained 76/76 + collision union resolve + canon batch-8 reorg"
st["last_round"] = 311
st["updated"] = NOW
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# heartbeat
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = NOW
hb["current_task"] = "R312 done: pool 76/76 drained, harvest->bm-b; R313 next: Monday window + supply line"
hb["verdict"] = "py_low_board_clear completion face (pool 0 ready all-done; supply waiting MF_IC_P1 EM unblock)"
epoch = int(time.time())
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = NOW
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int"
orders = sorted(f for f in os.listdir(os.path.join(ROOT, "fleet", "orders"))
                if f.startswith("O-") and f.endswith(".md"))
ack = hb.get("orders_ack", [])
assert set(orders) <= set(ack) and len(set(orders) & set(ack)) == len(orders), \
    f"orders_ack gate: {len(orders)} orders vs ack"
hb["round_no"] = 312
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# inbox archive
src = os.path.join(ROOT, "fleet", "inbox", "MSG-20260927-1025-bm-c-t19-stage2c-prereg.md")
dst_dir = os.path.join(ROOT, "fleet", "inbox", "processed")
os.makedirs(dst_dir, exist_ok=True)
if os.path.exists(src):
    shutil.move(src, os.path.join(dst_dir, os.path.basename(src)))
    print("inbox: 1 msg processed-archived")

# post-verify
hb2 = json.load(open(hp, encoding="utf-8"))
print(f"report appended; state round_no={st['round_no']}; heartbeat epoch={hb2['heartbeat_epoch_utc']} "
      f"(int={isinstance(hb2['heartbeat_epoch_utc'], int)}) clock={hb2['clock_read']}; "
      f"orders gate {len(orders)}/{len(ack)} PASS")
