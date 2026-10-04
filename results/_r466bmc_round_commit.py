"""r466 bm-c final round commit + merge-cycle driver (r437/r648 absorb law):
1. targeted add (porcelain, own-guard vs foreign faces) + round commit
2. fetch; behind>0 -> absorb daemon treadmill faces + merge origin/main cycles (max 3)
3. merge UU -> print UU list, exit 3 (canon resolver runs as next step)
   merge clean -> push_verify single-source, exit its rc
Fail-closed: deletions or foreign faces abort before any add."""
import json
import os
import subprocess
import sys

C = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOREIGN = ("round_reports-bm-a", "round_reports-bm-b", "state-bm-a.json",
           "state-bm-b.json", "fleet/machines/bm-a", "fleet/machines/bm-b",
           "CODELY.md", "HQ-FEEDBACK.md", "fleet/orders/", "fleet/tasks/")
ROUND_MSG = ("round 466: golden-week watch + S0 zero-intersection absorb+merge (430689bdb) "
              "+ fund-trio watch V726/Q560/D412 + S6 38/38 rc0 + closeout bookkeeping -- r466 bm-c")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, creationflags=C, cwd=ROOT)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")


def porcelain():
    rc, out, err = git("status", "--porcelain")
    assert rc == 0, "porcelain fail " + err[:200]
    paths = []
    for ln in out.splitlines():
        if not ln.strip():
            continue
        st, p = ln[:2].strip(), ln[3:].strip().strip('"')
        assert "D" not in st, "unexpected deletion in worktree: " + ln
        assert "U" not in st, "unexpected unmerged state pre-commit: " + ln
        for m in FOREIGN:
            assert m not in p, "foreign face in dirty set, abort: " + p
        if p:
            paths.append(p)
    return paths


def absorb(msg):
    paths = porcelain()
    if not paths:
        return False
    rc, out, err = git("add", "--", *paths)
    assert rc == 0, "absorb add fail " + err[:200]
    rc, out, err = git("commit", "-m", msg)
    assert rc == 0, "absorb commit fail " + (out + err)[:300]
    print("ABSORB_COMMIT", len(paths), "faces")
    return True


def push_verify():
    pr = subprocess.run([sys.executable, "Tools/push_verify.py"],
                        capture_output=True, creationflags=C, cwd=ROOT)
    txt = (pr.stdout or b"").decode("utf-8", "replace") + " || " + \
        (pr.stderr or b"").decode("utf-8", "replace")
    print("PUSH_VERIFY_RC", pr.returncode)
    print(txt.strip()[-400:])
    return pr.returncode


def main():
    # 1. round commit (all current own products)
    paths = porcelain()
    if paths:
        rc, out, err = git("add", "--", *paths)
        assert rc == 0, "round add fail " + err[:200]
        rc, out, err = git("commit", "-m", ROUND_MSG)
        assert rc == 0, "round commit fail " + (out + err)[:300]
        print("ROUND_COMMIT", len(paths), "faces")
    else:
        print("ROUND_COMMIT nothing-dirty")
    # 2. fetch + behind
    rc, out, err = git("fetch", "origin")
    assert rc == 0, "fetch fail " + err[:200]
    rc, out, _ = git("rev-list", "--count", "HEAD..origin/main")
    behind = int(out.strip() or 0)
    print("BEHIND", behind)
    if behind == 0:
        sys.exit(push_verify())
    # 3. absorb+merge cycles
    for cycle in (1, 2, 3):
        absorb("absorb r466 bm-c: daemon treadmill faces (round-close merge window) -- r437 absorb law")
        rc, out, err = git("merge", "origin/main", "--no-edit")
        if rc == 0:
            print("MERGE_CLEAN cycle", cycle, (out or err).strip()[:160])
            sys.exit(push_verify())
        rc2, st, _ = git("status", "--porcelain")
        uu = [l[3:].strip().strip('"') for l in st.splitlines() if l.startswith("UU")]
        if uu:
            print("UU_FACES", json.dumps(uu))
            with open(os.path.join(ROOT, "results", "_r466bmc_uu_faces.json"), "w",
                      encoding="utf-8", newline="\n") as f:
                json.dump({"cycle": cycle, "uu": sorted(uu)}, f, ensure_ascii=False, indent=1)
            sys.exit(3)
        print("MERGE_REFUSED cycle", cycle, (out + err)[:300])


if __name__ == "__main__":
    main()
