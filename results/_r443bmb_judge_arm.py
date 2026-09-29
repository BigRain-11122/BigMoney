import json, os, sys, glob
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# pit-103 host_gates pre-flight: Money02 deep-panel ohlcv parquet non-empty
cands = glob.glob("Money02/**/*.parquet", recursive=True)
total = sum(os.path.getsize(p) for p in cands[:5]) if cands else 0
print(f"deep-panel parquet files found: {len(cands)} (sample bytes: {total})")
assert cands, "host_gates FAIL: no parquet under Money02/"
assert total > 0, "host_gates FAIL: parquet empty"

path = "results/runnable_pool.json"
p = json.load(open(path, encoding="utf-8"))
assert not [x for x in p["entries"] if x.get("id") == "TRIAL-LABOR-W11-JUDGE"], "JUDGE exists"

scr = json.load(open("results/trial_labor_w11/w11_screen.json", encoding="utf-8"))
n_nulls = scr.get("n_nulls", 200)
n_distinct = scr.get("n_distinct", 1262)
survivors = scr.get("survivors")
if isinstance(survivors, list):
    n_surv = len(survivors)
else:
    n_surv = survivors
p95 = scr.get("null_p95_line") or scr.get("null_p95") or scr.get("p95_line")
print("screen face: distinct", n_distinct, "nulls", n_nulls, "survivors", n_surv, "p95", p95)

scr_entry = [x for x in p["entries"] if x.get("id") == "TRIAL-LABOR-W11-SCREEN"][0]
scr_entry["status"] = "done"
scr_entry["done_at"] = "2026-09-30T01:03:00+08:00"
scr_entry["result_ref"] = (
    "results/trial_labor_w11/w11_screen.json + w11_screen_cells.csv (1,462/1,462 cells ckpt complete 01:03 "
    "runner pid14156 manual-tick ignition 00:53:27 r443 autofill lineage; finalize landed same round: distinct "
    "1,262 + nulls 200, null p95_line 0.5148 IN prereg sec.5.2 band [0.50,0.52] (W1-W10 lineage 0.5116-0.5196 "
    "continuation), survivors 229/1,262 = 18.15%; RESEARCH FACT: STD segmented survival std10_hi 73/296 24.66% > "
    "none 121/688 17.59% > std20_hi 35/278 12.59% = first STD-axis screen enrichment face (positive 10-day / "
    "negative 20-day asymmetry, r237 probe drift note consistent); MOM continuation oversold 94/452 20.80% vs "
    "none 135/810 16.67% = 1.25x positive-axis (weaker than W10 1.88x); nine-gate interaction survival face "
    "computed; ledger live-head prev read + 1,462 = 350,018 linear append (pit-112 out-dict embed verified); "
    "judge-prep PASS same round; TRIAL-LABOR-W11-JUDGE pool entry submitted same commit (host_gates MSG-1305 "
    "wiring verified, lane_owner=bm-b)"
)
for sh in scr_entry["shards"]:
    sh["status"] = "done"
    sh["done_at"] = "2026-09-30 01:03:00"
    sh["result_ref"] = (
        "results/trial_labor_w11/checkpoint/screen_shard_0of1.jsonl (1,462/1,462 rows complete, cross-kill resume law)"
    )

