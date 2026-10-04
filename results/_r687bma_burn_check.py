# -*- coding: utf-8 -*-
"""r687 bm-a: verify judge shard-2 burn launch (autofill tail entry + pid
liveness via CIM full-scan + early checkpoint presence)."""
import json, io, subprocess

d = json.load(open("results/autofill_state.bm-a.json", encoding="utf-8"))
launches = d.get("launches", [])
recent = launches[-3:] if launches else []
out = {"n_launches": len(launches), "recent": recent}
pids = [l.get("pid") for l in recent if l.get("pid")]
if pids:
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-CimInstance Win32_Process | Where-Object { " +
                        " | ".join("$_.ProcessId -eq %d" % p for p in pids) +
                        " } | ForEach-Object { $_.ProcessId.ToString() + ' ' " +
                        "+ $_.CommandLine }"], capture_output=True)
    out["proc_lines"] = r.stdout.decode("utf-8", "replace").strip()[-500:]
r2 = subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-ChildItem results\\mass_trial -Filter "
                    "'w3_judge*' | Select-Object -First 6 Name"],
                   capture_output=True)
out["ckpt_dir_list"] = r2.stdout.decode("utf-8", "replace").strip()[:400]
with io.open("results/_r687bma_burn_check.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("WROTE burn check")
