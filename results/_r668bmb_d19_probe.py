# r668 bm-b S0.5 D-19 watermark probe -- sparse-clone raw-bytes fallback (r631 recipe, K: absent, no local group tree)
import subprocess, hashlib, json, os, sys, tempfile

REPO = "https://github.com/BigRain-11122/FluxGroup.git"
tmp = os.path.join(tempfile.gettempdir(), "fg-sparse-r668bmb")
rc = 0
if not os.path.isdir(os.path.join(tmp, ".git")):
    p = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", REPO, tmp],
                       capture_output=True)
    rc = p.returncode
    if rc != 0:
        print(json.dumps({"clone_rc": rc, "err": p.stderr.decode(errors="replace")[-400:]})); sys.exit(2)
else:
    p = subprocess.run(["git", "-C", tmp, "fetch", "origin"], capture_output=True)
    rc = p.returncode if p.returncode else 0

p = subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks", "docs/decisions.md", "docs/orders.md"],
                   capture_output=True)
if p.returncode != 0:
    print(json.dumps({"sparse_rc": p.returncode, "err": p.stderr.decode(errors="replace")[-400:]})); sys.exit(2)

def raw(path):
    # r660: git show origin bytes via subprocess, never hash on-disk translated copies
    p = subprocess.run(["git", "-C", tmp, "show", "origin/main:" + path], capture_output=True)
    return p.returncode, p.stdout

rc_dec, dec = raw("docs/decisions.md")
rc_ord, ord_ = raw("docs/orders.md")
sha256_dec = hashlib.sha256(dec).hexdigest().upper() if rc_dec == 0 else None
sha1_ord = hashlib.sha1(ord_).hexdigest().upper() if rc_ord == 0 else None

state = json.load(open(r"C:\Fluxgroup\FluxGroup\quant\bigmoney\state.json", encoding="utf-8"))
out = {
    "probe_at": "2026-10-04T11:37:00+08:00",
    "decisions_sha256": sha256_dec,
    "decisions_watermark": state.get("last_decisions_sha"),
    "decisions_match": sha256_dec == state.get("last_decisions_sha") if sha256_dec else False,
    "orders_sha1": sha1_ord,
    "orders_watermark": state.get("last_orders_sha"),
    "orders_match": sha1_ord == state.get("last_orders_sha") if sha1_ord else False,
    "decisions_bytes": len(dec) if rc_dec == 0 else -1,
    "orders_bytes": len(ord_) if rc_ord == 0 else -1,
}
with open(r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r668bmb_d19_probe.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=True)
print(json.dumps(out))
if not out["decisions_match"] and rc_dec == 0:
    lines = dec.decode("utf-8", errors="replace").splitlines()
    with open(r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r668bmb_d19_newlines.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines[-80:]))
