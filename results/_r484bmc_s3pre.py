"""r484 bm-c S3 pre-flight: watermark red flag + saturation engine status (bm-c = Tools\ copy per XML anchor law r467)."""
import subprocess
import os
import json

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = os.path.join(REPO, "results", "_r484bmc_s3pre_out.txt")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
lines = []

# watermark red flag
wm_path = os.path.join(REPO, "results", "watermark_red.json")
if os.path.exists(wm_path):
    try:
        with open(wm_path, encoding="utf-8") as f:
            wm = json.load(f)
        lines.append(f"watermark_red: {json.dumps(wm, ensure_ascii=False)[:600]}")
    except Exception as e:
        lines.append(f"watermark_red PARSE_FAIL {e}")
else:
    lines.append("watermark_red.json absent")

# saturation engine status: bm-c registered task runs Tools\saturation_engine.py (r467 law)
r = subprocess.run(["python", "Tools\\saturation_engine.py", "status"], capture_output=True, cwd=REPO, creationflags=CNW)
lines.append(f"satengine rc={r.returncode}")
out = r.stdout.decode("utf-8", "replace").strip()
err = r.stderr.decode("utf-8", "replace").strip()
if out:
    lines.append("satengine_stdout:")
    lines.extend(out.splitlines()[-30:])
if err:
    lines.append("satengine_stderr:")
    lines.extend(err.splitlines()[-10:])

with open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(lines))
print("PROBE_DONE")
