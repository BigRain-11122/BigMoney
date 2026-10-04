import json, subprocess, hashlib, os, tempfile, shutil
repo = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
FG = r"K:\Fluxgroup\FluxGroup"
mid = "bm-a"

def read_state():
    with open(os.path.join(repo, "state-bm-a.json"), "rb") as f:
        return json.loads(f.read().decode('utf-8'))

st = read_state()
prev = st.get("last_decisions_sha")
print("state last_decisions_sha:", prev)

if os.path.isdir(FG):
    subprocess.run(["git", "-C", FG, "fetch", "origin"], capture_output=True)
    r = subprocess.run(["git", "-C", FG, "show", "origin/main:docs/decisions.md"], capture_output=True)
    if r.returncode == 0:
        blob = r.stdout
    else:
        blob = None
else:
    # sparse clone fallback (r631): ssh first, unique tempdir
    blob = None
    for url in ["git@github.com:BigRain-11122/FluxGroup.git", "https://github.com/BigRain-11122/FluxGroup.git"]:
        td = tempfile.mkdtemp()
        try:
            c1 = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", url, td], capture_output=True)
            if c1.returncode != 0:
                continue
            subprocess.run(["git", "-C", td, "sparse-checkout", "set", "--skip-checks", "docs/decisions.md"], capture_output=True)
            r = subprocess.run(["git", "-C", td, "show", "origin/main:docs/decisions.md"], capture_output=True)
            if r.returncode == 0:
                blob = r.stdout
                break
        finally:
            shutil.rmtree(td, ignore_errors=True)

assert blob is not None, "cannot read decisions.md from any channel"
cur = hashlib.sha256(blob).hexdigest().upper()
print("origin decisions sha256:", cur)
if prev == cur:
    print("VERDICT: MATCH - zero action")
else:
    print("VERDICT: CHANGED - need to consume board")
    # extract board lines mentioning this machine
    text = blob.decode('utf-8')
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ("bm-a" in ln) or ("BigMoney" in ln) or ("quant" in ln):
            print(f"L{i+1}: {ln[:200]}")
    # also show tail 40 lines (newest decisions)
    print("--- TAIL 40 ---")
    for ln in lines[-40:]:
        print(ln[:200])
