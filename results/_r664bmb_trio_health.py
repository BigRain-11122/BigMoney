# -*- coding: utf-8 -*-
# r664 bm-b trio NULLS burn health probe (watch face, r663 pattern reuse):
# - nulls.jsonl line counts + dup-key check per family (r660 dup_k=0 baseline)
# - burner liveness via CIM Win32_Process FULL SCAN + cmdline match (r659/r661
#   law: no tasklist /FI single-pid filter; full-scan form only; watch face
#   no kill/respawn decision -> single form acceptable, keepalive claim refresh
#   is the independent second evidence)
import json, os, subprocess, io

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {"probe": "r664bmb_trio_health", "machine": "bm-b"}

FAMS = {
    "FUND-VALUE-P1-NULLS": os.path.join(REPO, "results", "fund_value_p1", "nulls.jsonl"),
    "FUND-QUALITY-P1-NULLS": os.path.join(REPO, "results", "fund_quality_p1", "nulls.jsonl"),
    "FUND-DIVLOWVOL-P1-NULLS": os.path.join(REPO, "results", "fund_divlowvol_p1", "nulls.jsonl"),
}

def fam_stats(path):
    keys = set()
    n = 0
    with io.open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n += 1
            try:
                d = json.loads(line)
                keys.add(str(d.get("k", d.get("key", d.get("sig", n)))))
            except Exception:
                keys.add("unparsed:" + str(n))
    return n, len(keys)

def datetime_mtime(p):
    import datetime
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec="seconds")

for fam, path in FAMS.items():
    try:
        n, k = fam_stats(path)
        out[fam] = {"lines": n, "keys": k, "dup_k": n - k,
                    "mtime": datetime_mtime(path)}
    except Exception as e:
        out[fam] = {"error": str(e)[:200]}

# burner liveness: CIM full scan (subprocess, not single-pid filter)
p = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'fund_(value|quality|divlowvol)_p1' } | "
     "Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],
    capture_output=True)
try:
    procs = json.loads(p.stdout.decode("utf-8", "replace") or "[]")
    if isinstance(procs, dict):
        procs = [procs]
    burns = []
    for pr in procs:
        cl = str(pr.get("CommandLine", ""))[:120]
        burns.append({"pid": pr.get("ProcessId"), "cmd": cl})
    out["burners"] = burns
    out["burner_n"] = len(burns)
except Exception as e:
    out["burners_error"] = str(e)[:200] + " raw:" + p.stdout.decode("utf-8", "replace")[-200:]

with io.open(os.path.join(REPO, "results", "_r664bmb_trio_health.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps({k: (v if k != "burners" else str(len(v)) + " procs") for k, v in out.items()}, ensure_ascii=False)[:600])
