import json, subprocess, hashlib, os, sys

# D-19 content-addressed check (r660 law: hash origin blob bytes via git show, never working-tree copy)
CAND_PATHS = [
    r"K:\Fluxgroup\FluxGroup",
    r"C:\Users\sjs20\Desktop\FluxGroup",
]
repo = None
for p in CAND_PATHS:
    if os.path.isdir(p) and os.path.isdir(os.path.join(p, ".git")):
        repo = p
        break

def git_show(repo, path):
    r = subprocess.run(["git", "-C", repo, "show", "origin/main:" + path],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

state_path = "state-bm-a.json"
st = json.load(open(state_path, encoding="utf-8"))
prev_sha = st.get("last_decisions_sha")

if repo:
    subprocess.run(["git", "-C", repo, "fetch", "origin"], capture_output=True, timeout=120)
    blob = git_show(repo, "docs/decisions.md")
else:
    # sparse clone fallback (r631 bm-b recipe)
    tmp = os.path.join(os.environ.get("TEMP", "."), "fluxgroup_d19_sparse")
    if not os.path.isdir(tmp):
        subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                        "https://github.com/BigRain-11122/FluxGroup.git", tmp], capture_output=True, timeout=300)
    subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks", "docs/decisions.md"], capture_output=True, timeout=120)
    subprocess.run(["git", "-C", tmp, "fetch", "--depth", "1", "origin", "main"], capture_output=True, timeout=120)
    blob = git_show(tmp, "docs/decisions.md")

if blob is None:
    print(json.dumps({"mode": "no-repo-no-blob", "verdict": "SKIP"}))
    sys.exit(0)

sha = hashlib.sha256(blob).hexdigest()
changed = (prev_sha != sha)
out = {"sha": sha, "prev_sha": prev_sha, "changed": changed, "mode": "repo" if repo else "sparse"}
if changed:
    # extract only lines mentioning BigMoney / quant / bm-a relevant to this company
    text = blob.decode("utf-8", errors="replace")
    relevant = []
    for line in text.splitlines():
        low = line.lower()
        if any(k in low for k in ["bigmoney", "quant", "bm-a", "bm-a", "量化子公司"]):
            relevant.append(line)
    out["relevant_lines"] = relevant[-40:]
print(json.dumps(out, ensure_ascii=False, indent=1))
