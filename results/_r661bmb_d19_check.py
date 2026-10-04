# -*- coding: utf-8 -*-
# r661 bm-b D-19 decisions watermark check (r631 sparse-clone recipe + r660 subprocess raw-bytes law)
import json, subprocess, tempfile, shutil, hashlib, os, re, sys, io

CLONE_URL = "git@github.com:BigRain-11122/FluxGroup.git"
tmp = os.path.join(tempfile.gettempdir(), "fg-d19-bmb-r661")
rc_all = {}

def run(cmd, cwd=None):
    p = subprocess.run(cmd, capture_output=True, cwd=cwd)
    return p.returncode, p.stdout, p.stderr

try:
    if os.path.exists(tmp):
        shutil.rmtree(tmp, ignore_errors=True)
    rc, so, se = run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", CLONE_URL, tmp])
    if rc != 0:
        print(json.dumps({"stage": "clone", "rc": rc, "err": se.decode("utf-8", "replace")[-400:]}))
        sys.exit(2)
    rc, so, se = run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks", "docs/decisions.md"])
    if rc != 0:
        print(json.dumps({"stage": "sparse", "rc": rc, "err": se.decode("utf-8", "replace")[-400:]}))
        sys.exit(2)
    # raw bytes via git show (HEAD == origin/main in depth-1 clone)
    p = subprocess.run(["git", "-C", tmp, "show", "HEAD:docs/decisions.md"], capture_output=True)
    if p.returncode != 0:
        print(json.dumps({"stage": "show", "rc": p.returncode, "err": p.stderr.decode("utf-8", "replace")[-400:]}))
        sys.exit(2)
    blob = p.stdout
    new_sha = hashlib.sha256(blob).hexdigest().upper()
    state = json.load(open("state.json", encoding="utf-8"))
    old_sha = (state.get("last_decisions_sha") or "").upper()
    text = blob.decode("utf-8", "replace")
    # extract decision rows mentioning bm-b/BigMoney/quant (for info when changed)
    lines = text.splitlines()
    hits = [l for l in lines if re.search(r"bm-b|BigMoney|quant", l, re.I) and re.match(r"^[-*]?\s*[-*]?\s*(D-|20\d\d)", l)]
    verdict = "MATCH" if new_sha == old_sha else "CHANGED"
    out = {
        "probe": "d19_decisions", "machine": "bm-b",
        "old_sha": old_sha, "new_sha": new_sha, "verdict": verdict,
        "total_lines": len(lines),
        "bm_relevant_lines": hits[-12:],
    }
    with io.open("results/_r661bmb_d19_check.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("VERDICT:", verdict, "| new_sha:", new_sha[:16], "| relevant lines:", len(hits))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
