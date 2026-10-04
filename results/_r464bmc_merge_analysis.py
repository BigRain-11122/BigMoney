"""r464 bm-c merge-conflict analysis: merge-base both-sides change sets."""
import subprocess

C = 0x08000000


def g(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True, creationflags=C,
                       cwd=".")
    return r.stdout.decode("utf-8", "replace"), r.returncode


def main():
    mb, rc = g("merge-base", "HEAD", "origin/main")
    mb = mb.strip()
    print("MERGE_BASE", mb)
    mine_s, _ = g("diff", "--name-only", mb, "HEAD")
    theirs_s, _ = g("diff", "--name-only", mb, "origin/main")
    mine = set(x for x in mine_s.splitlines() if x.strip())
    theirs = set(x for x in theirs_s.splitlines() if x.strip())
    both = sorted(mine & theirs)
    print("MINE_ONLY", len(mine - theirs))
    print("THEIRS_ONLY", len(theirs - mine))
    print("BOTH_SIDES", len(both))
    for x in both:
        print("  BOTH", x)


if __name__ == "__main__":
    main()
