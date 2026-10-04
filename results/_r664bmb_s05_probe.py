# -*- coding: utf-8 -*-
# r664 bm-b S0.5 probe: D-19 decisions watermark (sparse-clone origin-blob route, r631/r661 recipe;
#     C: real path exists but has no .git -> git-tree route unavailable)
# + orders diff (same-caliber ls-tree vs heartbeat ack, r646 law)
import json, subprocess, io, hashlib, re, sys, tempfile, shutil, os

GRP_URL = "git@github.com:BigRain-11122/FluxGroup.git"
tmp = os.path.join(tempfile.gettempdir(), "fg-d19-bmb-r664")
out = {"machine": "bm-b", "round": 664}

def run(cmd, cwd=None):
    p = subprocess.run(cmd, capture_output=True, cwd=cwd)
    return p.returncode, p.stdout, p.stderr

# --- leg 1: D-19 decisions watermark ---
try:
    if os.path.exists(tmp):
        shutil.rmtree(tmp, ignore_errors=True)
    rc, so, se = run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", GRP_URL, tmp])
    if rc == 0:
        rc, so, se = run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks",
                          "docs/decisions.md", "docs/orders.md"])
    if rc != 0:
        out["decisions"] = {"stage": "clone/sparse", "rc": rc, "err": se.decode("utf-8", "replace")[-300:]}
    else:
        p = subprocess.run(["git", "-C", tmp, "show", "HEAD:docs/decisions.md"], capture_output=True)
        if p.returncode != 0:
            out["decisions"] = {"stage": "show", "rc": p.returncode, "err": p.stderr.decode("utf-8", "replace")[-300:]}
        else:
            blob = p.stdout
            new_sha = hashlib.sha256(blob).hexdigest().upper()
            state = json.load(open("state.json", encoding="utf-8"))
            old_sha = (state.get("last_decisions_sha") or "").upper()
            verdict = "MATCH" if new_sha == old_sha else "CHANGED"
            text = blob.decode("utf-8", "replace")
            lines = text.splitlines()
            hits = [l for l in lines if re.search(r"bm-b|BigMoney|quant", l, re.I) and re.match(r"^[-*]?\s*[-*]?\s*(D-|20\d\d)", l)]
            out["decisions"] = {
                "old_sha": old_sha, "new_sha": new_sha, "verdict": verdict,
                "total_lines": len(lines), "bm_relevant_lines": hits[-12:],
            }
        # group orders.md leg (per-key method: SHA-1 40-hex, r458 law)
        p2 = subprocess.run(["git", "-C", tmp, "show", "HEAD:docs/orders.md"], capture_output=True)
        if p2.returncode != 0:
            out["group_orders"] = {"stage": "show", "rc": p2.returncode,
                                  "err": p2.stderr.decode("utf-8", "replace")[-200:]}
        else:
            ob = p2.stdout
            o_sha1 = hashlib.sha1(ob).hexdigest().upper()
            st2 = json.load(open("state.json", encoding="utf-8"))
            o_old = (st2.get("last_orders_sha") or "").upper()
            o_verdict = "MATCH" if o_sha1 == o_old else "CHANGED"
            o_text = ob.decode("utf-8", "replace")
            o_hits = [l for l in o_text.splitlines() if re.search(r"bm-b|BigMoney|quant", l, re.I)]
            out["group_orders"] = {
                "old_sha": o_old, "new_sha": o_sha1, "verdict": o_verdict,
                "bm_relevant_tail": o_hits[-15:],
            }
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# --- leg 2: orders diff vs heartbeat ack (same caliber both sides) ---
p = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", "fleet/orders/"], capture_output=True)
names = [l for l in p.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
all_orders = set(n.split("/")[-1] for n in names if n.split("/")[-1].startswith("O-") and n.endswith(".md"))
hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
acked = set(hb.get("orders_ack", []))
missing = sorted(all_orders - acked)
out["orders"] = {
    "total_orders_on_origin": len(all_orders), "acked_count": len(acked),
    "missing_unacked": missing, "acked_but_not_on_origin": sorted(acked - all_orders),
}

with io.open("results/_r664bmb_s05_probe.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("D19:", out.get("decisions", {}).get("verdict", "ERR"),
      "| GRP_ORDERS:", out.get("group_orders", {}).get("verdict", "ERR"),
      "| ORDERS_MISSING:", len(missing), missing)
