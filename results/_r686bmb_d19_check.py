"""r686 bm-b: D-19 decisions/orders dual watermark check (fresh-read law).

Group tree read path (D-20261004-02③): prefer K: group tree; fallback any
local group tree real path; else temp sparse clone of origin blob. All
hashing on git-show original bytes via subprocess capture (r660 law).
Writes results/_r686bmb_d19_check.<machine>.json (r1081 per-machine law:
shared tracked path was a three-machine overwrite race, live-fire pop-UU
bm-a vs bm-c r1121); exit 0 = checked, 2 = mechanism fault.

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


def _watermark_differs(full: str, wm: str) -> bool:
    """Prefix-aware delta test (r1111): the stored watermark is a truncation of
    the full digest (8 hex chars in state-bm-a.json), so a plain string compare
    reports 'changed' on EVERY round -- a false P0 that makes the whole S0.5
    board look new. Compare the shorter string against the longer one's prefix;
    only a real digest difference counts as a delta."""
    a = (full or "").strip().lower()
    b = (wm or "").strip().lower()
    if not a or not b:
        return True
    if len(a) >= len(b):
        return not a.startswith(b)
    return not b.startswith(a)


def _parse_triple(v):
    """D-20261024-03 shape: <sha16>@<commit7>/<bytes>. Returns tuple or None."""
    if not isinstance(v, str):
        return None
    w = v.strip()
    if "@" not in w or "/" not in w:
        return None
    sha, rest = w.split("@", 1)
    commit, _, nbytes = rest.partition("/")
    if len(sha) != 16 or len(commit) not in (7, 40) or not nbytes.isdigit():
        return None
    if not all(c in "0123456789abcdefABCDEF" for c in sha + commit):
        return None
    return (sha.lower(), commit.lower(), int(nbytes))


def _watermark_changed(full, wm, triple, wm_triple):
    """Triple-first delta test (D-20261024-03): compare commit+length, then
    digest. Falls back to the r1111 prefix test when no stored triple exists,
    so machines mid-migration keep their zero-false-P0 behaviour."""
    t = _parse_triple(triple)
    wt = _parse_triple(wm_triple)
    if t and wt:
        if t[1] != wt[1] or t[2] != wt[2]:
            return True
        return not t[0].startswith(wt[0])
    return _watermark_differs(full, wm)


# D-20261025-08 v2 four-tuple: {repo, commit_sha, blob_bytes, sha256}.
# A content digest alone cannot tell "content changed" from "read a stale
# branch / rewritten history" -- the ghost-watermark family (bm-b r1142/r1145
# could not reproduce a stored DEC sha at origin, so the advance target was a
# phantom). The source trio is what makes a digest reproducible; the digest
# stays as the content fingerprint.
QUAD_PREFIX = "v2:"


def _parse_quad(v):
    """v2:<repo>@<commit40>/<bytes>#<sha64>. Returns tuple or None."""
    if not isinstance(v, str):
        return None
    w = v.strip()
    if not w.startswith(QUAD_PREFIX):
        return None
    body = w[len(QUAD_PREFIX):]
    if "@" not in body or "/" not in body or "#" not in body:
        return None
    repo, rest = body.split("@", 1)
    commit, rest2 = rest.split("/", 1)
    nbytes, _, sha = rest2.partition("#")
    if not repo or len(commit) != 40 or not nbytes.isdigit() or len(sha) != 64:
        return None
    if not all(c in "0123456789abcdefABCDEF" for c in commit + sha):
        return None
    return (repo, commit.lower(), int(nbytes), sha.lower())


def quad_status(new_quad, wm_quad):
    """Compare a freshly read quad against the stored one.

      migrating     no stored v2 quad yet (legacy keys rule) -- honest
      same          all four equal
      source_ahead  same repo, same content, newer commit -> safe to advance
      delta         content differs (blob_bytes or sha256) -> real delta
      stale         repo differs or candidate unparseable -> hold; never
                    advance on an unreproducible watermark
    """
    t = _parse_quad(new_quad)
    wt = _parse_quad(wm_quad)
    if wt is None:
        return "migrating", "no stored v2 quad"
    if t is None:
        return "stale", "candidate quad unparseable"
    if t[0] != wt[0]:
        return "stale", "repo mismatch: %r != %r" % (t[0], wt[0])
    if t[2] != wt[2] or t[3] != wt[3]:
        return "delta", "content differs (bytes %d->%d)" % (wt[2], t[2])
    if t[1] != wt[1]:
        return "source_ahead", "same content, newer commit %s" % t[1][:7]
    return "same", "all four equal"


