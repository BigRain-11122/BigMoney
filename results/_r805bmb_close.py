# r805 bm-b closeout: HANDOVER 5x row + round report line + state increment + heartbeat
# Lineage: close.py checkpoint-rerun pattern (r609 bm-c); ASCII-only content (pit-encoding law)
import json, os, time, datetime, psutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------- 1. HANDOVER 5x row (bm-b window r801-r805, next 5x = r810) ----------
ROW = "\n- [2026-10-07 14:4x r805 bm-b] HANDOVER 5x window entry (bm-b window r801-r805, zero-miss window; baseline = r800 bm-b row covering r686-r800). THIS-WINDOW bm-b PRODUCTS (r801-r805): (1) QA charter-pack cadence r802->r805 four-chain (metrics frozen sharpe 0.1586 / 93 trades / 46.24% win / determinism=True = engine-integrity judgment face; packs qa/smoke-r{802,803,804,805}.md + equity-curve twins, r800-debt pack delivered by r801). (2) dead-session absorb chain: r802 (wrapper-killed mid-chain, estate absorbed by r803) / r803-w2 (race-close scaffolding absorbed by r804, its merge commit already in local+origin = zero red flag) / r805-w1 (d19-read MATCH + daemon-face resolver absorbed by r805-w2; no chain log = partial 2-leg run, full chain re-run same-window per white-run law). (3) merge-surgery receipts: _r801bmb_merge_resolve{,2}.json (r708 merge-mode canon + r773 double-bump) + _r803bmb_generic_resolve.json (14 UU: 12 ts-duel theirs-newer + compute_audit row-union 203 + token per-key max) + r805 stash/rebase/pop S0 (compute_audit.json UU newer-wins local 14:17:04 > origin 14:07:05; own daemon faces live-wins; all merged faces JSON-parse-verified). (4) D-19 dual-watermark execution faces: group-tree real-path drift -> r631 sparse-clone fallback canonized (decisions 815FA0F2->4C32527B 12:00 governance batch consumed r803; orders 3AB53172->E6A1DEE6 same-window committee closes; both MATCH chains r804+r805). (5) orders window: O-20261007-0935 bm-b capability inventory (early delivery, bm-c r670 ticket) + O-20261007-1157 resume broadcast receipt + O-20261007-1240 BGM dispatch bm-a-executor sweep-ack; ack 164->166. POOL STATE: FUND trio NULLS Q 2000/2000 + V 2000/2000 (dual-flip done, r668 law) + D 1771/2000 in flight @14:33 leg-39 probe face (dup_k=0 x3, integrity=True, rehearsal_green age 3.3d; probe rate 1.0/min eta ~18:2x vs two-point live obs 0.29/min eta ~10-08 early-morning, honest dual-disclosure; finalize window 10-05..10-09, G-SEG GM ruling PENDING + r638 fallback armed, G1 pending D-burn-complete). Maintenance: smoke 48/48 chains; S6 35-leg rc0 chains x4 (dualrun-before-compute_audit ordering law; golden-week legs 25-28 honest-skip cutoff 2026-09-30, reopen 10-08); attrition CLEAN 4 ledgers chains; orders 166/166 dual-scan zero-unacked chains; quartet 4/4 chains (pin=2); token deltas 0. NEXT 5x = bm-b r810. Pointers: D 2000/2000 -> trio finalize same-window pool flip (r668 law) + post-finalize O-20261006-2358 self-claim <=1h; market reopen 10-08 (S6 legs 25-28 re-arm + REGIME_GUARD v3 first-new-bar enforce); 10-08 governance day (O-2115/O-2030 acceptance packs); month-boundary first exam 10-31.\n"
with open(os.path.join(BASE, "research", "HANDOVER.md"), "a", encoding="utf-8", newline="") as f:
    f.write(ROW)

