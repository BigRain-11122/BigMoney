import io, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t = io.open("scripts/science_gates.py", encoding="utf-8").read().splitlines()
start = next(i for i, l in enumerate(t) if l.startswith("SEED_REGISTRY"))
# find registry end: first line that is exactly '}' after start
end = next(i for i in range(start, len(t)) if t[i].strip() == "}")
vals = []
for l in t[start:end]:
    m = re.match(r'\s*"([a-z0-9_]+)":\s*([0-9_]+)', l)
    if m:
        vals.append((m.group(1), int(m.group(2).replace("_", ""))))
print("registry span lines", start + 1, "-", end + 1, "| keys=", len(vals))
top = sorted(vals, key=lambda kv: -kv[1])[:12]
for k, v in top:
    print("TOP:", k, "=", v)
used = [v for _, v in vals]
for c in [20329000]:
    hits = [k for k, v in vals if abs(v - c) <= 100]
    print("candidate", c, "band100 hits:", hits)
w14 = [(k, v) for k, v in vals if "w13" in k or "w14" in k]
print("w13/w14 keys:", w14)
