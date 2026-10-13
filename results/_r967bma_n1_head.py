# r967: N1 registry head check (pre-pre-seat: wave tail, seat vacancy, owner counts)
import json, re, subprocess, sys
sys.path.insert(0, r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\scripts")

GIT = r"C:\Program Files\Git\cmd\git.exe"
# read registry from origin (fresh) per origin-vacancy law
r = subprocess.run([GIT, "show", "origin/main:scripts/perpetual_faces.py"], capture_output=True)
src = r.stdout.decode("utf-8", "replace")

# N1_BANDS registry: extract last 6 entries
m = re.findall(r'"W(\d+)":\s*\{[^}]*?"owner":\s*"(\w+)"[^}]*?"A":\s*\[(\d+),\s*(\d+)\)[^}]*?"B":\s*\[(\d+),\s*(\d+)\)', src)
if not m:
    # fallback: look for WAVE_CONFIGS-like dict entries
    m = re.findall(r'"?W(\d+)"?\s*:\s*\{[^{}]*?owner[^{}]*?"bm-(\w)"', src)
print("band entries found:", len(m))
for row in m[-8:]:
    print("band:", row)

# find wave count / latest wave number referenced
waves = sorted(set(int(x[0]) for x in m)) if m else []
print("wave range:", (waves[0], waves[-1]) if waves else None, "count:", len(waves))

# results head: read n1 results of latest waves if present
import glob, os
res = sorted(glob.glob(r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\perpetual_faces\n1_w*_results.json"))
print("local results files:", len(res), "tail:", [os.path.basename(p) for p in res[-5:]])
if res:
    d = json.load(open(res[-1], encoding="utf-8"))
    keys = list(d.keys())
    print("latest results file keys sample:", keys[:12])
    for k in ("wave","ledger","K","n_eff","mu","sigma","owner","audit"):
        if k in d: print(" ", k, "=", str(d[k])[:100])
