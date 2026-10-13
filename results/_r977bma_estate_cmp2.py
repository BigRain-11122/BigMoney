import subprocess, json, os

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def show(ref):
    return subprocess.run([GIT, "show", ref], cwd=ROOT, capture_output=True).stdout

# 1. origin state
raw = show("origin/main:state-bm-a.json")
d = json.loads(raw.decode("utf-8"))
print("ORIGIN state-bm-a: round_no=", d.get("round_no"), "last_round=", d.get("last_round"), "ts=", d.get("ts"))
print("  now_active=", str(d.get("now_active"))[:100])
print("  verdict=", str(d.get("verdict"))[:140])

# 2. HEAD state
raw = show("HEAD:state-bm-a.json")
d2 = json.loads(raw.decode("utf-8"))
print("HEAD state-bm-a: round_no=", d2.get("round_no"), "ts=", d2.get("ts"))

# 3. local w17 faces conflict-marker scan
for p in ["results/trial_labor_w17/w17_judge.json", "results/trial_labor_w17/w17_reform_face.json"]:
    b = open(os.path.join(ROOT, p), "rb").read()
    mk = b.count(b"<<<<<<<") + b.count(b">>>>>>>") + b.count(b"=======")
    print(f"LOCAL {p}: {len(b)}B markers~{mk}")

# 4. origin w17 faces marker scan
for p in ["results/trial_labor_w17/w17_judge.json", "results/trial_labor_w17/w17_reform_face.json"]:
    b = show(f"origin/main:{p}")
    mk = b.count(b"<<<<<<<") + b.count(b">>>>>>>") + b.count(b"=======")
    print(f"ORIGIN {p}: {len(b)}B markers~{mk}")

# 5. marks-12/13 spot check
for p in ["results/paper/marks/marks-20261012.jsonl", "results/paper/marks/marks-20261013.jsonl"]:
    lines = [l for l in open(os.path.join(ROOT, p), encoding="utf-8").read().splitlines() if l.strip()]
    ok = 0
    ids = set()
    for l in lines:
        try:
            j = json.loads(l)
            ok += 1
            ids.add(j.get("trader") or j.get("id") or j.get("account") or "?")
        except Exception:
            pass
    print(f"MARKS {p}: {len(lines)} lines, {ok} valid-json, accounts~{sorted(ids)[:8]}")
    print("   sample:", lines[0][:150] if lines else "(empty)")
