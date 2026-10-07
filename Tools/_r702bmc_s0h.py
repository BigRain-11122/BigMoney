"""r702 bm-c S0h: r696 beat-window atomic absorb + direct rebase origin/main
(bypass transient pull ambiguity). Conflict faces resolved per canon:
regenerable probe report -> --theirs (r701 law), then atomic add+continue."""
import json
import os
import subprocess
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
REGEN_THEIRS = {"results/_orphan_face_probe.json"}
facts = {"tries": []}


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def conflicted():
    rc, out, _ = git(["diff", "--name-only", "--diff-filter=U"])
    return set(x for x in out.strip().splitlines() if x)


def resolve_loop():
    """Resolve UU faces per canon; atomic add+continue per r787 law."""
    n = 0
    while True:
        uu = conflicted()
        if not uu:
            break
        n += 1
        print("  UU pass %d: %s" % (n, sorted(uu)))
        for f in uu:
            if f in REGEN_THEIRS:
                git(["checkout", "--theirs", f])
                print("    --theirs (regenerable): %s" % f)
            else:
                print("    UNKNOWN FACE CONFLICT: %s -- STOP for manual" % f)
                return False
        git(["add", "-A"])
        rc, out, err = git(["rebase", "--continue"])
        if rc != 0 and b"edit all merge conflicts" in (out + err).encode("utf-8", "replace") and not conflicted():
            # r835 third-state probe: ls-files -u empty but continue refuses
            print("  r835 THIRD STATE detected (empty UU + continue refusal)")
            return "E42"
    return True


for tryno in range(1, 6):
    t0 = time.time()
    git(["add", "-A"])
    rc1, o1, e1 = git(["commit", "-m", "lane: bm-c r702 tail churn absorb w2 pre-rebase (daemon tick faces, r696 race law)"])
    committed = rc1 == 0
    rc2, o2, e2 = git(["rebase", "origin/main"])
    msg = (o2 + e2).strip()
    rec = {"try": tryno, "commit_rc": rc1, "rebase_rc": rc2, "out": msg[-400:]}
    facts["tries"].append(rec)
    print("== try %d: commit=%s rebase rc=%d (%.1fs)" % (tryno, "ok" if committed else "noop", rc2, time.time() - t0))
    print("   " + msg[-300:].replace("\n", " | "))
    if rc2 == 0:
        break
    if "unstaged" in msg or "you have unstaged" in msg.lower():
        time.sleep(2)
        continue
    if "CONFLICT" in msg or conflicted():
        res = resolve_loop()
        if res is True:
            rc3, o3, e3 = git(["rebase", "--continue"])
            # continue may complete rebase
            rc2 = rc3
            print("   continue rc=%d" % rc2, (o3 + e3).strip()[-200:])
            if rc2 == 0:
                break
        elif res == "E42":
            facts["e42"] = True
            break
        else:
            break
    else:
        time.sleep(2)

rc, out, err = git(["status", "-sb"])
facts["status"] = out.strip()
print("== status:", out.strip()[:200])
rc, out, err = git(["rev-list", "--count", "HEAD..origin/main"])
facts["behind"] = int(out.strip() or 0)
rc, out, err = git(["rev-list", "--count", "origin/main..HEAD"])
facts["ahead"] = int(out.strip() or 0)
print("== behind=%s ahead=%s" % (facts["behind"], facts["ahead"]))
rc, out, err = git(["log", "--oneline", "-8"])
print(out)

with open(os.path.join(REPO, "results", "_r702bmc_s0h_facts.json"), "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print("== facts saved")
