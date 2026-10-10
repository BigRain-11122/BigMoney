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
  * qa/ deletion + same-push treasure_guard quarantine manifest
    whose moved[] lists the exact path with sha256 -> allowed
    (D-20261010-07 fourth release category: manifest = the deletion's
    self-proof; membership-only criterion, nothing else relaxed;
    no-manifest qa/ deletions stay forbidden -- fail-closed intact);
  * everything else (foreign owner / no owner / unreadable blob) ->
    VIOLATION = push forbidden. Escape hatch: git push --no-verify
    (state the reason in the round report).

POOL GATE (MSG-2026-10-03-0612 proposal-2, bm-b fleet proposal; live
fire = bm-a r609 db66e6c45 reland ring replayed a pre-ring S6 settle
snapshot of results/runnable_pool.json over a fresher base, rolling
shard owner_since 05:48:07 -> 05:28:07 and opening a 7.6min
takeover-eval window): the second leg refuses any push whose shared
pool shard owner_since goes BACKWARD between the remote tip and the
tip being pushed. Forward moves, new shards, shard removals, and a
pool face absent from either tree all pass; an unparseable pool blob
on a tree that carries it fails closed (same philosophy as the
deletion leg). Single source here; pre-push hook and daemon belts
inherit via check-push/check_push.

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

# D-20261010-07 fourth release category: qa/ rotation deletions are
# self-certified by a treasure_guard quarantine manifest riding in the
# SAME push (results/_quarantine/<ts>/manifest.json, moved[] carrying
# src+sha256 -- the legacy files[] shape has no sha256 face and does
# not qualify).
QUARANTINE_PREFIX = "results/_quarantine/"
QA_PREFIX = "qa/"

