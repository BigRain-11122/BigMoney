import subprocess, sys
repo = r"C:\Fluxgroup\FluxGroup"
path = sys.argv[1] if len(sys.argv) > 1 else "cph4/research/R-20261018-memory-control-01.md"
out = sys.argv[2] if len(sys.argv) > 2 else r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1002bmb_group_blob.txt"
r = subprocess.run(["git", "-C", repo, "show", "origin/main:" + path], capture_output=True)
if r.returncode != 0:
    print("RC=%d %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[:200])); sys.exit(1)
open(out, "wb").write(r.stdout)
print("WROTE %d bytes -> %s" % (len(r.stdout), out))
