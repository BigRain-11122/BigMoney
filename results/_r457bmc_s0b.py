"""r457 bm-c S0b: face-intersection probe for daemon-treadmill pre-alignment (r437 law).
Changed set HEAD..origin/main vs local dirty faces; per-face blob compare for
dirty faces to classify ours-live-wins (daemon lane) vs origin-newer-wins (regen)."""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRTY = [
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]


def git(args, cwd=ROOT):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, changed, _ = git(["diff", "--name-only", "HEAD", "origin/main"])
    ch = [l.strip() for l in changed.splitlines() if l.strip()]
    print("CHANGED-HEAD..origin/main COUNT %d" % len(ch))
    for l in ch:
        print("  " + l)
    inter = [f for f in DIRTY if f in ch]
    print("INTERSECTION-DIRTY-x-CHANGED %d" % len(inter))
    for f in inter:
        print("  INT " + f)
    # per dirty face: local mtime + HEAD blob vs origin blob
    import datetime
    for f in DIRTY:
        p = os.path.join(ROOT, f.replace("/", os.sep))
        mt = datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec="seconds") if os.path.exists(p) else "?"
        _, h1, _ = git(["rev-parse", "HEAD:%s" % f])
        _, h2, _ = git(["rev-parse", "origin/main:%s" % f])
        print("FACE %s mtime=%s HEAD=%s ORIGIN=%s" % (f, mt, h1.strip()[:10] or "-", h2.strip()[:10] or "-"))
    # untracked check
    rc, st, _ = git(["status", "--porcelain"])
    print("--- porcelain ---")
    print(st.strip())


if __name__ == "__main__":
    main()
