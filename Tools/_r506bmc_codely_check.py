import subprocess, sys
r = subprocess.run(["git","show","HEAD:CODELY.md"], capture_output=True, creationflags=0x08000000)
t = r.stdout.decode("utf-8","replace")
lines = t.splitlines()
bad = [i for i,ln in enumerate(lines) if ln.startswith(("<<<<<<< ","||||||| ",">>>>>>> ")) or ln.rstrip("\r")=="======="]
print("line-start markers:", bad if bad else "NONE")
for probe in ("r705 bm-a] ", "r706 bm-a] ", "r506 bm-c] rebase"):
    print(("OK   " if probe in t else "MISS ") + probe)
print("total lines:", len(lines))
