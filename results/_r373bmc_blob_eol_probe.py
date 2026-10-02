import subprocess
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
r = subprocess.run(["git", "show", "origin/main:CODELY.md"], capture_output=True, cwd=ROOT,
                   creationflags=0x08000000)
b = r.stdout
print("blob bytes=%d crlf=%d lf=%d lines_lf=%d" % (
    len(b), b.count(b"\r\n"), b.count(b"\n"), len(b.split(b"\n"))))
r2 = subprocess.run(["git", "config", "core.autocrlf"], capture_output=True, cwd=ROOT,
                    creationflags=0x08000000)
print("autocrlf=" + r2.stdout.decode().strip())
