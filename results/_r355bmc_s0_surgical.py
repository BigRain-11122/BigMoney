# r355 bm-c S0 surgical integration (r530 diff-based payload law)
# Deliver r354 heritage (2 unpushed commits: W58 finalize product + tail shards
# + closeout) onto bm-b's W59-freeze head WITHOUT rebase (live-write lane files
# block rebase; r523/r532 family). Shared same-day regen faces -> origin side
# (r505 wall-clock-newer law; S6 chain re-derives them this round anyway).
# Assertions: r530 deletion-set + payload-count + r331 post-write ls-tree
# cross-check + r516 mirror (moved-file absence). Push = CAS by parent (FF).
def _main():
    import subprocess, sys, os, time, tempfile

    REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
    log = lambda *a: print(*a, flush=True)

    def git(args, env_extra=None, check=True):
        e = dict(os.environ)
        if env_extra:
            e.update(env_extra)
        p = subprocess.run(["git", "-C", REPO] + args, env=e,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p.stdout.decode("utf-8", "replace")
        err = p.stderr.decode("utf-8", "replace")
        if check and p.returncode != 0:
            log("GIT_FAIL rc=%d: git %s" % (p.returncode, " ".join(args)))
            log("STDERR:", err.strip())
            sys.exit(2)
        return out, err, p.returncode

    for attempt in range(1, 4):
        git(["fetch", "origin"])
        out, _, _ = git(["rev-parse", "HEAD"])
        head_old = out.strip()
        out, _, _ = git(["rev-parse", "origin/main"])
        base = out.strip()
        if head_old == base:
            log("ALREADY_SYNCED head==origin/main, nothing to do")
            return 0

        # payload = my ahead changes (merge-base..HEAD); incoming = same range on origin side
        out, _, _ = git(["merge-base", "HEAD", "origin/main"])
        mb = out.strip()
        out, _, _ = git(["diff", "--name-status", mb, "HEAD"])
        mine = {}          # path -> status letter
        mine_del = set()
        for ln in out.splitlines():
            parts = ln.split("\t")
            if parts[0].startswith("R"):
                mine[parts[2]] = "A"
                mine_del.add(parts[1])
            else:
                st, path = parts[0], parts[1]
                mine[path] = st
                if st == "D":
                    mine_del.add(path)
        out, _, _ = git(["diff", "--name-status", mb, "origin/main"])
        theirs = set()
        for ln in out.splitlines():
            parts = ln.split("\t")
            if parts[0].startswith("R"):
                theirs.add(parts[2]); theirs.add(parts[1])
            else:
                theirs.add(parts[1])
        shared = set(mine) & theirs
        overlay = {p: st for p, st in mine.items() if p not in shared and st != "D"}
        deletes = {p for p in mine_del if p not in theirs}
        log("attempt %d: base=%s payload=%d shared_origin_side=%d deletes=%d"
            % (attempt, base[:9], len(overlay), len(shared), len(deletes)))

        # temp index seeded from origin/main
        idx = os.path.join(tempfile.gettempdir(), "r355bmc_idx")
        if os.path.exists(idx):
            os.remove(idx)
        env_idx = {"GIT_INDEX_FILE": idx}
        git(["read-tree", base], env_extra=env_idx)
        for path in sorted(overlay):
            out, _, _ = git(["ls-tree", "HEAD", "--", path])
            row = out.strip()
            if not row:
                log("LS_TREE_MISS", path); sys.exit(2)
            meta_parts = row.split("\t")[0].split()
            mode, sha = meta_parts[0], meta_parts[-1]
            git(["update-index", "--add", "--cacheinfo", "%s,%s,%s" % (mode, sha, path)],
                env_extra=env_idx)
        for path in sorted(deletes):
            git(["update-index", "--force-remove", path], env_extra=env_idx)
        out, _, _ = git(["write-tree"], env_extra=env_idx)
        tree = out.strip()
        msg = ("r355 S0 surgical integration: deliver r354 heritage (W58 finalize product "
               "n1_w58_results.json ledger 492,148 + tail shards 9/10 + prereg s7/s8 backfill "
               "+ closeout bookkeeping) onto bm-b W59-freeze head via diff-based payload staging "
               "(r530 law); shared same-day regen faces taken origin-side per r505 wall-clock-newer "
               "law (S6 chain re-derives this round); deletion-set = MSG-0700 archive move only "
               "(r516 asserted); CAS push by parent [via bm-c r355]")
        out, _, _ = git(["commit-tree", tree, "-p", base, "-m", msg])
        new = out.strip()

        # --- assertions ---
        out, _, _ = git(["ls-tree", "-r", "--name-only", base])
        basefiles = set(out.splitlines())
        out, _, _ = git(["ls-tree", "-r", "--name-only", new])
        newfiles = set(out.splitlines())
        # deletion-set via pure tree math (diff -M folds moves into R pairs;
        # --diff-filter=D would never see them -> false red)
        pending_del = deletes & basefiles
        delivered_del = deletes - pending_del
        if delivered_del:
            log("NOTE already-delivered deletes on origin (r343 legal):", sorted(delivered_del))
        actual_absent = basefiles - newfiles
        if actual_absent != pending_del:
            log("ASSERT_FAIL deletion-set mismatch: extra_absent=%s missing_absent=%s"
                % (sorted(actual_absent - pending_del), sorted(pending_del - actual_absent)))
            sys.exit(3)
        out, _, _ = git(["diff", "--name-only", base, new])
        diffset = set(x for x in out.splitlines() if x.strip())
        allowed = set(overlay) | deletes
        unexpected = diffset - allowed
        if unexpected:
            log("ASSERT_FAIL unexpected diff entries:", sorted(unexpected))
            sys.exit(3)
        notdiff = set(overlay) - diffset - deletes
        if notdiff:
            log("NOTE byte-identical-to-origin (legal NOT_IN_DIFF r343):", sorted(notdiff))
        # r331 post-write ls-tree cross-check: origin's newest additions must survive
        must_have = ["research/PERPETUAL_N1_W59_PREREG.md", "research/PERPETUAL_FACES.md",
                     "scripts/perpetual_faces_n1.py", "scripts/perpetual_faces.py",
                     "results/p2cal_ext/n1_w59/shard-0-of-12.json",
                     "results/p2cal_ext/n1_w59/shard-5-of-12.json",
                     "results/perpetual_faces/n1_w58_results.json",
                     "research/PERPETUAL_N1_W58_PREREG.md",
                     "results/p2cal_ext/n1_w58/shard-9-of-12.json",
                     "results/p2cal_ext/n1_w58/shard-10-of-12.json",
                     "fleet/inbox/processed/MSG-20261002-0700-bm-a.md"]
        missing = [p for p in must_have if p not in newfiles]
        if missing:
            log("ASSERT_FAIL ls-tree missing:", missing); sys.exit(3)
        if "fleet/inbox/MSG-20261002-0700-bm-a.md" in newfiles:
            log("ASSERT_FAIL moved-source still present"); sys.exit(3)
        log("assertions PASS: new=%s D=%d changes=%d"
            % (new[:9], len(pending_del), len(diffset)))

        out, err, rc = git(["push", "origin", new + ":refs/heads/main"], check=False)
        if rc == 0:
            log("PUSH_OK", new[:9])
            out, _, rc2 = git(["update-ref", "refs/heads/main", new, head_old], check=False)
            if rc2 != 0:
                log("UPDATE_REF_CAS_FAIL (local main moved? inspect manually)")
                sys.exit(4)
            # sync index+worktree: reset --mixed then checkout materializes incoming
            git(["reset", "--mixed", new])
            git(["checkout", "--", "."])
            out, _, _ = git(["status", "--porcelain"])
            log("POST_SYNC_STATUS:")
            log(out.strip() or "(clean)")
            return 0
        log("PUSH_REJECTED attempt %d rc=%d stderr=%s" % (attempt, rc, err.strip()[:200]))
        time.sleep(8)
    log("CAS_PUSH_FAILED after 3 attempts -> fallback to machine branch")
    sys.exit(5)

if __name__ == "__main__":
    import sys
    sys.exit(_main() or 0)
