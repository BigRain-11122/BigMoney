# r329 bm-a: repull liveness probe + progress locate (next-round W2-A takeover fire evidence)
import json, re, io, os, subprocess, glob, time

out = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "machine": "bm-a", "round": 329}

# process liveness
try:
    p = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-Process -Id 47148 | Select-Object Id,CPU,StartTime | ConvertTo-Json -Compress"],
                       capture_output=True, text=True)
    out["proc_47148"] = json.loads(p.stdout) if p.stdout.strip() else None
except Exception as e:
    out["proc_47148"] = "probe-error: %s" % e

# progress: scan update_sina_mf.py for progress/state paths
src = io.open("scripts/update_sina_mf.py", encoding="utf-8").read()
paths = sorted(set(re.findall(r'["\']((?:results|data)/[A-Za-z0-9_/\.]*(?:progress|refresh|checkpoint)[A-Za-z0-9_/\.]*)["\']', src)))
out["script_state_paths"] = paths
prog_found = {}
for pth in paths:
    if os.path.exists(pth):
        raw = io.open(pth, "rb").read()
        try:
            d = json.loads(raw.decode("utf-8"))
            prog_found[pth] = {k: d[k] for k in list(d)[:12]}
        except Exception:
            prog_found[pth] = {"bytes": len(raw), "mtime": time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(pth)))}
out["progress_files"] = prog_found

# panel dir file count + freshest mtime
for d in glob.glob("data/sina_mf*") + glob.glob("data/*sina*"):
    if os.path.isdir(d):
        fs = glob.glob(os.path.join(d, "*"))
        out.setdefault("panel_dirs", []).append({"dir": d, "n_files": len(fs),
                                                 "newest": time.strftime("%H:%M:%S", time.localtime(max(os.path.getmtime(f) for f in fs))) if fs else None})

io.open("results/_r329bma_repull_probe.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out, ensure_ascii=False, indent=1)[:1800])
