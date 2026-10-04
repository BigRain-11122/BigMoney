# -*- coding: utf-8 -*-
# r663 bm-b S0 pool settle + claim-regression check + S0.5 D-19 watermark + orders delta.
# Laws: r437 checkout-merge netpath; r626d per-face newer-wins (no blind whole-file
# replay for pool faces); r660 subprocess raw-bytes (zero PS pipe); r458 per-key
# hash-method (orders=SHA-1 40-hex, decisions=SHA-256 64-hex); r646 set-diff law.
import json, os, subprocess, sys, hashlib, tempfile, shutil, io, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))

out = {"probe": "r663bmb_s05", "machine": "bm-b"}

def silent(args, cwd=None):
    p = subprocess.run(args, cwd=cwd or REPO, capture_output=True)
    return p.returncode, p.stdout, p.stderr

# ---- 1) pool face settle (sync_face: shared+my lane -> merged view, idempotent)
import merge_lane_views as mlv  # noqa: E402

def claims(path):
    d = json.load(io.open(path, encoding="utf-8"))
    m = {}
    for e in d.get("entries", []):
        for s in e.get("shards", []) or []:
            m[(str(e.get("id")), str(s.get("key")))] = (s.get("status"), s.get("owner"), s.get("owner_since"))
    return m

PRE = os.path.join(os.environ.get("TEMP", "."), "r663_pool_pre.json")
try:
    pre = claims(PRE) if os.path.exists(PRE) else {}
    settle = {}
    for face in ("runnable_pool", "crash_fuse"):
        try:
            r = mlv.sync_face(face)
            settle[face] = str(r)[:200]
        except Exception as e:
            settle[face] = "ERR " + str(e)[:150]
    out["settle"] = settle
    post = claims(os.path.join(REPO, "results", "runnable_pool.json"))
    reg = []
    for k, (st, ow, ts) in pre.items():
        if k not in post:
            if st in ("running", "ready"):
                reg.append(["MISSING", k, st, ow, ts])
            continue
        pst, pow_, pts = post[k]
        if ow == "bm-b" and ts and (not pts or str(pts) < str(ts)):
            reg.append(["BACKWARD", k, [st, ow, ts], [pst, pow_, pts]])
    out["pre_claims"] = len(pre)
    out["post_claims"] = len(post)
    out["claim_regressions"] = reg[:20]
    out["trio"] = {str(k[0]): {"pre": pre.get(k), "post": post.get(k)}
                   for k in pre if k[0] and "P1-NULLS" in str(k[0])}
except Exception as e:
    out["settle_section_error"] = str(e)[:300]

# ---- 2) group tree decisions/orders watermark (r631 sparse-clone fallback)
gt = None
for cand in (r"K:\Fluxgroup\FluxGroup", r"C:\Fluxgroup\FluxGroup"):
    if os.path.isdir(os.path.join(cand, ".git")):
        gt = cand
        break
