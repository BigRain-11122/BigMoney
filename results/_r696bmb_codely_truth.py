"""r696 bm-b: CODELY.md deep truth probe (size, markers, git state, encoding)."""
import os
import subprocess

blob = open("CODELY.md", "rb").read()
print("worktree size =", len(blob))
r = subprocess.run(["git", "show", "HEAD:CODELY.md"], capture_output=True)
print("HEAD size =", len(r.stdout))
r2 = subprocess.run(["git", "status", "--porcelain", "--", "CODELY.md"],
                    capture_output=True)
print("porcelain:", r2.stdout.decode().strip() or "(clean)")

# try strict utf-8 decode of worktree
try:
    blob.decode("utf-8")
    print("worktree strict-utf8: VALID")
except UnicodeDecodeError as e:
    print("worktree strict-utf8: INVALID at byte", e.start,
          "bytes:", blob[max(0, e.start - 20):e.start + 20])

# markers in HEAD blob (valid utf-8 source of truth)
head_txt = r.stdout.decode("utf-8", "replace")
print("HEAD ls-tree mark count =", head_txt.count("r696 bm-b] ls-tree"))
print("HEAD daemon mark count =", head_txt.count("daemon tick"))

# markers in worktree
wt_txt = blob.decode("utf-8", "replace")
print("WT ls-tree mark count =", wt_txt.count("r696 bm-b] ls-tree"))
print("WT daemon mark count =", wt_txt.count("daemon tick"))
i = wt_txt.find("daemon tick")
print("WT daemon context:", repr(wt_txt[i - 30:i + 40]) if i >= 0 else "n/a")
# where does ls-tree entry sit in WT vs HEAD
j = wt_txt.find("r696 bm-b] ls-tree")
print("WT ls-tree idx =", j, "| HEAD ls-tree idx =", head_txt.find("r696 bm-b] ls-tree"))
print("WT lines =", len(wt_txt.rstrip().split(chr(10))))
print("HEAD lines =", len(head_txt.rstrip().split(chr(10))))
