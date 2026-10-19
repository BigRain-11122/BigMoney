"""r1021 bm-b: S0 absorb = stash 6 own dirty faces -> ff-only origin/main ->
stash pop -> UU resolve per face law (newer-wins on daemon live faces,
versioned per r1020/r1028 pattern). Prints evidence; no push here.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NO_WINDOW = 0x08000000
FACES = [
    "content/drama/QUEUE.md",
    "content/drama/ROUND-LOG.md",
    "content/drama/loop_state.json",
    "fleet/machines/bm-b.json",
    "results/paper/marks/marks-20261019.jsonl",
    "results/watermark_red.json",
]


def sh(args, timeout=300, check=True):
    p = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True, timeout=timeout,
                       creationflags=NO_WINDOW)
    out = (p.stdout or b"") + (p.stderr or b"")
    txt = out.decode("utf-8", "replace")
    if check and p.returncode != 0:
        print("FAIL rc=%d args=%s\n%s" % (p.returncode, args, txt[-800:]))
        sys.exit(1)
    return p.returncode, txt


def main():
    rc, st = sh(["stash", "push", "-m", "r1021-s0-absorb"] + FACES)
    print("stash: %s" % st.strip()[-120:])
    rc, ff = sh(["merge", "--ff-only", "origin/main"])
    print("ff-only: %s" % ff.strip()[-160:])
    rc, pop = sh(["stash", "pop"], check=False)
    print("pop rc=%d: %s" % (rc, pop.strip()[-500:]))
    # collect conflict faces
    rc, stat = sh(["status", "--porcelain"])
    uu = [l[3:].strip() for l in stat.splitlines() if l.startswith("UU")]
    print("UU faces: %s" % uu)
    for face in uu:
        # ours = HEAD (origin-new after ff), theirs = stashed local side
        rc, ours = sh(["show", ":2:%s" % face], check=False)
        rc2, theirs = sh(["show", ":3:%s" % face], check=False)
        o_ts = _ts_of(ours, face)
        t_ts = _ts_of(theirs, face)
        if face.endswith("watermark_red.json"):
            pick = "theirs" if (t_ts or "") >= (o_ts or "") else "ours"
        elif face.endswith("marks-20261019.jsonl"):
            pick = "union"
        else:
            pick = "theirs" if face in FACES else "ours"  # own faces: local side wins
        print("resolve %s: ours_ts=%s theirs_ts=%s pick=%s" % (face, o_ts, t_ts, pick))
        if pick == "union":
            merged = _union_jsonl(ours, theirs)
            with open(os.path.join(ROOT, face), "w", encoding="utf-8", newline="\n") as f:
                f.write(merged)
        else:
            src = theirs if pick == "theirs" else ours
            with open(os.path.join(ROOT, face), "w", encoding="utf-8", newline="\n") as f:
                f.write(src)
        sh(["add", "--", face])
    rc, stat2 = sh(["status", "--porcelain"])
    print("post-status:")
    for l in stat2.splitlines():
        print("  %s" % l[:150])
    rc, head = sh(["rev-parse", "--short", "HEAD"])
    print("HEAD now: %s" % head.strip())


def _ts_of(text, face):
    m = re.search(r'"ts"\s*:\s*"([^"]+)"', text)
    if m:
        return m.group(1)
    m = re.search(r'"checked_at"\s*:\s*"([^"]+)"', text)
    return m.group(1) if m else ""


def _union_jsonl(a, b):
    rows = []
    seen = set()
    for chunk in (a, b):
        for line in chunk.splitlines():
            line = line.strip()
            if not line:
                continue
            if line in seen:
                continue
            seen.add(line)
            rows.append(line)

    def key(line):
        m = re.search(r'"ts"\s*:\s*"([^"]+)"', line)
        return m.group(1) if m else line[:19]
    rows.sort(key=key)
    return "\n".join(rows) + "\n"


if __name__ == "__main__":
    main()
