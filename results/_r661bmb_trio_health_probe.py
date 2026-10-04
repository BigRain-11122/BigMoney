# -*- coding: utf-8 -*-
# r661 bm-b fund-trio NULLS burn health probe (r659/r661 dual-form liveness law)
import json, io, os, subprocess, re, time

def nulls_progress(path):
    # tail-read k values from append-only jsonl
    last_k = None; n = 0; mtime = None
    try:
        mtime = time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(path)))
        with io.open(path, "rb") as f:
            f.seek(0, 2); size = f.tell()
            f.seek(max(0, size - 4000))
            tail = f.read().decode("utf-8", "replace")
        for line in tail.splitlines():
            line = line.strip()
            if line.startswith("{"):
                n += 1
                m = re.search(r'"k"\s*:\s*(\d+)', line)
                if m:
                    last_k = int(m.group(1))
    except FileNotFoundError:
        return {"missing": True}
    return {"last_k": last_k, "tail_lines": n, "mtime": mtime}

out = {"probe": "fund_trio_burn_health", "machine": "bm-b", "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
for fam in ("value", "quality", "divlowvol"):
    p = "results/fund_%s_p1/nulls.jsonl" % fam
    out[fam] = nulls_progress(p)

# liveness form 2: full CSV scan (not single-pid /FI filter per r659)
p = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True)
rows = p.stdout.decode("utf-8", "replace").splitlines()
python_procs = []
for r in rows[1:]:
    cols = r.replace('"', "").split(",")
    if len(cols) > 4:
        name, pid = cols[0].lower(), cols[1]
        if "python" in name:
            python_procs.append((name, pid))
# form 3: CIM command lines for burn runners
p2 = subprocess.run(["powershell", "-NoProfile", "-Command",
                     "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | "
                     "Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],
                    capture_output=True)
try:
    cl = json.loads(p2.stdout.decode("utf-8", "replace") or "[]")
    if isinstance(cl, dict):
        cl = [cl]
    burners = [c for c in cl if c.get("CommandLine") and re.search(r"fund_(value|quality|divlowvol)_p1", c["CommandLine"])]
    out["burn_runner_procs"] = [(c["ProcessId"], c["CommandLine"][:100]) for c in burners]
except Exception as e:
    out["cim_err"] = str(e)[:200]
out["python_proc_count"] = len(python_procs)

with io.open("results/_r661bmb_trio_health.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False)[:600])
