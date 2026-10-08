import json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(p):
    with open(os.path.join(ROOT, p), "r", encoding="utf-8") as f:
        return json.load(f)

shared = load("results/runnable_pool.json")
entries = shared["entries"] if isinstance(shared, dict) and "entries" in shared else shared

ready = [e for e in entries if e.get("status") == "ready"]
print(f"total={len(entries)} ready={len(ready)}")
print("--- first ready entry full dump ---")
if ready:
    print(json.dumps(ready[0], ensure_ascii=False, indent=1))

def w17(pool, tag):
    print(f"--- {tag} W17-ish entries ---")
    for e in pool:
        blob = json.dumps(e, ensure_ascii=False)
        if "w17" in blob.lower() or "W17" in blob:
            keep = {k: e.get(k) for k in e.keys()
                    if k not in ("cmd","command","argv","runner")}
            print(json.dumps(keep, ensure_ascii=False))

w17(entries, "local shared")

# origin face
out = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"],
                      cwd=ROOT, capture_output=True, timeout=60)
if out.returncode == 0:
    opool = json.loads(out.stdout.decode("utf-8"))
    oents = opool["entries"] if isinstance(opool, dict) and "entries" in opool else opool
    from collections import Counter
    print("origin status:", dict(Counter(e.get("status","?") for e in oents)))
    w17(oents, "origin")
else:
    print("origin read rc", out.returncode, out.stderr.decode()[:200])
