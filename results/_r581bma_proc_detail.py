import subprocess, json, datetime
out = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in @(103612,78424,78900,41168) } | "
     "Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],
    capture_output=True).stdout.decode("utf-8", "replace")
d = json.loads(out)
if isinstance(d, dict):
    d = [d]
for p in d:
    cd = p.get("CreationDate")
    if isinstance(cd, dict) and "value" in cd:
        cd = cd["value"]
    try:
        s = str(cd)
        epoch = int(s.strip("/Date() ").split("+")[0]) / 1000.0
        ts = datetime.datetime.fromtimestamp(epoch).strftime("%H:%M:%S")
    except Exception:
        ts = str(cd)
    print(f"pid={p['ProcessId']} parent={p.get('ParentProcessId')} created={ts}")
    print("  cmd:", (p.get("CommandLine") or "")[:400])
    print()
