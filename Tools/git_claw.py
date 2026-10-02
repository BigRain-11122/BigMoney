"""Tools/git_claw.py -- deletion-set ownership claw (D-20261002-04, T-144 legs 1+2).

LAW FACE: r519 family (r513/r525/r531/r540/r560/r574 -- six-plus live
offenders): whole-tree stale-base pushes and closeout sweeps deleted
peer-owned products from origin. The standing manual law ("pre-push
deletion-set self-proof, missing leg = push forbidden", F-20261001-03
lineage) becomes MECHANICAL here -- single source for both channels:

  * human/session + daemon pushes: Tools/git-hooks/pre-push (installed
    per machine by Tools/register_prepush_claw.ps1, mirrored by the S7
    self-heal line) -> CLI `check-push` below;
  * daemon in-code self-proof (belt under the hook): saturation_engine
    ledger_append_batch / autofill _staged_foreign_block / pool_worker
    _push_claims_and_ledger call these functions directly (r303
    single-source law: hooks and daemons never re-implement).

POLICY (fail-closed): deletions = files present in the OLD tree
(remote tip) and absent from the NEW tree (tip being pushed).
  * empty deletion set -> fast pass (the overwhelming common case;
    the claw adds one diff-tree per push, zero blob reads);
  * deleted blob carries owner evidence (audit.machine | machine |
    machine_id) == this machine -> allowed (self-owned yield/cleanup);
  * no owner evidence + allowlisted path (fleet/inbox/ move-to-
    processed pattern, r516 law) -> allowed;
  * everything else (foreign owner / no owner / unreadable blob) ->
    VIOLATION = push forbidden. Escape hatch: git push --no-verify
    (state the reason in the round report).

Exit codes: 0 normal, 1 violations (check-push), 2 mechanism fault.
Hermetic selftest: `python Tools/git_claw.py selftest` (temp repos,
real git binary, zero company-repo/network surface, r117 law).
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

# r516 law: inbox -> processed archive moves are the only no-owner
# deletion pattern with standing fleet precedent (r366 fixup face).
ALLOW_PREFIXES = ("fleet/inbox/",)

_ZERO = "0" * 40
_NO_WINDOW = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW


def _git(args, repo, timeout=60):
    """Zero-window git (U060/r317 discipline). bytes out (r568 law:
    never let a text layer translate what we hash/parse)."""
    return subprocess.run(["git", "-C", repo] + args,
                          capture_output=True, timeout=timeout,
                          creationflags=_NO_WINDOW)


def machine_id(repo=None):
    """This machine's fleet id (fleet/machine.json; honest fallback)."""
    repo = repo or os.getcwd()
    try:
        with open(os.path.join(repo, "fleet", "machine.json"),
                  encoding="utf-8") as fh:
            return str(json.load(fh).get("machine_id")
                       or os.environ.get("COMPUTERNAME", "unknown"))
    except Exception:
        return os.environ.get("COMPUTERNAME", "unknown")


def deleted_paths(old_sha, new_sha, repo):
    """Files present in old tree, absent from new tree (no-renames:
    a rename is a deletion face here, per the r519 family)."""
    if not old_sha or old_sha == _ZERO or old_sha == new_sha:
        return []
    r = _git(["diff-tree", "-r", "--no-renames", "--diff-filter=D",
              "--name-only", old_sha, new_sha], repo)
    if r.returncode != 0:
        raise RuntimeError("diff-tree rc=%d %s" % (
            r.returncode, (r.stderr or b"")[:160].decode(errors="replace")))
    return [l.strip().decode("utf-8", errors="replace")
            for l in (r.stdout or b"").splitlines() if l.strip()]


