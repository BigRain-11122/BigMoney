import subprocess, json

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def show(ref):
    return subprocess.run([GIT, "show", ref], cwd=ROOT, capture_output=True).stdout

# spot-check: update_status.json local vs origin (which is newer in data terms)
for p in ["results/update_status.json", "results/d19_watermark.json"]:
    lo = json.loads(open(ROOT + "\\" + p, "rb").read().decode("utf-8"))
    try:
        og = json.loads(show(f"origin/main:{p}").decode("utf-8"))
    except Exception as e:
        print(p, "origin parse fail:", e); continue
    def face(d, keys):
        out = {}
        for k in keys:
            v = d.get(k)
            if isinstance(v, str): out[k] = v
        return out
    ks = [k for k in list(lo.keys())[:40] if "ts" in k or "date" in k or "asof" in k or "cutoff" in k or "updated" in k]
    print(p)
    print("  LOCAL :", face(lo, ks))
    print("  ORIGIN:", face(og, ks))

# marks on origin: latest file
out = show("origin/main:results/paper/marks").decode()  # tree listing
print("\norigin marks tree tail:", out[-400:])
