# D-19 dual-key check for bm-a (r677/r680/r686-compliant: ssh-first dual URL, mkdtemp unique dir,
# subprocess raw-byte hashing, per-key hash-family self-adjudication by stored key length)
import json, hashlib, subprocess, sys, tempfile, shutil, os, re

REPO_SSH = "git@github.com:BigRain-11122/FluxGroup.git"
REPO_HTTPS = "https://github.com/BigRain-11122/FluxGroup.git"

def sh(args, cwd=None, timeout=120):
    return subprocess.run(args, capture_output=True, cwd=cwd, timeout=timeout)

state = json.load(open("state-bm-a.json", encoding="utf-8"))
dec_key = state.get("last_decisions_sha", "")
orders_key = state.get("last_orders_sha", "")

def method_for(k):
    k = (k or "").strip().lower()
    if len(k) == 40:
        return "sha1"
    if len(k) == 64:
        return "sha256"
    return "unknown"

def hash_bytes(b, m):
    if m == "sha1":
        return hashlib.sha1(b).hexdigest()
    return hashlib.sha256(b).hexdigest()

out = {"ts": "2026-10-04T23:08+08:00", "dec_method": method_for(dec_key),
       "orders_method": method_for(orders_key)}

tmp = None
try:
    tmp = tempfile.mkdtemp(prefix="d19bma_")
    rc = None
    for url in (REPO_SSH, REPO_HTTPS):
        r = sh(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", url, "tree"], cwd=tmp, timeout=180)
        if r.returncode == 0:
            rc = r
            out["clone_url"] = "ssh" if url == REPO_SSH else "https"
            break
        out.setdefault("clone_fail", []).append(url.split("//")[-1])
    if rc is None or rc.returncode != 0:
        out["verdict"] = "CLONE-FAIL"
        print(json.dumps(out, ensure_ascii=False))
        sys.exit(2)
    wt = os.path.join(tmp, "tree")
    sh(["git", "sparse-checkout", "set", "--skip-checks", "docs/decisions.md", "docs/orders.md"], cwd=wt, timeout=60)
    # raw bytes from git objects (never hash on-disk copies - r660 law)
    dec = sh(["git", "show", "origin/main:docs/decisions.md"], cwd=wt).stdout
    ordf = sh(["git", "show", "origin/main:docs/orders.md"], cwd=wt).stdout
    dm = method_for(dec_key)
    om = method_for(orders_key)
    dec_h = hash_bytes(dec, dm)
    ord_h = hash_bytes(ordf, om)
    out["dec_match"] = (dec_h == (dec_key or "").strip().lower())
    out["orders_match"] = (ord_h == (ord_key_h := (orders_key or "").strip().lower()))
    out["verdict"] = "MATCH" if (out["dec_match"] and out["orders_match"]) else "CHANGED"
    open("results/_r701bma_d19_probe.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(out, ensure_ascii=False))
    # if decisions changed, dump tail for consumption
    if not out["dec_match"]:
        open("results/_r701bma_decisions_snapshot.md", "wb").write(dec)
    if not out["orders_match"]:
        open("results/_r701bma_group_orders_snapshot.md", "wb").write(ordf)
finally:
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