judge = {
    "id": "TRIAL-LABOR-W11-JUDGE",
    "ticket_ref": (
        "T-2026-09-29-123 WAVE-11 judge slice (CEO O-2026-09-27-2245 thousand-trader order + O-2026-09-27-2250 standing law; "
        "prereg FROZEN bm-b r441 whole-package adoption of the bm-c r237 STD candidate; runner slice-1 built bm-b r442 "
        "selftest 47/47 + r442-close fix-first lineage; GENERATE landed 23:48:32 n=1,262 adopted r443 (r240 law); "
        "SCREEN burned r443 00:53:27 pid14156 manual-tick ignition autofill lineage, finalize landed r443: null p95 "
        "0.5148 IN [0.50,0.52] band, survivors 229/1,262 = 18.15%; RESEARCH FACT: STD segmented enrichment std10_hi "
        "24.66% > none 17.59% > std20_hi 12.59% (positive 10-day/negative 20-day asymmetry, first STD-axis screen face; "
        "MOM oversold 20.80% vs none 16.67% = 1.25x positive-axis continuation weaker than W10 1.88x))"
    ),
    "prereg_ref": (
        "research/TRIAL_LABOR_W11_PREREG.md FROZEN sec.0 TRIAL_LAB_W11_JUDGE (s3 full-judgment batch: batch_trials = "
        "screen survivors 229; dual nulls face; evidence_cutoff 2026-09-22 P-5C frozen binding; fourteen-tuple grammar "
        "sha16 128962592feeb8d3 == FROZEN pin; judged-supply declare window = eleven-source per prereg sec.0 ⑧)"
    ),
    "runner": "scripts/trial_labor_w11.py",
    "runner_args": ["judge", "--shard", "0", "--shards", "1"],
    "lane_owner": "bm-b",
    "priority": 1,
    "status": "ready",
    "entered_at": "2026-09-30T01:07:00+08:00",
    "entered_by": "bm-b r443",
    "data_gates": (
        "GATES ALL GREEN (direct-ready r443, W1-W10-JUDGE lineage): (1) TRIAL-LABOR-W11-SCREEN done -- w11_screen.json "
        "finalize r443 (1462/1462 cells, null p95 0.5148 IN band, survivors 229, ledger 350,018 linear append-verified); "
        "(2) judge-prep PASS -- manifest 48 members, census L/D == frozen, survivors 229, gate meta L/D all faces "
        "incl. STD meta 120-bar-warmup 128open/1383closed decidable 1511 std10-open 147; (3) grammar sha16 "
        "128962592feeb8d3 == FROZEN; (4) host_gates pit-103 MSG-1305: Money02 deep-panel ohlcv parquet non-empty "
        f"verified at submission pre-flight ({len(cands)} parquet files)"
    ),
    "consumer_plan": (
        "TRIAL-LABOR-W11-JUDGE -> judge-finalize (lane-owner separate round work per W5-W10 precedent) -> "
        "w11_judge.json (nine-gate x mom/std interaction disclosure columns per sec.3 incl. STD x MOM adjacency audit "
        "column + W10 real-mom exclusion rows law; G1'v2/G2/DSR/PBO/E[FP] faces) + ledger TRIAL_LAB_W11_JUDGE row "
        "(live-head prev read, pit-112 out-dict embed law) -> s4 intake (D6 binding gate -> STRATEGY_LIBRARY "
        "registration rows + TRIAL-<FAMILY>-<NN> paper onboarding) -> 48h CEO report clock starts at judge landing "
        "(CEO-REPORT-WAVE11) + W12 prereg reference-band feed (screen null p95 0.5148 entered into lineage table)"
    ),
    "shards": [
        {
            "key": "judge-0of1",
            "status": "ready",
            "checkpoint": (
                "results/trial_labor_w11/checkpoint/judge_shard_0of1.jsonl (append-per-cell done-set resume; "
                "dir gitignored per r429)"
            ),
            "note": "single shard; worker_cap() parallelism inside the shard (W8-W10-JUDGE same shape); dual nulls + deep-panel RAM r354 three-sample face",
            "owner": "bm-b",
            "owner_since": "2026-09-30 01:07:00",
        }
    ],
    "worker_class": "self-contained",
    "workers_plan": {
        "workers": "worker_cap() pool BelowNormal (16-core bm-b: <=12; W10-JUDGE 283 survivors ~33min wall; W11-JUDGE 229 survivors lighter; dual-leg x base/x2 CostPatch(2) engine curves per cell + window-grid beat vs passive + regime segments + dual nulls + descriptive faces)",
        "priority": "BelowNormal",
        "note": "hours-scale pool batch per prereg sec.0; RAM r354 three-sample gate (free RAM 6.2GB at arm > 4GB ban threshold); checkpoint every cell resume cross-kill",
    },
}
p["entries"].append(judge)
p["updated_at"] = "2026-09-30T01:07:00+08:00"

with open(path, "w", encoding="utf-8") as f:
    json.dump(p, f, ensure_ascii=False, indent=1)
print("pool updated: SCREEN shard -> done + JUDGE armed; entries:", len(p["entries"]))
