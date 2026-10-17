import subprocess, io
GT = r"K:\Fluxgroup\FluxGroup"
def show(path, out):
    r = subprocess.run(["git","-C",GT,"show","origin/main:"+path],capture_output=True)
    io.open(out,"wb").write(r.stdout)
    print("wrote", out, len(r.stdout), "bytes")
show("Tools/memory-budget-gate.py", r"results\_r1084bmc_gate_v2_origin.py")
show("cph4/research/R-20261018-memory-control-01.md", r"results\_r1084bmc_memctl_rdoc.md")
r = subprocess.run(["git","-C",GT,"show","origin/main:cph4/fleet/memory-slim/LEDGER.md"],capture_output=True)
lines = r.stdout.decode("utf-8","replace").splitlines()
open(r"results\_r1084bmc_ledger_tail.txt","w",encoding="utf-8").write("\n".join(lines[-14:])+"\n")
print("ledger total lines:", len(lines))
r2 = subprocess.run(["git","-C",GT,"ls-tree","--name-only","origin/main","cph4/skills/"],capture_output=True)
open(r"results\_r1084bmc_skills_list.txt","w",encoding="utf-8").write(r2.stdout.decode("utf-8","replace"))
print("skills canon entries listed")
