# r683 (bm-b): W3 judge shard-1 burn health watch (observation-only, no pool action)
# r659/r661 law: pid liveness via CSV full-scan + CIM full-scan dual-form (never single /FI form)
import json, os, subprocess, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARD = os.path.join(ROOT, "results", "mass_trial", "w3_judge_shard_1of4.jsonl")

out = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}
if os.path.exists(SHARD):
    st = os.stat(SHARD)
    out["size_b"] = st.st_size
    out["mtime_age_sec"] = round(time.time() - st.st_mtime, 1)
    with open(SHARD, "rb") as f:
        data = f.read()
    lines = [ln for ln in data.split(b"\n") if ln.strip()]
    out["rows"] = len(lines)
    try:
        last = json.loads(lines[-1])
        out["last_row"] = {k: last.get(k) for k in ("chunk", "ci", "k_lo", "done_k", "rows", "ts", "elapsed_s") if k in last}
        out["last_keys_sample"] = sorted(last.keys())[:12]
    except Exception as e:
        out["last_row_err"] = repr(e)
        out["last_line_head"] = lines[-1][:200].decode("utf-8", "replace")
else:
    out["missing"] = True

# dual-form pid liveness for known shard-1 pid 21200 (pool_core_samples 17:13:41)
PIDS = [21200]
r = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True)
csv_alive = set()
for row in r.stdout.decode("utf-8", "replace").splitlines():
    parts = [p.strip('"') for p in row.split('","')]
    if len(parts) >= 2 and parts[1].isdigit():
        csv_alive.add(int(parts[1]))
out["csv_form_alive"] = {p: (p in csv_alive) for p in PIDS}

try:
    r2 = subprocess.run(["powershell", "-NoProfile", "-Command",
                         "Get-CimInstance Win32_Process | Select-Object ProcessId,Name | ConvertTo-Json -Compress"],
                        capture_output=True)
    cim = json.loads(r2.stdout.decode("utf-8", "replace"))
    if isinstance(cim, dict):
        cim = [cim]
    cim_pids = {int(x["ProcessId"]) for x in cim}
    out["cim_form_alive"] = {p: (p in cim_pids) for p in PIDS}
except Exception as e:
    out["cim_err"] = repr(e)

print(json.dumps(out, ensure_ascii=True, indent=1))
