import subprocess, json, io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
FILES = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
]

def stages(path):
    out = subprocess.run(["git", "ls-files", "-u", "--", path], cwd=REPO, capture_output=True).stdout.decode('utf-8', 'replace')
    d = {}
    for line in out.strip().splitlines():
        parts = line.split()
        if len(parts) >= 4:
            d[parts[2]] = parts[1]  # stage -> blob sha
    return d

def blob(sha, n=1200):
    b = subprocess.run(["git", "cat-file", "blob", sha], cwd=REPO, capture_output=True).stdout
    txt = b.decode('utf-8', 'replace')
    return b, txt[:n], len(b)

for f in FILES:
    print("=" * 80)
    print("FILE:", f)
    st = stages(f)
    print("stages:", json.dumps(st))
    for s, sha in sorted(st.items()):
        b, head, size = blob(sha)
        print(f"--- stage {s} ({sha[:12]}) size={size} ---")
        print(repr(head))
        # for json try parse
        if f.endswith('.json'):
            try:
                j = json.loads(b.decode('utf-8'))
                print("  JSON keys:", list(j.keys())[:20])
                for k in ('generated','generated_at','ts','date','report_date','generated_utc','asof'):
                    if k in j:
                        print(f"  {k} = {j[k]!r}")
            except Exception as e:
                print("  JSON parse fail:", e)
    # head/tail of full file for md
    print()

# who created / touched the dash file on both sides
for f in FILES:
    print("=" * 80)
    print("HISTORY (first+recent):", f)
    for arg in (["git", "log", "--oneline", "-n", "6", "--", f], ["git", "log", "--oneline", "--follow", "--diff-filter=A", "--", f]):
        out = subprocess.run(arg, cwd=REPO, capture_output=True).stdout.decode('utf-8', 'replace')
        print("$", " ".join(arg[2:]))
        print(out.strip() or "(none)")

# no-dash twins existence check
out = subprocess.run(["git", "ls-files", "-s", "--", "docs/daily_report/"], cwd=REPO, capture_output=True).stdout.decode('utf-8', 'replace')
print("=" * 80)
print("docs/daily_report index:")
print(out)

# what filename does daily_report.py produce?
out = subprocess.run(["git", "grep", "-n", "REPORT-", "HEAD", "--", "scripts/daily_report.py"], cwd=REPO, capture_output=True).stdout.decode('utf-8', 'replace')
print("daily_report.py filename convention @HEAD:")
print(out or "(not found at HEAD)")
