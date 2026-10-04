"""r696 bm-b: dual-side CODELY marker probe (subprocess raw bytes, r660 law)."""
import subprocess

MARK = "r696 bm-b] ls-tree"


def show(rev):
    r = subprocess.run(["git", "show", rev + ":CODELY.md"], capture_output=True)
    assert r.returncode == 0, r.stderr[:200]
    return r.stdout.decode("utf-8", "replace")


ours = show("HEAD")
theirs = show("MERGE_HEAD")
print("ours_count=", ours.count(MARK))
print("theirs_count=", theirs.count(MARK))
print("ours_ls_tree=", ours.count("ls-tree"))
print("theirs_ls_tree=", theirs.count("ls-tree"))
# tail lines of each side
print("OURS_TAIL:", ours.rstrip().splitlines()[-1][:120])
print("THEIRS_TAIL:", theirs.rstrip().splitlines()[-1][:120])
# what does the working tree CODELY look like now (post failed resolver write)?
wt = open("CODELY.md", "rb").read().decode("utf-8", "replace")
print("wt_count=", wt.count(MARK))
