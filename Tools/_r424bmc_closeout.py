"""r424 bm-c closeout: state-bm-c.json + heartbeat + round report append.
EOL-preserving writes (state=LF, heartbeat/round report=CRLF, r289 probe law)."""
import json
import time
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
CLOCK = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())


def write_eol(path, text, eol):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text if eol == "\n" else text.replace("\n", "\r\n"))


# ---------------- state-bm-c.json (LF) ----------------
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 424
st["clock_read"] = CLOCK
st["heartbeat_epoch_utc"] = EPOCH
st["last_seen"] = CLOCK
st["last_ts"] = CLOCK
st["last_round"] = ("r424 bm-c: MASS_TRIAL_W2-JUDGE 4 shards enrolled+delivered "
                    "(N_judge=805, +164/-0 surgical) + SHARD-0 burn in-flight "
                    "(PID 21188)")
st["last_round_at"] = CLOCK
st["last_round_ts"] = CLOCK
st["current_task"] = (
    "r424: MASS_TRIAL_W2-JUDGE 4 shards enrolled into runnable_pool (origin-"
    "delivered, 4/4 verified); SHARD-0 claimed by local daemon 18:38:38 + "
    "judge burn in-flight (PID 21188, 11 RAM-gated workers, ckpt 68+/202); "
    "next: r425 adopt SHARD-0 done-flip + shards 1-3 claims -> judge-finalize "
    "--wave 2 when 4/4 done")
st["did"] = (
    "r424 bm-c: (1) MAIN DELIVERABLE: judge-prep artifact adopted ("
    "w2_judge_state.json committed d34a7d071: 806 survivors -> N_judge=805, "
    "collapse 1 [rep W2-18013<-W2-18025], manifest PASS 48/48, candidates "
    "sha16 1a8751ed16a9c641) + MASS-TRIAL-W2-JUDGE-SHARD-0..3 enrolled into "
    "runnable_pool.json per frozen prereg sec.9.1 execution face (r509 "
    "raw-text surgical +164/-0, 362->366 entries, 202/201/201/201 cells, "
    "host gate t18 deep cache *.parquet r316 law, lane_owner null priority "
    "1 BelowNormal, done-flip duty disclosed in entry notes per W1 no-"
    "handshake precedent) + push delivered same round (r598 law; one "
    "rejection -> tick-dirt self-commit r290 + rebase retry -> origin 4/4 "
    "entries verified 893754B). (2) BURN LIVE: local autofill daemon claimed "
    "SHARD-0 18:38:38 (1 min post-enrollment) + ignited runner PID 21188 "
    "18:38:48 -- wave-2 judgment burn IN-FLIGHT 10-03, 5 days ahead of "
    "O-2115 10-08 acceptance; 11 RAM-gated workers (RAM 4.7->7.6GB free "
    "recovered), ckpt w2_judge_shard_0of4.jsonl 68+/202 rows at 18:44. "
    "(3) S0: pull-rebase integrated 3 incoming (bm-a r635 + claim ticks); "
    "D-19 4167B784 MATCH; orders SHA 68947C17 MATCH; orders 152/152 zero-"
    "unacked. (4) S1 smoke 47/47; SatEngine rc0 alive. (5) S6 37 legs rc0 "
    "(dualrun streak 21 zero-drift; audit FLAG:ignition_sla on fresh W2-"
    "JUDGE entries = expected pre-claim window, self-healing via daemon "
    "claims -- SHARD-0 claimed+ignited same window; golden-week no-ops + "
    "lane-guards honest). (6) S7 4/4 self-heal green (loop pin=5 no-op, "
    "watchdog, both claws byte-fresh, attrition CLEAN).")
st["next"] = (
    "(a) r425: poll w2_judge_shard_0of4.jsonl (202/202) -> land SHARD-0 done "
    "flip (shard+entry two-layer r488/r489) + verify shards 1-3 claims "
    "(fleet daemons); all 4 done -> judge-finalize --wave 2 (single-shot "
    "ledger MASS_TRIAL_W2_JUDGE + 805-cell completeness probe + w2_judge."
    "json product) <=10-06; (b) D-06 full-reconciliation closeout 10-07; "
    "(c) T-143 assembly window post-10-09 (deliverable 10-29); (d) "
    "moneyflow GM ruling watch (MSG-1452/1543); (e) W14 lane zero-touch "
    "pending GM dual-ruling.")
st["verify"] = (
    "smoke 47/47 rc0; enroll surgical +164/-0 numstat + json.loads full "
    "parse + cell math 202/201/201/201=805; origin delivery 4/4 entries "
    "(blob 893754B, 366 entries, behind=0 post-push); burn PID 21188 alive "
    "with 11 worker children + ckpt rows streaming; dualrun streak 21 "
    "zero-drift; S6 37 legs rc0; S7 4/4 green (attrition CLEAN rc0); D-19 "
    "4167B784 MATCH; orders 152/152; WM insufficient_history golden-week "
    "honest no-red; push delivery verify post-commit (本地未达 origin=0)")
st["updated"] = CLOCK
st["updated_at"] = CLOCK
st["last_decisions_read_at"] = CLOCK
write_eol(sp, json.dumps(st, ensure_ascii=False, indent=1) + "\n", "\n")

# ---------------- heartbeat fleet/machines/bm-c.json (CRLF) ----------------
hp = r"fleet\machines\bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["activity_now"] = (
    "r424: MASS_TRIAL_W2-JUDGE 4 shards enrolled+origin-delivered; SHARD-0 "
    "judge burn in-flight locally (PID 21188, 11 workers)")
