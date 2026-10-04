# -*- coding: utf-8 -*-
"""r693 bm-a S0.5 orders/decisions dual-key check (r458/r672/r686 lineage).
Orders leg = same-shape set diff vs origin ls-tree (r477 full filenames, r669 basename filter).
Decisions leg = D-19 watermark: GROUP tree origin blob sha256 (r660 subprocess raw bytes).
Group tree fallback: K:/C: absent -> sparse clone (r631 recipe, r677 ssh-first, mkdtemp).
"""
import json, subprocess, hashlib, sys, io, os, tempfile, shutil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def git_bytes(args, cwd=None):
    return subprocess.run(["git"] + args, capture_output=True, cwd=cwd).stdout

# --- orders leg (this repo, fleet task orders) ---
ls = git_bytes(["ls-tree", "origin/main", "fleet/orders/", "--name-only"]).decode("utf-8")
origin_orders = {os.path.basename(ln.strip()) for ln in ls.splitlines()
                 if ln.strip().endswith(".md") and os.path.basename(ln.strip()).startswith("O-")}
ack = set(json.load(open("fleet/machines/bm-a.json", encoding="utf-8")).get("orders_ack", []))
ack_o = {a for a in ack if a.startswith("O-")}
extra = sorted(a for a in ack if not a.startswith("O-"))
unacked = sorted(origin_orders - ack_o)
print("ORDERS origin_o=%d ack_o=%d ack_extra=%s unacked=%d" % (len(origin_orders), len(ack_o), extra, len(unacked)))
for u in unacked:
    print("  UNACKED:", u)

# --- group tree locate / sparse clone fallback ---
GRP = None
for p in ("K:\\Fluxgroup\\FluxGroup", "C:\\Fluxgroup\\FluxGroup"):
    if os.path.exists(p):
        GRP = p
        break
tmpd = None
if GRP is None:
    tmpd = tempfile.mkdtemp(prefix="bm_d19_")
    for url in ("git@github.com:BigRain-11122/FluxGroup.git",
                "https://github.com/BigRain-11122/FluxGroup.git"):
        r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none",
                            "--sparse", url, tmpd], capture_output=True)
        if r.returncode == 0:
            subprocess.run(["git", "-C", tmpd, "sparse-checkout", "set", "--skip-checks",
                            "docs/decisions.md", "docs/orders.md"], capture_output=True)
            GRP = tmpd
            print("GROUPTREE sparse-clone ok via", url.split("@")[-1].split("/")[-1])
            break
        else:
            print("GROUPTREE clone fail rc=%d: %s" % (r.returncode, r.stderr.decode(errors="replace")[:150]))
            shutil.rmtree(tmpd, ignore_errors=True)
            tmpd = tempfile.mkdtemp(prefix="bm_d19_")
else:
    subprocess.run(["git", "-C", GRP, "fetch", "origin"], capture_output=True)
    print("GROUPTREE local at", GRP)

st = json.load(open("state-bm-a.json", encoding="utf-8"))
if GRP:
    dec = git_bytes(["show", "origin/main:docs/decisions.md"], cwd=GRP)
    ordm = git_bytes(["show", "origin/main:docs/orders.md"], cwd=GRP)
    sha_dec = hashlib.sha256(dec).hexdigest().upper() if dec else None
    sha_ord = hashlib.sha256(ordm).hexdigest().upper() if ordm else None
    wm_dec = str(st.get("last_decisions_sha", ""))
    print("DECISIONS wm=%s now=%s match=%s size=%d" % (wm_dec[:12], (sha_dec or "NONE")[:12],
          (sha_dec is not None and wm_dec.upper() == sha_dec), len(dec)))
    wm_ord = str(st.get("last_orders_sha", ""))
    method = st.get("last_orders_sha_method", "")
    if not method:
        method = "sha1" if len(wm_ord) == 40 else ("sha256" if len(wm_ord) == 64 else "?")
    if method == "sha1":
        h = hashlib.sha1(ordm).hexdigest().upper() if ordm else None
    else:
        h = sha_ord
    print("ORDERS_WM key_method=%s wm=%s now=%s match=%s size=%d" % (
        method, wm_ord[:12], (h or "NONE")[:12], (h is not None and wm_ord.upper() == h), len(ordm)))
    if sha_dec and wm_dec.upper() != sha_dec:
        open("results/_r693bma_decisions_blob.txt", "wb").write(dec)
        print("  decisions blob dumped -> results/_r693bma_decisions_blob.txt")
    if sha_ord and wm_ord.upper() != h:
        open("results/_r693bma_group_orders_blob.txt", "wb").write(ordm)
        print("  group orders blob dumped -> results/_r693bma_group_orders_blob.txt")
else:
    print("GROUPTREE unavailable - D-19 legs SKIPPED (report honestly)")
if tmpd:
    shutil.rmtree(tmpd, ignore_errors=True)
