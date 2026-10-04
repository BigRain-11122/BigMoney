"""r505 bm-c: extract full D-20261005-05 BigMoney rows (GBK decode) + ls-tree
cph4/oss-harvest/ from group origin (fresh-read law)."""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = os.path.normpath(os.path.join(ROOT, "..", ".."))


def git_raw(args, cwd):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def dec(b):
    try:
        s = b.decode("gbk")
        bad = s.count("\ufffd")
    except UnicodeDecodeError:
        return b.decode("gbk", "replace"), -1
    return s, bad


def main():
    rc, blob, _ = git_raw(["show", "origin/main:docs/decisions.md"], GROUP)
    out_path = os.path.join(ROOT, "results", "_r505bmc_d19_rows.txt")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for enc in ("utf-8", "gbk"):
            try:
                text = blob.decode(enc)
                f.write("[decode:%s OK]\n" % enc)
                break
            except UnicodeDecodeError:
                f.write("[decode:%s FAIL]\n" % enc)
                text = blob.decode("utf-8", "replace")
        lines = text.splitlines()
        for i, l in enumerate(lines):
            if "D-20261005" in l or "BigMoney" in l:
                f.write("L%d: %s\n" % (i + 1, l.strip()))
        f.write("=== cph4/oss-harvest tree @ origin/main ===\n")
        rc, out, err = git_raw(["ls-tree", "--name-only", "origin/main", "cph4/oss-harvest/"], GROUP)
        f.write((out.decode("utf-8", "replace") if rc == 0 else ("LS-FAIL " + err.strip()[:200])) + "\n")
        f.write("=== cph4/oss-harvest @ local working tree ===\n")
        p = os.path.join(GROUP, "cph4", "oss-harvest")
        if os.path.isdir(p):
            for n in sorted(os.listdir(p)):
                f.write(n + "\n")
        else:
            f.write("(dir absent locally)\n")
    print("WROTE " + out_path)


if __name__ == "__main__":
    main()
