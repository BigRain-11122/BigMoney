# -*- coding: utf-8 -*-
"""r687 bm-a S0 pool-face probe (r474 newer-wins check; r446 probe-to-file law)"""
import json, subprocess, sys, io

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
POOL = "results/runnable_pool.json"
OUT = REPO + r"\results\_r687bma_pool_face_probe.json"

def load_origin_blob():
    b = subprocess.run(["git", "-C", REPO, "show", "origin/main:" + POOL],
                       capture_output=True)
    if b.returncode != 0:
        return None, b.stderr.decode("utf-8", "replace")
    return json.loads(b.stdout.decode("utf-8", "replace")), None

def load_local():
    with open(REPO + "\\" + POOL.replace("/", "\\"), "rb") as f:
        return json.loads(f.read().decode("utf-8", "replace"))

def entries_index(doc):
    idx = {}
    for e in doc.get("entries", []):
        key = e.get("key") or e.get("id")
        idx[key] = e
    return idx

def main():
    out = {}
    origin, err = load_origin_blob()
    if origin is None:
        out["error"] = "origin blob fetch failed: " + str(err)[:300]
        with io.open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print("ORIGIN_FETCH_FAIL")
        return 2
    local = load_local()
    oi, li = entries_index(origin), entries_index(local)
    out["origin_entries"] = len(oi)
    out["local_entries"] = len(li)
    only_local = sorted(set(li) - set(oi))
    only_origin = sorted(set(oi) - set(li))
    out["only_local_keys"] = only_local
    out["only_origin_keys"] = only_origin
    reg = []
    for k in sorted(set(oi) & set(li)):
        a, b = oi[k], li[k]
        if a.get("owner") != b.get("owner") or a.get("status") != b.get("status"):
            reg.append({"key": k, "origin": {x: a.get(x) for x in ("owner", "status")},
                        "local": {x: b.get(x) for x in ("owner", "status")}})
        os_o = str(a.get("owner_since") or "")
        os_l = str(b.get("owner_since") or "")
        if os_o and os_l and os_o > os_l:
            reg.append({"key": k, "origin_owner_since": os_o,
                        "local_owner_since": os_l,
                        "type": "local_older_owner_since"})
    out["deltas"] = reg[:80]
    out["delta_count"] = len(reg)
    out["only_local_detail"] = [
        {"key": k, "owner": li[k].get("owner"), "status": li[k].get("status"),
         "shard": li[k].get("shard")} for k in only_local[:40]]
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("WROTE", OUT)
    return 0

if __name__ == "__main__":
    sys.exit(main())
