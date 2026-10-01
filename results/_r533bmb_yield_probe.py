import psutil, os, subprocess, re

try:
    p = psutil.Process(54560)
    print("pid 54560 ALIVE:", p.status(), " ".join((p.cmdline() or []))[:120])
except Exception as e:
    print("pid 54560:", e)
lp = os.path.join("logs", "saturation_engine", "PERPETUAL-N1-W44-0.log")
if os.path.exists(lp):
    print("burn log tail:", open(lp, encoding="utf-8", errors="replace").read()[-300:])
else:
    print("burn log absent")

subprocess.run(["git", "fetch", "origin"])
blob = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_FACES.md"],
                     capture_output=True).stdout.decode("utf-8", "replace")
rows = [l for l in blob.splitlines() if l.lstrip().startswith("- N1 ")]
print("canon rows:", len(rows), "| last wave:", re.findall(r"波(\d+)（", rows[-1]))
cfg = subprocess.run(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                     capture_output=True).stdout.decode("utf-8", "replace")
own = re.findall(r"(\d+):\s*\{[^{}]*?engine_owner...?\s*[:=]\s*...?([\w-]+)", cfg)
print("owners tail:", own[-4:])
r = subprocess.run(["git", "cat-file", "-e", "origin/main:results/perpetual_faces/n1_w43_results.json"])
print("n1_w43_results on origin:", r.returncode == 0)
# W45 slot vacancy on fresh origin
assert '45: {"a": (133_004, 135_003)' not in cfg, "W45 slot TAKEN in config"
assert "N1 波45" not in blob, "W45 canon row TAKEN"
print("W45 slot: VACANT")
