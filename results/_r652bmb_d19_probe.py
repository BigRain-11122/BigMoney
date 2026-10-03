# r652 bm-b D-19 watermark probe (r660 law: git show raw bytes -> sha256, no worktree-file hashing)
import subprocess, sys, hashlib, os

STATE = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\state.json"
LAST_SHA = "EB14B510D304A1D0A30175447CF9360D6BAB6DC20972CEEBCE35D47EF8935BFA"

candidates = [
    r"K:\Fluxgroup\FluxGroup",
    r"C:\Fluxgroup\FluxGroup",
]

repo = None
for c in candidates:
    if os.path.isdir(c) and os.path.isdir(os.path.join(c, ".git")):
        repo = c
        break

result = {"repo_used": repo, "match": None, "sha": None, "orders_ceo_rows": []}

if repo:
    subprocess.run(["git", "-C", repo, "fetch", "origin"],
                   capture_output=True, timeout=120)
    p = subprocess.run(["git", "-C", repo, "show", "origin/main:docs/decisions.md"],
                       capture_output=True, timeout=60)
    if p.returncode != 0:
        result["error"] = p.stderr.decode("utf-8", "replace")[:300]
        print("ERROR git show rc=%d" % p.returncode)
        sys.exit(2)
    blob = p.stdout
    sha = hashlib.sha256(blob).hexdigest().upper()
    result["sha"] = sha
    result["match"] = (sha == LAST_SHA)
    # orders.md CEO physical-item section (read for ceo-pending rows referencing bm-b/BigMoney)
    p2 = subprocess.run(["git", "-C", repo, "show", "origin/main:docs/orders.md"],
                         capture_output=True, timeout=60)
    if p2.returncode == 0:
        for line in p2.stdout.decode("utf-8", "replace").splitlines():
            low = line.lower()
            if ("bigmoney" in low or "bm-b" in low or "bmb" in low) and line.strip():
                result["orders_ceo_rows"].append(line.strip()[:200])
else:
    # sparse clone fallback (r631 recipe)
    tmp = os.path.join(os.environ.get("TEMP", "."), "_r652_d19_sparse")
    subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                    "https://github.com/BigRain-11122/FluxGroup.git", tmp],
                   capture_output=True, timeout=180)
    subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks",
                   "docs/decisions.md"], capture_output=True, timeout=60)
    p = subprocess.run(["git", "-C", tmp, "show", "origin/main:docs/decisions.md"],
                       capture_output=True, timeout=60)
    if p.returncode == 0:
        sha = hashlib.sha256(p.stdout).hexdigest().upper()
        result["repo_used"] = tmp
        result["sha"] = sha
        result["match"] = (sha == LAST_SHA)
    else:
        result["error"] = p.stderr.decode("utf-8", "replace")[:300]

print("REPO=" + str(result["repo_used"]))
print("SHA=" + str(result["sha"]))
print("MATCH=" + str(result["match"]))
for r in result["orders_ceo_rows"][:10]:
    print("CEO_ROW: " + r)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_r652bmb_d19_probe.json"), "w", encoding="utf-8") as f:
    import json
    json.dump(result, f, ensure_ascii=False, indent=1)
sys.exit(0)
