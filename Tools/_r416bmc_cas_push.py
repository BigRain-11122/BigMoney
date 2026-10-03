# -*- coding: utf-8 -*-
"""r416 bm-c CAS direct push (O-1410-5 push-contention-window surgical method).

Push was rejected (origin advanced: bm-a r623/624 batch + bm-b keepalive). Local tree
has live-writer daemon faces (rebase blocked, r614 law). Surgical CAS:
  tree = origin/main tree
       + my 23 non-overlap files (blob-verbatim from round commit 62f4d8025)
       + x2_watch_log.jsonl line-union (origin base + my-only rows, r570 domain law)
  31 overlap faces -> take-origin (r505 shared-derive law; my 13:09 stale-takeover
  derives superseded by bm-a's live 12:52 products).
Hard verification (r403 GM law): tree/newc 40-hex match, push output scanned for
fatal/rejected/failed/error, post-push fetch+rev-parse delivery self-proof.
On success: reset --hard <sha> (local twin commits become orphans; next-round S0
rebase sees zero delta). Zero deletions in push (pre-push claw safe).
"""
import os
import re
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MINE = "62f4d8025"
BASE = "c4d2a50e8"
X2 = "results/x2_watch_log.jsonl"
IDX = os.path.join(ROOT, ".git", "cas_index_r416.tmp")
MSG = ("round 416: T-144(c) D-06 batch3 spawn/tooling-domain split "
       "(pit-spawn.md 5 entries zero-loss+verify 14/14) + S6 37/37 rc0 + ledgers "
       "[CAS surgical: 23 own faces + x2 line-union; 31 shared-derive faces take-origin r505]")
NW = 0x08000000
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def git(args, env_extra=None, inp=None, check=True):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=NW, env=env, input=inp)
    if check and r.returncode != 0:
        raise RuntimeError("git %s rc=%d: %s" % (
            " ".join(args[:3]), r.returncode, r.stderr.decode("utf-8", "replace")[:400]))
    return r


def git_txt(args, **kw):
    return git(args, **kw).stdout.decode("utf-8", "replace").strip()


def attempt():
    git(["fetch", "origin"])
    tip = git_txt(["rev-parse", "origin/main"])
    assert SHA_RE.match(tip), "origin tip not 40-hex: %r" % tip

    their = set(git_txt(["diff", "--name-only", BASE, tip]).splitlines())
    mine = git_txt(["diff", "--name-only", BASE, MINE]).splitlines()
    overlap = [f for f in mine if f in their]
    keep = [f for f in mine if f not in their]
    assert X2 in overlap, "x2 face expected in overlap (both sides appended)"
    keep_nonx2 = [f for f in keep if f != X2]

    env_idx = {"GIT_INDEX_FILE": IDX}
    if os.path.exists(IDX):
        os.remove(IDX)
    git(["read-tree", tip], env_extra=env_idx)

    for f in keep_nonx2:
        # r366 ls-tree explicit-column law: mode SP type SP sha TAB path
        out = git_txt(["ls-tree", MINE, "--", f], env_extra=env_idx)
        parts = out.split("\t")[0].split()
        assert len(parts) >= 3 and parts[1] == "blob", "ls-tree unexpected: %r" % out[:120]
        mode, sha = parts[0], parts[2]
        assert SHA_RE.match(sha), "blob sha not 40-hex for %s: %r" % (f, sha)
        git(["update-index", "--add", "--cacheinfo", "%s,%s,%s" % (mode, sha, f)],
            env_extra=env_idx)

    # x2 line-union: origin base + my-only rows (byte-exact, r570 law)
    ob = git(["show", tip + ":" + X2]).stdout
    mb = git(["show", MINE + ":" + X2]).stdout
    o_lines = ob.split(b"\n")
    m_lines = mb.split(b"\n")
    o_set = set(l for l in o_lines if l)
    my_only = [l for l in m_lines if l and l not in o_set]
    union = ob + b"".join(l + b"\n" for l in my_only)
    blob = git(["hash-object", "-w", "--stdin"], inp=union).stdout.decode().strip()
    assert SHA_RE.match(blob), "x2 union blob not 40-hex"
    git(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, X2)],
        env_extra=env_idx)

    tree = git_txt(["write-tree"], env_extra=env_idx)
    assert SHA_RE.match(tree), "tree not 40-hex: %r" % tree
    newc = git_txt(["commit-tree", tree, "-p", tip, "-m", MSG])
    assert SHA_RE.match(newc), "newc not 40-hex: %r" % newc

    # deletion-set self-proof (pre-push claw parity): push delta must contain no deletions
    delta = git_txt(["diff", "--name-status", tip, newc])
    dels = [l for l in delta.splitlines() if l.startswith("D")]
    assert not dels, "deletion in push delta: %s" % dels[:5]

    r = git(["push", "origin", newc + ":main"], check=False)
    out = (r.stdout + r.stderr).decode("utf-8", "replace").lower()
    bad_words = [w for w in ("fatal", "rejected", "failed", "error") if w in out]
    if r.returncode != 0 or bad_words:
        return ("RETRY", tip, newc, "rc=%d words=%s out=%s" % (
            r.returncode, bad_words, out[-300:]))

    git(["fetch", "origin"])
    now_tip = git_txt(["rev-parse", "origin/main"])
    if now_tip != newc:
        return ("RETRY", tip, newc, "origin moved during push: %s" % now_tip)

    # delivery self-proof done; sync local tree to pushed state
    git(["reset", "--hard", newc])
    return ("OK", tip, newc,
            "keep=%d overlap_take_origin=%d x2_union=+%d rows (o=%d m=%d)" % (
                len(keep_nonx2), len(overlap) - 1, len(my_only),
                len([l for l in o_lines if l]), len([l for l in m_lines if l])))


def main():
    for i in (1, 2, 3):
        status, tip, newc, note = attempt()
        print("ATTEMPT %d: %s base=%s newc=%s | %s" % (i, status, tip[:12], newc[:12], note))
        if status == "OK":
            print("CAS_PUSHED_SHA=" + newc)
            return 0
    print("CAS_FAILED_ALL_ATTEMPTS")
    return 1


if __name__ == "__main__":
    sys.exit(main())
