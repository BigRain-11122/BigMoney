import subprocess, hashlib, json, sys
sys.stdout.reconfigure(encoding="utf-8")
repo = r"K:\Fluxgroup\FluxGroup"
subprocess.run(["git", "-C", repo, "fetch", "origin"],
               capture_output=True, timeout=60)
blob = subprocess.check_output(
    ["git", "-C", repo, "show", "origin/main:docs/decisions.md"])
sha = hashlib.sha256(blob).hexdigest()
st = json.load(open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json",
                    encoding="utf-8"))
prev = str(st.get("last_decisions_sha", "")).upper()
cur = sha.upper()
print("prev_sha:", prev)
print("cur_sha :", cur)
print("VERDICT:", "MATCH-unchanged zero-action" if prev == cur else "CHANGED")
if prev != cur:
    import re
    txt = blob.decode("utf-8", "replace")
    print("tail 2000 chars:")
    print(txt[-2000:])
