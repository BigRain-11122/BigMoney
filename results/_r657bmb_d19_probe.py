import subprocess, hashlib, os, tempfile, shutil

CANDIDATES = [r"K:\Fluxgroup\FluxGroup"]
BASE = os.path.dirname(os.path.abspath(__file__))
LAST = {
    "decisions": "EB14B510D304A1D0A30175447CF9360D6BAB6DC20972CEEBCE35D47EF8935BFA",
    "orders": "82A0CEF99F147C6F6D14A0C2233A44309768C548312F9069F7C33CF6A2AA311A",
}
PATHS = {"decisions": "docs/decisions.md", "orders": "docs/orders.md"}

def is_repo(p):
    return os.path.isdir(os.path.join(p, ".git")) or os.path.isfile(os.path.join(p, ".git"))

repo = None
for c in CANDIDATES:
    if is_repo(c):
        repo = c
        break

mode = "none"
if repo is not None:
    fr = subprocess.run(["git", "-C", repo, "fetch", "origin"], capture_output=True, timeout=180)
    mode = "existing:" + repo + " fetch_rc=" + str(fr.returncode)
else:
    tmp = os.path.join(tempfile.gettempdir(), "fg-sparse-d19-r657")
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                         "https://github.com/BigRain-11122/FluxGroup.git", tmp],
                        capture_output=True, timeout=300)
    if r.returncode != 0:
        print("CLONE_FAIL", r.stderr.decode("utf-8", "replace")[:400])
        raise SystemExit(2)
    subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks",
                    "docs/decisions.md", "docs/orders.md"], capture_output=True, timeout=120)
    repo = tmp
    mode = "sparse-clone"

print("mode:", mode)
for name in ("decisions", "orders"):
    r = subprocess.run(["git", "-C", repo, "show", "origin/main:" + PATHS[name]],
                       capture_output=True, timeout=60)
    if r.returncode != 0:
        print(name, "MISSING")
        continue
    blob = r.stdout
    sha = hashlib.sha256(blob).hexdigest().upper()
    with open(os.path.join(BASE, "_r657bmb_%s_snapshot.md" % name), "wb") as f:
        f.write(blob)
    print(name, "sha:", sha)
    print(name, "changed:", sha != LAST[name])
