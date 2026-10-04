import os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
FACES = {
    "value": os.path.join(BASE, "fund_value_p1", "nulls.jsonl"),
    "divlowvol": os.path.join(BASE, "fund_divlowvol_p1", "nulls.jsonl"),
    "quality": os.path.join(BASE, "fund_quality_p1", "nulls.jsonl"),
}
r656_counts = {"value": 645, "divlowvol": 350, "quality": 489}
r656_pids = {"value": 34396, "divlowvol": 57116, "quality": 30208}

out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
                     capture_output=True).stdout.decode("gbk", "replace")
alive_pids = set()
for line in out.splitlines():
    if line.startswith('"python'):
        try:
            alive_pids.add(int(line.split('","')[1]))
        except Exception:
            pass

for k, p in FACES.items():
    n = -1
    if os.path.exists(p):
        with open(p, "rb") as f:
            n = sum(1 for _ in f)
    delta = n - r656_counts[k] if n >= 0 else "?"
    pid_alive = r656_pids[k] in alive_pids
    print("trio %s lines=%s (delta_since_r656=%s) pid=%s alive=%s" % (k, n, delta, r656_pids[k], pid_alive))
print("python_proc_count:", len(alive_pids))
