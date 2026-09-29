import subprocess, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
r = subprocess.run(
    ["python", "tools/skills/bigmoney-conflict-resolve/scripts/classify_conflicts.py"],
    capture_output=True,
)
txt = r.stdout.decode("utf-8", errors="replace")
i = txt.find("{")
# find the outermost JSON object (from first '{' to last '}')
d = json.loads(txt[i : txt.rfind("}") + 1])
for e in d["classified"]:
    print(e["state"], e["path"], "->", e["class"])
print("unknown:", d.get("unknown"))