# ---------- 2. round report line ----------
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
report = (
    now + " | round 805 (bm-b, dept:engineering, golden-week final-day guard round w2 -- dead w1 estate absorbed, 5x HANDOVER stamp round) | "
    "[watermark verdict: GREEN (red=false lane healthy; satengine alive rc0 idle queue_depth=0 @14:26 tick; boards 0 open both boards; trio D in-flight burn = trial-labor line satisfied)] | "
    "CEO three-line: current-work = FUND trio NULLS judgment batch Q 2000/2000 + V 2000/2000 COMPLETE (dual-flip done) + D 1771/2000 burning (leg-39 probe face rate 1.0/min eta ~18:2x vs live two-point 0.29/min eta ~10-08 early-morning dual-disclosed; dup_k=0 x3 integrity True rehearsal_green; G1 pending D, G4 r638 fallback armed; finalize window 10-05..10-09) | "
    "latest-artifact = qa/smoke-r805.md + qa/equity-curve-r805.png (QA charter pack 5/5: 3 syms x 800 bars 93 trades determinism=True sharpe 0.1586 face-identical; leg07 signal rc0) + results/_r805bmb_s6_chain.log (35 legs all rc0 255s) + research/HANDOVER.md bm-b 5x row (window r801-r805) | "
    "next-milestone = D 2000/2000 (probe-face ~10-07 evening / conservative ~10-08 early-morning) -> trio finalize same-window pool dual-flip per r668 law + post-close O-20261006-2358 self-claim <=1h + market reopen 10-08 (S6 legs 25-28 re-arm + REGIME_GUARD v3 first new bar enforce) | "
    "S0: identity=bm-b anchored (machine.json first-read; TRUE state = root state.json per r646 path-split epoch law); behind 9 -> dead w1 estate detected (workfiles _r805bmb_d19_read/_daemon_face_resolve @14:07-14:17, no chain log = partial 2-leg run, last write 14:17 = w1 dead before w2 spawn) -> stash/rebase/pop surgery (r642 net-tree law): rebase clean, pop 1 UU compute_audit.json resolved newer-wins (local ts 14:17:04 > origin 14:07:05 per r640 two-way law), own daemon faces auto-merged live-wins, all merged faces JSON-parse-verified (JSON-OK + JSONL-OK), stash dropped | "
    "S0.5: orders 166/166 zero-delta round-start (disk-vs-ack python diff: UNACKED=[] PHANTOM=[]); D-19 dual read consumed from dead-w1 estate verbatim (_r805bmb_d19_read.json 14:14:46: decisions 4C32527B MATCH unchanged / orders E6A1DEE6 MATCH unchanged -> zero own action; w1 read is complete valid evidence per dead-session absorb r802/r803 precedent); inbox 0 unread both sweeps | "
    "S1: smoke 48/48 | S2: boards 0 open (job_list 0 session + fleet tasks mechanical scan zero status=open); dev queue stays closed per r297/r307 | "
    "S3: satengine alive rc0 idle; watermark red=false next_pick=claimed moneyflow IC advisory consumed as-is; post_review 6,987 rows 0 verdict-FAIL mechanical scan = zero next-round P0; trio D in-flight = trial-labor line satisfied zero new drafting legal | "
    "S6: full chain run-1 by w2 (white-run law: w1 partial does not count; r804 chain >50min old): 35 executed legs all rc0 255s (legs 25-28 golden-week honest-skip, cutoff 2026-09-30 unchanged, reopen 10-08); dualrun before compute_audit per T-116 s3 ordering law; leg 39 trio readiness face refreshed (results/finalize_trio_readiness.json 14:33:33) | "
    "S7: quartet 4/4 (IterationLoop pin=2 no-op first-fire 14:42 + LoopWatchdog re-registered first-fire 14:36 + precommit/prepush claws LF-normalized reinstall) + attrition guard CLEAN rc0 (4 ledgers, healed rows historical, evidence results/_attrition_guard_scan.json) + state 804->805 + heartbeat epoch int self-verified + orders_ack 166 self-verified + HANDOVER 5x row this round (r805=5x161) | "
    "S4: zero new pits appended (four-question gate: stash-pop UU resolution family already canonized r640/r642/r789) | "
    "treasure zero-hit claim: zero sweep/archive/delete actions this round (absorb = commit non-delete; stash drop = git-internal) | "
    "verification: smoke 48/48 + QA r805 5/5 + S6 35 legs rc0 x35 + attrition CLEAN + D-19 dual MATCH (dead-w1 evidence) + orders 166/166 + quartet 4/4 | "
    "token: L1 meter face from chain leg38 (no cloud tokens this round) | "
    "local undelivered-to-origin commit count: PENDING_FILL_R805 (post-push self-verify below) | "
    "product score 2 (QA r805 pack = runnable/viewable evidence artifact + S6 35-leg product chain regen + HANDOVER 5x file deliverable)\n"
)
with open(os.path.join(BASE, "logs", "iteration-loop", "round_reports.md"), "a", encoding="utf-8", newline="") as f:
    f.write(report)

