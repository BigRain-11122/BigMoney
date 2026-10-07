# r825 bm-a rebase-conflict resolver (SKILL.md bigmoney-conflict-resolve recipes;
# _r824bma_resolve.py lineage). UU set 11 faces:
#  - fleet/orders/O-20261007-1157-bm-c.md : receipt union (origin has bm-b receipt,
#    local has bm-a receipt -> take origin blob + fill bm-a line; both kept)
#  - results/compute_audit.json + results/token_usage.json : ALL_FACES twins ->
#    scripts/merge_lane_views.py resolve (canon tool, separate invocation)
#  - results/runnable_pool.json : claim-refresh race, BOTH differing shard fields
#    (W14-SCREEN owner bm-b@13:22:36 vs stale bm-c@13:16:08; FUND-DIVLOWVOL
#    bm-b@13:22:08 vs @13:08:08) favor origin -> max-merge = take origin side whole
#    (id sets identical 404/404, only those 2 shard fields differ, verified)
#  - 7 snapshot regen faces : deep-ts probe, newer wins (r311/D-09 law)
# Stage law (r351): :2: = origin side (rebase), :3: = local side.
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def stage_bytes(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage read fail {path}:{stage}: {r.stderr.decode('utf-8','replace')[:200]}")
    return r.stdout


def deep_ts(obj, _depth=0):
    if _depth > 6:
        return ""
    if isinstance(obj, dict):
        best = ""
        for k, v in obj.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if nk.startswith(("ts", "generated", "updated", "scannedat", "donets", "lastscan")) \
               and isinstance(v, str) and re.match(r"^20\d{2}-", v):
                if v > best:
                    best = v
            sub = deep_ts(v, _depth + 1)
            if sub > best:
                best = sub
        return best
    if isinstance(obj, list):
        best = ""
        for it in obj:
            sub = deep_ts(it, _depth + 1)
            if sub > best:
                best = sub
        return best
    return ""


def write(path, data):
    with open(path, "wb") as f:
        f.write(data)


# --- 1. pool: origin side whole (max-merge verified favors origin) ----------
pool_o = stage_bytes("results/runnable_pool.json", 2)
pool_l = json.loads(stage_bytes("results/runnable_pool.json", 3))
pool_oj = json.loads(pool_o)
oe = {e["id"]: e for e in pool_oj.get("entries", [])}
le = {e["id"]: e for e in pool_l.get("entries", [])}
assert set(oe) == set(le) and len(oe) == 404, (len(oe), len(le))
diffs = [k for k in oe if oe[k] != le[k]]
assert sorted(diffs) == ["FUND-DIVLOWVOL-P1-NULLS", "TRIAL-LABOR-W14-SCREEN"], diffs
write("results/runnable_pool.json", pool_o)
json.loads(pool_o)
print("pool: origin side whole (2 claim-refresh diffs -> newer origin claims kept)")

# --- 2. O-1157 receipt union: origin blob + bm-a receipt fill ---------------
o1157 = stage_bytes("fleet/orders/O-20261007-1157-bm-c.md", 2).decode("utf-8")
l1157 = stage_bytes("fleet/orders/O-20261007-1157-bm-c.md", 3).decode("utf-8")
assert "- [x] bm-b resume 确认" in o1157, "origin side missing bm-b receipt"
assert "- [ ] bm-a resume 确认：[via bm-a r___]" in o1157, "origin side bm-a slot not vacant"
assert "- [x] bm-a resume 确认" in l1157, "local side missing bm-a receipt"
needle = "- [ ] bm-a resume 确认：[via bm-a r___]"
new = ("- [x] bm-a resume 确认：维持全力（本机未停·满载运转中：IterationLoop r825 在位"
       "+SatEngine alive rc0+autofill/dispatcher 活面 churn 实证）[via bm-a r825]")
assert o1157.count(needle) == 1
merged = o1157.replace(needle, new)
write("fleet/orders/O-20261007-1157-bm-c.md", merged.encode("utf-8"))
assert "- [x] bm-a resume" in merged and "- [x] bm-b resume" in merged and "- [x] bm-c 循环班 ack" in merged
print("O-1157: receipt union OK (bm-a + bm-b + bm-c all three receipts present)")

# --- 3. snapshots: deep-ts probe, newer wins ---------------------------------
SNAPSHOTS = [
    "results/_attrition_guard_scan.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]
for p in SNAPSHOTS:
    b2 = stage_bytes(p, 2)
    b3 = stage_bytes(p, 3)
    try:
        t2 = deep_ts(json.loads(b2))
        t3 = deep_ts(json.loads(b3))
    except Exception:
        t2 = t3 = ""
    side = 2 if t2 >= t3 else 3
    print(f"  {p}: origin_ts={t2!r} local_ts={t3!r} -> side {side}")
    write(p, b2 if side == 2 else b3)

# --- 4. ALL_FACES twins via canon tool (separate process) -------------------
for face in ("results/compute_audit.json", "results/token_usage.json"):
    r = subprocess.run(["python", "-X", "utf8", "scripts\\merge_lane_views.py",
                        "resolve", face], capture_output=True, text=True)
    print(" ", face, "->", (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else f"rc={r.returncode}")
    assert r.returncode == 0, (face, r.stderr[:300])

# --- verify: every written json parses ---------------------------------------
for p in (["results/runnable_pool.json"] + SNAPSHOTS
          + ["results/compute_audit.json", "results/token_usage.json"]):
    json.load(open(p, encoding="utf-8"))
print("ALL PARSE-VERIFIED (pool whole + union receipt + 7 snapshots + 2 twins)")
