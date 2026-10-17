"""r1038 bm-a: D-19 decisions/orders dual watermark check (fresh-read law).

Clone lineage _r686bmb_d19_check.py (T22 machine-aware state face) with the
bm-a tree list only: K: group tree (absent on bm-a) -> C:/Users/sjs20/Desktop/FluxGroup
real-path group tree (bm-a local tree, per state last_decisions_src lineage).
Hashing on git-show original bytes via subprocess capture (r660 law).
Writes results/_r1038bma_d19_check.json; exit 0 = checked, 2 = mechanism fault.
"""
import hashlib
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))  # results/
ROOT = os.path.dirname(REPO)


def resolve_state(root):
    mj = os.path.join(root, "fleet", "machine.json")
    try:
        with open(mj, encoding="utf-8") as f:
            mid = json.load(f)["machine_id"]
    except Exception as e:
        return None, None, "machine.json unreadable: %r" % e
    fname = "state.json" if mid == "bm-b" else "state-%s.json" % mid
    path = os.path.join(root, fname)
    return path, mid, None


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha1(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()


def method_for(wm: str) -> str:
    w = (wm or "").strip()
    return "sha1" if len(w) == 40 else "sha256"


def git_show(tree, path):
    r = subprocess.run(["git", "-C", tree, "show", "origin/main:%s" % path],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def main() -> int:
    out = {"trees_tried": [], "decisions_sha": None, "orders_sha": None,
           "wm_decisions": None, "wm_orders": None,
           "decisions_changed": None, "orders_changed": None, "err": None,
           "machine": None, "state_path": None}
    try:
        STATE, mid, s_err = resolve_state(ROOT)
        out["machine"] = mid
        out["state_path"] = STATE
        if s_err:
            out["err"] = s_err
            json.dump(out, open(os.path.join(
                REPO, "_r1038bma_d19_check.json"), "w", encoding="utf-8"),
                ensure_ascii=True, indent=1)
            print("FAULT: %s" % s_err)
            return 2
        st = json.load(open(STATE, encoding="utf-8"))
        out["wm_decisions"] = st.get("last_decisions_sha")
        out["wm_orders"] = st.get("last_orders_sha")
        trees = []
        k = r"K:\Fluxgroup\FluxGroup"
        if os.path.isdir(k):
            trees.append(("k-tree", k))
        bma = r"C:\Users\sjs20\Desktop\FluxGroup"
        if os.path.isdir(os.path.join(bma, ".git")):
            trees.append(("bma-local-tree", bma))
        blob_d = None
        blob_o = None
        for tag, tree in trees:
            out["trees_tried"].append(tag)
            subprocess.run(["git", "-C", tree, "fetch", "origin"],
                           capture_output=True)
            blob_d = git_show(tree, "docs/decisions.md")
            if blob_d is None:
                subprocess.run(["git", "-C", tree, "fetch", "origin", "main"],
                               capture_output=True)
                blob_d = git_show(tree, "docs/decisions.md")
            if blob_d is not None:
                blob_o = git_show(tree, "docs/orders.md")
                break
        if blob_d is None:
            out["err"] = "no group tree reachable (K: absent + bm-a local tree absent)"
            json.dump(out, open(os.path.join(
                REPO, "_r1038bma_d19_check.json"), "w", encoding="utf-8"),
                ensure_ascii=True, indent=1)
            print("FAULT: %s" % out["err"])
            return 2
        m_d = method_for(out["wm_decisions"])
        m_o = method_for(out["wm_orders"])
        out["decisions_method"] = m_d
        out["orders_method"] = m_o
        out["decisions_sha"] = (sha256(blob_d) if m_d == "sha256" else sha1(blob_d)) if blob_d else None
        out["orders_sha"] = (sha256(blob_o) if m_o == "sha256" else sha1(blob_o)) if blob_o else None
        out["decisions_changed"] = (
            (out["decisions_sha"] or "").lower()
            != (out["wm_decisions"] or "").lower())
        out["orders_changed"] = (
            (out["orders_sha"] or "").lower()
            != (out["wm_orders"] or "").lower())
        if out["decisions_changed"]:
            open(os.path.join(REPO, "_r1038bma_decisions_fresh.md"), "wb").write(blob_d)
        if out["orders_changed"] and blob_o is not None:
            open(os.path.join(REPO, "_r1038bma_orders_fresh.md"), "wb").write(blob_o)
    except Exception as e:
        out["err"] = repr(e)
        json.dump(out, open(os.path.join(REPO, "_r1038bma_d19_check.json"),
                            "w", encoding="utf-8"), ensure_ascii=True, indent=1)
        return 2
    json.dump(out, open(os.path.join(REPO, "_r1038bma_d19_check.json"), "w",
                        encoding="utf-8"), ensure_ascii=True, indent=1)
    print(json.dumps({k: out[k] for k in
                      ("decisions_changed", "orders_changed",
                       "decisions_sha", "wm_decisions",
                       "orders_sha", "wm_orders",
                       "decisions_method", "orders_method", "trees_tried")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
