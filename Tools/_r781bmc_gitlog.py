"""r781 bm-c git-log tail probe: commits since r780 close (ba6a3823b)."""
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
p = subprocess.run(["git", "-C", ROOT, "log", "--oneline", "-8", "origin/main"],
                   capture_output=True)
print(p.stdout.decode("utf-8", "replace"))
p2 = subprocess.run(["git", "-C", ROOT, "log", "-3", "--stat", "--format=%h %s"],
                    capture_output=True)
print(p2.stdout.decode("utf-8", "replace")[:2600])
