"""r536 bm-c: git log recent commits to replicate close pattern."""
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
r = subprocess.run(["git", "log", "--oneline", "-6"], capture_output=True, cwd=ROOT,
                   creationflags=CREATE_NO_WINDOW)
print((r.stdout or b"").decode("utf-8", "replace"))