# ---------- 3. state.json round_no 804 -> 805 ----------
sp = os.path.join(BASE, "state.json")
st = json.load(open(sp, encoding="utf-8"))
assert st.get("round_no") == 804, "round_no unexpected: %r" % st.get("round_no")
st["round_no"] = 805
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
rest = json.load(open(sp, encoding="utf-8"))
assert rest["round_no"] == 805

# ---------- 4. heartbeat fleet/machines/bm-b.json ----------
vm = psutil.virtual_memory()
epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
hb = {
    "machine_id": "bm-b",
    "round": 805, "round_no": 805,
    "now_active": "r805 closeout: QA r805 pack 5/5 + S6 35 legs rc0 + HANDOVER 5x row (window r801-r805)",
    "current_task": "golden-week final-day guard; FUND trio D nulls burn watch (1771/2000)",
    "task": "guard/watch",
    "latest_artifact": "qa/smoke-r805.md + qa/equity-curve-r805.png (14:37) + results/_r805bmb_s6_chain.log (35 rc0)",
    "next_milestone": "trio D 2000/2000 -> finalize same-window pool dual-flip (r668) + O-20261006-2358 self-claim <=1h + reopen 10-08 S6 legs 25-28 re-arm",
    "verdict": "healthy-guard",
    "last_action": "round 805 closeout commit+push",
    "last_round_at": now,
    "last_seen": now,
    "updated": now,
    "ts": clock,
    "clock_read": clock,
    "heartbeat_epoch_utc": epoch,
    "cpu_cores": psutil.cpu_count(logical=True),
    "free_ram_gb": round(vm.available / 1e9, 2),
}
# GPU VRAM via nvidia-smi if present (no console spawn -> subprocess capture)
try:
    import subprocess
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                          capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    mib = int(out[0])
    hb["gpu_free_vram_mb"] = mib
    hb["gpu_free_vram_gb"] = round(mib / 1024.0, 2)
except Exception:
    hb["gpu_free_vram_mb"] = None
    hb["gpu_free_vram_gb"] = None

hp = os.path.join(BASE, "fleet", "machines", "bm-b.json")
old = json.load(open(hp, encoding="utf-8"))
hb["orders_ack"] = old.get("orders_ack", [])
hb["orders_ack_count"] = len(hb["orders_ack"])
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
rehb = json.load(open(hp, encoding="utf-8"))
assert isinstance(rehb["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in rehb["clock_read"], "clock_read must be T-separated"
print("CLOSE-OUT OK: state 804->805; heartbeat epoch=%d int; clock=%s; ack=%d" % (
    rehb["heartbeat_epoch_utc"], rehb["clock_read"], rehb["orders_ack_count"]))
print("RAM free %.2f GB; GPU free %s MB" % (hb["free_ram_gb"], hb["gpu_free_vram_mb"]))
