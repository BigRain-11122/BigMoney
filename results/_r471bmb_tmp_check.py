import json, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# 1) grammar ledger W13 row
led = io.open(r"research\TRIAL_GRAMMAR_LEDGER.md", encoding="utf-8").read()
hits = [l for l in led.splitlines() if ("W13" in l or "w13" in l or "SUMN" in l)]
print("ledger lines w/ W13/SUMN (tail 6):")
for l in hits[-6:]:
    print("  ", l[:170])

# 2) W13 screen null p95
s13 = json.load(open(r"results/trial_labor_w13/w13_screen.json", encoding="utf-8"))
d = json.dumps(s13)
m = re.findall(r'"[^"]*p9[^"]*"\s*:\s*[0-9.]+', d)
print("p95-ish fields:", m[:10])
nf = s13.get("null_family")
print("null_family:", json.dumps(nf, ensure_ascii=False)[:600] if nf else None)
# search nested
def walk(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if "p95" in str(k) or "p50" in str(k):
                print("  FOUND", p + "/" + str(k), "=", v)
            walk(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o[:300]):
            walk(v, p + f"[{i}]")
walk(s13)

# 3) DSR live head (attrition ledger chain head)
att = json.load(open(r"results/gate_attrition.json", encoding="utf-8"))
for k in att:
    if not isinstance(att[k], (dict, list)):
        print("attrition scalar:", k, "=", att[k])
