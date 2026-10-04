"""r659 S0.5/S0.6 probe: group decisions/orders D-19 content-address check + orders delta (same-scope ls-tree)."""
import json, subprocess, hashlib, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # bigmoney root

def silent(args, cwd=None):
    p = subprocess.run(args, cwd=cwd, capture_output=True)
    return p.returncode, p.stdout, p.stderr

# group tree preferred; absent -> temp sparse clone fallback (D-20261004-02(3), r631 recipe)
gt = None
for cand in (r"K:\Fluxgroup\FluxGroup", r"C:\Fluxgroup\FluxGroup"):
    if os.path.isdir(os.path.join(cand, ".git")):
        gt = cand
        break
res = {"group_tree": gt}
tmp = os.path.join(os.environ.get("TEMP", "."), "fg-d19-r659bmb")
if gt is None:
    if os.path.isdir(tmp):
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    rc, out, err = silent(["git", "clone", "--depth", "1", "--filter=blob:none",
                           "--sparse", "https://github.com/BigRain-11122/FluxGroup.git", tmp])
    res["clone_rc"] = rc
    if rc != 0:
        print(json.dumps({"d19": "CLONE_FAIL", "err": err.decode("utf-8", "replace")[-300:], **res}, ensure_ascii=False))
        sys.exit(0)
    gt = tmp
    res["group_tree"] = "sparse:" + tmp

rc, _, err = silent(["git", "-C", gt, "fetch", "origin"])
res["fetch_rc"] = rc
if rc != 0:
    res["fetch_err_tail"] = err.decode("utf-8", "replace")[-200:]

for face, key in (("docs/decisions.md", "decisions"), ("docs/orders.md", "orders")):
    rc, out, err = silent(["git", "-C", gt, "show", "origin/main:" + face])
    if rc == 0:
        res[key + "_sha256"] = hashlib.sha256(out).hexdigest().upper()
    else:
        res[key + "_error"] = err.decode("utf-8", "replace")[-200:]

# orders delta: same-scope ls-tree vs heartbeat ack (r646 law)
rc, out, err = silent(["git", "ls-tree", "origin/main", "fleet/orders/"])
order_files = sorted(
    ln.split("\t", 1)[1].strip() for ln in out.decode("utf-8", "replace").splitlines()
    if "\t" in ln and "/O-" in ln
)
hb = json.load(open(os.path.join(REPO, "fleet", "machines", "bm-b.json"), encoding="utf-8"))
ack = sorted(hb.get("orders_ack", []))
res["orders_ls_tree_n"] = len(order_files)
res["orders_ack_n"] = len(ack)
res["unacked"] = [f for f in order_files if f.replace("fleet/orders/", "") not in hb.get("orders_ack", [])]
res["ack_orphan"] = [a for a in hb.get("orders_ack", []) if "fleet/orders/" + a not in order_files]

# compare with state watermark
st = json.load(open(os.path.join(REPO, "state.json"), encoding="utf-8"))
res["prev_decisions_sha"] = st.get("last_decisions_sha")
res["prev_orders_sha"] = st.get("last_orders_sha")
res["decisions_match"] = res.get("decisions_sha256") == st.get("last_decisions_sha")
res["orders_match"] = res.get("orders_sha256") == st.get("last_orders_sha")
print(json.dumps(res, ensure_ascii=False, indent=1))
