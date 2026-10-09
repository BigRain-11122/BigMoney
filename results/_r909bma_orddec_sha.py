# -*- coding: utf-8 -*-
import hashlib
import subprocess

GIT = r"C:\Program Files\Git\cmd\git.exe"
K = r"C:\Users\sjs20\Desktop\FluxGroup"
for path, tag in (("docs/orders.md", "ORD"), ("docs/decisions.md", "DEC")):
    p = subprocess.run([GIT, "-C", K, "show", "origin/main:" + path],
                       capture_output=True)
    sha = hashlib.sha256(p.stdout).hexdigest()
    print(tag, "sha:", sha)
