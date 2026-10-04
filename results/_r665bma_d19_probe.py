"""r665 D-19 watermark probe: sha256 of origin decisions.md raw bytes (r660 law: git show subprocess, no disk copy)."""
import hashlib, subprocess

REPO = r"C:\Users\sjs20\Desktop\FluxGroup"
raw = subprocess.run(
    ["git", "-C", REPO, "show", "origin/main:docs/decisions.md"],
    capture_output=True, check=True,
).stdout
print("sha256:", hashlib.sha256(raw).hexdigest())
print("bytes:", len(raw))
