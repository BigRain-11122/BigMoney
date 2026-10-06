# -*- coding: utf-8 -*-
import subprocess

d = subprocess.run(["git", "show", "6957f509e", "--", "scripts/perpetual_faces.py"],
                   capture_output=True).stdout.decode("utf-8", errors="replace")
print(d)
