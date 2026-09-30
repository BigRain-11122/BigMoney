import io, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t = io.open("scripts/science_gates.py", encoding="utf-8").read().splitlines()
start = next(i for i, l in enumerate(t) if l.startswith("SEED_REGISTRY"))
vals = []
for l in t[start:start + 400]:
    m = re.match(r'\s*"([a-z0-9_]+)":\s*([0-9_]+)', l)
    if m:
        vals.append((m.group(1), int(m.group(2).replace("_", ""))))
for k, v in vals:
    print(k, "=", v)
print("--- max value =", max(v for _, v in vals))
used = [v for _, v in vals]
for c in [20329000, 20329001]:
    print("candidate", c, "collision:", c in used)
print("--- tail region ---")
for l in t[start:start + 400][-14:]:
    print(l)
