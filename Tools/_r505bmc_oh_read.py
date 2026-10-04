"""r505 bm-c: read OH-20261005-bigmoney.md at group origin + authorship
(git log for the path) to decide the OSS-harvest receipt leg."""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = os.path.normpath(os.path.join(ROOT, "..", ".."))


def git_raw(args, cwd):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def main():
    out_path = os.path.join(ROOT, "results", "_r505bmc_oh_read.txt")
    with open(out_path, "wb") as f:
        rc, blob, err = git_raw(["show", "origin/main:cph4/oss-harvest/OH-20261005-bigmoney.md"], GROUP)
        if rc != 0:
            f.write(("SHOW-FAIL " + err.strip()[:200]).encode("utf-8"))
        else:
            f.write(b"=== OH-20261005-bigmoney.md @ origin/main ===\n")
            f.write(blob)
        f.write(b"\n\n=== git log for path ===\n")
        rc, out, err = git_raw(["log", "--format=%h|%an|%ae|%ad|%s", "--date=iso", "-5",
                                "origin/main", "--", "cph4/oss-harvest/OH-20261005-bigmoney.md"], GROUP)
        f.write(out if rc == 0 else ("LOG-FAIL " + err).encode("utf-8", "replace"))
        f.write(b"\n\n=== reference: OH-20261004-cph4.md (latest sibling format) ===\n")
        rc, blob, err = git_raw(["show", "origin/main:cph4/oss-harvest/OH-20261004-cph4.md"], GROUP)
        f.write(blob if rc == 0 else ("SHOW-FAIL " + err).encode("utf-8", "replace"))
    print("WROTE " + out_path)


if __name__ == "__main__":
    main()
