import subprocess
out = subprocess.run(["git","-C",r"K:\Fluxgroup\FluxGroup","show","origin/main:docs/orders.md"],capture_output=True)
data = out.stdout.decode("utf-8","replace")
lines = data.splitlines()
open(r"results\_r1084bmc_ordtail.txt","w",encoding="utf-8").write("\n".join(lines[-36:])+"\n")
print("wrote", len(lines[-36:]), "tail lines; total", len(lines))
