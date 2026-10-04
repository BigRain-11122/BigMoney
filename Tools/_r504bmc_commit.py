"""r504 bm-c commit+delivery: targeted add (round-start dirty -> explicit
paths only, all own-machine faces), staged-list audit, commit, push_verify
(push+fetch+40hex proof). Then S7-close ledger line + second commit + final
push_verify. Hard validation per CAS batch law (40-hex, bad-word screen)."""
import json
import os
import re
import subprocess
import sys

CREATE = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True,
                       creationflags=CREATE, cwd=ROOT)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")


def main():
    # 1) add explicit paths (from status: all own faces this round)
    rc, st, _ = git("status", "--porcelain")
    paths = []
    for line in st.splitlines():
        line = line.rstrip("\n")
        if not line.strip():
            continue
        flag, path = line[:2], line[3:].strip()
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        paths.append(path)
    print("ADD-PATHS", len(paths))
    if paths:
        rc, out, err = git("add", "--", *paths)
        print("add rc=%d" % rc, (err or out).strip()[:200])

    # 2) staged audit
    rc, staged, _ = git("diff", "--cached", "--name-only")
    slist = [l for l in staged.splitlines() if l.strip()]
    print("STAGED", len(slist))
    missing = [p for p in paths if p not in slist]
    if missing:
        print("WARN paths not staged:", missing[:10])
    rc, other, _ = git("status", "--porcelain")
    unexpected_unstaged = [l for l in other.splitlines()
                           if l.strip() and l[:2] in (" M", "MM", "??", " D")]
    print("UNSTAGED-AFTER-ADD", len(unexpected_unstaged),
          [l[:80] for l in unexpected_unstaged[:6]])

    # 3) commit
    msg = ("round 504: N2-W15 12/12 milestone (bm-a SHARD-2 receipt, zero "
           "double-burn) + D-20261004-05 keep-alive face 6/6 + S6 38/38 "
           "(dualrun streak 4) + W3 custody + quartet 4/4")
    rc, out, err = git("commit", "-m", msg)
    print("COMMIT rc=%d" % rc)
    print((out + err).strip()[:300])
    rc, head, _ = git("rev-parse", "HEAD")
    head = head.strip()
    assert HEX40.match(head), "head not 40hex: %r" % head
    print("HEAD", head[:12])

    # 4) push_verify leg 1
    p = subprocess.run([sys.executable, "Tools/push_verify.py"],
                       capture_output=True, creationflags=CREATE, cwd=ROOT)
    print("PUSH-VERIFY-1 rc=%d" % p.returncode)
    print((p.stdout or b"").decode("utf-8", "replace").strip()[-600:])
    if p.returncode != 0:
        print("NOT-DELIVERED -- honest red; abort second commit leg")
        return 1

    # 5) S7-close ledger line + second commit
    import datetime
    ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    rc, ahead, _ = git("rev-list", "--count", "origin/main..HEAD")
    n = ahead.strip()
    line = (f"{ts} | r504 bm-c S7-close | 本地未达 origin commit 数={n}（DELIVERED） | "
            f"round commit {head[:9]} {len(slist)} 文件吸收入账（本机守护面 4 +S6 CEO 面"
            "再生+双跑对账 streak 4 行+验收窗探针 6+轮产出 8 脚本+S7 三簿记） | "
            "push_verify DELIVERED tip=remote（40hex 过+坏词筛零命中） | "
            "二次小 commit=本行（S7-close 行规）")
    with open(os.path.join(ROOT, "round_reports-bm-c.md"), "ab") as fh:
        fh.write(line.encode("utf-8") + b"\n")
    rc, out, err = git("add", "--", "round_reports-bm-c.md")
    rc, out, err = git("commit",
                       "-m", "round 504: S7-close delivery line (push_verify DELIVERED)")
    rc, head2, _ = git("rev-parse", "HEAD")
    head2 = head2.strip()
    assert HEX40.match(head2), "head2 not 40hex"
    print("HEAD2", head2[:12])

    # 6) final push_verify
    p = subprocess.run([sys.executable, "Tools/push_verify.py"],
                       capture_output=True, creationflags=CREATE, cwd=ROOT)
    print("PUSH-VERIFY-2 rc=%d" % p.returncode)
    print((p.stdout or b"").decode("utf-8", "replace").strip()[-400:])
    rc, ahead2, _ = git("rev-list", "--count", "origin/main..HEAD")
    print("FINAL-AHEAD", ahead2.strip())
    rc, st2, _ = git("status", "--porcelain")
    dirty = [l for l in st2.splitlines() if l.strip()]
    print("FINAL-DIRTY", len(dirty), [l[:70] for l in dirty[:6]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
