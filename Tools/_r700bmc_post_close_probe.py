"""r700 bm-c O-1300 post-close state probe: judge process face + fuse +
autofill last_tick (did the old-code relaunch happen?)."""
import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe' or "
      "Name='pythonw.exe'\" | Select-Object ProcessId,ParentProcessId,"
      "Name,CreationDate,@{n=\"cmd\";e={if($_.CommandLine){"
      "$_.CommandLine.Substring(0,[Math]::Min(100,$_.CommandLine.Length))"
      "}else{''}}} | ConvertTo-Json -Compress")
r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", creationflags=0x08000000)
obj = json.loads(r.stdout) if r.stdout.strip() else []
if isinstance(obj, dict):
    obj = [obj]
print("== python face:")
for o in obj:
    print(" ", o.get("ProcessId"), o.get("Name"), "ppid", o.get("ParentProcessId"),
          (o.get("cmd") or "")[:95])

for f in ("results/crash_fuse.json", "results/crash_fuse.bm-c.json",
          "results/autofill_state.bm-c.json"):
    try:
        d = json.load(open(ROOT + "\\" + f, encoding="utf-8"))
    except Exception as ex:
        print(f, "READ FAIL", ex)
        continue
    if "autofill" in f:
        lt = d.get("last_tick", {})
        print("== autofill last_tick:", json.dumps(
            {k: lt.get(k) for k in ("ts", "verdict", "entry", "pid",
                                    "shard", "park", "parked")},
            ensure_ascii=False))
    else:
        sigs = d.get("sigs", {})
        print("==", f, "sigs:", json.dumps(
            {k: {kk: v.get(kk) for kk in ("count", "last_crash_ts", "state")
                 if kk in v} for k, v in list(sigs.items())[:3]},
            ensure_ascii=False)[:300], "cleared:", len(d.get("cleared", {})))
