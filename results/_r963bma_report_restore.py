import subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GIT = r"C:\Program Files\Git\cmd\git.exe"
p = "results/post_review/REPORT-20261011.md"
blob = subprocess.run([GIT, "show", "HEAD:" + p], capture_output=True).stdout
with open(p, "wb") as f:
    f.write(blob)
print(f"recovered {p} bytes={len(blob)}")