hb["clock_read"] = CLOCK
hb["cpu_pct"] = 100.0
hb["cpu_util_pct"] = 100.0
hb["cpu_idle_pct"] = 0.0
hb["free_ram_gb"] = 7.6
hb["idle_ram_gb"] = 7.6
hb["ram_free_gb"] = 7.6
hb["gpu_free_vram_mib"] = 296
hb["gpu_free_vram_mb"] = 296
hb["gpu_idle_vram_mb"] = 296
hb["gpu_idle_vram_mib"] = 296
hb["gpu_vram_free_mb"] = 296
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = st["current_task"]
hb["latest_artifact"] = (
    "runnable_pool.json MASS-TRIAL-W2-JUDGE-SHARD-0..3 registration "
    "(enroll commit rebased->45c6d7258 on origin, 18:39 r424) + "
    "results/mass_trial/w2_judge_shard_0of4.jsonl burn checkpoint "
    "streaming (68+/202 rows 18:44)")
hb["next_milestone"] = (
    "all 4 judge shards done -> judge-finalize --wave 2 -> w2_judge.json + "
    "ledger MASS_TRIAL_W2_JUDGE by 10-06 (O-2115 acceptance 10-08); D-06 "
    "closeout 10-07")
hb["last_seen"] = CLOCK
hb["last_seen_at"] = CLOCK
hb["prod_lanes"] = (
    "MASS_TRIAL_W2 judge burn live (SHARD-0 local, 1-3 fleet-claimable); "
    "moneyflow lane GM-ruling pending; D-06 closeout 10-07")
hb["round_no"] = 424
hb["updated_at"] = CLOCK
hb["orders_ack"] = hb.get("orders_ack", [])
write_eol(hp, json.dumps(hb, ensure_ascii=False, indent=1) + "\n", "\r\n")

# heartbeat self-proof: epoch must be JSON int
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in hb2["clock_read"], "clock not T-separated"
print("heartbeat self-proof OK: epoch int", hb2["heartbeat_epoch_utc"],
      "clock", hb2["clock_read"])

# ---------------- round report append (CRLF) ----------------
line = (
    f"{CLOCK}\t| r424 bm-c\t| r424 bm-c: (1) MAIN DELIVERABLE (score 2, "
    "runnable registration + live burn): judge-prep artifact adopted "
    "(w2_judge_state.json committed d34a7d071: 806->805 collapse 1, rep "
    "W2-18013<-W2-18025, manifest PASS 48/48, sha16 1a8751ed16a9c641) + "
    "MASS-TRIAL-W2-JUDGE-SHARD-0..3 enrolled into runnable_pool.json per "
    "frozen prereg sec.9.1 (r509 raw-text surgical +164/-0, 362->366 "
    "entries, cells 202/201/201/201=805, host gate t18 deep *.parquet, "
    "lane_owner null priority 1, done-flip duty in entry notes per W1 "
    "no-handshake precedent) + same-round origin delivery (r598; one "
    "push reject -> tick-dirt self-commit r290 + rebase retry -> 4/4 "
    "verified 893754B). (2) BURN LIVE: local daemon claimed SHARD-0 "
    "18:38:38 (1 min post-enroll) + ignited PID 21188 18:38:48 -- wave-2 "
    "judgment IN-FLIGHT 10-03 (O-2115 acceptance 10-08, 5 days early); 11 "
    "RAM-gated workers (RAM 4.7->7.6GB recovered), ckpt 68+/202 rows "
    "18:44, ETA ~18:47; SHARDS 1-3 ready unclaimed for fleet daemons. "
    "(3) S0: 3 incoming integrated (bm-a r635 + claim ticks); D-19 "
    "4167B784 MATCH; orders 68947C17 MATCH; 152/152 zero-unacked. (4) S1 "
    "smoke 47/47; SatEngine rc0 alive. (5) S6 37 legs rc0 (dualrun "
    "streak 21 zero-drift; audit ignition_sla FLAG on fresh W2 entries = "
    "expected pre-claim window, SHARD-0 self-healed same window; "
    "golden-week no-ops + lane-guards honest). (6) S7 4/4 green (loop "
    "pin=5 no-op, watchdog, claws byte-fresh, attrition CLEAN). | WM "
    "verdict: green-no-red (py_watermark insufficient_history golden-week "
    "honest; board clear; bandit next_pick moneyflow-IC source-blocked "
    "standing). dept:策略/研究\t| 验证：enroll numstat +164/-0 + json.loads "
    "full parse + cell math; origin 4/4 entries behind=0 post-push; burn "
    "PID 21188 alive 11 children ckpt streaming; smoke 47/47; dualrun 21; "
    "S6 37 legs rc0; S7 4/4; orders 152/152; D-19/orders SHA MATCH\t| "
    "下轮：r425 poll SHARD-0 202/202 -> done-flip two-layer (r488/r489) + "
    "SHARDS 1-3 claim watch -> all 4 done -> judge-finalize --wave 2 "
    "(single-shot ledger + 805-cell probe + w2_judge.json) <=10-06; D-06 "
    "closeout 10-07; T-143 post-10-09; moneyflow GM ruling watch | 本地"
    "未达 origin commit 数=0（push 后 fetch 复核）")
with open("round_reports-bm-c.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(line.replace("\n", "\r\n") + "\r\n")
print("round report appended; state/heartbeat written; EPOCH", EPOCH)