def repo_id(tree: str):
    """owner/name from the origin url, so the watermark is portable across
    all three read paths (K: drive tree, C: tree, temp sparse clone)."""
    r = subprocess.run(["git", "-C", tree, "remote", "get-url", "origin"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    u = r.stdout.decode("utf-8", "replace").strip()
    if u.endswith(".git"):
        u = u[:-4]
    for sep in ("github.com:", "github.com/"):
        if sep in u:
            return u.split(sep, 1)[1]
    parts = [p for p in u.replace("\\", "/").split("/") if p]
    return "/".join(parts[-2:]) if len(parts) >= 2 else None


def git_show_at(tree: str, commit: str, path: str):
    r = subprocess.run(["git", "-C", tree, "show", "%s:%s" % (commit, path)],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def verify_stored(quad, tree, path):
    """D-20261025-08 acceptance leg: the STORED quad must reproduce the same
    blob at its own commit. This is the check that catches a ghost watermark
    (a digest that no commit in the group repo ever produced), which no
    forward comparison can see.

      absent          no stored quad (migrating)
      reproducible    blob at <commit>:<path> hashes to the stored digest
      not_reproducible history was rewritten / the quad is a phantom
      commit_absent   commit not in this clone (shallow/pruned) -> unprovable
      unverifiable    no tree, or the path is missing at that commit
    """
    t = _parse_quad(quad)
    if t is None:
        return "absent", "no stored quad"
    if not tree:
        return "unverifiable", "no group tree available"
    repo, commit, nbytes, sha = t
    r = subprocess.run(["git", "-C", tree, "cat-file", "-e",
                        commit + "^{commit}"], capture_output=True)
    if r.returncode != 0:
        return "commit_absent", "commit %s not in this clone" % commit[:7]
    b = git_show_at(tree, commit, path)
    if b is None:
        return "unverifiable", "path %s absent at %s" % (path, commit[:7])
    if len(b) != nbytes or sha256(b) != sha:
        return "not_reproducible", (
            "blob at %s:%s is %dB/%s, stored quad says %dB/%s"
            % (commit[:7], path, len(b), sha256(b)[:16], nbytes, sha[:16]))
    return "reproducible", "blob at %s:%s matches the stored quad" % (
        commit[:7], path)


def _v2_first_changed(v2_status, full_sha, wm_legacy, legacy_changed):
    """Content-first delta verdict (D-20261025-08).
      same / source_ahead -> NOT a delta: the blob bytes are identical, only
                             the origin tip moved (an unrelated commit).
      delta               -> real delta.
      migrating           -> fall back to the legacy content digest test (the
                             stored key holds a full digest), never the
                             commit-first triple.
      stale               -> keep the legacy verdict: a watermark we cannot
                             reproduce must never be read as 'nothing new'.
    """
    if v2_status in ("same", "source_ahead"):
        return False
    if v2_status == "delta":
        return True
    if v2_status == "migrating":
        return _watermark_differs(full_sha, wm_legacy)
    return legacy_changed


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
                REPO, "_r686bmb_d19_check.%s.json" % mid), "w", encoding="utf-8"),
                ensure_ascii=True, indent=1)
            print("FAULT: %s" % s_err)
            return 2
        st = json.load(open(STATE, encoding="utf-8"))
        out["wm_decisions"] = st.get("last_decisions_sha")
        out["wm_orders"] = st.get("last_orders_sha")
        # D-20261024-03 (triple watermark): <sha16>@<commit7>/<bytes>.
        # Additive: legacy prefix keys keep their behaviour; when a triple is
        # present the comparison becomes commit+length first, digest second.
        out["wm_decisions_triple"] = st.get("last_decisions_watermark")
        out["wm_orders_triple"] = st.get("last_orders_watermark")
        # D-20261025-08: v2 source-anchored quads (additive; legacy keys rule
        # until a quad exists, so mid-migration machines stay honest).
        out["wm_decisions_quad"] = st.get("last_decisions_watermark_v2")
        out["wm_orders_quad"] = st.get("last_orders_watermark_v2")
        trees = []
        k = r"K:\Fluxgroup\FluxGroup"
        if os.path.isdir(k):
            trees.append(("k-tree", k))
        for cand in (r"C:\Fluxgroup\FluxGroup",):
            if os.path.isdir(os.path.join(cand, ".git")):
                trees.append(("local-tree", cand))
        blob_d = None
        blob_o = None
        tree_used = None
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
                tree_used = tree
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
                    REPO, "_r686bmb_d19_check.%s.json" % mid), "w", encoding="utf-8"),
                    ensure_ascii=True, indent=1)
                return 2
            subprocess.run(["git", "-C", tw, "sparse-checkout", "set",
                           "--skip-checks", "docs/decisions.md"],
                          capture_output=True)
            blob_d = git_show(tw, "docs/decisions.md")
            blob_o = git_show(tw, "docs/orders.md")
            tree_used = tw
            out["trees_tried"].append("sparse-clone")
        m_d = method_for(out["wm_decisions"])
        m_o = method_for(out["wm_orders"])
        out["decisions_method"] = m_d
        out["orders_method"] = m_o
        out["decisions_sha"] = (sha256(blob_d) if m_d == "sha256" else sha1(blob_d)) if blob_d else None
        out["orders_sha"] = (sha256(blob_o) if m_o == "sha256" else sha1(blob_o)) if blob_o else None
        commit7 = None
        if tree_used:
            r = subprocess.run(["git", "-C", tree_used, "rev-parse",
                                "--short=7", "origin/main"], capture_output=True)
            if r.returncode == 0:
                commit7 = r.stdout.decode("ascii", "replace").strip() or None
        out["origin_commit7"] = commit7
        commit40 = None
        if tree_used:
            r = subprocess.run(["git", "-C", tree_used, "rev-parse",
                                "origin/main"], capture_output=True)
            if r.returncode == 0:
                commit40 = r.stdout.decode("ascii", "replace").strip() or None
        out["origin_commit"] = commit40
        out["group_repo"] = repo_id(tree_used) if tree_used else None
        out["decisions_blob_bytes"] = len(blob_d) if blob_d is not None else None
        out["orders_blob_bytes"] = len(blob_o) if blob_o is not None else None
        # v2 quads are ALWAYS full sha256 (D-20261025-08), independent of the
        # legacy key's algorithm (an orders key may still be 40-hex SHA-1).
        out["decisions_sha256"] = sha256(blob_d) if blob_d is not None else None
        out["orders_sha256"] = sha256(blob_o) if blob_o is not None else None
        out["decisions_quad"] = (
            "v2:%s@%s/%d#%s" % (out["group_repo"], commit40, len(blob_d),
                                out["decisions_sha256"])
            if (out["group_repo"] and commit40 and blob_d is not None) else None)
        out["orders_quad"] = (
            "v2:%s@%s/%d#%s" % (out["group_repo"], commit40, len(blob_o),
                                out["orders_sha256"])
            if (out["group_repo"] and commit40 and blob_o is not None) else None)
        # Refetch commands: the D-20261025-08 acceptance leg is that a stored
        # quad reproduces the same blob -- the command ships with the receipt.
        out["refetch"] = {
            "decisions": ("git -C <group-tree> show %s:docs/decisions.md" % commit40)
                         if commit40 else None,
            "orders": ("git -C <group-tree> show %s:docs/orders.md" % commit40)
                      if commit40 else None,
        }
        out["decisions_triple"] = (
            "%s@%s/%d" % (out["decisions_sha"][:16], commit7, len(blob_d))
            if (out["decisions_sha"] and commit7 and blob_d is not None) else None)
        out["orders_triple"] = (
            "%s@%s/%d" % (out["orders_sha"][:16], commit7, len(blob_o))
            if (out["orders_sha"] and commit7 and blob_o is not None) else None)
        out["decisions_changed"] = _watermark_changed(
            out["decisions_sha"], out["wm_decisions"], out["decisions_triple"],
            out["wm_decisions_triple"])
        out["orders_changed"] = _watermark_changed(
            out["orders_sha"], out["wm_orders"], out["orders_triple"],
            out["wm_orders_triple"])
        out["decisions_compare_mode"] = (
            "triple" if _parse_triple(out["wm_decisions_triple"]) else "prefix")
        out["orders_compare_mode"] = (
            "triple" if _parse_triple(out["wm_orders_triple"]) else "prefix")
        # v2 status rides alongside (never replaces) the legacy delta verdict:
        # state/orders consumption still keys on *_changed, while the source
        # trio tells us whether the advance target is reproducible.
        out["decisions_v2_status"], out["decisions_v2_why"] = quad_status(
            out["decisions_quad"], out.get("wm_decisions_quad"))
        out["orders_v2_status"], out["orders_v2_why"] = quad_status(
            out["orders_quad"], out.get("wm_orders_quad"))
        out["v2_advance_blocked"] = [
            n for n, s in (("decisions", out["decisions_v2_status"]),
                           ("orders", out["orders_v2_status"])) if s == "stale"]
        out["v2_migrated"] = [n for n, s in
                              (("decisions", out["decisions_v2_status"]),
                               ("orders", out["orders_v2_status"]))
                              if s != "migrating"]
        # Stored-quad reproducibility (the acceptance leg) + the content-first
        # delta verdict. The legacy triple compares commit BEFORE digest, so an
        # unrelated group commit makes both files report "changed" every round
        # (observed live this window: dec/ord sha identical, changed=true).
        # Content identity is the only honest basis for "did I miss anything";
        # the source trio is used for reproducibility, not for delta.
        out["decisions_stored_repro"], out["decisions_repro_why"] = verify_stored(
            out.get("wm_decisions_quad"), tree_used, "docs/decisions.md")
        out["orders_stored_repro"], out["orders_repro_why"] = verify_stored(
            out.get("wm_orders_quad"), tree_used, "docs/orders.md")
        out["stale_watermarks"] = [
            n for n, s in (("decisions", out["decisions_stored_repro"]),
                           ("orders", out["orders_stored_repro"]))
            if s == "not_reproducible"]
        out["legacy_changed"] = {"decisions": out["decisions_changed"],
                                 "orders": out["orders_changed"]}
        out["decisions_changed"] = _v2_first_changed(
            out["decisions_v2_status"], out["decisions_sha"],
            out["wm_decisions"], out["legacy_changed"]["decisions"])
        out["orders_changed"] = _v2_first_changed(
            out["orders_v2_status"], out["orders_sha"],
            out["wm_orders"], out["legacy_changed"]["orders"])
        if blob_d is not None:
            # dump full decision text for consumption if changed
            if out["decisions_changed"]:
                open(os.path.join(REPO, "_r686bmb_decisions_fresh.%s.md" % mid),
                     "wb").write(blob_d)
            if out["orders_changed"] and blob_o is not None:
                open(os.path.join(REPO, "_r686bmb_orders_fresh.%s.md" % mid),
                     "wb").write(blob_o)
    except Exception as e:  # mechanism fault -> report honestly
        out["err"] = repr(e)
        json.dump(out, open(os.path.join(REPO, "_r686bmb_d19_check.%s.json" % mid),
                            "w", encoding="utf-8"),
                  ensure_ascii=True, indent=1)
        return 2
    json.dump(out, open(os.path.join(REPO, "_r686bmb_d19_check.%s.json" % mid), "w",
                        encoding="utf-8"), ensure_ascii=True, indent=1)
    summary_keys = ("decisions_changed", "orders_changed",
                    "decisions_sha", "wm_decisions",
                    "orders_sha", "wm_orders",
                    "decisions_method", "orders_method",
                    "decisions_triple", "orders_triple",
                    "decisions_compare_mode", "orders_compare_mode",
                    "decisions_v2_status", "orders_v2_status",
                    "v2_advance_blocked", "group_repo", "origin_commit",
                    "decisions_stored_repro", "orders_stored_repro",
                    "stale_watermarks", "legacy_changed")
    print(json.dumps({k: out[k] for k in summary_keys}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
