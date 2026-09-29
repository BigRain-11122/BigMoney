import json, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
bad = []
ok = 0
for line in out.splitlines():
    p = line[3:].strip().strip('"')
    if p.endswith(".json") or p.endswith(".jsonl"):
        try:
            if p.endswith(".jsonl"):
                [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
            else:
                json.load(open(p, encoding="utf-8"))
            ok += 1
        except Exception as ex:
            bad.append((p, str(ex)[:60]))
print("parse-ok:", ok, "| bad:", bad)
