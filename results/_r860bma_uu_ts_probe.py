import re

for path in (r"results\update_status.json",
             r"docs\daily_report\REPORT-2026-10-08.json"):
    raw = open(path, encoding="utf-8").read()
    parts = re.split(r'<<<<<<< HEAD\r?\n|=======\r?\n|>>>>>>> [^\r\n]+\r?\n', raw)
    print("==", path, "| parts:", len(parts))
    for i, p in enumerate(parts[:3]):
        t = re.search(r'"(ts|generated_at|updated_at|updated)": "([^"]+)"', p)
        print(" side", i, "->", (t.group(2) if t else "no-ts"),
              "| bytes:", len(p))
