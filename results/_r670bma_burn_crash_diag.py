# r670 bm-a: burn crash diagnosis - find runner logs + autofill launch records
import json, os, subprocess, glob

d = json.load(open("results/autofill_state.bm-a.json", encoding="utf-8"))
print("=== autofill launches (last 3) ===")
for L in d.get("launches", [])[-3:]:
    print(json.dumps(L, ensure_ascii=False)[:500])
print("=== last_tick ===")
print(json.dumps(d.get("last_tick", {}), ensure_ascii=False)[:500])

# find any theme_judge logs / burn dirs
print("=== candidate log files ===")
for pat in ["results/theme_judge_p1*", "results/**/theme_judge*", "logs/*theme*", "results/_burn*"]:
    for p in glob.glob(pat, recursive=True):
        print("  ", p, os.path.getsize(p) if os.path.isfile(p) else "<dir>")

# runner code: look at output paths & log discipline
r = subprocess.run(["python", "-c",
    "import re;src=open('scripts/theme_judge_p1.py',encoding='utf-8').read();"
    "print('LOG refs:');"
    "[print(' ',m) for m in re.findall(r'[^\\n]*(?:log|stderr|burn_state|LOG_)[^\\n]*', src)[:25]]"],
    capture_output=True)
print(r.stdout.decode("utf-8", errors="replace"))
