"""r686 bm-b: D-19 decisions/orders dual watermark check (fresh-read law).

Group tree read path (D-20261004-02③): prefer K: group tree; fallback any
local group tree real path; else temp sparse clone of origin blob. All
hashing on git-show original bytes via subprocess capture (r660 law).
Writes results/_r686bmb_d19_check.json; exit 0 = checked, 2 = mechanism fault.

T22 (2026-10-10 r954 bm-a): state read is machine-context aware -- resolve
from fleet/machine.json (bm-b -> state.json legacy, others -> state-<id>.json,
r582 law); the module no longer hardcodes state.json. --state argv (injected
by d19_watermark.py cmd_probe/cmd_update) and D19_STATE env override the path,
but the basename MUST equal the machine-derived filename -- mismatch is a
mechanism fault (state-<id> read = the single legal watermark assertion
anchor; the r953 defect face was this probe reporting bm-b's watermark).
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.abspath(__file__))  # results/
ROOT = os.path.dirname(REPO)


def resolve_state(root, argv_state=None):
    """T22 machine-context law: state read = state-<machine_id>.json
    (bm-b = state.json legacy, r582). argv --state wins (caller-injected,
    e.g. d19_watermark.py), then D19_STATE env, then machine.json derive.
    Returns (state_path, machine_id, err); basename mismatch -> err."""
    mj = os.path.join(root, "fleet", "machine.json")
    try:
        with open(mj, encoding="utf-8") as f:
            mid = json.load(f)["machine_id"]
    except Exception as e:
        return None, None, "machine.json unreadable: %r" % e
    fname = "state.json" if mid == "bm-b" else "state-%s.json" % mid
    path = argv_state or os.environ.get("D19_STATE") or os.path.join(root, fname)
    if os.path.basename(path) != fname:
        return path, mid, ("state/machine mismatch: --state %s but machine %s "
                          "expects %s" % (path, mid, fname))
    return path, mid, None


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha1(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()


def method_for(wm: str) -> str:
    """Per-key method self-evidence (r458/r672): watermark length picks the
    hash family -- 40-hex = SHA-1 (orders key), 64-hex = SHA-256 (decisions)."""
    w = (wm or "").strip()
    return "sha1" if len(w) == 40 else "sha256"


def git_show(tree: str, path: str):
    r = subprocess.run(["git", "-C", tree, "show", "origin/main:%s" % path],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def main() -> int:
    argv_state = None
    if len(sys.argv) > 2 and sys.argv[1] == "--state":
        argv_state = sys.argv[2]
    elif "--state" in sys.argv:
        i = sys.argv.index("--state")
        if i + 1 < len(sys.argv):
            argv_state = sys.argv[i + 1]
    out = {"trees_tried": [], "decisions_sha": None, "orders_sha": None,
           "wm_decisions": None, "wm_orders": None,
           "decisions_changed": None, "orders_changed": None, "err": None,
           "machine": None, "state_path": None}
    try:
        STATE, mid, s_err = resolve_state(ROOT, argv_state)
        out["machine"] = mid
        out["state_path"] = STATE
        if s_err:
            out["err"] = s_err
            json.dump(out, open(os.path.join(
                REPO, "_r686bmb_d19_check.json"), "w", encoding="utf-8"),
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
        for cand in (r"C:\Fluxgroup\FluxGroup",):
            if os.path.isdir(os.path.join(cand, ".git")):
                trees.append(("local-tree", cand))
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
            # sparse clone fallback (r631 recipe)
            tmp = tempfile.mkdtemp(prefix="d19r686_")
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
                    REPO, "_r686bmb_d19_check.json"), "w", encoding="utf-8"),
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
        if blob_d is not None:
            # dump full decision text for consumption if changed
            if out["decisions_changed"]:
                open(os.path.join(REPO, "_r686bmb_decisions_fresh.md"),
                     "wb").write(blob_d)
            if out["orders_changed"] and blob_o is not None:
                open(os.path.join(REPO, "_r686bmb_orders_fresh.md"),
                     "wb").write(blob_o)
    except Exception as e:  # mechanism fault -> report honestly
        out["err"] = repr(e)
        json.dump(out, open(os.path.join(REPO, "_r686bmb_d19_check.json"),
                            "w", encoding="utf-8"),
                  ensure_ascii=True, indent=1)
        return 2
    json.dump(out, open(os.path.join(REPO, "_r686bmb_d19_check.json"), "w",
                        encoding="utf-8"), ensure_ascii=True, indent=1)
    print(json.dumps({k: out[k] for k in
                      ("decisions_changed", "orders_changed",
                       "decisions_sha", "wm_decisions",
                       "orders_sha", "wm_orders",
                       "decisions_method", "orders_method")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
