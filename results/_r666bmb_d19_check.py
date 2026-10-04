# -*- coding: utf-8 -*-
# r666 bm-b D-19 watermark check (r661 sparse-clone recipe; per-key hash family per r458:
# decisions=SHA-256 / group orders=SHA-1 -- read state *_sha_method before hashing)
import json, subprocess, tempfile, shutil, hashlib, os, re, sys, io

CLONE_URL = "git@github.com:BigRain-11122/FluxGroup.git"
tmp = os.path.join(tempfile.gettempdir(), "fg-d19-bmb-r666")

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
    state = json.load(open("state.json", encoding="utf-8"))
    out = {"probe": "d19_watermark", "machine": "bm-b", "faces": {}}
    for label, path, key, hname in [
        ("DECISIONS", "docs/decisions.md", "last_decisions_sha", "sha256"),
        ("GORDERS", "docs/orders.md", "last_orders_sha", "sha1"),
    ]:
        rc, so, se = run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks", path])
        p = subprocess.run(["git", "-C", tmp, "show", "HEAD:" + path], capture_output=True)
        if p.returncode != 0:
            out["faces"][label] = {"verdict": "SHOW_FAIL", "err": p.stderr.decode("utf-8", "replace")[-200:]}
            continue
        blob = p.stdout
        h = hashlib.sha256(blob) if hname == "sha256" else hashlib.sha1(blob)
        new_sha = h.hexdigest().upper()
        old_sha = (state.get(key) or "").upper()
        verdict = "MATCH" if new_sha == old_sha else "CHANGED"
        face = {"verdict": verdict, "old_sha": old_sha[:16], "new_sha": new_sha[:16], "bytes": len(blob)}
        if verdict == "CHANGED":
            text = blob.decode("utf-8", "replace")
            lines = text.splitlines()
            hits = [l for l in lines if re.search(r"bm-b|BigMoney|quant", l, re.I)]
            face["total_lines"] = len(lines)
            face["bm_relevant_tail"] = hits[-12:]
            open("results/_r666bmb_%s_new.txt" % label.lower(), "wb").write(blob)
        out["faces"][label] = face
    with io.open("results/_r666bmb_d19_check.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("DECISIONS:", out["faces"]["DECISIONS"]["verdict"], "| GORDERS:", out["faces"]["GORDERS"].get("verdict"))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
