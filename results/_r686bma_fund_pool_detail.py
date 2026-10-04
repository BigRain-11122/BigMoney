import json, os, subprocess
repo = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
with open(repo + r"\results\runnable_pool.json", "rb") as f:
    pool = json.loads(f.read().decode('utf-8'))
for e in pool.get("entries", []):
    if e.get("id", "").startswith("FUND-"):
        print("===", e.get("id"), "status=", e.get("status"))
        for k, v in e.items():
            if k in ("id", "status"):
                continue
            s = json.dumps(v, ensure_ascii=True)
            print("  ", k, "=", s[:400])
# check for running python processes related to fund nulls
r = subprocess.run(["powershell", "-NoProfile", "-Command",
    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Select-Object ProcessId, CommandLine | ConvertTo-Json -Compress"],
    capture_output=True)
out = r.stdout.decode('utf-8', 'replace')
try:
    procs = json.loads(out)
    if isinstance(procs, dict):
        procs = [procs]
    fund_procs = [p for p in procs if p.get("CommandLine") and ("fund" in p["CommandLine"].lower() or "nulls" in p["CommandLine"].lower())]
    print("python procs total:", len(procs), "fund/nulls related:", len(fund_procs))
    for p in fund_procs:
        print("  PID", p["ProcessId"], p["CommandLine"][:200])
except Exception as ex:
    print("proc parse fail:", ex)
    print(out[:500])
