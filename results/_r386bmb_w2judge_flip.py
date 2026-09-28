# TRIAL-LABOR-W2-JUDGE waiting->ready flip (r386 bm-b), r201 flip-script pattern.
# Gates per entry data_gates (W1-JUDGE r346 precedent): (1) screen-finalize
# survivors non-empty (2) judge-prep judge_state.json t18 manifest PASS +
# census==frozen (3) free RAM >=4GB three-sample across >=30s (r354 law).
import json, os, datetime

POOL = "results/runnable_pool.json"
RAM_SAMPLES = [(13.23, "13:48:31"), (12.55, "13:49:10"), (None, None)]  # 3rd filled below
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# gate 3 (r354): fresh sample here = 3rd, spanning sample1..sample3 > 30s
os_ram = os.popen("powershell -NoProfile -Command "
                 "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory").read()
ram3 = round(int(os_ram.strip()) / 1024 / 1024, 2)
RAM_SAMPLES[2] = (ram3, now[-8:])
assert all(v >= 4.0 for v, _ in RAM_SAMPLES), RAM_SAMPLES
print("gate3 RAM 3-sample PASS:", RAM_SAMPLES)

# gate 1: screen-finalize survivors non-empty
scr = json.load(open("results/trial_labor_w2/w2_screen.json", encoding="utf-8"))
survivors = scr.get("survivors")
n = len(survivors) if isinstance(survivors, list) else int(survivors or 0)
assert n > 0, "w2_screen.json survivors empty"
print("gate1 screen-finalize PASS: survivors =", n)

# gate 2: judge_state.json g_manifest PASS + grammar sha16 anchor + census==frozen
js = json.load(open("results/trial_labor_w2/judge_state.json", encoding="utf-8"))
gm = js.get("g_manifest") or {}
assert gm.get("verdict") == "PASS", gm.get("verdict")
assert gm.get("manifest_members") == 48, gm.get("manifest_members")
assert str(js.get("grammar_sha256", "")).startswith("1dd3d95792395cec"), js.get("grammar_sha256")
cf = js.get("census_frozen") or {}
expect_cf = {"L": {"6m": 1253, "12m": 1127, "24m": 875},
             "D": {"6m": 3104, "12m": 2978, "24m": 2726}}
assert cf == expect_cf, cf
print("gate2 judge-prep PASS: t18 g_manifest verdict =", gm.get("verdict"),
      "| grammar sha16 =", js.get("grammar_sha256")[:16], "| census_frozen L/D == frozen")

# flip
pool = json.load(open(POOL, encoding="utf-8-sig"))
for e in pool["entries"]:
    if e["id"] == "TRIAL-LABOR-W2-JUDGE":
        assert e["status"] == "waiting", e["status"]
        e["status"] = "ready"
        e["ready_at"] = now
        e["ready_note"] = (
            "r386 bm-b flip, ALL THREE gates discharged: (1) screen-finalize "
            f"survivors={n} non-empty (w2_screen.json 07:09:20); (2) judge-prep PASS "
            "judge_state.json 07:11:36 (t18 manifest PASS 48-member + census L/D==frozen "
            "L{1253,1127,875}/D{3104,2978,2726}, r365 gate-2 receipt); (3) RAM 3-sample "
            f"{RAM_SAMPLES[0][0]}/{RAM_SAMPLES[1][0]}/{ram3} GB >=4GB across >30s r354 law "
            "(census W2B finalized 13:43:11 runner-[done] receipt cells=5220 -> RAM released). "
            "Flip executor = bm-b deep-panel round per entry workers_plan note + W1-JUDGE "
            "r357 defer precedent. Sibling ordering: W1-JUDGE/MASS-JUDGE-x4/V2-P1 stay "
            "waiting this round (single judge burn ~7-8GB no-stack law, anti-OOM "
            "dual-company 23.9GB box)."
        )
        for sh in e["shards"]:
            assert sh["key"] == "judge-0of1"
            assert sh["status"] == "waiting"
            sh["status"] = "ready"
        break
else:
    raise SystemExit("entry not found")

tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
os.replace(tmp, POOL)
pool2 = json.load(open(POOL, encoding="utf-8-sig"))
e2 = [x for x in pool2["entries"] if x["id"] == "TRIAL-LABOR-W2-JUDGE"][0]
print("flip OK:", e2["status"], e2["ready_at"], "| shard:", e2["shards"][0]["status"])