def blob_owner(path, sha, repo):
    """Owner evidence inside the deleted blob: audit.machine | machine |
    machine_id (product-face and engine-state shapes both covered).
    None = no owner evidence (caller decides allowlist vs violation)."""
    r = _git(["show", "%s:%s" % (sha, path)], repo)
    if r.returncode != 0:
        return "?"                       # unreadable -> never allow
    try:
        d = json.loads((r.stdout or b"").decode("utf-8", errors="replace"))
    except Exception:
        return None
    if not isinstance(d, dict):
        return None
    audit = d.get("audit")
    if isinstance(audit, dict) and audit.get("machine"):
        return str(audit["machine"])
    for k in ("machine", "machine_id"):
        if d.get(k):
            return str(d[k])
    return None


def deletion_violations(old_sha, new_sha, repo, mid=None):
    """The claw. Returns [] = push allowed; non-empty = forbidden.
    Fail-closed: any unreadable face inside is itself a violation."""
    if mid is None:
        mid = machine_id(repo)
    try:
        paths = deleted_paths(old_sha, new_sha, repo)
    except Exception as exc:
        return [{"path": "<diff-tree>", "reason": "unreadable: %r" % (exc,)}]
    out = []
    for p in paths:
        norm = p.replace("\\", "/")
        owner = blob_owner(p, old_sha, repo)
        if owner == "?":
            out.append({"path": p, "reason": "blob unreadable (fail-closed)"})
        elif owner is None:
            if not norm.startswith(ALLOW_PREFIXES):
                out.append({"path": p, "reason": "no owner evidence"})
        elif owner != mid:
            out.append({"path": p, "reason": "foreign owner %s" % owner})
    return out


def staged_deletions(repo):
    """Staged-index deletion face (tick commits never carry deletions:
    D-20261002-04 leg-2/3 daemon-side gate)."""
    r = _git(["diff", "--cached", "--no-renames", "--diff-filter=D",
              "--name-only"], repo)
    if r.returncode != 0:
        raise RuntimeError("staged diff rc=%d" % r.returncode)
    return [l.strip().decode("utf-8", errors="replace")
            for l in (r.stdout or b"").splitlines() if l.strip()]


def staged_paths(repo):
    """Staged-index path set (whole-index commit hazard: `git commit`
    commits the ENTIRE index -- staged set must equal the writer's own
    adds or the commit is deferred, r494/F-20261002-02 family)."""
    r = _git(["diff", "--cached", "--name-only"], repo)
    if r.returncode != 0:
        raise RuntimeError("staged diff rc=%d" % r.returncode)
    return [l.strip().decode("utf-8", errors="replace")
            for l in (r.stdout or b"").splitlines() if l.strip()]


def check_push(old_sha, new_sha, repo=None):
    viol = deletion_violations(old_sha, new_sha, repo or os.getcwd())
    if viol:
        print("PRE-PUSH CLAW: deletion set carries non-self-owned files "
              "(D-20261002-04, r519 family). Push FORBIDDEN.")
        for v in viol[:10]:
            print("  D %s -- %s" % (v["path"], v["reason"]))
        print("Escape hatch: git push --no-verify (state the reason in "
              "the round report).")
        return 1
    return 0


