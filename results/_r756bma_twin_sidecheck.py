import json, subprocess
def sb(p, s):
    r = subprocess.run(["git", "show", f":{s}:{p}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None
for p in ["docs/live_usage/LIVE-2026-10-06.json", "docs/daily_report/REPORT-2026-10-06.json"]:
    for s, tag in [(2, "origin"), (3, "local")]:
        b = sb(p, s)
        if b:
            d = json.loads(b.decode("utf-8"))
            g = d.get("generated") or d.get("generated_at")
            print(f"{p} [{tag}] generated={g}")
