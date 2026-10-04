"""r501 bm-c: S0.5 = D-19 decisions/orders dual watermark check (fresh-read law)
+ fleet orders ack diff (ls-tree tree-ish form, full-filename same-shape law r477).

D-19 leg: copy of _r698bmb_d19_check.py lineage (r503 case-normalize, r458/r672
per-key method self-evidence by value length, D-20261004-02(3) fallback chain,
r660 subprocess raw-bytes). Orders-diff leg: ls-tree HEAD:fleet/orders (r696b
tree-ish law), O-*.md filter, same-shape set comparison vs heartbeat orders_ack.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.abspath(__file__))  # results/
ROOT = os.path.dirname(REPO)
STATE = os.path.join(ROOT, "state-bm-c.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
TAG = "_r501bmc"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha1(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()


def method_for(wm: str) -> str:
    w = (wm or "").strip()
    return "sha1" if len(w) == 40 else "sha256"


def git_show(tree: str, path: str):
    r = subprocess.run(["git", "-C", tree, "show", "origin/main:%s" % path],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def main() -> int:
    out = {"trees_tried": [], "decisions_sha": None, "orders_sha": None,
           "wm_decisions": None, "wm_orders": None,
           "decisions_changed": None, "orders_changed": None,
           "fleet_orders_total": None, "fleet_unacked": [], "err": None}
    try:
        st = json.load(open(STATE, encoding="utf-8"))
        out["wm_decisions"] = st.get("last_decisions_sha")
        out["wm_orders"] = st.get("last_orders_sha")
        trees = []
        k = r"K:\Fluxgroup\FluxGroup"
        if os.path.isdir(k):
            trees.append(("k-tree", k))
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
            tmp = tempfile.mkdtemp(prefix="d19r501_")
            url_ssh = "git@github.com:BigRain-11122/FluxGroup.git"
            url_https = "https://github.com/BigRain-11122/FluxGroup.git"
            tw = os.path.join(tmp, "fg")
            ok = False
            for u in (url_ssh, url_https):
                r = subprocess.run(["git", "clone", "--depth", "1",
                                    "--filter=blob:none", "--sparse", u, tw],
                                   capture_output=True)
                if r.returncode == 0:
                    ok = True
                    break
            if not ok:
                out["err"] = "all clone urls failed"
                json.dump(out, open(os.path.join(
                    REPO, TAG + "_s05.json"), "w", encoding="utf-8"),
                    ensure_ascii=True, indent=1)
                return 2
            subprocess.run(["git", "-C", tw, "sparse-checkout", "set",
                           "--skip-checks", "docs/decisions.md"],
                          capture_output=True)
            blob_d = git_show(tw, "docs/decisions.md")
            blob_o = git_show(tw, "docs/orders.md")
            out["trees_tried"].append("sparse-clone")
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
            (out["orders_sha"] or "").lower() != (out["wm_orders"] or "").lower())
        if out["decisions_changed"] and blob_d is not None:
            open(os.path.join(REPO, TAG + "_decisions_fresh.md"),
                 "wb").write(blob_d)
        if out["orders_changed"] and blob_o is not None:
            open(os.path.join(REPO, TAG + "_orders_fresh.md"),
                 "wb").write(blob_o)
        # --- fleet orders ack diff (same-shape full-filename sets) ---
        r = subprocess.run(["git", "-C", ROOT, "ls-tree", "--name-only",
                            "HEAD:fleet/orders"], capture_output=True)
        if r.returncode == 0:
            fleet = set(x for x in r.stdout.decode("utf-8", "replace")
                        .splitlines() if re.match(r"^O-.*\.md$", x))
            hb = json.load(open(HEART, encoding="utf-8-sig"))
            ack = set(a for a in hb.get("orders_ack", []) if a != "README.md")
            out["fleet_orders_total"] = len(fleet)
            out["fleet_unacked"] = sorted(fleet - ack)
            out["ack_extra"] = sorted(ack - fleet)
    except Exception as e:
        out["err"] = repr(e)
        json.dump(out, open(os.path.join(REPO, TAG + "_s05.json"), "w",
                     encoding="utf-8"), ensure_ascii=True, indent=1)
        return 2
    json.dump(out, open(os.path.join(REPO, TAG + "_s05.json"), "w",
                  encoding="utf-8"), ensure_ascii=True, indent=1)
    print(json.dumps({k: out.get(k) for k in
                      ("decisions_changed", "orders_changed",
                       "decisions_sha", "orders_sha",
                       "fleet_orders_total", "fleet_unacked",
                       "ack_extra", "err")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