# Shared pool face gated by the MSG-2026-10-03-0612 proposal-2 leg.
POOL_PATH = "results/runnable_pool.json"

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
    a rename is a deletion face here, per the r519 family).
    r369 fix (first live-fire 2026-10-02 14:1x): the pre-push hook hands
    us the REMOTE tip sha, whose objects may not exist locally yet in a
    racing window -> diff-tree rc=128 'bad object' -> false-FORBIDDEN on
    an empty deletion set. Fetch-once-retry before failing closed; the
    remote tip is always advertised, so a plain fetch brings the tree."""
    if not old_sha or old_sha == _ZERO or old_sha == new_sha:
        return []
    args = ["diff-tree", "-r", "--no-renames", "--diff-filter=D",
            "--name-only", old_sha, new_sha]
    r = _git(args, repo)
    if r.returncode != 0:
        _git(["fetch", "origin"], repo)          # best-effort object bring-in
        r = _git(args, repo)
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


def quarantined_src_paths(new_sha, repo):
    """Union of moved[].src entries across every
    results/_quarantine/<ts>/manifest.json blob present in the tree
    being pushed (D-20261010-07: the manifest is the deletion's
    self-proof, so it must ride the SAME push). Only manifests whose
    moved[] entries carry both src and sha256 qualify; unreadable /
    shape-wrong / legacy-shape manifests contribute nothing
    (fail-closed per claim). Only invoked when the deletion set
    actually carries qa/ paths (zero cost on the common case)."""
    r = _git(["ls-tree", "-r", "--name-only", new_sha, "--",
              QUARANTINE_PREFIX], repo)
    if r.returncode != 0:
        return frozenset()
    out = set()
    for line in (r.stdout or b"").splitlines():
        rel = line.strip().decode("utf-8", errors="replace")
        if not rel.endswith("manifest.json"):
            continue
        b = _git(["show", "%s:%s" % (new_sha, rel)], repo)
        if b.returncode != 0:
            continue
        try:
            d = json.loads((b.stdout or b"").decode("utf-8",
                                                    errors="replace"))
        except Exception:
            continue
        moved = d.get("moved") if isinstance(d, dict) else None
        if not isinstance(moved, list):
            continue
        for m in moved:
            if (isinstance(m, dict) and m.get("src")
                    and m.get("sha256")):
                out.add(str(m["src"]).replace("\\", "/"))
    return frozenset(out)


def deletion_violations(old_sha, new_sha, repo, mid=None):
    """The claw. Returns [] = push allowed; non-empty = forbidden.
    Fail-closed: any unreadable face inside is itself a violation."""
    if mid is None:
        mid = machine_id(repo)
    try:
        paths = deleted_paths(old_sha, new_sha, repo)
    except Exception as exc:
        return [{"path": "<diff-tree>", "reason": "unreadable: %r" % (exc,)}]
    if any(p.replace("\\", "/").startswith(QA_PREFIX) for p in paths):
        certified = quarantined_src_paths(new_sha, repo)
    else:
        certified = frozenset()
    out = []
    for p in paths:
        norm = p.replace("\\", "/")
        if norm in certified:
            continue  # quarantine-manifest self-certified (D-20261010-07)
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


def _norm_ts(ts):
    """owner_since face normalization: ' ' and 'T' separators both in
    the wild (lane faces vs shared face writers) -> unify before the
    lexicographic compare so equal stamps compare equal."""
    return str(ts).strip().replace(" ", "T")


def _pool_owner_since_map(sha, repo):
    """{entry_id|shard_key: owner_since} for one tree sha.
    None = pool face absent from that tree (nothing to gate).
    r369 racing-window law: fetch-once-retry before judging rc!=0;
    after the retry, 'does not exist' -> absent, anything else ->
    unreadable = raise (fail-closed)."""
    r = _git(["show", "%s:%s" % (sha, POOL_PATH)], repo)
    if r.returncode != 0:
        _git(["fetch", "origin"], repo)          # best-effort bring-in
        r = _git(["show", "%s:%s" % (sha, POOL_PATH)], repo)
    if r.returncode != 0:
        err = (r.stderr or b"").decode("utf-8", errors="replace")
        # two Windows git faces for the same fact (path absent from the
        # tree): "path 'X' does not exist in 'sha'" (file also absent on
        # disk) vs "path 'X' exists on disk, but not in 'sha'" (file on
        # disk, absent from tree) -- both mean ABSENT, not unreadable.
        if "does not exist" in err or "but not in" in err:
            return None
        raise RuntimeError("pool blob unreadable rc=%d %s" % (
            r.returncode, err[:120]))
    try:
        d = json.loads((r.stdout or b"").decode("utf-8", errors="replace"))
    except Exception:
        raise RuntimeError("pool blob unparseable (fail-closed)")
    ents = d.get("entries") if isinstance(d, dict) else d
    if not isinstance(ents, list):
        raise RuntimeError("pool blob shape unexpected (fail-closed)")
    out = {}
    for e in ents:
        if not isinstance(e, dict):
            raise RuntimeError("pool entry non-dict (fail-closed)")
        eid = str(e.get("id"))
        shards = e.get("shards")
        if shards is None:
            continue
        if not isinstance(shards, list):
            raise RuntimeError("pool shards non-list (fail-closed)")
        for s in shards:
            if not isinstance(s, dict):
                raise RuntimeError("pool shard non-dict (fail-closed)")
            if s.get("owner_since"):
                out[eid + "|" + str(s.get("key"))] = str(s["owner_since"])
    return out


def pool_claim_regressions(old_sha, new_sha, repo):
    """MSG-2026-10-03-0612 proposal-2: shared-pool shard owner_since
    monotonicity. Any shard present in both trees whose owner_since
    moves BACKWARD between remote tip and pushed tip = violation
    (reland-ring whole-file replay family). Forward/new/removed
    shards pass; pool absent from either tree passes."""
    try:
        old_map = _pool_owner_since_map(old_sha, repo)
        new_map = _pool_owner_since_map(new_sha, repo)
    except Exception as exc:
        return [{"shard": "<pool-blob>",
                 "reason": "unreadable: %r" % (exc,)}]
    if not old_map or not new_map:
        return []
    out = []
    for k, new_ts in new_map.items():
        old_ts = old_map.get(k)
        if old_ts and _norm_ts(new_ts) < _norm_ts(old_ts):
            out.append({"shard": k, "reason":
                        "owner_since %s -> %s (backward, ring-replay "
                        "family, MSG-0612)" % (old_ts, new_ts)})
    return out


def check_push(old_sha, new_sha, repo=None):
    repo = repo or os.getcwd()
    viol = deletion_violations(old_sha, new_sha, repo)
    pool_viol = pool_claim_regressions(old_sha, new_sha, repo)
    if viol or pool_viol:
        print("PRE-PUSH CLAW: deletion set carries non-self-owned files "
              "(D-20261002-04, r519 family). Push FORBIDDEN.")
        for v in viol[:10]:
            print("  D %s -- %s" % (v["path"], v["reason"]))
        if pool_viol:
            print("PRE-PUSH CLAW: shared-pool shard owner_since went "
                  "BACKWARD (MSG-2026-10-03-0612 proposal-2, ring-replay "
                  "family). Push FORBIDDEN.")
            for v in pool_viol[:10]:
                print("  POOL %s -- %s" % (v["shard"], v["reason"]))
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

        # ---- MSG-0612 proposal-2: pool claim monotonicity legs ----
        def _tip():
            return _git(["rev-parse", "HEAD"], repo).stdout.decode().strip()

        def _commit_pool(text, msg):
            fp = os.path.join(repo, *POOL_PATH.split("/"))
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, "w", encoding="utf-8") as fh:
                fh.write(text)
            _git(["add", POOL_PATH], repo)
            _git(["-c", "user.name=st", "-c", "user.email=st@t",
                  "commit", "-q", "-m", msg], repo)

        def _pool_json(s1, extra=None):
            e = {"id": "E1", "shards": [
                {"key": "S1", "owner": "bm-z", "owner_since": s1,
                 "status": "claimed"}]}
            if extra:
                e["shards"].append(extra)
            return json.dumps({"version": "test", "entries": [e]})

        pre_pool_tip = _tip()
        _commit_pool(_pool_json("2026-10-03 10:00:00"), "pool1")
        p1 = _tip()
        leg("pool absent from old tree passes",
            pool_claim_regressions(pre_pool_tip, p1, repo) == [])
        _commit_pool(_pool_json("2026-10-03 10:20:00",
                                {"key": "S2", "owner": "bm-z",
                                 "owner_since": "2026-10-03 10:00:00",
                                 "status": "claimed"}), "pool2")
        p2 = _tip()
        leg("forward move + new shard passes",
            pool_claim_regressions(p1, p2, repo) == [])
        _commit_pool(_pool_json("2026-10-03 10:05:00"), "pool3")
        p3 = _tip()
        rv = pool_claim_regressions(p2, p3, repo)
        leg("backward owner_since blocked",
            len(rv) == 1 and rv[0]["shard"] == "E1|S1"
            and "backward" in rv[0]["reason"])
        _commit_pool("{ not json", "pool4")
        p4 = _tip()
        leg("unparseable pool blob fails closed",
            len(pool_claim_regressions(p3, p4, repo)) == 1)
        _commit_pool(_pool_json("2026-10-03 10:20:00"), "pool5")
        p5 = _tip()
        leg("pool restored forward passes",
            pool_claim_regressions(p3, p5, repo) == [])
        _commit_pool(_pool_json("2026-10-03T10:20:00"), "pool6")
        p6 = _tip()
        leg("mixed-separator equal stamps pass (norm)",
            pool_claim_regressions(p5, p6, repo) == [])
        leg("CLI check-push pool regression blocks (rc 1)",
            check_push(p2, p3, repo) == 1)
        leg("CLI check-push pool forward passes (rc 0)",
            check_push(p1, p2, repo) == 0)

        # ---- D-20261010-07: quarantine manifest self-certification ----
        def _commit_qa_file(rel, text):
            fp = os.path.join(repo, *rel.split("/"))
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, "w", encoding="utf-8") as fh:
                fh.write(text)
            _git(["add", rel], repo)
            _git(["-c", "user.name=st", "-c", "user.email=st@t",
                  "commit", "-q", "-m", "qa fixture"], repo)
            return _tip()

        qa_base = _commit_qa_file("qa/old-r1.png", "png-bytes-r1")
        _git(["rm", "-q", "--", "qa/old-r1.png"], repo)
        _git(["-c", "user.name=st", "-c", "user.email=st@t",
              "commit", "-q", "-m", "qa delete, no manifest"], repo)
        leg("qa/ deletion WITHOUT manifest blocked",
            any(v["path"] == "qa/old-r1.png"
                for v in deletion_violations(qa_base, "HEAD", repo,
                                             mid="bm-z")))
        qa_base = _commit_qa_file("qa/old-r1.png", "png-bytes-r1")

        def _write_manifest(ts, moved):
            mdir = os.path.join(repo, "results", "_quarantine", ts)
            os.makedirs(mdir, exist_ok=True)
            with open(os.path.join(mdir, "manifest.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({"ts": ts, "moved": moved, "reason": "selftest",
                           "law": "TREASURE_PROTECTION_LAW §2",
                           "observation_window_days": 7}, fh)
            _git(["add", "results/_quarantine/%s/manifest.json" % ts],
                  repo)

        # same-push manifest listing the exact src+sha256 -> released
        _git(["rm", "-q", "--", "qa/old-r1.png"], repo)
        _write_manifest("20261010-1200", [
            {"src": "qa/old-r1.png",
             "dst": "results/_quarantine/20261010-1200/qa/old-r1.png",
             "sha256": "0" * 64, "size": 12}])
        _git(["-c", "user.name=st", "-c", "user.email=st@t",
              "commit", "-q", "-m", "qa rotate with manifest"], repo)
        leg("qa/ deletion with same-push manifest released",
            deletion_violations(qa_base, "HEAD", repo, mid="bm-z") == [])
        leg("CLI check-push manifest release passes (rc 0)",
            check_push(qa_base, "HEAD", repo) == 0)

        # manifest NOT listing the deleted path -> still blocked
        qa_base = _commit_qa_file("qa/old-r2.png", "png-bytes-r2")
        _git(["rm", "-q", "--", "qa/old-r2.png"], repo)
        _write_manifest("20261010-1300", [
            {"src": "qa/some-other.png",
             "dst": "results/_quarantine/20261010-1300/qa/some-other.png",
             "sha256": "1" * 64, "size": 12}])
        _git(["-c", "user.name=st", "-c", "user.email=st@t",
              "commit", "-q", "-m", "manifest path mismatch"], repo)
        leg("qa/ deletion manifest path mismatch blocked",
            any(v["path"] == "qa/old-r2.png"
                for v in deletion_violations(qa_base, "HEAD", repo,
                                             mid="bm-z")))

        # legacy files[] shape (no sha256 face) -> not a release proof
        qa_base = _commit_qa_file("qa/old-r3.png", "png-bytes-r3")
        _git(["rm", "-q", "--", "qa/old-r3.png"], repo)
        mdir = os.path.join(repo, "results", "_quarantine",
                            "20261010-1400")
        os.makedirs(mdir, exist_ok=True)
        with open(os.path.join(mdir, "manifest.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"ts": "2026-10-10T14:00:00+08:00",
                       "files": ["qa/old-r3.png"],
                       "reason": "selftest legacy shape"}, fh)
        _git(["add", "results/_quarantine/20261010-1400/manifest.json"],
             repo)
        _git(["-c", "user.name=st", "-c", "user.email=st@t",
              "commit", "-q", "-m", "legacy shape manifest"], repo)
        leg("legacy files[] manifest not a release proof",
            any(v["path"] == "qa/old-r3.png"
                for v in deletion_violations(qa_base, "HEAD", repo,
                                             mid="bm-z")))

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
