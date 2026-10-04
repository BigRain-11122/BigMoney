# r670 bm-b D-19 watermark probe: sparse clone origin blob raw bytes (r631 recipe)
# orders key = SHA-1 (40-hex), decisions key = SHA-256 (64-hex) per r458 self-cert
import json, os, subprocess, sys, tempfile, shutil

OUT = "results/_r670bmb_d19_check.json"
URL = "https://github.com/BigRain-11122/FluxGroup.git"
FACES = {"decisions": ("docs/decisions.md", "sha256"), "orders": ("docs/orders.md", "sha1")}

def run(args, cwd=None):
    p = subprocess.run(args, capture_output=True, cwd=cwd)
    return p.returncode, p.stdout, p.stderr

res = {"ts": "2026-10-04T12:2x", "machine": "bm-b", "round": "r670", "verdicts": {}}
tmp = tempfile.mkdtemp(prefix="fgd19-")
try:
    rc, so, se = run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", URL, tmp])
    if rc != 0:
        res["clone_rc"] = rc
        res["error"] = se.decode("utf-8", "replace")[:500]
        json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(res, ensure_ascii=False))
        sys.exit(2)
    rc, so, se = run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks",
                      "docs/decisions.md", "docs/orders.md"])
    if rc != 0:
        res["sparse_rc"] = rc
        res["error"] = se.decode("utf-8", "replace")[:500]
        json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(res, ensure_ascii=False))
        sys.exit(2)
    # raw bytes via git show origin/main (r660: subprocess raw, zero PS pipe)
    rc, so, se = run(["git", "-C", tmp, "rev-parse", "origin/main"])
    tip = so.decode().strip() if rc == 0 else ""
    res["group_tip"] = tip
    import hashlib
    st = json.load(open("state.json", encoding="utf-8"))
    for name, (path, algo) in FACES.items():
        rc, so, se = run(["git", "-C", tmp, "show", "origin/main:" + path])
        if rc != 0:
            res["verdicts"][name] = {"verdict": "MISSING", "err": se.decode("utf-8", "replace")[:200]}
            continue
        h = hashlib.sha256(so).hexdigest().upper() if algo == "sha256" else hashlib.sha1(so).hexdigest().upper()
        key = "last_decisions_sha" if name == "decisions" else "last_orders_sha"
        wm = (st.get(key) or "").upper()
        res["verdicts"][name] = {"verdict": "MATCH" if h == wm else "CHANGED",
                                 "computed": h, "watermark": wm}
finally:
    shutil.rmtree(tmp, ignore_errors=True)

json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False))
