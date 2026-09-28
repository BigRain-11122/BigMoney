"""r380 bm-b: REPORT twin staged-blob head probe (json uses different ts key)."""
import subprocess


def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                          capture_output=True).stdout


for st in ("2", "3"):
    b = blob(st, "docs/daily_report/REPORT-2026-09-28.json")
    print(f"--- REPORT.json stage :{st}: head 400 chars:")
    print(b[:400].decode("utf-8", errors="replace"))
    print()

b = blob("3", "docs/daily_report/REPORT-2026-09-28.md")
print("--- REPORT.md stage :3: first 300 chars:")
print(b[:300].decode("utf-8", errors="replace"))
