import json, subprocess, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}
# merged-view entry state (what autofill reads)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "mlv", os.path.join(ROOT, "scripts", "merge_lane_views.py"))
mlv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mlv)
view = mlv.face_view("runnable_pool", os.path.join(ROOT, "results"))
for e in view.get("entries", []):
    if e.get("id") == "N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN":
        out["entry"] = {"status": e.get("status"),
                        "shard": e.get("shards", [{}])[0]}
# runner alive?
r = subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                    "Where-Object {$_.CommandLine -match 'alphagen_rl_p1'} | "
                    "Select-Object -First 3 ProcessId,CommandLine | ConvertTo-Json -Compress"],
                   capture_output=True, text=True)
out["runner_procs"] = (r.stdout or "").strip()[:600]
print(json.dumps(out, ensure_ascii=True, indent=1)[:1800])
