"""r860 bm-a: TRIAL-LABOR-W16-JUDGE two-leg pool enrollment (r859 pit law).

Leg 1: Tools/autofill.py submit = orthodox single-write WITH validation
        (duplicate id / O-2355 / consumer_plan / rival rejections).
Leg 2: rollback the submit write, raw-text surgical insert preserving
        pool byte format (CRLF, raw CJK, per-field lines) + json.loads
        round-trip gate (r859 insert2 template, count gate, neighbor
        integrity, updated_at bump).
"""
import json
import subprocess
import sys
import datetime

POOL = r"results/runnable_pool.json"
LANE = r"results/runnable_pool.bm-a.json"
ENTRY_ID = "TRIAL-LABOR-W16-JUDGE"
ENTRY_OUT = r"results/_r860bma_w16judge_entry.json"

ARGS = [
    sys.executable, "Tools/autofill.py", "submit",
    "--id", ENTRY_ID,
    "--runner", "scripts/trial_labor_w16.py",
    "--runner-args", "judge,--shard,0,--shards,1",
    "--shards", "w16-judge-0of1",
    "--priority", "1",
    "--lane-owner", "bm-a",
    "--workers", "26",
    "--wp-priority", "BelowNormal",
    "--wp-note",
    "judge initargs carry BOTH leg panels + per-leg ATR20 + per-leg "
    "sixteen-gate state faces incl resi/cnt = heaviest per-worker state "
    "in the fleet; worker_cap RAM guard applies, free-RAM >=4GB "
    "in-runner gate per r354 three-sample law; BelowNormal = CEO 10% "
    "CPU reserve law",
    "--ticket-ref",
    "T-2026-10-05-172 WAVE-16 judge slice (TRIAL_LABOR_LAW sec.1 "
    "standing supply; prereg FROZEN 2026-10-05 11:1x bm-a r721; "
    "GENERATE done 10-07 19:20:06 candidates n=173 grammar sha16 "
    "ebf15822d2c8472e; SCREEN 373 cells burned autofill 03:32 rc=0 "
    "checkpoint full set; screen-finalize LANDED bm-a r860: null p95 "
    "0.5116 in ref band [0.50,0.52], survivors 40 -- judge physical "
    "dep satisfied; judge-prep PASS bm-a r860 same round: manifest "
    "48/48, census L/D == frozen, sixteen-gate dual-leg meta faithful "
    "incl resi/cnt)",
    "--prereg-ref",
    "research/TRIAL_LABOR_W16_PREREG.md FROZEN sec.0 TRIAL_LAB_W16_JUDGE "
    "(s3 full judgment batch: batch_trials = survivors 40 judged cells; "
    "reform-standard second registered wave per O-1058 five-step chain: "
    "L3 batch-internal BH FDR q<=REFORM_Q_LEVEL 10% + four-dim composite "
    "complete dual gate science_gates.g2_reform_fdr4d + L4 top-N=3/wave "
    "by composite; judge lines import science_gates frozen constants "
    "only (r271 single-canon law); E[FP]=0.05*N_judged; DSR = live chain "
    "head cross-wave no-reset, run-time live read governs = 649,011 "
    "frozen-window read post N2-W15; 48h CEO report clock starts at "
    "judge-finalize)",
    "--consumer-plan",
    "TRIAL-LABOR-W16-JUDGE -> judge-finalize (lane-owner separate round "
    "per W5-W14 precedent) -> w16_judge.json verdict face (reform gate "
    "eligible_reform + composite top-3 dual face) -> s4 intake (D6 "
    "binding gate -> STRATEGY_LIBRARY row + TRIAL-MAXRANK-* paper seat "
    "on eligible only) -> 48h CEO report face + scorecard CEO face; "
    "screen null p95 0.5116 -> W17 prereg reference band",
    "--data-gates",
    "GATES ALL GREEN: (1) standing_no_judge_inflight PASS -- no "
    "TRIAL-LABOR judge entry in flight at enrollment (all W1-W14 judge "
    "entries done; W16-SCREEN shard burn complete checkpoint 373/373, "
    "harvest flip pending daemon tick); (2) judge-prep real-data bm-a "
    "r860 exit 0 PASS: manifest 48 members PASS, census L/D == frozen, "
    "survivors 40, gate meta L/D na-window 199/199, vol meta 519/519 "
    "(leg-L anchors 594calm/518wild), yang/vconf/streak/tstate/amp/mom/"
    "std/rsqr/sumn meta faithful incl slope-split disclosures, "
    "judge_state.json in-repo; (3) screen-finalize LANDED bm-a r860: "
    "null p95 0.5116 in [0.50,0.52] ref band, survivors 40, "
    "w16_screen.json + w16_screen_cells.csv products in-repo; (4) RAM "
    "r354 three-sample at flip time in-runner gate authoritative (bm-a "
    "free ~54GB heartbeat face >= 4GB); burn via autofill pool face per "
    "O-2100 execution-face separation; judge-finalize = bm-a lane "
    "separate round per W5-W14 precedent; 48h CEO report clock starts "
    "at judge-finalize",
    "--data-deps",
    '["results/trial_labor_w16/w16_grammar.json", '
    '"results/trial_labor_w16/w16_screen.json", '
    '"results/trial_labor_w16/judge_state.json"]',
    "--shard-checkpoint",
    "results/trial_labor_w16/checkpoint/judge_shard_0of1.jsonl "
    "(append-per-cell done-set resume, W1/W2 cross-kill law; dir "
    "gitignored per r429; MACHINE-LOCAL = judge-finalize physical dep = "
    "burn machine per W13/W14 single-shard precedent)",
    "--shard-note",
    "single shard W1-W14-JUDGE precedent; 40 judged cells = lightest "
    "judge batch in lineage (W14 77, W13 99); worker_cap() parallelism "
    "inside the shard; dual nulls B/P resampling per prereg sec.0 not "
    "ledger +0",
]

