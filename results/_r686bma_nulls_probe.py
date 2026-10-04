import json
repo = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
with open(repo + r"\results\runnable_pool.json", "rb") as f:
    pool = json.loads(f.read().decode('utf-8'))
out = []
for e in pool.get("entries", []):
    if e.get("id", "").endswith("-NULLS") and e.get("status") == "ready":
        out.append({"id": e["id"], "status": e.get("status"), "owner": e.get("owner"),
                    "updated_at": e.get("updated_at"), "runner": e.get("runner"), "runner_args": e.get("runner_args"),
                    "shards": e.get("shards"), "host_gates": e.get("host_gates")})
with open(repo + r"\results\_r686bma_nulls_full.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=True, indent=1)
print("written", len(out), "entries")
# also: any python processes running now (full scan via CIM, python list)
import subprocess
r = subprocess.run(["powershell", "-NoProfile", "-Command",
    "$p = Get-CimInstance Win32_Process -Filter \"Name='python.exe'\"; Write-Output ('PROC_COUNT=' + @($p).Count); $p | ForEach-Object { Write-Output ('PID=' + $_.ProcessId + ' CMD=' + $_.CommandLine.Substring(0, [Math]::Min(160, $_.CommandLine.Length))) }"],
    capture_output=True)
print(r.stdout.decode('utf-8', 'replace')[:3000])