def selftest():
    """Hermetic: temp repos + real git binary, zero company surface."""
    fails = []
    n = [0]

    def leg(name, cond):
        n[0] += 1
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as td:
        repo = os.path.join(td, "repo")
        r = _git(["init", "-q", "--initial-branch=main", repo], td)
        ok_init = r.returncode == 0
        base = {
            "results/prod_other.json": '{"audit": {"machine": "bm-a"}}',
            "results/prod_self.json": '{"audit": {"machine": "bm-z"}}',
            "results/state_face.json": '{"machine_id": "bm-a"}',
            "results/prose.md": "# prose, no owner\n",
            "fleet/inbox/MSG-1.md": "# inbox msg, no owner\n",
            "results/keep.json": "{}",
        }
        for rel, text in base.items():
            fp = os.path.join(repo, *rel.split("/"))
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, "w", encoding="utf-8") as fh:
                fh.write(text)
        for a in (("add", "-A"),):
            _git(list(a), repo)
        _git(["-c", "user.name=st", "-c", "user.email=st@t",
              "commit", "-q", "-m", "base"], repo)
        old_sha = _git(["rev-parse", "HEAD"], repo).stdout.decode().strip()

        # no-deletion commit -> fast pass
        with open(os.path.join(repo, "results", "add1.json"), "w") as fh:
            fh.write("{}")
        _git(["add", "results/add1.json"], repo)
        _git(["-c", "user.name=st", "-c", "user.email=st@t",
              "commit", "-q", "-m", "add1"], repo)
        leg("init + base fixture", ok_init)
        leg("empty deletion set fast-pass",
            deletion_violations(old_sha, "HEAD", repo, mid="bm-z") == [])

        # delete faces: foreign product / self product / engine-state
        # shape / no-owner prose / allowlisted inbox move
        for rel in ("results/prod_other.json", "results/prod_self.json",
                    "results/state_face.json", "results/prose.md",
                    "fleet/inbox/MSG-1.md"):
            _git(["rm", "-q", "--", rel], repo)
        _git(["-c", "user.name=st", "-c", "user.email=st@t",
              "commit", "-q", "-m", "deletions"], repo)
        viol = deletion_violations(old_sha, "HEAD", repo, mid="bm-z")
        vpaths = {v["path"] for v in viol}
        vreason = {v["path"]: v["reason"] for v in viol}
        leg("foreign product blocked",
            "results/prod_other.json" in vpaths
            and vreason.get("results/prod_other.json", "").startswith(
                "foreign owner"))
        leg("engine-state machine_id shape blocked",
            "results/state_face.json" in vpaths)
        leg("no-owner prose blocked", "results/prose.md" in vpaths)
        leg("self-owned deletion allowed",
            "results/prod_self.json" not in vpaths)
        leg("inbox move-to-processed allowed",
            "fleet/inbox/MSG-1.md" not in vpaths)
        leg("kept file not flagged", "results/keep.json" not in vpaths)

        # staged-deletion face
        sd = staged_deletions(repo)
        leg("staged deletions empty on clean index", sd == [])
        _git(["rm", "-q", "--cached", "--", "results/keep.json"], repo)
        leg("staged deletion detected",
            staged_deletions(repo) == ["results/keep.json"])
        _git(["reset", "-q", "--", "results/keep.json"], repo)
        leg("staged-set paths readable", isinstance(
            staged_paths(repo), list))

        # CLI exit codes (check-push)
        leg("CLI check-push blocks (rc 1)",
            check_push(old_sha, "HEAD", repo) == 1)
        leg("CLI check-push same-sha pass (rc 0)",
            check_push("HEAD", "HEAD", repo) == 0)
        # new-branch face (old = zeros) = nothing to compare -> pass
        leg("new-branch zero-base pass",
            deletion_violations(_ZERO, "HEAD", repo, mid="bm-z") == [])

    # machine.json reader on the real tree (read-only environment fact)
    mid = machine_id(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    leg("machine.json reader", mid in ("bm-a", "bm-b", "bm-c"))

    print("selftest: %d/%d PASS" % (n[0] - len(fails), n[0]))
    if fails:
        print("FAIL: %r" % fails)
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description="deletion-set ownership claw")
    ap.add_argument("subcommand",
                    choices=["check-push", "selftest"])
    ap.add_argument("old_sha", nargs="?")
    ap.add_argument("new_sha", nargs="?")
    ap.add_argument("--repo", default=os.getcwd())
    a = ap.parse_args()
    if a.subcommand == "selftest":
        return selftest()
    if not a.old_sha or not a.new_sha:
        print("check-push needs <old_sha> <new_sha>")
        return 2
    try:
        return check_push(a.old_sha, a.new_sha, a.repo)
    except Exception as exc:
        print("claw mechanism fault: %r" % (exc,))
        return 2


if __name__ == "__main__":
    sys.exit(main())