# --- pre-flight: snapshot bytes -----------------------------------------
snap_pool = open(POOL, encoding="utf-8", newline="").read()
snap_lane = open(LANE, encoding="utf-8", newline="").read()
pre = json.loads(snap_pool)
assert len(pre["entries"]) == 407, "pre count gate"

# --- LEG 1: submit (validation + canonical write) ------------------------
print("LEG1: autofill submit ...", flush=True)
r = subprocess.run(ARGS, capture_output=True, text=True,
                    encoding="utf-8", errors="replace")
print("rc=", r.returncode)
print((r.stdout or "")[-1500:])
if r.stderr:
    print("STDERR tail:", r.stderr[-800:])
if r.returncode != 0:
    print("SUBMIT FAILED -> no rollback needed, abort")
    sys.exit(1)

# --- extract validated entry from submit's write --------------------------
d = json.loads(open(POOL, encoding="utf-8").read())
assert len(d["entries"]) == 408, "post-submit count gate"
entry = None
for e in d["entries"]:
    if e.get("id") == ENTRY_ID:
        entry = e
        break
assert entry is not None, "submitted entry not found"
with open(ENTRY_OUT, "w", encoding="utf-8", newline="") as fh:
    json.dump(entry, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("extracted entry ->", ENTRY_OUT, "| fields:", len(entry))

# --- rollback the submit write (snapshot restore) --------------------------
with open(POOL, "w", encoding="utf-8", newline="") as fh:
    fh.write(snap_pool)
with open(LANE, "w", encoding="utf-8", newline="") as fh:
    fh.write(snap_lane)
chk = json.loads(open(POOL, encoding="utf-8").read())
assert len(chk["entries"]) == 407, "rollback count gate"
print("rollback OK (407)")

# --- LEG 2: raw-text surgical insert ---------------------------------------
raw0 = open(POOL, encoding="utf-8", newline="").read()


def ser(v):
    return json.dumps(v, ensure_ascii=False)


lines = ["   " + ser(k) + ": " + ser(v) + "," for k, v in entry.items()]
lines[-1] = lines[-1].rstrip(",")
block = "  {\r\n" + "\r\n".join(lines) + "\r\n  }"

tail_anchor = "\r\n  }\r\n ]\r\n}"
assert raw0.endswith(tail_anchor) and raw0.count(tail_anchor) == 1, \
    "tail anchor unique gate"
new = (raw0[:-len(tail_anchor)]
       + "\r\n  },\r\n" + block
       + "\r\n ]\r\n}")

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
import re
m = re.search(r'"updated_at": "([^"]+)"', new)
assert m, "updated_at field present"
new = new[:m.start(1)] + now + new[m.end(1):]

# round-trip parse gate (r859 two-leg law: written string MUST re-parse)
d2 = json.loads(new)
assert len(d2["entries"]) == 408, "insert count gate"
e2 = next(x for x in d2["entries"] if x.get("id") == ENTRY_ID)
assert e2["status"] == "ready" and e2["shards"][0]["key"] == "w16-judge-0of1"
assert e2["shards"][0]["status"] == "ready" and e2["shards"][0]["owner"] is None
assert d2["entries"][0]["id"] == chk["entries"][0]["id"], "neighbor head"
assert d2["entries"][405]["id"] == chk["entries"][405]["id"], "neighbor 405"
assert d2["entries"][406]["id"] == "TRIAL-LABOR-W16-SCREEN", "neighbor tail-1"

with open(POOL, "w", encoding="utf-8", newline="") as fh:
    fh.write(new)

# post-write re-read validation (r629 60s-window law)
d3 = json.loads(open(POOL, encoding="utf-8").read())
assert len(d3["entries"]) == 408
print("LEG2 INSERTED OK | entries=408 | updated_at", now)
print("receipt: id=%s status=%s shard=%s workers=%s" % (
    e2["id"], e2["status"], e2["shards"][0]["key"],
    e2.get("workers_plan", {}).get("workers")))
