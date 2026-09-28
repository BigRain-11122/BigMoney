# r386-cont bm-b pool flips:
# (a) CENSUS-FUS-S2-W2B entry+shard done-flip (burn+finalize landed 13:43,
#     products committed 918f04ce by orphan r386 session; orphan bookkeeping);
# (b) TRIAL-LABOR-W2-JUDGE shard done-flip only (burn complete 404/404
#     14:01:54, checkpoint+log evidence; judge-finalize detached in-flight
#     pid 23800 -- entry done-flip deferred to finalize receipt);
# (c) TRIAL-LABOR-W1-JUDGE waiting->ready flip, gates re-verified fresh:
#     (1) judge-prep judge_state.json t18 PASS 48-member + census==frozen
#     (2) screen survivors non-empty (3) RAM 3-sample >=4GB >30s (r354).
#     Auto-flip candidate per r357 defer note "next bm-b round post-W2B".
import json, os, time, datetime, subprocess

POOL = "results/runnable_pool.json"
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ram_gb():
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
        capture_output=True, text=True).stdout.strip()
    return round(int(out) / 1024 / 1024, 2)

# ---- gate checks fresh (W1) ----
js = json.load(open("results/trial_labor_w1/judge_state.json", encoding="utf-8"))
gm = js.get("g_manifest") or {}
assert gm.get("verdict") == "PASS", gm.get("verdict")
assert gm.get("manifest_members") == 48, gm.get("manifest_members")
cf = js.get("census_frozen") or {}
assert cf == {"L": {"6m": 1253, "12m": 1127, "24m": 875},
              "D": {"6m": 3104, "12m": 2978, "24m": 2726}}, cf
scr = json.load(open("results/trial_labor_w1/w1_screen.json", encoding="utf-8"))
sv = scr.get("survivors")
n_sv = len(sv) if isinstance(sv, list) else int(sv or 0)
assert n_sv == 149, n_sv
print("gate1 judge-prep PASS (t18 48-member, census==frozen) | gate2 survivors =", n_sv)

# gate3: RAM 3-sample across >30s (r354)
r1, t1 = ram_gb(), datetime.datetime.now().strftime("%H:%M:%S")
time.sleep(16)
r2, t2 = ram_gb(), datetime.datetime.now().strftime("%H:%M:%S")
time.sleep(16)
r3, t3 = ram_gb(), datetime.datetime.now().strftime("%H:%M:%S")
samples = [(r1, t1), (r2, t2), (r3, t3)]
assert all(v >= 4.0 for v, _ in samples), samples
print("gate3 RAM 3-sample PASS:", samples)

# ---- burn-completion evidence (W2 shard) ----
ckpt = "results/trial_labor_w2/checkpoint/judge_shard_0of1.jsonl"
n_rows = sum(1 for ln in open(ckpt, encoding="utf-8") if ln.strip())
with open(ckpt, encoding="utf-8") as fh:
    ids = {json.loads(ln)["cell_id"] for ln in fh if ln.strip()}
w2scr = json.load(open("results/trial_labor_w2/w2_screen.json", encoding="utf-8"))
w2_sv = w2scr.get("survivors")
w2_n = len(w2_sv) if isinstance(w2_sv, list) else int(w2_sv)
missing = [c for c in (w2_sv if isinstance(w2_sv, list) else [])
           if f"JUDGE|{c}" not in ids]
assert w2_n == 404 and n_rows >= 404 and not missing, (w2_n, n_rows, missing[:3])
print("W2 shard burn evidence: checkpoint rows =", n_rows, "/ survivors =", w2_n)

# ---- flips ----
pool = json.load(open(POOL, encoding="utf-8-sig"))
for e in pool["entries"]:
    if e["id"] == "CENSUS-FUS-S2-W2B":
        assert e["status"] in ("ready", "running"), e["status"]
        e["status"] = "done"
        e["done_at"] = now
        e["done_note"] = (
            "r386-cont bm-b done-flip (orphan r386 session died post-push pre-"
            "bookkeeping): burn complete 2026-09-28 13:43:11 (5220/5220 combos, "
            "runner-[done] receipt), finalize products committed 918f04ce "
            "(w2b_results/w2b_summary/w2b_nulls/w2b_cells/w2b_top_matrices). "
            "Crash-fuse 13:50 CONFIRMx2 = stale-crash-trace face (r382 law: "
            "runner dead + pool not yet flipped by dying session), relaunch "
            "refusal lawful no-harm."
        )
        for sh in e["shards"]:
            assert sh["key"] == "censusw2b-0of1"
            sh["status"] = "done"
            sh["done_at"] = now
            sh["result_ref"] = "results/census_fusion_s2/w2b_results.json (chain 918f04ce)"
    elif e["id"] == "TRIAL-LABOR-W2-JUDGE":
        assert e["status"] == "ready", e["status"]
        for sh in e["shards"]:
            assert sh["key"] == "judge-0of1" and sh["status"] == "waiting"
            sh["status"] = "done"
            sh["done_at"] = now
            sh["result_ref"] = (ckpt + " (404/404 cells, log judge-shard "
                                "complete 14:01:54, autofill claim 53cc84ab)")
        e["note"] = (
            "r386-cont bm-b: burn complete 404/404 @14:01:54 (shard done-flip "
            "this round); judge-finalize detached in-flight pid 23800 "
            "(14:13:55, log logs/w2_judge_finalize_r386.log) -- entry done-flip "
            "deferred to finalize receipt (w2_judge.json). Siblings stay "
            "waiting single-burn no-stack; W1-JUDGE flipped ready this round "
            "as next burn."
        )
    elif e["id"] == "TRIAL-LABOR-W1-JUDGE":
        assert e["status"] == "waiting", e["status"]
        e["status"] = "ready"
        e["ready_at"] = now
        e["ready_note"] = (
            "r386-cont bm-b flip, gates discharged fresh: (1) judge-prep PASS "
            "results/trial_labor_w1/judge_state.json (t18 manifest PASS "
            "48-member + census L/D==frozen L{1253,1127,875}/"
            "D{3104,2978,2726}; r357 verified, re-verified at flip); "
            f"(2) screen-finalize survivors={n_sv} non-empty; (3) RAM 3-sample "
            f"{r1}/{r2}/{r3} GB >=4GB across >30s r354 law (samples {t1}/{t2}/{t3}; "
            "census W2B finalized 13:43 + W2-JUDGE burn complete 14:01:54 = "
            "RAM released). Auto-flip candidate per r357 defer note 'next "
            "bm-b round post-W2B'. Sibling ordering: MASS x4/V2-P1/W3/W4-JUDGE "
            "stay waiting (single-burn no-stack law, anti-OOM 23.9GB box)."
        )
        for sh in e["shards"]:
            assert sh["key"] == "judge-0of1" and sh["status"] == "waiting"
            sh["status"] = "ready"
pool["updated_at"] = now

tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
os.replace(tmp, POOL)

pool2 = json.load(open(POOL, encoding="utf-8-sig"))
for eid in ("CENSUS-FUS-S2-W2B", "TRIAL-LABOR-W2-JUDGE", "TRIAL-LABOR-W1-JUDGE"):
    e2 = [x for x in pool2["entries"] if x["id"] == eid][0]
    sh = e2["shards"][0]
    print(f"flip OK {eid}: entry={e2['status']} shard={sh['status']}")