tmp = os.path.join(tempfile.gettempdir(), "fg-d19-bmb-r663")
out["group_tree"] = gt
try:
    if gt is None:
        if os.path.isdir(tmp):
            shutil.rmtree(tmp, ignore_errors=True)
        rc, so, se = silent(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                             "https://github.com/BigRain-11122/FluxGroup.git", tmp])
        if rc != 0:
            out["clone_err"] = se.decode("utf-8", "replace")[-300:]
            raise RuntimeError("clone_fail")
        rc, so, se = silent(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks",
                             "docs/decisions.md", "docs/orders.md"])
        if rc != 0:
            out["sparse_err"] = se.decode("utf-8", "replace")[-300:]
            raise RuntimeError("sparse_fail")
        gt = tmp
        out["group_tree"] = "sparse:" + tmp
    else:
        rc, so, se = silent(["git", "-C", gt, "fetch", "origin"])
        out["fetch_rc"] = rc
    blobs = {}
    for face in ("docs/decisions.md", "docs/orders.md"):
        rc, blob, se = silent(["git", "-C", gt, "show", "origin/main:" + face])
        if rc == 0:
            blobs[face] = blob
        else:
            out[face + "_err"] = se.decode("utf-8", "replace")[-200:]
    state = json.load(io.open("state.json", encoding="utf-8"))
    dec_sha = hashlib.sha256(blobs["docs/decisions.md"]).hexdigest().upper() if "docs/decisions.md" in blobs else None
    # per-key method: orders watermark is SHA-1 (40-hex in state), decisions SHA-256
    ord_sha1 = hashlib.sha1(blobs["docs/orders.md"]).hexdigest().upper() if "docs/orders.md" in blobs else None
    out["decisions_sha256"] = dec_sha
    out["orders_sha1"] = ord_sha1
    out["prev_decisions_sha"] = state.get("last_decisions_sha")
    out["prev_orders_sha"] = state.get("last_orders_sha")
    out["decisions_match"] = (dec_sha == state.get("last_decisions_sha"))
    out["orders_match"] = (ord_sha1 == state.get("last_orders_sha"))
    if not out["decisions_match"] and "docs/decisions.md" in blobs:
        text = blobs["docs/decisions.md"].decode("utf-8", "replace")
        lines = text.splitlines()
        hits = [l for l in lines if re.search(r"bm-b|BigMoney|quant", l, re.I)]
        out["decisions_bm_relevant_tail"] = hits[-15:]
    if not out["orders_match"] and "docs/orders.md" in blobs:
        text = blobs["docs/orders.md"].decode("utf-8", "replace")
        hits = [l for l in text.splitlines() if re.search(r"bm-b|BigMoney|quant", l, re.I)]
        out["group_orders_bm_relevant_tail"] = hits[-15:]
except RuntimeError as e:
    out["d19_stage"] = str(e)
except Exception as e:
    out["d19_error"] = str(e)[:300]

# ---- 3) bigmoney orders set-diff: ls-tree vs heartbeat ack (r646 same-scope law)
try:
    rc, lsout, _ = silent(["git", "ls-tree", "origin/main", "fleet/orders/"])
    order_files = sorted(ln.split("\t", 1)[1].strip() for ln in lsout.decode("utf-8", "replace").splitlines()
                         if "\t" in ln and "/O-" in ln)
    # also include untracked/not-yet-pushed local order files (same-scope filesystem set)
    local_files = sorted("fleet/orders/" + f for f in os.listdir(os.path.join(REPO, "fleet", "orders"))
                         if f.startswith("O-") and f.endswith(".md"))
    hb = json.load(io.open(os.path.join(REPO, "fleet", "machines", "bm-b.json"), encoding="utf-8"))
    ack = set(hb.get("orders_ack", []))
    unacked = [f.split("/")[-1] for f in order_files if f.split("/")[-1] not in ack]
    unacked_local = [f.split("/")[-1] for f in local_files if f.split("/")[-1] not in ack]
    out["orders_ls_tree_n"] = len(order_files)
    out["orders_local_n"] = len(local_files)
    out["orders_ack_n"] = len(ack)
    out["unacked_origin"] = unacked
    out["unacked_local"] = unacked_local
    out["ack_orphan"] = sorted(a for a in ack if ("fleet/orders/" + a) not in set(order_files) | set(local_files))
except Exception as e:
    out["orders_delta_error"] = str(e)[:300]

with io.open(os.path.join(REPO, "results", "_r663bmb_s05.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("SETTLE:", json.dumps(out.get("settle", {}), ensure_ascii=False)[:300])
print("REGR:", len(out.get("claim_regressions", [])), "| PRE:", out.get("pre_claims"), "POST:", out.get("post_claims"))
print("D19:", out.get("decisions_match"), out.get("orders_match"), "| ORDERS unacked_origin:", out.get("unacked_origin"), "unacked_local:", out.get("unacked_local"))
