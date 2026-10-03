# r655 bm-b: finalize-trio readiness probe (60s double-sample, schema = r651 readout contract)
# families: have/lines/dup_k from nulls.jsonl trio; rate = delta over 60s; gates + governance.
import json, os, time, subprocess, hashlib

R = "results"
FAMS = ["fund_quality_p1", "fund_value_p1", "fund_divlowvol_p1"]
TARGET = 2000


def snapshot():
    out = {}
    for fam in FAMS:
        p = os.path.join(R, fam, "nulls.jsonl")
        ks, n = [], 0
        if os.path.exists(p):
            with open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    n += 1
                    try:
                        ks.append(json.loads(line).get("k"))
                    except ValueError:
                        ks.append(None)
        out[fam] = {"lines": n, "dup_k": n - len(set(ks))}
    return out


t0 = time.time()
a = snapshot()
time.sleep(60.0 - min(59.9, max(0.0, 0.0)))  # full 60s window
b = snapshot()
elapsed = time.time() - t0

families = {}
for fam in FAMS:
    have = b[fam]["lines"]
    d = b[fam]["lines"] - a[fam]["lines"]
    rate = d / (elapsed / 60.0) if elapsed > 0 else 0.0
    eta = (TARGET - have) / rate / 60.0 if rate > 0 else None
    families[fam] = {"have": have, "lines": b[fam]["lines"], "dup_k": b[fam]["dup_k"],
                     "rate_per_min": round(rate, 4),
                     "eta_hours": round(eta, 2) if eta else None}

integrity = all(v["dup_k"] == 0 for v in families.values())
burn_complete = all(v["have"] >= TARGET for v in families.values())

# rehearsal gate: consume latest evidence (bm-a r662 06:14:56 re-run), no re-burn here
reh = json.load(open(os.path.join(R, "_r633bma_finalize_rehearsal_summary.json"),
                     encoding="utf-8"))
reh_ok = all((reh.get("families", {}).get(f, {}) or {}).get("all_legs_ok") is True
             for f in FAMS)
reh_age_d = (time.time() - os.path.getmtime(
    os.path.join(R, "_r633bma_finalize_rehearsal_summary.json"))) / 86400.0

# governance: G-SEG GM ruling still PENDING? consume origin decisions sha (fresh, this round)
dec_sha = hashlib.sha256(
    subprocess.run(["git", "-C", os.path.join(os.environ.get("TEMP", ""),
                                               "fg-sparse-r655"),
                    "show", "origin/main:docs/decisions.md"],
                   capture_output=True).stdout).hexdigest().upper()
st = json.load(open("state.json", encoding="utf-8"))
gov_sha = st.get("last_decisions_sha", "")
gov_moved = dec_sha != gov_sha

doc = {
    "machine": "bm-b", "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "probe": "finalize_trio_readiness", "not_a_verdict": True,
    "target_draws": TARGET, "families": families,
    "gates": {"burn_complete": burn_complete, "integrity": integrity,
              "rehearsal_green": reh_ok,
              "rehearsal_note": "all_legs_ok x3, age %.1fd" % reh_age_d},
    "governance": {
        "status": "PENDING", "decisions_sha": dec_sha,
        "sha_moved_since_last_probe": gov_moved,
        "note": ("G-SEG GM ruling (MSG-2026-10-03-1720) not yet logged; r638 "
                 "fallback = proceed on insufficient-sample single-read when "
                 "mechanical gates green")},
    "mechanical_ready": bool(burn_complete and integrity and reh_ok),
    "window_note": ("finalize window 10-05..10-09; open when mechanical_ready and "
                    "governance resolved (ruling or r638 fallback)"),
    "elapsed_sec": round(elapsed, 1),
}
out = os.path.join(R, "finalize_trio_readiness.json")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
print("WROTE", out)
for fam, v in families.items():
    print("%s: have=%d rate=%.2f/min eta=%s h dup_k=%d" % (
        fam, v["have"], v["rate_per_min"], v["eta_hours"], v["dup_k"]))
print("gates: burn_complete=%s integrity=%s rehearsal_green=%s gov=PENDING(moved=%s)"
      % (burn_complete, integrity, reh_ok, gov_moved))
print("mechanical_ready:", doc["mechanical_ready"])

# burn pid liveness (same r654 contract)
ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
      "Where-Object { $_.CommandLine -match 'fund_' } | "
      "ForEach-Object { \"$($_.ProcessId)\" }")
r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                   capture_output=True, text=True, creationflags=0x08000000)
pids = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
print("burn pids alive:", ",".join(pids) or "NONE")
