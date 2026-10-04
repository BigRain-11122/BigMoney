# -*- coding: utf-8 -*-
# r674 bm-b r643 disambiguation: full cmdlines + cwd of concurrent codely sessions
import subprocess, json

def ps(cmd):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
    return r.stdout.decode("utf-8", "replace")

out = ps("Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'codely.exe' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress")
try:
    procs = json.loads(out or "[]")
    if isinstance(procs, dict):
        procs = [procs]
except Exception:
    procs = []

res = []
for p in procs:
    cmd = p.get("CommandLine") or ""
    # classify by prompt content markers
    tag = "unknown"
    if "Bigmoney" in cmd or "BigMoney" in cmd or "量化公司" in cmd:
        tag = "BIGMONEY"
    elif "BiuNiYiXia" in cmd or "biu" in cmd:
        tag = "BIU"
    elif "HomeWreck" in cmd:
        tag = "HOMEWRECK"
    elif "Phantom" in cmd:
        tag = "PHANTOM"
    res.append({"pid": p.get("ProcessId"), "parent": p.get("ParentProcessId"),
                "created": p.get("CreationDate"), "tag": tag,
                "cmd_head": cmd[:80], "cmd_len": len(cmd),
                "prompt_marker": cmd[cmd.find("-p"):cmd.find("-p")+120] if "-p" in cmd else ""})

with open(r"results\_r674bmb_codely_disambig.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("OK n=%d" % len(res))
